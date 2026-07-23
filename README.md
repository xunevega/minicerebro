# Minicerebro

Aplicacion especializada en escritura en lengua espanola. La V1 implementa el contrato funcional con conocimiento estable separado del perfil de preferencias, scoring editable, preferencias trazables, editor, comparador, laboratorio, feedback controlado, auditoria y cierre tecnico verificable.

## Limite de seguridad V1

Minicerebro V1 es una aplicacion local-first para desarrollo y uso en localhost. No debe exponerse a internet, dominios publicos ni redes abiertas sin anadir antes:

- autenticacion;
- secretos propios fuera de los valores de desarrollo;
- CORS de produccion;
- rate limiting, especialmente para `/generation`, `/correction`, `/rewrite`, `/continue` y `/variants`.

El `docker-compose.yml` liga PostgreSQL a `127.0.0.1` y usa credenciales de desarrollo. Son aceptables solo para entorno local.

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
- Arranque local con migraciones Alembic; `Base.metadata.create_all()` no se usa como mecanismo de esquema.
- React/Vite con pantallas V1: conocimiento, preferencias, perfil, scoring, editor, laboratorio, comparador, reglas, persistencia, Cerebro, aceptacion, cierre, roadmap, pantallas y auditoria.
- SQLAlchemy y Alembic con modelos persistentes para perfiles, preferencias, variables, evidencias, comparaciones, feedback, textos generados y eventos.
- Pipeline de conocimiento persistente e inspeccionable: fuentes, ediciones de fuente, nodos, evidencias, claims, fichas, version, consulta, historial y validacion auditada.
- Catalogo cerrado de 23 fuentes V1 registrado en `/knowledge/sources`; `POST /knowledge/sources` permite registrar una fuente persistente sin crear edicion ni publicar directamente; `POST /knowledge/sources/{source_id}/editions`, `GET /knowledge/sources/{source_id}/editions` y `GET /knowledge/editions/{edition_id}` registran y leen ediciones bibliograficas sin iniciar lote de ingestion ni publicacion; `POST /knowledge/editions/{edition_id}/index`, `GET /knowledge/editions/{edition_id}/index` y `GET /knowledge/index/{entry_id}` registran y leen un indice documental jerarquico sin crear nodos ni conocimiento; `POST /knowledge/index/{entry_id}/segments`, `GET /knowledge/index/{entry_id}/segments` y `GET /knowledge/segments/{segment_id}` registran segmentos textuales ordenados y localizados sin interpretar, resumir, crear embeddings, nodos ni conocimiento; `POST /knowledge/segments/{segment_id}/extractions`, `GET /knowledge/segments/{segment_id}/extractions` y `GET /knowledge/extractions/{extraction_id}` registran ejecuciones de extraccion auditables; `POST /knowledge/extractions/{extraction_id}/proposals`, `GET /knowledge/extractions/{extraction_id}/proposals`, `GET /knowledge/proposals/{proposal_id}`, `POST /knowledge/proposals/{proposal_id}/approve` y `POST /knowledge/proposals/{proposal_id}/reject` registran y revisan conocimiento candidato sin publicarlo directamente.
- Evidencias V1 como objetos documentales trazables en `/knowledge/evidence`: fuente, edicion, nodo, tipo, localizador, contexto, confianza, estado e historial de revision.
- Claims V1 como afirmaciones documentales en `/knowledge/claims`: tipo, nodo, dominio, alcance, estado, origen, enlaces de evidencia y revision.
- Relaciones V1 como grafo tipado en `/knowledge/relations`: origen, destino, tipo, direccion, cardinalidad, peso, confianza, contexto, estado y version.
- Versionado V1 en `/knowledge/versioning`, `/knowledge/versions` y `/knowledge/revisions`: revisiones historicas inmutables y snapshots persistidos por `knowledge_version` para fuentes, ediciones, nodos, relaciones, evidencias, claims, fichas, arbol, ontologia, esquemas y versiones de conocimiento; perfil/preferencias/scoring/eventos temporales quedan fuera del conocimiento estable.
- Publicacion V1 en `/knowledge/publication`, `/knowledge/publication/readiness`, `POST /knowledge/candidates` y `POST /knowledge/publications`: publicar significa convertir una `knowledge_version` candidata completa en conocimiento estable recuperable. El candidato congela un snapshot real con objetos validados/publicados; la publicacion activa ese snapshot, promueve sus nodos/evidencias/claims/relaciones a `published` y registra auditoria. No hay publicaciones parciales y una version publicada solo puede deprecarse o archivarse mediante una version posterior.
- Ingestion V1 en `/knowledge/ingestion`, `/knowledge/ingestion/batches` y `/knowledge/ingestion/readiness`: cualquier obra debe poder seguir el recorrido fuente-edicion-indice-segmentacion-extraccion-nodos-evidencias-claims-fichas-validacion-version candidata-publicacion; nunca publica directamente y se bloquea si falta edicion, localizador, derechos o integridad.
- Consulta V1 en `/knowledge/query/contract` y `/knowledge/query/interpretation`: define que una consulta es lectura contra conocimiento estable, normaliza texto, resuelve version, declara tipo/dominio, restricciones y contexto sin mutar perfil ni conocimiento.
- Recuperacion V1 en `/knowledge/query`: usa la interpretacion de consulta, lee contra el snapshot de version y recupera solo objetos `published`; conserva claims/evidencias/fuentes, limita relaciones, desglosa ranking y devuelve traza reproducible sin mezclar perfil y conocimiento.
- Perfil exportable mediante `GET /profiles/{profile_id}/export`, con preferencias, evidencias, variables por contexto, estadisticas y contradicciones sin incluir la base de conocimiento.
- Observabilidad V1 disponible desde auditoria: tiempos de interpretacion/generacion, calidad de recuperacion por validacion pendiente, scoring, comparaciones y feedback.
- Auditoria de Cerebro declarativa: no se importa ningun modulo completo sin evidencia pieza por pieza.
- Cierre V1 documentado en `docs/CIERRE_PLAN_V1.md`.
- Tests unitarios/API del scoring, comparador, persistencia, feedback, aceptacion, observabilidad, conocimiento y cierre.

`pgvector`, validacion editorial avanzada e ingestion bibliografica completa no forman parte del cierre V1. No hay V2 planificada; cualquier cambio posterior queda limitado a mantenimiento o refinamiento dentro del contrato V1.

El campo `gaps` de `GET /knowledge/status` se mantiene por compatibilidad, pero sus valores representan elementos fuera de alcance V1, no tareas pendientes del cierre.

## Validacion

```bash
make validate
make migrate-sqlite
make migrate-postgres
```

Limpieza de artefactos generados locales:

```bash
make clean-generated
```

Smokes UI contra una instancia real de frontend/backend:

```bash
FRONTEND_URL=http://127.0.0.1:5173 make smoke-ui
```

Endpoints de cierre:

- `GET /acceptance/v1`
- `GET /closure/conditions`
- `GET /closure/technical`
- `GET /contract/boundaries`
- `GET /profiles/default/export`
