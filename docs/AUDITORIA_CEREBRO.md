# MINICEREBRO V1
## Auditoría técnica de reutilización de Cerebro

**Versión:** 1.0  
**Repositorio auditado:** `editorial-brain-main.zip`  
**Proyecto origen:** Editorial Brain / Cerebro  
**Objetivo:** determinar qué piezas pueden reutilizarse, adaptarse, tomarse como referencia o descartarse para Minicerebro V1.  
**Documentos de referencia:**
- `CONTRATO_FUNCIONAL_MINICEREBRO_V1.md`
- `ARQUITECTURA_TECNICA_MINICEREBRO_V1.md`

---

# 0. Resultado ejecutivo

Cerebro contiene varias piezas útiles, pero **no debe reutilizarse como base completa de Minicerebro**.

La conclusión general es:

```text
REUTILIZAR DIRECTAMENTE............. 4 piezas
ADAPTAR............................. 8 piezas
USAR COMO REFERENCIA................ 7 piezas
DESCARTAR PARA MINICEREBRO.......... 9 piezas
```

La reutilización debe hacerse por extracción selectiva.

```text
CEREBRO
   │
   ├── extraer utilidades limpias
   ├── desacoplar módulos
   ├── sustituir el modelo de memoria
   ├── sustituir el modelo de reglas
   └── eliminar integraciones ajenas
        │
        ▼
MINICEREBRO
```

**Decisión arquitectónica:**

> Cerebro es cantera. No es cimiento.

---

# 1. Estado técnico observado

## 1.1 Stack actual

```text
Node.js >= 24
Express 5
PostgreSQL
pgvector
pdf-parse
JavaScript ESM
Frontend estático
Railway
n8n opcional
```

## 1.2 Tamaño aproximado

```text
server.mjs........................ 3.950 líneas
src/rag/harvesting.mjs............ 600 líneas
src/rag/pgvector.mjs.............. 633 líneas
src/rules/lifecycle.mjs........... 171 líneas
resto de módulos principales...... 256 líneas
tests............................. 240 líneas
```

El sistema está funcionalmente concentrado en `server.mjs`.

## 1.3 Pruebas ejecutadas

Resultado:

```text
7 pruebas
7 correctas
0 fallos
```

Cobertura real observada:

- contexto de generación;
- ciclo de vida de reglas;
- deduplicación de reglas;
- promoción por evidencias;
- caducidad;
- una parte del harvesting.

No hay cobertura suficiente para:

- API completa;
- PostgreSQL;
- pgvector;
- recuperación;
- generación;
- feedback;
- integración con Flow;
- seguridad;
- consolidación;
- mantenimiento.

---

# 2. Mapa real del proyecto

```text
editorial-brain-main/
├── server.mjs
├── src/
│   ├── rag/
│   │   ├── assessment.mjs
│   │   ├── harvesting.mjs
│   │   ├── local-assessment.mjs
│   │   ├── memory-store.mjs
│   │   └── pgvector.mjs
│   └── rules/
│       ├── generation-context.mjs
│       └── lifecycle.mjs
├── scripts/
│   ├── activate-rag.mjs
│   ├── bulk-research-ingest.mjs
│   ├── production-rag-workflow.mjs
│   ├── purge-paused-topic.mjs
│   └── setup-rag-db.mjs
├── public/
│   ├── app.js
│   ├── js/
│   └── styles.css
└── test/
```

---

# 3. Hallazgos principales

## 3.1 Punto fuerte

Cerebro ya resuelve parcialmente:

- normalización;
- valoración de materiales;
- chunking;
- embeddings;
- pgvector;
- recuperación semántica;
- memoria persistida;
- reglas con confianza;
- evidencias;
- caducidad;
- consolidación;
- feedback de texto;
- autenticación básica;
- fuentes externas.

## 3.2 Punto débil

Gran parte de la lógica está mezclada en `server.mjs`.

Eso provoca:

- alto acoplamiento;
- difícil reutilización;
- difícil prueba;
- difícil sustitución de dominio;
- riesgo de arrastrar Flow, Ads, memoria general y automatización;
- dificultad para distinguir conocimiento, preferencia y reglas.

## 3.3 Diferencia conceptual crítica

Cerebro usa este modelo:

```text
Entrada
→ Documento
→ Regla
→ Principio
→ Identidad
```

Minicerebro necesita este:

```text
Fuente académica
→ Ficha de conocimiento estable

Prompt del usuario
→ Preferencia explícita

Corrección
→ Evidencia de scoring

Scoring
→ Perfil editable
```

