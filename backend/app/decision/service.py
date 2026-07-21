from app.core.models import Contradiction, DecisionEvaluation, DecisionRule, ScoreVariable


def decision_rules() -> list[DecisionRule]:
    labels = [
        ("Restricciones tecnicas y linguisticas", "Limites de idioma, seguridad y contrato."),
        ("Peticion concreta del texto", "La instruccion actual del usuario manda sobre preferencias genericas."),
        ("Protecciones explicitas", "Terminos o fragmentos protegidos no se modifican."),
        ("Ajustes manuales", "El valor manual prevalece sobre calculo y aprendizaje propuesto."),
        ("Perfil contextual", "Preferencias del contexto activo antes que el perfil general."),
        ("Perfil general", "Base del usuario cuando el contexto no aporta suficiente informacion."),
        ("Referencias de autor", "Referencias literarias solo cuando existan y no contradigan lo anterior."),
        ("Conocimiento estilistico", "Reglas estables de lengua y estilo."),
        ("Comportamiento por defecto", "Salida conservadora cuando faltan datos."),
    ]
    return [
        DecisionRule(priority=index, label=label, description=description)
        for index, (label, description) in enumerate(labels, start=1)
    ]


def evaluate_decision_state(
    context: str,
    variables: list[ScoreVariable],
    contradictions: list[Contradiction],
) -> DecisionEvaluation:
    low_confidence = [variable.key for variable in variables if variable.confidence < 0.4]
    conflict_notes = [
        f"{item.variable_key}: {item.note}" for item in contradictions
    ]
    if conflict_notes:
        recommendation = "Aplicar prioridad y revisar la variable manualmente antes de aprender."
    elif low_confidence:
        recommendation = "Usar perfil general y proponer una prueba A/B antes de consolidar."
    else:
        recommendation = "Usar perfil contextual con confianza suficiente."

    return DecisionEvaluation(
        context=context,
        applied_priority=decision_rules(),
        conflicts=conflict_notes,
        low_confidence_variables=low_confidence,
        recommendation=recommendation,
    )
