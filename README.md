# Editados

Aplicacion especializada en escritura en lengua espanola. La V1 implementa el contrato funcional con conocimiento estable separado del perfil de preferencias, scoring editable, preferencias trazables, editor, comparador, laboratorio, feedback controlado, auditoria y cierre tecnico verificable.

## Limite de seguridad V1

Editados V1 es una aplicacion local-first para desarrollo y uso en localhost. No debe exponerse a internet, dominios publicos ni redes abiertas sin anadir antes:

- autenticacion;
- secretos propios fuera de los valores de desarrollo;
- CORS de produccion;
- rate limiting, especialmente para `/generation`, `/correction`, `/rewrite`, `/continue` y `/variants`.

El `docker-compose.yml` liga PostgreSQL a `127.0.0.1` y usa credenciales de desarrollo. Son aceptables solo para entorno local.

El estado declarativo de estos limites se puede consultar en `GET /security/status`.

## Desarrollo local

Backend:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e "backend[dev]"
cd backend
../.venv/bin/alembic upgrade head
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

## Railway backend

El repositorio incluye un `Dockerfile` para desplegar el backend FastAPI en Railway desde la raiz del repo.

Variables necesarias en el servicio backend:

```bash
DATABASE_URL=postgresql://...
CORS_ALLOW_ORIGINS=https://<tu-frontend>.up.railway.app
```

Variable opcional para generacion real:

```bash
OPENAI_API_KEY=...
```

El contenedor ejecuta:

