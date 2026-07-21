PYTHON ?= .venv/bin/python
RUFF ?= .venv/bin/ruff
PYTEST ?= .venv/bin/pytest
ALEMBIC ?= .venv/bin/alembic
SQLITE_DATABASE_URL ?= sqlite:////tmp/minicerebro-validate.sqlite3
POSTGRES_DATABASE_URL ?= postgresql+psycopg://postgres:postgres@localhost:5432/app
FRONTEND_URL ?= http://127.0.0.1:5173

.PHONY: validate lint test-backend build-frontend migrate-sqlite migrate-postgres smoke-ui

validate: lint test-backend build-frontend

lint:
	$(RUFF) check backend/app backend/tests backend/alembic

test-backend:
	$(PYTEST) backend/tests

build-frontend:
	cd frontend && npm run build

migrate-sqlite:
	cd backend && DATABASE_URL="$(SQLITE_DATABASE_URL)" ../$(ALEMBIC) upgrade head

migrate-postgres:
	cd backend && DATABASE_URL="$(POSTGRES_DATABASE_URL)" ../$(ALEMBIC) upgrade head

smoke-ui:
	cd frontend && FRONTEND_URL="$(FRONTEND_URL)" npm run test:smoke-ui
