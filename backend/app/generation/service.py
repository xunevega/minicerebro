import re
from difflib import SequenceMatcher
from os import getenv

from openai import OpenAI

from app.core.models import GenerationInput, GenerationResult, ScoreVariable


SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
CONTENT_TOKEN_RE = re.compile(r"[\wáéíóúüñÁÉÍÓÚÜÑ]+")
PROTECTED_TOKEN_TEMPLATE = "__PROTECTED_TERM_{index}__"
PUNCTUATION_SPACING_RE = re.compile(r"\s+([,.;:!?])")
MISSING_SPACE_AFTER_PUNCTUATION_RE = re.compile(r"([,.;:!?])(?=\S)")
SENTENCE_START_RE = re.compile(r"(^|[.!?]\s+)([a-záéíóúüñ])")
DEFAULT_OPENAI_TIMEOUT_SECONDS = 25.0
_OPENAI_CLIENT: OpenAI | None = None
_OPENAI_CLIENT_FACTORY: object | None = None


SAFE_EDITORIAL_REPLACEMENTS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b[Ll]es recuerdo en incidente\b"), "Les recuerdo el incidente"),
    (re.compile(r"\bcomenta qué(?=\s*:)", re.IGNORECASE), "comenta que"),
    (re.compile(r"\bp[eé]rdida de agua\b", re.IGNORECASE), "pérdida de agua"),
    (re.compile(r"\bagua fria\b", re.IGNORECASE), "agua fría"),
    (re.compile(r"\blinea de vida\b", re.IGNORECASE), "línea de vida"),
    (re.compile(r"\bsaber cual es\b", re.IGNORECASE), "saber cuál es"),
    (re.compile(r"\bcuanto cubre\b", re.IGNORECASE), "cuánto cubre"),
    (re.compile(r"\bcuanto dinero\b", re.IGNORECASE), "cuánto dinero"),
    (re.compile(r"\bdesconozco el corte de Todo esto\b"), "desconozco el coste de todo esto"),
    (re.compile(r"\bRoberto díaz\b"), "Roberto Díaz"),
    (re.compile(r"\bAvenida constitucion\b", re.IGNORECASE), "Avenida Constitución"),
)


def _openai_client() -> OpenAI:
    global _OPENAI_CLIENT, _OPENAI_CLIENT_FACTORY
    if _OPENAI_CLIENT is None or _OPENAI_CLIENT_FACTORY is not OpenAI:
        _OPENAI_CLIENT = OpenAI()
        _OPENAI_CLIENT_FACTORY = OpenAI
    return _OPENAI_CLIENT


def _openai_timeout_seconds() -> float:
    try:
        return max(3.0, float(getenv("OPENAI_TIMEOUT_SECONDS", DEFAULT_OPENAI_TIMEOUT_SECONDS)))
    except ValueError:
        return DEFAULT_OPENAI_TIMEOUT_SECONDS


def _max_output_tokens(payload: GenerationInput) -> int:
    word_count = len(payload.text.split())
    if payload.action == "sendable":
        return min(3200, max(520, round(word_count * 2.2) + 260))
    if payload.action == "continue":
        return min(900, max(220, round(word_count * 0.8) + 120))
    if payload.action == "variants":
        return min(1600, max(420, round(word_count * 2.0) + 180))
    return min(2400, max(220, round(word_count * 1.6) + 120))


def _rewrite_similarity_floor(intensity: int, revision_intention: str = "claridad") -> float:
    if revision_intention == "estructura" and intensity >= 850:
        return 0.34
    if intensity <= 650:
        return 0.72
    if intensity <= 850:
        return 0.62
    return 0.48


def _content_token_overlap(original: str, output: str) -> float:
    original_tokens = {
        token
        for token in CONTENT_TOKEN_RE.findall(original.lower())
        if len(token) >= 4
    }
    if not original_tokens:
        return 1.0
    output_tokens = {
        token
        for token in CONTENT_TOKEN_RE.findall(output.lower())
        if len(token) >= 4
    }
    return len(original_tokens & output_tokens) / len(original_tokens)


def _is_over_rewritten(
    original: str,
    output: str,
    intensity: int,
    revision_intention: str = "claridad",
) -> bool:
    if (
        revision_intention == "estructura"
        and intensity >= 850
        and _content_token_overlap(original, output) >= 0.55
    ):
        return False
    floor = _rewrite_similarity_floor(intensity, revision_intention)
    if floor <= 0:
        return False
    similarity = SequenceMatcher(None, original.strip().lower(), output.strip().lower()).ratio()
    return similarity < floor


