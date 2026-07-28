from pathlib import Path

import pytest

from app.knowledge.catalog import LATEST_PUBLISHED_KNOWLEDGE_VERSION
from app.knowledge.snapshot_data import (
    knowledge_snapshot_path,
    load_knowledge_seed_snapshot,
)


def test_static_knowledge_catalog_is_separate_from_runtime_service() -> None:
    root_dir = Path(__file__).resolve().parents[1]
    service_source = (root_dir / "app" / "knowledge" / "service.py").read_text()
    catalog_source = (root_dir / "app" / "knowledge" / "catalog.py").read_text()

    assert "def query_knowledge(" in service_source
    assert "V51_SEED_ITEMS = [" not in service_source
    assert "def seed_sources(" not in service_source
    assert "V51_SEED_ITEMS = [" in catalog_source
    assert "def seed_sources(" in catalog_source


def test_bootstrap_reads_knowledge_seed_from_catalog() -> None:
    root_dir = Path(__file__).resolve().parents[1]
    bootstrap_source = (root_dir / "app" / "db" / "bootstrap.py").read_text()

    assert "from app.knowledge.catalog import (" in bootstrap_source
    assert "from app.knowledge.service import (" not in bootstrap_source


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
