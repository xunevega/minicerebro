"""Comprobación de si el modelo aplicó las fichas (docs/POLITICA_CONOCIMIENTO.md).

Tras generar, se vuelven a pasar sobre la salida las señales de error y las métricas
de cada ficha que detectó un problema en el original, y se mira si el fragmento que
señaló el diagnóstico sigue igual. Solo se comprueba lo que es medible; el resto se
cuenta como «sin comprobación automática», no como aplicado.
"""

from __future__ import annotations

from app.oficio.selection import METRIC_FUNCTIONS, SelectedFicha, _canon, _signal_hits


def _problem_count(item: SelectedFicha, text: str) -> int:
    hits = _signal_hits(item.ficha, text, "error")
    for metric in item.ficha.metricas:
        hits.extend(METRIC_FUNCTIONS[metric](text))
    return len(hits)


def check_application(selected: list[SelectedFicha], original: str, output: str) -> dict:
    checks: list[dict] = []
    unchecked = 0
    canon_output = _canon(output)
    for item in selected:
        ficha = item.ficha
        if not item.problema:
            unchecked += 1
            continue
        before = _problem_count(item, original)
        if before:
            after = _problem_count(item, output)
            if after == 0:
                estado, detalle = "aplicada", "El problema ya no aparece en la propuesta."
            elif after < before:
                estado, detalle = "en_parte", f"Quedan {after} de {before} casos."
            else:
                estado, detalle = "sigue", "El problema sigue en la propuesta."
        elif item.fragmentos:
            # Problema señalado por el diagnóstico, sin patrón que medir: se mira el fragmento.
            if _canon(item.fragmentos[0]) in canon_output:
                estado, detalle = "sigue", f"El fragmento sigue igual: «{item.fragmentos[0][:90]}»."
            else:
                estado, detalle = "aplicada", "El fragmento señalado ha cambiado."
        else:
            unchecked += 1
            continue
        checks.append({"id": ficha.id, "nombre": ficha.nombre, "estado": estado, "detalle": detalle})
    return {"comprobadas": checks, "sin_comprobacion": unchecked}
