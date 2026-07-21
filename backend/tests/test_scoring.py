from app.core.models import ScorePatch
from app.core.seeds import seed_variables
from app.scoring.service import apply_manual_override


def test_manual_override_changes_effective_value_and_records_evidence():
    variable = seed_variables()[0]
    updated, evidence = apply_manual_override(
        variable, ScorePatch(manual_adjustment=80, reason="Prefiero mas ritmo.")
    )

    assert updated.effective_value == variable.calculated_value + 80
    assert evidence.source == f"score:{variable.key}"
    assert evidence.summary == "Prefiero mas ritmo."

