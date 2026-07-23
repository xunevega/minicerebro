"""ingestion contract

Revision ID: 20260723_0014
Revises: 20260723_0013
Create Date: 2026-07-23
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260723_0014"
down_revision: str | None = "20260723_0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "knowledge_ingestion_batches",
        sa.Column("id", sa.String(length=160), nullable=False),
        sa.Column("source_id", sa.String(length=80), nullable=False),
        sa.Column("source_edition_id", sa.String(length=120), nullable=False),
        sa.Column("batch_label", sa.String(length=160), nullable=False),
        sa.Column("scope", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("author", sa.String(length=120), nullable=False),
        sa.Column("tools", sa.JSON(), nullable=False),
        sa.Column("model_used", sa.String(length=120), nullable=True),
        sa.Column("configuration", sa.JSON(), nullable=False),
        sa.Column("progress", sa.JSON(), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("decisions", sa.JSON(), nullable=False),
        sa.Column("blockers", sa.JSON(), nullable=False),
        sa.Column("result", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.String(length=80), nullable=False),
        sa.Column("updated_at", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["knowledge_sources.id"]),
        sa.ForeignKeyConstraint(["source_edition_id"], ["knowledge_source_editions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_knowledge_ingestion_batches_source_id",
        "knowledge_ingestion_batches",
        ["source_id"],
    )
    op.create_index(
        "ix_knowledge_ingestion_batches_source_edition_id",
        "knowledge_ingestion_batches",
        ["source_edition_id"],
    )
    op.create_index(
        "ix_knowledge_ingestion_batches_status",
        "knowledge_ingestion_batches",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index("ix_knowledge_ingestion_batches_status", table_name="knowledge_ingestion_batches")
    op.drop_index(
        "ix_knowledge_ingestion_batches_source_edition_id",
        table_name="knowledge_ingestion_batches",
    )
    op.drop_index("ix_knowledge_ingestion_batches_source_id", table_name="knowledge_ingestion_batches")
    op.drop_table("knowledge_ingestion_batches")
