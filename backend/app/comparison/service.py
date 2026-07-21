from difflib import SequenceMatcher

from app.core.models import ComparisonInput, ComparisonResult
from app.core.text import words


def compare_texts(payload: ComparisonInput) -> ComparisonResult:
    original_words = words(payload.original)
    revised_words = words(payload.revised)
    original_set = set(original_words)
    revised_set = set(revised_words)

    changed = len(original_set.symmetric_difference(revised_set))
    denominator = max(1, len(original_set.union(revised_set)))
    modification = min(1000, round((changed / denominator) * 1000))

    length_delta = abs(len(revised_words) - len(original_words))
    stability = max(0, 1000 - round((length_delta / max(1, len(original_words))) * 1000))
    adequacy = round((stability + (1000 - modification // 2)) / 2)

    if modification < 250:
        summary = "Cambios leves: conserva gran parte de la formulacion original."
    elif modification < 650:
        summary = "Cambios medios: reescritura visible con continuidad reconocible."
    else:
        summary = "Cambios altos: conviene revisar si respeta la intencion inicial."

    lexical_delta = min(1000, round((changed / max(1, len(original_words))) * 1000))
    length_change = min(1000, round((length_delta / max(1, len(original_words))) * 1000))
    structure_change = 180 if "\n" in payload.original or "\n" in payload.revised else 80
    tone_change = min(1000, lexical_delta // 2 + length_change // 3)

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
            "lexico": lexical_delta,
            "longitud": length_change,
            "estructura": structure_change,
            "tono": tone_change,
        },
        changes=changes[:12],
    )
