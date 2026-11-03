# Baton: formatos de archivo

Formato exacto de cada archivo del flujo. Complementa [METODOLOGIA.md](METODOLOGIA.md).

> Formato versión 1 (2026-11-02).

---

## 0. Convenciones comunes

- **Markdown con frontmatter YAML.** El frontmatter guarda lo que leen las máquinas (skills, hook, app). El cuerpo guarda lo que leen las personas. La única excepción es `acceptance.lock`, que es texto plano por líneas para que un hook de shell lo lea sin dependencias.
- **Claves y valores fijos en español sin tildes** (`estado`, `TestsEnRevision`). Son parte del formato y no cambian con el idioma configurado. El texto libre del cuerpo sí sigue el `idioma` del proyecto.
- **`formato: 1`** en todo frontmatter. Permite migrar archivos cuando cambie el formato.
- **Fechas** en ISO 8601: `2026-11-02` para días y `2026-11-02T15:30-03:00` para momentos.
- **Sobrescrituras con motivo.** Fuera de `config.md`, cada valor de configuración que cambia se escribe como `{ valor, motivo }`. Un valor sin motivo es inválido.
- **Archivos generados.** Empiezan con `<!-- GENERADO por sync: no editar a mano -->`. Si alguien los edita, el siguiente sync sobrescribe esos cambios.
- **`HISTORY.md` tiene un solo escritor: `sync`.** Las skills que cambian algo (setup, kickoff, approve, etc.) llaman a sync y le pasan el motivo. Si el cambio se hizo a mano, el siguiente sync pide el motivo.

### Identificadores

| Qué | Forma | Ejemplo | Regla |
|---|---|---|---|
| Ítem | `<PREFIJO>-<nnn>` | `US-004` | el prefijo depende del tipo (ver `config.md`); nunca se reutiliza |
| Criterio | `AC-<n>` dentro del ítem, `<ítem>/AC-<n>` fuera de él | `US-004/AC-2` | nunca se renumera ni se reutiliza |
| Slice | `S<n>` dentro del ítem, `<ítem>-S<n>` fuera de él | `US-004-S1` | nunca se reutiliza |
| Solicitud | `<ítem>-R<n>` | `US-004-R1` | |
| Traspaso | `<AAAA-MM-DD-HHMM>-<ítem>[-<slice>]-<rol>` | `2026-11-02-1530-US-004-S1-driver` | |
| Entidad | nombre corto | `juan`, `sonnet` | se definen solo en `config.md` |
| Rol | fijo | `navigator`, `autor_tests`, `aprobador_tests`, `driver`, `verificador` | |

### Estados

- **Ítem:** `Candidato`, `Pendiente`, `Listo`, `TestsEnRevision`, `TestsCongelados`, `EnCurso`, `Escalado`, `EnVerificacion`, `EnRevision`, `Hecho`, `Descartado`.
- **Autonomía:** `Pair` > `Checkpoint` > `Delegado` (de más a menos control).

### Mapa de archivos

| Archivo | Ruta | Lo escribe | Tipo |
|---|---|---|---|
| Configuración del proyecto | `baton/config.md` | `setup` | maestro |
| Configuración del módulo | `baton/modules/<m>/module.md` | `kickoff` | maestro |
| Ítem | `baton/backlog/items/<ítem>.md` | Navigator o humano a mano; los demás roles solo cambian `estado` | maestro |
| Plan | `baton/modules/<m>/plans/<ítem>.md` | `plan` (Navigator) | maestro |
| Tests congelados | `baton/acceptance.lock` | `approve` | maestro |
| Solicitud | `baton/modules/<m>/requests/<ítem>-R<n>.md` | quien escala; decide el Navigator | registro |
| Traspaso | `baton/modules/<m>/handoffs/<id>.md` | el rol que entrega | registro |
| Reporte de slice | `baton/modules/<m>/reports/<ítem>-S<n>.md` | Driver, Verificador y humano, cada uno su sección | registro |
| Backlog | `baton/backlog/BACKLOG.md` | `sync` | generado |
| Historial | `baton/backlog/HISTORY.md` | `sync` | generado, solo crece |

