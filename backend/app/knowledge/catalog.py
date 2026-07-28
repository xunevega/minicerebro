from __future__ import annotations

from functools import lru_cache
from typing import Any, TypeVar

from pydantic import BaseModel

from app.core.models import (
    KnowledgeCard,
    KnowledgeClaim,
    KnowledgeClaimEvidenceLink,
    KnowledgeEvidenceItem,
    KnowledgeExtractionRun,
    KnowledgeIndexEntry,
    KnowledgeIngestionBatch,
    KnowledgeNode,
    KnowledgeNodeRelation,
    KnowledgeObjectRevision,
    KnowledgeProposal,
    KnowledgeRelation,
    KnowledgeSegment,
    KnowledgeSource,
    KnowledgeSourceEdition,
    KnowledgeVersion,
)
from app.knowledge.contracts import (
    DEFAULT_SOURCE_EDITION,
    DEFAULT_SOURCE_LOCATION,
    DEFAULT_SOURCE_LOCATORS,
    EXCLUDED_VERSIONED_OBJECT_TYPES,
    INGESTION_ALTERNATIVE_STATES,
    INGESTION_FLOW,
    INGESTION_LIFECYCLE,
    KNOWLEDGE_VERSION_IDS,
    LATEST_KNOWLEDGE_VERSION,
    PUBLICATION_LIFECYCLE,
    PUBLICATION_REQUIREMENTS,
    PUBLICATION_VALIDATIONS,
    QUERY_LIFECYCLE,
    QUERY_OUT_OF_SCOPE,
    VERSIONED_OBJECT_TYPES,
)
from app.knowledge.snapshot_data import load_knowledge_seed_snapshot

T = TypeVar("T", bound=BaseModel)

__all__ = [
    "DEFAULT_SOURCE_EDITION",
    "DEFAULT_SOURCE_LOCATION",
    "DEFAULT_SOURCE_LOCATORS",
    "DEFAULT_SOURCE_PUBLICATION_DATE",
    "DEFAULT_SOURCE_RIGHTS",
    "DEFAULT_SOURCE_STRUCTURE",
    "EXCLUDED_VERSIONED_OBJECT_TYPES",
    "INGESTION_ALTERNATIVE_STATES",
    "INGESTION_FLOW",
    "INGESTION_LIFECYCLE",
    "KNOWLEDGE_PUBLISHED_AT",
    "KNOWLEDGE_V1_PUBLISHED_AT",
    "KNOWLEDGE_VERSION",
    "KNOWLEDGE_VERSION_IDS",
    "LATEST_KNOWLEDGE_VERSION",
    "LATEST_PUBLISHED_KNOWLEDGE_VERSION",
    "PUBLICATION_LIFECYCLE",
    "PUBLICATION_REQUIREMENTS",
    "PUBLICATION_VALIDATIONS",
    "PUBLISHED_KNOWLEDGE_VERSION",
    "QUERY_LIFECYCLE",
    "QUERY_OUT_OF_SCOPE",
    "RELATION_UPDATED_AT",
    "VERSIONED_OBJECT_TYPES",
    "seed_cards",
    "seed_claim_evidence_links",
    "seed_claim_revisions",
    "seed_claims",
    "seed_evidence",
    "seed_evidence_revisions",
    "seed_extraction_runs",
    "seed_index_entries",
    "seed_ingestion_batches",
    "seed_node_relations",
    "seed_nodes",
    "seed_object_revisions",
    "seed_proposals",
    "seed_relations",
    "seed_segments",
    "seed_source_editions",
    "seed_sources",
    "seed_versions",
]
for _version_number in range(2, 52):
    __all__.append(f"KNOWLEDGE_V{_version_number}_VERSION")
    __all__.append(f"KNOWLEDGE_V{_version_number}_PUBLISHED_AT")

KNOWLEDGE_VERSION = "knowledge-v0"
PUBLISHED_KNOWLEDGE_VERSION = "knowledge-v1"
LATEST_PUBLISHED_KNOWLEDGE_VERSION = LATEST_KNOWLEDGE_VERSION

for _version_number in range(2, 52):
    globals()[f"KNOWLEDGE_V{_version_number}_VERSION"] = f"knowledge-v{_version_number}"

_PUBLISHED_AT_BY_VERSION = {
    row["id"]: row["published_at"]
    for row in load_knowledge_seed_snapshot(LATEST_PUBLISHED_KNOWLEDGE_VERSION)["tables"][
        "knowledge_versions"
    ]
}

KNOWLEDGE_PUBLISHED_AT = _PUBLISHED_AT_BY_VERSION.get(KNOWLEDGE_VERSION, "2026-07-21")
KNOWLEDGE_V1_PUBLISHED_AT = _PUBLISHED_AT_BY_VERSION.get(PUBLISHED_KNOWLEDGE_VERSION, "2026-07-22")
for _version_number in range(2, 52):
    _version_id = f"knowledge-v{_version_number}"
    globals()[f"KNOWLEDGE_V{_version_number}_PUBLISHED_AT"] = _PUBLISHED_AT_BY_VERSION.get(
        _version_id,
        "2026-07-22",
    )

