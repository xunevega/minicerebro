import hashlib
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.db.models import KnowledgeVersionSnapshotRecord
from app.db.session import SessionLocal
from app.main import app


client = TestClient(app)
REPO_ROOT = Path(__file__).resolve().parents[2]


CURRENT_PUBLISHED_VERSION = "knowledge-v51"
CURRENT_PUBLISHED_COUNTS = {
    "source_count": 26,
    "node_count": 237,
    "evidence_count": 235,
    "claim_count": 235,
    "card_count": 235,
}


def test_current_published_knowledge_version_is_frozen_before_data_migration() -> None:
    response = client.get("/knowledge/versions")

    assert response.status_code == 200
    versions = {item["id"]: item for item in response.json()}
    current = versions[CURRENT_PUBLISHED_VERSION]
    assert current["status"] == "published"
    assert current["published_at"] == "2026-07-27T17:00:00+00:00"
    for field, expected_count in CURRENT_PUBLISHED_COUNTS.items():
        assert current[field] == expected_count

    with SessionLocal() as session:
        snapshot = session.get(KnowledgeVersionSnapshotRecord, CURRENT_PUBLISHED_VERSION)

    assert snapshot is not None
    assert snapshot.status == "published"
    assert len(snapshot.source_ids) == CURRENT_PUBLISHED_COUNTS["source_count"]
    assert len(snapshot.node_ids) == CURRENT_PUBLISHED_COUNTS["node_count"]
    assert len(snapshot.evidence_ids) == CURRENT_PUBLISHED_COUNTS["evidence_count"]
    assert len(snapshot.claim_ids) == CURRENT_PUBLISHED_COUNTS["claim_count"]
    assert len(snapshot.card_ids) == CURRENT_PUBLISHED_COUNTS["card_count"]
    assert {
        "card-coherencia-textual",
        "card-transicion-de-idea",
        "card-palabra-precisa-en-contexto",
        "card-puntuacion-de-frase-larga",
        "card-diagnostico-de-parrafo",
        "card-tesis-visible-en-borrador",
        "card-escena-narrativa-funcional",
        "card-uniformidad-editorial",
        "card-problema-dominante-del-borrador",
        "card-promesa-de-lectura",
    } <= set(snapshot.card_ids)


def test_current_published_queries_are_frozen_before_data_migration() -> None:
    cases = [
        (
            "continuidad de voz deriva de estilo contradicciones progresion global",
            {
                "card-coherencia-textual",
                "card-deriva-de-estilo",
                "card-contradiccion-interna",
                "card-progresion-global",
            },
        ),
        (
            "necesito conectar una idea con otra y ordenar la transicion",
            {
                "card-transicion-de-idea",
                "card-conector-con-funcion",
                "card-orden-de-argumentos",
            },
        ),
        (
            "buscar una palabra precisa con sinonimos antonimos matiz y registro",
            {
                "card-palabra-precisa-en-contexto",
                "card-sinonimo-con-matiz",
                "card-antonimo-para-contraste",
                "card-registro-de-palabra",
            },
        ),
        (
            "lector previsto promesa de lectura ruptura de intencion situacion de lectura",
            {
                "card-lector-previsto",
                "card-promesa-de-lectura",
                "card-ruptura-de-intencion",
                "card-situacion-de-lectura",
            },
        ),
    ]

    for query, expected_cards in cases:
        response = client.post(
            "/knowledge/query",
            json={"query": query, "version": CURRENT_PUBLISHED_VERSION, "limit": 10},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["requested_version"] == CURRENT_PUBLISHED_VERSION
        assert payload["resolved_version"] == CURRENT_PUBLISHED_VERSION
        assert payload["version"] == CURRENT_PUBLISHED_VERSION
        assert payload["status"] == "ok"
        assert expected_cards & {card["id"] for card in payload["cards"]}
        assert {card["version"] for card in payload["cards"]} == {CURRENT_PUBLISHED_VERSION}
        assert {claim["version"] for claim in payload["claims"]} == {CURRENT_PUBLISHED_VERSION}
        assert {item["version"] for item in payload["evidence"]} == {CURRENT_PUBLISHED_VERSION}


def test_current_published_snapshot_export_is_reproducible(tmp_path) -> None:
    expected = (
        REPO_ROOT
        / "backend"
        / "app"
        / "knowledge"
        / "data"
        / f"{CURRENT_PUBLISHED_VERSION}.snapshot.json"
    )
    generated = tmp_path / f"{CURRENT_PUBLISHED_VERSION}.snapshot.json"

    subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "export-knowledge-snapshot.py"),
            "--version",
            CURRENT_PUBLISHED_VERSION,
            "--output",
            str(generated),
        ],
        check=True,
        cwd=REPO_ROOT,
    )

    assert _file_sha256(generated) == _file_sha256(expected)


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
