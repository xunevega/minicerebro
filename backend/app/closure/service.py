from app.core.models import ClosureCondition, ExpectedAnswerLine


def closure_conditions() -> list[ClosureCondition]:
    conditions = [
        ("V1 solo trata escritura en lengua espanola.", ["knowledge/status", "generation prompt"]),
        ("La base de conocimiento es estable y versionada.", ["GET /knowledge/status"]),
        ("El perfil de preferencias es independiente.", ["profiles", "preferences", "scores"]),
        ("El scoring es visible y editable.", ["GET/PATCH /profiles/{id}/scores"]),
        ("Toda evolucion del perfil es trazable.", ["GET /audit/events"]),
        ("Ninguna correccion modifica conocimiento academico.", ["feedback requiere aprobacion"]),
        ("Ningun aprendizaje se aplica sin revision o regla explicita.", ["feedback proposed/applied"]),
        ("La adecuacion se mide por la correccion necesaria.", ["POST /comparisons"]),
        ("La consistencia del usuario se analiza sin atribuir causas psicologicas.", ["decision/evaluate"]),
        ("Cerebro no se usa como base arquitectonica automatica.", ["cerebro-audit/candidates"]),
        ("La reutilizacion de Cerebro exige auditoria pieza por pieza.", ["cerebro-audit/gates"]),
        ("No se anaden modulos fuera de este contrato sin abrir una nueva version.", ["acceptance/v1"]),
    ]
    return [
        ClosureCondition(id=index, description=description, status="satisfied", evidence=evidence)
        for index, (description, evidence) in enumerate(conditions, start=1)
    ]


def expected_answer_lines() -> list[ExpectedAnswerLine]:
    lines = [
        ("Esto es lo que se sobre escribir.", ["GET /knowledge/cards"]),
        ("Esto es lo que me has dicho que te gusta.", ["GET /preferences"]),
        ("Esto es lo que deduzco de tus correcciones.", ["GET /feedback/proposals"]),
        ("Estas son las variables y sus pesos.", ["GET /profiles/default/scores"]),
        ("Esta es la confianza que tengo en cada una.", ["GET /profiles/default/statistics"]),
        ("Este texto se aproxima a tu perfil.", ["POST /generation", "POST /comparisons"]),
        ("Has modificado el texto.", ["ComparisonResult.modification_score"]),
        ("Estos cambios sugieren ajustar variables.", ["POST /comparisons/{id}/feedback"]),
        ("Nada cambiara hasta que lo apruebes.", ["PATCH /feedback/proposals/{id}"]),
    ]
    return [
        ExpectedAnswerLine(order=index, text=text, evidence=evidence)
        for index, (text, evidence) in enumerate(lines, start=1)
    ]
