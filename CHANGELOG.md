# Cambios

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Las versiones son de la metodología. El campo `formato` de los archivos tiene su propia numeración.

## [0.4.1] - 2026-11-04

Correcciones que salieron de los intentos 2 y 3 del piloto (defectos D7 a D23 de `pruebas/BITACORA-piloto.md`).

### Cambiado
- **El humano solo aprueba lo que tiene en pantalla.** `baton-item` primero resuelve las decisiones abiertas, después muestra los criterios y los slices en texto, y al final pide la aprobación. `baton-approve` muestra una tabla con cada criterio junto a lo que comprueba su test antes de preguntar.
- **Abrir un módulo** tiene una sola confirmación: primero las preguntas abiertas, después alcance, riesgos, configuración e ítems a la vista, y una aprobación.
- Las decisiones con opciones se preguntan con la herramienta interactiva del entorno; lo abierto, en texto. La configuración inicial va en dos tandas de hasta 4 preguntas.
- `baton-start` cierra con tablas (visión, configuración, mapa de módulos) y propone el nombre del proyecto a partir del producto, no de la carpeta.
- Cada skill trae las reglas que necesita, para que el agente no lea el código de `baton.py`.
- El router anuncia siempre `Rol · Paso · Sobre`, y `baton-module` se activa también ante "¿qué módulos faltan?".
- `baton-module` propone los módulos candidatos en una pregunta de selección múltiple y pide un motivo de fondo para cada cambio del mapa.
- El autor de tests puede probar una implementación desechable, fuera del repositorio, solo si duda de que un test se pueda poner en verde.
- **Primer congelado sin commit intermedio:** el hook acepta congelar un test por primera vez si su ítem no estaba congelado en el commit anterior. El driver sigue sin poder congelar tests nuevos de un ítem ya congelado.
- Un ítem puede volver de `Pendiente` a `Candidato` ("para después").

### Corregido
- `init --hook` reinstala su propio hook, y `baton/bin/baton.py init` ya no falla al copiarse sobre sí mismo.
- `validar` avisa si el verificador no tiene entidad: en Delegado se activa a la fuerza.
- El lock ya no congela los `.pyc` de `__pycache__`.
- El mapa de módulos corta el objetivo por palabra.

## [0.4.0] - 2026-11-03

Cambios que salieron de la primera prueba piloto.

### Agregado
- **Entender antes de decidir** (principio 8). `baton-start` detecta si el proyecto es nuevo o existente:
  - proyecto nuevo: entrevista corta inspirada en el *inception* de producto;
  - proyecto existente: análisis acotado con un resumen de lo que no se pudo confirmar.

  En los dos casos escribe la visión, y el humano la confirma antes de configurar nada.
- **Escala y stack**: la recomendación de stack depende de la escala (prototipo, MVP, producto pequeño, empezar pequeño y migrar fácil, gran escala). Queda en ADR-0001, con condiciones para revisarla.
- **Mapa de módulos** como backlog base, iterable: se agregan, dividen, fusionan o descartan módulos. Los módulos tienen ciclo de vida (`Candidato`, `Planificado`, `Activo`, `Cerrado`, `Descartado`).
- **Tipo de backlog** principal (historia, requerimiento o ticket) más auxiliares (bug, técnico), con una plantilla por tipo.
- `baton.py detectar`: stack, tests y comandos sin gastar tokens.
- Plantillas de visión y de ADR.
- El sync registra los cambios de la visión y de los ADR.

### Cambiado
- Hay un único punto de entrada, el router **`/baton`**, que sirve para empezar ("empecemos") y para seguir ("continúa"). Anuncia el rol y el paso, y las demás skills se pueden seguir llamando directamente.
- `baton-setup` pasa a ser `baton-start`.
- `baton-kickoff` pasa a ser `baton-module`, que ahora también define los ítems del módulo.
- `baton-refine` y `baton-plan` se unen en `baton-item`, con una sola confirmación.
- `baton-next` pasa a ser `baton`.
- Un ítem solo pasa a `Listo` si su módulo está `Activo`.
- Las skills ya no mandan a leer la documentación de la metodología: lo que el agente necesita está en la skill, en sus referencias y en las plantillas.

## [0.3.0] - 2026-11-03

### Agregado
- Metodología: principios, cuatro pilares, roles, invariantes, configuración por capas y niveles de autonomía (Pair, Checkpoint y Delegado).
- Formatos de archivo, versión 1: configuración, módulo, ítem, plan, `acceptance.lock`, solicitud, traspaso, reporte de slice y las vistas generadas.
- Skills del núcleo: `baton-setup`, `baton-kickoff`, `baton-refine`, `baton-plan`, `baton-tests`, `baton-approve`, `baton-drive`, `baton-sync` y `baton-next`.
- `baton.py`: validación, configuración efectiva, turnos, estados, traspasos, sincronización por instantánea y lock de tests.
- El hook pre-commit, que protege los tests de aceptación congelados.
- Prueba de punta a punta y guía del proyecto piloto.
