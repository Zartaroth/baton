# Bitácora del piloto

Proyecto: `gastos` · Guía: [GUIA-PILOTO.md](GUIA-PILOTO.md)

# Intento 3 · Baton 0.4, piloto en un repositorio independiente

Empieza el 2026-11-03, alrededor de las 18:20. Las sesiones de este intento son las de `~/.claude/projects/-home-zartaroth-Proyectos-baton-piloto/` creadas desde esa hora.

## Fases

| Fase | Sesión/modelo | Costo (/cost) | ¿Como lo pensé? | Fricción |
|---|---|---|---|---|
| 1 · Inicio del proyecto | A · Opus · sesión `491c3426`, 18:12–18:21 (9 min) | (anotar /cost) | Sí: entendió antes de configurar, todas las decisiones llegaron interactivas, y el cierre fue en tablas | Nombre del proyecto tomado de la carpeta; la escala no ofrecía MVP |
| 2 · Cambiar el mapa | A · Opus · sesión `2c15aa58`, 18:28–18:34 (6 min) | (anotar /cost) | Sí: dividir, fusionar y descartar funcionaron con motivo interactivo, y la visión quedó siempre coherente | La propuesta de candidatos llegó en texto; leyó `baton.py` para responder la invariante |
| 3 · `registro` (Delegado) | A · subagente · B Sonnet · C Haiku · hasta el punto 4: sesión `2c15aa58`, 18:34–18:51 (17 min) | (anotar /cost) | En parte: los ítems, el plan y los tests son de buena calidad, pero **aprobaste dos veces algo que no viste** | Criterios no mostrados antes de aprobar; tests no mostrados junto a sus criterios; el hook rechazó el commit de la aprobación |
| 4 · `saldos` (Pair) | A · subagente · B Sonnet | | | |
| 5 · Iterar | A · Opus | | | |
| 6 · Ataques | terminal | 0 | | |

## Resultado de cada verificación

| Fase | | Verificación | Detalle |
|---|---|---|---|
| 1 | ✅ | El router anunció `Rol · Paso` y lanzó `baton-start`. | "Rol: humano + Navigator · Paso: iniciar proyecto · Sobre: baton-piloto". |
| 1 | ⏭️ | "empecemos el proyecto", sin barra, activa el router. | no se probó. |
| 1 | ✅ | Usó `detectar`, no exploró a mano ni leyó la metodología. | **D9 verificado:** no leyó el código de `baton.py`; solo las referencias y plantillas de la skill. |
| 1 | ✅ | Entendió antes de configurar, en 2 rondas como máximo, con resumen y confirmación. | ronda 1 en texto; ronda 2 con el alcance propuesto en texto y 4 decisiones interactivas (escala, centavo, transferencias, alcance). Confirmó la visión con una pregunta interactiva. Escribió glosario y "Lo que no sabemos" (formato de montos, archivo del viaje, mayúsculas). |
| 1 | ✅ | Forma de preguntar: decisiones interactivas, abiertas en texto. | **D7 verificado:** toda la configuración en dos tandas interactivas de 4 preguntas, con la recomendación primero. ⚠️ La escala no ofrecía MVP y tuviste que escribirlo (D17). |
| 1 | ✅ | Stack después de la escala, 3 opciones con motivo, ADR con `## Revisar si`. | stdlib + JSON, Typer + SQLite, Go o Rust. 4 condiciones concretas para revisar. Agregó la arquitectura en tres capas a la visión. |
| 1 | ✅ | Cada recomendación cita el contexto. | "Checkpoint: sin datos sensibles, pero es el primer proyecto con Baton y conviene calibrar"; "CODEOWNERS no aplica: no hay remoto". |
| 1 | ❌ | El proyecto se llama `gastos`, no como la carpeta. | quedó `proyecto: baton-piloto`. Nunca preguntó ni propuso un nombre (D16). |
| 1 | ⏭️ | Al pedir "que sonnet también apruebe tests", se niega y cita la invariante. | los roles llegaron como pregunta interactiva y elegiste la propuesta. La guía no decía cómo meter el pedido; ahora dice "Other" y se prueba en la fase 2. |
| 1 | ✅ | Creó solo los módulos aceptados, en `Planificado`, con `## Objetivo`. | propuso `cuentas` y `liquidacion` (no `registro` y `saldos`); la guía de las fases 2 y 4 se adaptó. |
| 1 | ✅ | `validar` da `ok`, existe el hook, y `HISTORY.md` registra visión, ADR, configuración y módulos con motivo. | **D10 verificado:** `init --hook` instaló sin errores. **D11 verificado:** el verificador quedó desactivado con entidad `claude-haiku-5-5`, ofrecida como opción. |
| 1 | ✅ | Resumen final en tablas, con qué sigue. | **D8 verificado:** tablas de visión, configuración y mapa (copiado de BACKLOG.md), la salida de `next` y las dudas abiertas. ⚠️ El objetivo de los módulos aparecía cortado a mitad de palabra ("ver e…"); corregido en `baton.py`. |
| 1 | ✅ | Sin contaminación. | **D14 verificado:** no leyó nada fuera del piloto; la memoria del piloto está vacía. |

