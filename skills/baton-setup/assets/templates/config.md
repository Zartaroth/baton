---
formato: 1
proyecto: <nombre>
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
  destino: null

rutas:
  tests_aceptacion: tests/acceptance
  protegidos: []            # archivos extra que cubre acceptance.lock (config del runner, fixtures)

comandos:
  aceptacion: "<comando>"
  aceptacion_archivo: "<comando> {archivo}"
  unitarios: "<comando>"
  todos: "<comando>"

entidades:
  <persona>: { tipo: persona }
  <modelo>:  { tipo: modelo, modelo: <id>, herramienta: <herramienta> }

roles:
  navigator:       { entidades: [<persona>, <modelo-razonador>] }
  autor_tests:     { entidad: <modelo-razonador>, transporte: subagente }
  aprobador_tests: { entidades: [<persona>] }
  driver:          { entidad: <modelo-implementador>, transporte: sesion }
  verificador:     { entidad: <otro-modelo>, transporte: sesion, activo: false }

autonomia: Checkpoint       # Pair | Checkpoint | Delegado
autonomia_minima: null      # null | Checkpoint | Pair

slice_max:
  criterios: 3
  minutos: 30
---

# Configuración del proyecto

Notas: por qué se eligió esta configuración y convenciones del equipo.
