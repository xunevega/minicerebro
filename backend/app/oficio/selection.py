"""Diagnóstico del texto y selección de fichas (docs/POLITICA_CONOCIMIENTO.md, §4 y §5).

Las fichas no se eligen por palabras del texto, sino por:
1. señales y métricas que delatan el problema en el borrador;
2. la acción y la mirada elegidas;
3. el tipo de texto que declara el autor;
4. las relaciones «requiere» de las fichas ya elegidas.
"""

import re
import unicodedata
from dataclasses import dataclass, field
from itertools import pairwise

from app.oficio.catalog import Ficha, load_fichas

MAX_FICHAS = 12
# Los problemas confirmados en el texto no se quedan fuera por el tope: se añaden
# detrás de las elegidas, como mucho estos más.
MAX_PROBLEMAS_EXTRA = 6
MAX_FRAGMENTOS = 2
LONG_SENTENCE_WORDS = 45
REPETITION_WINDOW = 12
REPETITION_MIN_LETTERS = 6

# Acciones que trabajan ideas y bloques: las fichas de norma solo distraen.
ACCIONES_SIN_NORMA = {"review"}
# Corregir solo atiende norma.
ACCIONES_SOLO_NORMA = {"correction"}
ACCION_EQUIVALENTE = {"continue": "rewrite", "variants": "rewrite"}
ACCIONES_QUE_REESCRIBEN = {"rewrite", "sendable", "review"}
# Nombres antiguos de las miradas que aún llegan desde algunas pantallas.
MIRADA_EQUIVALENTE = {"claridad": "comprension", "comprensión": "comprension"}
# Postura del usuario ante una ficha (criterio personal): sube o baja su peso.
PESO_POR_POSTURA = {"liked": 1.5, "kept": 1.5, "changed": -1.0, "dismissed": -3.0}

PRIORIDAD_GENERAL = (
    "Orden general si dos fichas chocan y no hay relación más concreta: norma > sentido "
    "(hechos, tesis y matices) > claridad y precisión > concisión > ritmo y voz. En "
    "narrativa y textos literarios, ritmo y voz suben por encima de claridad y concisión."
)

SENTENCE_RE = re.compile(r"(?<=[.!?…])\s+|\n+")
WORD_RE = re.compile(r"[\wáéíóúüñÁÉÍÓÚÜÑ]+", re.UNICODE)
STOPWORDS = {
    "porque", "aunque", "cuando", "siempre", "también", "entonces", "mientras", "después",
    "nuestro", "nuestra", "nuestros", "nuestras", "aquello", "aquella", "aquellos", "aquellas",
    "cualquier", "ninguno", "ninguna", "algunos", "algunas", "mismo", "misma", "mismos",
    "mismas", "todavía", "tampoco", "durante", "contra", "desde", "hasta", "sobre", "entre",
    "puede", "pueden", "estaba", "estaban", "tienen", "hacer", "había", "habían", "sería",
}


@dataclass
class SelectedFicha:
    ficha: Ficha
    motivos: list[str] = field(default_factory=list)
    fragmentos: list[str] = field(default_factory=list)
    peso: float = 0.0
    # Hay un fallo concreto en el texto: señal de error (no descartada) o diagnóstico.
    problema: bool = False
    # Límites de fichas no elegidas que prevalecen sobre esta o chocan con ella.
    limites: list[str] = field(default_factory=list)


@dataclass
class Diagnosis:
    """Resultado del diagnóstico previo: señales falsas y problemas sin patrón."""

    descartadas: set[str] = field(default_factory=set)
    anadidas: dict[str, str] = field(default_factory=dict)


