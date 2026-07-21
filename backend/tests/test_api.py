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


def test_scores_are_available_by_context():
    response = client.get("/profiles/default/scores?context=ensayo")
    assert response.status_code == 200
    assert response.json()[0]["context"] == "ensayo"


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


def test_accepted_preference_proposes_and_applies_scoring():
    created = client.post(
        "/preferences",
        json={"text": "Prefiero textos directos y precisos.", "input_type": "prompt"},
    )
    preference_id = created.json()["id"]
    client.patch(f"/preferences/{preference_id}", json={"status": "accepted"})

    proposal = client.get(f"/preferences/{preference_id}/score-proposal")
    assert proposal.status_code == 200
    proposal_payload = proposal.json()
    assert proposal_payload["status"] == "pending_review"
    assert len(proposal_payload["items"]) >= 1

    applied = client.post(
        f"/preferences/{preference_id}/score-proposal/apply",
        json={"reason": "Aplicar preferencia aceptada."},
    )
    assert applied.status_code == 200
    assert len(applied.json()["variables"]) >= 1


def test_generation_uses_requested_context():
    response = client.post(
        "/generation",
        json={"text": "Una idea inicial", "action": "continue", "context": "tecnico"},
    )
    assert response.status_code == 200
    assert response.json()["learning_applied"] is False


def test_lab_simulation_does_not_persist_score_changes():
    before = client.get("/profiles/default/scores?context=general").json()
    target = before[0]

    response = client.post(
        "/lab/simulate",
        json={
            "text": "Una idea inicial",
            "action": "continue",
            "context": "general",
            "overrides": [{"variable_key": target["key"], "delta": 120}],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    simulated = next(
        item for item in payload["simulated_variables"] if item["key"] == target["key"]
    )
    after = client.get("/profiles/default/scores?context=general").json()
    persisted = next(item for item in after if item["key"] == target["key"])
    assert payload["learning_applied"] is False
    assert payload["generation"]["learning_applied"] is False
    assert simulated["manual_adjustment"] == target["manual_adjustment"] + 120
    assert persisted["manual_adjustment"] == target["manual_adjustment"]
    assert "lexico" in payload["comparison"]["dimensions"]


def test_knowledge_cards_and_statistics_are_exposed():
    cards = client.get("/knowledge/cards")
    assert cards.status_code == 200
    assert len(cards.json()) >= 1

    stats = client.get("/profiles/default/statistics?context=general")
    assert stats.status_code == 200
    assert stats.json()["profile_id"] == "default"


def test_comparison_includes_dimensions_and_changes():
    response = client.post(
        "/comparisons",
        json={"original": "Texto claro.", "revised": "Texto mucho mas claro.", "context": "general"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "lexico" in payload["dimensions"]
    assert isinstance(payload["changes"], list)
