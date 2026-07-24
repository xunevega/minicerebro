from datetime import UTC, datetime
from hashlib import sha256
from unicodedata import category, normalize

from app.core.models import (
    KnowledgeCard,
    KnowledgeClaim,
    KnowledgeClaimEvidenceLink,
    KnowledgeEvidenceItem,
    KnowledgeExtractionRun,
    KnowledgeIngestionBatch,
    KnowledgeIngestionBatchExport,
    KnowledgeIngestionPolicy,
    KnowledgeIngestionReadiness,
    KnowledgeIndexEntry,
    KnowledgeNode,
    KnowledgeNodeRelation,
    KnowledgeObjectRevision,
    KnowledgeProposal,
    KnowledgePublicationPolicy,
    KnowledgePublicationReadiness,
    KnowledgeQueryContract,
    KnowledgeQueryInput,
    KnowledgeQueryInterpretation,
    KnowledgeQueryResult,
    KnowledgeRelation,
    KnowledgeSegment,
    RetrievedKnowledgeCard,
    KnowledgeSource,
    KnowledgeSourceEdition,
    KnowledgeVersion,
    KnowledgeVersioningPolicy,
)

KNOWLEDGE_VERSION = "knowledge-v0"
PUBLISHED_KNOWLEDGE_VERSION = "knowledge-v1"
KNOWLEDGE_V2_VERSION = "knowledge-v2"
KNOWLEDGE_V3_VERSION = "knowledge-v3"
KNOWLEDGE_V4_VERSION = "knowledge-v4"
KNOWLEDGE_V5_VERSION = "knowledge-v5"
KNOWLEDGE_V6_VERSION = "knowledge-v6"
KNOWLEDGE_V7_VERSION = "knowledge-v7"
KNOWLEDGE_V8_VERSION = "knowledge-v8"
KNOWLEDGE_V9_VERSION = "knowledge-v9"
KNOWLEDGE_V10_VERSION = "knowledge-v10"
KNOWLEDGE_V11_VERSION = "knowledge-v11"
KNOWLEDGE_V12_VERSION = "knowledge-v12"
KNOWLEDGE_V13_VERSION = "knowledge-v13"
LATEST_PUBLISHED_KNOWLEDGE_VERSION = "knowledge-v14"
KNOWLEDGE_PUBLISHED_AT = "2026-07-22"
KNOWLEDGE_V1_PUBLISHED_AT = "2026-07-23"
KNOWLEDGE_V2_PUBLISHED_AT = "2026-07-23T01:00:00+00:00"
KNOWLEDGE_V3_PUBLISHED_AT = "2026-07-23T02:00:00+00:00"
KNOWLEDGE_V4_PUBLISHED_AT = "2026-07-23T03:00:00+00:00"
KNOWLEDGE_V5_PUBLISHED_AT = "2026-07-23T04:00:00+00:00"
KNOWLEDGE_V6_PUBLISHED_AT = "2026-07-23T05:00:00+00:00"
KNOWLEDGE_V7_PUBLISHED_AT = "2026-07-23T06:00:00+00:00"
KNOWLEDGE_V8_PUBLISHED_AT = "2026-07-23T07:00:00+00:00"
KNOWLEDGE_V9_PUBLISHED_AT = "2026-07-23T08:00:00+00:00"
KNOWLEDGE_V10_PUBLISHED_AT = "2026-07-23T09:00:00+00:00"
KNOWLEDGE_V11_PUBLISHED_AT = "2026-07-23T10:00:00+00:00"
KNOWLEDGE_V12_PUBLISHED_AT = "2026-07-23T11:00:00+00:00"
KNOWLEDGE_V13_PUBLISHED_AT = "2026-07-23T12:00:00+00:00"
KNOWLEDGE_V14_PUBLISHED_AT = "2026-07-23T13:00:00+00:00"
RELATION_UPDATED_AT = "2026-07-23"
LATEST_KNOWLEDGE_VERSION = LATEST_PUBLISHED_KNOWLEDGE_VERSION
PUBLICATION_LIFECYCLE = [
    "draft",
    "review",
    "validated",
    "candidate",
    "published",
    "deprecated",
    "archived",
]
PUBLICATION_REQUIREMENTS = [
    "integridad referencial",
    "sin nodos huerfanos",
    "sin claims sin evidencia",
    "sin evidencias sin fuente",
    "sin fichas vacias",
    "sin relaciones rotas",
    "sin conflictos criticos",
]
PUBLICATION_VALIDATIONS = [
    "estructura",
    "documentacion",
    "consistencia",
    "duplicados",
    "contradicciones",
    "tests",
    "integridad",
]
INGESTION_LIFECYCLE = [
    "registered",
    "acquisition_pending",
    "available",
    "structured",
    "segmented",
    "extracting",
    "normalizing",
    "review",
    "validated",
    "candidate",
    "published",
]
INGESTION_ALTERNATIVE_STATES = ["blocked", "failed", "cancelled"]
INGESTION_FLOW = [
    "registered_source",
    "edition",
    "document_structure",
    "segmentation",
    "extraction",
    "nodes",
    "evidence",
    "claims",
    "cards",
    "validation",
    "candidate_version",
]
QUERY_LIFECYCLE = ["query", "interpretation", "restrictions", "context", "retrieval"]
QUERY_OUT_OF_SCOPE = [
    "perfil",
    "preferencias",
    "scoring",
    "feedback",
    "laboratorio",
    "prompts",
    "generaciones",
    "historial de usuario",
]

V6_SEED_ITEMS = [
    {
        "key": "dequeismo",
        "source_id": "rae-dpd",
        "source_edition_id": "rae-dpd:edicion-2005",
        "edition_title": "Diccionario panhispanico de dudas",
        "edition_label": "Primera edicion, 2005",
        "publication_year": "2005",
        "publisher": "Santillana",
        "isbn": "pendiente de identificacion",
        "format": "obra de consulta",
        "access_location": "Madrid: Santillana, 2005",
        "structure": ["entrada", "duda de uso", "segmento"],
        "locator_system": ["edicion", "entrada", "apartado", "pagina"],
        "index_id": "rae-dpd:edicion-2005:dequeismo",
        "index_title": "Dequeismo y queismo",
        "index_locator": "Primera edicion 2005 > dudas gramaticales > dequeismo y queismo",
        "segment_id": "rae-dpd:edicion-2005:dequeismo:seg-1",
        "segment_title": "Dequeismo como duda gramatical",
        "segment_text": (
            "Resumen editorial minimo: el dequeismo y el queismo son dudas de regimen "
            "que afectan a la presencia o ausencia de la preposicion de ante "
            "subordinadas introducidas por que."
        ),
        "extraction_id": "ext-rae-dpd-2005-dequeismo-1",
        "node_id": "rae-dpd-dequeismo",
        "canonical_name": "Dequeismo y queismo",
        "node_type": "norma",
        "primary_branch": "gramatica",
        "secondary_branch": "dudas de uso",
        "node_summary": "Duda de regimen sobre la presencia de la preposicion de ante que.",
        "short_definition": "Norma de uso que controla si corresponde de que o que segun el regimen.",
        "aliases": ["queismo", "regimen de que"],
        "relation_target": "rae-norma-estilo",
        "relation_type": "depende_de",
        "card_id": "card-dequeismo-queismo",
        "card_type": "grammar_usage",
        "card_name": "Dequeismo y queismo",
        "card_definition": "Criterio para revisar la presencia o ausencia de de ante subordinadas con que.",
        "signals": ["de que", "que subordinante", "regimen verbal"],
        "risks": ["corregir por intuicion sin comprobar el regimen"],
        "contexts": ["revision gramatical", "ensayo", "edicion"],
        "evidence_id": "ev-rae-dpd-dequeismo",
        "evidence_section": "dequeismo y queismo",
        "evidence_context": "seed_usage_large_batch",
        "confidence": 0.63,
        "claim_id": "claim-rae-dpd-dequeismo",
        "statement": (
            "La revision de dequeismo y queismo exige comprobar el regimen que "
            "autoriza o descarta la secuencia de que."
        ),
        "claim_type": "usage",
        "domain": "grammar.usage",
        "related_node_ids": ["rae-norma-estilo", "rae-ngle-complemento-directo"],
    },
    {
        "key": "extranjerismos",
        "source_id": "fundeu-recomendaciones",
        "source_edition_id": "fundeu-recomendaciones:web-2026",
        "edition_title": "Recomendaciones de FundeuRAE",
        "edition_label": "Consulta digital viva, corte editorial 2026",
        "publication_year": "2026",
        "publisher": "FundeuRAE",
        "isbn": "no aplica",
        "format": "recurso digital",
        "access_location": "https://www.fundeu.es/",
        "structure": ["recomendacion", "criterio de uso", "segmento"],
        "locator_system": ["url", "tema", "fecha", "segmento"],
        "index_id": "fundeu-recomendaciones:web-2026:extranjerismos",
        "index_title": "Extranjerismos y alternativas en espanol",
        "index_locator": "Consulta digital 2026 > lexico actual > extranjerismos",
        "segment_id": "fundeu-recomendaciones:web-2026:extranjerismos:seg-1",
        "segment_title": "Extranjerismo como decision editorial",
        "segment_text": (
            "Resumen editorial minimo: ante extranjerismos de uso actual, la revision "
            "debe valorar si existe alternativa asentada en espanol, si conviene "
            "adaptar la forma o si procede marcar el extranjerismo."
        ),
        "extraction_id": "ext-fundeu-2026-extranjerismos-1",
        "node_id": "fundeu-extranjerismos",
        "canonical_name": "Extranjerismos",
        "node_type": "norma",
        "primary_branch": "lexico",
        "secondary_branch": "uso actual",
        "node_summary": "Criterio editorial para tratar voces extranjeras en textos espanoles.",
        "short_definition": "Decision de uso sobre prestamo, adaptacion o alternativa espanola.",
        "aliases": ["prestamos", "anglicismos", "voces extranjeras"],
        "relation_target": "rae-dle-precision-lexica",
        "relation_type": "relacionado_con",
        "card_id": "card-extranjerismos",
        "card_type": "lexical_usage",
        "card_name": "Extranjerismos",
        "card_definition": "Criterio para decidir entre extranjerismo, adaptacion o alternativa espanola.",
        "signals": ["prestamo", "alternativa espanola", "adaptacion grafica"],
        "risks": ["rechazar un uso asentado sin revisar contexto"],
        "contexts": ["medios", "texto tecnico", "revision lexica"],
        "evidence_id": "ev-fundeu-extranjerismos",
        "evidence_section": "extranjerismos y alternativas",
        "evidence_context": "seed_usage_large_batch",
        "confidence": 0.6,
        "claim_id": "claim-fundeu-extranjerismos",
        "statement": (
            "La revision de extranjerismos debe decidir entre alternativa espanola, "
            "adaptacion o marca explicita segun asentamiento y contexto."
        ),
        "claim_type": "lexical",
        "domain": "writing.lexicon",
        "related_node_ids": ["rae-dle-precision-lexica"],
    },
    {
        "key": "criterio-editorial",
        "source_id": "martinez-sousa-mele",
        "source_edition_id": "martinez-sousa-mele:edicion-2015",
        "edition_title": "Manual de estilo de la lengua espanola",
        "edition_label": "Edicion de referencia editorial, 2015",
        "publication_year": "2015",
        "publisher": "Trea",
        "isbn": "pendiente de identificacion",
        "format": "libro impreso",
        "access_location": "Gijon: Trea, 2015",
        "structure": ["capitulo", "criterio editorial", "segmento"],
        "locator_system": ["edicion", "capitulo", "apartado", "pagina"],
        "index_id": "martinez-sousa-mele:edicion-2015:criterio-editorial",
        "index_title": "Unidad de criterio editorial",
        "index_locator": "Edicion 2015 > estilo editorial > unidad de criterio",
        "segment_id": "martinez-sousa-mele:edicion-2015:criterio-editorial:seg-1",
        "segment_title": "Unidad de criterio en la revision",
        "segment_text": (
            "Resumen editorial minimo: la revision editorial no solo corrige casos "
            "aislados; tambien mantiene decisiones coherentes de grafia, estilo, "
            "terminologia y presentacion a lo largo de un texto."
        ),
        "extraction_id": "ext-martinez-sousa-2015-criterio-editorial-1",
        "node_id": "martinez-sousa-criterio-editorial",
        "canonical_name": "Unidad de criterio editorial",
        "node_type": "metodo",
        "primary_branch": "edicion",
        "secondary_branch": "estilo editorial",
        "node_summary": "Metodo para conservar decisiones coherentes durante la revision.",
        "short_definition": "Principio de coherencia aplicado a grafia, estilo, terminologia y presentacion.",
        "aliases": ["coherencia editorial", "criterio de edicion"],
        "relation_target": "manual-rasgos-escritura",
        "relation_type": "usa",
        "card_id": "card-unidad-criterio-editorial",
        "card_type": "editing_method",
        "card_name": "Unidad de criterio editorial",
        "card_definition": "Metodo para mantener decisiones editoriales coherentes en todo el texto.",
        "signals": ["coherencia", "terminologia estable", "criterio repetible"],
        "risks": ["correcciones locales que contradicen decisiones previas"],
        "contexts": ["edicion", "revision", "texto largo"],
        "evidence_id": "ev-martinez-sousa-criterio-editorial",
        "evidence_section": "unidad de criterio editorial",
        "evidence_context": "seed_editing_large_batch",
        "confidence": 0.62,
        "claim_id": "claim-martinez-sousa-criterio-editorial",
        "statement": (
            "La unidad de criterio editorial exige mantener decisiones coherentes "
            "de estilo, terminologia y presentacion a lo largo del texto."
        ),
        "claim_type": "editing",
        "domain": "editing.consistency",
        "related_node_ids": ["manual-rasgos-escritura", "rae-gtg-terminologia-gramatical"],
    },
]

V7_SEED_ITEMS = [
    {
        "key": "sujeto",
        "source_id": "rae-ngle",
        "source_edition_id": "rae-ngle:manual-2010",
        "index_id": "rae-ngle:manual-2010:sujeto",
        "index_title": "Sujeto",
        "index_locator": "Manual academico 2010 > sintaxis > funciones sintacticas > sujeto",
        "segment_id": "rae-ngle:manual-2010:sujeto:seg-1",
        "segment_title": "Sujeto como funcion sintactica",
        "segment_text": (
            "Resumen editorial minimo: el sujeto es una funcion sintactica vinculada "
            "a la predicacion y a la concordancia con el verbo finito."
        ),
        "extraction_id": "ext-rae-ngle-2010-sujeto-1",
        "node_id": "rae-ngle-sujeto",
        "canonical_name": "Sujeto",
        "node_type": "concepto",
        "primary_branch": "sintaxis",
        "secondary_branch": "funciones sintacticas",
        "node_summary": "Funcion sintactica vinculada a la predicacion y la concordancia verbal.",
        "short_definition": "Funcion sintactica que participa en la predicacion y concuerda con el verbo.",
        "aliases": ["sujeto gramatical"],
        "relation_target": "rae-norma-estilo",
        "relation_type": "depende_de",
        "card_id": "card-sujeto",
        "card_type": "grammar_concept",
        "card_name": "Sujeto",
        "card_definition": "Funcion sintactica que organiza la predicacion y la concordancia verbal.",
        "signals": ["concordancia verbal", "predicacion", "funcion sintactica"],
        "risks": ["confundir sujeto gramatical con tema discursivo"],
        "contexts": ["gramatica", "sintaxis", "revision linguistica"],
        "evidence_id": "ev-rae-ngle-sujeto",
        "evidence_section": "sujeto",
        "confidence": 0.64,
        "claim_id": "claim-rae-ngle-sujeto",
        "statement": (
            "El sujeto debe analizarse como funcion sintactica vinculada a la "
            "predicacion y a la concordancia verbal."
        ),
        "related_node_ids": ["rae-norma-estilo", "rae-gtg-terminologia-gramatical"],
    },
    {
        "key": "predicado",
        "source_id": "rae-ngle",
        "source_edition_id": "rae-ngle:manual-2010",
        "index_id": "rae-ngle:manual-2010:predicado",
        "index_title": "Predicado",
        "index_locator": "Manual academico 2010 > sintaxis > funciones sintacticas > predicado",
        "segment_id": "rae-ngle:manual-2010:predicado:seg-1",
        "segment_title": "Predicado y estructura oracional",
        "segment_text": (
            "Resumen editorial minimo: el predicado articula la informacion atribuida "
            "al sujeto o expresada por el nucleo verbal de la oracion."
        ),
        "extraction_id": "ext-rae-ngle-2010-predicado-1",
        "node_id": "rae-ngle-predicado",
        "canonical_name": "Predicado",
        "node_type": "concepto",
        "primary_branch": "sintaxis",
        "secondary_branch": "funciones sintacticas",
        "node_summary": "Funcion y estructura que organiza la informacion verbal de la oracion.",
        "short_definition": "Estructura sintactica organizada en torno al nucleo verbal.",
        "aliases": ["grupo verbal predicativo"],
        "relation_target": "rae-ngle-sujeto",
        "relation_type": "relacionado_con",
        "card_id": "card-predicado",
        "card_type": "grammar_concept",
        "card_name": "Predicado",
        "card_definition": "Estructura que organiza la informacion verbal atribuida en la oracion.",
        "signals": ["nucleo verbal", "estructura oracional", "predicacion"],
        "risks": ["reducir el predicado solo al verbo sin revisar complementos"],
        "contexts": ["gramatica", "sintaxis", "analisis oracional"],
        "evidence_id": "ev-rae-ngle-predicado",
        "evidence_section": "predicado",
        "confidence": 0.63,
        "claim_id": "claim-rae-ngle-predicado",
        "statement": (
            "El predicado organiza la informacion verbal de la oracion y debe "
            "analizarse junto con sus complementos."
        ),
        "related_node_ids": ["rae-ngle-sujeto", "rae-ngle-complemento-directo"],
    },
    {
        "key": "complemento-indirecto",
        "source_id": "rae-ngle",
        "source_edition_id": "rae-ngle:manual-2010",
        "index_id": "rae-ngle:manual-2010:complemento-indirecto",
        "index_title": "Complemento indirecto",
        "index_locator": "Manual academico 2010 > sintaxis > funciones sintacticas > complemento indirecto",
        "segment_id": "rae-ngle:manual-2010:complemento-indirecto:seg-1",
        "segment_title": "Complemento indirecto como participante",
        "segment_text": (
            "Resumen editorial minimo: el complemento indirecto expresa un participante "
            "asociado al destinatario, beneficiario o afectado por la predicacion."
        ),
        "extraction_id": "ext-rae-ngle-2010-complemento-indirecto-1",
        "node_id": "rae-ngle-complemento-indirecto",
        "canonical_name": "Complemento indirecto",
        "node_type": "concepto",
        "primary_branch": "sintaxis",
        "secondary_branch": "funciones sintacticas",
        "node_summary": "Funcion sintactica asociada a destinatario, beneficiario o afectado.",
        "short_definition": "Complemento que introduce un participante indirecto de la predicacion.",
        "aliases": ["objeto indirecto"],
        "relation_target": "rae-ngle-complemento-directo",
        "relation_type": "compara_con",
        "card_id": "card-complemento-indirecto",
        "card_type": "grammar_concept",
        "card_name": "Complemento indirecto",
        "card_definition": "Funcion sintactica asociada a destinatario, beneficiario o afectado.",
        "signals": ["destinatario", "beneficiario", "participante indirecto"],
        "risks": ["confundirlo con complemento directo por proximidad al verbo"],
        "contexts": ["gramatica", "sintaxis", "revision linguistica"],
        "evidence_id": "ev-rae-ngle-complemento-indirecto",
        "evidence_section": "complemento indirecto",
        "confidence": 0.63,
        "claim_id": "claim-rae-ngle-complemento-indirecto",
        "statement": (
            "El complemento indirecto identifica un participante indirecto de la "
            "predicacion, como destinatario, beneficiario o afectado."
        ),
        "related_node_ids": ["rae-ngle-complemento-directo", "rae-ngle-predicado"],
    },
    {
        "key": "atributo",
        "source_id": "rae-ngle",
        "source_edition_id": "rae-ngle:manual-2010",
        "index_id": "rae-ngle:manual-2010:atributo",
        "index_title": "Atributo",
        "index_locator": "Manual academico 2010 > sintaxis > funciones sintacticas > atributo",
        "segment_id": "rae-ngle:manual-2010:atributo:seg-1",
        "segment_title": "Atributo en construcciones copulativas",
        "segment_text": (
            "Resumen editorial minimo: el atributo caracteriza al sujeto en "
            "construcciones copulativas o semicopulativas."
        ),
        "extraction_id": "ext-rae-ngle-2010-atributo-1",
        "node_id": "rae-ngle-atributo",
        "canonical_name": "Atributo",
        "node_type": "concepto",
        "primary_branch": "sintaxis",
        "secondary_branch": "funciones sintacticas",
        "node_summary": "Funcion que caracteriza al sujeto en construcciones copulativas.",
        "short_definition": "Complemento que atribuye una propiedad al sujeto con verbos copulativos.",
        "aliases": ["atributo copulativo"],
        "relation_target": "rae-ngle-sujeto",
        "relation_type": "relacionado_con",
        "card_id": "card-atributo",
        "card_type": "grammar_concept",
        "card_name": "Atributo",
        "card_definition": "Complemento que caracteriza al sujeto en construcciones copulativas.",
        "signals": ["verbo copulativo", "caracterizacion", "propiedad atribuida"],
        "risks": ["confundir atributo con complemento predicativo sin revisar el verbo"],
        "contexts": ["gramatica", "sintaxis", "analisis oracional"],
        "evidence_id": "ev-rae-ngle-atributo",
        "evidence_section": "atributo",
        "confidence": 0.62,
        "claim_id": "claim-rae-ngle-atributo",
        "statement": (
            "El atributo caracteriza al sujeto en construcciones copulativas o "
            "semicopulativas."
        ),
        "related_node_ids": ["rae-ngle-sujeto", "rae-ngle-predicado"],
    },
    {
        "key": "complemento-regimen",
        "source_id": "rae-ngle",
        "source_edition_id": "rae-ngle:manual-2010",
        "index_id": "rae-ngle:manual-2010:complemento-regimen",
        "index_title": "Complemento de regimen",
        "index_locator": "Manual academico 2010 > sintaxis > funciones sintacticas > complemento de regimen",
        "segment_id": "rae-ngle:manual-2010:complemento-regimen:seg-1",
        "segment_title": "Complemento de regimen preposicional",
        "segment_text": (
            "Resumen editorial minimo: el complemento de regimen depende de una "
            "preposicion exigida o seleccionada por el predicado."
        ),
        "extraction_id": "ext-rae-ngle-2010-complemento-regimen-1",
        "node_id": "rae-ngle-complemento-regimen",
        "canonical_name": "Complemento de regimen",
        "node_type": "concepto",
        "primary_branch": "sintaxis",
        "secondary_branch": "funciones sintacticas",
        "node_summary": "Funcion sintactica introducida por una preposicion regida.",
        "short_definition": "Complemento preposicional seleccionado por el predicado.",
        "aliases": ["complemento de regimen preposicional", "suplemento"],
        "relation_target": "rae-dpd-dequeismo",
        "relation_type": "relacionado_con",
        "card_id": "card-complemento-regimen",
        "card_type": "grammar_concept",
        "card_name": "Complemento de regimen",
        "card_definition": "Complemento preposicional exigido o seleccionado por el predicado.",
        "signals": ["preposicion regida", "regimen verbal", "seleccion del predicado"],
        "risks": ["eliminar una preposicion exigida por falsa correccion"],
        "contexts": ["gramatica", "sintaxis", "dudas de uso"],
        "evidence_id": "ev-rae-ngle-complemento-regimen",
        "evidence_section": "complemento de regimen",
        "confidence": 0.64,
        "claim_id": "claim-rae-ngle-complemento-regimen",
        "statement": (
            "El complemento de regimen se reconoce por la preposicion seleccionada "
            "por el predicado y conecta con dudas como dequeismo y queismo."
        ),
        "related_node_ids": ["rae-dpd-dequeismo", "rae-ngle-predicado"],
    },
]

V8_SEED_ITEMS = [
    {
        "key": "subordinada-sustantiva",
        "source_id": "rae-ngle",
        "source_edition_id": "rae-ngle:manual-2010",
        "index_id": "rae-ngle:manual-2010:subordinada-sustantiva",
        "index_title": "Oracion subordinada sustantiva",
        "index_locator": "Manual academico 2010 > sintaxis > subordinacion > sustantivas",
        "segment_id": "rae-ngle:manual-2010:subordinada-sustantiva:seg-1",
        "segment_title": "Subordinada sustantiva como argumento",
        "segment_text": "Resumen editorial minimo: la subordinada sustantiva desempena funciones propias de los grupos nominales dentro de la oracion compleja.",
        "extraction_id": "ext-rae-ngle-2010-subordinada-sustantiva-1",
        "node_id": "rae-ngle-subordinada-sustantiva",
        "canonical_name": "Oracion subordinada sustantiva",
        "node_type": "concepto",
        "primary_branch": "sintaxis",
        "secondary_branch": "subordinacion",
        "node_summary": "Subordinada que cumple funciones propias de una unidad nominal.",
        "short_definition": "Oracion subordinada que actua como argumento o funcion nominal.",
        "aliases": ["subordinada completiva", "sustantiva"],
        "relation_target": "rae-ngle-predicado",
        "relation_type": "depende_de",
        "card_id": "card-subordinada-sustantiva",
        "card_type": "grammar_concept",
        "card_name": "Subordinada sustantiva",
        "card_definition": "Subordinada que cumple funciones equivalentes a una unidad nominal.",
        "signals": ["que completivo", "funcion nominal", "oracion compleja"],
        "risks": ["confundir nexo completivo con relativo"],
        "contexts": ["gramatica", "sintaxis", "revision linguistica"],
        "evidence_id": "ev-rae-ngle-subordinada-sustantiva",
        "evidence_section": "subordinadas sustantivas",
        "confidence": 0.64,
        "claim_id": "claim-rae-ngle-subordinada-sustantiva",
        "statement": "La subordinada sustantiva se analiza por la funcion nominal que desempena dentro de la oracion compleja.",
        "claim_type": "grammatical",
        "domain": "grammar.syntax",
        "related_node_ids": ["rae-ngle-predicado", "rae-gtg-terminologia-gramatical"],
    },
    {
        "key": "subordinada-adjetiva",
        "source_id": "rae-ngle",
        "source_edition_id": "rae-ngle:manual-2010",
        "index_id": "rae-ngle:manual-2010:subordinada-adjetiva",
        "index_title": "Oracion subordinada adjetiva",
        "index_locator": "Manual academico 2010 > sintaxis > subordinacion > relativas",
        "segment_id": "rae-ngle:manual-2010:subordinada-adjetiva:seg-1",
        "segment_title": "Subordinada adjetiva y antecedente",
        "segment_text": "Resumen editorial minimo: la subordinada adjetiva o relativa modifica un antecedente y aporta informacion especificativa o explicativa.",
        "extraction_id": "ext-rae-ngle-2010-subordinada-adjetiva-1",
        "node_id": "rae-ngle-subordinada-adjetiva",
        "canonical_name": "Oracion subordinada adjetiva",
        "node_type": "concepto",
        "primary_branch": "sintaxis",
        "secondary_branch": "subordinacion",
        "node_summary": "Subordinada relativa que modifica un antecedente.",
        "short_definition": "Oracion subordinada que funciona como modificador de un antecedente.",
        "aliases": ["subordinada relativa", "relativa"],
        "relation_target": "rae-ngle-subordinada-sustantiva",
        "relation_type": "compara_con",
        "card_id": "card-subordinada-adjetiva",
        "card_type": "grammar_concept",
        "card_name": "Subordinada adjetiva",
        "card_definition": "Subordinada relativa que modifica un antecedente.",
        "signals": ["antecedente", "relativo", "modificador"],
        "risks": ["no distinguir especificativa y explicativa"],
        "contexts": ["gramatica", "sintaxis", "puntuacion"],
        "evidence_id": "ev-rae-ngle-subordinada-adjetiva",
        "evidence_section": "subordinadas adjetivas",
        "confidence": 0.63,
        "claim_id": "claim-rae-ngle-subordinada-adjetiva",
        "statement": "La subordinada adjetiva se reconoce por modificar un antecedente mediante una estructura relativa.",
        "claim_type": "grammatical",
        "domain": "grammar.syntax",
        "related_node_ids": ["rae-ngle-subordinada-sustantiva", "rae-gtg-terminologia-gramatical"],
    },
    {
        "key": "subordinada-adverbial",
        "source_id": "rae-ngle",
        "source_edition_id": "rae-ngle:manual-2010",
        "index_id": "rae-ngle:manual-2010:subordinada-adverbial",
        "index_title": "Oracion subordinada adverbial",
        "index_locator": "Manual academico 2010 > sintaxis > subordinacion > adverbiales",
        "segment_id": "rae-ngle:manual-2010:subordinada-adverbial:seg-1",
        "segment_title": "Subordinada adverbial como circunstancia",
        "segment_text": "Resumen editorial minimo: la subordinada adverbial expresa relaciones circunstanciales o conectivas como tiempo, causa, condicion o finalidad.",
        "extraction_id": "ext-rae-ngle-2010-subordinada-adverbial-1",
        "node_id": "rae-ngle-subordinada-adverbial",
        "canonical_name": "Oracion subordinada adverbial",
        "node_type": "concepto",
        "primary_branch": "sintaxis",
        "secondary_branch": "subordinacion",
        "node_summary": "Subordinada que expresa relaciones circunstanciales o conectivas.",
        "short_definition": "Oracion subordinada con valor circunstancial, causal, condicional o final.",
        "aliases": ["adverbial", "subordinada circunstancial"],
        "relation_target": "rae-ngle-complemento-circunstancial",
        "relation_type": "relacionado_con",
        "card_id": "card-subordinada-adverbial",
        "card_type": "grammar_concept",
        "card_name": "Subordinada adverbial",
        "card_definition": "Subordinada con valor circunstancial o conectivo.",
        "signals": ["tiempo", "causa", "condicion", "finalidad"],
        "risks": ["tratar toda subordinada con nexo como el mismo tipo"],
        "contexts": ["gramatica", "sintaxis", "cohesion textual"],
        "evidence_id": "ev-rae-ngle-subordinada-adverbial",
        "evidence_section": "subordinadas adverbiales",
        "confidence": 0.62,
        "claim_id": "claim-rae-ngle-subordinada-adverbial",
        "statement": "La subordinada adverbial aporta una relacion circunstancial o conectiva al analisis de la oracion compleja.",
        "claim_type": "grammatical",
        "domain": "grammar.syntax",
        "related_node_ids": ["rae-ngle-complemento-circunstancial", "rae-ngle-predicado"],
    },
    {
        "key": "concordancia",
        "source_id": "rae-ngle",
        "source_edition_id": "rae-ngle:manual-2010",
        "index_id": "rae-ngle:manual-2010:concordancia",
        "index_title": "Concordancia",
        "index_locator": "Manual academico 2010 > morfosintaxis > concordancia",
        "segment_id": "rae-ngle:manual-2010:concordancia:seg-1",
        "segment_title": "Concordancia gramatical",
        "segment_text": "Resumen editorial minimo: la concordancia relaciona rasgos gramaticales entre elementos dependientes, especialmente sujeto y verbo o nombre y modificadores.",
        "extraction_id": "ext-rae-ngle-2010-concordancia-1",
        "node_id": "rae-ngle-concordancia",
        "canonical_name": "Concordancia",
        "node_type": "norma",
        "primary_branch": "morfosintaxis",
        "secondary_branch": "concordancia",
        "node_summary": "Relacion de rasgos gramaticales entre elementos conectados.",
        "short_definition": "Correspondencia de rasgos como numero, persona o genero entre elementos relacionados.",
        "aliases": ["concordancia gramatical"],
        "relation_target": "rae-ngle-sujeto",
        "relation_type": "requiere",
        "card_id": "card-concordancia",
        "card_type": "grammar_rule",
        "card_name": "Concordancia",
        "card_definition": "Correspondencia de rasgos gramaticales entre elementos relacionados.",
        "signals": ["numero", "persona", "genero", "sujeto y verbo"],
        "risks": ["corregir por proximidad y no por nucleo sintactico"],
        "contexts": ["gramatica", "revision", "correccion"],
        "evidence_id": "ev-rae-ngle-concordancia",
        "evidence_section": "concordancia",
        "confidence": 0.65,
        "claim_id": "claim-rae-ngle-concordancia",
        "statement": "La concordancia exige revisar la relacion de rasgos gramaticales entre elementos conectados, no solo la proximidad lineal.",
        "claim_type": "grammatical",
        "domain": "grammar.syntax",
        "related_node_ids": ["rae-ngle-sujeto", "rae-ngle-predicado"],
    },
    {
        "key": "complemento-circunstancial",
        "source_id": "rae-ngle",
        "source_edition_id": "rae-ngle:manual-2010",
        "index_id": "rae-ngle:manual-2010:complemento-circunstancial",
        "index_title": "Complemento circunstancial",
        "index_locator": "Manual academico 2010 > sintaxis > funciones sintacticas > complemento circunstancial",
        "segment_id": "rae-ngle:manual-2010:complemento-circunstancial:seg-1",
        "segment_title": "Complemento circunstancial",
        "segment_text": "Resumen editorial minimo: el complemento circunstancial aporta informacion de marco, modo, tiempo, lugar, causa u otras circunstancias de la predicacion.",
        "extraction_id": "ext-rae-ngle-2010-complemento-circunstancial-1",
        "node_id": "rae-ngle-complemento-circunstancial",
        "canonical_name": "Complemento circunstancial",
        "node_type": "concepto",
        "primary_branch": "sintaxis",
        "secondary_branch": "funciones sintacticas",
        "node_summary": "Complemento que aporta circunstancias de la predicacion.",
        "short_definition": "Funcion que expresa tiempo, lugar, modo, causa u otros marcos circunstanciales.",
        "aliases": ["circunstancial"],
        "relation_target": "rae-ngle-predicado",
        "relation_type": "depende_de",
        "card_id": "card-complemento-circunstancial",
        "card_type": "grammar_concept",
        "card_name": "Complemento circunstancial",
        "card_definition": "Complemento que aporta informacion circunstancial a la predicacion.",
        "signals": ["tiempo", "lugar", "modo", "causa"],
        "risks": ["confundir circunstancia con argumento exigido por el verbo"],
        "contexts": ["gramatica", "sintaxis", "analisis oracional"],
        "evidence_id": "ev-rae-ngle-complemento-circunstancial",
        "evidence_section": "complemento circunstancial",
        "confidence": 0.63,
        "claim_id": "claim-rae-ngle-complemento-circunstancial",
        "statement": "El complemento circunstancial anade informacion de marco a la predicacion sin ser necesariamente argumento seleccionado.",
        "claim_type": "grammatical",
        "domain": "grammar.syntax",
        "related_node_ids": ["rae-ngle-predicado", "rae-ngle-subordinada-adverbial"],
    },
    {
        "key": "complemento-predicativo",
        "source_id": "rae-ngle",
        "source_edition_id": "rae-ngle:manual-2010",
        "index_id": "rae-ngle:manual-2010:complemento-predicativo",
        "index_title": "Complemento predicativo",
        "index_locator": "Manual academico 2010 > sintaxis > funciones sintacticas > complemento predicativo",
        "segment_id": "rae-ngle:manual-2010:complemento-predicativo:seg-1",
        "segment_title": "Complemento predicativo",
        "segment_text": "Resumen editorial minimo: el complemento predicativo atribuye una propiedad a un participante y mantiene relacion con el predicado verbal.",
        "extraction_id": "ext-rae-ngle-2010-complemento-predicativo-1",
        "node_id": "rae-ngle-complemento-predicativo",
        "canonical_name": "Complemento predicativo",
        "node_type": "concepto",
        "primary_branch": "sintaxis",
        "secondary_branch": "funciones sintacticas",
        "node_summary": "Complemento que atribuye una propiedad dentro de una predicacion verbal.",
        "short_definition": "Funcion que caracteriza a un participante y depende del predicado verbal.",
        "aliases": ["predicativo"],
        "relation_target": "rae-ngle-atributo",
        "relation_type": "compara_con",
        "card_id": "card-complemento-predicativo",
        "card_type": "grammar_concept",
        "card_name": "Complemento predicativo",
        "card_definition": "Complemento que atribuye una propiedad a un participante dentro del predicado verbal.",
        "signals": ["propiedad atribuida", "participante", "predicado verbal"],
        "risks": ["confundirlo con atributo en estructuras copulativas"],
        "contexts": ["gramatica", "sintaxis", "analisis oracional"],
        "evidence_id": "ev-rae-ngle-complemento-predicativo",
        "evidence_section": "complemento predicativo",
        "confidence": 0.62,
        "claim_id": "claim-rae-ngle-complemento-predicativo",
        "statement": "El complemento predicativo atribuye una propiedad a un participante sin formar una construccion copulativa pura.",
        "claim_type": "grammatical",
        "domain": "grammar.syntax",
        "related_node_ids": ["rae-ngle-atributo", "rae-ngle-predicado"],
    },
]