---

## 1. Configuración del proyecto: `baton/config.md`

```markdown
---
formato: 1
proyecto: tienda
idioma: es

cadencia:
  modo: kanban              # kanban | scrum
  iteracion_dias: null      # obligatorio si modo = scrum
wip: 3                      # máximo de ítems en EnCurso, Escalado, EnVerificacion y EnRevision

tipos:                      # tipo de ítem → prefijo del id
  historia: US
  requisito: RQ
  bug: BUG
  tecnico: TEC

herramienta_externa:
  tipo: ninguna             # ninguna | jira | trello | github
  destino: null             # clave del proyecto, id del tablero u owner/repo

rutas:
  tests_aceptacion: tests/acceptance
  protegidos:               # archivos extra que cubre acceptance.lock
    - pytest.ini
    - tests/conftest.py

comandos:
  aceptacion: "pytest tests/acceptance"
  aceptacion_archivo: "pytest {archivo}"   # para verificar el rojo test por test
  unitarios: "pytest tests/unit"
  todos: "pytest"

entidades:
  juan:   { tipo: persona }
  opus:   { tipo: modelo, modelo: claude-opus-5-5,   herramienta: claude-code }
  sonnet: { tipo: modelo, modelo: claude-sonnet-5-5, herramienta: claude-code }
  codex:  { tipo: modelo, modelo: <id>,              herramienta: codex }

roles:
  navigator:       { entidades: [juan, opus] }
  autor_tests:     { entidad: opus,   transporte: subagente }
  aprobador_tests: { entidades: [juan] }
  driver:          { entidad: sonnet, transporte: sesion }
  verificador:     { entidad: codex,  transporte: externo, activo: true }

autonomia: Pair             # Pair | Checkpoint | Delegado
autonomia_minima: null      # null | Checkpoint | Pair; ningún módulo ni ítem baja de aquí

slice_max:
  criterios: 3
  minutos: 30
---

# Configuración del proyecto

Notas libres: por qué se eligió esta configuración, convenciones del equipo, etc.
```

**Reglas:**

- `transporte` (`subagente` | `sesion` | `externo`) solo aplica a entidades de tipo `modelo`. Una persona recibe el traspaso como archivo.
- `autonomia_minima` es opcional. Sirve para proyectos donde nadie debe trabajar por debajo de cierto nivel, por ejemplo por regulación. Solo se cambia a nivel de proyecto.

**Validaciones** (las hace `setup` al guardar y cualquier skill al cargar):

| Regla | Invariante | Si falla |
|---|---|---|
| `driver` no está en `aprobador_tests` y no es `autor_tests` | 1 | error |
| `autor_tests` no está en `aprobador_tests` | 2 | error |
| `verificador` es una entidad distinta del `driver` | 4 | aviso: se acepta la misma entidad solo en sesión distinta |
| Si `autonomia` es `Delegado`, `verificador.activo` es `true` | 8 | error |
| `autonomia` no es menor que `autonomia_minima` | 6 | error |
| `aprobador_tests` incluye al menos una persona | 9 | error |
| Toda entidad usada en `roles` existe en `entidades` | – | error |
| `iteracion_dias` está definido si `modo` es `scrum` | – | error |

---

## 2. Configuración del módulo: `baton/modules/<m>/module.md`

Guarda el alcance y **solo las diferencias** con `config.md`, cada una con su motivo.

```markdown
---
formato: 1
modulo: catalogo
estado: Activo              # Planificado | Activo | Cerrado
inicio: 2026-11-02
cierre: null
config:
  autonomia:
    valor: Delegado
    motivo: "CRUD interno sin datos sensibles; no hay tiempo de acompañar cada ítem"
    desde: 2026-11-02
  roles.driver:
    valor: { entidad: codex, transporte: externo }
    motivo: "Probar Codex en un módulo de bajo riesgo"
    desde: 2026-11-02
---

# Módulo catalogo

## Alcance
Qué incluye, en 3–6 líneas.

## Fuera de alcance

## Riesgos
Lo que evaluó el kickoff para recomendar la autonomía. Si el humano eligió un nivel
más bajo que el recomendado, se anota aquí.

## Referencias
- baton/system/adr/ADR-0002-busqueda.md
```

