---
name: baton-item
description: Detalla justo a tiempo un ítem de la metodología Baton. En un solo paso escribe su propósito, los criterios de aceptación Dado/Cuando/Entonces y la revisión de seguridad, y lo divide en slices verticales (el primero es un esqueleto andante). Pide una sola confirmación, marca el ítem como Listo y entrega el turno al autor de tests. Úsala cuando un ítem Pendiente de un módulo activo está por desarrollarse, o para cambiar su plan.
---

# baton-item

**Rol:** Navigator. El agente propone y **el humano decide**.

**Entrada:** un ítem `Pendiente` de un módulo `Activo`, la visión, los ADR y el `module.md`.

**Salida:**
- el ítem detallado;
- `baton/modules/<m>/plans/<ítem>.md`;
- el ítem en `Listo`;
- el traspaso al autor de tests.

No leas la documentación de la metodología: lo necesario está aquí y en `baton/templates/`.

## Cómo preguntar

- **Decisiones con opciones** (elegir entre alternativas, aceptar o descartar, mantener o cambiar, confirmar un resumen): usa la herramienta de preguntas interactivas de tu entorno, si la tiene (en Claude Code, `AskUserQuestion`). Pon tu recomendación como primera opción, marcada "(Recomendado)", con una línea de por qué. Agrupa hasta 4 preguntas por tanda.
- **Preguntas abiertas** (qué es el proyecto, para quién, el motivo de un cambio): hazlas en texto, todas juntas en un solo mensaje. No las fuerces a opciones.
- **Sin herramienta interactiva:** usa una lista numerada con las opciones y la recomendada marcada.
- Si el humano responde algo distinto de las opciones, tómalo como una corrección y no como un error.

## 1. Detallar el ítem

1. Lee el ítem, su `module.md`, la visión y los ADR relevantes.
2. **Propósito**, según el `tipo`. La plantilla `baton/templates/item-<tipo>.md` tiene las secciones:

   | Tipo | Sección | Forma |
   |---|---|---|
   | historia | `## Valor` | "Como <rol> quiero <acción> para <beneficio>" |
   | requerimiento | `## Requerimiento` y `## Justificación` | "El sistema debe…" |
   | ticket | `## Descripción` | |
   | bug | `## Comportamiento esperado`, `## Comportamiento actual` y `## Pasos para reproducir` | |
   | tecnico | `## Motivo` | |

3. **Criterios** (`## Criterios de aceptación`):
   - uno por comportamiento observable, con formato `### AC-<n> · <nombre>` y viñetas **Dado** / **Cuando** / **Entonces** (y **Y**);
   - datos concretos: "un carrito con 2 productos por $30", no "un carrito con productos";
   - el **Entonces** se comprueba desde afuera (respuesta, pantalla, archivo, salida), no por detalles internos;
   - incluye el caso feliz, los errores esperables y los bordes (vacío, límite, duplicado, sin permiso);
   - en un **bug**, el AC-1 reproduce el error.
4. **Seguridad** (`## Seguridad`). Revisa:
   - autenticación y autorización;
   - validación de entradas;
   - datos sensibles;
   - inyección;
   - abuso;
   - auditoría.

   Considera las restricciones de la visión. Si no hay impacto, escribe "sin impacto". Lo que encuentres como requisito se convierte en criterio.
5. **Ambigüedades.** Lo que no puedas decidir va a `## Preguntas abiertas`. Pregúntaselo al humano con opciones y tu recomendación. Nunca resuelvas tú una pregunta de negocio.
6. **Propuestas.** Las mejoras fuera del alcance del ítem no van como criterios. Créalas como ítems `Candidato` (`origen: agente`, `propuesto_por`, `## Por qué se propone`).

## 2. Dividir en slices

1. Consulta `slice_max` con `python3 baton/bin/baton.py efectiva <ítem>`.
2. Divide en slices **verticales**: cada uno atraviesa las capas necesarias y termina en algo que se puede ejecutar.
   - **S1 es el esqueleto andante:** el camino más delgado de punta a punta. Si es el primer ítem del primer módulo, S1 también deja montado el proyecto: estructura, runner de tests y lo mínimo del stack del ADR-0001.
   - Cada criterio vigente va en **exactamente un** slice.
   - Ningún slice supera `slice_max.criterios` ni se revisa en más de `slice_max.minutos`.