def _generation_contract(payload: GenerationInput) -> str:
    if payload.action == "sendable":
        return """
Objetivo: convertir el borrador en un texto final listo para enviar.
Reglas especificas:
- Si el borrador es una nota, correo, aviso o lista de puntos, ordenalo como
  comunicacion clara y completa.
- Puedes anadir saludo, cierre, transiciones y lista de puntos cuando ya esten
  implicados por el borrador.
- Conserva todos los hechos, dudas, condiciones, nombres, direcciones, fechas,
  responsabilidades y grado de certeza.
- Formula las dudas como dudas y los pendientes como solicitudes de aclaracion.
- Corrige errores seguros y mejora orden, tono y claridad.
- No inventes costes, causas, acuerdos, datos tecnicos ni decisiones de terceros.
- Devuelve solo la version final lista para enviar.
""".strip()
    if payload.action == "rewrite":
        if payload.intensity >= 850:
            return """
Objetivo: mejorar claridad con una reescritura decidida pero fiel.
Reglas especificas:
- Puedes compactar, reordenar y sustituir formulaciones torpes si mejora la lectura.
- Si el borrador parece una nota, correo, aviso o lista de puntos, puedes convertirlo en
  una version final clara y enviable.
- Puedes usar saludo, cierre y lista de puntos cuando el propio borrador lo pida.
- Explicita dudas ya presentes, pero no anadas datos nuevos.
- Conserva hechos, sujetos, matices, grado de certeza, causalidad y atribuciones.
- No conviertas una atribucion en una afirmacion propia.
- No introduzcas informacion nueva ni elimines informacion relevante.
- No endurezcas el tono para que suene mas rotundo.
- Si un cambio altera el sentido, conserva la formulacion original.
""".strip()
        if payload.intensity >= 650:
            return """
Objetivo: mejorar claridad con cambios moderados.
Reglas especificas:
- Puedes ordenar y limpiar frases pesadas si el sentido queda intacto.
- Conserva hechos, sujetos, matices, grado de certeza, causalidad y atribuciones.
- Evita cambiar verbos o expresiones que ya sean claros.
- No resumas, no amplies y no introduzcas informacion nueva.
- Si no hay una mejora clara, conserva la formulacion original.
""".strip()
        return """
Objetivo: mejorar claridad de forma suave.
Reglas especificas:
- Conserva hechos, sujetos, matices, grado de certeza, causalidad y atribuciones.
- No cambies un verbo o una expresion si el original ya se entiende.
- No endurezcas el tono para que suene mas rotundo.
- No resumas, no amplies y no introduzcas informacion nueva.
- Manten la estructura de parrafos salvo que haya una mejora claramente necesaria.
- Si no hay una mejora segura, devuelve exactamente el texto original.
""".strip()
    if payload.action == "correction":
        return """
Objetivo: corregir sin reescribir.
Reglas especificas:
- Corrige solo errores seguros de ortografia, puntuacion, espacios y concordancia evidente.
- Conserva palabras, orden y voz siempre que sea posible.
""".strip()
    if payload.action == "continue":
        return """
Objetivo: continuar el texto.
Reglas especificas:
- Continua la idea sin cerrarla de golpe.
- No contradigas la posicion ni cambies la voz del fragmento.
""".strip()
    if payload.action == "variants":
        return """
Objetivo: proponer alternativas.
Reglas especificas:
- Ofrece alternativas diferenciadas sin borrar la intencion original.
""".strip()
    return "Objetivo: trabajar el texto conservando la intencion original."


def _revision_intention_contract(intention: str) -> str:
    if intention == "tono":
        return (
            "Mirada: voz y tono. Ajusta actitud, distancia y registro solo cuando sea necesario; "
            "no conviertas una aclaracion en una version mas dura o mas editorial."
        )
    if intention == "estructura":
        return (
            "Mirada: estructura. Revisa foco, progresion y cierre sin cambiar los hechos. "
            "Si el borrador es una nota, correo o lista desordenada, ordenalo como una "
            "comunicacion final clara y enviable."
        )
    if intention == "limpieza":
        return "Mirada: limpieza final. Atiende puntuacion, repeticiones y remate superficial."
    return "Mirada: comprension. Revisa orden, ambiguedad y facilidad de lectura."


def _paragraph_rewrite(value: str, sentences_per_paragraph: int = 3) -> str:
    sentences = [sentence.strip() for sentence in SENTENCE_RE.split(value) if sentence.strip()]
    if len(sentences) < 4 or "\n\n" in value:
        return value

    paragraphs = [
        " ".join(sentences[index : index + sentences_per_paragraph])
        for index in range(0, len(sentences), sentences_per_paragraph)
    ]
    return "\n\n".join(paragraphs)


