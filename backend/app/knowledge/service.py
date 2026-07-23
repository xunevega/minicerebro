from datetime import UTC, datetime
from unicodedata import category, normalize

from app.core.models import (
    KnowledgeCard,
    KnowledgeClaim,
    KnowledgeClaimEvidenceLink,
    KnowledgeEvidenceItem,
    KnowledgeIngestionBatch,
    KnowledgeIngestionBatchExport,
    KnowledgeIngestionPolicy,
    KnowledgeIngestionReadiness,
    KnowledgeNode,
    KnowledgeNodeRelation,
    KnowledgeObjectRevision,
    KnowledgePublicationPolicy,
    KnowledgePublicationReadiness,
    KnowledgeQueryInput,
    KnowledgeQueryResult,
    KnowledgeRelation,
    RetrievedKnowledgeCard,
    KnowledgeSource,
    KnowledgeSourceEdition,
    KnowledgeVersion,
    KnowledgeVersioningPolicy,
)

KNOWLEDGE_VERSION = "knowledge-v0"
KNOWLEDGE_PUBLISHED_AT = "2026-07-22"
RELATION_UPDATED_AT = "2026-07-23"
LATEST_KNOWLEDGE_VERSION = KNOWLEDGE_VERSION
PUBLICATION_LIFECYCLE = [
    "draft",
    "review",
    "validated",
    "candidate",
    "published",
    "deprecated",
    "archived",
]
PUBLICATION_REQUIREMENTS = [
    "integridad referencial",
    "sin nodos huerfanos",
    "sin claims sin evidencia",
    "sin evidencias sin fuente",
    "sin fichas vacias",
    "sin relaciones rotas",
    "sin conflictos criticos",
]
PUBLICATION_VALIDATIONS = [
    "estructura",
    "documentacion",
    "consistencia",
    "duplicados",
    "contradicciones",
    "tests",
    "integridad",
]
INGESTION_LIFECYCLE = [
    "registered",
    "acquisition_pending",
    "available",
    "structured",
    "segmented",
    "extracting",
    "normalizing",
    "review",
    "validated",
    "candidate",
    "published",
]
INGESTION_ALTERNATIVE_STATES = ["blocked", "failed", "cancelled"]
INGESTION_FLOW = [
    "registered_source",
    "edition",
    "document_structure",
    "segmentation",
    "extraction",
    "nodes",
    "evidence",
    "claims",
    "cards",
    "validation",
    "candidate_version",
]

DEFAULT_SOURCE_EDITION = "pendiente de identificacion"
DEFAULT_SOURCE_PUBLICATION_DATE = "pendiente de identificacion"
DEFAULT_SOURCE_LOCATION = "pendiente de adquisicion"
DEFAULT_SOURCE_RIGHTS = "registro autorizado; contenido no ingerido"
DEFAULT_SOURCE_STRUCTURE = ["pendiente de estructuracion"]
DEFAULT_SOURCE_LOCATORS = ["edicion", "parte", "capitulo", "seccion", "pagina", "entrada", "url"]

VERSIONED_OBJECT_TYPES = [
    "source",
    "source_edition",
    "node",
    "relation",
    "evidence",
    "claim",
    "knowledge_card",
    "tree",
    "ontology",
    "schema",
    "knowledge_version",
]

EXCLUDED_VERSIONED_OBJECT_TYPES = [
    "profile",
    "preference",
    "scoring",
    "feedback",
    "laboratory",
    "prompt",
    "query",
    "generation",
    "user_history",
    "temporary_event",
]


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
        release_chain=["knowledge-v0"],
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
    )


def _empty_ingestion_metrics() -> dict:
    return {
        "nodes_created": 0,
        "evidence": 0,
        "claims": 0,
        "relations": 0,
        "cards": 0,
        "duplicates": 0,
        "contradictions": 0,
        "elapsed_seconds": 0,
        "coverage": 0,
    }


def _ingestion_blockers(source: KnowledgeSource, edition: KnowledgeSourceEdition) -> list[str]:
    blockers = []
    if edition.label == DEFAULT_SOURCE_EDITION:
        blockers.append("missing_edition")
    if edition.location == DEFAULT_SOURCE_LOCATION:
        blockers.append("missing_location")
    if edition.acquisition_status != "available":
        blockers.append("acquisition_not_available")
    if edition.validation_status != "validated":
        blockers.append("edition_not_validated")
    if not edition.locator_system or edition.locator_system == DEFAULT_SOURCE_LOCATORS:
        blockers.append("document_structure_pending")
    if "contenido no ingerido" in source.rights:
        blockers.append("rights_review_required")
    return blockers


