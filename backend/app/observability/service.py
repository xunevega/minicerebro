from app.core.models import ObservabilityMetric


def observability_metrics() -> list[ObservabilityMetric]:
    return [
        ObservabilityMetric(
            id="interpretation_time",
            source="audit_events preference.created.duration_ms",
            status="available",
        ),
        ObservabilityMetric(
            id="generation_time",
            source="audit_events text.generated.duration_ms",
            status="available",
        ),
        ObservabilityMetric(id="retrieved_cards", source="knowledge/cards", status="available"),
        ObservabilityMetric(id="adequacy_percentage", source="comparisons.adequacy_score", status="available"),
        ObservabilityMetric(id="average_modification", source="comparisons.modification_score", status="available"),
        ObservabilityMetric(id="doubtful_variables", source="profile statistics", status="available"),
        ObservabilityMetric(id="contradictions", source="profiles/{id}/contradictions", status="available"),
        ObservabilityMetric(id="approval_count", source="audit_events feedback.applied", status="available"),
        ObservabilityMetric(id="rejection_count", source="audit_events feedback.rejected", status="available"),
        ObservabilityMetric(id="manual_adjustment_ratio", source="score_variables", status="available"),
        ObservabilityMetric(
            id="retrieval_quality",
            source="knowledge/query-history.pending_validation_count",
            status="available",
        ),
    ]
