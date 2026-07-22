from app.core.models import (
    KnowledgeCard,
    KnowledgeClaim,
    KnowledgeClaimEvidenceLink,
    KnowledgeEvidenceItem,
    KnowledgeNode,
    KnowledgeNodeRelation,
    KnowledgeQueryInput,
    KnowledgeQueryResult,
    KnowledgeRelation,
    KnowledgeSource,
    KnowledgeSourceEdition,
    KnowledgeVersion,
)

KNOWLEDGE_VERSION = "knowledge-v0"
KNOWLEDGE_PUBLISHED_AT = "2026-07-22"
RELATION_UPDATED_AT = "2026-07-23"

DEFAULT_SOURCE_EDITION = "pendiente de identificacion"
DEFAULT_SOURCE_PUBLICATION_DATE = "pendiente de identificacion"
DEFAULT_SOURCE_LOCATION = "pendiente de adquisicion"
DEFAULT_SOURCE_RIGHTS = "registro autorizado; contenido no ingerido"
DEFAULT_SOURCE_STRUCTURE = ["pendiente de estructuracion"]
DEFAULT_SOURCE_LOCATORS = ["edicion", "parte", "capitulo", "seccion", "pagina", "entrada", "url"]


def _source(
    *,
    catalog_id: str,
    source_id: str,
    name: str,
    responsible: str,
    source_type: str,
    domains: list[str],
    authority_level: int,
    priority: int,
) -> KnowledgeSource:
    return KnowledgeSource(
        id=source_id,
        catalog_id=catalog_id,
        name=name,
        responsible=responsible,
        source_type=source_type,
        domains=domains,
        authority_level=authority_level,
        priority=priority,
        status="registered",
        edition=DEFAULT_SOURCE_EDITION,
        publication_date=DEFAULT_SOURCE_PUBLICATION_DATE,
        location=DEFAULT_SOURCE_LOCATION,
        acquisition_status="registered",
        validation_status="not_validated",
        rights=DEFAULT_SOURCE_RIGHTS,
        structure=DEFAULT_SOURCE_STRUCTURE,
        locator_system=DEFAULT_SOURCE_LOCATORS,
    )


