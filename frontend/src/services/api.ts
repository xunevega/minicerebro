import type {
  AuditEvent,
  ComparisonResult,
  Contradiction,
  GenerationAction,
  GenerationResult,
  KnowledgeCard,
  KnowledgeStatus,
  KnowledgeSource,
  LabOverride,
  LabSimulationResult,
  Preference,
  PreferenceStatus,
  ProfileSummary,
  ProfileStatistics,
  ScoreProposal,
  ScoreProposalApplyResult,
  ScoreUpdate,
  ScoreVariable,
} from "../types/api";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!response.ok) {
    throw new Error(`API ${response.status}: ${await response.text()}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export function getKnowledgeStatus() {
  return request<KnowledgeStatus>("/knowledge/status");
}

export function getKnowledgeCards() {
  return request<KnowledgeCard[]>("/knowledge/cards");
}

export function getKnowledgeSources() {
  return request<KnowledgeSource[]>("/knowledge/sources");
}

function withContext(path: string, context: string) {
  const separator = path.includes("?") ? "&" : "?";
  return `${path}${separator}context=${encodeURIComponent(context)}`;
}

export function getProfileSummary() {
  return request<ProfileSummary>("/profiles/default/summary");
}

export function getScores(context: string) {
  return request<ScoreVariable[]>(withContext("/profiles/default/scores", context));
}

export function getProfileStatistics(context: string) {
  return request<ProfileStatistics>(withContext("/profiles/default/statistics", context));
}

export function getContradictions(context: string) {
  return request<Contradiction[]>(withContext("/profiles/default/contradictions", context));
}

export function updateScore(
  variableKey: string,
  manualAdjustment: number,
  reason: string,
  context: string,
) {
  return request<ScoreUpdate>(withContext(`/profiles/default/scores/${variableKey}`, context), {
    method: "PATCH",
    body: JSON.stringify({ manual_adjustment: manualAdjustment, reason }),
  });
}

export function createPreference(text: string, context: string) {
  return request<Preference>("/preferences", {
    method: "POST",
    body: JSON.stringify({ text, input_type: "prompt", context }),
  });
}

export function getPreferences(context: string) {
  return request<Preference[]>(withContext("/preferences", context));
}

export function updatePreferenceStatus(preferenceId: string, status: PreferenceStatus) {
  return request<Preference>(`/preferences/${preferenceId}`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export function getScoreProposal(preferenceId: string) {
  return request<ScoreProposal>(`/preferences/${preferenceId}/score-proposal`);
}

export function applyScoreProposal(preferenceId: string, reason: string) {
  return request<ScoreProposalApplyResult>(`/preferences/${preferenceId}/score-proposal/apply`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
}

export async function deletePreference(preferenceId: string) {
  await request<void>(`/preferences/${preferenceId}`, { method: "DELETE" });
}

export function compareTexts(original: string, revised: string, context: string) {
  return request<ComparisonResult>("/comparisons", {
    method: "POST",
    body: JSON.stringify({ original, revised, context }),
  });
}

export function getAuditEvents() {
  return request<AuditEvent[]>("/audit/events");
}

export function generateText(
  text: string,
  action: GenerationAction,
  context: string,
  intensity: number,
  protectedTerms: string[],
) {
  return request<GenerationResult>("/generation", {
    method: "POST",
    body: JSON.stringify({
      text,
      action,
      context,
      intensity,
      protected_terms: protectedTerms,
    }),
  });
}

export function simulateLab(
  text: string,
  action: GenerationAction,
  context: string,
  intensity: number,
  protectedTerms: string[],
  overrides: LabOverride[],
) {
  return request<LabSimulationResult>("/lab/simulate", {
    method: "POST",
    body: JSON.stringify({
      text,
      action,
      context,
      intensity,
      protected_terms: protectedTerms,
      overrides,
    }),
  });
}
