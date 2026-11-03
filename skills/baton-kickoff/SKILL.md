---
name: baton-kickoff
description: Abre o reconfigura un módulo de la metodología Baton. Muestra la configuración heredada del proyecto, recomienda un nivel de autonomía según el riesgo y escribe baton/modules/<módulo>/module.md con el alcance y solo las diferencias, cada una con su motivo. Úsala al empezar a trabajar un módulo o para cambiar su configuración a mitad de camino.
---

# baton-kickoff

**Rol:** Navigator (humano + agente razonador). **Entrada:** `baton/config.md` y el alcance que describe el humano. **Salida:** `baton/modules/<m>/module.md`.

Los formatos están en `FORMATOS.md`, secciones 2 y 3. La plantilla es `baton/templates/module.md`.

## Pasos

1. **Alcance.** Pide al humano qué cubre el módulo y qué queda fuera. Revisa `baton/system/overview.md` y los ADR, y lista los ítems del backlog que podrían pertenecer al módulo (los que tienen `modulo: null` o un título relacionado).
2. **Riesgo.** Evalúa el módulo y escribe el resultado en `## Riesgos`. Considera:
   - si mueve dinero o datos personales;
   - si toca autenticación o permisos;
   - si migra datos;
   - si integra servicios externos;
   - si es reversible;
   - cuánta experiencia tiene el equipo en esa zona.
3. **Configuración heredada.** Ejecuta `python3 baton/bin/baton.py efectiva` y muéstrala en tres grupos: roles, autonomía y verificador, y tamaño de slice.
4. **Recomendación.** Recomienda una autonomía según el riesgo y explica por qué en una línea. Por ejemplo: pagos, seguridad o migraciones → Pair; CRUD interno → Delegado. Para cada grupo, pregunta "¿mantener o cambiar?".
5. **Si elige menos control que el recomendado:** avísalo **una vez** con el riesgo concreto y anótalo en `## Riesgos`. Luego respeta la decisión. Bajar el control está permitido (invariante 6). Comprueba solo que no quede bajo `autonomia_minima`.
6. **Escribe `module.md`.** En `config` van solo las claves que cambian, cada una como `{ valor, motivo, desde: <fecha de hoy> }`. Las claves permitidas son `roles.<rol>`, `roles.aprobador_tests`, `roles.verificador.activo`, `autonomia` y `slice_max.*`. Si la autonomía queda en Delegado, el verificador se activa solo: confirma que haya una entidad asignada.
7. **Ítems.** Asigna al módulo los ítems que el humano confirme: edita su campo `modulo`. Si faltan ítems, créalos como ítems ligeros (`baton/templates/item.md`, solo frontmatter, `estado: Pendiente`).
8. Ejecuta `python3 baton/bin/baton.py validar`.
9. Ejecuta `python3 baton/bin/baton.py sync --autor <persona> --motivo "kickoff de <m>" --ref baton-kickoff`. Si alguna diferencia de configuración tiene un motivo propio, pásalo con `--motivo-de`.
10. Resume la configuración efectiva del módulo y marca ↓ si se bajó el control.

## Volver a ejecutar a mitad del módulo

- Cambia solo lo que el humano pida, con `desde` igual a la fecha de hoy y su motivo.
- El cambio aplica desde el **siguiente** slice. Los traspasos ya creados conservan su `config_efectiva`.
- Para cerrar el módulo: `estado: Cerrado` y `cierre: <fecha>`, solo si no quedan ítems activos.

## No hagas

- No copies en `module.md` valores iguales a los del proyecto. Solo van las diferencias.
- No uses la recomendación de riesgo para bloquear la decisión del humano.