def seed_sources() -> list[KnowledgeSource]:
    return [
        _source(
            catalog_id="F001",
            source_id="rae-ngle",
            name="Nueva gramatica de la lengua espanola",
            responsible="Real Academia Espanola y Asociacion de Academias de la Lengua Espanola",
            source_type="gramatica descriptiva y normativa",
            domains=[
                "morfologia",
                "sintaxis",
                "categorias gramaticales",
                "funciones",
                "construcciones",
            ],
            authority_level=5,
            priority=1,
        ),
        _source(
            catalog_id="F002",
            source_id="rae-gtg",
            name="Glosario de terminos gramaticales",
            responsible="Real Academia Espanola y Asociacion de Academias de la Lengua Espanola",
            source_type="glosario gramatical especializado",
            domains=["terminologia gramatical", "relaciones conceptuales"],
            authority_level=5,
            priority=1,
        ),
        _source(
            catalog_id="F003",
            source_id="rae-ole",
            name="Ortografia de la lengua espanola",
            responsible="Real Academia Espanola y Asociacion de Academias de la Lengua Espanola",
            source_type="ortografia normativa",
            domains=["grafias", "acentuacion", "puntuacion", "mayusculas", "ortotipografia"],
            authority_level=5,
            priority=1,
        ),
        _source(
            catalog_id="F004",
            source_id="rae-dpd",
            name="Diccionario panhispanico de dudas",
            responsible="Real Academia Espanola y Asociacion de Academias de la Lengua Espanola",
            source_type="repertorio normativo de dudas",
            domains=["gramatica", "ortografia", "lexico", "extranjerismos", "dudas de uso"],
            authority_level=5,
            priority=1,
        ),
        _source(
            catalog_id="F005",
            source_id="rae-dle",
            name="Diccionario de la lengua espanola",
            responsible="Real Academia Espanola y Asociacion de Academias de la Lengua Espanola",
            source_type="diccionario general",
            domains=["lexico", "acepciones", "categorias", "locuciones", "marcas de uso"],
            authority_level=5,
            priority=1,
        ),
        _source(
            catalog_id="F006",
            source_id="rae-lese",
            name="Libro de estilo de la lengua espanola segun la norma panhispanica",
            responsible="Real Academia Espanola y Asociacion de Academias de la Lengua Espanola",
            source_type="manual institucional de estilo",
            domains=["redaccion", "escritura digital", "ortotipografia", "comunicacion"],
            authority_level=4,
            priority=2,
        ),
        _source(
            catalog_id="F007",
            source_id="rae-corpes",
            name="CORPES XXI",
            responsible="Real Academia Espanola y Asociacion de Academias de la Lengua Espanola",
            source_type="corpus linguistico",
            domains=["frecuencia", "distribucion", "registro", "pais", "genero", "contexto"],
            authority_level=4,
            priority=2,
        ),
        _source(
            catalog_id="F008",
            source_id="reyes-arte-escribir",
            name="El arte de escribir bien en espanol",
            responsible="Graciela Reyes",
            source_type="manual de redaccion y gramatica aplicada",
            domains=["redaccion", "pragmatica", "coherencia", "construccion textual", "estilo"],
            authority_level=4,
            priority=2,
        ),
        _source(
            catalog_id="F009",
            source_id="martinez-sousa-mele",
            name="Manual de estilo de la lengua espanola",
            responsible="Jose Martinez de Sousa",
            source_type="manual de estilo y edicion",
            domains=["estilo", "edicion", "ortotipografia", "presentacion"],
            authority_level=4,
            priority=2,
        ),
        _source(
            catalog_id="F010",
            source_id="fundeu-recomendaciones",
            name="Recomendaciones de FundeuRAE",
            responsible="FundeuRAE",
            source_type="recomendaciones de uso actual",
            domains=["neologismos", "tecnologia", "medios", "extranjerismos", "actualidad"],
            authority_level=3,
            priority=2,
        ),
        _source(
            catalog_id="F011",
            source_id="aristoteles-retorica",
            name="Retorica",
            responsible="Aristoteles",
            source_type="retorica clasica",
            domains=["persuasion", "argumentacion", "generos retoricos", "ethos", "pathos", "logos"],
            authority_level=5,
            priority=3,
        ),
        _source(
            catalog_id="F012",
            source_id="quintiliano-institutio",
            name="Institutio oratoria",
            responsible="Marco Fabio Quintiliano",
            source_type="retorica clasica",
            domains=["formacion del orador", "construccion del discurso", "estilo", "elocucion"],
            authority_level=5,
            priority=3,
        ),
        _source(
            catalog_id="F013",
            source_id="carnegie-hablar-publico",
            name="Como hablar bien en publico e influir en los hombres de negocios",
            responsible="Dale Carnegie",
            source_type="comunicacion oral y divulgacion practica",
            domains=["discurso oral", "exposicion", "audiencia", "comunicacion practica"],
            authority_level=3,
            priority=4,
        ),
        _source(
            catalog_id="F014",
            source_id="aristoteles-poetica",
            name="Poetica",
            responsible="Aristoteles",
            source_type="teoria literaria clasica",
            domains=["mimesis", "trama", "personaje", "tragedia", "reconocimiento", "peripecia"],
            authority_level=5,
            priority=3,
        ),
        _source(
            catalog_id="F015",
            source_id="wellek-warren-teoria-literatura",
            name="Teoria de la literatura",
            responsible="Rene Wellek y Austin Warren",
            source_type="manual general de teoria literaria",
            domains=["teoria literaria", "generos", "analisis", "historia", "critica"],
            authority_level=4,
            priority=3,
        ),
        _source(
            catalog_id="F016",
            source_id="genette-figuras-iii",
            name="Figuras III",
            responsible="Gerard Genette",
            source_type="narratologia",
            domains=["tiempo", "modo", "voz", "orden", "duracion", "frecuencia"],
            authority_level=5,
            priority=2,
        ),
        _source(
            catalog_id="F017",
            source_id="genette-discurso-relato",
            name="Discurso del relato",
            responsible="Gerard Genette",
            source_type="narratologia",
            domains=["estructura narrativa", "tiempo", "modo", "voz"],
            authority_level=5,
            priority=2,
        ),
        _source(
            catalog_id="F018",
            source_id="saussure-curso-linguistica",
            name="Curso de linguistica general",
            responsible="Ferdinand de Saussure",
            source_type="linguistica general",
            domains=["signo", "lengua", "habla", "sincronia", "diacronia"],
            authority_level=5,
            priority=3,
        ),
        _source(
            catalog_id="F019",
            source_id="chomsky-aspects",
            name="Aspectos de la teoria de la sintaxis",
            responsible="Noam Chomsky",
            source_type="teoria linguistica y sintaxis generativa",
            domains=["competencia", "actuacion", "estructura profunda", "gramatica generativa"],
            authority_level=4,
            priority=4,
        ),
        _source(
            catalog_id="F020",
            source_id="strunk-white-elements-style",
            name="The Elements of Style",
            responsible="William Strunk Jr. y E. B. White",
            source_type="manual de estilo en lengua inglesa",
            domains=["concision", "claridad", "edicion", "revision"],
            authority_level=3,
            priority=4,
        ),
        _source(
            catalog_id="F021",
            source_id="zinsser-on-writing-well",
            name="On Writing Well",
            responsible="William Zinsser",
            source_type="escritura de no ficcion",
            domains=["claridad", "sencillez", "voz", "revision", "no ficcion"],
            authority_level=4,
            priority=3,
        ),
        _source(
            catalog_id="F022",
            source_id="lazaro-correa-comentario-texto",
            name="Como se comenta un texto literario",
            responsible="Fernando Lazaro Carreter y Evaristo Correa Calderon",
            source_type="analisis y comentario de textos",
            domains=["lectura", "analisis", "estructura", "tema", "forma", "comentario literario"],
            authority_level=4,
            priority=3,
        ),
        _source(
            catalog_id="F023",
            source_id="martinez-sousa-ortotipografia",
            name="Ortografia y ortotipografia del espanol actual",
            responsible="Jose Martinez de Sousa",
            source_type="ortografia y ortotipografia especializada",
            domains=["edicion", "tipografia", "signos", "composicion", "convenciones graficas"],
            authority_level=4,
            priority=2,
        ),
    ]


