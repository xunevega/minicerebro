# MINICEREBRO V1
## Arquitectura técnica cerrada

**Versión:** 1.0  
**Estado:** Cerrada para implementación  
**Documento dependiente de:** `docs/CONTRATO_FUNCIONAL.md`
**Dominio:** Escritura en lengua española  
**Objetivo:** Implementar una aplicación especializada que combine conocimiento estable sobre lengua y literatura con un perfil editable y trazable de preferencias de escritura.

---

# 0. Principios técnicos

1. La base de conocimiento y el perfil del usuario son sistemas distintos.
2. Ningún ajuste del usuario modifica conocimiento académico.
3. Ninguna actualización del scoring se aplica sin trazabilidad.
4. Toda inferencia debe conservar:
   - origen;
   - confianza;
   - contexto;
   - fecha;
   - versión.
5. La arquitectura debe permitir auditar cada resultado.
6. El sistema debe poder funcionar aunque el módulo de aprendizaje esté desactivado.
7. La base de conocimiento debe ser versionable y reemplazable.
8. Los perfiles deben ser exportables.
9. La recuperación de conocimiento debe ser explícita y verificable.
10. Minicerebro V1 no es un framework generalista.

---

# 1. Arquitectura general

```text
┌──────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│                                                              │
│ Conocimiento · Preferencias · Resumen · Scoring · Editor    │
│ Laboratorio · Comparador · Estadísticas                     │
└──────────────────────────────┬───────────────────────────────┘
                               │ HTTPS / JSON
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                         API LAYER                            │
│                                                              │
│ Auth · Profiles · Preferences · Generation · Comparison     │
│ Knowledge · Statistics · Feedback · Versions                │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                      APPLICATION CORE                        │
│                                                              │
│ Preference Interpreter                                      │
│ Scoring Engine                                              │
│ Context Resolver                                            │
│ Knowledge Retriever                                         │
│ Generation Orchestrator                                     │
│ Change Comparator                                           │
│ Feedback Processor                                          │
│ Consistency Analyzer                                        │
└───────────────┬───────────────────────────────┬──────────────┘
                │                               │
                ▼                               ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│ KNOWLEDGE SUBSYSTEM         │   │ USER PROFILE SUBSYSTEM      │
│                             │   │                             │
│ Sources                     │   │ Preferences                 │
│ Documents                   │   │ Variables                   │
│ Cards                       │   │ Scores                      │
│ Relations                   │   │ Manual overrides            │
│ Provenance                  │   │ Context profiles            │
│ Versions                    │   │ Corrections                 │
│ Embeddings                  │   │ Statistics                  │
└───────────────┬─────────────┘   └───────────────┬─────────────┘
                │                                 │
                └────────────────┬────────────────┘
                                 ▼
┌──────────────────────────────────────────────────────────────┐
│                         DATA LAYER                           │
│ PostgreSQL · pgvector · Object Storage · Event Log          │
└──────────────────────────────────────────────────────────────┘
```

---

# 2. Stack recomendada

## 2.1 Backend

- Python 3.12+
- FastAPI
- Pydantic v2
- SQLAlchemy 2
- Alembic
- PostgreSQL 16+
- pgvector
- Redis opcional para colas y caché
- Celery, Dramatiq o RQ para procesos largos
- pytest
- Ruff
- mypy

## 2.2 Frontend

- React
- TypeScript
- Vite
- TanStack Query
- Zustand o reducer local para estado de edición
- Monaco Editor o editor propio basado en textarea enriquecido
- ECharts, Recharts o Chart.js para estadísticas
- diff-match-patch o equivalente para visualización textual

## 2.3 Almacenamiento

- PostgreSQL:
  - conocimiento estructurado;
  - preferencias;
  - scoring;
  - relaciones;
  - estadísticas;
  - historial.
- pgvector:
  - recuperación semántica de fichas;
  - ejemplos;
  - fragmentos;
  - preferencias.
- Object storage:
  - documentos fuente;
  - archivos procesados;
  - exportaciones;
  - snapshots.
- Event log:
  - toda modificación del perfil;
  - toda aprobación;
  - toda reversión.

---

# 3. Dominios internos

```text
knowledge
preferences
scoring
generation
comparison
feedback
statistics
profiles
contexts
versions
audit
```

Cada dominio debe tener:

- modelos;
- servicios;
- repositorios;
- contratos de entrada/salida;
- pruebas;
- eventos.

---

# 4. Modelo de datos

## 4.1 Fuentes

