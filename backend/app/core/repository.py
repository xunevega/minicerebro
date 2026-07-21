from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.models import (
    AuditEvent,
    ComparisonResult,
    Evidence,
    EvidenceType,
    Preference,
    PreferenceStatus,
    Profile,
    ProfileStatistics,
    ScoreProposal,
    ScoreVariable,
    Contradiction,
)
from app.core.seeds import seed_variables
from app.db.models import (
    AuditEventRecord,
    ComparisonRecord,
    EvidenceRecord,
    PreferenceRecord,
    ProfileRecord,
    ScoreVariableRecord,
)


def evidence_from_record(record: EvidenceRecord) -> Evidence:
    return Evidence(
        id=UUID(record.id),
        evidence_type=EvidenceType(record.evidence_type),
        source=record.source,
        summary=record.summary,
        weight=record.weight,
        context=record.context,
        created_at=record.created_at,
    )


def evidence_to_record(evidence: Evidence) -> EvidenceRecord:
    return EvidenceRecord(
        id=str(evidence.id),
        evidence_type=evidence.evidence_type.value,
        source=evidence.source,
        summary=evidence.summary,
        weight=evidence.weight,
        context=evidence.context,
        created_at=evidence.created_at,
    )


def preference_from_record(record: PreferenceRecord) -> Preference:
    return Preference(
        id=UUID(record.id),
        text=record.text,
        interpreted_as=record.interpreted_as,
        status=PreferenceStatus(record.status),
        evidence=evidence_from_record(record.evidence),
        affected_variables=record.affected_variables,
        created_at=record.created_at,
    )


def preference_to_record(profile_id: str, preference: Preference) -> PreferenceRecord:
    return PreferenceRecord(
        id=str(preference.id),
        profile_id=profile_id,
        evidence_id=str(preference.evidence.id),
        text=preference.text,
        interpreted_as=preference.interpreted_as,
        status=preference.status.value,
        affected_variables=preference.affected_variables,
        created_at=preference.created_at,
    )


def score_from_record(record: ScoreVariableRecord) -> ScoreVariable:
    return ScoreVariable(
        key=record.key,
        label=record.label,
        category=record.category,
        calculated_value=record.calculated_value,
        manual_adjustment=record.manual_adjustment,
        confidence=record.confidence,
        context=record.context,
        evidence_count=record.evidence_count,
        updated_at=record.updated_at,
    )


def profile_from_record(record: ProfileRecord) -> Profile:
    return Profile(
        id=record.id,
        name=record.name,
        language=record.language,
        summary=record.summary,
        variables=[score_from_record(variable) for variable in record.variables],
        preferences=[preference_from_record(preference) for preference in record.preferences],
        updated_at=record.updated_at,
    )


def comparison_from_record(record: ComparisonRecord) -> ComparisonResult:
    return ComparisonResult(
        id=UUID(record.id),
        modification_score=record.modification_score,
        adequacy_score=record.adequacy_score,
        changed_words=record.changed_words,
        original_words=record.original_words,
        revised_words=record.revised_words,
        summary=record.summary,
        dimensions={},
        changes=[],
        created_at=record.created_at,
    )


def audit_event_from_record(record: AuditEventRecord) -> AuditEvent:
    return AuditEvent(
        id=record.id,
        event_type=record.event_type,
        entity_type=record.entity_type,
        entity_id=record.entity_id,
        payload=record.payload,
        created_at=record.created_at,
    )


