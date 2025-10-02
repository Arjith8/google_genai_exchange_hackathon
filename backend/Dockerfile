FROM ghcr.io/astral-sh/uv:debian-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN uv venv

RUN uv sync 

COPY . .

EXPOSE 8000

CMD ["uv", "run", "fastapi", "run"]
