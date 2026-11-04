---
name: baton-module
description: Maneja los módulos de la metodología Baton. Edita el mapa de módulos (agregar, dividir, fusionar, descartar, priorizar, aceptar candidatos) y abre un módulo para desarrollarlo. Al abrirlo, entiende su alcance y riesgos, recomienda la configuración según el riesgo y define con el humano la lista de ítems del módulo. Úsala para abrir el siguiente módulo, cambiar el mapa, reconfigurar un módulo o cerrarlo, y también ante preguntas como "¿qué módulos faltan?" o "¿qué más agregarías?".
---

# baton-module

**Rol:** Navigator. El agente entiende, propone y recomienda. **El humano decide.**

**Entrada:** la visión (`baton/system/overview.md`), los ADR, `baton/config.md` y el mapa de módulos (la tabla "Mapa de módulos" de `baton/backlog/BACKLOG.md`).

**Plantillas:** `baton/templates/module.md` y `baton/templates/item-<tipo>.md`. No leas la documentación de la metodología: lo necesario está aquí.

## Cómo preguntar

- **Decisiones con opciones** (elegir entre alternativas, aceptar o descartar, mantener o cambiar, confirmar un resumen): usa la herramienta de preguntas interactivas de tu entorno, si la tiene (en Claude Code, `AskUserQuestion`). Pon tu recomendación como primera opción, marcada "(Recomendado)", con una línea de por qué. Agrupa hasta 4 preguntas por tanda.
- **Preguntas abiertas** (qué es el proyecto, para quién, el motivo de un cambio): hazlas en texto, todas juntas en un solo mensaje. No las fuerces a opciones.
- **Sin herramienta interactiva:** usa una lista numerada con las opciones y la recomendada marcada.
- Si el humano responde algo distinto de las opciones, tómalo como una corrección y no como un error.

Pregunta qué quiere hacer el humano, o dedúcelo de `python3 baton/bin/baton.py next --rol navigator`:

## A. Cambiar el mapa de módulos

El mapa es iterable: casi nunca se conocen todos los módulos al empezar.

| Acción | Cómo |
|---|---|
| Agregar | nuevo `baton/modules/<m>/module.md` con `estado: Planificado`, `prioridad` y `## Objetivo` |
| Aceptar o descartar un candidato | `baton.py estado modulo:<m> Planificado` o `baton.py estado modulo:<m> Descartado` |
| Repriorizar | edita `prioridad` en los `module.md` |
| Dividir | Si el original **conserva su nombre y su objetivo**, se mantiene, y se crean solo los nuevos. Si no, crea todos los módulos resultantes y descarta el original. En los dos casos, mueve los ítems (campo `modulo`) y anota la división en el `## Objetivo` de los módulos involucrados ("separado de X", "dividido en X e Y") |
| Fusionar | mueve los ítems al módulo que queda y descarta el otro con una nota |
| Descartar | `baton.py estado modulo:<m> Descartado`. Sus ítems no hechos pasan a `Descartado` o a otro módulo, según decida el humano |

**Proponer módulos** (por ejemplo, ante "¿qué falta?"):
1. Explica cada propuesta en una línea, con su motivo.
2. Pregunta con **una pregunta interactiva de selección múltiple**: "¿Cuáles agrego al mapa?", con una opción por módulo y la recomendada marcada.
3. Lo **elegido** se crea en `Planificado` (`origen: agente`, `propuesto_por`, `## Por qué se propone`). Si el humano dice "para después", se crea en `Candidato`.
4. Lo **no elegido** no se crea, y se menciona en el cierre como descartado.

Nunca agregues una propuesta sin respuesta del humano.

**Motivos:** cada cambio del mapa necesita un motivo de fondo, no "el humano lo pidió". Si el humano no lo dio, pregúntalo antes del sync, con motivos probables como opciones interactivas.

**Visión coherente:** si el cambio mueve algo dentro o fuera del alcance (un módulo nuevo, uno descartado), actualiza `## Alcance inicial` y `## Fuera de alcance` de `baton/system/overview.md`, con el mismo motivo. El mapa y la visión nunca deben contradecirse.

Al terminar, ejecuta `baton.py sync` **con el motivo de cada cambio** y muestra la tabla "Mapa de módulos" de `BACKLOG.md`.

## B. Abrir un módulo

Por defecto, el siguiente `Planificado` por prioridad. Se prepara todo y se aprueba **una sola vez**, como en `baton-item`: preguntas abiertas → propuesta completa a la vista → una aprobación.

### 1. Preparar la propuesta

1. **Entender.** A partir de la visión y del `## Objetivo`, prepara `## Alcance`, `## Fuera de alcance`, `## Riesgos` y `## Referencias` (ADR y contratos que aplican). Para los riesgos, evalúa si el módulo:
   - mueve dinero o datos personales;
   - toca autenticación o permisos;
   - migra datos;
   - integra servicios externos;
   - es reversible;
   - es una zona donde el equipo tiene poca experiencia.

   Si necesita una decisión de diseño nueva, propónla como ADR (`baton/templates/adr.md`).
