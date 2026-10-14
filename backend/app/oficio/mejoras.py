"""Propuestas de mejora de fichas a partir del uso (docs/POLITICA_CONOCIMIENTO.md).

Editados no cambia ninguna ficha por su cuenta: detecta fichas con indicios de
fallar, redacta una versión revisada con el modelo, la valida igual que una edición
manual y la deja como propuesta pendiente para que el autor la acepte o la rechace.

Indicios que se miran:
- la ficha se ha descartado o marcado «con reparos» desde «Leer» o la Biblioteca;
- las propuestas de Escribir en las que intervino se descartan mucho más que se aceptan;
- su señal salta en la mayoría de los textos (demasiado amplia);
- nunca entra en ningún texto y no tiene señal ni métrica (no se activa);
- el modelo la recibe pero el problema sigue en la propuesta (no se entiende o no se aplica).
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta
from os import getenv
from threading import Lock
from time import monotonic

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AuditEventRecord, OficioPropuestaRecord, ProfileOficioFichaRecord
from app.oficio.catalog import Ficha
from app.oficio.store import active_fichas, add_proposal, validate_ficha

MAX_PROPUESTAS_POR_PASADA = 3
EVENTOS_RECIENTES = 600
DIAS_DE_ESPERA_TRAS_RECHAZO = 14
MIN_RESULTADOS = 4
UMBRAL_DESCARTE = 0.6
MIN_SELECCIONES = 40
UMBRAL_DEMASIADO_AMPLIA = 0.6
MIN_SELECCIONES_SIN_USO = 60
MIN_COMPROBACIONES = 5
UMBRAL_NO_APLICADA = 0.6
INTERVALO_SEGUNDO_PLANO = 600

_last_background_run = 0.0
_background_lock = Lock()


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def _last_decisions(session: Session) -> dict[str, datetime]:
    """Fecha de la última propuesta decidida por ficha: el uso anterior ya se tuvo en cuenta."""
    last: dict[str, datetime] = {}
    for record in session.scalars(select(OficioPropuestaRecord)).all():
        if record.decided_at:
            decided = _aware(record.decided_at)
            if record.ficha_id not in last or decided > last[record.ficha_id]:
                last[record.ficha_id] = decided
    return last


def gather_evidence(session: Session) -> dict[str, dict]:
    last = _last_decisions(session)
    epoch = datetime.min.replace(tzinfo=UTC)
    events = session.scalars(
        select(AuditEventRecord)
        .where(
            AuditEventRecord.event_type.in_(["oficio.fichas.selected", "generation.outcome", "oficio.fichas.checked"])
        )
        .order_by(AuditEventRecord.id.desc())
        .limit(EVENTOS_RECIENTES)
    ).all()
    selections = 0
    selected = Counter()
    by_signal = Counter()
    outcomes: dict[str, Counter] = defaultdict(Counter)
    applied: dict[str, Counter] = defaultdict(Counter)
    for event in events:
        payload = event.payload or {}
        if event.event_type == "oficio.fichas.selected":
            selections += 1
            for item in payload.get("fichas", []):
                selected[item.get("id")] += 1
                if "señal en el texto" in item.get("motivos", []):
                    by_signal[item.get("id")] += 1
        elif event.event_type == "oficio.fichas.checked":
            for item in payload.get("fichas", []):
                ficha_id = item.get("id")
                if _aware(event.created_at) > last.get(ficha_id, epoch):
                    applied[ficha_id][item.get("estado")] += 1
        else:
            decision = payload.get("decision")
            for ficha_id in payload.get("fichas", []):
                if _aware(event.created_at) > last.get(ficha_id, epoch):
                    outcomes[ficha_id][decision] += 1
    stances = defaultdict(list)
    for record in session.scalars(select(ProfileOficioFichaRecord)).all():
        if record.stance in {"dismissed", "changed"} and _aware(record.updated_at) > last.get(record.card_id, epoch):
            stances[record.card_id].append(
                {"postura": record.stance, "comentario": record.feedback, "fecha": record.updated_at.isoformat()}
            )
    return {
        "selecciones": selections,
        "seleccionada": dict(selected),
        "por_senal": dict(by_signal),
        "resultados": {key: dict(value) for key, value in outcomes.items()},
        "aplicacion": {key: dict(value) for key, value in applied.items()},
        "posturas": dict(stances),
    }


def _blocked(session: Session) -> set[str]:
    now = datetime.now(UTC)
    blocked = set()
    for record in session.scalars(select(OficioPropuestaRecord)).all():
        if record.estado == "pendiente":
            blocked.add(record.ficha_id)
        elif record.estado == "rechazada" and record.decided_at:
            decided = record.decided_at if record.decided_at.tzinfo else record.decided_at.replace(tzinfo=UTC)
            if now - decided < timedelta(days=DIAS_DE_ESPERA_TRAS_RECHAZO):
                blocked.add(record.ficha_id)
    return blocked


def find_candidates(session: Session, evidence: dict | None = None) -> list[dict]:
    evidence = evidence or gather_evidence(session)
    fichas = active_fichas(session)
    blocked = _blocked(session)
    candidates: list[dict] = []

    for ficha_id, items in evidence["posturas"].items():
        if ficha_id in fichas and ficha_id not in blocked:
            comments = "; ".join(item["comentario"] for item in items if item["comentario"])[:400]
            candidates.append({
                "ficha_id": ficha_id,
                "tipo": "revisar",
                "motivo": "La has descartado o marcado con reparos." + (f" Comentarios: {comments}" if comments else ""),
                "evidencia": {"posturas": items},
            })

    for ficha_id, counts in evidence["resultados"].items():
        total = counts.get("accepted", 0) + counts.get("discarded", 0)
        if ficha_id in fichas and ficha_id not in blocked and total >= MIN_RESULTADOS:
            ratio = counts.get("discarded", 0) / total
            if ratio >= UMBRAL_DESCARTE:
                candidates.append({
                    "ficha_id": ficha_id,
                    "tipo": "revisar",
                    "motivo": f"Las propuestas en las que intervino se descartaron {counts.get('discarded', 0)} de {total} veces.",
                    "evidencia": {"resultados": counts},
                })

    for ficha_id, counts in evidence.get("aplicacion", {}).items():
        total_checks = sum(counts.values())
        if ficha_id in fichas and ficha_id not in blocked and total_checks >= MIN_COMPROBACIONES:
            still = counts.get("sigue", 0)
            if still / total_checks >= UMBRAL_NO_APLICADA:
                candidates.append({
                    "ficha_id": ficha_id,
                    "tipo": "revisar",
                    "motivo": (
                        f"El modelo la recibió pero el problema siguió en la propuesta {still} de "
                        f"{total_checks} veces: la regla o el ejemplo quizá no son claros, o la señal "
                        "salta en casos que no son errores."
                    ),
                    "evidencia": {"aplicacion": counts},
                })

    total = evidence["selecciones"]
    if total >= MIN_SELECCIONES:
        for ficha_id, count in evidence["por_senal"].items():
            if ficha_id in fichas and ficha_id not in blocked and count / total >= UMBRAL_DEMASIADO_AMPLIA:
                candidates.append({
                    "ficha_id": ficha_id,
                    "tipo": "acotar_senal",
                    "motivo": f"Su señal saltó en {count} de {total} textos: probablemente es demasiado amplia.",
                    "evidencia": {"por_senal": count, "selecciones": total},
                })
    if total >= MIN_SELECCIONES_SIN_USO:
        for ficha in fichas.values():
            never = evidence["seleccionada"].get(ficha.id, 0) == 0
            no_trigger = not ficha.senales and not ficha.metricas
            if never and no_trigger and ficha.id not in blocked:
                candidates.append({
                    "ficha_id": ficha.id,
                    "tipo": "anadir_senal",
                    "motivo": f"No ha entrado en ninguno de los últimos {total} textos y no tiene señal ni métrica.",
                    "evidencia": {"selecciones": total},
                })

    unique: dict[str, dict] = {}
    for candidate in candidates:
        unique.setdefault(candidate["ficha_id"], candidate)
    return list(unique.values())


PROMPT = """Eres el editor responsable de las fichas de oficio de Editados, un asistente de
escritura en español. Te paso una ficha y el motivo por el que parece fallar. Devuelve
la ficha revisada como un único objeto JSON con exactamente los mismos campos.

