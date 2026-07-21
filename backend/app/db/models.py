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


class KnowledgeSourceRecord(Base):
    __tablename__ = "knowledge_sources"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    name: Mapped[str] = mapped_column(String(240), nullable=False)
    source_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    authority_level: Mapped[int] = mapped_column(Integer, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)


class KnowledgeNodeRecord(Base):
    __tablename__ = "knowledge_nodes"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("knowledge_sources.id"), nullable=False)
    node_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(ForeignKey("knowledge_versions.id"), nullable=False)


class KnowledgeEvidenceItemRecord(Base):
    __tablename__ = "knowledge_evidence_items"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    node_id: Mapped[str] = mapped_column(ForeignKey("knowledge_nodes.id"), nullable=False)
    source_id: Mapped[str] = mapped_column(ForeignKey("knowledge_sources.id"), nullable=False)
    reference: Mapped[str] = mapped_column(String(240), nullable=False)
    excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    version: Mapped[str] = mapped_column(ForeignKey("knowledge_versions.id"), nullable=False)


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
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    version: Mapped[str] = mapped_column(ForeignKey("knowledge_versions.id"), nullable=False)


class AuditEventRecord(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(120), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
