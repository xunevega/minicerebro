from uuid import UUID

from app.core.models import (
    Evidence,
    Preference,
    PreferenceInput,
    PreferenceStatus,
    ScoreProposal,
    ScoreProposalItem,
)
from app.core.text import canonical_text
from app.scoring.service import initial_calculated_value


KEYWORD_VARIABLES = {
    "rapido": "dinamismo",
    "dinamico": "dinamismo",
    "directo": "dinamismo",
    "breve": "dinamismo",
    "breves": "dinamismo",
    "corta": "dinamismo",
    "cortas": "dinamismo",
    "dinamismo": "dinamismo",
    "preciso": "precision_lexica",
    "exacto": "precision_lexica",
    "sobrio": "sobriedad",
    "contenido": "sobriedad",
    "formal": "sobriedad",
    "argumento": "densidad_argumental",
    "tesis": "densidad_argumental",
}

NEGATION_CUES = ("no quiero", "no me gusta", "evita", "evitar", "menos")
DIRECTION_PREFIX = "direcciones="


def interpret_preference(payload: PreferenceInput) -> Preference:
    text = canonical_text(payload.text)
    directions = _variable_directions(text)
    affected = sorted(directions)
    if not affected:
        affected = ["precision_lexica"]
        directions = {"precision_lexica": 1}

    calculated = initial_calculated_value(payload.text)
    evidence = Evidence(
        evidence_type=payload.input_type,
        source="user_input",
        summary=(
            f"Entrada interpretada para {', '.join(affected)} con fuerza inicial {calculated}. "
            f"{DIRECTION_PREFIX}{_serialize_directions(directions)}"
        ),
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
    directions = _directions_from_summary(preference.evidence.summary)
    items = [
        ScoreProposalItem(
            variable_key=variable_key,
            context=preference.evidence.context,
            delta=base_delta * directions.get(variable_key, 1),
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


def _variable_directions(text: str) -> dict[str, int]:
    directions: dict[str, int] = {}
    for keyword, variable in KEYWORD_VARIABLES.items():
        index = text.find(keyword)
        if index == -1:
            continue
        direction = -1 if _is_negated(text, index) else 1
        previous = directions.get(variable)
        if previous is None or previous > direction:
            directions[variable] = direction
    return directions


def _is_negated(text: str, keyword_index: int) -> bool:
    prefix = text[max(0, keyword_index - 36):keyword_index].strip()
    return any(cue in prefix for cue in NEGATION_CUES)


def _serialize_directions(directions: dict[str, int]) -> str:
    return ",".join(
        f"{variable}:{'subir' if direction > 0 else 'bajar'}"
        for variable, direction in sorted(directions.items())
    )


def _directions_from_summary(summary: str) -> dict[str, int]:
    if DIRECTION_PREFIX not in summary:
        return {}
    raw_directions = summary.split(DIRECTION_PREFIX, 1)[1].strip().rstrip(".")
    directions: dict[str, int] = {}
    for item in raw_directions.split(","):
        if ":" not in item:
            continue
        variable, direction = item.split(":", 1)
        directions[variable] = -1 if direction == "bajar" else 1
    return directions
