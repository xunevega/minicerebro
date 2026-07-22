"""source contract catalog

Revision ID: 20260722_0005
Revises: 20260721_0004
Create Date: 2026-07-22
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260722_0005"
down_revision: str | None = "20260721_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "knowledge_sources",
        sa.Column("catalog_id", sa.String(length=40), nullable=False, server_default="pending"),
    )
    op.add_column(
        "knowledge_sources",
        sa.Column("responsible", sa.String(length=320), nullable=False, server_default="pending"),
    )
    op.add_column(
        "knowledge_sources",
        sa.Column("domains", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "knowledge_sources",
        sa.Column("edition", sa.String(length=160), nullable=False, server_default="pending"),
    )
    op.add_column(
        "knowledge_sources",
        sa.Column("publication_date", sa.String(length=80), nullable=False, server_default="pending"),
    )
    op.add_column(
        "knowledge_sources",
        sa.Column("location", sa.String(length=320), nullable=False, server_default="pending"),
    )
    op.add_column(
        "knowledge_sources",
        sa.Column(
            "acquisition_status",
            sa.String(length=40),
            nullable=False,
            server_default="registered",
        ),
    )
    op.add_column(
        "knowledge_sources",
        sa.Column(
            "validation_status",
            sa.String(length=40),
            nullable=False,
            server_default="not_validated",
        ),
    )
    op.add_column(
        "knowledge_sources",
        sa.Column("rights", sa.Text(), nullable=False, server_default="pending"),
    )
    op.add_column(
        "knowledge_sources",
        sa.Column("structure", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "knowledge_sources",
        sa.Column("locator_system", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.create_index(
        "ix_knowledge_sources_acquisition_status",
        "knowledge_sources",
        ["acquisition_status"],
    )
    op.create_index(
        "ix_knowledge_sources_validation_status",
        "knowledge_sources",
        ["validation_status"],
    )


def downgrade() -> None:
    op.drop_index("ix_knowledge_sources_validation_status", table_name="knowledge_sources")
    op.drop_index("ix_knowledge_sources_acquisition_status", table_name="knowledge_sources")
    op.drop_column("knowledge_sources", "locator_system")
    op.drop_column("knowledge_sources", "structure")
    op.drop_column("knowledge_sources", "rights")
    op.drop_column("knowledge_sources", "validation_status")
    op.drop_column("knowledge_sources", "acquisition_status")
    op.drop_column("knowledge_sources", "location")
    op.drop_column("knowledge_sources", "publication_date")
    op.drop_column("knowledge_sources", "edition")
    op.drop_column("knowledge_sources", "domains")
    op.drop_column("knowledge_sources", "responsible")
    op.drop_column("knowledge_sources", "catalog_id")