def seed_source_editions() -> list[KnowledgeSourceEdition]:
    return [
        KnowledgeSourceEdition(
            id=f"{source.id}:pending-edition",
            source_id=source.id,
            label=source.edition,
            publication_date=source.publication_date,
            location=source.location,
            acquisition_status=source.acquisition_status,
            validation_status=source.validation_status,
            rights=source.rights,
            structure=source.structure,
            locator_system=source.locator_system,
        )
        for source in seed_sources()
    ]


def seed_nodes() -> list[KnowledgeNode]:
    return [
        KnowledgeNode(
            id="rae-norma-estilo",
            source_id="rae-ngle",
            node_type="norma",
            title="Norma y uso en lengua espanola",
            summary="Nodo semilla para reglas normativas y criterios de uso estable.",
            canonical_name="Norma y uso en lengua espanola",
            primary_branch="lengua espanola",
            secondary_branch="norma y uso",
            short_definition="Concepto que agrupa criterios normativos y descriptivos estables.",
            long_definition=(
                "Nodo conceptual publicado para conectar fuentes academicas registradas, "
                "evidencias normativas y claims sobre uso estable de la lengua espanola."
            ),
            status="published",
            version=KNOWLEDGE_VERSION,
            created_at=KNOWLEDGE_PUBLISHED_AT,
            published_at=KNOWLEDGE_PUBLISHED_AT,
            aliases=["criterio normativo", "uso estable"],
        ),
        KnowledgeNode(
            id="manual-rasgos-escritura",
            source_id="rae-lese",
            node_type="categoria",
            title="Aplicacion practica de estilo",
            summary="Nodo semilla para rasgos de redaccion, estilo, dinamismo y sobriedad.",
            canonical_name="Aplicacion practica de estilo",
            primary_branch="escritura",
            secondary_branch="estilo",
            short_definition="Concepto que agrupa criterios practicos de estilo aplicados a escritura.",
            long_definition=(
                "Nodo conceptual publicado para conectar fuentes de estilo registradas, "
                "evidencias de redaccion y claims sobre dinamismo, sobriedad y claridad."
            ),
            status="published",
            version=KNOWLEDGE_VERSION,
            created_at=KNOWLEDGE_PUBLISHED_AT,
            published_at=KNOWLEDGE_PUBLISHED_AT,
            aliases=["criterio de estilo", "redaccion aplicada"],
        ),
    ]


