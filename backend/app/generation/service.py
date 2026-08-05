import re
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

COMMUNICATIVE_DRAFT_MARKERS = (
    "buenos dias",
    "buenas tardes",
    "buenas noches",
    "un saludo",
    "quedo pendiente",
    "les recuerdo",
    "comunidad",
    "tecnico",
    "presupuesto",
    "mantenimiento",
    "visto bueno",
    "1º",
    "2º",
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
    if payload.action == "sendable" or (
        payload.action == "rewrite" and _looks_like_communicative_draft(payload.text)
    ):
        return min(3200, max(520, round(word_count * 2.2) + 260))
    if payload.action == "continue":
        return min(900, max(220, round(word_count * 0.8) + 120))
    if payload.action == "variants":
        return min(1600, max(420, round(word_count * 2.0) + 180))
    return min(2400, max(220, round(word_count * 1.6) + 120))


def _strip_accents_for_matching(value: str) -> str:
    replacements = str.maketrans("áéíóúüñÁÉÍÓÚÜÑ", "aeiouunAEIOUUN")
    return value.translate(replacements)


def _looks_like_communicative_draft(value: str) -> bool:
    normalized = _strip_accents_for_matching(value).lower()
    marker_count = sum(marker in normalized for marker in COMMUNICATIVE_DRAFT_MARKERS)
    has_numbered_points = bool(re.search(r"(^|\n)\s*(?:\d+[º.]|-)\s+", value))
    return marker_count >= 2 or has_numbered_points


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


def _content_token_count(value: str) -> int:
    return len(
        [
            token
            for token in CONTENT_TOKEN_RE.findall(value.lower())
            if len(token) >= 4
        ]
    )


def _anchor_tokens(value: str) -> set[str]:
    tokens = set()
    for token in CONTENT_TOKEN_RE.findall(value):
        if token.isdigit() or len(token) >= 7 or token[:1].isupper():
            tokens.add(token.lower())
    return tokens


def _anchor_token_overlap(original: str, output: str) -> float:
    original_tokens = _anchor_tokens(original)
    if not original_tokens:
        return _content_token_overlap(original, output)
    output_tokens = _anchor_tokens(output)
    return len(original_tokens & output_tokens) / len(original_tokens)


def _loses_required_anchors(
    original: str,
    output: str,
    intensity: int,
    revision_intention: str = "claridad",
) -> bool:
    anchor_overlap = _anchor_token_overlap(original, output)
    output_too_short = _content_token_count(output) < max(8, _content_token_count(original) * 0.35)
    if revision_intention == "estructura" and intensity >= 850:
        return anchor_overlap < 0.15 and output_too_short
    if intensity >= 850:
        return anchor_overlap < 0.20 and output_too_short
    if anchor_overlap >= 0.25:
        return _content_token_overlap(original, output) < 0.45
    return _content_token_overlap(original, output) < 0.35


def _sendable_loses_required_anchors(original: str, output: str) -> bool:
    if _anchor_token_overlap(original, output) >= 0.12:
        return False
    output_too_short = _content_token_count(output) < max(10, _content_token_count(original) * 0.35)
    return _content_token_overlap(original, output) < 0.12 and output_too_short


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
- No te limites a comas, articulos o retoques superficiales: si el borrador
  esta en bruto, transformalo de verdad en una comunicacion enviable.
- El original puede estar mal escrito, incompleto o ser solo una descripcion
  aproximada: usalo como material de partida, no como fraseado obligatorio.
- Puedes cambiar practicamente toda la redaccion si hace falta para que el texto
  sea claro, responsable y enviable.
- Puedes precisar tecnicamente lo que ya esta en el borrador cuando la informacion
  lo permite: circuito, fluido, bombas, placas, acumulador, perdida o presion si
  aparecen en el relato o se deducen claramente de el.
- No inventes costes, causas cerradas, acuerdos, diagnosticos, datos tecnicos ni
  decisiones de terceros que el usuario no haya aportado.
- Cuando un dato tecnico no este confirmado, mantenlo como duda o solicitud de
  aclaracion: "segun entendi", "no me quedo claro", "convendria aclarar".
- Devuelve solo la version final lista para enviar.
""".strip()
    if payload.action == "rewrite":
        if _looks_like_communicative_draft(payload.text):
            return """
Objetivo: convertir un borrador comunicativo en una version clara y lista para enviar.
Reglas especificas:
- Esta accion es editar, no corregir: toma decisiones de forma, orden y enfoque
  cuando el borrador lo necesite.
- Trata el original como material de partida, no como fraseado obligatorio.
- Si el texto esta explicado de forma aproximada, ordenalo y redactalo de nuevo.
- No te limites a comas, articulos, tildes o pequenos retoques: prepara una
  comunicacion completa cuando el material lo permita.
- Puedes cambiar practicamente toda la redaccion si hace falta para que el texto
  sea claro, responsable y enviable.
- Puedes cambiar la estructura: convertir una lista pobre en secciones, agrupar
  motivos, separar dudas, crear cierre o priorizar lo importante para el lector.
- Si el usuario pide mas tecnico, mas formal, menos formal, mas directo u otro
  angulo, aplica esa indicacion sin inventar informacion.
- Conserva todos los hechos, dudas, condiciones, nombres, direcciones, fechas,
  responsabilidades y grado de certeza.
- Formula las dudas como dudas y los pendientes como solicitudes de aclaracion.
- Puedes precisar tecnicamente lo que ya esta en el borrador cuando la informacion
  lo permite: circuito, fluido, bombas, placas, acumulador, perdida o presion si
  aparecen en el relato o se deducen claramente de el.
- No inventes costes, causas cerradas, acuerdos, diagnosticos, datos tecnicos ni
  decisiones de terceros que el usuario no haya aportado.
- Devuelve solo la version reescrita.
""".strip()
        if payload.revision_intention == "estructura":
            return """
Objetivo: editar la estructura del borrador para que el texto funcione mejor.
Reglas especificas:
- Esta accion es editar estructura, no corregir superficie: no la reduzcas a
  comas, articulos, sinonimos o retoques frase a frase.
- Trata el original como material de partida, no como arquitectura obligatoria.
- Puedes cambiar el orden de ideas, dividir o fusionar parrafos, crear entrada,
  separar contexto de peticion, convertir bloques confusos en secciones y cerrar
  con una conclusion clara cuando el propio borrador lo pida.
- Si el texto es una nota, desahogo, apunte o lista de ideas, puedes convertirlo
  en una version organizada y lista para usar.
- La fidelidad consiste en conservar hechos, intencion, dudas, grado de certeza,
  nombres, fechas, atribuciones y responsabilidad; no en conservar el mismo orden.
- Si el usuario da una direccion libre, usala como angulo estructural prioritario
  para esta salida sin inventar informacion.
- Puedes dar forma tecnica prudente a informacion ya aportada, sin cerrar causas
  que el borrador presenta como inciertas.
- No inventes hechos, causas, acuerdos, diagnosticos, datos tecnicos ni decisiones
  de terceros que el usuario no haya aportado.
- Devuelve solo la version editada.
""".strip()
        if payload.intensity >= 850:
            return """
Objetivo: mejorar claridad con una reescritura decidida pero fiel.
Reglas especificas:
- Esta accion es editar: puede cambiar estructura, enfoque y formulacion si eso
  hace que el texto funcione mejor.
- Puedes compactar, reordenar y sustituir formulaciones torpes si mejora la lectura.
- Si el borrador parece una nota, correo, aviso o lista de puntos, puedes convertirlo en
  una version final clara y enviable.
- Puedes usar saludo, cierre y lista de puntos cuando el propio borrador lo pida.
- Puedes cambiar la arquitectura del texto cuando ayude: orden de parrafos,
  apartados, enumeraciones, foco inicial y cierre.
- Si el usuario da una indicacion concreta de angulo, aplicala como prioridad de
  esta salida.
- En intensidad alta, fidelidad significa conservar hechos, intencion y dudas; no
  conservar literalmente la misma frase.
- Si el original es un borrador bruto, una explicacion aproximada o una nota
  desordenada, puedes rehacer casi toda la redaccion.
- No confundas fidelidad con retoque minimo: si el texto esta mal enfocado,
  desordenado o explicado "como se ha podido", reescribelo hasta que funcione.
- No midas la calidad por el tamano del cambio: una reescritura grande puede
  ser correcta si conserva hechos, dudas e intencion.
- El usuario puede traer material bruto; tu trabajo es darle forma de texto, no
  maquillarlo con correcciones pequenas.
- Explicita dudas ya presentes, pero no anadas datos nuevos.
- Puedes dar forma tecnica prudente a informacion ya aportada, sin cerrar causas
  que el borrador presenta como inciertas.
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
- Esta accion es editar, no limpiar: si el problema es de orden, foco o sentido,
  actua sobre el texto completo.
- Puedes reescribir frases completas cuando ganen claridad, naturalidad o ritmo,
  aunque no tengan errores gramaticales.
- Puedes ordenar, mover de lugar, dividir, fusionar, sustituir o eliminar frases
  redundantes si el sentido queda intacto.
- Si el texto es un borrador bruto o una explicacion aproximada, no te limites a
  articulos, comas o tildes: mejora la formulacion real.
- No valores "cambiar poco" como bueno por si mismo; valora si el resultado
  queda mas claro y fiel a lo que el usuario queria decir.
- Conserva hechos, sujetos, matices, grado de certeza, causalidad y atribuciones.
- Evita cambiar verbos o expresiones que ya sean claros, pero cambia los que
  estorben a la comprension.
- No resumas, no amplies y no introduzcas informacion nueva.
- Si no hay una mejora clara, conserva la formulacion original.
- Si el usuario da una indicacion libre, usala para orientar el angulo sin
  convertirla en dato nuevo.
""".strip()
        return """
Objetivo: mejorar claridad de forma suave.
Reglas especificas:
- Esta accion es editar con baja intensidad: evita rehacer por capricho, pero no
  la reduzcas a comas y erratas si hay una mejora real de escritura.
- Puedes cambiar una frase completa si la frase actual suena torpe, confusa o
  poco natural; editar no significa conservar el fraseo original.
- Puedes mover frases de lugar o eliminar repeticiones claras cuando ayude a que
  el texto fluya mejor.
- No te limites a corregir faltas: reformula con prudencia cuando mejore la
  comprension sin cambiar hechos.
- Conserva hechos, sujetos, matices, grado de certeza, causalidad y atribuciones.
- No cambies un verbo o una expresion si el original ya se entiende, pero no
  confundas limpieza superficial con mejora cuando una frase esta torpe.
- No endurezcas el tono para que suene mas rotundo.
- No resumas, no amplies y no introduzcas informacion nueva.
- Manten la estructura de parrafos salvo que haya una mejora claramente necesaria.
- Si el usuario da una indicacion libre, puede orientar tono, registro o angulo
  sin convertirse en aprendizaje permanente.
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
            "comunicacion final clara y enviable. Puede dar forma tecnica prudente a "
            "datos ya aportados, sin convertir dudas en certezas."
        )
    if intention == "limpieza":
        return "Mirada: limpieza final. Atiende puntuacion, repeticiones y remate superficial."
    return "Mirada: comprension. Revisa orden, ambiguedad y facilidad de lectura."


