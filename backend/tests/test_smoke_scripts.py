from pathlib import Path

from app.knowledge.catalog import LATEST_PUBLISHED_KNOWLEDGE_VERSION


def test_production_smoke_defaults_track_current_published_knowledge() -> None:
    root_dir = Path(__file__).resolve().parents[2]
    script = (root_dir / "scripts" / "smoke-production.sh").read_text()

    assert f'EXPECTED_VERSION="${{EXPECTED_VERSION:-{LATEST_PUBLISHED_KNOWLEDGE_VERSION}}}"' in script
    assert "lector previsto promesa de lectura ruptura de intencion situacion de lectura" in script
    assert "knowledge-v36" not in script


def test_make_smoke_ui_passes_api_base_to_frontend_tests() -> None:
    root_dir = Path(__file__).resolve().parents[2]
    makefile = (root_dir / "Makefile").read_text()

    assert "API_BASE ?= http://127.0.0.1:8000" in makefile
    assert 'VITE_API_BASE="$(API_BASE)" npm run test:smoke-ui' in makefile
