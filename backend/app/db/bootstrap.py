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
    KnowledgeSourceRecord,
    KnowledgeVersionRecord,
    ProfileRecord,
    ScoreVariableRecord,
)
from app.db.session import database_url
from app.knowledge.service import seed_cards, seed_claims, seed_evidence, seed_nodes, seed_sources

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
        if session.get(KnowledgeSourceRecord, source.id) is not None:
            continue
        session.add(
            KnowledgeSourceRecord(
                id=source.id,
                name=source.name,
                source_type=source.source_type,
                authority_level=source.authority_level,
                priority=source.priority,
                status=source.status,
            )
        )
    session.flush()

    for node in seed_nodes():
        if session.get(KnowledgeNodeRecord, node.id) is not None:
            continue
        session.add(
            KnowledgeNodeRecord(
                id=node.id,
                source_id=node.source_id,
                node_type=node.node_type,
                title=node.title,
                summary=node.summary,
                version=node.version,
            )
        )
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
        if session.get(KnowledgeEvidenceItemRecord, evidence.id) is not None:
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
