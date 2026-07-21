# Cierre del plan V1

Fecha de cierre: 2026-07-22

Repositorio: `xunevega/minicerebro`

## Estado

El plan V1 queda cerrado hasta el punto 20 del contrato y la arquitectura tecnica. No hay V2 planificada.

Los puntos 21 y 22 no existen en los documentos V1 versionados. La aplicacion los expone como limites de contrato mediante `GET /contract/boundaries`, con estado `not_defined_in_v1`.

## Puntos cerrados

1. Persistencia real con SQLAlchemy, Alembic y PostgreSQL.
2. Preferencias trazables y revisables.
3. Scoring editable con ajuste manual.
4. Flujo de aceptacion/rechazo de preferencias.
5. Auditoria de eventos.
6. Generacion con proveedor determinista y soporte OpenAI opcional.
7. Comparador con dimensiones y cambios.
8. Conocimiento seed separado del perfil, trazable y validado en auditoria.
9. Estadisticas, contradicciones y contextos.
10. Laboratorio sin aprendizaje automatico.
11. Retroalimentacion controlada.
12. Pantallas V1.
13. Reglas de decision.
14. Persistencia funcional separada.
15. Auditoria de Cerebro como cantera, no cimiento.
16. Criterios de aceptacion V1.
17. Condiciones de cierre y observabilidad con tiempos auditados.
18. Resultado esperado y roadmap tecnico.
19. Gates de auditoria de Cerebro.
20. Criterio de cierre tecnico.

## Verificacion local

Comandos de cierre:

```bash
make validate
make migrate-sqlite
make migrate-postgres
FRONTEND_URL=http://127.0.0.1:5173 make smoke-ui
```

Endpoints de prueba:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/acceptance/v1
curl http://127.0.0.1:8000/closure/technical
curl http://127.0.0.1:8000/contract/boundaries
curl http://127.0.0.1:8000/profiles/default/export
```

## Condiciones

- V1 solo trata escritura en lengua espanola.
- Conocimiento estable y perfil editable siguen separados.
- El perfil es exportable sin incluir ni modificar la base de conocimiento.
- Conocimiento expone fuente, nodo, evidencia, claim, ficha, version, consulta e historial.
- La validacion visible de conocimiento queda auditada por consulta.
- La observabilidad V1 usa eventos reales para interpretacion, generacion, recuperacion, comparacion, scoring y feedback.
- Las `gaps` de conocimiento son elementos fuera de alcance V1, no pendientes de cierre.
- Ningun aprendizaje se aplica sin revision o regla explicita.
- Cerebro no se usa como base arquitectonica automatica y queda bloqueado hasta evidencia de codigo pieza por pieza.
- No hay V2 ni expansion multidominio planificada.
- Cualquier cambio posterior queda limitado a mantenimiento o refinamiento dentro del contrato V1.
