"""knowledge proposals

Revision ID: 20260723_0019
Revises: 20260723_0018
Create Date: 2026-07-23
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260723_0019"
down_revision: str | None = "20260723_0018"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "knowledge_proposals",
        sa.Column("id", sa.String(length=180), nullable=False),
        sa.Column("extraction_id", sa.String(length=180), nullable=False),
        sa.Column("segment_id", sa.String(length=180), nullable=False),
        sa.Column("proposal_type", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("title", sa.String(length=320), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("source_locator", sa.String(length=240), nullable=False),
        sa.Column("created_at", sa.String(length=80), nullable=False),
        sa.Column("updated_at", sa.String(length=80), nullable=False),
        sa.Column("reviewed_at", sa.String(length=80), nullable=True),
        sa.Column("reviewer", sa.String(length=120), nullable=True),
        sa.Column("decision_reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["extraction_id"], ["knowledge_extraction_runs.id"]),
        sa.ForeignKeyConstraint(["segment_id"], ["knowledge_segments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_knowledge_proposals_extraction_id",
        "knowledge_proposals",
        ["extraction_id"],
    )
    op.create_index("ix_knowledge_proposals_segment_id", "knowledge_proposals", ["segment_id"])
    op.create_index("ix_knowledge_proposals_status", "knowledge_proposals", ["status"])
    op.create_index(
        "ix_knowledge_proposals_proposal_type",
        "knowledge_proposals",
        ["proposal_type"],
    )


def downgrade() -> None:
    op.drop_index("ix_knowledge_proposals_proposal_type", table_name="knowledge_proposals")
    op.drop_index("ix_knowledge_proposals_status", table_name="knowledge_proposals")
    op.drop_index("ix_knowledge_proposals_segment_id", table_name="knowledge_proposals")
    op.drop_index("ix_knowledge_proposals_extraction_id", table_name="knowledge_proposals")
    op.drop_table("knowledge_proposals")
