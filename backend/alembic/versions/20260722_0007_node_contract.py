"""node contract

Revision ID: 20260722_0007
Revises: 20260722_0006
Create Date: 2026-07-22
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260722_0007"
down_revision: str | None = "20260722_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "knowledge_nodes",
        sa.Column("canonical_name", sa.String(length=240), nullable=False, server_default="pending"),
    )
    op.add_column(
        "knowledge_nodes",
        sa.Column("primary_branch", sa.String(length=120), nullable=False, server_default="general"),
    )
    op.add_column(
        "knowledge_nodes",
        sa.Column("secondary_branch", sa.String(length=120), nullable=False, server_default="general"),
    )
    op.add_column(
        "knowledge_nodes",
        sa.Column(
            "short_definition",
            sa.String(length=320),
            nullable=False,
            server_default="pendiente",
        ),
    )
    op.add_column(
        "knowledge_nodes",
        sa.Column("long_definition", sa.Text(), nullable=False, server_default="pendiente"),
    )
    op.add_column(
        "knowledge_nodes",
        sa.Column("status", sa.String(length=40), nullable=False, server_default="published"),
    )
    op.add_column(
        "knowledge_nodes",
        sa.Column("created_at", sa.String(length=80), nullable=False, server_default="2026-07-22"),
    )
    op.add_column(
        "knowledge_nodes",
        sa.Column("published_at", sa.String(length=80), nullable=False, server_default="2026-07-22"),
    )
    op.add_column(
        "knowledge_nodes",
        sa.Column("aliases", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.create_index("ix_knowledge_nodes_primary_branch", "knowledge_nodes", ["primary_branch"])
    op.create_index("ix_knowledge_nodes_status", "knowledge_nodes", ["status"])

    op.create_table(
        "knowledge_node_relations",
        sa.Column("id", sa.String(length=120), nullable=False),
        sa.Column("source_node_id", sa.String(length=80), nullable=False),
        sa.Column("target_node_id", sa.String(length=80), nullable=False),
        sa.Column("relation_type", sa.String(length=80), nullable=False),
        sa.Column("version", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["source_node_id"], ["knowledge_nodes.id"]),
        sa.ForeignKeyConstraint(["target_node_id"], ["knowledge_nodes.id"]),
        sa.ForeignKeyConstraint(["version"], ["knowledge_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_knowledge_node_relations_relation_type",
        "knowledge_node_relations",
        ["relation_type"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_knowledge_node_relations_relation_type",
        table_name="knowledge_node_relations",
    )
    op.drop_table("knowledge_node_relations")
    op.drop_index("ix_knowledge_nodes_status", table_name="knowledge_nodes")
    op.drop_index("ix_knowledge_nodes_primary_branch", table_name="knowledge_nodes")
    op.drop_column("knowledge_nodes", "aliases")
    op.drop_column("knowledge_nodes", "published_at")
    op.drop_column("knowledge_nodes", "created_at")
    op.drop_column("knowledge_nodes", "status")
    op.drop_column("knowledge_nodes", "long_definition")
    op.drop_column("knowledge_nodes", "short_definition")
    op.drop_column("knowledge_nodes", "secondary_branch")
    op.drop_column("knowledge_nodes", "primary_branch")
    op.drop_column("knowledge_nodes", "canonical_name")