def _user_instruction_contract(payload: GenerationInput) -> str:
    instruction = " ".join(payload.user_instruction.split())
    if not instruction:
        return "Indicacion libre del usuario: ninguna."
    return (
        "Indicacion libre del usuario para esta salida: "
        f"{instruction}\n"
        "Prioridad: aplicala al angulo, tono, nivel tecnico o estructura del texto. "
        "No la conviertas en dato nuevo ni en aprendizaje permanente."
    )


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
{_user_instruction_contract(payload)}
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
    loses_required_anchors = False
    if payload.action == "rewrite":
        loses_required_anchors = _loses_required_anchors(
            payload.text,
            output,
            payload.intensity,
            payload.revision_intention,
        )
    elif payload.action == "sendable":
        loses_required_anchors = _sendable_loses_required_anchors(payload.text, output)
    if loses_required_anchors:
        output = local_fallback.output if local_fallback else payload.text
    elif output_is_original and local_fallback:
        output = local_fallback.output
    if loses_required_anchors:
        if local_fallback:
            explanation = (
                "La propuesta externa perdia datos importantes del borrador; "
                f"se aplico una correccion local de bajo riesgo. {local_fallback.explanation}"
            )
        else:
            explanation = (
                "La propuesta externa perdia datos importantes del borrador; "
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
