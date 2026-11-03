---
name: baton-setup
description: Prepara un proyecto para trabajar con la metodología Baton. Hace las preguntas de configuración, escribe baton/config.md, crea la estructura de carpetas, instala baton.py y el hook que protege los tests de aceptación. Úsala al empezar a usar la metodología en un repositorio o para cambiar la configuración del proyecto.
---

# baton-setup

**Rol:** humano (con ayuda del agente). **Entrada:** respuestas del humano. **Salida:** `baton/config.md`, la estructura `baton/`, `baton/bin/baton.py`, el hook y, opcionalmente, CODEOWNERS.

Los formatos están en `FORMATOS.md` de la metodología. La plantilla está en `assets/templates/config.md` de esta skill.

## Antes de preguntar

1. Comprueba que el directorio sea un repositorio git y que `python3 -c "import yaml"` funcione. Si falta PyYAML, pide permiso para instalarlo (`pip install pyyaml`).
2. Si `baton/config.md` ya existe, estás en **modo cambio** (ver más abajo).
3. Revisa el repositorio para proponer valores por defecto: lenguaje, framework de tests y sus comandos (`package.json`, `pyproject.toml`, `Makefile`, etc.), carpeta de tests, archivos de configuración del runner y remoto de git (GitHub o GitLab).

## Preguntas

Hazlas **por grupos**. Cada grupo lleva una propuesta ya rellenada, y el humano responde "sí" o corrige. No preguntes campo por campo.

1. **Proyecto:** nombre e idioma de los documentos.
2. **Cadencia:** flujo continuo (kanban) o iteraciones (scrum, con duración), y el límite de ítems en curso (`wip`, por defecto 2–3 por persona).
3. **Personas y modelos:** quiénes participan (`entidades`) y qué rol cumple cada uno. Propón esto por defecto:
   - navigator: la persona + un modelo razonador;
   - autor_tests: el modelo razonador, por subagente;
   - aprobador_tests: la persona;
   - driver: un modelo implementador, en otra sesión;
   - verificador: un modelo distinto del driver, o desactivado.
4. **Autonomía por defecto:** explica los tres niveles en una línea cada uno. Pair revisa cada slice, Checkpoint cada ítem y Delegado el módulo completo. Recomienda Checkpoint, o Pair si el equipo recién empieza con el flujo. Pregunta también si quiere una `autonomia_minima`: solo hace falta si nadie debe bajar de cierto nivel, por ejemplo por regulación.
5. **Tests:** ruta de los tests de aceptación, comandos (`aceptacion`, `aceptacion_archivo` con `{archivo}`, `unitarios`, `todos`) y archivos `protegidos` (configuración del runner, fixtures compartidas).
6. **Herramienta externa:** ninguna, Jira, Trello o GitHub Issues.
7. **Protección:** instalar el hook de git (recomendado) y generar CODEOWNERS, si hay remoto en GitHub o GitLab. Explica que el hook atrapa descuidos y que la garantía real es CODEOWNERS.

Valida en cuanto recibas las respuestas, no al final. Si el humano asigna al driver como aprobador o como autor de tests, explícale la invariante que rompe y pide otra entidad.

## Pasos

1. Ejecuta `python3 <ruta de esta skill>/assets/baton.py init [--hook] [--codeowners "@usuario"]` desde la raíz del repositorio.
2. Escribe `baton/config.md` a partir de la plantilla, con las respuestas.
3. Ejecuta `python3 baton/bin/baton.py validar` y corrige hasta que diga `ok`.
4. Si generaste CODEOWNERS, agrega las reglas que imprime `python3 baton/bin/baton.py codeowners "@usuario"`.
5. Ejecuta `python3 baton/bin/baton.py sync --autor <persona> --motivo "setup inicial" --ref baton-setup`.
6. Muestra un resumen corto de la configuración y los archivos creados. Propón hacer commit, pero no lo hagas sin permiso.

## Modo cambio

Si `baton/config.md` ya existe:

1. Muestra los valores actuales agrupados y pregunta qué grupo quiere cambiar.
2. Pide el **motivo** de cada cambio.
3. Edita `baton/config.md`, valida y ejecuta `baton.py sync --autor <persona> --motivo-de "config:<clave>=<motivo>"` (o `--motivo` si todos comparten el mismo).
4. Si cambia `autonomia` o `autonomia_minima`, ejecuta `baton.py validar`. Avisa si algún módulo o ítem queda fuera de las reglas.

## No hagas

- No inventes entidades ni modelos: pregunta.
- No sobrescribas un hook de git existente sin preguntar (`init` falla en ese caso, a propósito).
- No hagas commit ni push sin permiso.
