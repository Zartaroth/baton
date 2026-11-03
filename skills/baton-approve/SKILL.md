---
name: baton-approve
description: Rol Aprobador de tests de la metodología Baton. Ayuda a una persona a revisar los tests de aceptación de un ítem contra sus criterios y, si los aprueba, los congela en baton/acceptance.lock y entrega el turno al Driver. Úsala cuando un ítem está en TestsEnRevision. La aprobación siempre la da una persona, en todos los niveles de autonomía.
---

# baton-approve

**Rol:** Aprobador de tests. Al menos una **persona** que no es el autor ni el Driver. **Entrada:** el traspaso del autor y los tests. **Salida:** `acceptance.lock` actualizado, el ítem en `TestsCongelados` y el traspaso al Driver. Si se rechaza, el ítem vuelve a `Listo`.

El agente **prepara la revisión y ejecuta los comandos**, pero **no aprueba**. Sin un "apruebo" explícito de la persona en esta sesión, no congeles nada.

## Pasos

1. Busca el traspaso con `python3 baton/bin/baton.py next --rol aprobador_tests` y márcalo con `tomar`.
2. **Presenta cada criterio junto a sus tests, en un mensaje de texto, antes de preguntar.** Es lo que la persona aprueba: sin esto, la aprobación no vale. Usa una tabla con una fila por criterio:

   | Criterio | Entonces (del ítem) | Qué comprueba el test (asserts clave, con sus valores) | Observación |
   |---|---|---|---|

   - No omitas ningún criterio, aunque sean muchos. Si un test tiene varios casos (`parametrize`), lista los valores.
   - Si la persona pide ver el código de un test, muéstralo completo.
   - Lo que leíste o pensaste sin mostrarlo no cuenta: la persona no lo ve.

   Por cada par, revisa esto y anota lo que encuentres en "Observación":
   - ¿El test comprueba exactamente el **Entonces**, ni más ni menos?
   - ¿Se puede implementar sin conocer detalles internos que todavía no existen?
   - ¿Tiene mocks del sistema que se prueba, `skip`, asserts débiles o datos ambiguos?
   - ¿El rojo verificado del traspaso falla por la razón correcta?
   - ¿Falta algún caso de los criterios?
3. Vuelve a ejecutar el archivo con `comandos.aceptacion_archivo` y confirma que el rojo coincide con el del traspaso.
4. Después de la tabla, pregunta a la persona: **¿apruebas o rechazas?** Si tu entorno tiene preguntas interactivas (en Claude Code, `AskUserQuestion`), úsalas con las opciones "Apruebo" y "Rechazo (te digo por qué)". La respuesta tiene que ser explícita: nunca la des por supuesta.

### Si aprueba

1. Ejecuta `python3 baton/bin/baton.py lock aprobar --item <ítem> --aprobado-por <persona>[,<otra>]`. Si viene de una solicitud, agrega `--solicitud <ítem>-R<n>`. El comando valida que quien aprueba es aprobador del ítem, que es una persona y que cada criterio vigente tiene su test.
2. Ejecuta `python3 baton/bin/baton.py estado <ítem> TestsCongelados`. Si había solicitud, ejecuta también `python3 baton/bin/baton.py estado <ítem>-R<n> Aplicada`.
3. Ejecuta `python3 baton/bin/baton.py sync --autor <persona> --motivo "<aprobación inicial | cambio por R<n>>" --ref acceptance.lock`.
4. Propón hacer **commit ahora** de los tests y el lock. El hook compara contra el último commit, así que el congelamiento protege desde ese momento.
5. Crea el traspaso para el primer slice pendiente: `python3 baton/bin/baton.py handoff --item <ítem> --slice <S> --de aprobador_tests --para driver --entidad-de <persona>`. Completa `## Qué se entrega`, `## Qué se espera` y `## Contexto`.

### Si rechaza

1. Ejecuta `python3 baton/bin/baton.py estado <ítem> Listo`.
2. Ejecuta `python3 baton/bin/baton.py handoff --item <ítem> --de aprobador_tests --para autor_tests --entidad-de <persona>` y escribe en `## Contexto` qué cambiar en cada test.
3. Ejecuta `python3 baton/bin/baton.py sync --autor <persona> --motivo "tests rechazados: <resumen>"`.

## Lote (Delegado)

En módulos Delegado, la persona puede aprobar de una vez todos los ítems del módulo que están en `TestsEnRevision`. Haz la revisión ítem por ítem en la misma sesión y, al final, pide una sola decisión. Después ejecuta `lock aprobar` y `estado` por cada ítem aprobado, y un solo sync.

## No hagas

- No edites los tests para "arreglarlos" durante la revisión. Si algo está mal, se rechaza y lo corrige el autor.
- No ejecutes `lock aprobar` en nombre de una persona que no confirmó.
