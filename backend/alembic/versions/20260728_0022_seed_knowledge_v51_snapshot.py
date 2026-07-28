"""seed knowledge v51 snapshot

Revision ID: 20260728_0022
Revises: 20260723_0021
Create Date: 2026-07-28
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

from app.knowledge.snapshot_data import load_knowledge_seed_snapshot

revision: str = "20260728_0022"
down_revision: str | None = "20260723_0021"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SNAPSHOT_VERSION = "knowledge-v51"


def upgrade() -> None:
    snapshot = load_knowledge_seed_snapshot(SNAPSHOT_VERSION)
    bind = op.get_bind()
    metadata = sa.MetaData()

    for table_name, rows in snapshot["tables"].items():
        table = sa.Table(table_name, metadata, autoload_with=bind)
        primary_key = next(iter(table.primary_key.columns))
        for row in rows:
            exists = bind.execute(
                sa.select(primary_key).where(primary_key == row[primary_key.name])
            ).first()
            if exists is not None:
                continue
            bind.execute(table.insert().values(**row))


def downgrade() -> None:
    # The upgrade is idempotent and may skip rows that already existed before this migration.
    # A destructive downgrade could delete pre-existing published knowledge, so data is preserved.
    return
