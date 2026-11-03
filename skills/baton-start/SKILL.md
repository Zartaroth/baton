---
name: baton-start
description: Inicia un proyecto con la metodología Baton. Detecta si el proyecto es nuevo o existente, entiende qué se va a construir (o desde dónde se parte) y lo confirma con el humano, recomienda el stack según la escala, configura las variables con ese contexto y arma el mapa inicial de módulos. Instala baton.py y el hook. Úsala una vez al empezar, o para actualizar la visión, el stack o la configuración.
---

# baton-start

**Rol:** Navigator (humano + agente). El agente entiende, propone y recomienda. **El humano decide.**

**Salida:**
- `baton/system/overview.md`: la visión;
- `baton/system/adr/ADR-0001-*.md`: el stack;
- `baton/config.md`;
- el mapa de módulos (`baton/modules/<m>/module.md`);
- la herramienta y el hook instalados.

**No leas la documentación de la metodología.** Todo lo que necesitas está en esta skill, en `references/` y en `assets/templates/`. Si algo falta, dilo en vez de buscarlo.

## Orden y por qué

**Entender → escala y stack → configurar → mapa de módulos.** Cada paso usa lo que se decidió en el anterior. Las recomendaciones de configuración salen del proyecto real, no de valores genéricos.

## 0. Preparar (sin gastar tokens)

1. Comprueba que el directorio sea un repositorio git y que `python3 -c "import yaml"` funcione. Si falta PyYAML, pide permiso para instalarlo.
2. Ejecuta `python3 <esta skill>/assets/baton.py detectar`. Devuelve en YAML:
   - `inicio`: `nuevo` o `existente`;
   - lenguajes, manifiestos, tests existentes y comandos de test sugeridos;
   - si hay issues que se puedan importar;
   - si Baton ya está instalado.

   **Usa ese resultado en vez de explorar el repositorio a mano.**
3. Si `baton_instalado` es `true`, ve a **Actualizar** (al final).
4. Ejecuta `python3 <esta skill>/assets/baton.py init`. Crea `baton/`, copia la herramienta a `baton/bin/baton.py` y las plantillas a `baton/templates/`.

## 1. Entender el proyecto

- Si `inicio` es `nuevo`, sigue [references/proyecto-nuevo.md](references/proyecto-nuevo.md).
- Si `inicio` es `existente`, sigue [references/proyecto-existente.md](references/proyecto-existente.md).

Los dos caminos terminan igual:

1. Escribes `baton/system/overview.md` desde `baton/templates/overview.md`.
2. Muestras un **resumen corto** de lo que entendiste.
3. El humano confirma, corrige, agrega o quita. Repite hasta que diga que está bien.

No sigas al paso 2 sin esa confirmación.

## 2. Escala y stack

Sigue [references/escala-y-stack.md](references/escala-y-stack.md). La recomendación de stack sale de la escala y las restricciones confirmadas en el paso 1, nunca antes.

El resultado es `baton/system/adr/ADR-0001-stack.md` (plantilla `baton/templates/adr.md`), en estado `Aceptado` una vez que el humano decide.

## 3. Configurar

Haz las preguntas **por grupos**. Cada grupo va con una propuesta ya rellenada a partir de la visión, del stack y de `detectar`, y explica en una línea por qué la recomiendas. El humano responde "sí" o corrige.

1. **Tipo de backlog:**
   - el **principal** define la plantilla de los ítems:
     - `historia`: "Como… quiero… para…". Para producto con usuarios.
     - `requerimiento`: "El sistema debe…". Para sistemas regulados, contratos o integraciones.
     - `ticket`: problema o tarea. Para mantenimiento o soporte.
   - los **auxiliares** siempre disponibles, por defecto `bug` y `tecnico`.

   Recomienda según el tipo de proyecto.
2. **Cadencia:** kanban o scrum (con duración), y el `wip` (2 o 3 ítems en curso por persona).
3. **Personas y modelos** (`entidades`) y **roles**. Propón esto por defecto:
   - navigator: la persona + un modelo razonador;
   - autor_tests: el modelo razonador, por subagente;
   - aprobador_tests: la persona;
   - driver: un modelo implementador, en otra sesión;
   - verificador: un modelo distinto del driver, o desactivado.

   Si el humano propone que el driver apruebe o escriba tests de aceptación, explica la invariante que rompe y pide otra entidad.
