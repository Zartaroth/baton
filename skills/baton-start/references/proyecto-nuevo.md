# Entender un proyecto nuevo

**Objetivo:** que el humano y el agente compartan la misma imagen de qué se va a construir, antes de decidir nada técnico. Se inspira en el *inception* de producto (Lean Inception: "es / no es / hace / no hace").

## Cómo preguntar

- Haz **2 rondas como máximo**, con varias preguntas por ronda, no una por una.
- Si el humano responde con poco detalle, **propón tú** una versión concreta y pide que la corrija. Corregir es más rápido que redactar.
- Lo que siga sin respuesta va a `## Lo que no sabemos`. No bloquea empezar.

**Ronda 1. El producto**
1. ¿Qué es, en una frase? ¿Qué problema resuelve?
2. ¿Para quién? ¿Hay distintos tipos de usuario?
3. ¿Cómo se sabrá que funcionó (objetivo o señal de éxito)?
4. **Es / no es · hace / no hace:** dos o tres líneas de cada uno. Ayuda a fijar el alcance.

**Ronda 2. Alcance, escala y restricciones**
1. ¿Qué tiene que hacer la **primera versión** que sirva? Lo mínimo que alguien usaría.
2. ¿Qué queda fuera a propósito?
3. **Escala y horizonte:**
   - prototipo para validar una idea;
   - MVP;
   - producto pequeño y estable;
   - empezar pequeño pero poder crecer fácil;
   - gran escala desde el inicio.

   Pregunta también por los usuarios esperados y el volumen de datos.
4. **Restricciones:**
   - ¿maneja datos personales o dinero?
   - ¿hay normas que cumplir?
   - ¿plataformas obligatorias (web, móvil, CLI)?
   - ¿plazos o presupuesto?
   - ¿qué lenguajes o tecnologías conoce el equipo?

## Qué escribir

Completa `baton/system/overview.md` con `inicio: nuevo`:

- secciones del producto: Propósito, Usuarios, Objetivos, Alcance inicial, Fuera de alcance, Escala y horizonte, Restricciones, Glosario y Lo que no sabemos;
- **Punto de partida:** escribe "proyecto nuevo";
- **Arquitectura:** déjala para después del paso de stack.

## Resumen para confirmar

Muestra **como máximo 10 líneas**:

```
Entendí que vas a construir <qué> para <quién>, para <objetivo>.
La primera versión hace <alcance> y no hace <fuera de alcance>.
Escala: <escala>. Restricciones clave: <...>.
No sé todavía: <lista corta>.
¿Está bien, o corrijo, agrego o quito algo?
```
