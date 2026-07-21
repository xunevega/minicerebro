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