```sql
sources
-------
id UUID PK
name TEXT
source_type TEXT
authority_level INTEGER
priority INTEGER
domain_tags JSONB
specialist_id UUID NULL
framework TEXT NULL
url TEXT NULL
metadata JSONB
status TEXT
created_at TIMESTAMP
updated_at TIMESTAMP
```

Tipos:

```text
normative
academic
primary
specialist
secondary
low_priority
```

---

## 4.2 Documentos

```sql
documents
---------
id UUID PK
source_id UUID FK
title TEXT
author TEXT
publication_year INTEGER NULL
language TEXT
content_hash TEXT
storage_path TEXT
processing_status TEXT
knowledge_version_id UUID FK
metadata JSONB
created_at TIMESTAMP
```

---

## 4.3 Fichas de conocimiento

```sql
knowledge_cards
---------------
id UUID PK
card_type TEXT
name TEXT
definition TEXT
payload JSONB
confidence NUMERIC(5,4)
knowledge_version_id UUID FK
status TEXT
created_at TIMESTAMP
updated_at TIMESTAMP
```

`payload` puede contener:

```json
{
  "effects": [],
  "signals": [],
  "risks": [],
  "exceptions": [],
  "contexts": [],
  "related_authors": [],
  "examples": [],
  "interpretations": []
}
```

---

## 4.4 Evidencias y procedencia

```sql
card_evidence
-------------
id UUID PK
card_id UUID FK
document_id UUID FK
source_id UUID FK
quote_start INTEGER NULL
quote_end INTEGER NULL
reference TEXT
interpretation TEXT
confidence NUMERIC(5,4)
created_at TIMESTAMP
```

---

## 4.5 Relaciones

```sql
knowledge_relations
-------------------
id UUID PK
source_card_id UUID FK
target_card_id UUID FK
relation_type TEXT
weight NUMERIC(5,4)
confidence NUMERIC(5,4)
metadata JSONB
```

Tipos mínimos:

```text
supports
contradicts
illustrates
derived_from
related_to
used_by_author
typical_of
exception_to
produces_effect
depends_on
```

---

## 4.6 Preferencias explícitas

```sql
preferences
-----------
id UUID PK
profile_id UUID FK
raw_input TEXT
input_type TEXT
context_id UUID NULL
status TEXT
interpretation JSONB
confirmed BOOLEAN
created_at TIMESTAMP
updated_at TIMESTAMP
```

Tipos:

```text
preference
rejection
limit
exception
example
favorite_phrase
author_reference
comparison
explained_correction
contextual_rule
criterion_change
```

---

## 4.7 Variables

```sql
score_variables
---------------
id UUID PK
key TEXT UNIQUE
group_name TEXT
display_name TEXT
description TEXT
min_value INTEGER DEFAULT 0
max_value INTEGER DEFAULT 1000
default_value INTEGER
metadata JSONB
```

---

## 4.8 Valor de variable por perfil

```sql
profile_scores
--------------
id UUID PK
profile_id UUID FK
variable_id UUID FK
context_id UUID NULL
calculated_value INTEGER
manual_override INTEGER NULL
effective_value INTEGER
confidence NUMERIC(5,4)
consistency NUMERIC(5,4)
coverage NUMERIC(5,4)
trend NUMERIC(7,4)
sample_count INTEGER
contradiction_count INTEGER
last_calculated_at TIMESTAMP
```

Regla:

```text
effective_value =
manual_override si existe
en otro caso calculated_value
```

---

## 4.9 Evidencias del scoring

```sql
score_evidence
--------------
id UUID PK
profile_score_id UUID FK
evidence_type TEXT
source_reference_id UUID
direction NUMERIC(7,4)
weight NUMERIC(7,4)
context_id UUID NULL
occurred_at TIMESTAMP
metadata JSONB
```

Tipos:

```text
prompt
confirmed_example
favorite_phrase
manual_adjustment
correction
variant_choice
explicit_rejection
confirmation
historical_pattern
```

---

## 4.10 Textos y versiones

```sql
texts
-----
id UUID PK
profile_id UUID FK
title TEXT
text_type TEXT
context_id UUID NULL
created_at TIMESTAMP

text_versions
-------------
id UUID PK
text_id UUID FK
version_number INTEGER
content TEXT
origin TEXT
generation_request JSONB
profile_snapshot_id UUID
created_at TIMESTAMP
```

Origen:

```text
user
generated
corrected
rewritten
accepted
```

---

## 4.11 Comparaciones

```sql
text_comparisons
----------------
id UUID PK
source_version_id UUID FK
target_version_id UUID FK
overall_change NUMERIC(5,2)
adequacy_score NUMERIC(5,2)
dimension_scores JSONB
semantic_change NUMERIC(5,2)
stylistic_change NUMERIC(5,2)
structural_change NUMERIC(5,2)
created_at TIMESTAMP
```

---

## 4.12 Eventos de feedback

```sql
feedback_events
---------------
id UUID PK
comparison_id UUID FK
profile_id UUID FK
proposal JSONB
decision TEXT
applied_changes JSONB
created_at TIMESTAMP
```

Decisiones:

```text
apply_all
apply_partial
review
reject
no_learning
mark_exception
mark_temporary
manual_override
```

---

# 5. Subsistema de conocimiento

## 5.1 Flujo de ingestión

```text
Fuente registrada
      ↓
Descarga / importación
      ↓
Normalización
      ↓
Segmentación
      ↓
Clasificación
      ↓
Extracción de conceptos
      ↓
Extracción de relaciones
      ↓
Generación de fichas
      ↓
Vinculación de evidencias
      ↓
Validación
      ↓
Publicación en versión
```

---

## 5.2 Contrato de extracción

El extractor debe producir:

```json
{
  "cards": [],
  "relations": [],
  "evidence": [],
  "uncertainties": [],
  "conflicts": [],
  "coverage": []
}
```

No debe publicar directamente.

Debe pasar por validación.

---

## 5.3 Validación

Validaciones mínimas:

- toda ficha tiene fuente;
- toda ficha tiene tipo;
- toda afirmación importante tiene evidencia;
- las citas o referencias existen;
- no se duplican conceptos equivalentes sin relación;
- las interpretaciones se distinguen de hechos normativos;
- las fuentes de baja prioridad no consolidan solas;
- los especialistas conservan su marco teórico;
- las contradicciones quedan registradas;
- la versión queda congelada tras publicación.

---

## 5.4 Recuperación

La recuperación debe combinar:

1. búsqueda estructurada;
2. filtrado por tipo;
3. relaciones;
4. búsqueda semántica;
5. prioridad de fuente;
6. contexto.

Ejemplo:

```text
Consulta:
“frases más cortas y dinámicas, sin tono telegráfico”

Recuperación:
- ficha frase breve;
- ficha dinamismo;
- ficha fragmentación;
- ficha variación rítmica;
- autores relevantes;
- riesgos;
- ejemplos;
- preferencias del usuario relacionadas.
```

---

# 6. Intérprete de preferencias

## 6.1 Entrada

```json
{
  "profile_id": "uuid",
  "text": "Quiero frases más cortas, pero no telegráficas.",
  "input_type": "preference",
  "context": "general"
}
```

## 6.2 Salida

```json
{
  "interpretation": {
    "summary": "Preferencia por frases más breves con variación y sin fragmentación excesiva.",
    "variables": [
      {
        "key": "sentence_length_short",
        "direction": 1,
        "strength": 0.55
      },
      {
        "key": "fragmentation",
        "direction": -1,
        "strength": 0.70
      },
      {
        "key": "length_variation",
        "direction": 1,
        "strength": 0.45
      }
    ],
    "contexts": ["general"],
    "limits": [],
    "contradictions": [],
    "knowledge_cards_used": []
  },
  "requires_confirmation": true
}
```

---

# 7. Motor de scoring

## 7.1 Modelo

Cada variable se calcula a partir de evidencias ponderadas.

```text
score = base
      + prompts
      + ejemplos confirmados
      + correcciones
      + elecciones
      + patrones
```

El resultado se normaliza a `0–1000`.

---

## 7.2 Pesos iniciales recomendados

```text
Prompt explícito confirmado........ 1.00
Ajuste manual...................... prioridad absoluta
Rechazo explicado.................. 0.95
Corrección manual.................. 0.80
Elección entre alternativas........ 0.60
Ejemplo confirmado................. 0.55
Aceptación sin cambios.............. 0.25
Patrón estadístico no confirmado.... 0.20
Evento aislado...................... 0.05
```

Estos pesos son configuración, no constantes incrustadas.

---

## 7.3 Decaimiento temporal

No se aplicará decaimiento a:

- ajustes manuales;
- preferencias explícitas confirmadas;
- límites;
- reglas contextuales.

Podrá aplicarse decaimiento a:

- correcciones aisladas;
- tendencias temporales;
- comportamiento reciente;
- patrones no confirmados.

---

## 7.4 Consistencia

La consistencia debe estimarse mediante:

- dispersión de evidencias;
- repetición;
- estabilidad temporal;
- diferencia entre contextos;
- contradicciones;
- tamaño de muestra.

Salida:

```text
0.00–0.25  muy baja
0.26–0.50  baja
0.51–0.70  media
0.71–0.85  alta
0.86–1.00  muy alta
```

---

