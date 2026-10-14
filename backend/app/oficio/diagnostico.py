"""Diagnóstico previo de fichas con el modelo (docs/POLITICA_CONOCIMIENTO.md).

Los patrones encuentran candidatas; el modelo, que lee el texto entero, decide:
- qué candidatas son de verdad un caso de su ficha (las demás se descartan);
- qué problemas hay en el texto que ningún patrón detecta, citando el fragmento.

El resultado se guarda en caché por texto, opciones, catálogo y modelo: el mismo
texto con las mismas opciones da siempre las mismas fichas. Sin modelo disponible,
Editados elige solo con patrones y lo dice.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import UTC, datetime
from os import getenv

from sqlalchemy.orm import Session

from app.db.models import OficioDiagnosticoRecord
from app.oficio.catalog import Ficha
from app.oficio.selection import (
    ACCION_EQUIVALENTE,
    Diagnosis,
    SelectedFicha,
    _allowed,
    _genre_matches,
    select_fichas,
)

VERSION_PROMPT = "1"
MAX_ANADIDAS = 5
MAX_TEXTO = 16000
MOTIVOS_DE_SENAL = {"señal en el texto", "pasaje que vigilar", "pasaje que proteger al reescribir"}

PROMPT = """Eres el editor jefe de Editados, un asistente de escritura en español.
Antes de editar, revisas el diagnóstico automático de un texto.

1. Candidatas: fichas que un patrón ha detectado en un fragmento. Para cada una, di si el
   fragmento es de verdad un caso de lo que la ficha corrige o vigila (true) o si el
   patrón ha saltado sin motivo (false). Mira el contexto de la frase, no solo la palabra.
2. Añadidas: mirando el índice, señala como mucho {max_anadidas} fichas cuyo problema
   aparece claramente en el texto aunque ningún patrón lo haya detectado. Cita el
   fragmento literal, copiado tal cual del texto. Solo fallos concretos y visibles; no
   añadas fichas generales «por si acaso» ni las que ya son candidatas.

Responde solo con JSON:
{{"candidatas": {{"<id>": true|false}}, "anadidas": [{{"id": "<id>", "fragmento": "<cita literal>"}}]}}

Acción: {accion}. Tipo de texto: {genero}. Dirección del autor: {direccion}
No marques como problema lo que el autor elige a propósito según su ficha:
{autor}

Candidatas:
{candidatas}

Índice de fichas (id: nombre: regla):
{indice}

