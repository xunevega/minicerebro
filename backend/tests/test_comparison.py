from app.comparison.service import compare_texts
from app.core.models import ComparisonInput


def test_compare_texts_returns_bounded_scores():
    result = compare_texts(
        ComparisonInput(original="Texto breve y claro.", revised="Texto breve, claro y mas preciso.")
    )

    assert 0 <= result.modification_score <= 1000
    assert 0 <= result.adequacy_score <= 1000
    assert result.changed_words > 0


def test_compare_texts_detects_reordered_same_words():
    result = compare_texts(
        ComparisonInput(
            original="La decision explica el origen del poder.",
            revised="El origen del poder explica la decision.",
        )
    )

    assert result.changed_words == 0
    assert result.modification_score > 0
    assert result.dimensions["estructura"] > 0


def test_compare_texts_detects_paragraph_structure_changes():
    result = compare_texts(
        ComparisonInput(
            original="Primera idea. Segunda idea.",
            revised="Primera idea.\n\nSegunda idea.",
        )
    )

    assert result.changed_words == 0
    assert result.modification_score > 0
    assert result.dimensions["estructura"] >= 120


def test_compare_texts_names_minimal_intervention():
    result = compare_texts(
        ComparisonInput(
            original="La mañana era clara y el texto seguia intacto.",
            revised="La mañana era clara y el texto seguía intacto.",
        )
    )

    assert result.modification_score <= 20
    assert "Intervencion minima" in result.summary
