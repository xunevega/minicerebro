import type {
  AuditEvent,
  AcceptanceCriterion,
  CerebroAuditCandidate,
  CerebroAuditGate,
  ClosureCondition,
  ComparisonResult,
  ContractBoundary,
  Contradiction,
  DecisionEvaluation,
  DecisionRule,
  ExpectedAnswerLine,
  FeedbackProposal,
  FeedbackStatus,
  GeneratedText,
  GenerationAction,
  GenerationResult,
  KnowledgeCard,
  KnowledgeClaim,
  KnowledgeEvidenceItem,
  KnowledgeExtractionRun,
  KnowledgeExtractionRunCreate,
  KnowledgeIngestionBatch,
  KnowledgeIngestionBatchExport,
  KnowledgeIngestionPolicy,
  KnowledgeIngestionReadiness,
  KnowledgeIndexEntry,
  KnowledgeIndexEntryCreate,
  KnowledgeNode,
  KnowledgeObjectRevision,
  KnowledgePublicationPolicy,
  KnowledgePublicationReadiness,
  KnowledgeProposal,
  KnowledgeProposalCreate,
  KnowledgeQueryContract,
  KnowledgeQueryHistoryItem,
  KnowledgeQueryInterpretation,
  KnowledgeQueryResult,
  KnowledgeQuerySummary,
  KnowledgeRelation,
  KnowledgeSegment,
  KnowledgeSegmentCreate,
  KnowledgeStatus,
  KnowledgeSource,
  KnowledgeSourceCreate,
  KnowledgeSourceEdition,
  KnowledgeSourceEditionCreate,
  KnowledgeVersioningPolicy,
  LabOverride,
  LabSimulationResult,
  ObservabilityMetric,
  Preference,
  PreferenceStatus,
  PersistenceDomain,
  ProfileExport,
  ProfileSummary,
  ProfileStatistics,
  ScoreProposal,
  ScoreProposalApplyResult,
  ScoreUpdate,
  ScoreVariable,
  TechnicalClosureCriterion,
  TechnicalRoadmapPhase,
  V1Screen,
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

function withParams(path: string, params: Record<string, string | undefined>) {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value) {
      search.set(key, value);
    }
  }
  const query = search.toString();
  return query ? `${path}?${query}` : path;
}

export function getKnowledgeCards(version?: string) {
  return request<KnowledgeCard[]>(withParams("/knowledge/cards", { version }));
}

export function getKnowledgeSources(version?: string) {
  return request<KnowledgeSource[]>(withParams("/knowledge/sources", { version }));
}

