"""Genera los PDF de cada sección (alumno y con zuzenketa) a partir de la web ya generada.

Uso:  python scripts/generar_pdf.py [--site _site] [--cache .pdf-cache] [--solo id1,id2]
Salida: _site/pdf/<seccion>.pdf y _site/pdf/<seccion>-zuzenketa.pdf

Para no ralentizar la publicación, cada sección tiene un hash (fichas, sección, plantillas,
CSS y JS). Si no cambia, se reutilizan los PDF de la carpeta de caché (Actions la restaura).
Necesita:  pip install playwright && python -m playwright install --with-deps chromium
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CONTENIDO = RAIZ / "contenido"


def cargar(carpeta):
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted((CONTENIDO / carpeta).glob("*.json"))]


def fitxak_publicadas():
    """Fichas visibles hoy (publicadas y no programadas), en el mismo orden que la web."""
    hoy = os.environ.get("KIMU_FECHA") or date.today().isoformat()
    lista = [f for f in cargar("fitxak") if f.get("publicado") and f.get("publicar_desde", "") <= hoy]
    return sorted(lista, key=lambda f: (f["orden"], f.get("lugar") == "actividades"))


def fitxak_por_seccion():
    por = {}
    for f in fitxak_publicadas():
        por.setdefault(f["seccion"], []).append(f)
    return por


def hash_seccion(seccion, fichas):
    h = hashlib.sha1()
    h.update(json.dumps(seccion, sort_keys=True).encode())
    h.update(json.dumps(fichas, sort_keys=True).encode())
    for carpeta, patrones in ((RAIZ / "estatico", ("*.css", "*.js")), (RAIZ / "plantillas", ("*.html",)),
                              (RAIZ / "scripts", ("build.py", "generar_pdf.py"))):
        for patron in patrones:
            for ruta in sorted(carpeta.glob(patron)):
                h.update(ruta.read_bytes())
    return h.hexdigest()


def crear_pdf(nav, site, fichas, destino, con_soluciones):
    """Une las hojas de todas las fichas en una sola página y la imprime en A4."""
    pg = nav.new_page(viewport={"width": 1280, "height": 900})
    try:
        hojas = []
        for f in fichas:
            pg.goto((site / f'{f["id"]}.html').as_uri())
            hojas.append(pg.evaluate("() => document.querySelector('.hojas').innerHTML"))
        pg.goto((site / f'{fichas[0]["id"]}.html').as_uri())
        pg.evaluate("h => { document.querySelector('.hojas').innerHTML = h.join(''); }", hojas)
        pg.evaluate("""conSol => document.querySelectorAll('.hoja-marco').forEach(m => {
            m.classList.toggle('oculta-impresion', !conSol && m.classList.contains('oculta-impresion-alumno'));
            m.style.zoom = 1; })""", con_soluciones)
        pg.wait_for_load_state("load")
        pg.pdf(path=str(destino), format="A4", print_background=True, prefer_css_page_size=True)
    finally:
        pg.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="_site")
    ap.add_argument("--cache", default=".pdf-cache")
    ap.add_argument("--solo", default="")
    args = ap.parse_args()
    site, cache = Path(args.site).resolve(), Path(args.cache).resolve()
    solo = set(filter(None, args.solo.split(",")))
    salida = site / "pdf"
    salida.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    hashes_ruta = cache / "hashes.json"
    hashes = json.loads(hashes_ruta.read_text()) if hashes_ruta.exists() else {}

    por_seccion = fitxak_por_seccion()
    secciones = [s for s in cargar("secciones") if por_seccion.get(s["id"]) and (site / f'{s["id"]}.html').is_file()
                 and (not solo or s["id"] in solo)]
    pendientes = []
    for s in secciones:
        h = hash_seccion(s, por_seccion[s["id"]])
        nombres = (f'{s["id"]}.pdf', f'{s["id"]}-zuzenketa.pdf')
        if hashes.get(s["id"]) == h and all((cache / n).is_file() for n in nombres):
            for n in nombres:
                shutil.copy2(cache / n, salida / n)
        else:
            pendientes.append((s, h, nombres))
    print(f"PDF: {len(secciones) - len(pendientes)} sección(es) sin cambios (caché), {len(pendientes)} por generar.")
    if not pendientes:
        return

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        nav = p.chromium.launch()
        for s, h, nombres in pendientes:
            fichas = [f for f in por_seccion[s["id"]] if (site / f'{f["id"]}.html').is_file()]
            for nombre, con in zip(nombres, (False, True)):
                crear_pdf(nav, site, fichas, cache / nombre, con)
                shutil.copy2(cache / nombre, salida / nombre)
            hashes[s["id"]] = h
            hashes_ruta.write_text(json.dumps(hashes, indent=1), encoding="utf-8")
            print(f"  ✓ {s['id']}: {len(fichas)} ficha(s)")
        nav.close()


if __name__ == "__main__":
    sys.exit(main())
