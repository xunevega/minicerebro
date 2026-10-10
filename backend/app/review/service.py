"""Modo Revisar: lectura de editor por bloques.

No corrige palabras. Lee el fragmento entero, opina sobre el planteamiento y,
para cada bloque (parrafo) con problemas, da un diagnostico con su porque y tres
reescrituras del bloque entero. De vez en cuando una de ellas es un "loco Ivan":
no arregla el bloque, lo replantea (otro orden, otra forma, otra estructura).
"""

from __future__ import annotations

import json
import random
import re
from os import getenv

from app.core.models import (
    BlockReviewInput,
    BlockReviewResult,
    ReviewAlternative,
    ReviewBlock,
    ReviewDiagnosis,
)
from app.generation import service as generation

MAX_REVIEW_WORDS = 1500
PROBE_PROBABILITY = 0.3
TRAP_SHARE = 0.35
PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n")

DIAGNOSIS_KINDS = (
    "confuso",
    "pesado",
    "falta_fuerza",
    "idea_suelta",
    "no_cuadra",
    "orden",
    "redundante",
    "otro",
)

TRAP_MOVES = (
    "introducir un error de norma verosimil (dequeismo, concordancia, regimen o puntuacion)",
    "cambiar sutilmente el sentido de una afirmacion del autor",
    "empeorar el orden logico de las ideas aunque suene bien",
    "anadir un tópico o frase hecha que suene profunda y no diga nada",
)

PROBE_MOVES = (
    "invertir el orden: empezar por la conclusion o por el final",
    "convertir la explicacion en una escena, un caso o un ejemplo concreto",
    "partir el bloque en dos con funciones distintas",
    "reducir el bloque a una sola frase rotunda",
    "plantear la idea como pregunta o como contraste",
    "cambiar el punto de vista o la voz desde la que se cuenta",
)


class ReviewTooLong(ValueError):
    pass


def split_blocks(text: str) -> list[str]:
    return [block.strip() for block in PARAGRAPH_SPLIT_RE.split(text.strip()) if block.strip()]


def choose_probes(block_count: int, rng: random.Random) -> dict[int, tuple[str, str]]:
    """Bloques cuya alternativa C sera un loco Ivan: (tipo, movimiento).

    Tipo "replanteamiento": alternativa valida pero distinta. Tipo "trampa":
    alternativa incorrecta a proposito, que siempre se revela despues.
    """

    def pick() -> tuple[str, str]:
        if rng.random() < TRAP_SHARE:
            return ("trampa", rng.choice(TRAP_MOVES))
        return ("replanteamiento", rng.choice(PROBE_MOVES))

    probes = {index: pick() for index in range(block_count) if rng.random() < PROBE_PROBABILITY}
    if not probes and block_count >= 3:
        probes[rng.randrange(block_count)] = pick()
    return probes


def _intensity_guidance(intensity: int) -> str:
    if intensity >= 750:
        return (
            "Intensidad alta: las alternativas pueden reescribir el bloque por completo "
            "y cambiar su arquitectura si gana fuerza."
        )
    if intensity >= 400:
        return (
            "Intensidad media: las alternativas deben notarse; reorganiza y reformula el "
            "bloque, no lo retoques palabra a palabra."
        )
    return (
        "Intensidad baja: las alternativas resuelven el problema con la menor "
        "intervencion posible, pero siempre a nivel de frase o bloque, no de palabra suelta."
    )


def _schema() -> dict:
    alternative = {
        "type": "object",
        "additionalProperties": False,
        "required": ["label", "approach", "text", "probe_reveal"],
        "properties": {
            "label": {"type": "string", "enum": ["A", "B", "C"]},
            "approach": {"type": "string"},
            "text": {"type": "string"},
            "probe_reveal": {"type": "string"},
        },
    }
    diagnosis = {
        "type": "object",
        "additionalProperties": False,
        "required": ["kind", "explanation"],
        "properties": {
            "kind": {"type": "string", "enum": list(DIAGNOSIS_KINDS)},
            "explanation": {"type": "string"},
        },
    }
    block = {
        "type": "object",
        "additionalProperties": False,
        "required": ["index", "has_problem", "diagnoses", "alternatives"],
        "properties": {
            "index": {"type": "integer"},
            "has_problem": {"type": "boolean"},
            "diagnoses": {"type": "array", "items": diagnosis},
            "alternatives": {"type": "array", "items": alternative},
        },
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["overview", "blocks"],
        "properties": {
            "overview": {"type": "string"},
            "blocks": {"type": "array", "items": block},
        },
    }


