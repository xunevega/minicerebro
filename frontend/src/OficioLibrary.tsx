import { type ReactElement, useCallback, useEffect, useMemo, useState } from "react";

import { OficioEditor } from "./OficioEditor";
import {
  accionLabels,
  campoLabels,
  emptyFicha,
  fieldText,
  metricaLabels,
  miradaLabels,
  normalize,
  propuestaTipoLabels,
  ramaLabel,
  ramas,
  relacionLabels,
} from "./oficioLabels";
import {
  acceptOficioProposal,
  generateOficioProposals,
  getEditorialLine,
  getOficioFichas,
  getOficioProposals,
  getOficioVersions,
  rejectOficioProposal,
  restoreOficioFicha,
  saveRevisionFeedback,
  setOficioFichaActive,
} from "./services/api";
import type {
  EditorialLine,
  OficioFicha,
  OficioFichaData,
  OficioFichaVersion,
  OficioPropuesta,
  ProfileKnowledgeCard,
} from "./types/api";

type Props = {
  context: string;
  profileCards: ProfileKnowledgeCard[];
  onProfileChanged: () => Promise<void> | void;
  canEdit?: boolean;
};

type Mode =
  | { kind: "view" }
  | { kind: "edit"; nueva: boolean; initial: OficioFichaData }
  | { kind: "history"; items: OficioFichaVersion[] }
  | { kind: "proposals" }
  | { kind: "editProposal"; proposal: OficioPropuesta };

const campos = Object.keys(campoLabels) as Array<keyof OficioFichaData>;

function toData(ficha: OficioFicha): OficioFichaData {
  const { version: _version, origen: _origen, activa: _activa, updated_at: _updated, ...data } = ficha;
  return data;
}

function changedFields(before: OficioFichaData | null, after: OficioFichaData) {
  return campos.filter((campo) => fieldText(before, campo) !== fieldText(after, campo));
}

function formatDate(value: string) {
  try {
    return new Date(value).toLocaleString("es-ES", { dateStyle: "medium", timeStyle: "short" });
  } catch {
    return value;
  }
}

function FieldDiff({ before, after }: { before: OficioFichaData | null; after: OficioFichaData }) {
  const fields = changedFields(before, after);
  if (!fields.length) return <p className="note">Sin cambios en el contenido de la ficha.</p>;
  return (
    <div className="oficioDiff">
      {fields.map((campo) => (
        <div className="oficioDiffRow" key={campo}>
          <span className="revisionLabel">{campoLabels[campo]}</span>
          <div className="oficioDiffColumns">
            <pre className="oficioDiffBefore">{fieldText(before, campo) || "—"}</pre>
            <pre className="oficioDiffAfter">{fieldText(after, campo) || "—"}</pre>
          </div>
        </div>
      ))}
    </div>
  );
}

