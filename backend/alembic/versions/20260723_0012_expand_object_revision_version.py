"""expand object revision version length

Revision ID: 20260723_0012
Revises: 20260723_0011
Create Date: 2026-07-23
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260723_0012"
down_revision: str | None = "20260723_0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("knowledge_object_revisions") as batch_op:
        batch_op.alter_column(
            "object_version",
            existing_type=sa.String(length=80),
            type_=sa.String(length=180),
            existing_nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("knowledge_object_revisions") as batch_op:
        batch_op.alter_column(
            "object_version",
            existing_type=sa.String(length=180),
            type_=sa.String(length=80),
            existing_nullable=False,
        )
