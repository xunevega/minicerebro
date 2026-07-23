from datetime import UTC, datetime
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.seeds import DEFAULT_PROFILE_ID, seed_variables
from app.db.models import (
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
    KnowledgeVersionRecord,
    ProfileRecord,
    ScoreVariableRecord,
)
from app.db.session import database_url
from app.knowledge.service import (
    seed_cards,
    seed_claim_evidence_links,
    seed_claim_revisions,
    seed_claims,
    seed_evidence,
    seed_evidence_revisions,
    seed_ingestion_batches,
    seed_node_relations,
    seed_nodes,
    seed_object_revisions,
    seed_relations,
    seed_source_editions,
    seed_sources,
)

BACKEND_DIR = Path(__file__).resolve().parents[2]


def upgrade_database() -> None:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url())
    command.upgrade(config, "head")


def ensure_seed_data(session: Session) -> None:
    profile = session.get(ProfileRecord, DEFAULT_PROFILE_ID)
    if profile is None:
        profile = ProfileRecord(
            id=DEFAULT_PROFILE_ID,
            name="Perfil inicial",
            language="es",
            summary="Perfil semilla con baja confianza. Las preferencias requieren revision explicita.",
            updated_at=datetime.now(UTC),
        )
        session.add(profile)

    existing_variables = session.scalars(
        select(ScoreVariableRecord).where(ScoreVariableRecord.profile_id == DEFAULT_PROFILE_ID)
    ).all()
    existing_keys = {variable.key for variable in existing_variables}

    for variable in seed_variables():
        if variable.key in existing_keys:
            continue
        session.add(
            ScoreVariableRecord(
                profile_id=DEFAULT_PROFILE_ID,
                key=variable.key,
                label=variable.label,
                category=variable.category,
                calculated_value=variable.calculated_value,
                manual_adjustment=variable.manual_adjustment,
                confidence=variable.confidence,
                context=variable.context,
                evidence_count=variable.evidence_count,
                updated_at=variable.updated_at,
            )
        )

    ensure_knowledge_seed_data(session)
    session.commit()


