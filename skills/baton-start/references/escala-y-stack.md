# Escala y stack

La recomendación se hace **después** de confirmar la visión: el stack correcto depende de la escala, las restricciones y lo que el equipo conoce.

## Qué implica cada escala

| Escala | Prioriza | Arquitectura típica | Evita |
|---|---|---|---|
| Prototipo | velocidad de aprendizaje | lo más simple: script, monolito, almacenamiento local | infraestructura, abstracciones |
| MVP | salir rápido sin deuda grave | monolito con capas claras y una base de datos administrada | microservicios, multi-región |
| Producto pequeño | mantenibilidad | monolito bien testeado | complejidad que no se usa |
| Empezar pequeño, migrar fácil | límites claros entre módulos | **monolito modular**: módulos con interfaces propias que mañana se pueden separar en servicios | acoplar módulos por la base de datos compartida |
| Gran escala desde el inicio | disponibilidad y escalado | servicios separados según la carga, colas, caché, observabilidad desde el día 1 | decisiones irreversibles sin medir |

## Criterios para recomendar

1. **Tecnología conocida y probada antes que novedosa.** Lo que el equipo ya domina gana, salvo que una restricción lo impida.
2. **Lo más simple que cumpla la escala de hoy**, con un camino claro hacia la de mañana. El patrón de la industria es *monolith first*: casi ningún sistema necesita microservicios al inicio.
3. **Las restricciones mandan.** Datos sensibles implican cifrado y control de acceso desde el diseño. Una plataforma obligatoria fija parte del stack.
4. **Cada pieza se justifica.** Si una pieza no responde a un requisito de la visión, sobra.

## Cómo presentarlo

- **2 o 3 opciones** en una tabla (opción, a favor, en contra), y tu **recomendación** con el motivo en una línea. Pide la elección con una pregunta interactiva: la recomendada primero, y cada opción con su resumen.
- Incluye lenguaje y framework, almacenamiento, framework de tests y cómo se ejecuta o despliega.
- El humano decide. Escríbelo en `baton/system/adr/ADR-0001-stack.md`:
  - `## Contexto`: cita la escala y las restricciones de la visión;
  - `## Opciones consideradas`: la tabla;
  - `## Decisión` y `## Consecuencias`;
  - `## Revisar si`: **condiciones concretas** para reconsiderar. Ejemplos: "más de 10 000 usuarios activos", "un segundo equipo trabajando en el mismo módulo", "latencia por encima de 300 ms".

  Así "empezar pequeño" no es una promesa vacía: queda escrito cuándo hay que crecer.
- Completa `## Arquitectura` de la visión con las piezas que resultan.

## Proyecto existente

El stack ya está decidido. Documenta en ADR-0001 lo que hay (`## Contexto`: "stack heredado") solo si sirve para las decisiones que vienen. Si la escala nueva no calza con el stack actual, señálalo como riesgo y propón un ADR aparte. No cambies el stack sin que el humano lo pida.
