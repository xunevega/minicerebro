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

export type KnowledgeStatus = {
  version: string;
  state: string;
  coverage: string[];
  gaps: string[];
  sources_policy: string;
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

export type ComparisonResult = {
  id: string;
  modification_score: number;
  adequacy_score: number;
  changed_words: number;
  original_words: number;
  revised_words: number;
  summary: string;
};
