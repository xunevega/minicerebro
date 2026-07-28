from pathlib import Path
import subprocess
import sys

import pytest

from app.knowledge.catalog import LATEST_PUBLISHED_KNOWLEDGE_VERSION
from app.knowledge.contracts import LATEST_KNOWLEDGE_VERSION
from app.knowledge.snapshot_data import (
    knowledge_snapshot_path,
    load_knowledge_seed_snapshot,
)
from app.db import bootstrap


def test_static_knowledge_catalog_is_separate_from_runtime_service() -> None:
    root_dir = Path(__file__).resolve().parents[1]
    service_source = (root_dir / "app" / "knowledge" / "service.py").read_text()
    catalog_source = (root_dir / "app" / "knowledge" / "catalog.py").read_text()

    assert "def query_knowledge(" in service_source
    assert "app.knowledge.catalog" not in service_source
    assert "V51_SEED_ITEMS = [" not in service_source
    assert "def seed_sources(" not in service_source
    assert "seed_sources" not in service_source
    assert "seed_cards" not in service_source
    assert "seed_claims" not in service_source
    assert "seed_evidence" not in service_source
    assert "seed_nodes" not in service_source
    assert "seed_relations" not in service_source
    assert "def seed_sources(" in catalog_source
    assert "load_knowledge_seed_snapshot" in catalog_source
    assert "V51_SEED_ITEMS = [" not in catalog_source


def test_runtime_app_does_not_import_static_knowledge_catalog() -> None:
    root_dir = Path(__file__).resolve().parents[1]
    allowed_paths = {
        root_dir / "app" / "knowledge" / "catalog.py",
        root_dir / "app" / "knowledge" / "legacy_seed.py",
    }
    offenders = []
    for path in sorted((root_dir / "app").rglob("*.py")):
        if path in allowed_paths:
            continue
        source = path.read_text()
        if "app.knowledge.catalog" in source:
            offenders.append(str(path.relative_to(root_dir)))

    assert offenders == []


def test_runtime_contract_version_tracks_legacy_catalog_version() -> None:
    assert LATEST_KNOWLEDGE_VERSION == LATEST_PUBLISHED_KNOWLEDGE_VERSION


def test_repository_passes_persisted_relations_to_knowledge_query() -> None:
    root_dir = Path(__file__).resolve().parents[1]
    repository_source = (root_dir / "app" / "core" / "repository.py").read_text()

    assert "relations=self.list_knowledge_relations(version=resolved_version)" in repository_source


def test_bootstrap_keeps_legacy_knowledge_seed_isolated() -> None:
    root_dir = Path(__file__).resolve().parents[1]
    bootstrap_source = (root_dir / "app" / "db" / "bootstrap.py").read_text()
    legacy_seed_source = (root_dir / "app" / "knowledge" / "legacy_seed.py").read_text()

    assert "from app.knowledge.legacy_seed import ensure_knowledge_seed_data" in bootstrap_source
    assert "app.knowledge.catalog" not in bootstrap_source
    assert "seed_sources" not in bootstrap_source
    assert "from app.knowledge.service import (" not in bootstrap_source
    assert "from app.knowledge.catalog import (" in legacy_seed_source
    assert "def ensure_knowledge_seed_data(" in legacy_seed_source


def test_current_snapshot_is_loaded_through_shared_data_contract() -> None:
    snapshot = load_knowledge_seed_snapshot(LATEST_PUBLISHED_KNOWLEDGE_VERSION)

    assert knowledge_snapshot_path(LATEST_PUBLISHED_KNOWLEDGE_VERSION).name == (
        f"{LATEST_PUBLISHED_KNOWLEDGE_VERSION}.snapshot.json"
    )
    assert snapshot["format"] == "knowledge-seed-snapshot-v1"
    assert snapshot["version"] == LATEST_PUBLISHED_KNOWLEDGE_VERSION
    assert snapshot["tables"]["knowledge_versions"]