## 7.5 Confianza

La confianza combina:

- número de muestras;
- consistencia;
- autoridad de la evidencia;
- confirmaciones;
- ausencia de contradicciones.

No debe confundirse con el valor de preferencia.

Ejemplo:

```text
Humor = 780
Confianza = 23%

Interpretación:
El valor es provisional.
```

---

## 7.6 Contexto

El score efectivo se resuelve así:

```text
manual_override_contextual
    ↓
calculated_contextual
    ↓
manual_override_general
    ↓
calculated_general
    ↓
default
```

---

# 8. Motor de generación

## 8.1 Construcción de contexto

La generación recibe:

```text
petición del usuario
+
tipo de texto
+
perfil contextual
+
variables efectivas
+
protecciones
+
fichas de conocimiento recuperadas
+
referencias parciales de autor
```

---

## 8.2 Prompt interno estructurado

```json
{
  "task": "generate",
  "language": "es",
  "text_type": "essay",
  "objective": "...",
  "constraints": [],
  "protected_elements": [],
  "style_variables": {},
  "author_traits": [],
  "knowledge_cards": [],
  "output_requirements": {}
}
```

---

## 8.3 Garantías

El motor debe:

- preservar los elementos protegidos;
- señalar cuando una preferencia entra en conflicto;
- no imitar autores de forma integral;
- aplicar rasgos concretos;
- registrar qué variables se utilizaron;
- guardar snapshot del perfil;
- generar varias opciones cuando la confianza sea baja.

---

# 9. Comparador de cambios

## 9.1 Capas de comparación

1. caracteres;
2. tokens;
3. palabras;
4. frases;
5. párrafos;
6. sintaxis;
7. semántica;
8. estructura;
9. estilo;
10. ideas.

---

## 9.2 Salida mínima

```json
{
  "overall_change": 57.0,
  "adequacy": 81.0,
  "dimensions": {
    "punctuation": 18.0,
    "lexical": 43.0,
    "syntactic": 64.0,
    "rhythm": 72.0,
    "tone": 35.0,
    "structure": 18.0,
    "ideas": 4.0
  },
  "affected_variables": [],
  "feedback_proposal": []
}
```

---

## 9.3 Adecuación

La adecuación se calcula a partir del cambio necesario, ponderado por importancia.

No debe ser:

```text
100 - porcentaje de caracteres cambiados
```

Debe diferenciar:

- cambios superficiales;
- cambios estilísticos;
- cambios estructurales;
- cambios semánticos.

---

# 10. Analizador de consistencia

## 10.1 Ventanas

- 7 días;
- 30 días;
- 90 días;
- histórico.

## 10.2 Clasificación

```text
stable
contextual
temporary_streak
noise
real_change
insufficient_data
```

## 10.3 Restricción

Nunca debe inferir estados psicológicos.

Solo puede describir patrones observables.

---

# 11. API

## 11.1 Conocimiento

```text
GET  /knowledge/status
GET  /knowledge/coverage
GET  /knowledge/versions
POST /knowledge/sources
POST /knowledge/rebuild
POST /knowledge/publish-version
```

## 11.2 Preferencias

```text
POST /preferences/interpret
POST /preferences
GET  /preferences
PATCH /preferences/{id}
DELETE /preferences/{id}
```

## 11.3 Perfil y scoring

```text
GET   /profiles/{id}
GET   /profiles/{id}/summary
GET   /profiles/{id}/scores
PATCH /profiles/{id}/scores/{variable}
POST  /profiles/{id}/recalculate
GET   /profiles/{id}/statistics
GET   /profiles/{id}/contradictions
```

## 11.4 Editor

```text
POST /generation
POST /correction
POST /rewrite
POST /variants
POST /continue
```

## 11.5 Comparación

```text
POST /comparisons
GET  /comparisons/{id}
POST /comparisons/{id}/feedback
```

## 11.6 Laboratorio

```text
POST /lab/simulate
POST /lab/compare
POST /lab/apply
```

---

# 12. Eventos

Eventos mínimos:

```text
knowledge.source_added
knowledge.version_published
preference.created
preference.confirmed
preference.rejected
score.recalculated
score.manual_override_set
score.manual_override_removed
text.generated
text.corrected
comparison.completed
feedback.proposed
feedback.applied
feedback.rejected
profile.snapshot_created
```

---

# 13. Auditoría y trazabilidad

Cada salida generada deberá poder reconstruirse con:

- versión de conocimiento;
- versión de perfil;
- valores efectivos;
- ajustes manuales;
- fichas recuperadas;
- referencias de autor;
- modelo utilizado;
- prompt interno;
- fecha;
- configuración.

