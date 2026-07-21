from app.core.models import CerebroAuditCandidate, CerebroAuditGate


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


def cerebro_audit_gates() -> list[CerebroAuditGate]:
    gates = [
        ("flow_console_dependency", "blocked_until_checked", "No debe arrastrar Flow Console."),
        ("general_memory_dependency", "blocked_until_checked", "No debe heredar memoria generalista."),
        ("world_model_dependency", "blocked_until_checked", "No debe traer world model."),
        ("signals_dependency", "blocked_until_checked", "No debe traer senales comerciales o reputacionales."),
        ("personal_entities_coupling", "blocked_until_checked", "No debe acoplar entidades personales."),
        ("data_schema", "blocked_until_checked", "Debe mapearse al esquema nuevo de Minicerebro."),
        ("test_quality", "blocked_until_checked", "Debe tener pruebas suficientes antes de adaptar."),
        ("reversibility", "blocked_until_checked", "Debe poder revertirse sin tocar perfil/knowledge."),
        ("maintainability", "blocked_until_checked", "Debe ser mantenible dentro de V1."),
    ]
    return [
        CerebroAuditGate(id=identifier, status=status, reason=reason)
        for identifier, status, reason in gates
    ]
