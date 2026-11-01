"""Miniaturas de las fichas: la primera hoja (A4) de cada ficha publicada, en WebP.

Uso:  python scripts/miniaturak.py [_site] [--denak]
      Escribe _site/miniaturak/<id>.webp. Sin --denak, salta las que ya existen
      (p. ej. las copiadas desde estatico/miniaturak/), para que sea rápido.
Necesita: pip install playwright pillow && python -m playwright install chromium

Las tarjetas de la web (portada, arloak, apartados) enseñan estas miniaturas;
si falta alguna, la tarjeta se queda con su icono (onerror en la plantilla).
"""
import io
import json
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent.parent
SITE = Path(next((a for a in sys.argv[1:] if not a.startswith("--")), "_site")).resolve()
DENAK = "--denak" in sys.argv
ANCHO = 480  # px; la tarjeta más grande la enseña a ~300 px, así vale para pantallas retina


def fichas_publicadas():
    for p in sorted((RAIZ / "contenido" / "fitxak").glob("*.json")):
        f = json.loads(p.read_text(encoding="utf-8"))
        if f.get("publicado") and (SITE / f'{f["id"]}.html').exists():
            yield f["id"]


def main():
    destino = SITE / "miniaturak"
    destino.mkdir(exist_ok=True)
    ids = [i for i in fichas_publicadas() if DENAK or not (destino / f"{i}.webp").exists()]
    print(f"Miniaturas por generar: {len(ids)}")
    hechas, fallos = 0, []
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pag = nav.new_page(viewport={"width": 1280, "height": 1800})
        for i in ids:
            try:
                pag.goto((SITE / f"{i}.html").as_uri(), wait_until="load")
                pag.evaluate("document.fonts.ready")
                hoja = pag.query_selector(".hoja:not(.soluciones)")
                if not hoja:
                    fallos.append(f"{i} (sin .hoja)")
                    continue
                im = Image.open(io.BytesIO(hoja.screenshot())).convert("RGB")
                alto = round(im.height * ANCHO / im.width)
                im = im.resize((ANCHO, alto), Image.LANCZOS).crop((0, 0, ANCHO, min(alto, round(ANCHO * 1.414))))
                im.save(destino / f"{i}.webp", "WEBP", quality=78)
                hechas += 1
            except Exception as e:  # una ficha rara no debe parar la publicación
                fallos.append(f"{i} ({e.__class__.__name__})")
        nav.close()
    print(f"✓ {hechas} miniatura(s) en {destino.relative_to(SITE.parent) if SITE.parent in destino.parents else destino}")
    if fallos:
        print("Sin miniatura (se verá el icono): " + ", ".join(fallos))


if __name__ == "__main__":
    main()
