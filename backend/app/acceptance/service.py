from app.core.models import AcceptanceCriterion


def v1_acceptance_criteria() -> list[AcceptanceCriterion]:
    criteria = [
        ("mostrar una base de conocimiento versionada y acreditada", ["GET /knowledge/status"]),
        ("registrar fuentes y especialistas sin modificar la logica", ["GET /knowledge/sources"]),
        ("convertir conocimiento a fichas internas", ["GET /knowledge/cards"]),
        ("introducir una preferencia mediante prompt", ["POST /preferences"]),
        ("mostrar la interpretacion antes de guardarla", ["POST /preferences/interpret"]),
        ("convertirla en variables", ["GET /preferences/{id}/score-proposal"]),
        ("editar variables manualmente", ["PATCH /profiles/{id}/scores/{variable}"]),
        ("mostrar scoring, confianza, consistencia y cobertura", ["GET /profiles/{id}/statistics"]),
        ("mantener perfiles por contexto", ["GET /profiles/{id}/scores?context=..."]),
        ("generar un texto desde una idea", ["POST /generation"]),
        ("corregir un texto", ["POST /correction"]),
        ("crear alternativas", ["POST /variants"]),
        ("comparar salida y correccion final", ["POST /comparisons"]),
        ("medir modificacion y adecuacion", ["ComparisonResult"]),
        ("proponer actualizaciones del scoring", ["POST /comparisons/{id}/feedback"]),
        ("aprobar o rechazar el aprendizaje", ["PATCH /feedback/proposals/{id}"]),
        ("mostrar un resumen humano del perfil", ["GET /profiles/{id}/summary"]),
        ("detectar contradicciones", ["GET /profiles/{id}/contradictions"]),
        ("distinguir patron estable de variacion temporal", ["GET /decision/evaluate"]),
        ("probar cambios en laboratorio sin alterar el perfil", ["POST /lab/simulate"]),
    ]
    return [
        AcceptanceCriterion(
            id=index,
            description=description,
            status="implemented",
            evidence=evidence,
        )
        for index, (description, evidence) in enumerate(criteria, start=1)
    ]
