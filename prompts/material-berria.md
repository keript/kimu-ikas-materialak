# Prompt para crear un material nuevo (Gemini, Claude o Copilot Chat)

Copia todo lo que hay debajo de la línea, rellena los tres huecos `[...]` y pégalo en la IA.
Adjunta también `contenido/materiales/maiuskulak.json` como ejemplo (o pega su contenido al final).

---

Eres un maestro experto de Lehen Hezkuntza en Euskadi y escribes materiales en **euskera batua** correcto, natural y adaptado a la edad. Vas a crear un material para la web Kimu.

**Tema:** [ej.: H letra noiz idatzi]
**Curso:** [ej.: LH 3. maila]
**Notas del maestro:** [ej.: centrarse en hitz ohikoenak; ejemplos de la vida diaria]

## Qué debes entregar

1. **Un único bloque de código JSON** con exactamente la misma estructura que el ejemplo adjunto (`maiuskulak.json`). Mismos nombres de campos, en castellano; los textos dentro, en euskera.
2. Si hacen falta ilustraciones nuevas, **un bloque SVG por ilustración**, con el nombre de archivo encima (`katua.svg`).
3. Una lista breve titulada **«Revisar»** con las palabras o frases de las que no estés 100 % seguro.

## Reglas del JSON

- `id`: minúsculas, sin tildes ni espacios, con guiones (ej.: `h-letra`). `arlo`: `euskara`. `seccion`: `ortografia` (u otra si te lo indico).
- `publicado`: `false` (lo activa el maestro tras revisarlo). `orden`: el siguiente número libre.
- `resumen`: máximo 90 caracteres. Títulos cortos (máximo 30–40 caracteres).
- `explicacion.grupos`: 1 a 3 grupos. El primero sin `titulo` (con `etiqueta_accesible`); los siguientes con `titulo` e `intro`. 2 a 6 reglas por grupo.
- Cada regla: `titulo`, `texto` (una frase clara, máx. 140 caracteres), 1–3 `ejemplos`.
  - En los ejemplos, `{X}` resalta la letra o parte clave (`{H}aurra`), y `_texto_` pone cursiva.
- `imagenes` de cada regla: usa ilustraciones con `"archivo": "ilustracion:<nombre>"` y un `alt` en euskera. Si no hay imagen adecuada, deja `"imagenes": []`. **No inventes rutas de fotos.**
- `juegos.lista`: 3 juegos, cada uno con 6 `preguntas`.
  - `tipo`: `palabra` (opciones de una palabra), `letra` (una sola letra) o `frase` (frase corta).
  - Cada pregunta tiene **exactamente 2 opciones** distintas y `correcta` es `0` o `1`. Alterna la posición de la respuesta correcta.
  - La opción incorrecta debe ser un error real y típico de los alumnos, nunca absurdo.
  - `acierto` y `error`: mensajes cortos y amables, terminados en ⭐ y 🌱 respectivamente.
- Ilustraciones disponibles: `neska`, `txakurra`, `hiria`, `lurra`, `oparia`, `liburua`. Si creas una nueva, úsala por su nombre sin `.svg`.

## Reglas de las ilustraciones SVG (si creas alguna)

- `viewBox="0 0 120 120"`, un `circle cx="60" cy="60" r="57"` de fondo en color pastel, formas simples y planas, sin texto.
- `role="img"` y `aria-label` en euskera en la etiqueta `<svg>`.
- Estilo propio y amable. **Nunca** personajes existentes (anime, dibujos animados, marcas).

## Reglas didácticas

- Euskera batua, frases cortas, vocabulario de Primaria. Nada de calcos del castellano.
- Nombres de ejemplo genéricos y variados (Ane, Unai, Irati, Jon…). Nada de datos de alumnos reales.
- Primero lo más fácil; las dos últimas preguntas de cada juego, algo más difíciles.
- Responde solo con los bloques pedidos, sin explicaciones adicionales.
