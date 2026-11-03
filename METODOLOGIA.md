# Baton: metodología de desarrollo iterativo con IA

El nombre viene del testigo (*baton*) de una carrera de relevos: quien lo tiene, tiene el turno, y el traspaso entre roles es pasarlo.

Evolución de SDD (Spec-Driven Development). Su objetivo es que el trabajo con agentes de IA sea **iterable**, que el **control sea atómico** (pieza por pieza) y que cada pieza se **verifique en cuanto se genera**, no todas al final.

Se inspira en las prácticas que mejor funcionaban antes de los agentes: backlog ágil, slices verticales, TDD y pair programming.

> Estado: versión 0.3 (2026-11-03). Los formatos de archivo están en [FORMATOS.md](FORMATOS.md) y las skills del núcleo en [skills/](skills/README.md). Pasos siguientes: probar con un proyecto real → `verify`, `review` y adaptadores → app visual.

---

## 1. Principios

1. **Cada dato vive en un solo lugar.** Lo demás se genera a partir de él.
2. **Nada se da por bueno sin una prueba ejecutable.** El criterio de aceptación se escribe como test antes del código.
3. **Quien implementa no decide ni se califica a sí mismo.** Decidir, implementar y verificar son roles separados.
4. **Unidades pequeñas y demostrables.** Cada slice se puede ejecutar y revisar en 15–30 minutos.
5. **El repositorio es el canal.** Todo estado, decisión y traspaso queda en archivos versionados. Ningún rol depende de la memoria de otro, así que cada rol puede estar en un agente, sesión o herramienta distinta.
6. **Todo cambio tiene motivo.** Ningún cambio de alcance, de configuración ni de test congelado ocurre sin quedar registrado.
7. **Modular.** Cada etapa consume y produce archivos definidos. Para saltarse una etapa, basta con dar su archivo a mano.

---

## 2. Los cuatro pilares

### 2.1 Backlog vivo (desarrollo iterativo)

**Problema en SDD:** pide la spec completa desde el inicio y genera muchos documentos (spec, plan, research, data-model, contracts, quickstart, tasks) que hay que validar juntos. Cambiar algo obliga a corregirlo en todos ellos, y se pierde el control de lo que se diseña.

**Propuesta:** la fuente de verdad del producto es un backlog de ítems pequeños y autocontenidos: una historia de usuario, un requisito o un ticket. Cada ítem tiene:

- id;
- valor que aporta;
- criterios de aceptación en formato *Dado / Cuando / Entonces*;
- prioridad;
- estado;
- historial.

Cambiar algo es editar un ítem, no N documentos.

El detalle se trabaja **justo a tiempo**. Al inicio solo hay una visión del sistema y un backlog ligero (títulos y prioridad). Los criterios, los tests y los slices de un ítem se escriben cuando ese ítem está por desarrollarse.

Dos cosas que cambian a distinto ritmo van separadas:

- **Backlog:** qué hace el sistema. Cambia mucho.
- **Mapa del sistema:** arquitectura, contratos y decisiones (ADR: una nota corta por decisión con contexto, decisión y consecuencias). Cambia poco y crece agregando entradas.

**Backlog actual e histórico** (detalle en la sección 6):

- Cada ítem es un archivo y es el **maestro**: un humano puede editarlo a mano en cualquier momento.
- `BACKLOG.md` (el resumen actual) y `HISTORY.md` (todos los cambios con su motivo) se **generan** a partir de los ítems.
- Los ítems terminados no se borran. El backlog acumulado describe el sistema completo.

### 2.2 Slices verticales

**Problema en SDD:** las primeras fases se dividen por capas (setup, base de datos, backend, frontend). Nada se puede probar hasta que todo está terminado, así que la revisión y las correcciones se acumulan al final.

**Propuesta:** cada fase de implementación es un **slice**, un incremento que atraviesa las capas necesarias (BD → API → UI) y termina en un comportamiento que se puede ejecutar y demostrar.

- **El primer slice de un módulo es un esqueleto andante** (*walking skeleton*): el camino más delgado de extremo a extremo. Reemplaza las fases de Setup y Foundational.
- **Tamaño:** un slice cubre uno o pocos criterios de aceptación. Si no se puede revisar en 15–30 minutos, es demasiado grande.
- **Definition of Done del slice:**
  - tests de aceptación del slice en verde;
  - tests anteriores sin romper;
  - demo o prueba manual descrita;
  - reporte de slice escrito.

