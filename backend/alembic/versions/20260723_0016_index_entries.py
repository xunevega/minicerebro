"""index entries

Revision ID: 20260723_0016
Revises: 20260723_0015
Create Date: 2026-07-23
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260723_0016"
down_revision: str | None = "20260723_0015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "knowledge_index_entries",
        sa.Column("id", sa.String(length=160), nullable=False),
        sa.Column("edition_id", sa.String(length=120), nullable=False),
        sa.Column("parent_id", sa.String(length=160), nullable=True),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("entry_order", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=320), nullable=False),
        sa.Column("locator", sa.String(length=240), nullable=False),
        sa.Column("page_start", sa.String(length=40), nullable=True),
        sa.Column("page_end", sa.String(length=40), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.String(length=80), nullable=False),
        sa.Column("updated_at", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["edition_id"], ["knowledge_source_editions.id"]),
        sa.ForeignKeyConstraint(["parent_id"], ["knowledge_index_entries.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_knowledge_index_entries_edition_id",
        "knowledge_index_entries",
        ["edition_id"],
    )
    op.create_index(
        "ix_knowledge_index_entries_parent_id",
        "knowledge_index_entries",
        ["parent_id"],
    )
    op.create_index(
        "ix_knowledge_index_entries_status",
        "knowledge_index_entries",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index("ix_knowledge_index_entries_status", table_name="knowledge_index_entries")
    op.drop_index("ix_knowledge_index_entries_parent_id", table_name="knowledge_index_entries")
    op.drop_index("ix_knowledge_index_entries_edition_id", table_name="knowledge_index_entries")
    op.drop_table("knowledge_index_entries")
