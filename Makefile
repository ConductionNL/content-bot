.PHONY: install dev-install run lint format docker-build docker-run

install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"

run:
	PYTHONPATH=src python -m conduction_content_bot

lint:
	ruff check src

format:
	black src

docker-build:
	docker build -t conduction-content-bot .

docker-run:
	docker run --rm --env-file .env --name conduction-content-bot conduction-content-bot

