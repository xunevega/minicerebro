from pathlib import Path

from app.core.models import GenerationInput
from app.generation import service
from app.oficio import load_fichas, oficio_block, select_fichas

ENSAYO = """El silencio de la mayoría
La democracia resolvió uno de los problemas políticos más antiguos. No resolvió, sin embargo, otro problema mucho más difícil.

Cuando un gobierno elegido actúa mal, se recuerda que ha sido votado. Haber sido elegido no convierte a un gobierno en competente, prudente o justo, del mismo modo que haber cumplido un procedimiento no garantiza que su resultado sea bueno.

John Stuart Mill insistió después en una idea parecida: la libertad individual no debía protegerse únicamente frente al Estado. Nadie se ve a sí mismo como parte de una fuerza que excluye, consiente o permite."""


def _ids(selected):
    return [item.ficha.id for item in selected]


def test_every_ficha_is_complete_and_relations_resolve():
    fichas = load_fichas()
    assert len(fichas) >= 40
    required = {
        relacion.ficha
        for ficha in fichas.values()
        for relacion in ficha.relaciones
        if relacion.tipo == "requiere"
    }
    for ficha in fichas.values():
        assert ficha.regla and ficha.aplica and ficha.no_aplica
        assert ficha.ejemplos and ficha.fuente.localizador
        # Toda ficha tiene que poder llegar al modelo por alguna vía.
        reachable = (
            ficha.senales or ficha.metricas or ficha.base.acciones or ficha.base.miradas
            or ficha.generos or ficha.id in required
        )
        assert reachable, ficha.id


def test_essay_edit_selects_by_diagnosis_not_by_words():
    selected = _ids(select_fichas(ENSAYO, "rewrite", "comprension", "ensayo de opinión"))
    assert "matices-protegidos" in selected
    assert "tiempo-ideas-atribuidas" in selected
    assert "analogias-y-comparaciones" in selected
    assert "enumeraciones-argumentales" in selected
    assert "argumentacion" in selected
    # «Haber sido elegido» ya no arrastra la ficha de «haber» impersonal.
    assert "haber-impersonal" not in selected


def test_correction_only_uses_norm_fichas():
    text = "Habían muchas dudas. Pienso de que no vendrá. Me di cuenta que era tarde."
    selected = select_fichas(text, "correction")
    assert {item.ficha.rama for item in selected} == {"lengua"}
    assert {"haber-impersonal", "dequeismo", "queismo", "formas-admitidas"} <= set(_ids(selected))


def test_review_leaves_out_norm_fichas():
    selected = select_fichas("Habían muchas dudas sobre el proyecto.", "review", genre="ensayo")
    assert all(item.ficha.rama != "lengua" for item in selected)


def test_genre_filters_genre_specific_fichas():
    dialogue = "—¿Vienes? —preguntó Ana.\n- No - dijo Luis."
    assert "raya-en-dialogo" in _ids(select_fichas(dialogue, "correction"))
    assert "raya-en-dialogo" not in _ids(select_fichas(dialogue, "correction", genre="ensayo"))
    assert "cuento-infantil" in _ids(select_fichas("Había una vez un lobo.", "rewrite", genre="cuento infantil"))


def test_block_carries_rule_examples_fragments_and_priorities():
    block = oficio_block(select_fichas(ENSAYO, "rewrite", "comprension", "ensayo"))
    assert "Regla:" in block and "No aplica:" in block and "Ejemplo: mal «" in block
    assert "En este texto:" in block and "del mismo modo que" in block
    assert "Prioridades entre estas fichas:" in block
    assert "«Matices protegidos» prevalece sobre" in block
    assert "norma > sentido" in block


def test_prompt_receives_oficio_block(monkeypatch):
    captured: dict[str, str] = {}

    class CapturingResponses:
        def create(self, **kwargs):
            captured["input"] = kwargs["input"]

            class Response:
                output_text = "Texto."

            return Response()

    class CapturingOpenAI:
        def __init__(self):
            self.responses = CapturingResponses()

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(service, "OpenAI", CapturingOpenAI)
    payload = GenerationInput(text=ENSAYO, action="rewrite", genre="ensayo de opinión")
    block = oficio_block(select_fichas(payload.text, payload.action, payload.revision_intention, payload.genre))
    service.rewrite_with_profile(payload, [], knowledge_notes=block)
    assert "## Matices protegidos" in captured["input"]
    assert "Tipo de texto declarado por el autor: ensayo de opinión" in captured["input"]


def test_policy_document_exists():
    policy = Path(__file__).resolve().parents[2] / "docs" / "POLITICA_CONOCIMIENTO.md"
    assert "La ficha de oficio es el formato válido" in policy.read_text(encoding="utf-8")


def test_error_signals_fire_on_bad_example_and_not_on_good_one():
    """Cada ficha con señales de error tiene que delatar su ejemplo malo y no el bueno."""
    from app.oficio.selection import METRIC_FUNCTIONS, _signal_hits

    # Métricas que se pueden comprobar sobre una frase de ejemplo (las de párrafo o de
    # texto completo necesitan textos largos y se prueban aparte).
    sentence_metrics = {
        "ques_encadenados", "des_encadenados", "mente_encadenados", "eco_sufijos",
        "intensificadores", "frases_cortas", "trato_mixto", "incisos",
    }
    problems = []
    for ficha in load_fichas().values():
        has_error_signals = any(senal.tipo == "error" for senal in ficha.senales)
        metrics = [metric for metric in ficha.metricas if metric in sentence_metrics]
        if not has_error_signals and not metrics:
            continue
        ejemplo = ficha.ejemplos[0]

        def fires(text: str, ficha=ficha, metrics=metrics) -> bool:
            hits = _signal_hits(ficha, text, "error")
            for metric in metrics:
                hits += METRIC_FUNCTIONS[metric](text)
            return bool(hits)

        if not fires(ejemplo.mal):
            problems.append(f"{ficha.id}: no salta en su ejemplo malo")
        if has_error_signals and _signal_hits(ficha, ejemplo.bien, "error"):
            problems.append(f"{ficha.id}: salta en su ejemplo bueno")
    assert not problems, "\n".join(problems)


def test_new_branches_are_covered():
    ramas = {ficha.rama for ficha in load_fichas().values()}
    assert ramas == {"lengua", "recursos", "composicion", "voz", "generos", "tradicion", "criterio"}
    assert len(load_fichas()) >= 120


def test_instruction_activates_tradition_fichas():
    selected = [item.ficha.id for item in select_fichas("El concejal entró.", "rewrite", instruction="hazlo más esperpéntico")]
    assert "esperpento" in selected
