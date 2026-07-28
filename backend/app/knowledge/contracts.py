from app.core.models import KnowledgeSource, KnowledgeSourceEdition


LATEST_KNOWLEDGE_VERSION = "knowledge-v51"
KNOWLEDGE_VERSION_IDS = [
    "knowledge-v0",
    "knowledge-v1",
    *[f"knowledge-v{version}" for version in range(2, 51)],
    LATEST_KNOWLEDGE_VERSION,
]

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
QUERY_LIFECYCLE = ["query", "interpretation", "restrictions", "context", "retrieval"]
QUERY_OUT_OF_SCOPE = [
    "perfil",
    "preferencias",
    "scoring",
    "feedback",
    "laboratorio",
    "prompts",
    "generaciones",
    "historial de usuario",
]

DEFAULT_SOURCE_EDITION = "pendiente de identificacion"
DEFAULT_SOURCE_LOCATION = "pendiente de adquisicion"
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


def ingestion_blockers(source: KnowledgeSource, edition: KnowledgeSourceEdition) -> list[str]:
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
