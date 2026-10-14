"""profile oficio fichas

Postura del usuario ante las fichas de oficio (docs/POLITICA_CONOCIMIENTO.md).

Revision ID: 20261014_0025
Revises: 20260816_0024
Create Date: 2026-10-14
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261014_0025"
down_revision: str | None = "20260816_0024"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "profile_oficio_fichas",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("profile_id", sa.String(length=80), nullable=False),
        sa.Column("card_id", sa.String(length=80), nullable=False),
        sa.Column("knowledge_version", sa.String(length=80), nullable=False),
        sa.Column("stance", sa.String(length=40), nullable=False),
        sa.Column("user_score", sa.Integer(), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=False),
        sa.Column("maintained_elements", sa.JSON(), nullable=False),
        sa.Column("change_requests", sa.JSON(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("profile_id", "card_id", name="uq_profile_oficio_ficha"),
    )
    op.create_index("ix_profile_oficio_fichas_profile_id", "profile_oficio_fichas", ["profile_id"])
    op.create_index("ix_profile_oficio_fichas_card_id", "profile_oficio_fichas", ["card_id"])
    op.create_index("ix_profile_oficio_fichas_stance", "profile_oficio_fichas", ["stance"])


def downgrade() -> None:
    op.drop_index("ix_profile_oficio_fichas_stance", table_name="profile_oficio_fichas")
    op.drop_index("ix_profile_oficio_fichas_card_id", table_name="profile_oficio_fichas")
    op.drop_index("ix_profile_oficio_fichas_profile_id", table_name="profile_oficio_fichas")
    op.drop_table("profile_oficio_fichas")
