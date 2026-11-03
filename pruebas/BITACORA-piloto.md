# Bitácora del piloto

Proyecto: `gastos` · Guía: [GUIA-PILOTO.md](GUIA-PILOTO.md)

# Intento 2 · Baton 0.4 (flujo de inicio)

## Fases

| Fase | Sesión/modelo | Costo (/cost) | ¿Como lo pensé? | Fricción |
|---|---|---|---|---|
| 1 · Inicio del proyecto | A · Opus | (anotar /cost) | Sí en lo esencial: entendió antes de configurar, recomendó el stack después de la escala y detectó una contradicción en el mapa | Configuración en texto, resumen final pobre, leyó el código de baton.py |
| 2 · Cambiar el mapa | A · Opus | (anotar /cost) | Sí: el mapa es iterable de verdad; cuidó que la visión y el mapa no se contradijeran y preguntó las ambigüedades | Candidatos propuestos y decididos en texto; motivo genérico al descartar; contaminación de memoria |
| 3 · `registro` (Delegado) | A · subagente · B Sonnet · C Haiku | | | |
| 4 · `saldos` (Pair) | A · subagente · B Sonnet | | | |
| 5 · Iterar | A · Opus | | | |
| 6 · Ataques | terminal | 0 | | |

## Defectos

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


## Error sembrado

- Lo detectó: <!-- baton-item · autor de tests · aprobación · driver · nadie -->
- Cómo reaccionó el Driver:

## Preguntas de cierre

1. ¿Decir "continúa" bastó para avanzar? ¿En qué momento no supiste qué hacer?
2. ¿El inicio entendió bien el proyecto? ¿Preguntó de más o de menos? ¿Las recomendaciones (stack, autonomía, configuración) tenían sentido?
3. ¿Algún rol necesitó contexto que no estaba en su traspaso?
4. ¿Qué archivo editaste a mano que debería generar una skill?
5. ¿Pair, Checkpoint y Delegado se sintieron distintos? ¿Cuánto costó cada uno?
6. ¿Dónde se detectó el error sembrado? ¿Dónde debería haberse detectado?
7. ¿Qué estado, campo o paso no usaste nunca?
8. ¿Qué te faltó más: `baton-verify` o `baton-review`?

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
