from datetime import UTC, datetime
from unicodedata import category, normalize

from app.core.models import (
    KnowledgeCard,
    KnowledgeClaim,
    KnowledgeEvidenceItem,
    KnowledgeGymCheck,
    KnowledgeGymReport,
    KnowledgeIngestionBatch,
    KnowledgeIngestionBatchExport,
    KnowledgeIngestionPolicy,
    KnowledgeIngestionReadiness,
    KnowledgeNode,
    KnowledgePublicationPolicy,
    KnowledgePublicationReadiness,
    KnowledgeQueryContract,
    KnowledgeQueryInput,
    KnowledgeQueryInterpretation,
    KnowledgeQueryResult,
    KnowledgeRelation,
    RetrievedKnowledgeCard,
    KnowledgeSource,
    KnowledgeSourceEdition,
    KnowledgeVersion,
    KnowledgeVersioningPolicy,
)
from app.knowledge.catalog import (
    _ingestion_blockers,
    DEFAULT_SOURCE_EDITION,
    DEFAULT_SOURCE_LOCATORS,
    EXCLUDED_VERSIONED_OBJECT_TYPES,
    INGESTION_ALTERNATIVE_STATES,
    INGESTION_FLOW,
    INGESTION_LIFECYCLE,
    KNOWLEDGE_VERSION_IDS,
    LATEST_KNOWLEDGE_VERSION,
    PUBLICATION_LIFECYCLE,
    PUBLICATION_REQUIREMENTS,
    PUBLICATION_VALIDATIONS,
    QUERY_LIFECYCLE,
    QUERY_OUT_OF_SCOPE,
    VERSIONED_OBJECT_TYPES,
    seed_cards,
    seed_claims,
    seed_evidence,
    seed_nodes,
    seed_relations,
    seed_sources,
)

def versioning_policy() -> KnowledgeVersioningPolicy:
    return KnowledgeVersioningPolicy(
        versioned_object_types=VERSIONED_OBJECT_TYPES,
        excluded_object_types=EXCLUDED_VERSIONED_OBJECT_TYPES,
        versioning_levels=[
            "revision",
            "object_version",
            "knowledge_version",
            "release",
        ],
        revision_triggers=[
            "cambia una definicion",
            "cambia una relacion",
            "cambia una evidencia",
            "cambia un claim",
            "cambia el contexto",
            "cambia la confianza",
            "cambia el localizador",
            "cambia la clasificacion",
            "cambia el estado",
            "cambia un alias",
            "cambia un tipo",
            "cambia la estructura de un nodo",
            "cambia una fuente o edicion",
            "cambia una ficha",
            "cambia el arbol, ontologia o esquema",
        ],
        non_revision_changes=[
            "cambios internos de almacenamiento",
            "optimizaciones",
            "indices",
            "cache",
        ],
        identifiers={
            "object_id": "identificador estable durante toda la vida del objeto",
            "revision": "numero incremental de modificacion del objeto",
            "revision_number": "revision incremental dentro del objeto",
            "object_version": "version estable del objeto revisionado",
            "knowledge_version": "snapshot de conocimiento al que pertenece",
            "release": "publicacion inmutable construida desde una knowledge_version",
        },
        immutable_after_publication=True,
        object_statuses=["active", "superseded", "deprecated", "withdrawn", "archived"],
        history_fields=[
            "author",
            "created_at",
            "updated_at",
            "reason",
            "change_type",
            "object_id",
            "before",
            "after",
            "previous_revision",
        ],
        historical_recovery=[
            "como era un nodo en una knowledge_version",
            "que claim existia",
            "que evidencia lo sustentaba",
            "que relaciones tenia",
            "que definicion tenia",
        ],
        compatibility_policy=(
            "Las referencias antiguas no se rompen; los objetos se sustituyen, fusionan, "
            "deprecian o archivan mediante nuevas revisiones que conservan identificadores "
            "e historial."
        ),
        audit_events=[
            "version.created",
            "revision.created",
            "revision.published",
            "revision.superseded",
            "knowledge.published",
            "knowledge.archived",
        ],
        source_versioning_levels=["logical_source", "edition", "document_version"],
        integrity_rules=[
            "no puede existir una revision sin objeto",
            "no puede existir un objeto sin historial",
            "no puede existir una version sin identificador",
            "no puede existir referencia a revision inexistente",
            "no puede existir version parcialmente publicada",
        ],
        publication_checks=[
            "migraciones aplicadas",
            "fuentes y ediciones registradas",
            "integridad referencial",
            "ausencia de objetos huerfanos",
            "ausencia de relaciones rotas",
            "nodos conectados",
            "evidencias con fuente, edicion y localizador",
            "claims con tipo, alcance y evidencia",
            "ausencia de claims sin evidencia",
            "ausencia de fichas sin nodo",
            "relaciones tipadas y versionadas",
            "fichas reconstruibles desde claims",
            "validacion automatica completa",
        ],
        publication_failure_state="cancelled",
        acceptance_criteria=[
            "todos los objetos tienen identificador estable",
            "toda modificacion crea una revision",
            "ninguna revision modifica versiones anteriores",
            "toda version de conocimiento puede reconstruirse integramente",
            "los identificadores permanecen constantes entre revisiones",
            "las referencias historicas siguen siendo validas",
            "las fusiones conservan trazabilidad",
            "las sustituciones nunca eliminan el historial",
            "la publicacion genera una instantanea inmutable",
        ],
        closure_questions=[
            "que era",
            "cuando existio",
            "en que version aparecio",
            "quien lo modifico",
            "por que cambio",
            "que sustituyo",
            "que lo sustituyo despues",
            "como era exactamente en cualquier version publicada",
        ],
        release_chain=[
            "knowledge-v0",
            "knowledge-v1",
            "knowledge-v2",
            "knowledge-v3",
            "knowledge-v4",
            "knowledge-v5",
        ],
    )


