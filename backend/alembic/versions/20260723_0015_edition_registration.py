"""edition registration

Revision ID: 20260723_0015
Revises: 20260723_0014
Create Date: 2026-07-23
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260723_0015"
down_revision: str | None = "20260723_0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "knowledge_source_editions",
        sa.Column("title", sa.String(length=240), nullable=False, server_default="pendiente de identificacion"),
    )
    op.add_column(
        "knowledge_source_editions",
        sa.Column(
            "edition_label",
            sa.String(length=160),
            nullable=False,
            server_default="pendiente de identificacion",
        ),
    )
    op.add_column(
        "knowledge_source_editions",
        sa.Column(
            "publication_year",
            sa.String(length=40),
            nullable=False,
            server_default="pendiente de identificacion",
        ),
    )
    op.add_column(
        "knowledge_source_editions",
        sa.Column("publisher", sa.String(length=240), nullable=False, server_default="pendiente de identificacion"),
    )
    op.add_column(
        "knowledge_source_editions",
        sa.Column("isbn", sa.String(length=80), nullable=False, server_default="pendiente de identificacion"),
    )
    op.add_column(
        "knowledge_source_editions",
        sa.Column("language", sa.String(length=40), nullable=False, server_default="es"),
    )
    op.add_column(
        "knowledge_source_editions",
        sa.Column("format", sa.String(length=80), nullable=False, server_default="pendiente de identificacion"),
    )
    op.add_column(
        "knowledge_source_editions",
        sa.Column(
            "access_location",
            sa.String(length=320),
            nullable=False,
            server_default="pendiente de adquisicion",
        ),
    )
    op.add_column(
        "knowledge_source_editions",
        sa.Column(
            "rights_status",
            sa.Text(),
            nullable=False,
            server_default="registro autorizado; contenido no ingerido",
        ),
    )
    op.add_column(
        "knowledge_source_editions",
        sa.Column("status", sa.String(length=40), nullable=False, server_default="registered"),
    )
    op.add_column(
        "knowledge_source_editions",
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
    )
    op.add_column(
        "knowledge_source_editions",
        sa.Column("created_at", sa.String(length=80), nullable=False, server_default="2026-07-23"),
    )
    op.add_column(
        "knowledge_source_editions",
        sa.Column("updated_at", sa.String(length=80), nullable=False, server_default="2026-07-23"),
    )
    op.create_index(
        "ix_knowledge_source_editions_status",
        "knowledge_source_editions",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index("ix_knowledge_source_editions_status", table_name="knowledge_source_editions")
    op.drop_column("knowledge_source_editions", "updated_at")
    op.drop_column("knowledge_source_editions", "created_at")
    op.drop_column("knowledge_source_editions", "notes")
    op.drop_column("knowledge_source_editions", "status")
    op.drop_column("knowledge_source_editions", "rights_status")
    op.drop_column("knowledge_source_editions", "access_location")
    op.drop_column("knowledge_source_editions", "format")
    op.drop_column("knowledge_source_editions", "language")
    op.drop_column("knowledge_source_editions", "isbn")
    op.drop_column("knowledge_source_editions", "publisher")
    op.drop_column("knowledge_source_editions", "publication_year")
    op.drop_column("knowledge_source_editions", "edition_label")
    op.drop_column("knowledge_source_editions", "title")