def seed_ingestion_batches() -> list[KnowledgeIngestionBatch]:
    sources_by_id = {source.id: source for source in seed_sources()}
    batches = []
    for edition in seed_source_editions():
        source = sources_by_id[edition.source_id]
        blockers = _ingestion_blockers(source, edition)
        batches.append(
            KnowledgeIngestionBatch(
                id=f"ingest-{edition.id}",
                source_id=source.id,
                source_edition_id=edition.id,
                batch_label="lote inicial pendiente de adquisicion",
                scope="edicion completa pendiente de identificacion documental",
                status="blocked" if blockers else "registered",
                author="minicerebro-seed",
                tools=["manual_review"],
                model_used=None,
                configuration={
                    "unit": "one_source_one_edition_one_batch",
                    "ai_origin_required": "automated",
                    "publishes_directly": False,
                },
                progress={
                    "registered_source": True,
                    "edition": not blockers,
                    "document_structure": False,
                    "segmentation": False,
                    "extraction": False,
                    "normalization": False,
                    "review": False,
                    "validation": False,
                    "candidate_version": False,
                },
                metrics=_empty_ingestion_metrics(),
                decisions=[],
                blockers=blockers,
                result="not_started",
                created_at=RELATION_UPDATED_AT,
                updated_at=RELATION_UPDATED_AT,
            )
        )
    return batches


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

    checks = [
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
                and all(item.status == "published" for item in evidence)
                and all(claim.status == "published" for claim in claims)
            ),
            "detail": "fuentes, evidencias y claims deben estar validados/publicados",
        },
    ]
    blockers = [check["label"] for check in checks if not check["passed"]]
    publishable = not blockers and version.status in {"candidate", "validated"}
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


def _source(
    *,
    catalog_id: str,
    source_id: str,
    name: str,
    responsible: str,
    source_type: str,
    domains: list[str],
    authority_level: int,
    priority: int,
) -> KnowledgeSource:
    return KnowledgeSource(
        id=source_id,
        catalog_id=catalog_id,
        name=name,
        responsible=responsible,
        source_type=source_type,
        domains=domains,
        authority_level=authority_level,
        priority=priority,
        status="registered",
        edition=DEFAULT_SOURCE_EDITION,
        publication_date=DEFAULT_SOURCE_PUBLICATION_DATE,
        location=DEFAULT_SOURCE_LOCATION,
        acquisition_status="registered",
        validation_status="not_validated",
        rights=DEFAULT_SOURCE_RIGHTS,
        structure=DEFAULT_SOURCE_STRUCTURE,
        locator_system=DEFAULT_SOURCE_LOCATORS,
    )


