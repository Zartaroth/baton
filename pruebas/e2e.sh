#!/usr/bin/env bash
# Prueba de punta a punta de baton.py: flujo completo, ataques al lock y solicitud de cambio.
# Uso: pruebas/e2e.sh [directorio-temporal]
set -u
AQUI=$(cd "$(dirname "$0")" && pwd)
FX=$AQUI/fixtures; D=${1:-$(mktemp -d)/demo}; SRC=$AQUI/../skills/baton-start/assets/baton.py
FALLAS=0
rm -rf $D && mkdir -p $D && cd $D && git init -q && git config user.email t@t && git config user.name t
python3 $SRC init --hook --codeowners @juan >/dev/null
f(){ python3 baton/bin/baton.py "$@"; local r=$?; echo "  [exit $r]"; }
ok(){ echo "OK   $1"; }; bad(){ echo "FALLA $1"; FALLAS=$((FALLAS+1)); }
cp $FX/config.md baton/config.md
mkdir -p baton/modules/{catalogo,pagos}/{plans,requests,reports}
cp $FX/module.md baton/modules/catalogo/module.md; cp $FX/pagos.md baton/modules/pagos/module.md
cp $FX/US-00*.md baton/backlog/items/
python3 baton/bin/baton.py sync --autor juan --motivo "visión inicial" >/dev/null && git add -A && git commit -qm init >/dev/null && ok "setup + sync + commit"
cp $FX/plan-US-001.md baton/modules/catalogo/plans/US-001.md
python3 baton/bin/baton.py estado US-001 Listo >/dev/null && ok "Pendiente → Listo con DoR"
mkdir -p tests/acceptance/catalogo
cat > tests/acceptance/catalogo/US_001_listar_test.py <<'PY'
import unittest
class T(unittest.TestCase):
    def test_US_001_AC_1_lista_con_precio(self): self.fail("no implementado")
    def test_US_001_AC_2_vacio(self): self.fail("no implementado")
PY
echo "# conftest" > tests/conftest.py
python3 baton/bin/baton.py estado US-001 TestsEnRevision >/dev/null
git add -A && git commit -qm "tests" >/dev/null && ok "autor commitea tests nuevos (ítem en TestsEnRevision)"
python3 baton/bin/baton.py lock aprobar --item US-001 --aprobado-por sonnet >/dev/null 2>&1 && bad "driver aprueba" || ok "driver no puede aprobar"
mkdir -p tests/acceptance/catalogo/__pycache__ && echo basura > tests/acceptance/catalogo/__pycache__/US_001_listar_test.cpython-314.pyc
python3 baton/bin/baton.py lock aprobar --item US-001 --aprobado-por juan >/dev/null && python3 baton/bin/baton.py estado US-001 TestsCongelados >/dev/null
grep -q "pyc" baton/acceptance.lock && bad "el lock congeló un .pyc" || ok "el lock ignora __pycache__"
python3 baton/bin/baton.py sync --autor juan --motivo "aprobación inicial" >/dev/null && git add -A && git commit -qm approve >/dev/null && ok "aprobación + commit"
# ataques
sed -i 's/self.fail("no implementado")/pass/' tests/acceptance/catalogo/US_001_listar_test.py
git add -A; git commit -qm hack1 >/dev/null 2>&1 && bad "edición de test congelado pasó" || ok "rechaza edición de test congelado"
H=$(sha256sum tests/acceptance/catalogo/US_001_listar_test.py | cut -d' ' -f1)
sed -i -E "s/^(tests\/acceptance\S+\s+)[0-9a-f]{64}/\1$H/" baton/acceptance.lock
git add -A; git commit -qm hack2 >/dev/null 2>&1 && bad "test + lock a mano pasó" || ok "rechaza test + lock editado a mano"
git reset -q --hard HEAD
echo x > tests/acceptance/conftest.py; git add -A; git commit -qm hack3 >/dev/null 2>&1 && bad "fixture nuevo pasó" || ok "rechaza fixture compartido nuevo"
git reset -q --hard HEAD; git clean -qfd
# driver
T=$(python3 baton/bin/baton.py handoff --item US-001 --slice S1 --de aprobador_tests --para driver)
python3 baton/bin/baton.py tomar $(basename $T .md) >/dev/null && python3 baton/bin/baton.py estado US-001 EnCurso >/dev/null && ok "driver toma el turno"
mkdir -p src && echo "print(1)" > src/app.py
mkdir -p baton/modules/catalogo/reports; sed -e 's/<ítem>/US-001/; s/<S n>/S1/; s/<entidad>/sonnet/' baton/templates/report.md > baton/modules/catalogo/reports/US-001-S1.md
python3 baton/bin/baton.py estado US-001-S1 Terminado >/dev/null
python3 baton/bin/baton.py next --rol driver | grep -q "slice S2" && ok "next muestra el siguiente slice (S2)" || bad "next"
python3 baton/bin/baton.py sync --autor sonnet --motivo "S1" >/dev/null && git add -A && git commit -qm s1 >/dev/null && ok "commit de código"
# solicitud de cambio legítima
mkdir -p baton/modules/catalogo/requests; sed -e 's/<ítem>-R<n>/US-001-R1/; s/^item: <ítem>/item: US-001/; s/<S n o null>/S2/; s/{ rol: <rol>, entidad: <entidad> }/{ rol: driver, entidad: sonnet }/; s/<AAAA-MM-DDTHH:MM±HH:MM>/2026-11-03T14:00-05:00/' baton/templates/request.md > baton/modules/catalogo/requests/US-001-R1.md
python3 baton/bin/baton.py estado US-001 Escalado >/dev/null
python3 baton/bin/baton.py estado US-001-R1 Aprobada >/dev/null
grep -q "^estado: Aprobada *# " baton/modules/catalogo/requests/US-001-R1.md && ok "estado conserva el comentario YAML" || bad "estado rompe comentario"
python3 baton/bin/baton.py estado US-001 Listo >/dev/null
sed -i 's/def test_US_001_AC_2_vacio(self): self.fail("no implementado")/def test_US_001_AC_2_vacio(self): self.fail("pendiente: muestra sin productos")/' tests/acceptance/catalogo/US_001_listar_test.py
python3 baton/bin/baton.py estado US-001 TestsEnRevision >/dev/null
python3 baton/bin/baton.py lock aprobar --item US-001 --aprobado-por juan --solicitud US-001-R1 >/dev/null && ok "recongela con solicitud aprobada"
python3 baton/bin/baton.py estado US-001-R1 Aplicada >/dev/null
python3 baton/bin/baton.py estado US-001 TestsCongelados >/dev/null
python3 baton/bin/baton.py sync --autor juan --motivo "ajuste por R1" --ref US-001-R1 >/dev/null
git add -A && git commit -qm r1 >/dev/null && ok "commit con solicitud aplicada pasa el hook" || bad "commit R1 rechazado"
# Delegado fuerza verificador
cat > baton/backlog/items/US-004.md <<'MD'
---
formato: 1
id: US-004
titulo: Ficha de producto
tipo: historia
modulo: catalogo
estado: Pendiente
prioridad: 3
origen: humano
creado: 2026-11-03
---
MD
python3 baton/bin/baton.py efectiva US-004 | grep -A1 "verificador_activo" | grep -q "valor: true" && ok "Delegado fuerza verificador" || bad "verificador no forzado"
# flujo de inicio: visión, mapa de módulos y tipos de backlog
mkdir -p baton/system && cp $FX/../../skills/baton-start/assets/templates/overview.md baton/system/overview.md
python3 baton/bin/baton.py sync --autor juan --motivo "visión inicial" >/dev/null
grep -q "| vision | creado" baton/backlog/HISTORY.md && ok "sync registra la visión" || bad "visión no registrada"
python3 baton/bin/baton.py estado US-002 Listo 2>&1 | grep -q "módulo Activo" && ok "ítem no pasa a Listo con su módulo sin abrir" || bad "módulo no abierto aceptado"
mkdir -p baton/modules/reportes
cat > baton/modules/reportes/module.md <<'MD'
---
formato: 1
modulo: reportes
titulo: Reportes
estado: Candidato
prioridad: 5
origen: agente
propuesto_por: opus
creado: 2026-11-03
config: {}
---
## Objetivo
Exportar los gastos.