**Reglas:**

- Los ítems del módulo **no** se listan aquí. Cada ítem declara su `modulo` y sync arma la lista.
- `desde` es obligatorio. Si se cambia la configuración a mitad del módulo, el cambio aplica desde el siguiente slice. Los slices ya empezados conservan la configuración de su traspaso.
- Las claves que acepta `config` están en la sección 3. Cualquier otra es un error.

---

## 3. Configuración efectiva

Se calcula en el orden **proyecto → módulo → ítem**. El nivel más específico gana, con estas reglas:

| Clave | Módulo | Ítem | Regla |
|---|---|---|---|
| `roles.navigator`, `roles.autor_tests`, `roles.driver`, `roles.verificador` | reemplaza | – | |
| `roles.aprobador_tests` | reemplaza | agrega | en el ítem se suma a los del módulo |
| `roles.verificador.activo` | reemplaza | solo `true` | se fuerza a `true` si la autonomía efectiva es `Delegado` |
| `autonomia` | reemplaza | reemplaza | puede subir o bajar; nunca queda bajo `autonomia_minima` |
| `slice_max.criterios`, `slice_max.minutos` | reemplaza | – | |
| todo lo demás | – | – | solo a nivel de proyecto |

**Control bajado (↓).** Si en algún punto de la cadena la autonomía queda más baja que la del nivel superior, el resultado se marca `bajada: true`. Se muestra como ↓ en `BACKLOG.md` y en cada traspaso.

Ejemplo: el proyecto está en `Pair` y el módulo `catalogo` en `Delegado` (↓). El ítem `US-009` del módulo sube a `Checkpoint`. Su autonomía efectiva es `Checkpoint ↓`: subió respecto del módulo, pero la cadena tiene una bajada.

---

## 4. Ítem: `baton/backlog/items/<ítem>.md`

### 4.1 Ítem refinado

```markdown
---
formato: 1
id: US-004
titulo: Cobrar con tarjeta
tipo: historia
modulo: pagos
estado: Listo
prioridad: 1                # 1 = más alta; se permiten empates
iteracion: null             # número de iteración si la cadencia es scrum
origen: humano              # humano | agente
creado: 2026-11-02
dependencias: [US-003]
config:
  autonomia:
    valor: Pair
    motivo: "Mueve dinero real"
---

## Valor
Como cliente quiero pagar con tarjeta para terminar la compra sin salir de la tienda.

## Criterios de aceptación

### AC-1 · Pago aprobado
- **Dado** un carrito con 2 productos por $30 y una tarjeta válida
- **Cuando** confirmo el pago
- **Entonces** el pedido queda en estado "pagado"
- **Y** recibo un recibo con el total cobrado

### AC-2 · Tarjeta rechazada
- **Dado** ...
- **Cuando** ...
- **Entonces** ...

### AC-3 · ~~Reintento automático~~
Retirado el 2026-11-04: lo resuelve la pasarela. Ver US-004-R1.

## Seguridad
Resultado de la revisión de refine. Ejemplo: los datos de tarjeta nunca pasan por
el servidor (tokenización en el cliente). Si no hay impacto, se escribe "sin impacto".

## Preguntas abiertas
(vacío)

## Fuera de alcance
- Pago en cuotas (US-012).

## Notas
```

### 4.2 Ítem ligero

Al inicio un ítem puede tener solo el frontmatter:

```markdown
---
formato: 1
id: US-012
titulo: Pago en cuotas
tipo: historia
modulo: pagos
estado: Pendiente
prioridad: 5
origen: humano
creado: 2026-11-02
---
```

Un **candidato** lleva `estado: Candidato`, `origen: agente`, `propuesto_por: <entidad>` y una sección `## Por qué se propone`.

### 4.3 Reglas