def seed_sources() -> list[KnowledgeSource]:
    return [
        _source(
            catalog_id="F001",
            source_id="rae-ngle",
            name="Nueva gramatica de la lengua espanola",
            responsible="Real Academia Espanola y Asociacion de Academias de la Lengua Espanola",
            source_type="gramatica descriptiva y normativa",
            domains=[
                "morfologia",
                "sintaxis",
                "categorias gramaticales",
                "funciones",
                "construcciones",
            ],
            authority_level=5,
            priority=1,
        ),
        _source(
            catalog_id="F002",
            source_id="rae-gtg",
            name="Glosario de terminos gramaticales",
            responsible="Real Academia Espanola y Asociacion de Academias de la Lengua Espanola",
            source_type="glosario gramatical especializado",
            domains=["terminologia gramatical", "relaciones conceptuales"],
            authority_level=5,
            priority=1,
        ),
        _source(
            catalog_id="F003",
            source_id="rae-ole",
            name="Ortografia de la lengua espanola",
            responsible="Real Academia Espanola y Asociacion de Academias de la Lengua Espanola",
            source_type="ortografia normativa",
            domains=["grafias", "acentuacion", "puntuacion", "mayusculas", "ortotipografia"],
            authority_level=5,
            priority=1,
        ),
        _source(
            catalog_id="F004",
            source_id="rae-dpd",
            name="Diccionario panhispanico de dudas",
            responsible="Real Academia Espanola y Asociacion de Academias de la Lengua Espanola",
            source_type="repertorio normativo de dudas",
            domains=["gramatica", "ortografia", "lexico", "extranjerismos", "dudas de uso"],
            authority_level=5,
            priority=1,
        ),
        _source(
            catalog_id="F005",
            source_id="rae-dle",
            name="Diccionario de la lengua espanola",
            responsible="Real Academia Espanola y Asociacion de Academias de la Lengua Espanola",
            source_type="diccionario general",
            domains=["lexico", "acepciones", "categorias", "locuciones", "marcas de uso"],
            authority_level=5,
            priority=1,
        ),
        _source(
            catalog_id="F006",
            source_id="rae-lese",
            name="Libro de estilo de la lengua espanola segun la norma panhispanica",
            responsible="Real Academia Espanola y Asociacion de Academias de la Lengua Espanola",
            source_type="manual institucional de estilo",
            domains=["redaccion", "escritura digital", "ortotipografia", "comunicacion"],
            authority_level=4,
            priority=2,
        ),
        _source(
            catalog_id="F007",
            source_id="rae-corpes",
            name="CORPES XXI",
            responsible="Real Academia Espanola y Asociacion de Academias de la Lengua Espanola",
            source_type="corpus linguistico",
            domains=["frecuencia", "distribucion", "registro", "pais", "genero", "contexto"],
            authority_level=4,
            priority=2,
        ),
        _source(
            catalog_id="F008",
            source_id="reyes-arte-escribir",
            name="El arte de escribir bien en espanol",
            responsible="Graciela Reyes",
            source_type="manual de redaccion y gramatica aplicada",
            domains=["redaccion", "pragmatica", "coherencia", "construccion textual", "estilo"],
            authority_level=4,
            priority=2,
        ),
        _source(
            catalog_id="F009",
            source_id="martinez-sousa-mele",
            name="Manual de estilo de la lengua espanola",
            responsible="Jose Martinez de Sousa",
            source_type="manual de estilo y edicion",
            domains=["estilo", "edicion", "ortotipografia", "presentacion"],
            authority_level=4,
            priority=2,
        ),
        _source(
            catalog_id="F010",
            source_id="fundeu-recomendaciones",
            name="Recomendaciones de FundeuRAE",
            responsible="FundeuRAE",
            source_type="recomendaciones de uso actual",
            domains=["neologismos", "tecnologia", "medios", "extranjerismos", "actualidad"],
            authority_level=3,
            priority=2,
        ),
        _source(
            catalog_id="F011",
            source_id="aristoteles-retorica",
            name="Retorica",
            responsible="Aristoteles",
            source_type="retorica clasica",
            domains=["persuasion", "argumentacion", "generos retoricos", "ethos", "pathos", "logos"],
            authority_level=5,
            priority=3,
        ),
        _source(
            catalog_id="F012",
            source_id="quintiliano-institutio",
            name="Institutio oratoria",
            responsible="Marco Fabio Quintiliano",
            source_type="retorica clasica",
            domains=["formacion del orador", "construccion del discurso", "estilo", "elocucion"],
            authority_level=5,
            priority=3,
        ),
        _source(
            catalog_id="F013",
            source_id="carnegie-hablar-publico",
            name="Como hablar bien en publico e influir en los hombres de negocios",
            responsible="Dale Carnegie",
            source_type="comunicacion oral y divulgacion practica",
            domains=["discurso oral", "exposicion", "audiencia", "comunicacion practica"],
            authority_level=3,
            priority=4,
        ),
        _source(
            catalog_id="F014",
            source_id="aristoteles-poetica",
            name="Poetica",
            responsible="Aristoteles",
            source_type="teoria literaria clasica",
            domains=["mimesis", "trama", "personaje", "tragedia", "reconocimiento", "peripecia"],
            authority_level=5,
            priority=3,
        ),
        _source(
            catalog_id="F015",
            source_id="wellek-warren-teoria-literatura",
            name="Teoria de la literatura",
            responsible="Rene Wellek y Austin Warren",
            source_type="manual general de teoria literaria",
            domains=["teoria literaria", "generos", "analisis", "historia", "critica"],
            authority_level=4,
            priority=3,
        ),
        _source(
            catalog_id="F016",
            source_id="genette-figuras-iii",
            name="Figuras III",
            responsible="Gerard Genette",
            source_type="narratologia",
            domains=["tiempo", "modo", "voz", "orden", "duracion", "frecuencia"],
            authority_level=5,
            priority=2,
        ),
        _source(
            catalog_id="F017",
            source_id="genette-discurso-relato",
            name="Discurso del relato",
            responsible="Gerard Genette",
            source_type="narratologia",
            domains=["estructura narrativa", "tiempo", "modo", "voz"],
            authority_level=5,
            priority=2,
        ),
        _source(
            catalog_id="F018",
            source_id="saussure-curso-linguistica",
            name="Curso de linguistica general",
            responsible="Ferdinand de Saussure",
            source_type="linguistica general",
            domains=["signo", "lengua", "habla", "sincronia", "diacronia"],
            authority_level=5,
            priority=3,
        ),
        _source(
            catalog_id="F019",
            source_id="chomsky-aspects",
            name="Aspectos de la teoria de la sintaxis",
            responsible="Noam Chomsky",
            source_type="teoria linguistica y sintaxis generativa",
            domains=["competencia", "actuacion", "estructura profunda", "gramatica generativa"],
            authority_level=4,
            priority=4,
        ),
        _source(
            catalog_id="F020",
            source_id="strunk-white-elements-style",
            name="The Elements of Style",
            responsible="William Strunk Jr. y E. B. White",
            source_type="manual de estilo en lengua inglesa",
            domains=["concision", "claridad", "edicion", "revision"],
            authority_level=3,
            priority=4,
        ),
        _source(
            catalog_id="F021",
            source_id="zinsser-on-writing-well",
            name="On Writing Well",
            responsible="William Zinsser",
            source_type="escritura de no ficcion",
            domains=["claridad", "sencillez", "voz", "revision", "no ficcion"],
            authority_level=4,
            priority=3,
        ),
        _source(
            catalog_id="F022",
            source_id="lazaro-correa-comentario-texto",
            name="Como se comenta un texto literario",
            responsible="Fernando Lazaro Carreter y Evaristo Correa Calderon",
            source_type="analisis y comentario de textos",
            domains=["lectura", "analisis", "estructura", "tema", "forma", "comentario literario"],
            authority_level=4,
            priority=3,
        ),
        _source(
            catalog_id="F023",
            source_id="martinez-sousa-ortotipografia",
            name="Ortografia y ortotipografia del espanol actual",
            responsible="Jose Martinez de Sousa",
            source_type="ortografia y ortotipografia especializada",
            domains=["edicion", "tipografia", "signos", "composicion", "convenciones graficas"],
            authority_level=4,
            priority=2,
        ),
    ]


