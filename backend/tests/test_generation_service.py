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


def test_deterministic_rewrite_fixes_obvious_community_notice_errors():
    text = (
        "Buenos días.\n\n"
        "Les recuerdo en incidente del ruido que generó hace poco por la perdida de agua del "
        "mismo y que los motores siguieran encendidos.\n\n"
        "En esta ocasión comenta qué:\n\n"
        "1º hay que sustituir unas válvulas que no funcionan y cortar el agua fria.\n\n"
        "4º que no hay linea de vida, que hay gancho pero no linea de vida.\n\n"
        "Dado que desconozco el corte de Todo esto, entiendo que habrá que saber cual es "
        "el coste total, cuanto cubre el mantenimiento y cuanto dinero extra hay que poner.\n\n"
        "Roberto díaz 5g\n"
        "Avenida constitucion 119"
    )

    result = service.rewrite_deterministic(
        GenerationInput(
            text=text,
            action="rewrite",
            context="general",
            revision_intention="estructura",
            intensity=1000,
        ),
        [],
    )

    assert result.output != text.strip()
    assert "Les recuerdo el incidente" in result.output
    assert "pérdida de agua" in result.output
    assert "comenta que:" in result.output
    assert "agua fría" in result.output
    assert "línea de vida" in result.output
    assert "desconozco el coste de todo esto" in result.output
    assert "saber cuál es" in result.output
    assert "cuánto cubre" in result.output
    assert "cuánto dinero" in result.output
    assert "Roberto Díaz" in result.output
    assert "Avenida Constitución" in result.output


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


def test_correction_uses_local_path_even_when_openai_is_configured(monkeypatch):
    class FailingOpenAI:
        def __init__(self):
            raise AssertionError("Correction must not initialize OpenAI")

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(service, "OpenAI", FailingOpenAI)

    result = service.rewrite_with_profile(
        GenerationInput(
            text=" hola ,mundo. esto funciona ? si ! ",
            action="correction",
            context="general",
        ),
        [],
    )

    assert result.output == "Hola, mundo. ¿Esto funciona? ¡Si!"
    assert result.provider == "deterministic"
    assert "Correccion local segura" in result.explanation


def test_openai_noop_uses_local_safe_correction_when_available(monkeypatch):
    class NoopResponses:
        def __init__(self, output: str):
            self.output = output

        def create(self, **kwargs):
            class Response:
                pass

            response = Response()
            response.output_text = self.output
            return response

    class NoopOpenAI:
        def __init__(self):
            self.responses = NoopResponses(
                "Les recuerdo en incidente del ruido por la perdida de agua y el agua fria."
            )

    original = "Les recuerdo en incidente del ruido por la perdida de agua y el agua fria."

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(service, "OpenAI", NoopOpenAI)

    result = service.rewrite_with_profile(
        GenerationInput(
            text=original,
            action="rewrite",
            context="general",
            intensity=500,
            revision_intention="tono",
        ),
        [],
    )

    assert result.output != original
    assert "Les recuerdo el incidente" in result.output
    assert "pérdida de agua" in result.output
    assert "agua fría" in result.output
    assert "no anadio cambios" in result.explanation
    assert result.provider == "openai"


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

    assert "mejorar claridad de forma suave" in captured["input"]
    assert "Conserva hechos, sujetos, matices" in captured["input"]
    assert "Mirada: voz y tono" in captured["input"]


def test_openai_prompt_allows_decided_rewrite_at_high_intensity(monkeypatch):
    captured: dict[str, str] = {}

    class CapturingResponses:
        def create(self, **kwargs):
            captured["input"] = kwargs["input"]

            class Response:
                output_text = (
                    "La democracia resolvio un problema antiguo: impedir que una sola persona "
                    "gobernara por capricho y permitir su sustitucion sin violencia."
                )

            return Response()

    class CapturingOpenAI:
        def __init__(self):
            self.responses = CapturingResponses()

    original = (
        "La democracia resolvio uno de los problemas politicos mas antiguos: como impedir "
        "que una sola persona gobernara por su voluntad y como sustituirla sin recurrir "
        "a la violencia."
    )

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(service, "OpenAI", CapturingOpenAI)

    result = service.rewrite_with_profile(
        GenerationInput(
            text=original,
            action="rewrite",
            context="general",
            intensity=1000,
            revision_intention="claridad",
        ),
        [],
    )

    assert result.output != original
    assert "reescritura decidida pero fiel" in captured["input"]
    assert "Puedes compactar, reordenar" in captured["input"]


