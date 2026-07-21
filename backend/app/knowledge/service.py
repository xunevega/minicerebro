from app.core.models import (
    KnowledgeCard,
    KnowledgeClaim,
    KnowledgeEvidenceItem,
    KnowledgeNode,
    KnowledgeQueryInput,
    KnowledgeQueryResult,
    KnowledgeSource,
    KnowledgeVersion,
)

KNOWLEDGE_VERSION = "knowledge-v0"


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
            version=KNOWLEDGE_VERSION,
        ),
        KnowledgeNode(
            id="manual-rasgos-escritura",
            source_id="manual-estilo",
            node_type="internal_manual_section",
            title="Rasgos operativos de escritura",
            summary="Nodo semilla para rasgos editables como dinamismo, sobriedad y precision.",
            version=KNOWLEDGE_VERSION,
        ),
    ]


def seed_evidence() -> list[KnowledgeEvidenceItem]:
    return [
        KnowledgeEvidenceItem(
            id="ev-precision-lexica",
            node_id="rae-norma-estilo",
            source_id="rae",
            reference="registro normativo semilla",
            excerpt="La precision lexica reduce ambiguedad y mejora verificabilidad.",
            confidence=0.58,
            version=KNOWLEDGE_VERSION,
        ),
        KnowledgeEvidenceItem(
            id="ev-dinamismo-frase",
            node_id="manual-rasgos-escritura",
            source_id="manual-estilo",
            reference="manual interno, rasgos de frase",
            excerpt="El dinamismo aumenta cuando la frase avanza con verbos activos y menos acumulacion.",
            confidence=0.52,
            version=KNOWLEDGE_VERSION,
        ),
        KnowledgeEvidenceItem(
            id="ev-sobriedad-voz",
            node_id="manual-rasgos-escritura",
            source_id="manual-estilo",
            reference="manual interno, rasgos de voz",
            excerpt="La sobriedad depende de contencion expresiva y baja ornamentacion.",
            confidence=0.5,
            version=KNOWLEDGE_VERSION,
        ),
    ]


def seed_claims() -> list[KnowledgeClaim]:
    return [
        KnowledgeClaim(
            id="claim-dinamismo-frase",
            evidence_id="ev-dinamismo-frase",
            card_id="frase-dinamismo",
            statement="El dinamismo de frase se asocia a avance sintactico y verbos activos.",
            confidence=0.52,
            version=KNOWLEDGE_VERSION,
        ),
        KnowledgeClaim(
            id="claim-precision-lexica",
            evidence_id="ev-precision-lexica",
            card_id="lexico-precision",
            statement="La precision lexica favorece formulaciones concretas y verificables.",
            confidence=0.58,
            version=KNOWLEDGE_VERSION,
        ),
        KnowledgeClaim(
            id="claim-sobriedad-voz",
            evidence_id="ev-sobriedad-voz",
            card_id="voz-sobriedad",
            statement="La sobriedad reduce enfasis decorativo y mantiene autoridad tonal.",
            confidence=0.5,
            version=KNOWLEDGE_VERSION,
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
            version=KNOWLEDGE_VERSION,
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
            version=KNOWLEDGE_VERSION,
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
            version=KNOWLEDGE_VERSION,
            payload={
                "signals": ["adjetivacion medida", "tono estable", "poca hipérbole"],
                "risks": ["sequedad", "falta de energia"],
                "contexts": ["ensayo", "tecnico"],
            },
        ),
    ]


def seed_versions() -> list[KnowledgeVersion]:
    return [
        KnowledgeVersion(
            id=KNOWLEDGE_VERSION,
            status="seed",
            published_at="not-published",
            source_count=len(seed_sources()),
            node_count=len(seed_nodes()),
            evidence_count=len(seed_evidence()),
            claim_count=len(seed_claims()),
            card_count=len(seed_cards()),
        )
    ]


def query_knowledge(payload: KnowledgeQueryInput) -> KnowledgeQueryResult:
    terms = {term for term in payload.query.lower().split() if len(term) > 2}
    cards = seed_cards()
    claims = seed_claims()
    evidence = seed_evidence()

    def score_card(card: KnowledgeCard) -> int:
        haystack = " ".join(
            [
                card.id,
                card.card_type,
                card.name,
                card.definition,
                " ".join(str(value) for value in card.payload.values()),
            ]
        ).lower()
        return sum(1 for term in terms if term in haystack)

    ranked_cards = [
        card
        for card in sorted(cards, key=score_card, reverse=True)
        if score_card(card) > 0 and card.version == payload.version
    ][: payload.limit]
    card_ids = {card.id for card in ranked_cards}
    matched_claims = [
        claim for claim in claims if claim.card_id in card_ids and claim.version == payload.version
    ]
    evidence_ids = {claim.evidence_id for claim in matched_claims}
    matched_evidence = [
        item for item in evidence if item.id in evidence_ids and item.version == payload.version
    ]
    return KnowledgeQueryResult(
        query=payload.query,
        version=payload.version,
        cards=ranked_cards,
        claims=matched_claims,
        evidence=matched_evidence,
    )