def seed_source_editions() -> list[KnowledgeSourceEdition]:
    return [
        KnowledgeSourceEdition(
            id=f"{source.id}:pending-edition",
            source_id=source.id,
            label=source.edition,
            publication_date=source.publication_date,
            location=source.location,
            acquisition_status=source.acquisition_status,
            validation_status=source.validation_status,
            rights=source.rights,
            structure=source.structure,
            locator_system=source.locator_system,
        )
        for source in seed_sources()
    ]


def seed_nodes() -> list[KnowledgeNode]:
    return [
        KnowledgeNode(
            id="rae-norma-estilo",
            source_id="rae-ngle",
            node_type="norma",
            title="Norma y uso en lengua espanola",
            summary="Nodo semilla para reglas normativas y criterios de uso estable.",
            canonical_name="Norma y uso en lengua espanola",
            primary_branch="lengua espanola",
            secondary_branch="norma y uso",
            short_definition="Concepto que agrupa criterios normativos y descriptivos estables.",
            long_definition=(
                "Nodo conceptual publicado para conectar fuentes academicas registradas, "
                "evidencias normativas y claims sobre uso estable de la lengua espanola."
            ),
            status="published",
            version=KNOWLEDGE_VERSION,
            created_at=KNOWLEDGE_PUBLISHED_AT,
            published_at=KNOWLEDGE_PUBLISHED_AT,
            aliases=["criterio normativo", "uso estable"],
        ),
        KnowledgeNode(
            id="manual-rasgos-escritura",
            source_id="rae-lese",
            node_type="categoria",
            title="Aplicacion practica de estilo",
            summary="Nodo semilla para rasgos de redaccion, estilo, dinamismo y sobriedad.",
            canonical_name="Aplicacion practica de estilo",
            primary_branch="escritura",
            secondary_branch="estilo",
            short_definition="Concepto que agrupa criterios practicos de estilo aplicados a escritura.",
            long_definition=(
                "Nodo conceptual publicado para conectar fuentes de estilo registradas, "
                "evidencias de redaccion y claims sobre dinamismo, sobriedad y claridad."
            ),
            status="published",
            version=KNOWLEDGE_VERSION,
            created_at=KNOWLEDGE_PUBLISHED_AT,
            published_at=KNOWLEDGE_PUBLISHED_AT,
            aliases=["criterio de estilo", "redaccion aplicada"],
        ),
    ]


def seed_node_relations() -> list[KnowledgeNodeRelation]:
    return [
        KnowledgeNodeRelation(
            id="rel-norma-define-estilo",
            source_node_id="rae-norma-estilo",
            target_node_id="manual-rasgos-escritura",
            relation_type="define",
            direction="outgoing",
            cardinality="N:N",
            weight=0.72,
            confidence=0.58,
            context="knowledge_graph",
            status="published",
            version=KNOWLEDGE_VERSION,
            created_at=KNOWLEDGE_PUBLISHED_AT,
            updated_at=RELATION_UPDATED_AT,
        ),
        KnowledgeNodeRelation(
            id="rel-estilo-depende-norma",
            source_node_id="manual-rasgos-escritura",
            target_node_id="rae-norma-estilo",
            relation_type="depende_de",
            direction="outgoing",
            cardinality="N:N",
            weight=0.68,
            confidence=0.58,
            context="knowledge_graph",
            status="published",
            version=KNOWLEDGE_VERSION,
            created_at=KNOWLEDGE_PUBLISHED_AT,
            updated_at=RELATION_UPDATED_AT,
        ),
    ]


def _relation(
    source_type: str,
    source_id: str,
    relation_type: str,
    target_type: str,
    target_id: str,
    *,
    cardinality: str = "N:N",
    weight: float = 1.0,
    confidence: float = 0.58,
    context: str = "knowledge_graph",
    status: str = "published",
) -> KnowledgeRelation:
    return KnowledgeRelation(
        id=f"rel-{source_type}-{source_id}-{relation_type}-{target_type}-{target_id}",
        source_entity_type=source_type,
        source_entity_id=source_id,
        target_entity_type=target_type,
        target_entity_id=target_id,
        relation_type=relation_type,
        direction="outgoing",
        cardinality=cardinality,
        weight=weight,
        confidence=confidence,
        context=context,
        status=status,
        version=KNOWLEDGE_VERSION,
        created_at=KNOWLEDGE_PUBLISHED_AT,
        updated_at=RELATION_UPDATED_AT,
    )


def seed_relations() -> list[KnowledgeRelation]:
    source_to_edition = [
        _relation("source", source.id, "contiene", "source_edition", f"{source.id}:pending-edition")
        for source in seed_sources()
    ]
    source_to_node = [
        _relation("source", node.source_id, "documentado_en", "node", node.id)
        for node in seed_nodes()
    ]
    node_to_node = [
        _relation(
            "node",
            relation.source_node_id,
            relation.relation_type,
            "node",
            relation.target_node_id,
            weight=relation.weight,
            confidence=relation.confidence,
            context=relation.context,
            status=relation.status,
        )
        for relation in seed_node_relations()
    ]
    node_to_evidence = [
        _relation(
            "node",
            evidence.node_id,
            "sostenido_por",
            "evidence",
            evidence.id,
            cardinality="1:N",
            confidence=evidence.confidence,
            context=evidence.context,
            status=evidence.status,
        )
        for evidence in seed_evidence()
    ]
    evidence_to_claim = [
        _relation(
            "evidence",
            claim.evidence_id,
            "sostenido_por",
            "claim",
            claim.id,
            cardinality="1:N",
            confidence=claim.confidence,
            context=claim.domain,
            status=claim.status,
        )
        for claim in seed_claims()
    ]
    claim_to_card = [
        _relation(
            "claim",
            claim.id,
            "aplicacion_de",
            "knowledge_card",
            claim.card_id,
            cardinality="N:1",
            confidence=claim.confidence,
            context=claim.domain,
            status=claim.status,
        )
        for claim in seed_claims()
    ]
    source_to_evidence = [
        _relation(
            "source_edition",
            evidence.source_edition_id,
            "documentado_en",
            "evidence",
            evidence.id,
            cardinality="1:N",
            confidence=evidence.confidence,
            context=evidence.context,
            status=evidence.status,
        )
        for evidence in seed_evidence()
    ]
    return [
        *source_to_edition,
        *source_to_node,
        *node_to_node,
        *node_to_evidence,
        *source_to_evidence,
        *evidence_to_claim,
        *claim_to_card,
    ]


def seed_evidence() -> list[KnowledgeEvidenceItem]:
    return [
        KnowledgeEvidenceItem(
            id="ev-precision-lexica",
            node_id="rae-norma-estilo",
            source_id="rae-dle",
            source_edition_id="rae-dle:pending-edition",
            evidence_type="documented_paraphrase",
            locator={
                "catalog_id": "F005",
                "edition": "pendiente de identificacion",
                "unit": "entrada lexica pendiente de ingestion",
                "locator": "pendiente de localizacion verificable",
                "url": None,
            },
            reference="catalogo F005; localizador pendiente de ingestion",
            excerpt="La precision lexica reduce ambiguedad y mejora verificabilidad.",
            context="general_rule",
            confidence=0.58,
            confidence_level=2,
            status="draft",
            version=KNOWLEDGE_VERSION,
            created_at=KNOWLEDGE_PUBLISHED_AT,
            updated_at=KNOWLEDGE_PUBLISHED_AT,
            incorporated_by="minicerebro-seed",
            reviewed_by=None,
            revision=1,
        ),
        KnowledgeEvidenceItem(
            id="ev-dinamismo-frase",
            node_id="manual-rasgos-escritura",
            source_id="rae-lese",
            source_edition_id="rae-lese:pending-edition",
            evidence_type="documented_paraphrase",
            locator={
                "catalog_id": "F006",
                "edition": "pendiente de identificacion",
                "unit": "criterio de estilo pendiente de ingestion",
                "locator": "pendiente de localizacion verificable",
                "url": None,
            },
            reference="catalogo F006; localizador pendiente de ingestion",
            excerpt="El dinamismo aumenta cuando la frase avanza con verbos activos y menos acumulacion.",
            context="commentary",
            confidence=0.52,
            confidence_level=2,
            status="draft",
            version=KNOWLEDGE_VERSION,
            created_at=KNOWLEDGE_PUBLISHED_AT,
            updated_at=KNOWLEDGE_PUBLISHED_AT,
            incorporated_by="minicerebro-seed",
            reviewed_by=None,
            revision=1,
        ),
        KnowledgeEvidenceItem(
            id="ev-sobriedad-voz",
            node_id="manual-rasgos-escritura",
            source_id="rae-lese",
            source_edition_id="rae-lese:pending-edition",
            evidence_type="documented_paraphrase",
            locator={
                "catalog_id": "F006",
                "edition": "pendiente de identificacion",
                "unit": "criterio de estilo pendiente de ingestion",
                "locator": "pendiente de localizacion verificable",
                "url": None,
            },
            reference="catalogo F006; localizador pendiente de ingestion",
            excerpt="La sobriedad depende de contencion expresiva y baja ornamentacion.",
            context="commentary",
            confidence=0.5,
            confidence_level=2,
            status="draft",
            version=KNOWLEDGE_VERSION,
            created_at=KNOWLEDGE_PUBLISHED_AT,
            updated_at=KNOWLEDGE_PUBLISHED_AT,
            incorporated_by="minicerebro-seed",
            reviewed_by=None,
            revision=1,
        ),
    ]


def seed_evidence_revisions() -> list[dict]:
    return [
        {
            "id": f"{evidence.id}:r1",
            "evidence_id": evidence.id,
            "revision": 1,
            "author": "minicerebro-seed",
            "reason": "registro inicial segun contrato de evidencias V1",
            "changes": {
                "status": evidence.status,
                "source_edition_id": evidence.source_edition_id,
                "locator": evidence.locator,
            },
            "created_at": evidence.created_at,
        }
        for evidence in seed_evidence()
    ]


def seed_claims() -> list[KnowledgeClaim]:
    return [
        KnowledgeClaim(
            id="claim-dinamismo-frase",
            evidence_id="ev-dinamismo-frase",
            card_id="frase-dinamismo",
            statement="El dinamismo de frase se asocia a avance sintactico y verbos activos.",
            claim_type="stylistic",
            node_id="manual-rasgos-escritura",
            related_node_ids=["rae-norma-estilo"],
            domain="writing.style",
            scope={
                "language": "es",
                "register": "general",
                "geography": "panhispanic",
                "period": "contemporary",
                "text_type": "writing",
            },
            status="draft",
            confidence=0.52,
            origin="seed_contract_entry",
            version=KNOWLEDGE_VERSION,
            revision=1,
            created_at=KNOWLEDGE_PUBLISHED_AT,
            updated_at=KNOWLEDGE_PUBLISHED_AT,
            published_at=None,
        ),
        KnowledgeClaim(
            id="claim-precision-lexica",
            evidence_id="ev-precision-lexica",
            card_id="lexico-precision",
            statement="La precision lexica favorece formulaciones concretas y verificables.",
            claim_type="stylistic",
            node_id="rae-norma-estilo",
            related_node_ids=["manual-rasgos-escritura"],
            domain="writing.lexicon",
            scope={
                "language": "es",
                "register": "general",
                "geography": "panhispanic",
                "period": "contemporary",
                "text_type": "writing",
            },
            status="draft",
            confidence=0.58,
            origin="seed_contract_entry",
            version=KNOWLEDGE_VERSION,
            revision=1,
            created_at=KNOWLEDGE_PUBLISHED_AT,
            updated_at=KNOWLEDGE_PUBLISHED_AT,
            published_at=None,
        ),
        KnowledgeClaim(
            id="claim-sobriedad-voz",
            evidence_id="ev-sobriedad-voz",
            card_id="voz-sobriedad",
            statement="La sobriedad reduce enfasis decorativo y mantiene autoridad tonal.",
            claim_type="stylistic",
            node_id="manual-rasgos-escritura",
            related_node_ids=["rae-norma-estilo"],
            domain="writing.style",
            scope={
                "language": "es",
                "register": "general",
                "geography": "panhispanic",
                "period": "contemporary",
                "text_type": "writing",
            },
            status="draft",
            confidence=0.5,
            origin="seed_contract_entry",
            version=KNOWLEDGE_VERSION,
            revision=1,
            created_at=KNOWLEDGE_PUBLISHED_AT,
            updated_at=KNOWLEDGE_PUBLISHED_AT,
            published_at=None,
        ),
    ]


def seed_claim_evidence_links() -> list[KnowledgeClaimEvidenceLink]:
    return [
        KnowledgeClaimEvidenceLink(
            id=f"{claim.id}:{claim.evidence_id}:primary",
            claim_id=claim.id,
            evidence_id=claim.evidence_id,
            role="primary",
            created_at=claim.created_at,
        )
        for claim in seed_claims()
    ]


def seed_claim_revisions() -> list[dict]:
    return [
        {
            "id": f"{claim.id}:r1",
            "claim_id": claim.id,
            "revision": 1,
            "knowledge_version": claim.version,
            "author": "minicerebro-seed",
            "reason": "registro inicial segun contrato de claims V1",
            "changed_fields": [
                "statement",
                "claim_type",
                "node_id",
                "domain",
                "scope",
                "status",
                "evidence_links",
            ],
            "previous_claim": {},
            "new_claim": {
                "statement": claim.statement,
                "claim_type": claim.claim_type,
                "node_id": claim.node_id,
                "domain": claim.domain,
                "scope": claim.scope,
                "status": claim.status,
                "evidence_id": claim.evidence_id,
            },
            "created_at": claim.created_at,
        }
        for claim in seed_claims()
    ]


def seed_cards() -> list[KnowledgeCard]:
    return [
        KnowledgeCard(
            id="frase-dinamismo",
            card_type="style_trait",
            name="Dinamismo de frase",
            definition="Rasgo asociado a ritmo, avance sintactico y baja friccion de lectura.",
            confidence=0.55,
            version=KNOWLEDGE_VERSION,
            payload={
                "signals": ["verbos activos", "oraciones menos acumulativas", "transiciones claras"],
                "risks": ["precipitacion", "perdida de matiz"],
                "contexts": ["articulo", "publicitario", "narrativa"],
            },
        ),
        KnowledgeCard(
            id="lexico-precision",
            card_type="style_trait",
            name="Precision lexica",
            definition="Eleccion de palabras especificas y verificables frente a formulaciones vagas.",
            confidence=0.6,
            version=KNOWLEDGE_VERSION,
            payload={
                "signals": ["terminos concretos", "menos comodines", "definiciones operativas"],
                "risks": ["rigidez", "tecnicismo innecesario"],
                "contexts": ["tecnico", "ensayo", "articulo"],
            },
        ),
        KnowledgeCard(
            id="voz-sobriedad",
            card_type="style_trait",
            name="Sobriedad",
            definition="Contencion expresiva que evita enfasis decorativo y conserva autoridad.",
            confidence=0.5,
            version=KNOWLEDGE_VERSION,
            payload={
                "signals": ["adjetivacion medida", "tono estable", "poca hipérbole"],
                "risks": ["sequedad", "falta de energia"],
                "contexts": ["ensayo", "tecnico"],
            },
        ),
    ]


