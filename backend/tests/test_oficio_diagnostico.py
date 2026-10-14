from fastapi.testclient import TestClient

from app.db.models import OficioDiagnosticoRecord
from app.db.session import SessionLocal
from app.main import app
from app.oficio import load_fichas, oficio_block, select_fichas
from app.oficio.comprobacion import check_application
from app.oficio.diagnostico import select_with_diagnosis
from app.oficio.mejoras import find_candidates

TEXTO = (
    "La propuesta pretende sustituirla por un comité. El plan consiste de tres fases. "
    "Ana miró por la ventana y Ana pensó que nadie vendría, aunque yo sabía que sí."
)


def _clear_cache():
    with SessionLocal() as session:
        session.query(OficioDiagnosticoRecord).delete()
        session.commit()


def _ids(items):
    return [item.ficha.id for item in items]


class FakeModel:
    def __init__(self, response):
        self.response = response
        self.calls = 0

    def __call__(self, prompt):
        self.calls += 1
        return self.response


def test_model_discards_false_signal_and_adds_problem_without_pattern():
    _clear_cache()
    fichas = load_fichas()
    plain = _ids(select_fichas(TEXTO, "rewrite", fichas=fichas))
    assert "sustituir-a-por" in plain
    assert "punto-de-vista" not in plain

    model = FakeModel({
        "candidatas": {"sustituir-a-por": False, "regimen-preposicional": True},
        "anadidas": [
            {"id": "punto-de-vista", "fragmento": "Ana pensó que nadie vendría, aunque yo sabía que sí"},
            {"id": "ironia", "fragmento": "una frase que no está en el texto"},
            {"id": "no-existe", "fragmento": "El plan"},
        ],
    })
    with SessionLocal() as session:
        selected, summary = select_with_diagnosis(session, TEXTO, "rewrite", fichas=fichas, call_model=model)
    ids = _ids(selected)
    assert "sustituir-a-por" not in ids
    assert "punto-de-vista" in ids
    item = next(item for item in selected if item.ficha.id == "punto-de-vista")
    assert "diagnóstico del texto" in item.motivos and item.problema
    # Solo se acepta lo verificable: fragmento literal e id existente.
    assert [entry["id"] for entry in summary["anadidas"]] == ["punto-de-vista"]
    assert summary["descartadas"][0]["id"] == "sustituir-a-por"
    assert summary["estado"] == "hecho"

    # Mismo texto y opciones: sale de la caché, sin volver a llamar al modelo.
    with SessionLocal() as session:
        again, cached = select_with_diagnosis(session, TEXTO, "rewrite", fichas=fichas, call_model=model)
    assert model.calls == 1
    assert cached["estado"] == "cache"
    assert _ids(again) == ids


def test_without_model_selection_falls_back_to_patterns():
    _clear_cache()
    fichas = load_fichas()
    with SessionLocal() as session:
        selected, summary = select_with_diagnosis(
            session, TEXTO, "rewrite", fichas=fichas, call_model=lambda prompt: None
        )
    assert summary["estado"] == "no_disponible"
    assert _ids(selected) == _ids(select_fichas(TEXTO, "rewrite", fichas=fichas))


def test_problems_are_never_cut_by_the_limit():
    text = "Habían muchas dudas. Pienso de que no vendrá. Me di cuenta que era tarde. El plan consiste de tres fases."
    selected = select_fichas(text, "correction", limit=2)
    ids = _ids(selected)
    for problem in ["haber-impersonal", "dequeismo", "queismo", "regimen-preposicional"]:
        assert problem in ids
    assert len(ids) > 2


def test_priorities_count_even_when_the_other_ficha_is_not_chosen():
    fichas = load_fichas()
    base = fichas["redundancia-real"].model_copy(update={"relaciones": []})
    guard = fichas["matices-protegidos"].model_copy(
        update={"base": fichas["matices-protegidos"].base.model_copy(update={"acciones": [], "miradas": []}),
                "senales": []}
    )
    subset = {base.id: base, guard.id: guard}
    selected = select_fichas("Un texto cualquiera.", "rewrite", fichas=subset)
    assert _ids(selected) == ["redundancia-real"]
    assert any("Matices protegidos" in limite for limite in selected[0].limites)
    assert "Límite: «Matices protegidos» prevalece sobre esta" in oficio_block(selected)


def test_application_check_measures_what_is_measurable():
    original = "El plan consiste de tres fases."
    selected = select_fichas(original, "correction")
    fixed = check_application(selected, original, "El plan consiste en tres fases.")
    kept = check_application(selected, original, original)
    state = {item["id"]: item["estado"] for item in fixed["comprobadas"]}
    assert state["regimen-preposicional"] == "aplicada"
    assert {item["id"]: item["estado"] for item in kept["comprobadas"]}["regimen-preposicional"] == "sigue"
    assert fixed["sin_comprobacion"] >= 1


def test_generation_reports_diagnosis_and_checks_and_feeds_proposals():
    _clear_cache()
    client = TestClient(app)
    for _ in range(5):
        response = client.post("/correction", json={"text": "El plan consiste de tres fases.", "context": "general"})
        assert response.status_code == 200, response.text
        body = response.json()
    assert body["diagnosis"]["estado"] in {"no_disponible", "hecho", "cache"}
    assert "comprobadas" in body["ficha_checks"]
    with SessionLocal() as session:
        candidates = {item["ficha_id"]: item for item in find_candidates(session)}
    states = {item["id"]: item["estado"] for item in body["ficha_checks"]["comprobadas"]}
    if states.get("regimen-preposicional") == "sigue":
        assert "regimen-preposicional" in candidates
        assert "siguió en la propuesta" in candidates["regimen-preposicional"]["motivo"]
