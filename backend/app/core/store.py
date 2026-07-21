from datetime import UTC, datetime

from uuid import UUID

from app.core.models import ComparisonResult, Preference, PreferenceStatus, Profile, ScoreVariable
from app.core.seeds import DEFAULT_PROFILE_ID, seed_variables


class InMemoryStore:
    def __init__(self) -> None:
        self.profile = Profile(
            id=DEFAULT_PROFILE_ID,
            name="Perfil inicial",
            summary="Perfil semilla con baja confianza. Las preferencias requieren revision explicita.",
            variables=seed_variables(),
            preferences=[],
            updated_at=datetime.now(UTC),
        )
        self.comparisons: dict[str, ComparisonResult] = {}

    def get_profile(self, profile_id: str) -> Profile:
        if profile_id != self.profile.id:
            raise KeyError(profile_id)
        return self.profile

    def update_variable(self, variable: ScoreVariable) -> None:
        self.profile.variables = [
            variable if current.key == variable.key else current for current in self.profile.variables
        ]
        self.profile.updated_at = datetime.now(UTC)

    def add_preference(self, preference: Preference) -> Preference:
        self.profile.preferences.append(preference)
        self.profile.updated_at = datetime.now(UTC)
        return preference

    def update_preference_status(
        self, preference_id: UUID, status: PreferenceStatus
    ) -> Preference:
        for index, preference in enumerate(self.profile.preferences):
            if preference.id == preference_id:
                updated = preference.model_copy(update={"status": status})
                self.profile.preferences[index] = updated
                self.profile.updated_at = datetime.now(UTC)
                return updated
        raise KeyError(str(preference_id))

    def delete_preference(self, preference_id: UUID) -> None:
        next_preferences = [
            preference for preference in self.profile.preferences if preference.id != preference_id
        ]
        if len(next_preferences) == len(self.profile.preferences):
            raise KeyError(str(preference_id))
        self.profile.preferences = next_preferences
        self.profile.updated_at = datetime.now(UTC)

    def add_comparison(self, comparison: ComparisonResult) -> ComparisonResult:
        self.comparisons[str(comparison.id)] = comparison
        return comparison


store = InMemoryStore()
