---
name: baton-sync
description: Sincroniza el backlog de la metodología Baton. Detecta qué cambió en ítems, configuración, planes, solicitudes, reportes y en el lock desde el último sync, pide el motivo de cada cambio que lo necesita, lo registra en HISTORY.md y regenera BACKLOG.md. Úsala después de editar archivos de baton/ a mano o cuando otra skill lo indique.
---

# baton-sync

**Rol:** cualquiera. **Entrada:** los archivos maestros de `baton/`. **Salida:** entradas nuevas en `baton/backlog/HISTORY.md`, `baton/backlog/BACKLOG.md` regenerado y `baton/.sync/snapshot.json` actualizado.

## Cómo detecta cambios

`baton.py` guarda una instantánea en `baton/.sync/snapshot.json` (se versiona con el repo) y la compara con los archivos actuales. Detecta cambios campo por campo en el frontmatter, por sección en el cuerpo y criterio por criterio. No depende de commits: también ve los cambios sin commitear.

## Pasos

1. Ejecuta `python3 baton/bin/baton.py sync --revisar`. Lista los cambios con su clave entre corchetes y marca `FALTA MOTIVO` en los que lo necesitan. Los cambios de estado del flujo no lo necesitan.
2. Si `validar` reporta errores, el sync se cancela. Muestra los errores y corrígelos (o pide al humano que decida) antes de seguir.
3. **Motivos:**
   - Si hiciste el cambio en esta sesión, ya sabes el motivo: úsalo.
   - Si no, sobre todo cuando son ediciones a mano del humano, **pregúntale**. Agrupa en una sola pregunta los cambios que parecen tener el mismo motivo. El motivo es una respuesta abierta: pregúntalo en texto, salvo que puedas proponer motivos probables como opciones.
   - **Nunca inventes un motivo.**
4. Ejecuta `python3 baton/bin/baton.py sync --autor <entidad> [--motivo "<común>"] [--motivo-de "<clave>=<motivo>" ...] [--ref <commit|solicitud|skill>]`. La clave puede ser la de la lista (`US-004:prioridad`) o el objeto completo (`US-004`).
5. Muestra el resultado: cuántos cambios se registraron y, si cambió algo importante, una línea con el estado del backlog.

## No hagas

- No edites `BACKLOG.md` ni `HISTORY.md` a mano. El primero se regenera y el segundo solo crece.
- No borres ni edites `baton/.sync/snapshot.json`. Si se pierde, el siguiente sync registra todo como creado.
