"""Carruseles para Instagram/Facebook de las fichas nuevas (sin servicios de pago).

Para cada ficha nueva crea en sare-sozialak/<fecha>-<id>/:
  1.png portada (título + Kimu) · 2.png y 3.png hojas de la ficha · 4.png «Doan: …» + QR
  testua.txt  texto de la publicación en euskera con 5 hashtags.
Las fichas ya tratadas se anotan en sare-sozialak/ikusiak.json. La primera vez (sin ese archivo)
solo cuentan como nuevas las programadas en los últimos 7 días; el resto se marca como vista.

Uso:  python scripts/sare_sozialak.py [--site _site] [--irteera sare-sozialak] [--max 5]
                                      [--gorputza issue.md] [--repo owner/repo]
Necesita la web generada (python scripts/build.py) y Playwright con Chromium.
"""
import argparse
import base64
import io
import json
import os
import re
import sys
from datetime import date, timedelta
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generar_pdf import RAIZ, fitxak_publicadas  # noqa: E402

URL = "https://keript.github.io/kimu-ikas-materialak/"
URL_CORTA = "keript.github.io/kimu-ikas-materialak"
HASHTAGS = "#euskara #lehenhezkuntza #NEAE #hezkuntza #kimu"
ANCHO, ALTO = 1080, 1350


def fitxa_berriak(fichas, ikusiak, hoy, lehen_aldia):
    """Fichas aún no tratadas; en la primera ejecución, solo las programadas la última semana."""
    limite = (date.fromisoformat(hoy) - timedelta(days=7)).isoformat()
    nuevas = []
    for f in fichas:
        if f["id"] in ikusiak or f.get("generado"):
            continue
        if lehen_aldia and f.get("publicar_desde", "") < limite:
            continue
        nuevas.append(f)
    return nuevas


def testua(f):
    """Texto de la publicación: título, resumen, enlace y 5 hashtags."""
    return (f'{f["icono"]} {f["nombre"]} {f.get("titulo_resalte", "")}'.strip() + f' · {f["curso"]}\n\n'
            f'{f["resumen"]}\n\n'
            f'Doakoa eta inprimatzeko prest: {URL}{f["id"]}.html\n\n{HASHTAGS}\n')


def _estilo(color="#8fd14f"):
    return (f"*{{box-sizing:border-box}}body{{margin:0;width:{ANCHO}px;height:{ALTO}px;display:flex;flex-direction:column;"
            f"align-items:center;justify-content:center;font-family:system-ui,'Segoe UI',Arial,sans-serif;color:#20241f;"
            f"background:linear-gradient(160deg,#fbfdf6 0%,#e9f5d8 100%);text-align:center;padding:70px;gap:34px}}"
            f".kimu{{height:520px}}.kimu svg{{height:100%;width:auto}}h1{{margin:0;font-size:84px;line-height:1.1}}"
            f"h1 span{{color:#3f7a22}}p{{margin:0;font-size:44px;line-height:1.3}}.etiq{{font-size:36px;font-weight:700;"
            f"background:{color};border-radius:999px;padding:10px 34px}}img.hoja{{max-width:960px;max-height:1230px;"
            f"box-shadow:0 12px 40px rgba(0,0,0,.2);border-radius:6px}}.qr svg{{width:300px;height:300px}}"
            f".url{{font-size:48px;font-weight:800;color:#3f7a22}}")


def _pagina(cuerpo):
    return f'<!doctype html><html lang="eu"><meta charset="utf-8"><style>{_estilo()}</style><body>{cuerpo}</body></html>'


def html_portada(f, kimu):
    return _pagina(f'<span class="etiq">{escape(f["curso"])} · {escape(f["tipo_material"])}</span>'
                   f'<div class="kimu">{kimu}</div>'
                   f'<h1>{escape(f["icono"])} {escape(f["nombre"])} <span>{escape(f.get("titulo_resalte", ""))}</span></h1>')


def html_hoja(png):
    return _pagina(f'<img class="hoja" alt="" src="data:image/png;base64,{base64.b64encode(png).decode()}">')


def html_resumen(f, kimu):
    return _pagina(f'<div class="kimu">{kimu}</div><p>{escape(f["resumen"])}</p>')


