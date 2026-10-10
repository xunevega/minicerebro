import { useMemo, useState } from "react";

import type { BlockReviewResult, ReviewBlock, ReviewChoice } from "./types/api";

type Choice = ReviewChoice["chosen"];

const DIAGNOSIS_LABELS: Record<string, string> = {
  confuso: "Confuso",
  pesado: "Pesado",
  falta_fuerza: "Le falta fuerza",
  idea_suelta: "Idea suelta",
  no_cuadra: "No cuadra",
  orden: "Orden",
  redundante: "Redundante",
  otro: "Otro",
};

type Props = {
  result: BlockReviewResult;
  onApply: (text: string) => void;
  onChoicesRecorded: (choices: ReviewChoice[]) => void;
  onClose: () => void;
};

function blockText(block: ReviewBlock, choice: Choice): string {
  if (choice === "mantener") return block.original;
  return block.alternatives.find((alt) => alt.label === choice)?.text ?? block.original;
}

function buildChoice(block: ReviewBlock, chosen: Choice, keptAfterReveal = true): ReviewChoice {
  const alternative = block.alternatives.find((alt) => alt.label === chosen);
  const probe = block.alternatives.find((alt) => alt.probe);
  return {
    block_index: block.index,
    chosen,
    diagnosis_kinds: block.diagnoses.map((diagnosis) => diagnosis.kind),
    approach: alternative?.approach ?? "",
    probe: Boolean(alternative?.probe),
    probe_kind: alternative?.probe ? alternative.probe_kind : probe ? `ofrecida:${probe.probe_kind}` : "",
    kept_after_reveal: keptAfterReveal,
  };
}

