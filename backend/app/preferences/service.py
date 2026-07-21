from uuid import UUID

from app.core.models import (
    Evidence,
    Preference,
    PreferenceInput,
    PreferenceStatus,
    ScoreProposal,
    ScoreProposalItem,
)
from app.scoring.service import initial_calculated_value


KEYWORD_VARIABLES = {
    "rapido": "dinamismo",
    "dinamico": "dinamismo",
    "directo": "dinamismo",
    "preciso": "precision_lexica",
    "exacto": "precision_lexica",
    "sobrio": "sobriedad",
    "contenido": "sobriedad",
    "argumento": "densidad_argumental",
    "tesis": "densidad_argumental",
}


def interpret_preference(payload: PreferenceInput) -> Preference:
    text = payload.text.lower()
    affected = sorted({variable for keyword, variable in KEYWORD_VARIABLES.items() if keyword in text})
    if not affected:
        affected = ["precision_lexica"]

    calculated = initial_calculated_value(payload.text)
    evidence = Evidence(
        evidence_type=payload.input_type,
        source="user_input",
        summary=f"Entrada interpretada para {', '.join(affected)} con fuerza inicial {calculated}.",
        weight=calculated / 1000,
        context=payload.context,
    )
    return Preference(
        text=payload.text,
        interpreted_as=(
            "Preferencia propuesta pendiente de confirmacion. "
            "No modifica conocimiento y no se consolida automaticamente."
        ),
        status=PreferenceStatus.proposed,
        evidence=evidence,
        affected_variables=affected,
    )


def build_score_proposal(preference: Preference) -> ScoreProposal:
    if preference.status != PreferenceStatus.accepted:
        return ScoreProposal(preference_id=preference.id, status="not_applicable", items=[])

    base_delta = max(10, min(80, round(preference.evidence.weight * 100)))
    items = [
        ScoreProposalItem(
            variable_key=variable_key,
            context=preference.evidence.context,
            delta=base_delta,
            reason=(
                f"Preferencia aceptada desde {preference.evidence.evidence_type.value}: "
                f"{preference.evidence.summary}"
            ),
        )
        for variable_key in preference.affected_variables
    ]
    return ScoreProposal(preference_id=preference.id, status="pending_review", items=items)


def empty_score_proposal(preference_id: UUID) -> ScoreProposal:
    return ScoreProposal(preference_id=preference_id, status="not_found", items=[])
