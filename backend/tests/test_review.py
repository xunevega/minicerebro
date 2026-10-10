import json
import random

import pytest
from fastapi.testclient import TestClient

from app.core.models import BlockReviewInput
from app.generation import service as generation
from app.main import app
from app.review import service as review

client = TestClient(app)

TEXT = (
    "Primer bloque con una idea.\n\n"
    "Segundo bloque que se repite y se repite.\n\n"
    "Tercer bloque que no cuadra."
)


def _stub_openai(monkeypatch, payload: dict, captured: dict | None = None):
    class Responses:
        def create(self, **kwargs):
            if captured is not None:
                captured.update(kwargs)

            class Response:
                status = "completed"
                output_text = json.dumps(payload)

            return Response()

    class StubOpenAI:
        def __init__(self):
            self.responses = Responses()

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(generation, "OpenAI", StubOpenAI)


def _model_output(trap_reveal: str = "Mete un dequeismo: 'pienso de que'.") -> dict:
    return {
        "overview": "El bloque 2 contradice al 0.",
        "blocks": [
            {"index": 0, "has_problem": False, "diagnoses": [], "alternatives": []},
            {
                "index": 1,
                "has_problem": True,
                "diagnoses": [{"kind": "pesado", "explanation": "Repite la misma idea."}],
                "alternatives": [
                    {"label": "A", "approach": "poda", "text": "Segundo bloque.", "probe_reveal": ""},
                    {"label": "B", "approach": "ejemplo", "text": "Por ejemplo, ...", "probe_reveal": ""},
                    {"label": "C", "approach": "invierte", "text": "Pienso de que...", "probe_reveal": trap_reveal},
                ],
            },
            {
                "index": 2,
                "has_problem": True,
                "diagnoses": [{"kind": "no_cuadra", "explanation": "Contradice el bloque 0."}],
                "alternatives": [
                    {"label": "A", "approach": "a", "text": "Tercero A.", "probe_reveal": ""},
                    {"label": "B", "approach": "b", "text": "Tercero B.", "probe_reveal": ""},
                    {"label": "C", "approach": "c", "text": "Tercero C.", "probe_reveal": "no deberia salir"},
                ],
            },
        ],
    }


def test_split_blocks_by_paragraph():
    assert review.split_blocks(TEXT) == [
        "Primer bloque con una idea.",
        "Segundo bloque que se repite y se repite.",
        "Tercer bloque que no cuadra.",
    ]


def test_probes_include_traps_and_replanteamientos():
    kinds = set()
    for seed in range(200):
        probes = review.choose_probes(6, random.Random(seed))
        kinds.update(kind for kind, _ in probes.values())
    assert kinds == {"trampa", "replanteamiento"}


def test_long_texts_get_a_probe():
    for seed in range(50):
        assert review.choose_probes(3, random.Random(seed))


def test_review_maps_blocks_and_reveals_only_real_probes(monkeypatch):
    captured: dict = {}
    _stub_openai(monkeypatch, _model_output(), captured)
    monkeypatch.setattr(review, "choose_probes", lambda count, rng: {1: ("trampa", "dequeismo")})

    result = review.review_blocks(BlockReviewInput(text=TEXT, intensity=500))

    assert captured["text"]["format"]["type"] == "json_schema"
    assert "TRAMPA" in captured["input"]
    assert "[1]\nSegundo bloque" in captured["input"]
    assert result.blocks[0].has_problem is False
    trap = result.blocks[1].alternatives[2]
    assert trap.probe is True and trap.probe_kind == "trampa"
    assert "dequeismo" in trap.probe_reveal
    not_probe = result.blocks[2].alternatives[2]
    assert not_probe.probe is False and not_probe.probe_reveal == ""
    assert result.learning_applied is False


def test_review_rejects_long_fragments(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    with pytest.raises(review.ReviewTooLong):
        review.review_blocks(BlockReviewInput(text="pal " * 1501))


def test_review_endpoint_and_choices(monkeypatch):
    _stub_openai(monkeypatch, _model_output())

    response = client.post("/review", json={"text": TEXT, "genre": "ensayo", "intensity": 500})
    assert response.status_code == 200
    assert len(response.json()["blocks"]) == 3

    choices = client.post(
        "/review/choices",
        json={
            "genre": "ensayo",
            "choices": [
                {"block_index": 1, "chosen": "C", "probe": True, "probe_kind": "trampa", "kept_after_reveal": False}
            ],
        },
    )
    assert choices.status_code == 200
    assert choices.json()["recorded"] == 1
    events = client.get("/audit/events").json()
    assert any(event["event_type"] == "review.choices.recorded" for event in events)
    assert all(TEXT not in str(event["payload"]) for event in events)


def test_review_endpoint_reports_long_text_and_model_failure(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    too_long = client.post("/review", json={"text": "pal " * 1501})
    assert too_long.status_code == 422

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    no_key = client.post("/review", json={"text": TEXT})
    assert no_key.status_code == 503
