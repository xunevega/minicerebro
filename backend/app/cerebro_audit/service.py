from app.core.models import CerebroAuditCandidate


def cerebro_audit_candidates() -> list[CerebroAuditCandidate]:
    candidates = [
        ("source_registry", "REFERENCIA", ["registro de fuentes", "prioridad", "estado"]),
        ("document_ingestion", "REFERENCIA", ["parser", "normalizacion", "trazabilidad"]),
        ("normalization", "ADAPTAR", ["canonicalText", "canonicalKey", "pruebas"]),
        ("entity_extraction", "REFERENCIA", ["extraccion", "limites", "falsos positivos"]),
        ("knowledge_cards", "ADAPTAR", ["schema", "version", "procedencia"]),
        ("relations", "REFERENCIA", ["grafo", "tipos de relacion", "validacion"]),
        ("confidence", "ADAPTAR", ["calculo", "evidencias", "umbral"]),
        ("provenance", "ADAPTAR", ["source_id", "version", "auditoria"]),
        ("contradictions", "ADAPTAR", ["deteccion", "explicacion", "resolucion"]),
        ("versioning", "REFERENCIA", ["publicacion", "rollback", "snapshot"]),
        ("semantic_retrieval", "REFERENCIA", ["pgvector", "ranking", "aislamiento"]),
        ("graph_validation", "REFERENCIA", ["reglas", "errores", "reportes"]),
        ("logging", "ADAPTAR", ["eventos", "sin textos sensibles", "correlation_id"]),
        ("importers", "DESCARTAR", ["entradas", "dependencias", "acoplamientos"]),
    ]
    return [
        CerebroAuditCandidate(
            component=component,
            classification=classification,
            status="pending_code_evidence",
            evidence_required=evidence,
            note="No se importa ningun modulo completo sin auditoria pieza por pieza.",
        )
        for component, classification, evidence in candidates
    ]