## Por qué se propone
Los usuarios lo piden.
MD
python3 baton/bin/baton.py next --rol navigator | grep -q "modulo:reportes · Candidato" && ok "next pide decidir el módulo candidato" || bad "next sin módulo candidato"
python3 baton/bin/baton.py estado modulo:reportes Activo >/dev/null 2>&1 && bad "módulo candidato pasó directo a Activo" || ok "módulo candidato no salta a Activo"
python3 baton/bin/baton.py estado modulo:reportes Descartado >/dev/null && ok "módulo candidato descartado"
python3 baton/bin/baton.py estado modulo:catalogo Cerrado 2>&1 | grep -q "ítems en desarrollo" && ok "no cierra un módulo con ítems en desarrollo" || bad "cerró módulo con trabajo"
grep -q "## Mapa de módulos" baton/backlog/BACKLOG.md && ok "BACKLOG.md muestra el mapa de módulos" || bad "sin mapa de módulos"
sed -e 's/^id: US-004/id: TEC-001/; s/^tipo: historia/tipo: tecnico/' baton/backlog/items/US-004.md > baton/backlog/items/TEC-001.md
python3 baton/bin/baton.py validar 2>&1 | grep -q "no está en backlog.principal" && ok "rechaza un tipo fuera del backlog configurado" || bad "tipo fuera del backlog aceptado"
rm baton/backlog/items/TEC-001.md
mkdir -p $D-vacio && git -C $D-vacio init -q && python3 baton/bin/baton.py --root $D-vacio detectar | grep -q "inicio: nuevo" && ok "detectar: proyecto vacío es nuevo" || bad "detectar"
python3 baton/bin/baton.py init --hook >/dev/null 2>&1 && ok "init --hook reinstala su propio hook" || bad "init --hook rechaza su propio hook"
sed -i 's/verificador:     { entidad: codex, transporte: externo, activo: false }/verificador:     { entidad: null, transporte: sesion, activo: false }/' baton/config.md
python3 baton/bin/baton.py validar 2>&1 | grep -q "el verificador no tiene entidad" && ok "avisa si el verificador no tiene entidad" || bad "sin aviso de verificador sin entidad"
git checkout -q -- baton/config.md
python3 baton/bin/baton.py validar >/dev/null && ok "validar ok al final" || { bad "validar"; python3 baton/bin/baton.py validar; }
echo; grep -A6 "## catalogo" baton/backlog/BACKLOG.md
echo; [ $FALLAS -eq 0 ] && echo "todo ok" || { echo "$FALLAS falla(s)"; exit 1; }
