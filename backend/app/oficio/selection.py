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

MAX_FICHAS = 10
MAX_FRAGMENTOS = 2
LONG_SENTENCE_WORDS = 45
REPETITION_WINDOW = 12
REPETITION_MIN_LETTERS = 6

# Acciones que trabajan ideas y bloques: las fichas de norma solo distraen.
ACCIONES_SIN_NORMA = {"review"}
# Corregir solo atiende norma.
ACCIONES_SOLO_NORMA = {"correction"}
ACCION_EQUIVALENTE = {"continue": "rewrite", "variants": "rewrite"}

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


def _signal_hits(ficha: Ficha, text: str) -> list[str]:
    """Busca cada señal en el texto tal cual y sin tildes (borradores escritos deprisa)."""
    hits: list[str] = []
    seen: set[int] = set()
    plain_text = _strip_accents(text)
    for senal in ficha.senales:
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


METRIC_FUNCTIONS = {
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


def select_fichas(
    text: str,
    action: str,
    intention: str = "comprension",
    genre: str = "",
    limit: int = MAX_FICHAS,
) -> list[SelectedFicha]:
    action = ACCION_EQUIVALENTE.get(action, action)
    fichas = load_fichas()
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
        if genre_specific and genre.strip() and not genre_ok:
            continue

        hits = _signal_hits(ficha, text)
        for metric in ficha.metricas:
            hits.extend(METRIC_FUNCTIONS[metric](text))
        if hits:
            add(ficha, "señal en el texto", 3.0 + min(len(hits), 3), hits)
        if action in ficha.base.acciones:
            add(ficha, "base de la acción", 4.0)
        if intention in ficha.base.miradas and action != "review":
            add(ficha, f"mirada «{intention}»", 2.5)
        # Las fichas con señales necesitan verlas en el texto; el género solo filtra.
        if genre_ok and (not ficha.senales or hits):
            add(ficha, "tipo de texto declarado", 4.5)

    # Relaciones «requiere»: entra la ficha requerida, con menos peso que quien la pide.
    required_by: dict[str, int] = {}
    for item in list(chosen.values()):
        for relacion in item.ficha.relaciones:
            target = fichas[relacion.ficha]
            if relacion.tipo == "requiere" and _allowed(target, action):
                required_by[target.id] = required_by.get(target.id, 0) + 1
    for target_id, count in required_by.items():
        motivo = "la requiere otra ficha" if count == 1 else f"la requieren {count} fichas"
        add(fichas[target_id], motivo, 1.0 * count)

    ranked = sorted(chosen.values(), key=lambda item: (-item.peso, item.ficha.id))
    return ranked[:limit]


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
        parts.append("\n".join(lines))
    priorities = _priorities(selected)
    parts.append(
        "\nPrioridades entre estas fichas:\n"
        + ("\n".join(priorities) + "\n" if priorities else "")
        + f"- {PRIORIDAD_GENERAL}"
    )
    return "\n".join(parts)
