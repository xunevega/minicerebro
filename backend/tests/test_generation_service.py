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


def test_deterministic_correction_fixes_safe_surface_errors():
    result = service.rewrite_deterministic(
        GenerationInput(
            text=" hola ,mundo. esto funciona ? si ! ",
            action="correction",
            context="general",
        ),
        [],
    )

    assert result.output == "Hola, mundo. ¿Esto funciona? ¡Si!"
    assert "Correccion local segura" in result.explanation
    assert result.learning_applied is False


def test_deterministic_correction_preserves_protected_terms():
    result = service.rewrite_deterministic(
        GenerationInput(
            text="la Mayoría , decide?",
            action="correction",
            context="general",
            protected_terms=["Mayoría"],
        ),
        [],
    )

    assert "Mayoría" in result.output
    assert result.output == "¿La Mayoría, decide?"


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


def test_openai_rewrite_rejects_over_aggressive_clarity_change(monkeypatch):
    class AggressiveResponses:
        def create(self, **kwargs):
            class Response:
                output_text = (
                    "El sindicato anuncio una ofensiva directa contra la direccion de RTVE "
                    "y exigio responsabilidades por el deterioro institucional."
                )

            return Response()

    class AggressiveOpenAI:
        def __init__(self):
            self.responses = AggressiveResponses()

    original = (
        "A finales de la semana pasada, la seccion sindical de CGT en RTVE decidio "
        "convocar estos paros ante la deriva que, a su juicio, ha tomado la corporacion."
    )

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(service, "OpenAI", AggressiveOpenAI)

    result = service.rewrite_with_profile(
        GenerationInput(
            text=original,
            action="rewrite",
            context="general",
            intensity=500,
            revision_intention="claridad",
        ),
        [],
    )

    assert result.output == original
    assert "cambiaba demasiado" in result.explanation
    assert result.learning_applied is False


def test_openai_prompt_includes_conservative_rewrite_and_revision_lens(monkeypatch):
    captured: dict[str, str] = {}

    class CapturingResponses:
        def create(self, **kwargs):
            captured["input"] = kwargs["input"]

            class Response:
                output_text = "Texto claro."

            return Response()

    class CapturingOpenAI:
        def __init__(self):
            self.responses = CapturingResponses()

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(service, "OpenAI", CapturingOpenAI)

    service.rewrite_with_profile(
        GenerationInput(
            text="Texto claro.",
            action="rewrite",
            context="general",
            intensity=500,
            revision_intention="tono",
        ),
        [],
    )

    assert "mejorar claridad de forma conservadora" in captured["input"]
    assert "Conserva hechos, sujetos, matices" in captured["input"]
    assert "Mirada: voz y tono" in captured["input"]
