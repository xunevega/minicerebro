from datetime import UTC, datetime
from pathlib import Path
from threading import Lock

from alembic import command
from alembic.config import Config
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.seeds import DEFAULT_PROFILE_ID, seed_variables
from app.db.models import (
    AuditEventRecord,
    KnowledgeCardRecord,
    KnowledgeClaimEvidenceLinkRecord,
    KnowledgeClaimRecord,
    KnowledgeClaimRevisionRecord,
    KnowledgeEvidenceItemRecord,
    KnowledgeEvidenceRevisionRecord,
    KnowledgeExtractionRunRecord,
    KnowledgeIngestionBatchRecord,
    KnowledgeIndexEntryRecord,
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
    seed_extraction_runs,
    seed_ingestion_batches,
    seed_index_entries,
    seed_node_relations,
    seed_nodes,
    seed_object_revisions,
    seed_proposals,
    seed_relations,
    seed_segments,
    seed_source_editions,
    seed_sources,
)

BACKEND_DIR = Path(__file__).resolve().parents[2]
_SEED_LOCK = Lock()


def _add_published_snapshot(
    session: Session,
    *,
    version_id: str,
    version_chain: set[str],
    timestamp: str,
) -> None:
    if session.get(KnowledgeVersionSnapshotRecord, version_id) is not None:
        return
    evidence = [item for item in seed_evidence() if item.version in version_chain]
    claims = [claim for claim in seed_claims() if claim.version in version_chain]
    cards = [card for card in seed_cards() if card.version in version_chain]
    node_ids_from_claims = {
        claim.node_id
        for claim in claims
    } | {
        related_node_id
        for claim in claims
        for related_node_id in claim.related_node_ids
    }
    node_ids_from_evidence = {item.node_id for item in evidence}
    nodes = [
        node
        for node in seed_nodes()
        if node.version in version_chain or node.id in node_ids_from_claims | node_ids_from_evidence
    ]
    source_ids = sorted({node.source_id for node in nodes} | {item.source_id for item in evidence})
    source_edition_ids = sorted({item.source_edition_id for item in evidence})
    node_ids = [node.id for node in nodes]
    evidence_ids = [item.id for item in evidence]
    claim_ids = [claim.id for claim in claims]
    card_ids = [card.id for card in cards]
    snapshot_object_ids = {
        *source_ids,
        *source_edition_ids,
        *node_ids,
        *evidence_ids,
        *claim_ids,
        *card_ids,
    }
    node_relation_ids = [
        relation.id
        for relation in seed_node_relations()
        if relation.version in version_chain
        and relation.source_node_id in snapshot_object_ids
        and relation.target_node_id in snapshot_object_ids
    ]
    relation_ids = [
        relation.id
        for relation in seed_relations()
        if relation.version in version_chain
        and relation.source_entity_id in snapshot_object_ids
        and relation.target_entity_id in snapshot_object_ids
    ]
    revision_ids = [
        revision.id
        for revision in seed_object_revisions()
        if revision.object_id in snapshot_object_ids or revision.object_id in relation_ids
    ]
    claim_evidence_link_ids = [
        link.id
        for link in seed_claim_evidence_links()
        if link.claim_id in claim_ids and link.evidence_id in evidence_ids
    ]
    session.add(
        KnowledgeVersionSnapshotRecord(
            version_id=version_id,
            status="published",
            source_ids=source_ids,
            source_edition_ids=source_edition_ids,
            node_ids=node_ids,
            node_relation_ids=node_relation_ids,
            relation_ids=relation_ids,
            evidence_ids=evidence_ids,
            claim_ids=claim_ids,
            claim_evidence_link_ids=claim_evidence_link_ids,
            card_ids=card_ids,
            revision_ids=revision_ids,
            created_at=timestamp,
            updated_at=timestamp,
        )
    )


def upgrade_database() -> None:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url())
    command.upgrade(config, "head")


