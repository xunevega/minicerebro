from app.knowledge.contracts import LATEST_KNOWLEDGE_VERSION
from app.knowledge.snapshot_data import load_knowledge_seed_snapshot


MINIMAL_EDITORIAL_LIBRARY = {
    "coherencia_texto_largo": {
        "card-idea-rectora-texto-largo",
        "card-continuidad-de-voz",
        "card-deriva-de-estilo",
        "card-contradiccion-interna",
        "card-progresion-global",
    },
    "conectores_transiciones": {
        "card-transicion-de-idea",
        "card-conector-con-funcion",
        "card-parrafo-puente",
        "card-orden-de-argumentos",
        "card-cierre-y-apertura",
    },
    "sinonimia_palabra_precisa": {
        "card-palabra-precisa-en-contexto",
        "card-sinonimo-con-matiz",
        "card-antonimo-para-contraste",
        "card-evitar-repeticion-mala",
        "card-registro-de-palabra",
    },
    "puntuacion_avanzada": {
        "card-coma-de-inciso",
        "card-punto-y-coma-en-serie-compleja",
        "card-dos-puntos-explicativos-aplicados",
        "card-puntuacion-de-frase-larga",
        "card-enumeracion-con-criterio",
    },
    "revision_parrafo": {
        "card-diagnostico-de-parrafo",
        "card-unidad-de-parrafo-aplicada",
        "card-avance-de-parrafo",
        "card-parrafo-puente-aplicado",
        "card-cierre-de-parrafo-aplicado",
    },
    "argumentacion": {
        "card-tesis-visible-en-borrador",
        "card-razon-que-no-repite",
        "card-ejemplo-anclado-a-la-tesis",
        "card-objecion-y-respuesta",
        "card-cierre-argumentativo",
    },
    "narrativa_practica": {
        "card-escena-con-objetivo",
        "card-punto-de-vista-estable",
        "card-tension-progresiva",
        "card-ritmo-narrativo-practico",
        "card-personaje-por-decision",
    },
    "estilo_editorial": {
        "card-uniformidad-editorial",
        "card-criterio-de-correccion",
        "card-limpieza-sin-borrar-voz",
        "card-sobriedad-aplicada",
    },
    "diagnostico_borrador": {
        "card-problema-dominante-del-borrador",
        "card-escala-de-revision",
        "card-foco-y-promesa",
        "card-exceso-o-falta",
    },
    "lectura_pragmatica": {
        "card-lector-previsto",
        "card-promesa-de-lectura",
        "card-ruptura-de-intencion",
        "card-situacion-de-lectura",
    },
}


def test_latest_snapshot_contains_minimal_editorial_library_with_traceability():
    snapshot = load_knowledge_seed_snapshot(LATEST_KNOWLEDGE_VERSION)
    tables = snapshot["tables"]
    published_snapshot = next(
        row
        for row in tables["knowledge_version_snapshots"]
        if row["version_id"] == LATEST_KNOWLEDGE_VERSION
    )
    published_card_ids = set(published_snapshot["card_ids"])
    cards = {row["id"]: row for row in tables["knowledge_cards"]}
    claims_by_card = {
        row["card_id"]: row for row in tables["knowledge_claims"] if row["status"] == "published"
    }
    evidence_by_id = {
        row["id"]: row
        for row in tables["knowledge_evidence_items"]
        if row["status"] == "published"
    }
    sources_by_id = {row["id"]: row for row in tables["knowledge_sources"]}

    assert snapshot["version"] == LATEST_KNOWLEDGE_VERSION
    assert len(MINIMAL_EDITORIAL_LIBRARY) == 10

    for area_name, expected_card_ids in MINIMAL_EDITORIAL_LIBRARY.items():
        assert expected_card_ids <= published_card_ids, area_name
        for card_id in expected_card_ids:
            card = cards[card_id]
            assert card["definition"].strip(), card_id
            assert card["payload"]["signals"], card_id
            assert card["payload"]["risks"], card_id

            claim = claims_by_card[card_id]
            assert claim["statement"].strip(), card_id

            evidence = evidence_by_id[claim["evidence_id"]]
            assert evidence["excerpt"].strip(), card_id
            assert evidence["source_id"] in sources_by_id, card_id
