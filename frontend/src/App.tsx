import { useEffect, useMemo, useState } from "react";
import {
  BookOpen,
  Brain,
  ClipboardCheck,
  Database,
  Flag,
  FilePenLine,
  FlaskConical,
  GitCompare,
  History,
  LayoutDashboard,
  PenLine,
  Route,
  Search,
  ShieldCheck,
  SlidersHorizontal,
} from "lucide-react";
import {
  applyProfileKnowledgeCardScoreProposal,
  applyScoreProposal,
  compareLabTexts,
  compareTexts,
  createKnowledgeCandidate,
  createPreference,
  createFeedbackProposal,
  deletePreference,
  decideFeedbackProposal,
  evaluateDecision,
  getAcceptanceCriteria,
  getAuditEvents,
  getCerebroAuditGates,
  getCerebroAuditCandidates,
  getClosureConditions,
  getContractBoundaries,
  getContradictions,
  getDecisionRules,
  getExpectedResult,
  getFeedbackProposals,
  getGeneratedTexts,
  generateText,
  getKnowledgeCards,
  getKnowledgeClaims,
  getKnowledgeEvidence,
  getKnowledgeNodes,
  getKnowledgeProposals,
  getKnowledgePublicationReadiness,
  getKnowledgeQueryHistory,
  getKnowledgeQuerySummary,
  getKnowledgeStatus,
  getKnowledgeSourceIngestionStatuses,
  getKnowledgeSources,
  getKnowledgeVersions,
  getPersistenceStatus,
  getPreferences,
  getProfileExport,
  getProfileKnowledgeCardScoreProposal,
  getProfileKnowledgeCards,
  getProfileSummary,
  getProfileStatistics,
  getScoreProposal,
  getScores,
  getObservabilityStatus,
  getTechnicalClosure,
  getTechnicalRoadmap,
  getV1Screens,
  approveKnowledgeProposal,
  queryKnowledge,
  publishKnowledgeVersion,
  registerKnowledgeExtractionRun,
  registerKnowledgeIndexEntries,
  registerKnowledgeProposals,
  registerKnowledgeSegments,
  registerKnowledgeSourceEdition,
  rejectKnowledgeProposal,
  saveProfileKnowledgeCard,
  simulateLab,
  updatePreferenceStatus,
  updateScore,
} from "./services/api";
import type {
  AuditEvent,
  AcceptanceCriterion,
  CerebroAuditGate,
  CerebroAuditCandidate,
  ClosureCondition,
  ComparisonResult,
  ContractBoundary,
  Contradiction,
  DecisionEvaluation,
  DecisionRule,
  ExpectedAnswerLine,
  FeedbackProposal,
  GeneratedText,
  GenerationAction,
  GenerationResult,
  KnowledgeCard,
  KnowledgeClaim,
  KnowledgeEvidenceItem,
  KnowledgeExtractionRun,
  KnowledgeIndexEntry,
  KnowledgeNode,
  KnowledgePublicationReadiness,
  KnowledgeProposal,
  KnowledgeQueryHistoryItem,
  KnowledgeQueryResult,
  KnowledgeQuerySummary,
  KnowledgeSegment,
  KnowledgeStatus,
  KnowledgeSourceEdition,
  KnowledgeSource,
  KnowledgeSourceIngestionStatus,
  KnowledgeVersion,
  LabSimulationResult,
  ObservabilityMetric,
  Preference,
  PreferenceStatus,
  PersistenceDomain,
  ProfileExport,
  ProfileKnowledgeCard,
  ProfileKnowledgeCardScoreProposal,
  ProfileKnowledgeCardStance,
  ProfileSummary,
  ProfileStatistics,
  ScoreProposal,
  ScoreVariable,
  TechnicalClosureCriterion,
  TechnicalRoadmapPhase,
  V1Screen,
} from "./types/api";

const tabs = [
  { id: "knowledge", label: "Lo que sabe la app", icon: BookOpen },
  { id: "preferences", label: "Preferencias", icon: PenLine },
  { id: "profile", label: "Ficha usuario", icon: Brain },
  { id: "scoring", label: "Puntuacion", icon: SlidersHorizontal },
  { id: "editor", label: "Escribir", icon: FilePenLine },
  { id: "lab", label: "Probar cambios", icon: FlaskConical },
  { id: "compare", label: "Comparar", icon: GitCompare },
  { id: "rules", label: "Reglas de decision", icon: ShieldCheck },
  { id: "persistence", label: "Datos guardados", icon: Database },
  { id: "cerebro", label: "Revision Cerebro", icon: Search },
  { id: "acceptance", label: "Aceptacion", icon: ClipboardCheck },
  { id: "closure", label: "Cierre V1", icon: Flag },
  { id: "roadmap", label: "Plan tecnico", icon: Route },
  { id: "screens", label: "Mapa de pantallas", icon: LayoutDashboard },
  { id: "audit", label: "Historial", icon: History },
] as const;

const contexts = ["general", "ensayo", "articulo", "tecnico", "publicitario", "narrativa"] as const;
const auditEventFilters = [
  { label: "Todos", eventType: "", entityType: "" },
  {
    label: "Consultas de conocimiento",
    eventType: "knowledge.query.executed",
    entityType: "knowledge_version",
  },
  { label: "Preferencias", eventType: "preference.created", entityType: "preference" },
  { label: "Textos generados", eventType: "text.generated", entityType: "generated_text" },
] as const;

const userKnowledgeCardStances: Array<{ value: ProfileKnowledgeCardStance; label: string }> = [
  { value: "liked", label: "Me gusta" },
  { value: "kept", label: "Mantener" },
  { value: "changed", label: "Cambiar" },
  { value: "dismissed", label: "Descartar" },
];

type TabId = (typeof tabs)[number]["id"];

const mainSections: Array<{
  id: string;
  label: string;
  description: string;
  icon: (typeof tabs)[number]["icon"];
  defaultTab: TabId;
  tabs: TabId[];
}> = [
  {
    id: "write",
    label: "Escribir",
    description: "Crear, corregir, comparar y probar textos.",
    icon: FilePenLine,
    defaultTab: "editor",
    tabs: ["editor", "compare", "lab"],
  },
  {
    id: "profile",
    label: "Mi perfil",
    description: "Preferencias, puntuacion y ficha personal.",
    icon: Brain,
    defaultTab: "preferences",
    tabs: ["preferences", "scoring", "profile"],
  },
  {
    id: "knowledge",
    label: "Conocimiento",
    description: "Fuentes, fichas, consulta y estado de ingestion.",
    icon: BookOpen,
    defaultTab: "knowledge",
    tabs: ["knowledge"],
  },
  {
    id: "system",
    label: "Sistema",
    description: "Diagnostico, historial, cierre y contrato tecnico.",
    icon: Database,
    defaultTab: "audit",
    tabs: ["audit", "persistence", "screens", "rules", "closure", "roadmap", "cerebro", "acceptance"],
  },
];