```bash
alembic upgrade head
python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

En Railway, genera el dominio del servicio apuntando al puerto `8000` y verifica:

```text
https://<tu-dominio>.up.railway.app/health
```

## Railway frontend

El frontend se despliega como un servicio Railway separado con `Root Directory` apuntando a `frontend`.
Railway debe autodetectar la app Vite con Railpack; no se fuerza `railway.json` para evitar builds con una version de Node incompatible con Vite.

Variables necesarias en el servicio frontend:

```bash
VITE_API_BASE=https://<tu-backend>.up.railway.app
```

Configuracion esperada:

```text
Root Directory: frontend
Pre-deploy command: vacio
Custom Start Command: vacio
```

Tras cada bloque fuerte de cambios, verificar en produccion:

```bash
curl https://<backend>.up.railway.app/health
curl https://<backend>.up.railway.app/knowledge/status
curl -X POST https://<backend>.up.railway.app/knowledge/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"tema estructura externa interna forma contenido comentario critico texto literario","version":"latest","limit":3}'
```

Con los dominios actuales de Railway tambien puede ejecutarse:

```bash
make smoke-production
```

## Estado de esta base

- FastAPI con endpoints del contrato V1 y superficies de cierre.
- `knowledge-v40` es la version publicada actual; acumula `knowledge-v8` (Gramatica Practica, Parte 2), `knowledge-v9` (Ortografia y Puntuacion), `knowledge-v10` (Estilo Editorial), `knowledge-v11` (Redaccion aplicada), `knowledge-v12` (Ortotipografia aplicada), `knowledge-v13` (Comentario de texto), `knowledge-v14` (Retorica y argumentacion), `knowledge-v15` (Construccion del discurso), `knowledge-v16` (Comunicacion oral practica), `knowledge-v17` (Teoria literaria clasica), `knowledge-v18` (Narratologia), `knowledge-v19` (Teoria literaria general), `knowledge-v20` (Narratologia aplicada), `knowledge-v21` (Linguistica general), `knowledge-v22` (Corpus y uso documentado), `knowledge-v23` (Sintaxis generativa), `knowledge-v24` (Estilo editorial anglosajon), `knowledge-v25` (Escritura de no ficcion), `knowledge-v26` (Sinonimos y antonimos), `knowledge-v27` (Diccionarios de uso e idea dada), `knowledge-v28` (Redaccion pragmatica y estilistica moderna), `knowledge-v29` (Puntuacion y correccion de estilo avanzada), `knowledge-v30` (Narratologia y creatividad practica aplicadas), `knowledge-v31` (Practica creativa de escena), `knowledge-v32` (Practica creativa de revision), `knowledge-v33` (Precision lexica aplicada), `knowledge-v34` (Sinonimia y eleccion lexica aplicada), `knowledge-v35` (Claridad de frase aplicada), `knowledge-v36` (Progresion de parrafo aplicada), `knowledge-v37` (Tono y registro aplicado), `knowledge-v38` (Argumentacion practica), `knowledge-v39` (Diagnostico de revision) y `knowledge-v40` (Revision aplicada por capas).
- Migraciones Alembic explicitas antes del arranque; `Base.metadata.create_all()` no se usa como mecanismo de esquema y la app no ejecuta migraciones durante el startup.
- React/Vite con navegacion V1 simplificada: `Escribir`, `Aprender de mi`, `Biblioteca`, `Historial` y `Sistema`. La jerga tecnica de conocimiento queda plegada en paneles tecnicos; la Biblioteca normal muestra estanterias, fichas editoriales y consulta contra la base publicada.
- SQLAlchemy y Alembic con modelos persistentes para perfiles, preferencias, variables, evidencias, comparaciones, feedback, textos generados y eventos.
- Pipeline de conocimiento persistente e inspeccionable: fuentes, ediciones de fuente, nodos, evidencias, claims, fichas, version, consulta, historial y validacion auditada.
- Catalogo cerrado de 26 fuentes V1 registrado en `/knowledge/sources`; `POST /knowledge/sources` permite registrar una fuente persistente sin crear edicion ni publicar directamente; `POST /knowledge/sources/{source_id}/editions`, `GET /knowledge/sources/{source_id}/editions` y `GET /knowledge/editions/{edition_id}` registran y leen ediciones bibliograficas sin iniciar lote de ingestion ni publicacion; `POST /knowledge/editions/{edition_id}/index`, `GET /knowledge/editions/{edition_id}/index` y `GET /knowledge/index/{entry_id}` registran y leen un indice documental jerarquico sin crear nodos ni conocimiento; `POST /knowledge/index/{entry_id}/segments`, `GET /knowledge/index/{entry_id}/segments` y `GET /knowledge/segments/{segment_id}` registran segmentos textuales ordenados y localizados sin interpretar, resumir, crear embeddings, nodos ni conocimiento; `POST /knowledge/segments/{segment_id}/extractions`, `GET /knowledge/segments/{segment_id}/extractions` y `GET /knowledge/extractions/{extraction_id}` registran ejecuciones de extraccion auditables; `POST /knowledge/extractions/{extraction_id}/proposals`, `GET /knowledge/extractions/{extraction_id}/proposals`, `GET /knowledge/proposals/{proposal_id}`, `POST /knowledge/proposals/{proposal_id}/approve` y `POST /knowledge/proposals/{proposal_id}/reject` registran y revisan conocimiento candidato sin publicarlo directamente.
- Evidencias V1 como objetos documentales trazables en `/knowledge/evidence`: fuente, edicion, nodo, tipo, localizador, contexto, confianza, estado e historial de revision.
- Claims V1 como afirmaciones documentales en `/knowledge/claims`: tipo, nodo, dominio, alcance, estado, origen, enlaces de evidencia y revision.
- Relaciones V1 como grafo tipado en `/knowledge/relations`: origen, destino, tipo, direccion, cardinalidad, peso, confianza, contexto, estado y version.
- Versionado V1 en `/knowledge/versioning`, `/knowledge/versions` y `/knowledge/revisions`: revisiones historicas inmutables y snapshots persistidos por `knowledge_version` para fuentes, ediciones, nodos, relaciones, evidencias, claims, fichas, arbol, ontologia, esquemas y versiones de conocimiento; perfil/preferencias/scoring/eventos temporales quedan fuera del conocimiento estable.
- Publicacion V1 en `/knowledge/publication`, `/knowledge/publication/readiness`, `POST /knowledge/candidates` y `POST /knowledge/publications`: publicar significa convertir una `knowledge_version` candidata completa en conocimiento estable recuperable. El candidato congela un snapshot real con objetos validados/publicados; la publicacion activa ese snapshot, promueve sus nodos/evidencias/claims/relaciones a `published` y registra auditoria. No hay publicaciones parciales y una version publicada solo puede deprecarse o archivarse mediante una version posterior.
- Ingestion V1 en `/knowledge/ingestion`, `/knowledge/ingestion/batches` y `/knowledge/ingestion/readiness`: cualquier obra debe poder seguir el recorrido fuente-edicion-indice-segmentacion-extraccion-nodos-evidencias-claims-fichas-validacion-version candidata-publicacion; nunca publica directamente y se bloquea si falta edicion, localizador, derechos o integridad.
- Consulta V1 en `/knowledge/query/contract` y `/knowledge/query/interpretation`: define que una consulta es lectura contra conocimiento estable, normaliza texto, resuelve version, declara tipo/dominio, restricciones y contexto sin mutar perfil ni conocimiento.
- Recuperacion V1 en `/knowledge/query`: usa la interpretacion de consulta, lee contra el snapshot de version y recupera solo objetos `published`; conserva claims/evidencias/fuentes, limita relaciones, desglosa ranking y devuelve traza reproducible sin mezclar perfil y conocimiento.
- Revision editorial en `POST /revision` y `POST /profiles/{profile_id}/revision`: aplica la ruta diagnostico-estructura-parrafo-frase-tono-limpieza sobre un texto concreto sin generar conocimiento, sin mutar perfil y sin guardar el texto crudo en auditoria. El feedback de una recomendacion se registra en `POST /revision/feedback/{card_id}` o `POST /profiles/{profile_id}/revision-feedback/{card_id}` como ficha personal y propuesta revisable de scoring, nunca como cambio de conocimiento estable.
- Calidad de la base en `GET /knowledge/gym`: ejecuta diagnosticos deterministas sobre la version publicada (`latest` por defecto) para medir precision de recuperacion, diversidad, trazabilidad, utilidad de fichas, redundancia y dieta general sin crear propuestas, nodos, claims, fichas ni eventos de usuario.
- Perfil exportable mediante `GET /profiles/{profile_id}/export`, con preferencias, evidencias, variables por contexto, estadisticas, contradicciones y fichas de usuario sin incluir la base de conocimiento.
- Ficha editorial y ficha de usuario en `GET /profiles/{profile_id}/editorial-card`, `GET/POST /profiles/{profile_id}/knowledge-cards/{card_id}` y `GET /profiles/{profile_id}/knowledge-cards`: la Biblioteca muestra cada ficha como ayuda editorial con uso, materia, nivel, senales, riesgos y fuentes; la ficha de usuario guarda feedback, score personal, elementos que mantiene y cambios que pide sin modificar la `KnowledgeCard` publicada ni el snapshot estable. `GET/POST .../score-proposal` convierte esa ficha personal en propuesta revisable de scoring del perfil.
- Observabilidad V1 disponible desde auditoria: tiempos de interpretacion/generacion, calidad de recuperacion por validacion pendiente, scoring, comparaciones y feedback.
- Auditoria de Cerebro declarativa: no se importa ningun modulo completo sin evidencia pieza por pieza.
- Cierre V1 documentado en `docs/CIERRE_PLAN_V1.md`.
- Knowledge-v6 publica el primer lote amplio de conocimiento estable sobre dequeismo/queismo, extranjerismos y unidad de criterio editorial, conservando knowledge-v5 como snapshot congelado.
- Knowledge-v7 publica el lote de gramatica practica sobre sujeto, predicado, complemento indirecto, atributo y complemento de regimen, conservando knowledge-v6 como snapshot congelado.
- Tests unitarios/API del scoring, comparador, persistencia, feedback, aceptacion, observabilidad, conocimiento y cierre.

`pgvector`, validacion editorial avanzada e ingestion bibliografica completa no forman parte del cierre V1. No hay V2 planificada; cualquier cambio posterior queda limitado a mantenimiento o refinamiento dentro del contrato V1.

El campo `gaps` de `GET /knowledge/status` se mantiene por compatibilidad, pero sus valores representan elementos fuera de alcance V1, no tareas pendientes del cierre.

## Validacion

```bash
make validate
make migrate-sqlite
make migrate-postgres
make smoke-production
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