V9_SEED_ITEMS = [
    {
        "key": "coma",
        "source_id": "rae-ole",
        "source_edition_id": "rae-ole:edicion-2010",
        "index_id": "rae-ole:edicion-2010:coma",
        "index_title": "Coma",
        "index_locator": "Ortografia 2010 > puntuacion > coma",
        "segment_id": "rae-ole:edicion-2010:coma:seg-1",
        "segment_title": "Coma y delimitacion",
        "segment_text": "Resumen editorial minimo: la coma delimita unidades sintacticas o discursivas y no debe usarse solo por pausa intuitiva.",
        "extraction_id": "ext-rae-ole-2010-coma-1",
        "node_id": "rae-ole-coma",
        "canonical_name": "Coma",
        "node_type": "norma",
        "primary_branch": "ortografia",
        "secondary_branch": "puntuacion",
        "node_summary": "Signo de puntuacion que delimita unidades sintacticas o discursivas.",
        "short_definition": "Signo usado para separar o delimitar unidades segun criterios sintacticos y discursivos.",
        "aliases": ["uso de la coma"],
        "relation_target": "rae-norma-estilo",
        "relation_type": "depende_de",
        "card_id": "card-coma",
        "card_type": "orthography_rule",
        "card_name": "Coma",
        "card_definition": "Criterio para delimitar unidades con coma sin depender solo de la pausa.",
        "signals": ["inciso", "enumeracion", "delimitacion"],
        "risks": ["poner coma entre sujeto y predicado sin justificacion"],
        "contexts": ["ortografia", "puntuacion", "revision"],
        "evidence_id": "ev-rae-ole-coma",
        "evidence_section": "coma",
        "confidence": 0.65,
        "claim_id": "claim-rae-ole-coma",
        "statement": "La coma debe justificarse por delimitacion sintactica o discursiva, no solo por una pausa de lectura.",
        "claim_type": "orthographic",
        "domain": "orthography.punctuation",
        "related_node_ids": ["rae-ngle-sujeto", "rae-ngle-predicado"],
    },
    {
        "key": "punto-y-coma",
        "source_id": "rae-ole",
        "source_edition_id": "rae-ole:edicion-2010",
        "index_id": "rae-ole:edicion-2010:punto-y-coma",
        "index_title": "Punto y coma",
        "index_locator": "Ortografia 2010 > puntuacion > punto y coma",
        "segment_id": "rae-ole:edicion-2010:punto-y-coma:seg-1",
        "segment_title": "Punto y coma y relacion interna",
        "segment_text": "Resumen editorial minimo: el punto y coma separa unidades relacionadas cuando la coma resulta insuficiente y el punto cortaria demasiado.",
        "extraction_id": "ext-rae-ole-2010-punto-y-coma-1",
        "node_id": "rae-ole-punto-y-coma",
        "canonical_name": "Punto y coma",
        "node_type": "norma",
        "primary_branch": "ortografia",
        "secondary_branch": "puntuacion",
        "node_summary": "Signo intermedio para separar unidades relacionadas.",
        "short_definition": "Signo que separa miembros complejos o en relacion estrecha.",
        "aliases": ["semicolon"],
        "relation_target": "rae-ole-coma",
        "relation_type": "compara_con",
        "card_id": "card-punto-y-coma",
        "card_type": "orthography_rule",
        "card_name": "Punto y coma",
        "card_definition": "Criterio para separar unidades relacionadas de complejidad media.",
        "signals": ["miembros complejos", "relacion estrecha", "separacion intermedia"],
        "risks": ["sustituirlo mecanicamente por coma o punto"],
        "contexts": ["ortografia", "puntuacion", "texto argumentativo"],
        "evidence_id": "ev-rae-ole-punto-y-coma",
        "evidence_section": "punto y coma",
        "confidence": 0.63,
        "claim_id": "claim-rae-ole-punto-y-coma",
        "statement": "El punto y coma conviene cuando hay separacion interna fuerte pero continuidad conceptual entre miembros.",
        "claim_type": "orthographic",
        "domain": "orthography.punctuation",
        "related_node_ids": ["rae-ole-coma", "manual-rasgos-escritura"],
    },
    {
        "key": "dos-puntos",
        "source_id": "rae-ole",
        "source_edition_id": "rae-ole:edicion-2010",
        "index_id": "rae-ole:edicion-2010:dos-puntos",
        "index_title": "Dos puntos",
        "index_locator": "Ortografia 2010 > puntuacion > dos puntos",
        "segment_id": "rae-ole:edicion-2010:dos-puntos:seg-1",
        "segment_title": "Dos puntos y anticipacion",
        "segment_text": "Resumen editorial minimo: los dos puntos anuncian enumeraciones, explicaciones, citas o desarrollos directamente vinculados con lo anterior.",
        "extraction_id": "ext-rae-ole-2010-dos-puntos-1",
        "node_id": "rae-ole-dos-puntos",
        "canonical_name": "Dos puntos",
        "node_type": "norma",
        "primary_branch": "ortografia",
        "secondary_branch": "puntuacion",
        "node_summary": "Signo que anuncia desarrollo, enumeracion, explicacion o cita.",
        "short_definition": "Signo de puntuacion con valor anunciador o explicativo.",
        "aliases": ["colon"],
        "relation_target": "rae-ole-coma",
        "relation_type": "relacionado_con",
        "card_id": "card-dos-puntos",
        "card_type": "orthography_rule",
        "card_name": "Dos puntos",
        "card_definition": "Criterio para anunciar enumeracion, explicacion, cita o desarrollo.",
        "signals": ["enumeracion", "explicacion", "cita"],
        "risks": ["usar dos puntos sin relacion directa con lo anterior"],
        "contexts": ["ortografia", "puntuacion", "exposicion"],
        "evidence_id": "ev-rae-ole-dos-puntos",
        "evidence_section": "dos puntos",
        "confidence": 0.63,
        "claim_id": "claim-rae-ole-dos-puntos",
        "statement": "Los dos puntos anuncian un desarrollo directamente vinculado con el segmento anterior.",
        "claim_type": "orthographic",
        "domain": "orthography.punctuation",
        "related_node_ids": ["manual-rasgos-escritura"],
    },
    {
        "key": "raya",
        "source_id": "rae-ole",
        "source_edition_id": "rae-ole:edicion-2010",
        "index_id": "rae-ole:edicion-2010:raya",
        "index_title": "Raya",
        "index_locator": "Ortografia 2010 > signos auxiliares > raya",
        "segment_id": "rae-ole:edicion-2010:raya:seg-1",
        "segment_title": "Raya en incisos y dialogos",
        "segment_text": "Resumen editorial minimo: la raya delimita incisos y marca intervenciones o acotaciones en dialogos, con convenciones propias.",
        "extraction_id": "ext-rae-ole-2010-raya-1",
        "node_id": "rae-ole-raya",
        "canonical_name": "Raya",
        "node_type": "norma",
        "primary_branch": "ortografia",
        "secondary_branch": "ortotipografia",
        "node_summary": "Signo usado en incisos, dialogos y acotaciones.",
        "short_definition": "Signo que delimita incisos o introduce intervenciones de dialogo.",
        "aliases": ["guion largo"],
        "relation_target": "rae-ole-coma",
        "relation_type": "compara_con",
        "card_id": "card-raya",
        "card_type": "orthography_rule",
        "card_name": "Raya",
        "card_definition": "Criterio para usar raya en incisos, dialogos y acotaciones.",
        "signals": ["inciso", "dialogo", "acotacion"],
        "risks": ["confundir raya con guion o signo menos"],
        "contexts": ["ortografia", "dialogo", "edicion"],
        "evidence_id": "ev-rae-ole-raya",
        "evidence_section": "raya",
        "confidence": 0.62,
        "claim_id": "claim-rae-ole-raya",
        "statement": "La raya tiene usos delimitadores y dialogales que no deben confundirse con el guion.",
        "claim_type": "orthographic",
        "domain": "orthography.punctuation",
        "related_node_ids": ["martinez-sousa-criterio-editorial"],
    },
    {
        "key": "comillas",
        "source_id": "rae-ole",
        "source_edition_id": "rae-ole:edicion-2010",
        "index_id": "rae-ole:edicion-2010:comillas",
        "index_title": "Comillas",
        "index_locator": "Ortografia 2010 > signos auxiliares > comillas",
        "segment_id": "rae-ole:edicion-2010:comillas:seg-1",
        "segment_title": "Comillas y marcacion",
        "segment_text": "Resumen editorial minimo: las comillas marcan citas, usos especiales, voces destacadas o distancias enunciativas segun convenciones tipograficas.",
        "extraction_id": "ext-rae-ole-2010-comillas-1",
        "node_id": "rae-ole-comillas",
        "canonical_name": "Comillas",
        "node_type": "norma",
        "primary_branch": "ortografia",
        "secondary_branch": "ortotipografia",
        "node_summary": "Signo usado para citas, usos especiales y marcas enunciativas.",
        "short_definition": "Signo que marca cita, mencion, uso especial o distancia enunciativa.",
        "aliases": ["comillas espanolas", "comillas latinas"],
        "relation_target": "martinez-sousa-criterio-editorial",
        "relation_type": "usa",
        "card_id": "card-comillas",
        "card_type": "orthography_rule",
        "card_name": "Comillas",
        "card_definition": "Criterio para marcar citas, usos especiales o distancia enunciativa.",
        "signals": ["cita", "mencion", "uso especial"],
        "risks": ["usar comillas como enfasis decorativo"],
        "contexts": ["ortografia", "edicion", "cita"],
        "evidence_id": "ev-rae-ole-comillas",
        "evidence_section": "comillas",
        "confidence": 0.62,
        "claim_id": "claim-rae-ole-comillas",
        "statement": "Las comillas deben responder a cita, mencion o uso especial, no a enfasis arbitrario.",
        "claim_type": "orthographic",
        "domain": "orthography.orthotypography",
        "related_node_ids": ["martinez-sousa-criterio-editorial"],
    },
    {
        "key": "tilde-diacritica",
        "source_id": "rae-ole",
        "source_edition_id": "rae-ole:edicion-2010",
        "index_id": "rae-ole:edicion-2010:tilde-diacritica",
        "index_title": "Tilde diacritica",
        "index_locator": "Ortografia 2010 > acentuacion > tilde diacritica",
        "segment_id": "rae-ole:edicion-2010:tilde-diacritica:seg-1",
        "segment_title": "Tilde diacritica",
        "segment_text": "Resumen editorial minimo: la tilde diacritica distingue ciertas palabras formalmente identicas con diferencias gramaticales o tonicas establecidas.",
        "extraction_id": "ext-rae-ole-2010-tilde-diacritica-1",
        "node_id": "rae-ole-tilde-diacritica",
        "canonical_name": "Tilde diacritica",
        "node_type": "norma",
        "primary_branch": "ortografia",
        "secondary_branch": "acentuacion",
        "node_summary": "Uso de tilde para distinguir pares o series gramaticales concretas.",
        "short_definition": "Tilde que diferencia determinadas palabras identicas en forma.",
        "aliases": ["acento diacritico"],
        "relation_target": "rae-ole-acentuacion-grafica",
        "relation_type": "es_parte_de",
        "card_id": "card-tilde-diacritica",
        "card_type": "orthography_rule",
        "card_name": "Tilde diacritica",
        "card_definition": "Criterio para distinguir palabras formalmente identicas en casos establecidos.",
        "signals": ["pares gramaticales", "distincion", "tilde"],
        "risks": ["extender la tilde diacritica fuera de los casos fijados"],
        "contexts": ["ortografia", "acentuacion", "correccion"],
        "evidence_id": "ev-rae-ole-tilde-diacritica",
        "evidence_section": "tilde diacritica",
        "confidence": 0.64,
        "claim_id": "claim-rae-ole-tilde-diacritica",
        "statement": "La tilde diacritica solo debe aplicarse en distinciones establecidas, no como refuerzo libre.",
        "claim_type": "orthographic",
        "domain": "orthography.accentuation",
        "related_node_ids": ["rae-ole-acentuacion-grafica"],
    },
    {
        "key": "mayusculas",
        "source_id": "rae-ole",
        "source_edition_id": "rae-ole:edicion-2010",
        "index_id": "rae-ole:edicion-2010:mayusculas",
        "index_title": "Mayusculas",
        "index_locator": "Ortografia 2010 > mayusculas y minusculas",
        "segment_id": "rae-ole:edicion-2010:mayusculas:seg-1",
        "segment_title": "Mayusculas y nombres propios",
        "segment_text": "Resumen editorial minimo: el uso de mayusculas depende de categorias como nombre propio, posicion textual, denominacion oficial o convencion institucional.",
        "extraction_id": "ext-rae-ole-2010-mayusculas-1",
        "node_id": "rae-ole-mayusculas",
        "canonical_name": "Mayusculas",
        "node_type": "norma",
        "primary_branch": "ortografia",
        "secondary_branch": "mayusculas",
        "node_summary": "Reglas de uso de mayusculas y minusculas en espanol.",
        "short_definition": "Criterios para decidir mayuscula segun funcion, nombre propio o convencion.",
        "aliases": ["uso de mayusculas"],
        "relation_target": "rae-norma-estilo",
        "relation_type": "depende_de",
        "card_id": "card-mayusculas",
        "card_type": "orthography_rule",
        "card_name": "Mayusculas",
        "card_definition": "Criterio para decidir mayuscula segun nombre propio, posicion o convencion.",
        "signals": ["nombre propio", "denominacion oficial", "inicio de enunciado"],
        "risks": ["usar mayuscula enfatica sin criterio normativo"],
        "contexts": ["ortografia", "edicion", "correccion"],
        "evidence_id": "ev-rae-ole-mayusculas",
        "evidence_section": "mayusculas",
        "confidence": 0.63,
        "claim_id": "claim-rae-ole-mayusculas",
        "statement": "La mayuscula debe justificarse por funcion ortografica o denominativa, no por enfasis subjetivo.",
        "claim_type": "orthographic",
        "domain": "orthography.capitalization",
        "related_node_ids": ["martinez-sousa-criterio-editorial"],
    },
    {
        "key": "abreviaturas",
        "source_id": "rae-ole",
        "source_edition_id": "rae-ole:edicion-2010",
        "index_id": "rae-ole:edicion-2010:abreviaturas",
        "index_title": "Abreviaturas",
        "index_locator": "Ortografia 2010 > abreviaciones > abreviaturas",
        "segment_id": "rae-ole:edicion-2010:abreviaturas:seg-1",
        "segment_title": "Abreviaturas",
        "segment_text": "Resumen editorial minimo: las abreviaturas reducen graficamente una palabra y siguen convenciones de punto, plural y lectura.",
        "extraction_id": "ext-rae-ole-2010-abreviaturas-1",
        "node_id": "rae-ole-abreviaturas",
        "canonical_name": "Abreviaturas",
        "node_type": "norma",
        "primary_branch": "ortografia",
        "secondary_branch": "abreviaciones",
        "node_summary": "Reducciones graficas convencionales de palabras.",
        "short_definition": "Forma abreviada de una palabra sometida a convenciones graficas.",
        "aliases": ["abreviacion grafica"],
        "relation_target": "martinez-sousa-criterio-editorial",
        "relation_type": "usa",
        "card_id": "card-abreviaturas",
        "card_type": "orthography_rule",
        "card_name": "Abreviaturas",
        "card_definition": "Criterio para usar formas abreviadas con convenciones graficas estables.",
        "signals": ["punto abreviativo", "plural", "forma reducida"],
        "risks": ["mezclar abreviatura, sigla y simbolo"],
        "contexts": ["ortografia", "edicion", "texto tecnico"],
        "evidence_id": "ev-rae-ole-abreviaturas",
        "evidence_section": "abreviaturas",
        "confidence": 0.62,
        "claim_id": "claim-rae-ole-abreviaturas",
        "statement": "Las abreviaturas requieren convenciones graficas estables y no deben confundirse con siglas o simbolos.",
        "claim_type": "orthographic",
        "domain": "orthography.abbreviations",
        "related_node_ids": ["rae-ole-siglas", "martinez-sousa-criterio-editorial"],
    },
    {
        "key": "siglas",
        "source_id": "rae-ole",
        "source_edition_id": "rae-ole:edicion-2010",
        "index_id": "rae-ole:edicion-2010:siglas",
        "index_title": "Siglas",
        "index_locator": "Ortografia 2010 > abreviaciones > siglas",
        "segment_id": "rae-ole:edicion-2010:siglas:seg-1",
        "segment_title": "Siglas y acronimos",
        "segment_text": "Resumen editorial minimo: las siglas representan denominaciones complejas mediante iniciales y tienen criterios propios de escritura, lectura y plural.",
        "extraction_id": "ext-rae-ole-2010-siglas-1",
        "node_id": "rae-ole-siglas",
        "canonical_name": "Siglas",
        "node_type": "norma",
        "primary_branch": "ortografia",
        "secondary_branch": "abreviaciones",
        "node_summary": "Formas creadas a partir de iniciales de denominaciones complejas.",
        "short_definition": "Abreviacion formada por iniciales con convenciones propias.",
        "aliases": ["acronimos"],
        "relation_target": "rae-ole-abreviaturas",
        "relation_type": "compara_con",
        "card_id": "card-siglas",
        "card_type": "orthography_rule",
        "card_name": "Siglas",
        "card_definition": "Criterio para escribir y leer siglas sin confundirlas con abreviaturas.",
        "signals": ["iniciales", "denominacion compleja", "plural"],
        "risks": ["anadir plural grafico impropio o puntos innecesarios"],
        "contexts": ["ortografia", "edicion", "texto institucional"],
        "evidence_id": "ev-rae-ole-siglas",
        "evidence_section": "siglas",
        "confidence": 0.62,
        "claim_id": "claim-rae-ole-siglas",
        "statement": "Las siglas tienen criterios graficos propios y no deben tratarse como abreviaturas ordinarias.",
        "claim_type": "orthographic",
        "domain": "orthography.abbreviations",
        "related_node_ids": ["rae-ole-abreviaturas", "martinez-sousa-criterio-editorial"],
    },
    {
        "key": "cursiva-extranjerismos",
        "source_id": "fundeu-recomendaciones",
        "source_edition_id": "fundeu-recomendaciones:web-2026",
        "index_id": "fundeu-recomendaciones:web-2026:cursiva-extranjerismos",
        "index_title": "Cursiva y extranjerismos",
        "index_locator": "Consulta digital 2026 > lexico actual > cursiva y extranjerismos",
        "segment_id": "fundeu-recomendaciones:web-2026:cursiva-extranjerismos:seg-1",
        "segment_title": "Marca tipografica de extranjerismos",
        "segment_text": "Resumen editorial minimo: los extranjerismos no adaptados pueden requerir marca tipografica, mientras que formas adaptadas o asentadas siguen otro tratamiento.",
        "extraction_id": "ext-fundeu-2026-cursiva-extranjerismos-1",
        "node_id": "fundeu-cursiva-extranjerismos",
        "canonical_name": "Cursiva en extranjerismos",
        "node_type": "norma",
        "primary_branch": "ortotipografia",
        "secondary_branch": "extranjerismos",
        "node_summary": "Criterio tipografico para marcar extranjerismos no adaptados.",
        "short_definition": "Uso de cursiva u otra marca en extranjerismos segun adaptacion y asentamiento.",
        "aliases": ["extranjerismos en cursiva"],
        "relation_target": "fundeu-extranjerismos",
        "relation_type": "depende_de",
        "card_id": "card-cursiva-extranjerismos",
        "card_type": "orthography_rule",
        "card_name": "Cursiva en extranjerismos",
        "card_definition": "Criterio para marcar tipograficamente extranjerismos segun adaptacion.",
        "signals": ["voz no adaptada", "marca tipografica", "prestamo"],
        "risks": ["poner cursiva a formas ya adaptadas o asentadas"],
        "contexts": ["ortotipografia", "lexico", "edicion"],
        "evidence_id": "ev-fundeu-cursiva-extranjerismos",
        "evidence_section": "cursiva y extranjerismos",
        "confidence": 0.6,
        "claim_id": "claim-fundeu-cursiva-extranjerismos",
        "statement": "La marca tipografica de extranjerismos depende de si la forma esta adaptada, asentada o se mantiene como voz extranjera.",
        "claim_type": "orthographic",
        "domain": "orthography.orthotypography",
        "related_node_ids": ["fundeu-extranjerismos", "martinez-sousa-criterio-editorial"],
    },
]

V10_SEED_ITEMS = [
    {
        "key": "claridad",
        "source_id": "rae-lese",
        "source_edition_id": "rae-lese:edicion-2018",
        "index_id": "rae-lese:edicion-2018:claridad",
        "index_title": "Claridad",
        "index_locator": "Libro de estilo 2018 > redaccion > claridad",
        "segment_id": "rae-lese:edicion-2018:claridad:seg-1",
        "segment_title": "Claridad de redaccion",
        "segment_text": "Resumen editorial minimo: la claridad exige que la estructura, el lexico y la progresion informativa faciliten la comprension del lector.",
        "extraction_id": "ext-rae-lese-2018-claridad-1",
        "node_id": "rae-lese-claridad",
        "canonical_name": "Claridad",
        "node_type": "concepto",
        "primary_branch": "escritura",
        "secondary_branch": "estilo",
        "node_summary": "Rasgo de escritura orientado a facilitar comprension.",
        "short_definition": "Cualidad de un texto cuya estructura y expresion facilitan la comprension.",
        "aliases": ["claridad textual"],
        "relation_target": "manual-rasgos-escritura",
        "relation_type": "depende_de",
        "card_id": "card-claridad",
        "card_type": "style_trait",
        "card_name": "Claridad",
        "card_definition": "Criterio para hacer comprensible la estructura, el lexico y la progresion del texto.",
        "signals": ["estructura visible", "lexico preciso", "progresion informativa"],
        "risks": ["simplificar hasta perder matiz"],
        "contexts": ["redaccion", "revision", "estilo"],
        "evidence_id": "ev-rae-lese-claridad",
        "evidence_section": "claridad",
        "confidence": 0.64,
        "claim_id": "claim-rae-lese-claridad",
        "statement": "La claridad se logra coordinando estructura, lexico y progresion informativa para facilitar la comprension.",
        "claim_type": "stylistic",
        "domain": "writing.style",
        "related_node_ids": ["rae-dle-precision-lexica", "manual-rasgos-escritura"],
    },
    {
        "key": "concision",
        "source_id": "rae-lese",
        "source_edition_id": "rae-lese:edicion-2018",
        "index_id": "rae-lese:edicion-2018:concision",
        "index_title": "Concision",
        "index_locator": "Libro de estilo 2018 > redaccion > concision",
        "segment_id": "rae-lese:edicion-2018:concision:seg-1",
        "segment_title": "Concision y economia expresiva",
        "segment_text": "Resumen editorial minimo: la concision reduce material redundante sin eliminar informacion necesaria ni empobrecer el sentido.",
        "extraction_id": "ext-rae-lese-2018-concision-1",
        "node_id": "rae-lese-concision",
        "canonical_name": "Concision",
        "node_type": "concepto",
        "primary_branch": "escritura",
        "secondary_branch": "estilo",
        "node_summary": "Rasgo de economia expresiva sin perdida de informacion necesaria.",
        "short_definition": "Criterio de reduccion de redundancia manteniendo sentido y precision.",
        "aliases": ["economia expresiva"],
        "relation_target": "rae-lese-claridad",
        "relation_type": "relacionado_con",
        "card_id": "card-concision",
        "card_type": "style_trait",
        "card_name": "Concision",
        "card_definition": "Criterio para reducir redundancia sin perder informacion necesaria.",
        "signals": ["menos redundancia", "frase mas limpia", "informacion necesaria"],
        "risks": ["recortar hasta volver ambiguo el texto"],
        "contexts": ["redaccion", "revision", "estilo"],
        "evidence_id": "ev-rae-lese-concision",
        "evidence_section": "concision",
        "confidence": 0.63,
        "claim_id": "claim-rae-lese-concision",
        "statement": "La concision elimina redundancias, pero debe conservar la informacion necesaria para el sentido.",
        "claim_type": "stylistic",
        "domain": "writing.style",
        "related_node_ids": ["rae-lese-claridad", "rae-dle-precision-lexica"],
    },
    {
        "key": "repeticion",
        "source_id": "rae-lese",
        "source_edition_id": "rae-lese:edicion-2018",
        "index_id": "rae-lese:edicion-2018:repeticion",
        "index_title": "Repeticion",
        "index_locator": "Libro de estilo 2018 > redaccion > repeticion",
        "segment_id": "rae-lese:edicion-2018:repeticion:seg-1",
        "segment_title": "Repeticion y cohesion",
        "segment_text": "Resumen editorial minimo: la repeticion puede ser defecto si empobrece el texto, pero tambien recurso de cohesion o enfasis cuando responde a una funcion.",
        "extraction_id": "ext-rae-lese-2018-repeticion-1",
        "node_id": "rae-lese-repeticion",
        "canonical_name": "Repeticion",
        "node_type": "recurso",
        "primary_branch": "escritura",
        "secondary_branch": "cohesion",
        "node_summary": "Reiteracion que puede ser defecto, cohesion o enfasis segun funcion.",
        "short_definition": "Reiteracion de una forma o idea con posible valor defectivo o funcional.",
        "aliases": ["reiteracion"],
        "relation_target": "rae-lese-claridad",
        "relation_type": "relacionado_con",
        "card_id": "card-repeticion",
        "card_type": "style_trait",
        "card_name": "Repeticion",
        "card_definition": "Criterio para distinguir repeticion pobre de repeticion funcional.",
        "signals": ["reiteracion", "cohesion", "enfasis"],
        "risks": ["eliminar una repeticion que sostiene cohesion"],
        "contexts": ["redaccion", "revision", "estilo"],
        "evidence_id": "ev-rae-lese-repeticion",
        "evidence_section": "repeticion",
        "confidence": 0.62,
        "claim_id": "claim-rae-lese-repeticion",
        "statement": "La repeticion debe evaluarse por su funcion textual antes de eliminarse como defecto.",
        "claim_type": "stylistic",
        "domain": "writing.style",
        "related_node_ids": ["rae-lese-claridad", "manual-rasgos-escritura"],
    },
    {
        "key": "tono-formal",
        "source_id": "rae-lese",
        "source_edition_id": "rae-lese:edicion-2018",
        "index_id": "rae-lese:edicion-2018:tono-formal",
        "index_title": "Tono formal",
        "index_locator": "Libro de estilo 2018 > registros > tono formal",
        "segment_id": "rae-lese:edicion-2018:tono-formal:seg-1",
        "segment_title": "Tono formal",
        "segment_text": "Resumen editorial minimo: el tono formal ajusta tratamiento, lexico y distancia enunciativa al contexto comunicativo y al destinatario.",
        "extraction_id": "ext-rae-lese-2018-tono-formal-1",
        "node_id": "rae-lese-tono-formal",
        "canonical_name": "Tono formal",
        "node_type": "concepto",
        "primary_branch": "escritura",
        "secondary_branch": "registro",
        "node_summary": "Ajuste de distancia, lexico y tratamiento a contextos formales.",
        "short_definition": "Registro que conserva distancia y adecuacion al contexto institucional o cuidado.",
        "aliases": ["formalidad"],
        "relation_target": "rae-lese-registro",
        "relation_type": "es_parte_de",
        "card_id": "card-tono-formal",
        "card_type": "style_trait",
        "card_name": "Tono formal",
        "card_definition": "Criterio para ajustar distancia, tratamiento y lexico a contextos formales.",
        "signals": ["distancia", "tratamiento", "lexico cuidado"],
        "risks": ["volver el texto rigido o burocratico"],
        "contexts": ["redaccion", "registro", "comunicacion institucional"],
        "evidence_id": "ev-rae-lese-tono-formal",
        "evidence_section": "tono formal",
        "confidence": 0.61,
        "claim_id": "claim-rae-lese-tono-formal",
        "statement": "El tono formal adapta distancia, tratamiento y lexico al contexto comunicativo y al destinatario.",
        "claim_type": "stylistic",
        "domain": "writing.register",
        "related_node_ids": ["rae-lese-registro", "rae-lese-adecuacion-lector"],
    },
    {
        "key": "tono-directo",
        "source_id": "rae-lese",
        "source_edition_id": "rae-lese:edicion-2018",
        "index_id": "rae-lese:edicion-2018:tono-directo",
        "index_title": "Tono directo",
        "index_locator": "Libro de estilo 2018 > registros > tono directo",
        "segment_id": "rae-lese:edicion-2018:tono-directo:seg-1",
        "segment_title": "Tono directo",
        "segment_text": "Resumen editorial minimo: el tono directo reduce rodeos y hace visible la accion comunicativa sin perder adecuacion ni respeto.",
        "extraction_id": "ext-rae-lese-2018-tono-directo-1",
        "node_id": "rae-lese-tono-directo",
        "canonical_name": "Tono directo",
        "node_type": "concepto",
        "primary_branch": "escritura",
        "secondary_branch": "registro",
        "node_summary": "Rasgo de comunicacion clara y poco rodeada.",
        "short_definition": "Tono que formula la accion comunicativa de modo explicito y sin rodeos innecesarios.",
        "aliases": ["directividad"],
        "relation_target": "rae-lese-dinamismo-frase",
        "relation_type": "usa",
        "card_id": "card-tono-directo",
        "card_type": "style_trait",
        "card_name": "Tono directo",
        "card_definition": "Criterio para decir la accion comunicativa sin rodeos innecesarios.",
        "signals": ["verbo claro", "peticion visible", "menos rodeo"],
        "risks": ["sonar brusco si no se ajusta al contexto"],
        "contexts": ["redaccion", "comunicacion", "revision"],
        "evidence_id": "ev-rae-lese-tono-directo",
        "evidence_section": "tono directo",
        "confidence": 0.61,
        "claim_id": "claim-rae-lese-tono-directo",
        "statement": "El tono directo mejora la accion comunicativa cuando reduce rodeos sin romper adecuacion ni respeto.",
        "claim_type": "stylistic",
        "domain": "writing.register",
        "related_node_ids": ["rae-lese-dinamismo-frase", "rae-lese-adecuacion-lector"],
    },
    {
        "key": "coherencia-terminologica",
        "source_id": "martinez-sousa-mele",
        "source_edition_id": "martinez-sousa-mele:edicion-2015",
        "index_id": "martinez-sousa-mele:edicion-2015:coherencia-terminologica",
        "index_title": "Coherencia terminologica",
        "index_locator": "Edicion 2015 > estilo editorial > coherencia terminologica",
        "segment_id": "martinez-sousa-mele:edicion-2015:coherencia-terminologica:seg-1",
        "segment_title": "Coherencia terminologica",
        "segment_text": "Resumen editorial minimo: la coherencia terminologica mantiene denominaciones estables para un mismo concepto a lo largo de un texto.",
        "extraction_id": "ext-martinez-sousa-2015-coherencia-terminologica-1",
        "node_id": "martinez-sousa-coherencia-terminologica",
        "canonical_name": "Coherencia terminologica",
        "node_type": "metodo",
        "primary_branch": "edicion",
        "secondary_branch": "terminologia",
        "node_summary": "Metodo para mantener denominaciones estables en un texto.",
        "short_definition": "Consistencia en el uso de terminos para un mismo concepto.",
        "aliases": ["consistencia terminologica"],
        "relation_target": "martinez-sousa-criterio-editorial",
        "relation_type": "es_parte_de",
        "card_id": "card-coherencia-terminologica",
        "card_type": "editing_method",
        "card_name": "Coherencia terminologica",
        "card_definition": "Criterio para mantener terminos estables para un mismo concepto.",
        "signals": ["termino estable", "mismo concepto", "glosario"],
        "risks": ["variar terminos por estilo y crear ambiguedad"],
        "contexts": ["edicion", "texto tecnico", "revision"],
        "evidence_id": "ev-martinez-sousa-coherencia-terminologica",
        "evidence_section": "coherencia terminologica",
        "confidence": 0.63,
        "claim_id": "claim-martinez-sousa-coherencia-terminologica",
        "statement": "La coherencia terminologica exige mantener denominaciones estables para un mismo concepto a lo largo del texto.",
        "claim_type": "editing",
        "domain": "editing.consistency",
        "related_node_ids": ["martinez-sousa-criterio-editorial", "rae-gtg-terminologia-gramatical"],
    },
    {
        "key": "registro",
        "source_id": "rae-lese",
        "source_edition_id": "rae-lese:edicion-2018",
        "index_id": "rae-lese:edicion-2018:registro",
        "index_title": "Registro",
        "index_locator": "Libro de estilo 2018 > registros > registro",
        "segment_id": "rae-lese:edicion-2018:registro:seg-1",
        "segment_title": "Registro comunicativo",
        "segment_text": "Resumen editorial minimo: el registro ajusta el texto a situacion, canal, relacion entre interlocutores y expectativas del genero.",
        "extraction_id": "ext-rae-lese-2018-registro-1",
        "node_id": "rae-lese-registro",
        "canonical_name": "Registro",
        "node_type": "concepto",
        "primary_branch": "escritura",
        "secondary_branch": "registro",
        "node_summary": "Ajuste linguistico a situacion comunicativa y genero.",
        "short_definition": "Variedad de uso ajustada a situacion, canal, destinatario y genero.",
        "aliases": ["registro comunicativo"],
        "relation_target": "rae-lese-adecuacion-lector",
        "relation_type": "depende_de",
        "card_id": "card-registro",
        "card_type": "style_trait",
        "card_name": "Registro",
        "card_definition": "Criterio para ajustar el texto a situacion, canal, destinatario y genero.",
        "signals": ["situacion", "canal", "destinatario", "genero"],
        "risks": ["mezclar registros sin intencion textual"],
        "contexts": ["redaccion", "registro", "estilo"],
        "evidence_id": "ev-rae-lese-registro",
        "evidence_section": "registro",
        "confidence": 0.62,
        "claim_id": "claim-rae-lese-registro",
        "statement": "El registro textual debe ajustarse a situacion, canal, destinatario y genero.",
        "claim_type": "stylistic",
        "domain": "writing.register",
        "related_node_ids": ["rae-lese-adecuacion-lector", "rae-lese-tono-formal"],
    },
    {
        "key": "adecuacion-lector",
        "source_id": "rae-lese",
        "source_edition_id": "rae-lese:edicion-2018",
        "index_id": "rae-lese:edicion-2018:adecuacion-lector",
        "index_title": "Adecuacion al lector",
        "index_locator": "Libro de estilo 2018 > redaccion > adecuacion al lector",
        "segment_id": "rae-lese:edicion-2018:adecuacion-lector:seg-1",
        "segment_title": "Adecuacion al lector",
        "segment_text": "Resumen editorial minimo: la adecuacion al lector ajusta informacion, tono y densidad segun conocimientos, expectativas y finalidad comunicativa.",
        "extraction_id": "ext-rae-lese-2018-adecuacion-lector-1",
        "node_id": "rae-lese-adecuacion-lector",
        "canonical_name": "Adecuacion al lector",
        "node_type": "metodo",
        "primary_branch": "escritura",
        "secondary_branch": "adecuacion",
        "node_summary": "Ajuste de informacion, tono y densidad al lector previsto.",
        "short_definition": "Criterio de revision que adapta el texto al lector y finalidad.",
        "aliases": ["adecuacion al destinatario"],
        "relation_target": "rae-lese-claridad",
        "relation_type": "usa",
        "card_id": "card-adecuacion-lector",
        "card_type": "editing_method",
        "card_name": "Adecuacion al lector",
        "card_definition": "Criterio para ajustar informacion, tono y densidad al lector previsto.",
        "signals": ["lector", "expectativas", "finalidad"],
        "risks": ["explicar demasiado o demasiado poco para el destinatario"],
        "contexts": ["redaccion", "revision", "comunicacion"],
        "evidence_id": "ev-rae-lese-adecuacion-lector",
        "evidence_section": "adecuacion al lector",
        "confidence": 0.63,
        "claim_id": "claim-rae-lese-adecuacion-lector",
        "statement": "La adecuacion al lector ajusta informacion, tono y densidad a conocimientos, expectativas y finalidad comunicativa.",
        "claim_type": "editing",
        "domain": "writing.audience",
        "related_node_ids": ["rae-lese-claridad", "rae-lese-registro"],
    },
]

