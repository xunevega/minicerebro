"""claim contract

Revision ID: 20260722_0009
Revises: 20260722_0008
Create Date: 2026-07-22
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260722_0009"
down_revision: str | None = "20260722_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "knowledge_claims",
        sa.Column("claim_type", sa.String(length=80), nullable=False, server_default="stylistic"),
    )
    op.add_column(
        "knowledge_claims",
        sa.Column("node_id", sa.String(length=80), nullable=False, server_default="pending-node"),
    )
    op.add_column(
        "knowledge_claims",
        sa.Column("related_node_ids", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "knowledge_claims",
        sa.Column("domain", sa.String(length=160), nullable=False, server_default="writing.style"),
    )
    op.add_column(
        "knowledge_claims",
        sa.Column("scope", sa.JSON(), nullable=False, server_default="{}"),
    )
    op.add_column(
        "knowledge_claims",
        sa.Column("status", sa.String(length=40), nullable=False, server_default="draft"),
    )
    op.add_column(
        "knowledge_claims",
        sa.Column(
            "origin",
            sa.String(length=120),
            nullable=False,
            server_default="seed_contract_migration",
        ),
    )
    op.add_column(
        "knowledge_claims",
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "knowledge_claims",
        sa.Column("created_at", sa.String(length=80), nullable=False, server_default="2026-07-22"),
    )
    op.add_column(
        "knowledge_claims",
        sa.Column("updated_at", sa.String(length=80), nullable=False, server_default="2026-07-22"),
    )
    op.add_column(
        "knowledge_claims",
        sa.Column("published_at", sa.String(length=80), nullable=True),
    )
    op.create_index("ix_knowledge_claims_claim_type", "knowledge_claims", ["claim_type"])
    op.create_index("ix_knowledge_claims_domain", "knowledge_claims", ["domain"])
    op.create_index("ix_knowledge_claims_status", "knowledge_claims", ["status"])

    op.create_table(
        "knowledge_claim_evidence_links",
        sa.Column("id", sa.String(length=120), nullable=False),
        sa.Column("claim_id", sa.String(length=80), nullable=False),
        sa.Column("evidence_id", sa.String(length=80), nullable=False),
        sa.Column("role", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["knowledge_claims.id"]),
        sa.ForeignKeyConstraint(["evidence_id"], ["knowledge_evidence_items.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_knowledge_claim_evidence_links_role",
        "knowledge_claim_evidence_links",
        ["role"],
    )

    op.create_table(
        "knowledge_claim_revisions",
        sa.Column("id", sa.String(length=120), nullable=False),
        sa.Column("claim_id", sa.String(length=80), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("knowledge_version", sa.String(length=80), nullable=False),
        sa.Column("author", sa.String(length=120), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("changed_fields", sa.JSON(), nullable=False),
        sa.Column("previous_claim", sa.JSON(), nullable=False),
        sa.Column("new_claim", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["knowledge_claims.id"]),
        sa.ForeignKeyConstraint(["knowledge_version"], ["knowledge_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("knowledge_claim_revisions")
    op.drop_index("ix_knowledge_claim_evidence_links_role", table_name="knowledge_claim_evidence_links")
    op.drop_table("knowledge_claim_evidence_links")
    op.drop_index("ix_knowledge_claims_status", table_name="knowledge_claims")
    op.drop_index("ix_knowledge_claims_domain", table_name="knowledge_claims")
    op.drop_index("ix_knowledge_claims_claim_type", table_name="knowledge_claims")
    op.drop_column("knowledge_claims", "published_at")
    op.drop_column("knowledge_claims", "updated_at")
    op.drop_column("knowledge_claims", "created_at")
    op.drop_column("knowledge_claims", "revision")
    op.drop_column("knowledge_claims", "origin")
    op.drop_column("knowledge_claims", "status")
    op.drop_column("knowledge_claims", "scope")
    op.drop_column("knowledge_claims", "domain")
    op.drop_column("knowledge_claims", "related_node_ids")
    op.drop_column("knowledge_claims", "node_id")
    op.drop_column("knowledge_claims", "claim_type")
