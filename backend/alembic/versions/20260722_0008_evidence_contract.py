"""evidence contract

Revision ID: 20260722_0008
Revises: 20260722_0007
Create Date: 2026-07-22
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260722_0008"
down_revision: str | None = "20260722_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "knowledge_evidence_items",
        sa.Column(
            "source_edition_id",
            sa.String(length=120),
            nullable=True,
        ),
    )
    op.add_column(
        "knowledge_evidence_items",
        sa.Column(
            "evidence_type",
            sa.String(length=80),
            nullable=False,
            server_default="documented_paraphrase",
        ),
    )
    op.add_column(
        "knowledge_evidence_items",
        sa.Column("locator", sa.JSON(), nullable=False, server_default="{}"),
    )
    op.add_column(
        "knowledge_evidence_items",
        sa.Column("context", sa.String(length=120), nullable=False, server_default="general_rule"),
    )
    op.add_column(
        "knowledge_evidence_items",
        sa.Column("confidence_level", sa.Integer(), nullable=False, server_default="2"),
    )
    op.add_column(
        "knowledge_evidence_items",
        sa.Column("status", sa.String(length=40), nullable=False, server_default="draft"),
    )
    op.add_column(
        "knowledge_evidence_items",
        sa.Column("created_at", sa.String(length=80), nullable=False, server_default="2026-07-22"),
    )
    op.add_column(
        "knowledge_evidence_items",
        sa.Column("updated_at", sa.String(length=80), nullable=False, server_default="2026-07-22"),
    )
    op.add_column(
        "knowledge_evidence_items",
        sa.Column(
            "incorporated_by",
            sa.String(length=120),
            nullable=False,
            server_default="minicerebro-seed",
        ),
    )
    op.add_column(
        "knowledge_evidence_items",
        sa.Column("reviewed_by", sa.String(length=120), nullable=True),
    )
    op.add_column(
        "knowledge_evidence_items",
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
    )
    op.create_index(
        "ix_knowledge_evidence_items_context",
        "knowledge_evidence_items",
        ["context"],
    )
    op.create_index(
        "ix_knowledge_evidence_items_evidence_type",
        "knowledge_evidence_items",
        ["evidence_type"],
    )
    op.create_index(
        "ix_knowledge_evidence_items_status",
        "knowledge_evidence_items",
        ["status"],
    )
    op.create_table(
        "knowledge_evidence_revisions",
        sa.Column("id", sa.String(length=120), nullable=False),
        sa.Column("evidence_id", sa.String(length=80), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("author", sa.String(length=120), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("changes", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["evidence_id"], ["knowledge_evidence_items.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("knowledge_evidence_revisions")
    op.drop_index("ix_knowledge_evidence_items_status", table_name="knowledge_evidence_items")
    op.drop_index("ix_knowledge_evidence_items_evidence_type", table_name="knowledge_evidence_items")
    op.drop_index("ix_knowledge_evidence_items_context", table_name="knowledge_evidence_items")
    op.drop_column("knowledge_evidence_items", "revision")
    op.drop_column("knowledge_evidence_items", "reviewed_by")
    op.drop_column("knowledge_evidence_items", "incorporated_by")
    op.drop_column("knowledge_evidence_items", "updated_at")
    op.drop_column("knowledge_evidence_items", "created_at")
    op.drop_column("knowledge_evidence_items", "status")
    op.drop_column("knowledge_evidence_items", "confidence_level")
    op.drop_column("knowledge_evidence_items", "context")
    op.drop_column("knowledge_evidence_items", "locator")
    op.drop_column("knowledge_evidence_items", "evidence_type")
    op.drop_column("knowledge_evidence_items", "source_edition_id")
