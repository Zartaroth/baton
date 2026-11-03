# Seguridad

## Alcance

Baton se ejecuta en local: `baton.py` y el hook de git leen y escriben archivos dentro de tu repositorio, y no hacen conexiones de red. Lo que más interesa reportar:

- formas de **saltarse la protección de los tests congelados** (`acceptance.lock`, el hook o las reglas de `baton.py lock revisar`) que no estén ya descritas como límite conocido en [FORMATOS.md §6.3](FORMATOS.md#63-qué-comprueban-el-hook-y-ci);
- entradas (frontmatter, nombres de archivo, el contenido del lock) que hagan que `baton.py` lea o escriba **fuera del repositorio** o ejecute comandos;
- instrucciones de una skill que puedan llevar a un agente a saltarse una invariante.

## Cómo reportar

**No abras un issue público.** Usa el [reporte privado de vulnerabilidades](../../security/advisories/new) de GitHub. Intentaremos responder en un plazo de 7 días.

Saltar el hook con `git commit --no-verify` es un límite conocido y documentado: la garantía fuerte es la regla de CODEOWNERS en el servidor.
