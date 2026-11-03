# Skills de Baton

Skills del núcleo de la metodología, en formato Agent Skills (`SKILL.md`). Ver [METODOLOGIA.md](../METODOLOGIA.md) y [FORMATOS.md](../FORMATOS.md).

| Skill | Rol | Cuándo |
|---|---|---|
| `baton-setup` | humano | una vez por proyecto, o para cambiar la configuración |
| `baton-kickoff` | Navigator | al abrir o reconfigurar un módulo |
| `baton-refine` | Navigator | un ítem Pendiente está por desarrollarse; aceptar o descartar candidatos |
| `baton-plan` | Navigator | después de refine: slices, ítem a Listo, traspaso al autor |
| `baton-tests` | Autor de tests | ítem en Listo |
| `baton-approve` | Aprobador (persona) | ítem en TestsEnRevision |
| `baton-drive` | Driver | ítem en TestsCongelados o EnCurso |
| `baton-sync` | cualquiera | después de editar a mano o cuando otra skill lo indique |
| `baton-next` | cualquiera | "¿qué me toca?" o "toma tu turno" |

## Reparto entre skills y `baton.py`

- **Las skills ponen el criterio:** qué preguntar, cómo escribir buenos criterios y tests, cuándo escalar.
- **`baton.py` hace lo determinista:** validar, calcular la configuración efectiva, decidir turnos, cambiar estados con transiciones válidas, crear traspasos, sincronizar y mantener el lock.

Así, dos agentes distintos que siguen la misma skill obtienen los mismos archivos.

`baton.py` vive en `baton-setup/assets/`. `baton-setup` lo copia al proyecto, en `baton/bin/baton.py`, y desde ahí lo usan las demás skills. Requiere Python 3.10+ y PyYAML.

## Instalación

Copia las carpetas `baton-*` a la carpeta de skills de tu herramienta. En Claude Code es `.claude/skills/` del proyecto o `~/.claude/skills/`. Después ejecuta `baton-setup` en el repositorio.

## Pruebas

`pruebas/e2e.sh` recorre el flujo completo en un repositorio temporal: setup, refine, tests, aprobación, Driver, solicitud de cambio y recongelamiento. También intenta saltarse la protección de tres maneras: editar un test congelado, editar el test y recalcular el lock a mano, y agregar un fixture nuevo.

```
bash pruebas/e2e.sh
```

## Pendiente

`baton-verify`, `baton-review` y los adaptadores (`adapter-jira`, `adapter-trello`, `adapter-github`).
