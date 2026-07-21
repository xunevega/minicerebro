# Minicerebro

Aplicacion especializada en escritura en lengua espanola. La V1 implementa el contrato funcional con conocimiento estable separado del perfil de preferencias, scoring editable, preferencias trazables, editor, comparador, laboratorio, feedback controlado, auditoria y cierre tecnico verificable.

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
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/app
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

- FastAPI con endpoints del contrato V1 y superficies de cierre.
- React/Vite con pantallas V1: conocimiento, preferencias, perfil, scoring, editor, laboratorio, comparador, reglas, persistencia, Cerebro, aceptacion, cierre, roadmap, pantallas y auditoria.
- SQLAlchemy y Alembic con modelos persistentes para perfiles, preferencias, variables, evidencias, comparaciones, feedback, textos generados y eventos.
- Pipeline de conocimiento persistente e inspeccionable: fuentes, nodos, evidencias, claims, fichas, version, consulta, historial y validacion auditada.
- Perfil exportable mediante `GET /profiles/{profile_id}/export`, con preferencias, evidencias, variables por contexto, estadisticas y contradicciones sin incluir la base de conocimiento.
- Observabilidad V1 disponible desde auditoria: tiempos de interpretacion/generacion, calidad de recuperacion por validacion pendiente, scoring, comparaciones y feedback.
- Auditoria de Cerebro declarativa: no se importa ningun modulo completo sin evidencia pieza por pieza.
- Cierre V1 documentado en `docs/CIERRE_PLAN_V1.md`.
- Tests unitarios/API del scoring, comparador, persistencia, feedback, aceptacion, observabilidad, conocimiento y cierre.

`pgvector`, validacion editorial avanzada y fuentes academicas versionadas no forman parte del cierre V1. No hay V2 planificada; cualquier cambio posterior queda limitado a mantenimiento o refinamiento dentro del contrato V1.

El campo `gaps` de `GET /knowledge/status` se mantiene por compatibilidad, pero sus valores representan elementos fuera de alcance V1, no tareas pendientes del cierre.

## Validacion

```bash
source .venv/bin/activate
ruff check backend/app backend/tests backend/alembic
pytest backend/tests
cd frontend
npm run build
```

Smokes UI contra una instancia real de frontend/backend:

```bash
cd frontend
FRONTEND_URL=http://127.0.0.1:5173 npm run test:smoke-ui
```

Endpoints de cierre:

- `GET /acceptance/v1`
- `GET /closure/conditions`
- `GET /closure/technical`
- `GET /contract/boundaries`
- `GET /profiles/default/export`