def ensure_knowledge_seed_data(session: Session) -> None:
    if session.get(KnowledgeVersionRecord, "knowledge-v0") is None:
        session.add(
            KnowledgeVersionRecord(
                id="knowledge-v0",
                status="seed",
                published_at="not-published",
            )
        )
    for source in seed_sources():
        source_record = session.get(KnowledgeSourceRecord, source.id)
        values = {
            "catalog_id": source.catalog_id,
            "name": source.name,
            "responsible": source.responsible,
            "source_type": source.source_type,
            "domains": source.domains,
            "authority_level": source.authority_level,
            "priority": source.priority,
            "status": source.status,
            "edition": source.edition,
            "publication_date": source.publication_date,
            "location": source.location,
            "acquisition_status": source.acquisition_status,
            "validation_status": source.validation_status,
            "rights": source.rights,
            "structure": source.structure,
            "locator_system": source.locator_system,
        }
        if source_record is not None:
            for field, value in values.items():
                setattr(source_record, field, value)
            continue
        session.add(KnowledgeSourceRecord(id=source.id, **values))
    session.flush()

    for node in seed_nodes():
        node_record = session.get(KnowledgeNodeRecord, node.id)
        if node_record is not None:
            node_record.source_id = node.source_id
            node_record.node_type = node.node_type
            node_record.title = node.title
            node_record.summary = node.summary
            node_record.canonical_name = node.canonical_name
            node_record.primary_branch = node.primary_branch
            node_record.secondary_branch = node.secondary_branch
            node_record.short_definition = node.short_definition
            node_record.long_definition = node.long_definition
            node_record.status = node.status
            node_record.version = node.version
            node_record.created_at = node.created_at
            node_record.published_at = node.published_at
            node_record.aliases = node.aliases
            continue
        session.add(
            KnowledgeNodeRecord(
                id=node.id,
                source_id=node.source_id,
                node_type=node.node_type,
                title=node.title,
                summary=node.summary,
                canonical_name=node.canonical_name,
                primary_branch=node.primary_branch,
                secondary_branch=node.secondary_branch,
                short_definition=node.short_definition,
                long_definition=node.long_definition,
                status=node.status,
                version=node.version,
                created_at=node.created_at,
                published_at=node.published_at,
                aliases=node.aliases,
            )
        )
    session.flush()

    for relation in seed_node_relations():
        relation_record = session.get(KnowledgeNodeRelationRecord, relation.id)
        values = {
            "source_node_id": relation.source_node_id,
            "target_node_id": relation.target_node_id,
            "relation_type": relation.relation_type,
            "direction": relation.direction,
            "cardinality": relation.cardinality,
            "weight": relation.weight,
            "confidence": relation.confidence,
            "context": relation.context,
            "status": relation.status,
            "version": relation.version,
            "created_at": relation.created_at,
            "updated_at": relation.updated_at,
        }
        if relation_record is not None:
            for field, value in values.items():
                setattr(relation_record, field, value)
            continue
        session.add(KnowledgeNodeRelationRecord(id=relation.id, **values))

    seed_relation_ids = {relation.id for relation in seed_node_relations()}
    stale_relations = session.scalars(select(KnowledgeNodeRelationRecord)).all()
    for stale_relation in stale_relations:
        if stale_relation.id not in seed_relation_ids:
            session.delete(stale_relation)

    for relation in seed_relations():
        relation_record = session.get(KnowledgeRelationRecord, relation.id)
        values = {
            "source_entity_type": relation.source_entity_type,
            "source_entity_id": relation.source_entity_id,
            "target_entity_type": relation.target_entity_type,
            "target_entity_id": relation.target_entity_id,
            "relation_type": relation.relation_type,
            "direction": relation.direction,
            "cardinality": relation.cardinality,
            "weight": relation.weight,
            "confidence": relation.confidence,
            "context": relation.context,
            "status": relation.status,
            "version": relation.version,
            "created_at": relation.created_at,
            "updated_at": relation.updated_at,
        }
        if relation_record is not None:
            for field, value in values.items():
                setattr(relation_record, field, value)
            continue
        session.add(KnowledgeRelationRecord(id=relation.id, **values))

    seed_graph_relation_ids = {relation.id for relation in seed_relations()}
    stale_graph_relations = session.scalars(select(KnowledgeRelationRecord)).all()
    for stale_relation in stale_graph_relations:
        if stale_relation.id not in seed_graph_relation_ids:
            session.delete(stale_relation)

    for revision in seed_object_revisions():
        revision_record = session.get(KnowledgeObjectRevisionRecord, revision.id)
        values = {
            "object_type": revision.object_type,
            "object_id": revision.object_id,
            "revision_number": revision.revision_number,
            "object_version": revision.object_version,
            "knowledge_version": revision.knowledge_version,
            "status": revision.status,
            "change_type": revision.change_type,
            "author": revision.author,
            "reason": revision.reason,
            "previous_revision": revision.previous_revision,
            "replaces_object_id": revision.replaces_object_id,
            "replaced_by_object_id": revision.replaced_by_object_id,
            "before": revision.before,
            "after": revision.after,
            "created_at": revision.created_at,
            "updated_at": revision.updated_at,
        }
        if revision_record is not None:
            for field, value in values.items():
                setattr(revision_record, field, value)
            continue
        session.add(KnowledgeObjectRevisionRecord(id=revision.id, **values))
    for card in seed_cards():
        if session.get(KnowledgeCardRecord, card.id) is not None:
            continue
        session.add(
            KnowledgeCardRecord(
                id=card.id,
                card_type=card.card_type,
                name=card.name,
                definition=card.definition,
                confidence=card.confidence,
                version=card.version,
                payload=card.payload,
            )
        )
    session.flush()

    for evidence in seed_evidence():
        evidence_record = session.get(KnowledgeEvidenceItemRecord, evidence.id)
        if evidence_record is not None:
            evidence_record.node_id = evidence.node_id
            evidence_record.source_id = evidence.source_id
            evidence_record.source_edition_id = evidence.source_edition_id
            evidence_record.evidence_type = evidence.evidence_type
            evidence_record.locator = evidence.locator
            evidence_record.reference = evidence.reference
            evidence_record.excerpt = evidence.excerpt
            evidence_record.context = evidence.context
            evidence_record.confidence = evidence.confidence
            evidence_record.confidence_level = evidence.confidence_level
            evidence_record.status = evidence.status
            evidence_record.version = evidence.version
            evidence_record.created_at = evidence.created_at
            evidence_record.updated_at = evidence.updated_at
            evidence_record.incorporated_by = evidence.incorporated_by
            evidence_record.reviewed_by = evidence.reviewed_by
            evidence_record.revision = evidence.revision
            continue
        session.add(
            KnowledgeEvidenceItemRecord(
                id=evidence.id,
                node_id=evidence.node_id,
                source_id=evidence.source_id,
                source_edition_id=evidence.source_edition_id,
                evidence_type=evidence.evidence_type,
                locator=evidence.locator,
                reference=evidence.reference,
                excerpt=evidence.excerpt,
                context=evidence.context,
                confidence=evidence.confidence,
                confidence_level=evidence.confidence_level,
                status=evidence.status,
                version=evidence.version,
                created_at=evidence.created_at,
                updated_at=evidence.updated_at,
                incorporated_by=evidence.incorporated_by,
                reviewed_by=evidence.reviewed_by,
                revision=evidence.revision,
            )
        )
    session.flush()

    for revision in seed_evidence_revisions():
        revision_record = session.get(KnowledgeEvidenceRevisionRecord, revision["id"])
        values = {
            "evidence_id": revision["evidence_id"],
            "revision": revision["revision"],
            "author": revision["author"],
            "reason": revision["reason"],
            "changes": revision["changes"],
            "created_at": revision["created_at"],
        }
        if revision_record is not None:
            for field, value in values.items():
                setattr(revision_record, field, value)
            continue
        session.add(KnowledgeEvidenceRevisionRecord(id=revision["id"], **values))

    for claim in seed_claims():
        claim_record = session.get(KnowledgeClaimRecord, claim.id)
        values = {
            "evidence_id": claim.evidence_id,
            "card_id": claim.card_id,
            "statement": claim.statement,
            "claim_type": claim.claim_type,
            "node_id": claim.node_id,
            "related_node_ids": claim.related_node_ids,
            "domain": claim.domain,
            "scope": claim.scope,
            "status": claim.status,
            "confidence": claim.confidence,
            "origin": claim.origin,
            "version": claim.version,
            "revision": claim.revision,
            "created_at": claim.created_at,
            "updated_at": claim.updated_at,
            "published_at": claim.published_at,
        }
        if claim_record is not None:
            for field, value in values.items():
                setattr(claim_record, field, value)
            continue
        session.add(KnowledgeClaimRecord(id=claim.id, **values))

    session.flush()

    for link in seed_claim_evidence_links():
        link_record = session.get(KnowledgeClaimEvidenceLinkRecord, link.id)
        values = {
            "claim_id": link.claim_id,
            "evidence_id": link.evidence_id,
            "role": link.role,
            "created_at": link.created_at,
        }
        if link_record is not None:
            for field, value in values.items():
                setattr(link_record, field, value)
            continue
        session.add(KnowledgeClaimEvidenceLinkRecord(id=link.id, **values))

    for revision in seed_claim_revisions():
        revision_record = session.get(KnowledgeClaimRevisionRecord, revision["id"])
        values = {
            "claim_id": revision["claim_id"],
            "revision": revision["revision"],
            "knowledge_version": revision["knowledge_version"],
            "author": revision["author"],
            "reason": revision["reason"],
            "changed_fields": revision["changed_fields"],
            "previous_claim": revision["previous_claim"],
            "new_claim": revision["new_claim"],
            "created_at": revision["created_at"],
        }
        if revision_record is not None:
            for field, value in values.items():
                setattr(revision_record, field, value)
            continue
        session.add(KnowledgeClaimRevisionRecord(id=revision["id"], **values))

    for edition in seed_source_editions():
        edition_record = session.get(KnowledgeSourceEditionRecord, edition.id)
        values = {
            "source_id": edition.source_id,
            "label": edition.label,
            "publication_date": edition.publication_date,
            "location": edition.location,
            "acquisition_status": edition.acquisition_status,
            "validation_status": edition.validation_status,
            "rights": edition.rights,
            "structure": edition.structure,
            "locator_system": edition.locator_system,
        }
        if edition_record is not None:
            for field, value in values.items():
                setattr(edition_record, field, value)
            continue
        session.add(KnowledgeSourceEditionRecord(id=edition.id, **values))

    seed_edition_ids = {edition.id for edition in seed_source_editions()}
    stale_editions = session.scalars(select(KnowledgeSourceEditionRecord)).all()
    for stale_edition in stale_editions:
        if stale_edition.id not in seed_edition_ids:
            session.delete(stale_edition)
    session.flush()

    for batch in seed_ingestion_batches():
        batch_record = session.get(KnowledgeIngestionBatchRecord, batch.id)
        values = {
            "source_id": batch.source_id,
            "source_edition_id": batch.source_edition_id,
            "batch_label": batch.batch_label,
            "scope": batch.scope,
            "status": batch.status,
            "author": batch.author,
            "tools": batch.tools,
            "model_used": batch.model_used,
            "configuration": batch.configuration,
            "progress": batch.progress,
            "metrics": batch.metrics,
            "decisions": batch.decisions,
            "blockers": batch.blockers,
            "result": batch.result,
            "created_at": batch.created_at,
            "updated_at": batch.updated_at,
        }
        if batch_record is not None:
            for field, value in values.items():
                setattr(batch_record, field, value)
            continue
        session.add(KnowledgeIngestionBatchRecord(id=batch.id, **values))

    seed_batch_ids = {batch.id for batch in seed_ingestion_batches()}
    stale_batches = session.scalars(select(KnowledgeIngestionBatchRecord)).all()
    for stale_batch in stale_batches:
        if stale_batch.id not in seed_batch_ids:
            session.delete(stale_batch)
