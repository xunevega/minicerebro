from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
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

SNAPSHOT_EXPORT_FORMAT = "knowledge-seed-snapshot-v1"

KNOWLEDGE_EXPORT_TABLES = (
    ("knowledge_versions", KnowledgeVersionRecord),
    ("knowledge_version_snapshots", KnowledgeVersionSnapshotRecord),
    ("knowledge_sources", KnowledgeSourceRecord),
    ("knowledge_source_editions", KnowledgeSourceEditionRecord),
    ("knowledge_ingestion_batches", KnowledgeIngestionBatchRecord),
    ("knowledge_index_entries", KnowledgeIndexEntryRecord),
    ("knowledge_segments", KnowledgeSegmentRecord),
    ("knowledge_extraction_runs", KnowledgeExtractionRunRecord),
    ("knowledge_proposals", KnowledgeProposalRecord),
    ("knowledge_nodes", KnowledgeNodeRecord),
    ("knowledge_node_relations", KnowledgeNodeRelationRecord),
    ("knowledge_relations", KnowledgeRelationRecord),
    ("knowledge_evidence_items", KnowledgeEvidenceItemRecord),
    ("knowledge_evidence_revisions", KnowledgeEvidenceRevisionRecord),
    ("knowledge_cards", KnowledgeCardRecord),
    ("knowledge_claims", KnowledgeClaimRecord),
    ("knowledge_claim_evidence_links", KnowledgeClaimEvidenceLinkRecord),
    ("knowledge_claim_revisions", KnowledgeClaimRevisionRecord),
    ("knowledge_object_revisions", KnowledgeObjectRevisionRecord),
)


def latest_published_snapshot_version(session: Session) -> str:
    versions = session.scalars(
        select(KnowledgeVersionRecord)
        .join(
            KnowledgeVersionSnapshotRecord,
            KnowledgeVersionSnapshotRecord.version_id == KnowledgeVersionRecord.id,
        )
        .where(KnowledgeVersionRecord.status == "published")
    ).all()
    if not versions:
        raise ValueError("no published knowledge snapshot is available")
    return max(versions, key=lambda version: _version_number(version.id)).id


def export_knowledge_seed_snapshot(
    session: Session,
    *,
    version: str,
) -> dict[str, Any]:
    snapshot = session.get(KnowledgeVersionSnapshotRecord, version)
    version_record = session.get(KnowledgeVersionRecord, version)
    if snapshot is None or version_record is None:
        raise ValueError(f"knowledge version is not available: {version}")

    tables = {
        table_name: _rows_for_model(session, model)
        for table_name, model in KNOWLEDGE_EXPORT_TABLES
    }

    return {
        "format": SNAPSHOT_EXPORT_FORMAT,
        "version": version,
        "status": version_record.status,
        "published_at": version_record.published_at,
        "counts": {
            table_name: len(rows)
            for table_name, rows in tables.items()
        },
        "snapshot_counts": {
            "source_count": len(snapshot.source_ids),
            "source_edition_count": len(snapshot.source_edition_ids),
            "node_count": len(snapshot.node_ids),
            "node_relation_count": len(snapshot.node_relation_ids),
            "relation_count": len(snapshot.relation_ids),
            "evidence_count": len(snapshot.evidence_ids),
            "claim_count": len(snapshot.claim_ids),
            "claim_evidence_link_count": len(snapshot.claim_evidence_link_ids),
            "card_count": len(snapshot.card_ids),
            "revision_count": len(snapshot.revision_ids),
        },
        "tables": tables,
    }


def _version_number(version_id: str) -> int:
    prefix = "knowledge-v"
    if not version_id.startswith(prefix):
        return -1
    value = version_id.removeprefix(prefix)
    return int(value) if value.isdigit() else -1


def _rows_for_model(session: Session, model: type) -> list[dict[str, Any]]:
    primary_key = list(model.__table__.primary_key.columns)[0].name
    rows = session.scalars(select(model).order_by(getattr(model, primary_key))).all()
    return [_record_to_dict(row) for row in rows]


def _record_to_dict(record: object) -> dict[str, Any]:
    return {
        column.name: getattr(record, column.name)
        for column in record.__table__.columns
    }
