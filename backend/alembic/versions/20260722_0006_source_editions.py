"""source editions

Revision ID: 20260722_0006
Revises: 20260722_0005
Create Date: 2026-07-22
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260722_0006"
down_revision: str | None = "20260722_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "knowledge_source_editions",
        sa.Column("id", sa.String(length=120), nullable=False),
        sa.Column("source_id", sa.String(length=80), nullable=False),
        sa.Column("label", sa.String(length=160), nullable=False),
        sa.Column("publication_date", sa.String(length=80), nullable=False),
        sa.Column("location", sa.String(length=320), nullable=False),
        sa.Column("acquisition_status", sa.String(length=40), nullable=False),
        sa.Column("validation_status", sa.String(length=40), nullable=False),
        sa.Column("rights", sa.Text(), nullable=False),
        sa.Column("structure", sa.JSON(), nullable=False),
        sa.Column("locator_system", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["knowledge_sources.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_knowledge_source_editions_acquisition_status",
        "knowledge_source_editions",
        ["acquisition_status"],
    )
    op.create_index(
        "ix_knowledge_source_editions_validation_status",
        "knowledge_source_editions",
        ["validation_status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_knowledge_source_editions_validation_status",
        table_name="knowledge_source_editions",
    )
    op.drop_index(
        "ix_knowledge_source_editions_acquisition_status",
        table_name="knowledge_source_editions",
    )
    op.drop_table("knowledge_source_editions")
