---
name: baton-drive
description: Rol Driver de la metodología Baton. Implementa un slice con TDD (rojo, verde, refactor) contra tests de aceptación congelados que no puede tocar, escribe el reporte del slice y entrega el turno según la autonomía. Escala en vez de decidir diseño o cambiar tests. Úsala cuando un ítem está en TestsCongelados o EnCurso, o cuando te toque el turno de driver.
---

# baton-drive

**Rol:** Driver. **Entrada:** un traspaso para `driver`. **Salida:** el código, los tests unitarios, `baton/modules/<m>/reports/<ítem>-<S>.md` y el traspaso siguiente.

**El traspaso es tu única fuente.** Lee solo lo que está en `leer` y no toques nada de `no_tocar`. Si te falta algo que no está ahí, escala.

## Pasos

1. Busca el traspaso con `python3 baton/bin/baton.py next --rol driver` y márcalo con `python3 baton/bin/baton.py tomar <id>`. Si el ítem está en `TestsCongelados`, ejecuta `python3 baton/bin/baton.py estado <ítem> EnCurso`. Si `next` dice "bloqueado: WIP", no empieces: avisa al humano.
2. **Rojo.** Ejecuta los tests de aceptación del slice (los de `## Tests del slice`) y confirma que fallan. Ejecuta también la suite completa y anota qué pasaba antes de empezar.
3. **Ciclo TDD**, en pasos chicos:
   - escribe un test unitario del *cómo* que falle;
   - escribe la implementación **mínima** que lo pase;
   - refactoriza con todo en verde;
   - repite hasta que pasen los tests de aceptación del slice.
4. **Antes de cerrar:**
   - pasan los tests de aceptación del slice;
   - pasan los tests de slices anteriores y los unitarios (`comandos.todos`);
   - los tests de slices futuros siguen en rojo, y eso es lo esperado;
   - `python3 baton/bin/baton.py lock revisar` dice `lock ok`.
5. **Alcance.** Implementa solo lo del slice. Lo que está en "Fuera de este slice" del plan no se hace, aunque sea fácil. Si ves deuda o mejoras, anótalas en el reporte.
6. **Commit.** Haz commit del slice solo si el humano autorizó que el Driver haga commits en este proyecto. Si no, deja `commits: []` y avisa que el slice está listo para commit.
7. **Reporte.** Crea `baton/modules/<m>/reports/<ítem>-<S>.md` desde `baton/templates/report.md`, con estos datos:
   - `resultado` con los números reales;
   - `## Rojo → verde`, con la razón de cada fallo inicial;
   - `## Decisiones tomadas`;
   - `## Cómo probarlo`, con la demo del plan.

   Si es un reintento después de un rechazo, sube `intento` y responde a cada hallazgo.
8. Sigue los pasos de `## Al terminar` del traspaso. Dependen de la autonomía y de si hay verificador: dicen a qué estado pasa el reporte y para quién es el siguiente traspaso.
9. Ejecuta `python3 baton/bin/baton.py sync --autor <entidad> --motivo "<ítem>-<S> implementado"`.

## Qué decides tú y qué escalas

| Decides solo | Escalas |
|---|---|
| nombres internos, estructura de funciones, tests unitarios, refactors que no cambian el comportamiento | cambios de contrato o de modelo de datos, dependencias nuevas, desviaciones del plan, dudas sobre un criterio o un test de aceptación |

**Para escalar:**

1. Crea `baton/modules/<m>/requests/<ítem>-R<n>.md` desde `baton/templates/request.md`, con:
   - `tipo`: `test`, `criterio`, `diseno` o `plan`;
   - qué pasa, la evidencia y tu propuesta.
2. Ejecuta `python3 baton/bin/baton.py estado <ítem> Escalado`.
3. Ejecuta `python3 baton/bin/baton.py handoff --item <ítem> --de driver --para navigator`.
4. Detente. No sigas implementando por tu cuenta mientras esperas.

## Nunca

- No edites, renombres, borres ni marques como `skip` un test de aceptación, ni las fixtures o la configuración del runner en `rutas.protegidos`.
- No edites `baton/acceptance.lock`, `baton/config.md`, `module.md`, los planes ni los criterios del ítem.
- No hagas un test que pase con lógica especial para el test: ramas que detectan el entorno de test o valores fijos que solo sirven para los datos del test.
- No marques tu slice como `Aprobado`. Ese estado lo pone alguien distinto de ti.