- **No hay campo de enlaces.** Los tests salen de `acceptance.lock`, los slices del plan y los commits de los reportes. Sync arma la trazabilidad a partir de esos archivos, así cada dato vive en un solo lugar.
- **Criterios:** un criterio retirado no se borra. Se tacha su título y se anota la fecha, el motivo y la solicitud.
- **Quién edita:** el Navigator y el humano editan todo. Los demás roles solo cambian `estado`, y solo cuando tienen el turno.
- **`config`** acepta solo las claves marcadas para ítem en la sección 3.
- **Definition of Ready** (requisito para pasar a `Listo`):
  - `## Valor` escrito;
  - al menos un criterio con Dado / Cuando / Entonces;
  - `## Preguntas abiertas` vacío;
  - `## Seguridad` escrito;
  - dependencias en `Hecho` o explicadas en `## Notas`;
  - plan creado.

---

## 5. Plan: `baton/modules/<m>/plans/<ítem>.md`

Define los slices. Su estado de ejecución vive en los reportes, no aquí.

```markdown
---
formato: 1
item: US-004
version: 1
slices:
  - id: S1
    titulo: "Esqueleto: pago aprobado de punta a punta"
    criterios: [AC-1]
  - id: S2
    titulo: Tarjeta rechazada
    criterios: [AC-2]
---

## S1 · Esqueleto: pago aprobado de punta a punta
- **Recorrido:** botón Pagar (UI) → POST /pagos (API) → tabla pagos (BD) → pasarela en sandbox.
- **Fuera de este slice:** manejo de errores y reintentos.
- **Demo:** con la tarjeta de prueba, comprar un producto y ver el pedido en "pagado".
- **Decisiones que aplican:** ADR-0003 (pasarela).
- **Escalar si:** hace falta cambiar el contrato de /pedidos.

## S2 · Tarjeta rechazada
...
```

**Reglas:**

- Cada criterio vigente del ítem está en **exactamente un** slice: el slice donde su test debe pasar.
- Ningún slice supera `slice_max.criterios`.
- S1 es el esqueleto andante del ítem.
- Cambiar el plan sube `version` y se registra con motivo. Los slices aprobados no se modifican.

---

## 6. Tests de aceptación y `baton/acceptance.lock`

### 6.1 Convención de nombres

- **Un archivo por ítem**, cuyo nombre empieza con el id del ítem: `tests/acceptance/<m>/US_004_cobro_test.py`. El sufijo lo pone el framework (`_test.py`, `.spec.ts`, etc.).
- **Cada test lleva el ítem y el criterio en su nombre**: `test_US_004_AC_1_pago_aprobado` o `it("US-004/AC-1 pago aprobado")`. Como separador valen `-`, `_` o `/`.
- Cada criterio vigente tiene al menos un test.

Con esto, cualquier herramienta asocia test → criterio sin entender el lenguaje, y el lock trabaja por archivo.

### 6.2 Formato del lock

Una línea por archivo protegido, con los campos separados por espacios:

```
# acceptance.lock · formato 1 · lo escribe solo `approve`
# archivo  sha256  item  criterios  aprobado_por  fecha  solicitud
tests/acceptance/pagos/US_004_cobro_test.py      3f1a…c9  US-004  AC-1,AC-2  juan        2026-11-04  US-004-R1
tests/acceptance/catalogo/US_009_precios_test.py 77b0…12  US-009  AC-1,AC-2  juan,maria  2026-11-03  -
tests/acceptance/conftest.py                     a41e…3d  *       -          juan        2026-11-02  -
pytest.ini                                       0c9d…e7  *       -          juan        2026-11-02  -
```

- `sha256` va completo (64 caracteres). Aquí está abreviado.
- `item` es `*` para archivos compartidos (fixtures, helpers, configuración del runner).
- `solicitud` es `-` en la primera aprobación, o el id de la solicitud que autorizó el último cambio.

### 6.3 Qué comprueban el hook y CI

1. Cada archivo del lock existe y su sha256 coincide.
2. Un archivo nuevo en una ruta protegida solo se acepta si su nombre empieza con el id de un ítem en `Listo` o `TestsEnRevision` (es decir, el Autor de tests está trabajando). Si es un archivo compartido nuevo, o un archivo de otro ítem, se rechaza.
3. Cada línea del lock nueva o modificada corresponde a un ítem en `TestsEnRevision` (primera aprobación) o tiene en `solicitud` el id de una solicitud en estado `Aprobada`.