def seed_versions() -> list[KnowledgeVersion]:
    return [
        KnowledgeVersion(
            id=KNOWLEDGE_VERSION,
            status="seed",
            published_at="not-published",
            source_count=len(seed_sources()),
            node_count=len(seed_nodes()),
            evidence_count=len(seed_evidence()),
            claim_count=len(seed_claims()),
            card_count=len(seed_cards()),
        )
    ]


def _object_revision(object_type: str, object_id: str, after: dict) -> KnowledgeObjectRevision:
    return KnowledgeObjectRevision(
        id=f"rev-{object_type}-{object_id}-r1",
        object_type=object_type,
        object_id=object_id,
        revision_number=1,
        object_version=f"{object_id}@r1",
        knowledge_version=KNOWLEDGE_VERSION,
        status="active",
        change_type="created",
        author="minicerebro-seed",
        reason="registro inicial segun contrato de versionado V1",
        previous_revision=None,
        replaces_object_id=None,
        replaced_by_object_id=None,
        before={},
        after=after,
        created_at=RELATION_UPDATED_AT,
        updated_at=RELATION_UPDATED_AT,
    )


def seed_object_revisions() -> list[KnowledgeObjectRevision]:
    revisions: list[KnowledgeObjectRevision] = []
    revisions.extend(
        _object_revision(
            "source",
            source.id,
            {
                "catalog_id": source.catalog_id,
                "name": source.name,
                "status": source.status,
                "authority_level": source.authority_level,
            },
        )
        for source in seed_sources()
    )
    revisions.extend(
        _object_revision(
            "source_edition",
            edition.id,
            {
                "source_id": edition.source_id,
                "label": edition.label,
                "acquisition_status": edition.acquisition_status,
                "validation_status": edition.validation_status,
            },
        )
        for edition in seed_source_editions()
    )
    revisions.extend(
        _object_revision(
            "node",
            node.id,
            {
                "canonical_name": node.canonical_name,
                "node_type": node.node_type,
                "primary_branch": node.primary_branch,
                "status": node.status,
                "relations": [relation.id for relation in seed_node_relations() if relation.source_node_id == node.id],
            },
        )
        for node in seed_nodes()
    )
    revisions.extend(
        _object_revision(
            "relation",
            relation.id,
            {
                "source_entity_type": relation.source_entity_type,
                "source_entity_id": relation.source_entity_id,
                "relation_type": relation.relation_type,
                "target_entity_type": relation.target_entity_type,
                "target_entity_id": relation.target_entity_id,
                "status": relation.status,
            },
        )
        for relation in seed_relations()
    )
    revisions.extend(
        _object_revision(
            "evidence",
            evidence.id,
            {
                "source_id": evidence.source_id,
                "source_edition_id": evidence.source_edition_id,
                "node_id": evidence.node_id,
                "status": evidence.status,
                "locator": evidence.locator,
            },
        )
        for evidence in seed_evidence()
    )
    revisions.extend(
        _object_revision(
            "claim",
            claim.id,
            {
                "statement": claim.statement,
                "claim_type": claim.claim_type,
                "node_id": claim.node_id,
                "status": claim.status,
                "evidence_id": claim.evidence_id,
            },
        )
        for claim in seed_claims()
    )
    revisions.extend(
        _object_revision(
            "knowledge_card",
            card.id,
            {
                "name": card.name,
                "card_type": card.card_type,
                "version": card.version,
                "payload_keys": sorted(card.payload),
            },
        )
        for card in seed_cards()
    )
    revisions.extend(
        [
            _object_revision(
                "tree",
                "knowledge-tree-v0",
                {"root": "knowledge-v0", "node_ids": [node.id for node in seed_nodes()]},
            ),
            _object_revision(
                "ontology",
                "knowledge-ontology-v0",
                {
                    "node_types": sorted({node.node_type for node in seed_nodes()}),
                    "relation_types": sorted({relation.relation_type for relation in seed_relations()}),
                },
            ),
            _object_revision(
                "schema",
                "knowledge-schema-v0",
                {"versioned_object_types": VERSIONED_OBJECT_TYPES},
            ),
            _object_revision(
                "knowledge_version",
                KNOWLEDGE_VERSION,
                {
                    "status": "seed",
                    "published_at": "not-published",
                    "immutable_after_publication": True,
                },
            ),
        ]
    )
    return revisions


QUERY_TYPE_KEYWORDS = {
    "definition": ["que es", "define", "definicion", "significa"],
    "normative_correction": ["correct", "coma", "debe", "norma", "lleva"],
    "descriptive_explanation": ["por que", "ambigua", "explica"],
    "writing_recommendation": ["claro", "mejor", "escritura", "parrafo", "estilo"],
    "literary_analysis": ["narrador", "focalizacion", "metafora", "literario"],
    "terminological": ["termino", "mismo", "alias", "equivale"],
    "historical": ["histor", "cambio", "version", "antes"],
    "evidence": ["fuente", "evidencia", "sostiene", "justifica"],
    "comparative": ["diferencia", "compara", "frente", "versus"],
}

