"""Ficha del autor: quién es cada cuenta como escritor (docs/POLITICA_CONOCIMIENTO.md).

Cada cuenta (correo y contraseña) tiene un perfil, y cada perfil tiene una ficha. La
ficha reúne en un solo sitio lo que hoy estaba repartido:

- lo que el autor escribe de sí mismo: cómo escribe, qué le gusta, qué evita, notas;
- sus gustos de «Mi criterio» con sus propias palabras, aceptados y rechazados;
- sus posturas sobre fichas de oficio («Me sirve», «No va conmigo»);
- su línea editorial aprendida (app/oficio/aprendizaje.py);
- sus cuatro rasgos de estilo, en palabras y no en números.

La parte escrita por el autor se guarda con versiones. El resto se calcula al vuelo
a partir de sus datos, así que siempre está al día. La ficha compilada se envía al
modelo en Escribir, Revisar y el diagnóstico.
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models import PreferenceStatus
from app.db.models import FichaAutorRecord, FichaAutorVersionRecord, ProfileOficioFichaRecord
from app.oficio.aprendizaje import build_line

MAX_ITEMS = 40
MAX_GUSTOS = 30

NIVELES = (
    (700, "alta"),
    (550, "algo alta"),
    (451, "media"),
    (300, "algo baja"),
    (0, "baja"),
)

RASGOS = {
    "precision_lexica": "precisión léxica (la palabra exacta frente a la aproximada)",
    "sobriedad": "sobriedad (contención frente a adorno)",
    "dinamismo": "dinamismo (frases ágiles y directas frente a pausadas)",
    "densidad_argumental": "densidad argumental (cuánto razonamiento por párrafo)",
}

POSTURAS = {
    "liked": "le sirve",
    "kept": "le sirve",
    "dismissed": "no va con él",
    "changed": "la usa con reparos",
}


class FichaAutorInput(BaseModel):
    """Lo que el autor escribe de sí mismo."""

    presentacion: str = Field(default="", max_length=2000)
    me_gusta: list[str] = Field(default_factory=list)
    evito: list[str] = Field(default_factory=list)
    notas: str = Field(default="", max_length=3000)

    @field_validator("me_gusta", "evito")
    @classmethod
    def _clean_items(cls, items: list[str]) -> list[str]:
        cleaned = []
        for item in items:
            text = " ".join(str(item).split())
            if text and text not in cleaned:
                cleaned.append(text[:300])
        if len(cleaned) > MAX_ITEMS:
            raise ValueError(f"Como mucho {MAX_ITEMS} elementos por lista.")
        return cleaned


def _empty() -> dict:
    return FichaAutorInput().model_dump()


def get_editable(session: Session, profile_id: str) -> tuple[dict, int, str | None]:
    record = session.get(FichaAutorRecord, profile_id)
    if record is None:
        return _empty(), 0, None
    return {**_empty(), **record.data}, record.version, record.updated_at.isoformat()


def save_editable(session: Session, profile_id: str, data: FichaAutorInput) -> tuple[dict, int]:
    record = session.get(FichaAutorRecord, profile_id)
    now = datetime.now(UTC)
    payload = data.model_dump()
    if record is None:
        record = FichaAutorRecord(profile_id=profile_id, data=payload, version=1, updated_at=now)
        session.add(record)
    else:
        if record.data == payload:
            return payload, record.version
        record.data = payload
        record.version += 1
        record.updated_at = now
    session.add(FichaAutorVersionRecord(profile_id=profile_id, version=record.version, data=payload, created_at=now))
    session.commit()
    return payload, record.version


def versions(session: Session, profile_id: str) -> list[dict]:
    rows = session.scalars(
        select(FichaAutorVersionRecord)
        .where(FichaAutorVersionRecord.profile_id == profile_id)
        .order_by(FichaAutorVersionRecord.version.desc())
    ).all()
    return [{"version": row.version, "data": row.data, "created_at": row.created_at.isoformat()} for row in rows]


def restore(session: Session, profile_id: str, version: int) -> tuple[dict, int]:
    row = session.scalar(
        select(FichaAutorVersionRecord).where(
            FichaAutorVersionRecord.profile_id == profile_id, FichaAutorVersionRecord.version == version
        )
    )
    if row is None:
        raise KeyError(version)
    return save_editable(session, profile_id, FichaAutorInput(**row.data))


def _nivel(value: int) -> str:
    for threshold, label in NIVELES:
        if value >= threshold:
            return label
    return "baja"


def compile_ficha(repository, profile_id: str, context: str = "general", fichas: dict | None = None) -> dict:
    """La ficha completa: lo escrito por el autor más lo que se sabe por sus datos."""
    session = repository.session
    editable, version, updated_at = get_editable(session, profile_id)

    gustos_aceptados, gustos_rechazados = [], []
    for preference in repository.list_preferences(profile_id):
        if preference.evidence.context not in {context, "general"}:
            continue
        if preference.status == PreferenceStatus.accepted:
            gustos_aceptados.append(preference.text.strip())
        elif preference.status == PreferenceStatus.rejected:
            gustos_rechazados.append(preference.text.strip())

    posturas = []
    names = {ficha_id: ficha.nombre for ficha_id, ficha in (fichas or {}).items()}
    for record in session.scalars(
        select(ProfileOficioFichaRecord).where(ProfileOficioFichaRecord.profile_id == profile_id)
    ).all():
        if record.stance in POSTURAS:
            posturas.append({
                "id": record.card_id,
                "nombre": names.get(record.card_id, record.card_id),
                "postura": POSTURAS[record.stance],
            })

    rasgos = []
    try:
        variables = repository.get_context_variables(profile_id, context)
    except KeyError:
        variables = []
    for variable in variables:
        rasgos.append({
            "clave": variable.key,
            "texto": RASGOS.get(variable.key, variable.label),
            "nivel": _nivel(variable.effective_value),
            "seguridad": round(variable.confidence, 2),
            # Solo cuenta lo que sale de ti (gustos, valoraciones o ajustes), no el valor de partida.
            "propio": variable.evidence_count > 0 or variable.manual_adjustment != 0,
        })

    linea = build_line(session, profile_id)
    return {
        "version": version,
        "updated_at": updated_at,
        "editable": editable,
        "gustos_aceptados": gustos_aceptados[:MAX_GUSTOS],
        "gustos_rechazados": gustos_rechazados[:MAX_GUSTOS],
        "posturas": sorted(posturas, key=lambda item: item["nombre"]),
        "linea": [item["texto"] for item in linea.tendencias] + linea.cambios,
        "linea_guia": [item.get("guia") or item["texto"] for item in linea.tendencias] + linea.cambios,
        "rasgos": rasgos,
    }


def ficha_prompt(compiled: dict) -> str:
    """La ficha del autor en palabras, para el modelo. Vacía si no hay nada que decir."""
    editable = compiled["editable"]
    parts: list[str] = []
    if editable.get("presentacion"):
        parts.append(f"Cómo se describe: {editable['presentacion']}")
    if editable.get("me_gusta"):
        parts.append("Le gusta:\n" + "\n".join(f"- {item}" for item in editable["me_gusta"]))
    if editable.get("evito"):
        parts.append("Evita:\n" + "\n".join(f"- {item}" for item in editable["evito"]))
    if compiled["gustos_aceptados"]:
        parts.append("Gustos que ha confirmado, con sus palabras:\n" + "\n".join(f"- {item}" for item in compiled["gustos_aceptados"]))
    if compiled["gustos_rechazados"]:
        parts.append("Interpretaciones que ha rechazado (no las apliques):\n" + "\n".join(f"- {item}" for item in compiled["gustos_rechazados"]))
    if compiled["posturas"]:
        parts.append(
            "Fichas de oficio que ha valorado: "
            + "; ".join(f"«{item['nombre']}» {item['postura']}" for item in compiled["posturas"])
            + "."
        )
    if compiled["linea_guia"]:
        parts.append("Línea editorial aprendida de sus decisiones:\n" + "\n".join(f"- {item}" for item in compiled["linea_guia"]))
    seguros = [item for item in compiled["rasgos"] if item.get("propio") and item["nivel"] != "media"]
    if seguros:
        parts.append(
            "Rasgos de estilo: " + "; ".join(f"{item['texto']}: {item['nivel']}" for item in seguros) + "."
        )
    if editable.get("notas"):
        parts.append(f"Notas del autor: {editable['notas']}")
    if not parts:
        return ""
    return (
        "Ficha del autor (su criterio; manda sobre las preferencias generales, nunca sobre la norma "
        "ni sobre los matices protegidos):\n" + "\n\n".join(parts)
    )
