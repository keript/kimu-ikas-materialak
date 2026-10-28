# Instrucciones para Copilot — Kimu

Kimu es una web de recursos educativos en euskera para **LH 3 y LH 4 (8–10 años)** y, desde octubre de 2026, también **LH 1 (6–7 años)**, publicada en GitHub Pages.

**Si el issue es de LH 1, lee además [`docs/estilo-lh1.md`](../docs/estilo-lh1.md)**: áreas `lh1-euskara`, `lh1-matematika`, `lh1-ingurunea` (`"maila": "LH 1"`), fichas con `"curso": "LH 1"` e id `lh1-…`, muy poco texto, iconos de acción, letra muy grande y una imagen real por palabra.

**Antes de crear o cambiar cualquier material, lee [`docs/estilo-materiales.md`](../docs/estilo-materiales.md).** Los materiales son herramientas reales de aula (fichas A4, procedimientos paso a paso, plantillas de escritura con versión adaptada, resúmenes de tema), no juegos infantiles. La web **se genera automáticamente**: nunca se escriben páginas HTML a mano.

## Cómo funciona

- `contenido/` — todo el texto de la web, en JSON. Los materiales son fichas en `contenido/fitxak/` (ver abajo). `contenido/materiales/` es el formato antiguo de juegos, sin uso.
- **Fichas A4** (el formato principal): `contenido/fitxak/<id>.json`, validadas por `contenido/esquema-fitxa.json`. Bloques y modos de ejercicio: [`docs/fichas.md`](../docs/fichas.md). Una sección con `"tipo": "pack"` lista sus fichas directamente.
- `contenido/arloak/` — áreas (euskara, matematika…). `contenido/secciones/` — secciones de un área (ortografia…).
- `contenido/ilustraciones/*.svg` — ilustraciones reutilizables de los juegos (viewBox 120×120, círculo de fondo, `role="img"` y `aria-label` en euskera).
- `plantillas/` — plantillas Jinja2 (`base.html`, `mosaico.html`, `explicacion.html`, `juegos.html`, `arlo_preparando.html`, `inicio.html`).
- `estatico/` — CSS, `juegos.js` (motor común de los juegos) y fotos en `estatico/assets/<id-material>/`.
- `scripts/build.py` — valida el contenido y genera la web en `_site/`. `python scripts/build.py --check` solo valida.
- `.github/workflows/publicar.yml` — en cada push a `main` valida, genera y publica. En los pull requests solo valida.

## Reglas

1. **No edites `_site/`** ni crees archivos `.html` en la raíz: se generan.
2. **Añadir un material = crear fichas JSON** en `contenido/fitxak/` siguiendo `docs/fichas.md` y usando `letra-larriak.json` + `letra-larriak-ariketak.json` como modelo: **teoría y ejercicios en fichas separadas**, enlazadas con `relacionada`. Si necesita fotos, van en `estatico/assets/<id>/`. `contenido/materiales/` (formato antiguo de juegos) no se usa para materiales nuevos.
3. **No cambies textos en euskera** de materiales existentes salvo que el issue lo pida expresamente. Los textos los revisa el autor, que es maestro.
4. Todo texto nuevo para alumnos va en **euskera batua**, frases cortas, nivel LH 3–4, sin tono infantil. Nada de traducciones literales del castellano. Si dudas de una palabra, déjala marcada en la descripción del PR.
5. **Nada de personajes, logos o imágenes con derechos** (anime, Disney, marcas…). Fotos solo de Unsplash o con licencia libre, y siempre con crédito en `creditos_imagenes` cuando la licencia lo exija.
6. **Nunca uses datos ni fotos de alumnos reales.** Nombres de ejemplo genéricos (Ane, Unai, Ttiki…).
7. Mantén el diseño: usa las variables CSS de `estatico/area.css` (`--accent`, `--soft`, `--ink`…). No añadas librerías ni frameworks; todo debe funcionar sin conexión a internet salvo las fotos.
8. Accesibilidad: `alt` en todas las imágenes, botones con texto, contraste suficiente, nada que dependa solo del color.
9. Si cambias el esquema, actualiza a la vez `contenido/esquema-fitxa.json`, la validación de `scripts/build.py`, las plantillas, `docs/fichas.md` y `prompts/material-berria.md`.
10. **Antes de terminar, ejecuta `pip install -r requirements.txt && python scripts/build.py`** y comprueba que no da errores. Si cambias algo visual, explica en el PR qué páginas cambian.

