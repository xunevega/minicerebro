# Knowledge catalog runtime boundary

`catalog.py` contains the static catalog used to build and export the published
knowledge snapshot.

`service.py` contains runtime policies, query interpretation, retrieval scoring,
publication readiness checks, and the knowledge gym.

Application runtime must read published knowledge from the database seeded by
Alembic data migrations. Request handlers must not call the static seed catalog
to answer normal API requests.

The expected flow is:

1. Update `catalog.py` only when preparing a new published knowledge version.
2. Export the immutable snapshot.
3. Store that snapshot through an Alembic data migration.
4. Serve runtime requests from persisted records.

Snapshot files live in `data/` and are loaded through `snapshot_data.py`, so
data migrations and scripts share the same format checks.

`legacy_seed.py` is only the explicit fallback used when
`MINICEREBRO_ALLOW_LEGACY_KNOWLEDGE_SEED=1`; normal application startup should
not use it once Alembic data migrations have loaded the published snapshot.