4. **Autonomía:** Pair revisa cada slice, Checkpoint cada ítem y Delegado el módulo completo. Recomienda según la visión: si hay datos sensibles, dinero o un equipo nuevo en el flujo, Pair o Checkpoint. Pregunta por una `autonomia_minima` solo si las restricciones lo justifican, por ejemplo por regulación.
5. **Tests:**
   - la ruta de los tests de aceptación;
   - los comandos (los de `detectar`, o los del stack recién elegido);
   - los archivos `protegidos`: la configuración del runner y las fixtures compartidas;
   - `slice_max`.

   Los tests que ya existen **no se congelan**: el lock solo cubre los tests de aceptación nuevos, que salen de criterios aprobados.
6. **Herramienta externa:** ninguna, Jira, Trello o GitHub Issues.
7. **Protección:** el hook de git (recomendado) y CODEOWNERS si hay remoto en GitHub o GitLab. El hook atrapa descuidos; la garantía fuerte es CODEOWNERS.

Escribe `baton/config.md` desde `baton/templates/config.md`. Si el humano aceptó el hook, ejecuta `python3 baton/bin/baton.py init --hook [--codeowners "@usuario"]`.

## 4. Mapa de módulos

El mapa de módulos es el **backlog base**: las grandes partes del sistema (épicas), con prioridad. **No es definitivo:** después se pueden agregar, dividir, fusionar o descartar módulos con `baton-module`.

1. Propón los módulos que salen del **alcance inicial** de la visión, en una tabla con nombre, objetivo en una línea y prioridad.
   - El primero debería ser el que entrega el flujo central de punta a punta. Su primer slice será el esqueleto andante del sistema.
   - No intentes adivinar todos los módulos del futuro.
2. El humano edita, quita, agrega o reordena. Lo que acepte se crea con `baton/templates/module.md`: solo el frontmatter y `## Objetivo`, con `estado: Planificado`. Lo que solo propusiste y no aceptó, no lo crees.
3. **Ítems semilla (opcional):** si el humano ya tiene ítems claros, créalos como ítems ligeros. Usa la plantilla del tipo (`baton/templates/item-<tipo>.md`), solo el frontmatter y el título, con `estado: Pendiente` y su `modulo`. El detalle se hace al abrir el módulo.
4. **Importar (opcional, solo si `issues_importables` o hay TODO en el código):** ofrécelo, sin hacerlo por defecto. Lo importado entra como ítem `Candidato` (`origen: agente`, `## Por qué se propone`: "importado del issue #N").

## 5. Registrar y cerrar

1. Ejecuta `python3 baton/bin/baton.py validar` y corrige hasta que diga `ok`.
2. Ejecuta `python3 baton/bin/baton.py sync --autor <persona> --motivo "inicio del proyecto" --ref baton-start`.
3. Muestra un resumen: la visión en 3 líneas, el stack, la configuración clave y el mapa de módulos. Indica el siguiente paso: "abrir el módulo `<primero>`; escribe **`/baton`** (o "continúa")".
4. Propón hacer commit, pero no lo hagas sin permiso.

## Actualizar (Baton ya instalado)

Pregunta qué cambió:
- **Visión:** edita `overview.md` y actualiza `actualizado`.
- **Stack:** crea un ADR nuevo que reemplace al anterior. En el viejo marca `estado: Reemplazado` y `reemplazado_por`.
- **Configuración:** el grupo que corresponda.
- **Mapa de módulos:** usa `baton-module`.

Pide el **motivo** de cada cambio y ejecuta `baton.py sync --motivo-de "<clave>=<motivo>"`. Si cambia `autonomia` o `autonomia_minima`, ejecuta `validar` y avisa qué módulos o ítems quedan fuera de las reglas.

## No hagas

- No configures antes de entender el proyecto.
- No recomiendes el stack antes de conocer la escala y las restricciones.
- No inventes entidades, modelos ni respuestas de negocio. Propón y pide confirmación.
- No sobrescribas un hook de git existente sin preguntar.
- No hagas commit ni push sin permiso.