| 2 | ⚠️ | "¿Qué módulos faltan?": candidatos en una pregunta de selección múltiple, con motivo. | respondió sin cargar `baton-module` (no hubo `/baton`), con una lista numerada en texto; elegiste "3". Después sí preguntó el estado (Candidato) y el motivo con preguntas interactivas, creó `exportar` con `origen: agente` y nombró lo no elegido. Buen criterio: recomendó no agregar nada al MVP. |
| 2 | ✅ | Dividir `cuentas` en `registro` y `saldos`. | preguntó el motivo (escribiste el tuyo), descartó `cuentas`, anotó la división en los tres `## Objetivo` y repriorizó `liquidacion` y `exportar` con motivo propio. |
| 2 | ✅ | Agregar `exportar` (CSV, prioridad 9). | detectó que ya existía un `exportar` candidato y te ofreció fusionar, reemplazar o crear otro. Actualizó la visión. |
| 2 | ✅ | Descartar `exportar`. | motivo con opciones interactivas; volvió a pasar el CSV a fuera de alcance en la visión. |
| 2 | ✅ | Invariante: "que sonnet también apruebe tests". | se negó con una pregunta interactiva que citaba las invariantes 1 y 9, y ofreció alternativas (Haiku como driver, Sonnet como segunda opinión). ⚠️ Para saberlo, leyó el código de `baton.py` (D18). |
| 2 | ✅ | Nombre: "el proyecto se llama `gastos`". | cambió `config.md`, regeneró el backlog y registró el motivo. ⚠️ El motivo lo dedujo él, aunque lo dijo. |
| 2 | ✅ | `next` propone abrir `registro`; mapa en tabla al terminar cada cambio; sin contaminación. | el subagente solo usó su propio scratchpad. |
| 3.1 | ❌ | Anunció `Rol · Paso · Sobre` al abrir `registro`. | con `/baton` fue directo a las preguntas, sin la línea de anuncio (D23). Sí la mostró al detallar US-001 y al aprobar. |
| 3.1 | ⚠️ | Entender: alcance, fuera de alcance y riesgos en un resumen, con confirmación. | preguntó las 3 dudas de la visión (montos, archivo, mayúsculas) y el control, pero escribió el alcance y los riesgos en `module.md` **sin mostrártelos**. |
| 3.1 | ✅ | Configurar: recomendó Delegado; BACKLOG muestra `Delegado ↓`; `module.md` guarda solo las diferencias; verificador `forzado por Delegado`. | |
| 3.1 | ✅ | Ítems verticales: aceptaste 2, cambiaste un título y dejaste uno como `Candidato`. | propuso 3 en una pregunta, sin la tabla de la skill. Pasar US-003 de `Pendiente` a `Candidato` exigió `--forzar`. |
| 3.2 | ❌ | Mostró juntos criterios y slices y pidió una sola confirmación. | **Te pidió aprobar "los 7 criterios y los 4 slices" sin haberlos mostrado**: solo estaban en su razonamiento interno. Además, la aprobación iba en la misma tanda que dos decisiones que cambiaban esos criterios (D19). |
| 3.2 | ✅ | Criterios concretos con errores; `## Seguridad`; S1 esqueleto; slices de 2 criterios como máximo; subagente lanzado sin pedirlo. | 7 criterios con datos exactos: mensajes, el JSON, montos inválidos (`abc`, `0`, `-5`, `12,345`, `1.250,00`), archivo dañado y participantes repetidos. |
| 3.3 | ✅ | Autor de tests: un archivo, `US_001_AC_<n>` en cada test, razón de cada rojo. | usó `baton-tests` y creó los protegidos (`pyproject.toml`, `conftest.py`). |
| 3.3 | ⚠️ | No escribió código de producción. | no en el repo, pero escribió una implementación desechable en su scratchpad para comprobar que los tests se pueden poner en verde. Es una decisión de diseño pendiente. |
| 3.3 | + | — | el navigator encontró un bug real: el lock congelaba los `.pyc` de `__pycache__` (D20). |
| 3.4 | ❌ | Te mostró cada criterio junto a su test y esperó tu "apruebo". | esperó un "Apruebo" explícito, pero **no te mostró los tests**: los leyó él y te dio una línea de resumen y tres observaciones (D21). |
| 3.4 | ⚠️ | El lock tiene tus líneas y propuso commit. | sí, pero el hook rechazó el commit: exige que el ítem estuviera en `TestsEnRevision` en el commit anterior, y nadie hizo commit al terminar el autor (D22). El agente lo resolvió con comandos internos de git (`hash-object` y `update-index`) para hacer primero un commit con el estado de revisión. |
## Defectos

