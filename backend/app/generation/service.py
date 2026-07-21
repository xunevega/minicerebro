from app.core.models import GenerationInput, GenerationResult, ScoreVariable


def rewrite_with_profile(payload: GenerationInput, variables: list[ScoreVariable]) -> GenerationResult:
    active = sorted(variables, key=lambda item: item.effective_value, reverse=True)[:3]
    preserved = payload.text
    for term in payload.protected_terms:
        preserved = preserved.replace(term, f"[[{term}]]")

    output = preserved.strip()
    if payload.action in {"rewrite", "correction"}:
        output = " ".join(output.split())
        if payload.intensity > 650 and not output.endswith("."):
            output = f"{output}."
    elif payload.action == "continue":
        output = f"{output}\n\nContinuacion propuesta: desarrolla la idea con precision y sin aprender nada automaticamente."
    elif payload.action == "variants":
        output = (
            f"Variante A: {output}\n\n"
            f"Variante B: {output} Mantiene la intencion y ajusta el ritmo.\n\n"
            f"Variante C: {output} Conserva terminos protegidos y reduce rodeos."
        )

    for term in payload.protected_terms:
        output = output.replace(f"[[{term}]]", term)

    return GenerationResult(
        output=output,
        explanation=(
            "Transformacion determinista de arranque. Usa el perfil solo para explicar contexto; "
            "no aplica aprendizaje ni llama a modelos externos."
        ),
        used_profile_variables=[item.key for item in active],
    )
