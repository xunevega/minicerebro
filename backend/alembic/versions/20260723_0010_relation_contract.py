"""relation contract

Revision ID: 20260723_0010
Revises: 20260722_0009
Create Date: 2026-07-23
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260723_0010"
down_revision: str | None = "20260722_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "knowledge_node_relations",
        sa.Column("direction", sa.String(length=40), nullable=False, server_default="outgoing"),
    )
    op.add_column(
        "knowledge_node_relations",
        sa.Column("cardinality", sa.String(length=20), nullable=False, server_default="N:N"),
    )
    op.add_column(
        "knowledge_node_relations",
        sa.Column("weight", sa.Float(), nullable=False, server_default="1.0"),
    )
    op.add_column(
        "knowledge_node_relations",
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.5"),
    )
    op.add_column(
        "knowledge_node_relations",
        sa.Column("context", sa.String(length=160), nullable=False, server_default="knowledge_graph"),
    )
    op.add_column(
        "knowledge_node_relations",
        sa.Column("status", sa.String(length=40), nullable=False, server_default="published"),
    )
    op.add_column(
        "knowledge_node_relations",
        sa.Column("updated_at", sa.String(length=80), nullable=False, server_default="2026-07-23"),
    )
    op.create_index(
        "ix_knowledge_node_relations_context",
        "knowledge_node_relations",
        ["context"],
    )
    op.create_index(
        "ix_knowledge_node_relations_status",
        "knowledge_node_relations",
        ["status"],
    )

    op.create_table(
        "knowledge_relations",
        sa.Column("id", sa.String(length=160), nullable=False),
        sa.Column("source_entity_type", sa.String(length=80), nullable=False),
        sa.Column("source_entity_id", sa.String(length=160), nullable=False),
        sa.Column("target_entity_type", sa.String(length=80), nullable=False),
        sa.Column("target_entity_id", sa.String(length=160), nullable=False),
        sa.Column("relation_type", sa.String(length=80), nullable=False),
        sa.Column("direction", sa.String(length=40), nullable=False),
        sa.Column("cardinality", sa.String(length=20), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("context", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("version", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.String(length=80), nullable=False),
        sa.Column("updated_at", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["version"], ["knowledge_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_knowledge_relations_source_entity_type",
        "knowledge_relations",
        ["source_entity_type"],
    )
    op.create_index(
        "ix_knowledge_relations_source_entity_id",
        "knowledge_relations",
        ["source_entity_id"],
    )
    op.create_index(
        "ix_knowledge_relations_target_entity_type",
        "knowledge_relations",
        ["target_entity_type"],
    )
    op.create_index(
        "ix_knowledge_relations_target_entity_id",
        "knowledge_relations",
        ["target_entity_id"],
    )
    op.create_index(
        "ix_knowledge_relations_relation_type",
        "knowledge_relations",
        ["relation_type"],
    )
    op.create_index("ix_knowledge_relations_context", "knowledge_relations", ["context"])
    op.create_index("ix_knowledge_relations_status", "knowledge_relations", ["status"])


def downgrade() -> None:
    op.drop_index("ix_knowledge_relations_status", table_name="knowledge_relations")
    op.drop_index("ix_knowledge_relations_context", table_name="knowledge_relations")
    op.drop_index("ix_knowledge_relations_relation_type", table_name="knowledge_relations")
    op.drop_index("ix_knowledge_relations_target_entity_id", table_name="knowledge_relations")
    op.drop_index("ix_knowledge_relations_target_entity_type", table_name="knowledge_relations")
    op.drop_index("ix_knowledge_relations_source_entity_id", table_name="knowledge_relations")
    op.drop_index("ix_knowledge_relations_source_entity_type", table_name="knowledge_relations")
    op.drop_table("knowledge_relations")
    op.drop_index("ix_knowledge_node_relations_status", table_name="knowledge_node_relations")
    op.drop_index("ix_knowledge_node_relations_context", table_name="knowledge_node_relations")
    op.drop_column("knowledge_node_relations", "updated_at")
    op.drop_column("knowledge_node_relations", "status")
    op.drop_column("knowledge_node_relations", "context")
    op.drop_column("knowledge_node_relations", "confidence")
    op.drop_column("knowledge_node_relations", "weight")
    op.drop_column("knowledge_node_relations", "cardinality")
    op.drop_column("knowledge_node_relations", "direction")
