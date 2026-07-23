from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.models import (
    AuditEventRecord,
    KnowledgeCardRecord,
    KnowledgeClaimEvidenceLinkRecord,
    KnowledgeClaimRecord,
    KnowledgeClaimRevisionRecord,
    KnowledgeEvidenceItemRecord,
    KnowledgeEvidenceRevisionRecord,
    KnowledgeExtractionRunRecord,
    KnowledgeIndexEntryRecord,
    KnowledgeIngestionBatchRecord,
    KnowledgeNodeRecord,
    KnowledgeNodeRelationRecord,
    KnowledgeObjectRevisionRecord,
    KnowledgeProposalRecord,
    KnowledgeRelationRecord,
    KnowledgeSegmentRecord,
    KnowledgeSourceRecord,
    KnowledgeSourceEditionRecord,
    KnowledgeVersionRecord,
    KnowledgeVersionSnapshotRecord,
    ProfileKnowledgeCardRecord,
    ScoreVariableRecord,
)
from app.db.session import SessionLocal
from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_cors_origins_include_configured_frontend_without_trailing_slash(monkeypatch):
    from app import main

    monkeypatch.setenv(
        "CORS_ALLOW_ORIGINS",
        "https://frontend-production-834c.up.railway.app/, https://otro.example",
    )

    assert main.cors_allow_origins() == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://frontend-production-834c.up.railway.app",
        "https://otro.example",
    ]


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


def test_profile_export_includes_traceable_profile_without_knowledge():
    created = client.post(
        "/preferences",
        json={
            "text": "Prefiero precision y claridad en ensayos.",
            "input_type": "prompt",
            "context": "ensayo",
        },
    )
    assert created.status_code == 200

    client.get("/profiles/default/scores?context=ensayo")

    response = client.get("/profiles/default/export")
    assert response.status_code == 200

    payload = response.json()
    assert payload["export_version"] == "profile-export-v1"
    assert payload["profile_id"] == "default"
    assert payload["profile"]["id"] == "default"
    assert "general" in payload["variables_by_context"]
    assert "ensayo" in payload["variables_by_context"]
    assert "effective_value" in payload["variables_by_context"]["general"][0]
    assert payload["statistics_by_context"]["ensayo"]["profile_id"] == "default"
    assert any(
        item["evidence"]["context"] == "ensayo" for item in payload["preferences"]
    )
    assert payload["knowledge_cards"] == []
    assert payload["knowledge_policy"] == (
        "La exportacion del perfil no incluye ni modifica la base de conocimiento."
    )
    assert "knowledge" not in payload


def test_profile_export_rejects_missing_profile():
    response = client.get("/profiles/missing/export")
    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"


def test_profile_knowledge_card_records_user_feedback_without_mutating_knowledge():
    try:
        assert client.get("/profiles/default").status_code == 200
        with SessionLocal() as session:
            card = session.get(KnowledgeCardRecord, "lexico-precision")
            assert card is not None
            original_version = card.version
            score_record = session.scalar(
                select(ScoreVariableRecord).where(
                    ScoreVariableRecord.profile_id == "default",
                    ScoreVariableRecord.key == "precision_lexica",
                    ScoreVariableRecord.context == "general",
                )
            )
            assert score_record is not None
            original_score = {
                "calculated_value": score_record.calculated_value,
                "manual_adjustment": score_record.manual_adjustment,
                "confidence": score_record.confidence,
                "evidence_count": score_record.evidence_count,
                "updated_at": score_record.updated_at,
            }

        response = client.post(
            "/profiles/default/knowledge-cards/lexico-precision",
            json={
                "knowledge_version": "knowledge-v0",
                "stance": "kept",
                "user_score": 820,
                "feedback": "Mantener esta ficha para precision lexica.",
                "maintained_elements": ["definicion", "tono"],
                "change_requests": [],
                "notes": "Preferencia personal, no conocimiento estable.",
            },
        )
        assert response.status_code == 200
        created = response.json()
        assert created["profile_id"] == "default"
        assert created["card_id"] == "lexico-precision"
        assert created["knowledge_version"] == "knowledge-v0"
        assert created["stance"] == "kept"
        assert created["user_score"] == 820
        assert created["maintained_elements"] == ["definicion", "tono"]
        assert created["change_requests"] == []

        updated = client.post(
            "/profiles/default/knowledge-cards/lexico-precision",
            json={
                "knowledge_version": "knowledge-v0",
                "stance": "changed",
                "user_score": 610,
                "feedback": "Me gusta la base, pero quiero ejemplos menos rigidos.",
                "maintained_elements": ["precision"],
                "change_requests": ["ejemplos menos rigidos"],
                "notes": "Ajuste de usuario.",
            },
        )
        assert updated.status_code == 200
        updated_payload = updated.json()
        assert updated_payload["id"] == created["id"]
        assert updated_payload["stance"] == "changed"
        assert updated_payload["user_score"] == 610
        assert updated_payload["change_requests"] == ["ejemplos menos rigidos"]

        listed = client.get("/profiles/default/knowledge-cards")
        assert listed.status_code == 200
        assert [item["id"] for item in listed.json()] == [created["id"]]

        detail = client.get(
            "/profiles/default/knowledge-cards/lexico-precision?knowledge_version=knowledge-v0"
        )
        assert detail.status_code == 200
        assert detail.json()["id"] == created["id"]

        score_proposal = client.get(
            "/profiles/default/knowledge-cards/lexico-precision/score-proposal"
            "?knowledge_version=knowledge-v0&context=general"
        )
        assert score_proposal.status_code == 200
        proposal_payload = score_proposal.json()
        assert proposal_payload["profile_knowledge_card_id"] == created["id"]
        assert proposal_payload["status"] == "pending_review"
        assert proposal_payload["items"][0]["variable_key"] == "precision_lexica"
        assert proposal_payload["items"][0]["delta"] < 0

        applied = client.post(
            "/profiles/default/knowledge-cards/lexico-precision/score-proposal/apply"
            "?knowledge_version=knowledge-v0&context=general",
            json={"reason": "Aplicar scoring desde ficha de usuario revisada."},
        )
        assert applied.status_code == 200
        applied_payload = applied.json()
        assert applied_payload["proposal"]["profile_knowledge_card_id"] == created["id"]
        assert applied_payload["variables"][0]["key"] == "precision_lexica"
        assert applied_payload["variables"][0]["calculated_value"] == (
            proposal_payload["items"][0]["proposed_value"]
        )

        export = client.get("/profiles/default/export")
        assert export.status_code == 200
        assert export.json()["knowledge_cards"][0]["id"] == created["id"]

        missing_profile = client.post(
            "/profiles/missing-profile/knowledge-cards/lexico-precision",
            json={
                "knowledge_version": "knowledge-v0",
                "stance": "liked",
                "user_score": 700,
                "feedback": "No debe crearse sin perfil.",
            },
        )
        assert missing_profile.status_code == 404

        missing_card = client.post(
            "/profiles/default/knowledge-cards/missing-card",
            json={
                "knowledge_version": "knowledge-v0",
                "stance": "liked",
                "user_score": 700,
                "feedback": "No debe crearse sin ficha de conocimiento.",
            },
        )
        assert missing_card.status_code == 404

        with SessionLocal() as session:
            records = session.scalars(
                select(ProfileKnowledgeCardRecord).where(
                    ProfileKnowledgeCardRecord.profile_id == "default",
                    ProfileKnowledgeCardRecord.card_id == "lexico-precision",
                    ProfileKnowledgeCardRecord.knowledge_version == "knowledge-v0",
                )
            ).all()
            assert len(records) == 1
            card = session.get(KnowledgeCardRecord, "lexico-precision")
            assert card is not None
            assert card.version == original_version
            event = session.scalars(
                select(AuditEventRecord).where(
                    AuditEventRecord.event_type == "profile.knowledge_card.updated",
                    AuditEventRecord.entity_id == created["id"],
                )
            ).first()
            assert event is not None
            assert event.payload["stable_knowledge_mutated"] is False
            score_event = session.scalars(
                select(AuditEventRecord).where(
                    AuditEventRecord.event_type == "profile.knowledge_card.score_applied",
                    AuditEventRecord.entity_id == created["id"],
                )
            ).first()
            assert score_event is not None
            assert score_event.payload["stable_knowledge_mutated"] is False
    finally:
        with SessionLocal() as session:
            record_ids = [
                record.id
                for record in session.scalars(
                    select(ProfileKnowledgeCardRecord).where(
                        ProfileKnowledgeCardRecord.profile_id == "default",
                        ProfileKnowledgeCardRecord.card_id == "lexico-precision",
                        ProfileKnowledgeCardRecord.knowledge_version == "knowledge-v0",
                    )
                ).all()
            ]
            session.query(AuditEventRecord).filter(
                AuditEventRecord.entity_id.in_(record_ids)
            ).delete(synchronize_session=False)
            session.query(ProfileKnowledgeCardRecord).filter(
                ProfileKnowledgeCardRecord.id.in_(record_ids)
            ).delete(synchronize_session=False)
            if "original_score" in locals():
                score_record = session.scalar(
                    select(ScoreVariableRecord).where(
                        ScoreVariableRecord.profile_id == "default",
                        ScoreVariableRecord.key == "precision_lexica",
                        ScoreVariableRecord.context == "general",
                    )
                )
                if score_record is not None:
                    score_record.calculated_value = original_score["calculated_value"]
                    score_record.manual_adjustment = original_score["manual_adjustment"]
                    score_record.confidence = original_score["confidence"]
                    score_record.evidence_count = original_score["evidence_count"]
                    score_record.updated_at = original_score["updated_at"]
            session.commit()


def test_profile_surfaces_reject_missing_profile_consistently():
    assert client.get("/profiles/missing/summary").status_code == 404
    assert client.get("/profiles/missing/scores").status_code == 404
    assert client.get("/profiles/missing/statistics").status_code == 404
    assert client.get("/profiles/missing/contradictions").status_code == 404
    assert client.get("/profiles/missing/knowledge-cards").status_code == 404
    patched = client.patch(
        "/profiles/missing/scores/dinamismo",
        json={"manual_adjustment": 10, "reason": "No debe crear perfil inexistente."},
    )
    assert patched.status_code == 404
    assert patched.json()["detail"] == "Profile not found"


def test_bootstrap_uses_alembic_without_create_all_or_manual_schema_patch():
    import inspect

    from app.db import bootstrap

    source = inspect.getsource(bootstrap)
    assert "command.upgrade" in source
    assert "create_all" not in source
    assert "ALTER TABLE" not in source
    assert "_SEED_LOCK" in source
    assert "with _SEED_LOCK" in source


def test_application_startup_does_not_run_alembic_migrations():
    import inspect

    from app import main

    source = inspect.getsource(main)
    assert "upgrade_database" not in source
    assert "command.upgrade" not in source
    assert "lifespan" not in source


