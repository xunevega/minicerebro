from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.models import (
    AuditEvent,
    ComparisonResult,
    FeedbackDecisionInput,
    FeedbackProposal,
    FeedbackProposalItem,
    FeedbackStatus,
    GeneratedText,
    Evidence,
    EvidenceType,
    KnowledgeCard,
    KnowledgeCandidateVersionCreate,
    KnowledgeClaim,
    KnowledgeClaimEvidenceLink,
    KnowledgeEvidenceItem,
    KnowledgeExtractionRun,
    KnowledgeExtractionRunCreate,
    KnowledgeIndexEntry,
    KnowledgeIndexEntryCreate,
    KnowledgeIngestionBatch,
    KnowledgeIngestionBatchExport,
    KnowledgeIngestionPolicy,
    KnowledgeIngestionReadiness,
    KnowledgeNode,
    KnowledgeNodeRelation,
    KnowledgeObjectRevision,
    KnowledgePublicationPolicy,
    KnowledgePublicationCreate,
    KnowledgePublicationReadiness,
    KnowledgeProposal,
    KnowledgeProposalCreate,
    KnowledgeProposalDecision,
    KnowledgeQueryContract,
    KnowledgeQueryInput,
    KnowledgeQueryHistoryItem,
    KnowledgeQueryInterpretation,
    KnowledgeQueryResult,
    KnowledgeQuerySummary,
    KnowledgeRelation,
    KnowledgeSegment,
    KnowledgeSegmentCreate,
    KnowledgeSource,
    KnowledgeSourceCreate,
    KnowledgeSourceEdition,
    KnowledgeSourceEditionCreate,
    KnowledgeSourceIngestionStatus,
    KnowledgeVersion,
    KnowledgeVersioningPolicy,
    Preference,
    PreferenceStatus,
    Profile,
    ProfileKnowledgeCard,
    ProfileKnowledgeCardInput,
    ProfileKnowledgeCardScoreProposal,
    ProfileKnowledgeCardScoreProposalItem,
    ProfileStatistics,
    ScoreProposal,
    ScoreVariable,
    Contradiction,
)
from app.core.seeds import seed_variables
from app.core.text import canonical_text, clamp_score
from app.db.models import (
    AuditEventRecord,
    ComparisonRecord,
    EvidenceRecord,
    FeedbackProposalRecord,
    GeneratedTextRecord,
    KnowledgeCardRecord,
    KnowledgeClaimEvidenceLinkRecord,
    KnowledgeClaimRecord,
    KnowledgeClaimRevisionRecord,
    KnowledgeEvidenceItemRecord,
    KnowledgeEvidenceRevisionRecord,
    KnowledgeExtractionRunRecord,
    KnowledgeIndexEntryRecord,
    KnowledgeIngestionBatchRecord,
    KnowledgeNodeRecord,
    KnowledgeNodeRelationRecord,
    KnowledgeObjectRevisionRecord,
    KnowledgeProposalRecord,
    KnowledgeRelationRecord,
    KnowledgeSegmentRecord,
    KnowledgeSourceRecord,
    KnowledgeSourceEditionRecord,
    KnowledgeVersionRecord,
    KnowledgeVersionSnapshotRecord,
    PreferenceRecord,
    ProfileKnowledgeCardRecord,
    ProfileRecord,
    ScoreVariableRecord,
)
from app.knowledge.service import (
    evaluate_ingestion_readiness,
    evaluate_publication_readiness,
    export_ingestion_batch,
    ingestion_policy,
    interpret_knowledge_query as build_knowledge_query_interpretation,
    publication_policy,
    query_contract,
    query_knowledge,
    resolve_knowledge_version,
    versioning_policy,
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


def profile_knowledge_card_from_record(record: ProfileKnowledgeCardRecord) -> ProfileKnowledgeCard:
    return ProfileKnowledgeCard(
        id=UUID(record.id),
        profile_id=record.profile_id,
        card_id=record.card_id,
        knowledge_version=record.knowledge_version,
        stance=record.stance,
        user_score=record.user_score,
        feedback=record.feedback,
        maintained_elements=record.maintained_elements,
        change_requests=record.change_requests,
        notes=record.notes,
        created_at=record.created_at,
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


def knowledge_query_history_from_record(record: AuditEventRecord) -> KnowledgeQueryHistoryItem:
    card_count = int(record.payload.get("card_count", 0))
    return KnowledgeQueryHistoryItem(
        event_id=record.id,
        version=record.entity_id,
        has_results=card_count > 0,
        query_length=int(record.payload.get("query_length", 0)),
        limit=int(record.payload.get("limit", 0)),
        card_count=card_count,
        claim_count=int(record.payload.get("claim_count", 0)),
        evidence_count=int(record.payload.get("evidence_count", 0)),
        pending_validation_count=int(record.payload.get("pending_validation_count", 0)),
        created_at=record.created_at,
    )


def feedback_from_record(record: FeedbackProposalRecord) -> FeedbackProposal:
    return FeedbackProposal(
        id=UUID(record.id),
        comparison_id=UUID(record.comparison_id),
        status=FeedbackStatus(record.status),
        context=record.context,
        items=[FeedbackProposalItem(**item) for item in record.items],
        rationale=record.rationale,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def feedback_to_record(profile_id: str, proposal: FeedbackProposal) -> FeedbackProposalRecord:
    return FeedbackProposalRecord(
        id=str(proposal.id),
        comparison_id=str(proposal.comparison_id),
        profile_id=profile_id,
        status=proposal.status.value,
        context=proposal.context,
        items=[item.model_dump() for item in proposal.items],
        rationale=proposal.rationale,
        created_at=proposal.created_at,
        updated_at=proposal.updated_at,
    )


def generated_text_from_record(record: GeneratedTextRecord) -> GeneratedText:
    return GeneratedText(
        id=UUID(record.id),
        profile_id=record.profile_id,
        context=record.context,
        action=record.action,
        input_text=record.input_text,
        output_text=record.output_text,
        provider=record.provider,
        used_profile_variables=record.used_profile_variables,
        learning_applied=record.learning_applied,
        created_at=record.created_at,
    )


def generated_text_to_record(text: GeneratedText) -> GeneratedTextRecord:
    return GeneratedTextRecord(
        id=str(text.id),
        profile_id=text.profile_id,
        context=text.context,
        action=text.action,
        input_text=text.input_text,
        output_text=text.output_text,
        provider=text.provider,
        used_profile_variables=text.used_profile_variables,
        learning_applied=text.learning_applied,
        created_at=text.created_at,
    )


def knowledge_source_edition_from_record(record: KnowledgeSourceEditionRecord) -> KnowledgeSourceEdition:
    return KnowledgeSourceEdition(
        id=record.id,
        source_id=record.source_id,
        title=record.title,
        edition_label=record.edition_label,
        publication_year=record.publication_year,
        publisher=record.publisher,
        isbn=record.isbn,
        language=record.language,
        format=record.format,
        access_location=record.access_location,
        rights_status=record.rights_status,
        status=record.status,
        notes=record.notes,
        created_at=record.created_at,
        updated_at=record.updated_at,
        label=record.label,
        publication_date=record.publication_date,
        location=record.location,
        acquisition_status=record.acquisition_status,
        validation_status=record.validation_status,
        rights=record.rights,
        structure=record.structure,
        locator_system=record.locator_system,
    )


def knowledge_source_from_record(
    record: KnowledgeSourceRecord,
    editions: list[KnowledgeSourceEdition] | None = None,
) -> KnowledgeSource:
    return KnowledgeSource(
        id=record.id,
        catalog_id=record.catalog_id,
        name=record.name,
        responsible=record.responsible,
        source_type=record.source_type,
        domains=record.domains,
        authority_level=record.authority_level,
        priority=record.priority,
        status=record.status,
        edition=record.edition,
        publication_date=record.publication_date,
        location=record.location,
        acquisition_status=record.acquisition_status,
        validation_status=record.validation_status,
        rights=record.rights,
        structure=record.structure,
        locator_system=record.locator_system,
        editions=editions or [],
    )


def knowledge_index_entry_from_record(
    record: KnowledgeIndexEntryRecord,
    children: list[KnowledgeIndexEntry] | None = None,
) -> KnowledgeIndexEntry:
    return KnowledgeIndexEntry(
        id=record.id,
        edition_id=record.edition_id,
        parent_id=record.parent_id,
        level=record.level,
        order=record.entry_order,
        title=record.title,
        locator=record.locator,
        page_start=record.page_start,
        page_end=record.page_end,
        status=record.status,
        created_at=record.created_at,
        updated_at=record.updated_at,
        children=children or [],
    )


def knowledge_segment_from_record(record: KnowledgeSegmentRecord) -> KnowledgeSegment:
    return KnowledgeSegment(
        id=record.id,
        index_entry_id=record.index_entry_id,
        parent_segment_id=record.parent_segment_id,
        segment_type=record.segment_type,
        title=record.title,
        text=record.text,
        order=record.segment_order,
        start_locator=record.start_locator,
        end_locator=record.end_locator,
        language=record.language,
        status=record.status,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def knowledge_extraction_run_from_record(
    record: KnowledgeExtractionRunRecord,
) -> KnowledgeExtractionRun:
    return KnowledgeExtractionRun(
        id=record.id,
        segment_id=record.segment_id,
        status=record.status,
        extractor_type=record.extractor_type,
        extractor_name=record.extractor_name,
        extractor_version=record.extractor_version,
        configuration=record.configuration,
        input_segment_revision=record.input_segment_revision,
        input_segment_hash=record.input_segment_hash,
        knowledge_version=record.knowledge_version,
        started_at=record.started_at,
        completed_at=record.completed_at,
        error_code=record.error_code,
        error_message=record.error_message,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def knowledge_proposal_from_record(record: KnowledgeProposalRecord) -> KnowledgeProposal:
    return KnowledgeProposal(
        id=record.id,
        extraction_id=record.extraction_id,
        segment_id=record.segment_id,
        proposal_type=record.proposal_type,
        status=record.status,
        title=record.title,
        payload=record.payload,
        rationale=record.rationale,
        confidence=record.confidence,
        source_locator=record.source_locator,
        created_at=record.created_at,
        updated_at=record.updated_at,
        reviewed_at=record.reviewed_at,
        reviewer=record.reviewer,
        decision_reason=record.decision_reason,
    )


def knowledge_ingestion_batch_from_record(
    record: KnowledgeIngestionBatchRecord,
) -> KnowledgeIngestionBatch:
    return KnowledgeIngestionBatch(
        id=record.id,
        source_id=record.source_id,
        source_edition_id=record.source_edition_id,
        batch_label=record.batch_label,
        scope=record.scope,
        status=record.status,
        author=record.author,
        tools=record.tools,
        model_used=record.model_used,
        configuration=record.configuration,
        progress=record.progress,
        metrics=record.metrics,
        decisions=record.decisions,
        blockers=record.blockers,
        result=record.result,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def knowledge_node_relation_from_record(record: KnowledgeNodeRelationRecord) -> KnowledgeNodeRelation:
    return KnowledgeNodeRelation(
        id=record.id,
        source_node_id=record.source_node_id,
        target_node_id=record.target_node_id,
        relation_type=record.relation_type,
        direction=record.direction,
        cardinality=record.cardinality,
        weight=record.weight,
        confidence=record.confidence,
        context=record.context,
        status=record.status,
        version=record.version,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def knowledge_relation_from_record(record: KnowledgeRelationRecord) -> KnowledgeRelation:
    return KnowledgeRelation(
        id=record.id,
        source_entity_type=record.source_entity_type,
        source_entity_id=record.source_entity_id,
        target_entity_type=record.target_entity_type,
        target_entity_id=record.target_entity_id,
        relation_type=record.relation_type,
        direction=record.direction,
        cardinality=record.cardinality,
        weight=record.weight,
        confidence=record.confidence,
        context=record.context,
        status=record.status,
        version=record.version,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def knowledge_object_revision_from_record(
    record: KnowledgeObjectRevisionRecord,
) -> KnowledgeObjectRevision:
    return KnowledgeObjectRevision(
        id=record.id,
        object_type=record.object_type,
        object_id=record.object_id,
        revision_number=record.revision_number,
        object_version=record.object_version,
        knowledge_version=record.knowledge_version,
        status=record.status,
        change_type=record.change_type,
        author=record.author,
        reason=record.reason,
        previous_revision=record.previous_revision,
        replaces_object_id=record.replaces_object_id,
        replaced_by_object_id=record.replaced_by_object_id,
        before=record.before,
        after=record.after,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def knowledge_node_from_record(
    record: KnowledgeNodeRecord,
    relations: list[KnowledgeNodeRelation] | None = None,
) -> KnowledgeNode:
    return KnowledgeNode(
        id=record.id,
        source_id=record.source_id,
        node_type=record.node_type,
        title=record.title,
        summary=record.summary,
        canonical_name=record.canonical_name,
        primary_branch=record.primary_branch,
        secondary_branch=record.secondary_branch,
        short_definition=record.short_definition,
        long_definition=record.long_definition,
        status=record.status,
        version=record.version,
        created_at=record.created_at,
        published_at=record.published_at,
        aliases=record.aliases,
        relations=relations or [],
    )


def knowledge_evidence_from_record(
    record: KnowledgeEvidenceItemRecord,
) -> KnowledgeEvidenceItem:
    return KnowledgeEvidenceItem(
        id=record.id,
        node_id=record.node_id,
        source_id=record.source_id,
        source_edition_id=record.source_edition_id,
        evidence_type=record.evidence_type,
        locator=record.locator,
        reference=record.reference,
        excerpt=record.excerpt,
        context=record.context,
        confidence=record.confidence,
        confidence_level=record.confidence_level,
        status=record.status,
        version=record.version,
        created_at=record.created_at,
        updated_at=record.updated_at,
        incorporated_by=record.incorporated_by,
        reviewed_by=record.reviewed_by,
        revision=record.revision,
    )


def knowledge_claim_evidence_link_from_record(
    record: KnowledgeClaimEvidenceLinkRecord,
) -> KnowledgeClaimEvidenceLink:
    return KnowledgeClaimEvidenceLink(
        id=record.id,
        claim_id=record.claim_id,
        evidence_id=record.evidence_id,
        role=record.role,
        created_at=record.created_at,
    )


def knowledge_claim_from_record(
    record: KnowledgeClaimRecord,
    evidence_links: list[KnowledgeClaimEvidenceLink] | None = None,
) -> KnowledgeClaim:
    return KnowledgeClaim(
        id=record.id,
        evidence_id=record.evidence_id,
        card_id=record.card_id,
        statement=record.statement,
        claim_type=record.claim_type,
        node_id=record.node_id,
        related_node_ids=record.related_node_ids,
        domain=record.domain,
        scope=record.scope,
        status=record.status,
        confidence=record.confidence,
        origin=record.origin,
        version=record.version,
        revision=record.revision,
        created_at=record.created_at,
        updated_at=record.updated_at,
        published_at=record.published_at,
        evidence_links=evidence_links or [],
    )


def knowledge_card_from_record(record: KnowledgeCardRecord) -> KnowledgeCard:
    return KnowledgeCard(
        id=record.id,
        card_type=record.card_type,
        name=record.name,
        definition=record.definition,
        confidence=record.confidence,
        version=record.version,
        payload=record.payload,
    )


def knowledge_version_from_record(
    record: KnowledgeVersionRecord, repository: "Repository"
) -> KnowledgeVersion:
    return KnowledgeVersion(
        id=record.id,
        status=record.status,
        published_at=record.published_at,
        source_count=len(repository.list_knowledge_sources(version=record.id)),
        node_count=len(repository.list_knowledge_nodes(version=record.id)),
        evidence_count=len(repository.list_knowledge_evidence(version=record.id)),
        claim_count=len(repository.list_knowledge_claims(version=record.id)),
        card_count=len(repository.list_knowledge_cards(version=record.id)),
    )


class Repository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def _knowledge_snapshot(self, version: str) -> KnowledgeVersionSnapshotRecord:
        record = self.session.get(KnowledgeVersionSnapshotRecord, version)
        if record is None:
            raise KeyError(version)
        return record

    def _build_knowledge_snapshot_record(
        self,
        version_id: str,
        status: str,
        created_at: str,
    ) -> KnowledgeVersionSnapshotRecord:
        publishable_statuses = {"validated", "published"}
        claims = self.session.scalars(
            select(KnowledgeClaimRecord)
            .where(KnowledgeClaimRecord.status.in_(publishable_statuses))
            .order_by(KnowledgeClaimRecord.id)
        ).all()
        claim_ids = [claim.id for claim in claims]
        evidence_ids = sorted({claim.evidence_id for claim in claims})
        card_ids = sorted({claim.card_id for claim in claims})
        claim_node_ids = {claim.node_id for claim in claims}
        related_node_ids = {
            node_id
            for claim in claims
            for node_id in claim.related_node_ids
        }
        evidence = self.session.scalars(
            select(KnowledgeEvidenceItemRecord)
            .where(
                KnowledgeEvidenceItemRecord.id.in_(evidence_ids),
                KnowledgeEvidenceItemRecord.status.in_(publishable_statuses),
            )
            .order_by(KnowledgeEvidenceItemRecord.id)
        ).all()
        evidence_ids = [item.id for item in evidence]
        evidence_node_ids = {item.node_id for item in evidence}
        source_ids = sorted({item.source_id for item in evidence})
        source_edition_ids = sorted({item.source_edition_id for item in evidence})
        node_ids = sorted(claim_node_ids | related_node_ids | evidence_node_ids)
        node_records = self.session.scalars(
            select(KnowledgeNodeRecord)
            .where(
                KnowledgeNodeRecord.id.in_(node_ids),
                KnowledgeNodeRecord.status.in_(publishable_statuses),
            )
            .order_by(KnowledgeNodeRecord.id)
        ).all()
        node_ids = [node.id for node in node_records]
        resolved_node_ids = set(node_ids)
        resolved_evidence_ids = set(evidence_ids)
        claims = [
            claim
            for claim in claims
            if claim.evidence_id in resolved_evidence_ids
            and claim.node_id in resolved_node_ids
            and set(claim.related_node_ids).issubset(resolved_node_ids)
        ]
        claim_ids = [claim.id for claim in claims]
        card_ids = sorted({claim.card_id for claim in claims})
        source_ids = sorted(set(source_ids) | {node.source_id for node in node_records})
        node_relation_ids = list(
            self.session.scalars(
                select(KnowledgeNodeRelationRecord.id)
                .where(
                    KnowledgeNodeRelationRecord.source_node_id.in_(node_ids),
                    KnowledgeNodeRelationRecord.target_node_id.in_(node_ids),
                    KnowledgeNodeRelationRecord.status.in_(publishable_statuses),
                )
                .order_by(KnowledgeNodeRelationRecord.id)
            ).all()
        )
        snapshot_object_ids = {
            *source_ids,
            *source_edition_ids,
            *node_ids,
            *evidence_ids,
            *claim_ids,
            *card_ids,
        }
        relations = self.session.scalars(
            select(KnowledgeRelationRecord)
            .where(KnowledgeRelationRecord.status.in_(publishable_statuses))
            .order_by(KnowledgeRelationRecord.id)
        ).all()
        relation_ids = [
            relation.id
            for relation in relations
            if relation.source_entity_id in snapshot_object_ids
            and relation.target_entity_id in snapshot_object_ids
        ]
        claim_evidence_link_ids = list(
            self.session.scalars(
                select(KnowledgeClaimEvidenceLinkRecord.id)
                .where(KnowledgeClaimEvidenceLinkRecord.claim_id.in_(claim_ids))
                .order_by(KnowledgeClaimEvidenceLinkRecord.id)
            ).all()
        )
        revision_object_ids = [
            *source_ids,
            *source_edition_ids,
            *node_ids,
            *relation_ids,
            *evidence_ids,
            *claim_ids,
            *card_ids,
        ]
        revision_ids = list(
            self.session.scalars(
                select(KnowledgeObjectRevisionRecord.id)
                .where(KnowledgeObjectRevisionRecord.object_id.in_(revision_object_ids))
                .order_by(KnowledgeObjectRevisionRecord.id)
            ).all()
        )

        return KnowledgeVersionSnapshotRecord(
            version_id=version_id,
            status=status,
            source_ids=source_ids,
            source_edition_ids=source_edition_ids,
            node_ids=node_ids,
            node_relation_ids=node_relation_ids,
            relation_ids=relation_ids,
            evidence_ids=evidence_ids,
            claim_ids=claim_ids,
            claim_evidence_link_ids=claim_evidence_link_ids,
            card_ids=card_ids,
            revision_ids=revision_ids,
            created_at=created_at,
            updated_at=created_at,
        )

    def list_knowledge_versions(self) -> list[KnowledgeVersion]:
        records = self.session.scalars(
            select(KnowledgeVersionRecord).order_by(KnowledgeVersionRecord.id)
        ).all()
        return [knowledge_version_from_record(record, self) for record in records]

    def knowledge_versioning_policy(self) -> KnowledgeVersioningPolicy:
        return versioning_policy()

    def knowledge_publication_policy(self) -> KnowledgePublicationPolicy:
        return publication_policy()

    def knowledge_ingestion_policy(self) -> KnowledgeIngestionPolicy:
        return ingestion_policy()

    def list_knowledge_ingestion_batches(
        self,
        source_id: str | None = None,
        status: str | None = None,
    ) -> list[KnowledgeIngestionBatch]:
        query = select(KnowledgeIngestionBatchRecord)
        if source_id:
            query = query.where(KnowledgeIngestionBatchRecord.source_id == source_id)
        if status:
            query = query.where(KnowledgeIngestionBatchRecord.status == status)
        records = self.session.scalars(
            query.order_by(KnowledgeIngestionBatchRecord.source_id, KnowledgeIngestionBatchRecord.id)
        ).all()
        return [knowledge_ingestion_batch_from_record(record) for record in records]

    def knowledge_ingestion_readiness(
        self,
        source_id: str,
        source_edition_id: str | None = None,
    ) -> KnowledgeIngestionReadiness:
        source_record = self.session.get(KnowledgeSourceRecord, source_id)
        if source_record is None:
            raise KeyError(source_id)
        editions = self.session.scalars(
            select(KnowledgeSourceEditionRecord).where(
                KnowledgeSourceEditionRecord.source_id == source_id
            )
        ).all()
        source = knowledge_source_from_record(
            source_record,
            [knowledge_source_edition_from_record(edition) for edition in editions],
        )
        edition_record = None
        if source_edition_id:
            edition_record = self.session.get(KnowledgeSourceEditionRecord, source_edition_id)
            if edition_record is None or edition_record.source_id != source_id:
                raise KeyError(source_edition_id)
        elif editions:
            edition_record = editions[0]
        edition = (
            knowledge_source_edition_from_record(edition_record)
            if edition_record is not None
            else None
        )
        return evaluate_ingestion_readiness(source, edition)

    def list_knowledge_source_ingestion_statuses(
        self,
        source_id: str | None = None,
    ) -> list[KnowledgeSourceIngestionStatus]:
        query = select(KnowledgeSourceRecord)
        if source_id:
            query = query.where(KnowledgeSourceRecord.id == source_id)
        records = self.session.scalars(
            query.order_by(KnowledgeSourceRecord.priority, KnowledgeSourceRecord.catalog_id)
        ).all()
        if source_id and not records:
            raise KeyError(source_id)
        return [self._knowledge_source_ingestion_status(record) for record in records]

    def _knowledge_source_ingestion_status(
        self,
        source: KnowledgeSourceRecord,
    ) -> KnowledgeSourceIngestionStatus:
        edition_count = self.session.scalar(
            select(func.count(KnowledgeSourceEditionRecord.id)).where(
                KnowledgeSourceEditionRecord.source_id == source.id
            )
        ) or 0
        index_entry_count = self.session.scalar(
            select(func.count(KnowledgeIndexEntryRecord.id))
            .select_from(KnowledgeIndexEntryRecord)
            .join(
                KnowledgeSourceEditionRecord,
                KnowledgeIndexEntryRecord.edition_id == KnowledgeSourceEditionRecord.id,
            )
            .where(KnowledgeSourceEditionRecord.source_id == source.id)
        ) or 0
        segment_count = self.session.scalar(
            select(func.count(KnowledgeSegmentRecord.id))
            .select_from(KnowledgeSegmentRecord)
            .join(
                KnowledgeIndexEntryRecord,
                KnowledgeSegmentRecord.index_entry_id == KnowledgeIndexEntryRecord.id,
            )
            .join(
                KnowledgeSourceEditionRecord,
                KnowledgeIndexEntryRecord.edition_id == KnowledgeSourceEditionRecord.id,
            )
            .where(KnowledgeSourceEditionRecord.source_id == source.id)
        ) or 0
        extraction_count = self.session.scalar(
            select(func.count(KnowledgeExtractionRunRecord.id))
            .select_from(KnowledgeExtractionRunRecord)
            .join(
                KnowledgeSegmentRecord,
                KnowledgeExtractionRunRecord.segment_id == KnowledgeSegmentRecord.id,
            )
            .join(
                KnowledgeIndexEntryRecord,
                KnowledgeSegmentRecord.index_entry_id == KnowledgeIndexEntryRecord.id,
            )
            .join(
                KnowledgeSourceEditionRecord,
                KnowledgeIndexEntryRecord.edition_id == KnowledgeSourceEditionRecord.id,
            )
            .where(KnowledgeSourceEditionRecord.source_id == source.id)
        ) or 0
        completed_extraction_count = self.session.scalar(
            select(func.count(KnowledgeExtractionRunRecord.id))
            .select_from(KnowledgeExtractionRunRecord)
            .join(
                KnowledgeSegmentRecord,
                KnowledgeExtractionRunRecord.segment_id == KnowledgeSegmentRecord.id,
            )
            .join(
                KnowledgeIndexEntryRecord,
                KnowledgeSegmentRecord.index_entry_id == KnowledgeIndexEntryRecord.id,
            )
            .join(
                KnowledgeSourceEditionRecord,
                KnowledgeIndexEntryRecord.edition_id == KnowledgeSourceEditionRecord.id,
            )
            .where(
                KnowledgeSourceEditionRecord.source_id == source.id,
                KnowledgeExtractionRunRecord.status == "completed",
            )
        ) or 0
        proposal_count = self.session.scalar(
            select(func.count(KnowledgeProposalRecord.id))
            .select_from(KnowledgeProposalRecord)
            .join(
                KnowledgeSegmentRecord,
                KnowledgeProposalRecord.segment_id == KnowledgeSegmentRecord.id,
            )
            .join(
                KnowledgeIndexEntryRecord,
                KnowledgeSegmentRecord.index_entry_id == KnowledgeIndexEntryRecord.id,
            )
            .join(
                KnowledgeSourceEditionRecord,
                KnowledgeIndexEntryRecord.edition_id == KnowledgeSourceEditionRecord.id,
            )
            .where(KnowledgeSourceEditionRecord.source_id == source.id)
        ) or 0
        reviewed_proposal_count = self.session.scalar(
            select(func.count(KnowledgeProposalRecord.id))
            .select_from(KnowledgeProposalRecord)
            .join(
                KnowledgeSegmentRecord,
                KnowledgeProposalRecord.segment_id == KnowledgeSegmentRecord.id,
            )
            .join(
                KnowledgeIndexEntryRecord,
                KnowledgeSegmentRecord.index_entry_id == KnowledgeIndexEntryRecord.id,
            )
            .join(
                KnowledgeSourceEditionRecord,
                KnowledgeIndexEntryRecord.edition_id == KnowledgeSourceEditionRecord.id,
            )
            .where(
                KnowledgeSourceEditionRecord.source_id == source.id,
                KnowledgeProposalRecord.status.in_(["approved", "rejected"]),
            )
        ) or 0
        node_count = self.session.scalar(
            select(func.count(KnowledgeNodeRecord.id)).where(KnowledgeNodeRecord.source_id == source.id)
        ) or 0
        evidence_count = self.session.scalar(
            select(func.count(KnowledgeEvidenceItemRecord.id)).where(
                KnowledgeEvidenceItemRecord.source_id == source.id
            )
        ) or 0
        claim_count = self.session.scalar(
            select(func.count(KnowledgeClaimRecord.id))
            .select_from(KnowledgeClaimRecord)
            .join(
                KnowledgeEvidenceItemRecord,
                KnowledgeClaimRecord.evidence_id == KnowledgeEvidenceItemRecord.id,
            )
            .where(KnowledgeEvidenceItemRecord.source_id == source.id)
        ) or 0
        card_count = self.session.scalar(
            select(func.count(func.distinct(KnowledgeClaimRecord.card_id)))
            .select_from(KnowledgeClaimRecord)
            .join(
                KnowledgeEvidenceItemRecord,
                KnowledgeClaimRecord.evidence_id == KnowledgeEvidenceItemRecord.id,
            )
            .where(KnowledgeEvidenceItemRecord.source_id == source.id)
        ) or 0
        published_object_count = self.session.scalar(
            select(func.count(KnowledgeEvidenceItemRecord.id)).where(
                KnowledgeEvidenceItemRecord.source_id == source.id,
                KnowledgeEvidenceItemRecord.status == "published",
            )
        ) or 0
        counts = {
            "editions": edition_count,
            "index_entries": index_entry_count,
            "segments": segment_count,
            "extractions": extraction_count,
            "completed_extractions": completed_extraction_count,
            "proposals": proposal_count,
            "reviewed_proposals": reviewed_proposal_count,
            "nodes": node_count,
            "evidence": evidence_count,
            "claims": claim_count,
            "cards": card_count,
            "published_evidence": published_object_count,
        }
        has_materialized_knowledge = node_count > 0 and evidence_count > 0 and claim_count > 0
        is_published = published_object_count > 0
        is_ingested = (
            segment_count > 0
            and completed_extraction_count > 0
            and proposal_count > 0
            and has_materialized_knowledge
        )
        current_phase = "registered"
        if edition_count > 0:
            current_phase = "edition_registered"
        if index_entry_count > 0:
            current_phase = "indexed"
        if segment_count > 0:
            current_phase = "segmented"
        if completed_extraction_count > 0:
            current_phase = "extracted"
        if proposal_count > 0:
            current_phase = "proposed"
        if reviewed_proposal_count > 0:
            current_phase = "reviewed"
        if is_ingested:
            current_phase = "validated"
        if is_published and is_ingested:
            current_phase = "published"
        blockers = []
        if edition_count == 0:
            blockers.append("missing_edition")
        if index_entry_count == 0:
            blockers.append("missing_index")
        if segment_count == 0:
            blockers.append("missing_segments")
        if completed_extraction_count == 0:
            blockers.append("missing_completed_extraction")
        if proposal_count == 0:
            blockers.append("missing_proposals")
        if not has_materialized_knowledge:
            blockers.append("missing_materialized_knowledge")
        if not is_published:
            blockers.append("missing_publication")
        return KnowledgeSourceIngestionStatus(
            source_id=source.id,
            source_name=source.name,
            current_phase=current_phase,
            is_registered=True,
            has_edition=edition_count > 0,
            has_index=index_entry_count > 0,
            has_segments=segment_count > 0,
            has_extractions=extraction_count > 0,
            has_proposals=proposal_count > 0,
            has_reviewed_proposals=reviewed_proposal_count > 0,
            has_materialized_knowledge=has_materialized_knowledge,
            is_published=is_published,
            is_ingested=is_ingested,
            counts=counts,
            blockers=blockers,
        )

    def export_knowledge_ingestion_batch(self, batch_id: str) -> KnowledgeIngestionBatchExport:
        record = self.session.get(KnowledgeIngestionBatchRecord, batch_id)
        if record is None:
            raise KeyError(batch_id)
        return export_ingestion_batch(knowledge_ingestion_batch_from_record(record))

    def knowledge_publication_readiness(self, version: str) -> KnowledgePublicationReadiness:
        record = self.session.get(KnowledgeVersionRecord, version)
        if record is None:
            raise KeyError(version)
        knowledge_version = knowledge_version_from_record(record, self)
        return evaluate_publication_readiness(
            knowledge_version,
            sources=self.list_knowledge_sources(version=version),
            nodes=self.list_knowledge_nodes(version=version),
            relations=self.list_knowledge_relations(version=version),
            evidence=self.list_knowledge_evidence(version=version),
            claims=self.list_knowledge_claims(version=version),
            cards=self.list_knowledge_cards(version=version),
        )

    def create_knowledge_candidate(
        self,
        payload: KnowledgeCandidateVersionCreate,
    ) -> KnowledgeVersion:
        if self.session.get(KnowledgeVersionRecord, payload.base_version) is None:
            raise KeyError(payload.base_version)
        self._knowledge_snapshot(payload.base_version)
        if self.session.get(KnowledgeVersionRecord, payload.id) is not None:
            raise ValueError("Knowledge version already exists")
        now = datetime.now(UTC).isoformat()
        record = KnowledgeVersionRecord(
            id=payload.id,
            status="candidate",
            published_at="not-published",
        )
        snapshot = self._build_knowledge_snapshot_record(
            version_id=payload.id,
            status="candidate",
            created_at=now,
        )
        self.session.add(record)
        self.session.add(snapshot)
        self.add_audit_event(
            "knowledge.candidate.created",
            "knowledge_version",
            payload.id,
            {
                "base_version": payload.base_version,
                "author": payload.author,
                "reason": payload.reason,
                "publication_created": False,
                "snapshot_created": True,
                "source_count": len(snapshot.source_ids),
                "node_count": len(snapshot.node_ids),
                "evidence_count": len(snapshot.evidence_ids),
                "claim_count": len(snapshot.claim_ids),
                "card_count": len(snapshot.card_ids),
            },
        )
        self.session.commit()
        return knowledge_version_from_record(record, self)

    def publish_knowledge_version(
        self,
        payload: KnowledgePublicationCreate,
    ) -> KnowledgeVersion:
        record = self.session.get(KnowledgeVersionRecord, payload.version)
        if record is None:
            raise KeyError(payload.version)
        snapshot = self._knowledge_snapshot(payload.version)
        if record.status == "published":
            raise ValueError("Knowledge version is already published")
        if record.status not in {"candidate", "validated"}:
            raise ValueError("Knowledge publication requires a candidate or validated version")
        readiness = self.knowledge_publication_readiness(payload.version)
        if not readiness.publishable:
            raise ValueError(
                "Knowledge version is not publishable: " + ", ".join(readiness.blockers)
            )
        now = datetime.now(UTC).isoformat()
        promoted = self._promote_snapshot_to_published(snapshot, payload.version, now)
        record.status = "published"
        record.published_at = now
        snapshot.status = "published"
        snapshot.updated_at = now
        self.add_audit_event(
            "knowledge.published",
            "knowledge_version",
            payload.version,
            {
                "author": payload.author,
                "reason": payload.reason,
                "base_version": payload.version,
                "snapshot_created": False,
                "snapshot_activated": True,
                "promoted": promoted,
                "source_count": len(snapshot.source_ids),
                "node_count": len(snapshot.node_ids),
                "evidence_count": len(snapshot.evidence_ids),
                "claim_count": len(snapshot.claim_ids),
                "card_count": len(snapshot.card_ids),
            },
        )
        self.session.commit()
        return knowledge_version_from_record(record, self)

    def _promote_snapshot_to_published(
        self,
        snapshot: KnowledgeVersionSnapshotRecord,
        version: str,
        published_at: str,
    ) -> dict[str, int]:
        node_count = 0
        for node in self.session.scalars(
            select(KnowledgeNodeRecord).where(KnowledgeNodeRecord.id.in_(snapshot.node_ids))
        ).all():
            node.status = "published"
            node.version = version
            node.published_at = published_at
            node_count += 1

        node_relation_count = 0
        for relation in self.session.scalars(
            select(KnowledgeNodeRelationRecord).where(
                KnowledgeNodeRelationRecord.id.in_(snapshot.node_relation_ids)
            )
        ).all():
            relation.status = "published"
            relation.version = version
            relation.updated_at = published_at
            node_relation_count += 1

        relation_count = 0
        for relation in self.session.scalars(
            select(KnowledgeRelationRecord).where(
                KnowledgeRelationRecord.id.in_(snapshot.relation_ids)
            )
        ).all():
            relation.status = "published"
            relation.version = version
            relation.updated_at = published_at
            relation_count += 1

        evidence_count = 0
        for evidence in self.session.scalars(
            select(KnowledgeEvidenceItemRecord).where(
                KnowledgeEvidenceItemRecord.id.in_(snapshot.evidence_ids)
            )
        ).all():
            evidence.status = "published"
            evidence.version = version
            evidence.updated_at = published_at
            evidence_count += 1

        claim_count = 0
        for claim in self.session.scalars(
            select(KnowledgeClaimRecord).where(KnowledgeClaimRecord.id.in_(snapshot.claim_ids))
        ).all():
            claim.status = "published"
            claim.version = version
            claim.published_at = published_at
            claim.updated_at = published_at
            claim_count += 1

        card_count = 0
        for card in self.session.scalars(
            select(KnowledgeCardRecord).where(KnowledgeCardRecord.id.in_(snapshot.card_ids))
        ).all():
            card.version = version
            card_count += 1

        revision_count = 0
        for revision in self.session.scalars(
            select(KnowledgeObjectRevisionRecord).where(
                KnowledgeObjectRevisionRecord.id.in_(snapshot.revision_ids)
            )
        ).all():
            revision.status = "published"
            revision.knowledge_version = version
            revision.updated_at = published_at
            revision_count += 1

        claim_revision_count = 0
        for revision in self.session.scalars(
            select(KnowledgeClaimRevisionRecord).where(
                KnowledgeClaimRevisionRecord.claim_id.in_(snapshot.claim_ids)
            )
        ).all():
            revision.knowledge_version = version
            claim_revision_count += 1

        return {
            "nodes": node_count,
            "node_relations": node_relation_count,
            "relations": relation_count,
            "evidence": evidence_count,
            "claims": claim_count,
            "cards": card_count,
            "object_revisions": revision_count,
            "claim_revisions": claim_revision_count,
        }

    def list_knowledge_object_revisions(
        self,
        object_type: str | None = None,
        object_id: str | None = None,
        knowledge_version: str | None = None,
    ) -> list[KnowledgeObjectRevision]:
        query = select(KnowledgeObjectRevisionRecord)
        if knowledge_version:
            snapshot = self._knowledge_snapshot(knowledge_version)
            query = query.where(KnowledgeObjectRevisionRecord.id.in_(snapshot.revision_ids))
        if object_type:
            query = query.where(KnowledgeObjectRevisionRecord.object_type == object_type)
        if object_id:
            query = query.where(KnowledgeObjectRevisionRecord.object_id == object_id)
        if knowledge_version and snapshot is None:
            query = query.where(
                KnowledgeObjectRevisionRecord.knowledge_version == knowledge_version
            )
        records = self.session.scalars(
            query.order_by(
                KnowledgeObjectRevisionRecord.object_type,
                KnowledgeObjectRevisionRecord.object_id,
                KnowledgeObjectRevisionRecord.revision_number,
            )
        ).all()
        return [knowledge_object_revision_from_record(record) for record in records]

    def list_knowledge_sources(self, version: str | None = None) -> list[KnowledgeSource]:
        query = select(KnowledgeSourceRecord)
        snapshot = self._knowledge_snapshot(version) if version else None
        if snapshot is not None:
            query = query.where(KnowledgeSourceRecord.id.in_(snapshot.source_ids))
        records = self.session.scalars(
            query.order_by(KnowledgeSourceRecord.priority, KnowledgeSourceRecord.catalog_id)
        ).all()
        edition_query = select(KnowledgeSourceEditionRecord)
        if snapshot is not None:
            edition_query = edition_query.where(
                KnowledgeSourceEditionRecord.id.in_(snapshot.source_edition_ids)
            )
        editions = self.session.scalars(edition_query.order_by(KnowledgeSourceEditionRecord.id)).all()
        editions_by_source: dict[str, list[KnowledgeSourceEdition]] = {}
        for edition in editions:
            editions_by_source.setdefault(edition.source_id, []).append(
                knowledge_source_edition_from_record(edition)
            )
        return [
            knowledge_source_from_record(record, editions_by_source.get(record.id, []))
            for record in records
        ]

    def register_knowledge_source(self, payload: KnowledgeSourceCreate) -> KnowledgeSource:
        if self.session.get(KnowledgeSourceRecord, payload.id) is not None:
            raise ValueError("Knowledge source already exists")
        catalog_match = self.session.scalars(
            select(KnowledgeSourceRecord).where(
                KnowledgeSourceRecord.catalog_id == payload.catalog_id
            )
        ).first()
        if catalog_match is not None:
            raise ValueError("Knowledge source catalog id already exists")
        record = KnowledgeSourceRecord(**payload.model_dump())
        self.session.add(record)
        self.add_audit_event(
            "knowledge.source.registered",
            "knowledge_source",
            payload.id,
            {
                "catalog_id": payload.catalog_id,
                "name": payload.name,
                "source_type": payload.source_type,
                "domains": payload.domains,
                "status": payload.status,
                "edition_created": False,
                "publishes_directly": False,
            },
        )
        self.session.commit()
        return knowledge_source_from_record(record, [])

    def list_knowledge_source_editions(self, source_id: str) -> list[KnowledgeSourceEdition]:
        if self.session.get(KnowledgeSourceRecord, source_id) is None:
            raise KeyError(source_id)
        records = self.session.scalars(
            select(KnowledgeSourceEditionRecord)
            .where(KnowledgeSourceEditionRecord.source_id == source_id)
            .order_by(KnowledgeSourceEditionRecord.id)
        ).all()
        return [knowledge_source_edition_from_record(record) for record in records]

    def get_knowledge_source_edition(self, edition_id: str) -> KnowledgeSourceEdition:
        record = self.session.get(KnowledgeSourceEditionRecord, edition_id)
        if record is None:
            raise KeyError(edition_id)
        return knowledge_source_edition_from_record(record)

    def register_knowledge_source_edition(
        self,
        source_id: str,
        payload: KnowledgeSourceEditionCreate,
    ) -> KnowledgeSourceEdition:
        if payload.source_id != source_id:
            raise ValueError("Knowledge edition source_id does not match path")
        if self.session.get(KnowledgeSourceRecord, source_id) is None:
            raise KeyError(source_id)
        if self.session.get(KnowledgeSourceEditionRecord, payload.id) is not None:
            raise ValueError("Knowledge source edition already exists")
        source_editions = self.session.scalars(
            select(KnowledgeSourceEditionRecord).where(
                KnowledgeSourceEditionRecord.source_id == source_id
            )
        ).all()
        normalized_payload = {
            "title": payload.title.strip().lower(),
            "edition_label": payload.edition_label.strip().lower(),
            "publication_year": payload.publication_year.strip().lower(),
            "publisher": payload.publisher.strip().lower(),
            "isbn": payload.isbn.strip().lower(),
        }
        for edition in source_editions:
            normalized_edition = {
                "title": edition.title.strip().lower(),
                "edition_label": edition.edition_label.strip().lower(),
                "publication_year": edition.publication_year.strip().lower(),
                "publisher": edition.publisher.strip().lower(),
                "isbn": edition.isbn.strip().lower(),
            }
            if normalized_edition == normalized_payload:
                raise ValueError("Knowledge source edition already exists")
        now = datetime.now(UTC).isoformat()
        record = KnowledgeSourceEditionRecord(
            id=payload.id,
            source_id=source_id,
            title=payload.title,
            edition_label=payload.edition_label,
            publication_year=payload.publication_year,
            publisher=payload.publisher,
            isbn=payload.isbn,
            language=payload.language,
            format=payload.format,
            access_location=payload.access_location,
            rights_status=payload.rights_status,
            status=payload.status,
            notes=payload.notes,
            created_at=now,
            updated_at=now,
            label=payload.edition_label,
            publication_date=payload.publication_year,
            location=payload.access_location,
            acquisition_status=payload.status,
            validation_status="not_validated",
            rights=payload.rights_status,
            structure=payload.structure,
            locator_system=payload.locator_system,
        )
        self.session.add(record)
        self.add_audit_event(
            "knowledge.edition.registered",
            "knowledge_source_edition",
            payload.id,
            {
                "source_id": source_id,
                "title": payload.title,
                "edition_label": payload.edition_label,
                "publication_year": payload.publication_year,
                "status": payload.status,
                "ingestion_batch_created": False,
                "index_created": False,
                "publishes_directly": False,
            },
        )
        self.session.commit()
        return knowledge_source_edition_from_record(record)

    def register_knowledge_index_entries(
        self,
        edition_id: str,
        payload: list[KnowledgeIndexEntryCreate],
    ) -> list[KnowledgeIndexEntry]:
        if self.session.get(KnowledgeSourceEditionRecord, edition_id) is None:
            raise KeyError(edition_id)
        if not payload:
            raise ValueError("Knowledge index entries cannot be empty")
        payload_ids = {entry.id for entry in payload}
        if len(payload_ids) != len(payload):
            raise ValueError("Knowledge index entry ids must be unique")
        for entry in payload:
            if entry.edition_id != edition_id:
                raise ValueError("Knowledge index entry edition_id does not match path")
            if self.session.get(KnowledgeIndexEntryRecord, entry.id) is not None:
                raise ValueError("Knowledge index entry already exists")
        existing_records = self.session.scalars(
            select(KnowledgeIndexEntryRecord).where(
                KnowledgeIndexEntryRecord.edition_id == edition_id
            )
        ).all()
        existing_ids = {record.id for record in existing_records}
        existing_parent_orders = {
            (record.parent_id, record.entry_order) for record in existing_records
        }
        payload_parent_orders: set[tuple[str | None, int]] = set()
        valid_parent_ids = existing_ids | payload_ids
        for entry in payload:
            if entry.parent_id is not None and entry.parent_id not in valid_parent_ids:
                raise ValueError("Knowledge index entry parent not found")
            parent_order = (entry.parent_id, entry.order)
            if parent_order in existing_parent_orders or parent_order in payload_parent_orders:
                raise ValueError("Knowledge index entry order already exists for parent")
            payload_parent_orders.add(parent_order)
        now = datetime.now(UTC).isoformat()
        records = [
            KnowledgeIndexEntryRecord(
                id=entry.id,
                edition_id=edition_id,
                parent_id=entry.parent_id,
                level=entry.level,
                entry_order=entry.order,
                title=entry.title,
                locator=entry.locator,
                page_start=entry.page_start,
                page_end=entry.page_end,
                status=entry.status,
                created_at=now,
                updated_at=now,
            )
            for entry in payload
        ]
        self.session.add_all(records)
        self.add_audit_event(
            "knowledge.index.registered",
            "knowledge_source_edition",
            edition_id,
            {
                "entry_count": len(records),
                "root_count": sum(1 for record in records if record.parent_id is None),
                "creates_knowledge": False,
                "nodes_created": False,
                "segmentation_started": False,
                "ingestion_batch_created": False,
                "publishes_directly": False,
            },
        )
        self.session.commit()
        return [knowledge_index_entry_from_record(record) for record in records]

    def list_knowledge_index_tree(self, edition_id: str) -> list[KnowledgeIndexEntry]:
        if self.session.get(KnowledgeSourceEditionRecord, edition_id) is None:
            raise KeyError(edition_id)
        records = self.session.scalars(
            select(KnowledgeIndexEntryRecord)
            .where(KnowledgeIndexEntryRecord.edition_id == edition_id)
            .order_by(
                KnowledgeIndexEntryRecord.level,
                KnowledgeIndexEntryRecord.parent_id,
                KnowledgeIndexEntryRecord.entry_order,
                KnowledgeIndexEntryRecord.id,
            )
        ).all()
        entries_by_id = {
            record.id: knowledge_index_entry_from_record(record) for record in records
        }
        roots: list[KnowledgeIndexEntry] = []
        for record in records:
            entry = entries_by_id[record.id]
            if record.parent_id is None:
                roots.append(entry)
                continue
            parent = entries_by_id.get(record.parent_id)
            if parent is not None:
                parent.children.append(entry)
        return sorted(roots, key=lambda entry: entry.order)

    def get_knowledge_index_entry(self, entry_id: str) -> KnowledgeIndexEntry:
        record = self.session.get(KnowledgeIndexEntryRecord, entry_id)
        if record is None:
            raise KeyError(entry_id)
        return knowledge_index_entry_from_record(record)

    def register_knowledge_segments(
        self,
        entry_id: str,
        payload: list[KnowledgeSegmentCreate],
    ) -> list[KnowledgeSegment]:
        if self.session.get(KnowledgeIndexEntryRecord, entry_id) is None:
            raise KeyError(entry_id)
        if not payload:
            raise ValueError("Knowledge segments cannot be empty")
        payload_ids = {segment.id for segment in payload}
        if len(payload_ids) != len(payload):
            raise ValueError("Knowledge segment ids must be unique")
        for segment in payload:
            if segment.index_entry_id != entry_id:
                raise ValueError("Knowledge segment index_entry_id does not match path")
            if self.session.get(KnowledgeSegmentRecord, segment.id) is not None:
                raise ValueError("Knowledge segment already exists")
        existing_records = self.session.scalars(
            select(KnowledgeSegmentRecord).where(
                KnowledgeSegmentRecord.index_entry_id == entry_id
            )
        ).all()
        existing_ids = {record.id for record in existing_records}
        existing_parent_orders = {
            (record.parent_segment_id, record.segment_order) for record in existing_records
        }
        payload_parent_orders: set[tuple[str | None, int]] = set()
        valid_parent_ids = existing_ids | payload_ids
        for segment in payload:
            if segment.parent_segment_id is not None and segment.parent_segment_id not in valid_parent_ids:
                raise ValueError("Knowledge segment parent not found")
            parent_order = (segment.parent_segment_id, segment.order)
            if parent_order in existing_parent_orders or parent_order in payload_parent_orders:
                raise ValueError("Knowledge segment order already exists for parent")
            payload_parent_orders.add(parent_order)
        now = datetime.now(UTC).isoformat()
        records = [
            KnowledgeSegmentRecord(
                id=segment.id,
                index_entry_id=entry_id,
                parent_segment_id=segment.parent_segment_id,
                segment_type=segment.segment_type,
                title=segment.title,
                text=segment.text,
                segment_order=segment.order,
                start_locator=segment.start_locator,
                end_locator=segment.end_locator,
                language=segment.language,
                status=segment.status,
                created_at=now,
                updated_at=now,
            )
            for segment in payload
        ]
        self.session.add_all(records)
        self.add_audit_event(
            "knowledge.segment.registered",
            "knowledge_index_entry",
            entry_id,
            {
                "segment_count": len(records),
                "index_entry_id": entry_id,
                "interprets_text": False,
                "summarizes_text": False,
                "embeddings_created": False,
                "nodes_created": False,
                "knowledge_created": False,
            },
        )
        self.session.commit()
        return [knowledge_segment_from_record(record) for record in records]

    def list_knowledge_segments(self, entry_id: str) -> list[KnowledgeSegment]:
        if self.session.get(KnowledgeIndexEntryRecord, entry_id) is None:
            raise KeyError(entry_id)
        records = self.session.scalars(
            select(KnowledgeSegmentRecord)
            .where(KnowledgeSegmentRecord.index_entry_id == entry_id)
            .order_by(
                KnowledgeSegmentRecord.parent_segment_id,
                KnowledgeSegmentRecord.segment_order,
                KnowledgeSegmentRecord.id,
            )
        ).all()
        return [knowledge_segment_from_record(record) for record in records]

    def get_knowledge_segment(self, segment_id: str) -> KnowledgeSegment:
        record = self.session.get(KnowledgeSegmentRecord, segment_id)
        if record is None:
            raise KeyError(segment_id)
        return knowledge_segment_from_record(record)

    def register_knowledge_extraction_run(
        self,
        segment_id: str,
        payload: KnowledgeExtractionRunCreate,
    ) -> KnowledgeExtractionRun:
        segment = self.session.get(KnowledgeSegmentRecord, segment_id)
        if segment is None:
            raise KeyError(segment_id)
        if payload.knowledge_version is not None and self.session.get(
            KnowledgeVersionRecord, payload.knowledge_version
        ) is None:
            raise KeyError(payload.knowledge_version)
        started_at = datetime.now(UTC).isoformat()
        completed_at = datetime.now(UTC).isoformat()
        now = completed_at
        error_code = payload.error_code
        error_message = payload.error_message
        if payload.status == "failed":
            error_code = error_code or "extraction_failed"
            error_message = error_message or "Extraction failed before producing proposals."
        elif payload.status in {"completed", "cancelled"}:
            error_code = None
            error_message = None
        record = KnowledgeExtractionRunRecord(
            id=f"ext-{uuid4()}",
            segment_id=segment_id,
            status=payload.status,
            extractor_type=payload.extractor_type,
            extractor_name=payload.extractor_name,
            extractor_version=payload.extractor_version,
            configuration=payload.configuration,
            input_segment_revision=1,
            input_segment_hash=sha256(segment.text.encode("utf-8")).hexdigest(),
            knowledge_version=payload.knowledge_version,
            started_at=started_at,
            completed_at=completed_at,
            error_code=error_code,
            error_message=error_message,
            created_at=now,
            updated_at=now,
        )
        self.session.add(record)
        self.add_audit_event(
            "knowledge.extraction.registered",
            "knowledge_extraction_run",
            record.id,
            {
                "segment_id": segment_id,
                "status": "pending",
                "extractor_type": payload.extractor_type,
                "extractor_name": payload.extractor_name,
                "extractor_version": payload.extractor_version,
                "proposals_created": False,
                "knowledge_created": False,
            },
        )
        self.add_audit_event(
            "knowledge.extraction.started",
            "knowledge_extraction_run",
            record.id,
            {"segment_id": segment_id, "status": "running"},
        )
        terminal_event = {
            "completed": "knowledge.extraction.completed",
            "failed": "knowledge.extraction.failed",
            "cancelled": "knowledge.extraction.cancelled",
        }[payload.status]
        self.add_audit_event(
            terminal_event,
            "knowledge_extraction_run",
            record.id,
            {
                "segment_id": segment_id,
                "status": payload.status,
                "error_code": error_code,
                "proposals_created": False,
                "nodes_created": False,
                "evidence_created": False,
                "claims_created": False,
                "cards_created": False,
                "published": False,
                "embeddings_created": False,
            },
        )
        self.session.commit()
        return knowledge_extraction_run_from_record(record)

    def list_knowledge_extraction_runs(self, segment_id: str) -> list[KnowledgeExtractionRun]:
        if self.session.get(KnowledgeSegmentRecord, segment_id) is None:
            raise KeyError(segment_id)
        records = self.session.scalars(
            select(KnowledgeExtractionRunRecord)
            .where(KnowledgeExtractionRunRecord.segment_id == segment_id)
            .order_by(KnowledgeExtractionRunRecord.created_at, KnowledgeExtractionRunRecord.id)
        ).all()
        return [knowledge_extraction_run_from_record(record) for record in records]

    def get_knowledge_extraction_run(self, extraction_id: str) -> KnowledgeExtractionRun:
        record = self.session.get(KnowledgeExtractionRunRecord, extraction_id)
        if record is None:
            raise KeyError(extraction_id)
        return knowledge_extraction_run_from_record(record)

    def register_knowledge_proposals(
        self,
        extraction_id: str,
        payload: list[KnowledgeProposalCreate],
    ) -> list[KnowledgeProposal]:
        extraction = self.session.get(KnowledgeExtractionRunRecord, extraction_id)
        if extraction is None:
            raise KeyError(extraction_id)
        if extraction.status != "completed":
            raise ValueError("Knowledge proposals require a completed extraction")
        if not payload:
            raise ValueError("Knowledge proposals cannot be empty")
        now = datetime.now(UTC).isoformat()
        records = [
            KnowledgeProposalRecord(
                id=f"prop-{uuid4()}",
                extraction_id=extraction_id,
                segment_id=extraction.segment_id,
                proposal_type=proposal.proposal_type,
                status="proposed",
                title=proposal.title,
                payload=proposal.payload,
                rationale=proposal.rationale,
                confidence=proposal.confidence,
                source_locator=proposal.source_locator,
                created_at=now,
                updated_at=now,
                reviewed_at=None,
                reviewer=None,
                decision_reason=None,
            )
            for proposal in payload
        ]
        self.session.add_all(records)
        self.add_audit_event(
            "knowledge.proposal.registered",
            "knowledge_extraction_run",
            extraction_id,
            {
                "proposal_count": len(records),
                "segment_id": extraction.segment_id,
                "proposal_types": [record.proposal_type for record in records],
                "status": "proposed",
                "nodes_created": False,
                "evidence_created": False,
                "claims_created": False,
                "cards_created": False,
                "published": False,
                "stable_knowledge_created": False,
            },
        )
        self.session.commit()
        return [knowledge_proposal_from_record(record) for record in records]

    def list_knowledge_proposals(self, extraction_id: str) -> list[KnowledgeProposal]:
        if self.session.get(KnowledgeExtractionRunRecord, extraction_id) is None:
            raise KeyError(extraction_id)
        records = self.session.scalars(
            select(KnowledgeProposalRecord)
            .where(KnowledgeProposalRecord.extraction_id == extraction_id)
            .order_by(KnowledgeProposalRecord.created_at, KnowledgeProposalRecord.id)
        ).all()
        return [knowledge_proposal_from_record(record) for record in records]

    def get_knowledge_proposal(self, proposal_id: str) -> KnowledgeProposal:
        record = self.session.get(KnowledgeProposalRecord, proposal_id)
        if record is None:
            raise KeyError(proposal_id)
        return knowledge_proposal_from_record(record)

    def approve_knowledge_proposal(
        self,
        proposal_id: str,
        decision: KnowledgeProposalDecision,
    ) -> KnowledgeProposal:
        record = self.session.get(KnowledgeProposalRecord, proposal_id)
        if record is None:
            raise KeyError(proposal_id)
        if record.status != "proposed":
            raise ValueError("Knowledge proposal is already decided")
        target_type, target_id = self._create_object_from_proposal(record, decision)
        now = datetime.now(UTC).isoformat()
        record.status = "approved"
        record.reviewed_at = now
        record.updated_at = now
        record.reviewer = decision.reviewer
        record.decision_reason = decision.reason
        self.add_audit_event(
            "knowledge.proposal.approved",
            "knowledge_proposal",
            proposal_id,
            {
                "proposal_type": record.proposal_type,
                "target_type": target_type,
                "target_id": target_id,
                "reviewer": decision.reviewer,
                "reason": decision.reason,
                "published": False,
                "candidate_version_created": False,
            },
        )
        self.session.commit()
        return knowledge_proposal_from_record(record)

    def reject_knowledge_proposal(
        self,
        proposal_id: str,
        decision: KnowledgeProposalDecision,
    ) -> KnowledgeProposal:
        record = self.session.get(KnowledgeProposalRecord, proposal_id)
        if record is None:
            raise KeyError(proposal_id)
        if record.status != "proposed":
            raise ValueError("Knowledge proposal is already decided")
        now = datetime.now(UTC).isoformat()
        record.status = "rejected"
        record.reviewed_at = now
        record.updated_at = now
        record.reviewer = decision.reviewer
        record.decision_reason = decision.reason
        self.add_audit_event(
            "knowledge.proposal.rejected",
            "knowledge_proposal",
            proposal_id,
            {
                "proposal_type": record.proposal_type,
                "reviewer": decision.reviewer,
                "reason": decision.reason,
                "stable_knowledge_created": False,
                "published": False,
            },
        )
        self.session.commit()
        return knowledge_proposal_from_record(record)

    def _create_object_from_proposal(
        self,
        proposal: KnowledgeProposalRecord,
        decision: KnowledgeProposalDecision,
    ) -> tuple[str, str]:
        if proposal.proposal_type == "node":
            return "node", self._create_node_from_proposal(proposal, decision)
        if proposal.proposal_type == "evidence":
            return "evidence", self._create_evidence_from_proposal(proposal, decision)
        if proposal.proposal_type == "claim":
            return "claim", self._create_claim_from_proposal(proposal, decision)
        if proposal.proposal_type == "relation":
            return "relation", self._create_relation_from_proposal(proposal)
        raise ValueError(
            "Knowledge proposal type requires a versioned mutation rule before approval"
        )

    def _required_payload_value(
        self,
        proposal: KnowledgeProposalRecord,
        key: str,
    ) -> str:
        value = proposal.payload.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"Knowledge proposal payload missing {key}")
        return value

    def _create_node_from_proposal(
        self,
        proposal: KnowledgeProposalRecord,
        decision: KnowledgeProposalDecision,
    ) -> str:
        node_id = self._required_payload_value(proposal, "id")
        source_id = self._required_payload_value(proposal, "source_id")
        version = proposal.payload.get("version", "knowledge-v0")
        if not isinstance(version, str):
            raise ValueError("Knowledge proposal payload missing version")
        if self.session.get(KnowledgeNodeRecord, node_id) is not None:
            raise ValueError("Knowledge node already exists")
        if self.session.get(KnowledgeSourceRecord, source_id) is None:
            raise KeyError(source_id)
        if self.session.get(KnowledgeVersionRecord, version) is None:
            raise KeyError(version)
        now = datetime.now(UTC).isoformat()
        aliases = proposal.payload.get("aliases", [])
        if not isinstance(aliases, list):
            raise ValueError("Knowledge proposal payload aliases must be a list")
        self.session.add(
            KnowledgeNodeRecord(
                id=node_id,
                source_id=source_id,
                node_type=self._required_payload_value(proposal, "node_type"),
                title=proposal.payload.get("title", proposal.title),
                summary=self._required_payload_value(proposal, "summary"),
                canonical_name=self._required_payload_value(proposal, "canonical_name"),
                primary_branch=self._required_payload_value(proposal, "primary_branch"),
                secondary_branch=self._required_payload_value(proposal, "secondary_branch"),
                short_definition=self._required_payload_value(proposal, "short_definition"),
                long_definition=self._required_payload_value(proposal, "long_definition"),
                status="validated",
                version=version,
                created_at=now,
                published_at="not-published",
                aliases=aliases,
            )
        )
        self.session.add(
            KnowledgeObjectRevisionRecord(
                id=f"{node_id}:r1",
                object_type="node",
                object_id=node_id,
                revision_number=1,
                object_version=f"{node_id}@r1",
                knowledge_version=version,
                status="validated",
                change_type="created_from_proposal",
                author=decision.reviewer,
                reason=decision.reason,
                previous_revision=None,
                replaces_object_id=None,
                replaced_by_object_id=None,
                before={},
                after=proposal.payload,
                created_at=now,
                updated_at=now,
            )
        )
        return node_id

    def _create_evidence_from_proposal(
        self,
        proposal: KnowledgeProposalRecord,
        decision: KnowledgeProposalDecision,
    ) -> str:
        evidence_id = self._required_payload_value(proposal, "id")
        node_id = self._required_payload_value(proposal, "node_id")
        source_id = self._required_payload_value(proposal, "source_id")
        source_edition_id = self._required_payload_value(proposal, "source_edition_id")
        version = proposal.payload.get("version", "knowledge-v0")
        locator = proposal.payload.get("locator")
        if not isinstance(version, str):
            raise ValueError("Knowledge proposal payload missing version")
        if not isinstance(locator, dict):
            raise ValueError("Knowledge proposal payload missing locator")
        if self.session.get(KnowledgeEvidenceItemRecord, evidence_id) is not None:
            raise ValueError("Knowledge evidence already exists")
        if self.session.get(KnowledgeNodeRecord, node_id) is None:
            raise KeyError(node_id)
        if self.session.get(KnowledgeSourceRecord, source_id) is None:
            raise KeyError(source_id)
        edition = self.session.get(KnowledgeSourceEditionRecord, source_edition_id)
        if edition is None or edition.source_id != source_id:
            raise KeyError(source_edition_id)
        if self.session.get(KnowledgeVersionRecord, version) is None:
            raise KeyError(version)
        now = datetime.now(UTC).isoformat()
        self.session.add(
            KnowledgeEvidenceItemRecord(
                id=evidence_id,
                node_id=node_id,
                source_id=source_id,
                source_edition_id=source_edition_id,
                evidence_type=self._required_payload_value(proposal, "evidence_type"),
                locator=locator,
                reference=self._required_payload_value(proposal, "reference"),
                excerpt=self._required_payload_value(proposal, "excerpt"),
                context=proposal.payload.get("context", "reviewed_proposal"),
                confidence=proposal.confidence,
                confidence_level=int(proposal.payload.get("confidence_level", 3)),
                status="validated",
                version=version,
                created_at=now,
                updated_at=now,
                incorporated_by=decision.reviewer,
                reviewed_by=decision.reviewer,
                revision=1,
            )
        )
        self.session.add(
            KnowledgeEvidenceRevisionRecord(
                id=f"{evidence_id}:r1",
                evidence_id=evidence_id,
                revision=1,
                author=decision.reviewer,
                reason=decision.reason,
                changes=proposal.payload,
                created_at=now,
            )
        )
        return evidence_id

    def _create_claim_from_proposal(
        self,
        proposal: KnowledgeProposalRecord,
        decision: KnowledgeProposalDecision,
    ) -> str:
        claim_id = self._required_payload_value(proposal, "id")
        evidence_id = self._required_payload_value(proposal, "evidence_id")
        card_id = self._required_payload_value(proposal, "card_id")
        node_id = self._required_payload_value(proposal, "node_id")
        version = proposal.payload.get("version", "knowledge-v0")
        related_node_ids = proposal.payload.get("related_node_ids", [])
        scope = proposal.payload.get("scope")
        if not isinstance(version, str):
            raise ValueError("Knowledge proposal payload missing version")
        if not isinstance(related_node_ids, list):
            raise ValueError("Knowledge proposal payload related_node_ids must be a list")
        if not isinstance(scope, dict):
            raise ValueError("Knowledge proposal payload missing scope")
        if self.session.get(KnowledgeClaimRecord, claim_id) is not None:
            raise ValueError("Knowledge claim already exists")
        if self.session.get(KnowledgeEvidenceItemRecord, evidence_id) is None:
            raise KeyError(evidence_id)
        if self.session.get(KnowledgeCardRecord, card_id) is None:
            raise KeyError(card_id)
        if self.session.get(KnowledgeNodeRecord, node_id) is None:
            raise KeyError(node_id)
        if self.session.get(KnowledgeVersionRecord, version) is None:
            raise KeyError(version)
        now = datetime.now(UTC).isoformat()
        claim_record = KnowledgeClaimRecord(
            id=claim_id,
            evidence_id=evidence_id,
            card_id=card_id,
            statement=self._required_payload_value(proposal, "statement"),
            claim_type=self._required_payload_value(proposal, "claim_type"),
            node_id=node_id,
            related_node_ids=related_node_ids,
            domain=self._required_payload_value(proposal, "domain"),
            scope=scope,
            status="validated",
            confidence=proposal.confidence,
            origin="approved_knowledge_proposal",
            version=version,
            revision=1,
            created_at=now,
            updated_at=now,
            published_at=None,
        )
        self.session.add(claim_record)
        self.session.flush()
        self.session.add(
            KnowledgeClaimEvidenceLinkRecord(
                id=f"{claim_id}:{evidence_id}:primary",
                claim_id=claim_id,
                evidence_id=evidence_id,
                role="primary",
                created_at=now,
            )
        )
        self.session.add(
            KnowledgeClaimRevisionRecord(
                id=f"{claim_id}:r1",
                claim_id=claim_id,
                revision=1,
                knowledge_version=version,
                author=decision.reviewer,
                reason=decision.reason,
                changed_fields=list(proposal.payload.keys()),
                previous_claim={},
                new_claim=proposal.payload,
                created_at=now,
            )
        )
        return claim_id

    def _create_relation_from_proposal(self, proposal: KnowledgeProposalRecord) -> str:
        relation_id = self._required_payload_value(proposal, "id")
        version = proposal.payload.get("version", "knowledge-v0")
        if not isinstance(version, str):
            raise ValueError("Knowledge proposal payload missing version")
        if self.session.get(KnowledgeRelationRecord, relation_id) is not None:
            raise ValueError("Knowledge relation already exists")
        if self.session.get(KnowledgeVersionRecord, version) is None:
            raise KeyError(version)
        now = datetime.now(UTC).isoformat()
        self.session.add(
            KnowledgeRelationRecord(
                id=relation_id,
                source_entity_type=self._required_payload_value(proposal, "source_entity_type"),
                source_entity_id=self._required_payload_value(proposal, "source_entity_id"),
                target_entity_type=self._required_payload_value(proposal, "target_entity_type"),
                target_entity_id=self._required_payload_value(proposal, "target_entity_id"),
                relation_type=self._required_payload_value(proposal, "relation_type"),
                direction=proposal.payload.get("direction", "outgoing"),
                cardinality=proposal.payload.get("cardinality", "N:N"),
                weight=float(proposal.payload.get("weight", 1.0)),
                confidence=proposal.confidence,
                context=proposal.payload.get("context", "reviewed_proposal"),
                status="validated",
                version=version,
                created_at=now,
                updated_at=now,
            )
        )
        return relation_id

    def list_knowledge_nodes(
        self,
        source_id: str | None = None,
        version: str | None = None,
    ) -> list[KnowledgeNode]:
        query = select(KnowledgeNodeRecord)
        snapshot = self._knowledge_snapshot(version) if version else None
        if snapshot is not None:
            query = query.where(KnowledgeNodeRecord.id.in_(snapshot.node_ids))
        if source_id:
            query = query.where(KnowledgeNodeRecord.source_id == source_id)
        if version and snapshot is None:
            query = query.where(KnowledgeNodeRecord.version == version)
        records = self.session.scalars(query.order_by(KnowledgeNodeRecord.id)).all()
        relation_query = select(KnowledgeNodeRelationRecord)
        if snapshot is not None:
            relation_query = relation_query.where(
                KnowledgeNodeRelationRecord.id.in_(snapshot.node_relation_ids)
            )
        if version and snapshot is None:
            relation_query = relation_query.where(KnowledgeNodeRelationRecord.version == version)
        relations = self.session.scalars(
            relation_query.order_by(KnowledgeNodeRelationRecord.id)
        ).all()
        relations_by_node: dict[str, list[KnowledgeNodeRelation]] = {}
        for relation in relations:
            relations_by_node.setdefault(relation.source_node_id, []).append(
                knowledge_node_relation_from_record(relation)
            )
        return [
            knowledge_node_from_record(record, relations_by_node.get(record.id, []))
            for record in records
        ]

    def list_knowledge_relations(
        self,
        version: str | None = None,
        source_entity_type: str | None = None,
        source_entity_id: str | None = None,
        relation_type: str | None = None,
    ) -> list[KnowledgeRelation]:
        query = select(KnowledgeRelationRecord)
        snapshot = self._knowledge_snapshot(version) if version else None
        if snapshot is not None:
            query = query.where(KnowledgeRelationRecord.id.in_(snapshot.relation_ids))
        if version and snapshot is None:
            query = query.where(KnowledgeRelationRecord.version == version)
        if source_entity_type:
            query = query.where(KnowledgeRelationRecord.source_entity_type == source_entity_type)
        if source_entity_id:
            query = query.where(KnowledgeRelationRecord.source_entity_id == source_entity_id)
        if relation_type:
            query = query.where(KnowledgeRelationRecord.relation_type == relation_type)
        records = self.session.scalars(query.order_by(KnowledgeRelationRecord.id)).all()
        return [knowledge_relation_from_record(record) for record in records]

    def list_knowledge_evidence(
        self,
        node_id: str | None = None,
        version: str | None = None,
    ) -> list[KnowledgeEvidenceItem]:
        query = select(KnowledgeEvidenceItemRecord)
        snapshot = self._knowledge_snapshot(version) if version else None
        if snapshot is not None:
            query = query.where(KnowledgeEvidenceItemRecord.id.in_(snapshot.evidence_ids))
        if node_id:
            query = query.where(KnowledgeEvidenceItemRecord.node_id == node_id)
        if version and snapshot is None:
            query = query.where(KnowledgeEvidenceItemRecord.version == version)
        records = self.session.scalars(query.order_by(KnowledgeEvidenceItemRecord.id)).all()
        return [knowledge_evidence_from_record(record) for record in records]

    def list_knowledge_claims(
        self,
        card_id: str | None = None,
        version: str | None = None,
    ) -> list[KnowledgeClaim]:
        query = select(KnowledgeClaimRecord)
        snapshot = self._knowledge_snapshot(version) if version else None
        if snapshot is not None:
            query = query.where(KnowledgeClaimRecord.id.in_(snapshot.claim_ids))
        if card_id:
            query = query.where(KnowledgeClaimRecord.card_id == card_id)
        if version and snapshot is None:
            query = query.where(KnowledgeClaimRecord.version == version)
        records = self.session.scalars(query.order_by(KnowledgeClaimRecord.id)).all()
        link_query = select(KnowledgeClaimEvidenceLinkRecord)
        if snapshot is not None:
            link_query = link_query.where(
                KnowledgeClaimEvidenceLinkRecord.id.in_(snapshot.claim_evidence_link_ids)
            )
        links = self.session.scalars(link_query.order_by(KnowledgeClaimEvidenceLinkRecord.id)).all()
        links_by_claim: dict[str, list[KnowledgeClaimEvidenceLink]] = {}
        for link in links:
            links_by_claim.setdefault(link.claim_id, []).append(
                knowledge_claim_evidence_link_from_record(link)
            )
        return [
            knowledge_claim_from_record(record, links_by_claim.get(record.id, []))
            for record in records
        ]

    def list_knowledge_cards(self, version: str | None = None) -> list[KnowledgeCard]:
        query = select(KnowledgeCardRecord)
        snapshot = self._knowledge_snapshot(version) if version else None
        if snapshot is not None:
            query = query.where(KnowledgeCardRecord.id.in_(snapshot.card_ids))
        if version and snapshot is None:
            query = query.where(KnowledgeCardRecord.version == version)
        records = self.session.scalars(query.order_by(KnowledgeCardRecord.id)).all()
        return [knowledge_card_from_record(record) for record in records]

    def knowledge_query_contract(self) -> KnowledgeQueryContract:
        return query_contract()

    def interpret_knowledge_query(
        self,
        payload: KnowledgeQueryInput,
    ) -> KnowledgeQueryInterpretation:
        resolved_version = resolve_knowledge_version(payload.version)
        if self.session.get(KnowledgeVersionRecord, resolved_version) is None:
            raise KeyError(resolved_version)
        return build_knowledge_query_interpretation(payload)

    def query_knowledge(self, payload: KnowledgeQueryInput) -> KnowledgeQueryResult:
        resolved_version = resolve_knowledge_version(payload.version)
        if self.session.get(KnowledgeVersionRecord, resolved_version) is None:
            raise KeyError(resolved_version)
        result = query_knowledge(
            payload,
            sources=self.list_knowledge_sources(version=resolved_version),
            nodes=self.list_knowledge_nodes(version=resolved_version),
            cards=self.list_knowledge_cards(version=resolved_version),
            claims=self.list_knowledge_claims(version=resolved_version),
            evidence=self.list_knowledge_evidence(version=resolved_version),
        )
        pending_validation_count = sum(
            1
            for item in [*result.cards, *result.claims, *result.evidence]
            if item.confidence < 0.7
        )
        self.add_audit_event(
            "knowledge.query.executed",
            "knowledge_version",
            resolved_version,
            {
                "query_length": len(payload.query),
                "limit": payload.limit,
                "card_count": result.card_count,
                "claim_count": result.claim_count,
                "evidence_count": result.evidence_count,
                "pending_validation_count": pending_validation_count,
                "requested_version": result.requested_version,
                "resolved_version": result.resolved_version,
                "query_type": result.query_type,
                "domain": result.domain,
                "status": result.status,
                "candidate_nodes": len(result.retrieval_trace["candidate_nodes"]),
                "candidate_cards": len(result.retrieval_trace["candidate_cards"]),
                "selected_cards": result.card_count,
                "selected_claims": result.claim_count,
                "selected_evidence": result.evidence_count,
                "relations_traversed": len(result.relations_followed),
                "max_depth_reached": 1 if result.relations_followed else 0,
                "cache_hit": False,
            },
        )
        self.session.commit()
        return result

    def list_knowledge_query_history(
        self,
        version: str,
        limit: int = 20,
    ) -> list[KnowledgeQueryHistoryItem]:
        if self.session.get(KnowledgeVersionRecord, version) is None:
            raise KeyError(version)
        records = self.session.scalars(
            select(AuditEventRecord)
            .where(
                AuditEventRecord.event_type == "knowledge.query.executed",
                AuditEventRecord.entity_type == "knowledge_version",
                AuditEventRecord.entity_id == version,
            )
            .order_by(AuditEventRecord.created_at.desc(), AuditEventRecord.id.desc())
            .limit(limit)
        ).all()
        return [knowledge_query_history_from_record(record) for record in records]

    def get_knowledge_query_summary(self, version: str) -> KnowledgeQuerySummary:
        if self.session.get(KnowledgeVersionRecord, version) is None:
            raise KeyError(version)
        records = self.session.scalars(
            select(AuditEventRecord)
            .where(
                AuditEventRecord.event_type == "knowledge.query.executed",
                AuditEventRecord.entity_type == "knowledge_version",
                AuditEventRecord.entity_id == version,
            )
            .order_by(AuditEventRecord.created_at.desc(), AuditEventRecord.id.desc())
        ).all()
        history = [knowledge_query_history_from_record(record) for record in records]
        empty_count = sum(1 for item in history if item.card_count == 0)
        return KnowledgeQuerySummary(
            version=version,
            total_count=len(history),
            empty_count=empty_count,
            hit_count=len(history) - empty_count,
            last_query_at=history[0].created_at if history else None,
        )

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

    def list_profile_knowledge_cards(self, profile_id: str) -> list[ProfileKnowledgeCard]:
        if self.session.get(ProfileRecord, profile_id) is None:
            raise KeyError(profile_id)
        records = self.session.scalars(
            select(ProfileKnowledgeCardRecord)
            .where(ProfileKnowledgeCardRecord.profile_id == profile_id)
            .order_by(ProfileKnowledgeCardRecord.updated_at.desc())
        ).all()
        return [profile_knowledge_card_from_record(record) for record in records]

    def get_profile_knowledge_card(
        self,
        profile_id: str,
        card_id: str,
        knowledge_version: str,
    ) -> ProfileKnowledgeCard:
        return profile_knowledge_card_from_record(
            self._profile_knowledge_card_record(profile_id, card_id, knowledge_version)
        )

    def upsert_profile_knowledge_card(
        self,
        profile_id: str,
        card_id: str,
        payload: ProfileKnowledgeCardInput,
    ) -> ProfileKnowledgeCard:
        profile = self.session.get(ProfileRecord, profile_id)
        if profile is None:
            raise KeyError(profile_id)
        if self.session.get(KnowledgeVersionRecord, payload.knowledge_version) is None:
            raise KeyError(payload.knowledge_version)
        card = self.session.get(KnowledgeCardRecord, card_id)
        if card is None:
            raise KeyError(card_id)
        record = self.session.scalar(
            select(ProfileKnowledgeCardRecord).where(
                ProfileKnowledgeCardRecord.profile_id == profile_id,
                ProfileKnowledgeCardRecord.card_id == card_id,
                ProfileKnowledgeCardRecord.knowledge_version == payload.knowledge_version,
            )
        )
        now = datetime.now(UTC)
        event_type = "profile.knowledge_card.registered"
        if record is None:
            record = ProfileKnowledgeCardRecord(
                id=str(uuid4()),
                profile_id=profile_id,
                card_id=card_id,
                knowledge_version=payload.knowledge_version,
                stance=payload.stance,
                user_score=payload.user_score,
                feedback=payload.feedback,
                maintained_elements=payload.maintained_elements,
                change_requests=payload.change_requests,
                notes=payload.notes,
                created_at=now,
                updated_at=now,
            )
            self.session.add(record)
        else:
            event_type = "profile.knowledge_card.updated"
            record.stance = payload.stance
            record.user_score = payload.user_score
            record.feedback = payload.feedback
            record.maintained_elements = payload.maintained_elements
            record.change_requests = payload.change_requests
            record.notes = payload.notes
            record.updated_at = now
        profile.updated_at = now
        self.add_audit_event(
            event_type,
            "profile_knowledge_card",
            record.id,
            {
                "profile_id": profile_id,
                "card_id": card_id,
                "knowledge_version": payload.knowledge_version,
                "stance": payload.stance,
                "user_score": payload.user_score,
                "stable_knowledge_mutated": False,
            },
        )
        self.session.commit()
        self.session.refresh(record)
        return profile_knowledge_card_from_record(record)

    def build_profile_knowledge_card_score_proposal(
        self,
        profile_id: str,
        card_id: str,
        knowledge_version: str,
        context: str,
    ) -> ProfileKnowledgeCardScoreProposal:
        profile_card = self._profile_knowledge_card_record(profile_id, card_id, knowledge_version)
        variables = self.get_context_variables(profile_id, context)
        variables_by_key = {variable.key: variable for variable in variables}
        variable_keys = self._variables_from_profile_knowledge_card(profile_card)
        delta = self._profile_knowledge_card_delta(profile_card)
        items = [
            ProfileKnowledgeCardScoreProposalItem(
                variable_key=variable_key,
                context=context,
                current_value=variables_by_key[variable_key].calculated_value,
                proposed_value=clamp_score(variables_by_key[variable_key].calculated_value + delta),
                delta=delta,
                reason=(
                    "Ficha de usuario "
                    f"{profile_card.stance} para {profile_card.card_id}: {profile_card.feedback}"
                ),
            )
            for variable_key in variable_keys
            if variable_key in variables_by_key
        ]
        return ProfileKnowledgeCardScoreProposal(
            profile_knowledge_card_id=UUID(profile_card.id),
            status="pending_review" if items else "not_applicable",
            items=items,
        )

    def apply_profile_knowledge_card_score_proposal(
        self,
        profile_id: str,
        card_id: str,
        knowledge_version: str,
        context: str,
        reason: str,
    ) -> list[ScoreVariable]:
        proposal = self.build_profile_knowledge_card_score_proposal(
            profile_id,
            card_id,
            knowledge_version,
            context,
        )
        if proposal.status != "pending_review":
            raise ValueError("Profile knowledge card score proposal is not pending review")
        updated_variables: list[ScoreVariable] = []
        now = datetime.now(UTC)
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
            record.calculated_value = item.proposed_value
            record.evidence_count += 1
            record.confidence = min(1, record.confidence + 0.02)
            record.updated_at = now
            updated_variables.append(score_from_record(record))
        profile = self.session.get(ProfileRecord, profile_id)
        if profile is not None:
            profile.updated_at = now
        self.add_audit_event(
            "profile.knowledge_card.score_applied",
            "profile_knowledge_card",
            str(proposal.profile_knowledge_card_id),
            {
                "profile_id": profile_id,
                "card_id": card_id,
                "knowledge_version": knowledge_version,
                "context": context,
                "reason": reason,
                "items": [item.model_dump() for item in proposal.items],
                "stable_knowledge_mutated": False,
            },
        )
        self.session.commit()
        return updated_variables

    def _profile_knowledge_card_record(
        self,
        profile_id: str,
        card_id: str,
        knowledge_version: str,
    ) -> ProfileKnowledgeCardRecord:
        record = self.session.scalar(
            select(ProfileKnowledgeCardRecord).where(
                ProfileKnowledgeCardRecord.profile_id == profile_id,
                ProfileKnowledgeCardRecord.card_id == card_id,
                ProfileKnowledgeCardRecord.knowledge_version == knowledge_version,
            )
        )
        if record is None:
            raise KeyError(card_id)
        return record

    def _variables_from_profile_knowledge_card(
        self,
        profile_card: ProfileKnowledgeCardRecord,
    ) -> list[str]:
        text = canonical_text(
            " ".join(
                [
                    profile_card.card_id,
                    profile_card.feedback,
                    " ".join(profile_card.maintained_elements),
                    " ".join(profile_card.change_requests),
                    profile_card.notes,
                ]
            )
        )
        hints = {
            "precision_lexica": ("precision", "lexic", "exact"),
            "sobriedad": ("sobri", "tono", "formal", "contenido"),
            "dinamismo": ("dinam", "direct", "breve", "frase", "ritmo"),
            "densidad_argumental": ("argument", "tesis", "densidad"),
        }
        matches = [
            variable_key
            for variable_key, terms in hints.items()
            if any(term in text for term in terms)
        ]
        return matches or ["precision_lexica"]

    def _profile_knowledge_card_delta(self, profile_card: ProfileKnowledgeCardRecord) -> int:
        base_delta = max(10, min(80, round(abs(profile_card.user_score - 500) / 10)))
        if profile_card.stance in {"liked", "kept"}:
            return base_delta
        if profile_card.stance == "changed":
            return -max(10, min(base_delta, 40))
        return -base_delta

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

    def add_preference(
        self, profile_id: str, preference: Preference, duration_ms: int | None = None
    ) -> Preference:
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
            {
                "status": preference.status.value,
                "affected_variables": preference.affected_variables,
                "duration_ms": duration_ms,
            },
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

    def add_feedback_proposal(
        self, profile_id: str, proposal: FeedbackProposal
    ) -> FeedbackProposal:
        if self.session.get(ProfileRecord, profile_id) is None:
            raise KeyError(profile_id)
        if self.session.get(ComparisonRecord, str(proposal.comparison_id)) is None:
            raise KeyError(str(proposal.comparison_id))
        self.session.add(feedback_to_record(profile_id, proposal))
        self.add_audit_event(
            "feedback.proposed",
            "comparison",
            str(proposal.comparison_id),
            {"proposal_id": str(proposal.id), "items": [item.model_dump() for item in proposal.items]},
        )
        self.session.commit()
        return proposal

    def list_feedback_proposals(self, profile_id: str) -> list[FeedbackProposal]:
        records = self.session.scalars(
            select(FeedbackProposalRecord)
            .where(FeedbackProposalRecord.profile_id == profile_id)
            .order_by(FeedbackProposalRecord.created_at.desc())
        ).all()
        return [feedback_from_record(record) for record in records]

    def decide_feedback_proposal(
        self,
        profile_id: str,
        proposal_id: UUID,
        decision: FeedbackDecisionInput,
    ) -> FeedbackProposal:
        record = self.session.scalar(
            select(FeedbackProposalRecord).where(
                FeedbackProposalRecord.profile_id == profile_id,
                FeedbackProposalRecord.id == str(proposal_id),
            )
        )
        if record is None:
            raise KeyError(str(proposal_id))
        if record.status != FeedbackStatus.proposed.value:
            raise ValueError("Feedback proposal is already closed")
        if decision.status == FeedbackStatus.proposed:
            raise ValueError("Feedback proposal must be applied or rejected")

        proposal = feedback_from_record(record)
        selected_keys = set(decision.variable_keys or [item.variable_key for item in proposal.items])
        applied_items = [item for item in proposal.items if item.variable_key in selected_keys]

        if decision.status == FeedbackStatus.applied:
            for item in applied_items:
                variable_record = self.session.scalar(
                    select(ScoreVariableRecord).where(
                        ScoreVariableRecord.profile_id == profile_id,
                        ScoreVariableRecord.key == item.variable_key,
                        ScoreVariableRecord.context == item.context,
                    )
                )
                if variable_record is None:
                    continue
                variable_record.calculated_value = item.proposed_value
                variable_record.evidence_count += 1
                variable_record.confidence = min(1, variable_record.confidence + 0.02)
                variable_record.updated_at = datetime.now(UTC)
            event_type = "feedback.applied"
        else:
            event_type = "feedback.rejected"

        record.status = decision.status.value
        record.updated_at = datetime.now(UTC)
        profile = self.session.get(ProfileRecord, profile_id)
        if profile is not None:
            profile.updated_at = datetime.now(UTC)
        self.add_audit_event(
            event_type,
            "feedback_proposal",
            str(proposal_id),
            {
                "reason": decision.reason,
                "applied_items": [item.model_dump() for item in applied_items],
            },
        )
        self.session.commit()
        self.session.refresh(record)
        return feedback_from_record(record)

    def add_generated_text(
        self, text: GeneratedText, duration_ms: int | None = None
    ) -> GeneratedText:
        if self.session.get(ProfileRecord, text.profile_id) is None:
            raise KeyError(text.profile_id)
        self.session.add(generated_text_to_record(text))
        self.add_audit_event(
            "text.generated",
            "generated_text",
            str(text.id),
            {
                "context": text.context,
                "action": text.action,
                "provider": text.provider,
                "used_profile_variables": text.used_profile_variables,
                "duration_ms": duration_ms,
            },
        )
        self.session.commit()
        return text

    def list_generated_texts(
        self, profile_id: str, limit: int = 50, context: str | None = None
    ) -> list[GeneratedText]:
        query = select(GeneratedTextRecord).where(GeneratedTextRecord.profile_id == profile_id)
        if context:
            query = query.where(GeneratedTextRecord.context == context)
        records = self.session.scalars(
            query.order_by(GeneratedTextRecord.created_at.desc()).limit(limit)
        ).all()
        return [generated_text_from_record(record) for record in records]

    def list_audit_events(
        self,
        limit: int = 50,
        event_type: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
    ) -> list[AuditEvent]:
        query = select(AuditEventRecord)
        if event_type:
            query = query.where(AuditEventRecord.event_type == event_type)
        if entity_type:
            query = query.where(AuditEventRecord.entity_type == entity_type)
        if entity_id:
            query = query.where(AuditEventRecord.entity_id == entity_id)
        records = self.session.scalars(
            query.order_by(AuditEventRecord.created_at.desc(), AuditEventRecord.id.desc()).limit(limit)
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
