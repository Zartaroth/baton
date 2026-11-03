# Skills de Baton

Skills del núcleo de la metodología, en formato Agent Skills (`SKILL.md`). Ver [METODOLOGIA.md](../METODOLOGIA.md) y [FORMATOS.md](../FORMATOS.md).

**Solo hace falta recordar una: `baton`.** Lee el estado del proyecto, anuncia qué rol tiene el turno y qué paso toca, y llama a la skill que corresponde. Basta con decir "continúa". Las demás también se pueden llamar directamente.

| Skill | Rol | Cuándo |
|---|---|---|
| `baton` | cualquiera | "¿qué sigue?", "continúa", "toma tu turno"; resuelve escalamientos |
| `baton-start` | humano + Navigator | una vez: entender el proyecto (nuevo o existente) → escala y stack → configurar → mapa de módulos. También para actualizar visión, stack o configuración |
| `baton-module` | Navigator | cambiar el mapa de módulos; abrir un módulo (entender → configurar → ítems); reconfigurarlo o cerrarlo |
| `baton-item` | Navigator | detallar un ítem: criterios + slices, con una sola confirmación → Listo |
| `baton-tests` | Autor de tests | ítem en Listo |
| `baton-approve` | Aprobador (persona) | ítem en TestsEnRevision |
| `baton-drive` | Driver | ítem en TestsCongelados o EnCurso |
| `baton-sync` | cualquiera | después de editar a mano |

## Flujo

```
baton-start  → entender · escala y stack · configurar · mapa de módulos   (una vez, actualizable)
baton-module → entender el módulo · configurarlo · definir sus ítems       (por módulo)
baton-item   → criterios + slices                                          (por ítem, justo a tiempo)
baton-tests → baton-approve → baton-drive → verificación → revisión        (roles separados, sin atajos)
```

Solo se juntan pasos de un **mismo rol**. Tests y aprobación, o Driver y Verificador, siguen separados: separarlos es el núcleo del control.

## Reparto entre skills y `baton.py`

- **Las skills ponen el criterio:** qué preguntar, cómo escribir buenos criterios y tests, cuándo escalar.
- **`baton.py` hace lo determinista:**
  - detectar si el proyecto es nuevo o existente, y su stack;
  - validar y calcular la configuración efectiva;
  - decidir turnos y cambiar estados con transiciones válidas;
  - crear traspasos, sincronizar y mantener el lock.

Así, dos agentes distintos que siguen la misma skill obtienen los mismos archivos, y nadie gasta tokens explorando lo que un script puede medir.

Las skills no mandan a leer la documentación de la metodología: todo lo que el agente necesita está en la skill, en sus `references/` y en `baton/templates/`.

`baton.py` vive en `baton-start/assets/`. `baton-start` lo copia al proyecto en `baton/bin/baton.py`, y desde ahí lo usan las demás skills. Requiere Python 3.10+ y PyYAML.

## Instalación

Copia las carpetas `baton` y `baton-*` a la carpeta de skills de tu herramienta. En Claude Code es `.claude/skills/` del proyecto o `~/.claude/skills/`. Después, en tu repositorio, di **"continúa"** o ejecuta `baton-start`.

## Pruebas

`pruebas/e2e.sh` recorre el flujo en un repositorio temporal:
- inicio, mapa de módulos y tipos de backlog;
- tests, aprobación, Driver, solicitud de cambio y recongelamiento;
- tres intentos de saltarse la protección.

```
bash pruebas/e2e.sh
```

## Pendiente

`baton-verify`, `baton-review` y los adaptadores (`adapter-jira`, `adapter-trello`, `adapter-github`).
