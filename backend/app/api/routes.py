from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.comparison.service import compare_texts
from app.core.repository import Repository
from app.core.models import (
    ApplyScoreProposalInput,
    ComparisonInput,
    DecisionEvaluation,
    DecisionEvaluationInput,
    DecisionRule,
    FeedbackDecisionInput,
    FeedbackProposalInput,
    GeneratedText,
    GenerationInput,
    KnowledgeStatus,
    LabSimulationInput,
    LabSimulationResult,
    PreferenceInput,
    PreferencePatch,
    PersistenceDomain,
    ScorePatch,
    V1Screen,
)
from app.api.deps import get_repository
from app.core.seeds import DEFAULT_PROFILE_ID
from app.decision.service import decision_rules, evaluate_decision_state
from app.feedback.service import build_feedback_proposal
from app.generation.service import rewrite_with_profile
from app.knowledge.service import seed_cards, seed_sources
from app.persistence.service import persistence_domains
from app.preferences.service import build_score_proposal, interpret_preference
from app.scoring.service import apply_manual_override, score_out
from app.ui.service import v1_screens

router = APIRouter()
RepositoryDep = Annotated[Repository, Depends(get_repository)]


@router.get("/knowledge/status")
def knowledge_status() -> KnowledgeStatus:
    return KnowledgeStatus(
        version="knowledge-v0",
        state="seed",
        coverage=["lengua espanola", "escritura", "estilo", "comparacion textual"],
        gaps=["fuentes academicas versionadas", "pgvector", "validacion editorial"],
        sources_policy="La base de conocimiento no cambia por preferencias ni correcciones del usuario.",
    )


@router.get("/knowledge/coverage")
def knowledge_coverage() -> dict[str, list[str]]:
    return {
        "covered": ["scoring editable", "comparador inicial", "perfil semilla"],
        "pending": ["registro academico", "fichas internas", "evidencias bibliograficas"],
    }


@router.get("/knowledge/versions")
def knowledge_versions() -> dict[str, list[dict[str, str]]]:
    return {"versions": [{"id": "knowledge-v0", "status": "seed", "published_at": "not-published"}]}


@router.get("/knowledge/sources")
def knowledge_sources():
    return seed_sources()


@router.get("/knowledge/cards")
def knowledge_cards():
    return seed_cards()


@router.get("/ui/screens")
def ui_screens() -> list[V1Screen]:
    return v1_screens()


@router.get("/decision/rules")
def decisions_rules() -> list[DecisionRule]:
    return decision_rules()


@router.post("/decision/evaluate")
def decision_evaluate(
    payload: DecisionEvaluationInput,
    repository: RepositoryDep,
) -> DecisionEvaluation:
    variables = repository.get_context_variables(DEFAULT_PROFILE_ID, payload.context)
    contradictions = repository.contradictions(DEFAULT_PROFILE_ID, payload.context)
    return evaluate_decision_state(payload.context, variables, contradictions)


@router.get("/persistence/status")
def persistence_status() -> list[PersistenceDomain]:
    return persistence_domains()


@router.post("/preferences/interpret")
def preferences_interpret(payload: PreferenceInput):
    return interpret_preference(payload)


@router.post("/preferences")
def preferences_create(payload: PreferenceInput, repository: RepositoryDep):
    preference = interpret_preference(payload)
    return repository.add_preference(DEFAULT_PROFILE_ID, preference)


@router.get("/preferences")
def preferences_list(repository: RepositoryDep, context: str | None = None):
    if context:
        return repository.list_preferences_for_context(DEFAULT_PROFILE_ID, context)
    return repository.list_preferences(DEFAULT_PROFILE_ID)


