---
name: baton-module
description: Maneja los módulos de la metodología Baton. Edita el mapa de módulos (agregar, dividir, fusionar, descartar, priorizar, aceptar candidatos) y abre un módulo para desarrollarlo. Al abrirlo, entiende su alcance y riesgos, recomienda la configuración según el riesgo y define con el humano la lista de ítems del módulo. Úsala para abrir el siguiente módulo, cambiar el mapa, reconfigurar un módulo o cerrarlo.
---

# baton-module

**Rol:** Navigator. El agente entiende, propone y recomienda. **El humano decide.**

**Entrada:** la visión (`baton/system/overview.md`), los ADR, `baton/config.md` y el mapa de módulos (la tabla "Mapa de módulos" de `baton/backlog/BACKLOG.md`).

**Plantillas:** `baton/templates/module.md` y `baton/templates/item-<tipo>.md`. No leas la documentación de la metodología: lo necesario está aquí.

Pregunta qué quiere hacer el humano, o dedúcelo de `python3 baton/bin/baton.py next --rol navigator`:

## A. Cambiar el mapa de módulos

El mapa es iterable: casi nunca se conocen todos los módulos al empezar.

| Acción | Cómo |
|---|---|
| Agregar | nuevo `baton/modules/<m>/module.md` con `estado: Planificado`, `prioridad` y `## Objetivo` |
| Aceptar o descartar un candidato | `baton.py estado modulo:<m> Planificado` o `baton.py estado modulo:<m> Descartado` |
| Repriorizar | edita `prioridad` en los `module.md` |
| Dividir | crea los módulos nuevos, mueve los ítems (campo `modulo`) y descarta el original con una nota en `## Objetivo`: "dividido en X e Y" |
| Fusionar | mueve los ítems al módulo que queda y descarta el otro con una nota |
| Descartar | `baton.py estado modulo:<m> Descartado`. Sus ítems no hechos pasan a `Descartado` o a otro módulo, según decida el humano |

Las propuestas del agente entran como `estado: Candidato`, `origen: agente`, `propuesto_por` y `## Por qué se propone`. Nunca las aceptes sin respuesta del humano. Al terminar, ejecuta `baton.py sync` **con el motivo de cada cambio**.

## B. Abrir un módulo

Por defecto, el siguiente `Planificado` por prioridad.

### 1. Entender

Es la "spec" del módulo, pero corta.

- A partir de la visión y del `## Objetivo`, propón `## Alcance`, `## Fuera de alcance`, `## Riesgos` y `## Referencias` (ADR y contratos que aplican).
- Pregunta lo que no puedas deducir, en una sola ronda.
- Para los riesgos, evalúa si el módulo:
  - mueve dinero o datos personales;
  - toca autenticación o permisos;
  - migra datos;
  - integra servicios externos;
  - es reversible;
  - es una zona donde el equipo tiene poca experiencia.
- Si el módulo necesita una decisión de diseño nueva, propónla como ADR (`baton/templates/adr.md`).
- Muestra un resumen de 5 líneas como máximo y pide confirmación.

### 2. Configurar

1. Muestra la configuración heredada con `baton.py efectiva modulo:<m>`, en tres grupos: roles, autonomía y verificador, y tamaño de slice.
2. **Recomienda según el riesgo**, con el motivo en una línea. Por ejemplo: pagos, seguridad o migraciones → Pair; CRUD interno → Delegado.
3. Para cada grupo, pregunta "¿mantener o cambiar?".
4. **Si el humano elige menos control que el recomendado,** avísale **una vez** con el riesgo concreto, anótalo en `## Riesgos` y respeta su decisión. Bajar el control está permitido. Solo comprueba que no quede bajo `autonomia_minima`.
5. En `config` van **solo las diferencias**, cada una como `{ valor, motivo, desde: <hoy> }`. Si la autonomía queda en Delegado, el verificador se activa solo: confirma que haya una entidad asignada.

### 3. Definir los ítems del módulo

1. Propón la lista en una tabla con id, tipo, título, una línea de propósito y prioridad.
   - Usa el **tipo principal** de `config.md` (`backlog.principal`). Usa los auxiliares (`bug`, `tecnico`) solo cuando corresponda.
   - Incluye los ítems semilla que ya existan con ese `modulo`, y los ítems sin módulo que encajen.
   - Divide en ítems **verticales**, que entregan algo usable, y no por capas.
   - Revisa que cada ítem cumpla **INVEST**: independiente, negociable, valioso, estimable, pequeño y testeable. Si un ítem parece de más de unos 6 criterios, propón dividirlo.
2. El humano corrige, edita, quita, agrega y prioriza.
3. Lo que **acepte** se crea como ítem ligero desde `baton/templates/item-<tipo>.md`:
   - el frontmatter completo y la sección de propósito en una línea;
   - `estado: Pendiente` (aceptado para desarrollo);
   - el id con el siguiente número libre de su prefijo.
4. Lo que quiera guardar sin aceptar todavía queda en `Candidato`. Lo que rechace no se crea.

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

## No hagas

- No detalles criterios aquí: eso lo hace `baton-item`, justo a tiempo, ítem por ítem.
- No abras más de un módulo a la vez salvo que el humano lo pida. Así el trabajo en curso se mantiene chico.
- No copies en `module.md` valores iguales a los del proyecto.
- No uses la recomendación de riesgo para bloquear la decisión del humano.
