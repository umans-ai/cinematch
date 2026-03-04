FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Create writable data directory for SQLite database
RUN mkdir -p /app/data && chmod 777 /app/data

# Copy dependency files first (better caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

# Copy app code separately (changes often)
COPY app/ ./app/

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
