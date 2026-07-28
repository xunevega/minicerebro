from pathlib import Path


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
