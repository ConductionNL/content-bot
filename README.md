### conduction-content-bot

A Slack bot that helps you generate concise, on-brand content (Dutch) for website pages and LinkedIn posts. It uses OpenAI for drafting, fetches reference content from your live website, and guides users through an iterative DM flow in Slack.


## Prerequisites
- Python 3.11+
- Slack app with Socket Mode enabled
  - App-level token (starts with `xapp-`) and Bot token (starts with `xoxb-`)
  - Recommended bot scopes: `chat:write`, `im:history` (for DMs)
  - Enable event subscription for messages in DMs if using Events API; with Socket Mode Bolt listens internally
  - Create/manage at the [Slack API apps dashboard](https://api.slack.com/apps)
- OpenAI API key
- [uv](https://docs.astral.sh/uv/) installed locally (or use the Makefile which invokes `uv`)

## Quick start (local)
1) Clone and enter the repo
```bash
git clone <your-fork-or-repo-url>
cd conduction-content-bot
```

2) Install (via Makefile or uv)
```bash
# Option A: Make (recommended)
make dev-install  # uses: uv sync --locked --extra dev

# Option B: uv only (no Makefile)
uv sync --locked --extra dev
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

# or directly with uv
PYTHONPATH=src uv run python -m conduction_content_bot
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

Note: The Docker image installs runtime dependencies using `uv sync --locked --no-dev` from `uv.lock` for reproducible builds and runs the app directly with Python.

### Run with Docker Compose
```bash
# Create .env file first (see step 3 above)
docker-compose up --build
```

The compose file uses `network_mode: "host"` for Slack Socket Mode connectivity.