"""initial persistence

Revision ID: 20260721_0001
Revises:
Create Date: 2026-07-21
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260721_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "profiles",
        sa.Column("id", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("language", sa.String(length=16), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "comparisons",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("modification_score", sa.Integer(), nullable=False),
        sa.Column("adequacy_score", sa.Integer(), nullable=False),
        sa.Column("changed_words", sa.Integer(), nullable=False),
        sa.Column("original_words", sa.Integer(), nullable=False),
        sa.Column("revised_words", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "evidences",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("evidence_type", sa.String(length=80), nullable=False),
        sa.Column("source", sa.String(length=240), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("context", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_evidences_evidence_type", "evidences", ["evidence_type"])
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("entity_type", sa.String(length=120), nullable=False),
        sa.Column("entity_id", sa.String(length=120), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_events_event_type", "audit_events", ["event_type"])
    op.create_table(
        "score_variables",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("profile_id", sa.String(length=80), nullable=False),
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("label", sa.String(length=200), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("calculated_value", sa.Integer(), nullable=False),
        sa.Column("manual_adjustment", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("context", sa.String(length=120), nullable=False),
        sa.Column("evidence_count", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_score_variables_key", "score_variables", ["key"])
    op.create_index("ix_score_variables_profile_id", "score_variables", ["profile_id"])
    op.create_table(
        "preferences",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("profile_id", sa.String(length=80), nullable=False),
        sa.Column("evidence_id", sa.String(length=36), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("interpreted_as", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("affected_variables", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["evidence_id"], ["evidences.id"]),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_preferences_profile_id", "preferences", ["profile_id"])
    op.create_index("ix_preferences_status", "preferences", ["status"])


def downgrade() -> None:
    op.drop_index("ix_preferences_status", table_name="preferences")
    op.drop_index("ix_preferences_profile_id", table_name="preferences")
    op.drop_table("preferences")
    op.drop_index("ix_score_variables_profile_id", table_name="score_variables")
    op.drop_index("ix_score_variables_key", table_name="score_variables")
    op.drop_table("score_variables")
    op.drop_index("ix_audit_events_event_type", table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_index("ix_evidences_evidence_type", table_name="evidences")
    op.drop_table("evidences")
    op.drop_table("comparisons")
    op.drop_table("profiles")

