# Minicerebro

Aplicacion especializada en escritura en lengua espanola. Esta primera base implementa el esqueleto funcional de V1: conocimiento estable separado del perfil, scoring editable con ajuste manual, preferencias trazables, comparador y editor basico.

## Desarrollo local

Backend:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e "backend[dev]"
cd backend
uvicorn app.main:app --reload
```

Persistencia con PostgreSQL:

```bash
cp .env.example .env
docker compose up -d postgres
export DATABASE_URL=postgresql+psycopg://minicerebro:minicerebro@localhost:5432/minicerebro
cd backend
../.venv/bin/alembic upgrade head
../.venv/bin/uvicorn app.main:app --reload
```

Si `DATABASE_URL` no esta definida, el backend usa `backend/minicerebro.sqlite3` como base local persistente de desarrollo.

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Por defecto el frontend espera la API en `http://localhost:8000`.

## Estado de esta base

- FastAPI con endpoints iniciales del contrato.
- React/Vite con pantallas V1 principales.
- SQLAlchemy y Alembic con modelos persistentes para perfiles, preferencias, variables, evidencias, comparaciones y eventos.
- Tests unitarios del scoring, comparador y API.

pgvector y generacion LLM quedan preparados como siguientes incrementos, no como dependencia obligatoria de esta base.