def seed_node_relations() -> list[KnowledgeNodeRelation]:
    return [
        KnowledgeNodeRelation(
            id="rel-norma-define-estilo",
            source_node_id="rae-norma-estilo",
            target_node_id="manual-rasgos-escritura",
            relation_type="define",
            direction="outgoing",
            cardinality="N:N",
            weight=0.72,
            confidence=0.58,
            context="knowledge_graph",
            status="published",
            version=KNOWLEDGE_VERSION,
            created_at=KNOWLEDGE_PUBLISHED_AT,
            updated_at=RELATION_UPDATED_AT,
        ),
        KnowledgeNodeRelation(
            id="rel-estilo-depende-norma",
            source_node_id="manual-rasgos-escritura",
            target_node_id="rae-norma-estilo",
            relation_type="depende_de",
            direction="outgoing",
            cardinality="N:N",
            weight=0.68,
            confidence=0.58,
            context="knowledge_graph",
            status="published",
            version=KNOWLEDGE_VERSION,
            created_at=KNOWLEDGE_PUBLISHED_AT,
            updated_at=RELATION_UPDATED_AT,
        ),
    ]


def _relation(
    source_type: str,
    source_id: str,
    relation_type: str,
    target_type: str,
    target_id: str,
    *,
    cardinality: str = "N:N",
    weight: float = 1.0,
    confidence: float = 0.58,
    context: str = "knowledge_graph",
    status: str = "published",
) -> KnowledgeRelation:
    return KnowledgeRelation(
        id=f"rel-{source_type}-{source_id}-{relation_type}-{target_type}-{target_id}",
        source_entity_type=source_type,
        source_entity_id=source_id,
        target_entity_type=target_type,
        target_entity_id=target_id,
        relation_type=relation_type,
        direction="outgoing",
        cardinality=cardinality,
        weight=weight,
        confidence=confidence,
        context=context,
        status=status,
        version=KNOWLEDGE_VERSION,
        created_at=KNOWLEDGE_PUBLISHED_AT,
        updated_at=RELATION_UPDATED_AT,
    )


