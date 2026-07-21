from app.core.models import KnowledgeCard, KnowledgeNode, KnowledgeSource


def seed_sources() -> list[KnowledgeSource]:
    return [
        KnowledgeSource(
            id="rae",
            name="Real Academia Espanola",
            source_type="normative",
            authority_level=5,
            priority=1,
            status="registered",
        ),
        KnowledgeSource(
            id="manual-estilo",
            name="Manual interno de rasgos de escritura",
            source_type="academic",
            authority_level=3,
            priority=2,
            status="seed",
        ),
    ]


def seed_nodes() -> list[KnowledgeNode]:
    return [
        KnowledgeNode(
            id="rae-norma-estilo",
            source_id="rae",
            node_type="source_section",
            title="Norma y uso en lengua espanola",
            summary="Nodo semilla para reglas normativas y criterios de uso estable.",
            version="knowledge-v0",
        ),
        KnowledgeNode(
            id="manual-rasgos-escritura",
            source_id="manual-estilo",
            node_type="internal_manual_section",
            title="Rasgos operativos de escritura",
            summary="Nodo semilla para rasgos editables como dinamismo, sobriedad y precision.",
            version="knowledge-v0",
        ),
    ]


def seed_cards() -> list[KnowledgeCard]:
    return [
        KnowledgeCard(
            id="frase-dinamismo",
            card_type="style_trait",
            name="Dinamismo de frase",
            definition="Rasgo asociado a ritmo, avance sintactico y baja friccion de lectura.",
            confidence=0.55,
            version="knowledge-v0",
            payload={
                "signals": ["verbos activos", "oraciones menos acumulativas", "transiciones claras"],
                "risks": ["precipitacion", "perdida de matiz"],
                "contexts": ["articulo", "publicitario", "narrativa"],
            },
        ),
        KnowledgeCard(
            id="lexico-precision",
            card_type="style_trait",
            name="Precision lexica",
            definition="Eleccion de palabras especificas y verificables frente a formulaciones vagas.",
            confidence=0.6,
            version="knowledge-v0",
            payload={
                "signals": ["terminos concretos", "menos comodines", "definiciones operativas"],
                "risks": ["rigidez", "tecnicismo innecesario"],
                "contexts": ["tecnico", "ensayo", "articulo"],
            },
        ),
        KnowledgeCard(
            id="voz-sobriedad",
            card_type="style_trait",
            name="Sobriedad",
            definition="Contencion expresiva que evita enfasis decorativo y conserva autoridad.",
            confidence=0.5,
            version="knowledge-v0",
            payload={
                "signals": ["adjetivacion medida", "tono estable", "poca hipérbole"],
                "risks": ["sequedad", "falta de energia"],
                "contexts": ["ensayo", "tecnico"],
            },
        ),
    ]
