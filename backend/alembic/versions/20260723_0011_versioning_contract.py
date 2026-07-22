"""versioning contract

Revision ID: 20260723_0011
Revises: 20260723_0010
Create Date: 2026-07-23
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260723_0011"
down_revision: str | None = "20260723_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "knowledge_object_revisions",
        sa.Column("id", sa.String(length=260), nullable=False),
        sa.Column("object_type", sa.String(length=80), nullable=False),
        sa.Column("object_id", sa.String(length=180), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("object_version", sa.String(length=180), nullable=False),
        sa.Column("knowledge_version", sa.String(length=80), nullable=False),
        sa.Column("author", sa.String(length=120), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("before", sa.JSON(), nullable=False),
        sa.Column("after", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["knowledge_version"], ["knowledge_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_knowledge_object_revisions_object_type",
        "knowledge_object_revisions",
        ["object_type"],
    )
    op.create_index(
        "ix_knowledge_object_revisions_object_id",
        "knowledge_object_revisions",
        ["object_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_knowledge_object_revisions_object_id",
        table_name="knowledge_object_revisions",
    )
    op.drop_index(
        "ix_knowledge_object_revisions_object_type",
        table_name="knowledge_object_revisions",
    )
    op.drop_table("knowledge_object_revisions")
