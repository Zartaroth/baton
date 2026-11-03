---
name: baton-tests
description: Rol Autor de tests de la metodología Baton. Convierte los criterios de aceptación de un ítem Listo en tests de aceptación ejecutables, verifica que fallen por la razón correcta (rojo verificado) y los entrega al aprobador. Úsala cuando un ítem está en Listo o cuando te toque el turno de autor_tests.
---

# baton-tests

**Rol:** Autor de tests. Nunca es el Driver ni el aprobador. **Entrada:** el traspaso, el ítem y el plan. **Salida:** el archivo de tests en rojo verificado, el ítem en `TestsEnRevision` y el traspaso al aprobador.

## Pasos

1. Busca tu traspaso con `python3 baton/bin/baton.py next --rol autor_tests` y márcalo con `python3 baton/bin/baton.py tomar <id>`. Lee solo lo que está en `leer`.
2. **Un archivo por ítem** en `<tests_aceptacion>/<módulo>/`, con el id del ítem al inicio del nombre: `US_004_cobro_test.py`, `US_004_cobro.spec.ts`, etc. El sufijo es el que necesita el framework para descubrir el archivo.
3. **Un test o más por criterio vigente**, con `<ITEM>_AC_<n>` en el nombre: `test_US_004_AC_1_pago_aprobado` o `it("US-004/AC-1 pago aprobado")`. Así el lock y la trazabilidad saben qué criterio cubre cada test.
4. **Cómo escribirlos:**
   - De **caja negra**: el test usa la interfaz pública (HTTP, UI, CLI, la función pública del módulo). No usa detalles internos que el Driver todavía no decidió.
   - El **Dado** se construye con datos explícitos dentro del test o con fixtures claras.
   - El **Entonces** se convierte en asserts sobre resultados observables. Un assert por idea, con un mensaje que diga qué criterio falló.
   - Solo se hacen mocks de **fronteras externas** (pasarela de pago, correo, reloj). Nunca del sistema que se prueba.
   - Nada de `skip`, `xfail`, `only`, `sleep` arbitrarios ni asserts que siempre pasan.
   - Si necesitas fixtures compartidas nuevas (archivos que no empiezan con un id de ítem), créalas ahora: después quedan congeladas con el ítem. Si el runner tiene un archivo de configuración que pueda saltarse tests, debe estar en `rutas.protegidos`.
5. **Rojo verificado.** Ejecuta el archivo con `comandos.aceptacion_archivo`. Cada test tiene que fallar **por la razón correcta**:
   - **Vale:** el assert falla, o falla porque la funcionalidad no existe (404, función o módulo de producción inexistente).
   - **No vale:** un error de sintaxis o de importación *del propio test*, una fixture rota o un error de entorno.
   - **Si un test pasa sin código nuevo**, el test es débil o la funcionalidad ya existe. Corrígelo o explícalo en el traspaso.
6. Ejecuta `python3 baton/bin/baton.py estado <ítem> TestsEnRevision`.
7. Ejecuta `python3 baton/bin/baton.py handoff --item <ítem> --de autor_tests --para aprobador_tests`. En `## Tests del slice` (o una tabla nueva, `## Rojo verificado`), pon por cada test: nombre, criterio, resultado y **la razón del fallo** copiada de la salida.
8. Ejecuta `python3 baton/bin/baton.py sync --autor <entidad> --motivo "tests de <ítem> escritos"`.

## Si vienes de una solicitud aprobada

Cambia solo los tests que lista `afecta` en la solicitud. Indica en el traspaso qué cambió y por qué, y la solicitud (`<ítem>-R<n>`), para que `approve` la use al recongelar.

## No hagas

- No escribas código de producción, ni siquiera "para que compile".
- No toques archivos que ya están en `baton/acceptance.lock` sin una solicitud aprobada. El hook rechazará el commit.
- No apruebes tus propios tests.
