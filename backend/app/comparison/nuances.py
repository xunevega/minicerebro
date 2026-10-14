"""Matices que una propuesta hace desaparecer (docs/CRITERIO_EDITORIAL.md).

Compara el original con la propuesta y señala modalizadores, marcas de
cronología, conectores y miembros de enumeraciones que estaban en el original y faltan en la propuesta.
No bloquea nada: marca, y el escritor decide si era relleno o sentido.
"""

from difflib import SequenceMatcher
import re
import unicodedata

TOKEN_RE = re.compile(r"[\wáéíóúüñÁÉÍÓÚÜÑ]+", re.UNICODE)

CERTAINTY = "Grado de certeza"
CHRONOLOGY = "Cronología"
CONNECTOR = "Conector o analogía"
ENUMERATION = "Enumeración"

# Marcadores protegidos, en forma canónica (minúsculas, sin tildes). Cada tupla
# es un grupo de equivalentes: cambiar "únicamente" por "solo" no pierde nada,
# así que se cuenta por grupo. Quedan fuera los intensificadores que el
# criterio permite recortar como relleno ("muy", "realmente", "mucho").
PROTECTED_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (CERTAINTY, ("necesariamente", "forzosamente")),
    (CERTAINTY, ("siempre",)),
    (CERTAINTY, ("nunca", "jamas")),
    (CERTAINTY, ("casi",)),
    (CERTAINTY, ("a menudo", "frecuentemente", "con frecuencia")),
    (CERTAINTY, ("completamente", "por completo", "totalmente", "del todo", "plenamente")),
    (CERTAINTY, ("generalmente", "normalmente", "habitualmente", "por lo general", "en general")),
    (CERTAINTY, ("a veces", "en ocasiones", "a ratos")),
    (CERTAINTY, ("rara vez", "raramente", "pocas veces")),
    (CERTAINTY, ("apenas",)),
    (CERTAINTY, ("quiza", "quizas", "tal vez", "acaso")),
    (CERTAINTY, ("probablemente", "posiblemente", "seguramente", "aparentemente")),
    (CERTAINTY, ("en parte", "parcialmente")),
    (CERTAINTY, ("solo", "solamente", "unicamente", "exclusivamente")),
    (CERTAINTY, ("especialmente", "sobre todo", "en particular", "particularmente")),
    (CERTAINTY, ("razonablemente", "relativamente")),
    (CERTAINTY, ("puede", "pueden", "podia", "podian", "podria", "podrian", "pudiera", "pudieran")),
    (CERTAINTY, ("suele", "suelen", "solia", "solian")),
    (CHRONOLOGY, ("despues", "luego", "mas tarde", "posteriormente")),
    (CHRONOLOGY, ("antes", "previamente")),
    (CHRONOLOGY, ("todavia", "aun")),
    (CHRONOLOGY, ("al final", "finalmente")),
    (CONNECTOR, ("sin embargo", "no obstante")),
    (CONNECTOR, ("aunque",)),
    (CONNECTOR, ("pero",)),
    (CONNECTOR, ("sino",)),
    (CONNECTOR, ("en realidad", "de hecho")),
    (CONNECTOR, ("precisamente",)),
    (CONNECTOR, ("en cambio",)),
    (CONNECTOR, ("por tanto", "por lo tanto", "por consiguiente", "asi pues")),
    (CONNECTOR, ("del mismo modo", "de la misma manera", "al igual que", "igual que")),
    (CONNECTOR, ("a diferencia de",)),
    (CONNECTOR, ("es decir", "o sea")),
    (CONNECTOR, ("incluso",)),
    (CONNECTOR, ("tampoco",)),
)

ENUMERATION_RE = re.compile(
    r"\b([\wáéíóúüñ]+), ([\wáéíóúüñ]+),? (?:y|o|ni|e|u) ([\wáéíóúüñ]+)\b",
    re.IGNORECASE | re.UNICODE,
)
ENUMERATION_STOPWORDS = {"el", "la", "los", "las", "un", "una", "de", "que", "y", "o"}
CONTEXT_WORDS = 7
MAX_FINDINGS = 40


