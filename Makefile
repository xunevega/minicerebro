PYTHON ?= .venv/bin/python
RUFF ?= .venv/bin/ruff
PYTEST ?= .venv/bin/pytest
ALEMBIC ?= .venv/bin/alembic
SQLITE_DATABASE_URL ?= sqlite:////tmp/minicerebro-validate.sqlite3
POSTGRES_DATABASE_URL ?= postgresql+psycopg://postgres:postgres@localhost:5432/app
FRONTEND_URL ?= http://127.0.0.1:5173
API_BASE ?= http://127.0.0.1:8000
BACKEND_URL ?= https://backend-production-4652.up.railway.app
PRODUCTION_FRONTEND_URL ?= https://frontend-production-834c.up.railway.app
EXPECTED_VERSION ?= knowledge-v51

.PHONY: validate lint test-backend build-frontend migrate-sqlite migrate-postgres smoke-ui smoke-production export-knowledge-snapshot clean-generated

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
	cd frontend && FRONTEND_URL="$(FRONTEND_URL)" VITE_API_BASE="$(API_BASE)" npm run test:smoke-ui

smoke-production:
	BACKEND_URL="$(BACKEND_URL)" FRONTEND_URL="$(PRODUCTION_FRONTEND_URL)" EXPECTED_VERSION="$(EXPECTED_VERSION)" sh scripts/smoke-production.sh

export-knowledge-snapshot:
	$(PYTHON) scripts/export-knowledge-snapshot.py --version "$(EXPECTED_VERSION)" --output "backend/app/knowledge/data/$(EXPECTED_VERSION).snapshot.json"

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
