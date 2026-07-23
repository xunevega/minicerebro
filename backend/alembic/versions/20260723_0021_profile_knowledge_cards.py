"""profile knowledge cards

Revision ID: 20260723_0021
Revises: 20260723_0020
Create Date: 2026-07-23
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260723_0021"
down_revision: str | None = "20260723_0020"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "profile_knowledge_cards",
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
        sa.ForeignKeyConstraint(["card_id"], ["knowledge_cards.id"]),
        sa.ForeignKeyConstraint(["knowledge_version"], ["knowledge_versions.id"]),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "profile_id",
            "card_id",
            "knowledge_version",
            name="uq_profile_knowledge_card_version",
        ),
    )
    op.create_index(
        "ix_profile_knowledge_cards_card_id",
        "profile_knowledge_cards",
        ["card_id"],
    )
    op.create_index(
        "ix_profile_knowledge_cards_knowledge_version",
        "profile_knowledge_cards",
        ["knowledge_version"],
    )
    op.create_index(
        "ix_profile_knowledge_cards_profile_id",
        "profile_knowledge_cards",
        ["profile_id"],
    )
    op.create_index(
        "ix_profile_knowledge_cards_stance",
        "profile_knowledge_cards",
        ["stance"],
    )


def downgrade() -> None:
    op.drop_index("ix_profile_knowledge_cards_stance", table_name="profile_knowledge_cards")
    op.drop_index("ix_profile_knowledge_cards_profile_id", table_name="profile_knowledge_cards")
    op.drop_index(
        "ix_profile_knowledge_cards_knowledge_version",
        table_name="profile_knowledge_cards",
    )
    op.drop_index("ix_profile_knowledge_cards_card_id", table_name="profile_knowledge_cards")
    op.drop_table("profile_knowledge_cards")
