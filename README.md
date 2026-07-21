# Minicerebro

Aplicacion especializada en escritura en lengua espanola. Esta primera base implementa el esqueleto funcional de V1: conocimiento estable separado del perfil, scoring editable con ajuste manual, preferencias trazables, comparador y editor basico.

## Desarrollo local

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

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
- Repositorio en memoria para permitir una primera app usable sin PostgreSQL.
- Tests unitarios del scoring, comparador y API.

PostgreSQL, pgvector, Alembic y generacion LLM quedan preparados como siguiente incremento, no como dependencia obligatoria de esta primera subida.