RELATION_UPDATED_AT = _PUBLISHED_AT_BY_VERSION.get(LATEST_PUBLISHED_KNOWLEDGE_VERSION, "2026-07-27")
DEFAULT_SOURCE_PUBLICATION_DATE = "pendiente de identificacion"
DEFAULT_SOURCE_RIGHTS = "registro autorizado; contenido no ingerido"
DEFAULT_SOURCE_STRUCTURE = ["pendiente de estructuracion"]


@lru_cache(maxsize=1)
def _snapshot_tables() -> dict[str, list[dict[str, Any]]]:
    snapshot = load_knowledge_seed_snapshot(LATEST_PUBLISHED_KNOWLEDGE_VERSION)
    return snapshot["tables"]


def _rows(table_name: str) -> list[dict[str, Any]]:
    return [dict(row) for row in _snapshot_tables()[table_name]]


def _models(model: type[T], table_name: str) -> list[T]:
    return [model.model_validate(row) for row in _rows(table_name)]


def _revision_dicts(table_name: str) -> list[dict[str, Any]]:
    return _rows(table_name)


def _version_number(version_id: str) -> int:
    prefix = "knowledge-v"
    if not version_id.startswith(prefix):
        return -1
    value = version_id.removeprefix(prefix)
    return int(value) if value.isdigit() else -1


def _adapt_index_entry(row: dict[str, Any]) -> dict[str, Any]:
    row["order"] = row.pop("entry_order")
    return row


def _adapt_segment(row: dict[str, Any]) -> dict[str, Any]:
    row["order"] = row.pop("segment_order")
    return row


def seed_ingestion_batches() -> list[KnowledgeIngestionBatch]:
    return _models(KnowledgeIngestionBatch, "knowledge_ingestion_batches")


def seed_sources() -> list[KnowledgeSource]:
    editions_by_source: dict[str, list[KnowledgeSourceEdition]] = {}
    for edition in seed_source_editions():
        editions_by_source.setdefault(edition.source_id, []).append(edition)

    sources = _models(KnowledgeSource, "knowledge_sources")
    return [
        source.model_copy(update={"editions": editions_by_source.get(source.id, [])})
        for source in sources
    ]


def seed_source_editions() -> list[KnowledgeSourceEdition]:
    return _models(KnowledgeSourceEdition, "knowledge_source_editions")


def seed_index_entries() -> list[KnowledgeIndexEntry]:
    return [
        KnowledgeIndexEntry.model_validate(_adapt_index_entry(row))
        for row in _rows("knowledge_index_entries")
    ]


def seed_segments() -> list[KnowledgeSegment]:
    return [
        KnowledgeSegment.model_validate(_adapt_segment(row))
        for row in _rows("knowledge_segments")
    ]


def seed_extraction_runs() -> list[KnowledgeExtractionRun]:
    return _models(KnowledgeExtractionRun, "knowledge_extraction_runs")


def seed_proposals() -> list[KnowledgeProposal]:
    return _models(KnowledgeProposal, "knowledge_proposals")


def seed_nodes() -> list[KnowledgeNode]:
    return _models(KnowledgeNode, "knowledge_nodes")


def seed_node_relations() -> list[KnowledgeNodeRelation]:
    return _models(KnowledgeNodeRelation, "knowledge_node_relations")


def seed_relations() -> list[KnowledgeRelation]:
    return _models(KnowledgeRelation, "knowledge_relations")


def seed_evidence() -> list[KnowledgeEvidenceItem]:
    return _models(KnowledgeEvidenceItem, "knowledge_evidence_items")


def seed_evidence_revisions() -> list[dict[str, Any]]:
    return _revision_dicts("knowledge_evidence_revisions")


def seed_claims() -> list[KnowledgeClaim]:
    return _models(KnowledgeClaim, "knowledge_claims")


def seed_claim_evidence_links() -> list[KnowledgeClaimEvidenceLink]:
    return _models(KnowledgeClaimEvidenceLink, "knowledge_claim_evidence_links")


def seed_claim_revisions() -> list[dict[str, Any]]:
    return _revision_dicts("knowledge_claim_revisions")


def seed_cards() -> list[KnowledgeCard]:
    return _models(KnowledgeCard, "knowledge_cards")


def seed_versions() -> list[KnowledgeVersion]:
    snapshot_by_version = {
        row["version_id"]: row for row in _rows("knowledge_version_snapshots")
    }
    versions = []
    for row in sorted(_rows("knowledge_versions"), key=lambda item: _version_number(item["id"])):
        snapshot = snapshot_by_version.get(row["id"], {})
        versions.append(
            KnowledgeVersion(
                id=row["id"],
                status=row["status"],
                published_at=row["published_at"],
                source_count=len(snapshot.get("source_ids", [])),
                node_count=len(snapshot.get("node_ids", [])),
                evidence_count=len(snapshot.get("evidence_ids", [])),
                claim_count=len(snapshot.get("claim_ids", [])),
                card_count=len(snapshot.get("card_ids", [])),
            )
        )
    return versions


def seed_object_revisions() -> list[KnowledgeObjectRevision]:
    return _models(KnowledgeObjectRevision, "knowledge_object_revisions")
