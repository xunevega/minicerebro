import { useEffect, useMemo, useState } from "react";

import { getOficioFichas, saveRevisionFeedback } from "./services/api";
import type { OficioFicha, ProfileKnowledgeCard } from "./types/api";

const ramas: Array<{ id: OficioFicha["rama"] | "todas"; label: string }> = [
  { id: "todas", label: "Todas" },
  { id: "lengua", label: "La lengua como material" },
  { id: "recursos", label: "Recursos expresivos" },
  { id: "composicion", label: "Composición" },
  { id: "voz", label: "Voz y estilo" },
  { id: "generos", label: "Géneros" },
  { id: "criterio", label: "Criterio" },
];

const accionLabels: Record<string, string> = {
  correction: "Corregir",
  rewrite: "Editar",
  sendable: "Hacer enviable",
  review: "Revisar por bloques",
  read: "Leer con fichas",
  continue: "Continuar",
  variants: "Variantes",
};

const miradaLabels: Record<string, string> = {
  comprension: "comprensión",
  estructura: "estructura",
  tono: "tono",
  limpieza: "limpieza",
};

const metricaLabels: Record<string, string> = {
  frase_larga: "frases muy largas",
  repeticion_cercana: "palabras repetidas muy cerca",
  anafora: "frases seguidas que empiezan igual",
  deriva_estilo: "cambio de ritmo entre el principio y el final",
  parrafo_largo: "párrafos muy largos",
  bloque_unico: "todo el texto en un solo bloque",
};

const relacionLabels: Record<string, string> = {
  prioridad_sobre: "Prevalece sobre",
  conflicto_con: "Choca con",
  requiere: "Requiere",
};

function normalize(value: string) {
  return value
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "");
}

type Props = {
  context: string;
  profileCards: ProfileKnowledgeCard[];
  onProfileChanged: () => Promise<void> | void;
};

export function OficioLibrary({ context, profileCards, onProfileChanged }: Props) {
  const [fichas, setFichas] = useState<OficioFicha[]>([]);
  const [rama, setRama] = useState<(typeof ramas)[number]["id"]>("todas");
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getOficioFichas()
      .then((items) => {
        const order = ramas.map((item) => item.id);
        items.sort((left, right) => order.indexOf(left.rama) - order.indexOf(right.rama));
        setFichas(items);
        setSelectedId((current) => current ?? items[0]?.id ?? null);
      })
      .catch((nextError: unknown) => setError((nextError as Error).message));
  }, []);

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
      if (rama !== "todas" && ficha.rama !== rama) return false;
      if (!needle) return true;
      return normalize(`${ficha.nombre} ${ficha.regla} ${ficha.aplica}`).includes(needle);
    });
  }, [fichas, rama, query]);

  const selected = selectedId ? (byId.get(selectedId) ?? null) : null;

  async function mark(ficha: OficioFicha, stance: "me_sirve" | "no_me_sirve") {
    setBusy(true);
    setError(null);
    try {
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
    } catch (nextError) {
      setError((nextError as Error).message);
    } finally {
      setBusy(false);
    }
  }

  function triggers(ficha: OficioFicha) {
    const lines: string[] = [];
    if (ficha.senales.length) lines.push("Cuando su señal aparece en tu texto.");
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
        <span className="statusPill">{fichas.length} fichas</span>
      </div>
      {error ? <p className="errorText">{error}</p> : null}
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
                className={ficha.id === selectedId ? "oficioItem active" : "oficioItem"}
                onClick={() => setSelectedId(ficha.id)}
                type="button"
              >
                <strong>{ficha.nombre}</strong>
                <span>{ramas.find((item) => item.id === ficha.rama)?.label}</span>
                {stanceLabel(ficha.id) ? <em>{stanceLabel(ficha.id)}</em> : null}
              </button>
            </li>
          ))}
          {!visible.length ? <li className="note">Ninguna ficha coincide.</li> : null}
        </ul>
        {selected ? (
          <article className="oficioDetail" aria-live="polite">
            <span className="fieldRole">{ramas.find((item) => item.id === selected.rama)?.label}</span>
            <h3>{selected.nombre}</h3>
            <p className="oficioRule">{selected.regla}</p>
            <div className="oficioColumns">
              <div>
                <span className="revisionLabel">Aplica</span>
                <p>{selected.aplica}</p>
              </div>
              <div>
                <span className="revisionLabel">No aplica</span>
                <p>{selected.no_aplica}</p>
              </div>
            </div>
            <span className="revisionLabel">Ejemplos</span>
            {selected.ejemplos.map((ejemplo) => (
              <div className="oficioExample" key={ejemplo.mal}>
                <p className="oficioBad">{ejemplo.mal}</p>
                <p className="oficioGood">{ejemplo.bien}</p>
                <p className="note">{ejemplo.porque}</p>
              </div>
            ))}
            <span className="revisionLabel">Cuándo la usa Editados</span>
            <ul className="oficioTriggers">
              {triggers(selected).map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
            {selected.relaciones.length ? (
              <>
                <span className="revisionLabel">Relación con otras fichas</span>
                <ul className="oficioRelations">
                  {selected.relaciones.map((relacion) => (
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
              Fuente: {selected.fuente.obra} · {selected.fuente.localizador}
            </p>
            <div className="buttonRow compactRow" aria-label={`Tu criterio sobre ${selected.nombre}`}>
              <button className="secondaryButton" disabled={busy} onClick={() => void mark(selected, "me_sirve")} type="button">
                Me sirve
              </button>
              <button className="secondaryButton" disabled={busy} onClick={() => void mark(selected, "no_me_sirve")} type="button">
                No va conmigo
              </button>
              {stanceLabel(selected.id) ? <span className="statusPill">{stanceLabel(selected.id)}</span> : null}
            </div>
            <p className="note">
              Tu postura no cambia la ficha: cambia cuánto pesa al elegir fichas para tus textos. Una ficha que
              descartas solo vuelve si el texto la pide con una señal clara.
            </p>
          </article>
        ) : null}
      </div>
    </section>
  );
}
