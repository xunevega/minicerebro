"""complete versioning contract fields

Revision ID: 20260723_0013
Revises: 20260723_0012
Create Date: 2026-07-23
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260723_0013"
down_revision: str | None = "20260723_0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("knowledge_object_revisions") as batch_op:
        batch_op.add_column(
            sa.Column("status", sa.String(length=40), nullable=False, server_default="active")
        )
        batch_op.add_column(
            sa.Column("change_type", sa.String(length=80), nullable=False, server_default="created")
        )
        batch_op.add_column(sa.Column("previous_revision", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("replaces_object_id", sa.String(length=180), nullable=True))
        batch_op.add_column(sa.Column("replaced_by_object_id", sa.String(length=180), nullable=True))
        batch_op.add_column(
            sa.Column("updated_at", sa.String(length=80), nullable=False, server_default="2026-07-23")
        )


def downgrade() -> None:
    with op.batch_alter_table("knowledge_object_revisions") as batch_op:
        batch_op.drop_column("updated_at")
        batch_op.drop_column("replaced_by_object_id")
        batch_op.drop_column("replaces_object_id")
        batch_op.drop_column("previous_revision")
        batch_op.drop_column("change_type")
        batch_op.drop_column("status")
