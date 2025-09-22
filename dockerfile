FROM python:3.11-slim
WORKDIR /app

# Base packages
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Copy project files
COPY pyproject.toml uv.lock README.md /app/
COPY src/ /app/src/

# Install runtime dependencies and the project from the lockfile
RUN uv sync --locked --no-dev

ENV PYTHONUNBUFFERED=1
CMD ["uv", "run", "python", "-m", "conduction_content_bot"]
