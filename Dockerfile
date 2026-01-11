# ---------- frontend ----------

FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

COPY app/frontend/package*.json ./
RUN npm ci

COPY app/frontend ./
RUN npm run build

# ---------- backend ----------

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN uv venv /app/.venv
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml ./
COPY app ./app

RUN uv pip install .

COPY --from=frontend-builder /app/frontend/dist ./app/frontend/dist

RUN adduser --system --group appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["gunicorn", "app.backend.main:app", \
     "--workers", "2", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000"]