def publication_policy() -> KnowledgePublicationPolicy:
    return KnowledgePublicationPolicy(
        meaning="Publicar convierte una version completa en conocimiento estable recuperable.",
        publication_unit="knowledge_version",
        non_publication_units=["source", "node", "claim", "evidence", "knowledge_card"],
        lifecycle=PUBLICATION_LIFECYCLE,
        requirements=PUBLICATION_REQUIREMENTS,
        validations=PUBLICATION_VALIDATIONS,
        publication_effects=[
            "congelar version",
            "versionar objetos",
            "crear snapshot completo",
            "registrar auditoria",
        ],
        immutable_after_publication=True,
        partial_publications_allowed=False,
        rollback_policy=(
            "Una version publicada no se edita ni se borra; puede marcarse deprecated o "
            "archived y publicar una nueva knowledge_version que la sustituya."
        ),
        audit_fields=["author", "created_at", "object", "reason", "base_version"],
        acceptance_criteria=[
            "la version completa supera requisitos de publicacion",
            "la version publicada queda recuperable por identificador",
            "el snapshot no mezcla objetos de otras versiones",
            "la auditoria permite saber quien, cuando, que, por que y contra que version",
        ],
        closure_criteria=[
            "la knowledge_version esta en estado published",
            "published_at contiene una fecha concreta",
            "todas las validaciones obligatorias estan superadas",
            "la version forma parte de la cadena oficial recuperable",
        ],
    )


def ingestion_policy() -> KnowledgeIngestionPolicy:
    return KnowledgeIngestionPolicy(
        meaning="Convertir una fuente registrada en conocimiento verificable, trazable y publicable.",
        ingestion_unit="one_source_one_edition_one_batch",
        scope=[
            "adquisicion documental",
            "analisis estructural",
            "segmentacion",
            "extraccion",
            "normalizacion",
            "deduplicacion",
            "validacion",
            "preparacion para publicacion",
        ],
        out_of_scope=[
            "recuperacion",
            "generacion",
            "modificacion del perfil",
            "scoring del usuario",
            "preferencias",
        ],
        lifecycle=INGESTION_LIFECYCLE,
        alternative_states=INGESTION_ALTERNATIVE_STATES,
        required_flow=INGESTION_FLOW,
        acquisition_fields=[
            "obra",
            "edicion",
            "isbn",
            "year",
            "language",
            "format",
            "location",
            "responsible",
            "legal_status",
        ],
        segment_types=["entrada", "apartado", "definicion", "regla", "ejemplo", "nota", "comentario"],
        produced_object_types=[
            "node",
            "evidence",
            "claim",
            "example",
            "relation",
            "alias",
            "definition",
            "knowledge_card",
        ],
        proposed_initial_status="proposed",
        ai_allowed_actions=[
            "detectar conceptos",
            "proponer nodos",
            "resumir",
            "identificar relaciones",
            "sugerir claims",
        ],
        ai_forbidden_actions=[
            "publicar",
            "validar",
            "sustituir una evidencia",
            "inventar localizadores",
        ],
        review_actions=["aceptar", "rechazar", "modificar", "dividir", "fusionar", "aplazar"],
        validation_checks=[
            "todos los IDs",
            "todas las referencias",
            "todos los localizadores",
            "relaciones validas",
            "ausencia de objetos huerfanos",
        ],
        required_events=[
            "ingestion.started",
            "ingestion.segmented",
            "ingestion.extracted",
            "ingestion.normalized",
            "ingestion.review_started",
            "ingestion.validated",
            "ingestion.failed",
            "ingestion.cancelled",
            "ingestion.completed",
        ],
        metric_fields=[
            "nodes_created",
            "evidence",
            "claims",
            "relations",
            "cards",
            "duplicates",
            "contradictions",
            "elapsed_seconds",
            "coverage",
        ],
        stop_conditions=[
            "missing_edition",
            "missing_locator",
            "corrupt_references",
            "integrity_failed",
            "unreconstructable_provenance",
        ],
        export_fields=["proposals", "conflicts", "metrics", "traceability"],
        final_state="candidate",
        acceptance_criteria=[
            "parte de una fuente registrada",
            "identifica la edicion",
            "conserva la trazabilidad",
            "segmenta correctamente",
            "genera propuestas coherentes",
            "detecta duplicados",
            "detecta contradicciones",
            "mantiene los localizadores",
            "supera la validacion",
            "prepara una version candidata",
        ],
        closure_flow=[
            "source",
            "edition",
            "index",
            "segmentation",
            "extraction",
            "nodes",
            "evidence",
            "claims",
            "cards",
            "validation",
            "candidate_version",
            "publication",
        ],
        closure_criteria=[
            "cualquier obra puede seguir el mismo recorrido completo",
            "el recorrido empieza en fuente y edicion identificadas",
            "el indice, la segmentacion y la extraccion son reconstruibles",
            "nodos, evidencias, claims y fichas quedan trazados",
            "la validacion precede siempre a la version candidata",
            "la publicacion solo ocurre despues de una version candidata valida",
        ],
    )


def evaluate_ingestion_readiness(
    source: KnowledgeSource | None,
    edition: KnowledgeSourceEdition | None,
) -> KnowledgeIngestionReadiness:
    if source is None:
        return KnowledgeIngestionReadiness(
            source_id="",
            source_edition_id=None,
            can_start=False,
            status="blocked",
            checks=[],
            blockers=["source_not_registered"],
        )
    if edition is None:
        return KnowledgeIngestionReadiness(
            source_id=source.id,
            source_edition_id=None,
            can_start=False,
            status="blocked",
            checks=[
                {
                    "id": "registered_source",
                    "label": "fuente registrada",
                    "passed": True,
                    "detail": source.name,
                }
            ],
            blockers=["missing_edition"],
        )
    blockers = _ingestion_blockers(source, edition)
    checks = [
        {
            "id": "registered_source",
            "label": "fuente registrada",
            "passed": True,
            "detail": source.name,
        },
        {
            "id": "edition_identified",
            "label": "edicion identificada",
            "passed": edition.label != DEFAULT_SOURCE_EDITION,
            "detail": edition.label,
        },
        {
            "id": "acquisition_available",
            "label": "adquisicion disponible",
            "passed": edition.acquisition_status == "available",
            "detail": edition.acquisition_status,
        },
        {
            "id": "document_structure_ready",
            "label": "estructura documental lista",
            "passed": edition.locator_system != DEFAULT_SOURCE_LOCATORS,
            "detail": ", ".join(edition.locator_system),
        },
        {
            "id": "rights_reviewed",
            "label": "derechos revisados",
            "passed": "contenido no ingerido" not in source.rights,
            "detail": source.rights,
        },
    ]
    return KnowledgeIngestionReadiness(
        source_id=source.id,
        source_edition_id=edition.id,
        can_start=not blockers,
        status="registered" if not blockers else "blocked",
        checks=checks,
        blockers=blockers,
    )


def export_ingestion_batch(batch: KnowledgeIngestionBatch) -> KnowledgeIngestionBatchExport:
    return KnowledgeIngestionBatchExport(
        batch=batch,
        proposals={
            "nodes": [],
            "evidence": [],
            "claims": [],
            "relations": [],
            "cards": [],
        },
        conflicts=[],
        metrics=batch.metrics,
        traceability={
            "source_id": batch.source_id,
            "source_edition_id": batch.source_edition_id,
            "batch_id": batch.id,
            "progress": batch.progress,
            "decisions": batch.decisions,
            "blockers": batch.blockers,
        },
        publication_note="La exportacion de lote no constituye publicacion.",
    )


def evaluate_publication_readiness(
    version: KnowledgeVersion,
    *,
    sources: list[KnowledgeSource],
    nodes: list[KnowledgeNode],
    relations: list[KnowledgeRelation],
    evidence: list[KnowledgeEvidenceItem],
    claims: list[KnowledgeClaim],
    cards: list[KnowledgeCard],
) -> KnowledgePublicationReadiness:
    source_ids = {source.id for source in sources}
    node_ids = {node.id for node in nodes}
    evidence_ids = {item.id for item in evidence}
    claim_ids = {claim.id for claim in claims}
    card_ids = {card.id for card in cards}
    entity_ids = {
        "source": source_ids,
        "source_edition": {edition.id for source in sources for edition in source.editions},
        "node": node_ids,
        "evidence": evidence_ids,
        "claim": claim_ids,
        "knowledge_card": card_ids,
    }
    claims_by_card: dict[str, list[KnowledgeClaim]] = {}
    for claim in claims:
        claims_by_card.setdefault(claim.card_id, []).append(claim)
    accepted_object_statuses = (
        {"published"} if version.status == "published" else {"validated", "published"}
    )

    checks = [
        {
            "id": "non_empty_snapshot",
            "label": "snapshot de conocimiento no vacio",
            "passed": bool(sources and nodes and evidence and claims and cards),
            "detail": "la publicacion debe contener fuente, nodo, evidencia, claim y ficha",
        },
        {
            "id": "referential_integrity",
            "label": "integridad referencial",
            "passed": True,
            "detail": "todos los objetos versionados se evaluan dentro de una knowledge_version",
        },
        {
            "id": "orphan_nodes",
            "label": "sin nodos huerfanos",
            "passed": all(node.source_id in source_ids for node in nodes),
            "detail": "cada nodo debe apuntar a una fuente registrada",
        },
        {
            "id": "claims_without_evidence",
            "label": "sin claims sin evidencia",
            "passed": all(claim.evidence_id in evidence_ids for claim in claims),
            "detail": "cada claim debe tener evidencia trazable",
        },
        {
            "id": "evidence_without_source",
            "label": "sin evidencias sin fuente",
            "passed": all(item.source_id in source_ids for item in evidence),
            "detail": "cada evidencia debe apuntar a fuente registrada",
        },
        {
            "id": "empty_cards",
            "label": "sin fichas vacias",
            "passed": all(claims_by_card.get(card.id) for card in cards),
            "detail": "cada ficha debe contener al menos un claim",
        },
        {
            "id": "broken_relations",
            "label": "sin relaciones rotas",
            "passed": all(
                relation.source_entity_id in entity_ids.get(relation.source_entity_type, set())
                and relation.target_entity_id in entity_ids.get(relation.target_entity_type, set())
                for relation in relations
            ),
            "detail": "cada relacion debe resolver origen y destino",
        },
        {
            "id": "critical_conflicts",
            "label": "sin conflictos criticos",
            "passed": True,
            "detail": "no hay registro persistido de contradicciones criticas activas",
        },
        {
            "id": "documentation_validated",
            "label": "validacion documental completa",
            "passed": (
                all(source.validation_status == "validated" for source in sources)
                and all(item.status in accepted_object_statuses for item in evidence)
                and all(claim.status in accepted_object_statuses for claim in claims)
            ),
            "detail": "fuentes, evidencias y claims deben estar validados/publicados",
        },
    ]
    blockers = [check["label"] for check in checks if not check["passed"]]
    publishable = (not blockers) and (version.status in {"candidate", "validated"})
    return KnowledgePublicationReadiness(
        version=version.id,
        status=version.status,
        publishable=publishable,
        publication_unit="knowledge_version",
        partial_publications_allowed=False,
        checks=checks,
        blockers=blockers,
        audit_preview={
            "event_type": "knowledge.published",
            "entity_type": "knowledge_version",
            "entity_id": version.id,
            "base_version": version.id,
            "required_fields": publication_policy().audit_fields,
        },
    )


QUERY_TYPE_KEYWORDS = {
    "definition": ["que es", "define", "definicion", "significa"],
    "normative_correction": ["correct", "coma", "debe", "norma", "lleva"],
    "descriptive_explanation": ["por que", "ambigua", "explica"],
    "writing_recommendation": ["claro", "mejor", "escritura", "parrafo", "estilo", "revision"],
    "literary_analysis": [
        "narrador",
        "focalizacion",
        "metafora",
        "literario",
        "escena",
        "personaje",
        "dialogo",
    ],
    "terminological": ["termino", "mismo", "alias", "equivale"],
    "historical": ["histor", "cambio", "version", "antes"],
    "evidence": ["fuente", "evidencia", "sostiene", "justifica"],
    "comparative": ["diferencia", "compara", "frente", "versus"],
}

DOMAIN_KEYWORDS = {
    "LENGUA": ["lengua", "norma", "coma", "gramatica", "lexica", "lexico"],
    "ESCRITURA": ["escritura", "estilo", "claro", "sobriedad", "dinamismo", "parrafo"],
    "TEORIA LITERARIA": [
        "narrador",
        "focalizacion",
        "metafora",
        "comparacion",
        "escena",
        "trama",
        "personaje",
        "dialogo",
        "tension",
    ],
    "GLOSARIO": ["termino", "definicion", "significa"],
}

