from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ProfileRecord(Base):
    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    language: Mapped[str] = mapped_column(String(16), nullable=False, default="es")
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    variables: Mapped[list[ScoreVariableRecord]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
    )
    preferences: Mapped[list[PreferenceRecord]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
    )


class ScoreVariableRecord(Base):
    __tablename__ = "score_variables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[str] = mapped_column(ForeignKey("profiles.id"), nullable=False, index=True)
    key: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    calculated_value: Mapped[int] = mapped_column(Integer, nullable=False)
    manual_adjustment: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    context: Mapped[str] = mapped_column(String(120), nullable=False, default="general")
    evidence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    profile: Mapped[ProfileRecord] = relationship(back_populates="variables")


class EvidenceRecord(Base):
    __tablename__ = "evidences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    evidence_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(240), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    context: Mapped[str] = mapped_column(String(120), nullable=False, default="general")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    preferences: Mapped[list[PreferenceRecord]] = relationship(back_populates="evidence")


class PreferenceRecord(Base):
    __tablename__ = "preferences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    profile_id: Mapped[str] = mapped_column(ForeignKey("profiles.id"), nullable=False, index=True)
    evidence_id: Mapped[str] = mapped_column(ForeignKey("evidences.id"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    interpreted_as: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    affected_variables: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    profile: Mapped[ProfileRecord] = relationship(back_populates="preferences")
    evidence: Mapped[EvidenceRecord] = relationship(back_populates="preferences")


class ComparisonRecord(Base):
    __tablename__ = "comparisons"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    modification_score: Mapped[int] = mapped_column(Integer, nullable=False)
    adequacy_score: Mapped[int] = mapped_column(Integer, nullable=False)
    changed_words: Mapped[int] = mapped_column(Integer, nullable=False)
    original_words: Mapped[int] = mapped_column(Integer, nullable=False)
    revised_words: Mapped[int] = mapped_column(Integer, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class FeedbackProposalRecord(Base):
    __tablename__ = "feedback_proposals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    comparison_id: Mapped[str] = mapped_column(ForeignKey("comparisons.id"), nullable=False, index=True)
    profile_id: Mapped[str] = mapped_column(ForeignKey("profiles.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    context: Mapped[str] = mapped_column(String(120), nullable=False, default="general")
    items: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    rationale: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class GeneratedTextRecord(Base):
    __tablename__ = "generated_texts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    profile_id: Mapped[str] = mapped_column(ForeignKey("profiles.id"), nullable=False, index=True)
    context: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    output_text: Mapped[str] = mapped_column(Text, nullable=False)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    used_profile_variables: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    learning_applied: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class KnowledgeVersionRecord(Base):
    __tablename__ = "knowledge_versions"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    published_at: Mapped[str] = mapped_column(String(80), nullable=False)


class KnowledgeObjectRevisionRecord(Base):
    __tablename__ = "knowledge_object_revisions"

    id: Mapped[str] = mapped_column(String(260), primary_key=True)
    object_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    object_id: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    object_version: Mapped[str] = mapped_column(String(180), nullable=False)
    knowledge_version: Mapped[str] = mapped_column(ForeignKey("knowledge_versions.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    change_type: Mapped[str] = mapped_column(String(80), nullable=False)
    author: Mapped[str] = mapped_column(String(120), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    previous_revision: Mapped[int | None] = mapped_column(Integer, nullable=True)
    replaces_object_id: Mapped[str | None] = mapped_column(String(180), nullable=True)
    replaced_by_object_id: Mapped[str | None] = mapped_column(String(180), nullable=True)
    before: Mapped[dict] = mapped_column(JSON, nullable=False)
    after: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[str] = mapped_column(String(80), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(80), nullable=False)


class KnowledgeSourceRecord(Base):
    __tablename__ = "knowledge_sources"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    catalog_id: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(240), nullable=False)
    responsible: Mapped[str] = mapped_column(String(320), nullable=False)
    source_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    domains: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    authority_level: Mapped[int] = mapped_column(Integer, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    edition: Mapped[str] = mapped_column(String(160), nullable=False)
    publication_date: Mapped[str] = mapped_column(String(80), nullable=False)
    location: Mapped[str] = mapped_column(String(320), nullable=False)
    acquisition_status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    validation_status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    rights: Mapped[str] = mapped_column(Text, nullable=False)
    structure: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    locator_system: Mapped[list[str]] = mapped_column(JSON, nullable=False)


class KnowledgeSourceEditionRecord(Base):
    __tablename__ = "knowledge_source_editions"

    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("knowledge_sources.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    edition_label: Mapped[str] = mapped_column(String(160), nullable=False)
    publication_year: Mapped[str] = mapped_column(String(40), nullable=False)
    publisher: Mapped[str] = mapped_column(String(240), nullable=False)
    isbn: Mapped[str] = mapped_column(String(80), nullable=False)
    language: Mapped[str] = mapped_column(String(40), nullable=False)
    format: Mapped[str] = mapped_column(String(80), nullable=False)
    access_location: Mapped[str] = mapped_column(String(320), nullable=False)
    rights_status: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(80), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(80), nullable=False)
    label: Mapped[str] = mapped_column(String(160), nullable=False)
    publication_date: Mapped[str] = mapped_column(String(80), nullable=False)
    location: Mapped[str] = mapped_column(String(320), nullable=False)
    acquisition_status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    validation_status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    rights: Mapped[str] = mapped_column(Text, nullable=False)
    structure: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    locator_system: Mapped[list[str]] = mapped_column(JSON, nullable=False)


class KnowledgeIngestionBatchRecord(Base):
    __tablename__ = "knowledge_ingestion_batches"

    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("knowledge_sources.id"), nullable=False, index=True)
    source_edition_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_source_editions.id"), nullable=False, index=True
    )
    batch_label: Mapped[str] = mapped_column(String(160), nullable=False)
    scope: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(120), nullable=False)
    tools: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    model_used: Mapped[str | None] = mapped_column(String(120), nullable=True)
    configuration: Mapped[dict] = mapped_column(JSON, nullable=False)
    progress: Mapped[dict] = mapped_column(JSON, nullable=False)
    metrics: Mapped[dict] = mapped_column(JSON, nullable=False)
    decisions: Mapped[list[dict]] = mapped_column(JSON, nullable=False)
    blockers: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    result: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[str] = mapped_column(String(80), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(80), nullable=False)


class KnowledgeIndexEntryRecord(Base):
    __tablename__ = "knowledge_index_entries"

    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    edition_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_source_editions.id"), nullable=False, index=True
    )
    parent_id: Mapped[str | None] = mapped_column(
        ForeignKey("knowledge_index_entries.id"), nullable=True, index=True
    )
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    entry_order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(320), nullable=False)
    locator: Mapped[str] = mapped_column(String(240), nullable=False)
    page_start: Mapped[str | None] = mapped_column(String(40), nullable=True)
    page_end: Mapped[str | None] = mapped_column(String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    created_at: Mapped[str] = mapped_column(String(80), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(80), nullable=False)


class KnowledgeSegmentRecord(Base):
    __tablename__ = "knowledge_segments"

    id: Mapped[str] = mapped_column(String(180), primary_key=True)
    index_entry_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_index_entries.id"), nullable=False, index=True
    )
    parent_segment_id: Mapped[str | None] = mapped_column(
        ForeignKey("knowledge_segments.id"), nullable=True, index=True
    )
    segment_type: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(320), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    segment_order: Mapped[int] = mapped_column(Integer, nullable=False)
    start_locator: Mapped[str] = mapped_column(String(240), nullable=False)
    end_locator: Mapped[str] = mapped_column(String(240), nullable=False)
    language: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    created_at: Mapped[str] = mapped_column(String(80), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(80), nullable=False)


class KnowledgeNodeRecord(Base):
    __tablename__ = "knowledge_nodes"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("knowledge_sources.id"), nullable=False)
    node_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_name: Mapped[str] = mapped_column(String(240), nullable=False)
    primary_branch: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    secondary_branch: Mapped[str] = mapped_column(String(120), nullable=False)
    short_definition: Mapped[str] = mapped_column(String(320), nullable=False)
    long_definition: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    version: Mapped[str] = mapped_column(ForeignKey("knowledge_versions.id"), nullable=False)
    created_at: Mapped[str] = mapped_column(String(80), nullable=False)
    published_at: Mapped[str] = mapped_column(String(80), nullable=False)
    aliases: Mapped[list[str]] = mapped_column(JSON, nullable=False)


class KnowledgeNodeRelationRecord(Base):
    __tablename__ = "knowledge_node_relations"

    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    source_node_id: Mapped[str] = mapped_column(ForeignKey("knowledge_nodes.id"), nullable=False)
    target_node_id: Mapped[str] = mapped_column(ForeignKey("knowledge_nodes.id"), nullable=False)
    relation_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(40), nullable=False)
    cardinality: Mapped[str] = mapped_column(String(20), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    context: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    version: Mapped[str] = mapped_column(ForeignKey("knowledge_versions.id"), nullable=False)
    created_at: Mapped[str] = mapped_column(String(80), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(80), nullable=False)


class KnowledgeRelationRecord(Base):
    __tablename__ = "knowledge_relations"

    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    source_entity_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    source_entity_id: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    target_entity_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    target_entity_id: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    relation_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(40), nullable=False)
    cardinality: Mapped[str] = mapped_column(String(20), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    context: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    version: Mapped[str] = mapped_column(ForeignKey("knowledge_versions.id"), nullable=False)
    created_at: Mapped[str] = mapped_column(String(80), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(80), nullable=False)


class KnowledgeEvidenceItemRecord(Base):
    __tablename__ = "knowledge_evidence_items"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    node_id: Mapped[str] = mapped_column(ForeignKey("knowledge_nodes.id"), nullable=False)
    source_id: Mapped[str] = mapped_column(ForeignKey("knowledge_sources.id"), nullable=False)
    source_edition_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_source_editions.id"), nullable=False
    )
    evidence_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    locator: Mapped[dict] = mapped_column(JSON, nullable=False)
    reference: Mapped[str] = mapped_column(String(240), nullable=False)
    excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_level: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    version: Mapped[str] = mapped_column(ForeignKey("knowledge_versions.id"), nullable=False)
    created_at: Mapped[str] = mapped_column(String(80), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(80), nullable=False)
    incorporated_by: Mapped[str] = mapped_column(String(120), nullable=False)
    reviewed_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)


