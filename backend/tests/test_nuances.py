from app.comparison.nuances import lost_nuances
from app.comparison.service import compare_texts
from app.core.models import ComparisonInput


def _markers(original: str, revised: str) -> list[str]:
    return [finding["marker"].lower() for finding in lost_nuances(original, revised)]


def test_flags_lost_certainty_markers():
    original = "En esas condiciones, muchas personas no cambian necesariamente de opinión."
    revised = "En esas condiciones, muchos no cambian de opinión."
    assert _markers(original, revised) == ["necesariamente"]


def test_flags_lost_quantifier_and_frequency():
    original = (
        "Podría aparecer como una opinión compartida por casi todos. "
        "A menudo está formada por ciudadanos normales."
    )
    revised = "Aparece como una opinión general. Son ciudadanos normales."
    markers = _markers(original, revised)
    assert "casi" in markers
    assert "a menudo" in markers
    assert "podría" in markers


def test_flags_lost_analogy_and_connector():
    original = (
        "Haber sido elegido no lo convierte en justo, del mismo modo que un procedimiento "
        "correcto no garantiza un buen resultado. Sin embargo, existe una tendencia."
    )
    revised = (
        "Haber sido elegido no lo convierte en justo; tampoco garantiza un buen resultado. "
        "Hay una tendencia."
    )
    findings = lost_nuances(original, revised)
    categories = {finding["marker"].lower(): finding["category"] for finding in findings}
    assert categories["del mismo modo"] == "Conector o analogía"
    assert categories["sin embargo"] == "Conector o analogía"


def test_flags_lost_chronology():
    original = "No demuestra la calidad de cada decisión adoptada después."
    revised = "No demuestra la calidad de cada decisión."
    assert _markers(original, revised) == ["después"]


def test_flags_truncated_enumeration():
    original = "Nadie se ve como parte de una fuerza que excluye, consiente o permite."
    revised = "Nadie se ve como parte de una fuerza que excluye."
    findings = lost_nuances(original, revised)
    assert len(findings) == 1
    assert findings[0]["category"] == "Enumeración"
    assert findings[0]["marker"] == "consiente, permite"


def test_equivalent_substitution_is_not_flagged():
    original = "No se habla únicamente de ruido. Los niños todavía no dominan las normas."
    revised = "No se habla solo de ruido. Los niños aún no dominan las normas."
    assert lost_nuances(original, revised) == []


def test_filler_intensifiers_are_not_flagged():
    original = "Es un problema mucho más difícil y realmente muy antiguo."
    revised = "Es un problema más difícil y antiguo."
    assert lost_nuances(original, revised) == []


def test_identical_text_has_no_findings():
    text = "Quizá ese sea el verdadero riesgo, aunque casi nadie lo vea."
    assert lost_nuances(text, text) == []


def test_marker_moved_within_text_is_not_flagged():
    original = "Siempre llega tarde a la reunión."
    revised = "Llega tarde a la reunión, siempre."
    assert lost_nuances(original, revised) == []


def test_findings_include_original_context():
    original = "La mayoría silenciosa no está formada por cobardes. A menudo la forman ciudadanos normales que trabajan."
    revised = "La mayoría silenciosa no está formada por cobardes. La forman ciudadanos normales que trabajan."
    findings = lost_nuances(original, revised)
    assert findings[0]["context"].count("A menudo") == 1


def test_comparison_result_carries_lost_nuances():
    result = compare_texts(
        ComparisonInput(
            original="El poder no se impondría siempre mediante la fuerza.",
            revised="El poder no se impondría mediante la fuerza.",
        )
    )
    assert [finding["marker"] for finding in result.lost_nuances] == ["siempre"]
