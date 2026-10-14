# Política de conocimiento de Editados

Qué conocimiento usa Editados, de dónde sale y cómo llega al modelo. Lo decide
el autor; el código lo aplica. Si algo choca con este documento, se cambia aquí
primero y en el código después.

Sustituye a la política anterior, que exigía ingerir el texto de cada obra
(edición, segmentación, extracción, evidencia) antes de poder usarla. Como las
obras de referencia tienen derechos, ese circuito no terminaba nunca: todas las
fuentes nacían como «contenido no ingerido», 291 de 294 evidencias acabaron
siendo resúmenes de una línea y el modelo recibía definiciones que ya conocía.

## 1. La ficha de oficio es el formato válido

Las normas, los criterios y las técnicas no están protegidos; lo está la
redacción concreta de cada obra. Editados no necesita el texto de la *Nueva
gramática* ni de Cassany: necesita saber qué dicen, explicado con palabras
propias y con un sitio donde comprobarlo.

Cada ficha tiene:

| Campo | Qué es |
|---|---|
| Regla | Lo que hay que hacer, en palabras propias y comprobable. |
| Aplica | Cuándo se aplica. |
| No aplica | Excepciones y falsos positivos: cuándo tocar sería un error. |
| Ejemplos | Pares propios «mal → bien» con el porqué. Nunca frases de las obras. |
| Fuente | Obra y localizador («DPD, s. v. *deber*»), o «criterio de Editados» si la regla es propia. |
| Señales | Patrones que delatan el problema en un texto (tipo «error») o marcan un pasaje que vigilar o proteger (tipo «vigilancia»). Cada señal de error tiene que saltar en el ejemplo malo de su ficha y no en el bueno: lo comprueban los tests. |
| Relaciones | Con qué otras fichas se prioriza, choca o se combina. |

Una ficha sin regla comprobable, sin «no aplica» o sin ejemplo no se publica.

## 2. Ingesta de obras

Solo para textos libres de derechos o con permiso expreso, y solo para sacar
ejemplos o modelos de estilo. No es requisito para crear fichas.

La base anterior (294 fichas y su circuito de ingesta) queda retirada del
producto: no alimenta propuestas, lecturas ni la Biblioteca. Sus tablas siguen
en la base de datos solo para conservar el historial antiguo.

### Dónde se usan las fichas de oficio

- Corregir, Editar, Hacer enviable, Continuar y Variantes: el modelo recibe las
  fichas elegidas con sus prioridades.
- Revisar por bloques: fichas de composición, voz, géneros y criterio.
- Leer con fichas: cada paso es una ficha, con lo que ve en el texto, la regla,
  un ejemplo, cuándo no aplica y la fuente.
- Biblioteca: todas las fichas, por rama, con sus relaciones.
- Mi criterio: «Me sirve» o «No va conmigo» en una ficha cambia su peso al
  elegir fichas para tus textos. Una ficha descartada solo vuelve si el texto la
  pide con una señal.

## 3. Las fichas se consultan entre ellas

Las relaciones entre fichas son parte del conocimiento, no un adorno:

- **prioridad_sobre:** si las dos piden cosas distintas, gana esta. Puede ir
  con condición («en narrativa», «en textos profesionales»).
- **conflicto_con:** las dos pueden tirar en sentidos opuestos; el modelo debe
  decidir con el criterio que indica la relación.
- **requiere:** antes de aplicar esta, hay que tener en cuenta la otra.

Orden general de prioridad, salvo relación más concreta:

1. Norma (lo que es error).
2. Sentido: hechos, tesis y matices protegidos.
3. Claridad y precisión.
4. Concisión.
5. Ritmo y voz, que suben por encima de claridad y concisión en narrativa y
   textos literarios.

## 4. Selección por diagnóstico, no por palabras

Las fichas no se eligen buscando palabras del texto (así llegaba «Haber
impersonal» a un ensayo porque decía «Haber sido elegido»). Se eligen así:

1. **Señales en el texto:** cada ficha con señales que aparecen en el borrador
   entra, con el fragmento donde aparece. Un fallo probable pesa más que un pasaje
   que vigilar, salvo en las fichas que protegen el sentido (matices, citas,
   analogías…) cuando la acción reescribe el texto.
2. **Acción y mirada:** cada acción (Corregir, Editar, Revisar…) y cada mirada
   (comprensión, estructura, tono, limpieza) tiene sus fichas de base.
3. **Tipo de texto y dirección:** el tipo que declara el autor activa las fichas
   de su género, y la dirección («más esperpéntico», «como un soneto») activa las
   fichas de tradición o de género que nombra. Sin género declarado, una ficha de
   género solo entra si su señal de error aparece en el texto.
4. **Relaciones:** las fichas requeridas por las elegidas entran también, y las
   prioridades entre las elegidas se envían al modelo. Si una ficha que no se ha
   elegido prevalece sobre una elegida o choca con ella, su regla viaja como
   límite de la elegida, sin ocupar plaza: una prioridad nunca se pierde porque
   la otra ficha no haya entrado.
5. **Diagnóstico con el modelo:** los patrones solo proponen candidatas. Antes de
   editar o leer, el modelo lee el texto entero y decide qué candidatas son de
   verdad un caso de su ficha (las demás se descartan) y qué problemas hay que
   ningún patrón detecta, con el fragmento literal. Solo se acepta lo
   comprobable: fichas que existen y fragmentos que están en el texto. El
   resultado se guarda en caché, así que el mismo texto con las mismas opciones
   da siempre las mismas fichas. Si el modelo no está disponible, se elige solo
   por patrones y se dice.
6. **Tope:** entran como mucho 12 fichas (7 en «Leer»), pero un problema
   confirmado en el texto nunca se queda fuera por el tope: se añade detrás.

## 5. Qué recibe el modelo

De cada ficha elegida: regla, cuándo aplica, cuándo no, un ejemplo, el
fragmento del texto si lo hay y los límites de otras fichas. Además, las
prioridades entre las fichas elegidas. Nunca solo el nombre y una definición.

Después de generar se comprueba si la propuesta aplicó las fichas que detectaron
un problema: se vuelven a pasar sus señales y métricas sobre la propuesta, o se
mira si el fragmento señalado sigue igual. El resultado (aplicada, en parte, sin
aplicar) se ve en «Ver detalles». Las fichas que son criterios generales no se
pueden medir así y se cuentan aparte, sin darlas por aplicadas. Si una ficha
sigue sin aplicarse en la mayoría de los textos, Editados propone revisarla.

## 6. Las fichas se editan y se mejoran

Los archivos YAML del repositorio son la versión original. Las ediciones se
guardan en la base de datos y prevalecen sobre el original. Editados usa siempre
la versión vigente de cada ficha.

- **Edición:** desde la Biblioteca, quien administra el conocimiento puede editar
  una ficha, crear una nueva y desactivarla o reactivarla. Cada cambio exige un
  motivo y queda en el historial con fecha y autor. Cualquier versión anterior se
  puede restaurar.
- **Validación al guardar:** una ficha solo se guarda si cumple el formato, sus
  relaciones apuntan a fichas activas y cada señal de error salta en su primer
  ejemplo malo y en ningún ejemplo bueno, ni suyo ni de otra ficha. No se puede
  desactivar una ficha de la que dependen otras.
- **Propuestas de mejora:** Editados busca fichas con indicios de fallar:
  - el autor la ha descartado o marcado con reparos;
  - las propuestas de Escribir en las que intervino se descartan en al menos el
    60 % de los casos, con un mínimo de 4;
  - su señal salta en al menos el 60 % de los textos, con un mínimo de 40;
  - no ha entrado en ninguno de los últimos 60 textos y no tiene ni señal ni
    métrica;
  - el modelo la recibe, pero el problema sigue en la propuesta en al menos el
    60 % de los casos, con un mínimo de 5.

  Para cada una redacta una versión revisada, la valida igual que una edición
  manual y la deja pendiente. **Nada cambia sin aprobación**: el autor la acepta,
  la edita antes de aceptarla o la rechaza. Una ficha rechazada no vuelve a
  proponerse durante 14 días, y el uso anterior a una decisión no cuenta para la
  siguiente.
- **Qué se registra:** aceptar o descartar una propuesta de Escribir guarda qué
  fichas intervinieron y la decisión, nunca el texto.

## 7. Lo que Editados aprende de cada autor (capa 3)

El aprendizaje es personal y no cambia las fichas. Sale de dos fuentes, siempre
del propio perfil:

- **Propuestas de Escribir aceptadas o descartadas**, con las fichas que las
  produjeron. Una ficha que la comprobación vio sin aplicar apenas cuenta, porque
  no explica la decisión. Con al menos 3 decisiones, la ficha sube o baja de peso
  al elegir fichas para ese autor.
- **Elecciones de «Revisar por bloques»:** qué tipo de versión elige (más breve,
  reordenada, con un ejemplo concreto…), cuándo mantiene su texto según el
  diagnóstico, qué replanteamientos del loco Iván acepta y en qué trampas cae
  (norma, sentido, orden, tópico). Con al menos 5 elecciones se convierte en su
  línea editorial. Lo reciente se compara con lo anterior para ver si cambia de
  gusto.

La línea editorial se usa de tres formas: pesos al elegir fichas (y puede traer
una ficha que trabaja lo que el autor prefiere o lo que no ve), una guía en
palabras para el modelo, y la proporción de replanteamientos en Revisar. Las
trampas no cambian con la línea, porque son lo que mide. Todo se ve en «Mi
criterio», en «Tu línea editorial».

Decidido el 14 de octubre de 2026.
