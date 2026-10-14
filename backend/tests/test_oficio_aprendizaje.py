import random

from fastapi.testclient import TestClient

from app.db.models import AuditEventRecord
from app.db.session import SessionLocal
from app.main import app
from app.oficio import select_fichas
from app.oficio.aprendizaje import build_line, line_prompt
from app.review import service as review

client = TestClient(app)


def _reset():
    with SessionLocal() as session:
        session.query(AuditEventRecord).filter(
            AuditEventRecord.event_type.in_(["generation.outcome", "review.choices.recorded"])
        ).delete(synchronize_session=False)
        session.commit()


def _current_profile():
    with SessionLocal() as session:
        row = session.query(AuditEventRecord).filter(
            AuditEventRecord.event_type.in_(["generation.outcome", "review.choices.recorded"])
        ).order_by(AuditEventRecord.id.desc()).first()
        return row.entity_id if row else None


def _choices(items):
    response = client.post(
        "/review/choices",
        json={"context": "general", "genre": "ensayo", "intensity": 500, "choices": items},
    )
    assert response.status_code == 200
    assert response.json()["learning_applied"] is True


def test_outcomes_teach_which_fichas_work_with_you():
    _reset()
    for _ in range(4):
        client.post("/generation/outcome", json={
            "decision": "accepted", "fichas": ["ejemplo-concreto", "redundancia-real"],
            "no_aplicadas": ["redundancia-real"], "action": "rewrite",
        })
    for _ in range(4):
        client.post("/generation/outcome", json={
            "decision": "discarded", "fichas": ["intensificadores"],
            "action": "rewrite",
        })
    data = client.get("/profile/linea-editorial").json()
    fichas = {item["id"]: item for item in data["fichas"]}
    assert data["propuestas"] == {"aceptadas": 4, "descartadas": 4}
    assert fichas["ejemplo-concreto"]["peso"] > 1.0
    assert fichas["intensificadores"]["peso"] < -1.0
    # Una ficha que acompañó pero no se aplicó pesa poco.
    assert "redundancia-real" not in fichas or fichas["redundancia-real"]["peso"] < fichas["ejemplo-concreto"]["peso"]
    assert fichas["ejemplo-concreto"]["nombre"]

    with SessionLocal() as session:
        linea = build_line(session, _current_profile())
    text = "Las cosas eran muy muy importantes y realmente muy decisivas para todos."
    plain = select_fichas(text, "rewrite")
    learned = select_fichas(text, "rewrite", learned=linea.pesos())
    rank = lambda items, ficha_id: [i.ficha.id for i in items].index(ficha_id) if ficha_id in [i.ficha.id for i in items] else 99
    assert rank(learned, "ejemplo-concreto") <= rank(plain, "ejemplo-concreto")
    assert rank(learned, "intensificadores") >= rank(plain, "intensificadores")


def test_review_choices_build_an_editorial_line_and_detect_changes():
    _reset()
    early = [
        {"block_index": i, "chosen": "A", "diagnosis_kinds": ["pesado"], "approach": "recorta y condensa la idea"}
        for i in range(10)
    ]
    _choices(early)
    _choices([
        {"block_index": 1, "chosen": "C", "probe": True, "probe_kind": "trampa", "probe_move": "sentido"},
        {"block_index": 2, "chosen": "C", "probe": True, "probe_kind": "trampa", "probe_move": "sentido"},
        {"block_index": 3, "chosen": "A", "probe_kind": "ofrecida:replanteamiento", "probe_move": "invertir", "approach": "ordena"},
        {"block_index": 4, "chosen": "A", "probe_kind": "ofrecida:replanteamiento", "probe_move": "voz", "approach": "ordena"},
        {"block_index": 5, "chosen": "A", "probe_kind": "ofrecida:replanteamiento", "probe_move": "partir", "approach": "ordena"},
    ])
    recent = [
        {"block_index": i, "chosen": "B", "diagnosis_kinds": ["falta_fuerza"], "approach": "lo convierte en un ejemplo concreto"}
        for i in range(10)
    ]
    _choices(recent)
    # Deshacer la trampa tras la revelación no cuenta como elección nueva.
    _choices([{"block_index": 1, "chosen": "C", "probe": True, "probe_kind": "trampa", "probe_move": "sentido", "kept_after_reveal": False}])

    data = client.get("/profile/linea-editorial").json()
    claves = {item["clave"] for item in data["tendencias"]}
    assert data["elecciones"] == 25
    assert "trampa:sentido" in claves
    assert "replanteamientos" in claves and data["apertura_replanteamiento"] == 0.0
    assert any("concretan" in cambio and "más" in cambio for cambio in data["cambios"])
    fichas = {item["id"]: item for item in data["fichas"]}
    assert fichas["matices-protegidos"]["peso"] >= 2.0

    with SessionLocal() as session:
        linea = build_line(session, _current_profile())
    prompt = line_prompt(linea)
    assert prompt.startswith("Línea editorial del autor")
    assert "no ver cambios de sentido" in prompt


def test_openness_changes_how_many_reframings_review_offers():
    def replan_count(apertura):
        total = 0
        for seed in range(300):
            probes = review.choose_probes(6, random.Random(seed), apertura=apertura)
            total += sum(1 for kind, _move in probes.values() if kind == "replanteamiento")
        return total

    assert replan_count(0.0) < replan_count(None) < replan_count(1.0)
    kinds = {review.move_key(kind, move) for seed in range(50) for kind, move in review.choose_probes(6, random.Random(seed)).values()}
    assert {"norma", "sentido", "orden", "topico"} & kinds
