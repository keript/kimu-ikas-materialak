# Fichas A4: cómo se escriben

Una ficha = un archivo `contenido/fitxak/<id>.json`, validado por `contenido/esquema-fitxa.json`.
Genera la página `<id>.html` con las hojas A4 listas para imprimir (y, si `"soluciones": true`, una hoja final de ZUZENKETA que solo se imprime con el botón «Zuzenketarekin»).
Modelos: `galdera-harridura-ikurrak.json` (resumen + ejercicios), `euskarari-gutuna.json` (plantilla de escritura con versión egokitua), `zazpi-lurralde.json` (póster horizontal), `euskararen-eguna-irakurmena.json` (lectura).

Lee antes la guía de estilo: [`estilo-materiales.md`](estilo-materiales.md).

## Campos de la ficha

`id`, `arlo`, `seccion`, `orden`, `publicado` (false = borrador sin enlaces), `curso` (`LH 3`, `LH 4`, `LH 3-4`), `tipo_material` (Gaiaren laburpena, Pausoz pauso, Idazketa-txantiloia, Horma-irudia, Ariketa-fitxa, Irakurmena), `nombre`, `titulo_resalte`, `icono`, `resumen`, `descripcion_meta`, `color` (verde, azul, rojo, naranja, morado, turquesa), `soluciones`, `hojas`.

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

`solucion`: texto o lista. Obligatoria si la ficha tiene `"soluciones": true`.

## Formato del texto

`**negrita**`, `_cursiva_`, `{L}` resalta (letra o palabra clave), `[ ]` casilla, `___` hueco largo.

## Comprobar que cabe

Cada hoja debe caber en un A4. Si no cabe, quita líneas o divide la hoja en dos.
Para verlo: `python scripts/build.py` y abre `_site/<id>.html` (o imprime a PDF).
