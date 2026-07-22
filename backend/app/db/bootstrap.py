from datetime import UTC, datetime
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.seeds import DEFAULT_PROFILE_ID, seed_variables
from app.db.models import (
    KnowledgeCardRecord,
    KnowledgeClaimRecord,
    KnowledgeEvidenceItemRecord,
    KnowledgeNodeRecord,
    KnowledgeNodeRelationRecord,
    KnowledgeSourceRecord,
    KnowledgeSourceEditionRecord,
    KnowledgeVersionRecord,
    ProfileRecord,
    ScoreVariableRecord,
)
from app.db.session import database_url
from app.knowledge.service import (
    seed_cards,
    seed_claims,
    seed_evidence,
    seed_node_relations,
    seed_nodes,
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
            "version": relation.version,
            "created_at": relation.created_at,
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
            evidence_record.reference = evidence.reference
            evidence_record.excerpt = evidence.excerpt
            evidence_record.confidence = evidence.confidence
            evidence_record.version = evidence.version
            continue
        session.add(
            KnowledgeEvidenceItemRecord(
                id=evidence.id,
                node_id=evidence.node_id,
                source_id=evidence.source_id,
                reference=evidence.reference,
                excerpt=evidence.excerpt,
                confidence=evidence.confidence,
                version=evidence.version,
            )
        )
    session.flush()

    for claim in seed_claims():
        if session.get(KnowledgeClaimRecord, claim.id) is not None:
            continue
        session.add(
            KnowledgeClaimRecord(
                id=claim.id,
                evidence_id=claim.evidence_id,
                card_id=claim.card_id,
                statement=claim.statement,
                confidence=claim.confidence,
                version=claim.version,
            )
        )

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

    seed_source_ids = {source.id for source in seed_sources()}
    stale_sources = session.scalars(select(KnowledgeSourceRecord)).all()
    for stale_source in stale_sources:
        if stale_source.id not in seed_source_ids:
            session.delete(stale_source)
