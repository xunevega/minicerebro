"""extraction runs

Revision ID: 20260723_0018
Revises: 20260723_0017
Create Date: 2026-07-23
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260723_0018"
down_revision: str | None = "20260723_0017"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "knowledge_extraction_runs",
        sa.Column("id", sa.String(length=180), nullable=False),
        sa.Column("segment_id", sa.String(length=180), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("extractor_type", sa.String(length=80), nullable=False),
        sa.Column("extractor_name", sa.String(length=160), nullable=False),
        sa.Column("extractor_version", sa.String(length=80), nullable=False),
        sa.Column("configuration", sa.JSON(), nullable=False),
        sa.Column("input_segment_revision", sa.Integer(), nullable=False),
        sa.Column("input_segment_hash", sa.String(length=64), nullable=False),
        sa.Column("knowledge_version", sa.String(length=80), nullable=True),
        sa.Column("started_at", sa.String(length=80), nullable=True),
        sa.Column("completed_at", sa.String(length=80), nullable=True),
        sa.Column("error_code", sa.String(length=120), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.String(length=80), nullable=False),
        sa.Column("updated_at", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["knowledge_version"], ["knowledge_versions.id"]),
        sa.ForeignKeyConstraint(["segment_id"], ["knowledge_segments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_knowledge_extraction_runs_segment_id",
        "knowledge_extraction_runs",
        ["segment_id"],
    )
    op.create_index(
        "ix_knowledge_extraction_runs_status",
        "knowledge_extraction_runs",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index("ix_knowledge_extraction_runs_status", table_name="knowledge_extraction_runs")
    op.drop_index("ix_knowledge_extraction_runs_segment_id", table_name="knowledge_extraction_runs")
    op.drop_table("knowledge_extraction_runs")
