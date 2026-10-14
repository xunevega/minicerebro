"""oficio diagnosticos

Caché del diagnóstico previo de fichas con el modelo (docs/POLITICA_CONOCIMIENTO.md).

Revision ID: 20261014_0027
Revises: 20261014_0026
Create Date: 2026-10-14
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261014_0027"
down_revision: str | None = "20261014_0026"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "oficio_diagnosticos",
        sa.Column("clave", sa.String(length=64), nullable=False),
        sa.Column("resultado", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("clave"),
    )


def downgrade() -> None:
    op.drop_table("oficio_diagnosticos")
