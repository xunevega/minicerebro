import type { OficioDiagnosis, OficioFichaChecks } from "./types/api";

const estadoLabels: Record<string, string> = {
  aplicada: "Aplicada",
  en_parte: "En parte",
  sigue: "Sin aplicar",
};

export function DiagnosisNote({ diagnosis }: { diagnosis?: OficioDiagnosis | null }) {
  if (!diagnosis) return null;
  if (diagnosis.estado === "no_disponible") {
    return (
      <p className="note">
        El diagnóstico con el modelo no estaba disponible: las fichas se eligieron solo por patrones.
      </p>
    );
  }
  return (
    <div className="fichasDiagnosis">
      {diagnosis.descartadas.length ? (
        <>
          <span className="revisionLabel">Señales descartadas por el diagnóstico</span>
          <ul>
            {diagnosis.descartadas.map((item) => (
              <li key={item.id}>
                «{item.nombre}» saltó en «{item.fragmento}», pero no era un caso de esa ficha.
              </li>
            ))}
          </ul>
        </>
      ) : null}
      {diagnosis.anadidas.length ? (
        <>
          <span className="revisionLabel">Problemas sin patrón que encontró el diagnóstico</span>
          <ul>
            {diagnosis.anadidas.map((item) => (
              <li key={item.id}>
                «{item.nombre}» en «{item.fragmento}».
              </li>
            ))}
          </ul>
        </>
      ) : null}
      {!diagnosis.descartadas.length && !diagnosis.anadidas.length ? (
        <p className="note">El diagnóstico confirmó las señales y no encontró problemas sin patrón.</p>
      ) : null}
    </div>
  );
}

type Props = {
  usedFichas: string[];
  diagnosis?: OficioDiagnosis | null;
  checks?: OficioFichaChecks | null;
};

export function FichasDetalle({ usedFichas, diagnosis, checks }: Props) {
  if (!usedFichas.length && !diagnosis) return null;
  return (
    <div className="fichasDetalle">
      {usedFichas.length ? (
        <>
          <span className="revisionLabel">Fichas de oficio que recibió el modelo</span>
          <ul>
            {usedFichas.map((nombre) => (
              <li key={nombre}>{nombre}</li>
            ))}
          </ul>
        </>
      ) : null}
      {checks && (checks.comprobadas.length || checks.sin_comprobacion) ? (
        <>
          <span className="revisionLabel">¿Las aplicó?</span>
          <ul className="fichaChecks">
            {checks.comprobadas.map((item) => (
              <li key={item.id}>
                <span className={`statusPill ${item.estado === "aplicada" ? "done" : "warning"}`}>
                  {estadoLabels[item.estado] ?? item.estado}
                </span>{" "}
                «{item.nombre}». {item.detalle}
              </li>
            ))}
          </ul>
          {checks.sin_comprobacion ? (
            <p className="note">
              {checks.sin_comprobacion === 1
                ? "1 ficha es un criterio general sin comprobación automática."
                : `${checks.sin_comprobacion} fichas son criterios generales sin comprobación automática.`}
            </p>
          ) : null}
        </>
      ) : null}
      <DiagnosisNote diagnosis={diagnosis} />
    </div>
  );
}
