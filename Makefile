PYTHON ?= .venv/bin/python
RUFF ?= .venv/bin/ruff
PYTEST ?= .venv/bin/pytest
ALEMBIC ?= .venv/bin/alembic
SQLITE_DATABASE_URL ?= sqlite:////tmp/minicerebro-validate.sqlite3
POSTGRES_DATABASE_URL ?= postgresql+psycopg://postgres:postgres@localhost:5432/app
FRONTEND_URL ?= http://127.0.0.1:5173
BACKEND_URL ?= https://backend-production-4652.up.railway.app
PRODUCTION_FRONTEND_URL ?= https://frontend-production-834c.up.railway.app
EXPECTED_VERSION ?= knowledge-v7

.PHONY: validate lint test-backend build-frontend migrate-sqlite migrate-postgres smoke-ui smoke-production clean-generated

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

smoke-production:
	BACKEND_URL="$(BACKEND_URL)" FRONTEND_URL="$(PRODUCTION_FRONTEND_URL)" EXPECTED_VERSION="$(EXPECTED_VERSION)" sh scripts/smoke-production.sh

clean-generated:
	find . -type f \( -name '.DS_Store' -o -name '*.pyc' -o -name '*.pyo' -o -name '*.tsbuildinfo' \) \
		-not -path './.git/*' \
		-not -path './.venv/*' \
		-not -path './frontend/node_modules/*' \
		-not -path './frontend/dist/*' \
		-delete
	find . -type d -name '__pycache__' \
		-not -path './.git/*' \
		-not -path './.venv/*' \
		-not -path './frontend/node_modules/*' \
		-not -path './frontend/dist/*' \
		-empty -delete
	find . -type d \( -name '.pytest_cache' -o -name '.ruff_cache' \) \
		-not -path './.git/*' \
		-not -path './.venv/*' \
		-not -path './frontend/node_modules/*' \
		-not -path './frontend/dist/*' \
		-prune -exec rm -rf {} +