No son el mismo sistema.

---

# 4. Matriz general de reutilización

| Componente | Clasificación | Decisión |
|---|---:|---|
| `src/rag/assessment.mjs` | ADAPTAR | Buena normalización de valoración, pero esquema demasiado editorial/general |
| `src/rag/local-assessment.mjs` | REFERENCIA | Fallback útil, pero heurística insuficiente para conocimiento literario |
| `src/rag/memory-store.mjs` | ADAPTAR | Patrón transaccional útil; el modelo `app_state` JSONB no sirve como base principal |
| `src/rag/pgvector.mjs` | ADAPTAR | Reutilizable para embeddings y búsqueda; debe cambiar el esquema |
| `src/rag/harvesting.mjs` | REFERENCIA | Infraestructura de cosecha útil; fuentes actuales no son las prioritarias |
| `src/rules/lifecycle.mjs` | REFERENCIA | Buena idea de evidencia/confianza; ciclo automático incompatible |
| `src/rules/generation-context.mjs` | REUTILIZAR | Pequeño, limpio y desacoplado; necesita nueva semántica de estados |
| Normalizadores de texto | REUTILIZAR | Útiles tal cual con pruebas adicionales |
| Deduplicación de strings | REUTILIZAR | Útil tal cual |
| Normalización de confianza | REUTILIZAR | Útil como utilidad, no como política |
| Registro de fuentes actual | ADAPTAR | Debe convertirse en registro académico/especialistas |
| Chunking | ADAPTAR | Buen punto de partida; faltan tipos literarios y referencias |
| Embeddings | ADAPTAR | Válidos; deben separar conocimiento y preferencias |
| Recuperación semántica | ADAPTAR | Útil; necesita filtros por dominio, autoridad y ficha |
| Procedencia | ADAPTAR | Existe de forma parcial; debe hacerse obligatoria |
| Feedback original/editado | ADAPTAR | Es la pieza más cercana al comparador, pero hoy es demasiado simple |
| Consolidación automática | DESCARTAR | Incompatible con conocimiento congelado y aprobación explícita |
| Investigación automática continua | DESCARTAR | Contraria a la base estable de V1 |
| Ads Brain | DESCARTAR | Fuera de alcance |
| Flow Console | DESCARTAR | Fuera de alcance |
| Señales comerciales | DESCARTAR | Fuera de alcance |
| Memoria temporal/permanente general | DESCARTAR | Modelo incorrecto para Minicerebro |
| World model implícito | DESCARTAR | Fuera de alcance |
| Exploración generalista | DESCARTAR | Debe sustituirse por recuperación especializada |
| UI actual | REFERENCIA | Puede inspirar navegación, no el producto final |

---

# 5. Piezas reutilizables directamente

## 5.1 Canonicalización de texto

Funciones observadas:

```text
canonicalText
canonicalKey
uniqueStrings
```

### Valor

- eliminan variaciones superficiales;
- normalizan acentos;
- reducen duplicados;
- producen claves estables;
- son pequeñas;
- no dependen de Flow ni de memoria.

### Decisión

```text
REUTILIZAR
```

### Acción

Extraer a:

```text
backend/app/core/text_normalization.mjs
```

Añadir pruebas para:

- signos literarios;
- comillas;
- guiones;
- nombres propios;
- castellano antiguo;
- poemas;
- versos;
- abreviaturas;
- Unicode.

---

## 5.2 Generación de contexto filtrado

Archivo:

```text
src/rules/generation-context.mjs
```

### Valor

Es un módulo:

- pequeño;
- puro;
- sin I/O;
- probado;
- fácil de sustituir.

### Problema

Usa estados:

```text
observation
learning
permanent
```

Minicerebro necesita:

```text
draft
confirmed
manual
contextual
temporary
disabled
```

### Decisión

```text
REUTILIZAR ESTRUCTURA
```

No reutilizar la semántica actual.

---

## 5.3 Utilidades de límites numéricos

Funciones equivalentes:

```text
clampWeight
clampConfidence
clampNumber
```

### Decisión

```text
REUTILIZAR
```

Mover a un módulo puro.

---

## 5.4 Comparación segura de secretos

Función:

```text
safeEqual
```

### Decisión

```text
REUTILIZAR
```

Solo como utilidad de seguridad.

---

# 6. Piezas que deben adaptarse

## 6.1 Assessment / valoración de materiales

Archivo:

```text
src/rag/assessment.mjs
```

### Lo que hace bien

- valida tipos;
- limita tamaños;
- normaliza arrays;
- extrae valoración de varias formas de respuesta;
- detecta respuestas sin contenido útil;
- separa tags, preferencias y pistas de prompt.

### Lo que no encaja

Tipos actuales:

```text
ejemplo_copy
spec
nota
prompt_previo
```

Minicerebro necesita:

```text
normative_rule
grammar_concept
style_principle
author_trait
critical_interpretation
literary_example
user_preference
favorite_phrase
correction_evidence
```

### Decisión

```text
ADAPTAR
```

### Reutilización estimada

```text
Código aprovechable: 35–45%
Idea aprovechable:   80%
```

---

## 6.2 Fallback local de valoración

Archivo:

```text
src/rag/local-assessment.mjs
```

### Lo que hace bien

- evita bloquear la ingesta;
- clasifica de forma local;
- detecta material técnico o estilístico;
- produce una salida coherente.

### Problema

Se basa en:

- conteo de palabras;
- regex;
- términos frecuentes;
- heurística ligera.

No distingue:

- teoría literaria;
- interpretación crítica;
- autor;
- obra;
- ejemplo;
- principio;
- norma;
- estilo.

### Decisión

```text
USAR COMO REFERENCIA
```

No debe ser el clasificador final.

---

## 6.3 Persistencia transaccional de memoria

Archivo:

```text
src/rag/memory-store.mjs
```

### Lo que hace bien

- usa transacciones;
- bloquea con `FOR UPDATE`;
- garantiza existencia de estado;
- evita condiciones de carrera;
- separa lectura y escritura.

### Problema principal

Guarda el estado general en:

```text
app_state.value JSONB
```

Eso no es suficiente para:

- miles de fichas;
- procedencia;
- scoring;
- estadísticas;
- versionado;
- consultas parciales;
- auditoría granular.

### Decisión

```text
ADAPTAR PATRÓN, NO ESQUEMA
```

### Acción

Reutilizar:

- patrón de bloqueo;
- transacción;
- API de repositorio.

Descartar:

- objeto gigante `rag_memory`;
- estado global único.

---

## 6.4 PostgreSQL y pgvector

Archivo:

```text
src/rag/pgvector.mjs
```

### Lo que hace bien

- instala extensión vector;
- instala pgcrypto;
- crea esquema;
- valida dimensiones;
- almacena documentos;
- almacena chunks;
- realiza búsquedas vectoriales;
- gestiona borrado y archivado;
- usa metadatos.

### Lo que debe cambiar

Esquema actual:

```text
documents
document_chunks
app_state
```

Minicerebro necesita:

```text
sources
documents
knowledge_cards
card_evidence
knowledge_relations
preferences
score_variables
profile_scores
score_evidence
texts
text_versions
text_comparisons
feedback_events
knowledge_versions
```

### Decisión

```text
ADAPTAR
```

### Reutilización estimada

```text
Infraestructura de conexión......... alta
Gestión de embeddings............... alta
Esquema............................. baja
Búsqueda semántica.................. media
Metadatos........................... media
```

---

## 6.5 Chunking

El proyecto ya tiene:

- por párrafos;
- por secciones;
- documento completo;
- chunks;
- descripción + OCR.

### Valor

Es una buena base operativa.

### Necesidades nuevas

Añadir:

```text
por poema
por estrofa
por escena
por capítulo
por epígrafe
por ejemplo crítico
por tesis/argumento
por ficha de autor
por definición
por excepción
```

También debe conservar:

- obra;
- autor;
- edición;
- página;
- capítulo;
- verso;
- contexto.

### Decisión

```text
ADAPTAR
```

---

## 6.6 Registro de fuentes

Actualmente las fuentes están orientadas a:

- Hacker News;
- GitHub;
- Reddit;
- Indie Hackers;
- Quora.

### Valor

Existe una abstracción de fuentes y cosechadores.

### Problema

Las fuentes prioritarias de Minicerebro son otras:

```text
RAE
ASALE
repositorios universitarios
Dialnet
JSTOR o equivalentes autorizados
Google Scholar como índice
Biblioteca Virtual Miguel de Cervantes
ediciones críticas
libros
artículos
tesis
especialistas
```

### Decisión

```text
ADAPTAR ARQUITECTURA
DESCARTAR LISTA ACTUAL COMO BASE
```

---

## 6.7 Recuperación y scoring de relevancia

Funciones observadas:

```text
scoreDocument
prioritizeEntitiesForQuery
attentionHeadsForItem
queryBrain
exploreBrain
```

### Valor

- ya existe selección por consulta;
- hay señales temporales;
- hay ponderación;
- hay búsqueda textual y semántica;
- existen entidades priorizadas.

### Problema

La relevancia actual mezcla:

- recencia;
- uso;
- clase de memoria;
- proyectos;
- Ads;
- identidad;
- señales operativas.

Minicerebro necesita:

```text
tipo de ficha
autoridad de fuente
versión
autor
obra
rasgo
contexto
confianza
relación
preferencia activa
```

### Decisión

```text
ADAPTAR
```

No copiar la función de scoring actual.

---

## 6.8 Feedback original/editado

Funciones observadas:

```text
feedbackTextStats
deriveFeedbackRules
deriveFeedbackRule
```

### Valor

Es la pieza más próxima a:

- comparador;
- aprendizaje por correcciones;
- generación de reglas.

### Limitación

El análisis actual parece centrado en:

- longitud;
- diferencias básicas;
- derivación de reglas textuales.

Minicerebro necesita:

- diff léxico;
- diff sintáctico;
- ritmo;
- tono;
- estructura;
- semántica;
- ideas;
- variables;
- peso;
- contexto;
- confianza;
- consistencia.

### Decisión

```text
ADAPTAR
```

### Reutilización estimada

```text
Idea:              muy alta
Código directo:    bajo
```

---

# 7. Piezas que solo sirven como referencia

## 7.1 Ciclo de vida de reglas

Archivo:

```text
src/rules/lifecycle.mjs
```

### Lo bueno

- evidencias;
- confianza;
- etapas;
- fusión;
- deduplicación;
- expiración;
- promoción.

### Lo incompatible

Promoción automática:

```text
observation
→ learning
→ permanent
```

Por cantidad de evidencias o confianza.

En Minicerebro esto no puede ocurrir sin control porque:

- una preferencia no se vuelve permanente por repetición ciega;
- un estado temporal puede producir varias correcciones iguales;
- el usuario puede editar manualmente;
- el conocimiento académico no debe evolucionar por feedback.

### Decisión

```text
REFERENCIA
```

Reutilizar conceptos, no el ciclo.

---

## 7.2 Consolidación de documentos y reglas

Funciones observadas:

```text
documentPatternCandidates
crystallizeDocumentPattern
consolidationReport
```

### Valor

La detección de patrones y duplicados es útil.

### Riesgo

La consolidación automática arrastra la filosofía generalista de Cerebro.

### Decisión

```text
REFERENCIA
```

Solo usar para:

- detectar duplicados;
- detectar conflictos;
- proponer fusiones.

Nunca consolidar automáticamente.

---

## 7.3 Mantenimiento

Funciones observadas:

```text
maintenanceReport
vectorConsistencyReport
```

### Valor

Útiles para:

- huérfanos;
- duplicados;
- inconsistencias;
- chunks sin documento;
- documentos sin vector.

### Decisión

```text
REFERENCIA FUERTE
```

Conviene reimplementar un módulo de mantenimiento específico.

---

## 7.4 Harvesting

Archivo:

```text
src/rag/harvesting.mjs
```

### Valor

- adaptadores por fuente;
- errores parciales;
- limpieza;
- normalización;
- triage;
- concurrencia;
- fallback.

### Problema

Está orientado a investigación web general y tendencias.

### Decisión

```text
REFERENCIA
```

El patrón es útil; las fuentes no.

---

## 7.5 UI actual

Vistas observadas:

```text
ads
explore
learn
memories
```

### Valor

- navegación modular;
- estado cliente;
- API separada;
- componentes simples.

### Problema

El producto es otro.

### Decisión

```text
REFERENCIA VISUAL Y ESTRUCTURAL
```

No reutilizar pantallas.

---

## 7.6 Automatización por intervalos

Función:

```text
scheduleRecurringJob
```

### Valor

Código reutilizable en abstracto.

### Problema

Minicerebro V1 no necesita investigación automática continua.

### Decisión

```text
REFERENCIA
```

---

## 7.7 Esquema de scripts operativos

Scripts observados:

```text
setup-rag-db
activate-rag
bulk-research-ingest
production-rag-workflow
purge-paused-topic
```

### Valor

Buena separación de tareas operativas.

### Decisión

