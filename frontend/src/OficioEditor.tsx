import { useState } from "react";

import {
  accionLabels,
  metricaLabels,
  miradaLabels,
  ramas,
  relacionLabels,
  slugify,
} from "./oficioLabels";
import { createOficioFicha, updateOficioFicha, validateOficioFicha } from "./services/api";
import type { OficioFicha, OficioFichaData, OficioSenal } from "./types/api";

type Props = {
  initial: OficioFichaData;
  nueva: boolean;
  fichas: OficioFicha[];
  /** Si se indica, «Guardar» no guarda: entrega la ficha (para aceptar una propuesta editada). */
  onSubmitInstead?: (ficha: OficioFichaData) => Promise<void>;
  submitLabel?: string;
  onSaved: (ficha: OficioFichaData) => void;
  onCancel: () => void;
};

const acciones = ["correction", "rewrite", "sendable", "review", "read"];
const miradas = ["comprension", "estructura", "tono", "limpieza"];

function toggle(list: string[], value: string) {
  return list.includes(value) ? list.filter((item) => item !== value) : [...list, value];
}

export function OficioEditor({ initial, nueva, fichas, onSubmitInstead, submitLabel, onSaved, onCancel }: Props) {
  const [ficha, setFicha] = useState<OficioFichaData>(() => structuredClone(initial));
  const [motivo, setMotivo] = useState("");
  const [problems, setProblems] = useState<string[]>([]);
  const [checked, setChecked] = useState<"ok" | null>(null);
  const [busy, setBusy] = useState(false);

  function update<K extends keyof OficioFichaData>(key: K, value: OficioFichaData[K]) {
    setFicha((current) => ({ ...current, [key]: value }));
    setChecked(null);
  }

  function updateSenal(index: number, patch: Partial<OficioSenal>) {
    update(
      "senales",
      ficha.senales.map((senal, position) => (position === index ? { ...senal, ...patch } : senal)),
    );
  }

  const prepared = (): OficioFichaData => ({
    ...ficha,
    id: nueva ? ficha.id || slugify(ficha.nombre) : ficha.id,
    generos: ficha.generos.map((item) => item.trim()).filter(Boolean),
  });

  async function check() {
    setBusy(true);
    setProblems([]);
    try {
      const result = await validateOficioFicha(prepared(), nueva);
      setProblems(result.problemas);
      setChecked(result.valida ? "ok" : null);
    } catch (nextError) {
      setProblems((nextError as Error).message.split("\n"));
    } finally {
      setBusy(false);
    }
  }

  async function save() {
    setBusy(true);
    setProblems([]);
    try {
      const data = prepared();
      if (onSubmitInstead) {
        await onSubmitInstead(data);
        onSaved(data);
        return;
      }
      if (!motivo.trim()) {
        setProblems(["Indica el motivo del cambio."]);
        return;
      }
      const saved = nueva ? await createOficioFicha(data, motivo) : await updateOficioFicha(data, motivo);
      onSaved(saved);
    } catch (nextError) {
      setProblems((nextError as Error).message.split("\n"));
    } finally {
      setBusy(false);
    }
  }

  const others = fichas.filter((item) => item.id !== ficha.id && item.activa !== false);

  return (
    <form
      className="oficioEditor"
      onSubmit={(event) => {
        event.preventDefault();
        void save();
      }}
    >
      <h3>{nueva ? "Nueva ficha" : `Editar «${initial.nombre}»`}</h3>

      <div className="oficioEditorGrid">
        <label>
          Nombre
          <input
            onChange={(event) => update("nombre", event.target.value)}
            required
            value={ficha.nombre}
          />
        </label>
        <label>
          Rama
          <select onChange={(event) => update("rama", event.target.value as OficioFichaData["rama"])} value={ficha.rama}>
            {ramas
              .filter((item) => item.id !== "todas")
              .map((item) => (
                <option key={item.id} value={item.id}>
                  {item.label}
                </option>
              ))}
          </select>
        </label>
        {nueva ? (
          <label>
            Identificador
            <input
              onChange={(event) => update("id", slugify(event.target.value))}
              placeholder={slugify(ficha.nombre) || "se-genera-del-nombre"}
              value={ficha.id}
            />
          </label>
        ) : null}
      </div>

      <label>
        Regla
        <textarea onChange={(event) => update("regla", event.target.value)} required rows={3} value={ficha.regla} />
      </label>
      <div className="oficioEditorGrid">
        <label>
          Aplica
          <textarea onChange={(event) => update("aplica", event.target.value)} required rows={3} value={ficha.aplica} />
        </label>
        <label>
          No aplica
          <textarea
            onChange={(event) => update("no_aplica", event.target.value)}
            required
            rows={3}
            value={ficha.no_aplica}
          />
        </label>
      </div>

      <fieldset>
        <legend>Ejemplos (propios, nunca de obras)</legend>
        {ficha.ejemplos.map((ejemplo, index) => (
          <div className="oficioEditorRow" key={index}>
            <input
              aria-label={`Ejemplo ${index + 1}, mal`}
              onChange={(event) =>
                update("ejemplos", ficha.ejemplos.map((item, i) => (i === index ? { ...item, mal: event.target.value } : item)))
              }
              placeholder="Mal"
              value={ejemplo.mal}
            />
            <input
              aria-label={`Ejemplo ${index + 1}, bien`}
              onChange={(event) =>
                update("ejemplos", ficha.ejemplos.map((item, i) => (i === index ? { ...item, bien: event.target.value } : item)))
              }
              placeholder="Bien"
              value={ejemplo.bien}
            />
            <input
              aria-label={`Ejemplo ${index + 1}, porque`}
              onChange={(event) =>
                update("ejemplos", ficha.ejemplos.map((item, i) => (i === index ? { ...item, porque: event.target.value } : item)))
              }
              placeholder="Porque…"
              value={ejemplo.porque}
            />
            {ficha.ejemplos.length > 1 ? (
              <button
                className="textButton"
                onClick={() => update("ejemplos", ficha.ejemplos.filter((_, i) => i !== index))}
                type="button"
              >
                Quitar
              </button>
            ) : null}
          </div>
        ))}
        <button
          className="textButton"
          onClick={() => update("ejemplos", [...ficha.ejemplos, { mal: "", bien: "", porque: "" }])}
          type="button"
        >
          Añadir ejemplo
        </button>
      </fieldset>

      <div className="oficioEditorGrid">
        <label>
          Fuente: obra
          <input
            onChange={(event) => update("fuente", { ...ficha.fuente, obra: event.target.value })}
            required
            value={ficha.fuente.obra}
          />
        </label>
        <label>
          Fuente: localizador
          <input
            onChange={(event) => update("fuente", { ...ficha.fuente, localizador: event.target.value })}
            placeholder="s. v. «…», capítulo…"
            required
            value={ficha.fuente.localizador}
          />
        </label>
      </div>

      <fieldset>
        <legend>Señales (expresiones regulares)</legend>
        <p className="note">
          Una señal de error tiene que saltar en el primer ejemplo malo y en ningún ejemplo bueno. Las de vigilancia
          marcan un pasaje que mirar o proteger.
        </p>
        {ficha.senales.map((senal, index) => (
          <div className="oficioEditorRow" key={index}>
            <input
              aria-label={`Señal ${index + 1}`}
              className="mono"
              onChange={(event) => updateSenal(index, { patron: event.target.value })}
              placeholder="\bpatrón\b"
              value={senal.patron}
            />
            <select
              aria-label={`Tipo de la señal ${index + 1}`}
              onChange={(event) => updateSenal(index, { tipo: event.target.value as OficioSenal["tipo"] })}
              value={senal.tipo ?? "error"}
            >
              <option value="error">Error</option>
              <option value="vigilancia">Vigilancia</option>
            </select>
            <label className="inlineCheck">
              <input
                checked={senal.sensible_mayusculas ?? false}
                onChange={(event) => updateSenal(index, { sensible_mayusculas: event.target.checked })}
                type="checkbox"
              />
              Distingue mayúsculas
            </label>
            <label className="inlineCheck">
              <input
                checked={senal.tambien_sin_tildes ?? true}
                onChange={(event) => updateSenal(index, { tambien_sin_tildes: event.target.checked })}
                type="checkbox"
              />
              También sin tildes
            </label>
            <button
              className="textButton"
              onClick={() => update("senales", ficha.senales.filter((_, i) => i !== index))}
              type="button"
            >
              Quitar
            </button>
          </div>
        ))}
        <button
          className="textButton"
          onClick={() => update("senales", [...ficha.senales, { patron: "", tipo: "error" }])}
          type="button"
        >
          Añadir señal
        </button>
      </fieldset>

      <fieldset>
        <legend>Cuándo entra además</legend>
        <div className="checkGrid">
          <span className="revisionLabel">Métricas</span>
          {Object.entries(metricaLabels).map(([key, label]) => (
            <label className="inlineCheck" key={key}>
              <input
                checked={ficha.metricas.includes(key)}
                onChange={() => update("metricas", toggle(ficha.metricas, key))}
                type="checkbox"
              />
              {label}
            </label>
          ))}
        </div>
        <div className="checkGrid">
          <span className="revisionLabel">Siempre en</span>
          {acciones.map((key) => (
            <label className="inlineCheck" key={key}>
              <input
                checked={ficha.base.acciones.includes(key)}
                onChange={() => update("base", { ...ficha.base, acciones: toggle(ficha.base.acciones, key) })}
                type="checkbox"
              />
              {accionLabels[key]}
            </label>
          ))}
        </div>
        <div className="checkGrid">
          <span className="revisionLabel">Con la mirada</span>
          {miradas.map((key) => (
            <label className="inlineCheck" key={key}>
              <input
                checked={ficha.base.miradas.includes(key)}
                onChange={() => update("base", { ...ficha.base, miradas: toggle(ficha.base.miradas, key) })}
                type="checkbox"
              />
              {miradaLabels[key]}
            </label>
          ))}
        </div>
        <label>
          Solo para estos tipos de texto (separados por comas)
          <input
            onChange={(event) => update("generos", event.target.value.split(","))}
            placeholder="ensayo, opinión, columna"
            value={ficha.generos.join(",")}
          />
        </label>
        <label className="inlineCheck">
          <input
            checked={ficha.protege ?? false}
            onChange={(event) => update("protege", event.target.checked)}
            type="checkbox"
          />
          Protege el sentido al reescribir (matices, citas, analogías…)
        </label>
      </fieldset>

      <fieldset>
        <legend>Relaciones con otras fichas</legend>
        {ficha.relaciones.map((relacion, index) => (
          <div className="oficioEditorRow" key={index}>
            <select
              aria-label={`Tipo de la relación ${index + 1}`}
              onChange={(event) =>
                update(
                  "relaciones",
                  ficha.relaciones.map((item, i) =>
                    i === index ? { ...item, tipo: event.target.value as typeof item.tipo } : item,
                  ),
                )
              }
              value={relacion.tipo}
            >
              {Object.entries(relacionLabels).map(([key, label]) => (
                <option key={key} value={key}>
                  {label}
                </option>
              ))}
            </select>
            <select
              aria-label={`Ficha de la relación ${index + 1}`}
              onChange={(event) =>
                update("relaciones", ficha.relaciones.map((item, i) => (i === index ? { ...item, ficha: event.target.value } : item)))
              }
              value={relacion.ficha}
            >
              <option value="">Elige ficha…</option>
              {others.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.nombre}
                </option>
              ))}
            </select>
            <input
              aria-label={`Criterio de la relación ${index + 1}`}
              onChange={(event) =>
                update("relaciones", ficha.relaciones.map((item, i) => (i === index ? { ...item, criterio: event.target.value } : item)))
              }
              placeholder="Criterio (cuándo gana o cómo se decide)"
              value={relacion.criterio}
            />
            <button
              className="textButton"
              onClick={() => update("relaciones", ficha.relaciones.filter((_, i) => i !== index))}
              type="button"
            >
              Quitar
            </button>
          </div>
        ))}
        <button
          className="textButton"
          onClick={() => update("relaciones", [...ficha.relaciones, { tipo: "requiere", ficha: "", criterio: "" }])}
          type="button"
        >
          Añadir relación
        </button>
      </fieldset>

      {onSubmitInstead ? null : (
        <label>
          Motivo del cambio
          <input
            onChange={(event) => setMotivo(event.target.value)}
            placeholder="Qué cambias y por qué"
            required
            value={motivo}
          />
        </label>
      )}

      {problems.length ? (
        <ul className="oficioProblems" role="alert">
          {problems.map((problem) => (
            <li key={problem}>{problem}</li>
          ))}
        </ul>
      ) : null}
      {checked === "ok" ? <p className="statusPill done">Todo correcto: formato, relaciones y señales.</p> : null}

      <div className="buttonRow compactRow">
        <button className="primaryButton" disabled={busy} type="submit">
          {submitLabel ?? (nueva ? "Crear ficha" : "Guardar cambios")}
        </button>
        <button className="secondaryButton" disabled={busy} onClick={() => void check()} type="button">
          Comprobar
        </button>
        <button className="ghostButton" disabled={busy} onClick={onCancel} type="button">
          Cancelar
        </button>
      </div>
    </form>
  );
}
