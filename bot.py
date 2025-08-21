import os, sys, time, random
import json
from typing import Dict, List, Any
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# --- Model wiring (OpenAI) ---
try:
    from openai import OpenAI, APIError, APIConnectionError, RateLimitError, APITimeoutError
except Exception:
    print("Install the OpenAI SDK: pip install openai", file=sys.stderr)
    raise

load_dotenv()

APP_TOKEN = os.getenv("SLACK_APP_TOKEN")   # xapp-...
BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")   # xoxb-...
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini") 
OPENAI_TIMEOUT_SECONDS = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "30"))
OPENAI_MAX_RETRIES = int(os.getenv("OPENAI_MAX_RETRIES", "3"))
BACKOFF_BASE_SECONDS = float(os.getenv("LLM_BACKOFF_BASE_SECONDS", "1.0"))
BACKOFF_MAX_SECONDS = float(os.getenv("LLM_BACKOFF_MAX_SECONDS", "15.0"))

from prompts import build_system_prompt, detect_page_key, KEYWORD_TO_PAGE, PAGE_TO_DISPLAY_KEY

if not APP_TOKEN or not BOT_TOKEN:
    print("Missing SLACK_APP_TOKEN or SLACK_BOT_TOKEN in .env", file=sys.stderr); sys.exit(1)
if not OPENAI_API_KEY:
    print("Missing OPENAI_API_KEY in .env", file=sys.stderr); sys.exit(1)

# Use client without internal retries; rely on our own retry wrapper for full control
oai = OpenAI(api_key=OPENAI_API_KEY, timeout=OPENAI_TIMEOUT_SECONDS, max_retries=0)
app = App(token=BOT_TOKEN)

HOME_VIEW_PATH = os.path.join(os.path.dirname(__file__), "home.json")
with open(HOME_VIEW_PATH, "r", encoding="utf-8") as f:
    HOME_VIEW = json.load(f)

# In-memory per-thread state: page_key + conversation history + waiting_for_content_description
THREADS: Dict[str, Dict[str, Any]] = {}


def _sleep_with_backoff(attempt_index: int) -> None:
    delay = min(BACKOFF_BASE_SECONDS * (2 ** attempt_index) + random.uniform(0, 0.5), BACKOFF_MAX_SECONDS)
    time.sleep(delay)


def _call_llm_with_retry(full_messages: List[dict]) -> str:
    last_error: Exception | None = None
    for attempt_index in range(OPENAI_MAX_RETRIES + 1):
        try:
            resp = oai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=full_messages,
                temperature=0.7,
                max_tokens=900,
                timeout=OPENAI_TIMEOUT_SECONDS,
            )
            return resp.choices[0].message.content.strip()
        except (APITimeoutError, APIConnectionError, RateLimitError) as err:
            last_error = err
        except APIError as err:
            # Retry on 5xx only
            status = getattr(err, "status_code", None)
            if status is not None and 500 <= int(status) < 600:
                last_error = err
            else:
                raise

        if attempt_index < OPENAI_MAX_RETRIES:
            _sleep_with_backoff(attempt_index)

    assert last_error is not None
    raise last_error


def generate_content(page_key: str, messages: List[dict]) -> str:
    """Return Markdown draft based on a conversation history and page context."""
    full_messages = [
        {"role": "system", "content": build_system_prompt(page_key)}
    ] + messages
    return _call_llm_with_retry(full_messages)