Texto:
<<<
{texto}
>>>
"""


def _canon(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.lower())
    plain = "".join(char for char in normalized if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", plain).strip()


def _short_rule(ficha: Ficha) -> str:
    first = re.split(r"(?<=[.:;])\s", ficha.regla.strip(), maxsplit=1)[0]
    return first[:140]


def _index(fichas: dict[str, Ficha], action: str, genre: str, instruction: str) -> list[Ficha]:
    action = ACCION_EQUIVALENTE.get(action, action)
    result = []
    for ficha in fichas.values():
        if not _allowed(ficha, action):
            continue
        declared = _genre_matches(ficha, genre) or (instruction.strip() and _genre_matches(ficha, instruction))
        if ficha.generos and genre.strip() and not declared:
            continue
        result.append(ficha)
    return sorted(result, key=lambda ficha: (ficha.rama, ficha.id))


def _candidates(selected: list[SelectedFicha]) -> list[SelectedFicha]:
    return [item for item in selected if item.fragmentos and MOTIVOS_DE_SENAL & set(item.motivos)]


def _extract_json(text: str) -> dict | None:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _call_model(prompt: str) -> dict | None:
    """Llamada al modelo. Devuelve None si no hay clave o algo falla."""
    if not getenv("OPENAI_API_KEY"):
        return None
    from app.generation.service import _openai_client

    try:
        response = _openai_client().responses.create(
            model=getenv("OPENAI_MODEL", "gpt-5-mini"),
            input=prompt,
            max_output_tokens=3000,
            reasoning={"effort": "low"},
            store=False,
            timeout=float(getenv("OFICIO_DIAGNOSTICO_TIMEOUT", "25")),
        )
    except Exception:  # noqa: BLE001 - sin diagnóstico se sigue con los patrones
        return None
    return _extract_json(getattr(response, "output_text", "") or "")


def _clean(raw: dict, candidates: list[SelectedFicha], index_ids: set[str], text: str) -> dict:
    """Solo se acepta lo verificable: ids existentes y fragmentos que están en el texto."""
    candidate_ids = {item.ficha.id for item in candidates}
    verdicts = raw.get("candidatas") if isinstance(raw.get("candidatas"), dict) else {}
    descartadas = sorted(
        ficha_id for ficha_id, value in verdicts.items() if ficha_id in candidate_ids and value is False
    )
    canon_text = _canon(text)
    anadidas: dict[str, str] = {}
    for item in raw.get("anadidas") or []:
        if not isinstance(item, dict):
            continue
        ficha_id = str(item.get("id", ""))
        fragment = str(item.get("fragmento", "")).strip().strip("«»\"")
        if ficha_id not in index_ids or ficha_id in candidate_ids or ficha_id in anadidas:
            continue
        if len(fragment) < 3 or _canon(fragment) not in canon_text:
            continue
        anadidas[ficha_id] = fragment[:220]
        if len(anadidas) >= MAX_ANADIDAS:
            break
    return {"descartadas": descartadas, "anadidas": anadidas}


def _key(parts: dict) -> str:
    return hashlib.sha256(json.dumps(parts, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def diagnose(
    session: Session | None,
    text: str,
    action: str,
    *,
    intention: str = "comprension",
    genre: str = "",
    instruction: str = "",
    fichas: dict[str, Ficha],
    preferences: dict[str, str] | None = None,
    call_model=None,
    autor: str = "",
) -> tuple[Diagnosis | None, dict]:
    """Devuelve el diagnóstico (o None) y un resumen legible para «Ver detalles»."""
    call_model = call_model or _call_model
    pre = select_fichas(
        text, action, intention=intention, genre=genre, limit=60,
        preferences=preferences, instruction=instruction, fichas=fichas,
    )
    candidates = _candidates(pre)
    index = _index(fichas, action, genre, instruction)
    index_lines = [f"{ficha.id}: {ficha.nombre}: {_short_rule(ficha)}" for ficha in index]
    candidate_lines = [
        f"- {item.ficha.id} ({item.ficha.nombre}): " + " | ".join(f"«{fragment}»" for fragment in item.fragmentos)
        for item in candidates
    ] or ["(ninguna)"]
    texto = text[:MAX_TEXTO]
    key = _key({
        "v": VERSION_PROMPT,
        "modelo": getenv("OPENAI_MODEL", "gpt-5-mini"),
        "texto": texto,
        "accion": action,
        "genero": genre.strip(),
        "direccion": instruction.strip(),
        "candidatas": candidate_lines,
        "indice": index_lines,
        "autor": autor,
    })

    cached = session.get(OficioDiagnosticoRecord, key) if session is not None else None
    if cached is not None:
        result, estado = cached.resultado, "cache"
    else:
        raw = call_model(PROMPT.format(
            max_anadidas=MAX_ANADIDAS,
            accion=action,
            genero=genre.strip() or "sin declarar",
            direccion=instruction.strip() or "ninguna",
            autor=autor or "(sin ficha del autor)",
            candidatas="\n".join(candidate_lines),
            indice="\n".join(index_lines),
            texto=texto,
        ))
        if raw is None:
            return None, {"estado": "no_disponible", "descartadas": [], "anadidas": []}
        result, estado = _clean(raw, candidates, {ficha.id for ficha in index}, texto), "hecho"
        if session is not None:
            session.merge(OficioDiagnosticoRecord(clave=key, resultado=result, created_at=datetime.now(UTC)))
            session.commit()

    fragments = {item.ficha.id: item.fragmentos[0] for item in candidates}
    summary = {
        "estado": estado,
        "descartadas": [
            {"id": ficha_id, "nombre": fichas[ficha_id].nombre, "fragmento": fragments.get(ficha_id, "")}
            for ficha_id in result["descartadas"] if ficha_id in fichas
        ],
        "anadidas": [
            {"id": ficha_id, "nombre": fichas[ficha_id].nombre, "fragmento": fragment}
            for ficha_id, fragment in result["anadidas"].items() if ficha_id in fichas
        ],
    }
    return Diagnosis(descartadas=set(result["descartadas"]), anadidas=dict(result["anadidas"])), summary


def select_with_diagnosis(
    session: Session | None,
    text: str,
    action: str,
    *,
    intention: str = "comprension",
    genre: str = "",
    instruction: str = "",
    preferences: dict[str, str] | None = None,
    fichas: dict[str, Ficha],
    limit: int | None = None,
    call_model=None,
    learned: dict[str, tuple[float, str]] | None = None,
    autor: str = "",
) -> tuple[list[SelectedFicha], dict]:
    diagnosis, summary = diagnose(
        session, text, action, intention=intention, genre=genre, instruction=instruction,
        fichas=fichas, preferences=preferences, call_model=call_model, autor=autor,
    )
    kwargs = {"limit": limit} if limit is not None else {}
    selected = select_fichas(
        text, action, intention=intention, genre=genre, preferences=preferences,
        instruction=instruction, fichas=fichas, diagnosis=diagnosis, learned=learned, **kwargs,
    )
    return selected, summary