class KnowledgeEvidenceRevisionRecord(Base):
    __tablename__ = "knowledge_evidence_revisions"

    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    evidence_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_evidence_items.id"), nullable=False
    )
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    author: Mapped[str] = mapped_column(String(120), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    changes: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[str] = mapped_column(String(80), nullable=False)


class KnowledgeCardRecord(Base):
    __tablename__ = "knowledge_cards"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    card_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(240), nullable=False)
    definition: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    version: Mapped[str] = mapped_column(ForeignKey("knowledge_versions.id"), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)


class KnowledgeClaimRecord(Base):
    __tablename__ = "knowledge_claims"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    evidence_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_evidence_items.id"), nullable=False
    )
    card_id: Mapped[str] = mapped_column(ForeignKey("knowledge_cards.id"), nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    claim_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    node_id: Mapped[str] = mapped_column(ForeignKey("knowledge_nodes.id"), nullable=False)
    related_node_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    domain: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    scope: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    origin: Mapped[str] = mapped_column(String(120), nullable=False)
    version: Mapped[str] = mapped_column(ForeignKey("knowledge_versions.id"), nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[str] = mapped_column(String(80), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(80), nullable=False)
    published_at: Mapped[str | None] = mapped_column(String(80), nullable=True)


class KnowledgeClaimEvidenceLinkRecord(Base):
    __tablename__ = "knowledge_claim_evidence_links"

    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    claim_id: Mapped[str] = mapped_column(ForeignKey("knowledge_claims.id"), nullable=False)
    evidence_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_evidence_items.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    created_at: Mapped[str] = mapped_column(String(80), nullable=False)


class KnowledgeClaimRevisionRecord(Base):
    __tablename__ = "knowledge_claim_revisions"

    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    claim_id: Mapped[str] = mapped_column(ForeignKey("knowledge_claims.id"), nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    knowledge_version: Mapped[str] = mapped_column(ForeignKey("knowledge_versions.id"), nullable=False)
    author: Mapped[str] = mapped_column(String(120), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    changed_fields: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    previous_claim: Mapped[dict] = mapped_column(JSON, nullable=False)
    new_claim: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[str] = mapped_column(String(80), nullable=False)


class AuditEventRecord(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(120), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
