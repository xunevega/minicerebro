from uuid import uuid4

from fastapi.testclient import TestClient

from app.autor.ficha import ficha_prompt
from app.core import security
from app.core.models import PreferenceInput
from app.main import app
from app.preferences.service import interpret_preference

client = TestClient(app)


def _account(monkeypatch, name):
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    security._rate_buckets.clear()
    email = f"{name}-{uuid4().hex[:8]}@example.com"
    response = client.post("/auth/register", json={"email": email, "password": "password12", "name": name})
    assert response.status_code == 200, response.text
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}, email


def test_each_account_keeps_its_own_ficha_with_versions(monkeypatch):
    ana, ana_email = _account(monkeypatch, "ana")
    luis, _ = _account(monkeypatch, "luis")

    assert client.get("/profile/ficha-autor").status_code == 401

    saved = client.put("/profile/ficha-autor", headers=ana, json={
        "presentacion": "Escribo ensayo de opinión, con frases largas y razonadas.",
        "me_gusta": ["frases largas con subordinadas", "frases largas con subordinadas", "  ironía seca "],
        "evito": ["adverbios en -mente"],
        "notas": "",
    })
    assert saved.status_code == 200, saved.text
    assert saved.json()["version"] == 1
    assert saved.json()["editable"]["me_gusta"] == ["frases largas con subordinadas", "ironía seca"]

    client.put("/profile/ficha-autor", headers=ana, json={"presentacion": "Ensayo y columna.", "evito": ["adverbios en -mente"]})
    ficha = client.get("/profile/ficha-autor", headers=ana).json()
    assert ficha["version"] == 2
    assert "Ensayo y columna." in ficha["prompt"]
    assert "adverbios en -mente" in ficha["prompt"]

    # La otra cuenta no ve nada de Ana.
    other = client.get("/profile/ficha-autor", headers=luis).json()
    assert other["version"] == 0 and other["prompt"] == ""

    versions = client.get("/profile/ficha-autor/versiones", headers=ana).json()
    assert [item["version"] for item in versions] == [2, 1]
    restored = client.post("/profile/ficha-autor/restaurar", headers=ana, json={"version": 1})
    assert restored.json()["version"] == 3
    assert "ironía seca" in restored.json()["editable"]["me_gusta"]

    # Se conserva al volver a entrar con correo y contraseña.
    login = client.post("/auth/login", json={"email": ana_email, "password": "password12"})
    again = client.get("/profile/ficha-autor", headers={"Authorization": f"Bearer {login.json()['token']}"}).json()
    assert again["version"] == 3


def test_gustos_reach_the_model_with_the_author_words(monkeypatch):
    ana, _ = _account(monkeypatch, "gustos")
    created = client.post("/preferences", headers=ana, json={"text": "Odio los adverbios terminados en -mente."})
    assert created.status_code == 200, created.text
    preference_id = created.json()["id"]
    accepted = client.patch(f"/preferences/{preference_id}", headers=ana, json={"status": "accepted"})
    assert accepted.status_code == 200, accepted.text
    ficha = client.get("/profile/ficha-autor", headers=ana).json()
    assert "Odio los adverbios terminados en -mente." in ficha["gustos_aceptados"]
    assert "Odio los adverbios terminados en -mente." in ficha["prompt"]


def test_gusto_without_keyword_is_not_forced_into_a_trait():
    preference = interpret_preference(PreferenceInput(text="Odio los adverbios terminados en -mente."))
    assert preference.affected_variables == []


def test_prompt_is_empty_without_data_and_traits_are_words():
    compiled = {
        "editable": {"presentacion": "", "me_gusta": [], "evito": [], "notas": ""},
        "gustos_aceptados": [], "gustos_rechazados": [], "posturas": [], "linea_guia": [],
        "rasgos": [{"clave": "sobriedad", "texto": "sobriedad", "nivel": "media", "seguridad": 0.9, "propio": True}],
    }
    assert ficha_prompt(compiled) == ""
    compiled["rasgos"][0]["nivel"] = "alta"
    assert "sobriedad: alta" in ficha_prompt(compiled)
