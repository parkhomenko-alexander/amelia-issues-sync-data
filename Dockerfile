FROM python:3.11.11-alpine3.20

RUN apk update && apk add --no-cache build-base python3-dev

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PATH="/root/.local/bin/:$PATH"
ENV PYTHONPATH=/app
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . ./