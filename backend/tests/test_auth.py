from fastapi.testclient import TestClient

from app.core import security
from app.main import app

client = TestClient(app)


def test_register_login_and_profile_isolation(monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("CORS_ALLOW_LOCALHOST", "false")
    monkeypatch.setenv("ENABLE_DOCS", "false")
    security._rate_buckets.clear()

    first = client.post(
        "/auth/register",
        json={"email": "ana@example.com", "password": "password12", "name": "Ana"},
    )
    assert first.status_code == 200, first.text
    first_token = first.json()["token"]
    first_profile = first.json()["user"]["profile_id"]
    assert first.json()["user"]["role"] == "admin"

    second = client.post(
        "/auth/register",
        json={"email": "luis@example.com", "password": "password12", "name": "Luis"},
    )
    assert second.status_code == 200, second.text
    second_token = second.json()["token"]
    assert second.json()["user"]["role"] == "user"

    mine = client.get("/preferences", headers={"Authorization": f"Bearer {first_token}"})
    assert mine.status_code == 200
    assert mine.json() == []

    created = client.post(
        "/preferences",
        headers={"Authorization": f"Bearer {first_token}"},
        json={"text": "Quiero frases cortas y precisas.", "input_type": "prompt", "context": "general"},
    )
    assert created.status_code == 200, created.text

    other = client.get("/preferences", headers={"Authorization": f"Bearer {second_token}"})
    assert other.status_code == 200
    assert other.json() == []

    forbidden = client.get(
        f"/profiles/{first_profile}/export",
        headers={"Authorization": f"Bearer {second_token}"},
    )
    assert forbidden.status_code == 403

    anonymous = client.get("/preferences")
    assert anonymous.status_code == 401

    forbidden_write = client.post(
        "/knowledge/candidates",
        headers={"Authorization": f"Bearer {second_token}"},
        json={
            "id": "knowledge-candidate-blocked",
            "base_version": "latest",
            "author": "Luis",
            "reason": "no debe publicar",
        },
    )
    assert forbidden_write.status_code == 403
    assert not security.docs_enabled()


def test_production_cors_omits_localhost(monkeypatch):
    from app import main

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("CORS_ALLOW_LOCALHOST", "false")
    monkeypatch.setenv(
        "CORS_ALLOW_ORIGINS",
        "https://frontend-production-834c.up.railway.app",
    )
    assert main.cors_allow_origins() == [
        "https://frontend-production-834c.up.railway.app",
    ]


def test_login_rejects_bad_password():
    created = client.post(
        "/auth/register",
        json={"email": "nora@example.com", "password": "password12"},
    )
    assert created.status_code == 200
    response = client.post(
        "/auth/login",
        json={"email": "nora@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401
