# Baton

[![pruebas](https://github.com/Zartaroth/baton/actions/workflows/pruebas.yml/badge.svg)](https://github.com/Zartaroth/baton/actions/workflows/pruebas.yml)
[![Licencia: MIT](https://img.shields.io/badge/licencia-MIT-blue.svg)](LICENSE)
[![Estado: experimental](https://img.shields.io/badge/estado-experimental-orange.svg)](#estado)

Metodología de desarrollo con agentes de IA. Combina un backlog vivo, slices verticales, TDD con tests de aceptación congelados y roles separados que se pasan el turno con archivos dentro del repositorio.

> *An AI-assisted development methodology: a living backlog, vertical slices, TDD against frozen acceptance tests, and separate roles that hand off turns through files in the repo. Documentation is in Spanish.*

El nombre viene del testigo (*baton*) de una carrera de relevos: quien lo tiene, tiene el turno, y el traspaso entre roles es pasarlo.

## Por qué

Baton evoluciona SDD (Spec-Driven Development) y resuelve cuatro de sus problemas:

| En SDD | En Baton |
|---|---|
| La spec completa va al inicio, repartida en muchos documentos que hay que mantener juntos | Un **backlog vivo** de ítems pequeños, detallados justo a tiempo. Cambiar algo es editar un ítem |
| Fases por capas (BD, backend, frontend) que no se pueden probar hasta el final | **Slices verticales** que se pueden demostrar, empezando por un esqueleto andante |
| Todo se verifica al final, y la IA puede ajustar los tests para que el código pase | Los tests de aceptación se escriben **antes**, una persona los aprueba y quedan **congelados** (hook y CODEOWNERS) |
| Se delega todo y se revisa el paquete completo al final | **Roles separados**: decidir, especificar con tests, implementar y verificar, con niveles de autonomía configurables |

## Cómo funciona

```
entender el proyecto → escala y stack → configurar → mapa de módulos      (una vez)
abrir un módulo: entenderlo → configurarlo → definir sus ítems           (por módulo)
detallar un ítem → tests en rojo verificado → aprobación humana y congelamiento
                 → Driver con TDD, slice por slice → verificación → revisión según autonomía
```

- **Roles:**
  - **Navigator:** humano + modelo razonador. Diseña y decide.
  - **Autor de tests.**
  - **Aprobador de tests:** siempre hay una persona.
  - **Driver:** implementa y nunca toca los tests de aceptación.
  - **Verificador:** un modelo distinto del Driver.
- **Autonomía:**
  - **Pair:** el humano revisa cada slice.
  - **Checkpoint:** revisa cada ítem.
  - **Delegado:** revisa el módulo al cerrar.

  Se configura por capas (proyecto → módulo → ítem), y el control se puede subir o bajar con motivo.
- **El repositorio es el canal:** cada turno deja un archivo de traspaso. Por eso cada rol puede vivir en otra sesión, en un subagente o en otra herramienta (Claude Code, Codex, etc.).

## Empezar

1. **Requisitos:** git, Python 3.10+ y PyYAML (`pip install pyyaml`).
2. Copia las carpetas `skills/baton-*` a la carpeta de skills de tu agente (en Claude Code, `.claude/skills/`).
3. En tu repositorio di **"continúa"**: el router `baton` lanza `baton-start`. Este detecta si el proyecto es nuevo o existente, entiende qué se va a construir, recomienda el stack según la escala, configura y arma el mapa de módulos.
4. Desde ahí, **"continúa"** sigue diciendo qué rol tiene el turno y qué paso toca.

## Contenido

| Archivo | Qué es |
|---|---|
| [METODOLOGIA.md](METODOLOGIA.md) | la metodología: principios, roles, invariantes, configuración, ciclo de vida |
| [FORMATOS.md](FORMATOS.md) | formato exacto de cada archivo |
| [skills/](skills/README.md) | skills del núcleo y `baton.py`, la herramienta determinista |
| [pruebas/](pruebas/) | prueba de punta a punta de `baton.py` y la guía del proyecto piloto |

## Estado

Versión 0.4, experimental. El núcleo está escrito y probado con la prueba automática. Falta probarlo con un proyecto real ([guía del piloto](pruebas/GUIA-PILOTO.md)) y escribir `baton-verify`, `baton-review` y los adaptadores para Jira, Trello y GitHub Issues.

## Contribuir

Lo más valioso es que lo pruebes y cuentes cómo te fue: abre un issue de tipo **Experiencia de uso**. Para proponer cambios, lee [CONTRIBUTING.md](CONTRIBUTING.md). Las ideas en borrador van en [Discusiones](https://github.com/Zartaroth/baton/discussions).

## Licencia

[MIT](LICENSE)
