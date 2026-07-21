from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EvidenceType(StrEnum):
    prompt = "prompt"
    example = "example"
    correction = "correction"
    manual_override = "manual_override"
    comparison_feedback = "comparison_feedback"


class PreferenceStatus(StrEnum):
    proposed = "proposed"
    accepted = "accepted"
    rejected = "rejected"


class ScoreVariable(BaseModel):
    key: str
    label: str
    category: str
    calculated_value: int = Field(ge=0, le=1000)
    manual_adjustment: int = Field(ge=-1000, le=1000)
    confidence: float = Field(ge=0, le=1)
    context: str
    evidence_count: int
    updated_at: datetime

    @property
    def effective_value(self) -> int:
        return max(0, min(1000, self.calculated_value + self.manual_adjustment))


class ScorePatch(BaseModel):
    manual_adjustment: int = Field(ge=-1000, le=1000)
    reason: str = Field(min_length=3, max_length=500)


class Evidence(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    evidence_type: EvidenceType
    source: str
    summary: str
    weight: float = Field(ge=0, le=1)
    context: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Preference(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    text: str
    interpreted_as: str
    status: PreferenceStatus = PreferenceStatus.proposed
    evidence: Evidence
    affected_variables: list[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PreferenceInput(BaseModel):
    text: str = Field(min_length=3, max_length=5000)
    input_type: EvidenceType = EvidenceType.prompt
    context: str = "general"


class PreferencePatch(BaseModel):
    status: PreferenceStatus


class Profile(BaseModel):
    id: str
    name: str
    language: str = "es"
    summary: str
    variables: list[ScoreVariable]
    preferences: list[Preference]
    updated_at: datetime


class KnowledgeStatus(BaseModel):
    version: str
    state: str
    coverage: list[str]
    gaps: list[str]
    sources_policy: str


class ComparisonInput(BaseModel):
    original: str = Field(min_length=1)
    revised: str = Field(min_length=1)
    context: str = "general"


class ComparisonResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    modification_score: int = Field(ge=0, le=1000)
    adequacy_score: int = Field(ge=0, le=1000)
    changed_words: int
    original_words: int
    revised_words: int
    summary: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class GenerationInput(BaseModel):
    text: str = Field(min_length=1, max_length=12000)
    action: str = "rewrite"
    context: str = "general"
    intensity: int = Field(default=500, ge=0, le=1000)
    protected_terms: list[str] = Field(default_factory=list)


class GenerationResult(BaseModel):
    output: str
    explanation: str
    used_profile_variables: list[str]
    learning_applied: bool = False


class AuditEvent(BaseModel):
    id: int
    event_type: str
    entity_type: str
    entity_id: str
    payload: dict
    created_at: datetime