def test_preference_interpretation_is_proposed():
    response = client.post(
        "/preferences/interpret",
        json={"text": "Me gusta un estilo sobrio y preciso.", "input_type": "prompt"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "proposed"


def test_preference_interpretation_positive_direction_proposes_positive_delta():
    created = client.post(
        "/preferences",
        json={"text": "Quiero un estilo directo y preciso.", "input_type": "prompt"},
    )
    assert created.status_code == 200
    preference_id = created.json()["id"]
    client.patch(f"/preferences/{preference_id}", json={"status": "accepted"})

    proposal = client.get(f"/preferences/{preference_id}/score-proposal")
    assert proposal.status_code == 200
    items = {item["variable_key"]: item for item in proposal.json()["items"]}
    assert items["dinamismo"]["delta"] > 0
    assert items["precision_lexica"]["delta"] > 0


def test_preference_interpretation_negations_propose_negative_delta():
    cases = [
        ("No quiero que sea tan directo.", "dinamismo"),
        ("No quiero frases mas cortas.", "dinamismo"),
        ("Menos dinamismo en este contexto.", "dinamismo"),
        ("Evita un tono formal.", "sobriedad"),
    ]
    for text, variable_key in cases:
        created = client.post("/preferences", json={"text": text, "input_type": "prompt"})
        assert created.status_code == 200
        preference_id = created.json()["id"]
        client.patch(f"/preferences/{preference_id}", json={"status": "accepted"})

        proposal = client.get(f"/preferences/{preference_id}/score-proposal")
        assert proposal.status_code == 200
        items = {item["variable_key"]: item for item in proposal.json()["items"]}
        assert items[variable_key]["delta"] < 0


def test_preference_interpretation_ambiguous_negation_does_not_invert_affirmed_terms():
    created = client.post(
        "/preferences",
        json={"text": "No solo directo, tambien preciso.", "input_type": "prompt"},
    )
    assert created.status_code == 200
    preference_id = created.json()["id"]
    client.patch(f"/preferences/{preference_id}", json={"status": "accepted"})

    proposal = client.get(f"/preferences/{preference_id}/score-proposal")
    assert proposal.status_code == 200
    items = {item["variable_key"]: item for item in proposal.json()["items"]}
    assert items["dinamismo"]["delta"] > 0
    assert items["precision_lexica"]["delta"] > 0


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


def test_preference_creation_audits_interpretation_duration():
    created = client.post(
        "/preferences",
        json={"text": "Prefiero un estilo preciso.", "input_type": "prompt"},
    )
    assert created.status_code == 200

    response = client.get("/audit/events")
    assert response.status_code == 200
    event = response.json()[0]
    assert event["event_type"] == "preference.created"
    assert event["payload"]["duration_ms"] >= 0
    assert "text" not in event["payload"]


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
        "knowledge.query.executed",
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


def test_generation_action_aliases_are_bound_to_their_routes():
    variants = client.post("/variants", json={"text": "Idea base", "context": "general"})
    assert variants.status_code == 200
    assert "Variante A:" in variants.json()["output"]

    continuation = client.post("/continue", json={"text": "Idea base", "context": "general"})
    assert continuation.status_code == 200
    assert "Continuacion propuesta:" in continuation.json()["output"]

    correction = client.post("/correction", json={"text": " Texto  con  espacios ", "context": "general"})
    assert correction.status_code == 200

    texts = client.get("/texts?context=general")
    assert texts.status_code == 200
    actions = [item["action"] for item in texts.json()[:3]]
    assert actions == ["correction", "continue", "variants"]


def test_generation_audits_duration_without_raw_text():
    response = client.post(
        "/generation",
        json={"text": "Texto con duracion auditada", "action": "rewrite", "context": "general"},
    )
    assert response.status_code == 200

    events = client.get("/audit/events")
    assert events.status_code == 200
    event = events.json()[0]
    assert event["event_type"] == "text.generated"
    assert event["payload"]["duration_ms"] >= 0
    assert "Texto con duracion auditada" not in str(event["payload"])


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


def test_lab_compare_does_not_persist_comparison():
    response = client.post(
        "/lab/compare",
        json={
            "original": "Texto base con una idea clara.",
            "revised": "Texto revisado con una idea mas clara y directa.",
            "context": "general",
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["modification_score"] > 0
    assert payload["adequacy_score"] >= 0
    assert payload["summary"]

    persisted = client.get(f"/comparisons/{payload['id']}")
    assert persisted.status_code == 404
    assert persisted.json()["detail"] == "Comparison not found"


def test_knowledge_cards_and_statistics_are_exposed():
    cards = client.get("/knowledge/cards")
    assert cards.status_code == 200
    assert len(cards.json()) >= 1

    status = client.get("/knowledge/status")
    assert status.status_code == 200
    assert all(item.startswith("fuera de alcance V1:") for item in status.json()["gaps"])

    stats = client.get("/profiles/default/statistics?context=general")
    assert stats.status_code == 200
    assert stats.json()["profile_id"] == "default"


def test_knowledge_sources_are_exposed():
    response = client.get("/knowledge/sources")
    assert response.status_code == 200

    sources = response.json()
    assert len(sources) == 23
    assert {source["catalog_id"] for source in sources} == {f"F{index:03}" for index in range(1, 24)}
    assert "manual-estilo" not in {source["id"] for source in sources}
    first_source = sources[0]
    assert {key: value for key, value in first_source.items() if key != "editions"} == {
        "id": "rae-ngle",
        "catalog_id": "F001",
        "name": "Nueva gramatica de la lengua espanola",
        "responsible": "Real Academia Espanola y Asociacion de Academias de la Lengua Espanola",
        "source_type": "gramatica descriptiva y normativa",
        "domains": [
            "morfologia",
            "sintaxis",
            "categorias gramaticales",
            "funciones",
            "construcciones",
        ],
        "authority_level": 5,
        "priority": 1,
        "status": "registered",
        "edition": "pendiente de identificacion",
        "publication_date": "pendiente de identificacion",
        "location": "pendiente de adquisicion",
        "acquisition_status": "registered",
        "validation_status": "not_validated",
        "rights": "registro autorizado; contenido no ingerido",
        "structure": ["pendiente de estructuracion"],
        "locator_system": ["edicion", "parte", "capitulo", "seccion", "pagina", "entrada", "url"],
    }
    first_editions = {edition["id"]: edition for edition in first_source["editions"]}
    assert set(first_editions) == {"rae-ngle:manual-2010", "rae-ngle:pending-edition"}
    assert first_editions["rae-ngle:manual-2010"]["edition_label"] == "Manual academico, 2010"
    assert first_editions["rae-ngle:manual-2010"]["isbn"] == "9788467032819"
    assert all(len(source["editions"]) >= 1 for source in sources)
    assert all(edition["source_id"] == source["id"] for source in sources for edition in source["editions"])

    versioned = client.get("/knowledge/sources?version=knowledge-v0")
    assert versioned.status_code == 200
    assert {source["id"] for source in versioned.json()} == {source["id"] for source in sources}
    versioned_first = next(source for source in versioned.json() if source["id"] == "rae-ngle")
    assert {edition["id"] for edition in versioned_first["editions"]} == {"rae-ngle:pending-edition"}

    missing_version = client.get("/knowledge/sources?version=missing-version")
    assert missing_version.status_code == 404
    assert missing_version.json()["detail"] == "Knowledge version not found"


def test_source_ingestion_status_distinguishes_registered_from_ingested():
    response = client.get("/knowledge/ingestion/sources?source_id=rae-ngle")
    assert response.status_code == 200

    status = response.json()[0]
    assert status["source_id"] == "rae-ngle"
    assert status["current_phase"] == "proposed"
    assert status["is_registered"] is True
    assert status["has_edition"] is True
    assert status["has_index"] is True
    assert status["has_segments"] is True
    assert status["has_extractions"] is True
    assert status["has_proposals"] is True
    assert status["has_reviewed_proposals"] is False
    assert status["is_ingested"] is False
    assert status["counts"]["nodes"] >= 1
    assert status["counts"]["index_entries"] >= 1
    assert status["counts"]["segments"] >= 1
    assert status["counts"]["completed_extractions"] >= 1
    assert status["counts"]["proposals"] >= 2
    assert "missing_materialized_knowledge" in status["blockers"]
    assert "missing_publication" in status["blockers"]

    missing = client.get("/knowledge/ingestion/sources?source_id=fuente-inexistente")
    assert missing.status_code == 404
    assert missing.json()["detail"] == "Knowledge source not found"


def test_seed_real_ingestion_batch_reaches_proposals_without_publication():
    edition = client.get("/knowledge/editions/rae-ngle:manual-2010")
    assert edition.status_code == 200
    assert edition.json()["source_id"] == "rae-ngle"
    assert edition.json()["edition_label"] == "Manual academico, 2010"
    assert edition.json()["status"] == "available"

    index = client.get("/knowledge/editions/rae-ngle:manual-2010/index")
    assert index.status_code == 200
    assert [entry["id"] for entry in index.json()] == [
        "rae-ngle:manual-2010:funciones-sintacticas"
    ]
    assert index.json()[0]["title"] == "Funciones sintacticas"

    segments = client.get(
        "/knowledge/index/rae-ngle:manual-2010:funciones-sintacticas/segments"
    )
    assert segments.status_code == 200
    assert [segment["id"] for segment in segments.json()] == [
        "rae-ngle:manual-2010:funciones-sintacticas:seg-1"
    ]
    assert "complemento directo" in segments.json()[0]["text"].lower()

    extractions = client.get(
        "/knowledge/segments/rae-ngle:manual-2010:funciones-sintacticas:seg-1/extractions"
    )
    assert extractions.status_code == 200
    assert [run["id"] for run in extractions.json()] == [
        "ext-rae-ngle-manual-2010-funciones-sintacticas-1"
    ]
    extraction = extractions.json()[0]
    assert extraction["status"] == "completed"
    assert extraction["extractor_name"] == "seed-editorial-extractor"
    assert extraction["knowledge_version"] is None

    proposals = client.get(
        "/knowledge/extractions/ext-rae-ngle-manual-2010-funciones-sintacticas-1/proposals"
    )
    assert proposals.status_code == 200
    assert {proposal["proposal_type"] for proposal in proposals.json()} == {"node", "evidence"}
    assert {proposal["status"] for proposal in proposals.json()} == {"proposed"}
    assert {proposal["reviewed_at"] for proposal in proposals.json()} == {None}
    assert all(proposal["segment_id"] == segments.json()[0]["id"] for proposal in proposals.json())

    with SessionLocal() as session:
        assert session.get(KnowledgeNodeRecord, "rae-ngle-complemento-directo") is None
        assert session.get(
            KnowledgeEvidenceItemRecord, "ev-rae-ngle-complemento-directo-candidata"
        ) is None
    status = client.get("/knowledge/ingestion/sources?source_id=rae-ngle").json()[0]
    assert status["current_phase"] == "proposed"
    assert status["is_ingested"] is False
    assert status["is_published"] is False
    assert "missing_materialized_knowledge" in status["blockers"]
    assert "missing_publication" in status["blockers"]


def test_register_knowledge_source_persists_without_registering_edition_or_publication():
    source_id = "test-fuente-registro"
    payload = {
        "id": source_id,
        "catalog_id": "TEST-F001",
        "name": "Fuente de prueba para registro",
        "responsible": "Equipo editorial",
        "source_type": "manual de prueba",
        "domains": ["escritura"],
        "authority_level": 3,
        "priority": 99,
    }
    try:
        response = client.post("/knowledge/sources", json=payload)
        assert response.status_code == 200

        created = response.json()
        assert created["id"] == source_id
        assert created["catalog_id"] == "TEST-F001"
        assert created["status"] == "registered"
        assert created["edition"] == "pendiente de identificacion"
        assert created["publication_date"] == "pendiente de identificacion"
        assert created["location"] == "pendiente de adquisicion"
        assert created["acquisition_status"] == "registered"
        assert created["validation_status"] == "not_validated"
        assert created["rights"] == "registro autorizado; contenido no ingerido"
        assert created["structure"] == ["pendiente de estructuracion"]
        assert created["locator_system"] == [
            "edicion",
            "parte",
            "capitulo",
            "seccion",
            "pagina",
            "entrada",
            "url",
        ]
        assert created["editions"] == []

        listed = client.get("/knowledge/sources").json()
        persisted = next(source for source in listed if source["id"] == source_id)
        assert persisted["editions"] == []
        versioned = client.get("/knowledge/sources?version=knowledge-v0")
        assert versioned.status_code == 200
        assert source_id not in {source["id"] for source in versioned.json()}

        duplicate = client.post("/knowledge/sources", json=payload)
        assert duplicate.status_code == 409
        assert duplicate.json()["detail"] == "Knowledge source already exists"

        with SessionLocal() as session:
            record = session.get(KnowledgeSourceRecord, source_id)
            assert record is not None
            editions = session.scalars(
                select(KnowledgeSourceEditionRecord).where(
                    KnowledgeSourceEditionRecord.source_id == source_id
                )
            ).all()
            assert editions == []
            event = session.scalars(
                select(AuditEventRecord).where(
                    AuditEventRecord.event_type == "knowledge.source.registered",
                    AuditEventRecord.entity_id == source_id,
                )
            ).first()
            assert event is not None
            assert event.payload["edition_created"] is False
            assert event.payload["publishes_directly"] is False
    finally:
        with SessionLocal() as session:
            session.query(AuditEventRecord).filter(
                AuditEventRecord.entity_id == source_id
            ).delete()
            session.query(KnowledgeSourceRecord).filter(
                KnowledgeSourceRecord.id == source_id
            ).delete()
            session.commit()


def test_source_ingestion_status_advances_through_document_pipeline():
    source_id = "test-fuente-estado-ingestion"
    edition_id = "test-fuente-estado-ingestion:primera"
    entry_id = "test-fuente-estado-ingestion:capitulo-1"
    segment_id = "test-fuente-estado-ingestion:segmento-1"
    source_payload = {
        "id": source_id,
        "catalog_id": "TEST-FSTATUS",
        "name": "Fuente para estado de ingestion",
        "responsible": "Equipo editorial",
        "source_type": "manual",
        "domains": ["escritura"],
        "authority_level": 3,
        "priority": 991,
    }
    edition_payload = {
        "id": edition_id,
        "source_id": source_id,
        "title": "Fuente para estado de ingestion",
        "edition_label": "Primera",
        "publication_year": "2026",
        "publisher": "Minicerebro",
        "isbn": "sin isbn",
        "language": "es",
        "format": "texto",
        "access_location": "fixture local",
        "rights_status": "uso interno",
        "status": "available",
        "notes": "fixture",
    }
    index_payload = [
        {
            "id": entry_id,
            "edition_id": edition_id,
            "parent_id": None,
            "level": 1,
            "order": 1,
            "title": "Capitulo 1",
            "locator": "capitulo 1",
            "page_start": "1",
            "page_end": "2",
            "status": "registered",
        }
    ]
    segment_payload = [
        {
            "id": segment_id,
            "index_entry_id": entry_id,
            "parent_segment_id": None,
            "segment_type": "paragraph",
            "title": "Segmento 1",
            "text": "La precision requiere elegir palabras concretas.",
            "order": 1,
            "start_locator": "capitulo 1 > p1",
            "end_locator": "capitulo 1 > p1",
            "language": "es",
            "status": "registered",
        }
    ]
    extraction_payload = {
        "extractor_type": "deterministic",
        "extractor_name": "status-smoke",
        "extractor_version": "1.0",
        "configuration": {"mode": "status"},
    }

    try:
        assert client.post("/knowledge/sources", json=source_payload).status_code == 200
        status = client.get(f"/knowledge/ingestion/sources?source_id={source_id}").json()[0]
        assert status["current_phase"] == "registered"
        assert status["is_ingested"] is False

        assert (
            client.post(f"/knowledge/sources/{source_id}/editions", json=edition_payload).status_code
            == 200
        )
        status = client.get(f"/knowledge/ingestion/sources?source_id={source_id}").json()[0]
        assert status["current_phase"] == "edition_registered"

        assert client.post(f"/knowledge/editions/{edition_id}/index", json=index_payload).status_code == 200
        status = client.get(f"/knowledge/ingestion/sources?source_id={source_id}").json()[0]
        assert status["current_phase"] == "indexed"

        assert client.post(f"/knowledge/index/{entry_id}/segments", json=segment_payload).status_code == 200
        status = client.get(f"/knowledge/ingestion/sources?source_id={source_id}").json()[0]
        assert status["current_phase"] == "segmented"

        assert (
            client.post(f"/knowledge/segments/{segment_id}/extractions", json=extraction_payload).status_code
            == 200
        )
        status = client.get(f"/knowledge/ingestion/sources?source_id={source_id}").json()[0]
        assert status["current_phase"] == "extracted"
        assert status["counts"]["completed_extractions"] == 1
        assert status["is_ingested"] is False
    finally:
        with SessionLocal() as session:
            event_entities = [source_id, edition_id, entry_id, segment_id]
            session.query(AuditEventRecord).filter(
                AuditEventRecord.entity_id.in_(event_entities)
            ).delete(synchronize_session=False)
            session.query(KnowledgeExtractionRunRecord).filter(
                KnowledgeExtractionRunRecord.segment_id == segment_id
            ).delete()
            session.query(KnowledgeSegmentRecord).filter(
                KnowledgeSegmentRecord.id == segment_id
            ).delete()
            session.query(KnowledgeIndexEntryRecord).filter(
                KnowledgeIndexEntryRecord.id == entry_id
            ).delete()
            session.query(KnowledgeSourceEditionRecord).filter(
                KnowledgeSourceEditionRecord.id == edition_id
            ).delete()
            session.query(KnowledgeSourceRecord).filter(
                KnowledgeSourceRecord.id == source_id
            ).delete()
            session.commit()


def test_register_knowledge_source_edition_persists_and_does_not_start_ingestion():
    source_id = "test-fuente-edicion"
    edition_id = "test-fuente-edicion:primera"
    source_payload = {
        "id": source_id,
        "catalog_id": "TEST-F002",
        "name": "Fuente de prueba con edicion",
        "responsible": "Equipo editorial",
        "source_type": "manual de prueba",
        "domains": ["escritura"],
        "authority_level": 3,
        "priority": 100,
    }
    edition_payload = {
        "id": edition_id,
        "source_id": source_id,
        "title": "Fuente de prueba con edicion",
        "edition_label": "Primera edicion revisada",
        "publication_year": "2026",
        "publisher": "Editorial de prueba",
        "isbn": "978-0-000000-00-1",
        "language": "es",
        "format": "pdf",
        "access_location": "/tmp/fuente-prueba.pdf",
        "rights_status": "uso local autorizado; contenido no ingerido",
        "status": "available",
        "notes": "Registro bibliografico para prueba.",
    }
    try:
        source_response = client.post("/knowledge/sources", json=source_payload)
        assert source_response.status_code == 200

        response = client.post(
            f"/knowledge/sources/{source_id}/editions",
            json=edition_payload,
        )
        assert response.status_code == 200

        created = response.json()
        assert created["id"] == edition_id
        assert created["source_id"] == source_id
        assert created["title"] == "Fuente de prueba con edicion"
        assert created["edition_label"] == "Primera edicion revisada"
        assert created["publication_year"] == "2026"
        assert created["publisher"] == "Editorial de prueba"
        assert created["isbn"] == "978-0-000000-00-1"
        assert created["language"] == "es"
        assert created["format"] == "pdf"
        assert created["access_location"] == "/tmp/fuente-prueba.pdf"
        assert created["rights_status"] == "uso local autorizado; contenido no ingerido"
        assert created["status"] == "available"
        assert created["notes"] == "Registro bibliografico para prueba."
        assert created["label"] == "Primera edicion revisada"
        assert created["publication_date"] == "2026"
        assert created["location"] == "/tmp/fuente-prueba.pdf"
        assert created["acquisition_status"] == "available"
        assert created["validation_status"] == "not_validated"
        assert created["rights"] == "uso local autorizado; contenido no ingerido"
        assert created["created_at"]
        assert created["updated_at"]

        by_source = client.get(f"/knowledge/sources/{source_id}/editions")
        assert by_source.status_code == 200
        assert [edition["id"] for edition in by_source.json()] == [edition_id]

        individual = client.get(f"/knowledge/editions/{edition_id}")
        assert individual.status_code == 200
        assert individual.json()["id"] == edition_id

        duplicate = client.post(
            f"/knowledge/sources/{source_id}/editions",
            json={**edition_payload, "id": "test-fuente-edicion:duplicada"},
        )
        assert duplicate.status_code == 409
        assert duplicate.json()["detail"] == "Knowledge source edition already exists"

        mismatch = client.post(
            "/knowledge/sources/rae-ngle/editions",
            json=edition_payload,
        )
        assert mismatch.status_code == 409
        assert mismatch.json()["detail"] == "Knowledge edition source_id does not match path"

        missing_source = client.post(
            "/knowledge/sources/fuente-inexistente/editions",
            json={**edition_payload, "source_id": "fuente-inexistente"},
        )
        assert missing_source.status_code == 404
        assert missing_source.json()["detail"] == "Knowledge source not found"

        missing_edition = client.get("/knowledge/editions/edicion-inexistente")
        assert missing_edition.status_code == 404
        assert missing_edition.json()["detail"] == "Knowledge edition not found"

        with SessionLocal() as session:
            record = session.get(KnowledgeSourceEditionRecord, edition_id)
            assert record is not None
            batches = session.scalars(
                select(KnowledgeIngestionBatchRecord).where(
                    KnowledgeIngestionBatchRecord.source_edition_id == edition_id
                )
            ).all()
            assert batches == []
            event = session.scalars(
                select(AuditEventRecord).where(
                    AuditEventRecord.event_type == "knowledge.edition.registered",
                    AuditEventRecord.entity_id == edition_id,
                )
            ).first()
            assert event is not None
            assert event.payload["source_id"] == source_id
            assert event.payload["ingestion_batch_created"] is False
            assert event.payload["index_created"] is False
            assert event.payload["publishes_directly"] is False
    finally:
        with SessionLocal() as session:
            session.query(AuditEventRecord).filter(
                AuditEventRecord.entity_id.in_([source_id, edition_id])
            ).delete(synchronize_session=False)
            session.query(KnowledgeSourceEditionRecord).filter(
                KnowledgeSourceEditionRecord.id == edition_id
            ).delete()
            session.query(KnowledgeSourceRecord).filter(
                KnowledgeSourceRecord.id == source_id
            ).delete()
            session.commit()


def test_register_knowledge_index_entries_builds_document_tree_without_knowledge():
    source_id = "test-fuente-indice"
    edition_id = "test-fuente-indice:primera"
    root_entry_id = "test-fuente-indice:primera:vol-1"
    chapter_entry_id = "test-fuente-indice:primera:cap-1"
    section_entry_id = "test-fuente-indice:primera:sec-1-1"
    source_payload = {
        "id": source_id,
        "catalog_id": "TEST-F003",
        "name": "Fuente de prueba con indice",
        "responsible": "Equipo editorial",
        "source_type": "manual de prueba",
        "domains": ["sintaxis"],
        "authority_level": 3,
        "priority": 101,
    }
    edition_payload = {
        "id": edition_id,
        "source_id": source_id,
        "title": "Fuente de prueba con indice",
        "edition_label": "Primera edicion estructurada",
        "publication_year": "2026",
        "publisher": "Editorial de prueba",
        "isbn": "978-0-000000-00-3",
        "language": "es",
        "format": "pdf",
        "access_location": "/tmp/fuente-indice.pdf",
        "rights_status": "uso local autorizado; contenido no ingerido",
        "status": "available",
        "notes": "Registro bibliografico para prueba de indice.",
    }
    index_payload = [
        {
            "id": root_entry_id,
            "edition_id": edition_id,
            "parent_id": None,
            "level": 1,
            "order": 1,
            "title": "Volumen I",
            "locator": "volumen I",
            "page_start": "1",
            "page_end": "200",
            "status": "registered",
        },
        {
            "id": chapter_entry_id,
            "edition_id": edition_id,
            "parent_id": root_entry_id,
            "level": 2,
            "order": 1,
            "title": "Capitulo 1",
            "locator": "volumen I > capitulo 1",
            "page_start": "1",
            "page_end": "40",
            "status": "registered",
        },
        {
            "id": section_entry_id,
            "edition_id": edition_id,
            "parent_id": chapter_entry_id,
            "level": 3,
            "order": 1,
            "title": "Complemento directo",
            "locator": "volumen I > capitulo 1 > 1.1",
            "page_start": "10",
            "page_end": "14",
            "status": "registered",
        },
    ]
    try:
        assert client.post("/knowledge/sources", json=source_payload).status_code == 200
        assert (
            client.post(f"/knowledge/sources/{source_id}/editions", json=edition_payload).status_code
            == 200
        )

        response = client.post(f"/knowledge/editions/{edition_id}/index", json=index_payload)
        assert response.status_code == 200
        created = response.json()
        assert [entry["id"] for entry in created] == [
            root_entry_id,
            chapter_entry_id,
            section_entry_id,
        ]
        assert created[2]["title"] == "Complemento directo"
        assert created[2]["children"] == []

        tree_response = client.get(f"/knowledge/editions/{edition_id}/index")
        assert tree_response.status_code == 200
        tree = tree_response.json()
        assert len(tree) == 1
        assert tree[0]["id"] == root_entry_id
        assert tree[0]["children"][0]["id"] == chapter_entry_id
        assert tree[0]["children"][0]["children"][0]["id"] == section_entry_id
        assert tree[0]["children"][0]["children"][0]["title"] == "Complemento directo"

        detail = client.get(f"/knowledge/index/{section_entry_id}")
        assert detail.status_code == 200
        assert detail.json()["locator"] == "volumen I > capitulo 1 > 1.1"

        duplicate = client.post(
            f"/knowledge/editions/{edition_id}/index",
            json=[
                {
                    **index_payload[0],
                    "id": "test-fuente-indice:primera:vol-1-duplicado",
                }
            ],
        )
        assert duplicate.status_code == 409
        assert duplicate.json()["detail"] == "Knowledge index entry order already exists for parent"

        missing_parent = client.post(
            f"/knowledge/editions/{edition_id}/index",
            json=[
                {
                    **index_payload[0],
                    "id": "test-fuente-indice:primera:huerfano",
                    "parent_id": "missing-parent",
                    "order": 2,
                }
            ],
        )
        assert missing_parent.status_code == 409
        assert missing_parent.json()["detail"] == "Knowledge index entry parent not found"

        missing_edition = client.post(
            "/knowledge/editions/edicion-inexistente/index",
            json=[{**index_payload[0], "edition_id": "edicion-inexistente"}],
        )
        assert missing_edition.status_code == 404
        assert missing_edition.json()["detail"] == "Knowledge edition not found"

        missing_entry = client.get("/knowledge/index/entrada-inexistente")
        assert missing_entry.status_code == 404
        assert missing_entry.json()["detail"] == "Knowledge index entry not found"

        nodes_after = client.get(f"/knowledge/nodes?source_id={source_id}")
        assert nodes_after.status_code == 200
        assert nodes_after.json() == []

        with SessionLocal() as session:
            records = session.scalars(
                select(KnowledgeIndexEntryRecord).where(
                    KnowledgeIndexEntryRecord.edition_id == edition_id
                )
            ).all()
            assert len(records) == 3
            batches = session.scalars(
                select(KnowledgeIngestionBatchRecord).where(
                    KnowledgeIngestionBatchRecord.source_edition_id == edition_id
                )
            ).all()
            assert batches == []
            event = session.scalars(
                select(AuditEventRecord).where(
                    AuditEventRecord.event_type == "knowledge.index.registered",
                    AuditEventRecord.entity_id == edition_id,
                )
            ).first()
            assert event is not None
            assert event.payload["entry_count"] == 3
            assert event.payload["creates_knowledge"] is False
            assert event.payload["nodes_created"] is False
            assert event.payload["segmentation_started"] is False
            assert event.payload["ingestion_batch_created"] is False
    finally:
        with SessionLocal() as session:
            session.query(AuditEventRecord).filter(
                AuditEventRecord.entity_id.in_([source_id, edition_id])
            ).delete(synchronize_session=False)
            session.query(KnowledgeIndexEntryRecord).filter(
                KnowledgeIndexEntryRecord.edition_id == edition_id
            ).delete()
            session.query(KnowledgeSourceEditionRecord).filter(
                KnowledgeSourceEditionRecord.id == edition_id
            ).delete()
            session.query(KnowledgeSourceRecord).filter(
                KnowledgeSourceRecord.id == source_id
            ).delete()
            session.commit()


def test_register_knowledge_segments_preserves_text_without_creating_knowledge():
    source_id = "test-fuente-segmentos"
    edition_id = "test-fuente-segmentos:primera"
    entry_id = "test-fuente-segmentos:primera:sec-1-1"
    segment_id = "test-fuente-segmentos:primera:sec-1-1:seg-1"
    child_segment_id = "test-fuente-segmentos:primera:sec-1-1:seg-1-a"
    source_payload = {
        "id": source_id,
        "catalog_id": "TEST-F004",
        "name": "Fuente de prueba con segmentos",
        "responsible": "Equipo editorial",
        "source_type": "manual de prueba",
        "domains": ["sintaxis"],
        "authority_level": 3,
        "priority": 102,
    }
    edition_payload = {
        "id": edition_id,
        "source_id": source_id,
        "title": "Fuente de prueba con segmentos",
        "edition_label": "Primera edicion segmentable",
        "publication_year": "2026",
        "publisher": "Editorial de prueba",
        "isbn": "978-0-000000-00-4",
        "language": "es",
        "format": "pdf",
        "access_location": "/tmp/fuente-segmentos.pdf",
        "rights_status": "uso local autorizado; contenido no ingerido",
        "status": "available",
        "notes": "Registro bibliografico para prueba de segmentos.",
    }
    index_payload = [
        {
            "id": entry_id,
            "edition_id": edition_id,
            "parent_id": None,
            "level": 1,
            "order": 1,
            "title": "Complemento directo",
            "locator": "capitulo 1 > 1.1",
            "page_start": "10",
            "page_end": "14",
            "status": "registered",
        }
    ]
    segment_payload = [
        {
            "id": segment_id,
            "index_entry_id": entry_id,
            "parent_segment_id": None,
            "segment_type": "paragraph",
            "title": "Parrafo inicial",
            "text": "El complemento directo aparece descrito en este apartado documental.",
            "order": 1,
            "start_locator": "capitulo 1 > 1.1 > p1",
            "end_locator": "capitulo 1 > 1.1 > p1",
            "language": "es",
            "status": "registered",
        },
        {
            "id": child_segment_id,
            "index_entry_id": entry_id,
            "parent_segment_id": segment_id,
            "segment_type": "sentence",
            "title": "Oracion 1",
            "text": "El complemento directo aparece descrito.",
            "order": 1,
            "start_locator": "capitulo 1 > 1.1 > p1:s1",
            "end_locator": "capitulo 1 > 1.1 > p1:s1",
            "language": "es",
            "status": "registered",
        },
    ]
    try:
        assert client.post("/knowledge/sources", json=source_payload).status_code == 200
        assert (
            client.post(f"/knowledge/sources/{source_id}/editions", json=edition_payload).status_code
            == 200
        )
        assert client.post(f"/knowledge/editions/{edition_id}/index", json=index_payload).status_code == 200

        response = client.post(f"/knowledge/index/{entry_id}/segments", json=segment_payload)
        assert response.status_code == 200
        created = response.json()
        assert [segment["id"] for segment in created] == [segment_id, child_segment_id]
        assert created[0]["index_entry_id"] == entry_id
        assert created[0]["parent_segment_id"] is None
        assert created[0]["segment_type"] == "paragraph"
        assert created[0]["order"] == 1
        assert created[0]["start_locator"] == "capitulo 1 > 1.1 > p1"
        assert created[0]["end_locator"] == "capitulo 1 > 1.1 > p1"
        assert created[0]["text"] == (
            "El complemento directo aparece descrito en este apartado documental."
        )
        assert created[1]["parent_segment_id"] == segment_id

        by_entry = client.get(f"/knowledge/index/{entry_id}/segments")
        assert by_entry.status_code == 200
        assert [segment["id"] for segment in by_entry.json()] == [segment_id, child_segment_id]

        detail = client.get(f"/knowledge/segments/{child_segment_id}")
        assert detail.status_code == 200
        assert detail.json()["text"] == "El complemento directo aparece descrito."

        duplicate_order = client.post(
            f"/knowledge/index/{entry_id}/segments",
            json=[
                {
                    **segment_payload[0],
                    "id": "test-fuente-segmentos:primera:sec-1-1:seg-duplicado",
                }
            ],
        )
        assert duplicate_order.status_code == 409
        assert duplicate_order.json()["detail"] == "Knowledge segment order already exists for parent"

        missing_parent = client.post(
            f"/knowledge/index/{entry_id}/segments",
            json=[
                {
                    **segment_payload[0],
                    "id": "test-fuente-segmentos:primera:sec-1-1:seg-huerfano",
                    "parent_segment_id": "missing-segment",
                    "order": 2,
                }
            ],
        )
        assert missing_parent.status_code == 409
        assert missing_parent.json()["detail"] == "Knowledge segment parent not found"

        missing_entry = client.post(
            "/knowledge/index/entrada-inexistente/segments",
            json=[{**segment_payload[0], "index_entry_id": "entrada-inexistente"}],
        )
        assert missing_entry.status_code == 404
        assert missing_entry.json()["detail"] == "Knowledge index entry not found"

        missing_segment = client.get("/knowledge/segments/segmento-inexistente")
        assert missing_segment.status_code == 404
        assert missing_segment.json()["detail"] == "Knowledge segment not found"

        nodes_after = client.get(f"/knowledge/nodes?source_id={source_id}")
        assert nodes_after.status_code == 200
        assert nodes_after.json() == []

        with SessionLocal() as session:
            records = session.scalars(
                select(KnowledgeSegmentRecord).where(
                    KnowledgeSegmentRecord.index_entry_id == entry_id
                )
            ).all()
            assert len(records) == 2
            event = session.scalars(
                select(AuditEventRecord).where(
                    AuditEventRecord.event_type == "knowledge.segment.registered",
                    AuditEventRecord.entity_id == entry_id,
                )
            ).first()
            assert event is not None
            assert event.payload["segment_count"] == 2
            assert event.payload["interprets_text"] is False
            assert event.payload["summarizes_text"] is False
            assert event.payload["embeddings_created"] is False
            assert event.payload["nodes_created"] is False
            assert event.payload["knowledge_created"] is False
    finally:
        with SessionLocal() as session:
            session.query(AuditEventRecord).filter(
                AuditEventRecord.entity_id.in_([source_id, edition_id, entry_id])
            ).delete(synchronize_session=False)
            session.query(KnowledgeSegmentRecord).filter(
                KnowledgeSegmentRecord.index_entry_id == entry_id
            ).delete()
            session.query(KnowledgeIndexEntryRecord).filter(
                KnowledgeIndexEntryRecord.edition_id == edition_id
            ).delete()
            session.query(KnowledgeSourceEditionRecord).filter(
                KnowledgeSourceEditionRecord.id == edition_id
            ).delete()
            session.query(KnowledgeSourceRecord).filter(
                KnowledgeSourceRecord.id == source_id
            ).delete()
            session.commit()


def test_register_knowledge_extraction_run_is_auditable_without_creating_knowledge():
    source_id = "test-fuente-extraccion"
    edition_id = "test-fuente-extraccion:primera"
    entry_id = "test-fuente-extraccion:primera:sec-1-1"
    segment_id = "test-fuente-extraccion:primera:sec-1-1:seg-1"
    source_payload = {
        "id": source_id,
        "catalog_id": "TEST-F005",
        "name": "Fuente de prueba con extraccion",
        "responsible": "Equipo editorial",
        "source_type": "manual de prueba",
        "domains": ["sintaxis"],
        "authority_level": 3,
        "priority": 103,
    }
    edition_payload = {
        "id": edition_id,
        "source_id": source_id,
        "title": "Fuente de prueba con extraccion",
        "edition_label": "Primera edicion extraible",
        "publication_year": "2026",
        "publisher": "Editorial de prueba",
        "isbn": "978-0-000000-00-5",
        "language": "es",
        "format": "pdf",
        "access_location": "/tmp/fuente-extraccion.pdf",
        "rights_status": "uso local autorizado; contenido no ingerido",
        "status": "available",
        "notes": "Registro bibliografico para prueba de extraccion.",
    }
    index_payload = [
        {
            "id": entry_id,
            "edition_id": edition_id,
            "parent_id": None,
            "level": 1,
            "order": 1,
            "title": "Complemento directo",
            "locator": "capitulo 1 > 1.1",
            "page_start": "10",
            "page_end": "14",
            "status": "registered",
        }
    ]
    segment_payload = [
        {
            "id": segment_id,
            "index_entry_id": entry_id,
            "parent_segment_id": None,
            "segment_type": "paragraph",
            "title": "Parrafo inicial",
            "text": "El complemento directo aparece descrito en este apartado documental.",
            "order": 1,
            "start_locator": "capitulo 1 > 1.1 > p1",
            "end_locator": "capitulo 1 > 1.1 > p1",
            "language": "es",
            "status": "registered",
        }
    ]
    extraction_payload = {
        "extractor_type": "deterministic",
        "extractor_name": "manual-placeholder",
        "extractor_version": "1.0",
        "configuration": {"mode": "smoke"},
    }
    try:
        assert client.post("/knowledge/sources", json=source_payload).status_code == 200
        assert (
            client.post(f"/knowledge/sources/{source_id}/editions", json=edition_payload).status_code
            == 200
        )
        assert client.post(f"/knowledge/editions/{edition_id}/index", json=index_payload).status_code == 200
        assert client.post(f"/knowledge/index/{entry_id}/segments", json=segment_payload).status_code == 200

        response = client.post(
            f"/knowledge/segments/{segment_id}/extractions",
            json=extraction_payload,
        )
        assert response.status_code == 200
        completed = response.json()
        assert completed["id"].startswith("ext-")
        assert completed["segment_id"] == segment_id
        assert completed["status"] == "completed"
        assert completed["extractor_type"] == "deterministic"
        assert completed["extractor_name"] == "manual-placeholder"
        assert completed["extractor_version"] == "1.0"
        assert completed["configuration"] == {"mode": "smoke"}
        assert completed["input_segment_revision"] == 1
        assert len(completed["input_segment_hash"]) == 64
        assert completed["knowledge_version"] is None
        assert completed["started_at"]
        assert completed["completed_at"]
        assert completed["error_code"] is None
        assert completed["error_message"] is None

        retry = client.post(
            f"/knowledge/segments/{segment_id}/extractions",
            json=extraction_payload,
        )
        assert retry.status_code == 200
        retry_payload = retry.json()
        assert retry_payload["id"] != completed["id"]
        assert retry_payload["segment_id"] == segment_id

        failed = client.post(
            f"/knowledge/segments/{segment_id}/extractions",
            json={
                **extraction_payload,
                "status": "failed",
                "error_code": "parser_error",
                "error_message": "No se pudo leer el segmento.",
            },
        )
        assert failed.status_code == 200
        failed_payload = failed.json()
        assert failed_payload["status"] == "failed"
        assert failed_payload["error_code"] == "parser_error"
        assert failed_payload["error_message"] == "No se pudo leer el segmento."

        by_segment = client.get(f"/knowledge/segments/{segment_id}/extractions")
        assert by_segment.status_code == 200
        extraction_ids = [item["id"] for item in by_segment.json()]
        assert completed["id"] in extraction_ids
        assert retry_payload["id"] in extraction_ids
        assert failed_payload["id"] in extraction_ids

        detail = client.get(f"/knowledge/extractions/{completed['id']}")
        assert detail.status_code == 200
        assert detail.json()["id"] == completed["id"]

        missing_segment = client.post(
            "/knowledge/segments/segmento-inexistente/extractions",
            json=extraction_payload,
        )
        assert missing_segment.status_code == 404
        assert missing_segment.json()["detail"] == "Knowledge segment or version not found"

        missing_extraction = client.get("/knowledge/extractions/ext-inexistente")
        assert missing_extraction.status_code == 404
        assert missing_extraction.json()["detail"] == "Knowledge extraction not found"

        nodes_after = client.get(f"/knowledge/nodes?source_id={source_id}")
        assert nodes_after.status_code == 200
        assert nodes_after.json() == []
        with SessionLocal() as session:
            runs = session.scalars(
                select(KnowledgeExtractionRunRecord).where(
                    KnowledgeExtractionRunRecord.segment_id == segment_id
                )
            ).all()
            assert len(runs) == 3
            evidence = session.scalars(
                select(KnowledgeEvidenceItemRecord).where(
                    KnowledgeEvidenceItemRecord.source_id == source_id
                )
            ).all()
            assert evidence == []
            claims = session.scalars(
                select(KnowledgeClaimRecord).where(KnowledgeClaimRecord.node_id == source_id)
            ).all()
            assert claims == []
            cards = session.scalars(
                select(KnowledgeCardRecord).where(KnowledgeCardRecord.id.contains(source_id))
            ).all()
            assert cards == []
            registered = session.scalars(
                select(AuditEventRecord).where(
                    AuditEventRecord.event_type == "knowledge.extraction.registered",
                    AuditEventRecord.entity_id == completed["id"],
                )
            ).first()
            assert registered is not None
            assert registered.payload["proposals_created"] is False
            assert registered.payload["knowledge_created"] is False
            terminal = session.scalars(
                select(AuditEventRecord).where(
                    AuditEventRecord.event_type == "knowledge.extraction.completed",
                    AuditEventRecord.entity_id == completed["id"],
                )
            ).first()
            assert terminal is not None
            assert terminal.payload["proposals_created"] is False
            assert terminal.payload["nodes_created"] is False
            assert terminal.payload["evidence_created"] is False
            assert terminal.payload["claims_created"] is False
            assert terminal.payload["cards_created"] is False
            assert terminal.payload["published"] is False
            assert terminal.payload["embeddings_created"] is False
            failed_event = session.scalars(
                select(AuditEventRecord).where(
                    AuditEventRecord.event_type == "knowledge.extraction.failed",
                    AuditEventRecord.entity_id == failed_payload["id"],
                )
            ).first()
            assert failed_event is not None
            assert failed_event.payload["error_code"] == "parser_error"
    finally:
        with SessionLocal() as session:
            extraction_ids = [
                record.id
                for record in session.scalars(
                    select(KnowledgeExtractionRunRecord).where(
                        KnowledgeExtractionRunRecord.segment_id == segment_id
                    )
                ).all()
            ]
            session.query(AuditEventRecord).filter(
                AuditEventRecord.entity_id.in_([source_id, edition_id, entry_id, *extraction_ids])
            ).delete(synchronize_session=False)
            session.query(KnowledgeExtractionRunRecord).filter(
                KnowledgeExtractionRunRecord.segment_id == segment_id
            ).delete()
            session.query(KnowledgeSegmentRecord).filter(
                KnowledgeSegmentRecord.index_entry_id == entry_id
            ).delete()
            session.query(KnowledgeIndexEntryRecord).filter(
                KnowledgeIndexEntryRecord.edition_id == edition_id
            ).delete()
            session.query(KnowledgeSourceEditionRecord).filter(
                KnowledgeSourceEditionRecord.id == edition_id
            ).delete()
            session.query(KnowledgeSourceRecord).filter(
                KnowledgeSourceRecord.id == source_id
            ).delete()
            session.commit()


def test_register_knowledge_proposals_from_completed_extraction_without_stable_objects():
    source_id = "test-fuente-propuestas"
    edition_id = "test-fuente-propuestas:primera"
    entry_id = "test-fuente-propuestas:primera:sec-1-1"
    segment_id = "test-fuente-propuestas:primera:sec-1-1:seg-1"
    source_payload = {
        "id": source_id,
        "catalog_id": "TEST-F006",
        "name": "Fuente de prueba con propuestas",
        "responsible": "Equipo editorial",
        "source_type": "manual de prueba",
        "domains": ["sintaxis"],
        "authority_level": 3,
        "priority": 104,
    }
    edition_payload = {
        "id": edition_id,
        "source_id": source_id,
        "title": "Fuente de prueba con propuestas",
        "edition_label": "Primera edicion propositiva",
        "publication_year": "2026",
        "publisher": "Editorial de prueba",
        "isbn": "978-0-000000-00-6",
        "language": "es",
        "format": "pdf",
        "access_location": "/tmp/fuente-propuestas.pdf",
        "rights_status": "uso local autorizado; contenido no ingerido",
        "status": "available",
        "notes": "Registro bibliografico para prueba de propuestas.",
    }
    index_payload = [
        {
            "id": entry_id,
            "edition_id": edition_id,
            "parent_id": None,
            "level": 1,
            "order": 1,
            "title": "Complemento directo",
            "locator": "capitulo 1 > 1.1",
            "page_start": "10",
            "page_end": "14",
            "status": "registered",
        }
    ]
    segment_payload = [
        {
            "id": segment_id,
            "index_entry_id": entry_id,
            "parent_segment_id": None,
            "segment_type": "paragraph",
            "title": "Parrafo inicial",
            "text": "El complemento directo aparece descrito en este apartado documental.",
            "order": 1,
            "start_locator": "capitulo 1 > 1.1 > p1",
            "end_locator": "capitulo 1 > 1.1 > p1",
            "language": "es",
            "status": "registered",
        }
    ]
    extraction_payload = {
        "extractor_type": "deterministic",
        "extractor_name": "manual-placeholder",
        "extractor_version": "1.0",
        "configuration": {"mode": "proposal-smoke"},
    }
    proposal_payload = [
        {
            "proposal_type": "node",
            "title": "Complemento directo",
            "payload": {
                "canonical_name": "Complemento directo",
                "node_type": "concepto",
            },
            "rationale": "El segmento contiene un apartado documental con ese titulo.",
            "confidence": 0.72,
            "source_locator": "capitulo 1 > 1.1 > p1",
        },
        {
            "proposal_type": "evidence",
            "title": "Evidencia textual sobre complemento directo",
            "payload": {
                "excerpt": "El complemento directo aparece descrito en este apartado documental.",
            },
            "rationale": "El texto del segmento puede sustentar una evidencia candidata.",
            "confidence": 0.68,
            "source_locator": "capitulo 1 > 1.1 > p1",
        },
    ]
    try:
        assert client.post("/knowledge/sources", json=source_payload).status_code == 200
        assert (
            client.post(f"/knowledge/sources/{source_id}/editions", json=edition_payload).status_code
            == 200
        )
        assert client.post(f"/knowledge/editions/{edition_id}/index", json=index_payload).status_code == 200
        assert client.post(f"/knowledge/index/{entry_id}/segments", json=segment_payload).status_code == 200
        extraction_response = client.post(
            f"/knowledge/segments/{segment_id}/extractions",
            json=extraction_payload,
        )
        assert extraction_response.status_code == 200
        extraction = extraction_response.json()

        response = client.post(
            f"/knowledge/extractions/{extraction['id']}/proposals",
            json=proposal_payload,
        )
        assert response.status_code == 200
        proposals = response.json()
        assert len(proposals) == 2
        assert {proposal["proposal_type"] for proposal in proposals} == {"node", "evidence"}
        assert {proposal["status"] for proposal in proposals} == {"proposed"}
        assert {proposal["segment_id"] for proposal in proposals} == {segment_id}
        assert {proposal["extraction_id"] for proposal in proposals} == {extraction["id"]}
        assert proposals[0]["payload"]["canonical_name"] == "Complemento directo"
        assert proposals[0]["reviewed_at"] is None
        assert proposals[0]["reviewer"] is None
        assert proposals[0]["decision_reason"] is None

        listed = client.get(f"/knowledge/extractions/{extraction['id']}/proposals")
        assert listed.status_code == 200
        assert {proposal["id"] for proposal in listed.json()} == {
            proposal["id"] for proposal in proposals
        }

        detail = client.get(f"/knowledge/proposals/{proposals[0]['id']}")
        assert detail.status_code == 200
        assert detail.json()["id"] == proposals[0]["id"]

        failed_extraction = client.post(
            f"/knowledge/segments/{segment_id}/extractions",
            json={
                **extraction_payload,
                "status": "failed",
                "error_code": "parser_error",
            },
        ).json()
        failed_proposal = client.post(
            f"/knowledge/extractions/{failed_extraction['id']}/proposals",
            json=proposal_payload,
        )
        assert failed_proposal.status_code == 409
        assert failed_proposal.json()["detail"] == (
            "Knowledge proposals require a completed extraction"
        )

        missing_extraction = client.post(
            "/knowledge/extractions/ext-inexistente/proposals",
            json=proposal_payload,
        )
        assert missing_extraction.status_code == 404
        assert missing_extraction.json()["detail"] == "Knowledge extraction not found"

        missing_proposal = client.get("/knowledge/proposals/prop-inexistente")
        assert missing_proposal.status_code == 404
        assert missing_proposal.json()["detail"] == "Knowledge proposal not found"

        nodes_after = client.get(f"/knowledge/nodes?source_id={source_id}")
        assert nodes_after.status_code == 200
        assert nodes_after.json() == []

        with SessionLocal() as session:
            proposal_records = session.scalars(
                select(KnowledgeProposalRecord).where(
                    KnowledgeProposalRecord.extraction_id == extraction["id"]
                )
            ).all()
            assert len(proposal_records) == 2
            evidence = session.scalars(
                select(KnowledgeEvidenceItemRecord).where(
                    KnowledgeEvidenceItemRecord.source_id == source_id
                )
            ).all()
            assert evidence == []
            claims = session.scalars(
                select(KnowledgeClaimRecord).where(KnowledgeClaimRecord.node_id == source_id)
            ).all()
            assert claims == []
            cards = session.scalars(
                select(KnowledgeCardRecord).where(KnowledgeCardRecord.id.contains(source_id))
            ).all()
            assert cards == []
            event = session.scalars(
                select(AuditEventRecord).where(
                    AuditEventRecord.event_type == "knowledge.proposal.registered",
                    AuditEventRecord.entity_id == extraction["id"],
                )
            ).first()
            assert event is not None
            assert event.payload["proposal_count"] == 2
            assert event.payload["proposal_types"] == ["node", "evidence"]
            assert event.payload["nodes_created"] is False
            assert event.payload["evidence_created"] is False
            assert event.payload["claims_created"] is False
            assert event.payload["cards_created"] is False
            assert event.payload["published"] is False
            assert event.payload["stable_knowledge_created"] is False
    finally:
        with SessionLocal() as session:
            extraction_ids = [
                record.id
                for record in session.scalars(
                    select(KnowledgeExtractionRunRecord).where(
                        KnowledgeExtractionRunRecord.segment_id == segment_id
                    )
                ).all()
            ]
            session.query(AuditEventRecord).filter(
                AuditEventRecord.entity_id.in_([source_id, edition_id, entry_id, *extraction_ids])
            ).delete(synchronize_session=False)
            session.query(KnowledgeProposalRecord).filter(
                KnowledgeProposalRecord.extraction_id.in_(extraction_ids)
            ).delete(synchronize_session=False)
            session.query(KnowledgeExtractionRunRecord).filter(
                KnowledgeExtractionRunRecord.segment_id == segment_id
            ).delete()
            session.query(KnowledgeSegmentRecord).filter(
                KnowledgeSegmentRecord.index_entry_id == entry_id
            ).delete()
            session.query(KnowledgeIndexEntryRecord).filter(
                KnowledgeIndexEntryRecord.edition_id == edition_id
            ).delete()
            session.query(KnowledgeSourceEditionRecord).filter(
                KnowledgeSourceEditionRecord.id == edition_id
            ).delete()
            session.query(KnowledgeSourceRecord).filter(
                KnowledgeSourceRecord.id == source_id
            ).delete()
            session.commit()


def test_approve_and_reject_knowledge_proposals_review_stable_objects():
    entry_id = "test-review-proposals-entry"
    segment_id = "test-review-proposals-segment"
    node_id = "test-review-proposals-node"
    evidence_id = "test-review-proposals-evidence"
    claim_id = "test-review-proposals-claim"
    decision = {
        "reviewer": "test-editor",
        "reason": "revision editorial de prueba",
    }
    proposals: list[dict] = []
    try:
        assert client.post(
            "/knowledge/editions/rae-ngle:pending-edition/index",
            json=[
                {
                    "id": entry_id,
                    "edition_id": "rae-ngle:pending-edition",
                    "parent_id": None,
                    "level": 1,
                    "order": 97,
                    "title": "Aprobacion de propuestas",
                    "locator": "smoke editorial > 1",
                    "page_start": "1",
                    "page_end": "2",
                    "status": "registered",
                }
            ],
        ).status_code == 200
        assert client.post(
            f"/knowledge/index/{entry_id}/segments",
            json=[
                {
                    "id": segment_id,
                    "index_entry_id": entry_id,
                    "parent_segment_id": None,
                    "segment_type": "paragraph",
                    "title": "Segmento editorial",
                    "text": "La revision editorial convierte propuestas en objetos trazables.",
                    "order": 1,
                    "start_locator": "smoke editorial > 1 > p1",
                    "end_locator": "smoke editorial > 1 > p1",
                    "language": "es",
                    "status": "registered",
                }
            ],
        ).status_code == 200
        extraction = client.post(
            f"/knowledge/segments/{segment_id}/extractions",
            json={
                "extractor_type": "deterministic",
                "extractor_name": "manual-placeholder",
                "extractor_version": "1.0",
                "configuration": {"mode": "review-proposals"},
            },
        ).json()
        response = client.post(
            f"/knowledge/extractions/{extraction['id']}/proposals",
            json=[
                {
                    "proposal_type": "node",
                    "title": "Nodo editorial de prueba",
                    "payload": {
                        "id": node_id,
                        "source_id": "rae-ngle",
                        "node_type": "concepto",
                        "title": "Nodo editorial de prueba",
                        "summary": "Nodo aprobado desde una propuesta editorial.",
                        "canonical_name": "Nodo editorial de prueba",
                        "primary_branch": "lengua espanola",
                        "secondary_branch": "auditoria",
                        "short_definition": "Concepto de prueba aprobado.",
                        "long_definition": "Concepto creado para probar la revision editorial de propuestas.",
                        "aliases": ["propuesta aprobada"],
                    },
                    "rationale": "El segmento propone un nodo revisable.",
                    "confidence": 0.81,
                    "source_locator": "smoke editorial > 1 > p1",
                },
                {
                    "proposal_type": "evidence",
                    "title": "Evidencia editorial de prueba",
                    "payload": {
                        "id": evidence_id,
                        "node_id": node_id,
                        "source_id": "rae-ngle",
                        "source_edition_id": "rae-ngle:pending-edition",
                        "evidence_type": "documented_paraphrase",
                        "locator": {
                            "catalog_id": "F001",
                            "edition": "pendiente de identificacion",
                            "unit": "smoke editorial",
                            "locator": "smoke editorial > 1 > p1",
                            "url": None,
                        },
                        "reference": "smoke editorial > 1 > p1",
                        "excerpt": "La revision editorial convierte propuestas en objetos trazables.",
                        "context": "reviewed_proposal",
                        "confidence_level": 4,
                    },
                    "rationale": "La evidencia procede del segmento revisado.",
                    "confidence": 0.82,
                    "source_locator": "smoke editorial > 1 > p1",
                },
                {
                    "proposal_type": "claim",
                    "title": "Claim editorial de prueba",
                    "payload": {
                        "id": claim_id,
                        "evidence_id": evidence_id,
                        "card_id": "lexico-precision",
                        "statement": "Las propuestas aprobadas se transforman en objetos trazables.",
                        "claim_type": "architectural",
                        "node_id": node_id,
                        "related_node_ids": ["rae-norma-estilo"],
                        "domain": "knowledge.review",
                        "scope": {"language": "es", "register": "technical"},
                    },
                    "rationale": "El claim queda sustentado por la evidencia aprobada.",
                    "confidence": 0.83,
                    "source_locator": "smoke editorial > 1 > p1",
                },
                {
                    "proposal_type": "definition",
                    "title": "Definicion no mutable",
                    "payload": {"node_id": node_id, "definition": "No mutar silenciosamente."},
                    "rationale": "Las definiciones requieren regla de mutacion versionada.",
                    "confidence": 0.5,
                    "source_locator": "smoke editorial > 1 > p1",
                },
            ],
        )
        assert response.status_code == 200
        proposals = response.json()
        proposal_by_type = {proposal["proposal_type"]: proposal for proposal in proposals}

        approved_node = client.post(
            f"/knowledge/proposals/{proposal_by_type['node']['id']}/approve",
            json=decision,
        )
        assert approved_node.status_code == 200
        assert approved_node.json()["status"] == "approved"

        approved_evidence = client.post(
            f"/knowledge/proposals/{proposal_by_type['evidence']['id']}/approve",
            json=decision,
        )
        assert approved_evidence.status_code == 200
        assert approved_evidence.json()["status"] == "approved"

        approved_claim = client.post(
            f"/knowledge/proposals/{proposal_by_type['claim']['id']}/approve",
            json=decision,
        )
        assert approved_claim.status_code == 200
        assert approved_claim.json()["status"] == "approved"

        repeated_approval = client.post(
            f"/knowledge/proposals/{proposal_by_type['claim']['id']}/approve",
            json=decision,
        )
        assert repeated_approval.status_code == 409
        assert repeated_approval.json()["detail"] == "Knowledge proposal is already decided"

        rejected_definition = client.post(
            f"/knowledge/proposals/{proposal_by_type['definition']['id']}/reject",
            json=decision,
        )
        assert rejected_definition.status_code == 200
        assert rejected_definition.json()["status"] == "rejected"

        unsupported_definition = client.post(
            f"/knowledge/proposals/{proposal_by_type['definition']['id']}/approve",
            json=decision,
        )
        assert unsupported_definition.status_code == 409
        assert unsupported_definition.json()["detail"] == "Knowledge proposal is already decided"

        with SessionLocal() as session:
            node = session.get(KnowledgeNodeRecord, node_id)
            assert node is not None
            assert node.status == "validated"
            assert node.published_at == "not-published"
            evidence = session.get(KnowledgeEvidenceItemRecord, evidence_id)
            assert evidence is not None
            assert evidence.status == "validated"
            assert evidence.reviewed_by == "test-editor"
            claim = session.get(KnowledgeClaimRecord, claim_id)
            assert claim is not None
            assert claim.status == "validated"
            assert claim.published_at is None
            link = session.get(
                KnowledgeClaimEvidenceLinkRecord,
                f"{claim_id}:{evidence_id}:primary",
            )
            assert link is not None
            assert link.role == "primary"
            node_revision = session.get(KnowledgeObjectRevisionRecord, f"{node_id}:r1")
            assert node_revision is not None
            assert node_revision.change_type == "created_from_proposal"
            assert node_revision.status == "validated"
            approved_event = session.scalars(
                select(AuditEventRecord).where(
                    AuditEventRecord.event_type == "knowledge.proposal.approved",
                    AuditEventRecord.entity_id == proposal_by_type["claim"]["id"],
                )
            ).first()
            assert approved_event is not None
            assert approved_event.payload["target_type"] == "claim"
            assert approved_event.payload["published"] is False
            rejected_event = session.scalars(
                select(AuditEventRecord).where(
                    AuditEventRecord.event_type == "knowledge.proposal.rejected",
                    AuditEventRecord.entity_id == proposal_by_type["definition"]["id"],
                )
            ).first()
            assert rejected_event is not None
            assert rejected_event.payload["stable_knowledge_created"] is False
    finally:
        proposal_ids = [proposal["id"] for proposal in proposals]
        with SessionLocal() as session:
            session.query(AuditEventRecord).filter(
                AuditEventRecord.entity_id.in_(
                    [entry_id, extraction["id"] if "extraction" in locals() else "", *proposal_ids]
                )
            ).delete(synchronize_session=False)
            session.query(KnowledgeClaimRevisionRecord).filter(
                KnowledgeClaimRevisionRecord.claim_id == claim_id
            ).delete(synchronize_session=False)
            session.query(KnowledgeClaimEvidenceLinkRecord).filter(
                KnowledgeClaimEvidenceLinkRecord.claim_id == claim_id
            ).delete(synchronize_session=False)
            session.query(KnowledgeClaimRecord).filter(
                KnowledgeClaimRecord.id == claim_id
            ).delete(synchronize_session=False)
            session.query(KnowledgeEvidenceRevisionRecord).filter(
                KnowledgeEvidenceRevisionRecord.evidence_id == evidence_id
            ).delete(synchronize_session=False)
            session.query(KnowledgeEvidenceItemRecord).filter(
                KnowledgeEvidenceItemRecord.id == evidence_id
            ).delete(synchronize_session=False)
            session.query(KnowledgeObjectRevisionRecord).filter(
                KnowledgeObjectRevisionRecord.object_id == node_id
            ).delete(synchronize_session=False)
            session.query(KnowledgeNodeRecord).filter(
                KnowledgeNodeRecord.id == node_id
            ).delete(synchronize_session=False)
            if "extraction" in locals():
                session.query(KnowledgeProposalRecord).filter(
                    KnowledgeProposalRecord.extraction_id == extraction["id"]
                ).delete(synchronize_session=False)
                session.query(KnowledgeExtractionRunRecord).filter(
                    KnowledgeExtractionRunRecord.id == extraction["id"]
                ).delete(synchronize_session=False)
            session.query(KnowledgeSegmentRecord).filter(
                KnowledgeSegmentRecord.id == segment_id
            ).delete(synchronize_session=False)
            session.query(KnowledgeIndexEntryRecord).filter(
                KnowledgeIndexEntryRecord.id == entry_id
            ).delete(synchronize_session=False)
            session.commit()


def test_knowledge_nodes_link_to_sources():
    response = client.get("/knowledge/nodes")
    assert response.status_code == 200

    nodes = response.json()
    source_ids = {source["id"] for source in client.get("/knowledge/sources").json()}
    assert len(nodes) >= 1
    assert {node["source_id"] for node in nodes} <= source_ids
    assert all(node["canonical_name"] for node in nodes)
    assert all(node["primary_branch"] for node in nodes)
    assert all(node["secondary_branch"] for node in nodes)
    assert all(node["short_definition"] for node in nodes)
    assert all(node["long_definition"] for node in nodes)
    assert {node["status"] for node in nodes} == {"published"}
    assert all(node["created_at"] == "2026-07-22" for node in nodes)
    assert all(node["published_at"] == "2026-07-22" for node in nodes)
    assert all(len(node["relations"]) >= 1 for node in nodes)
    assert all(relation["direction"] == "outgoing" for node in nodes for relation in node["relations"])
    assert all(relation["cardinality"] == "N:N" for node in nodes for relation in node["relations"])
    assert all(0 <= relation["weight"] <= 1 for node in nodes for relation in node["relations"])
    assert all(0 <= relation["confidence"] <= 1 for node in nodes for relation in node["relations"])
    assert all(relation["context"] for node in nodes for relation in node["relations"])
    assert {relation["status"] for node in nodes for relation in node["relations"]} == {"published"}
    assert all(
        relation["updated_at"] == "2026-07-23" for node in nodes for relation in node["relations"]
    )
    assert {
        relation["relation_type"]
        for node in nodes
        for relation in node["relations"]
    } <= {
        "es_parte_de",
        "contiene",
        "depende_de",
        "contradice",
        "equivale_a",
        "ejemplifica",
        "define",
        "usa",
        "describe",
        "aparece_en",
        "estudiado_por",
        "deriva_de",
        "requiere",
        "compara_con",
        "relacionado_con",
    }

    filtered = client.get("/knowledge/nodes?source_id=rae-ngle")
    assert filtered.status_code == 200
    assert all(node["source_id"] == "rae-ngle" for node in filtered.json())

    versioned = client.get("/knowledge/nodes?source_id=rae-ngle&version=knowledge-v0")
    assert versioned.status_code == 200
    assert versioned.json()[0]["id"] == "rae-norma-estilo"
    assert versioned.json()[0]["canonical_name"] == "Norma y uso en lengua espanola"
    assert versioned.json()[0]["relations"][0]["target_node_id"] == "manual-rasgos-escritura"

    missing_version = client.get("/knowledge/nodes?version=missing-version")
    assert missing_version.status_code == 404
    assert missing_version.json()["detail"] == "Knowledge version not found"


def test_knowledge_relations_expose_typed_graph():
    response = client.get("/knowledge/relations?version=knowledge-v0")
    assert response.status_code == 200
    relations = response.json()
    assert len(relations) >= 1
    assert all(relation["source_entity_type"] for relation in relations)
    assert all(relation["source_entity_id"] for relation in relations)
    assert all(relation["target_entity_type"] for relation in relations)
    assert all(relation["target_entity_id"] for relation in relations)
    assert all(relation["relation_type"] for relation in relations)
    assert all(relation["direction"] == "outgoing" for relation in relations)
    assert {relation["cardinality"] for relation in relations} <= {"1:1", "1:N", "N:1", "N:N"}
    assert all(0 <= relation["weight"] <= 1 for relation in relations)
    assert all(0 <= relation["confidence"] <= 1 for relation in relations)
    assert all(relation["context"] for relation in relations)
    assert {relation["status"] for relation in relations} <= {
        "draft",
        "validated",
        "published",
        "deprecated",
        "archived",
    }
    assert all(relation["version"] == "knowledge-v0" for relation in relations)
    assert all(relation["updated_at"] == "2026-07-23" for relation in relations)
    assert {
        ("source", "contiene", "source_edition"),
        ("node", "sostenido_por", "evidence"),
        ("evidence", "sostenido_por", "claim"),
        ("claim", "aplicacion_de", "knowledge_card"),
    } <= {
        (
            relation["source_entity_type"],
            relation["relation_type"],
            relation["target_entity_type"],
        )
        for relation in relations
    }

    filtered = client.get(
        "/knowledge/relations?version=knowledge-v0&source_entity_type=node&relation_type=sostenido_por"
    )
    assert filtered.status_code == 200
    assert all(relation["source_entity_type"] == "node" for relation in filtered.json())
    assert all(relation["relation_type"] == "sostenido_por" for relation in filtered.json())

    missing_version = client.get("/knowledge/relations?version=missing-version")
    assert missing_version.status_code == 404
    assert missing_version.json()["detail"] == "Knowledge version not found"


def test_knowledge_evidence_and_claims_link_nodes_to_cards():
    evidence = client.get("/knowledge/evidence")
    assert evidence.status_code == 200
    evidence_payload = evidence.json()

    nodes = {node["id"] for node in client.get("/knowledge/nodes").json()}
    source_payload = client.get("/knowledge/sources").json()
    sources = {source["id"] for source in source_payload}
    source_editions = {
        edition["id"]
        for source in source_payload
        for edition in source["editions"]
    }
    assert len(evidence_payload) >= 1
    assert {item["node_id"] for item in evidence_payload} <= nodes
    assert {item["source_id"] for item in evidence_payload} <= sources
    assert {item["source_edition_id"] for item in evidence_payload} <= source_editions
    assert all(item["evidence_type"] == "documented_paraphrase" for item in evidence_payload)
    assert all(item["locator"]["locator"] for item in evidence_payload)
    assert all(item["context"] in {"general_rule", "commentary"} for item in evidence_payload)
    assert {item["confidence_level"] for item in evidence_payload} == {2}
    assert {item["status"] for item in evidence_payload} == {"draft"}
    assert all(item["created_at"] == "2026-07-22" for item in evidence_payload)
    assert all(item["updated_at"] == "2026-07-22" for item in evidence_payload)
    assert {item["incorporated_by"] for item in evidence_payload} == {"minicerebro-seed"}
    assert {item["reviewed_by"] for item in evidence_payload} == {None}
    assert {item["revision"] for item in evidence_payload} == {1}

    claims = client.get("/knowledge/claims")
    assert claims.status_code == 200
    claim_payload = claims.json()
    card_ids = {card["id"] for card in client.get("/knowledge/cards").json()}
    evidence_ids = {item["id"] for item in evidence_payload}
    assert len(claim_payload) >= 1
    assert {claim["evidence_id"] for claim in claim_payload} <= evidence_ids
    assert {claim["card_id"] for claim in claim_payload} <= card_ids
    assert {claim["node_id"] for claim in claim_payload} <= nodes
    assert {claim["claim_type"] for claim in claim_payload} == {"stylistic"}
    assert all(claim["domain"] for claim in claim_payload)
    assert all(claim["scope"]["language"] == "es" for claim in claim_payload)
    assert all(claim["scope"]["register"] == "general" for claim in claim_payload)
    assert {claim["status"] for claim in claim_payload} == {"draft"}
    assert {claim["origin"] for claim in claim_payload} == {"seed_contract_entry"}
    assert {claim["revision"] for claim in claim_payload} == {1}
    assert {claim["published_at"] for claim in claim_payload} == {None}
    assert all(len(claim["evidence_links"]) >= 1 for claim in claim_payload)
    assert {
        link["role"]
        for claim in claim_payload
        for link in claim["evidence_links"]
    } == {"primary"}
    assert {
        link["evidence_id"]
        for claim in claim_payload
        for link in claim["evidence_links"]
    } <= evidence_ids

    filtered = client.get("/knowledge/claims?card_id=lexico-precision")
    assert filtered.status_code == 200
    assert all(claim["card_id"] == "lexico-precision" for claim in filtered.json())

    versioned_evidence = client.get(
        "/knowledge/evidence?node_id=rae-norma-estilo&version=knowledge-v0"
    )
    assert versioned_evidence.status_code == 200
    assert [item["id"] for item in versioned_evidence.json()] == ["ev-precision-lexica"]
    assert versioned_evidence.json()[0]["source_edition_id"] == "rae-dle:pending-edition"

    missing_evidence = client.get("/knowledge/evidence?version=missing-version")
    assert missing_evidence.status_code == 404
    assert missing_evidence.json()["detail"] == "Knowledge version not found"

    versioned_claims = client.get(
        "/knowledge/claims?card_id=lexico-precision&version=knowledge-v0"
    )
    assert versioned_claims.status_code == 200
    assert [claim["id"] for claim in versioned_claims.json()] == ["claim-precision-lexica"]
    assert versioned_claims.json()[0]["node_id"] == "rae-norma-estilo"
    assert versioned_claims.json()[0]["evidence_links"][0]["role"] == "primary"

    missing_claims = client.get("/knowledge/claims?version=missing-version")
    assert missing_claims.status_code == 404
    assert missing_claims.json()["detail"] == "Knowledge version not found"


def test_knowledge_cards_can_be_scoped_by_version():
    versioned = client.get("/knowledge/cards?version=knowledge-v0")
    assert versioned.status_code == 200
    assert {card["id"] for card in versioned.json()} == {
        "frase-dinamismo",
        "lexico-precision",
        "voz-sobriedad",
    }

    missing_version = client.get("/knowledge/cards?version=missing-version")
    assert missing_version.status_code == 404
    assert missing_version.json()["detail"] == "Knowledge version not found"


def test_knowledge_versions_include_chain_counts():
    response = client.get("/knowledge/versions")
    assert response.status_code == 200

    versions = response.json()
    version_sources = client.get("/knowledge/sources?version=knowledge-v0").json()
    assert versions[0]["id"] == "knowledge-v0"
    assert versions[0]["source_count"] == len(version_sources)
    assert versions[0]["node_count"] >= 1
    assert versions[0]["evidence_count"] >= 1
    assert versions[0]["claim_count"] >= 1
    assert versions[0]["card_count"] >= 1


def test_knowledge_versioning_policy_separates_stable_knowledge_from_profile_state():
    response = client.get("/knowledge/versioning")
    assert response.status_code == 200
    policy = response.json()

    assert {
        "source",
        "source_edition",
        "node",
        "relation",
        "evidence",
        "claim",
        "knowledge_card",
        "tree",
        "ontology",
        "schema",
        "knowledge_version",
    } <= set(policy["versioned_object_types"])
    assert {
        "profile",
        "preference",
        "scoring",
        "feedback",
        "laboratory",
        "prompt",
        "query",
        "generation",
        "user_history",
        "temporary_event",
    } <= set(policy["excluded_object_types"])
    assert policy["versioning_levels"] == [
        "revision",
        "object_version",
        "knowledge_version",
        "release",
    ]
    assert "cambia la confianza" in policy["revision_triggers"]
    assert "cambia el localizador" in policy["revision_triggers"]
    assert "cambia un alias" in policy["revision_triggers"]
    assert "cache" in policy["non_revision_changes"]
    assert policy["immutable_after_publication"] is True
    assert {"active", "superseded", "deprecated", "withdrawn", "archived"} <= set(
        policy["object_statuses"]
    )
    assert {
        "author",
        "created_at",
        "updated_at",
        "reason",
        "change_type",
        "object_id",
        "before",
        "after",
        "previous_revision",
    } <= set(policy["history_fields"])
    assert policy["source_versioning_levels"] == [
        "logical_source",
        "edition",
        "document_version",
    ]
    assert {
        "version.created",
        "revision.created",
        "revision.published",
        "revision.superseded",
        "knowledge.published",
        "knowledge.archived",
    } <= set(policy["audit_events"])
    assert "no puede existir una revision sin objeto" in policy["integrity_rules"]
    assert policy["publication_failure_state"] == "cancelled"
    assert "revision_number" in policy["identifiers"]
    assert "object_id" in policy["identifiers"]
    assert "knowledge_version" in policy["identifiers"]
    assert "release" in policy["identifiers"]
    assert "knowledge-v0" in policy["release_chain"]
    assert "la publicacion genera una instantanea inmutable" in policy["acceptance_criteria"]
    assert "que lo sustituyo despues" in policy["closure_questions"]
    assert "relaciones tipadas y versionadas" in policy["publication_checks"]


def test_knowledge_publication_policy_closes_publication_contract():
    response = client.get("/knowledge/publication")
    assert response.status_code == 200
    policy = response.json()

    assert "conocimiento estable recuperable" in policy["meaning"]
    assert policy["publication_unit"] == "knowledge_version"
    assert {"source", "node", "claim"} <= set(policy["non_publication_units"])
    assert policy["lifecycle"] == [
        "draft",
        "review",
        "validated",
        "candidate",
        "published",
        "deprecated",
        "archived",
    ]
    assert {
        "integridad referencial",
        "sin nodos huerfanos",
        "sin claims sin evidencia",
        "sin evidencias sin fuente",
        "sin fichas vacias",
        "sin relaciones rotas",
        "sin conflictos criticos",
    } <= set(policy["requirements"])
    assert {"estructura", "documentacion", "consistencia", "tests"} <= set(
        policy["validations"]
    )
    assert {"congelar version", "crear snapshot completo", "registrar auditoria"} <= set(
        policy["publication_effects"]
    )
    assert policy["immutable_after_publication"] is True
    assert policy["partial_publications_allowed"] is False
    assert {"author", "created_at", "object", "reason", "base_version"} <= set(
        policy["audit_fields"]
    )
    assert "published_at contiene una fecha concreta" in policy["closure_criteria"]


def test_knowledge_publication_readiness_reports_real_blockers():
    response = client.get("/knowledge/publication/readiness?version=knowledge-v0")
    assert response.status_code == 200
    readiness = response.json()

    assert readiness["version"] == "knowledge-v0"
    assert readiness["status"] == "seed"
    assert readiness["publication_unit"] == "knowledge_version"
    assert readiness["partial_publications_allowed"] is False
    assert readiness["publishable"] is False
    assert "validacion documental completa" in readiness["blockers"]
    checks = {check["id"]: check for check in readiness["checks"]}
    assert checks["orphan_nodes"]["passed"] is True
    assert checks["claims_without_evidence"]["passed"] is True
    assert checks["evidence_without_source"]["passed"] is True
    assert checks["empty_cards"]["passed"] is True
    assert checks["broken_relations"]["passed"] is True
    assert checks["documentation_validated"]["passed"] is False
    assert readiness["audit_preview"]["event_type"] == "knowledge.published"
    assert readiness["audit_preview"]["entity_id"] == "knowledge-v0"

    missing_version = client.get("/knowledge/publication/readiness?version=missing-version")
    assert missing_version.status_code == 404
    assert missing_version.json()["detail"] == "Knowledge version not found"


def test_candidate_version_creates_snapshot_and_publication_requires_gates():
    candidate_id = "test-candidate-publication"
    candidate_payload = {
        "id": candidate_id,
        "base_version": "knowledge-v0",
        "author": "test-suite",
        "reason": "probar publicacion real bloqueada por gates",
    }
    try:
        response = client.post("/knowledge/candidates", json=candidate_payload)
        assert response.status_code == 200
        candidate = response.json()
        assert candidate["id"] == candidate_id
        assert candidate["status"] == "candidate"
        assert candidate["published_at"] == "not-published"
        assert candidate["source_count"] == 0
        assert candidate["node_count"] == 0
        assert candidate["evidence_count"] == 0
        assert candidate["claim_count"] == 0
        assert candidate["card_count"] == 0

        with SessionLocal() as session:
            snapshot = session.get(KnowledgeVersionSnapshotRecord, candidate_id)
            assert snapshot is not None
            assert snapshot.status == "candidate"
            assert len(snapshot.source_ids) == candidate["source_count"]
            assert len(snapshot.evidence_ids) == candidate["evidence_count"]
            assert len(snapshot.claim_ids) == candidate["claim_count"]

        duplicate = client.post("/knowledge/candidates", json=candidate_payload)
        assert duplicate.status_code == 409
        assert duplicate.json()["detail"] == "Knowledge version already exists"

        missing_base = client.post(
            "/knowledge/candidates",
            json={
                **candidate_payload,
                "id": "test-candidate-missing-base",
                "base_version": "missing-version",
            },
        )
        assert missing_base.status_code == 404
        assert missing_base.json()["detail"] == "Base knowledge version not found"

        blocked_publication = client.post(
            "/knowledge/publications",
            json={
                "version": candidate_id,
                "author": "test-suite",
                "reason": "intento de publicacion con blockers",
            },
        )
        assert blocked_publication.status_code == 409
        assert "Knowledge version is not publishable" in blocked_publication.json()["detail"]
        assert "snapshot de conocimiento no vacio" in blocked_publication.json()["detail"]

        seed_publication = client.post(
            "/knowledge/publications",
            json={
                "version": "knowledge-v0",
                "author": "test-suite",
                "reason": "seed no es candidate",
            },
        )
        assert seed_publication.status_code == 409
        assert seed_publication.json()["detail"] == (
            "Knowledge publication requires a candidate or validated version"
        )

        missing_publication = client.post(
            "/knowledge/publications",
            json={
                "version": "missing-version",
                "author": "test-suite",
                "reason": "version inexistente",
            },
        )
        assert missing_publication.status_code == 404
        assert missing_publication.json()["detail"] == "Knowledge version not found"

        with SessionLocal() as session:
            event = session.scalars(
                select(AuditEventRecord).where(
                    AuditEventRecord.event_type == "knowledge.candidate.created",
                    AuditEventRecord.entity_id == candidate_id,
                )
            ).first()
            assert event is not None
            assert event.payload["snapshot_created"] is True
            assert event.payload["publication_created"] is False
    finally:
        with SessionLocal() as session:
            session.query(AuditEventRecord).filter(
                AuditEventRecord.entity_id.in_(
                    [candidate_id, "test-candidate-missing-base", "missing-version"]
                )
            ).delete(synchronize_session=False)
            session.query(KnowledgeVersionSnapshotRecord).filter(
                KnowledgeVersionSnapshotRecord.version_id == candidate_id
            ).delete(synchronize_session=False)
            session.query(KnowledgeVersionRecord).filter(
                KnowledgeVersionRecord.id == candidate_id
            ).delete(synchronize_session=False)
            session.commit()


def test_candidate_publication_promotes_validated_snapshot_to_published():
    candidate_id = "test-candidate-published"
    source_id = "test-publication-source"
    edition_id = "test-publication-source:edition"
    entry_id = "test-publication-source:edition:index"
    segment_id = "test-publication-source:edition:index:seg"
    node_id = "test-publication-node"
    evidence_id = "test-publication-evidence"
    claim_id = "test-publication-claim"
    relation_id = "test-publication-relation"
    decision = {
        "reviewer": "test-editor",
        "reason": "validar cadena candidata para publicacion",
    }
    proposals: list[dict] = []
    extraction: dict | None = None
    try:
        source_response = client.post(
            "/knowledge/sources",
            json={
                "id": source_id,
                "catalog_id": "TEST-PUB-001",
                "name": "Fuente validada para publicacion",
                "responsible": "Equipo editorial",
                "source_type": "manual de prueba",
                "domains": ["trazabilidad"],
                "authority_level": 4,
                "priority": 180,
                "status": "registered",
                "acquisition_status": "available",
                "validation_status": "validated",
                "rights": "uso local autorizado; contenido no ingerido automaticamente",
                "structure": ["capitulo", "seccion"],
            },
        )
        assert source_response.status_code == 200
        assert client.post(
            f"/knowledge/sources/{source_id}/editions",
            json={
                "id": edition_id,
                "source_id": source_id,
                "title": "Fuente validada para publicacion",
                "edition_label": "Edicion de prueba",
                "publication_year": "2026",
                "publisher": "Editorial de prueba",
                "isbn": "978-0-000000-01-7",
                "language": "es",
                "format": "pdf",
                "access_location": "/tmp/fuente-publicacion.pdf",
                "rights_status": "uso local autorizado; contenido no ingerido automaticamente",
                "status": "available",
                "notes": "Edicion usada para probar publicacion real.",
            },
        ).status_code == 200
        assert client.post(
            f"/knowledge/editions/{edition_id}/index",
            json=[
                {
                    "id": entry_id,
                    "edition_id": edition_id,
                    "parent_id": None,
                    "level": 1,
                    "order": 1,
                    "title": "Trazabilidad editorial",
                    "locator": "capitulo 1",
                    "page_start": "1",
                    "page_end": "4",
                    "status": "registered",
                }
            ],
        ).status_code == 200
        assert client.post(
            f"/knowledge/index/{entry_id}/segments",
            json=[
                {
                    "id": segment_id,
                    "index_entry_id": entry_id,
                    "parent_segment_id": None,
                    "segment_type": "paragraph",
                    "title": "Segmento publicable",
                    "text": "La publicacion convierte objetos validados en conocimiento trazable.",
                    "order": 1,
                    "start_locator": "capitulo 1 > p1",
                    "end_locator": "capitulo 1 > p1",
                    "language": "es",
                    "status": "registered",
                }
            ],
        ).status_code == 200
        extraction_response = client.post(
            f"/knowledge/segments/{segment_id}/extractions",
            json={
                "extractor_type": "deterministic",
                "extractor_name": "manual-placeholder",
                "extractor_version": "1.0",
                "configuration": {"mode": "publication-promotion"},
            },
        )
        assert extraction_response.status_code == 200
        extraction = extraction_response.json()
        response = client.post(
            f"/knowledge/extractions/{extraction['id']}/proposals",
            json=[
                {
                    "proposal_type": "node",
                    "title": "Nodo publicable de prueba",
                    "payload": {
                        "id": node_id,
                        "source_id": source_id,
                        "node_type": "concepto",
                        "title": "Nodo publicable de prueba",
                        "summary": "Nodo validado para probar publicacion.",
                        "canonical_name": "Nodo publicable de prueba",
                        "primary_branch": "lengua espanola",
                        "secondary_branch": "trazabilidad",
                        "short_definition": "Concepto validado para publicacion.",
                        "long_definition": (
                            "Concepto creado para verificar que la publicacion "
                            "promueve objetos validados."
                        ),
                        "aliases": ["publicacion trazable"],
                    },
                    "rationale": "El segmento contiene un concepto publicable.",
                    "confidence": 0.88,
                    "source_locator": "capitulo 1 > p1",
                },
                {
                    "proposal_type": "evidence",
                    "title": "Evidencia publicable de prueba",
                    "payload": {
                        "id": evidence_id,
                        "node_id": node_id,
                        "source_id": source_id,
                        "source_edition_id": edition_id,
                        "evidence_type": "documented_paraphrase",
                        "locator": {
                            "catalog_id": "TEST-PUB-001",
                            "edition": "Edicion de prueba",
                            "unit": "capitulo 1",
                            "locator": "capitulo 1 > p1",
                            "url": None,
                        },
                        "reference": "capitulo 1 > p1",
                        "excerpt": (
                            "La publicacion convierte objetos validados "
                            "en conocimiento trazable."
                        ),
                        "context": "reviewed_proposal",
                        "confidence_level": 4,
                    },
                    "rationale": "La evidencia procede del segmento revisado.",
                    "confidence": 0.89,
                    "source_locator": "capitulo 1 > p1",
                },
                {
                    "proposal_type": "claim",
                    "title": "Claim publicable de prueba",
                    "payload": {
                        "id": claim_id,
                        "evidence_id": evidence_id,
                        "card_id": "lexico-precision",
                        "statement": (
                            "La publicacion oficializa conocimiento trazable "
                            "solo desde objetos validados."
                        ),
                        "claim_type": "architectural",
                        "node_id": node_id,
                        "related_node_ids": [],
                        "domain": "knowledge.publication",
                        "scope": {"language": "es", "register": "technical"},
                    },
                    "rationale": "El claim queda sustentado por la evidencia validada.",
                    "confidence": 0.9,
                    "source_locator": "capitulo 1 > p1",
                },
                {
                    "proposal_type": "relation",
                    "title": "Relacion publicable de prueba",
                    "payload": {
                        "id": relation_id,
                        "source_entity_type": "claim",
                        "source_entity_id": claim_id,
                        "target_entity_type": "evidence",
                        "target_entity_id": evidence_id,
                        "relation_type": "depende_de",
                        "direction": "outgoing",
                        "cardinality": "N:1",
                        "weight": 1.0,
                        "context": "publication_readiness",
                    },
                    "rationale": "El claim depende de la evidencia revisada.",
                    "confidence": 0.87,
                    "source_locator": "capitulo 1 > p1",
                },
            ],
        )
        assert response.status_code == 200
        proposals = response.json()
        proposal_by_type = {proposal["proposal_type"]: proposal for proposal in proposals}
        for proposal_type in ("node", "evidence", "claim", "relation"):
            approved = client.post(
                f"/knowledge/proposals/{proposal_by_type[proposal_type]['id']}/approve",
                json=decision,
            )
            assert approved.status_code == 200
            assert approved.json()["status"] == "approved"

        with SessionLocal() as session:
            relation = session.get(KnowledgeRelationRecord, relation_id)
            assert relation is not None
            assert relation.status == "validated"
            assert relation.source_entity_id == claim_id
            assert relation.target_entity_id == evidence_id

        candidate = client.post(
            "/knowledge/candidates",
            json={
                "id": candidate_id,
                "base_version": "knowledge-v0",
                "author": "test-editor",
                "reason": "crear version candidata con snapshot validado",
            },
        )
        assert candidate.status_code == 200
        assert candidate.json()["source_count"] == 1
        assert candidate.json()["node_count"] == 1
        assert candidate.json()["evidence_count"] == 1
        assert candidate.json()["claim_count"] == 1
        assert candidate.json()["card_count"] == 1

        readiness = client.get(f"/knowledge/publication/readiness?version={candidate_id}")
        assert readiness.status_code == 200
        assert readiness.json()["publishable"] is True
        assert readiness.json()["blockers"] == []

        publication = client.post(
            "/knowledge/publications",
            json={
                "version": candidate_id,
                "author": "test-editor",
                "reason": "publicar snapshot validado de prueba",
            },
        )
        assert publication.status_code == 200
        published = publication.json()
        assert published["status"] == "published"
        assert published["published_at"] != "not-published"

        query = client.post(
            "/knowledge/query",
            json={"query": "conocimiento trazable", "version": candidate_id, "limit": 3},
        )
        assert query.status_code == 200
        query_payload = query.json()
        assert query_payload["card_count"] == 1
        assert query_payload["cards"][0]["id"] == "lexico-precision"
        assert query_payload["claims"][0]["status"] == "published"
        assert query_payload["evidence"][0]["status"] == "published"

        with SessionLocal() as session:
            snapshot = session.get(KnowledgeVersionSnapshotRecord, candidate_id)
            assert snapshot is not None
            assert snapshot.status == "published"
            assert snapshot.source_ids == [source_id]
            assert snapshot.node_ids == [node_id]
            assert snapshot.evidence_ids == [evidence_id]
            assert snapshot.claim_ids == [claim_id]
            assert snapshot.relation_ids == [relation_id]
            node = session.get(KnowledgeNodeRecord, node_id)
            evidence = session.get(KnowledgeEvidenceItemRecord, evidence_id)
            claim = session.get(KnowledgeClaimRecord, claim_id)
            relation = session.get(KnowledgeRelationRecord, relation_id)
            assert node is not None and node.status == "published"
            assert evidence is not None and evidence.status == "published"
            assert claim is not None and claim.status == "published"
            assert relation is not None and relation.status == "published"
            assert {node.version, evidence.version, claim.version, relation.version} == {
                candidate_id
            }
            event = session.scalars(
                select(AuditEventRecord).where(
                    AuditEventRecord.event_type == "knowledge.published",
                    AuditEventRecord.entity_id == candidate_id,
                )
            ).first()
            assert event is not None
            assert event.payload["snapshot_activated"] is True
            assert event.payload["promoted"]["nodes"] == 1
            assert event.payload["promoted"]["evidence"] == 1
            assert event.payload["promoted"]["claims"] == 1
            assert event.payload["promoted"]["relations"] == 1
    finally:
        proposal_ids = [proposal["id"] for proposal in proposals]
        with SessionLocal() as session:
            session.query(AuditEventRecord).filter(
                AuditEventRecord.entity_id.in_(
                    [
                        candidate_id,
                        source_id,
                        edition_id,
                        entry_id,
                        segment_id,
                        extraction["id"] if extraction is not None else "",
                        *proposal_ids,
                    ]
                )
            ).delete(synchronize_session=False)
            session.query(KnowledgeVersionSnapshotRecord).filter(
                KnowledgeVersionSnapshotRecord.version_id == candidate_id
            ).delete(synchronize_session=False)
            session.query(KnowledgeVersionRecord).filter(
                KnowledgeVersionRecord.id == candidate_id
            ).delete(synchronize_session=False)
            session.query(KnowledgeClaimRevisionRecord).filter(
                KnowledgeClaimRevisionRecord.claim_id == claim_id
            ).delete(synchronize_session=False)
            session.query(KnowledgeClaimEvidenceLinkRecord).filter(
                KnowledgeClaimEvidenceLinkRecord.claim_id == claim_id
            ).delete(synchronize_session=False)
            session.query(KnowledgeClaimRecord).filter(
                KnowledgeClaimRecord.id == claim_id
            ).delete(synchronize_session=False)
            session.query(KnowledgeEvidenceRevisionRecord).filter(
                KnowledgeEvidenceRevisionRecord.evidence_id == evidence_id
            ).delete(synchronize_session=False)
            session.query(KnowledgeEvidenceItemRecord).filter(
                KnowledgeEvidenceItemRecord.id == evidence_id
            ).delete(synchronize_session=False)
            session.query(KnowledgeObjectRevisionRecord).filter(
                KnowledgeObjectRevisionRecord.object_id == node_id
            ).delete(synchronize_session=False)
            session.query(KnowledgeRelationRecord).filter(
                KnowledgeRelationRecord.id == relation_id
            ).delete(synchronize_session=False)
            session.query(KnowledgeNodeRecord).filter(
                KnowledgeNodeRecord.id == node_id
            ).delete(synchronize_session=False)
            if extraction is not None:
                session.query(KnowledgeProposalRecord).filter(
                    KnowledgeProposalRecord.extraction_id == extraction["id"]
                ).delete(synchronize_session=False)
                session.query(KnowledgeExtractionRunRecord).filter(
                    KnowledgeExtractionRunRecord.id == extraction["id"]
                ).delete(synchronize_session=False)
            session.query(KnowledgeSegmentRecord).filter(
                KnowledgeSegmentRecord.id == segment_id
            ).delete(synchronize_session=False)
            session.query(KnowledgeIndexEntryRecord).filter(
                KnowledgeIndexEntryRecord.id == entry_id
            ).delete(synchronize_session=False)
            session.query(KnowledgeSourceEditionRecord).filter(
                KnowledgeSourceEditionRecord.id == edition_id
            ).delete(synchronize_session=False)
            session.query(KnowledgeSourceRecord).filter(
                KnowledgeSourceRecord.id == source_id
            ).delete(synchronize_session=False)
            card = session.get(KnowledgeCardRecord, "lexico-precision")
            if card is not None:
                card.version = "knowledge-v0"
            session.commit()


def test_knowledge_ingestion_policy_closes_documental_pipeline_contract():
    response = client.get("/knowledge/ingestion")
    assert response.status_code == 200
    policy = response.json()

    assert "conocimiento verificable" in policy["meaning"]
    assert policy["ingestion_unit"] == "one_source_one_edition_one_batch"
    assert {"adquisicion documental", "segmentacion"} <= set(policy["scope"])
    assert {"recuperacion", "generacion", "preferencias"} <= set(policy["out_of_scope"])
    assert policy["lifecycle"] == [
        "registered",
        "acquisition_pending",
        "available",
        "structured",
        "segmented",
        "extracting",
        "normalizing",
        "review",
        "validated",
        "candidate",
        "published",
    ]
    assert {"blocked", "failed", "cancelled"} <= set(policy["alternative_states"])
    assert policy["required_flow"][0] == "registered_source"
    assert policy["required_flow"][-1] == "candidate_version"
    assert policy["proposed_initial_status"] == "proposed"
    assert "inventar localizadores" in policy["ai_forbidden_actions"]
    assert "aplazar" in policy["review_actions"]
    assert "ingestion.completed" in policy["required_events"]
    assert "missing_edition" in policy["stop_conditions"]
    assert policy["final_state"] == "candidate"
    assert policy["closure_flow"] == [
        "source",
        "edition",
        "index",
        "segmentation",
        "extraction",
        "nodes",
        "evidence",
        "claims",
        "cards",
        "validation",
        "candidate_version",
        "publication",
    ]
    assert "cualquier obra puede seguir el mismo recorrido completo" in policy[
        "closure_criteria"
    ]
    assert "la validacion precede siempre a la version candidata" in policy[
        "closure_criteria"
    ]


def test_knowledge_ingestion_batches_are_persisted_and_exportable():
    response = client.get("/knowledge/ingestion/batches")
    assert response.status_code == 200
    batches = response.json()
    assert len(batches) == 24
    first = batches[0]
    assert first["source_id"]
    assert first["source_edition_id"].endswith(":pending-edition")
    assert first["status"] == "blocked"
    assert "missing_edition" in first["blockers"]
    assert first["configuration"]["publishes_directly"] is False
    assert first["metrics"]["nodes_created"] == 0
    assert "ingest-rae-ngle:manual-2010" in {batch["id"] for batch in batches}

    filtered = client.get("/knowledge/ingestion/batches?source_id=rae-dle&status=blocked")
    assert filtered.status_code == 200
    assert [batch["source_id"] for batch in filtered.json()] == ["rae-dle"]

    export = client.get(f"/knowledge/ingestion/batches/{first['id']}/export")
    assert export.status_code == 200
    exported = export.json()
    assert exported["batch"]["id"] == first["id"]
    assert exported["proposals"] == {
        "nodes": [],
        "evidence": [],
        "claims": [],
        "relations": [],
        "cards": [],
    }
    assert exported["traceability"]["batch_id"] == first["id"]
    assert exported["publication_note"] == "La exportacion de lote no constituye publicacion."

    missing = client.get("/knowledge/ingestion/batches/missing/export")
    assert missing.status_code == 404
    assert missing.json()["detail"] == "Ingestion batch not found"


def test_knowledge_ingestion_readiness_requires_identified_edition():
    response = client.get("/knowledge/ingestion/readiness?source_id=rae-dle")
    assert response.status_code == 200
    readiness = response.json()
    assert readiness["source_id"] == "rae-dle"
    assert readiness["source_edition_id"] == "rae-dle:pending-edition"
    assert readiness["can_start"] is False
    assert readiness["status"] == "blocked"
    assert "missing_edition" in readiness["blockers"]
    checks = {check["id"]: check for check in readiness["checks"]}
    assert checks["registered_source"]["passed"] is True
    assert checks["edition_identified"]["passed"] is False
    assert checks["rights_reviewed"]["passed"] is False

    missing = client.get("/knowledge/ingestion/readiness?source_id=missing-source")
    assert missing.status_code == 404
    assert missing.json()["detail"] == "Knowledge source or edition not found"


def test_knowledge_revisions_allow_historical_recovery():
    response = client.get("/knowledge/revisions?version=knowledge-v0")
    assert response.status_code == 200
    revisions = response.json()
    assert len(revisions) >= 1
    assert {
        "source",
        "source_edition",
        "node",
        "relation",
        "evidence",
        "claim",
        "knowledge_card",
        "tree",
        "ontology",
        "schema",
        "knowledge_version",
    } <= {revision["object_type"] for revision in revisions}
    assert all(revision["revision_number"] >= 1 for revision in revisions)
    assert all(revision["object_version"] for revision in revisions)
    assert all(revision["knowledge_version"] == "knowledge-v0" for revision in revisions)
    assert all(revision["status"] == "active" for revision in revisions)
    assert all(revision["change_type"] == "created" for revision in revisions)
    assert all(revision["author"] for revision in revisions)
    assert all(revision["reason"] for revision in revisions)
    assert all(revision["previous_revision"] is None for revision in revisions)
    assert all(revision["updated_at"] >= revision["created_at"] for revision in revisions)
    assert all("after" in revision for revision in revisions)

    node_response = client.get(
        "/knowledge/revisions?version=knowledge-v0&object_type=node&object_id=rae-norma-estilo"
    )
    assert node_response.status_code == 200
    node_revisions = node_response.json()
    assert len(node_revisions) == 1
    assert node_revisions[0]["after"]["canonical_name"] == "Norma y uso en lengua espanola"
    assert "relations" in node_revisions[0]["after"]

    missing_version = client.get("/knowledge/revisions?version=missing-version")
    assert missing_version.status_code == 404
    assert missing_version.json()["detail"] == "Knowledge version not found"


def test_knowledge_query_uses_only_published_cards_claims_and_evidence():
    response = client.post(
        "/knowledge/query",
        json={"query": "precision lexica verificable", "version": "knowledge-v0", "limit": 3},
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["version"] == "knowledge-v0"
    assert payload["requested_version"] == "knowledge-v0"
    assert payload["resolved_version"] == "knowledge-v0"
    assert payload["query_type"] == ["writing_recommendation"]
    assert "LENGUA" in payload["domain"]
    assert payload["status"] == "no_match"
    assert payload["cards"] == []
    assert payload["claims"] == []
    assert payload["evidence"] == []
    assert payload["sources"] == []
    assert payload["retrieved_cards"] == []
    assert payload["ranking"] == []
    assert payload["card_count"] == len(payload["cards"])
    assert payload["claim_count"] == len(payload["claims"])
    assert payload["evidence_count"] == len(payload["evidence"])
    assert payload["retrieval_trace"]["normalized_query"] == "precision lexica verificable"
    assert payload["retrieval_trace"]["filters"]["claim_status"] == ["published"]
    assert payload["retrieval_trace"]["candidate_cards"] == []
    assert payload["retrieval_trace"]["selected_cards"] == []
    assert payload["retrieval_trace"]["selected_claims"] == []
    assert payload["retrieval_trace"]["selected_evidence"] == []
    assert payload["limits"]["max_cards"] == 3


def test_knowledge_query_contract_separates_query_from_retrieval_and_generation():
    response = client.get("/knowledge/query/contract")
    assert response.status_code == 200

    payload = response.json()
    assert payload["lifecycle"] == [
        "query",
        "interpretation",
        "restrictions",
        "context",
        "retrieval",
    ]
    assert payload["query_unit"] == (
        "texto breve del usuario + version solicitada + limite de recuperacion"
    )
    assert "resolved_version" in payload["interpretation_fields"]
    assert "profile_mutation_allowed" in payload["restriction_fields"]
    assert "generaciones" in payload["out_of_scope"]
    assert payload["allowed_version_values"] == ["knowledge-v0", "latest"]
    assert "presentacion" in payload["profile_boundary"]
    assert "solicitud de recuperacion" in payload["retrieval_boundary"]
    assert "no forma parte" in payload["generation_boundary"]


def test_knowledge_query_interpretation_builds_restrictions_context_and_audit():
    query = "precision lexica verificable"
    response = client.post(
        "/knowledge/query/interpretation",
        json={"query": query, "version": "latest", "limit": 3},
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["query"] == query
    assert payload["normalized_query"] == "precision lexica verificable"
    assert payload["requested_version"] == "latest"
    assert payload["resolved_version"] == "knowledge-v0"
    assert payload["query_type"] == ["writing_recommendation"]
    assert "LENGUA" in payload["domain"]
    assert payload["restrictions"]["max_cards"] == 3
    assert payload["restrictions"]["profile_mutation_allowed"] is False
    assert payload["restrictions"]["stable_knowledge_mutation_allowed"] is False
    assert payload["restrictions"]["generation_allowed"] is False
    assert payload["context"]["profile_influence"] == "presentation_only"
    assert payload["context"]["retrieval_unit"] == "knowledge_card"
    assert payload["retrieval_request"]["required"] is True
    assert payload["retrieval_request"]["version"] == "knowledge-v0"
    assert payload["retrieval_request"]["query_terms"] == [
        "lexica",
        "precision",
        "verificable",
    ]
    assert payload["audit_payload"]["query_length"] == len(query)
    assert query not in str(payload["audit_payload"])

    missing = client.post(
        "/knowledge/query/interpretation",
        json={"query": query, "version": "missing-version", "limit": 3},
    )
    assert missing.status_code == 404
    assert missing.json()["detail"] == "Knowledge version not found"


def test_knowledge_query_resolves_latest_and_declares_no_match():
    latest_response = client.post(
        "/knowledge/query",
        json={"query": "precision lexica", "version": "latest", "limit": 1},
    )
    assert latest_response.status_code == 200
    latest_payload = latest_response.json()
    assert latest_payload["requested_version"] == "latest"
    assert latest_payload["resolved_version"] == "knowledge-v0"
    assert latest_payload["version"] == "knowledge-v0"
    assert latest_payload["status"] == "no_match"
    assert latest_payload["card_count"] == 0

    empty_response = client.post(
        "/knowledge/query",
        json={"query": "complemento directo", "version": "knowledge-v0", "limit": 3},
    )
    assert empty_response.status_code == 200
    empty_payload = empty_response.json()
    assert empty_payload["status"] == "no_match"
    assert empty_payload["cards"] == []
    assert empty_payload["retrieval_trace"]["candidate_cards"] == []
    assert empty_payload["retrieval_trace"]["selected_claims"] == []


def test_knowledge_query_records_audit_event_without_raw_query():
    query = "precision lexica verificable"
    response = client.post(
        "/knowledge/query",
        json={"query": query, "version": "knowledge-v0", "limit": 3},
    )
    assert response.status_code == 200
    result = response.json()

    events_response = client.get("/audit/events")
    assert events_response.status_code == 200
    event = events_response.json()[0]
    assert event["event_type"] == "knowledge.query.executed"
    assert event["entity_type"] == "knowledge_version"
    assert event["entity_id"] == "knowledge-v0"
    assert event["payload"]["query_length"] == len(query)
    assert event["payload"]["limit"] == 3
    assert event["payload"]["card_count"] == result["card_count"]
    assert event["payload"]["claim_count"] == result["claim_count"]
    assert event["payload"]["evidence_count"] == result["evidence_count"]
    assert event["payload"]["pending_validation_count"] == (
        result["card_count"] + result["claim_count"] + result["evidence_count"]
    )
    assert event["payload"]["requested_version"] == "knowledge-v0"
    assert event["payload"]["resolved_version"] == "knowledge-v0"
    assert event["payload"]["status"] == "no_match"
    assert event["payload"]["candidate_nodes"] == 0
    assert event["payload"]["selected_cards"] == result["card_count"]
    assert event["payload"]["cache_hit"] is False
    assert query not in str(event["payload"])

    filtered_response = client.get(
        "/audit/events",
        params={
            "event_type": "knowledge.query.executed",
            "entity_type": "knowledge_version",
            "entity_id": "knowledge-v0",
        },
    )
    assert filtered_response.status_code == 200
    filtered_events = filtered_response.json()
    assert len(filtered_events) > 0
    assert {item["event_type"] for item in filtered_events} == {"knowledge.query.executed"}
    assert {item["entity_type"] for item in filtered_events} == {"knowledge_version"}
    assert {item["entity_id"] for item in filtered_events} == {"knowledge-v0"}

    other_version_response = client.get(
        "/audit/events",
        params={
            "event_type": "knowledge.query.executed",
            "entity_type": "knowledge_version",
            "entity_id": "missing-version",
        },
    )
    assert other_version_response.status_code == 200
    assert other_version_response.json() == []


def test_knowledge_query_history_is_derived_from_audit_events():
    query = "precision lexica verificable"
    response = client.post(
        "/knowledge/query",
        json={"query": query, "version": "knowledge-v0", "limit": 3},
    )
    assert response.status_code == 200
    result = response.json()

    history_response = client.get("/knowledge/query-history?version=knowledge-v0")
    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) > 0
    item = history[0]
    assert item["version"] == "knowledge-v0"
    assert item["has_results"] is (result["card_count"] > 0)
    assert item["query_length"] == len(query)
    assert item["limit"] == 3
    assert item["card_count"] == result["card_count"]
    assert item["claim_count"] == result["claim_count"]
    assert item["evidence_count"] == result["evidence_count"]
    assert item["pending_validation_count"] == (
        result["card_count"] + result["claim_count"] + result["evidence_count"]
    )
    assert query not in str(item)


def test_knowledge_query_summary_is_derived_from_audit_events():
    empty_response = client.post(
        "/knowledge/query",
        json={"query": "zzzinexistente", "version": "knowledge-v0", "limit": 5},
    )
    assert empty_response.status_code == 200
    second_empty_response = client.post(
        "/knowledge/query",
        json={"query": "precision lexica", "version": "knowledge-v0", "limit": 5},
    )
    assert second_empty_response.status_code == 200

    response = client.get("/knowledge/query-summary?version=knowledge-v0")
    assert response.status_code == 200
    summary = response.json()
    assert summary["version"] == "knowledge-v0"
    assert summary["total_count"] >= 2
    assert summary["empty_count"] >= 2
    assert summary["hit_count"] == 0
    assert summary["last_query_at"] is not None


def test_knowledge_query_summary_counts_beyond_history_window():
    now = datetime.now(UTC)
    with SessionLocal() as session:
        session.add_all(
            AuditEventRecord(
                event_type="knowledge.query.executed",
                entity_type="knowledge_version",
                entity_id="knowledge-v0",
                payload={
                    "query_length": 4,
                    "limit": 5,
                    "card_count": 0,
                    "claim_count": 0,
                    "evidence_count": 0,
                },
                created_at=now,
            )
            for _ in range(101)
        )
        session.commit()

    summary_response = client.get("/knowledge/query-summary?version=knowledge-v0")
    assert summary_response.status_code == 200
    assert summary_response.json()["total_count"] >= 101

    history_response = client.get("/knowledge/query-history?version=knowledge-v0&limit=20")
    assert history_response.status_code == 200
    assert len(history_response.json()) == 20
    assert history_response.json()[0]["pending_validation_count"] == 0


def test_knowledge_query_history_rejects_missing_version():
    response = client.get("/knowledge/query-history?version=missing-version")

    assert response.status_code == 404
    assert response.json()["detail"] == "Knowledge version not found"


def test_knowledge_query_summary_rejects_missing_version():
    response = client.get("/knowledge/query-summary?version=missing-version")

    assert response.status_code == 404
    assert response.json()["detail"] == "Knowledge version not found"


def test_knowledge_query_matches_the_full_persisted_chain():
    evidence_match = client.post(
        "/knowledge/query",
        json={"query": "ambiguedad", "version": "knowledge-v0", "limit": 3},
    )
    assert evidence_match.status_code == 200
    assert evidence_match.json()["cards"] == []

    node_match = client.post(
        "/knowledge/query",
        json={"query": "reglas normativas", "version": "knowledge-v0", "limit": 3},
    )
    assert node_match.status_code == 200
    assert node_match.json()["cards"] == []

    source_match = client.post(
        "/knowledge/query",
        json={"query": "Diccionario lengua espanola", "version": "knowledge-v0", "limit": 3},
    )
    assert source_match.status_code == 200
    assert source_match.json()["cards"] == []


def test_knowledge_query_rejects_missing_version():
    before = client.get("/audit/events").json()
    response = client.post(
        "/knowledge/query",
        json={"query": "precision", "version": "missing-version", "limit": 3},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Knowledge version not found"
    after = client.get("/audit/events").json()
    assert after == before


def test_knowledge_pipeline_is_persisted():
    response = client.get("/knowledge/versions")
    assert response.status_code == 200

    with SessionLocal() as session:
        sources = session.scalars(select(KnowledgeSourceRecord)).all()
        source_editions = session.scalars(select(KnowledgeSourceEditionRecord)).all()
        nodes = session.scalars(select(KnowledgeNodeRecord)).all()
        node_relations = session.scalars(select(KnowledgeNodeRelationRecord)).all()
        object_revisions = session.scalars(select(KnowledgeObjectRevisionRecord)).all()
        ingestion_batches = session.scalars(select(KnowledgeIngestionBatchRecord)).all()
        relations = session.scalars(select(KnowledgeRelationRecord)).all()
        evidence = session.scalars(select(KnowledgeEvidenceItemRecord)).all()
        evidence_revisions = session.scalars(select(KnowledgeEvidenceRevisionRecord)).all()
        claims = session.scalars(select(KnowledgeClaimRecord)).all()
        claim_links = session.scalars(select(KnowledgeClaimEvidenceLinkRecord)).all()
        claim_revisions = session.scalars(select(KnowledgeClaimRevisionRecord)).all()
        cards = session.scalars(select(KnowledgeCardRecord)).all()
        snapshot = session.get(KnowledgeVersionSnapshotRecord, "knowledge-v0")

    version = response.json()[0]
    assert snapshot is not None
    assert set(snapshot.source_ids) == {source.id for source in sources}
    published_source_edition_ids = {
        edition.id for edition in source_editions if edition.id.endswith(":pending-edition")
    }
    assert set(snapshot.source_edition_ids) == published_source_edition_ids
    assert "rae-ngle:manual-2010" not in snapshot.source_edition_ids
    assert set(snapshot.node_ids) == {node.id for node in nodes}
    assert set(snapshot.evidence_ids) == {item.id for item in evidence}
    assert set(snapshot.claim_ids) == {claim.id for claim in claims}
    assert set(snapshot.card_ids) == {card.id for card in cards}
    assert version["source_count"] == len(sources)
    assert version["node_count"] == len(nodes)
    assert version["evidence_count"] == len(evidence)
    assert version["claim_count"] == len(claims)
    assert version["card_count"] == len(cards)
    assert len(source_editions) == 24
    assert {edition.source_id for edition in source_editions} == {source.id for source in sources}
    assert len(node_relations) >= len(nodes)
    assert {node.source_id for node in nodes} <= {source.id for source in sources}
    assert {relation.source_node_id for relation in node_relations} == {node.id for node in nodes}
    assert {relation.target_node_id for relation in node_relations} <= {node.id for node in nodes}
    assert len(relations) >= (
        len(source_editions) + len(nodes) + len(evidence) + len(claims) + len(cards)
    )
    assert all(relation.source_entity_id for relation in relations)
    assert all(relation.target_entity_id for relation in relations)
    assert all(relation.relation_type for relation in relations)
    assert {relation.direction for relation in relations} == {"outgoing"}
    assert {relation.version for relation in relations} == {"knowledge-v0"}
    assert len(object_revisions) >= len(sources) + len(source_editions) + len(nodes)
    assert {
        "source",
        "source_edition",
        "node",
        "relation",
        "evidence",
        "claim",
        "knowledge_card",
        "tree",
        "ontology",
        "schema",
        "knowledge_version",
    } <= {revision.object_type for revision in object_revisions}
    assert len(ingestion_batches) == len(source_editions)
    assert {batch.status for batch in ingestion_batches} == {"blocked"}
    assert all(batch.source_id for batch in ingestion_batches)
    assert all(batch.source_edition_id for batch in ingestion_batches)
    assert {item.node_id for item in evidence} <= {node.id for node in nodes}
    assert {item.source_edition_id for item in evidence} <= {
        edition.id for edition in source_editions
    }
    assert {item.status for item in evidence} == {"draft"}
    assert len(evidence_revisions) == len(evidence)
    assert {revision.evidence_id for revision in evidence_revisions} == {item.id for item in evidence}
    assert {claim.evidence_id for claim in claims} <= {item.id for item in evidence}
    assert {claim.node_id for claim in claims} <= {node.id for node in nodes}
    assert {claim.status for claim in claims} == {"draft"}
    assert {claim.claim_type for claim in claims} == {"stylistic"}
    assert len(claim_links) == len(claims)
    assert {link.claim_id for link in claim_links} == {claim.id for claim in claims}
    assert {link.evidence_id for link in claim_links} <= {item.id for item in evidence}
    assert {link.role for link in claim_links} == {"primary"}
    assert len(claim_revisions) == len(claims)
    assert {revision.claim_id for revision in claim_revisions} == {claim.id for claim in claims}
    assert {claim.card_id for claim in claims} <= {card.id for card in cards}


def test_knowledge_coverage_matches_closed_v1_scope():
    response = client.get("/knowledge/coverage")
    assert response.status_code == 200
    payload = response.json()
    assert "pending" not in payload
    assert "fichas internas" in payload["covered"]
    assert "evidencias trazables" in payload["covered"]
    assert "validacion visible y auditada" in payload["covered"]
    assert "pgvector" in payload["out_of_scope"]


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
    assert screen_ids == {
        "knowledge",
        "preferences",
        "profile",
        "scoring",
        "editor",
        "lab",
        "compare",
        "rules",
        "persistence",
        "cerebro",
        "acceptance",
        "closure",
        "roadmap",
        "screens",
        "audit",
    }
    assert {item["status"] for item in response.json()} == {"implemented"}


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
    assert domains["knowledge"]["status"] == "persisted"
    assert domains["versions"]["storage"] == "knowledge_versions"
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
    observability_items = {item["id"]: item for item in observability.json()}
    assert "adequacy_percentage" in observability_items
    assert observability_items["interpretation_time"]["status"] == "available"
    assert (
        observability_items["interpretation_time"]["source"]
        == "audit_events preference.created.duration_ms"
    )
    assert observability_items["generation_time"]["status"] == "available"
    assert (
        observability_items["generation_time"]["source"]
        == "audit_events text.generated.duration_ms"
    )
    assert observability_items["retrieval_quality"]["status"] == "available"
    assert (
        observability_items["retrieval_quality"]["source"]
        == "knowledge/query-history.pending_validation_count"
    )

    roadmap = client.get("/roadmap/technical")
    assert roadmap.status_code == 200
    roadmap_items = {item["name"]: item for item in roadmap.json()}
    assert roadmap_items["Esqueleto"]["status"] == "done"
    assert roadmap_items["Conocimiento"]["status"] == "done"
    assert "validacion visible y auditada" in roadmap_items["Conocimiento"]["items"]

    gates = client.get("/cerebro-audit/gates")
    assert gates.status_code == 200
    assert any(item["id"] == "world_model_dependency" for item in gates.json())


def test_cerebro_audit_remains_blocked_until_code_evidence_exists():
    candidates = client.get("/cerebro-audit/candidates")
    assert candidates.status_code == 200
    assert {item["status"] for item in candidates.json()} == {"pending_code_evidence"}

    gates = client.get("/cerebro-audit/gates")
    assert gates.status_code == 200
    assert {item["status"] for item in gates.json()} == {"blocked_until_checked"}


def test_closure_surfaces_do_not_report_open_planned_work():
    observability = client.get("/observability/status")
    assert observability.status_code == 200
    assert {item["status"] for item in observability.json()} == {"available"}

    roadmap = client.get("/roadmap/technical")
    assert roadmap.status_code == 200
    assert {item["status"] for item in roadmap.json()} == {"done"}

    coverage = client.get("/knowledge/coverage")
    assert coverage.status_code == 200
    assert "pending" not in coverage.json()


def test_technical_closure_and_contract_boundaries_are_exposed():
    technical = client.get("/closure/technical")
    assert technical.status_code == 200
    assert len(technical.json()) == 8
    assert technical.json()[0]["status"] == "satisfied"

    boundaries = client.get("/contract/boundaries")
    assert boundaries.status_code == 200
    sections = {item["section"]: item for item in boundaries.json()}
    assert sections[21]["status"] == "not_defined_in_v1"
    assert sections[22]["status"] == "not_defined_in_v1"
    assert "V2" not in sections[21]["next_step"]
    assert "V2" not in sections[22]["next_step"]