def _canon(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _tokens(value: str) -> list[tuple[str, int, int]]:
    return [(_canon(m.group()), m.start(), m.end()) for m in TOKEN_RE.finditer(value)]


def _find(seq: list[str], marker: tuple[str, ...]) -> list[int]:
    size = len(marker)
    return [i for i in range(len(seq) - size + 1) if tuple(seq[i : i + size]) == marker]


def _context(text: str, tokens: list[tuple[str, int, int]], start: int, end: int) -> str:
    first = tokens[max(0, start - CONTEXT_WORDS)][1]
    last = tokens[min(len(tokens) - 1, end + CONTEXT_WORDS - 1)][2]
    snippet = " ".join(text[first:last].split())
    prefix = "…" if start - CONTEXT_WORDS > 0 else ""
    suffix = "…" if end + CONTEXT_WORDS < len(tokens) else ""
    return f"{prefix}{snippet}{suffix}"


def _changed_positions(original: list[str], revised: list[str]) -> set[int]:
    changed: set[int] = set()
    for tag, i1, i2, _j1, _j2 in SequenceMatcher(None, original, revised, autojunk=False).get_opcodes():
        if tag != "equal":
            changed.update(range(i1, i2))
    return changed


def lost_nuances(original: str, revised: str) -> list[dict[str, str]]:
    original_tokens = _tokens(original)
    revised_tokens = _tokens(revised)
    original_words = [token[0] for token in original_tokens]
    revised_words = [token[0] for token in revised_tokens]
    changed = _changed_positions(original_words, revised_words)

    findings: list[tuple[int, dict[str, str]]] = []
    claimed: set[int] = set()

    for category, group in PROTECTED_GROUPS:
        members = sorted((tuple(item.split()) for item in group), key=len, reverse=True)

        def occurrences(seq: list[str], skip: set[int]) -> list[tuple[int, int]]:
            found: list[tuple[int, int]] = []
            taken: set[int] = set(skip)
            for member in members:
                for i in _find(seq, member):
                    span = set(range(i, i + len(member)))
                    if not span & taken:
                        taken |= span
                        found.append((i, len(member)))
            return sorted(found)

        original_hits = occurrences(original_words, claimed)
        lost_count = len(original_hits) - len(occurrences(revised_words, set()))
        if lost_count <= 0:
            continue
        # Las ocurrencias que quedan dentro de un tramo reescrito son las candidatas.
        candidates = [hit for hit in original_hits if changed.intersection(range(hit[0], hit[0] + hit[1]))]
        for i, size in candidates[:lost_count]:
            claimed.update(range(i, i + size))
            findings.append(
                (
                    i,
                    {
                        "category": category,
                        "marker": original[original_tokens[i][1] : original_tokens[i + size - 1][2]],
                        "context": _context(original, original_tokens, i, i + size),
                    },
                )
            )

    revised_vocabulary = set(revised_words)
    for match in ENUMERATION_RE.finditer(original):
        members = [match.group(n) for n in (1, 2, 3)]
        missing = [
            member for member in members
            if _canon(member) not in ENUMERATION_STOPWORDS and _canon(member) not in revised_vocabulary
        ]
        if not missing or len(missing) == len(members):
            # Si faltan todos, es una reformulación completa, no una enumeración recortada.
            continue
        start = next(i for i, token in enumerate(original_tokens) if token[1] >= match.start())
        end = next(i for i, token in enumerate(original_tokens) if token[2] >= match.end()) + 1
        findings.append(
            (
                start,
                {
                    "category": ENUMERATION,
                    "marker": ", ".join(missing),
                    "context": _context(original, original_tokens, start, end),
                },
            )
        )

    findings.sort(key=lambda item: item[0])
    return [finding for _position, finding in findings[:MAX_FINDINGS]]
