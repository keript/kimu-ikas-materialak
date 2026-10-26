"""Miniaturas reales de las fichas: captura de la 1.ª hoja de cada ficha publicada.

Guarda estatico/miniaturak/<id>.webp (ancho 360 px, calidad 70). Por defecto solo crea las que faltan.

Uso:  python scripts/build.py && python scripts/miniaturas.py [_site] [--todas] [--solo id1,id2] [--hay-faltantes]
  --todas           regenera también las que ya existen
  --hay-faltantes   no captura nada: sale con código 0 si falta alguna miniatura (para el workflow)
Necesita:  pip install playwright pillow && python -m playwright install --with-deps chromium
"""
import io
import json
import os
import shutil
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
POSICIONALES = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith("--") and sys.argv[i - 1] != "--solo"]
SITE = Path(POSICIONALES[0] if POSICIONALES else "_site").resolve()
DESTINO = RAIZ / "estatico" / "miniaturak"
ANCHO, CALIDAD = 360, 70


def fichas_publicadas():
    hoy = os.environ.get("KIMU_FECHA") or date.today().isoformat()
    ids = []
    for ruta in sorted((RAIZ / "contenido" / "fitxak").glob("*.json")):
        f = json.loads(ruta.read_text(encoding="utf-8"))
        if f.get("publicado") and f.get("publicar_desde", "") <= hoy:
            ids.append(f["id"])
    return ids


def main():
    ids = fichas_publicadas()
    if "--solo" in sys.argv:
        ids = [i for i in ids if i in set(sys.argv[sys.argv.index("--solo") + 1].split(","))]
    pendientes = ids if "--todas" in sys.argv else [i for i in ids if not (DESTINO / f"{i}.webp").is_file()]
    if "--hay-faltantes" in sys.argv:
        sys.exit(0 if pendientes else 1)
    if not pendientes:
        print("✓ Todas las fichas ya tienen miniatura.")
        return

    from PIL import Image
    from playwright.sync_api import sync_playwright

    DESTINO.mkdir(parents=True, exist_ok=True)
    fallos = []
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pg = nav.new_page(viewport={"width": 1280, "height": 1200}, color_scheme="light")
        for i in pendientes:
            pagina = SITE / f"{i}.html"
            try:
                pg.goto(pagina.as_uri())
                pg.wait_for_timeout(200)
                hoja = pg.query_selector("article.hoja")
                png = hoja.screenshot()
                img = Image.open(io.BytesIO(png)).convert("RGB")
                img = img.resize((ANCHO, round(img.height * ANCHO / img.width)), Image.LANCZOS)
                img.save(DESTINO / f"{i}.webp", "WEBP", quality=CALIDAD, method=6)
                if (SITE / "miniaturak").is_dir():
                    shutil.copy(DESTINO / f"{i}.webp", SITE / "miniaturak" / f"{i}.webp")
            except Exception as e:  # noqa: BLE001
                fallos.append(f"{i}: {str(e)[:120]}")
        nav.close()
    print(f"✓ {len(pendientes) - len(fallos)} miniatura(s) en estatico/miniaturak/.")
    if fallos:
        print("\n".join(fallos))
        sys.exit(1)


if __name__ == "__main__":
    main()