3. Cada slice lleva **Recorrido**, **Fuera de este slice**, **Demo** (pasos concretos y lo que se debe ver), **Decisiones que aplican** (ADR) y **Escalar si** (dónde debe detenerse el Driver). La plantilla es `baton/templates/plan.md`.
4. Si hace falta una decisión de diseño nueva, propónla. Cuando el humano la apruebe, escríbela como ADR.

## 3. Una sola confirmación

**El humano solo aprueba lo que tiene en pantalla.** El orden es este:

1. **Primero, las decisiones abiertas** (las que cambian criterios): resuélvelas en una tanda interactiva. No incluyas la aprobación en esa tanda, porque sus respuestas cambian lo que se aprueba.
2. **Después, muestra en un mensaje de texto** los criterios y los slices juntos, ya con esas decisiones aplicadas. Cada criterio va en una línea con su **Entonces** concreto (el dato, el mensaje o el archivo que se comprueba), no solo con su nombre. Lo que escribiste en tu razonamiento interno no cuenta: el humano no lo ve.
3. **Recién entonces, pide la aprobación** con una pregunta interactiva aparte.

Forma compacta del mensaje:

```
US-001 · Registrar gasto
AC-1 Gasto válido … · AC-2 Monto inválido … · AC-3 …
S1 (AC-1) esqueleto: CLI → lógica → JSON · S2 (AC-2, AC-3) validaciones
Seguridad: … · Preguntas abiertas: ninguna
¿Apruebas, o ajusto algo?
```

Pide la confirmación con una pregunta interactiva ("Apruebo" o "Ajustar…"). Ajusta hasta que el humano apruebe, y recién entonces escribe el ítem y el plan.

### Reglas que necesitas (no leas el código de `baton.py`)

- **Criterios:** `baton.py` los reconoce por el encabezado `### AC-<n> · <nombre>` dentro de `## Criterios de aceptación`. Un criterio retirado lleva `~~` en el título.
- **Definition of Ready** (lo que exige `estado <ítem> Listo`):
  - la sección de propósito de su tipo, con contenido;
  - al menos un criterio vigente, y cada uno con Dado, Cuando y Entonces;
  - `## Seguridad` escrita;
  - `## Preguntas abiertas` vacía o "Ninguna";
  - el plan en `baton/modules/<m>/plans/<ítem>.md`;
  - el módulo en `Activo`.
- Si dudas de un comando, usa `python3 baton/bin/baton.py <comando> --help`. Para comprobar reglas, `validar`.

## 4. Registrar y entregar

1. Ejecuta `python3 baton/bin/baton.py estado <ítem> Listo`. Si falla, el mensaje dice qué falta de la Definition of Ready.
2. Ejecuta `python3 baton/bin/baton.py handoff --item <ítem> --de navigator --para autor_tests --entidad-de <tu entidad>`. Completa en el traspaso `## Qué se entrega`, `## Qué se espera` y `## Contexto`.
3. Ejecuta `python3 baton/bin/baton.py sync --autor <entidad> --motivo "<ítem> detallado"`.
4. Según el `transporte` del autor de tests:
   - `subagente`: lánzalo con el traspaso como instrucción;
   - `sesion`: el humano abre otra sesión y le dice "toma tu turno";
   - `externo`: otra herramienta lee el traspaso.

## Candidatos

Si el ítem está en `Candidato`, muéstralo con `## Por qué se propone` y pregunta. Si el humano lo acepta: `baton.py estado <ítem> Pendiente`. Si lo descarta: `baton.py estado <ítem> Descartado`. Si hay varios, decídelos en una sola pregunta.

## Cambiar un ítem o plan ya en desarrollo

- **Criterios ya congelados** (el ítem estuvo en `TestsCongelados` o después): no se editan sin una solicitud aprobada. Un criterio que sobra se retira: se tacha su título con `~~` y se anotan la fecha y la solicitud. Nunca se borra ni se renumera.
- **Plan:** sube `version`. Los slices `Terminado` o `Aprobado` no se modifican, y los ids de slice no se reutilizan. Mover criterios entre slices no obliga a tocar los tests.
- Ejecuta sync con el motivo.

## No hagas

- No escribas tests ni código.
- No marques `Listo` sin la confirmación del humano.
