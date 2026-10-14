"""fichas autor

Ficha del autor por cuenta, con historial de versiones (docs/POLITICA_CONOCIMIENTO.md).

Revision ID: 20261014_0028
Revises: 20261014_0027
Create Date: 2026-10-14
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261014_0028"
down_revision: str | None = "20261014_0027"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "fichas_autor",
        sa.Column("profile_id", sa.String(length=80), sa.ForeignKey("profiles.id"), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("profile_id"),
    )
    op.create_table(
        "fichas_autor_versiones",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("profile_id", sa.String(length=80), sa.ForeignKey("profiles.id"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fichas_autor_versiones_profile_id", "fichas_autor_versiones", ["profile_id"])


def downgrade() -> None:
    op.drop_index("ix_fichas_autor_versiones_profile_id", table_name="fichas_autor_versiones")
    op.drop_table("fichas_autor_versiones")
    op.drop_table("fichas_autor")