export function App() {
  const [active, setActive] = useState<TabId>("knowledge");
  const [activeContext, setActiveContext] = useState("general");
  const [knowledge, setKnowledge] = useState<KnowledgeStatus | null>(null);
  const [knowledgeCards, setKnowledgeCards] = useState<KnowledgeCard[]>([]);
  const [knowledgeSources, setKnowledgeSources] = useState<KnowledgeSource[]>([]);
  const [knowledgeSourceIngestionStatuses, setKnowledgeSourceIngestionStatuses] = useState<
    KnowledgeSourceIngestionStatus[]
  >([]);
  const [knowledgeNodes, setKnowledgeNodes] = useState<KnowledgeNode[]>([]);
  const [knowledgeEvidence, setKnowledgeEvidence] = useState<KnowledgeEvidenceItem[]>([]);
  const [knowledgeClaims, setKnowledgeClaims] = useState<KnowledgeClaim[]>([]);
  const [knowledgeVersions, setKnowledgeVersions] = useState<KnowledgeVersion[]>([]);
  const [selectedKnowledgeVersion, setSelectedKnowledgeVersion] = useState("latest");
  const [loadedKnowledgeVersion, setLoadedKnowledgeVersion] = useState("knowledge-v3");
  const [manualIngestionSourceId, setManualIngestionSourceId] = useState("");
  const [manualIngestionEdition, setManualIngestionEdition] =
    useState<KnowledgeSourceEdition | null>(null);
  const [manualIngestionIndexEntry, setManualIngestionIndexEntry] =
    useState<KnowledgeIndexEntry | null>(null);
  const [manualIngestionSegment, setManualIngestionSegment] = useState<KnowledgeSegment | null>(null);
  const [manualIngestionExtraction, setManualIngestionExtraction] =
    useState<KnowledgeExtractionRun | null>(null);
  const [manualIngestionProposals, setManualIngestionProposals] = useState<KnowledgeProposal[]>([]);
  const [manualIngestionBusy, setManualIngestionBusy] = useState(false);
  const [candidateVersionId, setCandidateVersionId] = useState(`knowledge-candidate-${Date.now().toString(36)}`);
  const [candidateBaseVersion, setCandidateBaseVersion] = useState("knowledge-v3");
  const [candidateAuthor, setCandidateAuthor] = useState("minicerebro-ui");
  const [candidateReason, setCandidateReason] = useState(
    "Candidato creado desde la interfaz para revision de publicacion.",
  );
  const [publicationReadiness, setPublicationReadiness] =
    useState<KnowledgePublicationReadiness | null>(null);
  const [publicationTargetVersion, setPublicationTargetVersion] = useState("");
  const [publicationBusy, setPublicationBusy] = useState(false);
  const [knowledgeQuery, setKnowledgeQuery] = useState("complemento directo");
  const [knowledgeQueryLimit, setKnowledgeQueryLimit] = useState(5);
  const [knowledgeResult, setKnowledgeResult] = useState<KnowledgeQueryResult | null>(null);
  const [knowledgeQueryHistory, setKnowledgeQueryHistory] = useState<KnowledgeQueryHistoryItem[]>([]);
  const [knowledgeQuerySummary, setKnowledgeQuerySummary] = useState<KnowledgeQuerySummary | null>(null);
  const [knowledgeQueryHistoryLimit, setKnowledgeQueryHistoryLimit] = useState(20);
  const [selectedKnowledgeQueryEventId, setSelectedKnowledgeQueryEventId] = useState<number | null>(
    null,
  );
  const [selectedKnowledgeCardId, setSelectedKnowledgeCardId] = useState<string | null>(null);
  const [summary, setSummary] = useState<ProfileSummary | null>(null);
  const [profileExport, setProfileExport] = useState<ProfileExport | null>(null);
  const [profileKnowledgeCards, setProfileKnowledgeCards] = useState<ProfileKnowledgeCard[]>([]);
  const [profileKnowledgeCardStance, setProfileKnowledgeCardStance] =
    useState<ProfileKnowledgeCardStance>("kept");
  const [profileKnowledgeCardScore, setProfileKnowledgeCardScore] = useState(700);
  const [profileKnowledgeCardFeedback, setProfileKnowledgeCardFeedback] = useState(
    "Mantener esta ficha como referencia personal.",
  );
  const [profileKnowledgeCardMaintained, setProfileKnowledgeCardMaintained] =
    useState("definicion, precision");
  const [profileKnowledgeCardChanges, setProfileKnowledgeCardChanges] = useState("");
  const [profileKnowledgeCardNotes, setProfileKnowledgeCardNotes] = useState("");
  const [profileKnowledgeCardProposal, setProfileKnowledgeCardProposal] =
    useState<ProfileKnowledgeCardScoreProposal | null>(null);
  const [profileKnowledgeCardSaved, setProfileKnowledgeCardSaved] =
    useState<ProfileKnowledgeCard | null>(null);
  const [statistics, setStatistics] = useState<ProfileStatistics | null>(null);
  const [contradictions, setContradictions] = useState<Contradiction[]>([]);
  const [scores, setScores] = useState<ScoreVariable[]>([]);
  const [preferenceText, setPreferenceText] = useState("Me gusta un estilo sobrio, preciso y con ritmo.");
  const [preference, setPreference] = useState<Preference | null>(null);
  const [preferences, setPreferences] = useState<Preference[]>([]);
  const [scoreProposal, setScoreProposal] = useState<ScoreProposal | null>(null);
  const [original, setOriginal] = useState("Este texto explica una idea de manera general.");
  const [revised, setRevised] = useState("Este texto explica una idea con mas precision y menos rodeo.");
  const [comparison, setComparison] = useState<ComparisonResult | null>(null);
  const [feedbackProposals, setFeedbackProposals] = useState<FeedbackProposal[]>([]);
  const [activeFeedback, setActiveFeedback] = useState<FeedbackProposal | null>(null);
  const [screens, setScreens] = useState<V1Screen[]>([]);
  const [decisionRules, setDecisionRules] = useState<DecisionRule[]>([]);
  const [decisionEvaluation, setDecisionEvaluation] = useState<DecisionEvaluation | null>(null);
  const [persistenceDomains, setPersistenceDomains] = useState<PersistenceDomain[]>([]);
  const [generatedTexts, setGeneratedTexts] = useState<GeneratedText[]>([]);
  const [cerebroCandidates, setCerebroCandidates] = useState<CerebroAuditCandidate[]>([]);
  const [cerebroGates, setCerebroGates] = useState<CerebroAuditGate[]>([]);
  const [acceptanceCriteria, setAcceptanceCriteria] = useState<AcceptanceCriterion[]>([]);
  const [closureConditions, setClosureConditions] = useState<ClosureCondition[]>([]);
  const [expectedResult, setExpectedResult] = useState<ExpectedAnswerLine[]>([]);
  const [technicalClosure, setTechnicalClosure] = useState<TechnicalClosureCriterion[]>([]);
  const [contractBoundaries, setContractBoundaries] = useState<ContractBoundary[]>([]);
  const [observability, setObservability] = useState<ObservabilityMetric[]>([]);
  const [roadmap, setRoadmap] = useState<TechnicalRoadmapPhase[]>([]);
  const [editorText, setEditorText] = useState("Escribe aqui una idea o un texto para trabajar.");
  const [editorAction, setEditorAction] = useState<GenerationAction>("rewrite");
  const [editorIntensity, setEditorIntensity] = useState(500);
  const [protectedTerms, setProtectedTerms] = useState("");
  const [generation, setGeneration] = useState<GenerationResult | null>(null);
  const [labText, setLabText] = useState("Prueba aqui una frase antes de consolidar cambios.");
  const [labAction, setLabAction] = useState<GenerationAction>("rewrite");
  const [labIntensity, setLabIntensity] = useState(500);
  const [labOverrideKey, setLabOverrideKey] = useState("");
  const [labOverrideDelta, setLabOverrideDelta] = useState(0);
  const [labResult, setLabResult] = useState<LabSimulationResult | null>(null);
  const [labComparisonText, setLabComparisonText] = useState(
    "Prueba aqui una variante para compararla sin guardar.",
  );
  const [labComparison, setLabComparison] = useState<ComparisonResult | null>(null);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [auditFilter, setAuditFilter] = useState("Todos");
  const [scoreReason, setScoreReason] = useState("Ajuste manual revisado en la pantalla de scoring.");
  const [savingScoreKey, setSavingScoreKey] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const activeTab = tabs.find((tab) => tab.id === active) ?? tabs[0];
  const activeSection =
    mainSections.find((section) => section.tabs.includes(active)) ?? mainSections[2];
  const activeSectionTabs = tabs.filter((tab) => activeSection.tabs.includes(tab.id));
  const latestPublishedKnowledgeVersion =
    [...knowledgeVersions].reverse().find((version) => version.status === "published")?.id ??
    knowledge?.version ??
    "knowledge-v0";
  const effectiveKnowledgeVersion =
    selectedKnowledgeVersion === "latest" ? latestPublishedKnowledgeVersion : selectedKnowledgeVersion;

  useEffect(() => {
    getKnowledgeStatus()
      .then((knowledgeData) =>
        Promise.all([
          Promise.resolve(knowledgeData),
          getKnowledgeVersions(),
          getKnowledgeSourceIngestionStatuses(),
          getProfileSummary(),
          getProfileStatistics(activeContext),
          getContradictions(activeContext),
          getScores(activeContext),
          getProfileKnowledgeCards(),
          getPreferences(activeContext),
          getAuditEvents(),
          getFeedbackProposals(),
          getV1Screens(),
          getDecisionRules(),
          evaluateDecision(activeContext),
          getPersistenceStatus(),
          getGeneratedTexts(activeContext),
          getCerebroAuditCandidates(),
          getAcceptanceCriteria(),
          getCerebroAuditGates(),
          getClosureConditions(),
          getExpectedResult(),
          getTechnicalClosure(),
          getContractBoundaries(),
          getObservabilityStatus(),
          getTechnicalRoadmap(),
        ]),
      )
      .then(
        ([
          knowledgeData,
          versionData,
          sourceIngestionStatusData,
          summaryData,
          statisticsData,
          contradictionData,
          scoreData,
          profileKnowledgeCardData,
          preferenceData,
          auditData,
          feedbackData,
          screenData,
          rulesData,
          decisionData,
          persistenceData,
          textData,
          cerebroData,
          acceptanceData,
          gateData,
          closureData,
          expectedData,
          technicalClosureData,
          boundaryData,
          observabilityData,
          roadmapData,
        ]) => {
        setKnowledge(knowledgeData);
        setKnowledgeVersions(versionData);
        setKnowledgeSourceIngestionStatuses(sourceIngestionStatusData);
        setSummary(summaryData);
        setStatistics(statisticsData);
        setContradictions(contradictionData);
        setScores(scoreData);
        setProfileKnowledgeCards(profileKnowledgeCardData);
        setPreferences(preferenceData);
        setAuditEvents(auditData);
        setFeedbackProposals(feedbackData);
        setScreens(screenData);
        setDecisionRules(rulesData);
        setDecisionEvaluation(decisionData);
        setPersistenceDomains(persistenceData);
        setGeneratedTexts(textData);
        setCerebroCandidates(cerebroData);
        setAcceptanceCriteria(acceptanceData);
        setCerebroGates(gateData);
        setClosureConditions(closureData);
        setExpectedResult(expectedData);
        setTechnicalClosure(technicalClosureData);
        setContractBoundaries(boundaryData);
        setObservability(observabilityData);
        setRoadmap(roadmapData);
        },
      )
      .catch((nextError: Error) => setError(nextError.message));
  }, [activeContext]);

  useEffect(() => {
    if (!knowledge) return;
    setError(null);
    Promise.all([
      getKnowledgeCards(effectiveKnowledgeVersion),
      getKnowledgeSources(effectiveKnowledgeVersion),
      getKnowledgeNodes(undefined, effectiveKnowledgeVersion),
      getKnowledgeEvidence(undefined, effectiveKnowledgeVersion),
      getKnowledgeClaims(undefined, effectiveKnowledgeVersion),
      getKnowledgeQueryHistory(effectiveKnowledgeVersion),
      getKnowledgeQuerySummary(effectiveKnowledgeVersion),
    ])
      .then(
        ([
          cardData,
          sourceData,
          nodeData,
          evidenceData,
          claimData,
          queryHistoryData,
          querySummaryData,
        ]) => {
          setKnowledgeCards(cardData);
          setKnowledgeSources(sourceData);
          setKnowledgeNodes(nodeData);
          setKnowledgeEvidence(evidenceData);
          setKnowledgeClaims(claimData);
          setKnowledgeQueryHistory(queryHistoryData);
          setKnowledgeQuerySummary(querySummaryData);
          setLoadedKnowledgeVersion(effectiveKnowledgeVersion);
          if (selectedKnowledgeCardId && !cardData.some((card) => card.id === selectedKnowledgeCardId)) {
            setSelectedKnowledgeCardId(null);
          }
        },
      )
      .catch((nextError: Error) => setError(nextError.message));
  }, [effectiveKnowledgeVersion, knowledge]);

  const averageConfidence = useMemo(() => {
    if (scores.length === 0) return 0;
    return scores.reduce((total, item) => total + item.confidence, 0) / scores.length;
  }, [scores]);

  const cardById = useMemo(
    () => new Map(knowledgeCards.map((card) => [card.id, card])),
    [knowledgeCards],
  );
  const sourceById = useMemo(
    () => new Map(knowledgeSources.map((source) => [source.id, source])),
    [knowledgeSources],
  );
  const sourceIngestionStatusById = useMemo(
    () => new Map(knowledgeSourceIngestionStatuses.map((status) => [status.source_id, status])),
    [knowledgeSourceIngestionStatuses],
  );
  const nodeById = useMemo(
    () => new Map(knowledgeNodes.map((node) => [node.id, node])),
    [knowledgeNodes],
  );
  const evidenceById = useMemo(
    () => new Map(knowledgeEvidence.map((item) => [item.id, item])),
    [knowledgeEvidence],
  );
  const nodesBySource = useMemo(
    () => groupBy(knowledgeNodes, (node) => node.source_id),
    [knowledgeNodes],
  );
  const evidenceByNode = useMemo(
    () => groupBy(knowledgeEvidence, (item) => item.node_id),
    [knowledgeEvidence],
  );
  const claimsByEvidence = useMemo(
    () => groupBy(knowledgeClaims, (claim) => claim.evidence_id),
    [knowledgeClaims],
  );
  const claimsByCard = useMemo(
    () => groupBy(knowledgeClaims, (claim) => claim.card_id),
    [knowledgeClaims],
  );
  const selectedKnowledgeCard = selectedKnowledgeCardId
    ? (cardById.get(selectedKnowledgeCardId) ?? null)
    : null;
  const selectedProfileKnowledgeCard = selectedKnowledgeCard
    ? (profileKnowledgeCards.find(
        (item) =>
          item.card_id === selectedKnowledgeCard.id &&
          item.knowledge_version === selectedKnowledgeCard.version,
      ) ?? null)
    : null;
  const pendingKnowledgeValidationCount = useMemo(
    () =>
      [...knowledgeCards, ...knowledgeClaims, ...knowledgeEvidence].filter(
        (item) => validationLabel(item.confidence) === "Validacion pendiente",
      ).length,
    [knowledgeCards, knowledgeClaims, knowledgeEvidence],
  );
  const registeredOnlySourceCount = useMemo(
    () => knowledgeSourceIngestionStatuses.filter((item) => !item.is_ingested).length,
    [knowledgeSourceIngestionStatuses],
  );
  const ingestedSourceCount = useMemo(
    () => knowledgeSourceIngestionStatuses.filter((item) => item.is_ingested).length,
    [knowledgeSourceIngestionStatuses],
  );
  const publishedSourceCount = useMemo(
    () => knowledgeSourceIngestionStatuses.filter((item) => item.is_published).length,
    [knowledgeSourceIngestionStatuses],
  );
  const ingestionPhaseCounts = useMemo(
    () =>
      INGESTION_PHASE_ORDER.map((phase) => ({
        phase,
        label: ingestionPhaseLabel(phase),
        count: knowledgeSourceIngestionStatuses.filter((item) => item.current_phase === phase).length,
      })).filter((item) => item.count > 0),
    [knowledgeSourceIngestionStatuses],
  );
  const orderedIngestionStatuses = useMemo(
    () =>
      [...knowledgeSourceIngestionStatuses].sort((left, right) => {
        const leftRank = INGESTION_PHASE_ORDER.indexOf(left.current_phase);
        const rightRank = INGESTION_PHASE_ORDER.indexOf(right.current_phase);
        const normalizedLeftRank = leftRank === -1 ? INGESTION_PHASE_ORDER.length : leftRank;
        const normalizedRightRank = rightRank === -1 ? INGESTION_PHASE_ORDER.length : rightRank;
        return normalizedLeftRank - normalizedRightRank || left.source_name.localeCompare(right.source_name);
      }),
    [knowledgeSourceIngestionStatuses],
  );
  const manualIngestionStatus =
    knowledgeSourceIngestionStatuses.find((item) => item.source_id === manualIngestionSourceId) ??
    knowledgeSourceIngestionStatuses.find((item) => !item.is_ingested) ??
    knowledgeSourceIngestionStatuses[0] ??
    null;
  const manualIngestionSourceIdValue = manualIngestionStatus?.source_id ?? "";
  const candidateVersions = knowledgeVersions.filter((version) =>
    ["candidate", "validated"].includes(version.status),
  );
  const manualProposalTargetVersion = candidateVersions.some(
    (version) => version.id === publicationTargetVersion,
  )
    ? publicationTargetVersion
    : "candidate-pending";
  const publishableReadiness =
    publicationReadiness?.version === publicationTargetVersion && publicationReadiness.publishable;

  async function refreshAuditEvents(filterLabel = auditFilter) {
    setAuditEvents(await loadAuditEvents(filterLabel, loadedKnowledgeVersion));
  }

  function commaList(value: string) {
    return value
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
  }

  useEffect(() => {
    if (!selectedKnowledgeCard) return;
    if (selectedProfileKnowledgeCard) {
      setProfileKnowledgeCardStance(selectedProfileKnowledgeCard.stance);
      setProfileKnowledgeCardScore(selectedProfileKnowledgeCard.user_score);
      setProfileKnowledgeCardFeedback(selectedProfileKnowledgeCard.feedback);
      setProfileKnowledgeCardMaintained(selectedProfileKnowledgeCard.maintained_elements.join(", "));
      setProfileKnowledgeCardChanges(selectedProfileKnowledgeCard.change_requests.join(", "));
      setProfileKnowledgeCardNotes(selectedProfileKnowledgeCard.notes);
      setProfileKnowledgeCardSaved(selectedProfileKnowledgeCard);
    } else {
      setProfileKnowledgeCardStance("kept");
      setProfileKnowledgeCardScore(700);
      setProfileKnowledgeCardFeedback("Mantener esta ficha como referencia personal.");
      setProfileKnowledgeCardMaintained("definicion, precision");
      setProfileKnowledgeCardChanges("");
      setProfileKnowledgeCardNotes("");
      setProfileKnowledgeCardSaved(null);
    }
    setProfileKnowledgeCardProposal(null);
  }, [selectedKnowledgeCard?.id, selectedKnowledgeCard?.version]);

  async function handlePreference() {
    setError(null);
    try {
      const created = await createPreference(preferenceText, activeContext);
      setPreference(created);
      setPreferences((current) => [created, ...current]);
      setSummary(await getProfileSummary());
      await refreshAuditEvents();
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  async function handleKnowledgeQuery() {
    setError(null);
    try {
      setKnowledgeResult(
        await queryKnowledge(knowledgeQuery, selectedKnowledgeVersion, knowledgeQueryLimit),
      );
      setKnowledgeQueryHistory(
        await getKnowledgeQueryHistory(effectiveKnowledgeVersion, knowledgeQueryHistoryLimit),
      );
      setKnowledgeQuerySummary(await getKnowledgeQuerySummary(effectiveKnowledgeVersion));
      await refreshAuditEvents();
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  async function handleAuditFilter(nextFilter: string) {
    setError(null);
    setAuditFilter(nextFilter);
    try {
      await refreshAuditEvents(nextFilter);
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  async function handleKnowledgeQueryHistoryLimit(nextLimit: number) {
    setError(null);
    setKnowledgeQueryHistoryLimit(nextLimit);
    setSelectedKnowledgeQueryEventId(null);
    try {
      setKnowledgeQueryHistory(await getKnowledgeQueryHistory(effectiveKnowledgeVersion, nextLimit));
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  function handleExploreKnowledgeVersion(version: string) {
    setActive("knowledge");
    setError(null);
    setSelectedKnowledgeVersion(version);
  }

  async function handleCreateManualIngestionFlow() {
    if (!manualIngestionSourceIdValue) {
      setError("No hay fuente disponible para ingestion manual.");
      return;
    }
    setManualIngestionBusy(true);
    setError(null);
    try {
      const suffix = Date.now().toString(36);
      const sourceId = manualIngestionSourceIdValue;
      const sourceName = manualIngestionStatus?.source_name ?? sourceId;
      const editionId = `${sourceId}:ui-${suffix}`;
      const entryId = `${editionId}:index-1`;
      const segmentId = `${entryId}:segment-1`;
      const nodeId = `${sourceId}-ui-node-${suffix}`;
      const cardId = `${sourceId}-ui-card-${suffix}`;
      const evidenceId = `${sourceId}-ui-evidence-${suffix}`;
      const claimId = `${sourceId}-ui-claim-${suffix}`;
      const relationId = `${sourceId}-ui-relation-${suffix}`;
      const edition = await registerKnowledgeSourceEdition(sourceId, {
        id: editionId,
        source_id: sourceId,
        title: `${sourceName} - edicion manual UI`,
        edition_label: "registro manual UI",
        publication_year: "2026",
        publisher: "pendiente",
        isbn: `sin-isbn-${suffix}`,
        language: "es",
        format: "digital",
        access_location: "registro manual desde interfaz",
        rights_status: "pendiente",
        status: "registered",
        notes: "Edicion creada desde el flujo manual de ingestion; no inicia publicacion.",
        structure: ["entrada manual"],
        locator_system: ["ui"],
      });
      const [indexEntry] = await registerKnowledgeIndexEntries(edition.id, [
        {
          id: entryId,
          edition_id: edition.id,
          level: 1,
          order: 1,
          title: "Entrada documental manual",
          locator: "ui:1",
          page_start: null,
          page_end: null,
          status: "available",
        },
      ]);
      const [segment] = await registerKnowledgeSegments(indexEntry.id, [
        {
          id: segmentId,
          index_entry_id: indexEntry.id,
          segment_type: "manual_excerpt",
          title: "Segmento manual inicial",
          text: `Segmento de prueba para iniciar ingestion controlada de ${sourceName}.`,
          order: 1,
          start_locator: "ui:1",
          end_locator: "ui:1",
          language: "es",
          status: "available",
        },
      ]);
      const extraction = await registerKnowledgeExtractionRun(segment.id, {
        extractor_type: "deterministic",
        extractor_name: "manual-ui",
        extractor_version: "1.0",
        configuration: { mode: "manual_ui_minimum" },
        status: "completed",
        knowledge_version: null,
      });
      const proposals = await registerKnowledgeProposals(extraction.id, [
        {
          proposal_type: "node",
          title: "Nodo candidato manual",
          payload: {
            id: nodeId,
            source_id: sourceId,
            node_type: "concepto",
            title: "Nodo candidato manual",
            summary: "Concepto candidato creado desde una ingestion manual controlada.",
            canonical_name: "Nodo candidato manual",
            primary_branch: "lengua espanola",
            secondary_branch: "ingestion manual",
            short_definition: "Concepto candidato pendiente de revision editorial.",
            long_definition:
              "Concepto candidato generado por el flujo manual de ingestion de Minicerebro.",
            aliases: [],
            version: manualProposalTargetVersion,
          },
          rationale: "Propuesta registrada para probar revision sin publicar conocimiento.",
          confidence: 0.5,
          source_locator: "ui:1",
        },
        {
          proposal_type: "card",
          title: "Ficha candidata manual",
          payload: {
            id: cardId,
            card_type: "concept",
            name: "Ficha candidata manual",
            definition: "Ficha candidata creada desde ingestion manual revisable.",
            payload: {
              source_node_id: nodeId,
              source_id: sourceId,
              extraction_id: extraction.id,
            },
            version: manualProposalTargetVersion,
          },
          rationale: "Ficha propuesta para agrupar un claim revisable.",
          confidence: 0.5,
          source_locator: "ui:1",
        },
        {
          proposal_type: "evidence",
          title: "Evidencia candidata manual",
          payload: {
            id: evidenceId,
            node_id: nodeId,
            source_id: sourceId,
            source_edition_id: edition.id,
            evidence_type: "manual_excerpt",
            locator: {
              edition: edition.id,
              unit: indexEntry.id,
              locator: "ui:1",
              url: null,
            },
            reference: "ui:1",
            excerpt: `Segmento de prueba para iniciar ingestion controlada de ${sourceName}.`,
            context: "manual_ui_ingestion",
            confidence_level: 3,
            version: manualProposalTargetVersion,
          },
          rationale: "Evidencia propuesta desde el segmento documental registrado.",
          confidence: 0.5,
          source_locator: "ui:1",
        },
        {
          proposal_type: "claim",
          title: "Claim candidato manual",
          payload: {
            id: claimId,
            evidence_id: evidenceId,
            card_id: cardId,
            statement: "La ingestion manual crea conocimiento solo tras revision explicita.",
            claim_type: "process",
            node_id: nodeId,
            related_node_ids: [],
            domain: "knowledge.ingestion",
            scope: { language: "es", context: "manual_ui" },
            version: manualProposalTargetVersion,
          },
          rationale: "Claim propuesto para cerrar el recorrido nodo-evidencia-ficha.",
          confidence: 0.5,
          source_locator: "ui:1",
        },
        {
          proposal_type: "relation",
          title: "Relacion candidata manual",
          payload: {
            id: relationId,
            source_entity_type: "claim",
            source_entity_id: claimId,
            target_entity_type: "evidence",
            target_entity_id: evidenceId,
            relation_type: "depende_de",
            direction: "outgoing",
            cardinality: "N:1",
            weight: 1,
            context: "manual_ui_ingestion",
            version: manualProposalTargetVersion,
          },
          rationale: "Relacion propuesta para conservar trazabilidad del claim.",
          confidence: 0.5,
          source_locator: "ui:1",
        },
      ]);
      setManualIngestionEdition(edition);
      setManualIngestionIndexEntry(indexEntry);
      setManualIngestionSegment(segment);
      setManualIngestionExtraction(extraction);
      setManualIngestionProposals(proposals);
      setKnowledgeSourceIngestionStatuses(await getKnowledgeSourceIngestionStatuses());
      await refreshAuditEvents();
    } catch (nextError) {
      setError((nextError as Error).message);
    } finally {
      setManualIngestionBusy(false);
    }
  }

  async function handleLoadManualProposals() {
    if (!manualIngestionExtraction) return;
    setError(null);
    try {
      setManualIngestionProposals(await getKnowledgeProposals(manualIngestionExtraction.id));
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  async function handleManualProposalDecision(proposal: KnowledgeProposal, action: "approve" | "reject") {
    setError(null);
    try {
      const decide = action === "approve" ? approveKnowledgeProposal : rejectKnowledgeProposal;
      const updated = await decide(proposal.id, {
        reviewer: "minicerebro-ui",
        reason:
          action === "approve"
            ? "Revision manual desde la interfaz; no publica conocimiento."
            : "Rechazo manual desde la interfaz; no modifica conocimiento estable.",
      });
      setManualIngestionProposals((current) =>
        current.map((item) => (item.id === updated.id ? updated : item)),
      );
      setKnowledgeSourceIngestionStatuses(await getKnowledgeSourceIngestionStatuses());
      await refreshAuditEvents();
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  async function handleCheckPublicationReadiness(version = publicationTargetVersion) {
    if (!version) {
      setError("Selecciona una version candidata para comprobar publicacion.");
      return null;
    }
    setError(null);
    try {
      const readiness = await getKnowledgePublicationReadiness(version);
      setPublicationReadiness(readiness);
      return readiness;
    } catch (nextError) {
      setError((nextError as Error).message);
      return null;
    }
  }

  async function handleCreateCandidateVersion() {
    setPublicationBusy(true);
    setError(null);
    try {
      const candidate = await createKnowledgeCandidate({
        id: candidateVersionId,
        base_version: candidateBaseVersion,
        author: candidateAuthor,
        reason: candidateReason,
      });
      const versions = await getKnowledgeVersions();
      setKnowledgeVersions(versions);
      setPublicationTargetVersion(candidate.id);
      setSelectedKnowledgeVersion(candidate.id);
      setCandidateVersionId(`knowledge-candidate-${Date.now().toString(36)}`);
      setPublicationReadiness(await getKnowledgePublicationReadiness(candidate.id));
      await refreshAuditEvents();
    } catch (nextError) {
      setError((nextError as Error).message);
    } finally {
      setPublicationBusy(false);
    }
  }

  async function handlePublishCandidateVersion() {
    if (!publicationTargetVersion) {
      setError("Selecciona una version candidata para publicar.");
      return;
    }
    setPublicationBusy(true);
    setError(null);
    try {
      const readiness =
        publicationReadiness?.version === publicationTargetVersion
          ? publicationReadiness
          : await getKnowledgePublicationReadiness(publicationTargetVersion);
      setPublicationReadiness(readiness);
      if (!readiness.publishable) {
        setError(`La version no es publicable: ${readiness.blockers.join(", ")}`);
        return;
      }
      const published = await publishKnowledgeVersion({
        version: publicationTargetVersion,
        author: candidateAuthor,
        reason: candidateReason,
      });
      const versions = await getKnowledgeVersions();
      setKnowledgeVersions(versions);
      setSelectedKnowledgeVersion(published.id);
      setPublicationReadiness(await getKnowledgePublicationReadiness(published.id));
      await refreshAuditEvents();
    } catch (nextError) {
      setError((nextError as Error).message);
    } finally {
      setPublicationBusy(false);
    }
  }

  async function handlePreferenceStatus(preferenceId: string, status: PreferenceStatus) {
    setError(null);
    try {
      const updated = await updatePreferenceStatus(preferenceId, status);
      setPreferences((current) =>
        current.map((item) => (item.id === preferenceId ? updated : item)),
      );
      if (preference?.id === preferenceId) {
        setPreference(updated);
      }
      if (status === "accepted") {
        setScoreProposal(await getScoreProposal(preferenceId));
      } else if (preference?.id === preferenceId) {
        setScoreProposal(null);
      }
      await refreshAuditEvents();
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  async function handlePreferenceDelete(preferenceId: string) {
    setError(null);
    try {
      await deletePreference(preferenceId);
      setPreferences((current) => current.filter((item) => item.id !== preferenceId));
      if (preference?.id === preferenceId) {
        setPreference(null);
      }
      if (scoreProposal?.preference_id === preferenceId) {
        setScoreProposal(null);
      }
      setSummary(await getProfileSummary());
      await refreshAuditEvents();
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  async function handleCompare() {
    setError(null);
    try {
      setComparison(await compareTexts(original, revised, activeContext));
      await refreshAuditEvents();
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  async function handleFeedbackProposal() {
    if (!comparison) return;
    setError(null);
    try {
      const proposal = await createFeedbackProposal(comparison.id, activeContext);
      setActiveFeedback(proposal);
      setFeedbackProposals((current) => [proposal, ...current]);
      await refreshAuditEvents();
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  async function handleFeedbackDecision(proposal: FeedbackProposal, status: "applied" | "rejected") {
    setError(null);
    try {
      const decided = await decideFeedbackProposal(
        proposal.id,
        status,
        status === "applied" ? "Aplicar feedback revisado." : "No aprender de este texto.",
      );
      setActiveFeedback(decided);
      setFeedbackProposals((current) =>
        current.map((item) => (item.id === decided.id ? decided : item)),
      );
      setScores(await getScores(activeContext));
      await refreshAuditEvents();
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  async function handleScoreProposal(preferenceId: string) {
    setError(null);
    try {
      setScoreProposal(await getScoreProposal(preferenceId));
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  async function handleApplyScoreProposal() {
    if (!scoreProposal) return;
    setError(null);
    try {
      const applied = await applyScoreProposal(
        scoreProposal.preference_id,
        "Aplicar propuesta revisada desde Preferencias.",
      );
      setScores((current) =>
        current.map(
          (item) => applied.variables.find((variable) => variable.key === item.key) ?? item,
        ),
      );
      setScoreProposal(applied.proposal);
      await refreshAuditEvents();
      setActive("scoring");
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  async function handleSaveProfileKnowledgeCard() {
    if (!selectedKnowledgeCard) return;
    setError(null);
    try {
      const saved = await saveProfileKnowledgeCard(selectedKnowledgeCard.id, {
        knowledge_version: selectedKnowledgeCard.version,
        stance: profileKnowledgeCardStance,
        user_score: profileKnowledgeCardScore,
        feedback: profileKnowledgeCardFeedback,
        maintained_elements: commaList(profileKnowledgeCardMaintained),
        change_requests: commaList(profileKnowledgeCardChanges),
        notes: profileKnowledgeCardNotes,
      });
      setProfileKnowledgeCardSaved(saved);
      setProfileKnowledgeCards((current) => [
        saved,
        ...current.filter(
          (item) =>
            item.card_id !== saved.card_id || item.knowledge_version !== saved.knowledge_version,
        ),
      ]);
      setProfileExport(null);
      setProfileKnowledgeCardProposal(
        await getProfileKnowledgeCardScoreProposal(
          selectedKnowledgeCard.id,
          selectedKnowledgeCard.version,
          activeContext,
        ),
      );
      await refreshAuditEvents();
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  async function handleProfileKnowledgeCardScoreProposal() {
    if (!selectedKnowledgeCard) return;
    setError(null);
    try {
      setProfileKnowledgeCardProposal(
        await getProfileKnowledgeCardScoreProposal(
          selectedKnowledgeCard.id,
          selectedKnowledgeCard.version,
          activeContext,
        ),
      );
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  async function handleApplyProfileKnowledgeCardScoreProposal() {
    if (!selectedKnowledgeCard || !profileKnowledgeCardProposal) return;
    setError(null);
    try {
      const applied = await applyProfileKnowledgeCardScoreProposal(
        selectedKnowledgeCard.id,
        selectedKnowledgeCard.version,
        activeContext,
        "Aplicar scoring desde ficha de usuario revisada.",
      );
      setProfileKnowledgeCardProposal(applied.proposal);
      setScores((current) =>
        current.map(
          (item) => applied.variables.find((variable) => variable.key === item.key) ?? item,
        ),
      );
      setStatistics(await getProfileStatistics(activeContext));
      setProfileExport(null);
      await refreshAuditEvents();
      setActive("scoring");
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  async function handleGenerate() {
    setError(null);
    try {
      setGeneration(
        await generateText(
          editorText,
          editorAction,
          activeContext,
          editorIntensity,
          protectedTerms
            .split(",")
            .map((term) => term.trim())
            .filter(Boolean),
        ),
      );
      setGeneratedTexts(await getGeneratedTexts(activeContext));
      await refreshAuditEvents();
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  async function handleLabSimulation() {
    setError(null);
    try {
      setLabResult(
        await simulateLab(
          labText,
          labAction,
          activeContext,
          labIntensity,
          protectedTerms
            .split(",")
            .map((term) => term.trim())
            .filter(Boolean),
          labOverrideKey && labOverrideDelta !== 0
            ? [{ variable_key: labOverrideKey, delta: labOverrideDelta }]
            : [],
        ),
      );
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  async function handleLabCompare() {
    setError(null);
    try {
      setLabComparison(await compareLabTexts(labText, labComparisonText, activeContext));
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  async function handleProfileExport() {
    setError(null);
    try {
      setProfileExport(await getProfileExport());
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  async function handleScoreAdjustment(score: ScoreVariable, manualAdjustment: number) {
    setError(null);
    setSavingScoreKey(score.key);
    try {
      const updated = await updateScore(score.key, manualAdjustment, scoreReason, activeContext);
      setScores((current) =>
        current.map((item) => (item.key === updated.variable.key ? updated.variable : item)),
      );
      await refreshAuditEvents();
    } catch (nextError) {
      setError((nextError as Error).message);
    } finally {
      setSavingScoreKey(null);
    }
  }

  return (
    <main className="appShell">
      <aside className="sidebar" aria-label="Navegacion principal">
        <div className="brand">
          <span className="brandMark">M</span>
          <div>
            <strong>Minicerebro</strong>
            <span>V1 escritura</span>
          </div>
        </div>
        <nav>
          {mainSections.map((section) => {
            const Icon = section.icon;
            return (
              <button
                className={activeSection.id === section.id ? "tab active" : "tab"}
                key={section.id}
                onClick={() => setActive(section.defaultTab)}
                type="button"
                title={section.description}
              >
                <Icon size={18} />
                <span>{section.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <h1>{activeTab.label}</h1>
            <p>{activeSection.description}</p>
          </div>
          <div className="contextControl">
            <label htmlFor="contextSelect">Contexto</label>
            <select
              id="contextSelect"
              onChange={(event) => setActiveContext(event.target.value)}
              value={activeContext}
            >
              {contexts.map((context) => (
                <option key={context} value={context}>
                  {context}
                </option>
              ))}
            </select>
          </div>
        </header>

        {activeSectionTabs.length > 1 ? (
          <div className="subnav" aria-label={`Secciones de ${activeSection.label}`}>
            {activeSectionTabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  className={active === tab.id ? "subtab active" : "subtab"}
                  key={tab.id}
                  onClick={() => setActive(tab.id)}
                  type="button"
                >
                  <Icon size={16} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        ) : null}

        {error ? <div className="error">{error}</div> : null}

        {active === "knowledge" && (
          <section className="panel">
            <h2>Estado de conocimiento</h2>
            <div className="versionToolbar">
              <label htmlFor="knowledgeVersionSelect">Version explorada</label>
              <select
                id="knowledgeVersionSelect"
                onChange={(event) => setSelectedKnowledgeVersion(event.target.value)}
                value={selectedKnowledgeVersion}
              >
                <option value="latest">latest ({latestPublishedKnowledgeVersion})</option>
                {knowledgeVersions.map((version) => (
                  <option key={version.id} value={version.id}>
                    {version.id} · {version.status}
                  </option>
                ))}
              </select>
            </div>
            <div className="metricGrid">
              <Metric label="Version cargada" value={loadedKnowledgeVersion} />
              <Metric
                label="Publicacion"
                value={
                  knowledgeVersions.find((version) => version.id === loadedKnowledgeVersion)
                    ?.status ?? knowledge?.state ?? "..."
                }
              />
              <Metric label="Cobertura" value={`${knowledge?.coverage.length ?? 0} areas`} />
              <Metric label="Validacion" value={`${pendingKnowledgeValidationCount} pendientes`} />
              <Metric label="No ingeridas" value={registeredOnlySourceCount} />
            </div>
            <p className="note">{knowledge?.sources_policy}</p>
            <div className="proposalBox">
              <h3>Registro frente a ingestion</h3>
              <div className="metricGrid">
                <Metric label="Publicadas" value={publishedSourceCount} />
                <Metric label="Ingeridas" value={ingestedSourceCount} />
                <Metric label="No ingeridas" value={registeredOnlySourceCount} />
              </div>
              <div className="phaseSummary">
                {ingestionPhaseCounts.map((item) => (
                  <span className="phaseBadge" key={item.phase}>
                    {item.label}: {item.count}
                  </span>
                ))}
              </div>
              <div className="ingestionList">
                {orderedIngestionStatuses.map((status) => (
                  <article className="ingestionItem" key={status.source_id}>
                    <div className="ingestionHeader">
                      <div>
                        <strong>{status.source_name}</strong>
                        <span>{status.source_id}</span>
                      </div>
                      <span className={status.is_published ? "statusPill done" : "statusPill"}>
                        {ingestionPhaseLabel(status.current_phase)}
                      </span>
                    </div>
                    <div className="pipelineTrace" aria-label={`Pipeline ${status.source_name}`}>
                      {pipelineSteps(status).map((step) => (
                        <span className={step.done ? "pipelineStep done" : "pipelineStep"} key={step.label}>
                          {step.label}
                        </span>
                      ))}
                    </div>
                    <div className="ingestionMetrics">
                      <Metric label="Ed." value={status.counts.editions ?? 0} />
                      <Metric label="Idx." value={status.counts.index_entries ?? 0} />
                      <Metric label="Seg." value={status.counts.segments ?? 0} />
                      <Metric label="Ext." value={status.counts.completed_extractions ?? 0} />
                      <Metric label="Prop." value={status.counts.proposals ?? 0} />
                      <Metric
                        label="Obj."
                        value={
                          (status.counts.nodes ?? 0) +
                          (status.counts.evidence ?? 0) +
                          (status.counts.claims ?? 0) +
                          (status.counts.cards ?? 0)
                        }
                      />
                    </div>
                    <span className="blockerLine">
                      {status.blockers.length
                        ? status.blockers.slice(0, 3).map(ingestionBlockerLabel).join(" · ")
                        : "sin bloqueos"}
                    </span>
                  </article>
                ))}
              </div>
            </div>
            <div className="proposalBox">
              <h3>Ingestion manual minima</h3>
              <p className="note">
                Crea fuente-edicion-indice-segmento-extraction run-proposals. Solo una candidate
                real permite aprobar propuestas; publicar sigue separado.
              </p>
              <div className="rowActions">
                <select
                  aria-label="Fuente para ingestion manual"
                  onChange={(event) => setManualIngestionSourceId(event.target.value)}
                  value={manualIngestionSourceId || manualIngestionSourceIdValue}
                >
                  {knowledgeSourceIngestionStatuses.map((status) => (
                    <option key={status.source_id} value={status.source_id}>
                      {status.source_name} · {status.current_phase}
                    </option>
                  ))}
                </select>
                <select
                  aria-label="Candidate destino para propuestas"
                  onChange={(event) => setPublicationTargetVersion(event.target.value)}
                  value={publicationTargetVersion}
                >
                  <option value="">Sin candidate aprobable</option>
                  {candidateVersions.map((version) => (
                    <option key={version.id} value={version.id}>
                      {version.id} · {version.status}
                    </option>
                  ))}
                </select>
                <button
                  className="primaryButton"
                  disabled={!manualIngestionSourceIdValue || manualIngestionBusy}
                  onClick={handleCreateManualIngestionFlow}
                  type="button"
                >
                  {manualIngestionBusy ? "Creando..." : "Crear lote manual"}
                </button>
                <button
                  className="ghostButton"
                  disabled={!manualIngestionExtraction}
                  onClick={handleLoadManualProposals}
                  type="button"
                >
                  Recargar proposals
                </button>
              </div>
              <div className="pipelineTrace">
                <span className={manualIngestionEdition ? "pipelineStep done" : "pipelineStep"}>
                  Edicion
                </span>
                <span className={manualIngestionIndexEntry ? "pipelineStep done" : "pipelineStep"}>
                  Indice
                </span>
                <span className={manualIngestionSegment ? "pipelineStep done" : "pipelineStep"}>
                  Segmento
                </span>
                <span className={manualIngestionExtraction ? "pipelineStep done" : "pipelineStep"}>
                  ExtractionRun
                </span>
                <span className={manualIngestionProposals.length ? "pipelineStep done" : "pipelineStep"}>
                  Proposals
                </span>
              </div>
              {manualIngestionExtraction ? (
                <div className="metricGrid">
                  <Metric label="Edicion" value={manualIngestionEdition?.id ?? "..."} />
                  <Metric label="Segmento" value={manualIngestionSegment?.id ?? "..."} />
                  <Metric label="Extraccion" value={manualIngestionExtraction.status} />
                  <Metric label="Proposals" value={manualIngestionProposals.length} />
                  <Metric label="Destino" value={manualProposalTargetVersion} />
                </div>
              ) : null}
              {manualIngestionProposals.length ? (
                <div className="knowledgeGrid">
                  {manualIngestionProposals.map((proposal) => (
                    <article className="knowledgeItem" key={proposal.id}>
                      <strong>{proposal.title}</strong>
                      <span>
                        {proposal.proposal_type} · {proposal.status} · confianza{" "}
                        {proposal.confidence}
                      </span>
                      <p className="note">{proposal.rationale}</p>
                      <pre>{JSON.stringify(proposal.payload, null, 2)}</pre>
                      <div className="rowActions">
                        <button
                          className="ghostButton"
                          disabled={!canApproveProposal(proposal, knowledgeVersions)}
                          onClick={() => handleManualProposalDecision(proposal, "approve")}
                          type="button"
                        >
                          Aprobar
                        </button>
                        <button
                          className="ghostButton"
                          disabled={proposal.status !== "proposed"}
                          onClick={() => handleManualProposalDecision(proposal, "reject")}
                          type="button"
                        >
                          Rechazar
                        </button>
                      </div>
                      {!canApproveProposal(proposal, knowledgeVersions) &&
                      proposal.status === "proposed" ? (
                        <p className="note">
                          Aprobar requiere una version candidata real; rechazar no modifica
                          conocimiento estable.
                        </p>
                      ) : null}
                    </article>
                  ))}
                </div>
              ) : null}
            </div>
            <div className="proposalBox">
              <h3>Candidato y publicacion</h3>
              <p className="note">
                Crear candidato congela un snapshot revisable. Publicar solo activa una version si
                readiness pasa todos los gates.
              </p>
              <div className="rowActions">
                <input
                  aria-label="ID de candidate"
                  className="textInput"
                  onChange={(event) => setCandidateVersionId(event.target.value)}
                  value={candidateVersionId}
                />
                <select
                  aria-label="Version base de candidate"
                  onChange={(event) => setCandidateBaseVersion(event.target.value)}
                  value={candidateBaseVersion}
                >
                  {knowledgeVersions.map((version) => (
                    <option key={version.id} value={version.id}>
                      base {version.id}
                    </option>
                  ))}
                </select>
                <input
                  aria-label="Autor de candidate"
                  className="textInput"
                  onChange={(event) => setCandidateAuthor(event.target.value)}
                  value={candidateAuthor}
                />
                <button
                  className="primaryButton"
                  disabled={publicationBusy || !candidateVersionId || !candidateAuthor || !candidateReason}
                  onClick={handleCreateCandidateVersion}
                  type="button"
                >
                  Crear candidate
                </button>
              </div>
              <label className="fieldLabel" htmlFor="candidateReason">
                Motivo
              </label>
              <textarea
                id="candidateReason"
                onChange={(event) => setCandidateReason(event.target.value)}
                value={candidateReason}
              />
              <div className="rowActions">
                <select
                  aria-label="Version candidata para publicar"
                  onChange={(event) => {
                    setPublicationTargetVersion(event.target.value);
                    setPublicationReadiness(null);
                  }}
                  value={publicationTargetVersion}
                >
                  <option value="">Seleccionar candidate</option>
                  {candidateVersions.map((version) => (
                    <option key={version.id} value={version.id}>
                      {version.id} · {version.status}
                    </option>
                  ))}
                </select>
                <button
                  className="ghostButton"
                  disabled={!publicationTargetVersion || publicationBusy}
                  onClick={() => void handleCheckPublicationReadiness()}
                  type="button"
                >
                  Ver readiness
                </button>
                <button
                  className="primaryButton"
                  disabled={!publishableReadiness || publicationBusy}
                  onClick={handlePublishCandidateVersion}
                  type="button"
                >
                  Publicar candidate
                </button>
              </div>
              {publicationReadiness ? (
                <>
                  <div className="metricGrid">
                    <Metric label="Version" value={publicationReadiness.version} />
                    <Metric label="Estado" value={publicationReadiness.status} />
                    <Metric
                      label="Publicable"
                      value={publicationReadiness.publishable ? "si" : "no"}
                    />
                    <Metric label="Bloqueos" value={publicationReadiness.blockers.length} />
                  </div>
                  <div className="knowledgeGrid">
                    {publicationReadiness.checks.map((check) => (
                      <article className="knowledgeItem" key={check.id}>
                        <strong>{check.label}</strong>
                        <span>{check.passed ? "pasa" : "bloquea"}</span>
                        <p className="note">{check.detail}</p>
                      </article>
                    ))}
                  </div>
                  <List title="Blockers" items={publicationReadiness.blockers} />
                </>
              ) : null}
            </div>
            <div className="knowledgeGrid">
              {knowledgeSources.map((source) => (
                <article className="knowledgeItem" key={source.id}>
                  <strong>{source.name}</strong>
                  <span>
                    {source.source_type} · autoridad {source.authority_level}
                  </span>
                </article>
              ))}
            </div>
            <div className="knowledgeGrid">
              {knowledgeCards.map((card) => (
                <article className="knowledgeItem" key={card.id}>
                  <strong>{card.name}</strong>
                  <span>{card.definition}</span>
                  <button
                    className="ghostButton"
                    onClick={() => setSelectedKnowledgeCardId(card.id)}
                    type="button"
                  >
                    Inspeccionar
                  </button>
                </article>
              ))}
            </div>
            <div className="proposalBox">
              <h3>Exploracion persistente</h3>
              <p className="note">
                Version navegada: {loadedKnowledgeVersion}. knowledge-v0 queda congelada; latest
                resuelve a la ultima version publicada.
              </p>
              <h3>Trazabilidad persistente</h3>
              <div className="metricGrid">
                <Metric label="Fuentes" value={knowledgeSources.length} />
                <Metric label="Nodos" value={knowledgeNodes.length} />
                <Metric label="Evidencias" value={knowledgeEvidence.length} />
                <Metric label="Claims" value={knowledgeClaims.length} />
                <Metric label="Fichas" value={knowledgeCards.length} />
              </div>
              <div className="knowledgeGrid">
                {knowledgeSources.map((source) => (
                  <article className="knowledgeItem" key={source.id}>
                    <strong>{source.name}</strong>
                    <span>
                      {source.source_type} · {source.status}
                    </span>
                    {sourceIngestionStatusById.get(source.id) ? (
                      <div className="pipelineTrace">
                        {pipelineSteps(sourceIngestionStatusById.get(source.id)).map((step) => (
                          <span className={step.done ? "pipelineStep done" : "pipelineStep"} key={step.label}>
                            {step.label}
                          </span>
                        ))}
                      </div>
                    ) : null}
                    {(nodesBySource.get(source.id) ?? []).map((node) => (
                      <div className="listBlock" key={node.id}>
                        <h3>{node.title}</h3>
                        <p className="note">{node.summary}</p>
                        {(evidenceByNode.get(node.id) ?? []).map((item) => (
                          <div className="listBlock" key={item.id}>
                            <h3>{item.reference}</h3>
                            <p className="note">{item.excerpt}</p>
                            <h3>Claims</h3>
                            {(claimsByEvidence.get(item.id) ?? []).map((claim) => {
                              const card = cardById.get(claim.card_id);
                              return (
                                <div className="traceClaim" key={claim.id}>
                                  <span>
                                    {claim.statement} -&gt; {card?.name ?? claim.card_id}
                                  </span>
                                  <button
                                    className="ghostButton"
                                    onClick={() => setSelectedKnowledgeCardId(claim.card_id)}
                                    type="button"
                                  >
                                    Ver ficha
                                  </button>
                                </div>
                              );
                            })}
                          </div>
                        ))}
                      </div>
                    ))}
                  </article>
                ))}
              </div>
            </div>
            {selectedKnowledgeCard ? (
              <div className="proposalBox">
                <h3>Ficha seleccionada</h3>
                <article className="knowledgeItem">
                  <strong>{selectedKnowledgeCard.name}</strong>
                  <span>{selectedKnowledgeCard.definition}</span>
                  <ValidationPill confidence={selectedKnowledgeCard.confidence} />
                  <div className="metricGrid">
                    <Metric label="Confianza" value={selectedKnowledgeCard.confidence} />
                    <Metric label="Tipo" value={selectedKnowledgeCard.card_type} />
                    <Metric label="Version" value={selectedKnowledgeCard.version} />
                  </div>
                  <List title="Senales" items={payloadList(selectedKnowledgeCard.payload.signals)} />
                  <List title="Riesgos" items={payloadList(selectedKnowledgeCard.payload.risks)} />
                  <List title="Contextos" items={payloadList(selectedKnowledgeCard.payload.contexts)} />
                  <div className="auditList">
                    {(claimsByCard.get(selectedKnowledgeCard.id) ?? []).map((claim) => {
                      const evidence = evidenceById.get(claim.evidence_id);
                      const node = evidence ? nodeById.get(evidence.node_id) : null;
                      const source = evidence ? sourceById.get(evidence.source_id) : null;
                      return (
                        <article className="auditItem" key={claim.id}>
                          <div>
                            <strong>{claim.statement}</strong>
                            <span>
                              {source?.name ?? evidence?.source_id ?? "fuente desconocida"} -&gt;{" "}
                              {node?.title ?? evidence?.node_id ?? "nodo desconocido"} -&gt;{" "}
                              {evidence?.reference ?? claim.evidence_id}
                            </span>
                            <ValidationPill confidence={claim.confidence} />
                          </div>
                          <span>confianza {claim.confidence}</span>
                          <pre>
                            {evidence?.excerpt ?? "Evidencia no cargada."}
                            {evidence
                              ? `\nValidacion evidencia: ${validationLabel(evidence.confidence)}`
                              : ""}
                          </pre>
                        </article>
                      );
                    })}
                  </div>
                  <div className="userCardPanel">
                    <h3>Ficha de usuario</h3>
                    <div className="metricGrid">
                      <Metric
                        label="Estado"
                        value={profileKnowledgeCardSaved?.stance ?? "sin guardar"}
                      />
                      <Metric label="Score usuario" value={profileKnowledgeCardScore} />
                      <Metric label="Contexto" value={activeContext} />
                    </div>
                    <div className="buttonRow" role="group" aria-label="Estado de ficha de usuario">
                      {userKnowledgeCardStances.map((stance) => (
                        <button
                          className={
                            profileKnowledgeCardStance === stance.value
                              ? "ghostButton activeGhostButton"
                              : "ghostButton"
                          }
                          key={stance.value}
                          onClick={() => setProfileKnowledgeCardStance(stance.value)}
                          type="button"
                        >
                          {stance.label}
                        </button>
                      ))}
                    </div>
                    <label className="fieldLabel" htmlFor="profileKnowledgeCardScore">
                      Score personal
                    </label>
                    <input
                      id="profileKnowledgeCardScore"
                      max="1000"
                      min="0"
                      onChange={(event) => setProfileKnowledgeCardScore(Number(event.target.value))}
                      type="range"
                      value={profileKnowledgeCardScore}
                    />
                    <label className="fieldLabel" htmlFor="profileKnowledgeCardFeedback">
                      Feedback de usuario
                    </label>
                    <textarea
                      id="profileKnowledgeCardFeedback"
                      onChange={(event) => setProfileKnowledgeCardFeedback(event.target.value)}
                      value={profileKnowledgeCardFeedback}
                    />
                    <label className="fieldLabel" htmlFor="profileKnowledgeCardMaintained">
                      Mantener
                    </label>
                    <input
                      className="textInput"
                      id="profileKnowledgeCardMaintained"
                      onChange={(event) => setProfileKnowledgeCardMaintained(event.target.value)}
                      value={profileKnowledgeCardMaintained}
                    />
                    <label className="fieldLabel" htmlFor="profileKnowledgeCardChanges">
                      Cambiar
                    </label>
                    <input
                      className="textInput"
                      id="profileKnowledgeCardChanges"
                      onChange={(event) => setProfileKnowledgeCardChanges(event.target.value)}
                      value={profileKnowledgeCardChanges}
                    />
                    <label className="fieldLabel" htmlFor="profileKnowledgeCardNotes">
                      Notas
                    </label>
                    <textarea
                      id="profileKnowledgeCardNotes"
                      onChange={(event) => setProfileKnowledgeCardNotes(event.target.value)}
                      value={profileKnowledgeCardNotes}
                    />
                    <div className="rowActions">
                      <button
                        className="primaryButton"
                        onClick={handleSaveProfileKnowledgeCard}
                        type="button"
                      >
                        Guardar ficha
                      </button>
                      <button
                        className="ghostButton"
                        onClick={handleProfileKnowledgeCardScoreProposal}
                        type="button"
                      >
                        Calcular puntuacion sugerida
                      </button>
                    </div>
                    {profileKnowledgeCardProposal ? (
                      <div className="proposalBox">
                        <h3>Propuesta de scoring</h3>
                        <div className="metricGrid">
                          <Metric label="Estado" value={profileKnowledgeCardProposal.status} />
                          <Metric label="Ajustes" value={profileKnowledgeCardProposal.items.length} />
                        </div>
                        <div className="auditList">
                          {profileKnowledgeCardProposal.items.map((item) => (
                            <article
                              className="auditItem"
                              key={`${item.variable_key}-${item.context}`}
                            >
                              <div>
                                <strong>{item.variable_key}</strong>
                                <span>{item.reason}</span>
                              </div>
                              <span>
                                {item.current_value} -&gt; {item.proposed_value} ({item.delta})
                              </span>
                            </article>
                          ))}
                        </div>
                        <button
                          className="primaryButton editorButton"
                          disabled={profileKnowledgeCardProposal.items.length === 0}
                          onClick={handleApplyProfileKnowledgeCardScoreProposal}
                          type="button"
                        >
                        Aplicar a la puntuacion
                        </button>
                      </div>
                    ) : null}
                  </div>
                </article>
              </div>
            ) : null}
            <div className="proposalBox">
              <h3>Consulta</h3>
              <p className="note">La consulta usa la version explorada: {loadedKnowledgeVersion}.</p>
              <div className="rowActions">
                <input
                  className="textInput"
                  onChange={(event) => setKnowledgeQuery(event.target.value)}
                  value={knowledgeQuery}
                />
                <select
                  aria-label="Limite de fichas"
                  onChange={(event) => setKnowledgeQueryLimit(Number.parseInt(event.target.value, 10))}
                  value={knowledgeQueryLimit}
                >
                  {[3, 5, 10, 20].map((limit) => (
                    <option key={limit} value={limit}>
                      {limit} fichas
                    </option>
                  ))}
                </select>
                <button className="primaryButton" onClick={handleKnowledgeQuery} type="button">
                  Consultar
                </button>
              </div>
              {knowledgeResult ? (
                <>
                  <p className="note">
                    Resultado para "{knowledgeResult.query}" en version resuelta{" "}
                    {knowledgeResult.resolved_version}.
                  </p>
                  <div className="metricGrid">
                    <Metric label="Fichas" value={knowledgeResult.card_count} />
                    <Metric label="Claims" value={knowledgeResult.claim_count} />
                    <Metric label="Evidencias" value={knowledgeResult.evidence_count} />
                    <Metric
                      label="Validacion"
                      value={`${
                        [
                          ...knowledgeResult.cards,
                          ...knowledgeResult.claims,
                          ...knowledgeResult.evidence,
                        ].filter(
                          (item) => validationLabel(item.confidence) === "Validacion pendiente",
                        ).length
                      } pendientes`}
                    />
                  </div>
                  {knowledgeResult.cards.length > 0 ? (
                    <div className="knowledgeGrid">
                      {knowledgeResult.cards.map((card) => {
                        const cardClaims = knowledgeResult.claims.filter(
                          (claim) => claim.card_id === card.id,
                        );
                        const cardEvidenceIds = new Set(
                          cardClaims.map((claim) => claim.evidence_id),
                        );
                        const cardEvidence = knowledgeResult.evidence.filter((item) =>
                          cardEvidenceIds.has(item.id),
                        );

                        return (
                          <article className="knowledgeItem" key={card.id}>
                            <strong>{card.name}</strong>
                            <span>{card.definition}</span>
                            <ValidationPill confidence={card.confidence} />
                            <List
                              title="Claims"
                              items={cardClaims.map(
                                (claim) =>
                                  `${claim.statement} · ${validationLabel(claim.confidence)}`,
                              )}
                            />
                            <List
                              title="Evidencia"
                              items={cardEvidence.map(
                                (item) =>
                                  `${item.reference}: ${item.excerpt} · ${validationLabel(
                                    item.confidence,
                                  )}`,
                              )}
                            />
                            <button
                              className="ghostButton"
                              onClick={() => setSelectedKnowledgeCardId(card.id)}
                              type="button"
                            >
                              Inspeccionar
                            </button>
                          </article>
                        );
                      })}
                    </div>
                  ) : (
                    <article className="knowledgeItem">
                      <strong>Consulta valida sin resultados</strong>
                      <span>
                        0 fichas, 0 claims y 0 evidencias en version {knowledgeResult.version}.
                      </span>
                    </article>
                  )}
                </>
              ) : null}
            </div>
            <List title="Cobertura" items={knowledge?.coverage ?? []} />
            <List title="Todavia no incluido en V1" items={knowledge?.gaps ?? []} />
          </section>
        )}

        {active === "preferences" && (
          <section className="panel editorGrid">
            <div>
              <h2>Anadir preferencia</h2>
              <textarea value={preferenceText} onChange={(event) => setPreferenceText(event.target.value)} />
              <button className="primaryButton" onClick={handlePreference} type="button">
                Guardar como propuesta
              </button>
              <div className="preferenceList">
                <h2>Revision pendiente</h2>
                {preferences.length === 0 ? (
                  <p className="note">Todavia no hay preferencias registradas.</p>
                ) : (
                  preferences.map((item) => (
                    <article className="preferenceItem" key={item.id}>
                      <div>
                        <strong>{item.text}</strong>
                        <span>{item.affected_variables.join(", ")}</span>
                      </div>
                      <span className="statusPill">{item.status}</span>
                      <div className="rowActions">
                        <button
                          className="ghostButton"
                          onClick={() => handlePreferenceStatus(item.id, "accepted")}
                          type="button"
                        >
                          Aceptar
                        </button>
                        {item.status === "accepted" ? (
                          <button
                            className="ghostButton"
                            onClick={() => handleScoreProposal(item.id)}
                            type="button"
                          >
                            Ver ajuste sugerido
                          </button>
                        ) : null}
                        <button
                          className="ghostButton"
                          onClick={() => handlePreferenceStatus(item.id, "rejected")}
                          type="button"
                        >
                          Descartar
                        </button>
                        <button
                          className="ghostButton danger"
                          onClick={() => handlePreferenceDelete(item.id)}
                          type="button"
                        >
                          Eliminar
                        </button>
                      </div>
                    </article>
                  ))
                )}
              </div>
            </div>
            <div className="inspector">
              <h2>Como lo ha entendido</h2>
              {preference ? (
                <>
                  <p>{preference.interpreted_as}</p>
                  <List title="Variables afectadas" items={preference.affected_variables} />
                  <span className="statusPill">{preference.status}</span>
                </>
              ) : (
                <p className="note">La entrada se registra como propuesta; no consolida aprendizaje sola.</p>
              )}
              {scoreProposal ? (
                <div className="proposalBox">
                  <h3>Propuesta de scoring</h3>
                  {scoreProposal.items.length === 0 ? (
                    <p className="note">Esta preferencia todavia no genera cambios aplicables.</p>
                  ) : (
                    <>
                      {scoreProposal.items.map((item) => (
                        <div className="proposalItem" key={item.variable_key}>
                          <strong>
                            {item.context}:{item.variable_key} {item.delta > 0 ? "+" : ""}
                            {item.delta}
                          </strong>
                          <span>{item.reason}</span>
                        </div>
                      ))}
                      <button className="primaryButton" onClick={handleApplyScoreProposal} type="button">
                        Aplicar a la puntuacion
                      </button>
                    </>
                  )}
                </div>
              ) : null}
            </div>
          </section>
        )}

        {active === "editor" && (
          <section className="panel editorGrid">
            <div>
              <h2>Texto</h2>
              <textarea value={editorText} onChange={(event) => setEditorText(event.target.value)} />
              <div className="editorControls">
                <label>
                  Accion
                  <select
                    onChange={(event) => setEditorAction(event.target.value as GenerationAction)}
                    value={editorAction}
                  >
                    <option value="rewrite">Reescribir</option>
                    <option value="correction">Corregir</option>
                    <option value="continue">Continuar</option>
                    <option value="variants">Variantes</option>
                  </select>
                </label>
                <label>
                  Intensidad: {editorIntensity}
                  <input
                    max={1000}
                    min={0}
                    onChange={(event) => setEditorIntensity(Number.parseInt(event.target.value, 10))}
                    step={50}
                    type="range"
                    value={editorIntensity}
                  />
                </label>
              </div>
              <label className="fieldLabel" htmlFor="protectedTerms">
                Terminos protegidos
              </label>
              <input
                className="textInput"
                id="protectedTerms"
                onChange={(event) => setProtectedTerms(event.target.value)}
                placeholder="Separados por coma"
                value={protectedTerms}
              />
              <button className="primaryButton editorButton" onClick={handleGenerate} type="button">
                Generar texto
              </button>
            </div>
            <div className="inspector">
              <h2>Resultado</h2>
              {generation ? (
                <>
                  <textarea readOnly value={generation.output} />
                  <p className="note">{generation.explanation}</p>
                  <span className="statusPill">{generation.provider}</span>
                  <List title="Variables usadas" items={generation.used_profile_variables} />
                </>
              ) : (
                <p className="note">El editor usa el perfil del contexto activo sin aplicar aprendizaje.</p>
              )}
            </div>
          </section>
        )}

        {active === "lab" && (
          <section className="panel editorGrid">
            <div>
              <h2>Simulacion</h2>
              <textarea value={labText} onChange={(event) => setLabText(event.target.value)} />
              <div className="editorControls">
                <label>
                  Accion
                  <select
                    onChange={(event) => setLabAction(event.target.value as GenerationAction)}
                    value={labAction}
                  >
                    <option value="rewrite">Reescribir</option>
                    <option value="correction">Corregir</option>
                    <option value="continue">Continuar</option>
                    <option value="variants">Variantes</option>
                  </select>
                </label>
                <label>
                  Intensidad: {labIntensity}
                  <input
                    max={1000}
                    min={0}
                    onChange={(event) => setLabIntensity(Number.parseInt(event.target.value, 10))}
                    step={50}
                    type="range"
                    value={labIntensity}
                  />
                </label>
              </div>
              <div className="labControls">
                <label>
                  Variable temporal
                  <select
                    onChange={(event) => setLabOverrideKey(event.target.value)}
                    value={labOverrideKey}
                  >
                    <option value="">Sin override</option>
                    {scores.map((score) => (
                      <option key={score.key} value={score.key}>
                        {score.label}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Delta: {labOverrideDelta > 0 ? "+" : ""}
                  {labOverrideDelta}
                  <input
                    max={300}
                    min={-300}
                    onChange={(event) => setLabOverrideDelta(Number.parseInt(event.target.value, 10))}
                    step={10}
                    type="range"
                    value={labOverrideDelta}
                  />
                </label>
              </div>
              <button className="primaryButton editorButton" onClick={handleLabSimulation} type="button">
                Probar sin guardar
              </button>
              <textarea
                aria-label="Texto revisado de laboratorio"
                onChange={(event) => setLabComparisonText(event.target.value)}
                value={labComparisonText}
              />
              <button className="primaryButton editorButton" onClick={handleLabCompare} type="button">
                Comparar sin guardar
              </button>
            </div>
            <div className="inspector">
              <h2>Resultado</h2>
              {labResult ? (
                <>
                  <textarea readOnly value={labResult.generation.output} />
                  <p className="note">{labResult.generation.explanation}</p>
                  <span className="statusPill">{labResult.generation.provider}</span>
                  <Metric label="Modificacion" value={labResult.comparison.modification_score} />
                  <Metric label="Adecuacion" value={labResult.comparison.adequacy_score} />
                  <List
                    title="Variables simuladas"
                    items={labResult.simulated_variables.map(
                      (score) => `${score.key}: ${score.effective_value}`,
                    )}
                  />
                </>
              ) : (
                <p className="note">El laboratorio no escribe en preferencias, scoring ni evidencias.</p>
              )}
              {labComparison ? (
                <>
                  <h2>Comparacion temporal</h2>
                  <p className="note">{labComparison.summary}</p>
                  <Metric label="Modificacion temporal" value={labComparison.modification_score} />
                  <Metric label="Adecuacion temporal" value={labComparison.adequacy_score} />
                  <List
                    title="Cambios temporales"
                    items={labComparison.changes.map(
                      (change) => `${change.original} -> ${change.revised}`,
                    )}
                  />
                </>
              ) : null}
            </div>
          </section>
        )}

        {active === "profile" && (
          <section className="panel">
            <h2>Resumen humano</h2>
            <p>{summary?.summary}</p>
            <div className="metricGrid">
              <Metric label="Preferencias" value={summary?.preference_count ?? 0} />
              <Metric label="Confianza media" value={`${Math.round(averageConfidence * 100)}%`} />
              <Metric label="Cobertura" value={`${Math.round((statistics?.coverage ?? 0) * 100)}%`} />
            </div>
            <p className="note">{summary?.confidence_note}</p>
            <button className="primaryButton editorButton" onClick={handleProfileExport} type="button">
              Ver datos del perfil
            </button>
            {profileExport ? (
              <div className="proposalBox">
                <h2>Export del perfil</h2>
                <div className="metricGrid">
                  <Metric label="Formato" value={profileExport.export_version} />
                  <Metric
                    label="Contextos"
                    value={Object.keys(profileExport.variables_by_context).length}
                  />
                  <Metric label="Preferencias" value={profileExport.preferences.length} />
                  <Metric label="Fichas usuario" value={profileExport.knowledge_cards.length} />
                </div>
                <p className="note">{profileExport.knowledge_policy}</p>
                <List
                  title="Contextos exportados"
                  items={Object.entries(profileExport.variables_by_context).map(
                    ([context, variables]) => `${context}: ${variables.length} variables`,
                  )}
                />
                <List
                  title="Fichas de usuario"
                  items={
                    profileExport.knowledge_cards.length === 0
                      ? ["Sin fichas de usuario guardadas."]
                      : profileExport.knowledge_cards.map(
                          (item) =>
                            `${item.card_id}: ${item.stance} (${item.user_score}) en ${item.knowledge_version}`,
                        )
                  }
                />
              </div>
            ) : null}
            <List title="Variables con baja confianza" items={statistics?.low_confidence_variables ?? []} />
            <List
              title="Contradicciones"
              items={
                contradictions.length === 0
                  ? ["Sin contradicciones detectadas en este contexto."]
                  : contradictions.map((item) => `${item.variable_key}: ${item.note}`)
              }
            />
          </section>
        )}

        {active === "scoring" && (
          <section className="panel">
            <h2>Variables</h2>
            <label className="fieldLabel" htmlFor="scoreReason">
              Por que cambias la puntuacion
            </label>
            <input
              className="textInput"
              id="scoreReason"
              onChange={(event) => setScoreReason(event.target.value)}
              value={scoreReason}
            />
            <div className="scoreTable">
              {scores.map((score) => (
                <article className="scoreRow" key={score.key}>
                  <div>
                    <strong>{score.label}</strong>
                    <span>{score.category}</span>
                  </div>
                  <Meter label="Calculado" value={score.calculated_value} />
                  <div className="adjustControl">
                    <label htmlFor={`adjust-${score.key}`}>Ajuste: {score.manual_adjustment}</label>
                    <input
                      id={`adjust-${score.key}`}
                      max={300}
                      min={-300}
                      onChange={(event) =>
                        handleScoreAdjustment(score, Number.parseInt(event.target.value, 10))
                      }
                      step={10}
                      type="range"
                      value={score.manual_adjustment}
                    />
                    <button
                      className="ghostButton"
                      disabled={savingScoreKey === score.key}
                      onClick={() => handleScoreAdjustment(score, 0)}
                      type="button"
                    >
                      Restablecer
                    </button>
                  </div>
                  <Meter label="Efectivo" value={score.effective_value} />
                </article>
              ))}
            </div>
          </section>
        )}

        {active === "compare" && (
          <section className="panel editorGrid">
            <div>
              <h2>Textos</h2>
              <textarea value={original} onChange={(event) => setOriginal(event.target.value)} />
              <textarea value={revised} onChange={(event) => setRevised(event.target.value)} />
              <button className="primaryButton" onClick={handleCompare} type="button">
                Comparar
              </button>
            </div>
            <div className="inspector">
              <h2>Resultado</h2>
              {comparison ? (
                <>
                  <Metric label="Modificacion" value={comparison.modification_score} />
                  <Metric label="Adecuacion" value={comparison.adequacy_score} />
                  <p>{comparison.summary}</p>
                  <List
                    title="Dimensiones"
                    items={Object.entries(comparison.dimensions).map(([key, value]) => `${key}: ${value}`)}
                  />
                  <List
                    title="Cambios"
                    items={comparison.changes.map(
                      (change) => `${change.type}: ${change.original || "vacio"} -> ${change.revised || "vacio"}`,
                    )}
                  />
                  <button className="primaryButton editorButton" onClick={handleFeedbackProposal} type="button">
                    Crear aprendizaje sugerido
                  </button>
                </>
              ) : (
                <p className="note">El comparador mide modificacion y adecuacion sin actualizar el perfil.</p>
              )}
              {activeFeedback ? (
                <div className="proposalBox">
                  <h3>Feedback propuesto</h3>
                  <span className="statusPill">{activeFeedback.status}</span>
                  {activeFeedback.items.map((item) => (
                    <div className="proposalItem" key={item.variable_key}>
                      <strong>
                        {`${item.variable_key}: ${item.current_value} -> ${item.proposed_value}`}
                      </strong>
                      <span>{item.reason}</span>
                    </div>
                  ))}
                  {activeFeedback.status === "proposed" ? (
                    <div className="rowActions">
                      <button
                        className="ghostButton"
                        onClick={() => handleFeedbackDecision(activeFeedback, "applied")}
                        type="button"
                      >
                        Aprender esto
                      </button>
                      <button
                        className="ghostButton danger"
                        onClick={() => handleFeedbackDecision(activeFeedback, "rejected")}
                        type="button"
                      >
                        No aprender
                      </button>
                    </div>
                  ) : null}
                </div>
              ) : null}
            </div>
          </section>
        )}

        {active === "screens" && (
          <section className="panel">
            <h2>Pantallas V1</h2>
            <div className="knowledgeGrid">
              {screens.map((screen) => (
                <article className="knowledgeItem" key={screen.id}>
                  <strong>{screen.label}</strong>
                  <span>
                    {screen.status} · {screen.route}
                  </span>
                  <List title="Funciones" items={screen.functions} />
                </article>
              ))}
            </div>
            <List
              title="Feedback pendiente"
              items={
                feedbackProposals.length === 0
                  ? ["Sin propuestas pendientes."]
                  : feedbackProposals.map(
                      (proposal) =>
                        `${proposal.status}: ${proposal.items.length} variables · ${formatDate(
                          proposal.created_at,
                        )}`,
                    )
              }
            />
          </section>
        )}

        {active === "rules" && (
          <section className="panel editorGrid">
            <div>
              <h2>Prioridad de instrucciones</h2>
              <div className="auditList">
                {decisionRules.map((rule) => (
                  <article className="auditItem" key={rule.priority}>
                    <div>
                      <strong>
                        {rule.priority}. {rule.label}
                      </strong>
                      <span>{rule.description}</span>
                    </div>
                  </article>
                ))}
              </div>
            </div>
            <div className="inspector">
              <h2>Evaluacion</h2>
              {decisionEvaluation ? (
                <>
                  <p>{decisionEvaluation.recommendation}</p>
                  <List
                    title="Confianza baja"
                    items={
                      decisionEvaluation.low_confidence_variables.length === 0
                        ? ["Sin variables por debajo del umbral."]
                        : decisionEvaluation.low_confidence_variables
                    }
                  />
                  <List
                    title="Conflictos"
                    items={
                      decisionEvaluation.conflicts.length === 0
                        ? ["Sin conflictos detectados en este contexto."]
                        : decisionEvaluation.conflicts
                    }
                  />
                </>
              ) : (
                <p className="note">La evaluacion usa el contexto activo.</p>
              )}
            </div>
          </section>
        )}

        {active === "persistence" && (
          <section className="panel editorGrid">
            <div>
              <h2>Dominios persistidos</h2>
              <div className="knowledgeGrid">
                {persistenceDomains.map((domain) => (
                  <article className="knowledgeItem" key={domain.id}>
                    <strong>{domain.id}</strong>
                    <span>
                      {domain.status} · {domain.storage}
                    </span>
                  </article>
                ))}
              </div>
            </div>
            <div className="inspector">
              <h2>Textos</h2>
              {generatedTexts.length === 0 ? (
                <p className="note">Todavia no hay textos generados en este contexto.</p>
              ) : (
                <div className="auditList">
                  {generatedTexts.slice(0, 5).map((text) => (
                    <article className="auditItem" key={text.id}>
                      <div>
                        <strong>
                          {text.action} · {text.provider}
                        </strong>
                        <span>{formatDate(text.created_at)}</span>
                      </div>
                      <pre>{text.output_text}</pre>
                    </article>
                  ))}
                </div>
              )}
            </div>
          </section>
        )}

        {active === "cerebro" && (
          <section className="panel">
            <h2>Auditoria Cerebro</h2>
            <div className="knowledgeGrid">
              {cerebroCandidates.map((candidate) => (
                <article className="knowledgeItem" key={candidate.component}>
                  <strong>{candidate.component}</strong>
                  <span>
                    {candidate.classification} · {candidate.status}
                  </span>
                  <List title="Evidencia requerida" items={candidate.evidence_required} />
                </article>
              ))}
            </div>
            <List
              title="Bloqueos antes de reutilizar"
              items={cerebroGates.map((gate) => `${gate.id}: ${gate.status} · ${gate.reason}`)}
            />
          </section>
        )}

        {active === "acceptance" && (
          <section className="panel">
            <h2>Aceptacion V1</h2>
            <div className="auditList">
              {acceptanceCriteria.map((criterion) => (
                <article className="auditItem" key={criterion.id}>
                  <div>
                    <strong>
                      {criterion.id}. {criterion.description}
                    </strong>
                    <span>{criterion.status}</span>
                  </div>
                  <pre>{criterion.evidence.join("\n")}</pre>
                </article>
              ))}
            </div>
          </section>
        )}

        {active === "closure" && (
          <section className="panel editorGrid">
            <div>
              <h2>Condiciones de cierre</h2>
              <div className="auditList">
                {closureConditions.map((condition) => (
                  <article className="auditItem" key={condition.id}>
                    <div>
                      <strong>
                        {condition.id}. {condition.description}
                      </strong>
                      <span>{condition.status}</span>
                    </div>
                    <pre>{condition.evidence.join("\n")}</pre>
                  </article>
                ))}
              </div>
            </div>
            <div className="inspector">
              <h2>Cierre tecnico</h2>
              <div className="auditList">
                {technicalClosure.map((criterion) => (
                  <article className="auditItem" key={criterion.id}>
                    <div>
                      <strong>
                        {criterion.id}. {criterion.description}
                      </strong>
                      <span>{criterion.status}</span>
                    </div>
                    <pre>{criterion.evidence.join("\n")}</pre>
                  </article>
                ))}
              </div>
              <List
                title="Limites 21/22"
                items={contractBoundaries.map(
                  (boundary) =>
                    `${boundary.section}: ${boundary.status} · ${boundary.reason} · ${boundary.next_step}`,
                )}
              />
              <h2>Resultado esperado</h2>
              <div className="auditList">
                {expectedResult.map((line) => (
                  <article className="auditItem" key={line.order}>
                    <div>
                      <strong>{line.text}</strong>
                      <span>{line.evidence.join(", ")}</span>
                    </div>
                  </article>
                ))}
              </div>
            </div>
          </section>
        )}

        {active === "roadmap" && (
          <section className="panel editorGrid">
            <div>
              <h2>Roadmap tecnico</h2>
              <div className="knowledgeGrid">
                {roadmap.map((phase) => (
                  <article className="knowledgeItem" key={phase.id}>
                    <strong>
                      {phase.id}. {phase.name}
                    </strong>
                    <span>{phase.status}</span>
                    <List title="Items" items={phase.items} />
                  </article>
                ))}
              </div>
            </div>
            <div className="inspector">
              <h2>Observabilidad</h2>
              <div className="auditList">
                {observability.map((metric) => (
                  <article className="auditItem" key={metric.id}>
                    <div>
                      <strong>{metric.id}</strong>
                      <span>
                        {metric.status} · {metric.source}
                      </span>
                    </div>
                  </article>
                ))}
              </div>
            </div>
          </section>
        )}

        {active === "audit" && (
          <section className="panel">
            <div className="auditSection">
              <h2>Historial de consultas de conocimiento</h2>
              <div className="metricGrid">
                <Metric label="Consultas" value={knowledgeQuerySummary?.total_count ?? 0} />
                <Metric label="Con resultado" value={knowledgeQuerySummary?.hit_count ?? 0} />
                <Metric label="Sin resultado" value={knowledgeQuerySummary?.empty_count ?? 0} />
              </div>
              <p className="note">
                Ultima consulta:{" "}
                {knowledgeQuerySummary?.last_query_at
                  ? formatDate(knowledgeQuerySummary.last_query_at)
                  : "sin consultas"}
              </p>
              <div className="rowActions">
                <select
                  aria-label="Limite historial"
                  onChange={(event) =>
                    handleKnowledgeQueryHistoryLimit(Number.parseInt(event.target.value, 10))
                  }
                  value={knowledgeQueryHistoryLimit}
                >
                  {[20, 50, 100].map((limit) => (
                    <option key={limit} value={limit}>
                      {limit} consultas
                    </option>
                  ))}
                </select>
              </div>
              {knowledgeQueryHistory.length === 0 ? (
                <p className="note">Todavia no hay consultas de conocimiento registradas.</p>
              ) : (
                <div className="auditList">
                  {knowledgeQueryHistory.map((item) => (
                    <article className="auditItem" key={item.event_id}>
                      <div>
                        <strong>{item.version} -&gt; consulta</strong>
                        <span>
                          {item.has_results ? "con resultado" : "sin resultado"} ·{" "}
                          {item.query_length} caracteres · limite {item.limit}
                        </span>
                      </div>
                      <time>{formatDate(item.created_at)}</time>
                      <div className="rowActions">
                        <button
                          className="ghostButton"
                          onClick={() =>
                            setSelectedKnowledgeQueryEventId((current) =>
                              current === item.event_id ? null : item.event_id,
                            )
                          }
                          type="button"
                        >
                          Detalle
                        </button>
                        <button
                          className="ghostButton"
                          onClick={() => handleExploreKnowledgeVersion(item.version)}
                          type="button"
                        >
                          Ver version consultada
                        </button>
                      </div>
                      <pre>
                        {`${item.card_count} fichas · ${item.claim_count} claims · ${item.evidence_count} evidencias · ${item.pending_validation_count} validaciones pendientes`}
                      </pre>
                      {selectedKnowledgeQueryEventId === item.event_id && (
                        <dl className="auditDetail">
                          <div>
                            <dt>Evento</dt>
                            <dd>{item.event_id}</dd>
                          </div>
                          <div>
                            <dt>Version</dt>
                            <dd>{item.version}</dd>
                          </div>
                          <div>
                            <dt>Resultado</dt>
                            <dd>{item.has_results ? "con resultado" : "sin resultado"}</dd>
                          </div>
                          <div>
                            <dt>Limite</dt>
                            <dd>{item.limit}</dd>
                          </div>
                          <div>
                            <dt>Longitud</dt>
                            <dd>{item.query_length} caracteres</dd>
                          </div>
                          <div>
                            <dt>Recorrido</dt>
                            <dd>
                              {item.card_count} fichas · {item.claim_count} claims ·{" "}
                              {item.evidence_count} evidencias
                            </dd>
                          </div>
                          <div>
                            <dt>Validacion</dt>
                            <dd>{item.pending_validation_count} pendientes</dd>
                          </div>
                        </dl>
                      )}
                    </article>
                  ))}
                </div>
              )}
            </div>
            <div className="auditSection">
              <h2>Eventos recientes</h2>
              <div className="rowActions">
                <select
                  aria-label="Filtro auditoria"
                  onChange={(event) => handleAuditFilter(event.target.value)}
                  value={auditFilter}
                >
                  {auditEventFilters.map((filter) => (
                    <option key={filter.label} value={filter.label}>
                      {filter.label}
                    </option>
                  ))}
                </select>
              </div>
              {auditEvents.length === 0 ? (
                <p className="note">Todavia no hay eventos registrados.</p>
              ) : (
                <div className="auditList">
                  {auditEvents.map((event) => (
                    <article className="auditItem" key={event.id}>
                      <div>
                        <strong>{event.event_type}</strong>
                        <span>
                          {event.entity_type} · {event.entity_id}
                        </span>
                        <KnowledgeAuditTrace event={event} />
                      </div>
                      <time>{formatDate(event.created_at)}</time>
                      <pre>{JSON.stringify(event.payload, null, 2)}</pre>
                    </article>
                  ))}
                </div>
              )}
            </div>
          </section>
        )}
      </section>
    </main>
  );
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("es", {
    dateStyle: "short",
    timeStyle: "medium",
  }).format(new Date(value));
}

function groupBy<T>(items: T[], keyFor: (item: T) => string) {
  const grouped = new Map<string, T[]>();
  for (const item of items) {
    const key = keyFor(item);
    grouped.set(key, [...(grouped.get(key) ?? []), item]);
  }
  return grouped;
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function KnowledgeAuditTrace({ event }: { event: AuditEvent }) {
  if (event.event_type !== "knowledge.query.executed") {
    return null;
  }

  const cardCount = numberPayloadValue(event.payload.card_count);
  const claimCount = numberPayloadValue(event.payload.claim_count);
  const evidenceCount = numberPayloadValue(event.payload.evidence_count);

  return (
    <span className="auditTrace">
      {event.entity_id} -&gt; consulta · {cardCount} fichas · {claimCount} claims ·{" "}
      {evidenceCount} evidencias
    </span>
  );
}

function numberPayloadValue(value: unknown) {
  return typeof value === "number" ? value : 0;
}

function loadAuditEvents(filterLabel: string, knowledgeVersion?: string) {
  const filter = auditEventFilters.find((item) => item.label === filterLabel) ?? auditEventFilters[0];
  const entityId =
    filter.eventType === "knowledge.query.executed" ? knowledgeVersion : undefined;
  return getAuditEvents(filter.eventType, filter.entityType, entityId);
}

function payloadList(value: unknown) {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.filter((item): item is string => typeof item === "string");
}

function validationLabel(confidence: number) {
  return confidence >= 0.7 ? "Validado" : "Validacion pendiente";
}

const INGESTION_PHASE_ORDER = [
  "published",
  "validated",
  "reviewed",
  "proposed",
  "extracted",
  "segmented",
  "indexed",
  "edition_registered",
  "registered",
];

const INGESTION_PHASE_LABELS: Record<string, string> = {
  published: "publicada",
  validated: "validada",
  reviewed: "revisada",
  proposed: "propuesta",
  extracted: "extraida",
  segmented: "segmentada",
  indexed: "indexada",
  edition_registered: "con edicion",
  registered: "registrada",
};

const INGESTION_BLOCKER_LABELS: Record<string, string> = {
  missing_edition: "sin edicion",
  missing_index: "sin indice",
  missing_segments: "sin segmentos",
  missing_completed_extraction: "sin extraccion",
  missing_proposals: "sin propuestas",
  missing_materialized_knowledge: "sin conocimiento",
  missing_publication: "sin publicacion",
};

function ingestionPhaseLabel(phase: string) {
  return INGESTION_PHASE_LABELS[phase] ?? phase;
}

function ingestionBlockerLabel(blocker: string) {
  return INGESTION_BLOCKER_LABELS[blocker] ?? blocker;
}

function pipelineSteps(status?: KnowledgeSourceIngestionStatus) {
  return [
    { label: "Fuente", done: status?.is_registered ?? false },
    { label: "Edicion", done: status?.has_edition ?? false },
    { label: "Indice", done: status?.has_index ?? false },
    { label: "Segmento", done: status?.has_segments ?? false },
    { label: "ExtractionRun", done: status?.has_extractions ?? false },
    { label: "Proposals", done: status?.has_proposals ?? false },
    { label: "Conocimiento", done: status?.has_materialized_knowledge ?? false },
    { label: "Publicacion", done: status?.is_published ?? false },
  ];
}

function canApproveProposal(proposal: KnowledgeProposal, versions: KnowledgeVersion[]) {
  if (proposal.status !== "proposed") {
    return false;
  }
  const version = proposal.payload.version;
  if (typeof version !== "string") {
    return false;
  }
  const targetVersion = versions.find((item) => item.id === version);
  return Boolean(targetVersion && !["published", "seed"].includes(targetVersion.status));
}

function ValidationPill({ confidence }: { confidence: number }) {
  return <span className="statusPill">{validationLabel(confidence)}</span>;
}

function List({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="listBlock">
      <h3>{title}</h3>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

function Meter({ label, value, max = 1000 }: { label: string; value: number; max?: number }) {
  const width = `${Math.min(100, Math.abs(value / max) * 100)}%`;
  return (
    <div className="meter">
      <span>
        {label}: {value}
      </span>
      <div>
        <i style={{ width }} />
      </div>
    </div>
  );
}
