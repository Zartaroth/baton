# Bitácora del piloto

Proyecto: `gastos` · Guía: [GUIA-PILOTO.md](GUIA-PILOTO.md)

# Intento 3 · Baton 0.4, piloto en un repositorio independiente

Empieza el 2026-11-03, alrededor de las 18:20. Las sesiones de este intento son las de `~/.claude/projects/-home-zartaroth-Proyectos-baton-piloto/` creadas desde esa hora.

## Fases

| Fase | Sesión/modelo | Costo (/cost) | ¿Como lo pensé? | Fricción |
|---|---|---|---|---|
| 1 · Inicio del proyecto | A · Opus | | | |
| 2 · Cambiar el mapa | A · Opus | | | |
| 3 · `registro` (Delegado) | A · subagente · B Sonnet · C Haiku | | | |
| 4 · `saldos` (Pair) | A · subagente · B Sonnet | | | |
| 5 · Iterar | A · Opus | | | |
| 6 · Ataques | terminal | 0 | | |

## Defectos

| # | Fase | Qué pasó | Qué esperaba | Dónde se corrige (skill · baton.py · formato · metodología) |
|---|---|---|---|---|

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
