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


def test_openai_rewrite_rejects_fact_losing_clarity_change(monkeypatch):
    class FactLosingResponses:
        def create(self, **kwargs):
            class Response:
                output_text = (
                    "El sindicato anuncio una ofensiva directa contra la direccion de RTVE "
                    "y exigio responsabilidades por el deterioro institucional."
                )

            return Response()

    class FactLosingOpenAI:
        def __init__(self):
            self.responses = FactLosingResponses()

    original = (
        "A finales de la semana pasada, la seccion sindical de CGT en RTVE decidio "
        "convocar estos paros ante la deriva que, a su juicio, ha tomado la corporacion."
    )

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(service, "OpenAI", FactLosingOpenAI)

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
    assert "perdia datos importantes" in result.explanation
    assert result.learning_applied is False


def test_openai_rewrite_accepts_large_change_when_facts_remain(monkeypatch):
    class TransformingResponses:
        def create(self, **kwargs):
            class Response:
                output_text = (
                    "Buenos dias:\n\n"
                    "Acaba de pasar el tecnico del acumulador de agua caliente de la cubierta. "
                    "Segun ha indicado, habria que sustituir varias valvulas, cortar el agua fria "
                    "durante unas horas, avisar a la comunidad y colocar carteles con el horario.\n\n"
                    "Tambien ha explicado que debe reponerse el fluido del circuito entre las placas "
                    "y el acumulador, y que el episodio de ruido podria repetirse si continua la "
                    "perdida o la falta de presion.\n\n"
                    "Antes de autorizar los trabajos, convendria solicitar presupuesto detallado y "
                    "aclarar que parte cubre el mantenimiento y que importe tendria que asumir la "
                    "comunidad.\n\n"
                    "Un saludo,\nRoberto Diaz"
                )

            return Response()

    class TransformingOpenAI:
        def __init__(self):
            self.responses = TransformingResponses()

    original = (
        "tecnico acumulador agua caliente cubierta ruido perdida motores valvulas cortar agua fria "
        "carteles comunidad horas fluido placas acumulador pierde potencia agua coste mantenimiento "
        "dinero extra Roberto Diaz"
    )

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(service, "OpenAI", TransformingOpenAI)

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
    assert "acumulador" in result.output
    assert "mantenimiento" in result.output
    assert "Roberto Diaz" in result.output
    assert "perdia datos importantes" not in result.explanation
    assert result.provider == "openai"


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


def test_openai_prompt_includes_user_instruction_without_learning(monkeypatch):
    captured: dict[str, str] = {}

    class CapturingResponses:
        def create(self, **kwargs):
            captured["input"] = kwargs["input"]

            class Response:
                output_text = "Texto mas tecnico."

            return Response()

    class CapturingOpenAI:
        def __init__(self):
            self.responses = CapturingResponses()

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(service, "OpenAI", CapturingOpenAI)

    service.rewrite_with_profile(
        GenerationInput(
            text="Texto base.",
            action="rewrite",
            context="general",
            intensity=700,
            revision_intention="estructura",
            user_instruction="  mas tecnico y mas formal  ",
        ),
        [],
    )

    assert "Indicacion libre del usuario para esta salida: mas tecnico y mas formal" in captured["input"]
    assert "aplicala al angulo, tono, nivel tecnico o estructura" in captured["input"]
    assert "No la conviertas en dato nuevo ni en aprendizaje permanente" in captured["input"]
    assert "Esta accion es editar" in captured["input"]
    assert "editar la estructura del borrador" in captured["input"]
    assert "material de partida, no como arquitectura obligatoria" in captured["input"]
    assert "no en conservar el mismo orden" in captured["input"]


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
    assert "No confundas fidelidad con retoque minimo" in captured["input"]
    assert "reescritura grande puede" in captured["input"]
    assert "ser correcta" in captured["input"]
    assert "darle forma de texto" in captured["input"]
    assert "maquillarlo con correcciones pequenas" in captured["input"]


