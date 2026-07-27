"""seed knowledge v51 snapshot

Revision ID: 20260728_0022
Revises: 20260723_0021
Create Date: 2026-07-28
"""
from __future__ import annotations

from collections.abc import Sequence
import json
from pathlib import Path
from typing import Any

from alembic import op
import sqlalchemy as sa

revision: str = "20260728_0022"
down_revision: str | None = "20260723_0021"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SNAPSHOT_VERSION = "knowledge-v51"
SNAPSHOT_PATH = (
    Path(__file__).resolve().parents[2]
    / "app"
    / "knowledge"
    / "data"
    / f"{SNAPSHOT_VERSION}.snapshot.json"
)


def upgrade() -> None:
    snapshot = _load_snapshot()
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


def _load_snapshot() -> dict[str, Any]:
    payload = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    if payload["format"] != "knowledge-seed-snapshot-v1":
        raise RuntimeError(f"unexpected knowledge snapshot format: {payload['format']}")
    if payload["version"] != SNAPSHOT_VERSION:
        raise RuntimeError(f"unexpected knowledge snapshot version: {payload['version']}")
    return payload
