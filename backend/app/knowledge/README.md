# Knowledge catalog runtime boundary

`catalog.py` is a compact legacy adapter over the published knowledge snapshot.
It preserves the old `seed_*` API for tests and explicit fallback paths, but it
does not contain the full hardcoded catalog anymore.

`service.py` contains runtime policies, query interpretation, retrieval scoring,
publication readiness checks, and the knowledge gym.

Application runtime must read published knowledge from the database seeded by
Alembic data migrations. Request handlers must not call the static seed catalog
to answer normal API requests.

The expected flow is:

1. Build or export the immutable snapshot for the new published version.
2. Store that snapshot through an Alembic data migration.
3. Serve runtime requests from persisted records.

Snapshot files live in `data/` and are loaded through `snapshot_data.py`, so
data migrations and scripts share the same format checks.

`legacy_seed.py` is only the explicit fallback used when
`MINICEREBRO_ALLOW_LEGACY_KNOWLEDGE_SEED=1`; it imports the same snapshot data
as the Alembic migration. Normal application startup should not use it once
Alembic data migrations have loaded the published snapshot.
