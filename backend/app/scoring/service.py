from datetime import UTC, datetime

from app.core.models import Evidence, EvidenceType, ScorePatch, ScoreVariable
from app.core.text import clamp_score


def score_out(variable: ScoreVariable) -> dict:
    data = variable.model_dump()
    data["effective_value"] = variable.effective_value
    return data


def apply_manual_override(variable: ScoreVariable, patch: ScorePatch) -> tuple[ScoreVariable, Evidence]:
    updated = variable.model_copy(
        update={
            "manual_adjustment": patch.manual_adjustment,
            "updated_at": datetime.now(UTC),
        }
    )
    evidence = Evidence(
        evidence_type=EvidenceType.manual_override,
        source=f"score:{variable.key}",
        summary=patch.reason,
        weight=min(1, abs(patch.manual_adjustment) / 1000),
        context=variable.context,
    )
    return updated, evidence


def initial_calculated_value(text: str) -> int:
    return clamp_score(420 + min(len(text), 580))

