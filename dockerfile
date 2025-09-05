FROM python:3.11-slim
WORKDIR /app
COPY bot.py prompts.py home.json content_fetcher.py reference_content.json .
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir slack_bolt python-dotenv openai bs4 trafilatura  
ENV PYTHONUNBUFFERED=1
CMD ["python", "bot.py"]