V11_SEED_ITEMS = [
    {
        "key": "coherencia-textual",
        "source_id": "reyes-arte-escribir",
        "source_edition_id": "reyes-arte-escribir:edicion-2012",
        "index_id": "reyes-arte-escribir:edicion-2012:coherencia-textual",
        "index_title": "Coherencia textual",
        "index_locator": "Edicion 2012 > texto y sentido > coherencia textual",
        "segment_id": "reyes-arte-escribir:edicion-2012:coherencia-textual:seg-1",
        "segment_title": "Coherencia textual en redaccion",
        "segment_text": "Resumen editorial minimo: la coherencia textual organiza las ideas para que cada parte sostenga el sentido global y no contradiga el proposito del texto.",
        "extraction_id": "ext-reyes-2012-coherencia-textual-1",
        "node_id": "reyes-coherencia-textual",
        "canonical_name": "Coherencia textual",
        "node_type": "concepto",
        "primary_branch": "escritura",
        "secondary_branch": "organizacion textual",
        "node_summary": "Relacion de sentido que mantiene unido el texto completo.",
        "short_definition": "Criterio por el que las partes del texto sostienen un sentido global compatible.",
        "aliases": ["coherencia del texto"],
        "relation_target": "rae-lese-claridad",
        "relation_type": "depende_de",
        "card_id": "card-coherencia-textual",
        "card_type": "writing_method",
        "card_name": "Coherencia textual",
        "card_definition": "Criterio para revisar que las ideas sostengan un sentido global sin contradicciones.",
        "signals": ["sentido global", "ideas compatibles", "proposito textual"],
        "risks": ["corregir frases aisladas sin revisar el conjunto"],
        "contexts": ["redaccion", "revision", "ensayo"],
        "evidence_id": "ev-reyes-coherencia-textual",
        "evidence_section": "coherencia textual",
        "confidence": 0.62,
        "claim_id": "claim-reyes-coherencia-textual",
        "statement": "La coherencia textual exige que las partes del texto sostengan un sentido global compatible con su proposito.",
        "claim_type": "stylistic",
        "domain": "writing.coherence",
        "related_node_ids": ["rae-lese-claridad", "manual-rasgos-escritura"],
    },
    {
        "key": "progresion-informativa",
        "source_id": "reyes-arte-escribir",
        "source_edition_id": "reyes-arte-escribir:edicion-2012",
        "index_id": "reyes-arte-escribir:edicion-2012:progresion-informativa",
        "index_title": "Progresion informativa",
        "index_locator": "Edicion 2012 > texto y sentido > progresion informativa",
        "segment_id": "reyes-arte-escribir:edicion-2012:progresion-informativa:seg-1",
        "segment_title": "Orden de informacion",
        "segment_text": "Resumen editorial minimo: la progresion informativa introduce, retoma y desarrolla datos en un orden que permite seguir el avance del texto.",
        "extraction_id": "ext-reyes-2012-progresion-informativa-1",
        "node_id": "reyes-progresion-informativa",
        "canonical_name": "Progresion informativa",
        "node_type": "metodo",
        "primary_branch": "escritura",
        "secondary_branch": "organizacion textual",
        "node_summary": "Avance ordenado de datos e ideas dentro del texto.",
        "short_definition": "Orden que introduce, retoma y desarrolla informacion de modo seguible.",
        "aliases": ["avance informativo"],
        "relation_target": "reyes-coherencia-textual",
        "relation_type": "es_parte_de",
        "card_id": "card-progresion-informativa",
        "card_type": "writing_method",
        "card_name": "Progresion informativa",
        "card_definition": "Criterio para ordenar informacion nueva y conocida en el avance del texto.",
        "signals": ["informacion nueva", "informacion conocida", "avance"],
        "risks": ["saltar entre ideas sin puente"],
        "contexts": ["redaccion", "revision", "articulo"],
        "evidence_id": "ev-reyes-progresion-informativa",
        "evidence_section": "progresion informativa",
        "confidence": 0.62,
        "claim_id": "claim-reyes-progresion-informativa",
        "statement": "La progresion informativa ordena informacion conocida y nueva para que el texto avance sin saltos bruscos.",
        "claim_type": "stylistic",
        "domain": "writing.coherence",
        "related_node_ids": ["reyes-coherencia-textual", "rae-lese-claridad"],
    },
    {
        "key": "conectores",
        "source_id": "reyes-arte-escribir",
        "source_edition_id": "reyes-arte-escribir:edicion-2012",
        "index_id": "reyes-arte-escribir:edicion-2012:conectores",
        "index_title": "Conectores",
        "index_locator": "Edicion 2012 > cohesion > conectores",
        "segment_id": "reyes-arte-escribir:edicion-2012:conectores:seg-1",
        "segment_title": "Conectores y relaciones logicas",
        "segment_text": "Resumen editorial minimo: los conectores hacen explicitas relaciones logicas entre enunciados, pero deben responder a una relacion real y no decorar el texto.",
        "extraction_id": "ext-reyes-2012-conectores-1",
        "node_id": "reyes-conectores",
        "canonical_name": "Conectores",
        "node_type": "recurso",
        "primary_branch": "escritura",
        "secondary_branch": "cohesion",
        "node_summary": "Recursos que explicitan relaciones logicas entre segmentos.",
        "short_definition": "Palabras o expresiones que orientan la relacion entre partes del texto.",
        "aliases": ["marcadores discursivos", "enlaces textuales"],
        "relation_target": "reyes-progresion-informativa",
        "relation_type": "usa",
        "card_id": "card-conectores",
        "card_type": "writing_resource",
        "card_name": "Conectores",
        "card_definition": "Criterio para usar conectores que expresen relaciones logicas reales.",
        "signals": ["por tanto", "sin embargo", "ademas", "relacion logica"],
        "risks": ["anadir conectores decorativos o contradictorios"],
        "contexts": ["redaccion", "revision", "ensayo"],
        "evidence_id": "ev-reyes-conectores",
        "evidence_section": "conectores",
        "confidence": 0.61,
        "claim_id": "claim-reyes-conectores",
        "statement": "Los conectores deben expresar relaciones logicas reales entre partes del texto, no funcionar como adorno.",
        "claim_type": "stylistic",
        "domain": "writing.cohesion",
        "related_node_ids": ["reyes-progresion-informativa", "rae-lese-claridad"],
    },
    {
        "key": "enfoque-lector",
        "source_id": "reyes-arte-escribir",
        "source_edition_id": "reyes-arte-escribir:edicion-2012",
        "index_id": "reyes-arte-escribir:edicion-2012:enfoque-lector",
        "index_title": "Enfoque del lector",
        "index_locator": "Edicion 2012 > pragmatica > enfoque del lector",
        "segment_id": "reyes-arte-escribir:edicion-2012:enfoque-lector:seg-1",
        "segment_title": "Lector previsto",
        "segment_text": "Resumen editorial minimo: escribir para un lector previsto obliga a seleccionar informacion, tono y explicaciones segun lo que ese lector necesita para comprender.",
        "extraction_id": "ext-reyes-2012-enfoque-lector-1",
        "node_id": "reyes-enfoque-lector",
        "canonical_name": "Enfoque del lector",
        "node_type": "metodo",
        "primary_branch": "escritura",
        "secondary_branch": "pragmatica",
        "node_summary": "Metodo para ajustar el texto a las necesidades del lector previsto.",
        "short_definition": "Criterio de seleccion de informacion, tono y explicacion segun lector.",
        "aliases": ["lector previsto", "destinatario"],
        "relation_target": "rae-lese-adecuacion-lector",
        "relation_type": "equivale_a",
        "card_id": "card-enfoque-lector",
        "card_type": "writing_method",
        "card_name": "Enfoque del lector",
        "card_definition": "Criterio para seleccionar informacion y tono segun el lector previsto.",
        "signals": ["lector previsto", "necesidad de informacion", "tono adecuado"],
        "risks": ["escribir desde lo que sabe el autor y no desde lo que necesita el lector"],
        "contexts": ["redaccion", "revision", "comunicacion"],
        "evidence_id": "ev-reyes-enfoque-lector",
        "evidence_section": "enfoque del lector",
        "confidence": 0.62,
        "claim_id": "claim-reyes-enfoque-lector",
        "statement": "El enfoque del lector obliga a seleccionar informacion, tono y explicaciones segun las necesidades del destinatario previsto.",
        "claim_type": "editing",
        "domain": "writing.audience",
        "related_node_ids": ["rae-lese-adecuacion-lector", "rae-lese-registro"],
    },
    {
        "key": "revision-borrador",
        "source_id": "reyes-arte-escribir",
        "source_edition_id": "reyes-arte-escribir:edicion-2012",
        "index_id": "reyes-arte-escribir:edicion-2012:revision-borrador",
        "index_title": "Revision del borrador",
        "index_locator": "Edicion 2012 > proceso de escritura > revision del borrador",
        "segment_id": "reyes-arte-escribir:edicion-2012:revision-borrador:seg-1",
        "segment_title": "Revision como fase de escritura",
        "segment_text": "Resumen editorial minimo: la revision del borrador no es solo correccion superficial; comprueba organizacion, sentido, precision y adecuacion antes de cerrar el texto.",
        "extraction_id": "ext-reyes-2012-revision-borrador-1",
        "node_id": "reyes-revision-borrador",
        "canonical_name": "Revision del borrador",
        "node_type": "metodo",
        "primary_branch": "escritura",
        "secondary_branch": "proceso",
        "node_summary": "Fase de escritura que comprueba organizacion, sentido y adecuacion.",
        "short_definition": "Metodo de relectura y ajuste antes de cerrar un texto.",
        "aliases": ["revision de borrador", "reescritura"],
        "relation_target": "martinez-sousa-criterio-editorial",
        "relation_type": "relacionado_con",
        "card_id": "card-revision-borrador",
        "card_type": "editing_method",
        "card_name": "Revision del borrador",
        "card_definition": "Criterio para revisar organizacion, sentido, precision y adecuacion antes de cerrar.",
        "signals": ["borrador", "reescritura", "organizacion", "adecuacion"],
        "risks": ["limitar la revision a ortografia o superficie"],
        "contexts": ["revision", "redaccion", "edicion"],
        "evidence_id": "ev-reyes-revision-borrador",
        "evidence_section": "revision del borrador",
        "confidence": 0.62,
        "claim_id": "claim-reyes-revision-borrador",
        "statement": "La revision del borrador debe comprobar organizacion, sentido, precision y adecuacion, no solo correccion superficial.",
        "claim_type": "editing",
        "domain": "editing.revision",
        "related_node_ids": ["reyes-coherencia-textual", "martinez-sousa-criterio-editorial"],
    },
]

V12_SEED_ITEMS = [
    {
        "key": "versalitas",
        "source_id": "martinez-sousa-ortotipografia",
        "source_edition_id": "martinez-sousa-ortotipografia:edicion-2014",
        "index_id": "martinez-sousa-ortotipografia:edicion-2014:versalitas",
        "index_title": "Versalitas",
        "index_locator": "Edicion 2014 > composicion > versalitas",
        "segment_id": "martinez-sousa-ortotipografia:edicion-2014:versalitas:seg-1",
        "segment_title": "Uso editorial de versalitas",
        "segment_text": "Resumen editorial minimo: las versalitas son un recurso tipografico especializado y deben reservarse para convenciones editoriales estables, no para destacar por capricho.",
        "extraction_id": "ext-martinez-sousa-ortotipografia-2014-versalitas-1",
        "node_id": "martinez-sousa-versalitas",
        "canonical_name": "Versalitas",
        "node_type": "recurso",
        "primary_branch": "edicion",
        "secondary_branch": "ortotipografia",
        "node_summary": "Recurso tipografico de composicion editorial especializada.",
        "short_definition": "Letra con forma de mayuscula y altura aproximada de minuscula usada por convencion editorial.",
        "aliases": ["versalita"],
        "relation_target": "martinez-sousa-criterio-editorial",
        "relation_type": "es_parte_de",
        "card_id": "card-versalitas",
        "card_type": "orthotypography_rule",
        "card_name": "Versalitas",
        "card_definition": "Criterio para reservar versalitas a convenciones editoriales estables.",
        "signals": ["composicion", "convencion editorial", "destacado tipografico"],
        "risks": ["usar versalitas como enfasis decorativo"],
        "contexts": ["edicion", "ortotipografia", "maquetacion"],
        "evidence_id": "ev-martinez-sousa-versalitas",
        "evidence_section": "versalitas",
        "confidence": 0.61,
        "claim_id": "claim-martinez-sousa-versalitas",
        "statement": "Las versalitas deben responder a una convencion editorial estable y no a un destacado decorativo.",
        "claim_type": "orthographic",
        "domain": "orthography.orthotypography",
        "related_node_ids": ["martinez-sousa-criterio-editorial", "rae-ole-mayusculas"],
    },
    {
        "key": "jerarquia-comillas",
        "source_id": "martinez-sousa-ortotipografia",
        "source_edition_id": "martinez-sousa-ortotipografia:edicion-2014",
        "index_id": "martinez-sousa-ortotipografia:edicion-2014:jerarquia-comillas",
        "index_title": "Jerarquia de comillas",
        "index_locator": "Edicion 2014 > signos > jerarquia de comillas",
        "segment_id": "martinez-sousa-ortotipografia:edicion-2014:jerarquia-comillas:seg-1",
        "segment_title": "Comillas dentro de comillas",
        "segment_text": "Resumen editorial minimo: la jerarquia de comillas ordena los tipos de comillas cuando una cita contiene otra cita, manteniendo criterio editorial consistente.",
        "extraction_id": "ext-martinez-sousa-ortotipografia-2014-jerarquia-comillas-1",
        "node_id": "martinez-sousa-jerarquia-comillas",
        "canonical_name": "Jerarquia de comillas",
        "node_type": "norma",
        "primary_branch": "ortografia",
        "secondary_branch": "ortotipografia",
        "node_summary": "Orden de uso de comillas en citas anidadas.",
        "short_definition": "Criterio para alternar tipos de comillas cuando hay citas dentro de citas.",
        "aliases": ["comillas anidadas"],
        "relation_target": "rae-ole-comillas",
        "relation_type": "relacionado_con",
        "card_id": "card-jerarquia-comillas",
        "card_type": "orthotypography_rule",
        "card_name": "Jerarquia de comillas",
        "card_definition": "Criterio para mantener orden consistente en comillas anidadas.",
        "signals": ["cita anidada", "comillas espanolas", "comillas inglesas"],
        "risks": ["mezclar tipos de comillas sin jerarquia"],
        "contexts": ["citas", "edicion", "ortotipografia"],
        "evidence_id": "ev-martinez-sousa-jerarquia-comillas",
        "evidence_section": "jerarquia de comillas",
        "confidence": 0.62,
        "claim_id": "claim-martinez-sousa-jerarquia-comillas",
        "statement": "Las citas anidadas requieren una jerarquia estable de comillas para conservar claridad editorial.",
        "claim_type": "orthographic",
        "domain": "orthography.punctuation",
        "related_node_ids": ["rae-ole-comillas", "martinez-sousa-criterio-editorial"],
    },
    {
        "key": "espacios-signos",
        "source_id": "martinez-sousa-ortotipografia",
        "source_edition_id": "martinez-sousa-ortotipografia:edicion-2014",
        "index_id": "martinez-sousa-ortotipografia:edicion-2014:espacios-signos",
        "index_title": "Espacios ante signos",
        "index_locator": "Edicion 2014 > composicion > espacios ante signos",
        "segment_id": "martinez-sousa-ortotipografia:edicion-2014:espacios-signos:seg-1",
        "segment_title": "Espaciado y puntuacion",
        "segment_text": "Resumen editorial minimo: el espaciado alrededor de signos de puntuacion pertenece a la composicion ortotipografica y debe mantenerse uniforme.",
        "extraction_id": "ext-martinez-sousa-ortotipografia-2014-espacios-signos-1",
        "node_id": "martinez-sousa-espacios-signos",
        "canonical_name": "Espacios ante signos",
        "node_type": "norma",
        "primary_branch": "edicion",
        "secondary_branch": "ortotipografia",
        "node_summary": "Criterio de espaciado uniforme alrededor de signos de puntuacion.",
        "short_definition": "Regla de composicion que fija separaciones alrededor de signos.",
        "aliases": ["espaciado ortotipografico"],
        "relation_target": "rae-ole-coma",
        "relation_type": "relacionado_con",
        "card_id": "card-espacios-signos",
        "card_type": "orthotypography_rule",
        "card_name": "Espacios ante signos",
        "card_definition": "Criterio para mantener espaciado uniforme alrededor de signos.",
        "signals": ["espacio", "signo", "composicion"],
        "risks": ["mezclar criterios de espaciado en un mismo texto"],
        "contexts": ["edicion", "maquetacion", "revision"],
        "evidence_id": "ev-martinez-sousa-espacios-signos",
        "evidence_section": "espacios ante signos",
        "confidence": 0.61,
        "claim_id": "claim-martinez-sousa-espacios-signos",
        "statement": "El espaciado alrededor de signos debe seguir un criterio ortotipografico uniforme dentro del texto.",
        "claim_type": "orthographic",
        "domain": "orthography.orthotypography",
        "related_node_ids": ["rae-ole-coma", "martinez-sousa-coherencia-terminologica"],
    },
    {
        "key": "citas-bibliograficas",
        "source_id": "martinez-sousa-ortotipografia",
        "source_edition_id": "martinez-sousa-ortotipografia:edicion-2014",
        "index_id": "martinez-sousa-ortotipografia:edicion-2014:citas-bibliograficas",
        "index_title": "Citas bibliograficas",
        "index_locator": "Edicion 2014 > aparato critico > citas bibliograficas",
        "segment_id": "martinez-sousa-ortotipografia:edicion-2014:citas-bibliograficas:seg-1",
        "segment_title": "Consistencia en referencias",
        "segment_text": "Resumen editorial minimo: las citas bibliograficas requieren un sistema constante para ordenar autor, titulo, datos editoriales y localizadores.",
        "extraction_id": "ext-martinez-sousa-ortotipografia-2014-citas-bibliograficas-1",
        "node_id": "martinez-sousa-citas-bibliograficas",
        "canonical_name": "Citas bibliograficas",
        "node_type": "metodo",
        "primary_branch": "edicion",
        "secondary_branch": "aparato critico",
        "node_summary": "Metodo para mantener referencias bibliograficas consistentes.",
        "short_definition": "Sistema constante de presentacion de datos bibliograficos y localizadores.",
        "aliases": ["referencias bibliograficas"],
        "relation_target": "martinez-sousa-coherencia-terminologica",
        "relation_type": "usa",
        "card_id": "card-citas-bibliograficas",
        "card_type": "editing_method",
        "card_name": "Citas bibliograficas",
        "card_definition": "Criterio para mantener un sistema constante de referencias.",
        "signals": ["autor", "titulo", "editorial", "localizador"],
        "risks": ["alternar formatos de cita dentro del mismo trabajo"],
        "contexts": ["edicion", "ensayo", "aparato critico"],
        "evidence_id": "ev-martinez-sousa-citas-bibliograficas",
        "evidence_section": "citas bibliograficas",
        "confidence": 0.61,
        "claim_id": "claim-martinez-sousa-citas-bibliograficas",
        "statement": "Las citas bibliograficas deben seguir un sistema constante de ordenacion y presentacion de datos.",
        "claim_type": "editing",
        "domain": "editing.references",
        "related_node_ids": ["martinez-sousa-coherencia-terminologica", "martinez-sousa-criterio-editorial"],
    },
    {
        "key": "cursiva-titulos",
        "source_id": "martinez-sousa-ortotipografia",
        "source_edition_id": "martinez-sousa-ortotipografia:edicion-2014",
        "index_id": "martinez-sousa-ortotipografia:edicion-2014:cursiva-titulos",
        "index_title": "Cursiva en titulos",
        "index_locator": "Edicion 2014 > estilos tipograficos > cursiva en titulos",
        "segment_id": "martinez-sousa-ortotipografia:edicion-2014:cursiva-titulos:seg-1",
        "segment_title": "Titulos y marca tipografica",
        "segment_text": "Resumen editorial minimo: la cursiva en titulos depende del tipo de obra o unidad citada y debe aplicarse con criterio constante.",
        "extraction_id": "ext-martinez-sousa-ortotipografia-2014-cursiva-titulos-1",
        "node_id": "martinez-sousa-cursiva-titulos",
        "canonical_name": "Cursiva en titulos",
        "node_type": "norma",
        "primary_branch": "edicion",
        "secondary_branch": "ortotipografia",
        "node_summary": "Criterio para marcar tipograficamente titulos de obras y unidades citadas.",
        "short_definition": "Uso de cursiva segun el tipo de titulo o unidad bibliografica.",
        "aliases": ["titulos en cursiva"],
        "relation_target": "fundeu-cursiva-extranjerismos",
        "relation_type": "relacionado_con",
        "card_id": "card-cursiva-titulos",
        "card_type": "orthotypography_rule",
        "card_name": "Cursiva en titulos",
        "card_definition": "Criterio para aplicar cursiva a titulos con consistencia editorial.",
        "signals": ["titulo", "obra", "cursiva"],
        "risks": ["marcar unos titulos y otros no sin criterio"],
        "contexts": ["edicion", "bibliografia", "ortotipografia"],
        "evidence_id": "ev-martinez-sousa-cursiva-titulos",
        "evidence_section": "cursiva en titulos",
        "confidence": 0.61,
        "claim_id": "claim-martinez-sousa-cursiva-titulos",
        "statement": "La cursiva en titulos debe aplicarse segun el tipo de obra o unidad citada y con criterio constante.",
        "claim_type": "orthographic",
        "domain": "orthography.orthotypography",
        "related_node_ids": ["fundeu-cursiva-extranjerismos", "martinez-sousa-criterio-editorial"],
    },
]

V13_SEED_ITEMS = [
    {
        "key": "tema-texto-literario",
        "source_id": "lazaro-correa-comentario-texto",
        "source_edition_id": "lazaro-correa-comentario-texto:edicion-1974",
        "index_id": "lazaro-correa-comentario-texto:edicion-1974:tema-texto-literario",
        "index_title": "Tema del texto literario",
        "index_locator": "Edicion 1974 > comentario > tema",
        "segment_id": "lazaro-correa-comentario-texto:edicion-1974:tema-texto-literario:seg-1",
        "segment_title": "Determinacion del tema",
        "segment_text": "Resumen editorial minimo: el tema de un texto literario sintetiza el nucleo de sentido que organiza sus motivos, tono y desarrollo.",
        "extraction_id": "ext-lazaro-correa-1974-tema-texto-literario-1",
        "node_id": "lazaro-correa-tema-texto-literario",
        "canonical_name": "Tema del texto literario",
        "node_type": "concepto",
        "primary_branch": "literatura",
        "secondary_branch": "comentario de texto",
        "node_summary": "Nucleo de sentido que organiza motivos y desarrollo textual.",
        "short_definition": "Idea central que articula los motivos y la interpretacion de un texto literario.",
        "aliases": ["tema literario"],
        "relation_target": "manual-rasgos-escritura",
        "relation_type": "relacionado_con",
        "card_id": "card-tema-texto-literario",
        "card_type": "analysis_method",
        "card_name": "Tema del texto literario",
        "card_definition": "Criterio para formular el nucleo de sentido de un texto literario.",
        "signals": ["nucleo de sentido", "motivos", "interpretacion"],
        "risks": ["confundir tema con resumen argumental"],
        "contexts": ["comentario de texto", "literatura", "lectura"],
        "evidence_id": "ev-lazaro-correa-tema-texto-literario",
        "evidence_section": "tema",
        "confidence": 0.61,
        "claim_id": "claim-lazaro-correa-tema-texto-literario",
        "statement": "El tema sintetiza el nucleo de sentido que organiza motivos, tono y desarrollo del texto literario.",
        "claim_type": "stylistic",
        "domain": "literary_analysis.theme",
        "related_node_ids": ["manual-rasgos-escritura", "reyes-coherencia-textual"],
    },
    {
        "key": "estructura-externa",
        "source_id": "lazaro-correa-comentario-texto",
        "source_edition_id": "lazaro-correa-comentario-texto:edicion-1974",
        "index_id": "lazaro-correa-comentario-texto:edicion-1974:estructura-externa",
        "index_title": "Estructura externa",
        "index_locator": "Edicion 1974 > comentario > estructura externa",
        "segment_id": "lazaro-correa-comentario-texto:edicion-1974:estructura-externa:seg-1",
        "segment_title": "Partes visibles del texto",
        "segment_text": "Resumen editorial minimo: la estructura externa describe la division visible del texto en estrofas, parrafos, escenas o apartados.",
        "extraction_id": "ext-lazaro-correa-1974-estructura-externa-1",
        "node_id": "lazaro-correa-estructura-externa",
        "canonical_name": "Estructura externa",
        "node_type": "metodo",
        "primary_branch": "literatura",
        "secondary_branch": "comentario de texto",
        "node_summary": "Descripcion de la organizacion visible del texto.",
        "short_definition": "Division formal observable en partes, estrofas, parrafos, escenas o apartados.",
        "aliases": ["division externa"],
        "relation_target": "lazaro-correa-tema-texto-literario",
        "relation_type": "describe",
        "card_id": "card-estructura-externa",
        "card_type": "analysis_method",
        "card_name": "Estructura externa",
        "card_definition": "Criterio para describir la division formal visible de un texto.",
        "signals": ["estrofa", "parrafo", "escena", "apartado"],
        "risks": ["deducir interpretacion antes de describir la forma visible"],
        "contexts": ["comentario de texto", "literatura", "analisis"],
        "evidence_id": "ev-lazaro-correa-estructura-externa",
        "evidence_section": "estructura externa",
        "confidence": 0.6,
        "claim_id": "claim-lazaro-correa-estructura-externa",
        "statement": "La estructura externa describe la division formal visible del texto antes de interpretar su funcion.",
        "claim_type": "stylistic",
        "domain": "literary_analysis.structure",
        "related_node_ids": ["lazaro-correa-tema-texto-literario", "manual-rasgos-escritura"],
    },
    {
        "key": "estructura-interna",
        "source_id": "lazaro-correa-comentario-texto",
        "source_edition_id": "lazaro-correa-comentario-texto:edicion-1974",
        "index_id": "lazaro-correa-comentario-texto:edicion-1974:estructura-interna",
        "index_title": "Estructura interna",
        "index_locator": "Edicion 1974 > comentario > estructura interna",
        "segment_id": "lazaro-correa-comentario-texto:edicion-1974:estructura-interna:seg-1",
        "segment_title": "Organizacion del sentido",
        "segment_text": "Resumen editorial minimo: la estructura interna explica como progresan las ideas, tensiones o motivos dentro del texto.",
        "extraction_id": "ext-lazaro-correa-1974-estructura-interna-1",
        "node_id": "lazaro-correa-estructura-interna",
        "canonical_name": "Estructura interna",
        "node_type": "metodo",
        "primary_branch": "literatura",
        "secondary_branch": "comentario de texto",
        "node_summary": "Organizacion del sentido y progresion de motivos dentro del texto.",
        "short_definition": "Distribucion interpretativa de ideas, tensiones o motivos en el desarrollo textual.",
        "aliases": ["organizacion interna"],
        "relation_target": "lazaro-correa-estructura-externa",
        "relation_type": "compara_con",
        "card_id": "card-estructura-interna",
        "card_type": "analysis_method",
        "card_name": "Estructura interna",
        "card_definition": "Criterio para explicar la progresion de sentido dentro del texto.",
        "signals": ["progresion", "motivos", "tension", "desarrollo"],
        "risks": ["confundir partes visibles con desarrollo del sentido"],
        "contexts": ["comentario de texto", "interpretacion", "literatura"],
        "evidence_id": "ev-lazaro-correa-estructura-interna",
        "evidence_section": "estructura interna",
        "confidence": 0.61,
        "claim_id": "claim-lazaro-correa-estructura-interna",
        "statement": "La estructura interna explica la progresion de ideas, tensiones o motivos que construyen el sentido del texto.",
        "claim_type": "stylistic",
        "domain": "literary_analysis.structure",
        "related_node_ids": ["lazaro-correa-estructura-externa", "reyes-progresion-informativa"],
    },
    {
        "key": "forma-contenido",
        "source_id": "lazaro-correa-comentario-texto",
        "source_edition_id": "lazaro-correa-comentario-texto:edicion-1974",
        "index_id": "lazaro-correa-comentario-texto:edicion-1974:forma-contenido",
        "index_title": "Forma y contenido",
        "index_locator": "Edicion 1974 > comentario > forma y contenido",
        "segment_id": "lazaro-correa-comentario-texto:edicion-1974:forma-contenido:seg-1",
        "segment_title": "Relacion entre expresion y sentido",
        "segment_text": "Resumen editorial minimo: el comentario debe relacionar recursos formales con efectos de sentido, evitando separar forma y contenido como planos independientes.",
        "extraction_id": "ext-lazaro-correa-1974-forma-contenido-1",
        "node_id": "lazaro-correa-forma-contenido",
        "canonical_name": "Forma y contenido",
        "node_type": "metodo",
        "primary_branch": "literatura",
        "secondary_branch": "comentario de texto",
        "node_summary": "Relacion entre recursos expresivos y efectos de sentido.",
        "short_definition": "Metodo que vincula procedimientos formales con significado e interpretacion.",
        "aliases": ["relacion forma contenido"],
        "relation_target": "lazaro-correa-estructura-interna",
        "relation_type": "depende_de",
        "card_id": "card-forma-contenido",
        "card_type": "analysis_method",
        "card_name": "Forma y contenido",
        "card_definition": "Criterio para vincular recursos formales con efectos de sentido.",
        "signals": ["recurso formal", "efecto de sentido", "interpretacion"],
        "risks": ["listar recursos sin explicar su funcion"],
        "contexts": ["comentario de texto", "estilo", "literatura"],
        "evidence_id": "ev-lazaro-correa-forma-contenido",
        "evidence_section": "forma y contenido",
        "confidence": 0.62,
        "claim_id": "claim-lazaro-correa-forma-contenido",
        "statement": "El comentario literario debe relacionar recursos formales con efectos de sentido, no separarlos como planos independientes.",
        "claim_type": "stylistic",
        "domain": "literary_analysis.style",
        "related_node_ids": ["lazaro-correa-estructura-interna", "rae-lese-repeticion"],
    },
    {
        "key": "comentario-critico",
        "source_id": "lazaro-correa-comentario-texto",
        "source_edition_id": "lazaro-correa-comentario-texto:edicion-1974",
        "index_id": "lazaro-correa-comentario-texto:edicion-1974:comentario-critico",
        "index_title": "Comentario critico",
        "index_locator": "Edicion 1974 > comentario > valoracion",
        "segment_id": "lazaro-correa-comentario-texto:edicion-1974:comentario-critico:seg-1",
        "segment_title": "Valoracion argumentada",
        "segment_text": "Resumen editorial minimo: el comentario critico formula una valoracion apoyada en observaciones del texto, no en impresiones sueltas.",
        "extraction_id": "ext-lazaro-correa-1974-comentario-critico-1",
        "node_id": "lazaro-correa-comentario-critico",
        "canonical_name": "Comentario critico",
        "node_type": "metodo",
        "primary_branch": "literatura",
        "secondary_branch": "comentario de texto",
        "node_summary": "Valoracion argumentada a partir de observaciones textuales.",
        "short_definition": "Cierre interpretativo que justifica una valoracion con evidencias del texto.",
        "aliases": ["valoracion critica"],
        "relation_target": "lazaro-correa-forma-contenido",
        "relation_type": "requiere",
        "card_id": "card-comentario-critico",
        "card_type": "analysis_method",
        "card_name": "Comentario critico",
        "card_definition": "Criterio para formular una valoracion apoyada en observaciones textuales.",
        "signals": ["valoracion", "argumento", "observacion textual"],
        "risks": ["cerrar con opiniones no sustentadas por el texto"],
        "contexts": ["comentario de texto", "critica", "literatura"],
        "evidence_id": "ev-lazaro-correa-comentario-critico",
        "evidence_section": "comentario critico",
        "confidence": 0.61,
        "claim_id": "claim-lazaro-correa-comentario-critico",
        "statement": "El comentario critico debe apoyar su valoracion en observaciones textuales y no en impresiones aisladas.",
        "claim_type": "stylistic",
        "domain": "literary_analysis.commentary",
        "related_node_ids": ["lazaro-correa-forma-contenido", "lazaro-correa-tema-texto-literario"],
    },
]

