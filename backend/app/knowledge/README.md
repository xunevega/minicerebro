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