export function registerKnowledgeSource(payload: KnowledgeSourceCreate) {
  return request<KnowledgeSource>("/knowledge/sources", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getKnowledgeSourceEditions(sourceId: string) {
  return request<KnowledgeSourceEdition[]>(
    `/knowledge/sources/${encodeURIComponent(sourceId)}/editions`,
  );
}

export function registerKnowledgeSourceEdition(
  sourceId: string,
  payload: KnowledgeSourceEditionCreate,
) {
  return request<KnowledgeSourceEdition>(
    `/knowledge/sources/${encodeURIComponent(sourceId)}/editions`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function getKnowledgeEdition(editionId: string) {
  return request<KnowledgeSourceEdition>(
    `/knowledge/editions/${encodeURIComponent(editionId)}`,
  );
}

export function registerKnowledgeIndexEntries(
  editionId: string,
  payload: KnowledgeIndexEntryCreate[],
) {
  return request<KnowledgeIndexEntry[]>(
    `/knowledge/editions/${encodeURIComponent(editionId)}/index`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function getKnowledgeIndexTree(editionId: string) {
  return request<KnowledgeIndexEntry[]>(
    `/knowledge/editions/${encodeURIComponent(editionId)}/index`,
  );
}

export function getKnowledgeIndexEntry(entryId: string) {
  return request<KnowledgeIndexEntry>(`/knowledge/index/${encodeURIComponent(entryId)}`);
}

export function registerKnowledgeSegments(entryId: string, payload: KnowledgeSegmentCreate[]) {
  return request<KnowledgeSegment[]>(
    `/knowledge/index/${encodeURIComponent(entryId)}/segments`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function getKnowledgeSegments(entryId: string) {
  return request<KnowledgeSegment[]>(
    `/knowledge/index/${encodeURIComponent(entryId)}/segments`,
  );
}

export function getKnowledgeSegment(segmentId: string) {
  return request<KnowledgeSegment>(
    `/knowledge/segments/${encodeURIComponent(segmentId)}`,
  );
}

export function registerKnowledgeExtractionRun(
  segmentId: string,
  payload: KnowledgeExtractionRunCreate,
) {
  return request<KnowledgeExtractionRun>(
    `/knowledge/segments/${encodeURIComponent(segmentId)}/extractions`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function getKnowledgeExtractionRuns(segmentId: string) {
  return request<KnowledgeExtractionRun[]>(
    `/knowledge/segments/${encodeURIComponent(segmentId)}/extractions`,
  );
}

export function getKnowledgeExtractionRun(extractionId: string) {
  return request<KnowledgeExtractionRun>(
    `/knowledge/extractions/${encodeURIComponent(extractionId)}`,
  );
}

export function registerKnowledgeProposals(
  extractionId: string,
  payload: KnowledgeProposalCreate[],
) {
  return request<KnowledgeProposal[]>(
    `/knowledge/extractions/${encodeURIComponent(extractionId)}/proposals`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function getKnowledgeProposals(extractionId: string) {
  return request<KnowledgeProposal[]>(
    `/knowledge/extractions/${encodeURIComponent(extractionId)}/proposals`,
  );
}

export function getKnowledgeProposal(proposalId: string) {
  return request<KnowledgeProposal>(
    `/knowledge/proposals/${encodeURIComponent(proposalId)}`,
  );
}

export function getKnowledgeVersioning() {
  return request<KnowledgeVersioningPolicy>("/knowledge/versioning");
}

export function getKnowledgePublication() {
  return request<KnowledgePublicationPolicy>("/knowledge/publication");
}

export function getKnowledgePublicationReadiness(version?: string) {
  return request<KnowledgePublicationReadiness>(
    withParams("/knowledge/publication/readiness", { version }),
  );
}

export function getKnowledgeIngestion() {
  return request<KnowledgeIngestionPolicy>("/knowledge/ingestion");
}

export function getKnowledgeIngestionBatches(sourceId?: string, status?: string) {
  return request<KnowledgeIngestionBatch[]>(
    withParams("/knowledge/ingestion/batches", { source_id: sourceId, status }),
  );
}

export function getKnowledgeIngestionReadiness(sourceId: string, sourceEditionId?: string) {
  return request<KnowledgeIngestionReadiness>(
    withParams("/knowledge/ingestion/readiness", {
      source_id: sourceId,
      source_edition_id: sourceEditionId,
    }),
  );
}

export function getKnowledgeIngestionBatchExport(batchId: string) {
  return request<KnowledgeIngestionBatchExport>(
    `/knowledge/ingestion/batches/${encodeURIComponent(batchId)}/export`,
  );
}

export function getKnowledgeRevisions(version?: string) {
  return request<KnowledgeObjectRevision[]>(withParams("/knowledge/revisions", { version }));
}

export function getKnowledgeNodes(sourceId?: string, version?: string) {
  return request<KnowledgeNode[]>(
    withParams("/knowledge/nodes", { source_id: sourceId, version }),
  );
}

export function getKnowledgeRelations(version?: string) {
  return request<KnowledgeRelation[]>(withParams("/knowledge/relations", { version }));
}

export function getKnowledgeEvidence(nodeId?: string, version?: string) {
  return request<KnowledgeEvidenceItem[]>(
    withParams("/knowledge/evidence", { node_id: nodeId, version }),
  );
}

export function getKnowledgeClaims(cardId?: string, version?: string) {
  return request<KnowledgeClaim[]>(
    withParams("/knowledge/claims", { card_id: cardId, version }),
  );
}

export function queryKnowledge(query: string, version = "knowledge-v0", limit = 5) {
  return request<KnowledgeQueryResult>("/knowledge/query", {
    method: "POST",
    body: JSON.stringify({ query, version, limit }),
  });
}

export function getKnowledgeQueryContract() {
  return request<KnowledgeQueryContract>("/knowledge/query/contract");
}

export function interpretKnowledgeQuery(query: string, version = "knowledge-v0", limit = 5) {
  return request<KnowledgeQueryInterpretation>("/knowledge/query/interpretation", {
    method: "POST",
    body: JSON.stringify({ query, version, limit }),
  });
}

export function getKnowledgeQueryHistory(version = "knowledge-v0", limit = 20) {
  return request<KnowledgeQueryHistoryItem[]>(
    withParams("/knowledge/query-history", { version, limit: String(limit) }),
  );
}

export function getKnowledgeQuerySummary(version = "knowledge-v0") {
  return request<KnowledgeQuerySummary>(withParams("/knowledge/query-summary", { version }));
}

export function getV1Screens() {
  return request<V1Screen[]>("/ui/screens");
}

export function getDecisionRules() {
  return request<DecisionRule[]>("/decision/rules");
}

export function evaluateDecision(context: string) {
  return request<DecisionEvaluation>("/decision/evaluate", {
    method: "POST",
    body: JSON.stringify({ context }),
  });
}

export function getPersistenceStatus() {
  return request<PersistenceDomain[]>("/persistence/status");
}

export function getCerebroAuditCandidates() {
  return request<CerebroAuditCandidate[]>("/cerebro-audit/candidates");
}

export function getAcceptanceCriteria() {
  return request<AcceptanceCriterion[]>("/acceptance/v1");
}

export function getClosureConditions() {
  return request<ClosureCondition[]>("/closure/conditions");
}

export function getExpectedResult() {
  return request<ExpectedAnswerLine[]>("/closure/expected-result");
}

export function getTechnicalClosure() {
  return request<TechnicalClosureCriterion[]>("/closure/technical");
}

export function getContractBoundaries() {
  return request<ContractBoundary[]>("/contract/boundaries");
}

export function getObservabilityStatus() {
  return request<ObservabilityMetric[]>("/observability/status");
}

export function getTechnicalRoadmap() {
  return request<TechnicalRoadmapPhase[]>("/roadmap/technical");
}

export function getCerebroAuditGates() {
  return request<CerebroAuditGate[]>("/cerebro-audit/gates");
}

function withContext(path: string, context: string) {
  const separator = path.includes("?") ? "&" : "?";
  return `${path}${separator}context=${encodeURIComponent(context)}`;
}

export function getProfileSummary() {
  return request<ProfileSummary>("/profiles/default/summary");
}

export function getProfileExport() {
  return request<ProfileExport>("/profiles/default/export");
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

export function compareLabTexts(original: string, revised: string, context: string) {
  return request<ComparisonResult>("/lab/compare", {
    method: "POST",
    body: JSON.stringify({ original, revised, context }),
  });
}

export function createFeedbackProposal(comparisonId: string, context: string) {
  return request<FeedbackProposal>(`/comparisons/${comparisonId}/feedback`, {
    method: "POST",
    body: JSON.stringify({ context }),
  });
}

export function getFeedbackProposals() {
  return request<FeedbackProposal[]>("/feedback/proposals");
}

export function decideFeedbackProposal(
  proposalId: string,
  status: Exclude<FeedbackStatus, "proposed">,
  reason: string,
  variableKeys?: string[],
) {
  return request<FeedbackProposal>(`/feedback/proposals/${proposalId}`, {
    method: "PATCH",
    body: JSON.stringify({ status, reason, variable_keys: variableKeys }),
  });
}

export function getAuditEvents(eventType?: string, entityType?: string, entityId?: string) {
  return request<AuditEvent[]>(
    withParams("/audit/events", { event_type: eventType, entity_type: entityType, entity_id: entityId }),
  );
}

export function getGeneratedTexts(context: string) {
  return request<GeneratedText[]>(withContext("/texts", context));
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
