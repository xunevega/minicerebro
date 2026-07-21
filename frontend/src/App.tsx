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
  applyScoreProposal,
  compareLabTexts,
  compareTexts,
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
  getKnowledgeQueryHistory,
  getKnowledgeQuerySummary,
  getKnowledgeStatus,
  getKnowledgeSources,
  getPersistenceStatus,
  getPreferences,
  getProfileSummary,
  getProfileStatistics,
  getScoreProposal,
  getScores,
  getObservabilityStatus,
  getTechnicalClosure,
  getTechnicalRoadmap,
  getV1Screens,
  queryKnowledge,
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
  KnowledgeNode,
  KnowledgeQueryHistoryItem,
  KnowledgeQueryResult,
  KnowledgeQuerySummary,
  KnowledgeStatus,
  KnowledgeSource,
  LabSimulationResult,
  ObservabilityMetric,
  Preference,
  PreferenceStatus,
  PersistenceDomain,
  ProfileSummary,
  ProfileStatistics,
  ScoreProposal,
  ScoreVariable,
  TechnicalClosureCriterion,
  TechnicalRoadmapPhase,
  V1Screen,
} from "./types/api";

const tabs = [
  { id: "knowledge", label: "Conocimiento", icon: BookOpen },
  { id: "preferences", label: "Preferencias", icon: PenLine },
  { id: "profile", label: "Lo que sabe", icon: Brain },
  { id: "scoring", label: "Scoring", icon: SlidersHorizontal },
  { id: "editor", label: "Editor", icon: FilePenLine },
  { id: "lab", label: "Laboratorio", icon: FlaskConical },
  { id: "compare", label: "Comparador", icon: GitCompare },
  { id: "rules", label: "Reglas", icon: ShieldCheck },
  { id: "persistence", label: "Persistencia", icon: Database },
  { id: "cerebro", label: "Cerebro", icon: Search },
  { id: "acceptance", label: "Aceptacion", icon: ClipboardCheck },
  { id: "closure", label: "Cierre", icon: Flag },
  { id: "roadmap", label: "Roadmap", icon: Route },
  { id: "screens", label: "Pantallas", icon: LayoutDashboard },
  { id: "audit", label: "Auditoria", icon: History },
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

type TabId = (typeof tabs)[number]["id"];

export function App() {
  const [active, setActive] = useState<TabId>("knowledge");
  const [activeContext, setActiveContext] = useState("general");
  const [knowledge, setKnowledge] = useState<KnowledgeStatus | null>(null);
  const [knowledgeCards, setKnowledgeCards] = useState<KnowledgeCard[]>([]);
  const [knowledgeSources, setKnowledgeSources] = useState<KnowledgeSource[]>([]);
  const [knowledgeNodes, setKnowledgeNodes] = useState<KnowledgeNode[]>([]);
  const [knowledgeEvidence, setKnowledgeEvidence] = useState<KnowledgeEvidenceItem[]>([]);
  const [knowledgeClaims, setKnowledgeClaims] = useState<KnowledgeClaim[]>([]);
  const [knowledgeQuery, setKnowledgeQuery] = useState("precision lexica");
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

  useEffect(() => {
    getKnowledgeStatus()
      .then((knowledgeData) => {
        const version = knowledgeData.version;
        return Promise.all([
          Promise.resolve(knowledgeData),
          getKnowledgeCards(version),
          getKnowledgeSources(version),
          getKnowledgeNodes(undefined, version),
          getKnowledgeEvidence(undefined, version),
          getKnowledgeClaims(undefined, version),
          getKnowledgeQueryHistory(version),
          getKnowledgeQuerySummary(version),
          getProfileSummary(),
          getProfileStatistics(activeContext),
          getContradictions(activeContext),
          getScores(activeContext),
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
        ]);
      })
      .then(
        ([
          knowledgeData,
          cardData,
          sourceData,
          nodeData,
          evidenceData,
          claimData,
          queryHistoryData,
          querySummaryData,
          summaryData,
          statisticsData,
          contradictionData,
          scoreData,
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
        setKnowledgeCards(cardData);
        setKnowledgeSources(sourceData);
        setKnowledgeNodes(nodeData);
        setKnowledgeEvidence(evidenceData);
        setKnowledgeClaims(claimData);
        setKnowledgeQueryHistory(queryHistoryData);
        setKnowledgeQuerySummary(querySummaryData);
        setSummary(summaryData);
        setStatistics(statisticsData);
        setContradictions(contradictionData);
        setScores(scoreData);
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
  const pendingKnowledgeValidationCount = useMemo(
    () =>
      [...knowledgeCards, ...knowledgeClaims, ...knowledgeEvidence].filter(
        (item) => validationLabel(item.confidence) === "Validacion pendiente",
      ).length,
    [knowledgeCards, knowledgeClaims, knowledgeEvidence],
  );

  async function refreshAuditEvents(filterLabel = auditFilter) {
    setAuditEvents(await loadAuditEvents(filterLabel, knowledge?.version));
  }

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
        await queryKnowledge(knowledgeQuery, knowledge?.version, knowledgeQueryLimit),
      );
      setKnowledgeQueryHistory(
        await getKnowledgeQueryHistory(knowledge?.version, knowledgeQueryHistoryLimit),
      );
      setKnowledgeQuerySummary(await getKnowledgeQuerySummary(knowledge?.version));
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
      setKnowledgeQueryHistory(await getKnowledgeQueryHistory(knowledge?.version, nextLimit));
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  function handleExploreKnowledgeVersion(version: string) {
    setActive("knowledge");
    setError(null);
    if (knowledge?.version !== version) {
      setError(`La version ${version} no esta cargada en la exploracion actual.`);
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
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                className={active === tab.id ? "tab active" : "tab"}
                key={tab.id}
                onClick={() => setActive(tab.id)}
                type="button"
                title={tab.label}
              >
                <Icon size={18} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <h1>{tabs.find((tab) => tab.id === active)?.label}</h1>
            <p>Conocimiento estable y perfil de preferencias permanecen separados.</p>
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

        {error ? <div className="error">{error}</div> : null}

        {active === "knowledge" && (
          <section className="panel">
            <h2>Estado de conocimiento</h2>
            <div className="metricGrid">
              <Metric label="Version" value={knowledge?.version ?? "..."} />
              <Metric label="Estado" value={knowledge?.state ?? "..."} />
              <Metric label="Cobertura" value={`${knowledge?.coverage.length ?? 0} areas`} />
              <Metric label="Validacion" value={`${pendingKnowledgeValidationCount} pendientes`} />
            </div>
            <p className="note">{knowledge?.sources_policy}</p>
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
              <p className="note">Version navegada: {knowledge?.version ?? "..."}</p>
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
                </article>
              </div>
            ) : null}
            <div className="proposalBox">
              <h3>Consulta</h3>
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
                    Resultado para "{knowledgeResult.query}" en version {knowledgeResult.version}.
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
            <List title="Fuera de alcance V1" items={knowledge?.gaps ?? []} />
          </section>
        )}

        {active === "preferences" && (
          <section className="panel editorGrid">
            <div>
              <h2>Anadir preferencia</h2>
              <textarea value={preferenceText} onChange={(event) => setPreferenceText(event.target.value)} />
              <button className="primaryButton" onClick={handlePreference} type="button">
                Revisar interpretacion
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
                            Ver propuesta
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
              <h2>Interpretacion</h2>
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
                        Aplicar al scoring
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
                Ejecutar
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
                Simular
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
              Motivo del ajuste
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
                    Proponer feedback
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
                        Aplicar
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
                          Explorar version
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