2. **Configurar.** Consulta la configuración heredada con `baton.py efectiva modulo:<m>` y **recomienda según el riesgo**, con el motivo en una línea. Por ejemplo: pagos, seguridad o migraciones → Pair; CRUD interno → Delegado. Roles y tamaño de slice se mantienen salvo que el riesgo pida otra cosa.
3. **Ítems.** Prepara la lista:
   - Usa el **tipo principal** de `config.md` (`backlog.principal`). Usa los auxiliares (`bug`, `tecnico`) solo cuando corresponda.
   - Incluye los ítems semilla que ya existan con ese `modulo`, y los ítems sin módulo que encajen.
   - Divide en ítems **verticales**, que entregan algo usable, y no por capas.
   - Revisa que cada ítem cumpla **INVEST**: independiente, negociable, valioso, estimable, pequeño y testeable. Si un ítem parece de más de unos 6 criterios, propón dividirlo.

### 2. Preguntas abiertas (si las hay)

Lo que no puedas deducir (dudas de negocio de la visión que este módulo necesita, la autonomía si hay alternativas reales) va **primero**, en una tanda interactiva. No incluyas la aprobación en esa tanda: sus respuestas cambian la propuesta.

### 3. Mostrar y aprobar una vez

1. **Muestra en un mensaje de texto** la propuesta completa, ya con las respuestas aplicadas:
   - **Alcance** y **fuera de alcance**: 2 o 3 líneas cada uno.
   - **Riesgos:** los que encontraste, en una línea cada uno.
   - **Configuración:** la autonomía y el verificador recomendados, con el motivo, y lo que cambia respecto del proyecto (marca ↓ si baja el control).
   - **Ítems:** una tabla con id, tipo, título, una línea de propósito y prioridad.

   Lo que solo pensaste y no mostraste no cuenta: el humano no lo ve.
2. **Pide la aprobación** con una pregunta interactiva: "Apruebo", "Ajustar…" y, si aplica, "Dejar algún ítem como candidato". Ajusta hasta que apruebe.
3. **Si el humano elige menos control que el recomendado,** avísale **una vez** con el riesgo concreto, anótalo en `## Riesgos` y respeta su decisión. Bajar el control está permitido. Solo comprueba que no quede bajo `autonomia_minima`.
4. Recién entonces escribe:
   - `module.md`: las secciones, y en `config` **solo las diferencias**, cada una como `{ valor, motivo, desde: <hoy> }`. Si la autonomía queda en Delegado, el verificador se activa solo: confirma que haya una entidad asignada;
   - los ítems **aceptados**, como ítems ligeros desde `baton/templates/item-<tipo>.md`: el frontmatter completo, la sección de propósito en una línea, `estado: Pendiente` y el siguiente número libre de su prefijo;
   - los que el humano quiera guardar para después, en `Candidato`. Lo que rechace no se crea.

### 4. Activar y registrar

1. Ejecuta `python3 baton/bin/baton.py estado modulo:<m> Activo` y `python3 baton/bin/baton.py validar`.
2. Ejecuta `python3 baton/bin/baton.py sync --autor <persona> --motivo "apertura del módulo <m>" --ref baton-module`. Si alguna diferencia de configuración tiene un motivo propio, pásalo con `--motivo-de`.
3. Resume la configuración efectiva (marca ↓ si se bajó el control) y los ítems aceptados. Indica el siguiente paso: "detallar `<primer ítem>`; escribe **`/baton`** (o "continúa")".

## C. Reconfigurar a mitad del módulo

- Cambia solo lo que el humano pida, con `desde` igual a la fecha de hoy y su motivo.
- El cambio aplica desde el **siguiente** slice. Los traspasos ya creados conservan su `config_efectiva`.

## D. Cerrar el módulo

1. Cuando no quedan ítems abiertos, `baton.py next` lo indica.
2. Si la autonomía es Delegado, presenta al humano los reportes de slice del módulo para la revisión final.
3. Ejecuta `python3 baton/bin/baton.py estado modulo:<m> Cerrado`. El comando rechaza el cierre si quedan ítems en desarrollo.
4. Ejecuta sync con el motivo.

## Reglas que necesitas (no leas el código de `baton.py`)

- **Archivos:**
  - el módulo va en `baton/modules/<m>/module.md`, donde `<m>` es el campo `modulo`;
  - el ítem va en `baton/backlog/items/<ID>.md`, donde el nombre del archivo es su `id`;
  - el id es el prefijo de `tipos` en `config.md` más un número de 3 cifras (`US-001`).
- **Diferencias de configuración** en `module.md`:
  ```yaml
  config:
    autonomia: { valor: Delegado, motivo: "...", desde: 2026-11-03 }
  ```
  Claves permitidas: `autonomia`, `roles.<rol>`, `roles.verificador.activo`, `slice_max.criterios` y `slice_max.minutos`.
- **Estados de módulo:**
  - `Candidato` pasa a `Planificado` o `Descartado`;
  - `Planificado` pasa a `Activo` o `Descartado`;
  - `Activo` pasa a `Cerrado` o vuelve a `Planificado`;
  - `Cerrado` pasa a `Activo` (reabrir);
  - `Descartado` vuelve a `Planificado`.
- **Invariantes de roles:**
  - el driver no escribe ni aprueba tests de aceptación;
  - el autor y el aprobador de tests son entidades distintas;
  - entre los aprobadores hay al menos una persona;
  - el verificador no es el driver;
  - Delegado activa el verificador.
- Si dudas de un comando, usa `python3 baton/bin/baton.py <comando> --help`. Para comprobar reglas, `validar`.

## No hagas

- No detalles criterios aquí: eso lo hace `baton-item`, justo a tiempo, ítem por ítem.
- No abras más de un módulo a la vez salvo que el humano lo pida. Así el trabajo en curso se mantiene chico.
- No copies en `module.md` valores iguales a los del proyecto.
- No uses la recomendación de riesgo para bloquear la decisión del humano.
