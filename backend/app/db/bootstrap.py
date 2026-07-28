from datetime import UTC, datetime
import os
from pathlib import Path
from threading import Lock

from alembic import command
from alembic.config import Config
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.seeds import DEFAULT_PROFILE_ID, seed_variables
from app.db.models import (
    KnowledgeVersionRecord,
    KnowledgeVersionSnapshotRecord,
    ProfileRecord,
    ScoreVariableRecord,
)
from app.db.session import database_url
from app.knowledge.contracts import LATEST_KNOWLEDGE_VERSION
from app.knowledge.legacy_seed import ensure_knowledge_seed_data

BACKEND_DIR = Path(__file__).resolve().parents[2]
_SEED_LOCK = Lock()
LEGACY_KNOWLEDGE_SEED_ENV = "MINICEREBRO_ALLOW_LEGACY_KNOWLEDGE_SEED"


def upgrade_database() -> None:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url())
    command.upgrade(config, "head")


def ensure_seed_data(session: Session) -> None:
    with _SEED_LOCK:
        ensure_profile_seed_data(session)
        if not has_published_knowledge_snapshot(session):
            if not legacy_knowledge_seed_allowed():
                raise RuntimeError(
                    "published knowledge snapshot is missing. Run Alembic migrations first, "
                    f"or set {LEGACY_KNOWLEDGE_SEED_ENV}=1 for the legacy catalog fallback."
                )
            ensure_knowledge_seed_data(session)
        session.commit()


def ensure_profile_seed_data(session: Session) -> None:
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


def has_published_knowledge_snapshot(session: Session) -> bool:
    version = session.get(KnowledgeVersionRecord, LATEST_KNOWLEDGE_VERSION)
    snapshot = session.get(KnowledgeVersionSnapshotRecord, LATEST_KNOWLEDGE_VERSION)
    return version is not None and version.status == "published" and snapshot is not None


def legacy_knowledge_seed_allowed() -> bool:
    return os.getenv(LEGACY_KNOWLEDGE_SEED_ENV, "").strip().lower() in {"1", "true", "yes"}