def _canon(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _snippet(text: str, start: int, end: int, margin: int = 50) -> str:
    left = max(0, start - margin)
    right = min(len(text), end + margin)
    left = text.rfind(" ", 0, left) + 1 if left > 0 else 0
    space = text.find(" ", right)
    right = len(text) if space == -1 else space
    fragment = " ".join(text[left:right].split())
    return f"{'…' if left > 0 else ''}{fragment}{'…' if right < len(text) else ''}"


def _strip_accents(value: str) -> str:
    # Conserva la longitud (una letra por letra) para que las posiciones sigan valiendo.
    out = []
    for char in value:
        base = "".join(c for c in unicodedata.normalize("NFKD", char) if not unicodedata.combining(c))
        out.append(base[:1] or char)
    return "".join(out)


def _signal_hits(ficha: Ficha, text: str, tipo: str | None = None) -> list[str]:
    """Busca cada señal en el texto tal cual y sin tildes (borradores escritos deprisa).

    Con «tipo», solo las señales de ese tipo («error» o «vigilancia»).
    """
    hits: list[str] = []
    seen: set[int] = set()
    plain_text = _strip_accents(text)
    for senal in ficha.senales:
        if tipo is not None and senal.tipo != tipo:
            continue
        pattern = senal.regex()
        passes = [(pattern, text)]
        if senal.tambien_sin_tildes:
            passes.append((re.compile(_strip_accents(senal.patron), pattern.flags), plain_text))
        for regex, haystack in passes:
            for match in regex.finditer(haystack):
                if match.start() in seen:
                    continue
                seen.add(match.start())
                hits.append(_snippet(text, match.start(), match.end()))
                if len(hits) >= MAX_FRAGMENTOS:
                    return hits
    return hits


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in SENTENCE_RE.split(text) if part.strip()]


def _long_sentences(text: str) -> list[str]:
    found = []
    for sentence in _sentences(text):
        words = WORD_RE.findall(sentence)
        if len(words) > LONG_SENTENCE_WORDS:
            found.append(" ".join(words[:14]) + "… (" + str(len(words)) + " palabras)")
    return found


def _close_repetitions(text: str) -> list[str]:
    found = []
    for sentence_pair in _paired_sentences(text):
        tokens = WORD_RE.findall(sentence_pair)
        canon = [_canon(token) for token in tokens]
        for index, word in enumerate(canon):
            if len(word) < REPETITION_MIN_LETTERS or word in {_canon(s) for s in STOPWORDS}:
                continue
            window = canon[index + 1 : index + 1 + REPETITION_WINDOW]
            if word in window:
                found.append(f"«{tokens[index]}» repetida en: {' '.join(tokens[max(0, index - 4):index + 10])}…")
                break
        if len(found) >= MAX_FRAGMENTOS:
            break
    return found


def _paired_sentences(text: str) -> list[str]:
    sentences = _sentences(text)
    return [" ".join(sentences[i : i + 2]) for i in range(len(sentences))]


def _anaphoras(text: str) -> list[str]:
    found = []
    clauses = [part.strip() for part in re.split(r"[.;:]\s+|\n+", text) if part.strip()]
    for first, second in pairwise(clauses):
        a = WORD_RE.findall(first)
        b = WORD_RE.findall(second)
        if a and b and len(a[0]) >= 3 and _canon(a[0]) == _canon(b[0]):
            found.append(f"{' '.join(a[:6])}… / {' '.join(b[:6])}…")
            if len(found) >= MAX_FRAGMENTOS:
                break
    return found


def _paragraphs(text: str) -> list[str]:
    return [paragraph.strip() for paragraph in text.splitlines() if paragraph.strip()]