QUERY_TYPE_RELATION_PRIORITIES = {
    "definition": ["define", "equivale_a", "es_parte_de"],
    "normative_correction": ["contradice", "requiere", "describe"],
    "writing_recommendation": ["usa", "ejemplifica", "relacionado_con", "depende_de"],
    "literary_analysis": ["aparece_en", "estudiado_por", "usa"],
    "comparative": ["compara_con", "contradice", "equivale_a", "relacionado_con"],
}

QUERY_STOPWORDS = {
    "algo",
    "ante",
    "aqui",
    "cada",
    "como",
    "con",
    "contra",
    "cual",
    "cuando",
    "desde",
    "donde",
    "dos",
    "entre",
    "esta",
    "este",
    "esto",
    "hacer",
    "hacia",
    "las",
    "los",
    "mas",
    "menos",
    "mis",
    "muy",
    "para",
    "pero",
    "por",
    "que",
    "sea",
    "sin",
    "sobre",
    "una",
    "uno",
}

QUERY_TERM_EXPANSIONS = {
    "charla": {"dialogo", "dialogo con funcion", "conversacion"},
    "conversacion": {"dialogo", "dialogo con funcion", "dialogo funcional", "voz", "personaje"},
    "conversaciones": {"dialogo", "dialogo con funcion", "dialogo funcional", "voz", "personaje"},
    "decirlo": {"declarar", "explicitar", "subtexto"},
    "dialogos": {"dialogo"},
    "explicarlo": {"declarar", "explicitar", "subtexto"},
    "insinuar": {"sugerir", "subtexto", "inferencia"},
    "ocultar": {"ocultacion", "subtexto", "focalizacion"},
    "personajes": {"personaje"},
    "puente": {"transicion", "estructura"},
    "relleno": {"decorativa", "funcion", "transicion"},
    "rellenar": {"decorativa", "funcion"},
    "revisar": {"revision", "reescritura"},
    "sirva": {"funcion", "cambio", "decision"},
    "servir": {"funcion", "cambio", "decision"},
    "sugerir": {"subtexto", "inferencia"},
    "transicion": {"puente", "estructura"},
}

EDITORIAL_REVISION_ROUTE = [
    "card-diagnostico-de-reescritura",
    "card-revision-estructural",
    "card-diagnostico-de-coherencia",
    "card-revision-de-parrafo",
    "card-revision-de-frase",
    "card-revision-de-tono",
    "card-limpieza-final",
]
EDITORIAL_REVISION_ROUTE_ORDER = {
    card_id: index for index, card_id in enumerate(EDITORIAL_REVISION_ROUTE)
}
EDITORIAL_REVISION_QUERY_MARKERS = {
    "diagnostico",
    "limpieza",
    "parrafo",
    "reescritura",
    "revision",
    "revisar",
    "texto",
    "tono",
}


def _is_editorial_revision_query(normalized_query: str, terms: set[str]) -> bool:
    if not ({"revision", "revisar"} & terms):
        return False
    marker_count = len(EDITORIAL_REVISION_QUERY_MARKERS & terms)
    return marker_count >= 2 or "que le pasa a este texto" in normalized_query


def resolve_knowledge_version(version: str) -> str:
    if version == "latest":
        return LATEST_KNOWLEDGE_VERSION
    return version


def _normalize_query(query: str) -> str:
    decomposed = normalize("NFKD", query.lower())
    without_accents = "".join(char for char in decomposed if category(char) != "Mn")
    return " ".join(without_accents.split())


def _query_terms(normalized_query: str) -> set[str]:
    raw_terms = {
        term
        for term in normalized_query.split()
        if len(term) > 2 and term not in QUERY_STOPWORDS
    }
    tokenized = normalized_query.replace("-", " ").replace("/", " ")
    split_terms = {
        term
        for term in tokenized.split()
        if len(term) > 2 and term not in QUERY_STOPWORDS
    }
    return raw_terms | split_terms


def _expanded_query_terms(terms: set[str]) -> dict[str, set[str]]:
    return {term: {term, *QUERY_TERM_EXPANSIONS.get(term, set())} for term in terms}


def _detect_query_types(normalized_query: str) -> list[str]:
    detected = [
        query_type
        for query_type, keywords in QUERY_TYPE_KEYWORDS.items()
        if any(keyword in normalized_query for keyword in keywords)
    ]
    return detected or ["writing_recommendation"]


def _detect_domains(normalized_query: str, matched_nodes: list[KnowledgeNode]) -> list[str]:
    detected = [
        domain
        for domain, keywords in DOMAIN_KEYWORDS.items()
        if any(keyword in normalized_query for keyword in keywords)
    ]
    for node in matched_nodes:
        branch = node.primary_branch.upper()
        if "LENGUA" in branch and "LENGUA" not in detected:
            detected.append("LENGUA")
        if "ESCRITURA" in branch and "ESCRITURA" not in detected:
            detected.append("ESCRITURA")
    return detected or ["ESCRITURA"]


def _text_match_score(terms: set[str], haystack: str) -> float:
    if not terms:
        return 0.0
    normalized_haystack = _normalize_query(haystack)
    tokenized_haystack = normalized_haystack.replace("-", " ").replace("/", " ")
    haystack_terms = set(tokenized_haystack.split())
    expanded_terms = _expanded_query_terms(terms)
    matches = 0.0
    for term, alternatives in expanded_terms.items():
        if term in normalized_haystack:
            matches += 1.0
            continue
        expanded_alternatives = alternatives - {term}
        if expanded_alternatives & haystack_terms:
            matches += 0.55
            continue
        if any(alternative in normalized_haystack for alternative in expanded_alternatives):
            matches += 0.45
    return matches / len(terms)


