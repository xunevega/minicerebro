from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
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
    KnowledgeQueryContract,
    KnowledgeQueryInput,
    KnowledgeQueryHistoryItem,
    KnowledgeQueryInterpretation,
    KnowledgeQueryResult,
    KnowledgeQuerySummary,
    KnowledgeRelation,
    KnowledgeSource,
    KnowledgeSourceCreate,
    KnowledgeSourceEdition,
    KnowledgeSourceEditionCreate,
    KnowledgeVersion,
    KnowledgeVersioningPolicy,
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
    FeedbackProposalRecord,
    GeneratedTextRecord,
    KnowledgeCardRecord,
    KnowledgeClaimEvidenceLinkRecord,
    KnowledgeClaimRecord,
    KnowledgeEvidenceItemRecord,
    KnowledgeIngestionBatchRecord,
    KnowledgeNodeRecord,
    KnowledgeNodeRelationRecord,
    KnowledgeObjectRevisionRecord,
    KnowledgeRelationRecord,
    KnowledgeSourceRecord,
    KnowledgeSourceEditionRecord,
    KnowledgeVersionRecord,
    PreferenceRecord,
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

    def list_knowledge_object_revisions(
        self,
        object_type: str | None = None,
        object_id: str | None = None,
        knowledge_version: str | None = None,
    ) -> list[KnowledgeObjectRevision]:
        query = select(KnowledgeObjectRevisionRecord)
        if object_type:
            query = query.where(KnowledgeObjectRevisionRecord.object_type == object_type)
        if object_id:
            query = query.where(KnowledgeObjectRevisionRecord.object_id == object_id)
        if knowledge_version:
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
        records = self.session.scalars(
            query.order_by(KnowledgeSourceRecord.priority, KnowledgeSourceRecord.catalog_id)
        ).all()
        editions = self.session.scalars(
            select(KnowledgeSourceEditionRecord).order_by(KnowledgeSourceEditionRecord.id)
        ).all()
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

    def list_knowledge_nodes(
        self,
        source_id: str | None = None,
        version: str | None = None,
    ) -> list[KnowledgeNode]:
        query = select(KnowledgeNodeRecord)
        if source_id:
            query = query.where(KnowledgeNodeRecord.source_id == source_id)
        if version:
            query = query.where(KnowledgeNodeRecord.version == version)
        records = self.session.scalars(query.order_by(KnowledgeNodeRecord.id)).all()
        relation_query = select(KnowledgeNodeRelationRecord)
        if version:
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
        if version:
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
        if node_id:
            query = query.where(KnowledgeEvidenceItemRecord.node_id == node_id)
        if version:
            query = query.where(KnowledgeEvidenceItemRecord.version == version)
        records = self.session.scalars(query.order_by(KnowledgeEvidenceItemRecord.id)).all()
        return [knowledge_evidence_from_record(record) for record in records]

    def list_knowledge_claims(
        self,
        card_id: str | None = None,
        version: str | None = None,
    ) -> list[KnowledgeClaim]:
        query = select(KnowledgeClaimRecord)
        if card_id:
            query = query.where(KnowledgeClaimRecord.card_id == card_id)
        if version:
            query = query.where(KnowledgeClaimRecord.version == version)
        records = self.session.scalars(query.order_by(KnowledgeClaimRecord.id)).all()
        links = self.session.scalars(
            select(KnowledgeClaimEvidenceLinkRecord).order_by(KnowledgeClaimEvidenceLinkRecord.id)
        ).all()
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
        if version:
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
