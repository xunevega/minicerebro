import { useEffect, useMemo, useState } from "react";
import { BookOpen, Brain, FilePenLine, GitCompare, History, PenLine, SlidersHorizontal } from "lucide-react";
import {
  applyScoreProposal,
  compareTexts,
  createPreference,
  deletePreference,
  getAuditEvents,
  generateText,
  getKnowledgeStatus,
  getPreferences,
  getProfileSummary,
  getScoreProposal,
  getScores,
  updatePreferenceStatus,
  updateScore,
} from "./services/api";
import type {
  AuditEvent,
  ComparisonResult,
  GenerationAction,
  GenerationResult,
  KnowledgeStatus,
  Preference,
  PreferenceStatus,
  ProfileSummary,
  ScoreProposal,
  ScoreVariable,
} from "./types/api";

const tabs = [
  { id: "knowledge", label: "Conocimiento", icon: BookOpen },
  { id: "preferences", label: "Preferencias", icon: PenLine },
  { id: "profile", label: "Lo que sabe", icon: Brain },
  { id: "scoring", label: "Scoring", icon: SlidersHorizontal },
  { id: "editor", label: "Editor", icon: FilePenLine },
  { id: "compare", label: "Comparador", icon: GitCompare },
  { id: "audit", label: "Auditoria", icon: History },
] as const;

const contexts = ["general", "ensayo", "articulo", "tecnico", "publicitario", "narrativa"] as const;

type TabId = (typeof tabs)[number]["id"];

export function App() {
  const [active, setActive] = useState<TabId>("knowledge");
  const [activeContext, setActiveContext] = useState("general");
  const [knowledge, setKnowledge] = useState<KnowledgeStatus | null>(null);
  const [summary, setSummary] = useState<ProfileSummary | null>(null);
  const [scores, setScores] = useState<ScoreVariable[]>([]);
  const [preferenceText, setPreferenceText] = useState("Me gusta un estilo sobrio, preciso y con ritmo.");
  const [preference, setPreference] = useState<Preference | null>(null);
  const [preferences, setPreferences] = useState<Preference[]>([]);
  const [scoreProposal, setScoreProposal] = useState<ScoreProposal | null>(null);
  const [original, setOriginal] = useState("Este texto explica una idea de manera general.");
  const [revised, setRevised] = useState("Este texto explica una idea con mas precision y menos rodeo.");
  const [comparison, setComparison] = useState<ComparisonResult | null>(null);
  const [editorText, setEditorText] = useState("Escribe aqui una idea o un texto para trabajar.");
  const [editorAction, setEditorAction] = useState<GenerationAction>("rewrite");
  const [editorIntensity, setEditorIntensity] = useState(500);
  const [protectedTerms, setProtectedTerms] = useState("");
  const [generation, setGeneration] = useState<GenerationResult | null>(null);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [scoreReason, setScoreReason] = useState("Ajuste manual revisado en la pantalla de scoring.");
  const [savingScoreKey, setSavingScoreKey] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      getKnowledgeStatus(),
      getProfileSummary(),
      getScores(activeContext),
      getPreferences(activeContext),
      getAuditEvents(),
    ])
      .then(([knowledgeData, summaryData, scoreData, preferenceData, auditData]) => {
        setKnowledge(knowledgeData);
        setSummary(summaryData);
        setScores(scoreData);
        setPreferences(preferenceData);
        setAuditEvents(auditData);
      })
      .catch((nextError: Error) => setError(nextError.message));
  }, [activeContext]);

  const averageConfidence = useMemo(() => {
    if (scores.length === 0) return 0;
    return scores.reduce((total, item) => total + item.confidence, 0) / scores.length;
  }, [scores]);

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
      setAuditEvents(await getAuditEvents());
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
                  <List title="Variables usadas" items={generation.used_profile_variables} />
                </>
              ) : (
                <p className="note">El editor usa el perfil del contexto activo sin aplicar aprendizaje.</p>
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
            </div>
            <p className="note">{summary?.confidence_note}</p>
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
                </>
              ) : (
                <p className="note">El comparador mide modificacion y adecuacion sin actualizar el perfil.</p>
              )}
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
