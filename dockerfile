FROM python:3.11-slim
WORKDIR /app
COPY bot.py prompts.py home.json .
RUN pip install --no-cache-dir slack_bolt python-dotenv openai
ENV PYTHONUNBUFFERED=1
CMD ["python", "bot.py"]
