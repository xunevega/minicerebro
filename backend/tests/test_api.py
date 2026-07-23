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
    KnowledgeIngestionBatchRecord,
    KnowledgeNodeRecord,
    KnowledgeNodeRelationRecord,
    KnowledgeObjectRevisionRecord,
    KnowledgeRelationRecord,
    KnowledgeSourceRecord,
    KnowledgeSourceEditionRecord,
)
from app.db.session import SessionLocal
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
    assert payload["knowledge_policy"] == (
        "La exportacion del perfil no incluye ni modifica la base de conocimiento."
    )
    assert "knowledge" not in payload


def test_profile_export_rejects_missing_profile():
    response = client.get("/profiles/missing/export")
    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"


def test_profile_surfaces_reject_missing_profile_consistently():
    assert client.get("/profiles/missing/summary").status_code == 404
    assert client.get("/profiles/missing/scores").status_code == 404
    assert client.get("/profiles/missing/statistics").status_code == 404
    assert client.get("/profiles/missing/contradictions").status_code == 404
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
    assert sources[0] == {
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
        "editions": [
            {
                "id": "rae-ngle:pending-edition",
                "source_id": "rae-ngle",
                "label": "pendiente de identificacion",
                "publication_date": "pendiente de identificacion",
                "location": "pendiente de adquisicion",
                "acquisition_status": "registered",
                "validation_status": "not_validated",
                "rights": "registro autorizado; contenido no ingerido",
                "structure": ["pendiente de estructuracion"],
                "locator_system": [
                    "edicion",
                    "parte",
                    "capitulo",
                    "seccion",
                    "pagina",
                    "entrada",
                    "url",
                ],
            }
        ],
    }
    assert all(len(source["editions"]) == 1 for source in sources)
    assert {source["editions"][0]["source_id"] for source in sources} == {
        source["id"] for source in sources
    }

    versioned = client.get("/knowledge/sources?version=knowledge-v0")
    assert versioned.status_code == 200
    assert {source["id"] for source in versioned.json()} == {source["id"] for source in sources}

    missing_version = client.get("/knowledge/sources?version=missing-version")
    assert missing_version.status_code == 404
    assert missing_version.json()["detail"] == "Knowledge version not found"


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
    assert policy["closure_flow"][-1] == "publication"


def test_knowledge_ingestion_batches_are_persisted_and_exportable():
    response = client.get("/knowledge/ingestion/batches")
    assert response.status_code == 200
    batches = response.json()
    assert len(batches) == 23
    first = batches[0]
    assert first["source_id"]
    assert first["source_edition_id"].endswith(":pending-edition")
    assert first["status"] == "blocked"
    assert "missing_edition" in first["blockers"]
    assert first["configuration"]["publishes_directly"] is False
    assert first["metrics"]["nodes_created"] == 0

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


def test_knowledge_query_returns_cards_claims_and_evidence():
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
    assert payload["status"] == "low_confidence"
    assert payload["cards"][0]["id"] == "lexico-precision"
    assert payload["card_count"] == len(payload["cards"])
    assert payload["claim_count"] == len(payload["claims"])
    assert payload["evidence_count"] == len(payload["evidence"])
    assert payload["sources"][0]["id"] == "rae-dle"
    assert payload["retrieved_cards"][0]["card_id"] == "lexico-precision"
    assert payload["retrieved_cards"][0]["node_id"] == "rae-norma-estilo"
    assert payload["retrieved_cards"][0]["claim_ids"] == ["claim-precision-lexica"]
    assert payload["ranking"][0]["card_id"] == "lexico-precision"
    assert "concept_match" in payload["ranking"][0]["factors"]
    assert payload["retrieval_trace"]["normalized_query"] == "precision lexica verificable"
    assert payload["retrieval_trace"]["selected_cards"] == ["lexico-precision"]
    assert payload["limits"]["max_cards"] == 3
    assert {claim["card_id"] for claim in payload["claims"]} <= {
        card["id"] for card in payload["cards"]
    }
    assert {item["id"] for item in payload["evidence"]} >= {
        claim["evidence_id"] for claim in payload["claims"]
    }


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
    assert latest_payload["card_count"] == 1

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
    assert event["payload"]["status"] == "low_confidence"
    assert event["payload"]["candidate_nodes"] >= 1
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
    hit_response = client.post(
        "/knowledge/query",
        json={"query": "precision lexica", "version": "knowledge-v0", "limit": 5},
    )
    assert hit_response.status_code == 200

    response = client.get("/knowledge/query-summary?version=knowledge-v0")
    assert response.status_code == 200
    summary = response.json()
    assert summary["version"] == "knowledge-v0"
    assert summary["total_count"] >= 2
    assert summary["empty_count"] >= 1
    assert summary["hit_count"] >= 1
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
    assert evidence_match.json()["cards"][0]["id"] == "lexico-precision"

    node_match = client.post(
        "/knowledge/query",
        json={"query": "reglas normativas", "version": "knowledge-v0", "limit": 3},
    )
    assert node_match.status_code == 200
    assert node_match.json()["cards"][0]["id"] == "lexico-precision"

    source_match = client.post(
        "/knowledge/query",
        json={"query": "Diccionario lengua espanola", "version": "knowledge-v0", "limit": 3},
    )
    assert source_match.status_code == 200
    assert source_match.json()["cards"][0]["id"] == "lexico-precision"


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

    version = response.json()[0]
    assert version["source_count"] == len(sources)
    assert version["node_count"] == len(nodes)
    assert version["evidence_count"] == len(evidence)
    assert version["claim_count"] == len(claims)
    assert version["card_count"] == len(cards)
    assert len(source_editions) == 23
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