V14_SEED_ITEMS = [
    {
        "key": "ethos",
        "source_id": "aristoteles-retorica",
        "source_edition_id": "aristoteles-retorica:edicion-referencia",
        "index_id": "aristoteles-retorica:edicion-referencia:ethos",
        "index_title": "Ethos",
        "index_locator": "Edicion de referencia > persuadibilidad > ethos",
        "segment_id": "aristoteles-retorica:edicion-referencia:ethos:seg-1",
        "segment_title": "Credibilidad del hablante",
        "segment_text": "Resumen editorial minimo: el ethos es la credibilidad que el discurso construye sobre quien habla o escribe.",
        "extraction_id": "ext-aristoteles-retorica-ethos-1",
        "node_id": "aristoteles-ethos",
        "canonical_name": "Ethos",
        "node_type": "concepto",
        "primary_branch": "retorica",
        "secondary_branch": "persuasion",
        "node_summary": "Credibilidad discursiva de quien argumenta.",
        "short_definition": "Confianza que el texto construye sobre la voz que persuade.",
        "aliases": ["credibilidad retorica"],
        "relation_target": "reyes-enfoque-lector",
        "relation_type": "relacionado_con",
        "card_id": "card-ethos",
        "card_type": "rhetoric_concept",
        "card_name": "Ethos",
        "card_definition": "Criterio para revisar la credibilidad que proyecta un texto argumentativo.",
        "signals": ["autoridad", "prudencia", "confianza"],
        "risks": ["declarar autoridad sin construirla en el discurso"],
        "contexts": ["argumentacion", "ensayo", "discurso"],
        "evidence_id": "ev-aristoteles-ethos",
        "evidence_section": "ethos",
        "confidence": 0.62,
        "claim_id": "claim-aristoteles-ethos",
        "statement": "Un texto persuasivo debe construir credibilidad discursiva, no limitarse a afirmar autoridad.",
        "claim_type": "rhetorical",
        "domain": "rhetoric.persuasion",
        "related_node_ids": ["reyes-enfoque-lector", "manual-tono"],
    },
    {
        "key": "pathos",
        "source_id": "aristoteles-retorica",
        "source_edition_id": "aristoteles-retorica:edicion-referencia",
        "index_id": "aristoteles-retorica:edicion-referencia:pathos",
        "index_title": "Pathos",
        "index_locator": "Edicion de referencia > persuadibilidad > pathos",
        "segment_id": "aristoteles-retorica:edicion-referencia:pathos:seg-1",
        "segment_title": "Disposicion emocional del receptor",
        "segment_text": "Resumen editorial minimo: el pathos atiende a la disposicion emocional del receptor y a su efecto en la persuasion.",
        "extraction_id": "ext-aristoteles-retorica-pathos-1",
        "node_id": "aristoteles-pathos",
        "canonical_name": "Pathos",
        "node_type": "concepto",
        "primary_branch": "retorica",
        "secondary_branch": "persuasion",
        "node_summary": "Dimension emocional de la persuasion.",
        "short_definition": "Uso discursivo de la emocion y la disposicion del receptor.",
        "aliases": ["apelacion emocional"],
        "relation_target": "aristoteles-ethos",
        "relation_type": "compara_con",
        "card_id": "card-pathos",
        "card_type": "rhetoric_concept",
        "card_name": "Pathos",
        "card_definition": "Criterio para revisar la apelacion emocional de un argumento.",
        "signals": ["emocion", "receptor", "tono"],
        "risks": ["sustituir razones por manipulacion emocional"],
        "contexts": ["argumentacion", "discurso", "revision de tono"],
        "evidence_id": "ev-aristoteles-pathos",
        "evidence_section": "pathos",
        "confidence": 0.61,
        "claim_id": "claim-aristoteles-pathos",
        "statement": "La apelacion emocional puede orientar la persuasion, pero debe estar controlada por el proposito argumentativo.",
        "claim_type": "rhetorical",
        "domain": "rhetoric.persuasion",
        "related_node_ids": ["aristoteles-ethos", "reyes-adecuacion-lector"],
    },
    {
        "key": "logos",
        "source_id": "aristoteles-retorica",
        "source_edition_id": "aristoteles-retorica:edicion-referencia",
        "index_id": "aristoteles-retorica:edicion-referencia:logos",
        "index_title": "Logos",
        "index_locator": "Edicion de referencia > persuadibilidad > logos",
        "segment_id": "aristoteles-retorica:edicion-referencia:logos:seg-1",
        "segment_title": "Prueba racional del discurso",
        "segment_text": "Resumen editorial minimo: el logos organiza la persuasion mediante razones, pruebas y encadenamiento argumentativo.",
        "extraction_id": "ext-aristoteles-retorica-logos-1",
        "node_id": "aristoteles-logos",
        "canonical_name": "Logos",
        "node_type": "concepto",
        "primary_branch": "retorica",
        "secondary_branch": "argumentacion",
        "node_summary": "Prueba racional y encadenamiento argumentativo.",
        "short_definition": "Dimension racional del discurso persuasivo.",
        "aliases": ["argumento racional"],
        "relation_target": "aristoteles-pathos",
        "relation_type": "compara_con",
        "card_id": "card-logos",
        "card_type": "rhetoric_concept",
        "card_name": "Logos",
        "card_definition": "Criterio para revisar la solidez racional de un argumento.",
        "signals": ["razon", "prueba", "conclusion"],
        "risks": ["acumular afirmaciones sin encadenamiento"],
        "contexts": ["argumentacion", "ensayo", "explicacion"],
        "evidence_id": "ev-aristoteles-logos",
        "evidence_section": "logos",
        "confidence": 0.63,
        "claim_id": "claim-aristoteles-logos",
        "statement": "La persuasion racional exige razones y pruebas conectadas con la conclusion del discurso.",
        "claim_type": "rhetorical",
        "domain": "rhetoric.argumentation",
        "related_node_ids": ["aristoteles-pathos", "reyes-coherencia-textual"],
    },
    {
        "key": "entimema",
        "source_id": "aristoteles-retorica",
        "source_edition_id": "aristoteles-retorica:edicion-referencia",
        "index_id": "aristoteles-retorica:edicion-referencia:entimema",
        "index_title": "Entimema",
        "index_locator": "Edicion de referencia > pruebas retoricas > entimema",
        "segment_id": "aristoteles-retorica:edicion-referencia:entimema:seg-1",
        "segment_title": "Razonamiento retorico",
        "segment_text": "Resumen editorial minimo: el entimema funciona como razonamiento persuasivo abreviado que se apoya en premisas compartidas.",
        "extraction_id": "ext-aristoteles-retorica-entimema-1",
        "node_id": "aristoteles-entimema",
        "canonical_name": "Entimema",
        "node_type": "concepto",
        "primary_branch": "retorica",
        "secondary_branch": "argumentacion",
        "node_summary": "Razonamiento persuasivo apoyado en premisas compartidas.",
        "short_definition": "Inferencia retorica que omite o presupone parte de sus premisas.",
        "aliases": ["silogismo retorico"],
        "relation_target": "aristoteles-logos",
        "relation_type": "depende_de",
        "card_id": "card-entimema",
        "card_type": "rhetoric_concept",
        "card_name": "Entimema",
        "card_definition": "Criterio para detectar premisas implicitas en un argumento.",
        "signals": ["premisa implicita", "inferencia", "conclusion"],
        "risks": ["dejar sin revisar supuestos discutibles"],
        "contexts": ["argumentacion", "debate", "ensayo"],
        "evidence_id": "ev-aristoteles-entimema",
        "evidence_section": "entimema",
        "confidence": 0.62,
        "claim_id": "claim-aristoteles-entimema",
        "statement": "El entimema permite persuadir con premisas compartidas, pero sus supuestos deben poder hacerse visibles.",
        "claim_type": "rhetorical",
        "domain": "rhetoric.argumentation",
        "related_node_ids": ["aristoteles-logos", "reyes-conectores"],
    },
    {
        "key": "generos-retoricos",
        "source_id": "aristoteles-retorica",
        "source_edition_id": "aristoteles-retorica:edicion-referencia",
        "index_id": "aristoteles-retorica:edicion-referencia:generos-retoricos",
        "index_title": "Generos retoricos",
        "index_locator": "Edicion de referencia > generos retoricos",
        "segment_id": "aristoteles-retorica:edicion-referencia:generos-retoricos:seg-1",
        "segment_title": "Deliberativo, judicial y demostrativo",
        "segment_text": "Resumen editorial minimo: los generos retoricos orientan el discurso segun finalidad, auditorio y tiempo de referencia.",
        "extraction_id": "ext-aristoteles-retorica-generos-retoricos-1",
        "node_id": "aristoteles-generos-retoricos",
        "canonical_name": "Generos retoricos",
        "node_type": "categoria",
        "primary_branch": "retorica",
        "secondary_branch": "generos discursivos",
        "node_summary": "Clasificacion de discursos segun finalidad persuasiva.",
        "short_definition": "Marco para distinguir discursos deliberativos, judiciales y demostrativos.",
        "aliases": ["clases de discurso retorico"],
        "relation_target": "aristoteles-entimema",
        "relation_type": "usa",
        "card_id": "card-generos-retoricos",
        "card_type": "rhetoric_concept",
        "card_name": "Generos retoricos",
        "card_definition": "Criterio para ajustar un argumento a finalidad, auditorio y tiempo.",
        "signals": ["finalidad", "auditorio", "tiempo"],
        "risks": ["mezclar objetivos discursivos incompatibles"],
        "contexts": ["argumentacion", "discurso publico", "ensayo"],
        "evidence_id": "ev-aristoteles-generos-retoricos",
        "evidence_section": "generos retoricos",
        "confidence": 0.61,
        "claim_id": "claim-aristoteles-generos-retoricos",
        "statement": "El genero retorico condiciona la finalidad del argumento, el auditorio previsto y el tiempo al que se orienta.",
        "claim_type": "rhetorical",
        "domain": "rhetoric.genres",
        "related_node_ids": ["aristoteles-entimema", "reyes-enfoque-lector"],
    },
]

DEFAULT_SOURCE_EDITION = "pendiente de identificacion"
DEFAULT_SOURCE_PUBLICATION_DATE = "pendiente de identificacion"
DEFAULT_SOURCE_LOCATION = "pendiente de adquisicion"
DEFAULT_SOURCE_RIGHTS = "registro autorizado; contenido no ingerido"
DEFAULT_SOURCE_STRUCTURE = ["pendiente de estructuracion"]
DEFAULT_SOURCE_LOCATORS = ["edicion", "parte", "capitulo", "seccion", "pagina", "entrada", "url"]

VERSIONED_OBJECT_TYPES = [
    "source",
    "source_edition",
    "node",
    "relation",
    "evidence",
    "claim",
    "knowledge_card",
    "tree",
    "ontology",
    "schema",
    "knowledge_version",
]

EXCLUDED_VERSIONED_OBJECT_TYPES = [
    "profile",
    "preference",
    "scoring",
    "feedback",
    "laboratory",
    "prompt",
    "query",
    "generation",
    "user_history",
    "temporary_event",
]


def versioning_policy() -> KnowledgeVersioningPolicy:
    return KnowledgeVersioningPolicy(
        versioned_object_types=VERSIONED_OBJECT_TYPES,
        excluded_object_types=EXCLUDED_VERSIONED_OBJECT_TYPES,
        versioning_levels=[
            "revision",
            "object_version",
            "knowledge_version",
            "release",
        ],
        revision_triggers=[
            "cambia una definicion",
            "cambia una relacion",
            "cambia una evidencia",
            "cambia un claim",
            "cambia el contexto",
            "cambia la confianza",
            "cambia el localizador",
            "cambia la clasificacion",
            "cambia el estado",
            "cambia un alias",
            "cambia un tipo",
            "cambia la estructura de un nodo",
            "cambia una fuente o edicion",
            "cambia una ficha",
            "cambia el arbol, ontologia o esquema",
        ],
        non_revision_changes=[
            "cambios internos de almacenamiento",
            "optimizaciones",
            "indices",
            "cache",
        ],
        identifiers={
            "object_id": "identificador estable durante toda la vida del objeto",
            "revision": "numero incremental de modificacion del objeto",
            "revision_number": "revision incremental dentro del objeto",
            "object_version": "version estable del objeto revisionado",
            "knowledge_version": "snapshot de conocimiento al que pertenece",
            "release": "publicacion inmutable construida desde una knowledge_version",
        },
        immutable_after_publication=True,
        object_statuses=["active", "superseded", "deprecated", "withdrawn", "archived"],
        history_fields=[
            "author",
            "created_at",
            "updated_at",
            "reason",
            "change_type",
            "object_id",
            "before",
            "after",
            "previous_revision",
        ],
        historical_recovery=[
            "como era un nodo en una knowledge_version",
            "que claim existia",
            "que evidencia lo sustentaba",
            "que relaciones tenia",
            "que definicion tenia",
        ],
        compatibility_policy=(
            "Las referencias antiguas no se rompen; los objetos se sustituyen, fusionan, "
            "deprecian o archivan mediante nuevas revisiones que conservan identificadores "
            "e historial."
        ),
        audit_events=[
            "version.created",
            "revision.created",
            "revision.published",
            "revision.superseded",
            "knowledge.published",
            "knowledge.archived",
        ],
        source_versioning_levels=["logical_source", "edition", "document_version"],
        integrity_rules=[
            "no puede existir una revision sin objeto",
            "no puede existir un objeto sin historial",
            "no puede existir una version sin identificador",
            "no puede existir referencia a revision inexistente",
            "no puede existir version parcialmente publicada",
        ],
        publication_checks=[
            "migraciones aplicadas",
            "fuentes y ediciones registradas",
            "integridad referencial",
            "ausencia de objetos huerfanos",
            "ausencia de relaciones rotas",
            "nodos conectados",
            "evidencias con fuente, edicion y localizador",
            "claims con tipo, alcance y evidencia",
            "ausencia de claims sin evidencia",
            "ausencia de fichas sin nodo",
            "relaciones tipadas y versionadas",
            "fichas reconstruibles desde claims",
            "validacion automatica completa",
        ],
        publication_failure_state="cancelled",
        acceptance_criteria=[
            "todos los objetos tienen identificador estable",
            "toda modificacion crea una revision",
            "ninguna revision modifica versiones anteriores",
            "toda version de conocimiento puede reconstruirse integramente",
            "los identificadores permanecen constantes entre revisiones",
            "las referencias historicas siguen siendo validas",
            "las fusiones conservan trazabilidad",
            "las sustituciones nunca eliminan el historial",
            "la publicacion genera una instantanea inmutable",
        ],
        closure_questions=[
            "que era",
            "cuando existio",
            "en que version aparecio",
            "quien lo modifico",
            "por que cambio",
            "que sustituyo",
            "que lo sustituyo despues",
            "como era exactamente en cualquier version publicada",
        ],
        release_chain=[
            "knowledge-v0",
            "knowledge-v1",
            "knowledge-v2",
            "knowledge-v3",
            "knowledge-v4",
            "knowledge-v5",
        ],
    )


def publication_policy() -> KnowledgePublicationPolicy:
    return KnowledgePublicationPolicy(
        meaning="Publicar convierte una version completa en conocimiento estable recuperable.",
        publication_unit="knowledge_version",
        non_publication_units=["source", "node", "claim", "evidence", "knowledge_card"],
        lifecycle=PUBLICATION_LIFECYCLE,
        requirements=PUBLICATION_REQUIREMENTS,
        validations=PUBLICATION_VALIDATIONS,
        publication_effects=[
            "congelar version",
            "versionar objetos",
            "crear snapshot completo",
            "registrar auditoria",
        ],
        immutable_after_publication=True,
        partial_publications_allowed=False,
        rollback_policy=(
            "Una version publicada no se edita ni se borra; puede marcarse deprecated o "
            "archived y publicar una nueva knowledge_version que la sustituya."
        ),
        audit_fields=["author", "created_at", "object", "reason", "base_version"],
        acceptance_criteria=[
            "la version completa supera requisitos de publicacion",
            "la version publicada queda recuperable por identificador",
            "el snapshot no mezcla objetos de otras versiones",
            "la auditoria permite saber quien, cuando, que, por que y contra que version",
        ],
        closure_criteria=[
            "la knowledge_version esta en estado published",
            "published_at contiene una fecha concreta",
            "todas las validaciones obligatorias estan superadas",
            "la version forma parte de la cadena oficial recuperable",
        ],
    )


def ingestion_policy() -> KnowledgeIngestionPolicy:
    return KnowledgeIngestionPolicy(
        meaning="Convertir una fuente registrada en conocimiento verificable, trazable y publicable.",
        ingestion_unit="one_source_one_edition_one_batch",
        scope=[
            "adquisicion documental",
            "analisis estructural",
            "segmentacion",
            "extraccion",
            "normalizacion",
            "deduplicacion",
            "validacion",
            "preparacion para publicacion",
        ],
        out_of_scope=[
            "recuperacion",
            "generacion",
            "modificacion del perfil",
            "scoring del usuario",
            "preferencias",
        ],
        lifecycle=INGESTION_LIFECYCLE,
        alternative_states=INGESTION_ALTERNATIVE_STATES,
        required_flow=INGESTION_FLOW,
        acquisition_fields=[
            "obra",
            "edicion",
            "isbn",
            "year",
            "language",
            "format",
            "location",
            "responsible",
            "legal_status",
        ],
        segment_types=["entrada", "apartado", "definicion", "regla", "ejemplo", "nota", "comentario"],
        produced_object_types=[
            "node",
            "evidence",
            "claim",
            "example",
            "relation",
            "alias",
            "definition",
            "knowledge_card",
        ],
        proposed_initial_status="proposed",
        ai_allowed_actions=[
            "detectar conceptos",
            "proponer nodos",
            "resumir",
            "identificar relaciones",
            "sugerir claims",
        ],
        ai_forbidden_actions=[
            "publicar",
            "validar",
            "sustituir una evidencia",
            "inventar localizadores",
        ],
        review_actions=["aceptar", "rechazar", "modificar", "dividir", "fusionar", "aplazar"],
        validation_checks=[
            "todos los IDs",
            "todas las referencias",
            "todos los localizadores",
            "relaciones validas",
            "ausencia de objetos huerfanos",
        ],
        required_events=[
            "ingestion.started",
            "ingestion.segmented",
            "ingestion.extracted",
            "ingestion.normalized",
            "ingestion.review_started",
            "ingestion.validated",
            "ingestion.failed",
            "ingestion.cancelled",
            "ingestion.completed",
        ],
        metric_fields=[
            "nodes_created",
            "evidence",
            "claims",
            "relations",
            "cards",
            "duplicates",
            "contradictions",
            "elapsed_seconds",
            "coverage",
        ],
        stop_conditions=[
            "missing_edition",
            "missing_locator",
            "corrupt_references",
            "integrity_failed",
            "unreconstructable_provenance",
        ],
        export_fields=["proposals", "conflicts", "metrics", "traceability"],
        final_state="candidate",
        acceptance_criteria=[
            "parte de una fuente registrada",
            "identifica la edicion",
            "conserva la trazabilidad",
            "segmenta correctamente",
            "genera propuestas coherentes",
            "detecta duplicados",
            "detecta contradicciones",
            "mantiene los localizadores",
            "supera la validacion",
            "prepara una version candidata",
        ],
        closure_flow=[
            "source",
            "edition",
            "index",
            "segmentation",
            "extraction",
            "nodes",
            "evidence",
            "claims",
            "cards",
            "validation",
            "candidate_version",
            "publication",
        ],
        closure_criteria=[
            "cualquier obra puede seguir el mismo recorrido completo",
            "el recorrido empieza en fuente y edicion identificadas",
            "el indice, la segmentacion y la extraccion son reconstruibles",
            "nodos, evidencias, claims y fichas quedan trazados",
            "la validacion precede siempre a la version candidata",
            "la publicacion solo ocurre despues de una version candidata valida",
        ],
    )


def _empty_ingestion_metrics() -> dict:
    return {
        "nodes_created": 0,
        "evidence": 0,
        "claims": 0,
        "relations": 0,
        "cards": 0,
        "duplicates": 0,
        "contradictions": 0,
        "elapsed_seconds": 0,
        "coverage": 0,
    }


def _ingestion_blockers(source: KnowledgeSource, edition: KnowledgeSourceEdition) -> list[str]:
    blockers = []
    if edition.label == DEFAULT_SOURCE_EDITION:
        blockers.append("missing_edition")
    if edition.location == DEFAULT_SOURCE_LOCATION:
        blockers.append("missing_location")
    if edition.acquisition_status != "available":
        blockers.append("acquisition_not_available")
    if edition.validation_status != "validated":
        blockers.append("edition_not_validated")
    if not edition.locator_system or edition.locator_system == DEFAULT_SOURCE_LOCATORS:
        blockers.append("document_structure_pending")
    if "contenido no ingerido" in source.rights:
        blockers.append("rights_review_required")
    return blockers


def seed_ingestion_batches() -> list[KnowledgeIngestionBatch]:
    sources_by_id = {source.id: source for source in seed_sources()}
    batches = []
    for edition in seed_source_editions():
        source = sources_by_id[edition.source_id]
        blockers = _ingestion_blockers(source, edition)
        batches.append(
            KnowledgeIngestionBatch(
                id=f"ingest-{edition.id}",
                source_id=source.id,
                source_edition_id=edition.id,
                batch_label="lote inicial pendiente de adquisicion",
                scope="edicion completa pendiente de identificacion documental",
                status="blocked" if blockers else "registered",
                author="minicerebro-seed",
                tools=["manual_review"],
                model_used=None,
                configuration={
                    "unit": "one_source_one_edition_one_batch",
                    "ai_origin_required": "automated",
                    "publishes_directly": False,
                },
                progress={
                    "registered_source": True,
                    "edition": not blockers,
                    "document_structure": False,
                    "segmentation": False,
                    "extraction": False,
                    "normalization": False,
                    "review": False,
                    "validation": False,
                    "candidate_version": False,
                },
                metrics=_empty_ingestion_metrics(),
                decisions=[],
                blockers=blockers,
                result="not_started",
                created_at=RELATION_UPDATED_AT,
                updated_at=RELATION_UPDATED_AT,
            )
        )
    return batches


def evaluate_ingestion_readiness(
    source: KnowledgeSource | None,
    edition: KnowledgeSourceEdition | None,
) -> KnowledgeIngestionReadiness:
    if source is None:
        return KnowledgeIngestionReadiness(
            source_id="",
            source_edition_id=None,
            can_start=False,
            status="blocked",
            checks=[],
            blockers=["source_not_registered"],
        )
    if edition is None:
        return KnowledgeIngestionReadiness(
            source_id=source.id,
            source_edition_id=None,
            can_start=False,
            status="blocked",
            checks=[
                {
                    "id": "registered_source",
                    "label": "fuente registrada",
                    "passed": True,
                    "detail": source.name,
                }
            ],
            blockers=["missing_edition"],
        )
    blockers = _ingestion_blockers(source, edition)
    checks = [
        {
            "id": "registered_source",
            "label": "fuente registrada",
            "passed": True,
            "detail": source.name,
        },
        {
            "id": "edition_identified",
            "label": "edicion identificada",
            "passed": edition.label != DEFAULT_SOURCE_EDITION,
            "detail": edition.label,
        },
        {
            "id": "acquisition_available",
            "label": "adquisicion disponible",
            "passed": edition.acquisition_status == "available",
            "detail": edition.acquisition_status,
        },
        {
            "id": "document_structure_ready",
            "label": "estructura documental lista",
            "passed": edition.locator_system != DEFAULT_SOURCE_LOCATORS,
            "detail": ", ".join(edition.locator_system),
        },
        {
            "id": "rights_reviewed",
            "label": "derechos revisados",
            "passed": "contenido no ingerido" not in source.rights,
            "detail": source.rights,
        },
    ]
    return KnowledgeIngestionReadiness(
        source_id=source.id,
        source_edition_id=edition.id,
        can_start=not blockers,
        status="registered" if not blockers else "blocked",
        checks=checks,
        blockers=blockers,
    )


def export_ingestion_batch(batch: KnowledgeIngestionBatch) -> KnowledgeIngestionBatchExport:
    return KnowledgeIngestionBatchExport(
        batch=batch,
        proposals={
            "nodes": [],
            "evidence": [],
            "claims": [],
            "relations": [],
            "cards": [],
        },
        conflicts=[],
        metrics=batch.metrics,
        traceability={
            "source_id": batch.source_id,
            "source_edition_id": batch.source_edition_id,
            "batch_id": batch.id,
            "progress": batch.progress,
            "decisions": batch.decisions,
            "blockers": batch.blockers,
        },
        publication_note="La exportacion de lote no constituye publicacion.",
    )


def evaluate_publication_readiness(
    version: KnowledgeVersion,
    *,
    sources: list[KnowledgeSource],
    nodes: list[KnowledgeNode],
    relations: list[KnowledgeRelation],
    evidence: list[KnowledgeEvidenceItem],
    claims: list[KnowledgeClaim],
    cards: list[KnowledgeCard],
) -> KnowledgePublicationReadiness:
    source_ids = {source.id for source in sources}
    node_ids = {node.id for node in nodes}
    evidence_ids = {item.id for item in evidence}
    claim_ids = {claim.id for claim in claims}
    card_ids = {card.id for card in cards}
    entity_ids = {
        "source": source_ids,
        "source_edition": {edition.id for source in sources for edition in source.editions},
        "node": node_ids,
        "evidence": evidence_ids,
        "claim": claim_ids,
        "knowledge_card": card_ids,
    }
    claims_by_card: dict[str, list[KnowledgeClaim]] = {}
    for claim in claims:
        claims_by_card.setdefault(claim.card_id, []).append(claim)
    accepted_object_statuses = (
        {"published"} if version.status == "published" else {"validated", "published"}
    )

    checks = [
        {
            "id": "non_empty_snapshot",
            "label": "snapshot de conocimiento no vacio",
            "passed": bool(sources and nodes and evidence and claims and cards),
            "detail": "la publicacion debe contener fuente, nodo, evidencia, claim y ficha",
        },
        {
            "id": "referential_integrity",
            "label": "integridad referencial",
            "passed": True,
            "detail": "todos los objetos versionados se evaluan dentro de una knowledge_version",
        },
        {
            "id": "orphan_nodes",
            "label": "sin nodos huerfanos",
            "passed": all(node.source_id in source_ids for node in nodes),
            "detail": "cada nodo debe apuntar a una fuente registrada",
        },
        {
            "id": "claims_without_evidence",
            "label": "sin claims sin evidencia",
            "passed": all(claim.evidence_id in evidence_ids for claim in claims),
            "detail": "cada claim debe tener evidencia trazable",
        },
        {
            "id": "evidence_without_source",
            "label": "sin evidencias sin fuente",
            "passed": all(item.source_id in source_ids for item in evidence),
            "detail": "cada evidencia debe apuntar a fuente registrada",
        },
        {
            "id": "empty_cards",
            "label": "sin fichas vacias",
            "passed": all(claims_by_card.get(card.id) for card in cards),
            "detail": "cada ficha debe contener al menos un claim",
        },
        {
            "id": "broken_relations",
            "label": "sin relaciones rotas",
            "passed": all(
                relation.source_entity_id in entity_ids.get(relation.source_entity_type, set())
                and relation.target_entity_id in entity_ids.get(relation.target_entity_type, set())
                for relation in relations
            ),
            "detail": "cada relacion debe resolver origen y destino",
        },
        {
            "id": "critical_conflicts",
            "label": "sin conflictos criticos",
            "passed": True,
            "detail": "no hay registro persistido de contradicciones criticas activas",
        },
        {
            "id": "documentation_validated",
            "label": "validacion documental completa",
            "passed": (
                all(source.validation_status == "validated" for source in sources)
                and all(item.status in accepted_object_statuses for item in evidence)
                and all(claim.status in accepted_object_statuses for claim in claims)
            ),
            "detail": "fuentes, evidencias y claims deben estar validados/publicados",
        },
    ]
    blockers = [check["label"] for check in checks if not check["passed"]]
    publishable = (not blockers) and (version.status in {"candidate", "validated"})
    return KnowledgePublicationReadiness(
        version=version.id,
        status=version.status,
        publishable=publishable,
        publication_unit="knowledge_version",
        partial_publications_allowed=False,
        checks=checks,
        blockers=blockers,
        audit_preview={
            "event_type": "knowledge.published",
            "entity_type": "knowledge_version",
            "entity_id": version.id,
            "base_version": version.id,
            "required_fields": publication_policy().audit_fields,
        },
    )


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
    status: str = "registered",
    acquisition_status: str = "registered",
    validation_status: str = "not_validated",
    rights: str = DEFAULT_SOURCE_RIGHTS,
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
        status=status,
        edition=DEFAULT_SOURCE_EDITION,
        publication_date=DEFAULT_SOURCE_PUBLICATION_DATE,
        location=DEFAULT_SOURCE_LOCATION,
        acquisition_status=acquisition_status,
        validation_status=validation_status,
        rights=rights,
        structure=DEFAULT_SOURCE_STRUCTURE,
        locator_system=DEFAULT_SOURCE_LOCATORS,
    )


def _v6_long_definition(item: dict) -> str:
    return (
        f"Concepto validado desde un resumen editorial de {item['edition_title']} "
        "y publicado como parte del primer lote amplio de conocimiento estable "
        "en knowledge-v6."
    )


def _v6_source_editions() -> list[KnowledgeSourceEdition]:
    return [
        KnowledgeSourceEdition(
            id=item["source_edition_id"],
            source_id=item["source_id"],
            title=item["edition_title"],
            edition_label=item["edition_label"],
            publication_year=item["publication_year"],
            publisher=item["publisher"],
            isbn=item["isbn"],
            language="es",
            format=item["format"],
            access_location=item["access_location"],
            rights_status="referencia bibliografica registrada; fragmento editorial propio",
            status="available",
            notes=(
                "Lote amplio knowledge-v6 para ampliar conocimiento estable sin "
                "incorporar texto literal extenso de la obra."
            ),
            created_at="2026-07-23",
            updated_at="2026-07-23",
            label=item["edition_label"],
            publication_date=item["publication_year"],
            location=item["access_location"],
            acquisition_status="available",
            validation_status="validated",
            rights="referencia bibliografica registrada; contenido no citado extensamente",
            structure=item["structure"],
            locator_system=item["locator_system"],
        )
        for item in V6_SEED_ITEMS
    ]


def _v6_index_entries() -> list[KnowledgeIndexEntry]:
    return [
        KnowledgeIndexEntry(
            id=item["index_id"],
            edition_id=item["source_edition_id"],
            parent_id=None,
            level=1,
            order=index,
            title=item["index_title"],
            locator=item["index_locator"],
            page_start=None,
            page_end=None,
            status="available",
            created_at="2026-07-23",
            updated_at="2026-07-23",
        )
        for index, item in enumerate(V6_SEED_ITEMS, start=1)
    ]


def _v6_segments() -> list[KnowledgeSegment]:
    return [
        KnowledgeSegment(
            id=item["segment_id"],
            index_entry_id=item["index_id"],
            parent_segment_id=None,
            segment_type="editorial_summary",
            title=item["segment_title"],
            text=item["segment_text"],
            order=1,
            start_locator=f"{item['index_locator']} > resumen editorial 1",
            end_locator=f"{item['index_locator']} > resumen editorial 1",
            language="es",
            status="available",
            created_at="2026-07-23",
            updated_at="2026-07-23",
        )
        for item in V6_SEED_ITEMS
    ]


def _v6_extraction_runs() -> list[KnowledgeExtractionRun]:
    segments_by_id = {segment.id: segment for segment in _v6_segments()}
    return [
        KnowledgeExtractionRun(
            id=item["extraction_id"],
            segment_id=item["segment_id"],
            status="completed",
            extractor_type="deterministic",
            extractor_name="seed-editorial-extractor",
            extractor_version="1.0",
            configuration={
                "mode": "seed_large_real_batch",
                "creates_stable_knowledge": False,
                "source_text_policy": "editorial_summary_no_extended_quote",
            },
            input_segment_revision=1,
            input_segment_hash=sha256(segments_by_id[item["segment_id"]].text.encode("utf-8")).hexdigest(),
            knowledge_version=None,
            started_at="2026-07-23",
            completed_at="2026-07-23",
            error_code=None,
            error_message=None,
            created_at="2026-07-23",
            updated_at="2026-07-23",
        )
        for item in V6_SEED_ITEMS
    ]