def query_contract() -> KnowledgeQueryContract:
    return KnowledgeQueryContract(
        meaning=(
            "Una consulta es una peticion de lectura contra conocimiento estable; "
            "no modifica perfil, preferencias ni conocimiento publicado."
        ),
        query_unit="texto breve del usuario + version solicitada + limite de recuperacion",
        lifecycle=QUERY_LIFECYCLE,
        interpretation_fields=[
            "query",
            "normalized_query",
            "requested_version",
            "resolved_version",
            "query_type",
            "domain",
        ],
        restriction_fields=[
            "resolved_version",
            "limit",
            "max_cards",
            "profile_mutation_allowed",
            "stable_knowledge_mutation_allowed",
            "generation_allowed",
        ],
        context_fields=[
            "profile_influence",
            "stable_knowledge_mutation",
            "retrieval_unit",
            "ranking_policy",
        ],
        out_of_scope=QUERY_OUT_OF_SCOPE,
        allowed_version_values=[*KNOWLEDGE_VERSION_IDS, "latest"],
        profile_boundary=(
            "El perfil puede influir solo en presentacion u ordenacion futura; "
            "no altera la interpretacion contractual ni el conocimiento estable."
        ),
        retrieval_boundary=(
            "La consulta prepara una solicitud de recuperacion; la recuperacion decide "
            "fichas, claims, evidencias, fuentes y relaciones devueltas."
        ),
        generation_boundary="La generacion no forma parte de la consulta ni se ejecuta en este contrato.",
        audit_fields=[
            "query_length",
            "limit",
            "requested_version",
            "resolved_version",
            "query_type",
            "domain",
        ],
        acceptance_criteria=[
            "normaliza la consulta sin perder el texto original",
            "resuelve latest a una version existente",
            "declara tipo y dominio antes de recuperar",
            "rechaza versiones inexistentes",
            "no registra ni expone la consulta cruda en auditoria",
            "no muta perfil ni conocimiento estable",
        ],
    )


def interpret_knowledge_query(payload: KnowledgeQueryInput) -> KnowledgeQueryInterpretation:
    requested_version = payload.version
    resolved_version = resolve_knowledge_version(payload.version)
    normalized_query = _normalize_query(payload.query)
    query_types = _detect_query_types(normalized_query)
    domains = _detect_domains(normalized_query, [])
    restrictions = {
        "requested_version": requested_version,
        "resolved_version": resolved_version,
        "limit": payload.limit,
        "max_cards": payload.limit,
        "profile_mutation_allowed": False,
        "stable_knowledge_mutation_allowed": False,
        "generation_allowed": False,
        "retrieval_required": True,
    }
    context = {
        "profile_influence": "presentation_only",
        "stable_knowledge_mutation": False,
        "retrieval_unit": "knowledge_card",
        "ranking_policy": "deterministic_traceable",
    }
    return KnowledgeQueryInterpretation(
        query=payload.query,
        normalized_query=normalized_query,
        requested_version=requested_version,
        resolved_version=resolved_version,
        query_type=query_types,
        domain=domains,
        restrictions=restrictions,
        context=context,
        retrieval_request={
            "required": True,
            "version": resolved_version,
            "limit": payload.limit,
            "query_terms": sorted(_query_terms(normalized_query)),
            "query_type": query_types,
            "domain": domains,
        },
        audit_payload={
            "query_length": len(payload.query),
            "limit": payload.limit,
            "requested_version": requested_version,
            "resolved_version": resolved_version,
            "query_type": query_types,
            "domain": domains,
        },
    )


