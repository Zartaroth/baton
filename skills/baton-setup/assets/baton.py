#!/usr/bin/env python3
"""baton.py: herramienta determinista de la metodología.

Hace lo que no debe depender del criterio de un agente: validar archivos,
calcular la configuración efectiva, decir a quién le toca el turno, sincronizar
el backlog y el historial, mantener acceptance.lock y crear traspasos.

Requiere Python 3.10+ y PyYAML (pip install pyyaml).
Formatos: ver FORMATOS.md de la metodología.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("baton.py necesita PyYAML: pip install pyyaml")

FORMATO = 1

ESTADOS = ["Candidato", "Pendiente", "Listo", "TestsEnRevision", "TestsCongelados",
           "EnCurso", "Escalado", "EnVerificacion", "EnRevision", "Hecho", "Descartado"]
ESTADOS_SLICE = ["EnCurso", "EnVerificacion", "Rechazado", "EnRevision", "Terminado", "Aprobado"]
# Terminado: tests en verde, revisión humana diferida (Checkpoint/Delegado sin verificador).
# Aprobado: lo aprobó alguien distinto del Driver (verificador o humano).
SLICE_CERRADO = {"Terminado", "Aprobado"}
ESTADOS_SOLICITUD = ["Abierta", "Aprobada", "Rechazada", "Aplicada"]
ESTADOS_TRASPASO = ["Pendiente", "Tomado", "Cerrado"]
ROLES = ["navigator", "autor_tests", "aprobador_tests", "driver", "verificador"]
AUTONOMIA = {"Delegado": 0, "Checkpoint": 1, "Pair": 2}

TURNO = {
    "Candidato": "navigator", "Pendiente": "navigator", "Escalado": "navigator",
    "Listo": "autor_tests", "TestsEnRevision": "aprobador_tests",
    "TestsCongelados": "driver", "EnCurso": "driver",
    "EnVerificacion": "verificador", "EnRevision": "navigator",
}
WIP_ESTADOS = {"EnCurso", "Escalado", "EnVerificacion", "EnRevision"}
# Estados en los que el ítem ya pasó la Definition of Ready.
POST_DOR = {"Listo", "TestsEnRevision", "TestsCongelados", "EnCurso", "Escalado",
            "EnVerificacion", "EnRevision", "Hecho"}
TRANSICIONES = {
    "Candidato": {"Pendiente", "Descartado"},
    "Pendiente": {"Listo", "Descartado"},
    "Listo": {"TestsEnRevision", "Pendiente"},
    "TestsEnRevision": {"Listo", "TestsCongelados"},
    "TestsCongelados": {"EnCurso"},
    "EnCurso": {"Escalado", "EnVerificacion", "EnRevision", "Hecho"},
    "Escalado": {"Listo", "TestsCongelados"},
    "EnVerificacion": {"EnCurso", "EnRevision", "Hecho"},
    "EnRevision": {"EnCurso", "Hecho"},
    "Hecho": {"Pendiente"},
    "Descartado": set(),
}

# Claves que cada nivel puede sobrescribir (FORMATOS.md, sección 3).
CLAVES_MODULO = {"roles.navigator", "roles.autor_tests", "roles.aprobador_tests", "roles.driver",
                 "roles.verificador", "roles.verificador.activo", "autonomia",
                 "slice_max.criterios", "slice_max.minutos"}
CLAVES_ITEM = {"roles.aprobador_tests", "roles.verificador.activo", "autonomia"}

FM_RE = re.compile(r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)(.*)\Z", re.S)
AC_RE = re.compile(r"^###\s+(AC-\d+)\b(.*)$", re.M)
SEC_RE = re.compile(r"^##\s+(.+?)\s*$", re.M)
AVISO_GENERADO = "<!-- GENERADO por sync{extra}: no editar a mano -->"


class BatonError(Exception):
    pass


# ---------------------------------------------------------------- utilidades

def ahora() -> datetime:
    return datetime.now().astimezone().replace(microsecond=0)


def normalizar(v):
    """Convierte fechas a texto para poder comparar y guardar en JSON."""
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    if isinstance(v, dict):
        return {str(k): normalizar(x) for k, x in v.items()}
    if isinstance(v, list):
        return [normalizar(x) for x in v]
    return v


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def leer_md(path: Path) -> tuple[dict, str]:
    texto = path.read_text(encoding="utf-8")
    m = FM_RE.match(texto)
    if not m:
        raise BatonError(f"{path}: falta el frontmatter YAML (--- ... ---)")
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        raise BatonError(f"{path}: YAML inválido: {e}") from e
    if not isinstance(fm, dict):
        raise BatonError(f"{path}: el frontmatter debe ser un mapa")
    return normalizar(fm), m.group(2)


def secciones(body: str) -> dict[str, str]:
    """Secciones de nivel 2 (## Título) → contenido."""
    res, partes = {}, SEC_RE.split(body)
    for i in range(1, len(partes), 2):
        res[partes[i].strip()] = partes[i + 1].strip()
    return res


def criterios(body: str) -> dict[str, dict]:
    """Criterios ### AC-n dentro de '## Criterios de aceptación'."""
    sec = secciones(body).get("Criterios de aceptación", "")
    res, marcas = {}, list(AC_RE.finditer(sec))
    for i, m in enumerate(marcas):
        fin = marcas[i + 1].start() if i + 1 < len(marcas) else len(sec)
        bloque = sec[m.start():fin]
        res[m.group(1)] = {
            "titulo": m.group(2).strip(" ·-"),
            "retirado": "~~" in m.group(2),
            "texto": bloque,
            "hash": sha256(bloque.strip().encode())[:12],
        }
    return res


def vacio(texto: str) -> bool:
    t = re.sub(r"[()\s\-–.]", "", texto.lower())
    return t in ("", "vacío", "vacio", "ninguna", "ninguno", "nada")


def aplanar(d, prefijo="") -> dict:
    res = {}
    if isinstance(d, dict):
        for k, v in d.items():
            res.update(aplanar(v, f"{prefijo}{k}."))
    else:
        res[prefijo[:-1]] = d
    return res


def corto(v) -> str:
    if v is None:
        return "–"
    s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
    s = s.replace("\n", " ")
    return s if len(s) <= 60 else s[:57] + "…"


def celda(s) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def id_test(item_id: str) -> str:
    """US-004 → US_004 (forma usada en nombres de archivo y de test)."""
    return item_id.replace("-", "_")


def git(root: Path, *args, check=True) -> str:
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise BatonError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout if r.returncode == 0 else ""


# ---------------------------------------------------------------- proyecto

class Proyecto:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.flow = self.root / "baton"
        cfg_path = self.flow / "config.md"
        if not cfg_path.exists():
            raise BatonError("no existe baton/config.md: ejecuta primero el setup")
        self.config, _ = leer_md(cfg_path)
        self.modulos: dict[str, dict] = {}
        for p in sorted(self.flow.glob("modules/*/module.md")):
            fm, body = leer_md(p)
            self.modulos[fm.get("modulo", p.parent.name)] = {"fm": fm, "body": body, "path": p}
        self.items: dict[str, dict] = {}
        for p in sorted(self.flow.glob("backlog/items/*.md")):
            fm, body = leer_md(p)
            iid = fm.get("id", p.stem)
            self.items[iid] = {"fm": fm, "body": body, "path": p, "ac": criterios(body)}
        self.planes = self._cargar("modules/*/plans/*.md", "item")
        self.solicitudes = self._cargar("modules/*/requests/*.md", "id")
        self.traspasos = self._cargar("modules/*/handoffs/*.md", "id")
        self.reportes = {}
        for p in sorted(self.flow.glob("modules/*/reports/*.md")):
            fm, body = leer_md(p)
            self.reportes[f"{fm.get('item')}-{fm.get('slice')}"] = {"fm": fm, "body": body, "path": p}
        self.lock = leer_lock(self.flow / "acceptance.lock")

    def _cargar(self, patron, clave):
        res = {}
        for p in sorted(self.flow.glob(patron)):
            fm, body = leer_md(p)
            res[fm.get(clave, p.stem)] = {"fm": fm, "body": body, "path": p}
        return res

    # rutas
    def rel(self, p: Path) -> str:
        return p.resolve().relative_to(self.root).as_posix()

    @property
    def tests_dir(self) -> str:
        return self.config.get("rutas", {}).get("tests_aceptacion", "tests/acceptance").rstrip("/")

    @property
    def protegidos(self) -> list[str]:
        return list(self.config.get("rutas", {}).get("protegidos") or [])

    def es_protegido(self, ruta: str) -> bool:
        return ruta.startswith(self.tests_dir + "/") or ruta in self.protegidos

    def modulo_dir(self, m: str) -> Path:
        return self.flow / "modules" / m

    def archivos_tests(self, item_id: str) -> list[str]:
        """Archivos de tests de aceptación del ítem (empiezan con su id)."""
        base = self.root / self.tests_dir
        if not base.exists():
            return []
        pref = id_test(item_id)
        return sorted(self.rel(p) for p in base.rglob("*")
                      if p.is_file() and (p.name.startswith(pref + "_") or p.name.startswith(item_id + "_")))

    def entidad(self, nombre: str) -> dict:
        return (self.config.get("entidades") or {}).get(nombre) or {}

    def ids_items(self) -> list[str]:
        return list(self.items)


# ---------------------------------------------------------------- configuración efectiva

def entidades_de(rol_cfg) -> list[str]:
    if rol_cfg is None:
        return []
    if isinstance(rol_cfg, list):
        return list(rol_cfg)
    if "entidades" in rol_cfg:
        return list(rol_cfg["entidades"] or [])
    return [rol_cfg["entidad"]] if rol_cfg.get("entidad") else []


def efectiva(pr: Proyecto, modulo: str | None = None, item_id: str | None = None) -> dict:
    cfg = pr.config
    if item_id and not modulo:
        modulo = pr.items[item_id]["fm"].get("modulo")
    roles = copy.deepcopy(cfg.get("roles") or {})
    fuentes = {r: "proyecto" for r in roles}
    aut = {"valor": cfg.get("autonomia"), "fuente": "proyecto", "bajada": False}
    smax = dict(cfg.get("slice_max") or {})
    smax_fuente = "proyecto"
    activo_fuente = "proyecto"
    errores = []

    def aplicar(overrides, nivel, permitidas):
        nonlocal aut, smax_fuente, activo_fuente
        for clave, ov in (overrides or {}).items():
            if clave not in permitidas:
                errores.append(f"{nivel}: la clave '{clave}' no se puede sobrescribir en este nivel")
                continue
            if not isinstance(ov, dict) or "valor" not in ov or not ov.get("motivo"):
                errores.append(f"{nivel}: '{clave}' debe escribirse como {{valor, motivo}}")
                continue
            v = ov["valor"]
            if clave == "autonomia":
                if v not in AUTONOMIA:
                    errores.append(f"{nivel}: autonomia '{v}' no es válida")
                    continue
                bajada = aut["bajada"] or AUTONOMIA[v] < AUTONOMIA.get(aut["valor"], 0)
                aut = {"valor": v, "fuente": nivel.split(":")[0], "bajada": bajada}
            elif clave == "roles.aprobador_tests":
                nuevas = entidades_de(v)
                if nivel.startswith("item"):
                    previas = entidades_de(roles.get("aprobador_tests"))
                    nuevas = previas + [e for e in nuevas if e not in previas]
                roles["aprobador_tests"] = {"entidades": nuevas}
                fuentes["aprobador_tests"] = nivel.split(":")[0]
            elif clave == "roles.verificador.activo":
                if nivel.startswith("item") and v is not True:
                    errores.append(f"{nivel}: el ítem solo puede activar el verificador")
                    continue
                roles.setdefault("verificador", {})["activo"] = bool(v)
                activo_fuente = nivel.split(":")[0]
            elif clave.startswith("roles."):
                rol = clave.split(".", 1)[1]
                if not isinstance(v, dict):
                    errores.append(f"{nivel}: '{clave}' debe ser un mapa {{entidad, transporte}}")
                    continue
                base = roles.get(rol, {}) if rol == "verificador" else {}
                roles[rol] = {**{k: x for k, x in base.items() if k == "activo"}, **v}
                fuentes[rol] = nivel.split(":")[0]
            elif clave.startswith("slice_max."):
                smax[clave.split(".", 1)[1]] = v
                smax_fuente = nivel.split(":")[0]

    if modulo and modulo in pr.modulos:
        aplicar(pr.modulos[modulo]["fm"].get("config"), f"modulo:{modulo}", CLAVES_MODULO)
    if item_id:
        aplicar(pr.items[item_id]["fm"].get("config"), f"item:{item_id}", CLAVES_ITEM)

    minima = cfg.get("autonomia_minima")
    if minima and aut["valor"] in AUTONOMIA and AUTONOMIA[aut["valor"]] < AUTONOMIA.get(minima, 0):
        errores.append(f"la autonomía efectiva {aut['valor']} está por debajo de la mínima del proyecto ({minima})")
    ver = roles.setdefault("verificador", {})
    if aut["valor"] == "Delegado" and not ver.get("activo"):
        ver["activo"] = True
        activo_fuente = "forzado por Delegado"
        if not ver.get("entidad"):
            errores.append("la autonomía es Delegado pero no hay entidad para el verificador")

    return {
        "autonomia": aut,
        "autonomia_minima": minima,
        "roles": {r: {**roles[r], "fuente": fuentes.get(r, "proyecto")} for r in roles},
        "verificador_activo": {"valor": bool(ver.get("activo")), "fuente": activo_fuente},
        "slice_max": {**smax, "fuente": smax_fuente},
        "comandos": cfg.get("comandos") or {},
        "errores": errores,
    }


# ---------------------------------------------------------------- lock

LOCK_CAMPOS = ["archivo", "sha256", "item", "criterios", "aprobado_por", "fecha", "solicitud"]
LOCK_CABECERA = ("# acceptance.lock · formato 1 · lo escribe solo `approve` (baton.py lock aprobar)\n"
                 "# archivo  sha256  item  criterios  aprobado_por  fecha  solicitud\n")


def parsear_lock(texto: str) -> dict[str, dict]:
    res = {}
    for n, linea in enumerate(texto.splitlines(), 1):
        if not linea.strip() or linea.lstrip().startswith("#"):
            continue
        campos = linea.split()
        if len(campos) != len(LOCK_CAMPOS):
            raise BatonError(f"acceptance.lock línea {n}: se esperaban {len(LOCK_CAMPOS)} campos")
        fila = dict(zip(LOCK_CAMPOS, campos))
        res[fila["archivo"]] = fila
    return res


def leer_lock(path: Path) -> dict[str, dict]:
    return parsear_lock(path.read_text(encoding="utf-8")) if path.exists() else {}


def escribir_lock(path: Path, filas: dict[str, dict]):
    lineas = [LOCK_CABECERA.rstrip("\n")]
    for archivo in sorted(filas):
        lineas.append("  ".join(filas[archivo][c] for c in LOCK_CAMPOS))
    path.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def criterios_en_test(texto: str, item_id: str) -> set[str]:
    pref = re.escape(id_test(item_id)).replace("_", "[-_]")
    return {f"AC-{n}" for n in re.findall(pref + r"[-_/ ]AC[-_](\d+)", texto)}


# ---------------------------------------------------------------- validación

def validar(pr: Proyecto) -> tuple[list[str], list[str]]:
    errores, avisos = [], []
    cfg = pr.config
    if cfg.get("formato") != FORMATO:
        errores.append(f"config.md: formato debe ser {FORMATO}")
    ents = cfg.get("entidades") or {}
    roles = cfg.get("roles") or {}
    for r in ROLES:
        if r not in roles and r != "verificador":
            errores.append(f"config.md: falta el rol '{r}'")

    def revisar_roles(roles, donde):
        for r, rc in roles.items():
            if r not in ROLES:
                errores.append(f"{donde}: rol desconocido '{r}'")
                continue
            for e in entidades_de(rc):
                if e not in ents:
                    errores.append(f"{donde}: la entidad '{e}' del rol {r} no está en config.md")
        driver = set(entidades_de(roles.get("driver")))
        autor = set(entidades_de(roles.get("autor_tests")))
        aprob = set(entidades_de(roles.get("aprobador_tests")))
        ver = set(entidades_de(roles.get("verificador")))
        if driver & aprob or driver & autor:
            errores.append(f"{donde}: el driver no puede escribir ni aprobar tests de aceptación (invariante 1)")
        if autor & aprob:
            errores.append(f"{donde}: autor y aprobador de tests deben ser entidades distintas (invariante 2)")
        if ver and ver & driver:
            avisos.append(f"{donde}: verificador y driver son la misma entidad; usa una sesión distinta sin el contexto del driver (invariante 4)")
        if aprob and not any((ents.get(e) or {}).get("tipo") == "persona" for e in aprob):
            errores.append(f"{donde}: entre los aprobadores de tests debe haber al menos una persona (invariante 9)")

    if cfg.get("autonomia") not in AUTONOMIA:
        errores.append("config.md: autonomia debe ser Pair, Checkpoint o Delegado")
    if cfg.get("autonomia_minima") not in (None, *AUTONOMIA):
        errores.append("config.md: autonomia_minima no es válida")
    cad = cfg.get("cadencia") or {}
    if cad.get("modo") not in ("kanban", "scrum"):
        errores.append("config.md: cadencia.modo debe ser kanban o scrum")
    if cad.get("modo") == "scrum" and not cad.get("iteracion_dias"):
        errores.append("config.md: iteracion_dias es obligatorio con scrum")
    for e, d in ents.items():
        if (d or {}).get("tipo") not in ("persona", "modelo"):
            errores.append(f"config.md: la entidad '{e}' debe tener tipo persona o modelo")

    ef = efectiva(pr)
    errores += [f"config.md: {e}" for e in ef["errores"]]
    revisar_roles(roles, "config.md")

    for m, mod in pr.modulos.items():
        fm = mod["fm"]
        if fm.get("estado") not in ("Planificado", "Activo", "Cerrado"):
            errores.append(f"módulo {m}: estado no válido")
        for clave, ov in (fm.get("config") or {}).items():
            if isinstance(ov, dict) and not ov.get("desde"):
                errores.append(f"módulo {m}: '{clave}' necesita 'desde'")
        ef = efectiva(pr, modulo=m)
        errores += [f"módulo {m}: {e}" for e in ef["errores"]]
        revisar_roles({r: v for r, v in ef["roles"].items()}, f"módulo {m}")

    prefijos = set((cfg.get("tipos") or {}).values())
    for iid, it in pr.items.items():
        fm, donde = it["fm"], f"ítem {iid}"
        if fm.get("formato") != FORMATO:
            errores.append(f"{donde}: formato debe ser {FORMATO}")
        if it["path"].stem != iid:
            errores.append(f"{donde}: el archivo debe llamarse {iid}.md")
        tipos = cfg.get("tipos") or {}
        if fm.get("tipo") not in tipos:
            errores.append(f"{donde}: tipo '{fm.get('tipo')}' no está en config.md")
        elif not str(iid).startswith(tipos[fm["tipo"]] + "-"):
            errores.append(f"{donde}: el id debe empezar con {tipos[fm['tipo']]}-")
        if prefijos and str(iid).split("-")[0] not in prefijos:
            pass
        est = fm.get("estado")
        if est not in ESTADOS:
            errores.append(f"{donde}: estado '{est}' no válido")
            continue
        if not fm.get("titulo"):
            errores.append(f"{donde}: falta titulo")
        m = fm.get("modulo")
        if m and m not in pr.modulos:
            errores.append(f"{donde}: el módulo '{m}' no existe")
        if est in POST_DOR:
            if not m:
                errores.append(f"{donde}: un ítem en {est} necesita módulo")
            errores += [f"{donde}: {e}" for e in faltas_dor(pr, iid)]
        if m in pr.modulos:
            ef = efectiva(pr, item_id=iid)
            errores += [f"{donde}: {e}" for e in ef["errores"]]
            revisar_roles({r: v for r, v in ef["roles"].items()}, donde)
        for dep in fm.get("dependencias") or []:
            if dep not in pr.items:
                errores.append(f"{donde}: la dependencia {dep} no existe")
            elif est in POST_DOR and pr.items[dep]["fm"].get("estado") != "Hecho":
                avisos.append(f"{donde}: depende de {dep}, que no está Hecho")
        if fm.get("origen") == "agente" and not fm.get("propuesto_por"):
            avisos.append(f"{donde}: un ítem propuesto por un agente debería tener propuesto_por")

    for iid, pl in pr.planes.items():
        if iid not in pr.items:
            errores.append(f"plan {iid}: el ítem no existe")
            continue
        errores += [f"plan {iid}: {e}" for e in errores_plan(pr, iid)]

    for archivo, fila in pr.lock.items():
        if fila["item"] != "*" and fila["item"] not in pr.items:
            errores.append(f"acceptance.lock: {archivo} apunta a un ítem inexistente ({fila['item']})")
        if not (pr.root / archivo).exists():
            errores.append(f"acceptance.lock: {archivo} no existe")

    for rid, s in pr.solicitudes.items():
        if s["fm"].get("estado") not in ESTADOS_SOLICITUD:
            errores.append(f"solicitud {rid}: estado no válido")
    for tid, t in pr.traspasos.items():
        if t["fm"].get("estado") not in ESTADOS_TRASPASO:
            errores.append(f"traspaso {tid}: estado no válido")
    for rid, r in pr.reportes.items():
        if r["fm"].get("estado") not in ESTADOS_SLICE:
            errores.append(f"reporte {rid}: estado no válido")

    wip = cfg.get("wip")
    en_curso = [i for i, it in pr.items.items() if it["fm"].get("estado") in WIP_ESTADOS]
    if wip and len(en_curso) > wip:
        avisos.append(f"hay {len(en_curso)} ítems en curso y el límite es {wip}")
    return errores, avisos


def faltas_dor(pr: Proyecto, iid: str) -> list[str]:
    it = pr.items[iid]
    sec = secciones(it["body"])
    faltas = []
    if vacio(sec.get("Valor", "")):
        faltas.append("Definition of Ready: falta '## Valor'")
    vigentes = {k: v for k, v in it["ac"].items() if not v["retirado"]}
    if not vigentes:
        faltas.append("Definition of Ready: no hay criterios vigentes")
    for k, v in vigentes.items():
        t = v["texto"].lower()
        if not all(p in t for p in ("dado", "cuando", "entonces")):
            faltas.append(f"Definition of Ready: {k} no tiene Dado / Cuando / Entonces")
    if not vacio(sec.get("Preguntas abiertas", "")):
        faltas.append("Definition of Ready: hay preguntas abiertas")
    if vacio(sec.get("Seguridad", "")):
        faltas.append("Definition of Ready: falta '## Seguridad'")
    if iid not in pr.planes:
        faltas.append("Definition of Ready: falta el plan")
    return faltas


def errores_plan(pr: Proyecto, iid: str) -> list[str]:
    pl, it = pr.planes[iid], pr.items[iid]
    errs = []
    m = it["fm"].get("modulo")
    if m and pl["path"].parent.parent.name != m:
        errs.append(f"el plan debe estar en baton/modules/{m}/plans/")
    vigentes = {k for k, v in it["ac"].items() if not v["retirado"]}
    asignados: dict[str, str] = {}
    ids = set()
    maxc = (efectiva(pr, item_id=iid)["slice_max"] or {}).get("criterios") if m in pr.modulos else None
    for s in pl["fm"].get("slices") or []:
        sid = s.get("id")
        if not sid or not re.fullmatch(r"S\d+", str(sid)):
            errs.append(f"slice con id inválido: {sid}")
            continue
        if sid in ids:
            errs.append(f"slice {sid} repetido")
        ids.add(sid)
        cs = s.get("criterios") or []
        if maxc and len(cs) > maxc:
            errs.append(f"{sid} tiene {len(cs)} criterios; el máximo es {maxc}")
        for c in cs:
            if c not in it["ac"]:
                errs.append(f"{sid}: el criterio {c} no existe en el ítem")
            elif c in asignados:
                errs.append(f"{c} está en {asignados[c]} y en {sid}; debe estar en un solo slice")
            else:
                asignados[c] = sid
    for c in sorted(vigentes - set(asignados)):
        errs.append(f"el criterio {c} no está en ningún slice")
    return errs


# ---------------------------------------------------------------- estado y turnos

def avance(pr: Proyecto, iid: str) -> tuple[int, int]:
    slices = (pr.planes.get(iid, {}).get("fm", {}).get("slices")) or []
    hechos = sum(1 for s in slices if pr.reportes.get(f"{iid}-{s.get('id')}", {}).get("fm", {}).get("estado") in SLICE_CERRADO)
    return hechos, len(slices)


def tests_congelados(pr: Proyecto, iid: str) -> tuple[int, int]:
    vigentes = {k for k, v in pr.items[iid]["ac"].items() if not v["retirado"]}
    cong = set()
    for fila in pr.lock.values():
        if fila["item"] == iid and fila["criterios"] != "-":
            cong |= set(fila["criterios"].split(","))
    return len(vigentes & cong), len(vigentes)


def turno_de(pr: Proyecto, iid: str) -> str:
    est = pr.items[iid]["fm"].get("estado")
    if est == "EnRevision":
        return "humano"
    return TURNO.get(est, "–")


def siguiente_slice(pr: Proyecto, iid: str) -> str | None:
    for s in (pr.planes.get(iid, {}).get("fm", {}).get("slices")) or []:
        if pr.reportes.get(f"{iid}-{s.get('id')}", {}).get("fm", {}).get("estado") not in SLICE_CERRADO:
            return s.get("id")
    return None


def cambiar_estado(pr: Proyecto, objetivo: str, nuevo: str, forzar=False) -> str:
    m = re.fullmatch(r"(.+)-(S\d+)", objetivo)
    if m and objetivo not in pr.items:
        rep = pr.reportes.get(objetivo)
        if not rep:
            raise BatonError(f"no existe el reporte {objetivo}")
        if nuevo not in ESTADOS_SLICE:
            raise BatonError(f"estado de slice no válido: {nuevo}")
        path, previo = rep["path"], rep["fm"].get("estado")
    elif objetivo in pr.solicitudes:
        if nuevo not in ESTADOS_SOLICITUD:
            raise BatonError(f"estado de solicitud no válido: {nuevo}")
        path, previo = pr.solicitudes[objetivo]["path"], pr.solicitudes[objetivo]["fm"].get("estado")
    else:
        if objetivo not in pr.items:
            raise BatonError(f"no existe el ítem {objetivo}")
        if nuevo not in ESTADOS:
            raise BatonError(f"estado no válido: {nuevo}")
        path, previo = pr.items[objetivo]["path"], pr.items[objetivo]["fm"].get("estado")
        if not forzar and nuevo not in TRANSICIONES.get(previo, set()):
            raise BatonError(f"transición no permitida: {previo} → {nuevo} (usa --forzar si el humano lo decidió)")
        if nuevo in POST_DOR and previo in ("Pendiente", "Candidato"):
            faltas = faltas_dor(pr, objetivo)
            if faltas:
                raise BatonError("; ".join(faltas))
    texto = path.read_text(encoding="utf-8")
    fm_m = FM_RE.match(texto)
    nuevo_fm, n = re.subn(r"^estado:[ \t]*[^\s#]*", f"estado: {nuevo}", fm_m.group(1), count=1, flags=re.M)
    if n == 0:
        raise BatonError(f"{path}: no tiene campo estado")
    path.write_text(texto.replace(fm_m.group(1), nuevo_fm, 1), encoding="utf-8")
    return f"{objetivo}: {previo} → {nuevo}"


# ---------------------------------------------------------------- traspasos

def no_tocar(pr: Proyecto, rol: str, iid: str, m: str) -> list[str]:
    td = f"{pr.tests_dir}/**"
    base = ["baton/acceptance.lock", "baton/config.md", f"baton/modules/{m}/module.md",
            f"baton/modules/{m}/plans/**", f"baton/backlog/items/** (salvo el campo estado de {iid})"]
    if rol == "driver":
        return [td, *pr.protegidos, *base]
    if rol == "autor_tests":
        return [*base, "código de producción (solo escribe tests de aceptación)"]
    if rol == "verificador":
        return ["** (salvo la sección Verificación del reporte y el estado del ítem y del reporte)"]
    if rol == "aprobador_tests":
        return [td + " (si un test está mal se rechaza, no se corrige)", "código de producción"]
    return [td, "baton/acceptance.lock"]


def leer_para(pr: Proyecto, rol: str, iid: str, m: str, sid: str | None) -> list[str]:
    it = pr.items[iid]
    res = [pr.rel(it["path"]), f"baton/modules/{m}/module.md"]
    if (pr.flow / "system/overview.md").exists():
        res.append("baton/system/overview.md")
    if iid in pr.planes:
        res.append(pr.rel(pr.planes[iid]["path"]))
    if rol in ("aprobador_tests", "verificador"):
        res += pr.archivos_tests(iid)
    if rol in ("verificador", "navigator", "driver") and sid and f"{iid}-{sid}" in pr.reportes:
        res.append(pr.rel(pr.reportes[f"{iid}-{sid}"]["path"]))
    if rol == "verificador":
        res.append("baton/acceptance.lock")
    if rol == "navigator":
        res += [pr.rel(s["path"]) for s in pr.solicitudes.values()
                if s["fm"].get("item") == iid and s["fm"].get("estado") == "Abierta"]
    return res


def cierre_slice(ef: dict, iid: str, sid: str, rol: str) -> list[str]:
    aut = ef["autonomia"]["valor"]
    h = f"python3 baton/bin/baton.py handoff --item {iid}"
    if aut == "Pair":
        return [f"Cambiar el reporte y el ítem a `EnRevision`.",
                f"Crear el traspaso para la revisión humana: `{h} --slice {sid} --de {rol} --para navigator`."]
    final = ("cambiar el ítem a `EnRevision` y crear el traspaso para `navigator` (revisión del ítem)"
             if aut == "Checkpoint" else
             "cambiar el ítem a `Hecho` (el humano revisa al cerrar el módulo)")
    cierre = "Aprobado" if rol == "verificador" else "Terminado"
    return [f"Cambiar el reporte a `{cierre}` (autonomía {aut}: la revisión humana es después).",
            f"Si quedan slices: ítem en `EnCurso` y traspaso a `driver` con el siguiente: `{h} --slice <siguiente> --de {rol} --para driver`.",
            f"Si era el último slice: {final}."]


def al_terminar(pr: Proyecto, rol: str, iid: str, m: str, sid: str | None, ef: dict) -> list[str]:
    h = f"python3 baton/bin/baton.py handoff --item {iid}"
    rep = f"baton/modules/{m}/reports/{iid}-{sid}.md"
    escalar = (f"Si hay que escalar: crear `baton/modules/{m}/requests/{iid}-R<n>.md` (plantilla en baton/templates/request.md), "
               f"`python3 baton/bin/baton.py estado {iid} Escalado` y `{h} --de {rol} --para navigator`.")
    if rol == "autor_tests":
        return [f"Escribir los tests en `{pr.tests_dir}/{m}/{id_test(iid)}_<tema>_test.<ext>`, un archivo por ítem; "
                f"cada test con `{id_test(iid)}_AC_<n>` en el nombre.",
                f"Ejecutar cada archivo (`comandos.aceptacion_archivo`) y comprobar que falla **por la razón correcta**.",
                f"`python3 baton/bin/baton.py estado {iid} TestsEnRevision`.",
                f"Crear el traspaso `{h} --de autor_tests --para aprobador_tests` y completar en él la evidencia del rojo."]
    if rol == "aprobador_tests":
        return ["Revisar que cada test refleje su criterio, sea claro y se pueda implementar.",
                "Si apruebas: ejecutar la skill `baton-approve`.",
                f"Si rechazas: `python3 baton/bin/baton.py estado {iid} Listo` y `{h} --de aprobador_tests --para autor_tests`, con los motivos en `## Contexto`."]
    if rol == "driver":
        pasos = [f"Escribir `{rep}` (plantilla en baton/templates/report.md)."]
        if ef["verificador_activo"]["valor"]:
            pasos += [f"Cambiar el reporte y el ítem a `EnVerificacion`.",
                      f"Crear el traspaso `{h} --slice {sid} --de driver --para verificador`."]
        else:
            pasos += cierre_slice(ef, iid, sid, "driver")
        return pasos + [escalar]
    if rol == "verificador":
        return [f"Agregar tu entrada en `## Verificación` de `{rep}`, con tu propia medición de los tests.",
                f"Si rechazas: reporte a `Rechazado`, `python3 baton/bin/baton.py estado {iid} EnCurso` y `{h} --slice {sid} --de verificador --para driver`.",
                "Si apruebas:", *["  " + p for p in cierre_slice(ef, iid, sid, "verificador")]]
    return ["Decidir y escribir la decisión en el archivo que corresponda (solicitud, plan, ítem o reporte).",
            "Mover el ítem al estado que indica la decisión y crear el traspaso para el rol que sigue."]


def crear_traspaso(pr: Proyecto, iid: str, de: str, para: str, sid: str | None, entidad_de: str | None) -> Path:
    if iid not in pr.items:
        raise BatonError(f"no existe el ítem {iid}")
    if de not in ROLES or para not in ROLES:
        raise BatonError(f"roles válidos: {', '.join(ROLES)}")
    m = pr.items[iid]["fm"].get("modulo")
    if not m or m not in pr.modulos:
        raise BatonError(f"el ítem {iid} no tiene un módulo válido")
    ef = efectiva(pr, item_id=iid)
    if ef["errores"]:
        raise BatonError("; ".join(ef["errores"]))
    rol_para = ef["roles"].get(para, {})
    rol_de = ef["roles"].get(de, {})
    t = ahora()
    base = f"{t:%Y-%m-%d-%H%M}-{iid}{'-' + sid if sid else ''}-{para}"
    carpeta = pr.modulo_dir(m) / "handoffs"
    carpeta.mkdir(parents=True, exist_ok=True)
    tid, n = base, 2
    while (carpeta / f"{tid}.md").exists():
        tid, n = f"{base}-{n}", n + 1

    # cerrar el traspaso abierto del ítem: solo puede haber uno
    for otro in pr.traspasos.values():
        if otro["fm"].get("item") == iid and otro["fm"].get("estado") in ("Pendiente", "Tomado"):
            _set_campo(otro["path"], {"estado": "Cerrado", "cerrado": t.isoformat()})

    def entidad(rc, preferida=None):
        ents = entidades_de(rc)
        e = preferida or (ents[0] if ents else None)
        d = {"rol": None, "entidad": e if len(ents) <= 1 or preferida else ents}
        if rc.get("transporte"):
            d["transporte"] = rc["transporte"]
        return d

    d_de, d_para = entidad(rol_de, entidad_de), entidad(rol_para)
    d_de["rol"], d_para["rol"] = de, para
    d_de.pop("transporte", None)
    fm = {
        "formato": FORMATO, "id": tid, "item": iid, "slice": sid,
        "de": d_de, "para": d_para, "estado": "Pendiente",
        "creado": t.isoformat(), "tomado": None, "cerrado": None,
        "config_efectiva": {
            "autonomia": ef["autonomia"],
            "verificador": {**{k: v for k, v in ef["roles"].get("verificador", {}).items() if k != "activo"},
                            "activo": ef["verificador_activo"]["valor"]},
            "aprobador_tests": {"valor": entidades_de(ef["roles"].get("aprobador_tests")),
                                "fuente": ef["roles"].get("aprobador_tests", {}).get("fuente")},
            "driver": ef["roles"].get("driver"),
            "slice_max": ef["slice_max"],
            "comandos": ef["comandos"],
        },
        "leer": leer_para(pr, para, iid, m, sid),
        "no_tocar": no_tocar(pr, para, iid, m),
    }
    tests = ""
    if sid and iid in pr.planes:
        cs = next((s.get("criterios") or [] for s in pr.planes[iid]["fm"].get("slices") or [] if s.get("id") == sid), [])
        filas = []
        for archivo in pr.archivos_tests(iid):
            encontrados = criterios_en_test((pr.root / archivo).read_text(encoding="utf-8", errors="replace"), iid)
            for c in sorted(set(cs) & encontrados):
                filas.append(f"| {archivo} | {c} | (completar) |")
        tests = ("| Archivo | Criterio | Estado al entregar |\n|---|---|---|\n" + "\n".join(filas)) if filas else \
            f"Criterios del slice: {', '.join(cs) or '–'}."
    pasos = "\n".join(f"{i}. {p}" if not p.startswith("  ") else p
                      for i, p in enumerate(al_terminar(pr, para, iid, m, sid, ef), 1))
    aviso = ""
    if ef["autonomia"]["bajada"]:
        aviso = f"\n> Control bajado (↓): autonomía efectiva {ef['autonomia']['valor']}. Ver el motivo en module.md o en el ítem.\n"
    cuerpo = f"""{aviso}
## Qué se entrega
(completar)

## Qué se espera
(completar)

## Tests del slice
{tests or "(no aplica)"}

## Contexto
(completar: decisiones previas y lo relevante de la conversación. El receptor no puede asumir nada que no esté aquí o en `leer`.)

## Al terminar
{pasos}
"""
    path = carpeta / f"{tid}.md"
    path.write_text("---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n" + cuerpo,
                    encoding="utf-8")
    return path


def _set_campo(path: Path, valores: dict):
    texto = path.read_text(encoding="utf-8")
    m = FM_RE.match(texto)
    fm = m.group(1)
    for k, v in valores.items():
        fm = re.sub(rf"^{k}:[ \t]*[^\s#]*", f"{k}: {v}", fm, count=1, flags=re.M)
    path.write_text(texto.replace(m.group(1), fm, 1), encoding="utf-8")


# ---------------------------------------------------------------- sync

def foto(pr: Proyecto) -> dict:
    res = {}

    def sec_hash(body):
        return {k: sha256(v.encode())[:12] for k, v in secciones(body).items() if k != "Criterios de aceptación"}

    res["baton/config.md"] = {"tipo": "config", "objeto": "config", "fm": pr.config}
    for m, mod in pr.modulos.items():
        res[pr.rel(mod["path"])] = {"tipo": "modulo", "objeto": f"modulo:{m}", "fm": mod["fm"], "sec": sec_hash(mod["body"])}
    for iid, it in pr.items.items():
        res[pr.rel(it["path"])] = {"tipo": "item", "objeto": iid, "fm": it["fm"], "sec": sec_hash(it["body"]),
                                   "ac": {k: {"hash": v["hash"], "retirado": v["retirado"]} for k, v in it["ac"].items()}}
    for iid, pl in pr.planes.items():
        res[pr.rel(pl["path"])] = {"tipo": "plan", "objeto": f"{iid}/plan", "fm": pl["fm"], "sec": sec_hash(pl["body"])}
    for rid, s in pr.solicitudes.items():
        res[pr.rel(s["path"])] = {"tipo": "solicitud", "objeto": rid, "fm": {"estado": s["fm"].get("estado")}}
    for rid, r in pr.reportes.items():
        res[pr.rel(r["path"])] = {"tipo": "reporte", "objeto": rid,
                                  "fm": {"estado": r["fm"].get("estado"), "intento": r["fm"].get("intento")}}
    res["baton/acceptance.lock"] = {"tipo": "lock", "objeto": "lock", "lineas": pr.lock}
    return res


def diferencias(antes: dict, despues: dict) -> list[dict]:
    cambios = []

    def add(objeto, cambio, clave, requiere=True):
        cambios.append({"objeto": objeto, "cambio": cambio, "clave": clave, "requiere_motivo": requiere})

    for ruta in sorted(set(antes) | set(despues)):
        a, d = antes.get(ruta), despues.get(ruta)
        x = d or a
        obj, tipo = x["objeto"], x["tipo"]
        registro = tipo in ("solicitud", "reporte")
        if a is None:
            if tipo == "lock":
                for arch, fila in d["lineas"].items():
                    add("lock", f"congelado {arch} ({fila['item']}: {fila['criterios']})", f"lock:{arch}")
                continue
            add(obj, "creado" + (f" en estado {d['fm'].get('estado')}" if d.get("fm", {}).get("estado") else ""),
                f"{obj}:creado", not registro)
            continue
        if d is None:
            add(obj, "eliminado", f"{obj}:eliminado", True)
            continue
        if tipo == "lock":
            la, ld = a["lineas"], d["lineas"]
            for arch in sorted(set(la) | set(ld)):
                if arch not in la:
                    add("lock", f"congelado {arch} ({ld[arch]['item']}: {ld[arch]['criterios']})", f"lock:{arch}")
                elif arch not in ld:
                    add("lock", f"descongelado {arch}", f"lock:{arch}")
                elif la[arch] != ld[arch]:
                    add("lock", f"actualizado {arch} (solicitud {ld[arch]['solicitud']})", f"lock:{arch}")
            continue
        fa, fd = aplanar(a.get("fm", {})), aplanar(d.get("fm", {}))
        for k in sorted(set(fa) | set(fd)):
            if fa.get(k) != fd.get(k):
                add(obj, f"{k}: {corto(fa.get(k))} → {corto(fd.get(k))}", f"{obj}:{k}",
                    not (registro or k == "estado"))
        sa, sd = a.get("sec", {}), d.get("sec", {})
        for k in sorted(set(sa) | set(sd)):
            if sa.get(k) != sd.get(k):
                verbo = "agregada" if k not in sa else "eliminada" if k not in sd else "modificada"
                add(obj, f"sección «{k}» {verbo}", f"{obj}:§{k}")
        aa, ad = a.get("ac", {}), d.get("ac", {})
        for k in sorted(set(aa) | set(ad), key=lambda s: int(s.split("-")[1])):
            if k not in aa:
                add(f"{obj}/{k}", "nuevo", f"{obj}/{k}")
            elif k not in ad:
                add(f"{obj}/{k}", "eliminado (los criterios se retiran, no se borran)", f"{obj}/{k}")
            elif ad[k]["retirado"] and not aa[k]["retirado"]:
                add(f"{obj}/{k}", "retirado", f"{obj}/{k}")
            elif aa[k] != ad[k]:
                add(f"{obj}/{k}", "modificado", f"{obj}/{k}")
    return cambios


def motivo_para(c: dict, especificos: dict[str, str], general: str | None) -> str | None:
    for k in (c["clave"], c["objeto"]):
        if k in especificos:
            return especificos[k]
    if general:
        return general
    return None if c["requiere_motivo"] else "flujo"


def generar_backlog(pr: Proyecto) -> str:
    t = ahora()
    cfg = pr.config
    en_curso = sum(1 for it in pr.items.values() if it["fm"].get("estado") in WIP_ESTADOS)
    turnos: dict[str, int] = {}
    for iid in pr.items:
        tr = turno_de(pr, iid)
        if tr != "–":
            turnos[tr] = turnos.get(tr, 0) + 1
    lineas = [AVISO_GENERADO.format(extra=f" el {t.isoformat()}"),
              f"# Backlog · {cfg.get('proyecto', '')}", "",
              f"**En curso:** {en_curso} de {cfg.get('wip', '–')} · **Turnos:** "
              + (" · ".join(f"{k} {v}" for k, v in sorted(turnos.items())) or "ninguno"), ""]

    def orden(iid):
        return (pr.items[iid]["fm"].get("prioridad") or 999, iid)

    activos = [i for i in pr.items if pr.items[i]["fm"].get("estado") not in ("Candidato", "Hecho", "Descartado")]
    grupos: dict[str | None, list[str]] = {}
    for iid in activos:
        grupos.setdefault(pr.items[iid]["fm"].get("modulo"), []).append(iid)
    for m in sorted(grupos, key=lambda x: (x is None, x or "")):
        if m and m in pr.modulos:
            ef = efectiva(pr, modulo=m)
            aut = ef["autonomia"]["valor"] + (" ↓" if ef["autonomia"]["bajada"] else "")
            lineas.append(f"## {m} · {aut}")
        else:
            lineas.append("## Sin módulo")
        lineas += ["", "| ID | Título | Estado | Turno | Prioridad | Autonomía | Slices | Tests |",
                   "|---|---|---|---|---|---|---|---|"]
        for iid in sorted(grupos[m], key=orden):
            fm = pr.items[iid]["fm"]
            if m in pr.modulos:
                ef = efectiva(pr, item_id=iid)
                aut = ef["autonomia"]["valor"] + (" ↓" if ef["autonomia"]["bajada"] else "")
            else:
                aut = "–"
            h, tot = avance(pr, iid)
            c, v = tests_congelados(pr, iid)
            lineas.append(f"| {iid} | {celda(fm.get('titulo', ''))} | {fm.get('estado')} | {turno_de(pr, iid)} | "
                          f"{fm.get('prioridad', '–')} | {aut} | {f'{h}/{tot}' if tot else '–'} | "
                          f"{f'{c}/{v} congelados' if c else '–'} |")
        lineas.append("")
    cand = sorted((i for i in pr.items if pr.items[i]["fm"].get("estado") == "Candidato"), key=orden)
    lineas += ["## Candidatos", "", "| ID | Título | Propuesto por | Por qué |", "|---|---|---|---|"]
    for iid in cand:
        it = pr.items[iid]
        porque = secciones(it["body"]).get("Por qué se propone", "")
        lineas.append(f"| {iid} | {celda(it['fm'].get('titulo', ''))} | {it['fm'].get('propuesto_por', '–')} | {celda(corto(porque))} |")
    lineas += ["", "## Hecho", "", "| ID | Título | Módulo |", "|---|---|---|"]
    for iid in sorted((i for i in pr.items if pr.items[i]["fm"].get("estado") == "Hecho"), key=orden):
        fm = pr.items[iid]["fm"]
        lineas.append(f"| {iid} | {celda(fm.get('titulo', ''))} | {fm.get('modulo', '–')} |")
    return "\n".join(lineas) + "\n"


def sync(pr: Proyecto, autor: str, general: str | None, especificos: dict, ref: str | None, solo_revisar: bool) -> int:
    errores, avisos = validar(pr)
    for a in avisos:
        print(f"aviso: {a}")
    if errores:
        for e in errores:
            print(f"error: {e}")
        print("sync cancelado: corrige los errores primero.")
        return 1
    snap_path = pr.flow / ".sync" / "snapshot.json"
    antes = json.loads(snap_path.read_text(encoding="utf-8")) if snap_path.exists() else {}
    despues = normalizar(foto(pr))
    cambios = diferencias(antes, despues)
    faltan = [c for c in cambios if motivo_para(c, especificos, general) is None]
    if solo_revisar or faltan:
        if not cambios:
            print("sin cambios desde el último sync")
        for c in cambios:
            marca = "  FALTA MOTIVO" if c in faltan else ""
            print(f"- [{c['clave']}] {c['objeto']}: {c['cambio']}{marca}")
        if faltan:
            print(f"\n{len(faltan)} cambio(s) sin motivo. Usa --motivo \"...\" para todos "
                  "o --motivo-de CLAVE=\"...\" para uno.")
            return 3
        return 0
    if cambios:
        hist = pr.flow / "backlog" / "HISTORY.md"
        if not hist.exists():
            hist.parent.mkdir(parents=True, exist_ok=True)
            hist.write_text(AVISO_GENERADO.format(extra=": solo crece") + "\n# Historial\n\n"
                            "| Fecha | Autor | Objeto | Cambio | Motivo | Ref |\n|---|---|---|---|---|---|\n",
                            encoding="utf-8")
        fecha = ahora().strftime("%Y-%m-%dT%H:%M")
        with hist.open("a", encoding="utf-8") as f:
            for c in cambios:
                f.write(f"| {fecha} | {celda(autor)} | {celda(c['objeto'])} | {celda(c['cambio'])} | "
                        f"{celda(motivo_para(c, especificos, general))} | {celda(ref or '–')} |\n")
    (pr.flow / "backlog" / "BACKLOG.md").write_text(generar_backlog(pr), encoding="utf-8")
    snap_path.parent.mkdir(parents=True, exist_ok=True)
    snap_path.write_text(json.dumps(despues, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    print(f"sync: {len(cambios)} cambio(s) registrados en HISTORY.md; BACKLOG.md regenerado.")
    return 0


# ---------------------------------------------------------------- next

def next_(pr: Proyecto, rol: str | None, entidad: str | None) -> list[str]:
    salida = []
    en_curso = sum(1 for it in pr.items.values() if it["fm"].get("estado") in WIP_ESTADOS)
    wip = pr.config.get("wip")
    pendientes = {}
    for t in pr.traspasos.values():
        if t["fm"].get("estado") in ("Pendiente", "Tomado"):
            pendientes.setdefault(t["fm"].get("item"), []).append(t)
    roles = [rol] if rol else ROLES + ["humano"]
    for r in roles:
        filas = []
        for iid in sorted(pr.items, key=lambda i: (pr.items[i]["fm"].get("prioridad") or 999, i)):
            if turno_de(pr, iid) != r and not (r == "navigator" and turno_de(pr, iid) == "humano" and rol):
                continue
            fm = pr.items[iid]["fm"]
            est = fm.get("estado")
            m = fm.get("modulo")
            ef = efectiva(pr, item_id=iid) if m in pr.modulos else None
            if entidad and ef:
                rr = "navigator" if r == "humano" else r
                if entidad not in entidades_de(ef["roles"].get(rr)):
                    continue
            nota = ""
            if est == "TestsCongelados" and wip and en_curso >= wip:
                nota = f"  (bloqueado: WIP {en_curso}/{wip})"
            if est in ("EnCurso", "TestsCongelados"):
                sig = siguiente_slice(pr, iid)
                nota += f"  slice {sig}" if sig else ""
            if est == "EnRevision" and ef:
                nota += f"  revisión humana ({ef['autonomia']['valor']})"
            rol_t = "navigator" if r == "humano" else r
            tr = [x for x in pendientes.get(iid, []) if (x["fm"].get("para") or {}).get("rol") == rol_t]
            if tr:
                nota += "  traspaso: " + ", ".join(f"{pr.rel(x['path'])} [{x['fm'].get('estado')}]" for x in tr)
            filas.append(f"  {iid} · {est} · {fm.get('titulo', '')}{nota}")
        if filas or rol:
            salida.append(f"{r}:")
            salida += filas or ["  nada por ahora"]
    return salida


# ---------------------------------------------------------------- lock: aprobar y revisar

def lock_aprobar(pr: Proyecto, iid: str, aprobado_por: list[str], solicitud: str | None) -> list[str]:
    if iid not in pr.items:
        raise BatonError(f"no existe el ítem {iid}")
    ef = efectiva(pr, item_id=iid)
    aprob_validos = entidades_de(ef["roles"].get("aprobador_tests"))
    autor = set(entidades_de(ef["roles"].get("autor_tests")))
    driver = set(entidades_de(ef["roles"].get("driver")))
    for e in aprobado_por:
        if e not in aprob_validos:
            raise BatonError(f"{e} no es aprobador de tests de {iid} (aprobadores: {', '.join(aprob_validos)})")
        if e in autor or e in driver:
            raise BatonError(f"{e} es autor de tests o driver: no puede aprobar (invariantes 1 y 2)")
    if not any(pr.entidad(e).get("tipo") == "persona" for e in aprobado_por):
        raise BatonError("al menos un aprobador debe ser una persona (invariante 9)")
    est = pr.items[iid]["fm"].get("estado")
    if solicitud:
        s = pr.solicitudes.get(solicitud)
        if not s or s["fm"].get("estado") not in ("Aprobada", "Aplicada") or s["fm"].get("item") != iid:
            raise BatonError(f"la solicitud {solicitud} no existe, no es de {iid} o no está Aprobada")
    elif est != "TestsEnRevision":
        raise BatonError(f"{iid} está en {est}; sin solicitud aprobada solo se congela desde TestsEnRevision")
    archivos = pr.archivos_tests(iid)
    if not archivos:
        raise BatonError(f"no hay archivos de tests para {iid} en {pr.tests_dir} (deben empezar con {id_test(iid)}_)")
    vigentes = {k for k, v in pr.items[iid]["ac"].items() if not v["retirado"]}
    cubiertos, filas = set(), {}
    hoy, por = date.today().isoformat(), ",".join(aprobado_por)
    for a in archivos:
        contenido = (pr.root / a).read_bytes()
        cs = criterios_en_test(contenido.decode("utf-8", errors="replace"), iid)
        cubiertos |= cs
        filas[a] = {"archivo": a, "sha256": sha256(contenido), "item": iid,
                    "criterios": ",".join(sorted(cs, key=lambda c: int(c.split("-")[1]))) or "-",
                    "aprobado_por": por, "fecha": hoy, "solicitud": solicitud or "-"}
    faltan = vigentes - cubiertos
    if faltan:
        raise BatonError(f"criterios sin test: {', '.join(sorted(faltan))}")
    sobran = cubiertos - set(pr.items[iid]["ac"])
    if sobran:
        raise BatonError(f"tests que apuntan a criterios inexistentes: {', '.join(sorted(sobran))}")
    # archivos compartidos: protegidos y archivos del directorio de tests que no son de ningún ítem
    compartidos = [p for p in pr.protegidos if (pr.root / p).is_file()]
    base = pr.root / pr.tests_dir
    prefijos = tuple(id_test(i) + "_" for i in pr.items) + tuple(i + "_" for i in pr.items)
    if base.exists():
        compartidos += [pr.rel(p) for p in base.rglob("*") if p.is_file() and not p.name.startswith(prefijos)
                        and "__pycache__" not in p.parts and not p.name.endswith(".pyc")]
    for a in sorted(set(compartidos)):
        contenido = (pr.root / a).read_bytes()
        previa = pr.lock.get(a)
        if previa and previa["sha256"] == sha256(contenido):
            continue
        filas[a] = {"archivo": a, "sha256": sha256(contenido), "item": "*", "criterios": "-",
                    "aprobado_por": por, "fecha": hoy, "solicitud": solicitud or "-"}
    # quitar líneas de archivos del ítem que ya no existen
    nuevo = {k: v for k, v in pr.lock.items() if not (v["item"] == iid and k not in filas)}
    nuevo.update(filas)
    escribir_lock(pr.flow / "acceptance.lock", nuevo)
    return [f"congelado {a} ({f['criterios']})" for a, f in filas.items()]


def lock_revisar(pr: Proyecto, staged: bool, base_ref: str | None) -> list[str]:
    """Reglas de FORMATOS.md 6.3. Devuelve la lista de problemas."""
    root = pr.root
    problemas = []

    def contenido(ruta: str, ref: str | None) -> bytes | None:
        if ref is None:
            p = root / ruta
            return p.read_bytes() if p.is_file() else None
        r = subprocess.run(["git", "show", f"{ref}:{ruta}"], cwd=root, capture_output=True)
        return r.stdout if r.returncode == 0 else None

    ref_idx = "" if staged else None  # "" → `git show :ruta` lee el índice

    def actual(ruta):
        return contenido(ruta, ref_idx) if staged else contenido(ruta, None)

    lock_txt = actual("baton/acceptance.lock")
    lock = parsear_lock(lock_txt.decode()) if lock_txt else {}
    base_txt = contenido("baton/acceptance.lock", base_ref) if base_ref else None
    lock_base = parsear_lock(base_txt.decode()) if base_txt else {}

    def estado_item(iid, ref):
        it = pr.items.get(iid)
        if not it:
            return None
        txt = contenido(pr.rel(it["path"]), ref) if ref is not None else it["path"].read_bytes()
        if txt is None:
            return None
        m = re.search(r"^estado:\s*(\S+)", txt.decode(errors="replace"), re.M)
        return m.group(1) if m else None

    def estado_solicitud(rid, ref):
        s = pr.solicitudes.get(rid)
        if not s:
            return None
        txt = contenido(pr.rel(s["path"]), ref) if ref is not None else s["path"].read_bytes()
        m = re.search(r"^estado:\s*(\S+)", (txt or b"").decode(errors="replace"), re.M)
        return m.group(1) if m else None

    ref_actual = ref_idx if staged else None
    # regla 1: cada archivo del lock existe y su hash coincide
    for arch, fila in lock.items():
        data = actual(arch)
        if data is None:
            problemas.append(f"{arch} está congelado y no existe")
        elif sha256(data) != fila["sha256"]:
            problemas.append(f"{arch} está congelado y cambió (sha256 distinto). Abre una solicitud de cambio.")
    # regla 2: archivos en rutas protegidas que no están en el lock
    if staged:
        rutas = git(root, "diff", "--cached", "--name-only", "--diff-filter=ACMR").split()
    else:
        rutas = git(root, "ls-files").split()
    estados_autor = ("Listo", "TestsEnRevision")
    hay_autor = any(estado_item(i, ref_actual) in estados_autor for i in pr.items)
    for ruta in rutas:
        if not pr.es_protegido(ruta) or ruta in lock or ruta.endswith(".pyc") or "__pycache__" in ruta:
            continue
        nombre = ruta.rsplit("/", 1)[-1]
        dueno = next((i for i in pr.items if nombre.startswith(id_test(i) + "_") or nombre.startswith(i + "_")), None)
        if dueno:
            if estado_item(dueno, ref_actual) not in estados_autor:
                problemas.append(f"{ruta}: test nuevo de {dueno}, pero {dueno} no está en Listo ni TestsEnRevision")
        elif not hay_autor:
            problemas.append(f"{ruta}: archivo compartido nuevo en una ruta protegida y ningún ítem está en manos del autor de tests")
    # regla 3: líneas nuevas o cambiadas del lock
    if base_ref is not None:
        for arch, fila in lock.items():
            if lock_base.get(arch) == fila:
                continue
            sol = fila["solicitud"]
            if sol != "-":
                if estado_solicitud(sol, ref_actual) not in ("Aprobada", "Aplicada"):
                    problemas.append(f"lock: {arch} cambió con la solicitud {sol}, que no está Aprobada")
                continue
            if fila["item"] == "*":
                ok = any(estado_item(i, base_ref) == "TestsEnRevision" for i in pr.items) or not lock_base
            else:
                ok = estado_item(fila["item"], base_ref) == "TestsEnRevision"
            if not ok:
                problemas.append(f"lock: {arch} cambió sin solicitud aprobada y su ítem no venía de TestsEnRevision")
        for arch in sorted(set(lock_base) - set(lock)):
            iid = lock_base[arch]["item"]
            desde_autor = iid != "*" and estado_item(iid, base_ref) == "TestsEnRevision"
            con_solicitud = any(s["fm"].get("item") == iid and estado_solicitud(rid, ref_actual) in ("Aprobada", "Aplicada")
                                for rid, s in pr.solicitudes.items())
            if not (desde_autor or con_solicitud):
                problemas.append(f"lock: se quitó {arch}; descongelar requiere una solicitud aprobada")
    return problemas


# ---------------------------------------------------------------- init

def init(destino: Path, hook: bool, codeowners: str | None, forzar: bool) -> list[str]:
    origen = Path(__file__).resolve().parent
    hechos = []
    flow = destino / "baton"
    for d in ["system/adr", "backlog/items", "modules", "bin", "templates", "hooks", ".sync"]:
        (flow / d).mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__).resolve(), flow / "bin" / "baton.py")
    hechos.append("baton/bin/baton.py")
    tpl = origen / "templates"
    if tpl.exists():
        for p in tpl.glob("*.md"):
            dst = flow / "templates" / p.name
            if not dst.exists() or forzar:
                shutil.copy2(p, dst)
                hechos.append(f"baton/templates/{p.name}")
    hook_src = origen / "pre-commit"
    shutil.copy2(hook_src, flow / "hooks" / "pre-commit")
    (flow / "hooks" / "pre-commit").chmod(0o755)
    hechos.append("baton/hooks/pre-commit")
    for nombre, contenido in [("acceptance.lock", LOCK_CABECERA),
                              ("system/overview.md", "# Mapa del sistema\n\n## Arquitectura\n\n## Contratos\n\n## Decisiones\nVer adr/.\n")]:
        p = flow / nombre
        if not p.exists():
            p.write_text(contenido, encoding="utf-8")
            hechos.append(f"baton/{nombre}")
    if hook:
        hooks_dir = Path(git(destino, "rev-parse", "--git-path", "hooks").strip())
        hooks_dir = hooks_dir if hooks_dir.is_absolute() else destino / hooks_dir
        hooks_dir.mkdir(parents=True, exist_ok=True)
        dst = hooks_dir / "pre-commit"
        if dst.exists() and "baton.py" not in dst.read_text(errors="replace") and not forzar:
            raise BatonError(f"ya existe {dst} y no es de Baton: intégralo a mano o usa --forzar")
        dst.write_text("#!/bin/sh\n# Baton: solo actúa en ramas que tienen baton/ (el hook es común a todas las ramas)\n"
                       "[ -f baton/hooks/pre-commit ] || exit 0\nexec sh baton/hooks/pre-commit \"$@\"\n", encoding="utf-8")
        dst.chmod(0o755)
        hechos.append(f"hook instalado en {dst}")
    if codeowners:
        p = destino / ".github" / "CODEOWNERS"
        p.parent.mkdir(parents=True, exist_ok=True)
        bloque = (f"\n# baton: tests congelados y configuración; exigen revisión de un aprobador humano\n"
                  f"/baton/acceptance.lock {codeowners}\n/baton/config.md {codeowners}\n")
        actual = p.read_text(encoding="utf-8") if p.exists() else ""
        if "/baton/acceptance.lock" not in actual:
            p.write_text(actual + bloque, encoding="utf-8")
            hechos.append(".github/CODEOWNERS (agrega también las rutas protegidas cuando existan)")
    return hechos


def codeowners_rutas(pr: Proyecto, owners: str) -> list[str]:
    return [f"/{pr.tests_dir}/ {owners}", *[f"/{p} {owners}" for p in pr.protegidos],
            f"/baton/acceptance.lock {owners}", f"/baton/config.md {owners}"]


# ---------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="baton.py", description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=None, help="raíz del proyecto (por defecto, la raíz de git o el directorio actual)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="crea la estructura baton/ e instala la herramienta")
    p.add_argument("--hook", action="store_true", help="instala el hook pre-commit de git")
    p.add_argument("--codeowners", help="dueños para .github/CODEOWNERS, p. ej. '@juan'")
    p.add_argument("--forzar", action="store_true")

    sub.add_parser("validar", help="revisa todos los archivos del flujo")

    p = sub.add_parser("efectiva", help="configuración efectiva de un ítem o módulo")
    p.add_argument("objetivo", nargs="?", help="US-004 o modulo:pagos (vacío = proyecto)")

    p = sub.add_parser("next", help="qué le toca a cada rol")
    p.add_argument("--rol", choices=ROLES + ["humano"])
    p.add_argument("--entidad")

    p = sub.add_parser("estado", help="cambia el estado de un ítem, reporte (US-004-S1) o solicitud")
    p.add_argument("objetivo")
    p.add_argument("nuevo")
    p.add_argument("--forzar", action="store_true", help="salta la validación de transición (solo si el humano lo decide)")

    p = sub.add_parser("handoff", help="crea un traspaso")
    p.add_argument("--item", required=True)
    p.add_argument("--slice")
    p.add_argument("--de", required=True, choices=ROLES)
    p.add_argument("--para", required=True, choices=ROLES)
    p.add_argument("--entidad-de", help="entidad que entrega, si el rol tiene varias")

    p = sub.add_parser("tomar", help="marca un traspaso como Tomado")
    p.add_argument("id")

    p = sub.add_parser("sync", help="registra cambios en HISTORY.md y regenera BACKLOG.md")
    p.add_argument("--autor", help="entidad que ejecuta el sync (obligatorio salvo con --revisar)")
    p.add_argument("--motivo", help="motivo para todos los cambios que no tengan uno propio")
    p.add_argument("--motivo-de", action="append", default=[], metavar="CLAVE=MOTIVO")
    p.add_argument("--ref", help="commit, solicitud, traspaso o skill relacionada")
    p.add_argument("--revisar", action="store_true", help="solo muestra los cambios pendientes")

    p = sub.add_parser("lock", help="acceptance.lock")
    lsub = p.add_subparsers(dest="lockcmd", required=True)
    q = lsub.add_parser("aprobar", help="congela los tests de un ítem")
    q.add_argument("--item", required=True)
    q.add_argument("--aprobado-por", required=True, help="entidades separadas por coma")
    q.add_argument("--solicitud")
    q = lsub.add_parser("revisar", help="comprueba el lock (lo usan el hook y CI)")
    q.add_argument("--staged", action="store_true", help="revisa el índice de git (pre-commit)")
    q.add_argument("--base", help="ref de git contra la que comparar el lock (CI: la rama destino)")

    p = sub.add_parser("codeowners", help="imprime las reglas de CODEOWNERS recomendadas")
    p.add_argument("owners")

    a = ap.parse_args(argv)
    if a.root:
        root = Path(a.root)
    else:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        root = Path(top.stdout.strip()) if top.returncode == 0 else Path.cwd()

    try:
        if a.cmd == "init":
            for h in init(root, a.hook, a.codeowners, a.forzar):
                print(f"creado: {h}")
            return 0
        pr = Proyecto(root)
        if a.cmd == "validar":
            errores, avisos = validar(pr)
            for x in avisos:
                print(f"aviso: {x}")
            for x in errores:
                print(f"error: {x}")
            print("ok" if not errores else f"{len(errores)} error(es)")
            return 1 if errores else 0
        if a.cmd == "efectiva":
            obj = a.objetivo
            if obj and obj.startswith("modulo:"):
                ef = efectiva(pr, modulo=obj.split(":", 1)[1])
            elif obj:
                if obj not in pr.items:
                    raise BatonError(f"no existe el ítem {obj}")
                ef = efectiva(pr, item_id=obj)
            else:
                ef = efectiva(pr)
            print(yaml.safe_dump(ef, allow_unicode=True, sort_keys=False), end="")
            return 1 if ef["errores"] else 0
        if a.cmd == "next":
            print("\n".join(next_(pr, a.rol, a.entidad)))
            return 0
        if a.cmd == "estado":
            print(cambiar_estado(pr, a.objetivo, a.nuevo, a.forzar))
            return 0
        if a.cmd == "handoff":
            print(pr.rel(crear_traspaso(pr, a.item, a.de, a.para, a.slice, a.entidad_de)))
            return 0
        if a.cmd == "tomar":
            t = pr.traspasos.get(a.id)
            if not t:
                raise BatonError(f"no existe el traspaso {a.id}")
            if t["fm"].get("estado") != "Pendiente":
                raise BatonError(f"el traspaso está {t['fm'].get('estado')}")
            _set_campo(t["path"], {"estado": "Tomado", "tomado": ahora().isoformat()})
            print(f"{a.id}: Tomado")
            return 0
        if a.cmd == "sync":
            if not a.revisar and not a.autor:
                raise BatonError("sync necesita --autor")
            esp = {}
            for kv in a.motivo_de:
                if "=" not in kv:
                    raise BatonError(f"--motivo-de espera CLAVE=MOTIVO: {kv}")
                k, v = kv.split("=", 1)
                esp[k] = v
            return sync(pr, a.autor or "", a.motivo, esp, a.ref, a.revisar)
        if a.cmd == "lock":
            if a.lockcmd == "aprobar":
                for x in lock_aprobar(pr, a.item, [e.strip() for e in a.aprobado_por.split(",")], a.solicitud):
                    print(x)
                return 0
            base = a.base or ("HEAD" if a.staged and git(root, "rev-parse", "--verify", "HEAD", check=False) else None)
            problemas = lock_revisar(pr, a.staged, base)
            for x in problemas:
                print(f"rechazado: {x}")
            if problemas:
                print("\nLos tests de aceptación congelados solo cambian con una solicitud aprobada (FORMATOS.md §6–7).")
                return 1
            print("lock ok")
            return 0
        if a.cmd == "codeowners":
            print("\n".join(codeowners_rutas(pr, a.owners)))
            return 0
    except BatonError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
