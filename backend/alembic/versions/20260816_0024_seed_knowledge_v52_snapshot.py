"""seed knowledge v52 Spanish writing batch

Revision ID: 20260816_0024
Revises: 20260816_0023
Create Date: 2026-08-16
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

from app.knowledge.snapshot_data import load_knowledge_seed_snapshot

revision: str = "20260816_0024"
down_revision: str | None = "20260816_0023"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SNAPSHOT_VERSION = "knowledge-v52"
TABLE_ORDER = (
    "knowledge_versions",
    "knowledge_sources",
    "knowledge_source_editions",
    "knowledge_ingestion_batches",
    "knowledge_nodes",
    "knowledge_cards",
    "knowledge_evidence_items",
    "knowledge_claims",
    "knowledge_claim_evidence_links",
    "knowledge_claim_revisions",
    "knowledge_evidence_revisions",
    "knowledge_object_revisions",
    "knowledge_relations",
    "knowledge_node_relations",
    "knowledge_version_snapshots",
)


def upgrade() -> None:
    snapshot = load_knowledge_seed_snapshot(SNAPSHOT_VERSION)
    bind = op.get_bind()
    metadata = sa.MetaData()
    tables = snapshot["tables"]
    for table_name in TABLE_ORDER:
        rows = tables.get(table_name) or []
        if not rows:
            continue
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
    return
