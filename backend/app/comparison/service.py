from difflib import SequenceMatcher

from app.core.models import ComparisonInput, ComparisonResult
from app.core.text import canonical_text, words


def _paragraph_count(value: str) -> int:
    return len([block for block in value.splitlines() if block.strip()])


def compare_texts(payload: ComparisonInput) -> ComparisonResult:
    original_words = words(payload.original)
    revised_words = words(payload.revised)
    original_set = set(original_words)
    revised_set = set(revised_words)

    changed = len(original_set.symmetric_difference(revised_set))
    denominator = max(1, len(original_set.union(revised_set)))
    lexical_delta = min(1000, round((changed / denominator) * 1000))

    word_sequence_delta = round(
        (1 - SequenceMatcher(None, original_words, revised_words).ratio()) * 1000
    )
    text_shape_delta = round(
        (
            1
            - SequenceMatcher(
                None,
                canonical_text(payload.original),
                canonical_text(payload.revised),
            ).ratio()
        )
        * 1000
    )
    paragraph_delta = 0
    original_paragraphs = _paragraph_count(payload.original)
    revised_paragraphs = _paragraph_count(payload.revised)
    if original_paragraphs != revised_paragraphs:
        paragraph_delta = min(
            260,
            120 + abs(original_paragraphs - revised_paragraphs) * 45,
        )

    modification = min(
        1000,
        max(lexical_delta, word_sequence_delta, text_shape_delta, paragraph_delta),
    )

    length_delta = abs(len(revised_words) - len(original_words))
    stability = max(0, 1000 - round((length_delta / max(1, len(original_words))) * 1000))
    adequacy = round((stability + (1000 - modification // 2)) / 2)

    if modification < 250:
        summary = "Cambios leves: conserva gran parte de la formulacion original."
    elif modification < 650:
        summary = "Cambios medios: reescritura visible con continuidad reconocible."
    else:
        summary = "Cambios altos: conviene revisar si respeta la intencion inicial."

    lexical_dimension = min(1000, round((changed / max(1, len(original_words))) * 1000))
    length_change = min(1000, round((length_delta / max(1, len(original_words))) * 1000))
    structure_change = max(paragraph_delta, word_sequence_delta // 2, 80)
    tone_change = min(1000, lexical_dimension // 2 + length_change // 3 + text_shape_delta // 4)

    matcher = SequenceMatcher(None, original_words, revised_words)
    changes = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        changes.append(
            {
                "type": tag,
                "original": " ".join(original_words[i1:i2]),
                "revised": " ".join(revised_words[j1:j2]),
            }
        )

    return ComparisonResult(
        modification_score=modification,
        adequacy_score=max(0, min(1000, adequacy)),
        changed_words=changed,
        original_words=len(original_words),
        revised_words=len(revised_words),
        summary=summary,
        dimensions={
            "lexico": lexical_dimension,
            "longitud": length_change,
            "estructura": structure_change,
            "tono": tone_change,
        },
        changes=changes[:12],
    )
