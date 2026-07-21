from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.seeds import DEFAULT_PROFILE_ID, seed_variables
from app.db.models import ProfileRecord, ScoreVariableRecord
from app.db.session import Base, engine


def create_tables() -> None:
    Base.metadata.create_all(bind=engine())


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

    session.commit()