def query_knowledge(
    payload: KnowledgeQueryInput,
    sources: list[KnowledgeSource] | None = None,
    nodes: list[KnowledgeNode] | None = None,
    cards: list[KnowledgeCard] | None = None,
    claims: list[KnowledgeClaim] | None = None,
    evidence: list[KnowledgeEvidenceItem] | None = None,
) -> KnowledgeQueryResult:
    interpretation = interpret_knowledge_query(payload)
    requested_version = interpretation.requested_version
    resolved_version = interpretation.resolved_version
    normalized_query = interpretation.normalized_query
    terms = _query_terms(normalized_query)
    editorial_revision_query = _is_editorial_revision_query(normalized_query, terms)
    query_types = interpretation.query_type
    sources = sources if sources is not None else seed_sources()
    nodes = nodes if nodes is not None else seed_nodes()
    cards = cards if cards is not None else seed_cards()
    claims = claims if claims is not None else seed_claims()
    evidence = evidence if evidence is not None else seed_evidence()
    allowed_statuses = {"published"}
    published_claims = [claim for claim in claims if claim.status in allowed_statuses]
    published_evidence = [item for item in evidence if item.status in allowed_statuses]
    sources_by_id = {source.id: source for source in sources}
    nodes_by_id = {node.id: node for node in nodes}
    evidence_by_id = {item.id: item for item in published_evidence}
    claims_by_card: dict[str, list[KnowledgeClaim]] = {}
    for claim in published_claims:
        claims_by_card.setdefault(claim.card_id, []).append(claim)

    relations = seed_relations()
    relations_by_source = {
        (relation.source_entity_type, relation.source_entity_id): relation
        for relation in relations
        if relation.status in allowed_statuses and relation.confidence >= 0.5
    }
    candidate_nodes: set[str] = set()
    discarded_claims: list[str] = []
    ranking: list[dict] = []

    def evaluate_card(card: KnowledgeCard) -> tuple[float, dict, list[str], list[str]]:
        linked_claims = claims_by_card.get(card.id, [])
        linked_evidence = [
            evidence_by_id[claim.evidence_id]
            for claim in linked_claims
            if claim.evidence_id in evidence_by_id
        ]
        if not linked_claims or not linked_evidence:
            return 0.0, {"concept_match": 0.0}, [], []
        linked_nodes = [
            nodes_by_id[item.node_id] for item in linked_evidence if item.node_id in nodes_by_id
        ]
        linked_sources = [
            sources_by_id[item.source_id]
            for item in linked_evidence
            if item.source_id in sources_by_id
        ]
        haystack = " ".join(
            [
                card.id,
                card.card_type,
                card.name,
                card.definition,
                " ".join(str(value) for value in card.payload.values()),
                " ".join(
                    " ".join(
                        [
                            claim.statement,
                            claim.claim_type,
                            claim.node_id,
                            " ".join(claim.related_node_ids),
                            claim.domain,
                            " ".join(str(value) for value in claim.scope.values()),
                            claim.status,
                            claim.origin,
                        ]
                    )
                    for claim in linked_claims
                ),
                " ".join(f"{item.reference} {item.excerpt}" for item in linked_evidence),
                " ".join(
                    " ".join(
                        [
                            node.title,
                            node.summary,
                            node.node_type,
                            node.canonical_name,
                            node.primary_branch,
                            node.secondary_branch,
                            node.short_definition,
                            node.long_definition,
                            " ".join(node.aliases),
                        ]
                    )
                    for node in linked_nodes
                ),
                " ".join(
                    f"{source.name} {source.source_type} {source.status}"
                    for source in linked_sources
                ),
            ]
        )
        core_haystack = " ".join(
            [
                card.id,
                card.name,
                card.definition,
                " ".join(
                    " ".join(
                        [
                            node.title,
                            node.canonical_name,
                            node.primary_branch,
                            node.secondary_branch,
                            node.short_definition,
                            " ".join(node.aliases),
                        ]
                    )
                    for node in linked_nodes
                ),
            ]
        )
        concept_match = _text_match_score(terms, haystack)
        core_match = _text_match_score(terms, core_haystack)
        normalized_core_haystack = _normalize_query(core_haystack)
        natural_term_boost = 0.0
        if {"charla", "conversacion", "conversaciones"} & terms and "dialogo" in normalized_core_haystack:
            natural_term_boost = 2.5
        domain_match = 1.0 if any(term in haystack.lower() for term in ("lexic", "estilo", "escrit")) else 0.5
        if "TEORIA LITERARIA" in _detect_domains(normalized_query, []):
            literary_haystack = _normalize_query(
                " ".join(
                    [
                        card.card_type,
                        " ".join(claim.domain for claim in linked_claims),
                        " ".join(
                            f"{node.primary_branch} {node.secondary_branch} {node.node_type}"
                            for node in linked_nodes
                        ),
                    ]
                )
            )
            if not any(
                marker in literary_haystack
                for marker in ("liter", "narrat", "retoric", "poetic", "personaje")
            ):
                domain_match = 0.1
        scope_match = 1.0 if any(claim.scope.get("language") == "es" for claim in linked_claims) else 0.0
        context_match = 1.0 if any("general" in item.context for item in linked_evidence) else 0.5
        authority_score = (
            max((source.authority_level for source in linked_sources), default=0) / 5
        )
        evidence_score = max((item.confidence for item in linked_evidence), default=0)
        claim_confidence = max((claim.confidence for claim in linked_claims), default=0)
        relation_score = 0.0
        relation_paths: list[str] = []
        for item in linked_evidence:
            relation = relations_by_source.get(("node", item.node_id))
            if relation is None:
                continue
            relation_score = max(relation_score, relation.confidence * relation.weight)
            relation_paths.append(relation.id)
        status_score = 1.0
        version_score = 1.0
        factors = {
            "concept_match": round(concept_match, 3),
            "core_match": round(core_match, 3),
            "domain_match": round(domain_match, 3),
            "scope_match": round(scope_match, 3),
            "context_match": round(context_match, 3),
            "editorial_route_order": EDITORIAL_REVISION_ROUTE_ORDER.get(card.id),
            "authority_score": round(authority_score, 3),
            "evidence_score": round(evidence_score, 3),
            "claim_confidence": round(claim_confidence, 3),
            "relation_score": round(relation_score, 3),
            "natural_term_boost": round(natural_term_boost, 3),
            "version_score": round(version_score, 3),
            "status_score": round(status_score, 3),
        }
        score = round(
            (concept_match * 3)
            + (core_match * 5)
            + (domain_match * 0.5)
            + (scope_match * 0.25)
            + (authority_score * 0.35)
            + (evidence_score * 0.5)
            + (claim_confidence * 0.5)
            + (context_match * 0.25)
            + (relation_score * 0.35)
            + natural_term_boost
            + (version_score * 0.25)
            + (status_score * 0.25),
            3,
        )
        reasons = []
        if concept_match:
            reasons.append("coincidencia conceptual con consulta normalizada")
        if linked_claims:
            reasons.append("contiene claims aplicables")
        if linked_evidence:
            reasons.append("conserva evidencias trazables")
        if linked_sources:
            reasons.append("identifica fuentes de respaldo")
        if relation_paths:
            reasons.append("expansion controlada por relaciones")
        if editorial_revision_query and card.id in EDITORIAL_REVISION_ROUTE_ORDER:
            reasons.append("orden editorial por capas de revision")
        return score, factors, reasons, relation_paths

    evaluated_cards = []
    for card in cards:
        score, factors, reasons, relation_paths = evaluate_card(card)
        if score <= 0 or factors["concept_match"] <= 0:
            continue
        evaluated_cards.append((card, score, factors, reasons, relation_paths))
        ranking.append(
            {
                "card_id": card.id,
                "final_score": score,
                "factors": factors,
                "reasons": reasons,
            }
        )

    def evaluation_sort_key(
        item: tuple[KnowledgeCard, float, dict, list[str], list[str]],
    ) -> tuple[float, float, str]:
        card, score, factors, _, _ = item
        if editorial_revision_query:
            route_order = factors.get("editorial_route_order")
            if route_order is not None:
                return (route_order, -score, card.id)
        return (999.0, -score, card.id)

    def ranking_sort_key(item: dict) -> tuple[float, float, str]:
        route_order = item["factors"].get("editorial_route_order")
        if editorial_revision_query and route_order is not None:
            return (route_order, -item["final_score"], item["card_id"])
        return (999.0, -item["final_score"], item["card_id"])

    ranked_evaluations = sorted(evaluated_cards, key=evaluation_sort_key)[: payload.limit]
    ranked_cards = [item[0] for item in ranked_evaluations]
    card_ids = {card.id for card in ranked_cards}
    matched_claims = [
        claim
        for claim in claims
        if claim.card_id in card_ids
        and claim.status in allowed_statuses
        and claim.confidence >= 0.4
    ]
    for claim in claims:
        if claim.card_id in card_ids and claim not in matched_claims:
            discarded_claims.append(claim.id)
    evidence_ids = {claim.evidence_id for claim in matched_claims}
    matched_evidence = [
        item
        for item in evidence
        if item.id in evidence_ids
        and item.status in allowed_statuses
        and item.confidence >= 0.4
    ]
    matched_source_ids = {item.source_id for item in matched_evidence}
    matched_sources = [source for source in sources if source.id in matched_source_ids]
    matched_nodes = [
        nodes_by_id[item.node_id] for item in matched_evidence if item.node_id in nodes_by_id
    ]
    for node in matched_nodes:
        candidate_nodes.add(node.id)
    matched_relation_ids = {
        relation_path
        for _, _, _, _, relation_paths in ranked_evaluations
        for relation_path in relation_paths[:20]
    }
    relations_followed = [
        relation for relation in relations if relation.id in matched_relation_ids
    ][:20]
    domains = _detect_domains(normalized_query, matched_nodes)
    retrieved_cards = []
    for card, score, _, reasons, relation_paths in ranked_evaluations:
        card_claims = [claim for claim in matched_claims if claim.card_id == card.id]
        card_evidence = [
            item for item in matched_evidence if item.id in {claim.evidence_id for claim in card_claims}
        ]
        node_id = card_claims[0].node_id if card_claims else ""
        source_ids = sorted({item.source_id for item in card_evidence})
        retrieved_cards.append(
            RetrievedKnowledgeCard(
                card_id=card.id,
                node_id=node_id,
                name=card.name,
                summary=card.definition,
                score=score,
                reasons=reasons,
                claim_ids=[claim.id for claim in card_claims],
                source_ids=source_ids,
                relation_paths=relation_paths[:2],
                confidence=card.confidence,
            )
        )
    status = "ok"
    if not ranked_cards:
        status = "no_match"
    elif not matched_evidence:
        status = "insufficient_evidence"
    elif any(claim.confidence < 0.6 for claim in matched_claims):
        status = "low_confidence"
    return KnowledgeQueryResult(
        query=payload.query,
        version=resolved_version,
        requested_version=requested_version,
        resolved_version=resolved_version,
        query_type=query_types,
        domain=domains,
        context={
            **interpretation.context,
            "editorial_route": EDITORIAL_REVISION_ROUTE if editorial_revision_query else [],
            "normalized_query": normalized_query,
            "primary_domain": domains[0] if domains else None,
        },
        status=status,
        card_count=len(ranked_cards),
        claim_count=len(matched_claims),
        evidence_count=len(matched_evidence),
        cards=ranked_cards,
        claims=matched_claims,
        evidence=matched_evidence,
        sources=matched_sources,
        relations_followed=relations_followed,
        contradictions=[],
        ranking=sorted(ranking, key=ranking_sort_key)[: payload.limit],
        retrieved_cards=retrieved_cards,
        retrieval_trace={
            "original_query_preserved_in_response": True,
            "normalized_query": normalized_query,
            "requested_version": requested_version,
            "resolved_version": resolved_version,
            "filters": {
                "claim_status": sorted(allowed_statuses),
                "minimum_claim_confidence": 0.4,
                "minimum_evidence_confidence": 0.4,
                "max_relation_depth": 2,
                "max_nodes": 20,
            },
            "candidate_nodes": sorted(candidate_nodes),
            "candidate_cards": [item[0].id for item in evaluated_cards],
            "selected_cards": [card.id for card in ranked_cards],
            "selected_claims": [claim.id for claim in matched_claims],
            "selected_evidence": [item.id for item in matched_evidence],
            "discarded_claims": discarded_claims,
            "relations_followed": [relation.id for relation in relations_followed],
            "ranking_factors": [
                item["factors"]
                for item in sorted(
                    ranking,
                    key=ranking_sort_key,
                )[: payload.limit]
            ],
            "thresholds": {
                "supporting_claim_min_confidence": 0.4,
                "published_claim_min_confidence": 0.6,
                "primary_answer_min_confidence": 0.75,
            },
            "timings": {
                "interpretation_time": 0,
                "retrieval_time": 0,
            },
        },
        limits={
            "max_cards": payload.limit,
            "max_claims": len(matched_claims),
            "max_evidence": len(matched_evidence),
            "max_relation_depth": 2,
            "max_total_tokens": 0,
            "timeout": 0,
        },
        generated_at=datetime.now(UTC).isoformat(),
    )


