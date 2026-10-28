# Fichas A4: cómo se escriben

Una ficha = un archivo `contenido/fitxak/<id>.json`, validado por `contenido/esquema-fitxa.json`.
Genera la página `<id>.html` con las hojas A4 listas para imprimir (y, si `"soluciones": true`, una hoja final de ZUZENKETA que solo se imprime con el botón «Zuzenketarekin»).
Modelos: `galdera-harridura-ikurrak.json` (resumen + ejercicios), `euskarari-gutuna.json` (plantilla de escritura con versión egokitua), `zazpi-lurralde.json` (póster horizontal), `euskararen-eguna-irakurmena.json` (lectura).

Lee antes la guía de estilo: [`estilo-materiales.md`](estilo-materiales.md).

## Campos de la ficha

`id`, `arlo`, `seccion`, `orden`, `publicado` (false = borrador sin enlaces), `curso` (`LH 1`, `LH 3`, `LH 4`, `LH 3-4`), `tipo_material` (Gaiaren laburpena, Pausoz pauso, Idazketa-txantiloia, Horma-irudia, Ariketa-fitxa, Irakurmena), `nombre`, `titulo_resalte`, `icono`, `resumen`, `descripcion_meta`, `color` (verde, azul, rojo, naranja, morado, turquesa), `soluciones`, `hojas`.

**Teoría y ejercicios van en fichas separadas.** La de teoría lleva `"lugar": "teoria"` (sale en Arauak) y la de ejercicios `"lugar": "actividades"` (sale en Fitxak, con `"soluciones": true`). Cada una apunta a la otra con `"relacionada": "<id>"`, y su página muestra un botón para ir a la compañera. Ejemplo: `letra-larriak` + `letra-larriak-ariketak`.

Cada hoja: `titulo` (MAYÚSCULAS, máx. 34), `subtitulo`, `color`, `orientacion` (`vertical`/`horizontal`), `datos` (false = sin Izena/Data), `bloques`.

## Bloques

| tipo | campos | para qué |
|---|---|---|
| `objetivos` | `items`, `titulo` | «Zer ikasiko dugu?» |
| `apartado` | `titulo`, `texto`, `ejemplos`, `nota`, `color` | Regla numerada. Ejemplo como texto o `{"texto": "...", "bien": true}` / `{"texto": "...", "mal": true}` |
| `tarjetas` | `items` [{`titulo`, `grande`, `texto`, `pie`, `color`}], `columnas` | Rejilla de tarjetas (vocabulario, póster) |
| `tabla` | `cabecera`, `filas` | Tabla; celda `""` = hueco para escribir |
| `lectura` | `titulo`, `parrafos`, `glosario` | Texto con párrafos numerados |
| `entzun` | `audio`, `titulo`, `argibidea`, `testua`, `ahotsa` (emakumea/gizona), `abiadura` | Entzumena: QR al audio + reproductor en pantalla. El MP3 lo genera GitHub con Azure (`scripts/sortu_audioak.py`, workflow «Sortu audioak») a partir del bloque `lectura` de la misma ficha (o de `testua`). Modelo: `aneren-larunbata`. **Siempre una primera hoja «HITZ BERRIAK»** (`gogoratu` + `tarjetas` de 4–6 palabras difíciles con imagen y explicación muy sencilla) antes del audio: el nivel de euskera del alumnado es bajo y cada palabra poco frecuente se explica con imagen. Si cambias el texto, el audio se regenera solo (huella `.sha1`). |
| `ejercicio` | `enunciado`, `modo`, `solucion` + campos del modo | Ver modos abajo |
| `idazketa` | `partes` [{`etiqueta`, `color`, `pista`, `modelo`, `ayudas`, `lineas`, `ancho`: `derecha`/`mitad`}] | Plantilla de escritura (eredua / egokitua / lerro bikoitzak) |
| `pasos` | `items` [{`titulo`, `texto`}], `columnas` | Procedimiento paso a paso |
| `gogoratu` | `texto`, `titulo` | Caja amarilla de idea clave |
| `berrikusi` | `items` | Checklist de autoevaluación |
| `dibujo` | `alto` (mm), `texto` | Recuadro para dibujar |
| `nota` | `texto` | Texto pequeño |
| `parrafo` | `texto` | Párrafo de lectura numerado (para intercalar preguntas; usa `"numeracion_continua": true`) |
| `ilustracion` | `archivo` (SVG de `contenido/ilustraciones/`), `alto`, `pie` | Dibujo dentro de la hoja |
| `relleno` | — | Empuja lo siguiente al pie de la hoja |
| `tablero` | `casillas`, `arauak`, `txartelak` | Tablero horizontal con recorrido, reglas y retos |
| `flipbook` | `portada`, `pestanas` | Libro recortable con portada y 4–6 pestañas |
| `txartelak` | `items`, `erabilerak` (opcional) | Tarjetas de repaso a doble cara, 8 por hoja |
| `margotu` | `filas`, `leyenda`, `grande` (opcional) | «Margotu zenbakien arabera»: dibujo en cuadrícula con una operación por casilla. Lo genera `scripts/generar_margotu.py` |

### Bloques recortables e imprimibles

- **`tablero`**: `casillas` tiene exactamente 20 elementos `{ "texto", "tipo", "imagen" }`; `tipo` es `galdera`, `erronka`, `marraztu`, `azaldu` o `izarra`. El recorrido se dibuja en serpiente y muestra número, INICIO y META. `arauak` es una lista corta de 1–4 reglas; `txartelak` contiene 1–4 retos `{ "reto", "solucion" }`. La leyenda combina color e icono. Con `"soluciones": true`, las respuestas de los retos se añaden a la zuzenketa.
- **`flipbook`**: `portada` contiene `titulo` e `imagen`. `pestanas` contiene 4–6 elementos con `titulo`, `ideia`, `adibidea`, `galdera`, `imagen` y `color`. Se imprime en horizontal con las pestañas escalonadas, líneas discontinuas de corte e instrucciones de montaje.
- **`txartelak`**: `items` es una lista de `{ "aurrea", "atzea", "imagen" }`; la imagen es opcional. Se generan hojas de 8 tarjetas en una cuadrícula 2×4: primero los anversos y después los reversos, reflejados por filas para impresión a doble cara por el borde largo. Si hay más de 8 tarjetas, se crean hojas adicionales. `erabilerak` puede sugerir formas de trabajo.

- **`margotu`**: `filas` es la cuadrícula del dibujo (de 4×4 a 16×16); cada casilla es `{ "op": "3+4", "n": 7 }` (la operación y su resultado) o `null` si queda vacía. `leyenda` lista los colores `{ "n": 7, "color": "#d64545", "nombre": "gorria", "marka": "●" }`: cada resultado tiene un color único, con **nombre y marca** además del color. `grande: true` agranda letra y leyenda (LH 1). Con `"soluciones": true` se añade una hoja con el dibujo coloreado. No se escribe a mano: ver «Margotu zenbakien arabera» más abajo.

### Modos de `ejercicio`

| modo | campos |
|---|---|
| `lineas` | `lineas` |
| `completar` | `frases` (usa `[ ]` para casilla y `___` para hueco largo y `_____` (5) para una línea larga donde escribir palabras) |
| `elegir` | `items` [{`texto`, `opciones`}] |
| `verdadero_falso` | `items`, `etiquetas` (por defecto EGIA / GEZURRA) |
| `preguntas` | `items`, `lineas` (por pregunta) |
| `relacionar` | `izquierda`, `derecha` (mismo número; desordena la derecha) |
| `corregir` | `frases` (cada una con una línea debajo) |
| `clasificar` | `columnas`, `filas`, `palabras` |
| `operaciones` | `items` [{`a`, `b`, `op`}], `cab` (por defecto `["", "H", "U"]`), `columnas` | Operaciones en columnas con casillas para el resultado |

`solucion`: texto o lista. Obligatoria si la ficha tiene `"soluciones": true`.

## Minijuegos NEAE (Lotu, Sailkatu, Memoria)

Se generan solos en la página `<id>-jolasa.html`, junto a «Galderak», a partir de la ficha:
- **Lotu** ← ejercicios `relacionar` con `solucion` en formato `"izquierda → derecha"` o `"1. derecha"` (por orden). Mínimo 3 parejas.
- **Sailkatu** ← ejercicios `clasificar` con `palabras` y `solucion` `"Columna: a, b, c. Columna2: d, e"` (o separadas por `·`). Mínimo 4 palabras (3 en fichas LH 1).
- **Memoria** ← `txartelak` con `imagen` + `atzea` corto, `tarjetas` con `imagen` + `titulo` (≥ 4) y parejas `:icono:` → palabra de `relacionar`.

- **Margotu** ← bloque `margotu`: el alumno toca una casilla, resuelve la operación, elige el color del resultado y, si acierta, se pinta; al final aparece el dibujo completo.

Tocar y tocar (sin arrastrar), sin tiempo, sonido suave, pista después de 2 fallos. Escribe las soluciones en esos formatos para que salgan los juegos.

## Margotu zenbakien arabera (generador)

Cada dibujo es un JSON en `contenido/margotu/<id>.json` (cuadrícula de letras, colores con su resultado y reglas de operaciones: `batuketa`, `kenketa`, `biderketa`, `eramanik_gabe`). `python scripts/generar_margotu.py` crea la ficha `contenido/fitxak/<fitxa>.json` (`generado: true`, borrador) con una operación aleatoria —pero fija para cada dibujo— por casilla, cuyo resultado da el color. Los dibujos son originales, en pixel-art de 12×12 a 16×16. Niveles: LH 1 batuketak ≤ 10 (luego ≤ 20), LH 2 batuketak eta kenketak ≤ 20 (luego ≤ 100 sin llevadas), LH 3 taulak 2, 5, 10 (luego todas). Si el área del nivel aún no existe (LH 2), el dibujo queda preparado y el generador lo salta.

