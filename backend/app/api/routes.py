from fastapi import APIRouter, HTTPException

from app.comparison.service import compare_texts
from app.core.models import (
    ComparisonInput,
    GenerationInput,
    KnowledgeStatus,
    PreferenceInput,
    ScorePatch,
)
from app.core.store import store
from app.generation.service import rewrite_with_profile
from app.preferences.service import interpret_preference
from app.scoring.service import apply_manual_override, score_out

router = APIRouter()


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


@router.post("/preferences/interpret")
def preferences_interpret(payload: PreferenceInput):
    return interpret_preference(payload)


@router.post("/preferences")
def preferences_create(payload: PreferenceInput):
    preference = interpret_preference(payload)
    return store.add_preference(preference)


@router.get("/preferences")
def preferences_list():
    return store.profile.preferences


@router.get("/profiles/{profile_id}")
def profile_get(profile_id: str):
    try:
        return store.get_profile(profile_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Profile not found") from exc


@router.get("/profiles/{profile_id}/summary")
def profile_summary(profile_id: str):
    profile = profile_get(profile_id)
    return {
        "profile_id": profile.id,
        "summary": profile.summary,
        "preference_count": len(profile.preferences),
        "confidence_note": "Confianza baja hasta que existan evidencias confirmadas.",
    }


@router.get("/profiles/{profile_id}/scores")
def profile_scores(profile_id: str):
    profile = profile_get(profile_id)
    return [score_out(variable) for variable in profile.variables]


@router.patch("/profiles/{profile_id}/scores/{variable_key}")
def profile_score_patch(profile_id: str, variable_key: str, payload: ScorePatch):
    profile = profile_get(profile_id)
    variable = next((item for item in profile.variables if item.key == variable_key), None)
    if variable is None:
        raise HTTPException(status_code=404, detail="Variable not found")

    updated, evidence = apply_manual_override(variable, payload)
    store.update_variable(updated)
    return {"variable": score_out(updated), "evidence": evidence}


@router.post("/comparisons")
def comparisons_create(payload: ComparisonInput):
    return store.add_comparison(compare_texts(payload))


@router.get("/comparisons/{comparison_id}")
def comparisons_get(comparison_id: str):
    comparison = store.comparisons.get(comparison_id)
    if comparison is None:
        raise HTTPException(status_code=404, detail="Comparison not found")
    return comparison


@router.post("/generation")
@router.post("/correction")
@router.post("/rewrite")
@router.post("/continue")
def generation_create(payload: GenerationInput):
    return rewrite_with_profile(payload, store.profile.variables)

