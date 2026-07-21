from app.core.models import PersistenceDomain


def persistence_domains() -> list[PersistenceDomain]:
    return [
        _domain("knowledge", "seeded registry", "versioned"),
        _domain("preferences", "postgresql", "persisted"),
        _domain("profiles", "postgresql", "persisted"),
        _domain("scores", "postgresql", "persisted"),
        _domain("manual_overrides", "evidences + score_variables", "persisted"),
        _domain("contexts", "score_variables.context", "persisted"),
        _domain("texts", "generated_texts", "persisted"),
        _domain("versions", "knowledge/status + migrations", "partial"),
        _domain("comparisons", "postgresql", "persisted"),
        _domain("feedback", "feedback_proposals", "persisted"),
        _domain("statistics", "computed from persisted profile data", "computed"),
    ]


def _domain(identifier: str, storage: str, status: str) -> PersistenceDomain:
    return PersistenceDomain(
        id=identifier,
        storage=storage,
        status=status,
        separated_from_knowledge=identifier == "knowledge" or storage != "seeded registry",
    )