**Límite conocido:** el hook se puede saltar con `git commit --no-verify`, y un agente puede escribir una solicitud marcada como `Aprobada`. El hook atrapa descuidos. La garantía fuerte está en el servidor: una regla de CODEOWNERS (o su equivalente) que exige la revisión de un aprobador humano en todo PR que toque las rutas protegidas, `acceptance.lock` o `baton/config.md`. Setup debe ofrecer generarla.

---

## 7. Solicitud: `baton/modules/<m>/requests/<ítem>-R<n>.md`

Cubre los escalamientos del Driver y las solicitudes de cambio de un test congelado.

```markdown
---
formato: 1
id: US-004-R1
item: US-004
slice: S2
tipo: test                  # test | criterio | diseno | plan
abierta_por: { rol: driver, entidad: sonnet }
creada: 2026-11-03T10:12-03:00
estado: Abierta             # Abierta | Aprobada | Rechazada | Aplicada
decidida_por: null
decidida: null
afecta:
  - tests/acceptance/pagos/US_004_cobro_test.py::test_US_004_AC_3_reintento
---

## Qué pasa
El test espera 3 reintentos, pero la pasarela (ADR-0003) ya reintenta sola.

## Evidencia
Salida del test, documentación de la pasarela.

## Propuesta
Retirar AC-3.

## Decisión
(la escribe el Navigator)
```

**Al resolver una solicitud:**

| Tipo | Si se aprueba | Si se rechaza |
|---|---|---|
| `test` o `criterio` | ítem → `Listo`; el Autor reescribe, `approve` actualiza el lock con esta solicitud, y la solicitud pasa a `Aplicada` | ítem → `TestsCongelados`, con la explicación en `## Decisión` |
| `diseno` o `plan` | el Navigator actualiza el plan o el ADR; ítem → `TestsCongelados` | ítem → `TestsCongelados` |

Mientras la solicitud está `Abierta`, el ítem está en `Escalado`.

---

## 8. Traspaso: `baton/modules/<m>/handoffs/<id>.md`

```markdown
---
formato: 1
id: 2026-11-02-1530-US-004-S1-driver
item: US-004
slice: S1
de:   { rol: aprobador_tests, entidad: juan }
para: { rol: driver, entidad: sonnet, transporte: sesion }
estado: Pendiente           # Pendiente | Tomado | Cerrado
creado: 2026-11-02T15:30-03:00
tomado: null
cerrado: null
config_efectiva:            # foto al crear el traspaso; no se edita
  autonomia:       { valor: Pair, fuente: item, bajada: false }
  verificador:     { activo: true, entidad: codex, transporte: externo, fuente: proyecto }
  aprobador_tests: { valor: [juan], fuente: proyecto }
  driver:          { entidad: sonnet, transporte: sesion, fuente: proyecto }
  slice_max:       { criterios: 3, minutos: 30, fuente: proyecto }
  comandos:        { aceptacion: "pytest tests/acceptance", unitarios: "pytest tests/unit", todos: "pytest" }
leer:
  - baton/backlog/items/US-004.md
  - baton/modules/pagos/plans/US-004.md
  - baton/system/overview.md
  - baton/system/adr/ADR-0003-pasarela.md
no_tocar:
  - tests/acceptance/**
  - baton/acceptance.lock
  - baton/config.md
  - baton/modules/pagos/module.md
  - baton/modules/pagos/plans/**
  - baton/backlog/items/**   # salvo el campo estado de US-004
---

## Qué se entrega
Tests de aceptación de US-004 congelados (AC-1 y AC-2). S1 cubre AC-1.

## Qué se espera
Implementar S1 con TDD hasta que los tests de AC-1 pasen, sin romper los anteriores.
Los tests de AC-2 siguen en rojo: es lo esperado.

## Tests del slice
| Test | Criterio | Estado al entregar |
|---|---|---|
| tests/acceptance/pagos/US_004_cobro_test.py::test_US_004_AC_1_pago_aprobado | AC-1 | rojo verificado |

## Contexto
Decisiones previas y lo relevante de conversaciones anteriores, resumido.
El receptor no puede asumir nada que no esté aquí o en `leer`.

## Al terminar
1. Escribir `baton/modules/pagos/reports/US-004-S1.md`.
2. Cambiar US-004 a `EnVerificacion`.
3. Crear el traspaso para `verificador`.
4. Si hay que escalar: crear la solicitud en `requests/`, cambiar US-004 a `Escalado`
   y crear el traspaso para `navigator`.
```