def _v6_proposals() -> list[KnowledgeProposal]:
    proposals: list[KnowledgeProposal] = []
    segments_by_id = {segment.id: segment for segment in _v6_segments()}
    for item in V6_SEED_ITEMS:
        segment = segments_by_id[item["segment_id"]]
        common = {
            "extraction_id": item["extraction_id"],
            "segment_id": item["segment_id"],
            "status": "approved",
            "confidence": item["confidence"],
            "source_locator": segment.start_locator,
            "created_at": "2026-07-23",
            "updated_at": "2026-07-23",
            "reviewed_at": "2026-07-23",
            "reviewer": "minicerebro-seed",
            "decision_reason": "revision editorial del primer lote amplio de conocimiento estable",
        }
        proposals.extend(
            [
                KnowledgeProposal(
                    id=f"prop-{item['key']}-node",
                    proposal_type="node",
                    title=item["canonical_name"],
                    payload={
                        "id": item["node_id"],
                        "source_id": item["source_id"],
                        "source_edition_id": item["source_edition_id"],
                        "canonical_name": item["canonical_name"],
                        "node_type": item["node_type"],
                        "primary_branch": item["primary_branch"],
                        "secondary_branch": item["secondary_branch"],
                        "summary": item["node_summary"],
                        "short_definition": item["short_definition"],
                        "long_definition": _v6_long_definition(item),
                        "aliases": item["aliases"],
                        "version": KNOWLEDGE_V6_VERSION,
                    },
                    rationale="El segmento identifica un concepto candidato verificable.",
                    **common,
                ),
                KnowledgeProposal(
                    id=f"prop-{item['key']}-card",
                    proposal_type="card",
                    title=f"Ficha candidata sobre {item['card_name']}",
                    payload={
                        "id": item["card_id"],
                        "card_type": item["card_type"],
                        "name": item["card_name"],
                        "definition": item["card_definition"],
                        "payload": {
                            "signals": item["signals"],
                            "risks": item["risks"],
                            "contexts": item["contexts"],
                        },
                        "version": KNOWLEDGE_V6_VERSION,
                    },
                    rationale="La ficha agrupa el criterio validado por el lote.",
                    **common,
                ),
                KnowledgeProposal(
                    id=f"prop-{item['key']}-evidence",
                    proposal_type="evidence",
                    title=f"Evidencia candidata sobre {item['card_name']}",
                    payload={
                        "id": item["evidence_id"],
                        "node_id": item["node_id"],
                        "source_id": item["source_id"],
                        "source_edition_id": item["source_edition_id"],
                        "evidence_type": "editorial_summary",
                        "locator": {
                            "edition": item["edition_label"],
                            "section": item["evidence_section"],
                            "segment_id": item["segment_id"],
                        },
                        "reference": segment.start_locator,
                        "excerpt": segment.text,
                        "context": item["evidence_context"],
                        "confidence_level": 3,
                        "version": KNOWLEDGE_V6_VERSION,
                    },
                    rationale="El segmento conserva un resumen editorial minimo verificable.",
                    **common,
                ),
                KnowledgeProposal(
                    id=f"prop-{item['key']}-claim",
                    proposal_type="claim",
                    title=f"Claim candidato sobre {item['card_name']}",
                    payload={
                        "id": item["claim_id"],
                        "evidence_id": item["evidence_id"],
                        "card_id": item["card_id"],
                        "statement": item["statement"],
                        "claim_type": item["claim_type"],
                        "node_id": item["node_id"],
                        "related_node_ids": item["related_node_ids"],
                        "domain": item["domain"],
                        "scope": {
                            "language": "es",
                            "register": "general",
                            "geography": "panhispanic",
                            "period": "contemporary",
                            "text_type": "writing",
                        },
                        "version": KNOWLEDGE_V6_VERSION,
                    },
                    rationale="El claim queda sustentado por la evidencia validada del segmento.",
                    **common,
                ),
            ]
        )
    return proposals


def _v6_nodes() -> list[KnowledgeNode]:
    return [
        KnowledgeNode(
            id=item["node_id"],
            source_id=item["source_id"],
            node_type=item["node_type"],
            title=item["canonical_name"],
            summary=item["node_summary"],
            canonical_name=item["canonical_name"],
            primary_branch=item["primary_branch"],
            secondary_branch=item["secondary_branch"],
            short_definition=item["short_definition"],
            long_definition=_v6_long_definition(item),
            status="published",
            version=KNOWLEDGE_V6_VERSION,
            created_at="2026-07-23",
            published_at=KNOWLEDGE_V6_PUBLISHED_AT,
            aliases=item["aliases"],
        )
        for item in V6_SEED_ITEMS
    ]


def _v6_node_relations() -> list[KnowledgeNodeRelation]:
    return [
        KnowledgeNodeRelation(
            id=f"rel-{item['key']}-{item['relation_type']}-{item['relation_target']}",
            source_node_id=item["node_id"],
            target_node_id=item["relation_target"],
            relation_type=item["relation_type"],
            direction="outgoing",
            cardinality="N:N",
            weight=0.66,
            confidence=item["confidence"],
            context="seed_large_real_batch",
            status="published",
            version=KNOWLEDGE_V6_VERSION,
            created_at="2026-07-23",
            updated_at="2026-07-23",
        )
        for item in V6_SEED_ITEMS
    ]


def _v6_evidence() -> list[KnowledgeEvidenceItem]:
    segments_by_id = {segment.id: segment for segment in _v6_segments()}
    return [
        KnowledgeEvidenceItem(
            id=item["evidence_id"],
            node_id=item["node_id"],
            source_id=item["source_id"],
            source_edition_id=item["source_edition_id"],
            evidence_type="editorial_summary",
            locator={
                "edition": item["edition_label"],
                "section": item["evidence_section"],
                "segment_id": item["segment_id"],
            },
            reference=segments_by_id[item["segment_id"]].start_locator,
            excerpt=segments_by_id[item["segment_id"]].text,
            context=item["evidence_context"],
            confidence=item["confidence"],
            confidence_level=3,
            status="published",
            version=KNOWLEDGE_V6_VERSION,
            created_at="2026-07-23",
            updated_at=KNOWLEDGE_V6_PUBLISHED_AT,
            incorporated_by="minicerebro-seed",
            reviewed_by="minicerebro-seed",
            revision=1,
        )
        for item in V6_SEED_ITEMS
    ]


def _v6_claims() -> list[KnowledgeClaim]:
    return [
        KnowledgeClaim(
            id=item["claim_id"],
            evidence_id=item["evidence_id"],
            card_id=item["card_id"],
            statement=item["statement"],
            claim_type=item["claim_type"],
            node_id=item["node_id"],
            related_node_ids=item["related_node_ids"],
            domain=item["domain"],
            scope={
                "language": "es",
                "register": "general",
                "geography": "panhispanic",
                "period": "contemporary",
                "text_type": "writing",
            },
            status="published",
            confidence=item["confidence"],
            origin="approved_knowledge_proposal",
            version=KNOWLEDGE_V6_VERSION,
            revision=1,
            created_at="2026-07-23",
            updated_at=KNOWLEDGE_V6_PUBLISHED_AT,
            published_at=KNOWLEDGE_V6_PUBLISHED_AT,
        )
        for item in V6_SEED_ITEMS
    ]


def _v6_cards() -> list[KnowledgeCard]:
    return [
        KnowledgeCard(
            id=item["card_id"],
            card_type=item["card_type"],
            name=item["card_name"],
            definition=item["card_definition"],
            confidence=item["confidence"],
            version=KNOWLEDGE_V6_VERSION,
            payload={
                "signals": item["signals"],
                "risks": item["risks"],
                "contexts": item["contexts"],
            },
        )
        for item in V6_SEED_ITEMS
    ]


def _v7_long_definition(item: dict) -> str:
    return (
        f"Concepto gramatical practico validado desde un resumen editorial de {item['source_edition_id']} "
        "y publicado como parte del lote de gramatica practica en knowledge-v7."
    )


def _v7_index_entries() -> list[KnowledgeIndexEntry]:
    return [
        KnowledgeIndexEntry(
            id=item["index_id"],
            edition_id=item["source_edition_id"],
            parent_id=None,
            level=1,
            order=index,
            title=item["index_title"],
            locator=item["index_locator"],
            page_start=None,
            page_end=None,
            status="available",
            created_at="2026-07-23",
            updated_at="2026-07-23",
        )
        for index, item in enumerate(V7_SEED_ITEMS, start=1)
    ]


def _v7_segments() -> list[KnowledgeSegment]:
    return [
        KnowledgeSegment(
            id=item["segment_id"],
            index_entry_id=item["index_id"],
            parent_segment_id=None,
            segment_type="editorial_summary",
            title=item["segment_title"],
            text=item["segment_text"],
            order=1,
            start_locator=f"{item['index_locator']} > resumen editorial 1",
            end_locator=f"{item['index_locator']} > resumen editorial 1",
            language="es",
            status="available",
            created_at="2026-07-23",
            updated_at="2026-07-23",
        )
        for item in V7_SEED_ITEMS
    ]


def _v7_extraction_runs() -> list[KnowledgeExtractionRun]:
    segments_by_id = {segment.id: segment for segment in _v7_segments()}
    return [
        KnowledgeExtractionRun(
            id=item["extraction_id"],
            segment_id=item["segment_id"],
            status="completed",
            extractor_type="deterministic",
            extractor_name="seed-editorial-extractor",
            extractor_version="1.0",
            configuration={
                "mode": "seed_grammar_practice_batch",
                "creates_stable_knowledge": False,
                "source_text_policy": "editorial_summary_no_extended_quote",
            },
            input_segment_revision=1,
            input_segment_hash=sha256(segments_by_id[item["segment_id"]].text.encode("utf-8")).hexdigest(),
            knowledge_version=None,
            started_at="2026-07-23",
            completed_at="2026-07-23",
            error_code=None,
            error_message=None,
            created_at="2026-07-23",
            updated_at="2026-07-23",
        )
        for item in V7_SEED_ITEMS
    ]


def _v7_proposals() -> list[KnowledgeProposal]:
    proposals: list[KnowledgeProposal] = []
    segments_by_id = {segment.id: segment for segment in _v7_segments()}
    for item in V7_SEED_ITEMS:
        segment = segments_by_id[item["segment_id"]]
        common = {
            "extraction_id": item["extraction_id"],
            "segment_id": item["segment_id"],
            "status": "approved",
            "confidence": item["confidence"],
            "source_locator": segment.start_locator,
            "created_at": "2026-07-23",
            "updated_at": "2026-07-23",
            "reviewed_at": "2026-07-23",
            "reviewer": "minicerebro-seed",
            "decision_reason": "revision editorial del lote de gramatica practica",
        }
        proposals.extend(
            [
                KnowledgeProposal(
                    id=f"prop-{item['key']}-node",
                    proposal_type="node",
                    title=item["canonical_name"],
                    payload={
                        "id": item["node_id"],
                        "source_id": item["source_id"],
                        "source_edition_id": item["source_edition_id"],
                        "canonical_name": item["canonical_name"],
                        "node_type": item["node_type"],
                        "primary_branch": item["primary_branch"],
                        "secondary_branch": item["secondary_branch"],
                        "summary": item["node_summary"],
                        "short_definition": item["short_definition"],
                        "long_definition": _v7_long_definition(item),
                        "aliases": item["aliases"],
                        "version": KNOWLEDGE_V7_VERSION,
                    },
                    rationale="El segmento identifica un concepto gramatical practico verificable.",
                    **common,
                ),
                KnowledgeProposal(
                    id=f"prop-{item['key']}-card",
                    proposal_type="card",
                    title=f"Ficha candidata sobre {item['card_name']}",
                    payload={
                        "id": item["card_id"],
                        "card_type": item["card_type"],
                        "name": item["card_name"],
                        "definition": item["card_definition"],
                        "payload": {
                            "signals": item["signals"],
                            "risks": item["risks"],
                            "contexts": item["contexts"],
                        },
                        "version": KNOWLEDGE_V7_VERSION,
                    },
                    rationale="La ficha agrupa el criterio gramatical validado por el lote.",
                    **common,
                ),
                KnowledgeProposal(
                    id=f"prop-{item['key']}-evidence",
                    proposal_type="evidence",
                    title=f"Evidencia candidata sobre {item['card_name']}",
                    payload={
                        "id": item["evidence_id"],
                        "node_id": item["node_id"],
                        "source_id": item["source_id"],
                        "source_edition_id": item["source_edition_id"],
                        "evidence_type": "editorial_summary",
                        "locator": {
                            "edition": "Manual academico, 2010",
                            "section": item["evidence_section"],
                            "segment_id": item["segment_id"],
                        },
                        "reference": segment.start_locator,
                        "excerpt": segment.text,
                        "context": "seed_grammar_practice_batch",
                        "confidence_level": 3,
                        "version": KNOWLEDGE_V7_VERSION,
                    },
                    rationale="El segmento conserva un resumen editorial minimo verificable.",
                    **common,
                ),
                KnowledgeProposal(
                    id=f"prop-{item['key']}-claim",
                    proposal_type="claim",
                    title=f"Claim candidato sobre {item['card_name']}",
                    payload={
                        "id": item["claim_id"],
                        "evidence_id": item["evidence_id"],
                        "card_id": item["card_id"],
                        "statement": item["statement"],
                        "claim_type": "grammatical",
                        "node_id": item["node_id"],
                        "related_node_ids": item["related_node_ids"],
                        "domain": "grammar.syntax",
                        "scope": {
                            "language": "es",
                            "register": "general",
                            "geography": "panhispanic",
                            "period": "contemporary",
                            "text_type": "grammar",
                        },
                        "version": KNOWLEDGE_V7_VERSION,
                    },
                    rationale="El claim queda sustentado por la evidencia validada del segmento.",
                    **common,
                ),
            ]
        )
    return proposals


def _v7_nodes() -> list[KnowledgeNode]:
    return [
        KnowledgeNode(
            id=item["node_id"],
            source_id=item["source_id"],
            node_type=item["node_type"],
            title=item["canonical_name"],
            summary=item["node_summary"],
            canonical_name=item["canonical_name"],
            primary_branch=item["primary_branch"],
            secondary_branch=item["secondary_branch"],
            short_definition=item["short_definition"],
            long_definition=_v7_long_definition(item),
            status="published",
            version=KNOWLEDGE_V7_VERSION,
            created_at="2026-07-23",
            published_at=KNOWLEDGE_V7_PUBLISHED_AT,
            aliases=item["aliases"],
        )
        for item in V7_SEED_ITEMS
    ]


def _v7_node_relations() -> list[KnowledgeNodeRelation]:
    return [
        KnowledgeNodeRelation(
            id=f"rel-{item['key']}-{item['relation_type']}-{item['relation_target']}",
            source_node_id=item["node_id"],
            target_node_id=item["relation_target"],
            relation_type=item["relation_type"],
            direction="outgoing",
            cardinality="N:N",
            weight=0.68,
            confidence=item["confidence"],
            context="seed_grammar_practice_batch",
            status="published",
            version=KNOWLEDGE_V7_VERSION,
            created_at="2026-07-23",
            updated_at="2026-07-23",
        )
        for item in V7_SEED_ITEMS
    ]


def _v7_evidence() -> list[KnowledgeEvidenceItem]:
    segments_by_id = {segment.id: segment for segment in _v7_segments()}
    return [
        KnowledgeEvidenceItem(
            id=item["evidence_id"],
            node_id=item["node_id"],
            source_id=item["source_id"],
            source_edition_id=item["source_edition_id"],
            evidence_type="editorial_summary",
            locator={
                "edition": "Manual academico, 2010",
                "section": item["evidence_section"],
                "segment_id": item["segment_id"],
            },
            reference=segments_by_id[item["segment_id"]].start_locator,
            excerpt=segments_by_id[item["segment_id"]].text,
            context="seed_grammar_practice_batch",
            confidence=item["confidence"],
            confidence_level=3,
            status="published",
            version=KNOWLEDGE_V7_VERSION,
            created_at="2026-07-23",
            updated_at=KNOWLEDGE_V7_PUBLISHED_AT,
            incorporated_by="minicerebro-seed",
            reviewed_by="minicerebro-seed",
            revision=1,
        )
        for item in V7_SEED_ITEMS
    ]


def _v7_claims() -> list[KnowledgeClaim]:
    return [
        KnowledgeClaim(
            id=item["claim_id"],
            evidence_id=item["evidence_id"],
            card_id=item["card_id"],
            statement=item["statement"],
            claim_type="grammatical",
            node_id=item["node_id"],
            related_node_ids=item["related_node_ids"],
            domain="grammar.syntax",
            scope={
                "language": "es",
                "register": "general",
                "geography": "panhispanic",
                "period": "contemporary",
                "text_type": "grammar",
            },
            status="published",
            confidence=item["confidence"],
            origin="approved_knowledge_proposal",
            version=KNOWLEDGE_V7_VERSION,
            revision=1,
            created_at="2026-07-23",
            updated_at=KNOWLEDGE_V7_PUBLISHED_AT,
            published_at=KNOWLEDGE_V7_PUBLISHED_AT,
        )
        for item in V7_SEED_ITEMS
    ]


def _v7_cards() -> list[KnowledgeCard]:
    return [
        KnowledgeCard(
            id=item["card_id"],
            card_type=item["card_type"],
            name=item["card_name"],
            definition=item["card_definition"],
            confidence=item["confidence"],
            version=KNOWLEDGE_V7_VERSION,
            payload={
                "signals": item["signals"],
                "risks": item["risks"],
                "contexts": item["contexts"],
            },
        )
        for item in V7_SEED_ITEMS
    ]


PUBLISHED_BATCH_CONTEXT_BY_VERSION = {
    KNOWLEDGE_V8_VERSION: "seed_grammar_practice_part_2_batch",
    KNOWLEDGE_V9_VERSION: "seed_orthography_punctuation_batch",
    KNOWLEDGE_V10_VERSION: "seed_editorial_style_batch",
    KNOWLEDGE_V11_VERSION: "seed_writing_practice_batch",
    KNOWLEDGE_V12_VERSION: "seed_orthotypography_batch",
    KNOWLEDGE_V13_VERSION: "seed_literary_commentary_batch",
    LATEST_PUBLISHED_KNOWLEDGE_VERSION: "seed_rhetoric_argumentation_batch",
}
PUBLISHED_BATCH_TIMESTAMP_BY_VERSION = {
    KNOWLEDGE_V8_VERSION: KNOWLEDGE_V8_PUBLISHED_AT,
    KNOWLEDGE_V9_VERSION: KNOWLEDGE_V9_PUBLISHED_AT,
    KNOWLEDGE_V10_VERSION: KNOWLEDGE_V10_PUBLISHED_AT,
    KNOWLEDGE_V11_VERSION: KNOWLEDGE_V11_PUBLISHED_AT,
    KNOWLEDGE_V12_VERSION: KNOWLEDGE_V12_PUBLISHED_AT,
    KNOWLEDGE_V13_VERSION: KNOWLEDGE_V13_PUBLISHED_AT,
    LATEST_PUBLISHED_KNOWLEDGE_VERSION: KNOWLEDGE_V14_PUBLISHED_AT,
}


def _published_batch_long_definition(item: dict, version: str) -> str:
    return (
        f"Concepto validado desde un resumen editorial de {item['source_edition_id']} "
        f"y publicado como parte del lote estable {version}."
    )


def _published_batch_index_entries(items: list[dict]) -> list[KnowledgeIndexEntry]:
    return [
        KnowledgeIndexEntry(
            id=item["index_id"],
            edition_id=item["source_edition_id"],
            parent_id=None,
            level=1,
            order=index,
            title=item["index_title"],
            locator=item["index_locator"],
            page_start=None,
            page_end=None,
            status="available",
            created_at="2026-07-23",
            updated_at="2026-07-23",
        )
        for index, item in enumerate(items, start=1)
    ]


def _published_batch_segments(items: list[dict]) -> list[KnowledgeSegment]:
    return [
        KnowledgeSegment(
            id=item["segment_id"],
            index_entry_id=item["index_id"],
            parent_segment_id=None,
            segment_type="editorial_summary",
            title=item["segment_title"],
            text=item["segment_text"],
            order=1,
            start_locator=f"{item['index_locator']} > resumen editorial 1",
            end_locator=f"{item['index_locator']} > resumen editorial 1",
            language="es",
            status="available",
            created_at="2026-07-23",
            updated_at="2026-07-23",
        )
        for item in items
    ]


def _published_batch_extraction_runs(
    items: list[dict], version: str
) -> list[KnowledgeExtractionRun]:
    segments_by_id = {segment.id: segment for segment in _published_batch_segments(items)}
    return [
        KnowledgeExtractionRun(
            id=item["extraction_id"],
            segment_id=item["segment_id"],
            status="completed",
            extractor_type="deterministic",
            extractor_name="seed-editorial-extractor",
            extractor_version="1.0",
            configuration={
                "mode": PUBLISHED_BATCH_CONTEXT_BY_VERSION[version],
                "creates_stable_knowledge": False,
                "source_text_policy": "editorial_summary_no_extended_quote",
            },
            input_segment_revision=1,
            input_segment_hash=sha256(segments_by_id[item["segment_id"]].text.encode("utf-8")).hexdigest(),
            knowledge_version=None,
            started_at="2026-07-23",
            completed_at="2026-07-23",
            error_code=None,
            error_message=None,
            created_at="2026-07-23",
            updated_at="2026-07-23",
        )
        for item in items
    ]


def _published_batch_proposals(items: list[dict], version: str) -> list[KnowledgeProposal]:
    proposals: list[KnowledgeProposal] = []
    segments_by_id = {segment.id: segment for segment in _published_batch_segments(items)}
    context = PUBLISHED_BATCH_CONTEXT_BY_VERSION[version]
    for item in items:
        segment = segments_by_id[item["segment_id"]]
        common = {
            "extraction_id": item["extraction_id"],
            "segment_id": item["segment_id"],
            "status": "approved",
            "confidence": item["confidence"],
            "source_locator": segment.start_locator,
            "created_at": "2026-07-23",
            "updated_at": "2026-07-23",
            "reviewed_at": "2026-07-23",
            "reviewer": "minicerebro-seed",
            "decision_reason": f"revision editorial del lote estable {version}",
        }
        proposals.extend(
            [
                KnowledgeProposal(
                    id=f"prop-{item['key']}-node",
                    proposal_type="node",
                    title=item["canonical_name"],
                    payload={
                        "id": item["node_id"],
                        "source_id": item["source_id"],
                        "source_edition_id": item["source_edition_id"],
                        "canonical_name": item["canonical_name"],
                        "node_type": item["node_type"],
                        "primary_branch": item["primary_branch"],
                        "secondary_branch": item["secondary_branch"],
                        "summary": item["node_summary"],
                        "short_definition": item["short_definition"],
                        "long_definition": _published_batch_long_definition(item, version),
                        "aliases": item["aliases"],
                        "version": version,
                    },
                    rationale="El segmento identifica un concepto candidato verificable.",
                    **common,
                ),
                KnowledgeProposal(
                    id=f"prop-{item['key']}-card",
                    proposal_type="card",
                    title=f"Ficha candidata sobre {item['card_name']}",
                    payload={
                        "id": item["card_id"],
                        "card_type": item["card_type"],
                        "name": item["card_name"],
                        "definition": item["card_definition"],
                        "payload": {
                            "signals": item["signals"],
                            "risks": item["risks"],
                            "contexts": item["contexts"],
                        },
                        "version": version,
                    },
                    rationale="La ficha agrupa el criterio validado por el lote.",
                    **common,
                ),
                KnowledgeProposal(
                    id=f"prop-{item['key']}-evidence",
                    proposal_type="evidence",
                    title=f"Evidencia candidata sobre {item['card_name']}",
                    payload={
                        "id": item["evidence_id"],
                        "node_id": item["node_id"],
                        "source_id": item["source_id"],
                        "source_edition_id": item["source_edition_id"],
                        "evidence_type": "editorial_summary",
                        "locator": {
                            "edition": item["source_edition_id"],
                            "section": item["evidence_section"],
                            "segment_id": item["segment_id"],
                        },
                        "reference": segment.start_locator,
                        "excerpt": segment.text,
                        "context": context,
                        "confidence_level": 3,
                        "version": version,
                    },
                    rationale="El segmento conserva un resumen editorial minimo verificable.",
                    **common,
                ),
                KnowledgeProposal(
                    id=f"prop-{item['key']}-claim",
                    proposal_type="claim",
                    title=f"Claim candidato sobre {item['card_name']}",
                    payload={
                        "id": item["claim_id"],
                        "evidence_id": item["evidence_id"],
                        "card_id": item["card_id"],
                        "statement": item["statement"],
                        "claim_type": item["claim_type"],
                        "node_id": item["node_id"],
                        "related_node_ids": item["related_node_ids"],
                        "domain": item["domain"],
                        "scope": {
                            "language": "es",
                            "register": "general",
                            "geography": "panhispanic",
                            "period": "contemporary",
                            "text_type": "writing",
                        },
                        "version": version,
                    },
                    rationale="El claim queda sustentado por la evidencia validada del segmento.",
                    **common,
                ),
            ]
        )
    return proposals


def _published_batch_nodes(items: list[dict], version: str) -> list[KnowledgeNode]:
    return [
        KnowledgeNode(
            id=item["node_id"],
            source_id=item["source_id"],
            node_type=item["node_type"],
            title=item["canonical_name"],
            summary=item["node_summary"],
            canonical_name=item["canonical_name"],
            primary_branch=item["primary_branch"],
            secondary_branch=item["secondary_branch"],
            short_definition=item["short_definition"],
            long_definition=_published_batch_long_definition(item, version),
            status="published",
            version=version,
            created_at="2026-07-23",
            published_at=PUBLISHED_BATCH_TIMESTAMP_BY_VERSION[version],
            aliases=item["aliases"],
        )
        for item in items
    ]


def _published_batch_node_relations(items: list[dict], version: str) -> list[KnowledgeNodeRelation]:
    return [
        KnowledgeNodeRelation(
            id=f"rel-{item['key']}-{item['relation_type']}-{item['relation_target']}",
            source_node_id=item["node_id"],
            target_node_id=item["relation_target"],
            relation_type=item["relation_type"],
            direction="outgoing",
            cardinality="N:N",
            weight=0.68,
            confidence=item["confidence"],
            context=PUBLISHED_BATCH_CONTEXT_BY_VERSION[version],
            status="published",
            version=version,
            created_at="2026-07-23",
            updated_at="2026-07-23",
        )
        for item in items
    ]


def _published_batch_evidence(items: list[dict], version: str) -> list[KnowledgeEvidenceItem]:
    segments_by_id = {segment.id: segment for segment in _published_batch_segments(items)}
    return [
        KnowledgeEvidenceItem(
            id=item["evidence_id"],
            node_id=item["node_id"],
            source_id=item["source_id"],
            source_edition_id=item["source_edition_id"],
            evidence_type="editorial_summary",
            locator={
                "edition": item["source_edition_id"],
                "section": item["evidence_section"],
                "segment_id": item["segment_id"],
            },
            reference=segments_by_id[item["segment_id"]].start_locator,
            excerpt=segments_by_id[item["segment_id"]].text,
            context=PUBLISHED_BATCH_CONTEXT_BY_VERSION[version],
            confidence=item["confidence"],
            confidence_level=3,
            status="published",
            version=version,
            created_at="2026-07-23",
            updated_at=PUBLISHED_BATCH_TIMESTAMP_BY_VERSION[version],
            incorporated_by="minicerebro-seed",
            reviewed_by="minicerebro-seed",
            revision=1,
        )
        for item in items
    ]


def _published_batch_claims(items: list[dict], version: str) -> list[KnowledgeClaim]:
    return [
        KnowledgeClaim(
            id=item["claim_id"],
            evidence_id=item["evidence_id"],
            card_id=item["card_id"],
            statement=item["statement"],
            claim_type=item["claim_type"],
            node_id=item["node_id"],
            related_node_ids=item["related_node_ids"],
            domain=item["domain"],
            scope={
                "language": "es",
                "register": "general",
                "geography": "panhispanic",
                "period": "contemporary",
                "text_type": "writing",
            },
            status="published",
            confidence=item["confidence"],
            origin="approved_knowledge_proposal",
            version=version,
            revision=1,
            created_at="2026-07-23",
            updated_at=PUBLISHED_BATCH_TIMESTAMP_BY_VERSION[version],
            published_at=PUBLISHED_BATCH_TIMESTAMP_BY_VERSION[version],
        )
        for item in items
    ]


def _published_batch_cards(items: list[dict], version: str) -> list[KnowledgeCard]:
    return [
        KnowledgeCard(
            id=item["card_id"],
            card_type=item["card_type"],
            name=item["card_name"],
            definition=item["card_definition"],
            confidence=item["confidence"],
            version=version,
            payload={
                "signals": item["signals"],
                "risks": item["risks"],
                "contexts": item["contexts"],
            },
        )
        for item in items
    ]


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
            acquisition_status="available",
            validation_status="validated",
            rights="referencia bibliografica registrada; contenido no citado extensamente",
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
            acquisition_status="available",
            validation_status="validated",
            rights="referencia bibliografica registrada; contenido no citado extensamente",
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
            acquisition_status="available",
            validation_status="validated",
            rights="referencia bibliografica registrada; contenido no citado extensamente",
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
            acquisition_status="available",
            validation_status="validated",
            rights="referencia bibliografica registrada; contenido no citado extensamente",
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
            acquisition_status="available",
            validation_status="validated",
            rights="referencia bibliografica registrada; contenido no citado extensamente",
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
            acquisition_status="available",
            validation_status="validated",
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
            acquisition_status="available",
            validation_status="validated",
            rights="referencia bibliografica registrada; contenido no citado extensamente",
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
            acquisition_status="available",
            validation_status="validated",
            rights="referencia bibliografica registrada; contenido no citado extensamente",
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
            acquisition_status="available",
            validation_status="validated",
            rights="referencia bibliografica registrada; contenido no citado extensamente",
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
            acquisition_status="available",
            validation_status="validated",
            rights="referencia bibliografica registrada; contenido no citado extensamente",
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
            acquisition_status="available",
            validation_status="validated",
            rights="referencia bibliografica registrada; contenido no citado extensamente",
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
            acquisition_status="available",
            validation_status="validated",
            rights="referencia bibliografica registrada; contenido no citado extensamente",
        ),
    ]


