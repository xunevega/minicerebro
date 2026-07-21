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
  name: string;
  source_type: string;
  authority_level: number;
  priority: number;
  status: string;
};

export type ProfileSummary = {
  profile_id: string;
  summary: string;
  preference_count: number;
  confidence_note: string;
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