## Modo de juego en la pizarra

Las fichas que tengan preguntas aprovechables generan automáticamente una página `<id>-jolasa.html` y muestran el botón «Jolastu arbelean» (o «Jugar en la pizarra») junto a las opciones de impresión. Se extraen los bloques `txartelak` (anverso y reverso), y los ejercicios `elegir`, `verdadero_falso` y `relacionar`. Las preguntas sin una respuesta correcta que se pueda identificar no se incluyen.

En `txartelak`, la respuesta correcta es `atzea` y las otras tarjetas del mismo bloque aportan los distractores. En ejercicios, se usan las soluciones de la ficha para determinar la respuesta. El juego permite configurar de 2 a 4 equipos, sus nombres y colores y un tiempo de 10, 20 o 30 segundos (o sin límite). En la pregunta, las teclas `1`–`4` seleccionan respuestas y la barra espaciadora muestra la solución o avanza después de puntuar. El profesorado controla los puntos; no se guardan datos.

## Formato del texto

`**negrita**`, `_cursiva_`, `{L}` resalta (letra o palabra clave), `~5~` tachado, `[ ]` casilla, `___` hueco largo, `_____` línea larga para escribir palabras, `\n` salto de línea.

Un paso de `pasos` puede llevar `op`: `{"cab": ["", "H", "U"], "lleva": ["", "1", ""], "filas": [["", "3", "8"], ["+", "2", "5"]], "res": ["", "6", "3"]}` (celda vacía en `res` = casilla). Una hoja puede llevar `"tamano": "grande"` (teoría con poco texto). Los colores de cabecera de una `tabla` se ponen con `{"texto": "E", "color": "verde"}`. Las fichas de `gaztelera` salen con los textos de la hoja en castellano.

## Comprobar que cabe

Cada hoja debe caber en un A4. Si no cabe, quita líneas o divide la hoja en dos.
Para verlo: `python scripts/build.py` y abre `_site/<id>.html` (o imprime a PDF).

## Imágenes

Las imágenes están en `estatico/irudiak/` (Fluent Emoji de Microsoft, licencia MIT: uso libre, también comercial; la licencia está en `estatico/irudiak/LICENSE-fluentui-emoji.txt`).

- Campo `"imagen": "<nombre>"` en: ramas y centro de `mapa`, `tarjetas`, `apartado`, `pasos` y partes de `idazketa`.
- Dentro de un texto: `:nombre:` pone la imagen pequeña en línea.
- Cada ficha de teoría lleva al final una hoja horizontal con su **mapa mental**, con imagen en el centro y en cada rama.

Disponibles (142): abacus, artist-palette, baguette-bread, banana, basket, bell-pepper, bone, bookmark-tabs, books, bowl-with-spoon, boy, brain, bread, broccoli, butterfly, calendar, carrot, castle, cat, check-mark-button, cheese-wedge, chestnut, child, church, cityscape, clapping-hands, classical-building, clipboard, coin, cooked-rice, cooking, cow, crayon, cross-mark, cucumber, cup-with-straw, cut-of-meat, deciduous-tree, dog, door, droplet, duck, ear-of-corn, egg, envelope, euro-banknote, evergreen-tree, ewe, fallen-leaf, fish, flexed-biceps, fork-and-knife-with-plate, full-moon, girl, glass-of-milk, globe-showing-europe-africa, gloves, goat, grapes, handshake, heart-hands, hot-beverage, house, houses, hundred-points, input-latin-letters, input-latin-lowercase, input-latin-uppercase, input-numbers, keycap-1, keycap-10, keycap-2, keycap-3, keycap-4, keycap-5, keycap-6, kitchen-knife, kiwi-fruit, label, leafy-green, light-bulb, magnifying-glass-tilted-right, memo, mountain, musical-note, national-park, notebook, old-woman, open-book, package, paintbrush, party-popper, pear, pen, pencil, person-running, placard, potato, potted-plant, poultry-leg, pushpin, puzzle-piece, raising-hands, recycling-symbol, red-apple, red-exclamation-mark, red-question-mark, ringed-planet, sandwich, school, scissors, seedling, shopping-cart, sleeping-face, smiling-face-with-smiling-eyes, snow-capped-mountain, soccer-ball, spaghetti, speaker-high-volume, speech-balloon, spiral-calendar, star, straight-ruler, strawberry, student, sun, sun-with-face, tangerine, teacher, thinking-face, thumbs-up, tomato, tooth, trophy, warning, wastebasket, water-wave, waving-hand, world-map, wrapped-gift, writing-hand, yellow-heart.

Para añadir más: copiar el SVG «Color» de https://github.com/microsoft/fluentui-emoji a `estatico/irudiak/<nombre-en-minusculas>.svg`.