export function ReviewPanel({ result, onApply, onChoicesRecorded, onClose }: Props) {
  const problemBlocks = result.blocks.filter((block) => block.has_problem);
  const [choices, setChoices] = useState<Record<number, Choice>>({});
  const [applied, setApplied] = useState(false);
  const [undone, setUndone] = useState<Set<number>>(new Set());

  const pending = problemBlocks.filter((block) => !choices[block.index]).length;

  const finalChoices = useMemo(() => {
    const next: Record<number, Choice> = {};
    for (const block of result.blocks) {
      next[block.index] = undone.has(block.index) ? "mantener" : (choices[block.index] ?? "mantener");
    }
    return next;
  }, [choices, result.blocks, undone]);

  function composeText(selection: Record<number, Choice>) {
    return result.blocks.map((block) => blockText(block, selection[block.index] ?? "mantener")).join("\n\n");
  }

  function handleApply() {
    onApply(composeText(finalChoices));
    onChoicesRecorded(problemBlocks.map((block) => buildChoice(block, finalChoices[block.index])));
    setApplied(true);
  }

  function handleUndoTrap(block: ReviewBlock) {
    const nextUndone = new Set(undone);
    nextUndone.add(block.index);
    setUndone(nextUndone);
    const selection = { ...finalChoices, [block.index]: "mantener" as Choice };
    onApply(composeText(selection));
    onChoicesRecorded([buildChoice(block, choices[block.index] ?? "C", false)]);
  }

  const probeBlocks = problemBlocks.filter((block) => block.alternatives.some((alt) => alt.probe));

  return (
    <div className="reviewPanel">
      <div className="reviewOverview">
        <h3>Lectura del editor</h3>
        <p>{result.overview || "Sin comentarios sobre el planteamiento."}</p>
        <p className="note">
          {problemBlocks.length} de {result.blocks.length} bloques con algo que trabajar · {result.word_count} palabras
        </p>
      </div>

      {result.blocks.map((block) => {
        const selected = choices[block.index];
        return (
          <article className={`reviewBlock ${block.has_problem ? "hasProblem" : "isFine"}`} key={block.index}>
            <header>
              <strong>Bloque {block.index + 1}</strong>
              {block.has_problem ? (
                block.diagnoses.map((diagnosis) => (
                  <span className="diagnosisTag" key={diagnosis.kind}>
                    {DIAGNOSIS_LABELS[diagnosis.kind] ?? diagnosis.kind}
                  </span>
                ))
              ) : (
                <span className="diagnosisTag ok">Funciona</span>
              )}
            </header>
            {block.diagnoses.map((diagnosis) => (
              <p className="diagnosisText" key={`${diagnosis.kind}-text`}>
                {diagnosis.explanation}
              </p>
            ))}
            <details open={block.has_problem && !applied}>
              <summary>Tu versión</summary>
              <p className="blockOriginal">{block.original}</p>
            </details>
            {block.has_problem && !applied ? (
              <div className="reviewOptions" role="radiogroup" aria-label={`Opciones del bloque ${block.index + 1}`}>
                {block.alternatives.map((alt) => (
                  <label className={`reviewOption ${selected === alt.label ? "selected" : ""}`} key={alt.label}>
                    <input
                      checked={selected === alt.label}
                      name={`block-${block.index}`}
                      onChange={() => setChoices({ ...choices, [block.index]: alt.label })}
                      type="radio"
                    />
                    <span className="optionHead">
                      {alt.label} · {alt.approach}
                    </span>
                    <span className="optionText">{alt.text}</span>
                  </label>
                ))}
                <label className={`reviewOption keep ${selected === "mantener" ? "selected" : ""}`}>
                  <input
                    checked={selected === "mantener"}
                    name={`block-${block.index}`}
                    onChange={() => setChoices({ ...choices, [block.index]: "mantener" })}
                    type="radio"
                  />
                  <span className="optionHead">Mantener el mío</span>
                </label>
              </div>
            ) : null}
          </article>
        );
      })}

      {!applied ? (
        <div className="resultActions">
          <button className="primaryButton" disabled={problemBlocks.length === 0} onClick={handleApply} type="button">
            Aplicar elecciones{pending ? ` (${pending} sin elegir: se mantiene tu versión)` : ""}
          </button>
          <button className="ghostButton" onClick={onClose} type="button">
            Cerrar revisión
          </button>
        </div>
      ) : (
        <div className="reviewReveal">
          <h3>Elecciones aplicadas al borrador</h3>
          {probeBlocks.length === 0 ? (
            <p>En esta revisión no había ningún loco Iván.</p>
          ) : (
            <>
              <p>Ahora se puede contar: estas opciones eran un loco Iván.</p>
              {probeBlocks.map((block) => {
                const probe = block.alternatives.find((alt) => alt.probe);
                if (!probe) return null;
                const chosenProbe = choices[block.index] === probe.label;
                const isTrap = probe.probe_kind === "trampa";
                return (
                  <article className={`revealItem ${isTrap ? "trap" : "replan"}`} key={block.index}>
                    <strong>
                      Bloque {block.index + 1}, opción {probe.label}:{" "}
                      {isTrap ? "era una trampa" : "era un replanteamiento fuera de tu línea"}
                    </strong>
                    <p>{probe.probe_reveal || "Sin explicación del modelo."}</p>
                    {chosenProbe && isTrap ? (
                      undone.has(block.index) ? (
                        <p className="note">Deshecho: el bloque vuelve a tu versión original.</p>
                      ) : (
                        <>
                          <p className="note">La elegiste, así que ahora está en tu borrador.</p>
                          <button className="secondaryButton" onClick={() => handleUndoTrap(block)} type="button">
                            Deshacer este bloque
                          </button>
                        </>
                      )
                    ) : chosenProbe ? (
                      <p className="note">La elegiste. Si se repite, Editados lo tomará como un cambio de gusto.</p>
                    ) : (
                      <p className="note">No la elegiste.</p>
                    )}
                  </article>
                );
              })}
            </>
          )}
          <button className="ghostButton" onClick={onClose} type="button">
            Cerrar revisión
          </button>
        </div>
      )}
    </div>
  );
}