def _gym_status(score: float) -> str:
    if score >= 0.9:
        return "pass"
    if score >= 0.7:
        return "warning"
    return "fail"


def _gym_check(
    check_id: str,
    score: float,
    summary: str,
    details: dict | None = None,
) -> KnowledgeGymCheck:
    bounded_score = max(0.0, min(1.0, round(score, 3)))
    return KnowledgeGymCheck(
        id=check_id,
        status=_gym_status(bounded_score),
        score=bounded_score,
        summary=summary,
        details=details or {},
    )


def _gym_terms(text: str) -> set[str]:
    return {term for term in _query_terms(_normalize_query(text)) if len(term) > 3}


def _gym_similarity(left: KnowledgeCard, right: KnowledgeCard) -> float:
    left_terms = _gym_terms(f"{left.name} {left.definition}")
    right_terms = _gym_terms(f"{right.name} {right.definition}")
    if not left_terms or not right_terms:
        return 0.0
    return len(left_terms & right_terms) / len(left_terms | right_terms)


def knowledge_gym_report(
    version: str,
    sources: list[KnowledgeSource],
    nodes: list[KnowledgeNode],
    cards: list[KnowledgeCard],
    claims: list[KnowledgeClaim],
    evidence: list[KnowledgeEvidenceItem],
) -> KnowledgeGymReport:
    checks: list[KnowledgeGymCheck] = []
    published_claims = [claim for claim in claims if claim.status == "published"]
    published_evidence = [item for item in evidence if item.status == "published"]
    source_ids = {source.id for source in sources}
    evidence_by_id = {item.id: item for item in published_evidence}

    precision_cases = [
        ("complemento directo", "card-complemento-directo"),
        ("coma incidental", "card-coma-incidental"),
        ("sinonimia contextual", "card-sinonimia-contextual"),
        ("subtexto narrativo", "card-subtexto-narrativo"),
        ("gancho sin truco", "card-gancho-sin-truco"),
    ]
    precision_details = []
    selected_cards: list[str] = []
    precision_hits = 0
    for query, expected_card_id in precision_cases:
        result = query_knowledge(
            KnowledgeQueryInput(query=query, version=version, limit=5),
            sources=sources,
            nodes=nodes,
            cards=cards,
            claims=claims,
            evidence=evidence,
        )
        returned_ids = [card.id for card in result.cards]
        selected_cards.extend(returned_ids[:1])
        hit = expected_card_id in returned_ids
        precision_hits += 1 if hit else 0
        precision_details.append(
            {
                "query": query,
                "expected_card_id": expected_card_id,
                "returned_card_ids": returned_ids,
                "hit": hit,
            }
        )
    checks.append(
        _gym_check(
            "retrieval_precision",
            precision_hits / len(precision_cases),
            "Consultas controladas recuperan sus fichas esperadas.",
            {"cases": precision_details},
        )
    )

    unique_selected = len(set(selected_cards))
    diversity_score = unique_selected / max(1, len(selected_cards))
    checks.append(
        _gym_check(
            "retrieval_diversity",
            diversity_score,
            "Consultas distintas no deben devolver siempre la misma ficha principal.",
            {
                "top_card_ids": selected_cards,
                "unique_top_card_count": unique_selected,
            },
        )
    )

    broken_traceability: list[dict] = []
    for card in cards:
        card_claims = [claim for claim in published_claims if claim.card_id == card.id]
        if not card_claims:
            broken_traceability.append({"card_id": card.id, "issue": "missing_claim"})
            continue
        for claim in card_claims:
            supporting_evidence = evidence_by_id.get(claim.evidence_id)
            if supporting_evidence is None:
                broken_traceability.append(
                    {"card_id": card.id, "claim_id": claim.id, "issue": "missing_evidence"}
                )
                continue
            if supporting_evidence.source_id not in source_ids:
                broken_traceability.append(
                    {
                        "card_id": card.id,
                        "claim_id": claim.id,
                        "evidence_id": supporting_evidence.id,
                        "issue": "missing_source",
                    }
                )
    traceability_score = 1.0 - (len(broken_traceability) / max(1, len(cards)))
    checks.append(
        _gym_check(
            "traceability",
            traceability_score,
            "Cada ficha publicada conserva claim, evidencia y fuente.",
            {"issues": broken_traceability[:20], "issue_count": len(broken_traceability)},
        )
    )

    weak_payloads = []
    for card in cards:
        signals = card.payload.get("signals", [])
        risks = card.payload.get("risks", [])
        contexts = card.payload.get("contexts", [])
        if not signals or not risks or not contexts:
            weak_payloads.append(
                {
                    "card_id": card.id,
                    "missing": [
                        name
                        for name, value in (
                            ("signals", signals),
                            ("risks", risks),
                            ("contexts", contexts),
                        )
                        if not value
                    ],
                }
            )
    utility_score = 1.0 - (len(weak_payloads) / max(1, len(cards)))
    checks.append(
        _gym_check(
            "utility_payload",
            utility_score,
            "Las fichas deben tener senales, riesgos y contextos de uso.",
            {"weak_cards": weak_payloads[:20], "weak_card_count": len(weak_payloads)},
        )
    )

    redundant_pairs = []
    for index, left in enumerate(cards):
        for right in cards[index + 1 :]:
            similarity = _gym_similarity(left, right)
            if similarity >= 0.82:
                redundant_pairs.append(
                    {
                        "left_card_id": left.id,
                        "right_card_id": right.id,
                        "similarity": round(similarity, 3),
                    }
                )
    redundancy_score = 1.0 - (len(redundant_pairs) / max(1, len(cards)))
    checks.append(
        _gym_check(
            "redundancy",
            redundancy_score,
            "Detecta fichas que parecen demasiado solapadas.",
            {
                "pairs": redundant_pairs[:20],
                "pair_count": len(redundant_pairs),
            },
        )
    )

    broad_result = query_knowledge(
        KnowledgeQueryInput(query="estilo", version=version, limit=5),
        sources=sources,
        nodes=nodes,
        cards=cards,
        claims=claims,
        evidence=evidence,
    )
    specific_result = query_knowledge(
        KnowledgeQueryInput(query="coma incidental", version=version, limit=5),
        sources=sources,
        nodes=nodes,
        cards=cards,
        claims=claims,
        evidence=evidence,
    )
    broad_ids = {card.id for card in broad_result.cards}
    specific_ids = {card.id for card in specific_result.cards}
    hierarchy_score = 1.0 if broad_ids and specific_ids and broad_ids != specific_ids else 0.0
    checks.append(
        _gym_check(
            "query_granularity",
            hierarchy_score,
            "Una consulta amplia y una concreta deben producir recorridos distintos.",
            {
                "broad_query": "estilo",
                "broad_card_ids": sorted(broad_ids),
                "specific_query": "coma incidental",
                "specific_card_ids": sorted(specific_ids),
            },
        )
    )

    weak_count = (
        len(broken_traceability)
        + len(weak_payloads)
        + len(redundant_pairs)
        + (len(precision_cases) - precision_hits)
    )
    diet_score = 1.0 - (weak_count / max(1, len(cards) + len(precision_cases)))
    checks.append(
        _gym_check(
            "knowledge_diet",
            diet_score,
            "Resume si el conocimiento publicado esta util, variado y trazable.",
            {
                "healthy_card_count_estimate": max(0, len(cards) - len(weak_payloads)),
                "review_signal_count": weak_count,
                "note": "No elimina ni modifica conocimiento; solo senala revision.",
            },
        )
    )

    report_score = round(sum(check.score for check in checks) / len(checks), 3)
    report_status = "pass"
    if any(check.status == "fail" for check in checks):
        report_status = "fail"
    elif any(check.status == "warning" for check in checks):
        report_status = "warning"
    return KnowledgeGymReport(
        version=version,
        status=report_status,
        score=report_score,
        checked_card_count=len(cards),
        checked_claim_count=len(published_claims),
        checked_evidence_count=len(published_evidence),
        checks=checks,
        generated_at=datetime.now(UTC).isoformat(),
    )
