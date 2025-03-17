FROM python:3.11.11-alpine3.20

RUN apt update && apt -y upgrade && apt-get install curl ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . ./