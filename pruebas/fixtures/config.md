---
formato: 1
proyecto: tienda
idioma: es
cadencia: { modo: kanban, iteracion_dias: null }
wip: 2
tipos: { historia: US, bug: BUG }
herramienta_externa: { tipo: ninguna, destino: null }
rutas:
  tests_aceptacion: tests/acceptance
  protegidos: [tests/conftest.py]
comandos:
  aceptacion: "python3 -m unittest discover tests/acceptance"
  aceptacion_archivo: "python3 {archivo}"
  unitarios: "python3 -m unittest discover tests/unit"
  todos: "python3 -m unittest discover tests"
entidades:
  juan:   { tipo: persona }
  opus:   { tipo: modelo, modelo: claude-opus-5-5, herramienta: claude-code }
  sonnet: { tipo: modelo, modelo: claude-sonnet-5-5, herramienta: claude-code }
  codex:  { tipo: modelo, modelo: x, herramienta: codex }
roles:
  navigator:       { entidades: [juan, opus] }
  autor_tests:     { entidad: opus, transporte: subagente }
  aprobador_tests: { entidades: [juan] }
  driver:          { entidad: sonnet, transporte: sesion }
  verificador:     { entidad: codex, transporte: externo, activo: false }
autonomia: Pair
autonomia_minima: null
slice_max: { criterios: 2, minutos: 30 }
---
# Config