def seed_relations() -> list[KnowledgeRelation]:
    source_to_edition = [
        _relation("source", source.id, "contiene", "source_edition", f"{source.id}:pending-edition")
        for source in seed_sources()
    ]
    source_to_node = [
        _relation("source", node.source_id, "documentado_en", "node", node.id)
        for node in seed_nodes()
    ]
    node_to_node = [
        _relation(
            "node",
            relation.source_node_id,
            relation.relation_type,
            "node",
            relation.target_node_id,
            weight=relation.weight,
            confidence=relation.confidence,
            context=relation.context,
            status=relation.status,
        )
        for relation in seed_node_relations()
    ]
    node_to_evidence = [
        _relation(
            "node",
            evidence.node_id,
            "sostenido_por",
            "evidence",
            evidence.id,
            cardinality="1:N",
            confidence=evidence.confidence,
            context=evidence.context,
            status=evidence.status,
        )
        for evidence in seed_evidence()
    ]
    evidence_to_claim = [
        _relation(
            "evidence",
            claim.evidence_id,
            "sostenido_por",
            "claim",
            claim.id,
            cardinality="1:N",
            confidence=claim.confidence,
            context=claim.domain,
            status=claim.status,
        )
        for claim in seed_claims()
    ]
    claim_to_card = [
        _relation(
            "claim",
            claim.id,
            "aplicacion_de",
            "knowledge_card",
            claim.card_id,
            cardinality="N:1",
            confidence=claim.confidence,
            context=claim.domain,
            status=claim.status,
        )
        for claim in seed_claims()
    ]
    source_to_evidence = [
        _relation(
            "source_edition",
            evidence.source_edition_id,
            "documentado_en",
            "evidence",
            evidence.id,
            cardinality="1:N",
            confidence=evidence.confidence,
            context=evidence.context,
            status=evidence.status,
        )
        for evidence in seed_evidence()
    ]
    return [
        *source_to_edition,
        *source_to_node,
        *node_to_node,
        *node_to_evidence,
        *source_to_evidence,
        *evidence_to_claim,
        *claim_to_card,
    ]


def seed_evidence() -> list[KnowledgeEvidenceItem]:
    return [
        KnowledgeEvidenceItem(
            id="ev-precision-lexica",
            node_id="rae-norma-estilo",
            source_id="rae-dle",
            source_edition_id="rae-dle:pending-edition",
            evidence_type="documented_paraphrase",
            locator={
                "catalog_id": "F005",
                "edition": "pendiente de identificacion",
                "unit": "entrada lexica pendiente de ingestion",
                "locator": "pendiente de localizacion verificable",
                "url": None,
            },
            reference="catalogo F005; localizador pendiente de ingestion",
            excerpt="La precision lexica reduce ambiguedad y mejora verificabilidad.",
            context="general_rule",
            confidence=0.58,
            confidence_level=2,
            status="draft",
            version=KNOWLEDGE_VERSION,
            created_at=KNOWLEDGE_PUBLISHED_AT,
            updated_at=KNOWLEDGE_PUBLISHED_AT,
            incorporated_by="minicerebro-seed",
            reviewed_by=None,
            revision=1,
        ),
        KnowledgeEvidenceItem(
            id="ev-dinamismo-frase",
            node_id="manual-rasgos-escritura",
            source_id="rae-lese",
            source_edition_id="rae-lese:pending-edition",
            evidence_type="documented_paraphrase",
            locator={
                "catalog_id": "F006",
                "edition": "pendiente de identificacion",
                "unit": "criterio de estilo pendiente de ingestion",
                "locator": "pendiente de localizacion verificable",
                "url": None,
            },
            reference="catalogo F006; localizador pendiente de ingestion",
            excerpt="El dinamismo aumenta cuando la frase avanza con verbos activos y menos acumulacion.",
            context="commentary",
            confidence=0.52,
            confidence_level=2,
            status="draft",
            version=KNOWLEDGE_VERSION,
            created_at=KNOWLEDGE_PUBLISHED_AT,
            updated_at=KNOWLEDGE_PUBLISHED_AT,
            incorporated_by="minicerebro-seed",
            reviewed_by=None,
            revision=1,
        ),
        KnowledgeEvidenceItem(
            id="ev-sobriedad-voz",
            node_id="manual-rasgos-escritura",
            source_id="rae-lese",
            source_edition_id="rae-lese:pending-edition",
            evidence_type="documented_paraphrase",
            locator={
                "catalog_id": "F006",
                "edition": "pendiente de identificacion",
                "unit": "criterio de estilo pendiente de ingestion",
                "locator": "pendiente de localizacion verificable",
                "url": None,
            },
            reference="catalogo F006; localizador pendiente de ingestion",
            excerpt="La sobriedad depende de contencion expresiva y baja ornamentacion.",
            context="commentary",
            confidence=0.5,
            confidence_level=2,
            status="draft",
            version=KNOWLEDGE_VERSION,
            created_at=KNOWLEDGE_PUBLISHED_AT,
            updated_at=KNOWLEDGE_PUBLISHED_AT,
            incorporated_by="minicerebro-seed",
            reviewed_by=None,
            revision=1,
        ),
    ]


