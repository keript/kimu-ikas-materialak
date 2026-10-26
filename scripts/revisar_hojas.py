"""Revisión automática de la web generada (_site/), sin personas:
- ninguna hoja A4 se sale del papel,
- ninguna página de ficha o de juego da errores de JavaScript,
- los juegos se pueden empezar.

Uso:  python scripts/revisar_hojas.py [_site] [--solo id1,id2]
Sale con código 1 si encuentra problemas (así GitHub no fusiona ni publica algo roto).
Necesita:  pip install playwright && python -m playwright install --with-deps chromium
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

SITE = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "_site").resolve()
SOLO = None
if "--solo" in sys.argv:
    SOLO = set(sys.argv[sys.argv.index("--solo") + 1].split(","))

JS_DESBORDE = """() => [...document.querySelectorAll('article.hoja')].map((h, i) => {
  if (h.closest('.oculta-impresion')) return 0;
  const hb = h.getBoundingClientRect(); let over = 0;
  h.querySelectorAll('*').forEach(e => { const b = e.getBoundingClientRect();
    if (b.width && b.height) over = Math.max(over, b.bottom - hb.bottom, b.right - hb.right); });
  return Math.round(over);
})"""


def main():
    problemas = []
    paginas = sorted(SITE.glob("*.html"))
    with sync_playwright() as p:
        nav = p.chromium.launch()
        for ruta in paginas:
            base = ruta.stem.removesuffix("-jolasa")
            if SOLO and base not in SOLO:
                continue
            pg = nav.new_page(viewport={"width": 1280, "height": 900})
            errores = []
            pg.on("pageerror", lambda e: errores.append(str(e)[:140]))
            try:
                pg.goto(ruta.as_uri())
                pg.wait_for_timeout(150)
                if pg.query_selector("article.hoja"):
                    for i, over in enumerate(pg.evaluate(JS_DESBORDE), 1):
                        if over > 3:
                            problemas.append(f"{ruta.name}: la hoja {i} se sale del A4 ({over} px)")
                if ruta.stem.endswith("-jolasa"):
                    for modo in ("lotu", "sailkatu", "memoria"):
                        if pg.query_selector(f"[data-modo={modo}]"):
                            pg.click(f"[data-modo={modo}]", timeout=3000)
                            pg.click("#mini-atzera", timeout=3000)
                    if pg.is_visible("[data-modo=galderak]"):
                        pg.click("[data-modo=galderak]", timeout=3000)
                    if pg.is_visible("#jolasa-hasi"):
                        pg.click("#jolasa-hasi", timeout=3000)
            except Exception as e:  # noqa: BLE001
                problemas.append(f"{ruta.name}: no se pudo comprobar ({str(e)[:120]})")
            problemas += [f"{ruta.name}: error de JavaScript: {e}" for e in errores]
            pg.close()
        nav.close()
    if problemas:
        print("\n".join(problemas))
        print(f"\n✗ {len(problemas)} problema(s).")
        sys.exit(1)
    print(f"✓ Revisadas {len(paginas)} páginas: todo cabe en A4 y sin errores.")


if __name__ == "__main__":
    main()