### 2.3 TDD con tests protegidos

**Problema en SDD:** como todo se verifica al final, la IA puede ajustar los tests para que el código pase sin que nadie lo note. Puede editar asserts, saltarse tests o abusar de mocks. Los bugs y la sobreingeniería aparecen recién con un incidente.

**Propuesta:** los criterios de aceptación se convierten en tests **antes** de escribir código. El ciclo es *rojo → verde → refactor*: primero el test falla, luego una implementación mínima lo pasa, y después se mejora el código sin romperlo.

| Nivel | Qué valida | Quién lo escribe | ¿El Driver puede editarlo? |
|---|---|---|---|
| Aceptación | el **qué** (backlog) | Autor de tests | **No**, está congelado |
| Unitario | el **cómo** | Driver, dentro del ciclo TDD | Sí |

**Mecanismos de protección:**

- **Rojo verificado:** antes de implementar, el test debe fallar y por la razón correcta. Si pasa sin código nuevo o falla por un error de sintaxis, no vale.
- **Congelamiento:** al aprobarse, los tests de aceptación quedan en un manifiesto de sumas de verificación (`acceptance.lock`).
  - Un hook de git `pre-commit` y una revisión en CI rechazan cualquier cambio en esos tests que no venga con una solicitud aprobada.
  - La protección no depende del agente que se use.
  - El lock también cubre los archivos compartidos que pueden cambiar el resultado de los tests (fixtures, helpers, configuración del runner).
  - El hook local atrapa descuidos, pero se puede saltar. La garantía fuerte es una regla del servidor (CODEOWNERS o equivalente) que exige la revisión de un aprobador humano. Ver [FORMATOS.md](FORMATOS.md#6-tests-de-aceptación-y-batonacceptancelock).
- **Escalar en vez de editar:** si el Driver cree que un test está mal, abre una solicitud de cambio al Navigator y no lo toca.
- **Opcional, mutation testing:** introduce cambios pequeños a propósito en el código. Si los tests siguen pasando, son débiles.

### 2.4 AI Pair Programming (roles separados)

**Problema en SDD:** no define roles ni un flujo de diseño e implementación atómico. Está pensado para delegar todo y revisar el paquete completo al final, lo que quita control y sobrecarga la revisión.

**Propuesta:** separar estrictamente **decidir**, **especificar con tests**, **implementar** y **verificar**. Cada rol se asigna a una persona o a un modelo, y puede vivir en un subagente, otra sesión u otra herramienta. Ver la sección 3.

---

## 3. Roles

| Rol | Responsabilidad | Por defecto | Obligatorio |
|---|---|---|---|
| **Navigator** | Diseña el sistema y el backlog, refina ítems, planifica slices, decide escalamientos. Es el humano con un agente razonador que propone mejoras según la industria, pregunta lo ambiguo, detecta huecos y vulnerabilidades. **El humano decide.** | humano + modelo razonador | Sí |
| **Autor de tests** | Convierte criterios de aceptación en tests ejecutables. | agente del Navigator | Sí |
| **Aprobador de tests** | Revisa que los tests reflejen los criterios, sean claros e implementables, y los congela. | humano del Navigator | Sí |
| **Driver** | Implementa los slices con TDD y escribe el reporte. No toma decisiones de diseño: si necesita una, la escala. | modelo implementador | Sí |
| **Verificador** | Revisa cada slice antes de que llegue al humano: tests congelados intactos, alcance respetado, sin sobreingeniería, seguridad. | modelo distinto al Driver | Opcional (obligatorio en Delegado) |

**Propuestas del agente:** lo que propone el agente razonador entra al backlog como ítem **candidato**. Solo pasa a pendiente si el humano lo acepta. Así se evita que el alcance crezca solo.

**Protocolo de escalamiento del Driver:**

| Puede decidir solo | Debe escalar |
|---|---|
| nombres internos, estructura de funciones, tests unitarios, refactors que no cambian el comportamiento | cambios de contrato o de modelo de datos, dependencias nuevas, desviaciones del plan, dudas sobre un criterio o un test de aceptación |

### Invariantes (ninguna configuración puede romperlas)

1. El **Driver nunca escribe, edita ni aprueba** tests de aceptación.
2. **Autor y aprobador de tests son entidades distintas.**
3. Un test congelado solo cambia con una solicitud aprobada por el Navigator, y el cambio queda en `HISTORY.md`.
4. El **Verificador no es el Driver**: modelo distinto o, como mínimo, sesión distinta sin el contexto del Driver.
5. Ningún slice se cierra con tests en rojo.
6. Un módulo o un ítem puede **subir o bajar** el nivel de control respecto del nivel superior. Bajarlo exige motivo, queda marcado (↓) y nunca pasa por debajo de la autonomía mínima del proyecto.
7. Todo cambio de alcance, configuración o test congelado se registra con su motivo.
8. En **Delegado** el Verificador siempre está activo.
9. La **aprobación de tests de aceptación** ocurre en todos los niveles de autonomía, incluido Delegado, y al menos un aprobador es una persona.

---

## 4. Jerarquía y configuración por capas

```
Proyecto → Módulo → Ítem → Slice
```

- **Proyecto:** el sistema completo.
- **Módulo:** la parte del sistema que se desarrolla como bloque (lo que en SDD sería una spec o feature). Agrupa ítems.
- **Ítem:** historia de usuario, requisito o ticket.
- **Slice:** incremento vertical de un ítem.

### 4.1 Capas que heredan

La configuración se define en capas. Cada nivel **guarda solo lo que cambia** respecto del anterior. La **configuración efectiva** es la suma proyecto + módulo + ítem. Si cambia un valor por defecto del proyecto, ese cambio llega a todos los módulos que no lo sobrescribieron.

| Variable | Proyecto (setup) | Módulo (kickoff) | Ítem |
|---|---|---|---|
| Cadencia: flujo continuo (Kanban) o iteraciones (Scrum) y su duración | ✔ | – | – |
| Límite de ítems en curso | ✔ | – | – |
| Herramienta externa (Jira, Trello, GitHub Issues) | ✔ | – | – |
| Comandos de test, rutas, idioma de los documentos | ✔ | – | – |
| Rol → entidad (persona, modelo, herramienta, transporte) | ✔ | ✔ | – |
| Aprobador de tests | ✔ | ✔ | solo agregar aprobadores |
| Nivel de autonomía | ✔ | ✔ | subir o bajar |
| Autonomía mínima (piso que nadie puede bajar) | ✔ | – | – |
| Verificador activo | ✔ | ✔ | solo activar (forzado en Delegado) |
| Tamaño máximo de slice | ✔ | ✔ | – |

### 4.2 Setup (proyecto)

Es la primera skill que se ejecuta. Pregunta y guarda las variables del proyecto en `baton/config.md`:

- cadencia;
- límite de ítems en curso;
- roles por defecto;
- autonomía por defecto y autonomía mínima (opcional);
- herramienta externa;
- comandos de test.

También crea la estructura de carpetas e instala el hook de protección de tests. Se puede volver a ejecutar para cambiar valores, y cada cambio queda registrado con su motivo.

### 4.3 Kickoff (módulo)

Se ejecuta al empezar un módulo.

1. Muestra la configuración **heredada**. No pregunta todo desde cero, solo "¿mantener o cambiar?" por grupo.
2. El agente del Navigator **recomienda** según el riesgo del módulo. Por ejemplo, pagos, seguridad o migraciones de datos → Pair; un CRUD simple → Delegado. Si el humano elige menos control que el recomendado, el agente lo advierte una vez y anota el riesgo en `module.md`. El humano decide.
3. Guarda en `baton/modules/<módulo>/module.md` solo las diferencias, cada una con su motivo, junto con el alcance del módulo.
4. Se puede volver a ejecutar a mitad del módulo. El cambio aplica desde el siguiente slice y queda en el historial.

Este archivo no es "memoria de la IA". Es un archivo que **todo traspaso incluye** como configuración efectiva, así que cualquier agente de cualquier herramienta lo lee igual.

### 4.4 Excepción por ítem

Se define en el frontmatter del ítem y puede subir o bajar el control respecto del módulo:

- **Subir:** el ítem que maneja cobros reales dentro de un módulo Delegado pasa a Pair.
- **Bajar:** el ítem que solo cambia los textos del recibo dentro de un módulo Pair pasa a Checkpoint.

Lo mismo vale para un módulo respecto del proyecto. Aunque el proyecto esté configurado en Pair, por prisa o comodidad alguien puede trabajar su módulo en Delegado. El flujo lo permite en vez de obligar a saltárselo.

Bajar el control tiene tres resguardos:

1. **Motivo obligatorio**, registrado en `HISTORY.md`.
2. **Queda a la vista:** se marca ↓ en `BACKLOG.md` y en cada traspaso.
3. **Piso opcional:** nadie baja de la `autonomia_minima` del proyecto. Sirve, por ejemplo, para proyectos regulados donde nadie debe trabajar en Delegado.

Lo que nunca se relaja es la aprobación de tests y el Verificador en Delegado (invariantes 8 y 9).

---

## 5. Niveles de autonomía

Los archivos que se generan son siempre los mismos. Solo cambia **dónde está el punto de control humano**.

| Nivel | Revisión humana | Para qué |
|---|---|---|
| **Pair** | en cada slice | módulos críticos, aprendizaje, equipos que recién adoptan el flujo |
| **Checkpoint** | al cerrar cada ítem | caso general |
| **Delegado** | al cerrar el módulo, con los reportes de slice | trabajo de bajo riesgo o cuando no hay tiempo de acompañar |

La **aprobación de tests de aceptación** se mantiene en todos los niveles. Es el punto de control más barato y el que más protege, porque fija qué cuenta como terminado.

En Delegado, el humano puede aprobar los tests de todos los ítems del módulo en un solo lote al inicio. La aprobación de tests y el Verificador son lo que mantiene la calidad cuando el humano no revisa cada slice.

---

## 6. Backlog: maestro y vistas generadas

```
baton/backlog/
  items/US-001.md   ← MAESTRO, editable a mano
  BACKLOG.md        ← GENERADO: tabla resumen del estado actual
  HISTORY.md        ← GENERADO, solo crece: fecha | autor | objeto | cambio | motivo | ref
```

- **Ítem (maestro):** frontmatter con id, tipo, módulo, estado, prioridad, iteración y excepciones de configuración, más el cuerpo con el valor y los criterios *Dado / Cuando / Entonces*. No guarda enlaces: los tests, slices y commits salen del lock, el plan y los reportes.
- **sync:** detecta los cambios en los ítems desde el último sync. Pide el motivo de cada cambio si no lo tiene, regenera `BACKLOG.md` y agrega las entradas nuevas a `HISTORY.md`.
- **Edición humana:** el humano puede editar cualquier ítem a mano. El siguiente sync pide el motivo y propaga el cambio.
- **Trazabilidad:** ítem → criterio → test → slice → commit. Es la base de la app visual.

---

## 7. Ciclo de vida del ítem y turnos

El **estado** del ítem indica qué rol tiene el turno. Cada rol solo toma ítems en su estado, así que dos agentes nunca trabajan sobre lo mismo.

| Estado | Turno de |
|---|---|
| Candidato, Pendiente, Escalado | Navigator |
| Listo | Autor de tests |
| TestsEnRevisión | Aprobador de tests |
| TestsCongelados, EnCurso | Driver |
| EnVerificación | Verificador |
| EnRevisión | humano (según autonomía) |
| Hecho | nadie (archivo) |

```mermaid
stateDiagram-v2
    [*] --> Candidato: propuesta del agente
    [*] --> Pendiente: humano agrega
    Candidato --> Pendiente: humano acepta
    Candidato --> Descartado
    Pendiente --> Listo: Navigator refina
    Listo --> TestsEnRevision: Autor de tests escribe
    TestsEnRevision --> Listo: Aprobador rechaza
    TestsEnRevision --> TestsCongelados: Aprobador congela
    TestsCongelados --> EnCurso: Driver toma el turno
    EnCurso --> Escalado: duda de diseño o de test
    Escalado --> Listo: Navigator decide, cambian criterios o tests
    Escalado --> TestsCongelados: Navigator decide, tests sin cambio
    EnCurso --> EnVerificacion: slice terminado
    EnVerificacion --> EnCurso: rechazado
    EnVerificacion --> EnRevision: aprobado
    EnRevision --> EnCurso: corregir o siguiente slice
    EnRevision --> Hecho: último slice ok
    Hecho --> Pendiente: se reabre y queda en HISTORY
```

Sin Verificador, `EnVerificación` se salta. Según la autonomía, `EnRevisión` pasa automáticamente y el humano revisa después (al cerrar el ítem o el módulo).

---

## 8. Trabajo entre agentes y herramientas distintas

Los roles pueden estar en un subagente, en otra sesión del mismo agente o en otra herramienta (Claude Code, Codex, Antigravity, etc.). Para que todo funcione igual:

- **Traspaso (handoff):** cada cambio de turno deja un archivo con:
  - qué se entrega;
  - qué se espera;
  - criterios y tests;
  - archivos que no se pueden tocar;
  - configuración efectiva.

  Es el mismo contenido que recibiría un subagente. El **transporte** es configurable por rol:
  - `subagente`: se lanza automáticamente;
  - `sesión`: el humano abre otra sesión y le indica "toma tu turno";
  - `externo`: otra herramienta lee el archivo.
- **Comando "siguiente":** cualquier agente puede preguntar "¿qué me toca?". La respuesta sale de los estados y los traspasos, sin depender de la conversación.
- **Instrucciones neutrales:** las skills se escriben en el formato abierto de Agent Skills (`SKILL.md`). Lo propio de cada herramienta, como hooks de Claude Code o comandos de Codex, va en adaptadores, nunca en el núcleo.
- **Protección independiente del agente:** el congelamiento de tests se garantiza con git y CI, no con permisos de un agente.

---

## 9. Estructura de carpetas (propuesta)

```
baton/
  config.md                      proyecto (setup)
  acceptance.lock                sumas de verificación de tests congelados
  bin/baton.py                    herramienta determinista (la instala setup)
  hooks/pre-commit               protección de tests
  templates/                     plantillas de archivos
  .sync/snapshot.json            instantánea del último sync
  system/
    overview.md                  mapa del sistema
    adr/ADR-0001-<tema>.md       decisiones
  backlog/
    items/US-001.md              MAESTRO
    BACKLOG.md                   generado
    HISTORY.md                   generado, solo crece
  modules/<módulo>/
    module.md                    kickoff: alcance + diferencias de config con motivo
    plans/US-001.md              slices del ítem
    requests/US-001-R1.md        escalamientos y solicitudes de cambio de tests
    handoffs/<fecha>-<ítem>-<rol>.md
    reports/US-001-S1.md         reporte de slice
tests/acceptance/...             en la ruta de tests del proyecto, protegidos por el lock
```

---

## 10. Skills previstas

Cada skill tiene un **contrato de entrada y salida**. Si una se quita, su salida se puede dar a mano.

| Skill | Rol | Entrada | Salida |
|---|---|---|---|
| `setup` | humano | preguntas | `config.md`, estructura, hook |
| `vision` | Navigator | ideas, contexto | `system/`, ítems ligeros |
| `kickoff` | Navigator | config, alcance | `module.md` |
| `refine` | Navigator | ítem ligero | ítem con criterios (Definition of Ready) |
| `plan` | Navigator | ítem listo, mapa | `plans/<ítem>.md` en slices |
| `tests` | Autor de tests | criterios, plan | tests de aceptación en rojo verificado |
| `approve` | Aprobador | tests | `acceptance.lock` actualizado |
| `drive` | Driver | traspaso | código, tests unitarios, reporte de slice |
| `verify` | Verificador | reporte, diff, lock | veredicto con hallazgos |
| `review` | humano | reportes | aprobación o correcciones |
| `sync` | cualquiera | ítems | `BACKLOG.md`, `HISTORY.md` |
| `next` | cualquiera | estados | qué rol tiene el turno y sobre qué |
| `adapter-*` | – | ítems | sincronización con Jira, Trello o GitHub Issues |

---

## 11. Flujo general

```mermaid
flowchart TD
    SET["Setup del proyecto<br/>config.md · estructura · hook"] --> V

    subgraph DIS["Diseño: Navigator = humano + agente razonador"]
        V["Visión y mapa del sistema<br/>arquitectura · ADR · contratos"]
        B["Backlog ligero<br/>títulos + prioridad"]
        C["Propuestas del agente<br/>= ítems candidatos"]
        V --> B
        C -->|"humano acepta"| B
    end

    B --> K["Kickoff del módulo<br/>hereda config · cambia solo diferencias"]
    K --> S{"Siguiente ítem priorizado<br/>flujo continuo o iteración"}
    S --> R["Refinar justo a tiempo<br/>criterios Dado/Cuando/Entonces<br/>+ revisión de seguridad"]
    R --> DOR{"¿Definition of Ready?"}
    DOR -->|"no: ambigüedad"| R
    DOR -->|"sí"| P["Plan en slices verticales<br/>slice 1 = esqueleto andante"]
    P --> TA["Autor de tests<br/>tests de aceptación en rojo verificado"]
    TA --> AP{"Aprobador de tests<br/>nunca el Driver ni el autor"}
    AP -->|"rechaza"| TA
    AP -->|"aprueba"| FZ["Congelar<br/>acceptance.lock"]

    subgraph SLC["Ciclo por slice: Driver"]
        RED["Rojo<br/>tests del slice fallan"] --> GREEN["Verde<br/>implementación mínima"]
        GREEN --> REF["Refactor<br/>tests siempre en verde"]
        REF --> REP["Reporte de slice"]
    end

    FZ --> RED
    GREEN -.->|"el test parece incorrecto"| ESC["Solicitud de cambio<br/>al Navigator"]
    ESC -.-> TA

    REP --> VER{"Verificador opcional<br/>lock intacto · alcance · seguridad"}
    VER -->|"rechaza"| RED
    VER -->|"aprueba"| GATE{"Punto de control humano<br/>según autonomía"}
    GATE -->|"corregir"| RED
    GATE -->|"ok"| MAS{"¿Quedan slices del ítem?"}
    MAS -->|"sí"| RED
    MAS -->|"no"| SYNC["sync: actualiza ítem<br/>regenera BACKLOG.md<br/>agrega a HISTORY.md"]
    SYNC -->|"aprendizajes: ítems nuevos o cambios"| B
    SYNC --> S
```

## 12. Roles y repositorio compartido

```mermaid
flowchart LR
    subgraph ROL["Roles: persona, subagente, otra sesión u otra herramienta"]
        NAV["Navigator<br/>humano + modelo razonador"]
        TST["Autor de tests<br/>por defecto: agente del Navigator"]
        APR["Aprobador de tests<br/>por defecto: humano"]
        DRV["Driver<br/>ej. Sonnet, Codex, Antigravity"]
        VRF["Verificador<br/>modelo distinto al Driver"]
    end

    subgraph REPO["Repositorio = canal compartido"]
        CFG["config.md + module.md<br/>configuración por capas"]
        ITM["backlog/items/*.md<br/>maestro, editable a mano"]
        HND["handoffs/<br/>turno + entrega"]
        LCK["tests de aceptación<br/>+ acceptance.lock"]
        RPT["reports/*.md"]
    end

    EXT["Jira · Trello · GitHub Issues"] <-->|"adaptador"| ITM
    NAV --> ITM
    NAV --> CFG
    TST --> LCK
    APR --> LCK
    DRV --> RPT
    VRF --> RPT
    HND --- NAV & TST & APR & DRV & VRF
```

---

## 13. Pendientes

- [x] Nombre de la metodología: **Baton**.
- [x] Formatos exactos: ítem, `config.md`, `module.md`, plan, traspaso, reporte de slice, `acceptance.lock`. Ver [FORMATOS.md](FORMATOS.md).
- [ ] Revisar las decisiones de formato (sección 11 de FORMATOS.md).
- [x] Cómo detecta `sync` los cambios: con una instantánea propia (FORMATOS.md, sección 11).
- [x] Skills del núcleo: `baton-setup`, `baton-kickoff`, `baton-refine`, `baton-plan`, `baton-tests`, `baton-approve`, `baton-drive`, `baton-sync` y `baton-next`, más `baton.py`. Ver [skills/README.md](skills/README.md).
- [ ] Skills `baton-verify`, `baton-review` y los adaptadores.
- [ ] Probar el flujo con un proyecto pequeño real antes de construir la app visual.
- [ ] App visual: tablero por estados, trazabilidad ítem → test → commit, editor de configuración por capas.
