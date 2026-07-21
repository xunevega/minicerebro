# MINICEREBRO V1  
## Contrato funcional cerrado

**Versión:** 1.0  
**Estado:** Cerrado para diseño y desarrollo  
**Dominio:** Escritura en lengua española  
**Tipo de producto:** Aplicación especializada  
**No es:** framework general, asistente universal, memoria personal ni extensión de Cerebro

---

# 0. Propósito

Minicerebro es una aplicación especializada en **comprender, generar, corregir y adaptar textos en lengua española según un modelo explícito, editable y verificable de preferencias de escritura**.

El sistema se apoya en dos bases separadas:

1. **Conocimiento estable sobre lengua, escritura, literatura, autores, estilos y técnicas.**
2. **Perfil dinámico de preferencias del usuario**, construido mediante:
   - prompts;
   - ejemplos;
   - frases favoritas;
   - correcciones;
   - elecciones entre alternativas;
   - ajustes manuales del scoring.

La aplicación debe explicar:

- qué sabe;
- qué cree que le gusta al usuario;
- con qué confianza lo cree;
- de dónde sale cada puntuación;
- qué ha cambiado en un texto;
- cuánto ha tenido que corregir el usuario;
- cuánto se aproxima el resultado generado al perfil aprendido.

---

# 1. Alcance cerrado de la versión 1

Minicerebro V1 trabaja exclusivamente con:

- lengua española;
- redacción;
- estilo;
- narrativa;
- ensayo;
- artículo;
- texto divulgativo;
- texto técnico;
- texto publicitario;
- diálogo;
- poesía como conocimiento de referencia;
- autores y movimientos literarios como fuentes de rasgos y recursos;
- generación, revisión y comparación de textos.

## 1.1 Fuera de alcance

Quedan expresamente fuera de V1:

- memoria personal general;
- correo;
- calendario;
- automatizaciones;
- navegación autónoma permanente;
- monitorización del sistema;
- publicación en redes;
- integración con Flow Console;
- integración funcional con MiBØ;
- gestión de proyectos;
- análisis psicológico del usuario;
- diagnóstico emocional;
- aprendizaje silencioso no revisable;
- modificación automática de la base académica;
- soporte para fotografía, música, pintura u otros dominios;
- imitación integral de autores;
- entrenamiento de modelos fundacionales;
- edición colaborativa multiusuario;
- marketplace de estilos.

---

# 2. Principios no negociables

## 2.1 Separación de conocimiento y preferencia

El sistema debe mantener completamente separadas:

### Base de conocimiento

Contiene información técnica, lingüística, literaria y estilística.

Características:

- estable;
- versionada;
- trazable;
- ampliable de forma deliberada;
- no se modifica por los textos del usuario;
- no se modifica por correcciones del usuario;
- no se modifica por scoring.

### Perfil de preferencias

Contiene el modelo de gustos del usuario.

Características:

- editable;
- contextual;
- puntuable;
- explicable;
- reversible;
- alimentado por prompts y correcciones;
- nunca modifica la base de conocimiento.

---

## 2.2 Ningún aprendizaje opaco

Toda modificación del perfil debe poder responder:

- qué cambió;
- por qué cambió;
- qué evidencia lo produjo;
- cuánto pesa esa evidencia;
- en qué contexto se aplica;
- con qué confianza se mantiene;
- cómo revertirlo.

No se permite:

- consolidar preferencias sin registro;
- alterar variables sin trazabilidad;
- sustituir un ajuste manual sin aviso;
- confundir una decisión aislada con una preferencia estable.

---

## 2.3 El ajuste manual tiene prioridad

Para cada variable deben existir, como mínimo:

- valor calculado;
- ajuste manual;
- valor efectivo.

Ejemplo:

```text
Dinamismo

Valor calculado: 742
Ajuste manual:   +68
Valor efectivo:  810
```

El usuario podrá eliminar el ajuste manual y recuperar el valor calculado.

---

## 2.4 El conocimiento no evoluciona automáticamente

La base de conocimiento solo cambia mediante:

- incorporación deliberada de fuentes;
- ampliación de cobertura;
- corrección de fichas;
- actualización versionada;
- intervención técnica o editorial autorizada.