**Reglas:**

- **Ciclo del traspaso:** queda `Pendiente` al crearse, pasa a `Tomado` cuando el receptor empieza y a `Cerrado` cuando el receptor crea su propio traspaso de salida.
- Cada ítem tiene como máximo un traspaso `Pendiente` o `Tomado` a la vez.
- `config_efectiva` resuelve todas las variables de la sección 3, con su `fuente`. Así queda registrado qué configuración se usó en cada slice.
- En el traspaso del Autor al Aprobador, `## Tests del slice` muestra la evidencia del **rojo verificado**: la razón por la que falla cada test. `approve` vuelve a ejecutarlos antes de congelar.
- Las secciones `## Qué se espera` y `## Al terminar` salen de una plantilla por rol, que completa la skill.

---

## 9. Reporte de slice: `baton/modules/<m>/reports/<ítem>-S<n>.md`

```markdown
---
formato: 1
item: US-004
slice: S1
estado: EnVerificacion      # EnCurso | EnVerificacion | Rechazado | EnRevision | Terminado | Aprobado
intento: 1
driver: sonnet
commits: [a1b2c3d, e4f5a6b]
resultado:                  # lo declara el Driver; el Verificador lo vuelve a medir
  aceptacion_slice: { pasan: 1, fallan: 0 }
  aceptacion_resto: { pasan: 0, fallan: 1 }   # tests de slices futuros: rojo esperado
  unitarios:        { nuevos: 4, pasan: 31, fallan: 0 }
  anteriores_rotos: 0
  lock_intacto: true
---

## Qué se hizo
Resumen por capa, en 3–8 líneas.

## Rojo → verde
| Test | Fallaba por | Pasa |
|---|---|---|
| test_US_004_AC_1_pago_aprobado | 404 en POST /pagos | sí |

## Decisiones tomadas
Solo las que el Driver puede tomar solo. Las demás van en una solicitud.

## Solicitudes abiertas
Ninguna.

## Cómo probarlo
Pasos de la demo del plan y lo que se debe ver.

## Deuda y observaciones

---

## Verificación

### Intento 1 · codex · 2026-11-02T17:10-03:00
**Veredicto:** Rechazado
**Medición propia:** aceptación del slice 1/1, anteriores rotos 0, lock intacto.

| Severidad | Dónde | Hallazgo |
|---|---|---|
| alta | src/pagos/api.py:42 | el monto se toma del cliente y no del carrito |

## Revisión humana

### Intento 2 · juan · 2026-11-03T09:00-03:00 · alcance: slice
**Veredicto:** Aprobado
Comentarios.
```

**Reglas:**

- El Driver reescribe las secciones de arriba en cada intento. Las versiones anteriores quedan en git.
- `## Verificación` y `## Revisión humana` **solo crecen**: una entrada por intento.
- Si se rechaza, el Driver sube `intento` y vuelve a `EnCurso`.
- **Punto de control humano según autonomía:**
  - En `Pair`, cada slice pasa por `EnRevision`.
  - En `Checkpoint` y `Delegado`, el slice pasa a `Aprobado` si lo aprobó el Verificador, o a `Terminado` si no hay Verificador. Más tarde, `review` agrega una entrada `alcance: item` o `alcance: modulo` en cada reporte que revisa y deja los `Terminado` en `Aprobado`.
- **`Terminado` y `Aprobado` son distintos a propósito.** `Terminado` significa "tests en verde, revisión humana pendiente". El Driver nunca marca su propio slice como `Aprobado` (principio 3). Para avanzar al siguiente slice, los dos cuentan como cerrados.
- El estado del ítem refleja el del slice en curso. Cuando el último slice queda cerrado, el ítem pasa a `Hecho` (en Checkpoint, después de la revisión del ítem).

