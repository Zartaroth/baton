---
name: baton-next
description: Responde "¿qué me toca?" en la metodología Baton. Lee los estados de los ítems y los traspasos pendientes y dice qué rol tiene el turno y sobre qué, sin depender de la conversación. Con "toma tu turno", toma el siguiente trabajo del rol de esta sesión y ejecuta la skill que corresponde. Úsala al abrir una sesión nueva o cuando no esté claro qué sigue.
---

# baton-next

**Rol:** cualquiera. **Entrada:** los estados y los traspasos. **Salida:** qué toca y, con "toma tu turno", el trabajo ya iniciado.

## Pasos

1. Ejecuta `python3 baton/bin/baton.py next`. Si sabes el rol o la entidad de esta sesión, filtra con `--rol <rol>` y/o `--entidad <entidad>`.
2. Muestra el resultado ordenado por prioridad. Por cada ítem: estado, slice siguiente, traspaso pendiente y si está bloqueado por WIP.
3. Si el humano dice **"toma tu turno"**:
   1. Averigua el rol de esta sesión. Puede estar en la instrucción, en el traspaso que te pasaron o en `config.md` según tu entidad. Si no está claro, pregunta.
   2. Toma el primer ítem de ese rol que no esté bloqueado y que tenga un traspaso `Pendiente` dirigido a ti.
   3. Ejecuta la skill que corresponde:

| Estado del ítem | Rol | Skill |
|---|---|---|
| Candidato, Pendiente | navigator | `baton-refine`, luego `baton-plan` |
| Escalado | navigator | lee la solicitud abierta, presenta la decisión al humano y aplícala (ver abajo) |
| Listo | autor_tests | `baton-tests` |
| TestsEnRevision | aprobador_tests | `baton-approve` |
| TestsCongelados, EnCurso | driver | `baton-drive` |
| EnVerificacion | verificador | `baton-verify` (si no está instalada: revisa el reporte, el diff y el lock y escribe el veredicto en `## Verificación`) |
| EnRevision | humano | muestra los reportes de slice y pide la decisión |

## Decidir un escalamiento (Navigator)

1. Presenta al humano la solicitud (qué pasa, evidencia, propuesta) con tu recomendación.
2. Escribe la decisión en `## Decisión`, junto con `decidida_por` y `decidida`.
3. Aplícala:
   - **Aprobada, de tipo `test` o `criterio`:** ejecuta `estado <ítem>-R<n> Aprobada`, ajusta el ítem si cambia un criterio (retíralo con `~~`, no lo borres), ejecuta `estado <ítem> Listo` y crea un traspaso para `autor_tests`.
   - **Aprobada, de tipo `diseno` o `plan`:** actualiza el plan o el ADR, ejecuta `estado <ítem>-R<n> Aplicada` y `estado <ítem> TestsCongelados`, y crea un traspaso para `driver`.
   - **Rechazada:** ejecuta `estado <ítem>-R<n> Rechazada` y `estado <ítem> TestsCongelados`, y crea un traspaso para `driver` con la explicación.
4. Ejecuta sync con el motivo de la decisión.

## No hagas

- No tomes trabajo de otro rol aunque esté libre. Que dos roles trabajen sobre lo mismo rompe los turnos.
- No saltes el límite de WIP sin que el humano lo decida.
