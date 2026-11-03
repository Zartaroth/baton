# Entender un proyecto existente

**Objetivo:** saber desde dónde se parte y hacia dónde se quiere ir, sin leer todo el código.

## Análisis acotado

Lee solo esto, en este orden, y detente cuando tengas una imagen clara:

1. El resultado de `baton.py detectar`. Ya te da lenguajes, manifiestos, tests y comandos.
2. El `README` y los manifiestos (`package.json`, `pyproject.toml`, etc.): propósito, dependencias y scripts.
3. La estructura: `git ls-files | head -200` o el árbol de 2 niveles. No abras cada archivo.
4. Los puntos de entrada: el `main`, las rutas o endpoints, los comandos de la CLI, las páginas.
5. El modelo de datos: el esquema, las migraciones o los modelos principales.
6. Los tests: la configuración del runner y **un** test representativo.
7. La CI y el despliegue, si existen.
8. `git log --oneline -20`: en qué se estuvo trabajando hace poco.

**Presupuesto:** unos 15 archivos. Si el proyecto es grande, quédate con el módulo o la zona que el humano quiere tocar primero, y pregúntale cuál es.

## Preguntas al humano (una ronda)

1. ¿Qué se quiere lograr ahora con el proyecto: una funcionalidad nueva, una refactorización, estabilizarlo, migrarlo?
2. ¿Qué no se debe tocar?
3. ¿La escala y las restricciones cambian respecto de hoy? Las opciones de escala están en `proyecto-nuevo.md`, ronda 2.
4. Si `detectar` encontró issues o TODO: **¿quieres importarlos como candidatos?** Por defecto, no.

## Qué escribir

Completa `baton/system/overview.md` con `inicio: existente`:

- **Punto de partida:** stack, estructura, qué funciona, tests existentes (cuántos y de qué tipo) y deuda visible. Para cada afirmación, indica tu grado de confianza: *visto en el código*, *inferido* o *supuesto*.
- **Alcance inicial:** lo que se va a construir o cambiar ahora, no lo que ya existe.
- **Arquitectura:** la que hay hoy, con sus piezas principales.
- **Lo que no sabemos:** todo lo que no pudiste confirmar.

## Resumen para confirmar

Muestra **como máximo 12 líneas**:

```
Parto de: <qué es hoy>, hecho con <stack>, con <n> tests de <tipo>.
Funciona: <...>. Riesgos o deuda visibles: <...>.
Ahora quieres: <objetivo>. No se toca: <...>.
No pude confirmar: <lista corta>.
¿Lo entendí bien, o corrijo, agrego o quito algo?
```

Los tests existentes **no se congelan**. El lock de Baton solo cubre los tests de aceptación nuevos, porque esos salen de criterios aprobados.
