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

    return ComparisonResult(
        modification_score=modification,
        adequacy_score=max(0, min(1000, adequacy)),
        changed_words=changed,
        original_words=len(original_words),
        revised_words=len(revised_words),
        summary=summary,
    )

