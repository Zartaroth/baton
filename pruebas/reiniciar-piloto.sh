#!/usr/bin/env bash
# Reinicia el piloto de Baton: lo deja como un proyecto recién creado y vuelve a enlazar las skills.
# El piloto es un repositorio git independiente (rama piloto), no un worktree de la metodología.
# Uso: bash pruebas/reiniciar-piloto.sh [carpeta-del-piloto] [--copiar]
#   --copiar  copia las skills en vez de enlazarlas (si tu agente no sigue enlaces simbólicos)
set -euo pipefail

METODOLOGIA=$(cd "$(dirname "$0")/.." && pwd)
PILOTO=$HOME/Proyectos/baton-piloto
COPIAR=0
for a in "$@"; do
  case $a in
    --copiar) COPIAR=1 ;;
    *) PILOTO=$a ;;
  esac
done

cd "$PILOTO"
rama=$(git rev-parse --abbrev-ref HEAD)
[ "$(git rev-parse --git-common-dir)" = ".git" ] || echo "aviso: $PILOTO parece un worktree. Claude Code le cargaría la memoria del repositorio principal; usa un repositorio independiente (ver la guía)." >&2
[ "$rama" = piloto ] || { echo "error: $PILOTO está en la rama '$rama', no en 'piloto'. No toco nada." >&2; exit 1; }

# respaldar lo generado por el intento anterior
if [ -d baton ]; then
  respaldo=$(mktemp -d "${TMPDIR:-/tmp}/baton-piloto-respaldo.XXXX")
  cp -r baton "$respaldo/"
  echo "respaldo del baton/ anterior: $respaldo/baton"
fi

# volver al primer commit ("Inicio del proyecto") y borrar todo lo generado, salvo .venv y .claude
primero=$(git rev-list --max-parents=0 HEAD | tail -1)
git reset -q --hard "$primero"
git clean -qfdx -e .venv -e .claude   # .claude guarda los permisos que ya aprobaste
echo "piloto en el commit inicial: $(git log --oneline -1)"

# skills: el router baton y las baton-*
mkdir -p .claude/skills
rm -rf .claude/skills/baton .claude/skills/baton-*
for s in "$METODOLOGIA"/skills/baton "$METODOLOGIA"/skills/baton-*; do
  if [ $COPIAR -eq 1 ]; then cp -r "$s" .claude/skills/; else ln -s "$s" .claude/skills/; fi
done
excl="$(git rev-parse --git-common-dir)/info/exclude"
grep -qx ".claude/skills/" "$excl" 2>/dev/null || echo ".claude/skills/" >> "$excl"
echo "skills ($([ $COPIAR -eq 1 ] && echo copiadas || echo enlazadas)): $(ls .claude/skills | tr '\n' ' ')"
[ -x .venv/bin/pytest ] && echo "pytest: $(.venv/bin/pytest --version 2>&1)" || echo "aviso: falta .venv con pytest (python3 -m venv .venv && .venv/bin/pip install pytest pyyaml)"
echo "listo: abre 'claude' en $PILOTO y escribe /baton"
