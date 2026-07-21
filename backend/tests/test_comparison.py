from app.comparison.service import compare_texts
from app.core.models import ComparisonInput


def test_compare_texts_returns_bounded_scores():
    result = compare_texts(
        ComparisonInput(original="Texto breve y claro.", revised="Texto breve, claro y mas preciso.")
    )

    assert 0 <= result.modification_score <= 1000
    assert 0 <= result.adequacy_score <= 1000
    assert result.changed_words > 0

