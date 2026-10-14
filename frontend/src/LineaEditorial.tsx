import { useEffect, useState } from "react";

import { getEditorialLine } from "./services/api";
import type { EditorialLine } from "./types/api";

export function LineaEditorial() {
  const [line, setLine] = useState<EditorialLine | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getEditorialLine()
      .then(setLine)
      .catch((nextError: unknown) => setError((nextError as Error).message));
  }, []);

  if (error) return null;
  if (!line) return null;

  const decisiones = line.propuestas.aceptadas + line.propuestas.descartadas;
  const favor = line.fichas.filter((item) => item.peso > 0).sort((a, b) => b.peso - a.peso);
  const contra = line.fichas.filter((item) => item.peso < 0).sort((a, b) => a.peso - b.peso);
  const empty = !line.tendencias.length && !line.cambios.length && !line.fichas.length;

  return (
    <section className="panel lineaEditorial" aria-label="Tu línea editorial">
      <div className="versionHeader">
        <div>
          <h2>Tu línea editorial</h2>
          <p className="note">
            Lo que Editados aprende de tus decisiones: las propuestas que aceptas o descartas en Escribir y lo
            que eliges en Revisar, incluidos los replanteamientos y las trampas del loco Iván. Se usa para elegir
            fichas, para orientar al modelo y para decidir cuántos replanteamientos te ofrece. No cambia las
            fichas.
          </p>
        </div>
        <div className="buttonRow compactRow">
          <span className="statusPill">{decisiones} propuestas decididas</span>
          <span className="statusPill">{line.elecciones} elecciones en Revisar</span>
        </div>
      </div>
      {empty ? (
        <p className="note">
          Todavía no hay decisiones suficientes. Hacen falta al menos 3 propuestas con la misma ficha o 5
          elecciones en Revisar para sacar una tendencia.
        </p>
      ) : null}
      {line.tendencias.length ? (
        <>
          <span className="revisionLabel">Tendencias</span>
          <ul className="lineaList">
            {line.tendencias.map((item) => (
              <li key={item.clave}>{item.texto}</li>
            ))}
          </ul>
        </>
      ) : null}
      {line.cambios.length ? (
        <>
          <span className="revisionLabel">Cambios de gusto</span>
          <ul className="lineaList">
            {line.cambios.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </>
      ) : null}
      {favor.length || contra.length ? (
        <div className="oficioColumns">
          <div>
            <span className="revisionLabel">Fichas que pesan más contigo</span>
            <ul className="lineaList">
              {favor.map((item) => (
                <li key={item.id}>
                  <strong>{item.nombre}</strong> <span className="note">— {item.motivo}</span>
                </li>
              ))}
              {!favor.length ? <li className="note">Ninguna todavía.</li> : null}
            </ul>
          </div>
          <div>
            <span className="revisionLabel">Fichas que pesan menos contigo</span>
            <ul className="lineaList">
              {contra.map((item) => (
                <li key={item.id}>
                  <strong>{item.nombre}</strong> <span className="note">— {item.motivo}</span>
                </li>
              ))}
              {!contra.length ? <li className="note">Ninguna todavía.</li> : null}
            </ul>
          </div>
        </div>
      ) : null}
    </section>
  );
}