def test_openai_prompt_allows_sendable_redraft_for_high_intensity_structure(monkeypatch):
    captured: dict[str, str] = {}

    class CapturingResponses:
        def create(self, **kwargs):
            captured["input"] = kwargs["input"]

            class Response:
                output_text = "Buenos dias:\n\nTexto ordenado para enviar."

            return Response()

    class CapturingOpenAI:
        def __init__(self):
            self.responses = CapturingResponses()

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(service, "OpenAI", CapturingOpenAI)

    service.rewrite_with_profile(
        GenerationInput(
            text="Buenos dias. el tecnico dice: 1 hay que arreglar valvulas 2 avisar comunidad",
            action="rewrite",
            context="general",
            intensity=1000,
            revision_intention="estructura",
        ),
        [],
    )

    assert "nota, correo, aviso o lista de puntos" in captured["input"]
    assert "version final clara y enviable" in captured["input"]
    assert "comunicacion final clara y enviable" in captured["input"]


def test_openai_prompt_defines_sendable_action(monkeypatch):
    captured: dict[str, object] = {}

    class CapturingResponses:
        def create(self, **kwargs):
            captured.update(kwargs)

            class Response:
                output_text = "Buenos dias:\n\nTexto listo para enviar.\n\nUn saludo."

            return Response()

    class CapturingOpenAI:
        def __init__(self):
            self.responses = CapturingResponses()

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(service, "OpenAI", CapturingOpenAI)

    service.rewrite_with_profile(
        GenerationInput(
            text="tecnico dice valvulas agua fria ruido coste comunidad",
            action="sendable",
            context="general",
            intensity=1000,
            revision_intention="estructura",
        ),
        [],
    )

    prompt = str(captured["input"])
    assert "texto final listo para enviar" in prompt
    assert "Formula las dudas como dudas" in prompt
    assert "No inventes costes, causas" in prompt
    assert captured["max_output_tokens"] >= 520


def test_high_intensity_structure_accepts_sendable_redraft(monkeypatch):
    class SendableResponses:
        def create(self, **kwargs):
            class Response:
                output_text = (
                    "Buenos dias:\n\n"
                    "Acaba de pasar el tecnico encargado del acumulador de agua caliente "
                    "situado en la cubierta.\n\n"
                    "Les recuerdo el incidente ocurrido recientemente, cuando se produjo "
                    "una perdida de agua o de fluido y las bombas continuaron funcionando, "
                    "generando un ruido considerable.\n\n"
                    "En esta ocasion, el tecnico me ha indicado que es necesario sustituir "
                    "varias valvulas, cortar temporalmente el suministro de agua fria y "
                    "avisar previamente a la comunidad. Tambien ha senalado que debe "
                    "reponerse el fluido del circuito y que el ruido podria repetirse si "
                    "no se localiza la causa de la perdida.\n\n"
                    "Por ultimo, ha indicado que en la zona de trabajo no existe linea de vida, "
                    "aunque si hay algun punto de anclaje.\n\n"
                    "Dado que desconozco el alcance y el coste de estas actuaciones, entiendo "
                    "que convendria solicitar un presupuesto detallado antes de autorizar los "
                    "trabajos.\n\n"
                    "Un saludo,\n\n"
                    "Roberto Diaz"
                )

            return Response()

    class SendableOpenAI:
        def __init__(self):
            self.responses = SendableResponses()

    original = (
        "Buenos dias. Acaba de pasar el tecnico del acumulador de agua caliente. "
        "Les recuerdo en incidente del ruido por perdida de agua y motores encendidos. "
        "Dice que hay que sustituir valvulas, cortar agua fria, rellenar fluido y que "
        "el ruido puede volver. Tambien dice que no hay linea de vida. "
        "Dado que desconozco el coste, habra que saber cuanto cubre mantenimiento. "
        "Roberto Diaz"
    )

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(service, "OpenAI", SendableOpenAI)

    result = service.rewrite_with_profile(
        GenerationInput(
            text=original,
            action="rewrite",
            context="general",
            intensity=1000,
            revision_intention="estructura",
        ),
        [],
    )

    assert result.output != original
    assert "Buenos dias:" in result.output
    assert "presupuesto detallado" in result.output
    assert "cambiaba demasiado" not in result.explanation
    assert result.provider == "openai"


