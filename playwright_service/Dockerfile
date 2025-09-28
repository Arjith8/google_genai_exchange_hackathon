FROM ghcr.io/astral-sh/uv:debian-slim

WORKDIR /playwright_service

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync 

RUN uv run playwright install chromium

RUN uv run playwright install-deps

COPY . .

EXPOSE 8000

CMD ["uv", "run", "fastapi", "run"]