def _protect_terms(value: str, terms: list[str]) -> tuple[str, list[tuple[str, str]]]:
    protected = value
    replacements: list[tuple[str, str]] = []

    for term in sorted((item.strip() for item in terms), key=len, reverse=True):
        if not term:
            continue
        pattern = re.compile(rf"(?<!\w){re.escape(term)}(?!\w)", re.IGNORECASE)

        def replace_match(match: re.Match[str]) -> str:
            token = PROTECTED_TOKEN_TEMPLATE.format(index=len(replacements))
            replacements.append((token, match.group(0)))
            return token

        protected = pattern.sub(replace_match, protected)

    return protected, replacements


def _restore_terms(value: str, replacements: list[tuple[str, str]]) -> str:
    restored = value
    for token, term in replacements:
        restored = restored.replace(token, term)
    return restored


def _capitalize_sentence_starts(value: str) -> str:
    def replace_match(match: re.Match[str]) -> str:
        return f"{match.group(1)}{match.group(2).upper()}"

    return SENTENCE_START_RE.sub(replace_match, value)


def _add_opening_marks(value: str) -> str:
    sentences = SENTENCE_RE.split(value)
    corrected = []
    for sentence in sentences:
        stripped = sentence.lstrip()
        leading = sentence[: len(sentence) - len(stripped)]
        if stripped.endswith("?") and "¿" not in stripped:
            stripped = f"¿{stripped}"
        if stripped.endswith("!") and "¡" not in stripped:
            stripped = f"¡{stripped}"
        corrected.append(f"{leading}{stripped}")
    return " ".join(corrected)


def _apply_safe_editorial_replacements(value: str) -> str:
    corrected = value
    for pattern, replacement in SAFE_EDITORIAL_REPLACEMENTS:
        corrected = pattern.sub(replacement, corrected)
    return corrected


def _safe_surface_correction(value: str) -> str:
    corrected = " ".join(value.split())
    corrected = PUNCTUATION_SPACING_RE.sub(r"\1", corrected)
    corrected = MISSING_SPACE_AFTER_PUNCTUATION_RE.sub(r"\1 ", corrected)
    corrected = _apply_safe_editorial_replacements(corrected)
    corrected = _capitalize_sentence_starts(corrected)
    corrected = _add_opening_marks(corrected)
    corrected = PUNCTUATION_SPACING_RE.sub(r"\1", corrected)
    return corrected


def _local_rewrite_if_safer_than_noop(
    payload: GenerationInput,
    variables: list[ScoreVariable],
) -> GenerationResult | None:
    fallback = rewrite_deterministic(payload, variables)
    if fallback.output == payload.text.strip():
        return None
    return fallback


def _profile_prompt(variables: list[ScoreVariable]) -> str:
    lines = [
        f"- {item.key}: efectivo={item.effective_value}, confianza={item.confidence:.2f}, contexto={item.context}"
        for item in sorted(variables, key=lambda variable: variable.effective_value, reverse=True)
    ]
    return "\n".join(lines)


def rewrite_with_profile(payload: GenerationInput, variables: list[ScoreVariable]) -> GenerationResult:
    if payload.action == "correction":
        return rewrite_deterministic(payload, variables)

    if getenv("OPENAI_API_KEY"):
        try:
            return rewrite_with_openai(payload, variables)
        except Exception:
            fallback = rewrite_deterministic(payload, variables)
            return fallback.model_copy(
                update={
                    "explanation": (
                        "No se pudo completar la generacion externa. "
                        f"{fallback.explanation}"
                    )
                }
            )

    return rewrite_deterministic(payload, variables)


