# Fichas A4: cómo se escriben

Una ficha = un archivo `contenido/fitxak/<id>.json`, validado por `contenido/esquema-fitxa.json`.
Genera la página `<id>.html` con las hojas A4 listas para imprimir (y, si `"soluciones": true`, una hoja final de ZUZENKETA que solo se imprime con el botón «Zuzenketarekin»).
Modelos: `galdera-harridura-ikurrak.json` (resumen + ejercicios), `euskarari-gutuna.json` (plantilla de escritura con versión egokitua), `zazpi-lurralde.json` (póster horizontal), `euskararen-eguna-irakurmena.json` (lectura).

Lee antes la guía de estilo: [`estilo-materiales.md`](estilo-materiales.md).

## Campos de la ficha

`id`, `arlo`, `seccion`, `orden`, `publicado` (false = borrador sin enlaces), `curso` (`LH 3`, `LH 4`, `LH 3-4`), `tipo_material` (Gaiaren laburpena, Pausoz pauso, Idazketa-txantiloia, Horma-irudia, Ariketa-fitxa, Irakurmena), `nombre`, `titulo_resalte`, `icono`, `resumen`, `descripcion_meta`, `color` (verde, azul, rojo, naranja, morado, turquesa), `soluciones`, `hojas`.

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

### Modos de `ejercicio`

| modo | campos |
|---|---|
| `lineas` | `lineas` |
| `completar` | `frases` (usa `[ ]` para casilla y `___` para hueco largo) |
| `elegir` | `items` [{`texto`, `opciones`}] |
| `verdadero_falso` | `items`, `etiquetas` (por defecto EGIA / GEZURRA) |
| `preguntas` | `items`, `lineas` (por pregunta) |
| `relacionar` | `izquierda`, `derecha` (mismo número; desordena la derecha) |
| `corregir` | `frases` (cada una con una línea debajo) |
| `clasificar` | `columnas`, `filas`, `palabras` |
| `operaciones` | `items` [{`a`, `b`, `op`}], `cab` (por defecto `["", "H", "U"]`), `columnas` | Operaciones en columnas con casillas para el resultado |

`solucion`: texto o lista. Obligatoria si la ficha tiene `"soluciones": true`.

## Formato del texto

`**negrita**`, `_cursiva_`, `{L}` resalta (letra o palabra clave), `~5~` tachado, `[ ]` casilla, `___` hueco largo, `\n` salto de línea.

Un paso de `pasos` puede llevar `op`: `{"cab": ["", "H", "U"], "lleva": ["", "1", ""], "filas": [["", "3", "8"], ["+", "2", "5"]], "res": ["", "6", "3"]}` (celda vacía en `res` = casilla). Una hoja puede llevar `"tamano": "grande"` (teoría con poco texto). Los colores de cabecera de una `tabla` se ponen con `{"texto": "E", "color": "verde"}`. Las fichas de `gaztelera` salen con los textos de la hoja en castellano.

## Comprobar que cabe

Cada hoja debe caber en un A4. Si no cabe, quita líneas o divide la hoja en dos.
Para verlo: `python scripts/build.py` y abre `_site/<id>.html` (o imprime a PDF).
