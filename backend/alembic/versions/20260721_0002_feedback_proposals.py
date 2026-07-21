"""feedback proposals

Revision ID: 20260721_0002
Revises: 20260721_0001
Create Date: 2026-07-21
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260721_0002"
down_revision: str | None = "20260721_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "feedback_proposals",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("comparison_id", sa.String(length=36), nullable=False),
        sa.Column("profile_id", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("context", sa.String(length=120), nullable=False),
        sa.Column("items", sa.JSON(), nullable=False),
        sa.Column("rationale", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["comparison_id"], ["comparisons.id"]),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_feedback_proposals_comparison_id", "feedback_proposals", ["comparison_id"])
    op.create_index("ix_feedback_proposals_profile_id", "feedback_proposals", ["profile_id"])
    op.create_index("ix_feedback_proposals_status", "feedback_proposals", ["status"])


def downgrade() -> None:
    op.drop_index("ix_feedback_proposals_status", table_name="feedback_proposals")
    op.drop_index("ix_feedback_proposals_profile_id", table_name="feedback_proposals")
    op.drop_index("ix_feedback_proposals_comparison_id", table_name="feedback_proposals")
    op.drop_table("feedback_proposals")