## Ikas-egoerak: el kit completo (criterios de Kimu)

Cuando un issue traiga una ikas-egoera, crea un **pack** propio (`contenido/secciones/<id>.json`, `"tipo": "pack"`) en el arlo que toque, con estas fichas:

1. **Teoría** (`lugar: teoria`, una o varias): sola, sin ejercicios, muy visual (tarjetas con `imagen`, `gogoratu`) y **un mapa mental (`mapa`) al final**.
2. **Ariketak** (`lugar: actividades`, `soluciones: true`), cada ficha con:
   - **Ejemplo resuelto** al principio (`pasos` o `gogoratu`).
   - Actividades de **dificultad gradual**: ⭐ → ⭐⭐ → ⭐⭐⭐ en el enunciado.
   - Un **reto final** (`apartado` titulado «ERRONKA») ligado al producto final de la egoera.
   - **Checklist** al final (`berrikusi`: «Irakurri dut», «Berrikusi dut», «Egiaztatu dut»…).
3. **Irakurgaia + galderak** si hay lectura: modelo `ibaiaren-eguna` (texto con párrafos numerados en una ficha; en otra, una pregunta por párrafo, test + abiertas, ordenatu, iritzia, hiztegia).
4. **Estazioak** (rincones): una ficha con **4 estaciones** (`tarjetas`, 2 columnas). Cada una lleva: Helburua, Argibideak, Materialak, Denbora y Zeregina breve. Añade un **pasaporte** (`tabla` con nombre de estación y casilla `[ ]`) y las soluciones en la zuzenketa.
5. **Errepaso-txartelak**: 12 tarjetas numeradas de repaso (pregunta o reto en cada una; respuestas en la zuzenketa) e ideas de uso (bakarka, binaka, talde txikian, talde-erronka).
6. **Infografia**: una hoja `orientacion: horizontal` que resume el tema en 4–6 bloques ordenados, con flechas o `mapa`, un recuadro «FUNTSEZKOA» con 3 ideas y una pregunta rápida de autoevaluación.
7. **Irakaslearen gida** (`lugar: teoria`, `datos: false`): objetivo, sesiones (`tabla`: saioa, jarduera, fitxa, denbora), materiales, tarea final y checklist del alumnado.

**Evita:** enunciados ambiguos, retos repetidos, letra pequeña, soluciones mezcladas con el ejercicio, errores de cálculo o de contenido, actividades sin objetivo, tono infantil. Revisa todas las soluciones.

**Matemáticas:** usa la notación de clase **M · milakoak, E · ehunekoak, H · hamarrekoak, B · batekoak** (nunca «U/unitateak») con sus colores fijos: **M `amarillo`, E `verde`, H `rojo`, B `azul`**. En el arlo matematika se aplican solos: las palabras milako/ehuneko/hamarreko/bateko y las letras M E H B se colorean al generar la web, y las tarjetas, apartados y ramas cuyo título las nombra toman su color. Deskonposatu en dos formas: zifren balioaren arabera (2000 + 100 + 40 + 8) y posizioaren arabera (2 M + 1 E + 4 H + 8 B). Zuzen numerikoak, alderatu (< > =) eta biribildu hamarrekora / ehunekora.

**Siempre:** «kuia», nunca «kalabaza». No publiques material del colegio ni copies documentos adjuntos literalmente: adapta y crea material original.

## Alumnado NEAE (criterio base de Kimu)

