from app.core.models import Evidence, Preference, PreferenceInput, PreferenceStatus
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