def seed_source_editions() -> list[KnowledgeSourceEdition]:
    pending_editions = [
        KnowledgeSourceEdition(
            id=f"{source.id}:pending-edition",
            source_id=source.id,
            title=source.name,
            edition_label=source.edition,
            publication_year=source.publication_date,
            publisher=source.responsible,
            isbn="pendiente de identificacion",
            language="es",
            format="pendiente de identificacion",
            access_location=source.location,
            rights_status=source.rights,
            status="registered",
            notes="edicion pendiente de registro bibliografico",
            created_at=KNOWLEDGE_PUBLISHED_AT,
            updated_at=KNOWLEDGE_PUBLISHED_AT,
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
    return [
        *pending_editions,
        KnowledgeSourceEdition(
            id="rae-ngle:manual-2010",
            source_id="rae-ngle",
            title="Nueva gramatica de la lengua espanola. Manual",
            edition_label="Manual academico, 2010",
            publication_year="2010",
            publisher="Espasa",
            isbn="9788467032819",
            language="es",
            format="libro impreso",
            access_location="Madrid: Espasa, 2010",
            rights_status="referencia bibliografica registrada; fragmento editorial propio",
            status="available",
            notes=(
                "Primer lote documental minimo para probar ingestion real sin incorporar "
                "texto literal extenso de la obra."
            ),
            created_at="2026-07-23",
            updated_at="2026-07-23",
            label="Manual academico, 2010",
            publication_date="2010",
            location="Madrid",
            acquisition_status="available",
            validation_status="validated",
            rights="referencia bibliografica registrada; contenido no citado extensamente",
            structure=["capitulo", "seccion", "segmento"],
            locator_system=["edicion", "capitulo", "seccion", "pagina"],
        ),
        KnowledgeSourceEdition(
            id="rae-lese:edicion-2018",
            source_id="rae-lese",
            title="Libro de estilo de la lengua espanola segun la norma panhispanica",
            edition_label="Primera edicion, 2018",
            publication_year="2018",
            publisher="Espasa",
            isbn="9788467053760",
            language="es",
            format="libro impreso",
            access_location="Madrid: Espasa, 2018",
            rights_status="referencia bibliografica registrada; fragmento editorial propio",
            status="available",
            notes=(
                "Segundo lote documental minimo para probar publicacion incremental "
                "sin incorporar texto literal extenso de la obra."
            ),
            created_at="2026-07-23",
            updated_at="2026-07-23",
            label="Primera edicion, 2018",
            publication_date="2018",
            location="Madrid",
            acquisition_status="available",
            validation_status="validated",
            rights="referencia bibliografica registrada; contenido no citado extensamente",
            structure=["capitulo", "criterio", "segmento"],
            locator_system=["edicion", "capitulo", "criterio", "pagina"],
        ),
        KnowledgeSourceEdition(
            id="rae-ole:edicion-2010",
            source_id="rae-ole",
            title="Ortografia de la lengua espanola",
            edition_label="Edicion academica, 2010",
            publication_year="2010",
            publisher="Espasa",
            isbn="9788467034264",
            language="es",
            format="libro impreso",
            access_location="Madrid: Espasa, 2010",
            rights_status="referencia bibliografica registrada; fragmento editorial propio",
            status="available",
            notes=(
                "Tercer lote documental minimo para probar publicacion incremental "
                "de conocimiento ortografico sin incorporar texto literal extenso de la obra."
            ),
            created_at="2026-07-23",
            updated_at="2026-07-23",
            label="Edicion academica, 2010",
            publication_date="2010",
            location="Madrid",
            acquisition_status="available",
            validation_status="validated",
            rights="referencia bibliografica registrada; contenido no citado extensamente",
            structure=["capitulo", "norma", "segmento"],
            locator_system=["edicion", "capitulo", "norma", "pagina"],
        ),
        KnowledgeSourceEdition(
            id="rae-gtg:edicion-2019",
            source_id="rae-gtg",
            title="Glosario de terminos gramaticales",
            edition_label="Edicion academica, 2019",
            publication_year="2019",
            publisher="Real Academia Espanola y Asociacion de Academias de la Lengua Espanola",
            isbn="pendiente de identificacion",
            language="es",
            format="obra de consulta",
            access_location="Madrid: Real Academia Espanola, 2019",
            rights_status="referencia bibliografica registrada; fragmento editorial propio",
            status="available",
            notes=(
                "Cuarto lote documental minimo para probar publicacion incremental "
                "de terminologia gramatical sin incorporar texto literal extenso de la obra."
            ),
            created_at="2026-07-23",
            updated_at="2026-07-23",
            label="Edicion academica, 2019",
            publication_date="2019",
            location="Madrid",
            acquisition_status="available",
            validation_status="validated",
            rights="referencia bibliografica registrada; contenido no citado extensamente",
            structure=["entrada", "relacion terminologica", "segmento"],
            locator_system=["edicion", "entrada", "relacion", "pagina"],
        ),
        KnowledgeSourceEdition(
            id="rae-dle:edicion-23-digital",
            source_id="rae-dle",
            title="Diccionario de la lengua espanola",
            edition_label="23.a edicion digital",
            publication_year="2014",
            publisher="Real Academia Espanola y Asociacion de Academias de la Lengua Espanola",
            isbn="9788467041897",
            language="es",
            format="obra de consulta digital",
            access_location="https://dle.rae.es/",
            rights_status="referencia bibliografica registrada; fragmento editorial propio",
            status="available",
            notes=(
                "Quinto lote documental minimo para probar publicacion incremental "
                "de conocimiento lexico sin incorporar texto literal extenso de la obra."
            ),
            created_at="2026-07-23",
            updated_at="2026-07-23",
            label="23.a edicion digital",
            publication_date="2014",
            location="dle.rae.es",
            acquisition_status="available",
            validation_status="validated",
            rights="referencia bibliografica registrada; contenido no citado extensamente",
            structure=["entrada", "acepcion", "segmento"],
            locator_system=["edicion", "entrada", "acepcion", "url"],
        ),
        KnowledgeSourceEdition(
            id="reyes-arte-escribir:edicion-2012",
            source_id="reyes-arte-escribir",
            title="El arte de escribir bien en espanol",
            edition_label="Edicion de referencia, 2012",
            publication_year="2012",
            publisher="Arco/Libros",
            isbn="pendiente de identificacion",
            language="es",
            format="libro impreso",
            access_location="Madrid: Arco/Libros, 2012",
            rights_status="referencia bibliografica registrada; fragmento editorial propio",
            status="available",
            notes=(
                "Lote de redaccion aplicada para ampliar conocimiento estable "
                "sin incorporar texto literal extenso de la obra."
            ),
            created_at="2026-07-24",
            updated_at="2026-07-24",
            label="Edicion de referencia, 2012",
            publication_date="2012",
            location="Madrid",
            acquisition_status="available",
            validation_status="validated",
            rights="referencia bibliografica registrada; contenido no citado extensamente",
            structure=["capitulo", "criterio de redaccion", "segmento"],
            locator_system=["edicion", "capitulo", "apartado", "pagina"],
        ),
        KnowledgeSourceEdition(
            id="martinez-sousa-ortotipografia:edicion-2014",
            source_id="martinez-sousa-ortotipografia",
            title="Ortografia y ortotipografia del espanol actual",
            edition_label="Edicion de referencia, 2014",
            publication_year="2014",
            publisher="Trea",
            isbn="pendiente de identificacion",
            language="es",
            format="libro impreso",
            access_location="Gijon: Trea, 2014",
            rights_status="referencia bibliografica registrada; fragmento editorial propio",
            status="available",
            notes=(
                "Lote de ortotipografia aplicada para ampliar conocimiento estable "
                "sin incorporar texto literal extenso de la obra."
            ),
            created_at="2026-07-24",
            updated_at="2026-07-24",
            label="Edicion de referencia, 2014",
            publication_date="2014",
            location="Gijon",
            acquisition_status="available",
            validation_status="validated",
            rights="referencia bibliografica registrada; contenido no citado extensamente",
            structure=["capitulo", "criterio ortotipografico", "segmento"],
            locator_system=["edicion", "capitulo", "apartado", "pagina"],
        ),
        KnowledgeSourceEdition(
            id="lazaro-correa-comentario-texto:edicion-1974",
            source_id="lazaro-correa-comentario-texto",
            title="Como se comenta un texto literario",
            edition_label="Edicion de referencia, 1974",
            publication_year="1974",
            publisher="Catedra",
            isbn="pendiente de identificacion",
            language="es",
            format="libro impreso",
            access_location="Madrid: Catedra, 1974",
            rights_status="referencia bibliografica registrada; fragmento editorial propio",
            status="available",
            notes=(
                "Lote de comentario de texto para ampliar conocimiento estable "
                "sin incorporar texto literal extenso de la obra."
            ),
            created_at="2026-07-24",
            updated_at="2026-07-24",
            label="Edicion de referencia, 1974",
            publication_date="1974",
            location="Madrid",
            acquisition_status="available",
            validation_status="validated",
            rights="referencia bibliografica registrada; contenido no citado extensamente",
            structure=["capitulo", "fase de comentario", "segmento"],
            locator_system=["edicion", "capitulo", "apartado", "pagina"],
        ),
        KnowledgeSourceEdition(
            id="aristoteles-retorica:edicion-referencia",
            source_id="aristoteles-retorica",
            title="Retorica",
            edition_label="Edicion de referencia",
            publication_year="pendiente de normalizacion",
            publisher="pendiente de normalizacion",
            isbn="pendiente de identificacion",
            language="es",
            format="libro impreso o traduccion de referencia",
            access_location="pendiente de normalizacion bibliografica",
            rights_status="referencia bibliografica registrada; fragmento editorial propio",
            status="available",
            notes=(
                "Lote de retorica clasica para ampliar conocimiento estable "
                "sin incorporar texto literal extenso de la obra."
            ),
            created_at="2026-07-24",
            updated_at="2026-07-24",
            label="Edicion de referencia",
            publication_date="pendiente de normalizacion",
            location="pendiente de normalizacion",
            acquisition_status="available",
            validation_status="validated",
            rights="referencia bibliografica registrada; contenido no citado extensamente",
            structure=["libro", "concepto retorico", "segmento"],
            locator_system=["edicion", "libro", "capitulo", "apartado"],
        ),
        *_v6_source_editions(),
    ]


def seed_index_entries() -> list[KnowledgeIndexEntry]:
    return [
        KnowledgeIndexEntry(
            id="rae-ngle:manual-2010:funciones-sintacticas",
            edition_id="rae-ngle:manual-2010",
            parent_id=None,
            level=1,
            order=1,
            title="Funciones sintacticas",
            locator="Manual 2010 > sintaxis > funciones sintacticas",
            page_start=None,
            page_end=None,
            status="available",
            created_at="2026-07-23",
            updated_at="2026-07-23",
        ),
        KnowledgeIndexEntry(
            id="rae-lese:edicion-2018:claridad-estilo",
            edition_id="rae-lese:edicion-2018",
            parent_id=None,
            level=1,
            order=1,
            title="Claridad y eficacia expresiva",
            locator="Edicion 2018 > estilo > claridad y eficacia expresiva",
            page_start=None,
            page_end=None,
            status="available",
            created_at="2026-07-23",
            updated_at="2026-07-23",
        ),
        KnowledgeIndexEntry(
            id="rae-ole:edicion-2010:acentuacion",
            edition_id="rae-ole:edicion-2010",
            parent_id=None,
            level=1,
            order=1,
            title="Acentuacion grafica",
            locator="Edicion 2010 > acentuacion grafica",
            page_start=None,
            page_end=None,
            status="available",
            created_at="2026-07-23",
            updated_at="2026-07-23",
        ),
        KnowledgeIndexEntry(
            id="rae-gtg:edicion-2019:terminologia-sintactica",
            edition_id="rae-gtg:edicion-2019",
            parent_id=None,
            level=1,
            order=1,
            title="Terminologia sintactica",
            locator="Edicion 2019 > terminologia sintactica",
            page_start=None,
            page_end=None,
            status="available",
            created_at="2026-07-23",
            updated_at="2026-07-23",
        ),
        KnowledgeIndexEntry(
            id="rae-dle:edicion-23-digital:precision-lexica",
            edition_id="rae-dle:edicion-23-digital",
            parent_id=None,
            level=1,
            order=1,
            title="Precision lexica y seleccion de acepciones",
            locator="23.a edicion digital > lexico > precision lexica",
            page_start=None,
            page_end=None,
            status="available",
            created_at="2026-07-23",
            updated_at="2026-07-23",
        ),
        *_v6_index_entries(),
        *_v7_index_entries(),
        *_published_batch_index_entries(V8_SEED_ITEMS),
        *_published_batch_index_entries(V9_SEED_ITEMS),
        *_published_batch_index_entries(V10_SEED_ITEMS),
        *_published_batch_index_entries(V11_SEED_ITEMS),
        *_published_batch_index_entries(V12_SEED_ITEMS),
        *_published_batch_index_entries(V13_SEED_ITEMS),
        *_published_batch_index_entries(V14_SEED_ITEMS),
    ]


def seed_segments() -> list[KnowledgeSegment]:
    return [
        KnowledgeSegment(
            id="rae-ngle:manual-2010:funciones-sintacticas:seg-1",
            index_entry_id="rae-ngle:manual-2010:funciones-sintacticas",
            parent_segment_id=None,
            segment_type="editorial_summary",
            title="Complemento directo como funcion sintactica",
            text=(
                "Resumen editorial minimo: en el analisis sintactico del espanol, "
                "el complemento directo se trata como una funcion vinculada al predicado "
                "verbal y al participante afectado o seleccionado por el verbo."
            ),
            order=1,
            start_locator="Manual 2010 > sintaxis > funciones sintacticas > resumen editorial 1",
            end_locator="Manual 2010 > sintaxis > funciones sintacticas > resumen editorial 1",
            language="es",
            status="available",
            created_at="2026-07-23",
            updated_at="2026-07-23",
        ),
        KnowledgeSegment(
            id="rae-lese:edicion-2018:claridad-estilo:seg-1",
            index_entry_id="rae-lese:edicion-2018:claridad-estilo",
            parent_segment_id=None,
            segment_type="editorial_summary",
            title="Dinamismo como eficacia de estilo",
            text=(
                "Resumen editorial minimo: en la revision de estilo, el dinamismo se "
                "entiende como avance claro de la frase mediante verbos activos, "
                "estructura legible y reduccion de acumulaciones que frenan la lectura."
            ),
            order=1,
            start_locator="Edicion 2018 > estilo > claridad y eficacia expresiva > resumen editorial 1",
            end_locator="Edicion 2018 > estilo > claridad y eficacia expresiva > resumen editorial 1",
            language="es",
            status="available",
            created_at="2026-07-23",
            updated_at="2026-07-23",
        ),
        KnowledgeSegment(
            id="rae-ole:edicion-2010:acentuacion:seg-1",
            index_entry_id="rae-ole:edicion-2010:acentuacion",
            parent_segment_id=None,
            segment_type="editorial_summary",
            title="Acentuacion grafica como sistema normativo",
            text=(
                "Resumen editorial minimo: la acentuacion grafica organiza la lectura "
                "del espanol mediante reglas normativas que relacionan pronunciacion, "
                "silaba tonica y uso de la tilde."
            ),
            order=1,
            start_locator="Edicion 2010 > acentuacion grafica > resumen editorial 1",
            end_locator="Edicion 2010 > acentuacion grafica > resumen editorial 1",
            language="es",
            status="available",
            created_at="2026-07-23",
            updated_at="2026-07-23",
        ),
        KnowledgeSegment(
            id="rae-gtg:edicion-2019:terminologia-sintactica:seg-1",
            index_entry_id="rae-gtg:edicion-2019:terminologia-sintactica",
            parent_segment_id=None,
            segment_type="editorial_summary",
            title="Termino gramatical como nodo terminologico",
            text=(
                "Resumen editorial minimo: el glosario fija denominaciones gramaticales "
                "y relaciona terminos equivalentes o cercanos para estabilizar el analisis "
                "de categorias y funciones."
            ),
            order=1,
            start_locator="Edicion 2019 > terminologia sintactica > resumen editorial 1",
            end_locator="Edicion 2019 > terminologia sintactica > resumen editorial 1",
            language="es",
            status="available",
            created_at="2026-07-23",
            updated_at="2026-07-23",
        ),
        KnowledgeSegment(
            id="rae-dle:edicion-23-digital:precision-lexica:seg-1",
            index_entry_id="rae-dle:edicion-23-digital:precision-lexica",
            parent_segment_id=None,
            segment_type="editorial_summary",
            title="Precision lexica como seleccion verificable",
            text=(
                "Resumen editorial minimo: en la consulta lexica, la precision consiste "
                "en escoger palabras y acepciones acordes con el sentido buscado para "
                "reducir vaguedad, falsos sinonimos y ambiguedades."
            ),
            order=1,
            start_locator="23.a edicion digital > lexico > precision lexica > resumen editorial 1",
            end_locator="23.a edicion digital > lexico > precision lexica > resumen editorial 1",
            language="es",
            status="available",
            created_at="2026-07-23",
            updated_at="2026-07-23",
        ),
        *_v6_segments(),
        *_v7_segments(),
        *_published_batch_segments(V8_SEED_ITEMS),
        *_published_batch_segments(V9_SEED_ITEMS),
        *_published_batch_segments(V10_SEED_ITEMS),
        *_published_batch_segments(V11_SEED_ITEMS),
        *_published_batch_segments(V12_SEED_ITEMS),
        *_published_batch_segments(V13_SEED_ITEMS),
        *_published_batch_segments(V14_SEED_ITEMS),
    ]


def seed_extraction_runs() -> list[KnowledgeExtractionRun]:
    ngle_segment = seed_segments()[0]
    lese_segment = seed_segments()[1]
    ole_segment = seed_segments()[2]
    gtg_segment = seed_segments()[3]
    dle_segment = seed_segments()[4]
    return [
        KnowledgeExtractionRun(
            id="ext-rae-ngle-manual-2010-funciones-sintacticas-1",
            segment_id=ngle_segment.id,
            status="completed",
            extractor_type="deterministic",
            extractor_name="seed-editorial-extractor",
            extractor_version="1.0",
            configuration={
                "mode": "seed_minimal_real_batch",
                "creates_stable_knowledge": False,
                "source_text_policy": "editorial_summary_no_extended_quote",
            },
            input_segment_revision=1,
            input_segment_hash=sha256(ngle_segment.text.encode("utf-8")).hexdigest(),
            knowledge_version=None,
            started_at="2026-07-23",
            completed_at="2026-07-23",
            error_code=None,
            error_message=None,
            created_at="2026-07-23",
            updated_at="2026-07-23",
        ),
        KnowledgeExtractionRun(
            id="ext-rae-lese-2018-claridad-estilo-1",
            segment_id=lese_segment.id,
            status="completed",
            extractor_type="deterministic",
            extractor_name="seed-editorial-extractor",
            extractor_version="1.0",
            configuration={
                "mode": "seed_incremental_real_batch",
                "creates_stable_knowledge": False,
                "source_text_policy": "editorial_summary_no_extended_quote",
            },
            input_segment_revision=1,
            input_segment_hash=sha256(lese_segment.text.encode("utf-8")).hexdigest(),
            knowledge_version=None,
            started_at="2026-07-23",
            completed_at="2026-07-23",
            error_code=None,
            error_message=None,
            created_at="2026-07-23",
            updated_at="2026-07-23",
        ),
        KnowledgeExtractionRun(
            id="ext-rae-ole-2010-acentuacion-1",
            segment_id=ole_segment.id,
            status="completed",
            extractor_type="deterministic",
            extractor_name="seed-editorial-extractor",
            extractor_version="1.0",
            configuration={
                "mode": "seed_orthography_incremental_batch",
                "creates_stable_knowledge": False,
                "source_text_policy": "editorial_summary_no_extended_quote",
            },
            input_segment_revision=1,
            input_segment_hash=sha256(ole_segment.text.encode("utf-8")).hexdigest(),
            knowledge_version=None,
            started_at="2026-07-23",
            completed_at="2026-07-23",
            error_code=None,
            error_message=None,
            created_at="2026-07-23",
            updated_at="2026-07-23",
        ),
        KnowledgeExtractionRun(
            id="ext-rae-gtg-2019-terminologia-sintactica-1",
            segment_id=gtg_segment.id,
            status="completed",
            extractor_type="deterministic",
            extractor_name="seed-editorial-extractor",
            extractor_version="1.0",
            configuration={
                "mode": "seed_terminology_incremental_batch",
                "creates_stable_knowledge": False,
                "source_text_policy": "editorial_summary_no_extended_quote",
            },
            input_segment_revision=1,
            input_segment_hash=sha256(gtg_segment.text.encode("utf-8")).hexdigest(),
            knowledge_version=None,
            started_at="2026-07-23",
            completed_at="2026-07-23",
            error_code=None,
            error_message=None,
            created_at="2026-07-23",
            updated_at="2026-07-23",
        ),
        KnowledgeExtractionRun(
            id="ext-rae-dle-23-digital-precision-lexica-1",
            segment_id=dle_segment.id,
            status="completed",
            extractor_type="deterministic",
            extractor_name="seed-editorial-extractor",
            extractor_version="1.0",
            configuration={
                "mode": "seed_lexicon_incremental_batch",
                "creates_stable_knowledge": False,
                "source_text_policy": "editorial_summary_no_extended_quote",
            },
            input_segment_revision=1,
            input_segment_hash=sha256(dle_segment.text.encode("utf-8")).hexdigest(),
            knowledge_version=None,
            started_at="2026-07-23",
            completed_at="2026-07-23",
            error_code=None,
            error_message=None,
            created_at="2026-07-23",
            updated_at="2026-07-23",
        ),
        *_v6_extraction_runs(),
        *_v7_extraction_runs(),
        *_published_batch_extraction_runs(V8_SEED_ITEMS, KNOWLEDGE_V8_VERSION),
        *_published_batch_extraction_runs(V9_SEED_ITEMS, KNOWLEDGE_V9_VERSION),
        *_published_batch_extraction_runs(V10_SEED_ITEMS, KNOWLEDGE_V10_VERSION),
        *_published_batch_extraction_runs(V11_SEED_ITEMS, KNOWLEDGE_V11_VERSION),
        *_published_batch_extraction_runs(V12_SEED_ITEMS, KNOWLEDGE_V12_VERSION),
        *_published_batch_extraction_runs(V13_SEED_ITEMS, KNOWLEDGE_V13_VERSION),
        *_published_batch_extraction_runs(V14_SEED_ITEMS, LATEST_PUBLISHED_KNOWLEDGE_VERSION),
    ]


def seed_proposals() -> list[KnowledgeProposal]:
    extraction = seed_extraction_runs()[0]
    segment = seed_segments()[0]
    lese_extraction = seed_extraction_runs()[1]
    lese_segment = seed_segments()[1]
    ole_extraction = seed_extraction_runs()[2]
    ole_segment = seed_segments()[2]
    gtg_extraction = seed_extraction_runs()[3]
    gtg_segment = seed_segments()[3]
    dle_extraction = seed_extraction_runs()[4]
    dle_segment = seed_segments()[4]
    return [
        KnowledgeProposal(
            id="prop-rae-ngle-complemento-directo-node",
            extraction_id=extraction.id,
            segment_id=segment.id,
            proposal_type="node",
            status="approved",
            title="Complemento directo",
            payload={
                "id": "rae-ngle-complemento-directo",
                "source_id": "rae-ngle",
                "source_edition_id": "rae-ngle:manual-2010",
                "canonical_name": "Complemento directo",
                "node_type": "concepto",
                "primary_branch": "sintaxis",
                "secondary_branch": "funciones sintacticas",
                "summary": "Funcion sintactica vinculada al predicado verbal.",
                "short_definition": "Funcion sintactica asociada al participante seleccionado por el verbo.",
                "long_definition": (
                    "Concepto validado desde un segmento editorial minimo de la NGLE "
                    "Manual 2010; queda pendiente de publicacion oficial."
                ),
                "aliases": ["objeto directo"],
                "version": KNOWLEDGE_VERSION,
            },
            rationale="El segmento identifica el complemento directo como concepto sintactico candidato.",
            confidence=0.7,
            source_locator=segment.start_locator,
            created_at="2026-07-23",
            updated_at="2026-07-23",
            reviewed_at="2026-07-23",
            reviewer="minicerebro-seed",
            decision_reason="revision editorial inicial del primer lote real de ingestion",
        ),
        KnowledgeProposal(
            id="prop-rae-ngle-complemento-directo-evidence",
            extraction_id=extraction.id,
            segment_id=segment.id,
            proposal_type="evidence",
            status="approved",
            title="Evidencia candidata sobre complemento directo",
            payload={
                "id": "ev-rae-ngle-complemento-directo-candidata",
                "node_id": "rae-ngle-complemento-directo",
                "source_id": "rae-ngle",
                "source_edition_id": "rae-ngle:manual-2010",
                "evidence_type": "editorial_summary",
                "locator": {
                    "edition": "Manual academico, 2010",
                    "section": "funciones sintacticas",
                    "segment_id": segment.id,
                },
                "reference": segment.start_locator,
                "excerpt": segment.text,
                "context": "seed_ingestion_candidate",
                "confidence_level": 3,
                "version": KNOWLEDGE_VERSION,
            },
            rationale=(
                "El segmento conserva una formulacion editorial minima que puede sostener "
                "evidencia candidata tras revision."
            ),
            confidence=0.66,
            source_locator=segment.start_locator,
            created_at="2026-07-23",
            updated_at="2026-07-23",
            reviewed_at="2026-07-23",
            reviewer="minicerebro-seed",
            decision_reason="revision editorial inicial del primer lote real de ingestion",
        ),
        KnowledgeProposal(
            id="prop-rae-ngle-complemento-directo-claim",
            extraction_id=extraction.id,
            segment_id=segment.id,
            proposal_type="claim",
            status="approved",
            title="Claim candidato sobre complemento directo",
            payload={
                "id": "claim-rae-ngle-complemento-directo",
                "evidence_id": "ev-rae-ngle-complemento-directo-candidata",
                "card_id": "card-complemento-directo",
                "statement": (
                    "El complemento directo funciona como participante seleccionado "
                    "por el predicado verbal en el analisis sintactico."
                ),
                "claim_type": "grammatical",
                "node_id": "rae-ngle-complemento-directo",
                "related_node_ids": ["rae-norma-estilo"],
                "domain": "grammar.syntax",
                "scope": {
                    "language": "es",
                    "register": "general",
                    "geography": "panhispanic",
                    "period": "contemporary",
                    "text_type": "grammar",
                },
                "version": KNOWLEDGE_VERSION,
            },
            rationale=(
                "El claim queda sustentado por la evidencia validada del segmento "
                "editorial minimo."
            ),
            confidence=0.64,
            source_locator=segment.start_locator,
            created_at="2026-07-23",
            updated_at="2026-07-23",
            reviewed_at="2026-07-23",
            reviewer="minicerebro-seed",
            decision_reason="revision editorial inicial del primer lote real de ingestion",
        ),
        KnowledgeProposal(
            id="prop-rae-lese-dinamismo-frase-node",
            extraction_id=lese_extraction.id,
            segment_id=lese_segment.id,
            proposal_type="node",
            status="approved",
            title="Dinamismo de frase",
            payload={
                "id": "rae-lese-dinamismo-frase",
                "source_id": "rae-lese",
                "source_edition_id": "rae-lese:edicion-2018",
                "canonical_name": "Dinamismo de frase",
                "node_type": "concepto",
                "primary_branch": "escritura",
                "secondary_branch": "estilo",
                "summary": "Criterio de estilo asociado al avance claro de la frase.",
                "short_definition": "Rasgo de escritura basado en avance, claridad y baja friccion.",
                "long_definition": (
                    "Concepto validado desde un segmento editorial minimo del Libro de estilo "
                    "2018 y publicado como segundo lote estable de conocimiento."
                ),
                "aliases": ["ritmo de frase", "avance sintactico"],
                "version": KNOWLEDGE_V2_VERSION,
            },
            rationale="El segmento identifica dinamismo como criterio de eficacia expresiva.",
            confidence=0.66,
            source_locator=lese_segment.start_locator,
            created_at="2026-07-23",
            updated_at="2026-07-23",
            reviewed_at="2026-07-23",
            reviewer="minicerebro-seed",
            decision_reason="revision editorial del segundo lote real de ingestion",
        ),
        KnowledgeProposal(
            id="prop-rae-lese-dinamismo-frase-card",
            extraction_id=lese_extraction.id,
            segment_id=lese_segment.id,
            proposal_type="card",
            status="approved",
            title="Ficha candidata sobre dinamismo de frase",
            payload={
                "id": "card-dinamismo-frase",
                "card_type": "style_trait",
                "name": "Dinamismo de frase",
                "definition": "Rasgo asociado a avance claro, verbos activos y lectura fluida.",
                "payload": {
                    "signals": ["verbos activos", "frase con avance", "menos acumulacion"],
                    "risks": ["perdida de matiz", "ritmo demasiado abrupto"],
                    "contexts": ["articulo", "publicitario", "narrativa"],
                },
                "version": KNOWLEDGE_V2_VERSION,
            },
            rationale="La ficha agrupa el criterio de estilo validado por el lote.",
            confidence=0.62,
            source_locator=lese_segment.start_locator,
            created_at="2026-07-23",
            updated_at="2026-07-23",
            reviewed_at="2026-07-23",
            reviewer="minicerebro-seed",
            decision_reason="revision editorial del segundo lote real de ingestion",
        ),
        KnowledgeProposal(
            id="prop-rae-lese-dinamismo-frase-evidence",
            extraction_id=lese_extraction.id,
            segment_id=lese_segment.id,
            proposal_type="evidence",
            status="approved",
            title="Evidencia candidata sobre dinamismo de frase",
            payload={
                "id": "ev-rae-lese-dinamismo-frase",
                "node_id": "rae-lese-dinamismo-frase",
                "source_id": "rae-lese",
                "source_edition_id": "rae-lese:edicion-2018",
                "evidence_type": "editorial_summary",
                "locator": {
                    "edition": "Primera edicion, 2018",
                    "section": "claridad y eficacia expresiva",
                    "segment_id": lese_segment.id,
                },
                "reference": lese_segment.start_locator,
                "excerpt": lese_segment.text,
                "context": "seed_ingestion_incremental",
                "confidence_level": 3,
                "version": KNOWLEDGE_V2_VERSION,
            },
            rationale="El segmento conserva un resumen editorial minimo verificable.",
            confidence=0.62,
            source_locator=lese_segment.start_locator,
            created_at="2026-07-23",
            updated_at="2026-07-23",
            reviewed_at="2026-07-23",
            reviewer="minicerebro-seed",
            decision_reason="revision editorial del segundo lote real de ingestion",
        ),
        KnowledgeProposal(
            id="prop-rae-lese-dinamismo-frase-claim",
            extraction_id=lese_extraction.id,
            segment_id=lese_segment.id,
            proposal_type="claim",
            status="approved",
            title="Claim candidato sobre dinamismo de frase",
            payload={
                "id": "claim-rae-lese-dinamismo-frase",
                "evidence_id": "ev-rae-lese-dinamismo-frase",
                "card_id": "card-dinamismo-frase",
                "statement": (
                    "El dinamismo de frase se apoya en avance claro, verbos activos "
                    "y reduccion de acumulaciones que frenan la lectura."
                ),
                "claim_type": "stylistic",
                "node_id": "rae-lese-dinamismo-frase",
                "related_node_ids": ["manual-rasgos-escritura"],
                "domain": "writing.style",
                "scope": {
                    "language": "es",
                    "register": "general",
                    "geography": "panhispanic",
                    "period": "contemporary",
                    "text_type": "writing",
                },
                "version": KNOWLEDGE_V2_VERSION,
            },
            rationale="El claim queda sustentado por la evidencia validada del segmento.",
            confidence=0.62,
            source_locator=lese_segment.start_locator,
            created_at="2026-07-23",
            updated_at="2026-07-23",
            reviewed_at="2026-07-23",
            reviewer="minicerebro-seed",
            decision_reason="revision editorial del segundo lote real de ingestion",
        ),
        KnowledgeProposal(
            id="prop-rae-ole-acentuacion-grafica-node",
            extraction_id=ole_extraction.id,
            segment_id=ole_segment.id,
            proposal_type="node",
            status="approved",
            title="Acentuacion grafica",
            payload={
                "id": "rae-ole-acentuacion-grafica",
                "source_id": "rae-ole",
                "source_edition_id": "rae-ole:edicion-2010",
                "canonical_name": "Acentuacion grafica",
                "node_type": "norma",
                "primary_branch": "ortografia",
                "secondary_branch": "acentuacion",
                "summary": "Sistema normativo que regula el uso de la tilde en espanol.",
                "short_definition": "Norma ortografica que relaciona pronunciacion, silaba tonica y tilde.",
                "long_definition": (
                    "Concepto validado desde un segmento editorial minimo de la Ortografia "
                    "2010 y publicado como tercer lote estable de conocimiento."
                ),
                "aliases": ["uso de la tilde", "tilde"],
                "version": KNOWLEDGE_V3_VERSION,
            },
            rationale="El segmento identifica la acentuacion grafica como norma ortografica estable.",
            confidence=0.65,
            source_locator=ole_segment.start_locator,
            created_at="2026-07-23",
            updated_at="2026-07-23",
            reviewed_at="2026-07-23",
            reviewer="minicerebro-seed",
            decision_reason="revision editorial del tercer lote real de ingestion",
        ),
        KnowledgeProposal(
            id="prop-rae-ole-acentuacion-grafica-card",
            extraction_id=ole_extraction.id,
            segment_id=ole_segment.id,
            proposal_type="card",
            status="approved",
            title="Ficha candidata sobre acentuacion grafica",
            payload={
                "id": "card-acentuacion-grafica",
                "card_type": "orthography_rule",
                "name": "Acentuacion grafica",
                "definition": "Norma para orientar el uso de la tilde segun pronunciacion y silaba tonica.",
                "payload": {
                    "signals": ["silaba tonica", "tilde", "pronunciacion"],
                    "risks": ["requiere reglas especificas por tipo de palabra"],
                    "contexts": ["ortografia", "revision linguistica", "edicion"],
                },
                "version": KNOWLEDGE_V3_VERSION,
            },
            rationale="La ficha agrupa la norma ortografica validada por el lote.",
            confidence=0.63,
            source_locator=ole_segment.start_locator,
            created_at="2026-07-23",
            updated_at="2026-07-23",
            reviewed_at="2026-07-23",
            reviewer="minicerebro-seed",
            decision_reason="revision editorial del tercer lote real de ingestion",
        ),
        KnowledgeProposal(
            id="prop-rae-ole-acentuacion-grafica-evidence",
            extraction_id=ole_extraction.id,
            segment_id=ole_segment.id,
            proposal_type="evidence",
            status="approved",
            title="Evidencia candidata sobre acentuacion grafica",
            payload={
                "id": "ev-rae-ole-acentuacion-grafica",
                "node_id": "rae-ole-acentuacion-grafica",
                "source_id": "rae-ole",
                "source_edition_id": "rae-ole:edicion-2010",
                "evidence_type": "editorial_summary",
                "locator": {
                    "edition": "Edicion academica, 2010",
                    "section": "acentuacion grafica",
                    "segment_id": ole_segment.id,
                },
                "reference": ole_segment.start_locator,
                "excerpt": ole_segment.text,
                "context": "seed_orthography_incremental",
                "confidence_level": 3,
                "version": KNOWLEDGE_V3_VERSION,
            },
            rationale="El segmento conserva un resumen editorial minimo verificable.",
            confidence=0.63,
            source_locator=ole_segment.start_locator,
            created_at="2026-07-23",
            updated_at="2026-07-23",
            reviewed_at="2026-07-23",
            reviewer="minicerebro-seed",
            decision_reason="revision editorial del tercer lote real de ingestion",
        ),
        KnowledgeProposal(
            id="prop-rae-ole-acentuacion-grafica-claim",
            extraction_id=ole_extraction.id,
            segment_id=ole_segment.id,
            proposal_type="claim",
            status="approved",
            title="Claim candidato sobre acentuacion grafica",
            payload={
                "id": "claim-rae-ole-acentuacion-grafica",
                "evidence_id": "ev-rae-ole-acentuacion-grafica",
                "card_id": "card-acentuacion-grafica",
                "statement": (
                    "La acentuacion grafica orienta el uso de la tilde relacionando "
                    "pronunciacion, silaba tonica y norma ortografica."
                ),
                "claim_type": "orthographic",
                "node_id": "rae-ole-acentuacion-grafica",
                "related_node_ids": ["rae-norma-estilo"],
                "domain": "orthography.accentuation",
                "scope": {
                    "language": "es",
                    "register": "general",
                    "geography": "panhispanic",
                    "period": "contemporary",
                    "text_type": "orthography",
                },
                "version": KNOWLEDGE_V3_VERSION,
            },
            rationale="El claim queda sustentado por la evidencia validada del segmento.",
            confidence=0.63,
            source_locator=ole_segment.start_locator,
            created_at="2026-07-23",
            updated_at="2026-07-23",
            reviewed_at="2026-07-23",
            reviewer="minicerebro-seed",
            decision_reason="revision editorial del tercer lote real de ingestion",
        ),
        KnowledgeProposal(
            id="prop-rae-gtg-terminologia-gramatical-node",
            extraction_id=gtg_extraction.id,
            segment_id=gtg_segment.id,
            proposal_type="node",
            status="approved",
            title="Terminologia gramatical",
            payload={
                "id": "rae-gtg-terminologia-gramatical",
                "source_id": "rae-gtg",
                "source_edition_id": "rae-gtg:edicion-2019",
                "canonical_name": "Terminologia gramatical",
                "node_type": "metodo",
                "primary_branch": "gramatica",
                "secondary_branch": "terminologia",
                "summary": "Sistema de denominaciones para estabilizar el analisis gramatical.",
                "short_definition": "Conjunto controlado de terminos usados para nombrar categorias y funciones.",
                "long_definition": (
                    "Concepto validado desde un segmento editorial minimo del Glosario "
                    "de terminos gramaticales 2019 y publicado como cuarto lote estable "
                    "de conocimiento."
                ),
                "aliases": ["nomenclatura gramatical", "terminos gramaticales"],
                "version": KNOWLEDGE_V4_VERSION,
            },
            rationale="El segmento identifica la terminologia como soporte del analisis gramatical.",
            confidence=0.64,
            source_locator=gtg_segment.start_locator,
            created_at="2026-07-23",
            updated_at="2026-07-23",
            reviewed_at="2026-07-23",
            reviewer="minicerebro-seed",
            decision_reason="revision editorial del cuarto lote real de ingestion",
        ),
        KnowledgeProposal(
            id="prop-rae-gtg-terminologia-gramatical-card",
            extraction_id=gtg_extraction.id,
            segment_id=gtg_segment.id,
            proposal_type="card",
            status="approved",
            title="Ficha candidata sobre terminologia gramatical",
            payload={
                "id": "card-terminologia-gramatical",
                "card_type": "grammar_method",
                "name": "Terminologia gramatical",
                "definition": "Marco de nombres estables para categorias, funciones y relaciones gramaticales.",
                "payload": {
                    "signals": ["denominacion estable", "alias controlados", "relaciones conceptuales"],
                    "risks": ["confundir sinonimos con conceptos distintos"],
                    "contexts": ["gramatica", "glosario", "revision linguistica"],
                },
                "version": KNOWLEDGE_V4_VERSION,
            },
            rationale="La ficha agrupa la utilidad del glosario para consulta y trazabilidad.",
            confidence=0.62,
            source_locator=gtg_segment.start_locator,
            created_at="2026-07-23",
            updated_at="2026-07-23",
            reviewed_at="2026-07-23",
            reviewer="minicerebro-seed",
            decision_reason="revision editorial del cuarto lote real de ingestion",
        ),
        KnowledgeProposal(
            id="prop-rae-gtg-terminologia-gramatical-evidence",
            extraction_id=gtg_extraction.id,
            segment_id=gtg_segment.id,
            proposal_type="evidence",
            status="approved",
            title="Evidencia candidata sobre terminologia gramatical",
            payload={
                "id": "ev-rae-gtg-terminologia-gramatical",
                "node_id": "rae-gtg-terminologia-gramatical",
                "source_id": "rae-gtg",
                "source_edition_id": "rae-gtg:edicion-2019",
                "evidence_type": "editorial_summary",
                "locator": {
                    "edition": "Edicion academica, 2019",
                    "section": "terminologia sintactica",
                    "segment_id": gtg_segment.id,
                },
                "reference": gtg_segment.start_locator,
                "excerpt": gtg_segment.text,
                "context": "seed_terminology_incremental",
                "confidence_level": 3,
                "version": KNOWLEDGE_V4_VERSION,
            },
            rationale="El segmento conserva un resumen editorial minimo verificable.",
            confidence=0.62,
            source_locator=gtg_segment.start_locator,
            created_at="2026-07-23",
            updated_at="2026-07-23",
            reviewed_at="2026-07-23",
            reviewer="minicerebro-seed",
            decision_reason="revision editorial del cuarto lote real de ingestion",
        ),
        KnowledgeProposal(
            id="prop-rae-gtg-terminologia-gramatical-claim",
            extraction_id=gtg_extraction.id,
            segment_id=gtg_segment.id,
            proposal_type="claim",
            status="approved",
            title="Claim candidato sobre terminologia gramatical",
            payload={
                "id": "claim-rae-gtg-terminologia-gramatical",
                "evidence_id": "ev-rae-gtg-terminologia-gramatical",
                "card_id": "card-terminologia-gramatical",
                "statement": (
                    "La terminologia gramatical estabiliza la consulta al fijar "
                    "denominaciones y relaciones entre categorias y funciones."
                ),
                "claim_type": "terminological",
                "node_id": "rae-gtg-terminologia-gramatical",
                "related_node_ids": ["rae-ngle-complemento-directo"],
                "domain": "grammar.terminology",
                "scope": {
                    "language": "es",
                    "register": "general",
                    "geography": "panhispanic",
                    "period": "contemporary",
                    "text_type": "grammar",
                },
                "version": KNOWLEDGE_V4_VERSION,
            },
            rationale="El claim queda sustentado por la evidencia validada del segmento.",
            confidence=0.62,
            source_locator=gtg_segment.start_locator,
            created_at="2026-07-23",
            updated_at="2026-07-23",
            reviewed_at="2026-07-23",
            reviewer="minicerebro-seed",
            decision_reason="revision editorial del cuarto lote real de ingestion",
        ),
        KnowledgeProposal(
            id="prop-rae-dle-precision-lexica-node",
            extraction_id=dle_extraction.id,
            segment_id=dle_segment.id,
            proposal_type="node",
            status="approved",
            title="Precision lexica",
            payload={
                "id": "rae-dle-precision-lexica",
                "source_id": "rae-dle",
                "source_edition_id": "rae-dle:edicion-23-digital",
                "canonical_name": "Precision lexica",
                "node_type": "concepto",
                "primary_branch": "lexico",
                "secondary_branch": "seleccion lexica",
                "summary": "Criterio para elegir palabras y acepciones con sentido verificable.",
                "short_definition": "Rasgo de escritura basado en seleccionar palabras exactas para el sentido buscado.",
                "long_definition": (
                    "Concepto validado desde un segmento editorial minimo del Diccionario "
                    "de la lengua espanola y publicado como quinto lote estable de conocimiento."
                ),
                "aliases": ["exactitud lexica", "propiedad lexica"],
                "version": KNOWLEDGE_V5_VERSION,
            },
            rationale="El segmento identifica la precision como criterio lexico verificable.",
            confidence=0.63,
            source_locator=dle_segment.start_locator,
            created_at="2026-07-23",
            updated_at="2026-07-23",
            reviewed_at="2026-07-23",
            reviewer="minicerebro-seed",
            decision_reason="revision editorial del quinto lote real de ingestion",
        ),
        KnowledgeProposal(
            id="prop-rae-dle-precision-lexica-card",
            extraction_id=dle_extraction.id,
            segment_id=dle_segment.id,
            proposal_type="card",
            status="approved",
            title="Ficha candidata sobre precision lexica",
            payload={
                "id": "card-precision-lexica",
                "card_type": "lexical_trait",
                "name": "Precision lexica",
                "definition": "Criterio para elegir palabras concretas y acepciones acordes con el sentido buscado.",
                "payload": {
                    "signals": ["palabras concretas", "acepciones pertinentes", "menos vaguedad"],
                    "risks": ["tecnicismo innecesario", "perdida de naturalidad"],
                    "contexts": ["revision lexica", "ensayo", "texto tecnico"],
                },
                "version": KNOWLEDGE_V5_VERSION,
            },
            rationale="La ficha agrupa el criterio lexico validado por el lote.",
            confidence=0.61,
            source_locator=dle_segment.start_locator,
            created_at="2026-07-23",
            updated_at="2026-07-23",
            reviewed_at="2026-07-23",
            reviewer="minicerebro-seed",
            decision_reason="revision editorial del quinto lote real de ingestion",
        ),
        KnowledgeProposal(
            id="prop-rae-dle-precision-lexica-evidence",
            extraction_id=dle_extraction.id,
            segment_id=dle_segment.id,
            proposal_type="evidence",
            status="approved",
            title="Evidencia candidata sobre precision lexica",
            payload={
                "id": "ev-rae-dle-precision-lexica",
                "node_id": "rae-dle-precision-lexica",
                "source_id": "rae-dle",
                "source_edition_id": "rae-dle:edicion-23-digital",
                "evidence_type": "editorial_summary",
                "locator": {
                    "edition": "23.a edicion digital",
                    "section": "precision lexica y seleccion de acepciones",
                    "segment_id": dle_segment.id,
                },
                "reference": dle_segment.start_locator,
                "excerpt": dle_segment.text,
                "context": "seed_lexicon_incremental",
                "confidence_level": 3,
                "version": KNOWLEDGE_V5_VERSION,
            },
            rationale="El segmento conserva un resumen editorial minimo verificable.",
            confidence=0.61,
            source_locator=dle_segment.start_locator,
            created_at="2026-07-23",
            updated_at="2026-07-23",
            reviewed_at="2026-07-23",
            reviewer="minicerebro-seed",
            decision_reason="revision editorial del quinto lote real de ingestion",
        ),
        KnowledgeProposal(
            id="prop-rae-dle-precision-lexica-claim",
            extraction_id=dle_extraction.id,
            segment_id=dle_segment.id,
            proposal_type="claim",
            status="approved",
            title="Claim candidato sobre precision lexica",
            payload={
                "id": "claim-rae-dle-precision-lexica",
                "evidence_id": "ev-rae-dle-precision-lexica",
                "card_id": "card-precision-lexica",
                "statement": (
                    "La precision lexica reduce vaguedad y ambiguedad al elegir palabras "
                    "y acepciones acordes con el sentido buscado."
                ),
                "claim_type": "lexical",
                "node_id": "rae-dle-precision-lexica",
                "related_node_ids": ["rae-norma-estilo", "manual-rasgos-escritura"],
                "domain": "writing.lexicon",
                "scope": {
                    "language": "es",
                    "register": "general",
                    "geography": "panhispanic",
                    "period": "contemporary",
                    "text_type": "writing",
                },
                "version": KNOWLEDGE_V5_VERSION,
            },
            rationale="El claim queda sustentado por la evidencia validada del segmento.",
            confidence=0.61,
            source_locator=dle_segment.start_locator,
            created_at="2026-07-23",
            updated_at="2026-07-23",
            reviewed_at="2026-07-23",
            reviewer="minicerebro-seed",
            decision_reason="revision editorial del quinto lote real de ingestion",
        ),
        *_v6_proposals(),
        *_v7_proposals(),
        *_published_batch_proposals(V8_SEED_ITEMS, KNOWLEDGE_V8_VERSION),
        *_published_batch_proposals(V9_SEED_ITEMS, KNOWLEDGE_V9_VERSION),
        *_published_batch_proposals(V10_SEED_ITEMS, KNOWLEDGE_V10_VERSION),
        *_published_batch_proposals(V11_SEED_ITEMS, KNOWLEDGE_V11_VERSION),
        *_published_batch_proposals(V12_SEED_ITEMS, KNOWLEDGE_V12_VERSION),
        *_published_batch_proposals(V13_SEED_ITEMS, KNOWLEDGE_V13_VERSION),
        *_published_batch_proposals(V14_SEED_ITEMS, LATEST_PUBLISHED_KNOWLEDGE_VERSION),
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
        KnowledgeNode(
            id="rae-ngle-complemento-directo",
            source_id="rae-ngle",
            node_type="concepto",
            title="Complemento directo",
            summary="Funcion sintactica vinculada al predicado verbal.",
            canonical_name="Complemento directo",
            primary_branch="sintaxis",
            secondary_branch="funciones sintacticas",
            short_definition="Funcion sintactica asociada al participante seleccionado por el verbo.",
            long_definition=(
                "Concepto validado desde el primer lote real de ingestion de la NGLE Manual "
                "2010. Queda materializado como conocimiento estable publicado en knowledge-v1."
            ),
            status="published",
            version=PUBLISHED_KNOWLEDGE_VERSION,
            created_at="2026-07-23",
            published_at=KNOWLEDGE_V1_PUBLISHED_AT,
            aliases=["objeto directo"],
        ),
        KnowledgeNode(
            id="rae-lese-dinamismo-frase",
            source_id="rae-lese",
            node_type="concepto",
            title="Dinamismo de frase",
            summary="Criterio de estilo asociado al avance claro de la frase.",
            canonical_name="Dinamismo de frase",
            primary_branch="escritura",
            secondary_branch="estilo",
            short_definition="Rasgo de escritura basado en avance, claridad y baja friccion.",
            long_definition=(
                "Concepto validado desde el segundo lote real de ingestion del Libro de "
                "estilo 2018. Queda materializado como conocimiento estable publicado "
                "en knowledge-v2."
            ),
            status="published",
            version=KNOWLEDGE_V2_VERSION,
            created_at="2026-07-23",
            published_at=KNOWLEDGE_V2_PUBLISHED_AT,
            aliases=["ritmo de frase", "avance sintactico"],
        ),
        KnowledgeNode(
            id="rae-ole-acentuacion-grafica",
            source_id="rae-ole",
            node_type="norma",
            title="Acentuacion grafica",
            summary="Sistema normativo que regula el uso de la tilde en espanol.",
            canonical_name="Acentuacion grafica",
            primary_branch="ortografia",
            secondary_branch="acentuacion",
            short_definition="Norma ortografica que relaciona pronunciacion, silaba tonica y tilde.",
            long_definition=(
                "Concepto validado desde el tercer lote real de ingestion de la Ortografia "
                "2010. Queda materializado como conocimiento estable publicado en knowledge-v3."
            ),
            status="published",
            version=KNOWLEDGE_V3_VERSION,
            created_at="2026-07-23",
            published_at=KNOWLEDGE_V3_PUBLISHED_AT,
            aliases=["uso de la tilde", "tilde"],
        ),
        KnowledgeNode(
            id="rae-gtg-terminologia-gramatical",
            source_id="rae-gtg",
            node_type="metodo",
            title="Terminologia gramatical",
            summary="Sistema de denominaciones para estabilizar el analisis gramatical.",
            canonical_name="Terminologia gramatical",
            primary_branch="gramatica",
            secondary_branch="terminologia",
            short_definition="Conjunto controlado de terminos usados para nombrar categorias y funciones.",
            long_definition=(
                "Concepto validado desde el cuarto lote real de ingestion del Glosario "
                "de terminos gramaticales 2019. Queda materializado como conocimiento "
                "estable publicado en knowledge-v4."
            ),
            status="published",
            version=KNOWLEDGE_V4_VERSION,
            created_at="2026-07-23",
            published_at=KNOWLEDGE_V4_PUBLISHED_AT,
            aliases=["nomenclatura gramatical", "terminos gramaticales"],
        ),
        KnowledgeNode(
            id="rae-dle-precision-lexica",
            source_id="rae-dle",
            node_type="concepto",
            title="Precision lexica",
            summary="Criterio para elegir palabras y acepciones con sentido verificable.",
            canonical_name="Precision lexica",
            primary_branch="lexico",
            secondary_branch="seleccion lexica",
            short_definition="Rasgo de escritura basado en seleccionar palabras exactas para el sentido buscado.",
            long_definition=(
                "Concepto validado desde el quinto lote real de ingestion del Diccionario "
                "de la lengua espanola. Queda materializado como conocimiento estable "
                "publicado en knowledge-v5."
            ),
            status="published",
            version=KNOWLEDGE_V5_VERSION,
            created_at="2026-07-23",
            published_at=KNOWLEDGE_V5_PUBLISHED_AT,
            aliases=["exactitud lexica", "propiedad lexica"],
        ),
        *_v6_nodes(),
        *_v7_nodes(),
        *_published_batch_nodes(V8_SEED_ITEMS, KNOWLEDGE_V8_VERSION),
        *_published_batch_nodes(V9_SEED_ITEMS, KNOWLEDGE_V9_VERSION),
        *_published_batch_nodes(V10_SEED_ITEMS, KNOWLEDGE_V10_VERSION),
        *_published_batch_nodes(V11_SEED_ITEMS, KNOWLEDGE_V11_VERSION),
        *_published_batch_nodes(V12_SEED_ITEMS, KNOWLEDGE_V12_VERSION),
        *_published_batch_nodes(V13_SEED_ITEMS, KNOWLEDGE_V13_VERSION),
        *_published_batch_nodes(V14_SEED_ITEMS, LATEST_PUBLISHED_KNOWLEDGE_VERSION),
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
        KnowledgeNodeRelation(
            id="rel-complemento-directo-depende-norma",
            source_node_id="rae-ngle-complemento-directo",
            target_node_id="rae-norma-estilo",
            relation_type="depende_de",
            direction="outgoing",
            cardinality="N:1",
            weight=0.7,
            confidence=0.64,
            context="seed_ingestion_candidate",
            status="published",
            version=PUBLISHED_KNOWLEDGE_VERSION,
            created_at="2026-07-23",
            updated_at="2026-07-23",
        ),
        KnowledgeNodeRelation(
            id="rel-dinamismo-frase-depende-rasgos-escritura",
            source_node_id="rae-lese-dinamismo-frase",
            target_node_id="manual-rasgos-escritura",
            relation_type="depende_de",
            direction="outgoing",
            cardinality="N:1",
            weight=0.7,
            confidence=0.62,
            context="seed_ingestion_incremental",
            status="published",
            version=KNOWLEDGE_V2_VERSION,
            created_at="2026-07-23",
            updated_at="2026-07-23",
        ),
        KnowledgeNodeRelation(
            id="rel-acentuacion-grafica-depende-norma",
            source_node_id="rae-ole-acentuacion-grafica",
            target_node_id="rae-norma-estilo",
            relation_type="depende_de",
            direction="outgoing",
            cardinality="N:1",
            weight=0.7,
            confidence=0.63,
            context="seed_orthography_incremental",
            status="published",
            version=KNOWLEDGE_V3_VERSION,
            created_at="2026-07-23",
            updated_at="2026-07-23",
        ),
        KnowledgeNodeRelation(
            id="rel-terminologia-gramatical-relaciona-complemento-directo",
            source_node_id="rae-gtg-terminologia-gramatical",
            target_node_id="rae-ngle-complemento-directo",
            relation_type="relacionado_con",
            direction="outgoing",
            cardinality="N:N",
            weight=0.68,
            confidence=0.62,
            context="seed_terminology_incremental",
            status="published",
            version=KNOWLEDGE_V4_VERSION,
            created_at="2026-07-23",
            updated_at="2026-07-23",
        ),
        KnowledgeNodeRelation(
            id="rel-precision-lexica-depende-norma",
            source_node_id="rae-dle-precision-lexica",
            target_node_id="rae-norma-estilo",
            relation_type="depende_de",
            direction="outgoing",
            cardinality="N:1",
            weight=0.67,
            confidence=0.61,
            context="seed_lexicon_incremental",
            status="published",
            version=KNOWLEDGE_V5_VERSION,
            created_at="2026-07-23",
            updated_at="2026-07-23",
        ),
        *_v6_node_relations(),
        *_v7_node_relations(),
        *_published_batch_node_relations(V8_SEED_ITEMS, KNOWLEDGE_V8_VERSION),
        *_published_batch_node_relations(V9_SEED_ITEMS, KNOWLEDGE_V9_VERSION),
        *_published_batch_node_relations(V10_SEED_ITEMS, KNOWLEDGE_V10_VERSION),
        *_published_batch_node_relations(V11_SEED_ITEMS, KNOWLEDGE_V11_VERSION),
        *_published_batch_node_relations(V12_SEED_ITEMS, KNOWLEDGE_V12_VERSION),
        *_published_batch_node_relations(V13_SEED_ITEMS, KNOWLEDGE_V13_VERSION),
        *_published_batch_node_relations(V14_SEED_ITEMS, LATEST_PUBLISHED_KNOWLEDGE_VERSION),
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
    version: str = KNOWLEDGE_VERSION,
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
        version=version,
        created_at=KNOWLEDGE_PUBLISHED_AT,
        updated_at=RELATION_UPDATED_AT,
    )


def seed_relations() -> list[KnowledgeRelation]:
    source_to_edition = [
        _relation("source", source.id, "contiene", "source_edition", f"{source.id}:pending-edition")
        for source in seed_sources()
    ]
    source_to_node = [
        _relation(
            "source",
            node.source_id,
            "documentado_en",
            "node",
            node.id,
            status=node.status,
            version=node.version,
        )
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
            version=relation.version,
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
            version=evidence.version,
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
            version=claim.version,
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
            version=claim.version,
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
            version=evidence.version,
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
        KnowledgeEvidenceItem(
            id="ev-rae-ngle-complemento-directo-candidata",
            node_id="rae-ngle-complemento-directo",
            source_id="rae-ngle",
            source_edition_id="rae-ngle:manual-2010",
            evidence_type="editorial_summary",
            locator={
                "edition": "Manual academico, 2010",
                "section": "funciones sintacticas",
                "segment_id": "rae-ngle:manual-2010:funciones-sintacticas:seg-1",
            },
            reference="Manual 2010 > sintaxis > funciones sintacticas > resumen editorial 1",
            excerpt=seed_segments()[0].text,
            context="seed_ingestion_candidate",
            confidence=0.66,
            confidence_level=3,
            status="published",
            version=PUBLISHED_KNOWLEDGE_VERSION,
            created_at="2026-07-23",
            updated_at=KNOWLEDGE_V1_PUBLISHED_AT,
            incorporated_by="minicerebro-seed",
            reviewed_by="minicerebro-seed",
            revision=1,
        ),
        KnowledgeEvidenceItem(
            id="ev-rae-lese-dinamismo-frase",
            node_id="rae-lese-dinamismo-frase",
            source_id="rae-lese",
            source_edition_id="rae-lese:edicion-2018",
            evidence_type="editorial_summary",
            locator={
                "edition": "Primera edicion, 2018",
                "section": "claridad y eficacia expresiva",
                "segment_id": "rae-lese:edicion-2018:claridad-estilo:seg-1",
            },
            reference="Edicion 2018 > estilo > claridad y eficacia expresiva > resumen editorial 1",
            excerpt=seed_segments()[1].text,
            context="seed_ingestion_incremental",
            confidence=0.62,
            confidence_level=3,
            status="published",
            version=KNOWLEDGE_V2_VERSION,
            created_at="2026-07-23",
            updated_at=KNOWLEDGE_V2_PUBLISHED_AT,
            incorporated_by="minicerebro-seed",
            reviewed_by="minicerebro-seed",
            revision=1,
        ),
        KnowledgeEvidenceItem(
            id="ev-rae-ole-acentuacion-grafica",
            node_id="rae-ole-acentuacion-grafica",
            source_id="rae-ole",
            source_edition_id="rae-ole:edicion-2010",
            evidence_type="editorial_summary",
            locator={
                "edition": "Edicion academica, 2010",
                "section": "acentuacion grafica",
                "segment_id": "rae-ole:edicion-2010:acentuacion:seg-1",
            },
            reference="Edicion 2010 > acentuacion grafica > resumen editorial 1",
            excerpt=seed_segments()[2].text,
            context="seed_orthography_incremental",
            confidence=0.63,
            confidence_level=3,
            status="published",
            version=KNOWLEDGE_V3_VERSION,
            created_at="2026-07-23",
            updated_at=KNOWLEDGE_V3_PUBLISHED_AT,
            incorporated_by="minicerebro-seed",
            reviewed_by="minicerebro-seed",
            revision=1,
        ),
        KnowledgeEvidenceItem(
            id="ev-rae-gtg-terminologia-gramatical",
            node_id="rae-gtg-terminologia-gramatical",
            source_id="rae-gtg",
            source_edition_id="rae-gtg:edicion-2019",
            evidence_type="editorial_summary",
            locator={
                "edition": "Edicion academica, 2019",
                "section": "terminologia sintactica",
                "segment_id": "rae-gtg:edicion-2019:terminologia-sintactica:seg-1",
            },
            reference="Edicion 2019 > terminologia sintactica > resumen editorial 1",
            excerpt=seed_segments()[3].text,
            context="seed_terminology_incremental",
            confidence=0.62,
            confidence_level=3,
            status="published",
            version=KNOWLEDGE_V4_VERSION,
            created_at="2026-07-23",
            updated_at=KNOWLEDGE_V4_PUBLISHED_AT,
            incorporated_by="minicerebro-seed",
            reviewed_by="minicerebro-seed",
            revision=1,
        ),
        KnowledgeEvidenceItem(
            id="ev-rae-dle-precision-lexica",
            node_id="rae-dle-precision-lexica",
            source_id="rae-dle",
            source_edition_id="rae-dle:edicion-23-digital",
            evidence_type="editorial_summary",
            locator={
                "edition": "23.a edicion digital",
                "section": "precision lexica y seleccion de acepciones",
                "segment_id": "rae-dle:edicion-23-digital:precision-lexica:seg-1",
            },
            reference="23.a edicion digital > lexico > precision lexica > resumen editorial 1",
            excerpt=seed_segments()[4].text,
            context="seed_lexicon_incremental",
            confidence=0.61,
            confidence_level=3,
            status="published",
            version=KNOWLEDGE_V5_VERSION,
            created_at="2026-07-23",
            updated_at=KNOWLEDGE_V5_PUBLISHED_AT,
            incorporated_by="minicerebro-seed",
            reviewed_by="minicerebro-seed",
            revision=1,
        ),
        *_v6_evidence(),
        *_v7_evidence(),
        *_published_batch_evidence(V8_SEED_ITEMS, KNOWLEDGE_V8_VERSION),
        *_published_batch_evidence(V9_SEED_ITEMS, KNOWLEDGE_V9_VERSION),
        *_published_batch_evidence(V10_SEED_ITEMS, KNOWLEDGE_V10_VERSION),
        *_published_batch_evidence(V11_SEED_ITEMS, KNOWLEDGE_V11_VERSION),
        *_published_batch_evidence(V12_SEED_ITEMS, KNOWLEDGE_V12_VERSION),
        *_published_batch_evidence(V13_SEED_ITEMS, KNOWLEDGE_V13_VERSION),
        *_published_batch_evidence(V14_SEED_ITEMS, LATEST_PUBLISHED_KNOWLEDGE_VERSION),
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
        KnowledgeClaim(
            id="claim-rae-ngle-complemento-directo",
            evidence_id="ev-rae-ngle-complemento-directo-candidata",
            card_id="card-complemento-directo",
            statement=(
                "El complemento directo funciona como participante seleccionado "
                "por el predicado verbal en el analisis sintactico."
            ),
            claim_type="grammatical",
            node_id="rae-ngle-complemento-directo",
            related_node_ids=["rae-norma-estilo"],
            domain="grammar.syntax",
            scope={
                "language": "es",
                "register": "general",
                "geography": "panhispanic",
                "period": "contemporary",
                "text_type": "grammar",
            },
            status="published",
            confidence=0.64,
            origin="approved_knowledge_proposal",
            version=PUBLISHED_KNOWLEDGE_VERSION,
            revision=1,
            created_at="2026-07-23",
            updated_at=KNOWLEDGE_V1_PUBLISHED_AT,
            published_at=KNOWLEDGE_V1_PUBLISHED_AT,
        ),
        KnowledgeClaim(
            id="claim-rae-lese-dinamismo-frase",
            evidence_id="ev-rae-lese-dinamismo-frase",
            card_id="card-dinamismo-frase",
            statement=(
                "El dinamismo de frase se apoya en avance claro, verbos activos "
                "y reduccion de acumulaciones que frenan la lectura."
            ),
            claim_type="stylistic",
            node_id="rae-lese-dinamismo-frase",
            related_node_ids=["manual-rasgos-escritura"],
            domain="writing.style",
            scope={
                "language": "es",
                "register": "general",
                "geography": "panhispanic",
                "period": "contemporary",
                "text_type": "writing",
            },
            status="published",
            confidence=0.62,
            origin="approved_knowledge_proposal",
            version=KNOWLEDGE_V2_VERSION,
            revision=1,
            created_at="2026-07-23",
            updated_at=KNOWLEDGE_V2_PUBLISHED_AT,
            published_at=KNOWLEDGE_V2_PUBLISHED_AT,
        ),
        KnowledgeClaim(
            id="claim-rae-ole-acentuacion-grafica",
            evidence_id="ev-rae-ole-acentuacion-grafica",
            card_id="card-acentuacion-grafica",
            statement=(
                "La acentuacion grafica orienta el uso de la tilde relacionando "
                "pronunciacion, silaba tonica y norma ortografica."
            ),
            claim_type="orthographic",
            node_id="rae-ole-acentuacion-grafica",
            related_node_ids=["rae-norma-estilo"],
            domain="orthography.accentuation",
            scope={
                "language": "es",
                "register": "general",
                "geography": "panhispanic",
                "period": "contemporary",
                "text_type": "orthography",
            },
            status="published",
            confidence=0.63,
            origin="approved_knowledge_proposal",
            version=KNOWLEDGE_V3_VERSION,
            revision=1,
            created_at="2026-07-23",
            updated_at=KNOWLEDGE_V3_PUBLISHED_AT,
            published_at=KNOWLEDGE_V3_PUBLISHED_AT,
        ),
        KnowledgeClaim(
            id="claim-rae-gtg-terminologia-gramatical",
            evidence_id="ev-rae-gtg-terminologia-gramatical",
            card_id="card-terminologia-gramatical",
            statement=(
                "La terminologia gramatical estabiliza la consulta al fijar "
                "denominaciones y relaciones entre categorias y funciones."
            ),
            claim_type="terminological",
            node_id="rae-gtg-terminologia-gramatical",
            related_node_ids=["rae-ngle-complemento-directo"],
            domain="grammar.terminology",
            scope={
                "language": "es",
                "register": "general",
                "geography": "panhispanic",
                "period": "contemporary",
                "text_type": "grammar",
            },
            status="published",
            confidence=0.62,
            origin="approved_knowledge_proposal",
            version=KNOWLEDGE_V4_VERSION,
            revision=1,
            created_at="2026-07-23",
            updated_at=KNOWLEDGE_V4_PUBLISHED_AT,
            published_at=KNOWLEDGE_V4_PUBLISHED_AT,
        ),
        KnowledgeClaim(
            id="claim-rae-dle-precision-lexica",
            evidence_id="ev-rae-dle-precision-lexica",
            card_id="card-precision-lexica",
            statement=(
                "La precision lexica reduce vaguedad y ambiguedad al elegir palabras "
                "y acepciones acordes con el sentido buscado."
            ),
            claim_type="lexical",
            node_id="rae-dle-precision-lexica",
            related_node_ids=["rae-norma-estilo", "manual-rasgos-escritura"],
            domain="writing.lexicon",
            scope={
                "language": "es",
                "register": "general",
                "geography": "panhispanic",
                "period": "contemporary",
                "text_type": "writing",
            },
            status="published",
            confidence=0.61,
            origin="approved_knowledge_proposal",
            version=KNOWLEDGE_V5_VERSION,
            revision=1,
            created_at="2026-07-23",
            updated_at=KNOWLEDGE_V5_PUBLISHED_AT,
            published_at=KNOWLEDGE_V5_PUBLISHED_AT,
        ),
        *_v6_claims(),
        *_v7_claims(),
        *_published_batch_claims(V8_SEED_ITEMS, KNOWLEDGE_V8_VERSION),
        *_published_batch_claims(V9_SEED_ITEMS, KNOWLEDGE_V9_VERSION),
        *_published_batch_claims(V10_SEED_ITEMS, KNOWLEDGE_V10_VERSION),
        *_published_batch_claims(V11_SEED_ITEMS, KNOWLEDGE_V11_VERSION),
        *_published_batch_claims(V12_SEED_ITEMS, KNOWLEDGE_V12_VERSION),
        *_published_batch_claims(V13_SEED_ITEMS, KNOWLEDGE_V13_VERSION),
        *_published_batch_claims(V14_SEED_ITEMS, LATEST_PUBLISHED_KNOWLEDGE_VERSION),
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
        KnowledgeCard(
            id="card-complemento-directo",
            card_type="grammar_concept",
            name="Complemento directo",
            definition="Funcion sintactica asociada al participante seleccionado por el verbo.",
            confidence=0.64,
            version=PUBLISHED_KNOWLEDGE_VERSION,
            payload={
                "signals": [
                    "vinculo con el predicado verbal",
                    "participante seleccionado por el verbo",
                    "analisis dentro de funciones sintacticas",
                ],
                "risks": ["requiere ampliacion con mas evidencias en futuros lotes"],
                "contexts": ["gramatica", "sintaxis", "revision linguistica"],
            },
        ),
        KnowledgeCard(
            id="card-dinamismo-frase",
            card_type="style_trait",
            name="Dinamismo de frase",
            definition="Rasgo asociado a avance claro, verbos activos y lectura fluida.",
            confidence=0.62,
            version=KNOWLEDGE_V2_VERSION,
            payload={
                "signals": ["verbos activos", "frase con avance", "menos acumulacion"],
                "risks": ["perdida de matiz", "ritmo demasiado abrupto"],
                "contexts": ["articulo", "publicitario", "narrativa"],
            },
        ),
        KnowledgeCard(
            id="card-acentuacion-grafica",
            card_type="orthography_rule",
            name="Acentuacion grafica",
            definition="Norma para orientar el uso de la tilde segun pronunciacion y silaba tonica.",
            confidence=0.63,
            version=KNOWLEDGE_V3_VERSION,
            payload={
                "signals": ["silaba tonica", "tilde", "pronunciacion"],
                "risks": ["requiere reglas especificas por tipo de palabra"],
                "contexts": ["ortografia", "revision linguistica", "edicion"],
            },
        ),
        KnowledgeCard(
            id="card-terminologia-gramatical",
            card_type="grammar_method",
            name="Terminologia gramatical",
            definition="Marco de nombres estables para categorias, funciones y relaciones gramaticales.",
            confidence=0.62,
            version=KNOWLEDGE_V4_VERSION,
            payload={
                "signals": ["denominacion estable", "alias controlados", "relaciones conceptuales"],
                "risks": ["confundir sinonimos con conceptos distintos"],
                "contexts": ["gramatica", "glosario", "revision linguistica"],
            },
        ),
        KnowledgeCard(
            id="card-precision-lexica",
            card_type="lexical_trait",
            name="Precision lexica",
            definition="Criterio para elegir palabras concretas y acepciones acordes con el sentido buscado.",
            confidence=0.61,
            version=KNOWLEDGE_V5_VERSION,
            payload={
                "signals": ["palabras concretas", "acepciones pertinentes", "menos vaguedad"],
                "risks": ["tecnicismo innecesario", "perdida de naturalidad"],
                "contexts": ["revision lexica", "ensayo", "texto tecnico"],
            },
        ),
        *_v6_cards(),
        *_v7_cards(),
        *_published_batch_cards(V8_SEED_ITEMS, KNOWLEDGE_V8_VERSION),
        *_published_batch_cards(V9_SEED_ITEMS, KNOWLEDGE_V9_VERSION),
        *_published_batch_cards(V10_SEED_ITEMS, KNOWLEDGE_V10_VERSION),
        *_published_batch_cards(V11_SEED_ITEMS, KNOWLEDGE_V11_VERSION),
        *_published_batch_cards(V12_SEED_ITEMS, KNOWLEDGE_V12_VERSION),
        *_published_batch_cards(V13_SEED_ITEMS, KNOWLEDGE_V13_VERSION),
        *_published_batch_cards(V14_SEED_ITEMS, LATEST_PUBLISHED_KNOWLEDGE_VERSION),
    ]


def seed_versions() -> list[KnowledgeVersion]:
    v1_sources = [source for source in seed_sources() if source.id == "rae-ngle"]
    v1_nodes = [
        node
        for node in seed_nodes()
        if node.id in {"rae-ngle-complemento-directo", "rae-norma-estilo"}
    ]
    v1_evidence = [
        evidence
        for evidence in seed_evidence()
        if evidence.version == PUBLISHED_KNOWLEDGE_VERSION
    ]
    v1_claims = [
        claim
        for claim in seed_claims()
        if claim.version == PUBLISHED_KNOWLEDGE_VERSION
    ]
    v1_cards = [
        card
        for card in seed_cards()
        if card.version == PUBLISHED_KNOWLEDGE_VERSION
    ]
    v2_sources = [
        source for source in seed_sources() if source.id in {"rae-ngle", "rae-lese"}
    ]
    v2_nodes = [
        node
        for node in seed_nodes()
        if node.id
        in {
            "rae-norma-estilo",
            "manual-rasgos-escritura",
            "rae-ngle-complemento-directo",
            "rae-lese-dinamismo-frase",
        }
    ]
    v2_evidence = [
        evidence
        for evidence in seed_evidence()
        if evidence.version in {PUBLISHED_KNOWLEDGE_VERSION, KNOWLEDGE_V2_VERSION}
    ]
    v2_claims = [
        claim
        for claim in seed_claims()
        if claim.version in {PUBLISHED_KNOWLEDGE_VERSION, KNOWLEDGE_V2_VERSION}
    ]
    v2_cards = [
        card
        for card in seed_cards()
        if card.version in {PUBLISHED_KNOWLEDGE_VERSION, KNOWLEDGE_V2_VERSION}
    ]
    v3_sources = [
        source for source in seed_sources() if source.id in {"rae-ngle", "rae-lese", "rae-ole"}
    ]
    v3_nodes = [
        node
        for node in seed_nodes()
        if node.id
        in {
            "rae-norma-estilo",
            "manual-rasgos-escritura",
            "rae-ngle-complemento-directo",
            "rae-lese-dinamismo-frase",
            "rae-ole-acentuacion-grafica",
        }
    ]
    v3_evidence = [
        evidence
        for evidence in seed_evidence()
        if evidence.version
        in {PUBLISHED_KNOWLEDGE_VERSION, KNOWLEDGE_V2_VERSION, KNOWLEDGE_V3_VERSION}
    ]
    v3_claims = [
        claim
        for claim in seed_claims()
        if claim.version
        in {PUBLISHED_KNOWLEDGE_VERSION, KNOWLEDGE_V2_VERSION, KNOWLEDGE_V3_VERSION}
    ]
    v3_cards = [
        card
        for card in seed_cards()
        if card.version
        in {PUBLISHED_KNOWLEDGE_VERSION, KNOWLEDGE_V2_VERSION, KNOWLEDGE_V3_VERSION}
    ]
    v4_sources = [
        source
        for source in seed_sources()
        if source.id in {"rae-ngle", "rae-lese", "rae-ole", "rae-gtg"}
    ]
    v4_nodes = [
        node
        for node in seed_nodes()
        if node.id
        in {
            "rae-norma-estilo",
            "manual-rasgos-escritura",
            "rae-ngle-complemento-directo",
            "rae-lese-dinamismo-frase",
            "rae-ole-acentuacion-grafica",
            "rae-gtg-terminologia-gramatical",
        }
    ]
    v4_evidence = [
        evidence
        for evidence in seed_evidence()
        if evidence.version
        in {
            PUBLISHED_KNOWLEDGE_VERSION,
            KNOWLEDGE_V2_VERSION,
            KNOWLEDGE_V3_VERSION,
            KNOWLEDGE_V4_VERSION,
        }
    ]
    v4_claims = [
        claim
        for claim in seed_claims()
        if claim.version
        in {
            PUBLISHED_KNOWLEDGE_VERSION,
            KNOWLEDGE_V2_VERSION,
            KNOWLEDGE_V3_VERSION,
            KNOWLEDGE_V4_VERSION,
        }
    ]
    v4_cards = [
        card
        for card in seed_cards()
        if card.version
        in {
            PUBLISHED_KNOWLEDGE_VERSION,
            KNOWLEDGE_V2_VERSION,
            KNOWLEDGE_V3_VERSION,
            KNOWLEDGE_V4_VERSION,
        }
    ]
    v5_sources = [
        source
        for source in seed_sources()
        if source.id in {"rae-ngle", "rae-lese", "rae-ole", "rae-gtg", "rae-dle"}
    ]
    v5_nodes = [
        node
        for node in seed_nodes()
        if node.id
        in {
            "rae-norma-estilo",
            "manual-rasgos-escritura",
            "rae-ngle-complemento-directo",
            "rae-lese-dinamismo-frase",
            "rae-ole-acentuacion-grafica",
            "rae-gtg-terminologia-gramatical",
            "rae-dle-precision-lexica",
        }
    ]
    v5_evidence = [
        evidence
        for evidence in seed_evidence()
        if evidence.version
        in {
            PUBLISHED_KNOWLEDGE_VERSION,
            KNOWLEDGE_V2_VERSION,
            KNOWLEDGE_V3_VERSION,
            KNOWLEDGE_V4_VERSION,
            KNOWLEDGE_V5_VERSION,
        }
    ]
    v5_claims = [
        claim
        for claim in seed_claims()
        if claim.version
        in {
            PUBLISHED_KNOWLEDGE_VERSION,
            KNOWLEDGE_V2_VERSION,
            KNOWLEDGE_V3_VERSION,
            KNOWLEDGE_V4_VERSION,
            KNOWLEDGE_V5_VERSION,
        }
    ]
    v5_cards = [
        card
        for card in seed_cards()
        if card.version
        in {
            PUBLISHED_KNOWLEDGE_VERSION,
            KNOWLEDGE_V2_VERSION,
            KNOWLEDGE_V3_VERSION,
            KNOWLEDGE_V4_VERSION,
            KNOWLEDGE_V5_VERSION,
        }
    ]
    v6_source_ids = {
        "rae-ngle",
        "rae-lese",
        "rae-ole",
        "rae-gtg",
        "rae-dle",
        *{item["source_id"] for item in V6_SEED_ITEMS},
    }
    v6_sources = [source for source in seed_sources() if source.id in v6_source_ids]
    v6_node_ids = {
        "rae-norma-estilo",
        "manual-rasgos-escritura",
        "rae-ngle-complemento-directo",
        "rae-lese-dinamismo-frase",
        "rae-ole-acentuacion-grafica",
        "rae-gtg-terminologia-gramatical",
        "rae-dle-precision-lexica",
        *{item["node_id"] for item in V6_SEED_ITEMS},
    }
    v6_nodes = [node for node in seed_nodes() if node.id in v6_node_ids]
    published_chain = {
        PUBLISHED_KNOWLEDGE_VERSION,
        KNOWLEDGE_V2_VERSION,
        KNOWLEDGE_V3_VERSION,
        KNOWLEDGE_V4_VERSION,
        KNOWLEDGE_V5_VERSION,
        KNOWLEDGE_V6_VERSION,
    }
    v6_evidence = [evidence for evidence in seed_evidence() if evidence.version in published_chain]
    v6_claims = [claim for claim in seed_claims() if claim.version in published_chain]
    v6_cards = [card for card in seed_cards() if card.version in published_chain]
    v7_source_ids = v6_source_ids
    v7_sources = [source for source in seed_sources() if source.id in v7_source_ids]
    v7_node_ids = {*v6_node_ids, *{item["node_id"] for item in V7_SEED_ITEMS}}
    v7_nodes = [node for node in seed_nodes() if node.id in v7_node_ids]
    v7_chain = {*published_chain, KNOWLEDGE_V7_VERSION}
    v7_evidence = [evidence for evidence in seed_evidence() if evidence.version in v7_chain]
    v7_claims = [claim for claim in seed_claims() if claim.version in v7_chain]
    v7_cards = [card for card in seed_cards() if card.version in v7_chain]
    v8_chain = {*v7_chain, KNOWLEDGE_V8_VERSION}
    v8_sources = v7_sources
    v8_node_ids = {*v7_node_ids, *{item["node_id"] for item in V8_SEED_ITEMS}}
    v8_nodes = [node for node in seed_nodes() if node.id in v8_node_ids]
    v8_evidence = [evidence for evidence in seed_evidence() if evidence.version in v8_chain]
    v8_claims = [claim for claim in seed_claims() if claim.version in v8_chain]
    v8_cards = [card for card in seed_cards() if card.version in v8_chain]
    v9_chain = {*v8_chain, KNOWLEDGE_V9_VERSION}
    v9_sources = v7_sources
    v9_node_ids = {*v8_node_ids, *{item["node_id"] for item in V9_SEED_ITEMS}}
    v9_nodes = [node for node in seed_nodes() if node.id in v9_node_ids]
    v9_evidence = [evidence for evidence in seed_evidence() if evidence.version in v9_chain]
    v9_claims = [claim for claim in seed_claims() if claim.version in v9_chain]
    v9_cards = [card for card in seed_cards() if card.version in v9_chain]
    v10_chain = {*v9_chain, KNOWLEDGE_V10_VERSION}
    v10_sources = v7_sources
    v10_node_ids = {*v9_node_ids, *{item["node_id"] for item in V10_SEED_ITEMS}}
    v10_nodes = [node for node in seed_nodes() if node.id in v10_node_ids]
    v10_evidence = [evidence for evidence in seed_evidence() if evidence.version in v10_chain]
    v10_claims = [claim for claim in seed_claims() if claim.version in v10_chain]
    v10_cards = [card for card in seed_cards() if card.version in v10_chain]
    v11_chain = {*v10_chain, KNOWLEDGE_V11_VERSION}
    v11_sources = [
        source
        for source in seed_sources()
        if source.id in {*v7_source_ids, *{item["source_id"] for item in V11_SEED_ITEMS}}
    ]
    v11_node_ids = {*v10_node_ids, *{item["node_id"] for item in V11_SEED_ITEMS}}
    v11_nodes = [node for node in seed_nodes() if node.id in v11_node_ids]
    v11_evidence = [evidence for evidence in seed_evidence() if evidence.version in v11_chain]
    v11_claims = [claim for claim in seed_claims() if claim.version in v11_chain]
    v11_cards = [card for card in seed_cards() if card.version in v11_chain]
    v12_chain = {*v11_chain, KNOWLEDGE_V12_VERSION}
    v12_sources = [
        source
        for source in seed_sources()
        if source.id in {*v7_source_ids, *{item["source_id"] for item in V11_SEED_ITEMS}, *{item["source_id"] for item in V12_SEED_ITEMS}}
    ]
    v12_node_ids = {*v11_node_ids, *{item["node_id"] for item in V12_SEED_ITEMS}}
    v12_nodes = [node for node in seed_nodes() if node.id in v12_node_ids]
    v12_evidence = [evidence for evidence in seed_evidence() if evidence.version in v12_chain]
    v12_claims = [claim for claim in seed_claims() if claim.version in v12_chain]
    v12_cards = [card for card in seed_cards() if card.version in v12_chain]
    v13_chain = {*v12_chain, KNOWLEDGE_V13_VERSION}
    v13_sources = [
        source
        for source in seed_sources()
        if source.id in {
            *v7_source_ids,
            *{item["source_id"] for item in V11_SEED_ITEMS},
            *{item["source_id"] for item in V12_SEED_ITEMS},
            *{item["source_id"] for item in V13_SEED_ITEMS},
        }
    ]
    v13_node_ids = {*v12_node_ids, *{item["node_id"] for item in V13_SEED_ITEMS}}
    v13_nodes = [node for node in seed_nodes() if node.id in v13_node_ids]
    v13_evidence = [evidence for evidence in seed_evidence() if evidence.version in v13_chain]
    v13_claims = [claim for claim in seed_claims() if claim.version in v13_chain]
    v13_cards = [card for card in seed_cards() if card.version in v13_chain]
    latest_chain = {*v13_chain, LATEST_PUBLISHED_KNOWLEDGE_VERSION}
    latest_sources = [
        source
        for source in seed_sources()
        if source.id in {
            *v7_source_ids,
            *{item["source_id"] for item in V11_SEED_ITEMS},
            *{item["source_id"] for item in V12_SEED_ITEMS},
            *{item["source_id"] for item in V13_SEED_ITEMS},
            *{item["source_id"] for item in V14_SEED_ITEMS},
        }
    ]
    latest_node_ids = {*v13_node_ids, *{item["node_id"] for item in V14_SEED_ITEMS}}
    latest_nodes = [node for node in seed_nodes() if node.id in latest_node_ids]
    latest_evidence = [evidence for evidence in seed_evidence() if evidence.version in latest_chain]
    latest_claims = [claim for claim in seed_claims() if claim.version in latest_chain]
    latest_cards = [card for card in seed_cards() if card.version in latest_chain]
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
        ),
        KnowledgeVersion(
            id=PUBLISHED_KNOWLEDGE_VERSION,
            status="published",
            published_at=KNOWLEDGE_V1_PUBLISHED_AT,
            source_count=len(v1_sources),
            node_count=len(v1_nodes),
            evidence_count=len(v1_evidence),
            claim_count=len(v1_claims),
            card_count=len(v1_cards),
        ),
        KnowledgeVersion(
            id=KNOWLEDGE_V2_VERSION,
            status="published",
            published_at=KNOWLEDGE_V2_PUBLISHED_AT,
            source_count=len(v2_sources),
            node_count=len(v2_nodes),
            evidence_count=len(v2_evidence),
            claim_count=len(v2_claims),
            card_count=len(v2_cards),
        ),
        KnowledgeVersion(
            id=KNOWLEDGE_V3_VERSION,
            status="published",
            published_at=KNOWLEDGE_V3_PUBLISHED_AT,
            source_count=len(v3_sources),
            node_count=len(v3_nodes),
            evidence_count=len(v3_evidence),
            claim_count=len(v3_claims),
            card_count=len(v3_cards),
        ),
        KnowledgeVersion(
            id=KNOWLEDGE_V4_VERSION,
            status="published",
            published_at=KNOWLEDGE_V4_PUBLISHED_AT,
            source_count=len(v4_sources),
            node_count=len(v4_nodes),
            evidence_count=len(v4_evidence),
            claim_count=len(v4_claims),
            card_count=len(v4_cards),
        ),
        KnowledgeVersion(
            id=KNOWLEDGE_V5_VERSION,
            status="published",
            published_at=KNOWLEDGE_V5_PUBLISHED_AT,
            source_count=len(v5_sources),
            node_count=len(v5_nodes),
            evidence_count=len(v5_evidence),
            claim_count=len(v5_claims),
            card_count=len(v5_cards),
        ),
        KnowledgeVersion(
            id=KNOWLEDGE_V6_VERSION,
            status="published",
            published_at=KNOWLEDGE_V6_PUBLISHED_AT,
            source_count=len(v6_sources),
            node_count=len(v6_nodes),
            evidence_count=len(v6_evidence),
            claim_count=len(v6_claims),
            card_count=len(v6_cards),
        ),
        KnowledgeVersion(
            id=KNOWLEDGE_V7_VERSION,
            status="published",
            published_at=KNOWLEDGE_V7_PUBLISHED_AT,
            source_count=len(v7_sources),
            node_count=len(v7_nodes),
            evidence_count=len(v7_evidence),
            claim_count=len(v7_claims),
            card_count=len(v7_cards),
        ),
        KnowledgeVersion(
            id=KNOWLEDGE_V8_VERSION,
            status="published",
            published_at=KNOWLEDGE_V8_PUBLISHED_AT,
            source_count=len(v8_sources),
            node_count=len(v8_nodes),
            evidence_count=len(v8_evidence),
            claim_count=len(v8_claims),
            card_count=len(v8_cards),
        ),
        KnowledgeVersion(
            id=KNOWLEDGE_V9_VERSION,
            status="published",
            published_at=KNOWLEDGE_V9_PUBLISHED_AT,
            source_count=len(v9_sources),
            node_count=len(v9_nodes),
            evidence_count=len(v9_evidence),
            claim_count=len(v9_claims),
            card_count=len(v9_cards),
        ),
        KnowledgeVersion(
            id=KNOWLEDGE_V10_VERSION,
            status="published",
            published_at=KNOWLEDGE_V10_PUBLISHED_AT,
            source_count=len(v10_sources),
            node_count=len(v10_nodes),
            evidence_count=len(v10_evidence),
            claim_count=len(v10_claims),
            card_count=len(v10_cards),
        ),
        KnowledgeVersion(
            id=KNOWLEDGE_V11_VERSION,
            status="published",
            published_at=KNOWLEDGE_V11_PUBLISHED_AT,
            source_count=len(v11_sources),
            node_count=len(v11_nodes),
            evidence_count=len(v11_evidence),
            claim_count=len(v11_claims),
            card_count=len(v11_cards),
        ),
        KnowledgeVersion(
            id=KNOWLEDGE_V12_VERSION,
            status="published",
            published_at=KNOWLEDGE_V12_PUBLISHED_AT,
            source_count=len(v12_sources),
            node_count=len(v12_nodes),
            evidence_count=len(v12_evidence),
            claim_count=len(v12_claims),
            card_count=len(v12_cards),
        ),
        KnowledgeVersion(
            id=KNOWLEDGE_V13_VERSION,
            status="published",
            published_at=KNOWLEDGE_V13_PUBLISHED_AT,
            source_count=len(v13_sources),
            node_count=len(v13_nodes),
            evidence_count=len(v13_evidence),
            claim_count=len(v13_claims),
            card_count=len(v13_cards),
        ),
        KnowledgeVersion(
            id=LATEST_PUBLISHED_KNOWLEDGE_VERSION,
            status="published",
            published_at=KNOWLEDGE_V14_PUBLISHED_AT,
            source_count=len(latest_sources),
            node_count=len(latest_nodes),
            evidence_count=len(latest_evidence),
            claim_count=len(latest_claims),
            card_count=len(latest_cards),
        ),
    ]