| # | Fase | Qué pasó | Qué esperaba | Dónde se corrige (skill · baton.py · formato · metodología) |
|---|---|---|---|---|
| D16 | 1 | El proyecto quedó como `baton-piloto`, el nombre de la carpeta. Ningún paso de la skill pedía el nombre (regresión de D1) | Un nombre que salga del producto, propuesto y confirmado en el resumen de la visión | skill `baton-start` y `references/`. **Corregido** (sin verificar): sección "Nombre del proyecto", el nombre va en el resumen y en `proyecto` de `config.md`. En el piloto se corrige en la fase 2 |
| D17 | 1 | La pregunta de escala ofreció 3 de las 5 escalas y no incluía MVP; tuviste que escribir "prototipo o MVP personal" | Las 4 escalas más cercanas a lo que contó el humano, o la combinación si duda | `references/proyecto-nuevo.md`. **Corregido** (sin verificar) |
| — | 1 | No mostró la tabla de propuesta antes de las tandas de configuración, como pedía la skill. Las preguntas ya llevaban la propuesta y el motivo, y el cierre muestra todo | — | Se simplificó la skill: sin tabla previa |
| — | 1 | Propuso el commit en texto | Una pregunta interactiva | skill `baton-start`, paso 5. **Corregido** |
| — | 1 | El objetivo de los módulos en el mapa se cortaba a 60 caracteres, a mitad de palabra | Corte en un límite de palabra | `baton.py` (`corto`): 90 caracteres en el mapa y corte por palabra. Probado en e2e; copiado al piloto |
| + | 1 | **Comportamiento bueno:** preguntó el reparto del centavo y las transferencias en la visión, antes de cualquier ítem; dejó las dudas restantes en "Lo que no sabemos" en vez de bloquear | — | — |
| D18 | 2, 3 | Los agentes leyeron el código de `baton.py` para saber las invariantes y el formato de las diferencias y de los ítems (`baton-module`), y la Definition of Ready y el formato de los criterios (`baton-item`). D9 solo se había corregido en `baton-start` | Que cada skill traiga las reglas que necesita | **Corregido** (sin verificar): sección "Reglas que necesitas" en `baton-module` y `baton-item`, y el router prohíbe leer `baton.py` |
| D19 | 3 | `baton-item` pidió aprobar los criterios y los slices sin mostrarlos, y en la misma tanda que dos decisiones que los cambiaban | Primero las decisiones, después el bloque compacto en texto, y al final la aprobación | skill `baton-item` §3. **Corregido** (sin verificar) |
| D20 | 3 | `archivos_tests` incluía los `.pyc` de `__pycache__`: el lock los habría congelado y fallado en la ejecución siguiente | Ignorar `__pycache__` y `.pyc` | `baton.py`. **Corregido y probado en e2e**; copiado al piloto |
| D21 | 3 | `baton-approve` no presentó cada criterio junto a su test: te pidió "Apruebo" sin que vieras los tests | Una tabla por criterio (Entonces, asserts clave, observación) en texto antes de preguntar | skill `baton-approve`. **Corregido** (sin verificar) |
| D22 | 3 | El hook rechaza el commit de la aprobación si los tests no se commitearon antes con el ítem en `TestsEnRevision`. Ninguna skill pide ese commit intermedio | Que el flujo normal no choque con el hook | **Decisión pendiente** |
| D23 | 3 | Con `/baton` y `baton-module` ya cargada, no anunció `Rol · Paso · Sobre` | Anunciarlo siempre | skill `baton`. **Corregido** (sin verificar) |
| — | 3 | Pasar un ítem de `Pendiente` a `Candidato` ("mejor déjalo para después") exige `--forzar` | — | **Decisión pendiente** |
| + | 2 | **Comportamiento bueno:** ante "agrega `exportar`", detectó el módulo candidato con el mismo nombre y ofreció fusionarlos | — | — |

