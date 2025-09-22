import json
import logging
import os
import random
import sys
import time
from threading import Lock, RLock
from typing import Any, Dict, List

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from .prompts import PAGE_TO_DISPLAY_KEY, build_system_prompt, detect_page_key

# --- Model wiring (OpenAI) ---
try:
    from openai import (
        APIConnectionError,
        APIError,
        APITimeoutError,
        OpenAI,
        RateLimitError,
    )
except Exception:
    print("Install the OpenAI SDK: pip install openai", file=sys.stderr)
    raise


APP_TOKEN = os.getenv("SLACK_APP_TOKEN")  # xapp-...
BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")  # xoxb-...
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
OPENAI_TIMEOUT_SECONDS = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "30"))
OPENAI_MAX_RETRIES = int(os.getenv("OPENAI_MAX_RETRIES", "3"))
BACKOFF_BASE_SECONDS = float(os.getenv("LLM_BACKOFF_BASE_SECONDS", "1.0"))
BACKOFF_MAX_SECONDS = float(os.getenv("LLM_BACKOFF_MAX_SECONDS", "15.0"))
HISTORY_MAX_MESSAGES = int(os.getenv("HISTORY_MAX_MESSAGES", "10"))


if not APP_TOKEN or not BOT_TOKEN:
    print("Missing SLACK_APP_TOKEN or SLACK_BOT_TOKEN in environment", file=sys.stderr)
    sys.exit(1)
if not OPENAI_API_KEY:
    print("Missing OPENAI_API_KEY in environment", file=sys.stderr)
    sys.exit(1)

# Use client without internal retries; rely on our own retry wrapper for full control
oai = OpenAI(api_key=OPENAI_API_KEY, timeout=OPENAI_TIMEOUT_SECONDS, max_retries=0)
app = App(token=BOT_TOKEN)

# Load Slack App Home tab Block Kit view from home.json.
HOME_VIEW_PATH = os.path.join(os.path.dirname(__file__), "home.json")
with open(HOME_VIEW_PATH, "r", encoding="utf-8") as f:
    HOME_VIEW = json.load(f)

# In-memory per-thread state: page_key + conversation history + waiting_for_content_description
THREADS: Dict[str, Dict[str, Any]] = {}

# Per-conversation locks to prevent race conditions on shared state
CONV_LOCKS: Dict[str, RLock] = {}
CONV_LOCKS_MASTER: Lock = Lock()


def _get_conv_lock(conversation_id: str) -> RLock:
    with CONV_LOCKS_MASTER:
        lock = CONV_LOCKS.get(conversation_id)
        if lock is None:
            lock = RLock()
            CONV_LOCKS[conversation_id] = lock
        return lock


def _sleep_with_backoff(attempt_index: int) -> None:
    """
    @param attempt_index: Zero-based retry attempt index used to compute
    exponential backoff.
    @returns: None
    """
    delay = min(
        BACKOFF_BASE_SECONDS * (2**attempt_index) + random.uniform(0, 0.5),
        BACKOFF_MAX_SECONDS,
    )
    time.sleep(delay)


def _cap_history(history: List[dict], max_messages: int | None = None) -> List[dict]:
    """
    Enforce a maximum number of messages in the conversation history.
    Preserves the initial system message if present and keeps the most recent
    messages after that, so the total length is at most ``max_messages``.
    """
    if max_messages is None:
        max_messages = HISTORY_MAX_MESSAGES
    if not history or max_messages <= 0:
        return []
    if history[0].get("role") == "system":
        system_msg = history[0]
        tail = history[1:]
        keep = max_messages - 1
        if keep <= 0:
            return [system_msg]
        return [system_msg] + tail[-keep:]
    # No system message at index 0; just keep the last max_messages
    return history[-max_messages:]


def _format_code_block(text: str) -> str:
    """Wrap text in a Slack code block, escaping embedded triple backticks.

    Replaces occurrences of ``` inside the text with ``\u200b` to avoid
    prematurely closing the fence.
    """
    safe_text = (text or "").replace("```", "``\u200b`")
    return f"```{safe_text}```"


def _call_llm_with_retry(full_messages: List[dict]) -> str:
    """
    @param full_messages: Complete list of chat messages to send to the model,
    including system and conversation history.
    @returns: Assistant response content as a stripped string.
    @raises: APIError, APIConnectionError, RateLimitError, APITimeoutError on
    terminal failures after retries.
    """
    last_error: Exception | None = None
    for attempt_index in range(OPENAI_MAX_RETRIES + 1):
        try:
            resp = oai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=full_messages,
                timeout=OPENAI_TIMEOUT_SECONDS,
            )
            content = resp.choices[0].message.content or ""
            return content.strip()
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


