import type {
  AuditEvent,
  ComparisonResult,
  KnowledgeStatus,
  Preference,
  PreferenceStatus,
  ProfileSummary,
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

export function getProfileSummary() {
  return request<ProfileSummary>("/profiles/default/summary");
}

export function getScores() {
  return request<ScoreVariable[]>("/profiles/default/scores");
}

export function updateScore(variableKey: string, manualAdjustment: number, reason: string) {
  return request<ScoreUpdate>(`/profiles/default/scores/${variableKey}`, {
    method: "PATCH",
    body: JSON.stringify({ manual_adjustment: manualAdjustment, reason }),
  });
}

export function createPreference(text: string) {
  return request<Preference>("/preferences", {
    method: "POST",
    body: JSON.stringify({ text, input_type: "prompt", context: "general" }),
  });
}

export function getPreferences() {
  return request<Preference[]>("/preferences");
}

export function updatePreferenceStatus(preferenceId: string, status: PreferenceStatus) {
  return request<Preference>(`/preferences/${preferenceId}`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export async function deletePreference(preferenceId: string) {
  await request<void>(`/preferences/${preferenceId}`, { method: "DELETE" });
}

export function compareTexts(original: string, revised: string) {
  return request<ComparisonResult>("/comparisons", {
    method: "POST",
    body: JSON.stringify({ original, revised, context: "general" }),
  });
}

export function getAuditEvents() {
  return request<AuditEvent[]>("/audit/events");
}