def test_openai_rewrite_treats_community_note_as_communicative_draft(monkeypatch):
    captured: dict[str, object] = {}

    class CapturingResponses:
        def create(self, **kwargs):
            captured.update(kwargs)

            class Response:
                output_text = (
                    "Buenos dias:\n\n"
                    "Acaba de pasar el tecnico encargado del acumulador de agua caliente."
                )

            return Response()

    class CapturingOpenAI:
        def __init__(self):
            self.responses = CapturingResponses()

    rough_note = (
        "Buenos dias.\n\n"
        "Acaba de pasar el tecnico del acumulador de agua caliente.\n\n"
        "1º hay que sustituir unas valvulas y avisar a la comunidad.\n"
        "2º hay que rellenar fluido.\n\n"
        "Dado que desconozco el coste, habra que pedir presupuesto."
    )

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(service, "OpenAI", CapturingOpenAI)

    service.rewrite_with_profile(
        GenerationInput(
            text=rough_note,
            action="rewrite",
            context="general",
            intensity=500,
            revision_intention="estructura",
        ),
        [],
    )

    assert "borrador comunicativo" in captured["input"]
    assert "version clara y lista para enviar" in captured["input"]
    assert "Esta accion es editar, no corregir" in captured["input"]
    assert "No te limites a comas, articulos, tildes" in captured["input"]
    assert "practicamente toda la redaccion" in captured["input"]
    assert "Puedes cambiar la estructura" in captured["input"]
    assert "mas tecnico, mas formal, menos formal" in captured["input"]
    assert captured["max_output_tokens"] >= 520


def test_medium_rewrite_prompt_does_not_equate_fidelity_with_small_edits(monkeypatch):
    captured: dict[str, str] = {}

    class CapturingResponses:
        def create(self, **kwargs):
            captured["input"] = kwargs["input"]

            class Response:
                output_text = "Texto reescrito con mejor orden."

            return Response()

    class CapturingOpenAI:
        def __init__(self):
            self.responses = CapturingResponses()

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(service, "OpenAI", CapturingOpenAI)

    service.rewrite_with_profile(
            GenerationInput(
                text="Bestiario de un alcoholico. Uno pasa procesos. Luego te excluyen y sigues mejor.",
                action="rewrite",
                context="general",
                intensity=700,
                revision_intention="estructura",
            ),
        [],
    )

    assert "no la reduzcas a" in captured["input"]
    assert "comas, articulos, sinonimos o retoques frase a frase" in captured["input"]
    assert "no como arquitectura obligatoria" in captured["input"]
    assert "Manten la estructura de parrafos" not in captured["input"]


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

    assert "borrador comunicativo" in captured["input"]
    assert "version clara y lista para enviar" in captured["input"]
    assert "No te limites a comas, articulos, tildes" in captured["input"]


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
    assert "Puedes precisar tecnicamente" in prompt
    assert "circuito, fluido, bombas, placas, acumulador" in prompt
    assert "No inventes costes, causas cerradas" in prompt
    assert "no me quedo claro" in prompt
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


def test_sendable_action_allows_near_total_redraft_from_uncertain_description(monkeypatch):
    class SendableResponses:
        def create(self, **kwargs):
            class Response:
                output_text = (
                    "Buenos días:\n\n"
                    "Acaba de pasar el técnico encargado del acumulador de agua caliente "
                    "situado en la cubierta.\n\n"
                    "Según me ha explicado, sería necesario sustituir varias válvulas y, para "
                    "realizar esos trabajos, cortar temporalmente el suministro de agua fría. "
                    "También habría que avisar previamente a la comunidad y colocar carteles con "
                    "la fecha y el horario del corte.\n\n"
                    "Además, me ha indicado que debe reponerse el fluido del circuito entre las "
                    "placas solares y el acumulador. No me quedó claro si la pérdida es de agua, "
                    "de fluido o de presión, por lo que convendría que la empresa aclarase la "
                    "causa exacta y confirmase cómo se evitará que vuelva a producirse el ruido "
                    "cuando las bombas continúan funcionando en esas condiciones.\n\n"
                    "Por último, señaló que en la zona donde debe trabajar no hay línea de vida, "
                    "aunque sí algún punto de anclaje. Agradecería que se comprobase este punto.\n\n"
                    "Antes de autorizar la reparación, entiendo que habría que solicitar un "
                    "presupuesto o informe detallado que indique qué parte cubre el mantenimiento "
                    "y qué importe adicional tendría que asumir la comunidad.\n\n"
                    "Un saludo,\n\n"
                    "Roberto Díaz"
                )

            return Response()

    class SendableOpenAI:
        def __init__(self):
            self.responses = SendableResponses()

    original = (
        "tecnico acumulador tejado ruido por perdida algo agua o fluido no se motores "
        "siguieron encendidos valvulas agua fria carteles vecinos placas lejos del acumulador "
        "fluido motor ruido volvera no hay linea vida gancho coste mantenimiento comunidad "
        "Roberto Diaz"
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

    assert result.output != original
    assert "Buenos días:" in result.output
    assert "fluido del circuito entre las placas solares y el acumulador" in result.output
    assert "No me quedó claro" in result.output
    assert "bombas continúan funcionando" in result.output
    assert "línea de vida" in result.output
    assert "mantenimiento" in result.output
    assert "Roberto Díaz" in result.output
    assert "perdia datos importantes" not in result.explanation
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
