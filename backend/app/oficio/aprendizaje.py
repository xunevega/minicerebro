"""Capa 3: lo que Editados aprende de las decisiones de cada autor.

Dos fuentes, siempre del propio perfil:
- Propuestas de Escribir aceptadas o descartadas, con las fichas que las produjeron
  (y, si se sabe, cuáles se aplicaron de verdad). Miden qué fichas funcionan contigo.
- Elecciones de «Revisar por bloques»: qué alternativa eliges, cuándo mantienes tu
  texto, qué replanteamientos del loco Iván aceptas y en qué trampas caes. Forman tu
  línea editorial, y se compara lo reciente con lo anterior para ver si cambias.

Se usa para elegir fichas (pesos), para orientar al modelo (la línea, en palabras)
y para decidir cuántos replanteamientos ofrecer en Revisar. Nada de esto cambia las
fichas: eso solo ocurre con propuestas que el autor aprueba.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AuditEventRecord

EVENTOS = 600
MIN_RESULTADOS_FICHA = 3
MIN_ELECCIONES = 5
MIN_SONDAS = 3
PESO_MAX = 2.5
PESO_LINEA = 1.5
PESO_TRAMPA = 2.0
UMBRAL_MOVIMIENTO = 0.4
UMBRAL_CAMBIO = 0.3
VENTANA_RECIENTE = 10
PESO_FICHA_NO_APLICADA = 0.3

# Qué hace la alternativa elegida, según su «approach»; y qué fichas lo trabajan.
MOVIMIENTOS: dict[str, tuple[str, tuple[str, ...], tuple[str, ...]]] = {
    "concision": (
        "versiones más breves, que recortan y condensan",
        ("recort", "reduc", "condens", "sintetiz", "acort", "elimin", "quita", "una sola frase", "aligera"),
        ("redundancia-real", "cortar-el-principio"),
    ),
    "orden": (
        "versiones que reordenan las ideas",
        ("ordena", "reorden", "invierte", "empieza por", "abre con", "antepone", "mueve", "orden"),
        ("claridad-y-orden", "parrafo-y-progresion"),
    ),
    "concrecion": (
        "versiones que concretan con un ejemplo, un caso o una escena",
        ("ejemplo", "caso", "escena", "concret", "imagen"),
        ("ejemplo-concreto", "imagen-sensorial"),
    ),
    "fuerza": (
        "versiones que dan fuerza a la idea principal",
        ("rotund", "tesis", "contundent", "remata", "enfatiz", "destaca", "fuerza"),
        ("arranque-y-cierre",),
    ),
    "contraste": (
        "versiones que plantean la idea como pregunta o contraste",
        ("pregunta", "contraste", "oposici", "antítesis", "antitesis"),
        ("antitesis", "pregunta-retorica"),
    ),
    "voz": (
        "versiones que cambian el punto de vista o la voz",
        ("punto de vista", "voz", "primera persona", "narrador"),
        ("punto-de-vista", "voz-del-autor"),
    ),
}

TRAMPAS: dict[str, tuple[str, tuple[str, ...]]] = {
    "norma": ("errores de norma", ("dequeismo", "concordancia-sujeto-coordinado", "regimen-preposicional")),
    "sentido": ("cambios de sentido", ("matices-protegidos", "tiempo-ideas-atribuidas")),
    "orden": ("un orden peor de las ideas", ("claridad-y-orden", "conectores-logicos")),
    "topico": ("tópicos que suenan bien y no dicen nada", ("topicos-y-frases-hechas",)),
}

DIAGNOSTICOS = {
    "confuso": "confuso",
    "pesado": "pesado",
    "falta_fuerza": "le falta fuerza",
    "idea_suelta": "idea suelta",
    "no_cuadra": "no cuadra",
    "orden": "orden",
    "redundante": "redundante",
}


@dataclass
class Linea:
    elecciones: int = 0
    aceptadas: int = 0
    descartadas: int = 0
    tendencias: list[dict] = field(default_factory=list)
    cambios: list[str] = field(default_factory=list)
    fichas: dict[str, dict] = field(default_factory=dict)
    apertura: float | None = None

    def pesos(self) -> dict[str, tuple[float, str]]:
        return {ficha_id: (item["peso"], item["motivo"]) for ficha_id, item in self.fichas.items()}

    def as_dict(self) -> dict:
        return {
            "elecciones": self.elecciones,
            "propuestas": {"aceptadas": self.aceptadas, "descartadas": self.descartadas},
            "tendencias": self.tendencias,
            "cambios": self.cambios,
            "fichas": [{"id": ficha_id, **item} for ficha_id, item in sorted(self.fichas.items())],
            "apertura_replanteamiento": self.apertura,
        }


def _events(session: Session, profile_id: str, types: list[str]) -> list[AuditEventRecord]:
    rows = session.scalars(
        select(AuditEventRecord)
        .where(AuditEventRecord.event_type.in_(types))
        .where(AuditEventRecord.entity_type == "profile")
        .where(AuditEventRecord.entity_id == profile_id)
        .order_by(AuditEventRecord.id.desc())
        .limit(EVENTOS)
    ).all()
    return list(reversed(rows))


def _movement(approach: str) -> str | None:
    text = approach.lower()
    for key, (_label, keywords, _fichas) in MOVIMIENTOS.items():
        if any(keyword in text for keyword in keywords):
            return key
    return None


def _shares(choices: list[dict]) -> tuple[Counter, int]:
    moves = Counter()
    changed = 0
    for choice in choices:
        if choice.get("chosen") == "mantener" or (choice.get("probe") and choice.get("probe_kind") == "trampa"):
            continue
        changed += 1
        move = _movement(str(choice.get("approach", "")))
        if move:
            moves[move] += 1
    return moves, changed


def _add_ficha(linea: Linea, ficha_id: str, peso: float, motivo: str) -> None:
    item = linea.fichas.setdefault(ficha_id, {"peso": 0.0, "motivo": motivo, "aceptadas": 0, "descartadas": 0})
    item["peso"] = round(max(-PESO_MAX - PESO_TRAMPA, min(PESO_MAX + PESO_TRAMPA, item["peso"] + peso)), 2)
    if motivo not in item["motivo"]:
        item["motivo"] = f"{item['motivo']}; {motivo}"


def build_line(session: Session, profile_id: str | None) -> Linea:
    linea = Linea()
    if not profile_id:
        return linea
    events = _events(session, profile_id, ["generation.outcome", "review.choices.recorded"])

    # 1. Propuestas de Escribir: qué fichas acompañan lo que aceptas y lo que descartas.
    counts: dict[str, list[float]] = {}
    raw_counts: Counter = Counter()
    for event in events:
        if event.event_type != "generation.outcome":
            continue
        payload = event.payload or {}
        decision = payload.get("decision")
        if decision == "accepted":
            linea.aceptadas += 1
        elif decision == "discarded":
            linea.descartadas += 1
        else:
            continue
        no_aplicadas = set(payload.get("no_aplicadas") or [])
        for ficha_id in payload.get("fichas", []):
            weight = PESO_FICHA_NO_APLICADA if ficha_id in no_aplicadas else 1.0
            pair = counts.setdefault(ficha_id, [0.0, 0.0])
            pair[0 if decision == "accepted" else 1] += weight
            raw_counts[ficha_id] += 1
    for ficha_id, (accepted, discarded) in counts.items():
        if raw_counts[ficha_id] < MIN_RESULTADOS_FICHA:
            continue
        peso = (accepted - discarded) / (accepted + discarded + 2) * PESO_MAX
        if abs(peso) < 0.3:
            continue
        motivo = "funciona contigo" if peso > 0 else "suele acabar en propuestas que descartas"
        _add_ficha(linea, ficha_id, peso, motivo)
        linea.fichas[ficha_id]["aceptadas"] = round(accepted, 1)
        linea.fichas[ficha_id]["descartadas"] = round(discarded, 1)

    # 2. Revisar por bloques: elecciones, replanteamientos y trampas.
    choices: list[dict] = []
    for event in events:
        if event.event_type == "review.choices.recorded":
            choices.extend(item for item in (event.payload or {}).get("choices", []) if isinstance(item, dict))
    # Deshacer tras la revelación llega como una elección repetida del mismo bloque:
    # no cuenta como elección nueva, solo corrige la anterior.
    corrections = [choice for choice in choices if choice.get("kept_after_reveal") is False]
    choices = [choice for choice in choices if choice.get("kept_after_reveal") is not False]
    linea.elecciones = len(choices)
    if not choices:
        return linea

    moves, changed = _shares(choices)
    if changed >= MIN_ELECCIONES:
        for key, count in moves.most_common():
            share = count / changed
            if share < UMBRAL_MOVIMIENTO:
                break
            label, _keywords, fichas = MOVIMIENTOS[key]
            linea.tendencias.append({
                "clave": f"movimiento:{key}",
                "texto": f"Cuando cambias un bloque, eliges sobre todo {label} ({count} de {changed}).",
                "evidencia": count,
            })
            for ficha_id in fichas:
                _add_ficha(linea, ficha_id, PESO_LINEA, f"tu línea editorial: {label}")

    by_diagnosis: dict[str, Counter] = {}
    for choice in choices:
        for kind in choice.get("diagnosis_kinds", []):
            by_diagnosis.setdefault(kind, Counter())["mantener" if choice.get("chosen") == "mantener" else "cambio"] += 1
    for kind, counter in sorted(by_diagnosis.items()):
        total = sum(counter.values())
        if kind not in DIAGNOSTICOS or total < MIN_ELECCIONES:
            continue
        kept = counter["mantener"] / total
        if kept >= 0.6:
            linea.tendencias.append({
                "clave": f"mantiene:{kind}",
                "texto": (
                    f"Cuando un bloque está «{DIAGNOSTICOS[kind]}», sueles mantener tu versión "
                    f"({counter['mantener']} de {total})."
                ),
                "guia": f"Si un bloque está «{DIAGNOSTICOS[kind]}», propón cambios mínimos.",
                "evidencia": total,
            })
        elif kept <= 0.2:
            linea.tendencias.append({
                "clave": f"cambia:{kind}",
                "texto": (
                    f"Cuando un bloque está «{DIAGNOSTICOS[kind]}», casi siempre aceptas cambiarlo "
                    f"({counter['cambio']} de {total})."
                ),
                "evidencia": total,
            })

    offered = accepted = 0
    traps_fallen: Counter = Counter()
    traps_seen: Counter = Counter()
    for choice in choices:
        kind = str(choice.get("probe_kind", ""))
        move = str(choice.get("probe_move", ""))
        if kind.endswith("replanteamiento"):
            offered += 1
            if choice.get("probe") and kind == "replanteamiento":
                accepted += 1
        if kind.endswith("trampa"):
            traps_seen[move or "otra"] += 1
            if choice.get("probe") and kind == "trampa":
                traps_fallen[move or "otra"] += 1
    accepted -= sum(1 for choice in corrections if choice.get("probe_kind") == "replanteamiento")
    accepted = max(0, accepted)
    if offered >= MIN_SONDAS:
        linea.apertura = round(accepted / offered, 2)
        guia = ""
        if linea.apertura >= 0.5:
            texto = f"Aceptas replanteamientos de fondo ({accepted} de {offered})."
            guia = "Acepta replanteamientos de fondo: se puede proponer otra estructura."
        elif linea.apertura <= 0.2:
            texto = f"Rara vez aceptas replanteamientos ({accepted} de {offered})."
            guia = "Rara vez acepta replanteamientos: mejora el bloque sin cambiar su planteamiento."
        else:
            texto = f"Aceptas algunos replanteamientos ({accepted} de {offered})."
        linea.tendencias.append({"clave": "replanteamientos", "texto": texto, "guia": guia, "evidencia": offered})
    for move, fallen in traps_fallen.items():
        seen = traps_seen[move]
        if fallen >= 2 or (seen >= MIN_SONDAS and fallen / seen >= 0.5):
            label, fichas = TRAMPAS.get(move, ("trampas de otro tipo", ()))
            linea.tendencias.append({
                "clave": f"trampa:{move}",
                "texto": f"Has elegido {fallen} de {seen} trampas con {label}: Editados lo vigila más en tus textos.",
                "guia": f"El autor tiende a no ver {label}: vigílalo especialmente y no los introduzcas.",
                "evidencia": seen,
            })
            for ficha_id in fichas:
                _add_ficha(linea, ficha_id, PESO_TRAMPA, f"caes en trampas con {label}")

    # 3. ¿Cambias de gusto? Lo reciente frente a lo anterior.
    if len(choices) >= 2 * VENTANA_RECIENTE:
        before_moves, before_changed = _shares(choices[:-VENTANA_RECIENTE])
        recent_moves, recent_changed = _shares(choices[-VENTANA_RECIENTE:])
        if before_changed >= MIN_ELECCIONES and recent_changed >= MIN_ELECCIONES:
            for key, (label, _keywords, _fichas) in MOVIMIENTOS.items():
                before = before_moves[key] / before_changed
                recent = recent_moves[key] / recent_changed
                if recent - before >= UMBRAL_CAMBIO:
                    linea.cambios.append(f"Últimamente eliges más {label} que antes.")
                elif before - recent >= UMBRAL_CAMBIO:
                    linea.cambios.append(f"Últimamente eliges menos {label} que antes.")
        before_keep = sum(1 for c in choices[:-VENTANA_RECIENTE] if c.get("chosen") == "mantener")
        recent_keep = sum(1 for c in choices[-VENTANA_RECIENTE:] if c.get("chosen") == "mantener")
        before_rate = before_keep / max(1, len(choices) - VENTANA_RECIENTE)
        recent_rate = recent_keep / VENTANA_RECIENTE
        if recent_rate - before_rate >= UMBRAL_CAMBIO:
            linea.cambios.append("Últimamente mantienes tu texto más a menudo que antes.")
        elif before_rate - recent_rate >= UMBRAL_CAMBIO:
            linea.cambios.append("Últimamente aceptas cambiar tus bloques más que antes.")
    return linea


def line_prompt(linea: Linea) -> str:
    """La línea editorial en palabras, para el modelo. Vacía si no hay evidencia."""
    lines = [item.get("guia") or item["texto"] for item in linea.tendencias] + linea.cambios
    if not lines:
        return ""
    return (
        "Línea editorial del autor, aprendida de sus decisiones (orienta cómo resolver; "
        "no sustituye a las fichas ni a la norma):\n" + "\n".join(f"- {line}" for line in lines)
    )
