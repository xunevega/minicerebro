FROM python:3.13-slim

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/pyproject.toml backend/alembic.ini ./backend/
COPY backend/alembic ./backend/alembic
COPY backend/app ./backend/app

WORKDIR /app/backend

RUN python -m pip install --upgrade pip && \
    python -m pip install -e .

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