def test_snapshot_loader_rejects_missing_version() -> None:
    with pytest.raises(FileNotFoundError):
        load_knowledge_seed_snapshot("knowledge-v999")


def test_current_alembic_data_migration_uses_shared_snapshot_loader() -> None:
    root_dir = Path(__file__).resolve().parents[1]
    migration_source = (
        root_dir
        / "alembic"
        / "versions"
        / "20260728_0022_seed_knowledge_v51_snapshot.py"
    ).read_text()

    assert "from app.knowledge.snapshot_data import load_knowledge_seed_snapshot" in migration_source
    assert "load_knowledge_seed_snapshot(SNAPSHOT_VERSION)" in migration_source
    assert "json.loads" not in migration_source


def test_snapshot_export_script_does_not_import_static_catalog() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    script_source = (repo_root / "scripts" / "export-knowledge-snapshot.py").read_text()

    assert "app.knowledge.catalog" not in script_source
    assert "LATEST_PUBLISHED_KNOWLEDGE_VERSION" not in script_source
    assert "latest_published_snapshot_version" in script_source


def test_snapshot_migration_generator_uses_shared_snapshot_loader(tmp_path) -> None:
    repo_root = Path(__file__).resolve().parents[2]

    subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "create-knowledge-snapshot-migration.py"),
            "--version",
            LATEST_PUBLISHED_KNOWLEDGE_VERSION,
            "--revision-id",
            "20260728_0099",
            "--down-revision",
            "20260728_0022",
            "--create-date",
            "2026-07-28",
            "--output-dir",
            str(tmp_path),
        ],
        check=True,
        cwd=repo_root,
    )

    generated = tmp_path / "20260728_0099_seed_knowledge_v51_snapshot.py"
    migration_source = generated.read_text()

    assert "from app.knowledge.snapshot_data import load_knowledge_seed_snapshot" in migration_source
    assert 'revision: str = "20260728_0099"' in migration_source
    assert 'down_revision: str | None = "20260728_0022"' in migration_source
    assert f'SNAPSHOT_VERSION = "{LATEST_PUBLISHED_KNOWLEDGE_VERSION}"' in migration_source
    assert "load_knowledge_seed_snapshot(SNAPSHOT_VERSION)" in migration_source
    assert "json.loads" not in migration_source


def test_seed_data_rejects_missing_published_snapshot_without_legacy_flag(monkeypatch) -> None:
    calls = []

    class FakeSession:
        def commit(self) -> None:
            calls.append("commit")

    monkeypatch.delenv(bootstrap.LEGACY_KNOWLEDGE_SEED_ENV, raising=False)
    monkeypatch.setattr(bootstrap, "ensure_profile_seed_data", lambda session: calls.append("profile"))
    monkeypatch.setattr(bootstrap, "has_published_knowledge_snapshot", lambda session: False)
    monkeypatch.setattr(
        bootstrap,
        "ensure_knowledge_seed_data",
        lambda session: calls.append("legacy"),
    )

    with pytest.raises(RuntimeError, match="published knowledge snapshot is missing"):
        bootstrap.ensure_seed_data(FakeSession())

    assert calls == ["profile"]


def test_seed_data_legacy_catalog_fallback_requires_explicit_flag(monkeypatch) -> None:
    calls = []

    class FakeSession:
        def commit(self) -> None:
            calls.append("commit")

    monkeypatch.setenv(bootstrap.LEGACY_KNOWLEDGE_SEED_ENV, "1")
    monkeypatch.setattr(bootstrap, "ensure_profile_seed_data", lambda session: calls.append("profile"))
    monkeypatch.setattr(bootstrap, "has_published_knowledge_snapshot", lambda session: False)
    monkeypatch.setattr(
        bootstrap,
        "ensure_knowledge_seed_data",
        lambda session: calls.append("legacy"),
    )

    bootstrap.ensure_seed_data(FakeSession())

    assert calls == ["profile", "legacy", "commit"]
