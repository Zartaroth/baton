---
name: baton
description: 'Punto de entrada único de la metodología Baton (comando /baton). Úsala para empezar un proyecto ("empecemos", "inicia el proyecto", "start") y para avanzar ("continúa", "siguiente", "¿qué sigue?", "toma tu turno"). Lee el estado (mapa de módulos, ítems y traspasos), anuncia qué rol tiene el turno y qué paso toca, y ejecuta la skill correspondiente: si el proyecto no está iniciado, lanza baton-start. También resuelve los escalamientos del Navigator. Úsala siempre que no esté claro qué skill de Baton usar.'
---

# baton

**Rol:** cualquiera. Es el **router**: el humano solo necesita recordar `/baton`, que sirve igual para empezar un proyecto vacío y para seguir a mitad del trabajo. Las demás skills se pueden seguir llamando directamente (`/baton-start`, `/baton-item`, etc.).

## Pasos

1. Si no existe `baton/config.md`, el proyecto no empezó: ejecuta `baton-start`.
2. Ejecuta `python3 baton/bin/baton.py next`. Si sabes el rol o la entidad de esta sesión, filtra con `--rol <rol>` y/o `--entidad <entidad>`.
3. **Anuncia siempre en una línea quién actúa y qué paso toca:** `Rol: <rol> · Paso: <qué> · Sobre: <módulo o ítem>`. Que haya un router no debe ocultar qué rol está actuando.
4. Si el humano invocó `/baton` sin más, o dijo "empecemos", "continúa" o "toma tu turno":
   1. Averigua el rol de esta sesión. Puede estar en la instrucción, en el traspaso o en `config.md` según tu entidad. Si no está claro, pregunta.
   2. Toma la primera tarea de ese rol que no esté bloqueada: primero las del mapa de módulos y después los ítems por prioridad, con un traspaso `Pendiente` dirigido a ti si corresponde.
   3. Ejecuta la skill que corresponde:

| Situación | Rol | Skill |
|---|---|---|
| No hay `baton/config.md` | humano + Navigator | `baton-start` |
| Mapa de módulos vacío, módulo `Candidato`, siguiente módulo `Planificado`, módulo sin ítems abiertos, ítems sin módulo | navigator | `baton-module` |
| Ítem `Pendiente` o `Candidato` de un módulo `Activo` | navigator | `baton-item` |
| Ítem `Escalado` | navigator | decidir el escalamiento (ver abajo) |
| `Listo` | autor_tests | `baton-tests` |
| `TestsEnRevision` | aprobador_tests | `baton-approve` |
| `TestsCongelados`, `EnCurso` | driver | `baton-drive` |
| `EnVerificacion` | verificador | `baton-verify`. Si no está instalada: revisa el reporte, el diff y el lock, y escribe el veredicto en `## Verificación` del reporte |
| `EnRevision` | humano | muestra los reportes de slice y pide la decisión |

5. Si el humano solo preguntó "¿qué sigue?", muestra lo que toca para cada rol, ordenado por prioridad, y espera.

## Decidir un escalamiento (Navigator)

1. Presenta al humano la solicitud abierta (qué pasa, evidencia, propuesta). Pide la decisión con una pregunta interactiva, si tu entorno la tiene: las opciones son las alternativas, con tu recomendación primero.
2. Escribe la decisión en `## Decisión`, junto con `decidida_por` y `decidida`.
3. Aplícala:
   - **Aprobada, de tipo `test` o `criterio`:** ejecuta `estado <ítem>-R<n> Aprobada` y ajusta el criterio en el ítem (retíralo con `~~`, no lo borres). Luego `estado <ítem> Listo` y un traspaso para `autor_tests`.
   - **Aprobada, de tipo `diseno` o `plan`:** actualiza el plan o el ADR. Luego `estado <ítem>-R<n> Aplicada`, `estado <ítem> TestsCongelados` y un traspaso para `driver`.
   - **Rechazada:** `estado <ítem>-R<n> Rechazada`, `estado <ítem> TestsCongelados` y un traspaso para `driver` con la explicación.
4. Ejecuta sync con el motivo de la decisión.

## No hagas

- No tomes trabajo de otro rol aunque esté libre. Que dos roles trabajen sobre lo mismo rompe los turnos.
- No saltes el límite de WIP sin que el humano lo decida.
