from datetime import UTC, datetime

from app.core.models import ScoreVariable


DEFAULT_PROFILE_ID = "default"


def seed_variables() -> list[ScoreVariable]:
    now = datetime.now(UTC)
    return [
        ScoreVariable(
            key="dinamismo",
            label="Dinamismo",
            category="frase",
            calculated_value=620,
            manual_adjustment=0,
            confidence=0.42,
            context="general",
            evidence_count=0,
            updated_at=now,
        ),
        ScoreVariable(
            key="precision_lexica",
            label="Precision lexica",
            category="lexico",
            calculated_value=700,
            manual_adjustment=0,
            confidence=0.38,
            context="general",
            evidence_count=0,
            updated_at=now,
        ),
        ScoreVariable(
            key="sobriedad",
            label="Sobriedad",
            category="voz",
            calculated_value=650,
            manual_adjustment=0,
            confidence=0.35,
            context="general",
            evidence_count=0,
            updated_at=now,
        ),
        ScoreVariable(
            key="densidad_argumental",
            label="Densidad argumental",
            category="argumentacion",
            calculated_value=580,
            manual_adjustment=0,
            confidence=0.31,
            context="general",
            evidence_count=0,
            updated_at=now,
        ),
    ]

