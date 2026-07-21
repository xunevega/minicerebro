"""knowledge pipeline

Revision ID: 20260721_0004
Revises: 20260721_0003
Create Date: 2026-07-21
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260721_0004"
down_revision: str | None = "20260721_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "knowledge_versions",
        sa.Column("id", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("published_at", sa.String(length=80), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_knowledge_versions_status", "knowledge_versions", ["status"])

    op.create_table(
        "knowledge_sources",
        sa.Column("id", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=240), nullable=False),
        sa.Column("source_type", sa.String(length=80), nullable=False),
        sa.Column("authority_level", sa.Integer(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_knowledge_sources_source_type", "knowledge_sources", ["source_type"])
    op.create_index("ix_knowledge_sources_status", "knowledge_sources", ["status"])

    op.create_table(
        "knowledge_nodes",
        sa.Column("id", sa.String(length=80), nullable=False),
        sa.Column("source_id", sa.String(length=80), nullable=False),
        sa.Column("node_type", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("version", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["knowledge_sources.id"]),
        sa.ForeignKeyConstraint(["version"], ["knowledge_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_knowledge_nodes_node_type", "knowledge_nodes", ["node_type"])

    op.create_table(
        "knowledge_cards",
        sa.Column("id", sa.String(length=80), nullable=False),
        sa.Column("card_type", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=240), nullable=False),
        sa.Column("definition", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("version", sa.String(length=80), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["version"], ["knowledge_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_knowledge_cards_card_type", "knowledge_cards", ["card_type"])

    op.create_table(
        "knowledge_evidence_items",
        sa.Column("id", sa.String(length=80), nullable=False),
        sa.Column("node_id", sa.String(length=80), nullable=False),
        sa.Column("source_id", sa.String(length=80), nullable=False),
        sa.Column("reference", sa.String(length=240), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("version", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["node_id"], ["knowledge_nodes.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["knowledge_sources.id"]),
        sa.ForeignKeyConstraint(["version"], ["knowledge_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "knowledge_claims",
        sa.Column("id", sa.String(length=80), nullable=False),
        sa.Column("evidence_id", sa.String(length=80), nullable=False),
        sa.Column("card_id", sa.String(length=80), nullable=False),
        sa.Column("statement", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("version", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["card_id"], ["knowledge_cards.id"]),
        sa.ForeignKeyConstraint(["evidence_id"], ["knowledge_evidence_items.id"]),
        sa.ForeignKeyConstraint(["version"], ["knowledge_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("knowledge_claims")
    op.drop_table("knowledge_evidence_items")
    op.drop_index("ix_knowledge_cards_card_type", table_name="knowledge_cards")
    op.drop_table("knowledge_cards")
    op.drop_index("ix_knowledge_nodes_node_type", table_name="knowledge_nodes")
    op.drop_table("knowledge_nodes")
    op.drop_index("ix_knowledge_sources_status", table_name="knowledge_sources")
    op.drop_index("ix_knowledge_sources_source_type", table_name="knowledge_sources")
    op.drop_table("knowledge_sources")
    op.drop_index("ix_knowledge_versions_status", table_name="knowledge_versions")
    op.drop_table("knowledge_versions")