---

## 10. Vistas generadas

### 10.1 `baton/backlog/BACKLOG.md`

```markdown
<!-- GENERADO por sync el 2026-11-02T18:00-03:00: no editar a mano -->
# Backlog · tienda

**En curso:** 2 de 3 · **Turnos:** navigator 1 · autor_tests 1 · driver 1

## pagos · Pair
| ID | Título | Estado | Turno | Prioridad | Autonomía | Slices | Tests |
|---|---|---|---|---|---|---|---|
| US-004 | Cobrar con tarjeta | EnCurso | driver | 1 | Pair | 1/2 | 2/2 congelados |
| US-006 | Texto del recibo | Listo | autor_tests | 3 | Checkpoint ↓ | 0/1 | – |

## catalogo · Delegado ↓
| ... |

## Candidatos
| ID | Título | Propuesto por | Por qué |
|---|---|---|---|

## Hecho
| ID | Título | Módulo | Cerrado |
|---|---|---|---|
```

### 10.2 `baton/backlog/HISTORY.md`

```markdown
<!-- GENERADO por sync: solo crece; no editar a mano -->
# Historial

| Fecha | Autor | Objeto | Cambio | Motivo | Ref |
|---|---|---|---|---|---|
| 2026-11-02T10:00 | juan | config | autonomia: – → Pair | primer proyecto con el flujo | setup |
| 2026-11-02T10:20 | juan | modulo:catalogo | autonomia: Pair → Delegado ↓ | CRUD interno sin datos sensibles | kickoff |
| 2026-11-02T11:05 | opus | US-004 | estado: Pendiente → Listo | refinado | – |
| 2026-11-02T15:30 | juan | US-004 | tests congelados: AC-1, AC-2, AC-3 | aprobación inicial | acceptance.lock |
| 2026-11-04T09:40 | juan | US-004/AC-3 | retirado | lo resuelve la pasarela | US-004-R1 |
```

- **Objeto:** `config`, `modulo:<m>`, `<ítem>`, `<ítem>/AC-<n>`, `<ítem>/plan`, `<ítem>-S<n>` o `lock`.
- **Ref:** commit, solicitud, traspaso, reporte o skill.
- **Motivo:** obligatorio en cambios de alcance, configuración y tests (principio 6). En los cambios de estado propios del flujo, el motivo es el evento.

---

## 11. Decisiones de formato para revisar

1. Claves y valores fijos en español sin tildes, independientes del idioma del proyecto.
2. El ítem no guarda enlaces: la trazabilidad se arma desde el lock, el plan y los reportes.
3. El estado de cada slice vive en su reporte, no en el plan.
4. Un archivo de tests de aceptación por ítem, para que el lock trabaje por archivo sin entender el lenguaje.
5. Entre los aprobadores de tests tiene que haber al menos una persona.
6. La garantía fuerte de los tests congelados es CODEOWNERS en el servidor. El hook local atrapa descuidos.
7. Un ítem `Escalado` puede volver a `TestsCongelados` cuando la decisión no cambia los tests (antes solo podía volver a `Listo`).
8. El estado de slice `Terminado` separa "tests en verde" de "aprobado por otro". Ver la sección 9.
9. `sync` detecta los cambios comparando con una instantánea propia (`baton/.sync/snapshot.json`, versionada), no con `git diff`. Así ve cambios sin commitear, compara campo por campo y no depende del historial de git.

---

## 12. Archivos de la herramienta

`baton-setup` instala esto en el proyecto:

```
baton/
  bin/baton.py          herramienta determinista: validar, efectiva, next, estado, handoff, tomar, sync, lock
  hooks/pre-commit     llama a `baton.py lock revisar --staged`; .git/hooks/pre-commit lo invoca
  templates/*.md       plantillas de config, módulo, ítem, plan, solicitud y reporte
  .sync/snapshot.json  instantánea del último sync
```

Los traspasos no tienen plantilla: los genera `baton.py handoff`, que calcula `config_efectiva`, `leer`, `no_tocar` y `## Al terminar` según el rol y la autonomía.