El público principal es **alumnado de PT (Pedagogía Terapéutica) y NEAE** (TDAH, TEA, dislexia, DEA, incorporación tardía) y sus docentes. Todo —fichas, teoría, juegos y la propia web— debe ser **muy visual**:
- **Imágenes reales o dibujos realistas**, nunca caricaturas infantiles ni abstractas. Una imagen = un concepto, reconocible a la primera. Prioriza fotos con licencia libre de uso comercial (Pexels, Unsplash, Wikimedia Commons CC0/CC BY) guardadas en `estatico/assets/<id>/` con crédito en `creditos_imagenes`; si no, iconos de `estatico/irudiak`.
- **Lectura fácil:** frases cortas (sujeto + verbo + complemento), una idea por frase, una instrucción por enunciado, palabras frecuentes. Nada de dobles negaciones.
- **Apoyo visual en cada enunciado** (icono de la acción: idatzi ✏️, inguratu, lotu, marraztu…) y ejemplo hecho antes de cada tipo de ejercicio nuevo.
- **Estructura predecible:** mismo orden en todas las fichas (título → ejemplo → ejercicios ⭐ → ⭐⭐ → ⭐⭐⭐ → berrikusi). Pocos elementos por hoja y mucho espacio para escribir.
- Letra grande (no reducir el tamaño de la plantilla), alto contraste, nada que dependa solo del color.
- **Una imagen por ítem** en los ejercicios de texto: pon `:icono:` al inicio de cada frase/ítem (tras «a)») y en las palabras de clasificar. **Huecos de escritura ≥ 4 cm** (`___`); en matemáticas, más cortos.
- **Imágenes reales etiquetadas:** las imágenes realistas van en `estatico/irudiak-errealak/` (fondo blanco, sin texto). Para etiquetarlas, añade su entrada en `scripts/irudi_etiketatuak.py` y ejecútalo: genera `<id>.svg` (con nombres, para teoría) y `<id>-hutsik.svg` (casillas numeradas, para etiquetar). Úsalas con el bloque `ilustracion`.
- **Pedir imágenes nuevas:** si falta una imagen realista, añádela a `contenido/irudiak/eskaerak.json` (`id`, `aspect`, `prompt` en inglés describiendo solo el contenido, con cada parte bien separada). Al fusionar en `main`, GitHub la genera con Gemini y la guarda en `estatico/irudiak-errealak/<id>.jpg`. Mientras no exista, usa iconos de `estatico/irudiak`.
- **Colores pastel:** no fuerces colores intensos; usa los `color` de la plantilla (ya son pastel).
- **No uses pictogramas ARASAAC**: su licencia (CC BY-NC-SA) no permite uso comercial.

**Fichas «egokitua» (⭐ indartzeko, NEAE/PT) — obligatorio:** marca cada hoja con `"egokitua": true` (letra ~21 px, interlineado 1,6, casillas grandes), **máximo 3 ítems por ejercicio**, y en cada ejercicio un **ejemplo resuelto** con el campo `"ejemplo"` (se muestra como «✓ Adibidea»). Pocas cosas por hoja. En matemáticas lo hace solo `scripts/generar_mate.py` (función `egokitu`).

## Juegos (se generan solos)

Cada ficha con `relacionar`, `clasificar`, `txartelak` o `tarjetas` con imagen genera minijuegos NEAE (Lotu, Sailkatu, Memoria) además de «Galderak». Escribe las `solucion` en los formatos de `docs/fichas.md` («Minijuegos NEAE») para que salgan; comprueba en `_site/<id>-jolasa.html` que aparecen.

## Kimu 3.0: receta de calidad (obligatoria)

Sigue [`docs/kalitatea.md`](../docs/kalitatea.md). Antes de terminar ejecuta `python scripts/kalitatea.py --solo <ids de tus fichas> --min 9.5`: si alguna ficha saca menos de 9,5, mejórala (te dice qué falta). El revisor automático no fusiona PR con fichas por debajo de 9,5.

## Calidad 10/10 (obligatorio en todo material nuevo)

