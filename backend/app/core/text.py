import re
import unicodedata


WORD_RE = re.compile(r"\b[\wáéíóúüñÁÉÍÓÚÜÑ]+\b", re.UNICODE)


def canonical_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip().lower())
    without_marks = "".join(char for char in normalized if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", without_marks)


def words(value: str) -> list[str]:
    return WORD_RE.findall(canonical_text(value))


def clamp_score(value: int) -> int:
    return max(0, min(1000, value))

