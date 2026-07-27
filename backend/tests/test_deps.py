from dataclasses import dataclass

from app.api import deps


@dataclass
class FakeBind:
    url: str


class FakeSession:
    def __init__(self, url: str) -> None:
        self._bind = FakeBind(url)

    def get_bind(self) -> FakeBind:
        return self._bind


def test_ensure_seed_data_once_caches_sqlite_urls(monkeypatch):
    calls = []
    database_url = "sqlite:////tmp/minicerebro-seed-cache-test.sqlite3"
    deps._SEEDED_DATABASE_URLS.discard(database_url)

    def fake_ensure_seed_data(session):
        calls.append(session)

    monkeypatch.setattr(deps, "ensure_seed_data", fake_ensure_seed_data)

    deps.ensure_seed_data_once(FakeSession(database_url))
    deps.ensure_seed_data_once(FakeSession(database_url))

    assert len(calls) == 1