Reglas de la política de conocimiento:
- La regla va en palabras propias, comprobable; «aplica» y «no_aplica» delimitan.
- Ejemplos propios (mal, bien, porque); nunca frases de obras reales.
- La fuente no se inventa: conserva la obra y el localizador salvo error evidente.
- Señales: expresiones regulares de Python. Tipo «error» = delata un fallo probable;
  tipo «vigilancia» = marca un pasaje que mirar. Toda señal de error debe saltar en el
  primer ejemplo «mal» y no en ningún ejemplo «bien».
- No cambies el «id». Cambia lo mínimo necesario para resolver el motivo.
- Si el motivo es que la ficha sobra o no tiene arreglo, devuelve la ficha igual y
  explica en el campo «nota_editor» por qué (es el único campo extra permitido).

Motivo: {motivo}
Evidencia: {evidencia}
{problemas}
Ficha actual:
{ficha}
"""


def _extract_json(text: str) -> dict | None:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def draft_revision(ficha: Ficha, motivo: str, evidencia: dict, problemas: list[str] | None = None) -> dict | None:
    """Pide al modelo una versión revisada de la ficha. Sin clave de OpenAI, no hace nada."""
    if not getenv("OPENAI_API_KEY"):
        return None
    from app.generation.service import _openai_client, _openai_timeout_seconds

    prompt = PROMPT.format(
        motivo=motivo,
        evidencia=json.dumps(evidencia, ensure_ascii=False)[:1500],
        problemas=(
            "La versión anterior que propusiste no pasó la validación: " + "; ".join(problemas)
            if problemas
            else ""
        ),
        ficha=json.dumps(ficha.model_dump(), ensure_ascii=False, indent=2),
    )
    response = _openai_client().responses.create(
        model=getenv("OPENAI_MODEL", "gpt-5-mini"),
        input=prompt,
        max_output_tokens=6000,
        reasoning={"effort": "low"},
        store=False,
        timeout=max(60.0, _openai_timeout_seconds()),
    )
    return _extract_json(getattr(response, "output_text", "") or "")


def run_improvements(session: Session, limit: int = MAX_PROPUESTAS_POR_PASADA, drafter=draft_revision) -> dict:
    """Busca fichas con indicios de fallar y deja propuestas validadas. No aplica nada."""
    candidates = find_candidates(session)
    fichas = active_fichas(session)
    created, skipped = [], []
    for candidate in candidates[:limit]:
        ficha = fichas[candidate["ficha_id"]]
        draft = drafter(ficha, candidate["motivo"], candidate["evidencia"])
        if draft is None:
            skipped.append({"ficha_id": ficha.id, "razon": "No se pudo redactar la propuesta (modelo no disponible)."})
            continue
        nota = str(draft.pop("nota_editor", "") or "").strip()
        draft["id"] = ficha.id
        _, problems = validate_ficha(session, draft, ficha.id)
        if problems:
            retry = drafter(ficha, candidate["motivo"], candidate["evidencia"], problems)
            if retry is None:
                skipped.append({"ficha_id": ficha.id, "razon": "; ".join(problems)})
                continue
            nota = str(retry.pop("nota_editor", "") or nota).strip()
            retry["id"] = ficha.id
            _, problems = validate_ficha(session, retry, ficha.id)
            draft = retry
        if problems:
            skipped.append({"ficha_id": ficha.id, "razon": "; ".join(problems)})
            continue
        if draft == ficha.model_dump() and not nota:
            skipped.append({"ficha_id": ficha.id, "razon": "El modelo no propuso cambios."})
            continue
        evidencia = dict(candidate["evidencia"])
        if nota:
            evidencia["nota_editor"] = nota
        record = add_proposal(session, ficha.id, candidate["tipo"], draft, candidate["motivo"], evidencia)
        created.append(record.id)
    session.commit()
    return {"candidatas": len(candidates), "creadas": len(created), "omitidas": skipped}


def run_in_background() -> None:
    """Pasada en segundo plano tras recibir uso nuevo; como mucho una cada diez minutos."""
    global _last_background_run
    with _background_lock:
        if monotonic() - _last_background_run < INTERVALO_SEGUNDO_PLANO:
            return
        _last_background_run = monotonic()
    from app.db.session import SessionLocal

    session = SessionLocal()
    try:
        run_improvements(session)
    except Exception:  # noqa: BLE001 - una pasada fallida no debe afectar al uso normal
        session.rollback()
    finally:
        session.close()