def _prompt(
    payload: BlockReviewInput,
    blocks: list[str],
    probes: dict[int, tuple[str, str]],
    notes: list[tuple[str, str]],
) -> str:
    numbered = "\n\n".join(f"[{index}]\n{block}" for index, block in enumerate(blocks))
    lines = []
    for index, (kind, move) in sorted(probes.items()):
        if kind == "trampa":
            lines.append(
                f"- Bloque {index}: la alternativa C es una TRAMPA: {move}. Debe parecer "
                "una propuesta normal y verosimil; su approach no delata la trampa. En "
                "probe_reveal explica con precision que esta mal y por que."
            )
        else:
            lines.append(
                f"- Bloque {index}: la alternativa C es un replanteamiento: {move}. No "
                "arregla el bloque tal como esta: propone otra manera de plantearlo. En "
                "probe_reveal explica que planteamiento distinto proponia."
            )
    probe_lines = "\n".join(lines) if lines else "- Ninguno en esta pasada."
    protected = ", ".join(payload.protected_terms) or "ninguno"
    instruction = " ".join(payload.user_instruction.split()) or "ninguna"
    notes_block = generation._knowledge_notes_contract(notes)
    return f"""
Eres el editor de Editados. Lees como un editor de oficio, no como un corrector:
no vas a la palabra, vas al bloque, a la idea y al planteamiento.

Tipo de texto declarado por el autor: {payload.genre.strip() or "no declarado"}
Direccion del autor para esta revision: {instruction}
Terminos protegidos (no se tocan): {protected}
{_intensity_guidance(payload.intensity)}

Tarea:
1. overview: un parrafo sobre el planteamiento del fragmento. Cual es la tesis o
   la historia, si las ideas siguen un orden, que no cuadra con que, que falta o
   sobra. Concreto y referido a los bloques por numero.
2. Para cada bloque [n], en el mismo orden:
   - has_problem: false si el bloque funciona; entonces diagnoses y alternatives
     van vacios. No inventes problemas en un bloque que funciona.
   - diagnoses: uno o dos, con kind y una explicacion concreta de lo que pasa en
     ESE bloque ("las tres frases dicen lo mismo", "la idea clave queda al final").
       confuso: no se entiende o mezcla ideas. pesado: se hace largo o repetitivo.
       falta_fuerza: el punto importante queda flojo o enterrado.
       idea_suelta: aparece una idea y no se desarrolla ni conecta.
       no_cuadra: contradice o no encaja con otro bloque. orden: las ideas van
       en mal orden. redundante: repite lo ya dicho en otro bloque. otro.
   - alternatives: exactamente tres (A, B, C) si has_problem es true. Cada una es
     el bloque ENTERO reescrito, no frases sueltas. approach dice en pocas
     palabras que hace esa version ("ordena la idea y la abre con la tesis",
     "lo convierte en un ejemplo"). Las tres deben ser realmente distintas entre
     si, no variaciones de palabras.

Reglas:
- Conserva lo que el autor dice: hechos, tesis, nombres, citas. Recorta solo
  redundancias. Puedes cambiar orden, forma, recursos y lexico.
- No introduzcas errores de norma.
- Respeta la voz del autor salvo en la alternativa de replanteamiento.

Sondas obligatorias (loco Ivan). Solo en los bloques indicados y solo si el
bloque tiene problema; en cualquier otra alternativa, probe_reveal va vacio:
{probe_lines}

{notes_block}

Texto, dividido en bloques numerados:

{numbered}
""".strip()


def review_blocks(
    payload: BlockReviewInput,
    knowledge_notes: list[tuple[str, str]] | None = None,
    rng: random.Random | None = None,
) -> BlockReviewResult:
    blocks = split_blocks(payload.text)
    word_count = len(payload.text.split())
    if word_count > MAX_REVIEW_WORDS:
        raise ReviewTooLong(
            f"Revisar trabaja con fragmentos de hasta {MAX_REVIEW_WORDS} palabras "
            f"(este tiene {word_count}). Divide el texto y revisalo por partes."
        )
    if not getenv("OPENAI_API_KEY"):
        raise generation.GenerationUnavailable(
            "Revisar necesita el modelo de escritura y no hay clave configurada."
        )

    probes = choose_probes(len(blocks), rng or random.Random())
    model = getenv("OPENAI_MODEL", "gpt-5-mini")
    effort = generation._reasoning_effort()
    max_tokens = min(32000, round(word_count * 6) + 1500) + generation.REASONING_TOKEN_BUDGET[effort]
    try:
        response = generation._openai_client().responses.create(
            model=model,
            input=_prompt(payload, blocks, probes, knowledge_notes or []),
            max_output_tokens=max_tokens,
            reasoning={"effort": effort},
            text={
                "format": {
                    "type": "json_schema",
                    "name": "revision_por_bloques",
                    "schema": _schema(),
                    "strict": True,
                }
            },
            store=False,
            timeout=max(generation._openai_timeout_seconds(), 120.0),
        )
    except Exception as exc:
        raise generation.GenerationUnavailable(
            "No se ha podido contactar con el modelo de escritura. Tu texto no se ha modificado."
        ) from exc

    if getattr(response, "status", None) == "incomplete":
        raise generation.GenerationUnavailable(
            "La revision no se completo (fragmento demasiado largo). Prueba con un trozo mas corto."
        )
    raw = (getattr(response, "output_text", "") or "").strip()
    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise generation.GenerationUnavailable(
            "El modelo devolvio una revision ilegible. Tu texto no se ha modificado."
        ) from exc

    by_index = {item["index"]: item for item in data.get("blocks", []) if isinstance(item, dict)}
    review_blocks_out: list[ReviewBlock] = []
    for index, original in enumerate(blocks):
        item = by_index.get(index, {})
        alternatives = [
            ReviewAlternative(
                label=alt["label"],
                approach=alt["approach"],
                text=alt["text"].strip(),
                probe=alt["label"] == "C" and index in probes,
                probe_kind=probes[index][0] if alt["label"] == "C" and index in probes else "",
                probe_reveal=(
                    alt.get("probe_reveal", "").strip()
                    if alt["label"] == "C" and index in probes
                    else ""
                ),
            )
            for alt in item.get("alternatives", [])
            if alt.get("text", "").strip()
        ]
        has_problem = bool(item.get("has_problem")) and bool(alternatives)
        review_blocks_out.append(
            ReviewBlock(
                index=index,
                original=original,
                has_problem=has_problem,
                diagnoses=[
                    ReviewDiagnosis(kind=diag["kind"], explanation=diag["explanation"])
                    for diag in item.get("diagnoses", [])
                ]
                if has_problem
                else [],
                alternatives=alternatives if has_problem else [],
            )
        )

    return BlockReviewResult(
        overview=str(data.get("overview", "")).strip(),
        blocks=review_blocks_out,
        word_count=word_count,
        provider="openai",
        model=model,
        probe_blocks=sorted(probes),
    )
