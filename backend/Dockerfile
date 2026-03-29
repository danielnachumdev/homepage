# Build from homepage repo root (directory that contains pyproject.toml and uv.lock):
#   docker build -f backend/Dockerfile .
#
FROM python:3.11-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

COPY backend/ ./backend/

WORKDIR /app/backend

EXPOSE 8000

CMD ["uv", "run", "--project", "/app", "python", "__main__.py"]
