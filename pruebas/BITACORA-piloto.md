# Bitácora del piloto

Proyecto: `gastos` · Guía: [GUIA-PILOTO.md](GUIA-PILOTO.md)

## Fases

| Fase | Sesión/modelo | Costo (/cost) | ¿Como lo pensé? | Fricción |
|---|---|---|---|---|
| 1 · Inicio del proyecto | A · Opus | | | |
| 2 · Abrir `registro` | A · Opus | | | |
| 3 · Cambiar el mapa | A · Opus | | | |
| 4 · registro (Delegado) | A · subagente · B Sonnet · C Haiku | | | |
| 5 · saldos (Pair) | A · subagente · B Sonnet | | | |
| 6 · Candidato y configuración | A · Opus | | | |
| 7 · Ataques | terminal | 0 | | |

## Defectos

| # | Fase | Qué pasó | Qué esperaba | Dónde se corrige (skill · baton.py · formato · metodología) |
|---|---|---|---|---|
| D1 | 1 (intento 1) | El setup configuró sin saber qué se iba a construir: propuso el nombre de la carpeta como nombre del proyecto | Entender el proyecto (nuevo o existente) antes de configurar | skill · metodología. **Corregido** en `flujo-inicio`: `baton-start` |
| D2 | 1 (intento 1) | No se podía elegir el tipo de backlog (historia, requerimiento o ticket) | Elegirlo al inicio | formato · baton.py. **Corregido**: `backlog.principal` + `auxiliares` |
| D3 | 2 (intento 1) | Sin una skill de visión, el agente buscó FORMATOS.md con `find /` y leyó la metodología | Que la skill tuviera el formato | skill · plantilla. **Corregido**: plantilla `overview.md` y skills autosuficientes |
| D4 | 2 (intento 1) | Creó ítems con un módulo que todavía no existía; falló la validación | El orden: mapa de módulos → abrir módulo → ítems | metodología. **Corregido**: mapa de módulos y `baton-module` |
| D5 | 1 (intento 1) | El agente gastó 3 o 4 llamadas explorando el repo, incluido el código de baton.py | Que lo determinista lo midiera un script | baton.py. **Corregido**: `baton.py detectar` |
| D6 | 2 (intento 1) | Para aceptar candidatos cargó una skill completa (refine) | Decidir candidatos dentro de la revisión de la lista | skill. **Corregido**: candidatos en `baton-module` y `baton-item` |

## Error sembrado

- Lo detectó: <!-- baton-item · autor · aprobación · driver · nadie -->
- Cómo reaccionó el Driver:

## Preguntas de cierre

1. ¿Algún rol necesitó contexto que no estaba en su traspaso?
2. ¿Qué archivo editaste a mano que debería generar una skill?
3. ¿Qué pregunta de un agente sobró, y cuál faltó?
4. ¿Pair, Checkpoint y Delegado se sintieron distintos? ¿Cuánto costó cada uno?
5. ¿Dónde se detectó el error sembrado? ¿Dónde debería haberse detectado?
6. ¿Qué estado, campo o paso no usaste nunca?
7. ¿Qué te faltó más: `baton-verify`, `baton-review` o una skill de visión?
