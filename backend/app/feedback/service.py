from app.core.models import ComparisonResult, FeedbackProposal, FeedbackProposalItem, ScoreVariable


def build_feedback_proposal(
    comparison: ComparisonResult,
    variables: list[ScoreVariable],
    context: str,
) -> FeedbackProposal:
    by_key = {variable.key: variable for variable in variables}
    items: list[FeedbackProposalItem] = []
    rationale: list[str] = [comparison.summary]

    length_delta = comparison.revised_words - comparison.original_words
    if length_delta < 0 and "dinamismo" in by_key:
        items.append(_item(by_key["dinamismo"], context, 20, "El texto corregido queda mas breve."))
        rationale.append(f"El texto corregido reduce {abs(length_delta)} palabras.")
    elif length_delta > 0 and "densidad_argumental" in by_key:
        items.append(
            _item(
                by_key["densidad_argumental"],
                context,
                15,
                "El texto corregido desarrolla mas la argumentacion.",
            )
        )
        rationale.append(f"El texto corregido anade {length_delta} palabras.")

    if comparison.modification_score >= 350 and "precision_lexica" in by_key:
        items.append(
            _item(
                by_key["precision_lexica"],
                context,
                18,
                "La correccion introduce cambios lexicos relevantes.",
            )
        )
        rationale.append("La modificacion lexical supera el umbral de retroalimentacion.")

    if comparison.adequacy_score < 500 and "sobriedad" in by_key:
        items.append(
            _item(
                by_key["sobriedad"],
                context,
                -12,
                "La adecuacion baja sugiere revisar la intensidad del estilo aplicado.",
            )
        )
        rationale.append("La adecuacion queda baja y exige aprobacion antes de aprender.")

    return FeedbackProposal(
        comparison_id=comparison.id,
        context=context,
        items=items,
        rationale=rationale,
    )


def _item(
    variable: ScoreVariable,
    context: str,
    delta: int,
    reason: str,
) -> FeedbackProposalItem:
    proposed = max(0, min(1000, variable.calculated_value + delta))
    return FeedbackProposalItem(
        variable_key=variable.key,
        context=context,
        current_value=variable.calculated_value,
        proposed_value=proposed,
        delta=proposed - variable.calculated_value,
        reason=reason,
    )