- **Poco texto, mucha imagen.** Tarjeta: título ≤ 4 palabras y texto ≤ 15 palabras. Apartado: ≤ 35 palabras. Si necesitas más, divide en dos tarjetas.
- **Cada tarjeta, apartado y rama del mapa lleva `imagen`** (estatico/irudiak, lista en docs/fichas.md). No repitas la misma imagen en una hoja.
- **Ninguna hoja medio vacía:** si sobra más de un tercio, añade una actividad, una tarjeta o usa `tamano: grande`. Ninguna hoja puede salirse del A4.
- **Ejercicios variados:** no más de 2 bloques seguidos del mismo `modo`. Mezcla relacionar, clasificar, elegir, egia/gezurra, completar, marraztu.
- **Enunciados cortos e imperativos** (≤ 15 palabras), con ⭐/⭐⭐/⭐⭐⭐.
- **Euskera natural:** nada de calcos (ej.: «anoa», no «errazio»). Marca en el PR las palabras dudosas.
- **Títulos de hoja ≤ 24 caracteres** para que quepan en una línea.
- Revisa cada solución dos veces (cálculos, orden, letras).

## Matemáticas por unidades (generador)

Las fichas `mate-<unidad>-*` las genera `scripts/generar_mate.py` (4 niveles: indartzeko egokitua, sendotzeko, sakontzeko, berrikusketa) con números aleatorios y soluciones calculadas. **No las edites a mano** (`generado: true`). Para una unidad nueva del libro, añade una función `unitatea_X_Y(r)` siguiendo las existentes (solo temario: ejercicios originales, nunca copiados) y regístrala en `UNITATEAK`. Versiones nuevas: Actions → «Sortu mate fitxak».


- En `ejemplos`: `{G}aur` resalta la letra G; `_Haizearen orrazia_` pone cursiva.
- En `creditos_imagenes`: enlaces con `[texto](https://...)`.
- En las fichas: `**negrita**`, `_cursiva_`, `{X}` resaltado, `[ ]` casilla, `___` hueco largo (ver `docs/fichas.md`).
- `publicado: false` valida el material pero no lo publica (borrador).

## Idioma

Comenta el código y escribe los PR en castellano. El contenido para el público, en euskera (salvo el arlo `gaztelera`, en castellano).

## Nivel de euskera (decisión de Iker, 26-10-2026)
El nivel de euskera del alumnado es cada vez más bajo. En todo material (sobre todo lecturas y entzumenak): vocabulario frecuente, frases cortas, y **cada palabra poco habitual (p. ej. «ogi txigortua», «azoka», «hunkitu») se presenta antes con imagen y una explicación muy sencilla** (hoja o caja «Hitz berriak»). Las historias deben tener hilo: inicio, problema y solución.

## Imágenes nuevas
Si falta una imagen real, añade un grupo de 4 palabras a `contenido/irudiak/hiztegia-irudiak.json` (`id`, `izena`, `hitzak` id→palabra, `edukia` en inglés describiendo las 4 fotos en orden) y usa ya esos ids en las fichas (sale el marcador «irudia laster» hasta que exista la foto: ejecuta `python scripts/foto_irudia.py`). Un workflow abre solo el issue para que Iker la genere; no hace falta avisar.

## Publicación semanal (decisión de Iker, 26-10-2026)
Todo material nuevo entra como borrador (`"publicado": false`, sin `publicar_desde`). Cada domingo `scripts/astekoa.py` propone a Iker 6 borradores (lunes LH 1 … sábado LH 6) y él los aprueba en un issue. **Cada material nuevo debe traer su juego en pantalla** (Lotu, Sailkatu, Memoria o Galderak): es lo que más gusta en clase. Si un material tiene teoría y ariketak, enlázalos con `relacionada` para que se publiquen juntos.

## Antes de terminar un PR (obligatorio)
Ejecuta `python scripts/build.py && python scripts/revisar_hojas.py _site --solo <tus ids>` y `python scripts/kalitatea.py --solo <tus ids> --min 9.5`. El fallo más común es que **la hoja se sale del A4**: reparte los bloques en más hojas, quita líneas de escritura o reduce ítems. Actualiza tu rama con `main` antes de terminar para evitar conflictos.
