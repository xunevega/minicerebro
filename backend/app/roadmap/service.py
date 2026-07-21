from app.core.models import TechnicalRoadmapPhase


def technical_roadmap() -> list[TechnicalRoadmapPhase]:
    phases = [
        ("Esqueleto", "done", ["FastAPI", "PostgreSQL", "modelos", "migraciones", "frontend basico"]),
        ("Preferencias", "done", ["interpretacion", "confirmacion", "scoring", "resumen humano"]),
        ("Generacion", "done", ["editor", "contextos", "protecciones", "variantes", "textos persistidos"]),
        ("Comparacion", "done", ["diff", "dimensiones", "adecuacion", "feedback"]),
        ("Estadisticas", "done", ["confianza", "consistencia", "cobertura", "contradicciones"]),
        ("Conocimiento", "partial", ["registro", "fichas", "versiones", "validacion pendiente"]),
        ("Laboratorio", "done", ["simulacion", "A/B inicial", "sin guardado automatico"]),
    ]
    return [
        TechnicalRoadmapPhase(id=index, name=name, status=status, items=items)
        for index, (name, status, items) in enumerate(phases, start=1)
    ]
