from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_profile_scores_include_effective_value():
    response = client.get("/profiles/default/scores")
    assert response.status_code == 200
    assert "effective_value" in response.json()[0]


def test_patch_score_records_manual_override():
    response = client.patch(
        "/profiles/default/scores/dinamismo",
        json={"manual_adjustment": 70, "reason": "Quiero mas ritmo en este contexto."},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["variable"]["manual_adjustment"] == 70
    assert payload["variable"]["effective_value"] == 690
    assert payload["evidence"]["evidence_type"] == "manual_override"


def test_preference_interpretation_is_proposed():
    response = client.post(
        "/preferences/interpret",
        json={"text": "Me gusta un estilo sobrio y preciso.", "input_type": "prompt"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "proposed"


def test_preference_can_be_accepted_and_deleted():
    created = client.post(
        "/preferences",
        json={"text": "Prefiero frases directas y precisas.", "input_type": "prompt"},
    )
    preference_id = created.json()["id"]

    patched = client.patch(f"/preferences/{preference_id}", json={"status": "accepted"})
    assert patched.status_code == 200
    assert patched.json()["status"] == "accepted"

    deleted = client.delete(f"/preferences/{preference_id}")
    assert deleted.status_code == 204


def test_audit_events_are_exposed():
    created = client.post(
        "/preferences",
        json={"text": "Prefiero un tono contenido.", "input_type": "prompt"},
    )
    assert created.status_code == 200

    response = client.get("/audit/events")
    assert response.status_code == 200
    events = response.json()
    assert len(events) > 0
    assert events[0]["event_type"] in {
        "preference.created",
        "preference.status_updated",
        "preference.deleted",
        "score.manual_override",
        "comparison.created",
    }