def _object_revision(object_type: str, object_id: str, after: dict) -> KnowledgeObjectRevision:
    return KnowledgeObjectRevision(
        id=f"rev-{object_type}-{object_id}-r1",
        object_type=object_type,
        object_id=object_id,
        revision_number=1,
        object_version=f"{object_id}@r1",
        knowledge_version=KNOWLEDGE_VERSION,
        status="active",
        change_type="created",
        author="minicerebro-seed",
        reason="registro inicial segun contrato de versionado V1",
        previous_revision=None,
        replaces_object_id=None,
        replaced_by_object_id=None,
        before={},
        after=after,
        created_at=RELATION_UPDATED_AT,
        updated_at=RELATION_UPDATED_AT,
    )


def seed_object_revisions() -> list[KnowledgeObjectRevision]:
    revisions: list[KnowledgeObjectRevision] = []
    revisions.extend(
        _object_revision(
            "source",
            source.id,
            {
                "catalog_id": source.catalog_id,
                "name": source.name,
                "status": source.status,
                "authority_level": source.authority_level,
            },
        )
        for source in seed_sources()
    )
    revisions.extend(
        _object_revision(
            "source_edition",
            edition.id,
            {
                "source_id": edition.source_id,
                "label": edition.label,
                "acquisition_status": edition.acquisition_status,
                "validation_status": edition.validation_status,
            },
        )
        for edition in seed_source_editions()
    )
    revisions.extend(
        _object_revision(
            "node",
            node.id,
            {
                "canonical_name": node.canonical_name,
                "node_type": node.node_type,
                "primary_branch": node.primary_branch,
                "status": node.status,
                "relations": [relation.id for relation in seed_node_relations() if relation.source_node_id == node.id],
            },
        )
        for node in seed_nodes()
    )
    revisions.extend(
        _object_revision(
            "relation",
            relation.id,
            {
                "source_entity_type": relation.source_entity_type,
                "source_entity_id": relation.source_entity_id,
                "relation_type": relation.relation_type,
                "target_entity_type": relation.target_entity_type,
                "target_entity_id": relation.target_entity_id,
                "status": relation.status,
            },
        )
        for relation in seed_relations()
    )
    revisions.extend(
        _object_revision(
            "evidence",
            evidence.id,
            {
                "source_id": evidence.source_id,
                "source_edition_id": evidence.source_edition_id,
                "node_id": evidence.node_id,
                "status": evidence.status,
                "locator": evidence.locator,
            },
        )
        for evidence in seed_evidence()
    )
    revisions.extend(
        _object_revision(
            "claim",
            claim.id,
            {
                "statement": claim.statement,
                "claim_type": claim.claim_type,
                "node_id": claim.node_id,
                "status": claim.status,
                "evidence_id": claim.evidence_id,
            },
        )
        for claim in seed_claims()
    )
    revisions.extend(
        _object_revision(
            "knowledge_card",
            card.id,
            {
                "name": card.name,
                "card_type": card.card_type,
                "version": card.version,
                "payload_keys": sorted(card.payload),
            },
        )
        for card in seed_cards()
    )
    revisions.extend(
        [
            _object_revision(
                "tree",
                "knowledge-tree-v0",
                {"root": "knowledge-v0", "node_ids": [node.id for node in seed_nodes()]},
            ),
            _object_revision(
                "ontology",
                "knowledge-ontology-v0",
                {
                    "node_types": sorted({node.node_type for node in seed_nodes()}),
                    "relation_types": sorted({relation.relation_type for relation in seed_relations()}),
                },
            ),
            _object_revision(
                "schema",
                "knowledge-schema-v0",
                {"versioned_object_types": VERSIONED_OBJECT_TYPES},
            ),
            _object_revision(
                "knowledge_version",
                KNOWLEDGE_VERSION,
                {
                    "status": "seed",
                    "published_at": "not-published",
                    "immutable_after_publication": True,
                },
            ),
        ]
    )
    return revisions