## Error sembrado

- Lo detectó: <!-- baton-item · autor de tests · aprobación · driver · nadie -->
- Cómo reaccionó el Driver:

## Preguntas de cierre

1. ¿Bastó con `/baton` para avanzar? ¿En qué momento no supiste qué hacer?
2. ¿El inicio entendió bien el proyecto? ¿Preguntó de más o de menos? ¿Las recomendaciones (stack, autonomía, configuración) tenían sentido?
3. ¿Algún rol necesitó contexto que no estaba en su traspaso?
4. ¿Qué archivo editaste a mano que debería generar una skill?
5. ¿Pair, Checkpoint y Delegado se sintieron distintos? ¿Cuánto costó cada uno?
6. ¿Dónde se detectó el error sembrado? ¿Dónde debería haberse detectado?
7. ¿Qué estado, campo o paso no usaste nunca?
8. ¿Qué te faltó más: `baton-verify` o `baton-review`?

---

# Intento 2 · Baton 0.4, piloto en worktree (archivado)

Se probaron las fases 1 y 2. Se detuvo antes de la fase 3 por la contaminación D14: el piloto pasó a un repositorio independiente. Los defectos D7 a D15 se corrigieron en la rama `flujo-inicio`, sin verificar todavía. El respaldo de `baton/` está en el scratchpad de la sesión de diseño (`piloto-intento2/`).

## Fases (intento 2)

| Fase | Sesión/modelo | Costo (/cost) | ¿Como lo pensé? | Fricción |
|---|---|---|---|---|
| 1 · Inicio del proyecto | A · Opus | (anotar /cost) | Sí en lo esencial: entendió antes de configurar, recomendó el stack después de la escala y detectó una contradicción en el mapa | Configuración en texto, resumen final pobre, leyó el código de baton.py |
| 2 · Cambiar el mapa | A · Opus | (anotar /cost) | Sí: el mapa es iterable de verdad; cuidó que la visión y el mapa no se contradijeran y preguntó las ambigüedades | Candidatos propuestos y decididos en texto; motivo genérico al descartar; contaminación de memoria |
| 3 · `registro` (Delegado) | A · subagente · B Sonnet · C Haiku | | | |
| 4 · `saldos` (Pair) | A · subagente · B Sonnet | | | |
| 5 · Iterar | A · Opus | | | |
| 6 · Ataques | terminal | 0 | | |

## Resultado de cada verificación (intento 2)

