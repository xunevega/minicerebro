from fastapi.testclient import TestClient

from app.db.models import (
    AuditEventRecord,
    OficioFichaRecord,
    OficioFichaVersionRecord,
    OficioPropuestaRecord,
    ProfileOficioFichaRecord,
)
from app.db.session import SessionLocal
from app.main import app
from app.oficio import load_fichas, mejoras, select_fichas
from app.oficio.store import active_fichas

client = TestClient(app)


def _reset():
    with SessionLocal() as session:
        for model in (OficioPropuestaRecord, OficioFichaVersionRecord, OficioFichaRecord, ProfileOficioFichaRecord):
            session.query(model).delete()
        session.query(AuditEventRecord).filter(
            AuditEventRecord.event_type.in_(["generation.outcome", "oficio.fichas.selected"])
        ).delete(synchronize_session=False)
        session.commit()


def _ficha(ficha_id: str) -> dict:
    return load_fichas()[ficha_id].model_dump()


def test_edit_changes_the_active_catalog_and_keeps_history():
    _reset()
    ficha = _ficha("dequeismo")
    ficha["no_aplica"] = ficha["no_aplica"] + " Tampoco en citas literales."
    response = client.put("/oficio/fichas/dequeismo", json={"ficha": ficha, "motivo": "Añadir citas"})
    assert response.status_code == 200, response.text

    with SessionLocal() as session:
        assert "citas literales" in active_fichas(session)["dequeismo"].no_aplica

    listed = {item["id"]: item for item in client.get("/oficio/fichas").json()}
    assert listed["dequeismo"]["version"] == 1
    assert listed["dequeismo"]["origen"] == "editada"

    history = client.get("/oficio/fichas/dequeismo/versiones").json()
    assert [item["version"] for item in history] == [1, 0]
    assert history[0]["motivo"] == "Añadir citas"

    restored = client.post("/oficio/fichas/dequeismo/restaurar", json={"version": 0})
    assert restored.status_code == 200
    with SessionLocal() as session:
        assert "citas literales" not in active_fichas(session)["dequeismo"].no_aplica


def test_edit_is_rejected_when_signal_stops_catching_its_bad_example():
    _reset()
    ficha = _ficha("dequeismo")
    ficha["ejemplos"][0]["mal"] = "Algo que no tiene nada que ver."
    response = client.put("/oficio/fichas/dequeismo", json={"ficha": ficha, "motivo": "Prueba"})
    assert response.status_code == 422
    assert any("ejemplo malo" in problem for problem in response.json()["detail"]["problemas"])

    check = client.post("/oficio/fichas/validar", json={"ficha": ficha})
    assert check.json()["valida"] is False


def test_motivo_is_required_and_id_cannot_change():
    _reset()
    ficha = _ficha("queismo")
    assert client.put("/oficio/fichas/queismo", json={"ficha": ficha, "motivo": ""}).status_code == 422


def test_create_new_ficha_and_deactivate_it():
    _reset()
    nueva = {
        "id": "prueba-pleonasmo-propio",
        "rama": "composicion",
        "nombre": "Pleonasmo de prueba",
        "regla": "No se escribe «persona humana»: toda persona es humana y sobra el adjetivo.",
        "aplica": "Textos expositivos.",
        "no_aplica": "Textos filosóficos que oponen persona a otras entidades.",
        "ejemplos": [{"mal": "Toda persona humana tiene derechos.", "bien": "Toda persona tiene derechos.", "porque": "Sobra «humana»."}],
        "fuente": {"obra": "Criterio de Editados", "localizador": "prueba"},
        "senales": [{"patron": "\\bpersona humana\\b"}],
    }
    created = client.post("/oficio/fichas", json={"ficha": nueva, "motivo": "Nueva"})
    assert created.status_code == 200, created.text
    with SessionLocal() as session:
        catalog = active_fichas(session)
        assert "prueba-pleonasmo-propio" in [
            x.ficha.id for x in select_fichas("Toda persona humana importa.", "rewrite", fichas=catalog)
        ]

    duplicated = client.post("/oficio/fichas", json={"ficha": nueva, "motivo": "Otra vez"})
    assert duplicated.status_code == 422

    off = client.post("/oficio/fichas/prueba-pleonasmo-propio/activa", json={"activa": False, "motivo": "Retirar"})
    assert off.status_code == 200
    with SessionLocal() as session:
        assert "prueba-pleonasmo-propio" not in active_fichas(session)


def test_cannot_deactivate_a_ficha_others_depend_on():
    _reset()
    response = client.post("/oficio/fichas/matices-protegidos/activa", json={"activa": False, "motivo": "x"})
    assert response.status_code == 422


def test_dismissed_ficha_produces_a_validated_proposal_that_can_be_accepted(monkeypatch):
    _reset()
    client.post(
        "/revision/feedback/referencia-ambigua",
        json={"knowledge_version": "oficio", "context": "general", "stance": "no_me_sirve", "feedback": "Salta siempre"},
    )

    def fake_drafter(ficha, motivo, evidencia, problemas=None):
        data = ficha.model_dump()
        data["no_aplica"] += " Tampoco si solo hay un personaje en la escena."
        return data

    with SessionLocal() as session:
        result = mejoras.run_improvements(session, drafter=fake_drafter)
    assert result["creadas"] >= 1

    pending = client.get("/oficio/propuestas").json()
    proposal = next(item for item in pending if item["ficha_id"] == "referencia-ambigua")
    assert "descartado" in proposal["motivo"]
    assert proposal["actual"]["no_aplica"] != proposal["propuesta"]["no_aplica"]

    accepted = client.post(f"/oficio/propuestas/{proposal['id']}/aceptar", json={})
    assert accepted.status_code == 200
    assert accepted.json()["estado"] == "aceptada"
    with SessionLocal() as session:
        assert "un personaje" in active_fichas(session)["referencia-ambigua"].no_aplica
        # El descarte ya se tuvo en cuenta: no vuelve a proponer lo mismo.
        assert all(c["ficha_id"] != "referencia-ambigua" for c in mejoras.find_candidates(session))


def test_invalid_draft_is_not_saved(monkeypatch):
    _reset()
    client.post(
        "/revision/feedback/dequeismo",
        json={"knowledge_version": "oficio", "context": "general", "stance": "no_me_sirve"},
    )

    def broken_drafter(ficha, motivo, evidencia, problemas=None):
        data = ficha.model_dump()
        data["senales"] = [{"patron": "nunca-salta-xyz"}]
        return data

    with SessionLocal() as session:
        result = mejoras.run_improvements(session, drafter=broken_drafter)
    assert result["creadas"] == 0
    assert result["omitidas"] and "ejemplo malo" in result["omitidas"][0]["razon"]


def test_generation_outcomes_feed_the_proposal_triggers():
    _reset()
    for decision in ["discarded", "discarded", "discarded", "accepted"]:
        response = client.post(
            "/generation/outcome",
            json={"decision": decision, "fichas": ["redundancia-real"], "action": "rewrite"},
        )
        assert response.status_code == 200
    with SessionLocal() as session:
        candidates = {c["ficha_id"]: c for c in mejoras.find_candidates(session)}
    assert "redundancia-real" in candidates
    assert "3 de 4" in candidates["redundancia-real"]["motivo"]
    assert client.post("/generation/outcome", json={"decision": "otra", "fichas": []}).status_code == 422