def seed_evidence_revisions() -> list[dict]:
    return [
        {
            "id": f"{evidence.id}:r1",
            "evidence_id": evidence.id,
            "revision": 1,
            "author": "minicerebro-seed",
            "reason": "registro inicial segun contrato de evidencias V1",
            "changes": {
                "status": evidence.status,
                "source_edition_id": evidence.source_edition_id,
                "locator": evidence.locator,
            },
            "created_at": evidence.created_at,
        }
        for evidence in seed_evidence()
    ]


def seed_claims() -> list[KnowledgeClaim]:
    return [
        KnowledgeClaim(
            id="claim-dinamismo-frase",
            evidence_id="ev-dinamismo-frase",
            card_id="frase-dinamismo",
            statement="El dinamismo de frase se asocia a avance sintactico y verbos activos.",
            claim_type="stylistic",
            node_id="manual-rasgos-escritura",
            related_node_ids=["rae-norma-estilo"],
            domain="writing.style",
            scope={
                "language": "es",
                "register": "general",
                "geography": "panhispanic",
                "period": "contemporary",
                "text_type": "writing",
            },
            status="draft",
            confidence=0.52,
            origin="seed_contract_entry",
            version=KNOWLEDGE_VERSION,
            revision=1,
            created_at=KNOWLEDGE_PUBLISHED_AT,
            updated_at=KNOWLEDGE_PUBLISHED_AT,
            published_at=None,
        ),
        KnowledgeClaim(
            id="claim-precision-lexica",
            evidence_id="ev-precision-lexica",
            card_id="lexico-precision",
            statement="La precision lexica favorece formulaciones concretas y verificables.",
            claim_type="stylistic",
            node_id="rae-norma-estilo",
            related_node_ids=["manual-rasgos-escritura"],
            domain="writing.lexicon",
            scope={
                "language": "es",
                "register": "general",
                "geography": "panhispanic",
                "period": "contemporary",
                "text_type": "writing",
            },
            status="draft",
            confidence=0.58,
            origin="seed_contract_entry",
            version=KNOWLEDGE_VERSION,
            revision=1,
            created_at=KNOWLEDGE_PUBLISHED_AT,
            updated_at=KNOWLEDGE_PUBLISHED_AT,
            published_at=None,
        ),
        KnowledgeClaim(
            id="claim-sobriedad-voz",
            evidence_id="ev-sobriedad-voz",
            card_id="voz-sobriedad",
            statement="La sobriedad reduce enfasis decorativo y mantiene autoridad tonal.",
            claim_type="stylistic",
            node_id="manual-rasgos-escritura",
            related_node_ids=["rae-norma-estilo"],
            domain="writing.style",
            scope={
                "language": "es",
                "register": "general",
                "geography": "panhispanic",
                "period": "contemporary",
                "text_type": "writing",
            },
            status="draft",
            confidence=0.5,
            origin="seed_contract_entry",
            version=KNOWLEDGE_VERSION,
            revision=1,
            created_at=KNOWLEDGE_PUBLISHED_AT,
            updated_at=KNOWLEDGE_PUBLISHED_AT,
            published_at=None,
        ),
    ]