def _style_drift(text: str) -> list[str]:
    """Longitud media de frase muy distinta entre el primer y el último tercio."""
    lengths = [len(WORD_RE.findall(sentence)) for sentence in _sentences(text)]
    if len(lengths) < 8:
        return []
    third = max(1, len(lengths) // 3)
    start = sum(lengths[:third]) / third
    end = sum(lengths[-third:]) / third
    if abs(start - end) < 8:
        return []
    message = (
        f"El primer tramo va con frases de unas {round(start)} palabras y el último con unas "
        f"{round(end)}: el ritmo y la distancia cambian entre el principio y el final."
    )
    return [message]


def _long_paragraphs(text: str) -> list[str]:
    found = []
    for paragraph in _paragraphs(text):
        words = WORD_RE.findall(paragraph)
        if len(words) > 90:
            found.append(" ".join(words[:12]) + f"… ({len(words)} palabras en un párrafo)")
            if len(found) >= MAX_FRAGMENTOS:
                break
    return found


def _single_block(text: str) -> list[str]:
    paragraphs = _paragraphs(text)
    words = WORD_RE.findall(text)
    if len(paragraphs) == 1 and len(words) > 80:
        return [f"Todo el texto va en un solo bloque de {len(words)} palabras."]
    return []


def _sentence_fragment(sentence: str, words: int = 12) -> str:
    tokens = WORD_RE.findall(sentence)
    return " ".join(tokens[:words]) + ("…" if len(tokens) > words else "")


def _count_per_sentence(text: str, pattern: re.Pattern[str], minimum: int, label: str) -> list[str]:
    found = []
    for sentence in _sentences(text):
        count = len(pattern.findall(sentence))
        if count >= minimum:
            found.append(f"{_sentence_fragment(sentence)} ({count} {label} en una frase)")
            if len(found) >= MAX_FRAGMENTOS:
                break
    return found


QUE_RE = re.compile(r"\bque\b", re.IGNORECASE)
DE_CHAIN_RE = re.compile(r"\bde\b(?:\s+\S+){1,3}?\s+de\b(?:\s+\S+){1,3}?\s+de\b(?:\s+\S+){1,3}?\s+de\b", re.IGNORECASE)
MENTE_RE = re.compile(r"\b\w{4,}mente\b", re.IGNORECASE)
SUFIJO_RE = re.compile(r"\b\w+(ción|ciones|miento|mientos|mente|idad|idades)\b", re.IGNORECASE)
INTENSIFICADOR_RE = re.compile(
    r"\b(muy|realmente|absolutamente|totalmente|completamente|increíblemente|"
    r"tremendamente|enormemente|sumamente|súper|super|verdaderamente|extremadamente)\b",
    re.IGNORECASE,
)
USTED_RE = re.compile(r"\busted(es)?\b", re.IGNORECASE)
TU_RE = re.compile(r"\b(tú|vosotros|vosotras|contigo|os)\b|\b(tienes|puedes|quieres|sabes|debes|eres|estás|vas)\b", re.IGNORECASE)


def _que_chains(text: str) -> list[str]:
    return _count_per_sentence(text, QUE_RE, 4, "«que»")


def _de_chains(text: str) -> list[str]:
    found = []
    for sentence in _sentences(text):
        match = DE_CHAIN_RE.search(sentence)
        if match:
            found.append("…" + " ".join(match.group(0).split()) + "…")
            if len(found) >= MAX_FRAGMENTOS:
                break
    return found


def _mente_chains(text: str) -> list[str]:
    return _count_per_sentence(text, MENTE_RE, 2, "adverbios en -mente")


def _suffix_echo(text: str) -> list[str]:
    found = []
    for sentence in _sentences(text):
        endings = [match.group(1).lower() for match in SUFIJO_RE.finditer(sentence)]
        for ending in set(endings):
            if endings.count(ending) >= 3:
                found.append(f"{_sentence_fragment(sentence)} ({endings.count(ending)} palabras en -{ending})")
                break
        if len(found) >= MAX_FRAGMENTOS:
            break
    return found


def _intensifiers(text: str) -> list[str]:
    words = WORD_RE.findall(text)
    hits = INTENSIFICADOR_RE.findall(text)
    if len(hits) >= 3 and len(hits) * 100 / max(1, len(words)) >= 1.5:
        return [f"{len(hits)} intensificadores en {len(words)} palabras («{hits[0]}», «{hits[1]}», «{hits[2]}»…)"]
    return []


def _short_sentence_runs(text: str) -> list[str]:
    run: list[str] = []
    for sentence in _sentences(text):
        if len(WORD_RE.findall(sentence)) < 8:
            run.append(sentence)
            if len(run) >= 6:
                return [f"{len(run)} frases muy cortas seguidas: «{run[0]}» … «{run[-1]}»"]
        else:
            run = []
    return []


def _mixed_address(text: str) -> list[str]:
    usted = USTED_RE.search(text)
    tu = TU_RE.search(text)
    if usted and tu:
        return [f"Trato de usted («{usted.group(0)}») y de tú («{tu.group(0)}») en el mismo texto."]
    return []


def _chained_insertions(text: str) -> list[str]:
    """Frases con muchos incisos: cuatro o más comas en poco espacio."""
    found = []
    for sentence in _sentences(text):
        words = WORD_RE.findall(sentence)
        if sentence.count(",") >= 4 and 18 <= len(words) <= 60:
            found.append(f"{_sentence_fragment(sentence)} ({sentence.count(',')} comas en una frase)")
            if len(found) >= MAX_FRAGMENTOS:
                break
    return found


METRIC_FUNCTIONS = {
    "incisos": _chained_insertions,
    "ques_encadenados": _que_chains,
    "des_encadenados": _de_chains,
    "mente_encadenados": _mente_chains,
    "eco_sufijos": _suffix_echo,
    "intensificadores": _intensifiers,
    "frases_cortas": _short_sentence_runs,
    "trato_mixto": _mixed_address,
    "deriva_estilo": _style_drift,
    "parrafo_largo": _long_paragraphs,
    "bloque_unico": _single_block,
    "frase_larga": _long_sentences,
    "repeticion_cercana": _close_repetitions,
    "anafora": _anaphoras,
}


def _genre_matches(ficha: Ficha, genre: str) -> bool:
    declared = _canon(genre)
    return any(_canon(keyword) in declared for keyword in ficha.generos)


def _allowed(ficha: Ficha, action: str) -> bool:
    if action in ACCIONES_SOLO_NORMA:
        return ficha.rama == "lengua"
    if action in ACCIONES_SIN_NORMA:
        return ficha.rama != "lengua"
    return True


SENTENCE_METRICS = {
    "ques_encadenados", "des_encadenados", "mente_encadenados", "eco_sufijos",
    "intensificadores", "frases_cortas", "trato_mixto", "incisos",
}


def check_ficha_signals(ficha: Ficha, others: list[Ficha] | None = None) -> list[str]:
    """Problemas de calidad de las señales de una ficha (los mismos que exigen los tests).

    Cada señal de error tiene que saltar en el ejemplo malo y no en el bueno; si se
    pasan otras fichas, tampoco puede saltar en los ejemplos buenos de ninguna.
    """
    problems: list[str] = []
    error_signals = [senal for senal in ficha.senales if senal.tipo == "error"]
    metrics = [metric for metric in ficha.metricas if metric in SENTENCE_METRICS]
    if not error_signals and not metrics:
        return problems
    for index, ejemplo in enumerate(ficha.ejemplos, start=1):
        hits = _signal_hits(ficha, ejemplo.mal, "error")
        for metric in metrics:
            hits += METRIC_FUNCTIONS[metric](ejemplo.mal)
        if index == 1 and not hits:
            problems.append("Ninguna señal de error salta en el primer ejemplo malo.")
        if error_signals and _signal_hits(ficha, ejemplo.bien, "error"):
            problems.append(f"Una señal de error salta en el ejemplo bueno {index}.")
    if error_signals:
        for other in others or []:
            if other.id == ficha.id:
                continue
            for ejemplo in other.ejemplos:
                if _signal_hits(ficha, ejemplo.bien, "error"):
                    problems.append(
                        f"Una señal de error salta en el ejemplo bueno de «{other.nombre}»: "
                        f"«{ejemplo.bien[:80]}»."
                    )
                    break
    return problems


def select_fichas(
    text: str,
    action: str,
    intention: str = "comprension",
    genre: str = "",
    limit: int = MAX_FICHAS,
    preferences: dict[str, str] | None = None,
    instruction: str = "",
    fichas: dict[str, Ficha] | None = None,
    diagnosis: Diagnosis | None = None,
    learned: dict[str, tuple[float, str]] | None = None,
) -> list[SelectedFicha]:
    action = ACCION_EQUIVALENTE.get(action, action)
    intention = MIRADA_EQUIVALENTE.get(intention, intention)
    fichas = fichas if fichas is not None else load_fichas()
    chosen: dict[str, SelectedFicha] = {}

    def add(ficha: Ficha, motivo: str, peso: float, fragmentos: list[str] | None = None) -> None:
        item = chosen.setdefault(ficha.id, SelectedFicha(ficha=ficha))
        if motivo not in item.motivos:
            item.motivos.append(motivo)
        item.peso += peso
        for fragment in fragmentos or []:
            if fragment not in item.fragmentos and len(item.fragmentos) < MAX_FRAGMENTOS:
                item.fragmentos.append(fragment)

    for ficha in fichas.values():
        if not _allowed(ficha, action):
            continue
        genre_specific = bool(ficha.generos)
        genre_ok = bool(genre.strip()) and _genre_matches(ficha, genre)
        # La dirección del autor («más esperpéntico», «como un soneto») también activa fichas.
        instruction_ok = bool(instruction.strip()) and _genre_matches(ficha, instruction)
        if genre_specific and genre.strip() and not (genre_ok or instruction_ok):
            continue

        discarded = diagnosis is not None and ficha.id in diagnosis.descartadas
        error_hits = [] if discarded else _signal_hits(ficha, text, "error")
        signal_errors = bool(error_hits)
        if not discarded:
            for metric in ficha.metricas:
                error_hits.extend(METRIC_FUNCTIONS[metric](text))
        watch_hits = [] if discarded else _signal_hits(ficha, text, "vigilancia")
        diagnosed = diagnosis.anadidas.get(ficha.id) if diagnosis is not None else None
        if diagnosed is not None:
            add(ficha, "diagnóstico del texto", 4.0, [diagnosed] if diagnosed else [])
            chosen[ficha.id].problema = True
            signal_errors = True
        if genre_specific and not (genre_ok or instruction_ok):
            # Sin el género declarado, una ficha de género solo entra si su señal de error
            # aparece en el texto; las métricas y los pasajes que vigilar no bastan.
            if not signal_errors:
                continue
            watch_hits = []
        hits = error_hits + watch_hits
        if error_hits:
            add(ficha, "señal en el texto", 3.0 + min(len(error_hits), 3), error_hits)
            chosen[ficha.id].problema = True
        if watch_hits:
            # Un sitio que vigilar pesa menos que un fallo probable, salvo que la ficha
            # proteja el sentido y la acción vaya a reescribir el texto.
            if ficha.protege and action in ACCIONES_QUE_REESCRIBEN:
                add(ficha, "pasaje que proteger al reescribir", 3.0 + min(len(watch_hits), 3), watch_hits)
            else:
                add(ficha, "pasaje que vigilar", 1.5 + 0.5 * min(len(watch_hits), 2), watch_hits)
        if instruction_ok:
            add(ficha, "pedido en tu dirección", 5.0)
        if action in ficha.base.acciones:
            add(ficha, "base de la acción", 4.0)
        if intention in ficha.base.miradas and action != "review":
            add(ficha, f"mirada «{intention}»", 2.5)
        # Las fichas con señales necesitan verlas en el texto; el género solo filtra.
        if genre_ok and (not ficha.senales or hits):
            add(ficha, "tipo de texto declarado", 3.5)

    # Relaciones «requiere»: entra la ficha requerida, con menos peso que quien la pide.
    required_by: dict[str, int] = {}
    for item in list(chosen.values()):
        for relacion in item.ficha.relaciones:
            target = fichas.get(relacion.ficha)
            if target is None:
                continue
            if relacion.tipo == "requiere" and _allowed(target, action):
                required_by[target.id] = required_by.get(target.id, 0) + 1
    for target_id, count in required_by.items():
        motivo = "la requiere otra ficha" if count == 1 else f"la requieren {count} fichas"
        add(fichas[target_id], motivo, 1.0 * count)

    # Criterio personal: lo que el usuario descartó baja; lo que le sirvió sube.
    # Una ficha descartada solo se queda si el texto la pide con una señal.
    for ficha_id, stance in (preferences or {}).items():
        item = chosen.get(ficha_id)
        if item is None:
            continue
        item.peso += PESO_POR_POSTURA.get(stance, 0.0)
        if stance == "dismissed" and not item.fragmentos:
            del chosen[ficha_id]
        elif stance in {"liked", "kept"}:
            item.motivos.append("te sirvió antes")

    # Capa 3: lo aprendido de tus decisiones (app/oficio/aprendizaje.py). Sube o baja
    # el peso de las elegidas y puede traer una ficha de tu línea editorial.
    for ficha_id, (peso, motivo) in (learned or {}).items():
        item = chosen.get(ficha_id)
        if item is not None:
            item.peso += peso
            if motivo not in item.motivos:
                item.motivos.append(motivo)
            continue
        ficha = fichas.get(ficha_id)
        if ficha is None or peso < 1.0 or not _allowed(ficha, action):
            continue
        if ficha.generos and not (
            (genre.strip() and _genre_matches(ficha, genre))
            or (instruction.strip() and _genre_matches(ficha, instruction))
        ):
            continue
        add(ficha, motivo, peso)

    ranked = sorted(chosen.values(), key=lambda item: (-item.peso, item.ficha.id))
    selected = ranked[:limit]
    left_out = [item for item in ranked[limit:] if item.problema]
    selected.extend(left_out[:MAX_PROBLEMAS_EXTRA])
    _attach_limits(selected, fichas, action)
    return selected


def _attach_limits(selected: list[SelectedFicha], fichas: dict[str, Ficha], action: str) -> None:
    """Las prioridades cuentan aunque la otra ficha no se haya elegido.

    Si una ficha ausente prevalece sobre una elegida, o choca con ella, su regla viaja
    como límite de la elegida, sin ocupar plaza.
    """
    ids = {item.ficha.id for item in selected}
    for item in selected:
        item.limites = []
        for other in fichas.values():
            if other.id in ids or not _allowed(other, action):
                continue
            for relacion in other.relaciones:
                if relacion.ficha != item.ficha.id or relacion.tipo == "requiere":
                    continue
                verbo = "prevalece sobre esta" if relacion.tipo == "prioridad_sobre" else "choca con esta"
                criterio = f" Criterio: {relacion.criterio}" if relacion.criterio else ""
                item.limites.append(f"«{other.nombre}» {verbo}: {other.regla}{criterio}")
        for relacion in item.ficha.relaciones:
            other = fichas.get(relacion.ficha)
            if relacion.tipo != "conflicto_con" or other is None or other.id in ids:
                continue
            criterio = f" Criterio: {relacion.criterio}" if relacion.criterio else ""
            item.limites.append(f"Choca con «{other.nombre}»: {other.regla}{criterio}")


def _priorities(selected: list[SelectedFicha]) -> list[str]:
    ids = {item.ficha.id for item in selected}
    names = {item.ficha.id: item.ficha.nombre for item in selected}
    lines: list[str] = []
    seen: set[frozenset[str]] = set()
    for item in selected:
        for relacion in item.ficha.relaciones:
            if relacion.tipo == "requiere" or relacion.ficha not in ids:
                continue
            key = frozenset({item.ficha.id, relacion.ficha, relacion.tipo})
            if key in seen:
                continue
            seen.add(key)
            verbo = "prevalece sobre" if relacion.tipo == "prioridad_sobre" else "choca con"
            criterio = f": {relacion.criterio}" if relacion.criterio else ""
            lines.append(f"- «{item.ficha.nombre}» {verbo} «{names[relacion.ficha]}»{criterio}")
    return lines


def oficio_block(selected: list[SelectedFicha]) -> str:
    if not selected:
        return ""
    parts = [
        (
            "Fichas de oficio para este texto. Aplícalas como criterio de editor; no las cites "
            "ni menciones en la salida. Si una no encaja en un caso concreto, manda su «No aplica»."
        ),
    ]
    for item in selected:
        ficha = item.ficha
        ejemplo = ficha.ejemplos[0]
        lines = [
            f"\n## {ficha.nombre} ({'; '.join(item.motivos)})",
            f"Regla: {ficha.regla}",
            f"Aplica: {ficha.aplica}",
            f"No aplica: {ficha.no_aplica}",
            f"Ejemplo: mal «{ejemplo.mal}» → bien «{ejemplo.bien}». {ejemplo.porque}",
        ]
        if item.fragmentos:
            lines.append("En este texto: " + " | ".join(f"«{fragment}»" for fragment in item.fragmentos))
        for limite in item.limites:
            lines.append(f"Límite: {limite}")
        parts.append("\n".join(lines))
    priorities = _priorities(selected)
    parts.append(
        "\nPrioridades entre estas fichas:\n"
        + ("\n".join(priorities) + "\n" if priorities else "")
        + f"- {PRIORIDAD_GENERAL}"
    )
    return "\n".join(parts)