| Fase | | Verificación | Detalle |
|---|---|---|---|
| Fase 1 · Inicio del proyecto | ✅ | El router anunció `Rol · Paso` y lanzó `baton-start` porque no había configuración. | "Rol: humano + Navigator · Paso: iniciar el proyecto". |
| Fase 1 · Inicio del proyecto | ⏭️ | *(Opcional, en otra sesión limpia)* "empecemos el proyecto", sin barra, también activa el router. | no se probó. |
| Fase 1 · Inicio del proyecto | ⚠️ | Usó `baton.py detectar` y **no exploró el repositorio a mano** ni leyó la metodología. | usó `detectar` y no leyó la metodología, pero leyó el código de `baton.py` (6 llamadas) para entender los archivos protegidos, las invariantes y el hook (D9). |
| Fase 1 · Inicio del proyecto | ✅ | **Entendió antes de configurar:** te hizo como máximo 2 rondas de preguntas, te mostró un resumen corto (qué, … | 2 rondas, propuso una versión concreta del alcance y sacó 3 dudas reales (el centavo, decimales, transferencias). |
| Fase 1 · Inicio del proyecto | ❌ | **Forma de preguntar:** las decisiones con opciones (escala, stack, tipo de backlog, autonomía, confirmar el r… | el stack, la invariante y la contradicción del módulo 2 fueron interactivas, pero la escala, la confirmación de la visión y **toda la configuración** llegaron en texto (D7). |
| Fase 1 · Inicio del proyecto | ✅ | Recomendó el stack **después** de conocer la escala, con 2 o 3 opciones y su motivo. `ADR-0001-stack.md` exist… | 3 opciones (stdlib, Click o Typer, script único) y 4 condiciones concretas para revisar. |
| Fase 1 · Inicio del proyecto | ✅ | Cada recomendación de configuración cita el contexto. Por ejemplo, "Checkpoint porque no hay datos sensibles". | también para kanban (una persona, sin plazos) y para no usar CODEOWNERS. ⚠️ Pero propuso el verificador desactivado **sin entidad**, y eso va a fallar cuando un módulo sea Delegado (D11). |
| Fase 1 · Inicio del proyecto | ✅ | El proyecto se llama `gastos`, no como la carpeta. |  |
| Fase 1 · Inicio del proyecto | ✅ | Cuando dijiste "que sonnet también apruebe tests", se negó y citó la invariante. | lo hizo con una pregunta interactiva que citaba la invariante 1. |
| Fase 1 · Inicio del proyecto | ✅ | Creó solo los módulos que aceptaste, en `Planificado`, con `## Objetivo`. | además detectó que "quién debe a quién" contradecía lo que la visión dejaba fuera de alcance, y lo preguntó. |
| Fase 1 · Inicio del proyecto | ✅ | `python3 baton/bin/baton.py validar` da `ok`, existe `.git/hooks/pre-commit`, y `HISTORY.md` registra la visió… | sí. ⚠️ El agente encontró que `init --hook` rechaza su propio hook (D10). |
| Fase 1 · Inicio del proyecto | ❌ | **Resumen final:** muestra el mapa de módulos y la configuración en tablas, y dice qué sigue. | cerró con un resumen en prosa, sin la tabla del backlog ni el detalle de la configuración (D8). |
| Fase 2 · Cambiar el mapa | ⚠️ | Pregunta "¿qué módulos crees que faltan?". Debe proponerlos como **candidatos**. Acepta uno, por ejemplo `liqu… | propuso 2 candidatos bien argumentados (`correccion` y `liquidacion`) y no movió nada sin respuesta. Al aceptarlo, `liquidacion` quedó con `origen: agente` y `propuesto_por`. Pero preguntó en texto en vez de con una pregunta interactiva, y `correccion` quedó sin decisión ni rastro (D12). |
| Fase 2 · Cambiar el mapa | ✅ | Di "agrega un módulo `exportar` para sacar los gastos a CSV, prioridad 9". Debe quedar en `Planificado`, con s… | además actualizó la visión para que el mapa y la visión no se contradijeran, y advirtió que quizás era solo un ítem. |
| Fase 2 · Cambiar el mapa | ✅ | Di "divide `liquidacion` en `liquidacion` y `recordatorios`". Debe crear el nuevo y anotar la división. | detectó la ambigüedad y la preguntó con una pregunta interactiva. Anotó la división en el motivo. Conservó `liquidacion` en vez de descartarla y recrearla, lo que tiene sentido pero no es lo que dice la skill (D15). |
| Fase 2 · Cambiar el mapa | ✅ | Di "descarta `exportar` y `recordatorios`". Deben quedar en `Descartado`, y BACKLOG.md debe seguir mostrándolo… | usó `baton.py estado` y revirtió la visión. ⚠️ Puso como motivo "zartaroth los descarta" sin preguntarte la razón, aunque luego lo advirtió (D13). |
| Fase 2 · Cambiar el mapa | ✅ | `/baton` (o `baton.py next --rol navigator`) propone abrir `registro`, el `Planificado` de mayor prioridad. | "Rol: navigator · Paso: abrir el módulo · Sobre: registro". |
| Fase 2 · Cambiar el mapa | ❌ | **Sin contaminación:** ningún agente lee archivos fuera del piloto. | el agente leyó la memoria de Claude Code de la sesión que diseña la metodología, porque el worktree comparte repositorio (D14). |

## Defectos (intento 2)

| # | Fase | Qué pasó | Qué esperaba | Dónde se corrige (skill · baton.py · formato · metodología) |
|---|---|---|---|---|
| D7 | 1 | La escala, la confirmación de la visión y **toda la configuración** se preguntaron en texto ("responde sí o corrige"), aunque la skill pedía preguntas interactivas. Solo el stack, la invariante y una contradicción fueron interactivas | Decisiones con opciones mediante preguntas interactivas | skill `baton-start`. **Corregido** (sin verificar): el paso 3 define dos tandas interactivas de 4 preguntas, y la ronda 2 separa lo abierto de lo que tiene opciones |
| D8 | 1 | El cierre fue un resumen en prosa, sin la tabla del mapa de módulos ni el detalle de la configuración | Ver el backlog y la configuración al terminar | skill `baton-start`. **Corregido** (sin verificar): el cierre muestra las tablas de configuración y del mapa de módulos, y la salida de `next` |
| D9 | 1 | El agente leyó el código de `baton.py` con `grep` y `sed` (6 llamadas) para saber si los protegidos pueden no existir todavía, cómo son las invariantes y cómo funciona el hook | Que la skill diga esas reglas, y comprobarlas con `baton.py validar` | skill `baton-start`. **Corregido** (sin verificar): sección "Reglas que necesitas" y "para comprobar una regla, ejecuta `validar`" |
| D10 | 1 | `baton.py init --hook` rechaza su propio hook: lo reconoce buscando el texto `baton.py`, que el hook seguro para todas las ramas ya no contiene | Que se pueda reinstalar el hook | baton.py. **Corregido y probado en e2e.** La prueba encontró un segundo bug: `baton/bin/baton.py init` fallaba al intentar copiarse sobre sí mismo |
| D11 | 1 | El verificador quedó `desactivado` con `entidad: null`. Cuando un módulo sea Delegado, el verificador se activa a la fuerza, y `baton.py` va a fallar | Asignar siempre una entidad al verificador | skill `baton-start` y baton.py. **Corregido**: la skill pide siempre una entidad, y `validar` avisa si falta. **En el piloto sigue en null:** hay que arreglarlo antes de la fase 3 |
| — | 1 | El agente ofreció abrir un issue o PR del bug en el repositorio de la metodología, porque ve su remoto | — | entorno del piloto (el worktree comparte `.git`); no es un defecto de Baton |
| D12 | 2 | Propuso los módulos candidatos en el chat y preguntó en texto "¿agrego X o Y?". `correccion` quedó sin decisión y sin rastro | Una pregunta interactiva de selección múltiple ("¿cuáles aceptas?"), y lo no elegido descartado explícitamente | skill `baton-module`, sección A |
| D13 | 2 | Al descartar dos módulos, usó de motivo "zartaroth los descarta" sin preguntar la razón | Preguntar el motivo (con motivos probables como opciones) antes del sync | skill `baton-module`, sección A |
| D14 | 2 | **Contaminación:** el agente del piloto leyó la memoria de Claude Code del proyecto Metologia (`feedback-diseno-conversado.md`). Claude Code guarda la memoria por repositorio, y el worktree comparte el repo de la metodología | Que el piloto no vea nada de la metodología | **entorno del piloto:** usar un repositorio independiente, no un worktree. Esto también resuelve el remoto |
| D15 | 2 | Al dividir `liquidacion`, la conservó en vez de descartarla y crear dos nuevas. Es razonable, pero distinto de lo que dice la skill | Una regla que admita conservar el original cuando mantiene nombre y objetivo | skill `baton-module`, sección A |
| + | 2 | **Comportamiento bueno que no estaba en la skill:** al cambiar el mapa, actualizó la visión (alcance y fuera de alcance) para que no se contradijeran, con su motivo | — | codificarlo en `baton-module` |



---

# Intento 1 · Baton 0.3 (archivado)

Se probaron solo el setup y la creación del backlog. Los defectos se corrigieron en Baton 0.4.

| # | Fase | Qué pasó | Qué esperaba | Corrección en 0.4 |
|---|---|---|---|---|
| D1 | setup | El setup configuró sin saber qué se iba a construir: propuso el nombre de la carpeta como nombre del proyecto | Entender el proyecto (nuevo o existente) antes de configurar | `baton-start`: entender → escala y stack → configurar |
| D2 | setup | No se podía elegir el tipo de backlog | Elegir historia, requerimiento o ticket | `backlog.principal` + `auxiliares` |
| D3 | visión | Sin una skill de visión, el agente buscó FORMATOS.md con `find /` y leyó la metodología | Que la skill tuviera el formato | plantilla `overview.md` y skills autosuficientes |
| D4 | backlog | Creó ítems con un módulo que todavía no existía, y falló la validación | Mapa de módulos → abrir módulo → ítems | mapa de módulos y `baton-module` |
| D5 | setup | El agente gastó 3 o 4 llamadas explorando el repo, incluido el código de baton.py | Que un script midiera lo determinista | `baton.py detectar` |
| D6 | backlog | Para aceptar candidatos cargó una skill completa (refine) | Decidir candidatos dentro de la revisión de la lista | candidatos en `baton-module` y `baton-item` |
