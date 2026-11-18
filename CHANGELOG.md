# Cambios

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Las versiones son de la metodología. El campo `formato` de los archivos tiene su propia numeración.

## [0.4.0] - 2026-11-18

### Agregado
- Skill `baton-verify`: el Verificador mide por su cuenta (tests intactos, aceptación, regresión, rojo real, alcance, arquitectura, seguridad con llamadas reales y diseño) y escribe el veredicto en el reporte.
- Continuidad entre IA: `baton/system/operacion.md` (cómo operar el repositorio) y `baton/system/bitacora.md` (estado vivo del Navigator), con sus plantillas. `init` los crea, `next` recuerda leerlos y los traspasos los incluyen en `leer`.
- `baton-next`: paso de contexto al empezar y actualización de la bitácora al cerrar una sesión.

### Corregido
- `pruebas/e2e.sh` funciona en rutas con espacios.

### Origen
- Lecciones del primer proyecto piloto: el conocimiento operativo y el estado del Navigator quedaban fuera de Baton (en la conversación o en archivos ignorados), así que otra IA no podía continuar sin él.

## [0.3.0] - 2026-11-03

### Agregado
- Metodología: principios, cuatro pilares, roles, invariantes, configuración por capas y niveles de autonomía (Pair, Checkpoint y Delegado).
- Formatos de archivo, versión 1: configuración, módulo, ítem, plan, `acceptance.lock`, solicitud, traspaso, reporte de slice y las vistas generadas.
- Skills del núcleo: `baton-setup`, `baton-kickoff`, `baton-refine`, `baton-plan`, `baton-tests`, `baton-approve`, `baton-drive`, `baton-sync` y `baton-next`.
- `baton.py`: validación, configuración efectiva, turnos, estados, traspasos, sincronización por instantánea y lock de tests.
- El hook pre-commit, que protege los tests de aceptación congelados.
- Prueba de punta a punta y guía del proyecto piloto.
