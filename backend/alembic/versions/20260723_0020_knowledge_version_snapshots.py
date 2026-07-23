"""knowledge version snapshots

Revision ID: 20260723_0020
Revises: 20260723_0019
Create Date: 2026-07-23
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260723_0020"
down_revision: str | None = "20260723_0019"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "knowledge_version_snapshots",
        sa.Column("version_id", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("source_ids", sa.JSON(), nullable=False),
        sa.Column("source_edition_ids", sa.JSON(), nullable=False),
        sa.Column("node_ids", sa.JSON(), nullable=False),
        sa.Column("node_relation_ids", sa.JSON(), nullable=False),
        sa.Column("relation_ids", sa.JSON(), nullable=False),
        sa.Column("evidence_ids", sa.JSON(), nullable=False),
        sa.Column("claim_ids", sa.JSON(), nullable=False),
        sa.Column("claim_evidence_link_ids", sa.JSON(), nullable=False),
        sa.Column("card_ids", sa.JSON(), nullable=False),
        sa.Column("revision_ids", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.String(length=80), nullable=False),
        sa.Column("updated_at", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["version_id"], ["knowledge_versions.id"]),
        sa.PrimaryKeyConstraint("version_id"),
    )
    op.create_index(
        "ix_knowledge_version_snapshots_status",
        "knowledge_version_snapshots",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index("ix_knowledge_version_snapshots_status", table_name="knowledge_version_snapshots")
    op.drop_table("knowledge_version_snapshots")
