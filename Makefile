.PHONY: install dev-install run lint format docker-build docker-run

install:
	uv sync --locked

dev-install:
	uv sync --locked --extra dev

run:
	PYTHONPATH=src uv run python -m conduction_content_bot

lint:
	uv run ruff check src

format:
	uv run black src

docker-build:
	docker build -t conduction-content-bot .

docker-run:
	docker run --rm --env-file .env --name conduction-content-bot conduction-content-bot