class Repository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_profile(self, profile_id: str) -> Profile:
        record = self.session.scalar(
            select(ProfileRecord)
            .where(ProfileRecord.id == profile_id)
            .options(
                selectinload(ProfileRecord.variables),
                selectinload(ProfileRecord.preferences).selectinload(PreferenceRecord.evidence),
            )
        )
        if record is None:
            raise KeyError(profile_id)
        return profile_from_record(record)

    def get_context_variables(self, profile_id: str, context: str) -> list[ScoreVariable]:
        self.ensure_context_variables(profile_id, context)
        records = self.session.scalars(
            select(ScoreVariableRecord)
            .where(
                ScoreVariableRecord.profile_id == profile_id,
                ScoreVariableRecord.context == context,
            )
            .order_by(ScoreVariableRecord.id)
        ).all()
        return [score_from_record(record) for record in records]

    def ensure_context_variables(self, profile_id: str, context: str) -> None:
        existing = self.session.scalar(
            select(ScoreVariableRecord).where(
                ScoreVariableRecord.profile_id == profile_id,
                ScoreVariableRecord.context == context,
            )
        )
        if existing is not None:
            return

        profile = self.session.get(ProfileRecord, profile_id)
        if profile is None:
            raise KeyError(profile_id)

        base_records = self.session.scalars(
            select(ScoreVariableRecord)
            .where(
                ScoreVariableRecord.profile_id == profile_id,
                ScoreVariableRecord.context == "general",
            )
            .order_by(ScoreVariableRecord.id)
        ).all()
        if not base_records:
            for variable in seed_variables():
                base_records.append(
                    ScoreVariableRecord(
                        profile_id=profile_id,
                        key=variable.key,
                        label=variable.label,
                        category=variable.category,
                        calculated_value=variable.calculated_value,
                        manual_adjustment=variable.manual_adjustment,
                        confidence=variable.confidence,
                        context="general",
                        evidence_count=variable.evidence_count,
                        updated_at=variable.updated_at,
                    )
                )

        now = datetime.now(UTC)
        for record in base_records:
            self.session.add(
                ScoreVariableRecord(
                    profile_id=profile_id,
                    key=record.key,
                    label=record.label,
                    category=record.category,
                    calculated_value=record.calculated_value,
                    manual_adjustment=0,
                    confidence=max(0.1, record.confidence * 0.75),
                    context=context,
                    evidence_count=0,
                    updated_at=now,
                )
            )
        profile.updated_at = now
        self.add_audit_event(
            "context.created",
            "profile_context",
            context,
            {"profile_id": profile_id, "source_context": "general"},
        )
        self.session.commit()

    def add_preference(self, profile_id: str, preference: Preference) -> Preference:
        profile = self.session.get(ProfileRecord, profile_id)
        if profile is None:
            raise KeyError(profile_id)
        self.session.add(evidence_to_record(preference.evidence))
        self.session.add(preference_to_record(profile_id, preference))
        profile.updated_at = datetime.now(UTC)
        self.add_audit_event(
            "preference.created",
            "preference",
            str(preference.id),
            {"status": preference.status.value, "affected_variables": preference.affected_variables},
        )
        self.session.commit()
        return preference

    def list_preferences(self, profile_id: str) -> list[Preference]:
        records = self.session.scalars(
            select(PreferenceRecord)
            .where(PreferenceRecord.profile_id == profile_id)
            .options(selectinload(PreferenceRecord.evidence))
            .order_by(PreferenceRecord.created_at.desc())
        ).all()
        return [preference_from_record(record) for record in records]

    def list_preferences_for_context(self, profile_id: str, context: str) -> list[Preference]:
        records = self.session.scalars(
            select(PreferenceRecord)
            .join(EvidenceRecord)
            .where(
                PreferenceRecord.profile_id == profile_id,
                EvidenceRecord.context == context,
            )
            .options(selectinload(PreferenceRecord.evidence))
            .order_by(PreferenceRecord.created_at.desc())
        ).all()
        return [preference_from_record(record) for record in records]

    def update_preference_status(
        self, profile_id: str, preference_id: UUID, status: PreferenceStatus
    ) -> Preference:
        record = self.session.scalar(
            select(PreferenceRecord)
            .where(
                PreferenceRecord.profile_id == profile_id,
                PreferenceRecord.id == str(preference_id),
            )
            .options(selectinload(PreferenceRecord.evidence))
        )
        if record is None:
            raise KeyError(str(preference_id))
        record.status = status.value
        profile = self.session.get(ProfileRecord, profile_id)
        if profile is not None:
            profile.updated_at = datetime.now(UTC)
        self.add_audit_event(
            "preference.status_updated",
            "preference",
            str(preference_id),
            {"status": status.value},
        )
        self.session.commit()
        self.session.refresh(record)
        return preference_from_record(record)

    def get_preference(self, profile_id: str, preference_id: UUID) -> Preference:
        record = self.session.scalar(
            select(PreferenceRecord)
            .where(
                PreferenceRecord.profile_id == profile_id,
                PreferenceRecord.id == str(preference_id),
            )
            .options(selectinload(PreferenceRecord.evidence))
        )
        if record is None:
            raise KeyError(str(preference_id))
        return preference_from_record(record)

    def delete_preference(self, profile_id: str, preference_id: UUID) -> None:
        record = self.session.scalar(
            select(PreferenceRecord).where(
                PreferenceRecord.profile_id == profile_id,
                PreferenceRecord.id == str(preference_id),
            )
        )
        if record is None:
            raise KeyError(str(preference_id))
        evidence_id = record.evidence_id
        self.session.delete(record)
        evidence = self.session.get(EvidenceRecord, evidence_id)
        if evidence is not None:
            self.session.delete(evidence)
        profile = self.session.get(ProfileRecord, profile_id)
        if profile is not None:
            profile.updated_at = datetime.now(UTC)
        self.add_audit_event("preference.deleted", "preference", str(preference_id), {})
        self.session.commit()

    def update_variable(self, profile_id: str, variable: ScoreVariable, evidence: Evidence) -> None:
        self.ensure_context_variables(profile_id, variable.context)
        record = self.session.scalar(
            select(ScoreVariableRecord).where(
                ScoreVariableRecord.profile_id == profile_id,
                ScoreVariableRecord.key == variable.key,
                ScoreVariableRecord.context == variable.context,
            )
        )
        if record is None:
            raise KeyError(variable.key)
        record.manual_adjustment = variable.manual_adjustment
        record.updated_at = variable.updated_at
        profile = self.session.get(ProfileRecord, profile_id)
        if profile is not None:
            profile.updated_at = datetime.now(UTC)
        self.session.add(evidence_to_record(evidence))
        self.add_audit_event(
            "score.manual_override",
            "score_variable",
            f"{variable.context}:{variable.key}",
            {
                "context": variable.context,
                "manual_adjustment": variable.manual_adjustment,
                "reason": evidence.summary,
            },
        )
        self.session.commit()

    def apply_score_proposal(
        self, profile_id: str, proposal: ScoreProposal, reason: str
    ) -> list[ScoreVariable]:
        if proposal.status != "pending_review":
            raise ValueError("Score proposal is not pending review")

        updated_variables: list[ScoreVariable] = []
        for context in {item.context for item in proposal.items}:
            self.ensure_context_variables(profile_id, context)

        for item in proposal.items:
            record = self.session.scalar(
                select(ScoreVariableRecord).where(
                    ScoreVariableRecord.profile_id == profile_id,
                    ScoreVariableRecord.key == item.variable_key,
                    ScoreVariableRecord.context == item.context,
                )
            )
            if record is None:
                continue
            record.calculated_value = max(0, min(1000, record.calculated_value + item.delta))
            record.evidence_count += 1
            record.confidence = min(1, record.confidence + 0.03)
            record.updated_at = datetime.now(UTC)
            updated_variables.append(score_from_record(record))

        profile = self.session.get(ProfileRecord, profile_id)
        if profile is not None:
            profile.updated_at = datetime.now(UTC)

        self.add_audit_event(
            "score.proposal_applied",
            "preference",
            str(proposal.preference_id),
            {
                "reason": reason,
                "items": [item.model_dump() for item in proposal.items],
            },
        )
        self.session.commit()
        return updated_variables

    def add_comparison(self, comparison: ComparisonResult) -> ComparisonResult:
        record = ComparisonRecord(
            id=str(comparison.id),
            modification_score=comparison.modification_score,
            adequacy_score=comparison.adequacy_score,
            changed_words=comparison.changed_words,
            original_words=comparison.original_words,
            revised_words=comparison.revised_words,
            summary=comparison.summary,
            created_at=comparison.created_at,
        )
        self.session.add(record)
        self.add_audit_event("comparison.created", "comparison", str(comparison.id), {})
        self.session.commit()
        return comparison

    def get_comparison(self, comparison_id: UUID) -> ComparisonResult:
        record = self.session.get(ComparisonRecord, str(comparison_id))
        if record is None:
            raise KeyError(str(comparison_id))
        return comparison_from_record(record)

    def list_audit_events(self, limit: int = 50) -> list[AuditEvent]:
        records = self.session.scalars(
            select(AuditEventRecord)
            .order_by(AuditEventRecord.created_at.desc(), AuditEventRecord.id.desc())
            .limit(limit)
        ).all()
        return [audit_event_from_record(record) for record in records]

    def profile_statistics(self, profile_id: str, context: str) -> ProfileStatistics:
        variables = self.get_context_variables(profile_id, context)
        preferences = self.list_preferences_for_context(profile_id, context)
        accepted = [item for item in preferences if item.status == PreferenceStatus.accepted]
        average_confidence = (
            sum(variable.confidence for variable in variables) / len(variables) if variables else 0
        )
        low_confidence = [variable.key for variable in variables if variable.confidence < 0.4]
        return ProfileStatistics(
            profile_id=profile_id,
            context=context,
            variable_count=len(variables),
            preference_count=len(preferences),
            accepted_preference_count=len(accepted),
            average_confidence=round(average_confidence, 4),
            coverage=round(min(1, len(accepted) / max(1, len(variables))), 4),
            low_confidence_variables=low_confidence,
        )

    def contradictions(self, profile_id: str, context: str) -> list[Contradiction]:
        preferences = self.list_preferences_for_context(profile_id, context)
        result: list[Contradiction] = []
        variable_keys = sorted({key for item in preferences for key in item.affected_variables})
        for key in variable_keys:
            accepted_count = sum(
                1
                for preference in preferences
                if key in preference.affected_variables and preference.status == PreferenceStatus.accepted
            )
            rejected_count = sum(
                1
                for preference in preferences
                if key in preference.affected_variables and preference.status == PreferenceStatus.rejected
            )
            if accepted_count and rejected_count:
                result.append(
                    Contradiction(
                        variable_key=key,
                        accepted_count=accepted_count,
                        rejected_count=rejected_count,
                        note="Hay senales aceptadas y rechazadas para la misma variable.",
                    )
                )
        return result

    def add_audit_event(
        self, event_type: str, entity_type: str, entity_id: str, payload: dict
    ) -> None:
        self.session.add(
            AuditEventRecord(
                event_type=event_type,
                entity_type=entity_type,
                entity_id=entity_id,
                payload=payload,
                created_at=datetime.now(UTC),
            )
        )