@router.patch("/preferences/{preference_id}")
def preferences_patch(preference_id: UUID, payload: PreferencePatch, repository: RepositoryDep):
    try:
        return repository.update_preference_status(
            DEFAULT_PROFILE_ID, preference_id, payload.status
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Preference not found") from exc


@router.delete("/preferences/{preference_id}", status_code=204)
def preferences_delete(preference_id: UUID, repository: RepositoryDep):
    try:
        repository.delete_preference(DEFAULT_PROFILE_ID, preference_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Preference not found") from exc


@router.get("/preferences/{preference_id}/score-proposal")
def preference_score_proposal(preference_id: UUID, repository: RepositoryDep):
    try:
        preference = repository.get_preference(DEFAULT_PROFILE_ID, preference_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Preference not found") from exc
    return build_score_proposal(preference)


@router.post("/preferences/{preference_id}/score-proposal/apply")
def preference_score_proposal_apply(
    preference_id: UUID, payload: ApplyScoreProposalInput, repository: RepositoryDep
):
    try:
        preference = repository.get_preference(DEFAULT_PROFILE_ID, preference_id)
        proposal = build_score_proposal(preference)
        updated = repository.apply_score_proposal(DEFAULT_PROFILE_ID, proposal, payload.reason)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Preference not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"proposal": proposal, "variables": [score_out(variable) for variable in updated]}


@router.get("/profiles/{profile_id}")
def profile_get(profile_id: str, repository: RepositoryDep):
    try:
        return repository.get_profile(profile_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Profile not found") from exc


@router.get("/profiles/{profile_id}/summary")
def profile_summary(profile_id: str, repository: RepositoryDep):
    profile = profile_get(profile_id, repository)
    return {
        "profile_id": profile.id,
        "summary": profile.summary,
        "preference_count": len(profile.preferences),
        "confidence_note": "Confianza baja hasta que existan evidencias confirmadas.",
    }


@router.get("/profiles/{profile_id}/scores")
def profile_scores(profile_id: str, repository: RepositoryDep, context: str = "general"):
    return [score_out(variable) for variable in repository.get_context_variables(profile_id, context)]


@router.get("/profiles/{profile_id}/statistics")
def profile_statistics(profile_id: str, repository: RepositoryDep, context: str = "general"):
    return repository.profile_statistics(profile_id, context)


@router.get("/profiles/{profile_id}/contradictions")
def profile_contradictions(profile_id: str, repository: RepositoryDep, context: str = "general"):
    return repository.contradictions(profile_id, context)


@router.patch("/profiles/{profile_id}/scores/{variable_key}")
def profile_score_patch(
    profile_id: str,
    variable_key: str,
    payload: ScorePatch,
    repository: RepositoryDep,
    context: str = "general",
):
    variables = repository.get_context_variables(profile_id, context)
    variable = next((item for item in variables if item.key == variable_key), None)
    if variable is None:
        raise HTTPException(status_code=404, detail="Variable not found")

    updated, evidence = apply_manual_override(variable, payload)
    repository.update_variable(profile_id, updated, evidence)
    return {"variable": score_out(updated), "evidence": evidence}


@router.post("/comparisons")
def comparisons_create(payload: ComparisonInput, repository: RepositoryDep):
    return repository.add_comparison(compare_texts(payload))


@router.get("/comparisons/{comparison_id}")
def comparisons_get(comparison_id: UUID, repository: RepositoryDep):
    try:
        return repository.get_comparison(comparison_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Comparison not found") from exc


@router.post("/comparisons/{comparison_id}/feedback")
def comparison_feedback_create(
    comparison_id: UUID,
    payload: FeedbackProposalInput,
    repository: RepositoryDep,
):
    try:
        comparison = repository.get_comparison(comparison_id)
        variables = repository.get_context_variables(DEFAULT_PROFILE_ID, payload.context)
        proposal = build_feedback_proposal(comparison, variables, payload.context)
        if payload.note:
            proposal.rationale.append(payload.note)
        return repository.add_feedback_proposal(DEFAULT_PROFILE_ID, proposal)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Comparison not found") from exc


@router.get("/feedback/proposals")
def feedback_proposals_list(repository: RepositoryDep):
    return repository.list_feedback_proposals(DEFAULT_PROFILE_ID)


@router.patch("/feedback/proposals/{proposal_id}")
def feedback_proposal_decide(
    proposal_id: UUID,
    payload: FeedbackDecisionInput,
    repository: RepositoryDep,
):
    try:
        return repository.decide_feedback_proposal(DEFAULT_PROFILE_ID, proposal_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Feedback proposal not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/audit/events")
def audit_events(repository: RepositoryDep, limit: int = 50):
    bounded_limit = max(1, min(limit, 100))
    return repository.list_audit_events(bounded_limit)


@router.get("/texts")
def generated_texts_list(
    repository: RepositoryDep,
    context: str | None = None,
    limit: int = 50,
):
    bounded_limit = max(1, min(limit, 100))
    return repository.list_generated_texts(DEFAULT_PROFILE_ID, bounded_limit, context)


@router.post("/generation")
@router.post("/correction")
@router.post("/rewrite")
@router.post("/continue")
@router.post("/variants")
def generation_create(payload: GenerationInput, repository: RepositoryDep):
    variables = repository.get_context_variables(DEFAULT_PROFILE_ID, payload.context)
    generation = rewrite_with_profile(payload, variables)
    repository.add_generated_text(
        GeneratedText(
            profile_id=DEFAULT_PROFILE_ID,
            context=payload.context,
            action=payload.action,
            input_text=payload.text,
            output_text=generation.output,
            provider=generation.provider,
            used_profile_variables=generation.used_profile_variables,
            learning_applied=generation.learning_applied,
        )
    )
    return generation


@router.post("/lab/simulate")
def lab_simulate(payload: LabSimulationInput, repository: RepositoryDep) -> LabSimulationResult:
    variables = repository.get_context_variables(DEFAULT_PROFILE_ID, payload.context)
    deltas = {override.variable_key: override.delta for override in payload.overrides}
    simulated_variables = [
        variable.model_copy(
            update={
                "manual_adjustment": max(
                    -1000,
                    min(1000, variable.manual_adjustment + deltas.get(variable.key, 0)),
                )
            }
        )
        for variable in variables
    ]
    generation_input = GenerationInput(
        text=payload.text,
        action=payload.action,
        context=payload.context,
        intensity=payload.intensity,
        protected_terms=payload.protected_terms,
    )
    generation = rewrite_with_profile(generation_input, simulated_variables)
    comparison = compare_texts(
        ComparisonInput(
            original=payload.text,
            revised=generation.output,
            context=payload.context,
        )
    )
    return LabSimulationResult(
        generation=generation,
        comparison=comparison,
        simulated_variables=[score_out(variable) for variable in simulated_variables],
        learning_applied=False,
    )
