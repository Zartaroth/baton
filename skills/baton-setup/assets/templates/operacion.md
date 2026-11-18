---
formato: 1
actualizado: AAAA-MM-DD
---

# Manual de operación

Lo que cualquier agente (de cualquier herramienta o modelo) necesita para trabajar en este repositorio sin preguntar. Es **estable**: cambia cuando cambia el proyecto, no en cada sesión. El estado vivo va en `bitacora.md`.

## Entorno

<!-- Cómo se levanta todo desde cero, en orden. Comandos exactos. -->

```bash
# dependencias
# infraestructura (base de datos, colas, correo de desarrollo…)
# migraciones y datos semilla
# servidores (con puertos)
```

- Cómo saber que está arriba: <!-- p. ej. curl a un endpoint que responda 200 -->
- Qué hacer si una sesión se reinició: <!-- volver a levantar X, Y -->

## Cómo medir

| Qué | Comando |
|---|---|
| Aceptación de un archivo | <!-- igual que comandos.aceptacion_archivo de config.md --> |
| Unitarios | |
| Tipos, lint, reglas de arquitectura | |
| Base de datos sin deriva | |

- Regresión mínima antes de cada commit: <!-- qué tests -->
- Fallos intermitentes conocidos y cómo distinguirlos: <!-- p. ej. ECONNREFUSED cuando otro agente recarga el servidor: repetir -->
- Pila propia para medir aislado (worktree limpio, otra base, otros puertos): <!-- cómo -->

## Reglas de git

- Commits: <!-- convención, idioma, línea de coautoría por entidad -->
- **Árbol e índice compartidos** (si varios agentes trabajan a la vez): commit con rutas explícitas `git commit -m "…" -- <rutas>`; archivos nuevos con `git add <rutas> && git commit … -- <rutas>`; revisar `git show --stat HEAD`.
- Prohibido: `git add -A`, `--no-verify`, `git stash`, `git checkout <ref> -- …`, `git reset` sobre trabajo ajeno. Si algo desaparece, detenerse y avisar al Navigator.
- Hooks: <!-- qué corren y cómo se comportan si fallan -->
- Archivos generados que se commitean tal como se generan: <!-- p. ej. tipos del cliente, árbol de rutas -->

## Arquitectura en una página

<!-- Lo mínimo para no romper nada: dónde va cada cosa, reglas que verifica una herramienta, cómo se comunican los módulos, dónde está el contrato. Enlaza overview.md y los ADR. -->

## Fuentes de referencia

<!-- Repositorios o diseños de origen que se transcriben, y cómo consultarlos. -->

## Trampas conocidas

<!-- Lo que ya hizo perder tiempo una vez. Una línea por trampa, con su solución. -->