def ensure_seed_data(session: Session) -> None:
    with _SEED_LOCK:
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
    if session.get(KnowledgeVersionRecord, "knowledge-v1") is None:
        session.add(
            KnowledgeVersionRecord(
                id="knowledge-v1",
                status="published",
                published_at="2026-07-23",
            )
        )
    if session.get(KnowledgeVersionRecord, "knowledge-v2") is None:
        session.add(
            KnowledgeVersionRecord(
                id="knowledge-v2",
                status="published",
                published_at="2026-07-23T01:00:00+00:00",
            )
        )
    if session.get(KnowledgeVersionRecord, "knowledge-v3") is None:
        session.add(
            KnowledgeVersionRecord(
                id="knowledge-v3",
                status="published",
                published_at="2026-07-23T02:00:00+00:00",
            )
        )
    if session.get(KnowledgeVersionRecord, "knowledge-v4") is None:
        session.add(
            KnowledgeVersionRecord(
                id="knowledge-v4",
                status="published",
                published_at="2026-07-23T03:00:00+00:00",
            )
        )
    if session.get(KnowledgeVersionRecord, "knowledge-v5") is None:
        session.add(
            KnowledgeVersionRecord(
                id="knowledge-v5",
                status="published",
                published_at="2026-07-23T04:00:00+00:00",
            )
        )
    if session.get(KnowledgeVersionRecord, "knowledge-v6") is None:
        session.add(
            KnowledgeVersionRecord(
                id="knowledge-v6",
                status="published",
                published_at="2026-07-23T05:00:00+00:00",
            )
        )
    if session.get(KnowledgeVersionRecord, "knowledge-v7") is None:
        session.add(
            KnowledgeVersionRecord(
                id="knowledge-v7",
                status="published",
                published_at="2026-07-23T06:00:00+00:00",
            )
        )
    if session.get(KnowledgeVersionRecord, "knowledge-v8") is None:
        session.add(
            KnowledgeVersionRecord(
                id="knowledge-v8",
                status="published",
                published_at="2026-07-23T07:00:00+00:00",
            )
        )
    if session.get(KnowledgeVersionRecord, "knowledge-v9") is None:
        session.add(
            KnowledgeVersionRecord(
                id="knowledge-v9",
                status="published",
                published_at="2026-07-23T08:00:00+00:00",
            )
        )
    if session.get(KnowledgeVersionRecord, "knowledge-v10") is None:
        session.add(
            KnowledgeVersionRecord(
                id="knowledge-v10",
                status="published",
                published_at="2026-07-23T09:00:00+00:00",
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
            "title": edition.title,
            "edition_label": edition.edition_label,
            "publication_year": edition.publication_year,
            "publisher": edition.publisher,
            "isbn": edition.isbn,
            "language": edition.language,
            "format": edition.format,
            "access_location": edition.access_location,
            "rights_status": edition.rights_status,
            "status": edition.status,
            "notes": edition.notes,
            "created_at": edition.created_at,
            "updated_at": edition.updated_at,
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
    session.flush()

    for entry in seed_index_entries():
        entry_record = session.get(KnowledgeIndexEntryRecord, entry.id)
        values = {
            "edition_id": entry.edition_id,
            "parent_id": entry.parent_id,
            "level": entry.level,
            "entry_order": entry.order,
            "title": entry.title,
            "locator": entry.locator,
            "page_start": entry.page_start,
            "page_end": entry.page_end,
            "status": entry.status,
            "created_at": entry.created_at,
            "updated_at": entry.updated_at,
        }
        if entry_record is not None:
            for field, value in values.items():
                setattr(entry_record, field, value)
            continue
        session.add(KnowledgeIndexEntryRecord(id=entry.id, **values))
    session.flush()

    for segment in seed_segments():
        segment_record = session.get(KnowledgeSegmentRecord, segment.id)
        values = {
            "index_entry_id": segment.index_entry_id,
            "parent_segment_id": segment.parent_segment_id,
            "segment_type": segment.segment_type,
            "title": segment.title,
            "text": segment.text,
            "segment_order": segment.order,
            "start_locator": segment.start_locator,
            "end_locator": segment.end_locator,
            "language": segment.language,
            "status": segment.status,
            "created_at": segment.created_at,
            "updated_at": segment.updated_at,
        }
        if segment_record is not None:
            for field, value in values.items():
                setattr(segment_record, field, value)
            continue
        session.add(KnowledgeSegmentRecord(id=segment.id, **values))
    session.flush()

    for extraction in seed_extraction_runs():
        extraction_record = session.get(KnowledgeExtractionRunRecord, extraction.id)
        values = {
            "segment_id": extraction.segment_id,
            "status": extraction.status,
            "extractor_type": extraction.extractor_type,
            "extractor_name": extraction.extractor_name,
            "extractor_version": extraction.extractor_version,
            "configuration": extraction.configuration,
            "input_segment_revision": extraction.input_segment_revision,
            "input_segment_hash": extraction.input_segment_hash,
            "knowledge_version": extraction.knowledge_version,
            "started_at": extraction.started_at,
            "completed_at": extraction.completed_at,
            "error_code": extraction.error_code,
            "error_message": extraction.error_message,
            "created_at": extraction.created_at,
            "updated_at": extraction.updated_at,
        }
        if extraction_record is not None:
            for field, value in values.items():
                setattr(extraction_record, field, value)
            continue
        session.add(KnowledgeExtractionRunRecord(id=extraction.id, **values))
    session.flush()

    for proposal in seed_proposals():
        proposal_record = session.get(KnowledgeProposalRecord, proposal.id)
        values = {
            "extraction_id": proposal.extraction_id,
            "segment_id": proposal.segment_id,
            "proposal_type": proposal.proposal_type,
            "status": proposal.status,
            "title": proposal.title,
            "payload": proposal.payload,
            "rationale": proposal.rationale,
            "confidence": proposal.confidence,
            "source_locator": proposal.source_locator,
            "created_at": proposal.created_at,
            "updated_at": proposal.updated_at,
            "reviewed_at": proposal.reviewed_at,
            "reviewer": proposal.reviewer,
            "decision_reason": proposal.decision_reason,
        }
        if proposal_record is not None:
            for field, value in values.items():
                setattr(proposal_record, field, value)
            continue
        session.add(KnowledgeProposalRecord(id=proposal.id, **values))

    seed_audit_events = [
        (
            "knowledge.index.registered",
            "knowledge_source_edition",
            "rae-ngle:manual-2010",
            {
                "entry_count": len(seed_index_entries()),
                "seed_batch": True,
                "stable_knowledge_created": False,
            },
        ),
        (
            "knowledge.segment.registered",
            "knowledge_index_entry",
            "rae-ngle:manual-2010:funciones-sintacticas",
            {
                "segment_count": len(seed_segments()),
                "seed_batch": True,
                "stable_knowledge_created": False,
            },
        ),
        (
            "knowledge.extraction.completed",
            "knowledge_extraction_run",
            "ext-rae-ngle-manual-2010-funciones-sintacticas-1",
            {
                "segment_id": "rae-ngle:manual-2010:funciones-sintacticas:seg-1",
                "status": "completed",
                "proposals_created": True,
                "nodes_created": True,
                "evidence_created": True,
                "claims_created": True,
                "cards_created": True,
                "published": False,
                "embeddings_created": False,
                "seed_batch": True,
            },
        ),
        (
            "knowledge.proposal.registered",
            "knowledge_extraction_run",
            "ext-rae-ngle-manual-2010-funciones-sintacticas-1",
            {
                "proposal_count": len(seed_proposals()),
                "segment_id": "rae-ngle:manual-2010:funciones-sintacticas:seg-1",
                "proposal_types": [proposal.proposal_type for proposal in seed_proposals()],
                "status": "approved",
                "published": False,
                "stable_knowledge_created": True,
                "seed_batch": True,
            },
        ),
        (
            "knowledge.proposal.approved",
            "knowledge_extraction_run",
            "ext-rae-ngle-manual-2010-funciones-sintacticas-1",
            {
                "proposal_count": len(seed_proposals()),
                "segment_id": "rae-ngle:manual-2010:funciones-sintacticas:seg-1",
                "proposal_types": [proposal.proposal_type for proposal in seed_proposals()],
                "materialized_node_ids": ["rae-ngle-complemento-directo"],
                "materialized_evidence_ids": ["ev-rae-ngle-complemento-directo-candidata"],
                "materialized_claim_ids": ["claim-rae-ngle-complemento-directo"],
                "materialized_card_ids": ["card-complemento-directo"],
                "published": False,
                "seed_batch": True,
            },
        ),
    ]
    for event_type, entity_type, entity_id, payload in seed_audit_events:
        existing_event = session.scalars(
            select(AuditEventRecord).where(
                AuditEventRecord.event_type == event_type,
                AuditEventRecord.entity_type == entity_type,
                AuditEventRecord.entity_id == entity_id,
            )
        ).first()
        if existing_event is None:
            session.add(
                AuditEventRecord(
                    event_type=event_type,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    payload=payload,
                    created_at=datetime.now(UTC),
                )
            )
        else:
            existing_event.payload = payload

    if session.get(KnowledgeVersionSnapshotRecord, "knowledge-v0") is None:
        candidate_object_ids = {
            "rae-ngle:manual-2010",
            "rae-ngle-complemento-directo",
            "ev-rae-ngle-complemento-directo-candidata",
            "claim-rae-ngle-complemento-directo",
            "card-complemento-directo",
            "rae-lese:edicion-2018",
            "rae-lese-dinamismo-frase",
            "ev-rae-lese-dinamismo-frase",
            "claim-rae-lese-dinamismo-frase",
            "card-dinamismo-frase",
            "rae-ole:edicion-2010",
            "rae-ole-acentuacion-grafica",
            "ev-rae-ole-acentuacion-grafica",
            "claim-rae-ole-acentuacion-grafica",
            "card-acentuacion-grafica",
            "rae-gtg:edicion-2019",
            "rae-gtg-terminologia-gramatical",
            "ev-rae-gtg-terminologia-gramatical",
            "claim-rae-gtg-terminologia-gramatical",
            "card-terminologia-gramatical",
            "rae-dle:edicion-23-digital",
            "rae-dle-precision-lexica",
            "ev-rae-dle-precision-lexica",
            "claim-rae-dle-precision-lexica",
            "card-precision-lexica",
            "rae-dpd:edicion-2005",
            "rae-dpd-dequeismo",
            "ev-rae-dpd-dequeismo",
            "claim-rae-dpd-dequeismo",
            "card-dequeismo-queismo",
            "fundeu-recomendaciones:web-2026",
            "fundeu-extranjerismos",
            "ev-fundeu-extranjerismos",
            "claim-fundeu-extranjerismos",
            "card-extranjerismos",
            "martinez-sousa-mele:edicion-2015",
            "martinez-sousa-criterio-editorial",
            "ev-martinez-sousa-criterio-editorial",
            "claim-martinez-sousa-criterio-editorial",
            "card-unidad-criterio-editorial",
            "rae-ngle-sujeto",
            "ev-rae-ngle-sujeto",
            "claim-rae-ngle-sujeto",
            "card-sujeto",
            "rae-ngle-predicado",
            "ev-rae-ngle-predicado",
            "claim-rae-ngle-predicado",
            "card-predicado",
            "rae-ngle-complemento-indirecto",
            "ev-rae-ngle-complemento-indirecto",
            "claim-rae-ngle-complemento-indirecto",
            "card-complemento-indirecto",
            "rae-ngle-atributo",
            "ev-rae-ngle-atributo",
            "claim-rae-ngle-atributo",
            "card-atributo",
            "rae-ngle-complemento-regimen",
            "ev-rae-ngle-complemento-regimen",
            "claim-rae-ngle-complemento-regimen",
            "card-complemento-regimen",
        }
        published_versions = {
            "knowledge-v1",
            "knowledge-v2",
            "knowledge-v3",
            "knowledge-v4",
            "knowledge-v5",
            "knowledge-v6",
            "knowledge-v7",
            "knowledge-v8",
            "knowledge-v9",
            "knowledge-v10",
        }
        candidate_object_ids.update(
            node.id for node in seed_nodes() if node.version in published_versions
        )
        candidate_object_ids.update(
            evidence.id for evidence in seed_evidence() if evidence.version in published_versions
        )
        candidate_object_ids.update(
            claim.id for claim in seed_claims() if claim.version in published_versions
        )
        candidate_object_ids.update(
            card.id for card in seed_cards() if card.version in published_versions
        )
        published_source_editions = [
            edition for edition in seed_source_editions() if edition.id not in candidate_object_ids
        ]
        published_nodes = [node for node in seed_nodes() if node.id not in candidate_object_ids]
        published_node_relations = [
            relation
            for relation in seed_node_relations()
            if relation.source_node_id not in candidate_object_ids
            and relation.target_node_id not in candidate_object_ids
        ]
        published_evidence = [
            evidence for evidence in seed_evidence() if evidence.id not in candidate_object_ids
        ]
        published_claims = [claim for claim in seed_claims() if claim.id not in candidate_object_ids]
        published_claim_evidence_links = [
            link
            for link in seed_claim_evidence_links()
            if link.claim_id not in candidate_object_ids and link.evidence_id not in candidate_object_ids
        ]
        published_cards = [card for card in seed_cards() if card.id not in candidate_object_ids]
        published_relations = [
            relation
            for relation in seed_relations()
            if relation.source_entity_id not in candidate_object_ids
            and relation.target_entity_id not in candidate_object_ids
        ]
        published_revisions = [
            revision
            for revision in seed_object_revisions()
            if revision.object_id not in candidate_object_ids
        ]
        session.add(
            KnowledgeVersionSnapshotRecord(
                version_id="knowledge-v0",
                status="seed_snapshot",
                source_ids=[source.id for source in seed_sources()],
                source_edition_ids=[edition.id for edition in published_source_editions],
                node_ids=[node.id for node in published_nodes],
                node_relation_ids=[relation.id for relation in published_node_relations],
                relation_ids=[relation.id for relation in published_relations],
                evidence_ids=[evidence.id for evidence in published_evidence],
                claim_ids=[claim.id for claim in published_claims],
                claim_evidence_link_ids=[link.id for link in published_claim_evidence_links],
                card_ids=[card.id for card in published_cards],
                revision_ids=[revision.id for revision in published_revisions],
                created_at="2026-07-22",
                updated_at="2026-07-22",
            )
        )
    if session.get(KnowledgeVersionSnapshotRecord, "knowledge-v5") is None:
        source_ids = ["rae-ngle", "rae-lese", "rae-ole", "rae-gtg", "rae-dle"]
        source_edition_ids = [
            "rae-ngle:manual-2010",
            "rae-lese:edicion-2018",
            "rae-ole:edicion-2010",
            "rae-gtg:edicion-2019",
            "rae-dle:edicion-23-digital",
        ]
        node_ids = [
            "rae-norma-estilo",
            "manual-rasgos-escritura",
            "rae-ngle-complemento-directo",
            "rae-lese-dinamismo-frase",
            "rae-ole-acentuacion-grafica",
            "rae-gtg-terminologia-gramatical",
            "rae-dle-precision-lexica",
        ]
        evidence_ids = [
            "ev-rae-ngle-complemento-directo-candidata",
            "ev-rae-lese-dinamismo-frase",
            "ev-rae-ole-acentuacion-grafica",
            "ev-rae-gtg-terminologia-gramatical",
            "ev-rae-dle-precision-lexica",
        ]
        claim_ids = [
            "claim-rae-ngle-complemento-directo",
            "claim-rae-lese-dinamismo-frase",
            "claim-rae-ole-acentuacion-grafica",
            "claim-rae-gtg-terminologia-gramatical",
            "claim-rae-dle-precision-lexica",
        ]
        card_ids = [
            "card-complemento-directo",
            "card-dinamismo-frase",
            "card-acentuacion-grafica",
            "card-terminologia-gramatical",
            "card-precision-lexica",
        ]
        snapshot_object_ids = {
            *source_ids,
            *source_edition_ids,
            *node_ids,
            *evidence_ids,
            *claim_ids,
            *card_ids,
        }
        version_chain = {
            "knowledge-v1",
            "knowledge-v2",
            "knowledge-v3",
            "knowledge-v4",
            "knowledge-v5",
        }
        node_relation_ids = [
            relation.id
            for relation in seed_node_relations()
            if relation.version in version_chain
            and relation.source_node_id in snapshot_object_ids
            and relation.target_node_id in snapshot_object_ids
        ]
        relation_ids = [
            relation.id
            for relation in seed_relations()
            if relation.version in version_chain
            and relation.source_entity_id in snapshot_object_ids
            and relation.target_entity_id in snapshot_object_ids
        ]
        revision_ids = [
            revision.id
            for revision in seed_object_revisions()
            if revision.object_id in snapshot_object_ids or revision.object_id in relation_ids
        ]
        claim_evidence_link_ids = [
            link.id
            for link in seed_claim_evidence_links()
            if link.claim_id in claim_ids and link.evidence_id in evidence_ids
        ]
        session.add(
            KnowledgeVersionSnapshotRecord(
                version_id="knowledge-v5",
                status="published",
                source_ids=source_ids,
                source_edition_ids=source_edition_ids,
                node_ids=node_ids,
                node_relation_ids=node_relation_ids,
                relation_ids=relation_ids,
                evidence_ids=evidence_ids,
                claim_ids=claim_ids,
                claim_evidence_link_ids=claim_evidence_link_ids,
                card_ids=card_ids,
                revision_ids=revision_ids,
                created_at="2026-07-23T04:00:00+00:00",
                updated_at="2026-07-23T04:00:00+00:00",
            )
        )
    if session.get(KnowledgeVersionSnapshotRecord, "knowledge-v6") is None:
        source_ids = [
            "rae-ngle",
            "rae-lese",
            "rae-ole",
            "rae-gtg",
            "rae-dle",
            "rae-dpd",
            "fundeu-recomendaciones",
            "martinez-sousa-mele",
        ]
        source_edition_ids = [
            "rae-ngle:manual-2010",
            "rae-lese:edicion-2018",
            "rae-ole:edicion-2010",
            "rae-gtg:edicion-2019",
            "rae-dle:edicion-23-digital",
            "rae-dpd:edicion-2005",
            "fundeu-recomendaciones:web-2026",
            "martinez-sousa-mele:edicion-2015",
        ]
        node_ids = [
            "rae-norma-estilo",
            "manual-rasgos-escritura",
            "rae-ngle-complemento-directo",
            "rae-lese-dinamismo-frase",
            "rae-ole-acentuacion-grafica",
            "rae-gtg-terminologia-gramatical",
            "rae-dle-precision-lexica",
            "rae-dpd-dequeismo",
            "fundeu-extranjerismos",
            "martinez-sousa-criterio-editorial",
        ]
        evidence_ids = [
            "ev-rae-ngle-complemento-directo-candidata",
            "ev-rae-lese-dinamismo-frase",
            "ev-rae-ole-acentuacion-grafica",
            "ev-rae-gtg-terminologia-gramatical",
            "ev-rae-dle-precision-lexica",
            "ev-rae-dpd-dequeismo",
            "ev-fundeu-extranjerismos",
            "ev-martinez-sousa-criterio-editorial",
        ]
        claim_ids = [
            "claim-rae-ngle-complemento-directo",
            "claim-rae-lese-dinamismo-frase",
            "claim-rae-ole-acentuacion-grafica",
            "claim-rae-gtg-terminologia-gramatical",
            "claim-rae-dle-precision-lexica",
            "claim-rae-dpd-dequeismo",
            "claim-fundeu-extranjerismos",
            "claim-martinez-sousa-criterio-editorial",
        ]
        card_ids = [
            "card-complemento-directo",
            "card-dinamismo-frase",
            "card-acentuacion-grafica",
            "card-terminologia-gramatical",
            "card-precision-lexica",
            "card-dequeismo-queismo",
            "card-extranjerismos",
            "card-unidad-criterio-editorial",
        ]
        snapshot_object_ids = {
            *source_ids,
            *source_edition_ids,
            *node_ids,
            *evidence_ids,
            *claim_ids,
            *card_ids,
        }
        version_chain = {
            "knowledge-v1",
            "knowledge-v2",
            "knowledge-v3",
            "knowledge-v4",
            "knowledge-v5",
            "knowledge-v6",
        }
        node_relation_ids = [
            relation.id
            for relation in seed_node_relations()
            if relation.version in version_chain
            and relation.source_node_id in snapshot_object_ids
            and relation.target_node_id in snapshot_object_ids
        ]
        relation_ids = [
            relation.id
            for relation in seed_relations()
            if relation.version in version_chain
            and relation.source_entity_id in snapshot_object_ids
            and relation.target_entity_id in snapshot_object_ids
        ]
        revision_ids = [
            revision.id
            for revision in seed_object_revisions()
            if revision.object_id in snapshot_object_ids or revision.object_id in relation_ids
        ]
        claim_evidence_link_ids = [
            link.id
            for link in seed_claim_evidence_links()
            if link.claim_id in claim_ids and link.evidence_id in evidence_ids
        ]
        session.add(
            KnowledgeVersionSnapshotRecord(
                version_id="knowledge-v6",
                status="published",
                source_ids=source_ids,
                source_edition_ids=source_edition_ids,
                node_ids=node_ids,
                node_relation_ids=node_relation_ids,
                relation_ids=relation_ids,
                evidence_ids=evidence_ids,
                claim_ids=claim_ids,
                claim_evidence_link_ids=claim_evidence_link_ids,
                card_ids=card_ids,
                revision_ids=revision_ids,
                created_at="2026-07-23T05:00:00+00:00",
                updated_at="2026-07-23T05:00:00+00:00",
            )
        )
    if session.get(KnowledgeVersionSnapshotRecord, "knowledge-v7") is None:
        source_ids = [
            "rae-ngle",
            "rae-lese",
            "rae-ole",
            "rae-gtg",
            "rae-dle",
            "rae-dpd",
            "fundeu-recomendaciones",
            "martinez-sousa-mele",
        ]
        source_edition_ids = [
            "rae-ngle:manual-2010",
            "rae-lese:edicion-2018",
            "rae-ole:edicion-2010",
            "rae-gtg:edicion-2019",
            "rae-dle:edicion-23-digital",
            "rae-dpd:edicion-2005",
            "fundeu-recomendaciones:web-2026",
            "martinez-sousa-mele:edicion-2015",
        ]
        node_ids = [
            "rae-norma-estilo",
            "manual-rasgos-escritura",
            "rae-ngle-complemento-directo",
            "rae-lese-dinamismo-frase",
            "rae-ole-acentuacion-grafica",
            "rae-gtg-terminologia-gramatical",
            "rae-dle-precision-lexica",
            "rae-dpd-dequeismo",
            "fundeu-extranjerismos",
            "martinez-sousa-criterio-editorial",
            "rae-ngle-sujeto",
            "rae-ngle-predicado",
            "rae-ngle-complemento-indirecto",
            "rae-ngle-atributo",
            "rae-ngle-complemento-regimen",
        ]
        evidence_ids = [
            "ev-rae-ngle-complemento-directo-candidata",
            "ev-rae-lese-dinamismo-frase",
            "ev-rae-ole-acentuacion-grafica",
            "ev-rae-gtg-terminologia-gramatical",
            "ev-rae-dle-precision-lexica",
            "ev-rae-dpd-dequeismo",
            "ev-fundeu-extranjerismos",
            "ev-martinez-sousa-criterio-editorial",
            "ev-rae-ngle-sujeto",
            "ev-rae-ngle-predicado",
            "ev-rae-ngle-complemento-indirecto",
            "ev-rae-ngle-atributo",
            "ev-rae-ngle-complemento-regimen",
        ]
        claim_ids = [
            "claim-rae-ngle-complemento-directo",
            "claim-rae-lese-dinamismo-frase",
            "claim-rae-ole-acentuacion-grafica",
            "claim-rae-gtg-terminologia-gramatical",
            "claim-rae-dle-precision-lexica",
            "claim-rae-dpd-dequeismo",
            "claim-fundeu-extranjerismos",
            "claim-martinez-sousa-criterio-editorial",
            "claim-rae-ngle-sujeto",
            "claim-rae-ngle-predicado",
            "claim-rae-ngle-complemento-indirecto",
            "claim-rae-ngle-atributo",
            "claim-rae-ngle-complemento-regimen",
        ]
        card_ids = [
            "card-complemento-directo",
            "card-dinamismo-frase",
            "card-acentuacion-grafica",
            "card-terminologia-gramatical",
            "card-precision-lexica",
            "card-dequeismo-queismo",
            "card-extranjerismos",
            "card-unidad-criterio-editorial",
            "card-sujeto",
            "card-predicado",
            "card-complemento-indirecto",
            "card-atributo",
            "card-complemento-regimen",
        ]
        snapshot_object_ids = {
            *source_ids,
            *source_edition_ids,
            *node_ids,
            *evidence_ids,
            *claim_ids,
            *card_ids,
        }
        version_chain = {
            "knowledge-v1",
            "knowledge-v2",
            "knowledge-v3",
            "knowledge-v4",
            "knowledge-v5",
            "knowledge-v6",
            "knowledge-v7",
        }
        node_relation_ids = [
            relation.id
            for relation in seed_node_relations()
            if relation.version in version_chain
            and relation.source_node_id in snapshot_object_ids
            and relation.target_node_id in snapshot_object_ids
        ]
        relation_ids = [
            relation.id
            for relation in seed_relations()
            if relation.version in version_chain
            and relation.source_entity_id in snapshot_object_ids
            and relation.target_entity_id in snapshot_object_ids
        ]
        revision_ids = [
            revision.id
            for revision in seed_object_revisions()
            if revision.object_id in snapshot_object_ids or revision.object_id in relation_ids
        ]
        claim_evidence_link_ids = [
            link.id
            for link in seed_claim_evidence_links()
            if link.claim_id in claim_ids and link.evidence_id in evidence_ids
        ]
        session.add(
            KnowledgeVersionSnapshotRecord(
                version_id="knowledge-v7",
                status="published",
                source_ids=source_ids,
                source_edition_ids=source_edition_ids,
                node_ids=node_ids,
                node_relation_ids=node_relation_ids,
                relation_ids=relation_ids,
                evidence_ids=evidence_ids,
                claim_ids=claim_ids,
                claim_evidence_link_ids=claim_evidence_link_ids,
                card_ids=card_ids,
                revision_ids=revision_ids,
                created_at="2026-07-23T06:00:00+00:00",
                updated_at="2026-07-23T06:00:00+00:00",
            )
        )
    _add_published_snapshot(
        session,
        version_id="knowledge-v8",
        version_chain={
            "knowledge-v1",
            "knowledge-v2",
            "knowledge-v3",
            "knowledge-v4",
            "knowledge-v5",
            "knowledge-v6",
            "knowledge-v7",
            "knowledge-v8",
        },
        timestamp="2026-07-23T07:00:00+00:00",
    )
    _add_published_snapshot(
        session,
        version_id="knowledge-v9",
        version_chain={
            "knowledge-v1",
            "knowledge-v2",
            "knowledge-v3",
            "knowledge-v4",
            "knowledge-v5",
            "knowledge-v6",
            "knowledge-v7",
            "knowledge-v8",
            "knowledge-v9",
        },
        timestamp="2026-07-23T08:00:00+00:00",
    )
    _add_published_snapshot(
        session,
        version_id="knowledge-v10",
        version_chain={
            "knowledge-v1",
            "knowledge-v2",
            "knowledge-v3",
            "knowledge-v4",
            "knowledge-v5",
            "knowledge-v6",
            "knowledge-v7",
            "knowledge-v8",
            "knowledge-v9",
            "knowledge-v10",
        },
        timestamp="2026-07-23T09:00:00+00:00",
    )
    if session.get(KnowledgeVersionSnapshotRecord, "knowledge-v1") is None:
        source_ids = ["rae-ngle"]
        source_edition_ids = ["rae-ngle:manual-2010"]
        node_ids = ["rae-ngle-complemento-directo", "rae-norma-estilo"]
        evidence_ids = ["ev-rae-ngle-complemento-directo-candidata"]
        claim_ids = ["claim-rae-ngle-complemento-directo"]
        card_ids = ["card-complemento-directo"]
        snapshot_object_ids = {
            *source_ids,
            *source_edition_ids,
            *node_ids,
            *evidence_ids,
            *claim_ids,
            *card_ids,
        }
        node_relation_ids = [
            relation.id
            for relation in seed_node_relations()
            if relation.version == "knowledge-v1"
            and relation.source_node_id in snapshot_object_ids
            and relation.target_node_id in snapshot_object_ids
        ]
        relation_ids = [
            relation.id
            for relation in seed_relations()
            if relation.version == "knowledge-v1"
            and relation.source_entity_id in snapshot_object_ids
            and relation.target_entity_id in snapshot_object_ids
        ]
        revision_ids = [
            revision.id
            for revision in seed_object_revisions()
            if revision.object_id in snapshot_object_ids or revision.object_id in relation_ids
        ]
        claim_evidence_link_ids = [
            link.id
            for link in seed_claim_evidence_links()
            if link.claim_id in claim_ids and link.evidence_id in evidence_ids
        ]
        session.add(
            KnowledgeVersionSnapshotRecord(
                version_id="knowledge-v1",
                status="published",
                source_ids=source_ids,
                source_edition_ids=source_edition_ids,
                node_ids=node_ids,
                node_relation_ids=node_relation_ids,
                relation_ids=relation_ids,
                evidence_ids=evidence_ids,
                claim_ids=claim_ids,
                claim_evidence_link_ids=claim_evidence_link_ids,
                card_ids=card_ids,
                revision_ids=revision_ids,
                created_at="2026-07-23",
                updated_at="2026-07-23",
            )
        )
    if session.get(KnowledgeVersionSnapshotRecord, "knowledge-v2") is None:
        source_ids = ["rae-ngle", "rae-lese"]
        source_edition_ids = ["rae-ngle:manual-2010", "rae-lese:edicion-2018"]
        node_ids = [
            "rae-norma-estilo",
            "manual-rasgos-escritura",
            "rae-ngle-complemento-directo",
            "rae-lese-dinamismo-frase",
        ]
        evidence_ids = [
            "ev-rae-ngle-complemento-directo-candidata",
            "ev-rae-lese-dinamismo-frase",
        ]
        claim_ids = [
            "claim-rae-ngle-complemento-directo",
            "claim-rae-lese-dinamismo-frase",
        ]
        card_ids = ["card-complemento-directo", "card-dinamismo-frase"]
        snapshot_object_ids = {
            *source_ids,
            *source_edition_ids,
            *node_ids,
            *evidence_ids,
            *claim_ids,
            *card_ids,
        }
        node_relation_ids = [
            relation.id
            for relation in seed_node_relations()
            if relation.version in {"knowledge-v1", "knowledge-v2"}
            and relation.source_node_id in snapshot_object_ids
            and relation.target_node_id in snapshot_object_ids
        ]
        relation_ids = [
            relation.id
            for relation in seed_relations()
            if relation.version in {"knowledge-v1", "knowledge-v2"}
            and relation.source_entity_id in snapshot_object_ids
            and relation.target_entity_id in snapshot_object_ids
        ]
        revision_ids = [
            revision.id
            for revision in seed_object_revisions()
            if revision.object_id in snapshot_object_ids or revision.object_id in relation_ids
        ]
        claim_evidence_link_ids = [
            link.id
            for link in seed_claim_evidence_links()
            if link.claim_id in claim_ids and link.evidence_id in evidence_ids
        ]
        session.add(
            KnowledgeVersionSnapshotRecord(
                version_id="knowledge-v2",
                status="published",
                source_ids=source_ids,
                source_edition_ids=source_edition_ids,
                node_ids=node_ids,
                node_relation_ids=node_relation_ids,
                relation_ids=relation_ids,
                evidence_ids=evidence_ids,
                claim_ids=claim_ids,
                claim_evidence_link_ids=claim_evidence_link_ids,
                card_ids=card_ids,
                revision_ids=revision_ids,
                created_at="2026-07-23T01:00:00+00:00",
                updated_at="2026-07-23T01:00:00+00:00",
            )
        )
    if session.get(KnowledgeVersionSnapshotRecord, "knowledge-v3") is None:
        source_ids = ["rae-ngle", "rae-lese", "rae-ole"]
        source_edition_ids = [
            "rae-ngle:manual-2010",
            "rae-lese:edicion-2018",
            "rae-ole:edicion-2010",
        ]
        node_ids = [
            "rae-norma-estilo",
            "manual-rasgos-escritura",
            "rae-ngle-complemento-directo",
            "rae-lese-dinamismo-frase",
            "rae-ole-acentuacion-grafica",
        ]
        evidence_ids = [
            "ev-rae-ngle-complemento-directo-candidata",
            "ev-rae-lese-dinamismo-frase",
            "ev-rae-ole-acentuacion-grafica",
        ]
        claim_ids = [
            "claim-rae-ngle-complemento-directo",
            "claim-rae-lese-dinamismo-frase",
            "claim-rae-ole-acentuacion-grafica",
        ]
        card_ids = ["card-complemento-directo", "card-dinamismo-frase", "card-acentuacion-grafica"]
        snapshot_object_ids = {
            *source_ids,
            *source_edition_ids,
            *node_ids,
            *evidence_ids,
            *claim_ids,
            *card_ids,
        }
        node_relation_ids = [
            relation.id
            for relation in seed_node_relations()
            if relation.version in {"knowledge-v1", "knowledge-v2", "knowledge-v3"}
            and relation.source_node_id in snapshot_object_ids
            and relation.target_node_id in snapshot_object_ids
        ]
        relation_ids = [
            relation.id
            for relation in seed_relations()
            if relation.version in {"knowledge-v1", "knowledge-v2", "knowledge-v3"}
            and relation.source_entity_id in snapshot_object_ids
            and relation.target_entity_id in snapshot_object_ids
        ]
        revision_ids = [
            revision.id
            for revision in seed_object_revisions()
            if revision.object_id in snapshot_object_ids or revision.object_id in relation_ids
        ]
        claim_evidence_link_ids = [
            link.id
            for link in seed_claim_evidence_links()
            if link.claim_id in claim_ids and link.evidence_id in evidence_ids
        ]
        session.add(
            KnowledgeVersionSnapshotRecord(
                version_id="knowledge-v3",
                status="published",
                source_ids=source_ids,
                source_edition_ids=source_edition_ids,
                node_ids=node_ids,
                node_relation_ids=node_relation_ids,
                relation_ids=relation_ids,
                evidence_ids=evidence_ids,
                claim_ids=claim_ids,
                claim_evidence_link_ids=claim_evidence_link_ids,
                card_ids=card_ids,
                revision_ids=revision_ids,
                created_at="2026-07-23T02:00:00+00:00",
                updated_at="2026-07-23T02:00:00+00:00",
            )
        )
    if session.get(KnowledgeVersionSnapshotRecord, "knowledge-v4") is None:
        source_ids = ["rae-ngle", "rae-lese", "rae-ole", "rae-gtg"]
        source_edition_ids = [
            "rae-ngle:manual-2010",
            "rae-lese:edicion-2018",
            "rae-ole:edicion-2010",
            "rae-gtg:edicion-2019",
        ]
        node_ids = [
            "rae-norma-estilo",
            "manual-rasgos-escritura",
            "rae-ngle-complemento-directo",
            "rae-lese-dinamismo-frase",
            "rae-ole-acentuacion-grafica",
            "rae-gtg-terminologia-gramatical",
        ]
        evidence_ids = [
            "ev-rae-ngle-complemento-directo-candidata",
            "ev-rae-lese-dinamismo-frase",
            "ev-rae-ole-acentuacion-grafica",
            "ev-rae-gtg-terminologia-gramatical",
        ]
        claim_ids = [
            "claim-rae-ngle-complemento-directo",
            "claim-rae-lese-dinamismo-frase",
            "claim-rae-ole-acentuacion-grafica",
            "claim-rae-gtg-terminologia-gramatical",
        ]
        card_ids = [
            "card-complemento-directo",
            "card-dinamismo-frase",
            "card-acentuacion-grafica",
            "card-terminologia-gramatical",
        ]
        snapshot_object_ids = {
            *source_ids,
            *source_edition_ids,
            *node_ids,
            *evidence_ids,
            *claim_ids,
            *card_ids,
        }
        node_relation_ids = [
            relation.id
            for relation in seed_node_relations()
            if relation.version in {"knowledge-v1", "knowledge-v2", "knowledge-v3", "knowledge-v4"}
            and relation.source_node_id in snapshot_object_ids
            and relation.target_node_id in snapshot_object_ids
        ]
        relation_ids = [
            relation.id
            for relation in seed_relations()
            if relation.version in {"knowledge-v1", "knowledge-v2", "knowledge-v3", "knowledge-v4"}
            and relation.source_entity_id in snapshot_object_ids
            and relation.target_entity_id in snapshot_object_ids
        ]
        revision_ids = [
            revision.id
            for revision in seed_object_revisions()
            if revision.object_id in snapshot_object_ids or revision.object_id in relation_ids
        ]
        claim_evidence_link_ids = [
            link.id
            for link in seed_claim_evidence_links()
            if link.claim_id in claim_ids and link.evidence_id in evidence_ids
        ]
        session.add(
            KnowledgeVersionSnapshotRecord(
                version_id="knowledge-v4",
                status="published",
                source_ids=source_ids,
                source_edition_ids=source_edition_ids,
                node_ids=node_ids,
                node_relation_ids=node_relation_ids,
                relation_ids=relation_ids,
                evidence_ids=evidence_ids,
                claim_ids=claim_ids,
                claim_evidence_link_ids=claim_evidence_link_ids,
                card_ids=card_ids,
                revision_ids=revision_ids,
                created_at="2026-07-23T03:00:00+00:00",
                updated_at="2026-07-23T03:00:00+00:00",
            )
        )
