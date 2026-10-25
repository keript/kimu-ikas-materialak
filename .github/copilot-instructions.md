# Instrucciones para Copilot — Kimu

Kimu es una web de recursos educativos en euskera para **LH 3 y LH 4 (8–10 años)**, publicada en GitHub Pages.

**Antes de crear o cambiar cualquier material, lee [`docs/estilo-materiales.md`](../docs/estilo-materiales.md).** Los materiales son herramientas reales de aula (fichas A4, procedimientos paso a paso, plantillas de escritura con versión adaptada, resúmenes de tema), no juegos infantiles. La web **se genera automáticamente**: nunca se escriben páginas HTML a mano.

## Cómo funciona

- `contenido/` — todo el texto de la web, en JSON. **Un material = un archivo** en `contenido/materiales/<id>.json`, validado por `contenido/esquema-material.json`.
- `contenido/arloak/` — áreas (euskara, matematika…). `contenido/secciones/` — secciones de un área (ortografia…).
- `contenido/ilustraciones/*.svg` — ilustraciones reutilizables de los juegos (viewBox 120×120, círculo de fondo, `role="img"` y `aria-label` en euskera).
- `plantillas/` — plantillas Jinja2 (`base.html`, `mosaico.html`, `explicacion.html`, `juegos.html`, `arlo_preparando.html`, `inicio.html`).
- `estatico/` — CSS, `juegos.js` (motor común de los juegos) y fotos en `estatico/assets/<id-material>/`.
- `scripts/build.py` — valida el contenido y genera la web en `_site/`. `python scripts/build.py --check` solo valida.
- `.github/workflows/publicar.yml` — en cada push a `main` valida, genera y publica. En los pull requests solo valida.

## Reglas

1. **No edites `_site/`** ni crees archivos `.html` en la raíz: se generan.
2. **Añadir un material = crear un único JSON** en `contenido/materiales/` siguiendo el esquema y usando `maiuskulak.json` como modelo. Si necesita fotos, van en `estatico/assets/<id>/`. Si necesita ilustraciones nuevas, crea SVG en `contenido/ilustraciones/` con el mismo estilo que las existentes.
3. **No cambies textos en euskera** de materiales existentes salvo que el issue lo pida expresamente. Los textos los revisa el autor, que es maestro.
4. Todo texto nuevo para alumnos va en **euskera batua**, frases cortas, nivel LH 3–4, sin tono infantil. Nada de traducciones literales del castellano. Si dudas de una palabra, déjala marcada en la descripción del PR.
5. **Nada de personajes, logos o imágenes con derechos** (anime, Disney, marcas…). Fotos solo de Unsplash o con licencia libre, y siempre con crédito en `creditos_imagenes` cuando la licencia lo exija.
6. **Nunca uses datos ni fotos de alumnos reales.** Nombres de ejemplo genéricos (Ane, Unai, Ttiki…).
7. Mantén el diseño: usa las variables CSS de `estatico/area.css` (`--accent`, `--soft`, `--ink`…). No añadas librerías ni frameworks; todo debe funcionar sin conexión a internet salvo las fotos.
8. Accesibilidad: `alt` en todas las imágenes, botones con texto, contraste suficiente, nada que dependa solo del color.
9. Si cambias el esquema, actualiza a la vez `contenido/esquema-material.json`, la validación de `scripts/build.py`, las plantillas, `maiuskulak.json` y `prompts/material-berria.md`.
10. **Antes de terminar, ejecuta `pip install -r requirements.txt && python scripts/build.py`** y comprueba que no da errores. Si cambias algo visual, explica en el PR qué páginas cambian.

## Formato especial de textos

- En `ejemplos`: `{G}aur` resalta la letra G; `_Haizearen orrazia_` pone cursiva.
- En `creditos_imagenes`: enlaces con `[texto](https://...)`.
- En `imagenes[].archivo`: `maiuskulak/jaiak.jpg` (foto en `estatico/assets/`) o `ilustracion:neska` (SVG de `contenido/ilustraciones/`).
- `publicado: false` valida el material pero no lo publica (borrador).

## Idioma

Comenta el código y escribe los PR en castellano. El contenido para el público, en euskera (salvo el arlo `gaztelera`, en castellano).
