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
        "text.generated",
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


def test_generation_is_persisted_as_text():
    response = client.post(
        "/generation",
        json={"text": "Texto para persistir", "action": "rewrite", "context": "general"},
    )
    assert response.status_code == 200

    texts = client.get("/texts?context=general")
    assert texts.status_code == 200
    payload = texts.json()
    assert payload[0]["input_text"] == "Texto para persistir"
    assert payload[0]["output_text"] == response.json()["output"]
    assert payload[0]["learning_applied"] is False


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


def test_feedback_proposal_requires_explicit_application():
    comparison = client.post(
        "/comparisons",
        json={
            "original": "Texto claro y corto.",
            "revised": "Texto claro, corto y con mas precision.",
            "context": "general",
        },
    )
    assert comparison.status_code == 200
    scores_before = client.get("/profiles/default/scores?context=general").json()

    proposal = client.post(
        f"/comparisons/{comparison.json()['id']}/feedback",
        json={"context": "general", "note": "Correccion revisada."},
    )
    assert proposal.status_code == 200
    proposal_payload = proposal.json()
    assert proposal_payload["status"] == "proposed"
    assert len(proposal_payload["items"]) >= 1

    scores_after_proposal = client.get("/profiles/default/scores?context=general").json()
    assert scores_after_proposal == scores_before

    applied = client.patch(
        f"/feedback/proposals/{proposal_payload['id']}",
        json={"status": "applied", "reason": "Aplicar aprendizaje revisado."},
    )
    assert applied.status_code == 200
    assert applied.json()["status"] == "applied"

    scores_after_apply = client.get("/profiles/default/scores?context=general").json()
    assert scores_after_apply != scores_before


def test_v1_screens_are_exposed():
    response = client.get("/ui/screens")
    assert response.status_code == 200
    screen_ids = {item["id"] for item in response.json()}
    assert {"knowledge", "preferences", "profile", "scoring", "editor", "lab", "compare"} <= screen_ids


def test_decision_rules_and_persistence_status_are_exposed():
    rules = client.get("/decision/rules")
    assert rules.status_code == 200
    assert rules.json()[0]["label"] == "Restricciones tecnicas y linguisticas"

    evaluation = client.post("/decision/evaluate", json={"context": "general"})
    assert evaluation.status_code == 200
    assert "recommendation" in evaluation.json()

    persistence = client.get("/persistence/status")
    assert persistence.status_code == 200
    domains = {item["id"]: item for item in persistence.json()}
    assert domains["knowledge"]["storage"] == "seeded registry"
    assert domains["texts"]["status"] == "persisted"


def test_cerebro_audit_and_acceptance_are_exposed():
    audit = client.get("/cerebro-audit/candidates")
    assert audit.status_code == 200
    candidates = {item["component"]: item for item in audit.json()}
    assert candidates["source_registry"]["classification"] == "REFERENCIA"
    assert candidates["importers"]["classification"] == "DESCARTAR"

    acceptance = client.get("/acceptance/v1")
    assert acceptance.status_code == 200
    criteria = acceptance.json()
    assert len(criteria) == 20
    assert all(item["status"] == "implemented" for item in criteria)


def test_closure_observability_roadmap_and_cerebro_gates_are_exposed():
    closure = client.get("/closure/conditions")
    assert closure.status_code == 200
    assert len(closure.json()) == 12
    assert closure.json()[0]["status"] == "satisfied"

    expected = client.get("/closure/expected-result")
    assert expected.status_code == 200
    assert expected.json()[-1]["text"] == "Nada cambiara hasta que lo apruebes."

    observability = client.get("/observability/status")
    assert observability.status_code == 200
    assert any(item["id"] == "adequacy_percentage" for item in observability.json())

    roadmap = client.get("/roadmap/technical")
    assert roadmap.status_code == 200
    assert roadmap.json()[0]["name"] == "Esqueleto"

    gates = client.get("/cerebro-audit/gates")
    assert gates.status_code == 200
    assert any(item["id"] == "world_model_dependency" for item in gates.json())