@app.event("message")
def on_dm_events(body, event, say):
    if event.get("channel_type") != "im" or event.get("subtype") or event.get("bot_id"):
        return
    user_text = (event.get("text") or "").strip()
    if not user_text:
        return
    try:
        # Determine conversation id: use the thread if present, otherwise start a new thread at this message's ts
        conversation_id = event.get("thread_ts") or event.get("ts")

        # Quick help
        if user_text.lower() in {"help", "hi", "hello", "hallo", "hulp"}:
            keywords_overview = ", ".join(f"`{PAGE_TO_DISPLAY_KEY[page]}`" for page in PAGE_TO_DISPLAY_KEY.keys())
            say(
                channel=event["channel"],
                thread_ts=conversation_id,
                text=(
                    "Welkom! Ik genereer content voor je website en LinkedIn.\n\n"
                    "Begin door een pagina te kiezen waarvoor we content gaan maken. Je kunt kiezen uit de volgende keywords:\n"
                    f"{keywords_overview}\n\n"
                    "Vertel me daarna kort wat je nodig hebt. Geef in elk geval:\n"
                    "- Doelgroep\n"
                    "- Doel\n"
                    "- Belangrijke punten (moeten erin)\n"
                    "- Toon en stijl\n"
                    "- Lengte/format (bijv. 3–7 zinnen)\n\n"
                    "Vervolgens kun je de output iteratief verbeteren door te reageren (bijv. 'korter', 'formeler', 'voeg CTA toe'). "
                    "Typ 'reset' om opnieuw te beginnen."
                ),
            )
            return

        # Reset current thread context on demand
        if user_text.lower() in {"reset", "new", "start over", "opnieuw", "nieuw"}:
            THREADS[conversation_id] = {"page_key": None, "history": [], "waiting_for_content_description": False}
            keywords_overview = ", ".join(f"`{PAGE_TO_DISPLAY_KEY[page]}`" for page in PAGE_TO_DISPLAY_KEY.keys())
            say(
                channel=event["channel"],
                thread_ts=conversation_id,
                text=(
                    "Context gewist voor deze thread. Start met een nieuw keyword om content te genereren. Kies uit:  "
                    f"{keywords_overview}."
                ),
            )
            return

        # Initialize or update thread state
        state = THREADS.get(conversation_id)
        if not state:
            state = {"page_key": None, "history": [], "waiting_for_content_description": False}
            THREADS[conversation_id] = state

        # Check if we're waiting for content description
        if state.get("waiting_for_content_description", False):
            # User provided content description, now generate content
            page_key = state.get("page_key")
            if page_key:
                history: List[dict] = state.get("history", [])
                history.append({"role": "user", "content": user_text})
                draft = generate_content(page_key, history)
                history.append({"role": "assistant", "content": draft})
                state["history"] = history
                state["waiting_for_content_description"] = False
                THREADS[conversation_id] = state

                # Send as a code block so formatting is preserved, in thread
                say(channel=event["channel"], thread_ts=conversation_id, text=f"```{draft}```")
            return

        # Check if we need to detect a page key
        if not state.get("page_key"):
            detected_page = detect_page_key(user_text)
            if detected_page:
                state["page_key"] = detected_page
                state["waiting_for_content_description"] = True
                THREADS[conversation_id] = state
                
                # Ask for content description (NL) with only a small title difference
                page_name = detected_page.lower().replace('_', ' ')
                is_linkedin = detected_page == "LINKEDIN"
                titel = "een LinkedIn-post" if is_linkedin else f"content voor de pagina `{page_name}`"
                prompt_text = (
                    f"Hoi! Ik help je met het schrijven van {titel}.\n\n"
                    "Vertel kort waar de content over moet gaan. Geef bij voorkeur:\n"
                    "- Doelgroep\n"
                    "- Doel (bijv. informeren, aankondigen, uitnodigen tot contact)\n"
                    "- Belangrijke punten/links (moeten erin)\n"
                    "- Toon en stijl (bijv. nuchter, professioneel, vriendelijk)\n"
                    "- Lengte/format (bijv. 3–7 zinnen, met CTA)\n\n"
                    "Je kunt de output daarna iteratief verbeteren door te reageren (bijv. 'korter', 'formeler/menselijker', 'voeg CTA toe', '3 varianten')."
                )

                say(channel=event["channel"], thread_ts=conversation_id, text=prompt_text)
                return
            else:
                # No page key detected, ask for clarification (NL) and show available keywords
                keywords_overview = ", ".join(f"`{PAGE_TO_DISPLAY_KEY[page]}`" for page in PAGE_TO_DISPLAY_KEY.keys())
                say(
                    channel=event["channel"],
                    thread_ts=conversation_id,
                    text=(
                        "Ik kon geen keyword herkennen. Start je bericht met een keyword om de pagina te kiezen waarvoor we content gaan genereren.\n\n"
                        f"Herkende keywords: {keywords_overview}"
                    )
                )
                return
        
        # Continue existing conversation (page key already set, not waiting for description)
        history: List[dict] = state.get("history", [])
        history.append({"role": "user", "content": user_text})
        draft = generate_content(state["page_key"], history)
        history.append({"role": "assistant", "content": draft})
        state["history"] = history
        THREADS[conversation_id] = state

        # Send as a code block so formatting is preserved, in thread
        say(channel=event["channel"], thread_ts=conversation_id, text=f"```{draft}```")
    except Exception as e:
        say(channel=event["channel"], thread_ts=event.get("thread_ts") or event.get("ts"), text=f"Sorry, I couldn’t generate that ({e}). Try again.")

@app.event("app_home_opened")
def publish_home_tab(client, event, logger):
    if event.get("tab") != "home":
        return
    try:
        client.views_publish(user_id=event["user"], view=HOME_VIEW)
    except Exception:
        logger.exception("Failed to publish Home tab")

if __name__ == "__main__":
    print("Connecting to Slack via Socket Mode…")
    SocketModeHandler(app, APP_TOKEN).start()
