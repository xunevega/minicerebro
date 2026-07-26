from os import getenv

from openai import OpenAI

from app.core.models import GenerationInput, GenerationResult, ScoreVariable


def _profile_prompt(variables: list[ScoreVariable]) -> str:
    lines = [
        f"- {item.key}: efectivo={item.effective_value}, confianza={item.confidence:.2f}, contexto={item.context}"
        for item in sorted(variables, key=lambda variable: variable.effective_value, reverse=True)
    ]
    return "\n".join(lines)


def rewrite_with_profile(payload: GenerationInput, variables: list[ScoreVariable]) -> GenerationResult:
    if getenv("OPENAI_API_KEY"):
        return rewrite_with_openai(payload, variables)

    active = sorted(variables, key=lambda item: item.effective_value, reverse=True)[:3]
    preserved = payload.text
    for term in payload.protected_terms:
        preserved = preserved.replace(term, f"[[{term}]]")

    original = preserved.strip()
    output = original
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

    if output == payload.text.strip():
        explanation = (
            "No se aplicaron cambios deterministas seguros. El texto ya estaba limpio para este "
            "modo local; para una reescritura profunda hace falta activar generacion externa."
        )
    else:
        explanation = (
            "Transformacion determinista local. Corrige solo cambios seguros y no aprende nada "
            "automaticamente."
        )

    return GenerationResult(
        output=output,
        explanation=explanation,
        used_profile_variables=[item.key for item in active],
    )


def rewrite_with_openai(payload: GenerationInput, variables: list[ScoreVariable]) -> GenerationResult:
    active = sorted(variables, key=lambda item: item.effective_value, reverse=True)[:5]
    model = getenv("OPENAI_MODEL", "gpt-5-mini")
    prompt = f"""
Eres Minicerebro V1, una app especializada en escritura en lengua espanola.
Accion: {payload.action}
Contexto: {payload.context}
Intensidad: {payload.intensity}/1000
Terminos protegidos: {", ".join(payload.protected_terms) or "ninguno"}

Perfil efectivo:
{_profile_prompt(active)}

Reglas:
- No aprendas nada.
- No afirmes que has actualizado el perfil.
- Respeta los terminos protegidos literalmente.
- Devuelve solo el texto resultante, sin explicaciones externas.

Texto:
{payload.text}
""".strip()

    client = OpenAI()
    response = client.responses.create(model=model, input=prompt)
    output = getattr(response, "output_text", "").strip()
    if not output:
        output = payload.text

    return GenerationResult(
        output=output,
        explanation=(
            f"Generacion LLM con {model}. Usa perfil y contexto solo para esta salida; "
            "no aplica aprendizaje automatico."
        ),
        used_profile_variables=[item.key for item in active],
        learning_applied=False,
        provider="openai",
    )
