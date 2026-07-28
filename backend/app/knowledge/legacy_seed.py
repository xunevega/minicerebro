from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

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
    KnowledgeSourceEditionRecord,
    KnowledgeSourceRecord,
    KnowledgeVersionRecord,
    KnowledgeVersionSnapshotRecord,
)
from app.knowledge.contracts import LATEST_KNOWLEDGE_VERSION
from app.knowledge.snapshot_data import load_knowledge_seed_snapshot

SNAPSHOT_TABLE_ORDER = [
    "knowledge_versions",
    "knowledge_sources",
    "knowledge_source_editions",
    "knowledge_ingestion_batches",
    "knowledge_index_entries",
    "knowledge_segments",
    "knowledge_extraction_runs",
    "knowledge_proposals",
    "knowledge_nodes",
    "knowledge_node_relations",
    "knowledge_relations",
    "knowledge_cards",
    "knowledge_evidence_items",
    "knowledge_evidence_revisions",
    "knowledge_claims",
    "knowledge_claim_evidence_links",
    "knowledge_claim_revisions",
    "knowledge_object_revisions",
    "knowledge_version_snapshots",
]

SNAPSHOT_TABLE_RECORDS = {
    "knowledge_cards": KnowledgeCardRecord,
    "knowledge_claim_evidence_links": KnowledgeClaimEvidenceLinkRecord,
    "knowledge_claim_revisions": KnowledgeClaimRevisionRecord,
    "knowledge_claims": KnowledgeClaimRecord,
    "knowledge_evidence_items": KnowledgeEvidenceItemRecord,
    "knowledge_evidence_revisions": KnowledgeEvidenceRevisionRecord,
    "knowledge_extraction_runs": KnowledgeExtractionRunRecord,
    "knowledge_index_entries": KnowledgeIndexEntryRecord,
    "knowledge_ingestion_batches": KnowledgeIngestionBatchRecord,
    "knowledge_node_relations": KnowledgeNodeRelationRecord,
    "knowledge_nodes": KnowledgeNodeRecord,
    "knowledge_object_revisions": KnowledgeObjectRevisionRecord,
    "knowledge_proposals": KnowledgeProposalRecord,
    "knowledge_relations": KnowledgeRelationRecord,
    "knowledge_segments": KnowledgeSegmentRecord,
    "knowledge_source_editions": KnowledgeSourceEditionRecord,
    "knowledge_sources": KnowledgeSourceRecord,
    "knowledge_version_snapshots": KnowledgeVersionSnapshotRecord,
    "knowledge_versions": KnowledgeVersionRecord,
}

LEGACY_AUDIT_EVENTS = [
    (
        "knowledge.index.registered",
        "knowledge_source_edition",
        "rae-ngle:manual-2010",
        {
            "seed_batch": True,
            "stable_knowledge_created": False,
        },
    ),
    (
        "knowledge.segment.registered",
        "knowledge_index_entry",
        "rae-ngle:manual-2010:funciones-sintacticas",
        {
            "seed_batch": True,
            "stable_knowledge_created": False,
        },
    ),
    (
        "knowledge.extraction.completed",
        "knowledge_extraction_run",
        "ext-rae-ngle-manual-2010-funciones-sintacticas-1",
        {
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
            "materialized_node_ids": ["rae-ngle-complemento-directo"],
            "materialized_evidence_ids": ["ev-rae-ngle-complemento-directo-candidata"],
            "materialized_claim_ids": ["claim-rae-ngle-complemento-directo"],
            "materialized_card_ids": ["card-complemento-directo"],
            "published": False,
            "seed_batch": True,
        },
    ),
]


def ensure_knowledge_seed_data(session: Session) -> None:
    snapshot = load_knowledge_seed_snapshot(LATEST_KNOWLEDGE_VERSION)
    _insert_snapshot_tables(session, snapshot["tables"])
    _ensure_legacy_audit_events(session, snapshot["tables"])


def _insert_snapshot_tables(session: Session, tables: dict[str, list[dict[str, Any]]]) -> None:
    for table_name in SNAPSHOT_TABLE_ORDER:
        rows = tables.get(table_name, [])
        if not rows:
            continue
        record_class = SNAPSHOT_TABLE_RECORDS[table_name]
        table = record_class.__table__
        primary_key = next(iter(table.primary_key.columns))
        for row in rows:
            exists = session.execute(
                select(primary_key).where(primary_key == row[primary_key.name])
            ).first()
            if exists is not None:
                continue
            session.execute(table.insert().values(**row))
        session.flush()


def _ensure_legacy_audit_events(session: Session, tables: dict[str, list[dict[str, Any]]]) -> None:
    counts = {table_name: len(rows) for table_name, rows in tables.items()}
    for event_type, entity_type, entity_id, payload in LEGACY_AUDIT_EVENTS:
        existing_event = session.scalars(
            select(AuditEventRecord).where(
                AuditEventRecord.event_type == event_type,
                AuditEventRecord.entity_type == entity_type,
                AuditEventRecord.entity_id == entity_id,
            )
        ).first()
        event_payload = {
            **payload,
            "snapshot_version": LATEST_KNOWLEDGE_VERSION,
            "snapshot_counts": counts,
        }
        if existing_event is None:
            session.add(
                AuditEventRecord(
                    event_type=event_type,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    payload=event_payload,
                    created_at=datetime.now(UTC),
                )
            )
            continue
        existing_event.payload = event_payload
