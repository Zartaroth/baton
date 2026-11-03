---
name: baton-refine
description: Refina justo a tiempo un ítem del backlog de la metodología Baton. Escribe el valor y los criterios de aceptación Dado/Cuando/Entonces, revisa la seguridad, detecta ambigüedades y deja el ítem cumpliendo la Definition of Ready salvo el plan. También sirve para aceptar o descartar ítems candidatos. Úsala cuando un ítem Pendiente está por desarrollarse.
---

# baton-refine

**Rol:** Navigator. El agente propone y **el humano decide**. **Entrada:** un ítem `Pendiente` (o `Candidato`), el mapa del sistema y los ADR. **Salida:** el ítem refinado. Después sigue `baton-plan`.

## Candidatos

Si el ítem está en `Candidato`, muéstralo con su `## Por qué se propone` y pregunta:

- si el humano lo acepta: `python3 baton/bin/baton.py estado <ítem> Pendiente`;
- si lo descarta: `python3 baton/bin/baton.py estado <ítem> Descartado`.

Nunca lo muevas sin respuesta.

## Pasos

1. Lee el ítem, `baton/system/overview.md`, los ADR relevantes y el `module.md` de su módulo.
2. **Valor.** Escribe `## Valor` como "Como <rol> quiero <acción> para <beneficio>".
3. **Criterios.** Escribe uno por comportamiento observable, con estas reglas:
   - formato `### AC-<n> · <nombre>` y viñetas **Dado** / **Cuando** / **Entonces** (y **Y**);
   - datos concretos: "un carrito con 2 productos por $30", no "un carrito con productos";
   - el **Entonces** describe algo que se puede comprobar desde afuera (respuesta, pantalla, registro), no detalles internos;
   - incluye el caso feliz, los errores esperables y los bordes (vacío, límite, duplicado, sin permiso);
   - si salen más de unos 6 criterios, propone dividir el ítem.
4. **Seguridad.** Revisa y escribe el resultado en `## Seguridad`:
   - autenticación y autorización;
   - validación de entradas;
   - datos sensibles (almacenamiento, logs, tránsito);
   - inyección;
   - abuso (límites de uso, enumeración);
   - auditoría.

   Si no hay impacto, escribe "sin impacto". Lo que encuentres como requisito se convierte en criterio.
5. **Ambigüedades.** Todo lo que no puedas decidir con lo que hay va a `## Preguntas abiertas`. Pregúntaselo al humano y, al resolverlo, borra la pregunta y ajusta los criterios.
6. **Propuestas.** Si detectas mejoras o huecos fuera del alcance del ítem, **no** los agregues como criterios. Créalos como ítems nuevos con `estado: Candidato`, `origen: agente`, `propuesto_por: <tu entidad>` y `## Por qué se propone`.
7. **Criterios ya congelados.** Si el ítem estuvo en `TestsCongelados` o después, no edites un criterio sin una solicitud aprobada. Un criterio que sobra se retira: se tacha su título con `~~` y se anotan la fecha y la solicitud. Nunca se borra ni se renumera.
8. Revisa la Definition of Ready (FORMATOS.md 4.3): valor, criterios con Dado/Cuando/Entonces, sin preguntas abiertas, seguridad escrita y dependencias resueltas o explicadas. Lo único que falta es el plan.
9. Ejecuta `python3 baton/bin/baton.py sync --autor <entidad> --motivo "refinado de <ítem>"`. Si hubo cambios de alcance con un motivo propio, usa `--motivo-de`.
10. Continúa con `baton-plan`.

## No hagas

- No escribas tests ni código.
- No marques el ítem como `Listo`: lo hace `baton-plan` cuando existe el plan.
- No resuelvas tú una pregunta abierta de negocio. Preséntale opciones al humano, con tu recomendación.