@app.event("message")
def on_dm_events(event, say):
    """
    Slack DM message event handler.
    @param event: Slack event payload dict for the message.
    @param say: Callable to send a message back to Slack.
    @returns: None
    """
    if event.get("channel_type") != "im" or event.get("subtype") or event.get("bot_id"):
        return
    user_text = (event.get("text") or "").strip()
    if not user_text:
        return
    try:
        # Determine conversation id: use the thread if present, otherwise start
        # a new thread at this message's ts
        conversation_id = event.get("thread_ts") or event.get("ts")
        conv_lock = _get_conv_lock(conversation_id)

        # Quick help
        if user_text.lower() in {"help", "hi", "hello", "hallo", "hulp"}:
            keywords_overview = ", ".join(
                f"`{PAGE_TO_DISPLAY_KEY[page]}`" for page in PAGE_TO_DISPLAY_KEY.keys()
            )
            say(
                channel=event["channel"],
                thread_ts=conversation_id,
                text=(
                    "Welkom! Ik genereer content voor je website en LinkedIn.\n\n"
                    "Begin door een pagina te kiezen waarvoor we content gaan"
                    " maken. Je kunt kiezen uit de volgende keywords:\n"
                    f"{keywords_overview}\n\n"
                    "Vertel me daarna kort wat je nodig hebt. Geef in elk geval:\n"
                    "- Doelgroep\n"
                    "- Doel\n"
                    "- Belangrijke punten (moeten erin)\n"
                    "- Toon en stijl\n"
                    "- Lengte/format (bijv. 3–7 zinnen)\n\n"
                    "Vervolgens kun je de output iteratief verbeteren door te"
                    " reageren (bijv. 'korter', 'formeler', 'voeg CTA toe'). "
                    "Typ 'reset' om opnieuw te beginnen."
                ),
            )
            return

        # Reset current thread context on demand
        if user_text.lower() in {"reset", "new", "start over", "opnieuw", "nieuw"}:
            with conv_lock:
                THREADS[conversation_id] = {
                    "page_key": None,
                    "history": [],
                    "waiting_for_content_description": False,
                    "page_content": None,
                }
            keywords_overview = ", ".join(
                f"`{PAGE_TO_DISPLAY_KEY[page]}`" for page in PAGE_TO_DISPLAY_KEY.keys()
            )
            say(
                channel=event["channel"],
                thread_ts=conversation_id,
                text=(
                    "Context gewist voor deze thread. Start met een nieuw"
                    " keyword om content te genereren. Kies uit:  "
                    f"{keywords_overview}."
                ),
            )
            return

        # Initialize or update thread state
        with conv_lock:
            state = THREADS.get(conversation_id)
            if not state:
                state = {
                    "page_key": None,
                    "history": [],
                    "waiting_for_content_description": False,
                    "page_content": None,
                }
                THREADS[conversation_id] = state

        # Check if we're waiting for content description
        if state.get("waiting_for_content_description", False):
            # User provided content description, now generate content
            page_key = state.get("page_key")
            if page_key:
                with conv_lock:
                    history: List[dict] = state.get("history", [])
                    if not history:
                        history.append({"role": "system", "content": state["page_content"]})
                    history.append({"role": "user", "content": user_text})
                    history = _cap_history(history)
                    state["history"] = history

                draft = _call_llm_with_retry(history)  # generate_content(page_key, history)

                with conv_lock:
                    history.append({"role": "assistant", "content": draft})
                    history = _cap_history(history)
                    state["history"] = history
                    state["waiting_for_content_description"] = False
                    THREADS[conversation_id] = state

                # Send as a code block so formatting is preserved, in thread
                say(
                    channel=event["channel"],
                    thread_ts=conversation_id,
                    text=_format_code_block(draft),
                )
                return
            else:
                # Missing page key; reset waiting flag and prompt for a keyword again
                with conv_lock:
                    state["waiting_for_content_description"] = False
                    THREADS[conversation_id] = state
                keywords_overview = ", ".join(
                    f"`{PAGE_TO_DISPLAY_KEY[page]}`" for page in PAGE_TO_DISPLAY_KEY.keys()
                )
                say(
                    channel=event["channel"],
                    thread_ts=conversation_id,
                    text=(
                        "Ik kon het opgegeven keyword niet vinden. "
                        "Kies eerst een keyword en probeer het opnieuw.\n\n"
                        f"Beschikbare keywords: {keywords_overview}"
                    ),
                )
                return

        # Check if we need to detect a page key
        if not state.get("page_key"):

            detected_page = detect_page_key(user_text)
            if detected_page:
                page_content = build_system_prompt(detected_page)
                # If we couldn't build content for the detected page, inform the
                # user and ask to pick another keyword
                if page_content is None:
                    keywords_overview = ", ".join(
                        f"`{PAGE_TO_DISPLAY_KEY[page]}`" for page in PAGE_TO_DISPLAY_KEY.keys()
                    )
                    say(
                        channel=event["channel"],
                        thread_ts=conversation_id,
                        text=(
                            "Ik kon geen content vinden voor deze pagina. Kies"
                            " alsjeblieft een ander keyword.\n\n"
                            f"Beschikbare keywords: {keywords_overview}"
                        ),
                    )
                    return
                with conv_lock:
                    state["page_key"] = detected_page
                    state["page_content"] = page_content
                    state["waiting_for_content_description"] = True
                    THREADS[conversation_id] = state

                # Ask for content description (NL) with only a small title difference
                page_name = detected_page.lower().replace("_", " ")
                is_linkedin = detected_page == "LINKEDIN"
                titel = (
                    "een LinkedIn-post" if is_linkedin else f"content voor de pagina `{page_name}`"
                )
                prompt_text = (
                    f"Hoi! Ik help je met het schrijven van {titel}.\n\n"
                    "Vertel kort waar de content over moet gaan. Geef bij voorkeur:\n"
                    "- Doelgroep\n"
                    "- Doel (bijv. informeren, aankondigen, uitnodigen tot contact)\n"
                    "- Belangrijke punten/links (moeten erin)\n"
                    "- Toon en stijl (bijv. nuchter, professioneel, vriendelijk)\n"
                    "- Lengte/format (bijv. 3–7 zinnen, met CTA)\n\n"
                    "Je kunt de output daarna iteratief verbeteren door te"
                    " reageren (bijv. 'korter', 'formeler/menselijker',"
                    " 'voeg CTA toe', '3 varianten')."
                )
                say(
                    channel=event["channel"],
                    thread_ts=conversation_id,
                    text=prompt_text,
                )
                return
            else:
                # No page key detected, ask for clarification (NL) and show
                # available keywords
                keywords_overview = ", ".join(
                    f"`{PAGE_TO_DISPLAY_KEY[page]}`" for page in PAGE_TO_DISPLAY_KEY.keys()
                )
                say(
                    channel=event["channel"],
                    thread_ts=conversation_id,
                    text=(
                        "Ik kon geen keyword herkennen. Start je bericht met een"
                        " keyword om de pagina te kiezen waarvoor we content gaan"
                        " genereren.\n\n"
                        f"Herkende keywords: {keywords_overview}"
                    ),
                )
                return

        # Continue existing conversation (page key already set, not waiting for description)
        with conv_lock:
            history: List[dict] = state.get("history", [])
            if not history:
                history.append({"role": "system", "content": state["page_content"]})
            history.append({"role": "user", "content": user_text})
            history = _cap_history(history)
            state["history"] = history

        draft = _call_llm_with_retry(history)  # generate_content(state["page_key"], history)

        with conv_lock:
            history.append({"role": "assistant", "content": draft})
            history = _cap_history(history)
            state["history"] = history
            THREADS[conversation_id] = state

        # Send as a code block so formatting is preserved, in thread
        say(
            channel=event["channel"],
            thread_ts=conversation_id,
            text=_format_code_block(draft),
        )
    except Exception as e:
        say(
            channel=event["channel"],
            thread_ts=event.get("thread_ts") or event.get("ts"),
            text="Sorry, I couldn’t generate that. Please try again.",
        )
        logging.exception(f"Error generating content: {e}")


def main() -> None:
    handler = SocketModeHandler(
        app,
        APP_TOKEN,
        auto_reconnect_enabled=True,
        trace_enabled=False,
        ping_pong_trace_enabled=False,
        all_message_trace_enabled=False,
        ping_interval=10,
        concurrency=10,
    )
    handler.start()


if __name__ == "__main__":
    main()