def test_sendable_action_accepts_ordered_email_from_notes(monkeypatch):
    class SendableResponses:
        def create(self, **kwargs):
            class Response:
                output_text = (
                    "Buenos dias:\n\n"
                    "Acaba de pasar el tecnico encargado del acumulador de agua caliente "
                    "situado en la cubierta.\n\n"
                    "Segun me ha indicado, es necesario sustituir varias valvulas, cortar "
                    "temporalmente el agua fria y avisar previamente a la comunidad.\n\n"
                    "Tambien convendria aclarar el coste total, que parte cubre el contrato "
                    "de mantenimiento y que importe adicional tendria que asumir la comunidad.\n\n"
                    "Un saludo,\n\n"
                    "Roberto Diaz"
                )

            return Response()

    class SendableOpenAI:
        def __init__(self):
            self.responses = SendableResponses()

    original = (
        "Buenos dias tecnico acumulador cubierta valvulas agua fria avisar comunidad "
        "coste mantenimiento dinero extra Roberto Diaz"
    )

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(service, "OpenAI", SendableOpenAI)

    result = service.rewrite_with_profile(
        GenerationInput(
            text=original,
            action="sendable",
            context="general",
            intensity=1000,
            revision_intention="estructura",
        ),
        [],
    )

    assert "Buenos dias:" in result.output
    assert "agua fria" in result.output
    assert "mantenimiento" in result.output
    assert "Roberto Diaz" in result.output
    assert "cambiaba demasiado" not in result.explanation
    assert result.provider == "openai"


def test_sendable_action_allows_real_transformation_from_rough_notes(monkeypatch):
    class SendableResponses:
        def create(self, **kwargs):
            class Response:
                output_text = (
                    "Buenos días:\n\n"
                    "Acaba de pasar el técnico encargado del acumulador de agua caliente "
                    "situado en la cubierta.\n\n"
                    "Según me ha indicado, es necesario sustituir varias válvulas, cortar "
                    "temporalmente el suministro de agua fría, avisar previamente a la comunidad "
                    "e indicar mediante carteles la fecha y el horario del corte.\n\n"
                    "También ha señalado que debe reponerse el fluido del circuito y que el ruido "
                    "podría repetirse si no se localiza la causa de la pérdida.\n\n"
                    "Dado que desconozco el alcance y el coste de estas actuaciones, entiendo que "
                    "convendría solicitar un presupuesto detallado antes de autorizar los trabajos.\n\n"
                    "Un saludo,\n\n"
                    "Roberto Díaz"
                )

            return Response()

    class SendableOpenAI:
        def __init__(self):
            self.responses = SendableResponses()

    original = (
        "tecnico acumulador cubierta ruido perdida motores valvulas cortar agua fria "
        "carteles comunidad fluido placas coste mantenimiento Roberto Diaz"
    )

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(service, "OpenAI", SendableOpenAI)

    result = service.rewrite_with_profile(
        GenerationInput(
            text=original,
            action="sendable",
            context="general",
            intensity=1000,
            revision_intention="estructura",
        ),
        [],
    )

    assert "Buenos días:" in result.output
    assert "presupuesto detallado" in result.output
    assert "Roberto Díaz" in result.output
    assert "cambiaba demasiado" not in result.explanation
    assert result.provider == "openai"


def test_high_intensity_rewrite_allows_substantial_clarity_change(monkeypatch):
    class ClarityResponses:
        def create(self, **kwargs):
            class Response:
                output_text = (
                    "La escena de Guerra Mundial Z no es pura ficción. En realidad existe "
                    "una unidad llamada Makhleket HaBakara dentro de la Dirección de Inteligencia "
                    "Militar israelí, Aman. Su función es evaluar críticamente los supuestos "
                    "de inteligencia y explorar escenarios improbables."
                )

            return Response()

    class ClarityOpenAI:
        def __init__(self):
            self.responses = ClarityResponses()

    original = (
        "La escena de Guerra Mundial Z no es pura ficción. Existe realmente una unidad conocida "
        "como Makhleket HaBakara dentro de la Dirección de Inteligencia Militar israelí (Aman), "
        "cuya función es evaluar críticamente los supuestos de inteligencia, examinar escenarios "
        "improbables y proponer evaluaciones adversariales."
    )

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(service, "OpenAI", ClarityOpenAI)

    result = service.rewrite_with_profile(
        GenerationInput(
            text=original,
            action="rewrite",
            context="general",
            intensity=1000,
            revision_intention="claridad",
        ),
        [],
    )

    assert result.output != original
    assert "Makhleket HaBakara" in result.output
    assert "Aman" in result.output
    assert "cambiaba demasiado" not in result.explanation
    assert result.provider == "openai"


def test_openai_request_uses_latency_controls(monkeypatch):
    captured: dict[str, object] = {}

    class CapturingResponses:
        def create(self, **kwargs):
            captured.update(kwargs)

            class Response:
                output_text = "Texto claro."

            return Response()

    class CapturingOpenAI:
        def __init__(self):
            self.responses = CapturingResponses()

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_TIMEOUT_SECONDS", "9")
    monkeypatch.setattr(service, "OpenAI", CapturingOpenAI)

    service.rewrite_with_profile(
        GenerationInput(
            text="Texto claro.",
            action="rewrite",
            context="general",
            intensity=500,
        ),
        [],
    )

    assert captured["max_output_tokens"] >= 220
    assert captured["reasoning"] == {"effort": "minimal"}
    assert captured["store"] is False
    assert captured["timeout"] == 9.0