---

# 14. Seguridad

- autenticación obligatoria;
- separación por usuario;
- cifrado en tránsito;
- cifrado de secretos;
- no registrar textos completos en logs técnicos;
- exportación de datos;
- eliminación de datos;
- snapshots reversibles;
- auditoría de acciones;
- perfiles privados por defecto.

---

# 15. Estructura de proyecto

```text
minicerebro/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── knowledge/
│   │   ├── preferences/
│   │   ├── scoring/
│   │   ├── generation/
│   │   ├── comparison/
│   │   ├── feedback/
│   │   ├── statistics/
│   │   ├── profiles/
│   │   ├── contexts/
│   │   ├── audit/
│   │   └── db/
│   ├── tests/
│   └── alembic/
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── features/
│   │   ├── services/
│   │   ├── state/
│   │   └── types/
├── knowledge/
│   ├── registry/
│   ├── sources/
│   ├── schemas/
│   ├── versions/
│   └── validation/
├── docs/
│   ├── CONTRATO_FUNCIONAL.md
│   ├── ARQUITECTURA_TECNICA.md
│   └── AUDITORIA_CEREBRO.md
└── docker-compose.yml
```

---

# 16. Pruebas

## 16.1 Unitarias

- cálculo de scoring;
- resolución de contexto;
- prioridad de ajuste manual;
- consistencia;
- confianza;
- comparación;
- versionado;
- interpretación de preferencias.

## 16.2 Integración

```text
prompt
→ interpretación
→ confirmación
→ scoring
→ generación
→ corrección
→ comparación
→ propuesta
→ aprobación
→ nuevo scoring
```

## 16.3 Regresión

Casos fijos:

- frases breves sin tono telegráfico;
- metáfora funcional;
- cierre no explicativo;
- diferencia entre ensayo y texto técnico;
- contradicción entre prompt y correcciones;
- racha temporal;
- ajuste manual que prevalece.

---

# 17. Observabilidad

Métricas:

- tiempo de interpretación;
- tiempo de generación;
- fichas recuperadas;
- porcentaje de adecuación;
- modificación media;
- variables dudosas;
- contradicciones;
- número de aprobaciones;
- número de rechazos;
- ratio de ajustes manuales;
- calidad de recuperación.

Logs:

- estructurados;
- sin textos sensibles;
- con correlation_id;
- con profile_id anonimizado;
- con versión de conocimiento.

---

# 18. Roadmap técnico de implementación

## Fase 1 — Esqueleto

- FastAPI;
- PostgreSQL;
- modelos;
- migraciones;
- perfiles;
- variables;
- scoring manual;
- frontend básico.

## Fase 2 — Preferencias

- interpretación;
- confirmación;
- fichas de preferencia;
- actualización de scoring;
- resumen humano.

## Fase 3 — Generación

- editor;
- perfiles contextuales;
- protecciones;
- variantes;
- snapshots.

## Fase 4 — Comparación

- diff;
- dimensiones;
- adecuación;
- propuesta de feedback.

## Fase 5 — Estadísticas

- confianza;
- consistencia;
- cobertura;
- tendencias;
- contradicciones.

## Fase 6 — Conocimiento

- registro de fuentes;
- ingestión;
- fichas;
- relaciones;
- versiones;
- validación.

## Fase 7 — Laboratorio

- simulación;
- A/B;
- aplicación selectiva.

---

# 19. Puntos para la auditoría de Cerebro

La auditoría deberá localizar, con evidencia de código:

```text
source_registry
document_ingestion
normalization
entity_extraction
knowledge_cards
relations
confidence
provenance
contradictions
versioning
semantic_retrieval
graph_validation
logging
importers
```

Cada componente se clasificará:

```text
REUTILIZAR
ADAPTAR
REFERENCIA
DESCARTAR
```

No se importará ningún módulo completo hasta verificar:

- dependencia con Flow Console;
- dependencia con memoria general;
- dependencia con world model;
- dependencia con señales;
- acoplamiento con entidades personales;
- esquema de datos;
- calidad de pruebas;
- reversibilidad;
- mantenibilidad.

---

# 20. Criterio de cierre técnico

La arquitectura se considera cerrada cuando:

- los límites coinciden con el contrato funcional;
- el modelo de datos permite trazabilidad completa;
- la base de conocimiento está separada del perfil;
- el scoring es editable;
- el ajuste manual prevalece;
- la consistencia temporal está contemplada;
- el comparador distingue cambio superficial y profundo;
- la auditoría de Cerebro puede ejecutarse sin redefinir el producto.

---

**FIN DE LA ARQUITECTURA TÉCNICA V1.0**
