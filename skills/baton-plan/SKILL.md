---
name: baton-plan
description: Divide un ítem refinado de la metodología Baton en slices verticales demostrables (el primero es un esqueleto andante), escribe baton/modules/<m>/plans/<ítem>.md, marca el ítem como Listo y entrega el turno al autor de tests. Úsala después de baton-refine o cuando haya que cambiar el plan de un ítem.
---

# baton-plan

**Rol:** Navigator. **Entrada:** un ítem refinado, el mapa del sistema y los ADR. **Salida:** el plan, el ítem en `Listo` y el traspaso al autor de tests.

El formato está en FORMATOS.md, sección 5. La plantilla es `baton/templates/plan.md`.

## Pasos

1. Lee el ítem, su `module.md`, `baton/system/overview.md` y los ADR. Consulta `slice_max` con `python3 baton/bin/baton.py efectiva <ítem>`.
2. **Divide en slices verticales.** Cada slice atraviesa las capas necesarias (UI → API → BD, o la forma que tenga el sistema) y termina en algo que se puede ejecutar.
   - **S1 es el esqueleto andante:** el camino más delgado de punta a punta para el criterio principal. Si el módulo es nuevo, S1 también deja montado lo mínimo de infraestructura.
   - Cada criterio vigente va en **exactamente un** slice: el slice donde su test debe pasar.
   - Ningún slice supera `slice_max.criterios` ni se puede revisar en más de `slice_max.minutos`.
   - Ordena los slices por dependencia y luego por valor.
3. **Cada slice** lleva:
   - **Recorrido**: capas y piezas que toca;
   - **Fuera de este slice**: lo que se deja para después a propósito;
   - **Demo**: pasos concretos y lo que se debe ver;
   - **Decisiones que aplican**: los ADR;
   - **Escalar si**: los puntos donde el Driver debe detenerse a preguntar.
4. **Decisiones de diseño.** Si el plan necesita una decisión nueva de arquitectura, contrato o modelo de datos, propónla al humano. Cuando la apruebe, escríbela como ADR en `baton/system/adr/ADR-<nnnn>-<tema>.md` (contexto, decisión, consecuencias). No la dejes implícita en el plan.
5. Escribe `baton/modules/<m>/plans/<ítem>.md` y ejecuta `python3 baton/bin/baton.py validar`.
6. Ejecuta `python3 baton/bin/baton.py estado <ítem> Listo`. Si falla, el mensaje dice qué falta de la Definition of Ready.
7. Ejecuta `python3 baton/bin/baton.py handoff --item <ítem> --de navigator --para autor_tests --entidad-de <tu entidad>`. Completa en el traspaso `## Qué se entrega`, `## Qué se espera` y `## Contexto`.
8. Ejecuta `python3 baton/bin/baton.py sync --autor <entidad> --motivo "plan de <ítem>"`.
9. Dile al humano cómo sigue el turno según el `transporte` del autor de tests:
   - `subagente`: lánzalo con el traspaso como instrucción;
   - `sesion`: el humano abre otra sesión y le dice "toma tu turno";
   - `externo`: otra herramienta lee el traspaso.

## Cambiar un plan existente

- Sube `version`.
- Los slices con reporte `Terminado` o `Aprobado` no se modifican.
- Los ids de slice nunca se reutilizan.
- Ejecuta sync con el motivo.
- Si el cambio mueve criterios entre slices que ya tienen tests congelados, no hace falta tocar los tests: la relación criterio → slice vive en el plan.
