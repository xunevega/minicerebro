"""segments

Revision ID: 20260723_0017
Revises: 20260723_0016
Create Date: 2026-07-23
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260723_0017"
down_revision: str | None = "20260723_0016"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "knowledge_segments",
        sa.Column("id", sa.String(length=180), nullable=False),
        sa.Column("index_entry_id", sa.String(length=160), nullable=False),
        sa.Column("parent_segment_id", sa.String(length=180), nullable=True),
        sa.Column("segment_type", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=320), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("segment_order", sa.Integer(), nullable=False),
        sa.Column("start_locator", sa.String(length=240), nullable=False),
        sa.Column("end_locator", sa.String(length=240), nullable=False),
        sa.Column("language", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.String(length=80), nullable=False),
        sa.Column("updated_at", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["index_entry_id"], ["knowledge_index_entries.id"]),
        sa.ForeignKeyConstraint(["parent_segment_id"], ["knowledge_segments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_knowledge_segments_index_entry_id", "knowledge_segments", ["index_entry_id"])
    op.create_index(
        "ix_knowledge_segments_parent_segment_id",
        "knowledge_segments",
        ["parent_segment_id"],
    )
    op.create_index("ix_knowledge_segments_status", "knowledge_segments", ["status"])


def downgrade() -> None:
    op.drop_index("ix_knowledge_segments_status", table_name="knowledge_segments")
    op.drop_index("ix_knowledge_segments_parent_segment_id", table_name="knowledge_segments")
    op.drop_index("ix_knowledge_segments_index_entry_id", table_name="knowledge_segments")
    op.drop_table("knowledge_segments")
