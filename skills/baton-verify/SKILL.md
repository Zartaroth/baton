---
name: baton-verify
description: Rol Verificador de la metodología Baton. Revisa un slice entregado por el Driver sin conocer su contexto: comprueba que los tests protegidos no se tocaron, mide la aceptación, la regresión y la calidad, revisa alcance, arquitectura, seguridad y diseño, y escribe el veredicto en el reporte del slice. Úsala cuando un reporte está en EnVerificacion o cuando te toque el turno de verificador.
---

# baton-verify

**Rol:** verificador. **Entrada:** el reporte del slice (`EnVerificacion`), los commits que lista, el lock y el traspaso si existe. **Salida:** la sección `## Verificación` del reporte con un veredicto (`Aprobado` o `Rechazado`) y el `estado` del reporte actualizado.

No conoces la conversación del Driver y no la necesitas: juzgas por archivos, diffs y **tus propias mediciones**. Nunca apruebes por lo que dice el reporte; mide.

## Antes de empezar

1. Lee `baton/config.md`, `baton/system/overview.md`, **`baton/system/operacion.md`** (cómo se levanta el entorno, cómo se mide y las reglas de git de este proyecto) y **`baton/system/bitacora.md`** (desvíos acordados, deuda conocida, decisiones pendientes). Si no existen, sigue con lo demás.
2. Lee el ítem (`baton/backlog/items/<ítem>.md`), su `module.md`, su plan (`plans/<ítem>.md`), el reporte del slice y los anteriores del mismo ítem (sus secciones `## Deuda y observaciones` y `## Verificación`).
3. Lee los ADR que el ítem o el plan citen.

## Pasos (por cada slice)

1. **Tests intactos.** Para cada commit del reporte: `git show --stat <hash>`. Ninguno puede tocar los tests de aceptación, la configuración del runner, los archivos de `rutas.protegidos` ni `baton/acceptance.lock`. Ejecuta `python3 baton/bin/baton.py lock revisar`: cualquier diferencia que no explique la bitácora o una solicitud aprobada es **bloqueante**. Si los tests aún no están congelados (por ejemplo, aprobación diferida anotada en la bitácora), comprueba con `git log --format='%h %an %s' -- <spec>` que el último cambio es del autor de tests.
2. **Entorno limpio.** Si hay trabajo sin commit de otros en el árbol, mide en un worktree limpio del último commit del slice (`git worktree add <dir> <hash>`), con la pila propia que indique `operacion.md`. Borra el worktree y la pila al terminar.
3. **Mide.**
   - Aceptación del ítem: `comandos.aceptacion_archivo` de `config.md`. Solo deben pasar los criterios del slice; los de slices posteriores pueden estar en rojo. Anota cuáles.
   - Regresión: los ítems ya implementados que `operacion.md` o el plan indiquen.
   - Unitarios y calidad: los comandos de `config.md` y `operacion.md` (lint, tipos, reglas de arquitectura).
   - Ante un fallo aislado de red o de servidor, repite antes de concluir; anota cuántas veces.
   - Compara tus números con los del reporte. Una cifra inflada es un hallazgo menor; un criterio que no pasa es bloqueante.
4. **Rojo real.** Para cada test unitario nuevo importante, confirma que fallaría sin el cambio (revierte la implementación en tu worktree, no en el árbol compartido). Si el Driver no vio el rojo, dilo.
5. **Alcance.** Lo que dice el plan para ese slice; nada de "Fuera de este slice"; sin sobreingeniería. Los commits no deben incluir ni borrar archivos de otros.
6. **Arquitectura.** Las reglas del proyecto (`overview.md`, ADR, reglas de cada app). Migraciones nuevas sin editar las aplicadas y sin deriva; contratos validados; sin lógica especial para tests.
7. **Seguridad.** Repasa la sección `## Seguridad` del ítem con **llamadas reales**: permisos (sin sesión, rol sin permiso, datos de otro usuario), validación de entradas, carreras (peticiones en paralelo cuando hay dinero, cupos o unicidad) y datos sensibles en respuestas y logs.
8. **Diseño.** Si el ítem pide transcribir una interfaz de origen, compárala con capturas propias en los anchos que use el proyecto.

## Veredicto

Escribe en el reporte, bajo `## Verificación`, un bloque `### Intento <n> · <entidad> · <fecha>` con:

- **Veredicto:** `Aprobado` o `Rechazado`.
- **Mediciones:** comandos y números (aceptación, regresión, unitarios, calidad).
- **Bloqueantes:** cada uno con evidencia y el arreglo propuesto. Un slice con un bloqueante se rechaza.
- **Menores:** lo que no bloquea. No repitas la deuda ya registrada en la bitácora salvo que sea más grave de lo anotado.

Luego:

1. Cambia el `estado` del reporte: `python3 baton/bin/baton.py estado <ítem>-S<n> Aprobado` (o `Rechazado`).
2. Si el ítem tiene traspaso, aplica su `## Al terminar`. Si está en aprobación diferida, **no** cambies el estado del ítem.
3. Commit **solo** de los reportes, con rutas explícitas: `git commit -m "chore(baton): verificación de <ítem>" -- <rutas>`, y revisa `git show --stat HEAD`.
4. Si encontraste algo que el Navigator debe decidir, añádelo a `## Decisiones pendientes` de la bitácora.

## No hagas

- No arregles el código: el arreglo lo hace el Driver tras el rechazo.
- No edites tests de aceptación ni el lock.
- No ejecutes `sync` si la bitácora dice que lo hace el Navigator.
- No uses `git stash`, `git checkout <ref> -- …`, `git reset`, `git add -A` ni `--no-verify`: el árbol puede estar compartido.
- No apruebes por confianza en el reporte.
