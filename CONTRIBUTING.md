# Cómo contribuir a Baton

¡Gracias por tu interés! Baton es una metodología en construcción. Lo que más la mejora es que alguien la use de verdad y cuente qué funcionó y qué no.

> *Contributions are welcome in Spanish or English. The docs are in Spanish for now; English translations are a welcome contribution too.*

## Formas de contribuir

En orden de impacto:

1. **Contar tu experiencia de uso.** Prueba Baton en un proyecto, aunque sea pequeño (puedes seguir [la guía del piloto](pruebas/GUIA-PILOTO.md)), y abre un issue de tipo **Experiencia de uso**. Dónde hubo fricción, qué rol necesitó contexto que no estaba en el traspaso, cuántos tokens gastó cada nivel de autonomía: esa información vale más que cualquier PR.
2. **Proponer cambios a la metodología.** Abre primero una **Discusión** en la categoría *Ideas* o un issue de tipo **Propuesta**. Un cambio a los principios, roles, invariantes o formatos afecta todo lo demás, así que conviene acordarlo antes de escribirlo.
3. **Reportar errores** en `baton.py` o en las skills, con un issue de tipo **Error**.
4. **Código y documentación:** correcciones, skills nuevas (`baton-verify`, `baton-review`, adaptadores), traducciones.

Si buscas por dónde empezar, mira los issues con la etiqueta [`good first issue`](../../labels/good%20first%20issue).

## Reglas del proyecto

Las mismas que Baton pide a quien lo usa:

- **Las invariantes de [METODOLOGIA.md](METODOLOGIA.md#invariantes-ninguna-configuración-puede-romperlas) no se negocian en un PR.** Si crees que una debe cambiar, ábrelo como propuesta y explica el motivo.
- **Cada dato vive en un solo lugar.** Si un cambio duplica información entre archivos, probablemente hay una forma mejor.
- **Todo cambio tiene motivo.** Explica el *por qué* en el PR, no solo el *qué*.
- **Si cambias un formato** ([FORMATOS.md](FORMATOS.md)), actualiza en el mismo PR `baton.py`, las plantillas y las skills que lo usan. Si el cambio no es compatible con los archivos existentes, sube el número de `formato`.
- **Lo determinista va en `baton.py`, el criterio va en las skills.** Si una skill le pide a un agente algo que siempre debería dar el mismo resultado, eso le corresponde a `baton.py`.
- **Las skills son neutrales respecto de la herramienta.** Lo propio de Claude Code, Codex u otra herramienta va en adaptadores, no en el núcleo.

## Preparar el entorno

```bash
git clone https://github.com/Zartaroth/baton.git
cd baton
pip install pyyaml          # o el paquete de tu sistema (python-yaml)
bash pruebas/e2e.sh         # prueba de punta a punta; debe terminar en "todo ok"
```

## Enviar un PR

1. Haz un fork y crea una rama desde `main` (`fix/...`, `feat/...` o `docs/...`).
2. Haz cambios pequeños y enfocados: un tema por PR.
3. Si tocas `baton.py`, `bash pruebas/e2e.sh` tiene que pasar. Si arreglas un error, agrega a la prueba el caso que lo reproduce.
4. Escribe en español o inglés, siguiendo el estilo de los documentos: frases cortas, tablas para comparar y nada de jerga sin explicar. Las claves y los valores de los formatos van en español sin tildes (`estado`, `TestsEnRevision`).
5. Completa la plantilla del PR. CI ejecuta las pruebas automáticamente.

## Código de conducta

Al participar aceptas el [código de conducta](CODE_OF_CONDUCT.md).
