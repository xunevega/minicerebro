from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_profile_scores_include_effective_value():
    response = client.get("/profiles/default/scores")
    assert response.status_code == 200
    assert "effective_value" in response.json()[0]


def test_preference_interpretation_is_proposed():
    response = client.post(
        "/preferences/interpret",
        json={"text": "Me gusta un estilo sobrio y preciso.", "input_type": "prompt"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "proposed"

