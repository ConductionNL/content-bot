### conduction-content-bot

A Slack bot that helps you generate concise, on-brand content (Dutch) for website pages and LinkedIn posts. It uses OpenAI for drafting, fetches reference content from your live website, and guides users through an iterative DM flow in Slack.

## Features
- **Slack DM flow**: Users DM the bot with a keyword (e.g., "over ons", "linkedin") and a short brief; the bot drafts and iterates.
- **Reference-aware**: Pulls readable snippets from your site to match tone and context; falls back to `reference_content.json`.
- **Home tab**: Publishes a Block Kit Home view from `home.json`.
- **Resilient LLM calls**: Retries with exponential backoff; caps conversation history.

## Project layout
- `src/conduction_content_bot/__main__.py`: Entrypoint that runs the bot via `python -m conduction_content_bot`.
- `src/conduction_content_bot/bot.py`: Slack Bolt Socket Mode app, DM handlers, OpenAI calls, retry/backoff, history.
- `src/conduction_content_bot/prompts.py`: System prompt builder, keyword detection, reference content loader.
- `src/conduction_content_bot/content_fetcher.py`: Fetches pages and extracts readable HTML using trafilatura + BeautifulSoup.
- `src/conduction_content_bot/reference_content.json`: Fallback reference snippets per page key.
- `src/conduction_content_bot/home.json`: Slack App Home view (Block Kit JSON).
- `pyproject.toml`: Project metadata and dependencies.
- `Makefile`: Common tasks (`install`, `dev-install`, `run`, `lint`, `format`, `docker-*`).
- `dockerfile`: Container build for production use.
- `docker-compose.yml`: Compose service to build and run the bot via Docker.

## Prerequisites
- Python 3.11+
- Slack app with Socket Mode enabled
  - App-level token (starts with `xapp-`) and Bot token (starts with `xoxb-`)
  - Recommended bot scopes: `chat:write`, `im:history` (for DMs)
  - Enable event subscription for messages in DMs if using Events API; with Socket Mode Bolt listens internally
  - Create/manage at the [Slack API apps dashboard](https://api.slack.com/apps)
- OpenAI API key

## Quick start (local)
1) Clone and enter the repo
```bash
git clone <your-fork-or-repo-url>
cd conduction-content-bot
```

2) Install (via Makefile or pip)
```bash
# Option A: Make (recommended)
python -m venv .venv && source .venv/bin/activate
make dev-install  # or: make install

# Option B: pip only
python -m venv .venv && source .venv/bin/activate
pip install -e .  # add .[dev] for ruff/black/pytest
```

3) Create a `.env`
```env
SLACK_APP_TOKEN=xapp-...
SLACK_BOT_TOKEN=xoxb-...
OPENAI_API_KEY=sk-...

# Optional overrides
OPENAI_MODEL=gpt-5-mini
OPENAI_TIMEOUT_SECONDS=30
OPENAI_MAX_RETRIES=3
LLM_BACKOFF_BASE_SECONDS=1.0
LLM_BACKOFF_MAX_SECONDS=15.0
HISTORY_MAX_MESSAGES=10

# For content fetching (defaults to https://conduction.nl)
WEBSITE_BASE_URL=https://conduction.nl
```

4) Run the bot
```bash
# via Makefile
make run

# or directly
PYTHONPATH=src python -m conduction_content_bot
```

### Makefile targets
```bash
make install       # pip install -e .
make dev-install   # pip install -e .[dev]
make run           # PYTHONPATH=src python -m conduction_content_bot
make lint          # ruff check src
make format        # black src
make docker-build  # docker build -t conduction-content-bot .
make docker-run    # docker run --rm --env-file .env --name conduction-content-bot conduction-content-bot
```

## Run with Docker
Build image:
```bash
docker build -t conduction-content-bot .
```

Run container (reads variables from your `.env`):
```bash
docker run --rm \
  --env-file .env \
  --name conduction-content-bot \
  conduction-content-bot
```

### Run with Docker Compose
```bash
docker compose up -d
```
Compose reads your `.env` automatically. The provided compose file builds the image and runs the bot (using `network_mode: host`).

Note: `docker-compose.yml` includes `MAX_REFERENCE_CHARS` and `WEB_FETCH_TTL_SECONDS` for future use. These are currently not used by the code and can be omitted from your `.env`.

## Using the bot in Slack
- DM the bot. Start with a keyword to pick a page, then describe your request.
  - Recognized keywords (examples): `over ons`, `beheer`, `projecten`, `common ground`, `trainingen`, `linkedin`, `home`.
- Commands:
  - `help`: Shows usage tips and available keywords
  - `reset`: Clears context for the current DM thread
- The bot replies with drafts as code blocks to preserve formatting. Iterate by replying (e.g., "korter", "formeler", "voeg CTA toe").

## Reference content and customization
- Live-site reference: The bot fetches pages based on `PAGE_TO_URL` in `content_fetcher.py` under `WEBSITE_BASE_URL`.
- Fallback: If fetching fails, it uses `reference_content.json`.
- To adjust which pages are supported:
  - Update `PAGE_TO_URL` in `content_fetcher.py` and the keyword maps in `prompts.py` (`KEYWORD_TO_PAGE`, `PAGE_TO_DISPLAY_KEY`).
  - Optionally expand `reference_content.json` with matching keys, for example:
```json
{
  "OVER_ONS": "<h1>Over ons</h1><p>Wij zijn ...</p>",
  "BEHEER": "<h1>Beheer</h1><p>Onze beheerdiensten ...</p>",
  "HOME": "<h1>Welkom</h1><p>Intro ...</p>"
}
```

## Environment variables
- **SLACK_APP_TOKEN**: App-level token (`xapp-...`) for Socket Mode.
- **SLACK_BOT_TOKEN**: Bot token (`xoxb-...`) with `chat:write`, `im:history`.
- **OPENAI_API_KEY**: OpenAI API key.
- **OPENAI_MODEL**: Model name (default: `gpt-5-mini`).
- **OPENAI_TIMEOUT_SECONDS**: Per-request timeout (default: 30).
- **OPENAI_MAX_RETRIES**: Retry attempts for transient failures (default: 3).
- **LLM_BACKOFF_BASE_SECONDS**: Exponential backoff base (default: 1.0).
- **LLM_BACKOFF_MAX_SECONDS**: Backoff cap (default: 15.0).
- **HISTORY_MAX_MESSAGES**: Max messages to keep per thread (default: 10).
- **WEBSITE_BASE_URL**: Base URL for `PAGE_TO_URL` resolution (default: `https://conduction.nl`).

## Repo housekeeping
- `.gitignore` includes entries for local secrets and artifacts: `.env`, `.venv/`, and Python cache directories.
- Linting/formatting: `ruff` and `black` are available via the `dev` extra.

## Notes and troubleshooting
- Logging is verbose by default (DEBUG for Slack SDK). If needed, lower the level in `bot.py`.
- If messages do not arrive:
  - Verify the bot is installed to your workspace and you can DM it.
  - Check tokens and scopes; ensure Socket Mode is enabled.
- If reference fetching fails: check `WEBSITE_BASE_URL`, network access, and the selectors in `content_fetcher.py`.
- OpenAI errors: transient timeouts and rate limits are retried; persistent 4xx errors are surfaced in logs.

---
Maintained for Conduction. Contributions welcome via PR.

