from app.core.models import V1Screen


def v1_screens() -> list[V1Screen]:
    return [
        V1Screen(
            id="knowledge",
            label="Conocimiento",
            route="/knowledge",
            status="implemented",
            functions=["version", "cobertura", "fuentes", "lagunas"],
        ),
        V1Screen(
            id="preferences",
            label="Anadir preferencias",
            route="/preferences",
            status="implemented",
            functions=["prompts", "gustos", "limites", "revision"],
        ),
        V1Screen(
            id="profile",
            label="Lo que sabe de mi",
            route="/profile",
            status="implemented",
            functions=["resumen", "confianza", "contradicciones", "confirmacion"],
        ),
        V1Screen(
            id="scoring",
            label="Perfil y scoring",
            route="/scoring",
            status="implemented",
            functions=["variables", "ajustes", "contexto", "valor efectivo"],
        ),
        V1Screen(
            id="editor",
            label="Editor",
            route="/editor",
            status="implemented",
            functions=["generar", "corregir", "reescribir", "proteger elementos"],
        ),
        V1Screen(
            id="lab",
            label="Laboratorio",
            route="/lab",
            status="implemented",
            functions=["variables temporales", "pruebas", "comparacion", "sin guardado automatico"],
        ),
        V1Screen(
            id="compare",
            label="Comparador",
            route="/compare",
            status="implemented",
            functions=["cambios", "adecuacion", "impacto", "retroalimentacion"],
        ),
    ]