def html_final(f, qr_svg):
    return _pagina(f'<p>Doakoa eta inprimatzeko prest</p><div class="qr">{qr_svg}</div>'
                   f'<p>Doan:</p><p class="url">{URL_CORTA}</p>')


def qr_svg(url):
    import segno
    buf = io.BytesIO()
    segno.make(url, error="m").save(buf, kind="svg", scale=4, border=1, xmldecl=False, svgns=True, nl=False)
    return buf.getvalue().decode()


def crear_carrusel(nav, site, f, carpeta, kimu):
    carpeta.mkdir(parents=True, exist_ok=True)
    pg = nav.new_page(viewport={"width": 1400, "height": 1000}, device_scale_factor=1.5)
    pg.goto((site / f'{f["id"]}.html').as_uri())
    pg.wait_for_timeout(200)
    marcos = pg.query_selector_all(".hoja-marco:not(.oculta-impresion-alumno)")
    capturas = []
    for m in marcos[:2]:
        pg.evaluate("m => { m.style.zoom = 1; }", m)
        capturas.append(m.screenshot(type="png"))
    pg.close()

    portada = nav.new_page(viewport={"width": ANCHO, "height": ALTO})
    slides = [html_portada(f, kimu)] + [html_hoja(c) for c in capturas]
    if len(capturas) < 2:
        slides.append(html_resumen(f, kimu))
    slides.append(html_final(f, qr_svg(f'{URL}{f["id"]}.html')))
    for i, html in enumerate(slides, 1):
        portada.set_content(html)
        portada.screenshot(path=str(carpeta / f"{i}.png"))
    portada.close()
    (carpeta / "testua.txt").write_text(testua(f), encoding="utf-8")
    return len(slides)


def gorputza(repo, rama, lanak):
    """Cuerpo del issue «Argitaratzeko prest» con las imágenes enlazadas (raw.githubusercontent)."""
    base = f"https://raw.githubusercontent.com/{repo}/{rama}/sare-sozialak"
    partes = ["Argitaratzeko prest. Deskargatu irudiak eta kopiatu testua mugikorretik argitaratzeko.\n"]
    for f, carpeta in lanak:
        n = carpeta.name
        imgs = " ".join(f"![{f['nombre']} {i}]({base}/{n}/{i}.png)" for i in range(1, 5))
        partes.append(f"## {f['icono']} {f['nombre']}\n\n{imgs}\n\n```\n{testua(f)}```\n")
    return "\n".join(partes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="_site")
    ap.add_argument("--irteera", default="sare-sozialak")
    ap.add_argument("--max", type=int, default=5)
    ap.add_argument("--gorputza", default="")
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "keript/kimu-ikas-materialak"))
    ap.add_argument("--rama", default="main")
    args = ap.parse_args()
    site, irteera = Path(args.site).resolve(), Path(args.irteera).resolve()
    hoy = os.environ.get("KIMU_FECHA") or date.today().isoformat()
    irteera.mkdir(parents=True, exist_ok=True)
    ikusiak_ruta = irteera / "ikusiak.json"
    lehen_aldia = not ikusiak_ruta.exists()
    ikusiak = set(json.loads(ikusiak_ruta.read_text(encoding="utf-8"))) if not lehen_aldia else set()

    fichas = [f for f in fitxak_publicadas() if (site / f'{f["id"]}.html').is_file()]
    berriak = fitxa_berriak(fichas, ikusiak, hoy, lehen_aldia)[:args.max]
    if lehen_aldia:
        ikusiak |= {f["id"] for f in fichas}  # lo anterior ya estaba publicado
    kimu = (RAIZ / "estatico" / "kimu.svg").read_text(encoding="utf-8").strip()

    lanak = []
    if berriak:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            nav = p.chromium.launch()
            for f in berriak:
                carpeta = irteera / f'{hoy}-{f["id"]}'
                crear_carrusel(nav, site, f, carpeta, kimu)
                lanak.append((f, carpeta))
                print(f"  ✓ {carpeta.name}")
            nav.close()
    ikusiak |= {f["id"] for f, _ in lanak}
    ikusiak_ruta.write_text(json.dumps(sorted(ikusiak), indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"Sare sozialak: {len(lanak)} karrusel berri.")
    if args.gorputza and lanak:
        Path(args.gorputza).write_text(gorputza(args.repo, args.rama, lanak), encoding="utf-8")


if __name__ == "__main__":
    main()
