export type ScoreVariable = {
  key: string;
  label: string;
  category: string;
  calculated_value: number;
  manual_adjustment: number;
  effective_value: number;
  confidence: number;
  context: string;
  evidence_count: number;
};

export type ScoreUpdate = {
  variable: ScoreVariable;
  evidence: {
    id: string;
    evidence_type: "manual_override";
    source: string;
    summary: string;
    weight: number;
    context: string;
    created_at: string;
  };
};

export type ScoreProposal = {
  preference_id: string;
  status: "pending_review" | "not_applicable" | "not_found";
  items: Array<{
    variable_key: string;
    context: string;
    delta: number;
    reason: string;
  }>;
};

export type ScoreProposalApplyResult = {
  proposal: ScoreProposal;
  variables: ScoreVariable[];
};

export type KnowledgeStatus = {
  version: string;
  state: string;
  coverage: string[];
  gaps: string[];
  sources_policy: string;
};

export type KnowledgeCard = {
  id: string;
  card_type: string;
  name: string;
  definition: string;
  confidence: number;
  version: string;
  payload: Record<string, unknown>;
};

export type KnowledgeSource = {
  id: string;
  catalog_id: string;
  name: string;
  responsible: string;
  source_type: string;
  domains: string[];
  authority_level: number;
  priority: number;
  status: string;
  edition: string;
  publication_date: string;
  location: string;
  acquisition_status: string;
  validation_status: string;
  rights: string;
  structure: string[];
  locator_system: string[];
  editions: KnowledgeSourceEdition[];
};

