from datetime import UTC, datetime

from app.core.models import GenerationInput, ScoreVariable
from app.generation import service
from app.generation.service import _protect_terms, _restore_terms


def test_protected_terms_ignore_partial_words():
    protected, replacements = _protect_terms("martes mar", ["mar"])

    assert "martes" in protected
    assert "mar" not in protected.split()[-1]
    assert _restore_terms(protected, replacements) == "martes mar"


def test_protected_terms_preserve_original_casing():
    protected, replacements = _protect_terms("La Mayoría decide.", ["mayoría"])

    assert "Mayoría" not in protected
    assert _restore_terms(protected, replacements) == "La Mayoría decide."


def test_openai_failure_falls_back_to_deterministic_generation(monkeypatch):
    class FailingResponses:
        def create(self, **kwargs):
            raise RuntimeError("rate limit")

    class FailingOpenAI:
        def __init__(self):
            self.responses = FailingResponses()

    variable = ScoreVariable(
        key="dinamismo",
        label="Dinamismo",
        category="tono",
        calculated_value=500,
        manual_adjustment=0,
        confidence=0.5,
        context="general",
        evidence_count=0,
        updated_at=datetime.now(UTC),
    )

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(service, "OpenAI", FailingOpenAI)

    result = service.rewrite_with_profile(
        GenerationInput(
            text="Primera frase. Segunda frase. Tercera frase. Cuarta frase.",
            action="rewrite",
            context="general",
        ),
        [variable],
    )

    assert result.provider == "deterministic"
    assert result.learning_applied is False
    assert "No se pudo completar la generacion externa" in result.explanation
    assert "Reescritura estructural local" in result.explanation
    assert "\n\n" in result.output
