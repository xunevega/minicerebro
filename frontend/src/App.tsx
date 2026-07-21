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
  KnowledgeQueryResult,
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
  const [knowledgeResult, setKnowledgeResult] = useState<KnowledgeQueryResult | null>(null);
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
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [scoreReason, setScoreReason] = useState("Ajuste manual revisado en la pantalla de scoring.");
  const [savingScoreKey, setSavingScoreKey] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      getKnowledgeStatus(),
      getKnowledgeCards(),
      getKnowledgeSources(),
      getKnowledgeNodes(),
      getKnowledgeEvidence(),
      getKnowledgeClaims(),
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
    ])
      .then(([
        knowledgeData,
        cardData,
        sourceData,
        nodeData,
        evidenceData,
        claimData,
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
      })
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

  async function handlePreference() {
    setError(null);
    try {
      const created = await createPreference(preferenceText, activeContext);
      setPreference(created);
      setPreferences((current) => [created, ...current]);
      setSummary(await getProfileSummary());
      setAuditEvents(await getAuditEvents());
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  async function handleKnowledgeQuery() {
    setError(null);
    try {
      setKnowledgeResult(await queryKnowledge(knowledgeQuery));
    } catch (nextError) {
      setError((nextError as Error).message);
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
      setAuditEvents(await getAuditEvents());
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
      setAuditEvents(await getAuditEvents());
    } catch (nextError) {
      setError((nextError as Error).message);
    }
  }

  async function handleCompare() {
    setError(null);
    try {
      setComparison(await compareTexts(original, revised, activeContext));
      setAuditEvents(await getAuditEvents());
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
      setAuditEvents(await getAuditEvents());
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
      setAuditEvents(await getAuditEvents());
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
      setAuditEvents(await getAuditEvents());
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
      setAuditEvents(await getAuditEvents());
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

  async function handleScoreAdjustment(score: ScoreVariable, manualAdjustment: number) {
    setError(null);
    setSavingScoreKey(score.key);
    try {
      const updated = await updateScore(score.key, manualAdjustment, scoreReason, activeContext);
      setScores((current) =>
        current.map((item) => (item.key === updated.variable.key ? updated.variable : item)),
      );
      setAuditEvents(await getAuditEvents());
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
                </article>
              ))}
            </div>
            <div className="proposalBox">
              <h3>Exploracion persistente</h3>
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
                            <List
                              title="Claims"
                              items={(claimsByEvidence.get(item.id) ?? []).map((claim) => {
                                const card = cardById.get(claim.card_id);
                                return `${claim.statement} -> ${card?.name ?? claim.card_id}`;
                              })}
                            />
                          </div>
                        ))}
                      </div>
                    ))}
                  </article>
                ))}
              </div>
            </div>
            <div className="proposalBox">
              <h3>Consulta</h3>
              <div className="rowActions">
                <input
                  className="textInput"
                  onChange={(event) => setKnowledgeQuery(event.target.value)}
                  value={knowledgeQuery}
                />
                <button className="primaryButton" onClick={handleKnowledgeQuery} type="button">
                  Consultar
                </button>
              </div>
              {knowledgeResult ? (
                <>
                  <p className="note">
                    Resultado para "{knowledgeResult.query}" en version {knowledgeResult.version}.
                  </p>
                  {knowledgeResult.cards.length > 0 ? (
                    <div className="knowledgeGrid">
                      {knowledgeResult.cards.map((card) => (
                        <article className="knowledgeItem" key={card.id}>
                          <strong>{card.name}</strong>
                          <span>{card.definition}</span>
                          <List
                            title="Claims"
                            items={knowledgeResult.claims
                              .filter((claim) => claim.card_id === card.id)
                              .map((claim) => claim.statement)}
                          />
                          <List
                            title="Evidencia"
                            items={knowledgeResult.evidence.map(
                              (item) => `${item.reference}: ${item.excerpt}`,
                            )}
                          />
                        </article>
                      ))}
                    </div>
                  ) : (
                    <p className="note">Sin fichas para esta consulta.</p>
                  )}
                </>
              ) : null}
            </div>
            <List title="Cobertura" items={knowledge?.coverage ?? []} />
            <List title="Lagunas" items={knowledge?.gaps ?? []} />
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
            <h2>Eventos recientes</h2>
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
                    </div>
                    <time>{formatDate(event.created_at)}</time>
                    <pre>{JSON.stringify(event.payload, null, 2)}</pre>
                  </article>
                ))}
              </div>
            )}
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