export type KnowledgeObjectRevision = {
  id: string;
  object_type: string;
  object_id: string;
  revision_number: number;
  object_version: string;
  knowledge_version: string;
  status: string;
  change_type: string;
  author: string;
  reason: string;
  previous_revision: number | null;
  replaces_object_id: string | null;
  replaced_by_object_id: string | null;
  before: Record<string, unknown>;
  after: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type KnowledgeVersioningPolicy = {
  versioned_object_types: string[];
  excluded_object_types: string[];
  versioning_levels: string[];
  revision_triggers: string[];
  non_revision_changes: string[];
  identifiers: Record<string, string>;
  immutable_after_publication: boolean;
  object_statuses: string[];
  history_fields: string[];
  historical_recovery: string[];
  compatibility_policy: string;
  audit_events: string[];
  source_versioning_levels: string[];
  integrity_rules: string[];
  publication_checks: string[];
  publication_failure_state: string;
  acceptance_criteria: string[];
  closure_questions: string[];
  release_chain: string[];
};

export type KnowledgePublicationPolicy = {
  meaning: string;
  publication_unit: string;
  non_publication_units: string[];
  lifecycle: string[];
  requirements: string[];
  validations: string[];
  publication_effects: string[];
  immutable_after_publication: boolean;
  partial_publications_allowed: boolean;
  rollback_policy: string;
  audit_fields: string[];
  acceptance_criteria: string[];
  closure_criteria: string[];
};

export type KnowledgePublicationReadiness = {
  version: string;
  status: string;
  publishable: boolean;
  publication_unit: string;
  partial_publications_allowed: boolean;
  checks: Array<{
    id: string;
    label: string;
    passed: boolean;
    detail: string;
  }>;
  blockers: string[];
  audit_preview: Record<string, unknown>;
};

export type KnowledgeSourceEdition = {
  id: string;
  source_id: string;
  label: string;
  publication_date: string;
  location: string;
  acquisition_status: string;
  validation_status: string;
  rights: string;
  structure: string[];
  locator_system: string[];
};

export type KnowledgeNode = {
  id: string;
  source_id: string;
  node_type: string;
  title: string;
  summary: string;
  canonical_name: string;
  primary_branch: string;
  secondary_branch: string;
  short_definition: string;
  long_definition: string;
  status: string;
  version: string;
  created_at: string;
  published_at: string;
  aliases: string[];
  relations: KnowledgeNodeRelation[];
};

export type KnowledgeNodeRelation = {
  id: string;
  source_node_id: string;
  target_node_id: string;
  relation_type: string;
  direction: string;
  cardinality: string;
  weight: number;
  confidence: number;
  context: string;
  status: string;
  version: string;
  created_at: string;
  updated_at: string;
};

export type KnowledgeRelation = {
  id: string;
  source_entity_type: string;
  source_entity_id: string;
  target_entity_type: string;
  target_entity_id: string;
  relation_type: string;
  direction: string;
  cardinality: string;
  weight: number;
  confidence: number;
  context: string;
  status: string;
  version: string;
  created_at: string;
  updated_at: string;
};

export type KnowledgeClaim = {
  id: string;
  evidence_id: string;
  card_id: string;
  statement: string;
  claim_type: string;
  node_id: string;
  related_node_ids: string[];
  domain: string;
  scope: Record<string, unknown>;
  status: string;
  confidence: number;
  origin: string;
  version: string;
  revision: number;
  created_at: string;
  updated_at: string;
  published_at: string | null;
  evidence_links: KnowledgeClaimEvidenceLink[];
};

export type KnowledgeClaimEvidenceLink = {
  id: string;
  claim_id: string;
  evidence_id: string;
  role: string;
  created_at: string;
};

export type KnowledgeEvidenceItem = {
  id: string;
  node_id: string;
  source_id: string;
  source_edition_id: string;
  evidence_type: string;
  locator: Record<string, unknown>;
  reference: string;
  excerpt: string;
  context: string;
  confidence: number;
  confidence_level: number;
  status: string;
  version: string;
  created_at: string;
  updated_at: string;
  incorporated_by: string;
  reviewed_by: string | null;
  revision: number;
};

export type KnowledgeQueryResult = {
  query: string;
  version: string;
  requested_version: string;
  resolved_version: string;
  query_type: string[];
  domain: string[];
  context: Record<string, unknown>;
  status: string;
  card_count: number;
  claim_count: number;
  evidence_count: number;
  cards: KnowledgeCard[];
  claims: KnowledgeClaim[];
  evidence: KnowledgeEvidenceItem[];
  sources: KnowledgeSource[];
  relations_followed: KnowledgeRelation[];
  contradictions: Array<Record<string, unknown>>;
  ranking: Array<{
    card_id: string;
    final_score: number;
    factors: Record<string, number>;
    reasons: string[];
  }>;
  retrieved_cards: Array<{
    card_id: string;
    node_id: string;
    name: string;
    summary: string;
    score: number;
    reasons: string[];
    claim_ids: string[];
    source_ids: string[];
    relation_paths: string[];
    confidence: number;
  }>;
  retrieval_trace: Record<string, unknown>;
  limits: Record<string, unknown>;
  generated_at: string;
};

export type KnowledgeQueryHistoryItem = {
  event_id: number;
  version: string;
  has_results: boolean;
  query_length: number;
  limit: number;
  card_count: number;
  claim_count: number;
  evidence_count: number;
  pending_validation_count: number;
  created_at: string;
};

export type KnowledgeQuerySummary = {
  version: string;
  total_count: number;
  empty_count: number;
  hit_count: number;
  last_query_at: string | null;
};

export type ProfileSummary = {
  profile_id: string;
  summary: string;
  preference_count: number;
  confidence_note: string;
};

export type ProfileExport = {
  export_version: string;
  exported_at: string;
  profile_id: string;
  variables_by_context: Record<string, ScoreVariable[]>;
  preferences: Preference[];
  knowledge_policy: string;
};

export type Preference = {
  id: string;
  text: string;
  interpreted_as: string;
  status: "proposed" | "accepted" | "rejected";
  affected_variables: string[];
};

export type PreferenceStatus = Preference["status"];

export type ComparisonResult = {
  id: string;
  modification_score: number;
  adequacy_score: number;
  changed_words: number;
  original_words: number;
  revised_words: number;
  summary: string;
  dimensions: Record<string, number>;
  changes: Array<{ type: string; original: string; revised: string }>;
};

export type FeedbackStatus = "proposed" | "applied" | "rejected";

export type FeedbackProposal = {
  id: string;
  comparison_id: string;
  status: FeedbackStatus;
  context: string;
  items: Array<{
    variable_key: string;
    context: string;
    current_value: number;
    proposed_value: number;
    delta: number;
    reason: string;
  }>;
  rationale: string[];
  created_at: string;
  updated_at: string;
};

export type AuditEvent = {
  id: number;
  event_type: string;
  entity_type: string;
  entity_id: string;
  payload: Record<string, unknown>;
  created_at: string;
};

export type GenerationAction = "rewrite" | "correction" | "continue" | "variants";

export type GenerationResult = {
  output: string;
  explanation: string;
  used_profile_variables: string[];
  learning_applied: boolean;
  provider: string;
};

export type LabOverride = {
  variable_key: string;
  delta: number;
};

export type LabSimulationResult = {
  generation: GenerationResult;
  comparison: ComparisonResult;
  simulated_variables: ScoreVariable[];
  learning_applied: boolean;
};

export type ProfileStatistics = {
  profile_id: string;
  context: string;
  variable_count: number;
  preference_count: number;
  accepted_preference_count: number;
  average_confidence: number;
  coverage: number;
  low_confidence_variables: string[];
};

export type Contradiction = {
  variable_key: string;
  accepted_count: number;
  rejected_count: number;
  note: string;
};

export type V1Screen = {
  id: string;
  label: string;
  route: string;
  status: string;
  functions: string[];
};

export type DecisionRule = {
  priority: number;
  label: string;
  description: string;
};

export type DecisionEvaluation = {
  context: string;
  applied_priority: DecisionRule[];
  conflicts: string[];
  low_confidence_variables: string[];
  recommendation: string;
};

export type PersistenceDomain = {
  id: string;
  storage: string;
  status: string;
  separated_from_knowledge: boolean;
};

export type GeneratedText = {
  id: string;
  profile_id: string;
  context: string;
  action: string;
  input_text: string;
  output_text: string;
  provider: string;
  used_profile_variables: string[];
  learning_applied: boolean;
  created_at: string;
};

export type CerebroAuditCandidate = {
  component: string;
  classification: string;
  status: string;
  evidence_required: string[];
  note: string;
};

export type AcceptanceCriterion = {
  id: number;
  description: string;
  status: string;
  evidence: string[];
};

export type ClosureCondition = {
  id: number;
  description: string;
  status: string;
  evidence: string[];
};

export type ExpectedAnswerLine = {
  order: number;
  text: string;
  evidence: string[];
};

export type ObservabilityMetric = {
  id: string;
  source: string;
  status: string;
};

export type TechnicalRoadmapPhase = {
  id: number;
  name: string;
  status: string;
  items: string[];
};

export type CerebroAuditGate = {
  id: string;
  status: string;
  reason: string;
};

export type TechnicalClosureCriterion = {
  id: number;
  description: string;
  status: string;
  evidence: string[];
};

export type ContractBoundary = {
  section: number;
  status: string;
  reason: string;
  next_step: string;
};
