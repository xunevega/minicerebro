"""oficio fichas editables y propuestas

Fichas de oficio editadas desde la app, su historial y las propuestas de mejora
(docs/POLITICA_CONOCIMIENTO.md).

Revision ID: 20261014_0026
Revises: 20261014_0025
Create Date: 2026-10-14
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261014_0026"
down_revision: str | None = "20261014_0025"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "oficio_fichas",
        sa.Column("id", sa.String(length=80), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("origen", sa.String(length=20), nullable=False),
        sa.Column("activa", sa.Boolean(), nullable=False),
        sa.Column("updated_by", sa.String(length=200), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "oficio_ficha_versiones",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("ficha_id", sa.String(length=80), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("activa", sa.Boolean(), nullable=False),
        sa.Column("motivo", sa.Text(), nullable=False),
        sa.Column("autor", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_oficio_ficha_versiones_ficha_id", "oficio_ficha_versiones", ["ficha_id"])
    op.create_table(
        "oficio_propuestas",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("ficha_id", sa.String(length=80), nullable=False),
        sa.Column("tipo", sa.String(length=40), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("motivo", sa.Text(), nullable=False),
        sa.Column("evidencia", sa.JSON(), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decided_by", sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_oficio_propuestas_ficha_id", "oficio_propuestas", ["ficha_id"])
    op.create_index("ix_oficio_propuestas_estado", "oficio_propuestas", ["estado"])


def downgrade() -> None:
    op.drop_index("ix_oficio_propuestas_estado", table_name="oficio_propuestas")
    op.drop_index("ix_oficio_propuestas_ficha_id", table_name="oficio_propuestas")
    op.drop_table("oficio_propuestas")
    op.drop_index("ix_oficio_ficha_versiones_ficha_id", table_name="oficio_ficha_versiones")
    op.drop_table("oficio_ficha_versiones")
    op.drop_table("oficio_fichas")