def seed_claim_evidence_links() -> list[KnowledgeClaimEvidenceLink]:
    return [
        KnowledgeClaimEvidenceLink(
            id=f"{claim.id}:{claim.evidence_id}:primary",
            claim_id=claim.id,
            evidence_id=claim.evidence_id,
            role="primary",
            created_at=claim.created_at,
        )
        for claim in seed_claims()
    ]


def seed_claim_revisions() -> list[dict]:
    return [
        {
            "id": f"{claim.id}:r1",
            "claim_id": claim.id,
            "revision": 1,
            "knowledge_version": claim.version,
            "author": "minicerebro-seed",
            "reason": "registro inicial segun contrato de claims V1",
            "changed_fields": [
                "statement",
                "claim_type",
                "node_id",
                "domain",
                "scope",
                "status",
                "evidence_links",
            ],
            "previous_claim": {},
            "new_claim": {
                "statement": claim.statement,
                "claim_type": claim.claim_type,
                "node_id": claim.node_id,
                "domain": claim.domain,
                "scope": claim.scope,
                "status": claim.status,
                "evidence_id": claim.evidence_id,
            },
            "created_at": claim.created_at,
        }
        for claim in seed_claims()
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


def query_knowledge(
    payload: KnowledgeQueryInput,
    sources: list[KnowledgeSource] | None = None,
    nodes: list[KnowledgeNode] | None = None,
    cards: list[KnowledgeCard] | None = None,
    claims: list[KnowledgeClaim] | None = None,
    evidence: list[KnowledgeEvidenceItem] | None = None,
) -> KnowledgeQueryResult:
    terms = {term for term in payload.query.lower().split() if len(term) > 2}
    sources = sources if sources is not None else seed_sources()
    nodes = nodes if nodes is not None else seed_nodes()
    cards = cards if cards is not None else seed_cards()
    claims = claims if claims is not None else seed_claims()
    evidence = evidence if evidence is not None else seed_evidence()
    sources_by_id = {source.id: source for source in sources}
    nodes_by_id = {node.id: node for node in nodes}
    evidence_by_id = {item.id: item for item in evidence}
    claims_by_card: dict[str, list[KnowledgeClaim]] = {}
    for claim in claims:
        claims_by_card.setdefault(claim.card_id, []).append(claim)

    def score_card(card: KnowledgeCard) -> int:
        linked_claims = claims_by_card.get(card.id, [])
        linked_evidence = [
            evidence_by_id[claim.evidence_id]
            for claim in linked_claims
            if claim.evidence_id in evidence_by_id
        ]
        linked_nodes = [
            nodes_by_id[item.node_id] for item in linked_evidence if item.node_id in nodes_by_id
        ]
        linked_sources = [
            sources_by_id[item.source_id]
            for item in linked_evidence
            if item.source_id in sources_by_id
        ]
        haystack = " ".join(
            [
                card.id,
                card.card_type,
                card.name,
                card.definition,
                " ".join(str(value) for value in card.payload.values()),
                " ".join(
                    " ".join(
                        [
                            claim.statement,
                            claim.claim_type,
                            claim.node_id,
                            " ".join(claim.related_node_ids),
                            claim.domain,
                            " ".join(str(value) for value in claim.scope.values()),
                            claim.status,
                            claim.origin,
                        ]
                    )
                    for claim in linked_claims
                ),
                " ".join(f"{item.reference} {item.excerpt}" for item in linked_evidence),
                " ".join(
                    " ".join(
                        [
                            node.title,
                            node.summary,
                            node.node_type,
                            node.canonical_name,
                            node.primary_branch,
                            node.secondary_branch,
                            node.short_definition,
                            node.long_definition,
                            " ".join(node.aliases),
                        ]
                    )
                    for node in linked_nodes
                ),
                " ".join(
                    f"{source.name} {source.source_type} {source.status}"
                    for source in linked_sources
                ),
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
        card_count=len(ranked_cards),
        claim_count=len(matched_claims),
        evidence_count=len(matched_evidence),
        cards=ranked_cards,
        claims=matched_claims,
        evidence=matched_evidence,
    )
