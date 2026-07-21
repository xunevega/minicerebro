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


class FeedbackStatus(StrEnum):
    proposed = "proposed"
    applied = "applied"
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


class ScoreProposalItem(BaseModel):
    variable_key: str
    context: str
    delta: int = Field(ge=-300, le=300)
    reason: str


class ScoreProposal(BaseModel):
    preference_id: UUID
    status: str
    items: list[ScoreProposalItem]


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


class ApplyScoreProposalInput(BaseModel):
    reason: str = Field(min_length=3, max_length=500)


class FeedbackProposalInput(BaseModel):
    context: str = "general"
    note: str = Field(default="", max_length=500)


class FeedbackProposalItem(BaseModel):
    variable_key: str
    context: str
    current_value: int = Field(ge=0, le=1000)
    proposed_value: int = Field(ge=0, le=1000)
    delta: int = Field(ge=-300, le=300)
    reason: str


class FeedbackProposal(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    comparison_id: UUID
    status: FeedbackStatus = FeedbackStatus.proposed
    context: str
    items: list[FeedbackProposalItem]
    rationale: list[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class FeedbackDecisionInput(BaseModel):
    status: FeedbackStatus
    reason: str = Field(min_length=3, max_length=500)
    variable_keys: list[str] | None = None


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


class KnowledgeVersion(BaseModel):
    id: str
    status: str
    published_at: str
    source_count: int
    node_count: int
    evidence_count: int
    claim_count: int
    card_count: int


class KnowledgeSource(BaseModel):
    id: str
    name: str
    source_type: str
    authority_level: int
    priority: int
    status: str


class KnowledgeNode(BaseModel):
    id: str
    source_id: str
    node_type: str
    title: str
    summary: str
    version: str


class KnowledgeEvidenceItem(BaseModel):
    id: str
    node_id: str
    source_id: str
    reference: str
    excerpt: str
    confidence: float = Field(ge=0, le=1)
    version: str


class KnowledgeClaim(BaseModel):
    id: str
    evidence_id: str
    card_id: str
    statement: str
    confidence: float = Field(ge=0, le=1)
    version: str


class KnowledgeQueryInput(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    version: str = "knowledge-v0"
    limit: int = Field(default=5, ge=1, le=20)


class KnowledgeCard(BaseModel):
    id: str
    card_type: str
    name: str
    definition: str
    confidence: float = Field(ge=0, le=1)
    version: str
    payload: dict


class KnowledgeQueryResult(BaseModel):
    query: str
    version: str
    card_count: int
    claim_count: int
    evidence_count: int
    cards: list[KnowledgeCard]
    claims: list[KnowledgeClaim]
    evidence: list[KnowledgeEvidenceItem]


class KnowledgeQueryHistoryItem(BaseModel):
    event_id: int
    version: str
    has_results: bool
    query_length: int
    limit: int
    card_count: int
    claim_count: int
    evidence_count: int
    pending_validation_count: int
    created_at: datetime


class KnowledgeQuerySummary(BaseModel):
    version: str
    total_count: int
    empty_count: int
    hit_count: int
    last_query_at: datetime | None = None


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
    dimensions: dict[str, int] = Field(default_factory=dict)
    changes: list[dict[str, str]] = Field(default_factory=list)
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
    provider: str = "deterministic"


class GeneratedText(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    profile_id: str
    context: str
    action: str
    input_text: str
    output_text: str
    provider: str
    used_profile_variables: list[str]
    learning_applied: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class LabOverride(BaseModel):
    variable_key: str
    delta: int = Field(ge=-300, le=300)


class LabSimulationInput(BaseModel):
    text: str = Field(min_length=1, max_length=12000)
    action: str = "rewrite"
    context: str = "general"
    intensity: int = Field(default=500, ge=0, le=1000)
    protected_terms: list[str] = Field(default_factory=list)
    overrides: list[LabOverride] = Field(default_factory=list)


class LabSimulationResult(BaseModel):
    generation: GenerationResult
    comparison: ComparisonResult
    simulated_variables: list[dict]
    learning_applied: bool = False


class AuditEvent(BaseModel):
    id: int
    event_type: str
    entity_type: str
    entity_id: str
    payload: dict
    created_at: datetime


class ProfileStatistics(BaseModel):
    profile_id: str
    context: str
    variable_count: int
    preference_count: int
    accepted_preference_count: int
    average_confidence: float
    coverage: float
    low_confidence_variables: list[str]


class Contradiction(BaseModel):
    variable_key: str
    accepted_count: int
    rejected_count: int
    note: str


class V1Screen(BaseModel):
    id: str
    label: str
    route: str
    status: str
    functions: list[str]


class DecisionRule(BaseModel):
    priority: int
    label: str
    description: str


class DecisionEvaluationInput(BaseModel):
    context: str = "general"


class DecisionEvaluation(BaseModel):
    context: str
    applied_priority: list[DecisionRule]
    conflicts: list[str]
    low_confidence_variables: list[str]
    recommendation: str


class PersistenceDomain(BaseModel):
    id: str
    storage: str
    status: str
    separated_from_knowledge: bool


class CerebroAuditCandidate(BaseModel):
    component: str
    classification: str
    status: str
    evidence_required: list[str]
    note: str


class AcceptanceCriterion(BaseModel):
    id: int
    description: str
    status: str
    evidence: list[str]


class ClosureCondition(BaseModel):
    id: int
    description: str
    status: str
    evidence: list[str]


class ExpectedAnswerLine(BaseModel):
    order: int
    text: str
    evidence: list[str]


class ObservabilityMetric(BaseModel):
    id: str
    source: str
    status: str


class TechnicalRoadmapPhase(BaseModel):
    id: int
    name: str
    status: str
    items: list[str]


class CerebroAuditGate(BaseModel):
    id: str
    status: str
    reason: str


class TechnicalClosureCriterion(BaseModel):
    id: int
    description: str
    status: str
    evidence: list[str]


class ContractBoundary(BaseModel):
    section: int
    status: str
    reason: str
    next_step: str