Ejemplo:

```text
Base literaria v1.0
+ especialista Jesús G. Maestro
= Base literaria v1.1
```

No se permite que una corrección de estilo del usuario modifique una ficha sobre Cervantes, sintaxis o retórica.

---

# 3. Arquitectura funcional

```text
┌──────────────────────────────────────────────────────────────┐
│ 1. FUENTES Y CONOCIMIENTO                                   │
│ Aprende y estructura el conocimiento mínimo definido        │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. FICHAS INTERNAS                                          │
│ Convierte lo aprendido en unidades consultables             │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. ENTRADA DE PREFERENCIAS                                  │
│ Prompts, ejemplos, frases, referencias y matices             │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. SCORING Y PERFIL                                         │
│ Variables, pesos, confianza, consistencia y contexto         │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. GENERADOR Y CORRECTOR                                    │
│ Genera, corrige, reescribe y produce alternativas            │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ 6. COMPARADOR DE CAMBIOS                                    │
│ Mide modificaciones, adecuación y aprendizaje propuesto      │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ 7. RETROALIMENTACIÓN CONTROLADA                             │
│ Aplicar, revisar, matizar, descartar o no aprender           │
└──────────────────────────────────────────────────────────────┘
```

---

# 4. Módulo 1 — Fuentes y conocimiento

## 4.1 Objetivo

Construir una base profunda, estable y consultable que permita al sistema saber:

- dónde acudir;
- qué tipo de conocimiento necesita;
- qué fuente tiene prioridad;
- qué rasgo técnico o literario debe recuperar;
- qué ejemplos apoyan una afirmación;
- qué interpretaciones son discutidas.

La interfaz no debe presentar este módulo como una biblioteca de uso cotidiano.

Debe presentarlo como una **ficha de acreditación del conocimiento disponible**.

---

## 4.2 Conocimiento mínimo obligatorio

### Lengua española

- gramática;
- sintaxis;
- ortografía;
- morfología;
- semántica;
- pragmática;
- puntuación;
- léxico;
- cohesión;
- coherencia;
- registro;
- norma y uso;
- errores frecuentes;
- excepciones relevantes.

### Escritura

- claridad;
- concisión;
- precisión;
- ritmo;
- voz;
- tono;
- estructura;
- progresión;
- apertura;
- cierre;
- descripción;
- diálogo;
- argumentación;
- exposición;
- narración;
- edición;
- reescritura.

### Teoría y recursos

- retórica;
- estilística;
- narratología;
- figuras literarias;
- elipsis;
- ironía;
- paradoja;
- metáfora;
- comparación;
- repetición;
- enumeración;
- focalización;
- distancia narrativa;
- punto de vista;
- musicalidad;
- tensión;
- densidad;
- concreción;
- abstracción.

### Géneros y ámbitos

- narrativa;
- ensayo;
- artículo;
- periodismo;
- divulgación;
- escritura técnica;
- publicidad;
- guion;
- poesía;
- correspondencia;
- discurso.

### Literatura y autores

- historia de la literatura;
- movimientos;
- escuelas;
- autores;
- principios de estilo;
- procedimientos;
- evolución;
- influencias;
- debates críticos;
- especialistas concretos;
- fragmentos demostrativos.

---

## 4.3 Jerarquía de fuentes

El sistema debe clasificar las fuentes, como mínimo, en:

1. **Normativas**
   - RAE;
   - ASALE;
   - DLE;
   - DPD;
   - Ortografía;
   - Gramática.

2. **Académicas**
   - artículos;
   - monografías;
   - tesis;
   - ediciones críticas;
   - publicaciones universitarias.

3. **Especialistas**
   - investigadores centrados en un autor;
   - críticos con corpus amplio;
   - expertos registrados por dominio.

4. **Fuentes primarias**
   - obras;
   - prólogos;
   - cartas;
   - entrevistas;
   - textos del propio autor.

5. **Fuentes secundarias**
   - conferencias;
   - debates;
   - entrevistas a especialistas;
   - análisis divulgativos con respaldo.

6. **Fuentes de baja prioridad**
   - foros;
   - blogs;
   - comentarios;
   - debates no académicos.

Las fuentes de baja prioridad pueden aportar hipótesis, nunca consolidar por sí solas una ficha.

---

## 4.4 Registro de especialistas

Añadir un especialista no debe requerir modificar la lógica del sistema.

Debe existir un registro de configuración equivalente a:

```yaml
id: jesus_g_maestro
name: Jesús G. Maestro
domains:
  - teoría literaria
  - Cervantes
  - literatura española
priority: high
source_types:
  - libros
  - artículos
  - conferencias
frameworks:
  - materialismo filosófico
```

La aplicación debe conservar el marco interpretativo de cada especialista y no convertirlo automáticamente en verdad universal.

---

## 4.5 Ficha visible de conocimiento

La pantalla de conocimiento mostrará:

- versión activa;
- cobertura por áreas;
- fuentes procesadas;
- especialistas registrados;
- lagunas conocidas;
- fecha de validación;
- estado de la base.

Ejemplo:

```text
Base de conocimiento: v1.0
Estado: validada

Lengua española................ 98%
Teoría literaria............... 94%
Narrativa...................... 96%
Ensayo......................... 91%
Autores clásicos............... 95%
Literatura contemporánea....... 81%

Especialistas registrados: 36
Fuentes académicas: 1.284
Fichas internas: 8.412
Lagunas conocidas: 7
```

No será una pantalla principal de navegación documental.

---

# 5. Módulo 2 — Fichas internas

## 5.1 Objetivo

Convertir documentos y fuentes en unidades estructuradas, enlazadas y recuperables.

Las fichas son internas. Su función es permitir que el sistema acceda al conocimiento con precisión.

---

## 5.2 Tipos mínimos de ficha

- concepto técnico;
- regla lingüística;
- principio de estilo;
- recurso literario;
- efecto estilístico;
- riesgo;
- excepción;
- autor;
- rasgo de autor;
- obra;
- fragmento demostrativo;
- movimiento;
- género;
- fuente;
- especialista;
- interpretación;
- contradicción;
- relación entre conceptos.

---

## 5.3 Esquema mínimo de ficha

```json
{
  "id": "string",
  "type": "style_principle",
  "name": "Dinamismo de la frase",
  "definition": "string",
  "effects": [],
  "signals": [],
  "risks": [],
  "exceptions": [],
  "contexts": [],
  "related_concepts": [],
  "related_authors": [],
  "examples": [],
  "sources": [],
  "interpretations": [],
  "confidence": 0.0,
  "knowledge_version": "1.0"
}
```

---

## 5.4 Requisitos de trazabilidad

Toda afirmación estructurada debe poder vincularse con:

- fuente;
- autor de la fuente;
- tipo de fuente;
- fragmento o referencia;
- fecha de incorporación;
- nivel de confianza;
- interpretación;
- versión.

---

# 6. Módulo 3 — Entrada de preferencias

## 6.1 Objetivo

Permitir que el usuario enseñe al sistema lo que le gusta mediante lenguaje natural y ejemplos.

---

## 6.2 Tipos de entrada

El usuario podrá introducir:

- preferencia;
- rechazo;
- límite;
- excepción;
- ejemplo;
- frase favorita;
- referencia a un autor;
- comparación;
- corrección explicada;
- matiz contextual;
- contradicción deliberada;
- cambio de criterio.

Ejemplos:

```text
Quiero frases más cortas, pero no telegráficas.

Ten en cuenta a Pla en la observación, no en todo el estilo.

Me encanta esta frase por cómo gira al final.

En ensayo tolero más digresión que en un artículo.

Has quitado demasiado humor.

Quiero menos Borges en la sintaxis, pero conservar la densidad.
```

---

## 6.3 Interpretación obligatoria

Antes de consolidar una entrada, el sistema debe mostrar:

- qué ha entendido;
- qué variables afecta;
- en qué dirección;
- con qué intensidad;
- en qué contexto;
- qué fichas de conocimiento ha consultado;
- qué contradicciones detecta;
- qué parte no puede inferir.

Ejemplo:

```text
Entrada:
“Quiero frases más dinámicas, pero que sigan pareciendo escritas.”

Interpretación:
- aumentar dinamismo;
- reducir ligeramente la longitud media;
- aumentar variación;
- mantener transiciones;
- limitar fragmentación;
- evitar secuencias telegráficas.
```

Acciones disponibles:

- guardar;
- corregir interpretación;
- ampliar;
- limitar por contexto;
- descartar.

---

## 6.4 Acumulación de preferencias

Una entrada nueva podrá:

- crear una preferencia;
- ampliar una existente;
- matizarla;
- limitarla;
- contradecirla;
- suspenderla;
- sustituirla;
- marcarla como temporal;
- convertirla en ajuste manual.

No se debe borrar automáticamente la preferencia anterior.

---

# 7. Módulo 4 — Scoring y perfil

## 7.1 Objetivo

Traducir las preferencias del usuario a variables numéricas explicables, editables y contextualizadas.

---

## 7.2 Escala

La escala funcional será:

```text
0–1000
```

El valor no representa calidad universal.

Representa la intensidad de una preferencia dentro del perfil.

---

## 7.3 Fuentes del scoring

Cada variable se alimenta de:

1. prompts explícitos;
2. ejemplos confirmados;
3. frases favoritas;
4. correcciones;
5. elecciones entre alternativas;
6. ajustes manuales;
7. confirmaciones;
8. rechazos;
9. patrones repetidos;
10. contexto.

---

## 7.4 Variables mínimas

### Frase

- longitud;
- variación;
- complejidad;
- subordinación;
- coordinación;
- fragmentación;
- verbos activos;
- ritmo telegráfico.

### Voz

- distancia;
- personalidad;
- autoridad;
- ironía;
- humor;
- emoción explícita;
- sobriedad;
- contundencia.

### Léxico

- precisión;
- rareza;
- tecnicismo;
- coloquialidad;
- ornamentación;
- adjetivación;
- abstracción;
- concreción.

### Recursos

- metáfora;
- metáfora funcional;
- comparación;
- elipsis;
- paradoja;
- repetición;
- enumeración;
- imagen sensorial;
- simbolismo.

### Estructura

- linealidad;
- digresión;
- progresión;
- tensión;
- densidad;
- apertura;
- cierre abierto;
- cierre contundente;
- cierre explicativo.

### Argumentación

- explicitud;
- ejemplos;
- contraargumento;
- incertidumbre;
- desarrollo;
- síntesis;
- capacidad de conclusión.

### Edición

- concisión;
- redundancia tolerada;
- explicación;
- ritmo;
- claridad;
- conservación de la voz;
- agresividad de reescritura.

---

## 7.5 Metadatos de cada variable

Cada variable deberá mostrar:

- valor calculado;
- ajuste manual;
- valor efectivo;
- confianza;
- consistencia;
- cobertura;
- número de evidencias;
- número de contradicciones;
- tendencia;
- valor reciente;
- valor histórico;
- contexto;
- fecha de último cambio;
- origen porcentual.

Ejemplo:

```text
IRONÍA

Valor calculado........ 704
Ajuste manual.......... +20
Valor efectivo......... 724

Confianza.............. 91%
Consistencia........... 78%
Cobertura.............. 84%

Origen:
- prompts.............. 45%
- correcciones......... 38%
- ajustes manuales..... 17%
```

---

## 7.6 Perfiles por contexto

La aplicación admitirá como mínimo:

- general;
- ensayo;
- artículo;
- narrativa;
- divulgación;
- técnico;
- publicidad;
- redes.

El perfil contextual hereda del general y permite sobreescrituras.

---

## 7.7 Resumen humano del perfil

El scoring debe generar una ficha legible:

```text
Prefieres textos claros y con movimiento.

Acortas las aperturas y las afirmaciones, pero mantienes
frases más largas cuando desarrollan una idea.

Te gustan las metáforas que sustituyen explicaciones.
Rechazas las ornamentales.

Toleras la digresión en ensayo, no en textos técnicos.

Prefieres cierres que añaden un giro o una consecuencia.
```

Cada afirmación deberá mostrar:

- confianza;
- muestras;
- variables relacionadas;
- opción de confirmar;
- opción de matizar;
- opción de rechazar.

---

# 8. Estadísticas y calidad del perfil

## 8.1 Objetivo

Mostrar no solo qué cree el sistema, sino cuánto puede confiarse en ello.

---

## 8.2 Indicadores generales

- confianza general;
- consistencia;
- estabilidad;
- cobertura;
- contradicciones;
- variables dudosas;
- variables consolidadas;
- variables sin datos;
- desviación reciente;
- evolución de adecuación;
- corrección media necesaria.

---

## 8.3 Consistencia temporal

Cada variable tendrá:

- valor base;
- valor de 7 días;
- valor de 30 días;
- valor histórico;
- desviación;
- tendencia;
- clasificación temporal.

Clasificaciones:

```text
Preferencia estable
Variación contextual
Racha temporal
Ruido
Cambio real
Sin datos suficientes
```

El sistema no atribuirá causas psicológicas.

Podrá afirmar:

> Esta semana tus correcciones se apartan del patrón habitual.

No podrá afirmar:

> Estás deprimido y por eso escribes así.

---

## 8.4 Variables dudosas

Una variable se marcará como dudosa cuando:

- tenga pocas muestras;
- muestre contradicciones;
- cambie mucho entre textos equivalentes;
- dependa demasiado del contexto;
- el usuario no haya confirmado la interpretación;
- el ajuste manual contradiga continuamente el comportamiento.

---

## 8.5 Contradicciones

La aplicación debe mostrar contradicciones de forma resoluble:

```text
Prompt:
“Quiero frases cortas.”

Comportamiento:
Has alargado el 72% de las frases propuestas.

Posibles explicaciones:
- solo en ensayo;
- solo durante el desarrollo;
- el prompt está desactualizado;
- falta distinguir tipos de frase.
```

Acciones:

- resolver;
- limitar por contexto;
- mantener contradicción;
- invalidar prompt;
- pedir más datos.

---

# 9. Módulo 5 — Generador y corrector

## 9.1 Objetivo

Crear y transformar textos utilizando:

```text
conocimiento estable
+
petición concreta
+
perfil contextual
+
scoring efectivo
```

---

## 9.2 Entradas admitidas

- idea;
- título;
- notas;
- esquema;
- fragmento;
- texto completo;
- objetivo;
- género;
- público;
- longitud;
- referencias;
- perfil;
- variables protegidas;
- intensidad de cambio.

---

## 9.3 Acciones

- generar;
- continuar;
- corregir;
- reescribir;
- reducir;
- ampliar;
- reestructurar;
- crear alternativas;
- cambiar tono;
- cambiar ritmo;
- aplicar rasgos de autores;
- conservar elementos;
- comparar.

---

## 9.4 Autores como referencias parciales

No se permitirá una imitación integral opaca.

Debe poder especificarse:

```text
Hemingway:
- ritmo 40%
- frase 30%
- elipsis 20%

Pla:
- precisión observacional 35%

Borges:
- densidad conceptual 20%
```

El sistema podrá aplicar solo rasgos concretos.

---

## 9.5 Protección de elementos

El usuario podrá proteger:

- ideas;
- estructura;
- vocabulario;
- metáforas;
- tono;
- cierre;
- citas;
- nombres;
- longitud;
- voz.

---

## 9.6 Intensidad

La transformación deberá admitir:

- mínima;
- ligera;
- media;
- profunda;
- texto nuevo basado en la idea.

---

# 10. Módulo 6 — Comparador de cambios

## 10.1 Objetivo

Medir de forma explicable cuánto se ha cambiado y cuánto se aproxima el resultado al perfil.

---

## 10.2 Dos métricas obligatorias

### A. Modificación

Cuánto ha cambiado el texto.

```text
0%   = no se ha cambiado nada
100% = texto completamente diferente
```

### B. Adecuación

Cuánto se aproxima la salida inicial al resultado finalmente aceptado.

```text
Más corrección necesaria = menor adecuación
Menos corrección necesaria = mayor adecuación
```

La adecuación nunca se calculará como simple inversa de caracteres modificados.

---

## 10.3 Dimensiones de cambio

- puntuación;
- ortografía;
- léxico;
- sintaxis;
- ritmo;
- tono;
- estructura;
- ideas;
- orden;
- voz;
- recursos;
- longitud.

Ejemplo:

```text
Cambio textual........ 82%
Cambio sintáctico..... 71%
Cambio de ritmo....... 65%
Cambio estructural.... 18%
Cambio de ideas........ 4%

Adecuación general.... 79%
```

---

## 10.4 Ponderación funcional

Los cambios tendrán pesos diferentes.

Ejemplo orientativo:

```text
Puntuación............ 0.10
Palabra............... 0.25
Sintaxis.............. 0.45
Ritmo................. 0.50
Párrafo............... 0.70
Estructura............ 0.90
Idea.................. 1.00
```

La implementación exacta pertenece a la arquitectura técnica, pero la separación funcional es obligatoria.

---

## 10.5 Estados legibles

```text
0%        No se ha cambiado nada
1–10%     Ajustes mínimos
11–30%    Corrección ligera
31–60%    Reescritura parcial
61–85%    Reescritura profunda
86–99%    Texto casi nuevo
100%      Texto nuevo basado solo en la idea
```

---

# 11. Módulo 7 — Retroalimentación controlada

## 11.1 Objetivo

Convertir correcciones en propuestas de actualización, nunca en cambios silenciosos.

---

## 11.2 Flujo

```text
Texto generado
      ↓
Texto corregido
      ↓
Comparación
      ↓
Variables afectadas
      ↓
Propuesta de actualización
      ↓
Aprobación, revisión o rechazo
```

---

## 11.3 Acciones posibles

- aplicar todo;
- revisar variable por variable;
- aplicar parcialmente;
- matizar;
- limitar por contexto;
- no aprender de este texto;
- marcar como excepción;
- marcar como estado temporal;
- convertir en ajuste manual.

---

## 11.4 Ejemplo

```text
Aprendizaje propuesto:

Frase breve:
682 → 697

Cierre explicativo:
291 → 276

Ornamentación:
219 → 211

Motivo:
- acortaste 8 de 11 frases;
- eliminaste 4 explicaciones;
- mantuviste 2 metáforas;
- reforzaste el cierre.
```

---

# 12. Pantallas de V1

## 12.1 Conocimiento

Función:

- mostrar acreditación;
- versión;
- cobertura;
- fuentes;
- especialistas;
- lagunas.

No es una biblioteca operativa.

---

## 12.2 Añadir preferencias

Función:

- introducir prompts;
- añadir ejemplos;
- explicar gustos;
- registrar límites;
- incorporar frases favoritas;
- revisar interpretación.

---

## 12.3 Lo que sabe de mí

Función:

- resumen humano;
- preferencias;
- rechazos;
- matices;
- excepciones;
- confianza;
- muestras;
- confirmación.

---

## 12.4 Perfil y scoring

Función:

- editar variables;
- ver estadísticas;
- ver procedencia;
- ver confianza;
- comparar valor calculado y efectivo;
- modificar ajustes;
- filtrar por contexto;
- ver evolución.

---

## 12.5 Editor

Función:

- escribir;
- generar;
- corregir;
- reescribir;
- comparar;
- elegir alternativas;
- proteger elementos;
- aplicar perfiles.

---

## 12.6 Laboratorio

Función:

- mover variables temporalmente;
- generar pruebas;
- comparar A/B;
- no guardar automáticamente;
- convertir una prueba en perfil solo con confirmación.

---

## 12.7 Comparador

Función:

- mostrar cambios;
- clasificar cambios;
- medir adecuación;
- explicar impacto;
- producir retroalimentación.

---

# 13. Reglas de decisión

## 13.1 Prioridad de instrucciones

Orden obligatorio:

1. restricciones técnicas y lingüísticas;
2. petición concreta del texto;
3. protecciones explícitas;
4. ajustes manuales;
5. perfil contextual;
6. perfil general;
7. referencias de autor;
8. conocimiento estilístico;
9. comportamiento por defecto.

---

## 13.2 Conflictos

Cuando dos preferencias entren en conflicto, el sistema debe:

1. detectar el conflicto;
2. mostrarlo;
3. aplicar la prioridad;
4. explicar la decisión;
5. permitir cambiarla.

---

## 13.3 Datos insuficientes

Cuando no haya suficiente información:

- no inventar una preferencia;
- usar el perfil general;
- marcar baja confianza;
- proponer una prueba A/B;
- permitir desactivar la variable.

---

# 14. Persistencia funcional

La aplicación deberá persistir por separado:

```text
knowledge/
preferences/
profiles/
scores/
manual_overrides/
contexts/
texts/
versions/
comparisons/
feedback/
statistics/
```

No se permite mezclar conocimiento académico con datos personales de preferencia.

---

# 15. Auditoría de Cerebro para reutilización

La auditoría técnica de Cerebro será posterior a este contrato.

## 15.1 Candidatos a reutilización

Buscar piezas equivalentes a:

- registro de fuentes;
- normalización;
- extracción;
- creación de fichas;
- procedencia;
- confianza;
- relaciones;
- contradicciones;
- versionado;
- recuperación;
- validación de grafos;
- logs;
- importadores.

## 15.2 Piezas que no deben heredarse

- memorias generalistas;
- learning silencioso;
- working memory;
- RAM;
- world model;
- AroundTheWorld;
- señales comerciales;
- señales reputacionales;
- integración con Flow Console;
- integración con MiBØ;
- proactividad;
- monitorización general;
- entidades personales;
- automatizaciones.

## 15.3 Criterio de auditoría

Cada pieza se clasificará como:

```text
REUTILIZAR
ADAPTAR
USAR COMO REFERENCIA
DESCARTAR
```

Minicerebro debe nacer como producto independiente.

Cerebro se tratará como cantera, no como cimiento.

---

# 16. Criterios de aceptación de V1

La V1 se considerará funcionalmente terminada cuando permita:

1. mostrar una base de conocimiento versionada y acreditada;
2. registrar fuentes y especialistas sin modificar la lógica;
3. convertir conocimiento a fichas internas;
4. introducir una preferencia mediante prompt;
5. mostrar la interpretación antes de guardarla;
6. convertirla en variables;
7. editar variables manualmente;
8. mostrar scoring, confianza, consistencia y cobertura;
9. mantener perfiles por contexto;
10. generar un texto desde una idea;
11. corregir un texto;
12. crear alternativas;
13. comparar salida y corrección final;
14. medir modificación y adecuación;
15. proponer actualizaciones del scoring;
16. aprobar o rechazar el aprendizaje;
17. mostrar un resumen humano del perfil;
18. detectar contradicciones;
19. distinguir patrón estable de variación temporal;
20. probar cambios en laboratorio sin alterar el perfil.

---

# 17. Condiciones de cierre

Este contrato queda cerrado con las siguientes condiciones:

- V1 solo trata escritura en lengua española.
- La base de conocimiento es estable y versionada.
- El perfil de preferencias es independiente.
- El scoring es visible y editable.
- Toda evolución del perfil es trazable.
- Ninguna corrección modifica conocimiento académico.
- Ningún aprendizaje se aplica sin revisión o regla explícita.
- La adecuación se mide por la corrección necesaria.
- La consistencia del usuario se analiza sin atribuir causas psicológicas.
- Cerebro no se usa como base arquitectónica automática.
- La reutilización de Cerebro exige auditoría pieza por pieza.
- No se añaden módulos fuera de este contrato sin abrir una nueva versión.

---

# 18. Resultado esperado

Minicerebro V1 debe poder responder, de forma verificable:

```text
Esto es lo que sé sobre escribir.

Esto es lo que me has dicho que te gusta.

Esto es lo que deduzco de tus correcciones.

Estas son las variables y sus pesos.

Esta es la confianza que tengo en cada una.

Este texto se aproxima un 84% a tu perfil.

Has modificado un 16%.

Estos cambios sugieren ajustar tres variables.

Nada cambiará hasta que lo apruebes.
```

---

**FIN DEL CONTRATO FUNCIONAL V1.0**