```text
REFERENCIA
```

Crear scripts nuevos específicos:

```text
setup-db
ingest-knowledge-source
validate-knowledge-version
publish-knowledge-version
rebuild-embeddings
audit-profile
```

---

# 8. Piezas a descartar

## 8.1 Ads Brain

Fuera de alcance.

```text
DESCARTAR
```

---

## 8.2 Flow Console

Toda lógica de envío de:

- campañas;
- consejos;
- calendario;
- acciones;
- tendencias.

```text
DESCARTAR
```

---

## 8.3 Señales comerciales y reputacionales

No forman parte del criterio de escritura.

```text
DESCARTAR
```

---

## 8.4 Investigación automática periódica

Minicerebro requiere base estable y versionada.

```text
DESCARTAR
```

La investigación será:

- deliberada;
- por lote;
- validada;
- publicada en versión.

---

## 8.5 Memoria temporal / semipermanente / permanente

Modelo actual:

```text
temporary
semi-permanent
permanent
```

No sirve como núcleo.

Minicerebro necesita:

```text
knowledge_versioned
preference_confirmed
preference_contextual
evidence_temporary
manual_override
```

```text
DESCARTAR
```

---

## 8.6 Cristalización input → identity

Modelo actual:

```text
input
candidate
document
rule
principle
identity
```

Incompatible con la separación de dominios.

```text
DESCARTAR
```

---

## 8.7 Aprendizaje silencioso

La arquitectura funcional exige revisión.

```text
DESCARTAR
```

---

## 8.8 Exploración generalista

El módulo de exploración mezcla:

- personas;
- proyectos;
- memoria;
- noticias;
- investigación externa.

```text
DESCARTAR
```

Sustituir por recuperación especializada.

---

## 8.9 Monolito `server.mjs`

No debe copiarse.

```text
DESCARTAR COMO ESTRUCTURA
```

Se extraerán funciones concretas.

---

# 9. Riesgos técnicos observados

## 9.1 Monolito

`server.mjs` concentra cerca de 4.000 líneas.

Riesgos:

- difícil mantenimiento;
- pruebas incompletas;
- dependencias circulares funcionales;
- reutilización costosa;
- fallos con gran radio de impacto.

### Acción

No ampliar Cerebro para convertirlo en Minicerebro.

Crear repositorio o raíz independiente.

---

## 9.2 Estado global en JSONB

`app_state` almacena `rag_memory` como objeto grande.

Riesgos:

- bloqueo de todo el estado;
- escrituras completas;
- consultas ineficientes;
- difícil trazabilidad;
- difícil migración;
- difícil estadística.

### Acción

Usar tablas normalizadas.

---

## 9.3 Reglas automáticas demasiado generales

Las reglas mezclan:

- estilo;
- identidad;
- operación;
- contenido;
- marketing;
- memoria.

### Acción

No migrar reglas existentes.

---

## 9.4 Confianza no equivalente a confianza estadística

La confianza actual es útil como señal operativa, pero no representa necesariamente:

- consistencia;
- cobertura;
- estabilidad;
- contradicción;
- tamaño de muestra.

### Acción

Crear métricas separadas.

---

## 9.5 Pruebas insuficientes

Aunque las pruebas actuales pasan, la cobertura es limitada.

### Acción

No considerar reutilizable ningún módulo con I/O sin pruebas nuevas.

---

## 9.6 Dependencia de n8n

Algunas rutas dependen de webhooks externos.

### Acción

Minicerebro no debe necesitar n8n para sus funciones nucleares.

n8n podrá usarse para ingestión auxiliar, nunca como motor obligatorio.

---

## 9.7 Dependencia de modelos concretos

Se observan prompts y referencias a proveedores concretos.

### Acción

Crear interfaz:

```text
LLMProvider
EmbeddingProvider
```

Evitar lógica de negocio incrustada en prompts de un proveedor.

---

# 10. Arquitectura de extracción recomendada

No hacer fork completo.

Crear una carpeta temporal:

```text
migration/
├── text-normalization/
├── pgvector-reference/
├── ingestion-reference/
├── feedback-reference/
├── maintenance-reference/
└── source-registry-reference/
```

Proceso:

```text
1. Copiar solo la pieza candidata.
2. Eliminar dependencias de server.mjs.
3. Añadir contrato explícito.
4. Añadir pruebas.
5. Renombrar al dominio Minicerebro.
6. Integrar.
7. Borrar la copia temporal.
```

---

