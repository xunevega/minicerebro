"""generated texts

Revision ID: 20260721_0003
Revises: 20260721_0002
Create Date: 2026-07-21
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260721_0003"
down_revision: str | None = "20260721_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "generated_texts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("profile_id", sa.String(length=80), nullable=False),
        sa.Column("context", sa.String(length=120), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("output_text", sa.Text(), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("used_profile_variables", sa.JSON(), nullable=False),
        sa.Column("learning_applied", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_generated_texts_context", "generated_texts", ["context"])
    op.create_index("ix_generated_texts_profile_id", "generated_texts", ["profile_id"])


def downgrade() -> None:
    op.drop_index("ix_generated_texts_profile_id", table_name="generated_texts")
    op.drop_index("ix_generated_texts_context", table_name="generated_texts")
    op.drop_table("generated_texts")