DOMAIN_KEYWORDS = {
    "LENGUA": ["lengua", "norma", "coma", "gramatica", "lexica", "lexico"],
    "ESCRITURA": ["escritura", "estilo", "claro", "sobriedad", "dinamismo", "parrafo"],
    "TEORIA LITERARIA": ["narrador", "focalizacion", "metafora", "comparacion"],
    "GLOSARIO": ["termino", "definicion", "significa"],
}

QUERY_TYPE_RELATION_PRIORITIES = {
    "definition": ["define", "equivale_a", "es_parte_de"],
    "normative_correction": ["contradice", "requiere", "describe"],
    "writing_recommendation": ["usa", "ejemplifica", "relacionado_con", "depende_de"],
    "literary_analysis": ["aparece_en", "estudiado_por", "usa"],
    "comparative": ["compara_con", "contradice", "equivale_a", "relacionado_con"],
}


def resolve_knowledge_version(version: str) -> str:
    if version == "latest":
        return LATEST_KNOWLEDGE_VERSION
    return version


def _normalize_query(query: str) -> str:
    decomposed = normalize("NFKD", query.lower())
    without_accents = "".join(char for char in decomposed if category(char) != "Mn")
    return " ".join(without_accents.split())


def _query_terms(normalized_query: str) -> set[str]:
    return {term for term in normalized_query.split() if len(term) > 2}


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
    return sum(1 for term in terms if term in normalized_haystack) / len(terms)


def query_knowledge(
    payload: KnowledgeQueryInput,
    sources: list[KnowledgeSource] | None = None,
    nodes: list[KnowledgeNode] | None = None,
    cards: list[KnowledgeCard] | None = None,
    claims: list[KnowledgeClaim] | None = None,
    evidence: list[KnowledgeEvidenceItem] | None = None,
) -> KnowledgeQueryResult:
    requested_version = payload.version
    resolved_version = resolve_knowledge_version(payload.version)
    normalized_query = _normalize_query(payload.query)
    terms = _query_terms(normalized_query)
    query_types = _detect_query_types(normalized_query)
    sources = sources if sources is not None else seed_sources()
    nodes = nodes if nodes is not None else seed_nodes()
    cards = cards if cards is not None else seed_cards()
    claims = claims if claims is not None else seed_claims()
    evidence = evidence if evidence is not None else seed_evidence()
    sources_by_id = {source.id: source for source in sources}
    nodes_by_id = {node.id: node for node in nodes}
    evidence_by_id = {item.id: item for item in evidence}
    claims_by_card: dict[str, list[KnowledgeClaim]] = {}
    for claim in claims:
        claims_by_card.setdefault(claim.card_id, []).append(claim)

    relations = seed_relations()
    relations_by_source = {
        (relation.source_entity_type, relation.source_entity_id): relation
        for relation in relations
        if relation.version == resolved_version and relation.confidence >= 0.5
    }
    allowed_statuses = {"published", "draft"}
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
        concept_match = _text_match_score(terms, haystack)
        domain_match = 1.0 if any(term in haystack.lower() for term in ("lexic", "estilo", "escrit")) else 0.5
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
        status_score = 1.0 if card.version == resolved_version else 0.0
        version_score = 1.0 if card.version == resolved_version else 0.0
        factors = {
            "concept_match": round(concept_match, 3),
            "domain_match": round(domain_match, 3),
            "scope_match": round(scope_match, 3),
            "context_match": round(context_match, 3),
            "authority_score": round(authority_score, 3),
            "evidence_score": round(evidence_score, 3),
            "claim_confidence": round(claim_confidence, 3),
            "relation_score": round(relation_score, 3),
            "version_score": round(version_score, 3),
            "status_score": round(status_score, 3),
        }
        score = round(
            concept_match
            + domain_match
            + scope_match
            + authority_score
            + evidence_score
            + context_match
            + relation_score
            + version_score
            + status_score,
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
        return score, factors, reasons, relation_paths

    evaluated_cards = []
    for card in cards:
        if card.version != resolved_version:
            continue
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

    ranked_evaluations = sorted(evaluated_cards, key=lambda item: item[1], reverse=True)[
        : payload.limit
    ]
    ranked_cards = [item[0] for item in ranked_evaluations]
    card_ids = {card.id for card in ranked_cards}
    matched_claims = [
        claim
        for claim in claims
        if claim.card_id in card_ids
        and claim.version == resolved_version
        and claim.status in allowed_statuses
        and claim.confidence >= 0.4
    ]
    for claim in claims:
        if claim.version == resolved_version and claim.card_id in card_ids and claim not in matched_claims:
            discarded_claims.append(claim.id)
    evidence_ids = {claim.evidence_id for claim in matched_claims}
    matched_evidence = [
        item
        for item in evidence
        if item.id in evidence_ids
        and item.version == resolved_version
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
            "normalized_query": normalized_query,
            "primary_domain": domains[0] if domains else None,
            "profile_influence": "presentation_only",
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
        ranking=ranking[: payload.limit],
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
            "ranking_factors": [item["factors"] for item in ranking[: payload.limit]],
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
