# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl && \
    rm -rf /var/lib/apt/lists/*

# --- Poetry ---
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# только зависимости
COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-root --only main

# теперь код
COPY . /app

EXPOSE 8000

# по умолчанию запускаем REST API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
