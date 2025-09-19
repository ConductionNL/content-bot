FROM python:3.11-slim
WORKDIR /app
COPY src/ /app/src/
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir slack_bolt openai beautifulsoup4 trafilatura python-dotenv
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app/src
CMD ["python", "-m", "conduction_content_bot"]