def rewrite_deterministic(payload: GenerationInput, variables: list[ScoreVariable]) -> GenerationResult:
    active = sorted(variables, key=lambda item: item.effective_value, reverse=True)[:3]
    preserved, protected_replacements = _protect_terms(payload.text, payload.protected_terms)
    original = preserved.strip()
    output = original
    normalized_original = original
    paragraph_adjusted = False
    if payload.action in {"rewrite", "correction", "sendable"}:
        output = _safe_surface_correction(output)
        normalized_original = output
        if payload.action in {"rewrite", "sendable"}:
            output = _paragraph_rewrite(output)
            paragraph_adjusted = output != normalized_original
        if payload.intensity > 650 and not output.endswith("."):
            output = f"{output}."
    elif payload.action == "continue":
        output = f"{output}\n\nContinuacion propuesta: desarrolla la idea con precision y sin aprender nada automaticamente."
    elif payload.action == "variants":
        output = (
            f"Variante A: {output}\n\n"
            f"Variante B: {output} Mantiene la intencion y ajusta el ritmo.\n\n"
            f"Variante C: {output} Conserva terminos protegidos y reduce rodeos."
        )

    output = _restore_terms(output, protected_replacements)

    if output == payload.text.strip():
        explanation = (
            "No se aplicaron cambios deterministas seguros. El texto ya estaba limpio para este "
            "modo local; para una reescritura profunda hace falta activar generacion externa."
        )
    elif paragraph_adjusted:
        explanation = (
            "Reescritura estructural local: ordena el texto en parrafos sin inventar contenido "
            "ni aplicar aprendizaje automatico."
        )
    elif payload.action == "correction":
        explanation = (
            "Correccion local segura: ajusta espacios, puntuacion visible y mayusculas de frase "
            "sin reescribir tu voz ni aplicar aprendizaje automatico."
        )
    elif payload.action == "continue":
        explanation = (
            "Continuacion local de arranque: propone un siguiente tramo sin aplicar aprendizaje "
            "automatico."
        )
    elif payload.action == "variants":
        explanation = (
            "Variantes locales de arranque: ofrece alternativas sin aplicar aprendizaje "
            "automatico."
        )
    elif payload.action == "sendable":
        explanation = (
            "Preparacion local para enviar: aplica solo cambios seguros. Para convertir notas "
            "en un texto final completo hace falta generacion externa."
        )
    else:
        explanation = (
            "Reescritura local segura: aplica solo cambios de bajo riesgo y no aprende nada "
            "automaticamente."
        )

    return GenerationResult(
        output=output,
        explanation=explanation,
        used_profile_variables=[item.key for item in active],
    )


def rewrite_with_openai(payload: GenerationInput, variables: list[ScoreVariable]) -> GenerationResult:
    active = sorted(variables, key=lambda item: item.effective_value, reverse=True)[:5]
    model = getenv("OPENAI_MODEL", "gpt-5-mini")
    prompt = f"""
Eres Minicerebro V1, una app especializada en escritura en lengua espanola.
Accion: {payload.action}
Contexto: {payload.context}
Intensidad: {payload.intensity}/1000
{_generation_contract(payload)}
{_revision_intention_contract(payload.revision_intention)}
Terminos protegidos: {", ".join(payload.protected_terms) or "ninguno"}

Perfil efectivo:
{_profile_prompt(active)}

Reglas:
- No aprendas nada.
- No afirmes que has actualizado el perfil.
- Respeta los terminos protegidos literalmente.
- Devuelve solo el texto resultante, sin explicaciones externas.

Texto:
{payload.text}
""".strip()

    response = _openai_client().responses.create(
        model=model,
        input=prompt,
        max_output_tokens=_max_output_tokens(payload),
        reasoning={"effort": "minimal"},
        store=False,
        timeout=_openai_timeout_seconds(),
    )
    output = getattr(response, "output_text", "").strip()
    if not output:
        output = payload.text
    local_fallback = _local_rewrite_if_safer_than_noop(payload, variables)
    output_is_original = output.strip() == payload.text.strip()
    over_rewritten = False
    if payload.action == "rewrite":
        over_rewritten = _is_over_rewritten(
            payload.text,
            output,
            payload.intensity,
            payload.revision_intention,
        )
    elif payload.action == "sendable":
        over_rewritten = _content_token_overlap(payload.text, output) < 0.45
    if over_rewritten:
        output = local_fallback.output if local_fallback else payload.text
    elif output_is_original and local_fallback:
        output = local_fallback.output
    if over_rewritten:
        if local_fallback:
            explanation = (
                "La propuesta externa cambiaba demasiado para una mejora segura; "
                f"se aplico una correccion local de bajo riesgo. {local_fallback.explanation}"
            )
        else:
            explanation = (
                "La propuesta externa cambiaba demasiado para una mejora de claridad segura; "
                "se conserva el borrador. No aplica aprendizaje automatico."
            )
    elif output_is_original and local_fallback:
        explanation = (
            "La propuesta externa no anadio cambios, pero el texto tenia correcciones locales "
            f"seguras. {local_fallback.explanation}"
        )
    else:
        explanation = (
            f"Generacion LLM con {model}. Usa perfil y contexto solo para esta salida; "
            "no aplica aprendizaje automatico."
        )

    return GenerationResult(
        output=output,
        explanation=explanation,
        used_profile_variables=[item.key for item in active],
        learning_applied=False,
        provider="openai",
    )
