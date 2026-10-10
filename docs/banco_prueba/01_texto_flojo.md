# Banco de prueba 01 — Texto flojo (Revisar por bloques)

Texto escrito a propósito con problemas de bloque, idea y planteamiento. Sirve
para medir qué detecta "Revisar por bloques" y qué se le escapa.

Tipo de texto que hay que declarar: `artículo de opinión breve`

## Texto

```text
Hoy en día el teletrabajo es un tema muy importante en la sociedad actual y todo el mundo habla de ello, porque es algo que afecta a muchas personas y que cada vez está más presente en nuestras vidas.

Trabajar desde casa tiene ventajas y desventajas. Por un lado se ahorra tiempo en desplazamientos, y por otro lado los niños están en casa y hay que atenderlos, lo cual hace que la productividad baje bastante, aunque también depende de la edad de los niños y de si hay alguien más en casa, y además las empresas tienen que pagar ordenadores.

El problema es que en casa uno se distrae. Hay muchas distracciones. Es muy fácil distraerse con cualquier cosa. La televisión, el móvil o la nevera hacen que uno pierda la concentración y se distraiga.

En Japón, por ejemplo, la gente trabaja muchísimas horas en la oficina.

Como todos sabemos, en casa se trabaja más que en la oficina, porque no hay pausas para el café ni reuniones inútiles, así que las empresas salen ganando.

En base a todo esto, yo creo que lo mejor es un modelo mixto, donde habían días en casa y días en la oficina, porque así se aprovecha lo mejor de cada sitio.

En conclusión, el teletrabajo tiene cosas buenas y cosas malas, y en casa es muy fácil distraerse con la televisión y el móvil.
```

## Lo que debería detectar

| Bloque | Problema sembrado | Diagnóstico esperado |
|---|---|---|
| 1 | Arranque de tópico que no dice nada ("hoy en día", "sociedad actual") | falta_fuerza |
| 2 | Mezcla tres ideas (tiempo, niños, ordenadores) en una frase interminable | confuso |
| 3 | Cuatro frases dicen lo mismo (distraerse) | pesado |
| 4 | Japón aparece y no se conecta con nada | idea_suelta |
| 5 | Dice que en casa se trabaja más; el bloque 2 y el 3 dicen lo contrario | no_cuadra |
| 6 | La tesis (modelo mixto) aparece al final; debería orientar el texto | orden (en la lectura global) |
| 7 | Repite el bloque 3 en lugar de cerrar | redundante |

Errores de norma sembrados (no son el objetivo de Revisar, pero las alternativas
no deben conservarlos): "en base a" (mejor "a partir de" o "con base en"),
"habían días" (debe ser "hubiera días" o "haya días").

## Cómo puntuar

- Detección: bloques con el diagnóstico esperado o equivalente, sobre 7.
- Lectura global: menciona la contradicción 2/3 frente a 5 y que la tesis llega tarde.
- Calidad de las alternativas: reescriben el bloque entero y las tres son distintas.
- Norma: ninguna alternativa conserva "en base a" ni "habían días".