QUERY_TYPE_KEYWORDS = {
    "definition": ["que es", "define", "definicion", "significa"],
    "normative_correction": ["correct", "coma", "debe", "norma", "lleva"],
    "descriptive_explanation": ["por que", "ambigua", "explica"],
    "writing_recommendation": ["claro", "mejor", "escritura", "parrafo", "estilo"],
    "literary_analysis": ["narrador", "focalizacion", "metafora", "literario"],
    "terminological": ["termino", "mismo", "alias", "equivale"],
    "historical": ["histor", "cambio", "version", "antes"],
    "evidence": ["fuente", "evidencia", "sostiene", "justifica"],
    "comparative": ["diferencia", "compara", "frente", "versus"],
}

DOMAIN_KEYWORDS = {
    "LENGUA": ["lengua", "norma", "coma", "gramatica", "lexica", "lexico"],
    "ESCRITURA": ["escritura", "estilo", "claro", "sobriedad", "dinamismo", "parrafo"],
    "TEORIA LITERARIA": ["narrador", "focalizacion", "metafora", "comparacion"],
    "GLOSARIO": ["termino", "definicion", "significa"],
}

QUERY_TYPE_RELATION_PRIORITIES = {
    "definition": ["define", "equivale_a", "es_parte_de"],
    "normative_correction": ["contradice", "requiere", "describe"],
    "writing_recommendation": ["usa", "ejemplifica", "relacionado_con", "depende_de"],
    "literary_analysis": ["aparece_en", "estudiado_por", "usa"],
    "comparative": ["compara_con", "contradice", "equivale_a", "relacionado_con"],
}


def resolve_knowledge_version(version: str) -> str:
    if version == "latest":
        return LATEST_KNOWLEDGE_VERSION
    return version


def _normalize_query(query: str) -> str:
    decomposed = normalize("NFKD", query.lower())
    without_accents = "".join(char for char in decomposed if category(char) != "Mn")
    return " ".join(without_accents.split())


def _query_terms(normalized_query: str) -> set[str]:
    return {term for term in normalized_query.split() if len(term) > 2}


def _detect_query_types(normalized_query: str) -> list[str]:
    detected = [
        query_type
        for query_type, keywords in QUERY_TYPE_KEYWORDS.items()
        if any(keyword in normalized_query for keyword in keywords)
    ]
    return detected or ["writing_recommendation"]


def _detect_domains(normalized_query: str, matched_nodes: list[KnowledgeNode]) -> list[str]:
    detected = [
        domain
        for domain, keywords in DOMAIN_KEYWORDS.items()
        if any(keyword in normalized_query for keyword in keywords)
    ]
    for node in matched_nodes:
        branch = node.primary_branch.upper()
        if "LENGUA" in branch and "LENGUA" not in detected:
            detected.append("LENGUA")
        if "ESCRITURA" in branch and "ESCRITURA" not in detected:
            detected.append("ESCRITURA")
    return detected or ["ESCRITURA"]


def _text_match_score(terms: set[str], haystack: str) -> float:
    if not terms:
        return 0.0
    normalized_haystack = _normalize_query(haystack)
    return sum(1 for term in terms if term in normalized_haystack) / len(terms)


def query_contract() -> KnowledgeQueryContract:
    return KnowledgeQueryContract(
        meaning=(
            "Una consulta es una peticion de lectura contra conocimiento estable; "
            "no modifica perfil, preferencias ni conocimiento publicado."
        ),
        query_unit="texto breve del usuario + version solicitada + limite de recuperacion",
        lifecycle=QUERY_LIFECYCLE,
        interpretation_fields=[
            "query",
            "normalized_query",
            "requested_version",
            "resolved_version",
            "query_type",
            "domain",
        ],
        restriction_fields=[
            "resolved_version",
            "limit",
            "max_cards",
            "profile_mutation_allowed",
            "stable_knowledge_mutation_allowed",
            "generation_allowed",
        ],
        context_fields=[
            "profile_influence",
            "stable_knowledge_mutation",
            "retrieval_unit",
            "ranking_policy",
        ],
        out_of_scope=QUERY_OUT_OF_SCOPE,
        allowed_version_values=[
            KNOWLEDGE_VERSION,
            PUBLISHED_KNOWLEDGE_VERSION,
            KNOWLEDGE_V2_VERSION,
            KNOWLEDGE_V3_VERSION,
            KNOWLEDGE_V4_VERSION,
            KNOWLEDGE_V5_VERSION,
            KNOWLEDGE_V6_VERSION,
            KNOWLEDGE_V7_VERSION,
            KNOWLEDGE_V8_VERSION,
            KNOWLEDGE_V9_VERSION,
            KNOWLEDGE_V10_VERSION,
            KNOWLEDGE_V11_VERSION,
            KNOWLEDGE_V12_VERSION,
            KNOWLEDGE_V13_VERSION,
            LATEST_PUBLISHED_KNOWLEDGE_VERSION,
            "latest",
        ],
        profile_boundary=(
            "El perfil puede influir solo en presentacion u ordenacion futura; "
            "no altera la interpretacion contractual ni el conocimiento estable."
        ),
        retrieval_boundary=(
            "La consulta prepara una solicitud de recuperacion; la recuperacion decide "
            "fichas, claims, evidencias, fuentes y relaciones devueltas."
        ),
        generation_boundary="La generacion no forma parte de la consulta ni se ejecuta en este contrato.",
        audit_fields=[
            "query_length",
            "limit",
            "requested_version",
            "resolved_version",
            "query_type",
            "domain",
        ],
        acceptance_criteria=[
            "normaliza la consulta sin perder el texto original",
            "resuelve latest a una version existente",
            "declara tipo y dominio antes de recuperar",
            "rechaza versiones inexistentes",
            "no registra ni expone la consulta cruda en auditoria",
            "no muta perfil ni conocimiento estable",
        ],
    )


def interpret_knowledge_query(payload: KnowledgeQueryInput) -> KnowledgeQueryInterpretation:
    requested_version = payload.version
    resolved_version = resolve_knowledge_version(payload.version)
    normalized_query = _normalize_query(payload.query)
    query_types = _detect_query_types(normalized_query)
    domains = _detect_domains(normalized_query, [])
    restrictions = {
        "requested_version": requested_version,
        "resolved_version": resolved_version,
        "limit": payload.limit,
        "max_cards": payload.limit,
        "profile_mutation_allowed": False,
        "stable_knowledge_mutation_allowed": False,
        "generation_allowed": False,
        "retrieval_required": True,
    }
    context = {
        "profile_influence": "presentation_only",
        "stable_knowledge_mutation": False,
        "retrieval_unit": "knowledge_card",
        "ranking_policy": "deterministic_traceable",
    }
    return KnowledgeQueryInterpretation(
        query=payload.query,
        normalized_query=normalized_query,
        requested_version=requested_version,
        resolved_version=resolved_version,
        query_type=query_types,
        domain=domains,
        restrictions=restrictions,
        context=context,
        retrieval_request={
            "required": True,
            "version": resolved_version,
            "limit": payload.limit,
            "query_terms": sorted(_query_terms(normalized_query)),
            "query_type": query_types,
            "domain": domains,
        },
        audit_payload={
            "query_length": len(payload.query),
            "limit": payload.limit,
            "requested_version": requested_version,
            "resolved_version": resolved_version,
            "query_type": query_types,
            "domain": domains,
        },
    )


def query_knowledge(
    payload: KnowledgeQueryInput,
    sources: list[KnowledgeSource] | None = None,
    nodes: list[KnowledgeNode] | None = None,
    cards: list[KnowledgeCard] | None = None,
    claims: list[KnowledgeClaim] | None = None,
    evidence: list[KnowledgeEvidenceItem] | None = None,
) -> KnowledgeQueryResult:
    interpretation = interpret_knowledge_query(payload)
    requested_version = interpretation.requested_version
    resolved_version = interpretation.resolved_version
    normalized_query = interpretation.normalized_query
    terms = _query_terms(normalized_query)
    query_types = interpretation.query_type
    sources = sources if sources is not None else seed_sources()
    nodes = nodes if nodes is not None else seed_nodes()
    cards = cards if cards is not None else seed_cards()
    claims = claims if claims is not None else seed_claims()
    evidence = evidence if evidence is not None else seed_evidence()
    allowed_statuses = {"published"}
    published_claims = [claim for claim in claims if claim.status in allowed_statuses]
    published_evidence = [item for item in evidence if item.status in allowed_statuses]
    sources_by_id = {source.id: source for source in sources}
    nodes_by_id = {node.id: node for node in nodes}
    evidence_by_id = {item.id: item for item in published_evidence}
    claims_by_card: dict[str, list[KnowledgeClaim]] = {}
    for claim in published_claims:
        claims_by_card.setdefault(claim.card_id, []).append(claim)

    relations = seed_relations()
    relations_by_source = {
        (relation.source_entity_type, relation.source_entity_id): relation
        for relation in relations
        if relation.status in allowed_statuses and relation.confidence >= 0.5
    }
    candidate_nodes: set[str] = set()
    discarded_claims: list[str] = []
    ranking: list[dict] = []

    def evaluate_card(card: KnowledgeCard) -> tuple[float, dict, list[str], list[str]]:
        linked_claims = claims_by_card.get(card.id, [])
        linked_evidence = [
            evidence_by_id[claim.evidence_id]
            for claim in linked_claims
            if claim.evidence_id in evidence_by_id
        ]
        if not linked_claims or not linked_evidence:
            return 0.0, {"concept_match": 0.0}, [], []
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
        )
        concept_match = _text_match_score(terms, haystack)
        domain_match = 1.0 if any(term in haystack.lower() for term in ("lexic", "estilo", "escrit")) else 0.5
        scope_match = 1.0 if any(claim.scope.get("language") == "es" for claim in linked_claims) else 0.0
        context_match = 1.0 if any("general" in item.context for item in linked_evidence) else 0.5
        authority_score = (
            max((source.authority_level for source in linked_sources), default=0) / 5
        )
        evidence_score = max((item.confidence for item in linked_evidence), default=0)
        claim_confidence = max((claim.confidence for claim in linked_claims), default=0)
        relation_score = 0.0
        relation_paths: list[str] = []
        for item in linked_evidence:
            relation = relations_by_source.get(("node", item.node_id))
            if relation is None:
                continue
            relation_score = max(relation_score, relation.confidence * relation.weight)
            relation_paths.append(relation.id)
        status_score = 1.0
        version_score = 1.0
        factors = {
            "concept_match": round(concept_match, 3),
            "domain_match": round(domain_match, 3),
            "scope_match": round(scope_match, 3),
            "context_match": round(context_match, 3),
            "authority_score": round(authority_score, 3),
            "evidence_score": round(evidence_score, 3),
            "claim_confidence": round(claim_confidence, 3),
            "relation_score": round(relation_score, 3),
            "version_score": round(version_score, 3),
            "status_score": round(status_score, 3),
        }
        score = round(
            concept_match
            + domain_match
            + scope_match
            + authority_score
            + evidence_score
            + context_match
            + relation_score
            + version_score
            + status_score,
            3,
        )
        reasons = []
        if concept_match:
            reasons.append("coincidencia conceptual con consulta normalizada")
        if linked_claims:
            reasons.append("contiene claims aplicables")
        if linked_evidence:
            reasons.append("conserva evidencias trazables")
        if linked_sources:
            reasons.append("identifica fuentes de respaldo")
        if relation_paths:
            reasons.append("expansion controlada por relaciones")
        return score, factors, reasons, relation_paths

    evaluated_cards = []
    for card in cards:
        score, factors, reasons, relation_paths = evaluate_card(card)
        if score <= 0 or factors["concept_match"] <= 0:
            continue
        evaluated_cards.append((card, score, factors, reasons, relation_paths))
        ranking.append(
            {
                "card_id": card.id,
                "final_score": score,
                "factors": factors,
                "reasons": reasons,
            }
        )

    ranked_evaluations = sorted(evaluated_cards, key=lambda item: item[1], reverse=True)[
        : payload.limit
    ]
    ranked_cards = [item[0] for item in ranked_evaluations]
    card_ids = {card.id for card in ranked_cards}
    matched_claims = [
        claim
        for claim in claims
        if claim.card_id in card_ids
        and claim.status in allowed_statuses
        and claim.confidence >= 0.4
    ]
    for claim in claims:
        if claim.card_id in card_ids and claim not in matched_claims:
            discarded_claims.append(claim.id)
    evidence_ids = {claim.evidence_id for claim in matched_claims}
    matched_evidence = [
        item
        for item in evidence
        if item.id in evidence_ids
        and item.status in allowed_statuses
        and item.confidence >= 0.4
    ]
    matched_source_ids = {item.source_id for item in matched_evidence}
    matched_sources = [source for source in sources if source.id in matched_source_ids]
    matched_nodes = [
        nodes_by_id[item.node_id] for item in matched_evidence if item.node_id in nodes_by_id
    ]
    for node in matched_nodes:
        candidate_nodes.add(node.id)
    matched_relation_ids = {
        relation_path
        for _, _, _, _, relation_paths in ranked_evaluations
        for relation_path in relation_paths[:20]
    }
    relations_followed = [
        relation for relation in relations if relation.id in matched_relation_ids
    ][:20]
    domains = _detect_domains(normalized_query, matched_nodes)
    retrieved_cards = []
    for card, score, _, reasons, relation_paths in ranked_evaluations:
        card_claims = [claim for claim in matched_claims if claim.card_id == card.id]
        card_evidence = [
            item for item in matched_evidence if item.id in {claim.evidence_id for claim in card_claims}
        ]
        node_id = card_claims[0].node_id if card_claims else ""
        source_ids = sorted({item.source_id for item in card_evidence})
        retrieved_cards.append(
            RetrievedKnowledgeCard(
                card_id=card.id,
                node_id=node_id,
                name=card.name,
                summary=card.definition,
                score=score,
                reasons=reasons,
                claim_ids=[claim.id for claim in card_claims],
                source_ids=source_ids,
                relation_paths=relation_paths[:2],
                confidence=card.confidence,
            )
        )
    status = "ok"
    if not ranked_cards:
        status = "no_match"
    elif not matched_evidence:
        status = "insufficient_evidence"
    elif any(claim.confidence < 0.6 for claim in matched_claims):
        status = "low_confidence"
    return KnowledgeQueryResult(
        query=payload.query,
        version=resolved_version,
        requested_version=requested_version,
        resolved_version=resolved_version,
        query_type=query_types,
        domain=domains,
        context={
            **interpretation.context,
            "normalized_query": normalized_query,
            "primary_domain": domains[0] if domains else None,
        },
        status=status,
        card_count=len(ranked_cards),
        claim_count=len(matched_claims),
        evidence_count=len(matched_evidence),
        cards=ranked_cards,
        claims=matched_claims,
        evidence=matched_evidence,
        sources=matched_sources,
        relations_followed=relations_followed,
        contradictions=[],
        ranking=ranking[: payload.limit],
        retrieved_cards=retrieved_cards,
        retrieval_trace={
            "original_query_preserved_in_response": True,
            "normalized_query": normalized_query,
            "requested_version": requested_version,
            "resolved_version": resolved_version,
            "filters": {
                "claim_status": sorted(allowed_statuses),
                "minimum_claim_confidence": 0.4,
                "minimum_evidence_confidence": 0.4,
                "max_relation_depth": 2,
                "max_nodes": 20,
            },
            "candidate_nodes": sorted(candidate_nodes),
            "candidate_cards": [item[0].id for item in evaluated_cards],
            "selected_cards": [card.id for card in ranked_cards],
            "selected_claims": [claim.id for claim in matched_claims],
            "selected_evidence": [item.id for item in matched_evidence],
            "discarded_claims": discarded_claims,
            "relations_followed": [relation.id for relation in relations_followed],
            "ranking_factors": [item["factors"] for item in ranking[: payload.limit]],
            "thresholds": {
                "supporting_claim_min_confidence": 0.4,
                "published_claim_min_confidence": 0.6,
                "primary_answer_min_confidence": 0.75,
            },
            "timings": {
                "interpretation_time": 0,
                "retrieval_time": 0,
            },
        },
        limits={
            "max_cards": payload.limit,
            "max_claims": len(matched_claims),
            "max_evidence": len(matched_evidence),
            "max_relation_depth": 2,
            "max_total_tokens": 0,
            "timeout": 0,
        },
        generated_at=datetime.now(UTC).isoformat(),
    )