# 11. Módulos nuevos de Minicerebro

```text
src/
├── knowledge/
│   ├── source-registry
│   ├── document-ingestion
│   ├── card-extraction
│   ├── evidence
│   ├── relations
│   ├── validation
│   ├── retrieval
│   └── versioning
├── preferences/
│   ├── interpreter
│   ├── confirmation
│   └── contradictions
├── scoring/
│   ├── variables
│   ├── calculator
│   ├── confidence
│   ├── consistency
│   ├── context
│   └── overrides
├── generation/
│   ├── context-builder
│   ├── orchestrator
│   └── providers
├── comparison/
│   ├── lexical
│   ├── syntactic
│   ├── semantic
│   ├── structural
│   └── adequacy
└── feedback/
    ├── proposal
    ├── approval
    └── event-log
```

---

# 12. Orden de reutilización

## Fase A — Extraer utilidades seguras

```text
canonicalText
canonicalKey
uniqueStrings
clampNumber
safeEqual
```

## Fase B — Rehacer persistencia

Usar como referencia:

```text
memory-store
pgvector
setup-rag-db
```

Pero crear esquema nuevo.

## Fase C — Adaptar valoración

Usar como referencia:

```text
assessment
local-assessment
chunking
```

## Fase D — Adaptar recuperación

Usar:

```text
vector search
metadata filters
query scoring
```

Sin memoria temporal ni Ads.

## Fase E — Rehacer scoring

Inspirarse en:

```text
confidence
evidenceCount
lifecycle
feedback
```

No copiar promoción automática.

## Fase F — Rehacer comparador

Tomar como semilla:

```text
feedbackTextStats
deriveFeedbackRules
```

Crear análisis multidimensional nuevo.

---

# 13. Matriz detallada de decisión

## REUTILIZAR

```text
canonicalText
canonicalKey
uniqueStrings
clampNumber / clampConfidence como utilidades
safeEqual
estructura pura de generationContext
```

## ADAPTAR

```text
assessment
memory-store
pgvector
chunking
source registry
retrieval
feedback original/editado
maintenance checks
```

## REFERENCIA

```text
local-assessment
harvesting
rule lifecycle
consolidation
UI modular
scripts operativos
scheduler
```

## DESCARTAR

```text
Ads Brain
Flow dispatch
señales comerciales
investigación periódica
memoria por retención
cristalización general
aprendizaje silencioso
exploración generalista
server.mjs como base
```

---

# 14. Estimación de reutilización real

```text
Código total reutilizable directamente......... 5–10%
Código adaptable............................... 15–25%
Ideas y patrones reutilizables................. 40–55%
Arquitectura completa reutilizable............. 0%
Modelo de datos reutilizable................... 10–15%
Frontend reutilizable.......................... 5–10%
```

Esto no significa que Cerebro sea inútil.

Significa que ya ha resuelto problemas valiosos, pero para otro contrato.

---

# 15. Decisión final

Minicerebro debe crearse como aplicación independiente.

```text
NO:
editorial-brain/
└── añadir minicerebro dentro

SÍ:
minicerebro/
├── conocimiento especializado
├── preferencias
├── scoring
├── generación
├── comparación
└── feedback
```

Cerebro seguirá alimentando Flow Console.

Minicerebro no dependerá de Cerebro en producción.

Podrá reutilizar código extraído y desacoplado, pero no consultar su memoria general.

---

# 16. Condiciones para considerar una pieza reciclada

Una pieza solo podrá marcarse como reutilizada cuando:

1. no importe `server.mjs`;
2. no dependa de Flow Console;
3. no dependa de Ads;
4. no dependa del modelo general de memoria;
5. tenga interfaz explícita;
6. tenga pruebas;
7. use el esquema de Minicerebro;
8. conserve trazabilidad;
9. respete la aprobación del usuario;
10. pueda sustituirse sin romper el sistema.

---

# 17. Resultado de la auditoría

```text
CONTRATO FUNCIONAL........ COMPLETO
ARQUITECTURA TÉCNICA...... COMPLETA
AUDITORÍA DE CEREBRO...... COMPLETA

Decisión:
Crear Minicerebro limpio.

Reciclar:
utilidades, patrones de persistencia,
pgvector, chunking, valoración,
recuperación y semillas de feedback.

No reciclar:
memoria general, cristalización,
automatizaciones, Ads, Flow,
investigación continua y monolito.
```

---

**FIN DE LA AUDITORÍA TÉCNICA V1.0**
