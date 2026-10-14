import { useCallback, useEffect, useState } from "react";

import { getFichaAutor, getFichaAutorVersions, restoreFichaAutor, saveFichaAutor } from "./services/api";
import type { FichaAutor as FichaAutorData, FichaAutorEditable } from "./types/api";

type Props = { context: string; email?: string | null };

const toLines = (items: string[]) => items.join("\n");
const fromLines = (text: string) =>
  text
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

function formatDate(value: string) {
  try {
    return new Date(value).toLocaleString("es-ES", { dateStyle: "medium", timeStyle: "short" });
  } catch {
    return value;
  }
}

export function FichaAutor({ context, email }: Props) {
  const [ficha, setFicha] = useState<FichaAutorData | null>(null);
  const [draft, setDraft] = useState({ presentacion: "", me_gusta: "", evito: "", notas: "" });
  const [versions, setVersions] = useState<Array<{ version: number; data: FichaAutorEditable; created_at: string }> | null>(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    const next = await getFichaAutor(context);
    setFicha(next);
    setDraft({
      presentacion: next.editable.presentacion,
      me_gusta: toLines(next.editable.me_gusta),
      evito: toLines(next.editable.evito),
      notas: next.editable.notas,
    });
  }, [context]);

  useEffect(() => {
    load().catch((nextError: unknown) => setError((nextError as Error).message));
  }, [load]);

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

  async function save() {
    await run(async () => {
      const result = await saveFichaAutor({
        presentacion: draft.presentacion,
        me_gusta: fromLines(draft.me_gusta),
        evito: fromLines(draft.evito),
        notas: draft.notas,
      });
      await load();
      if (versions) setVersions(await getFichaAutorVersions());
      setNotice(`Ficha guardada (versión ${result.version}).`);
    });
  }

  async function toggleVersions() {
    if (versions) {
      setVersions(null);
      return;
    }
    await run(async () => setVersions(await getFichaAutorVersions()));
  }

  async function restore(version: number) {
    await run(async () => {
      const result = await restoreFichaAutor(version);
      await load();
      setVersions(await getFichaAutorVersions());
      setNotice(`Restaurada la versión ${version} como versión ${result.version}.`);
    });
  }

  if (!ficha) return error ? <p className="errorText">{error}</p> : null;

  return (
    <section className="panel fichaAutor" aria-label="Tu ficha de autor">
      <div className="versionHeader">
        <div>
          <h2>Tu ficha de autor</h2>
          <p className="note">
            Quién eres como escritor, en un solo sitio y con tus palabras. Se guarda en tu cuenta
            {email ? ` (${email})` : ""} con historial de versiones, y Editados la envía al modelo al escribir,
            revisar y diagnosticar. Manda sobre los gustos generales, nunca sobre la norma ni sobre los matices
            de tu texto.
          </p>
        </div>
        <div className="buttonRow compactRow">
          <span className="statusPill">{ficha.version ? `Versión ${ficha.version}` : "Sin guardar todavía"}</span>
          <button className="secondaryButton" disabled={busy} onClick={() => void toggleVersions()} type="button">
            {versions ? "Ocultar historial" : "Historial"}
          </button>
        </div>
      </div>
      {error ? <p className="errorText">{error}</p> : null}
      {notice ? <p className="successText">{notice}</p> : null}

      <form
        className="oficioEditor"
        onSubmit={(event) => {
          event.preventDefault();
          void save();
        }}
      >
        <label>
          Cómo escribes
          <textarea
            onChange={(event) => setDraft({ ...draft, presentacion: event.target.value })}
            placeholder="Qué escribes, para quién y cómo suena tu voz."
            rows={3}
            value={draft.presentacion}
          />
        </label>
        <div className="oficioEditorGrid">
          <label>
            Te gusta (una cosa por línea)
            <textarea
              onChange={(event) => setDraft({ ...draft, me_gusta: event.target.value })}
              placeholder={"Frases largas y razonadas\nIronía seca"}
              rows={5}
              value={draft.me_gusta}
            />
          </label>
          <label>
            Evitas (una cosa por línea)
            <textarea
              onChange={(event) => setDraft({ ...draft, evito: event.target.value })}
              placeholder={"Adverbios en -mente\nTópicos de cierre"}
              rows={5}
              value={draft.evito}
            />
          </label>
        </div>
        <label>
          Notas
          <textarea
            onChange={(event) => setDraft({ ...draft, notas: event.target.value })}
            placeholder="Cualquier otra cosa que un editor debería saber de ti."
            rows={2}
            value={draft.notas}
          />
        </label>
        <div className="buttonRow compactRow">
          <button className="primaryButton" disabled={busy} type="submit">
            Guardar ficha
          </button>
        </div>
      </form>

      {versions ? (
        <ol className="oficioVersions">
          {versions.map((item) => (
            <li key={item.version}>
              <div className="oficioVersionHead">
                <strong>Versión {item.version}</strong>
                <span className="note">{formatDate(item.created_at)}</span>
                {item.version === ficha.version ? (
                  <span className="statusPill">Vigente</span>
                ) : (
                  <button className="secondaryButton" disabled={busy} onClick={() => void restore(item.version)} type="button">
                    Restaurar
                  </button>
                )}
              </div>
              <p className="note">
                {item.data.presentacion || "Sin descripción"} · {item.data.me_gusta.length} gustos ·{" "}
                {item.data.evito.length} cosas que evitas
              </p>
            </li>
          ))}
          {!versions.length ? <li className="note">Todavía no hay versiones guardadas.</li> : null}
        </ol>
      ) : null}

      <span className="revisionLabel">Lo que Editados sabe por tus decisiones</span>
      <div className="oficioColumns">
        <div>
          <strong>Gustos confirmados</strong>
          <ul className="lineaList">
            {ficha.gustos_aceptados.map((item) => (
              <li key={item}>{item}</li>
            ))}
            {!ficha.gustos_aceptados.length ? <li className="note">Ninguno todavía.</li> : null}
          </ul>
          {ficha.gustos_rechazados.length ? (
            <>
              <strong>Interpretaciones que rechazaste</strong>
              <ul className="lineaList">
                {ficha.gustos_rechazados.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </>
          ) : null}
        </div>
        <div>
          <strong>Fichas de oficio que has valorado</strong>
          <ul className="lineaList">
            {ficha.posturas.map((item) => (
              <li key={item.id}>
                {item.nombre}: {item.postura}
              </li>
            ))}
            {!ficha.posturas.length ? <li className="note">Ninguna todavía.</li> : null}
          </ul>
          <strong>Rasgos de estilo</strong>
          <ul className="lineaList">
            {ficha.rasgos.map((item) => (
              <li key={item.clave}>
                {item.texto}: {item.nivel}
                {item.propio ? "" : " (valor de partida)"}
              </li>
            ))}
          </ul>
        </div>
      </div>
      {ficha.linea.length ? (
        <>
          <strong>Tu línea editorial</strong>
          <ul className="lineaList">
            {ficha.linea.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </>
      ) : null}
      <details className="quietDetails">
        <summary>Ver lo que recibe el modelo</summary>
        <pre className="fichaAutorPrompt">{ficha.prompt || "Todavía no hay nada que enviar: la ficha está vacía."}</pre>
      </details>
    </section>
  );
}
