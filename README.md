# Kimu — ikas-materialak

Recursos educativos visuales en euskera para Lehen Hezkuntza.
Web: https://keript.github.io/kimu-ikas-materialak/

La web **se genera sola** a partir de archivos de contenido. No se escribe HTML a mano.

**Guía de estilo:** [`docs/estilo-materiales.md`](docs/estilo-materiales.md). Materiales reales para LH 3–4, no infantiles.

## Añadir un material nuevo (cada semana)

1. **Redactar.** Pide el material a Claude, o usa el prompt de [`prompts/material-berria.md`](prompts/material-berria.md) con Gemini. Sale un archivo JSON.
2. **Guardarlo** como `contenido/materiales/<id>.json` con `"publicado": false`.
   En GitHub: *Add file → Create new file*, pega el contenido y pulsa *Commit*.
3. **Revisar la vista previa.** En 1–2 minutos estará en `https://keript.github.io/kimu-ikas-materialak/<id>.html`. No aparece en los menús hasta que la publiques.
4. **Publicar.** Si está bien, cambia `"publicado": false` por `true` y haz *Commit*. Aparecerá en Arauak y en Fitxak automáticamente.

Si el contenido tiene un error (falta un campo, la respuesta correcta no existe, una imagen no está…), la publicación se para y en la pestaña **Actions** de GitHub verás exactamente qué arreglar. La web publicada no se rompe nunca.

**Con Copilot:** abre un *issue* con la plantilla «Material berria», pega el JSON o describe el material, y asígnaselo a Copilot. Copilot sigue las reglas de [`.github/copilot-instructions.md`](.github/copilot-instructions.md) y abre un pull request que se valida solo.

## Dónde está cada cosa

| Carpeta | Qué contiene | ¿Lo tocas? |
|---|---|---|
| `contenido/materiales/` | Un JSON por material (explicación + juegos + fichas) | **Sí, cada semana** |
| `contenido/arloak/`, `contenido/secciones/` | Áreas y secciones de la web | De vez en cuando |
| `contenido/ilustraciones/` | Dibujos SVG de los juegos, reutilizables | Al añadir dibujos |
| `estatico/assets/<id>/` | Fotos de cada material | Si usas fotos |
| `plantillas/`, `estatico/*.css`, `estatico/juegos.js` | Diseño y funcionamiento | Solo para cambiar el diseño |
| `scripts/build.py` | Valida y genera la web | No |
| `_site/` | La web generada (no se sube a GitHub) | Nunca |

## Formato de los textos

- `{G}aur jolastuko gara.` → resalta la **G** en verde.
- `_Haizearen orrazia_` → cursiva.
- `[Fred Romero, CC BY 2.0](https://...)` → enlace (en los créditos de fotos).
- Imagen de una regla: `"archivo": "maiuskulak/jaiak.jpg"` (foto) o `"archivo": "ilustracion:neska"` (dibujo).

## Probar en tu ordenador (opcional)

```bash
pip install -r requirements.txt
python scripts/build.py --check   # solo comprueba
python scripts/build.py           # genera la web en _site/ (abre _site/index.html)
```

## Configuración inicial (una sola vez)

En GitHub: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