export function OficioLibrary({ context, profileCards, onProfileChanged, canEdit = false }: Props) {
  const [fichas, setFichas] = useState<OficioFicha[]>([]);
  const [rama, setRama] = useState<(typeof ramas)[number]["id"]>("todas");
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [mode, setMode] = useState<Mode>({ kind: "view" });
  const [proposals, setProposals] = useState<OficioPropuesta[]>([]);
  const [learned, setLearned] = useState<Map<string, EditorialLine["fichas"][number]>>(new Map());

  const loadFichas = useCallback(async () => {
    const items = await getOficioFichas();
    const order = ramas.map((item) => item.id);
    items.sort((left, right) => order.indexOf(left.rama) - order.indexOf(right.rama));
    setFichas(items);
    setSelectedId((current) => current ?? items[0]?.id ?? null);
  }, []);

  const loadProposals = useCallback(async () => {
    if (!canEdit) return;
    setProposals(await getOficioProposals());
  }, [canEdit]);

  useEffect(() => {
    loadFichas().catch((nextError: unknown) => setError((nextError as Error).message));
    loadProposals().catch(() => undefined);
    getEditorialLine()
      .then((line) => setLearned(new Map(line.fichas.map((item) => [item.id, item]))))
      .catch(() => undefined);
  }, [loadFichas, loadProposals]);

  const stanceById = useMemo(() => {
    const map = new Map<string, string>();
    for (const card of profileCards) {
      if (card.knowledge_version === "oficio") map.set(card.card_id, card.stance);
    }
    return map;
  }, [profileCards]);

  const byId = useMemo(() => new Map(fichas.map((ficha) => [ficha.id, ficha])), [fichas]);

  const visible = useMemo(() => {
    const needle = normalize(query.trim());
    return fichas.filter((ficha) => {
      if (!canEdit && !ficha.activa) return false;
      if (rama !== "todas" && ficha.rama !== rama) return false;
      if (!needle) return true;
      return normalize(`${ficha.nombre} ${ficha.regla} ${ficha.aplica}`).includes(needle);
    });
  }, [fichas, rama, query, canEdit]);

  const activeCount = fichas.filter((ficha) => ficha.activa).length;
  const selected = selectedId ? (byId.get(selectedId) ?? null) : null;

  async function run(task: () => Promise<void>) {
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      await task();
    } catch (nextError) {
      setError((nextError as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function mark(ficha: OficioFicha, stance: "me_sirve" | "no_me_sirve") {
    await run(async () => {
      await saveRevisionFeedback(ficha.id, {
        knowledge_version: "oficio",
        context,
        stance,
        feedback:
          stance === "me_sirve"
            ? `Me sirve la ficha «${ficha.nombre}».`
            : `La ficha «${ficha.nombre}» no va conmigo.`,
        maintained_elements: stance === "me_sirve" ? [ficha.nombre] : [],
        change_requests: stance === "no_me_sirve" ? [ficha.nombre] : [],
        user_score: stance === "me_sirve" ? 780 : 300,
      });
      await onProfileChanged();
    });
  }

  async function showHistory(ficha: OficioFicha) {
    await run(async () => {
      setMode({ kind: "history", items: await getOficioVersions(ficha.id) });
    });
  }

  async function restore(ficha: OficioFicha, version: number) {
    await run(async () => {
      await restoreOficioFicha(ficha.id, version);
      await loadFichas();
      setMode({ kind: "history", items: await getOficioVersions(ficha.id) });
      setNotice(`Restaurada la versión ${version} de «${ficha.nombre}».`);
    });
  }

  async function toggleActive(ficha: OficioFicha) {
    const motivo = ficha.activa ? "Retirada desde la Biblioteca." : "Reactivada desde la Biblioteca.";
    await run(async () => {
      await setOficioFichaActive(ficha.id, !ficha.activa, motivo);
      await loadFichas();
      setNotice(ficha.activa ? `«${ficha.nombre}» ya no se usa.` : `«${ficha.nombre}» vuelve a usarse.`);
    });
  }

  async function searchImprovements() {
    await run(async () => {
      const result = await generateOficioProposals();
      await loadProposals();
      const parts = [
        result.candidatas
          ? `${result.candidatas} fichas con indicios de fallar`
          : "Ninguna ficha con indicios de fallar por ahora",
        `${result.creadas} propuestas nuevas`,
      ];
      if (result.omitidas.length) parts.push(`${result.omitidas.length} descartadas por no pasar la validación`);
      setNotice(`${parts.join(" · ")}.`);
      setMode({ kind: "proposals" });
    });
  }

  async function decide(proposal: OficioPropuesta, accept: boolean, ficha?: OficioFichaData) {
    await run(async () => {
      if (accept) await acceptOficioProposal(proposal.id, ficha);
      else await rejectOficioProposal(proposal.id);
      await Promise.all([loadFichas(), loadProposals()]);
      setNotice(accept ? "Propuesta aceptada: la ficha ya está cambiada." : "Propuesta rechazada.");
      setMode({ kind: "proposals" });
    });
  }

  function triggers(ficha: OficioFichaData) {
    const lines: string[] = [];
    if (ficha.senales.some((senal) => senal.tipo !== "vigilancia")) {
      lines.push("Cuando aparece en tu texto lo que delata el problema.");
    }
    if (ficha.senales.some((senal) => senal.tipo === "vigilancia")) {
      lines.push("Cuando hay en tu texto un pasaje que conviene vigilar o proteger.");
    }
    if (ficha.metricas.length) {
      lines.push(`Cuando el texto tiene ${ficha.metricas.map((item) => metricaLabels[item] ?? item).join(" o ")}.`);
    }
    if (ficha.base.acciones.length) {
      lines.push(`Siempre en ${ficha.base.acciones.map((item) => accionLabels[item] ?? item).join(", ")}.`);
    }
    if (ficha.base.miradas.length) {
      lines.push(`Con la mirada ${ficha.base.miradas.map((item) => miradaLabels[item] ?? item).join(" o ")}.`);
    }
    if (ficha.generos.length) lines.push(`Solo para textos de tipo: ${ficha.generos.join(", ")}.`);
    if (!lines.length) lines.push("Cuando otra ficha elegida la requiere.");
    return lines;
  }

  const stanceLabel = (id: string) => {
    const stance = stanceById.get(id);
    if (stance === "kept" || stance === "liked") return "Te sirve";
    if (stance === "dismissed") return "Descartada por ti";
    if (stance === "changed") return "Con reparos";
    return null;
  };

  function renderDetail(current: OficioFicha) {
    return (
      <article className="oficioDetail" aria-live="polite">
        <span className="oficioMeta">
          {ramaLabel(current.rama)}
          {current.version ? ` · versión ${current.version}` : ""}
          {current.origen === "nueva" ? " · creada por ti" : current.origen === "editada" ? " · editada" : ""}
        </span>
        <h3>{current.nombre}</h3>
        {!current.activa ? <p className="statusPill warning">Desactivada: Editados no la usa.</p> : null}
        <p className="oficioRule">{current.regla}</p>
        <div className="oficioColumns">
          <div>
            <span className="revisionLabel">Aplica</span>
            <p>{current.aplica}</p>
          </div>
          <div>
            <span className="revisionLabel">No aplica</span>
            <p>{current.no_aplica}</p>
          </div>
        </div>
        <span className="revisionLabel">Ejemplos</span>
        {current.ejemplos.map((ejemplo) => (
          <div className="oficioExample" key={ejemplo.mal}>
            <p className="oficioBad">{ejemplo.mal}</p>
            <p className="oficioGood">{ejemplo.bien}</p>
            <p className="note">{ejemplo.porque}</p>
          </div>
        ))}
        <span className="revisionLabel">Cuándo la usa Editados</span>
        <ul className="oficioTriggers">
          {triggers(current).map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
        {current.relaciones.length ? (
          <>
            <span className="revisionLabel">Relación con otras fichas</span>
            <ul className="oficioRelations">
              {current.relaciones.map((relacion) => (
                <li key={`${relacion.tipo}-${relacion.ficha}`}>
                  {relacionLabels[relacion.tipo]}{" "}
                  <button className="textButton" onClick={() => setSelectedId(relacion.ficha)} type="button">
                    {byId.get(relacion.ficha)?.nombre ?? relacion.ficha}
                  </button>
                  {relacion.criterio ? <span className="note"> — {relacion.criterio}</span> : null}
                </li>
              ))}
            </ul>
          </>
        ) : null}
        <p className="note">
          Fuente: {current.fuente.obra} · {current.fuente.localizador}
        </p>
        <div className="buttonRow compactRow" aria-label={`Tu criterio sobre ${current.nombre}`}>
          <button className="secondaryButton" disabled={busy} onClick={() => void mark(current, "me_sirve")} type="button">
            Me sirve
          </button>
          <button
            className="secondaryButton"
            disabled={busy}
            onClick={() => void mark(current, "no_me_sirve")}
            type="button"
          >
            No va conmigo
          </button>
          {stanceLabel(current.id) ? <span className="statusPill">{stanceLabel(current.id)}</span> : null}
        </div>
        {learned.get(current.id) ? (
          <p className="note">
            Contigo: {learned.get(current.id)?.motivo}
            {learned.get(current.id)?.aceptadas || learned.get(current.id)?.descartadas
              ? ` (propuestas aceptadas: ${learned.get(current.id)?.aceptadas}; descartadas: ${learned.get(current.id)?.descartadas})`
              : ""}
            .
          </p>
        ) : null}
        <p className="note">
          Tu postura cambia cuánto pesa la ficha al elegir las de tus textos. Si la descartas, Editados además
          preparará una propuesta para corregirla, que verás en «Propuestas».
        </p>
        {canEdit ? (
          <div className="buttonRow compactRow" aria-label={`Editar ${current.nombre}`}>
            <button
              className="primaryButton"
              disabled={busy}
              onClick={() => setMode({ kind: "edit", nueva: false, initial: toData(current) })}
              type="button"
            >
              Editar
            </button>
            <button className="secondaryButton" disabled={busy} onClick={() => void showHistory(current)} type="button">
              Historial
            </button>
            <button className="secondaryButton" disabled={busy} onClick={() => void toggleActive(current)} type="button">
              {current.activa ? "Desactivar" : "Reactivar"}
            </button>
          </div>
        ) : null}
      </article>
    );
  }

  function renderHistory(current: OficioFicha, items: OficioFichaVersion[]) {
    return (
      <article className="oficioDetail">
        <span className="oficioMeta">Historial</span>
        <h3>{current.nombre}</h3>
        {!items.length ? (
          <p className="note">Nunca se ha editado: es la versión original de Editados.</p>
        ) : (
          <ol className="oficioVersions">
            {items.map((item, index) => {
              const previous = items[index + 1]?.data ?? null;
              const isCurrent = item.version === current.version;
              return (
                <li key={item.version}>
                  <div className="oficioVersionHead">
                    <strong>Versión {item.version}</strong>
                    <span className="note">
                      {formatDate(item.created_at)} · {item.autor || "Editados"}
                      {!item.activa ? " · desactivada" : ""}
                    </span>
                    {isCurrent ? (
                      <span className="statusPill">Vigente</span>
                    ) : (
                      <button
                        className="secondaryButton"
                        disabled={busy}
                        onClick={() => void restore(current, item.version)}
                        type="button"
                      >
                        Restaurar
                      </button>
                    )}
                  </div>
                  <p>{item.motivo}</p>
                  {previous ? (
                    <details>
                      <summary>Qué cambió</summary>
                      <FieldDiff after={item.data} before={previous} />
                    </details>
                  ) : null}
                </li>
              );
            })}
          </ol>
        )}
        <div className="buttonRow compactRow">
          <button className="secondaryButton" onClick={() => setMode({ kind: "view" })} type="button">
            Volver a la ficha
          </button>
        </div>
      </article>
    );
  }

  function renderProposals() {
    return (
      <section className="oficioProposals" aria-label="Propuestas de mejora">
        <div className="versionHeader">
          <div>
            <h3>Propuestas de mejora</h3>
            <p className="note">
              Editados las prepara cuando una ficha da indicios de fallar: la descartas, sus propuestas se
              descartan mucho, su señal salta en casi todos los textos o no entra en ninguno. Cada propuesta ya
              pasó la misma validación que una edición tuya. Nada cambia hasta que la aceptas.
            </p>
          </div>
          <button className="secondaryButton" disabled={busy} onClick={() => void searchImprovements()} type="button">
            Buscar mejoras ahora
          </button>
        </div>
        {!proposals.length ? <p className="note">No hay propuestas pendientes.</p> : null}
        {proposals.map((proposal) => {
          const nota = typeof proposal.evidencia?.nota_editor === "string" ? proposal.evidencia.nota_editor : "";
          return (
            <article className="oficioProposal" key={proposal.id}>
              <div className="oficioVersionHead">
                <strong>{proposal.actual?.nombre ?? proposal.propuesta.nombre}</strong>
                <span className="statusPill">{propuestaTipoLabels[proposal.tipo] ?? proposal.tipo}</span>
                <span className="note">{formatDate(proposal.created_at)}</span>
              </div>
              <p>{proposal.motivo}</p>
              {nota ? <p className="note">Nota del editor: {nota}</p> : null}
              <FieldDiff after={proposal.propuesta} before={proposal.actual} />
              <div className="buttonRow compactRow">
                <button className="primaryButton" disabled={busy} onClick={() => void decide(proposal, true)} type="button">
                  Aceptar
                </button>
                <button
                  className="secondaryButton"
                  disabled={busy}
                  onClick={() => setMode({ kind: "editProposal", proposal })}
                  type="button"
                >
                  Editar antes de aceptar
                </button>
                <button className="secondaryButton" disabled={busy} onClick={() => void decide(proposal, false)} type="button">
                  Rechazar
                </button>
              </div>
            </article>
          );
        })}
        <div className="buttonRow compactRow">
          <button className="secondaryButton" onClick={() => setMode({ kind: "view" })} type="button">
            Volver a las fichas
          </button>
        </div>
      </section>
    );
  }

  async function afterSave(saved: OficioFichaData, nueva: boolean) {
    await loadFichas();
    setSelectedId(saved.id);
    setMode({ kind: "view" });
    setNotice(nueva ? `Ficha «${saved.nombre}» creada.` : `Ficha «${saved.nombre}» guardada.`);
  }

  let main: ReactElement | null = null;
  if (mode.kind === "edit") {
    main = (
      <OficioEditor
        fichas={fichas}
        initial={mode.initial}
        nueva={mode.nueva}
        onCancel={() => setMode({ kind: "view" })}
        onSaved={(saved) => void afterSave(saved, mode.nueva)}
      />
    );
  } else if (mode.kind === "editProposal") {
    main = (
      <OficioEditor
        fichas={fichas}
        initial={mode.proposal.propuesta}
        nueva={false}
        onCancel={() => setMode({ kind: "proposals" })}
        onSaved={() => undefined}
        onSubmitInstead={(ficha) => decide(mode.proposal, true, ficha)}
        submitLabel="Aceptar con mis cambios"
      />
    );
  } else if (mode.kind === "proposals") {
    main = renderProposals();
  } else if (selected) {
    main = mode.kind === "history" ? renderHistory(selected, mode.items) : renderDetail(selected);
  }

  const fullWidth = mode.kind === "edit" || mode.kind === "editProposal" || mode.kind === "proposals";

  return (
    <section className="panel">
      <div className="versionHeader">
        <div>
          <h2>Fichas de oficio</h2>
          <p className="note">
            Lo que Editados sabe y usa al corregir, editar y leer tu texto: regla, cuándo aplica, cuándo no,
            ejemplos y fuente. Las elige según lo que aparece en cada texto.
          </p>
        </div>
        <div className="buttonRow compactRow">
          <span className="statusPill">{activeCount} fichas</span>
          {canEdit ? (
            <>
              <button
                className={mode.kind === "proposals" ? "phaseBadge active" : "phaseBadge"}
                onClick={() => {
                  setNotice(null);
                  setMode({ kind: "proposals" });
                }}
                type="button"
              >
                Propuestas{proposals.length ? ` (${proposals.length})` : ""}
              </button>
              <button
                className="secondaryButton"
                disabled={busy}
                onClick={() => setMode({ kind: "edit", nueva: true, initial: emptyFicha() })}
                type="button"
              >
                Nueva ficha
              </button>
            </>
          ) : null}
        </div>
      </div>
      {error ? <p className="errorText">{error}</p> : null}
      {notice ? <p className="successText">{notice}</p> : null}
      {fullWidth ? (
        main
      ) : (
        <>
          <div className="libraryFilterBar" aria-label="Ramas del oficio">
            {ramas.map((item) => (
              <button
                className={rama === item.id ? "phaseBadge active" : "phaseBadge"}
                key={item.id}
                onClick={() => setRama(item.id)}
                type="button"
              >
                {item.label}
              </button>
            ))}
          </div>
          <label className="oficioSearch">
            <span className="srOnly">Buscar ficha</span>
            <input
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Buscar: dequeísmo, conectores, diálogo…"
              type="search"
              value={query}
            />
          </label>
          <div className="oficioLibrary">
            <ul className="oficioList" aria-label="Fichas">
              {visible.map((ficha) => (
                <li key={ficha.id}>
                  <button
                    className={[
                      "oficioItem",
                      ficha.id === selectedId ? "active" : "",
                      ficha.activa ? "" : "inactive",
                    ]
                      .filter(Boolean)
                      .join(" ")}
                    onClick={() => {
                      setSelectedId(ficha.id);
                      setMode({ kind: "view" });
                    }}
                    type="button"
                  >
                    <strong>{ficha.nombre}</strong>
                    <span>{ramaLabel(ficha.rama)}</span>
                    {!ficha.activa ? <em>Desactivada</em> : stanceLabel(ficha.id) ? <em>{stanceLabel(ficha.id)}</em> : null}
                  </button>
                </li>
              ))}
              {!visible.length ? <li className="note">Ninguna ficha coincide.</li> : null}
            </ul>
            {main}
          </div>
        </>
      )}
    </section>
  );
}
