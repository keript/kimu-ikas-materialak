"""Fotos/ilustraciones realistas → iconos de ficha (estatico/irudiak/<id>.svg).

Las fichas usan imágenes por nombre ("imagen": "arbola" → estatico/irudiak/arbola.svg).
Este script mete cada foto de estatico/irudiak-errealak/<id>.jpg|png dentro de un SVG
(cuadrado, fondo blanco, esquinas redondeadas), para que se usen igual que los iconos.

Si la foto aún no existe, crea un marcador gris con la palabra («irudia laster»), así
Copilot puede preparar las fichas con los nombres definitivos antes de tener la imagen.

Uso:
  python scripts/foto_irudia.py                     # procesa contenido/irudiak/hiztegia-irudiak.json
  python scripts/foto_irudia.py --sareta FOTO.jpg arbola,aulkia,arraina,astoa
        # corta una imagen 2×2 (4 dibujos) en 4 fotos, en orden de lectura
"""
import argparse
import base64
import io
import json
from pathlib import Path

from PIL import Image, ImageChops

RAIZ = Path(__file__).resolve().parent.parent
FOTOS = RAIZ / "estatico" / "irudiak-errealak"
ICONOS = RAIZ / "estatico" / "irudiak"
LISTA = RAIZ / "contenido" / "irudiak" / "hiztegia-irudiak.json"
LADO = 360  # px del cuadrado final


def recortar_blanco(im: Image.Image, margen=0.06) -> Image.Image:
    """Quita el fondo blanco sobrante y deja un margen proporcional."""
    rgb = im.convert("RGB")
    fondo = Image.new("RGB", rgb.size, (255, 255, 255))
    diff = ImageChops.difference(rgb, fondo).convert("L").point(lambda v: 255 if v > 18 else 0)
    caja = diff.getbbox()
    if not caja:
        return rgb
    x0, y0, x1, y1 = caja
    m = int(max(x1 - x0, y1 - y0) * margen)
    return rgb.crop((max(0, x0 - m), max(0, y0 - m), min(rgb.width, x1 + m), min(rgb.height, y1 + m)))


def cuadrado(im: Image.Image) -> Image.Image:
    im = recortar_blanco(im)
    lado = max(im.size)
    lienzo = Image.new("RGB", (lado, lado), (255, 255, 255))
    lienzo.paste(im, ((lado - im.width) // 2, (lado - im.height) // 2))
    return lienzo.resize((LADO, LADO), Image.LANCZOS)


def svg_foto(id_: str, ruta: Path, alt: str) -> str:
    buf = io.BytesIO()
    cuadrado(Image.open(ruta)).save(buf, "JPEG", quality=82, optimize=True)
    datos = base64.b64encode(buf.getvalue()).decode()
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" role="img" aria-label="{alt}">'
            f'<defs><clipPath id="c"><rect width="120" height="120" rx="14"/></clipPath></defs>'
            f'<image clip-path="url(#c)" width="120" height="120" href="data:image/jpeg;base64,{datos}"/></svg>\n')


def svg_marcador(alt: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" role="img" aria-label="{alt}">'
            '<rect x="3" y="3" width="114" height="114" rx="14" fill="#f3f4f1" stroke="#9aa1ad" stroke-width="2" stroke-dasharray="6 5"/>'
            f'<text x="60" y="58" font-family="Nunito, sans-serif" font-size="16" font-weight="800" text-anchor="middle" fill="#55605a">{alt}</text>'
            '<text x="60" y="80" font-family="Nunito, sans-serif" font-size="11" text-anchor="middle" fill="#7a837d">irudia laster</text></svg>\n')


def foto_de(id_: str):
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        if (FOTOS / f"{id_}{ext}").is_file():
            return FOTOS / f"{id_}{ext}"
    return None


def sareta(ruta: Path, ids: list[str], columnas=2):
    im = Image.open(ruta).convert("RGB")
    filas = -(-len(ids) // columnas)
    w, h = im.width // columnas, im.height // filas
    for i, id_ in enumerate(ids):
        c, f = i % columnas, i // columnas
        m = int(min(w, h) * 0.015)  # deja fuera las líneas divisorias que a veces dibuja Gemini
        trozo = im.crop((c * w + m, f * h + m, (c + 1) * w - m, (f + 1) * h - m))
        trozo = recortar_blanco(trozo, margen=0.04)
        trozo.save(FOTOS / f"{id_}.jpg", "JPEG", quality=90)
        print(f"  {id_}.jpg")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sareta", nargs=2, metavar=("FOTO", "IDS"))
    a = ap.parse_args()
    if a.sareta:
        sareta(Path(a.sareta[0]), a.sareta[1].split(","))
    lista = json.loads(LISTA.read_text(encoding="utf-8"))
    hechas, marcadores = 0, 0
    for grupo in lista["taldeak"]:
        for id_, alt in grupo["hitzak"].items():
            foto = foto_de(id_)
            destino = ICONOS / f"{id_}.svg"
            if foto:
                destino.write_text(svg_foto(id_, foto, alt), encoding="utf-8")
                hechas += 1
            elif not destino.exists() or "irudia laster" in destino.read_text(encoding="utf-8"):
                destino.write_text(svg_marcador(alt), encoding="utf-8")
                marcadores += 1
    print(f"✓ {hechas} foto(s) convertida(s), {marcadores} marcador(es) «irudia laster».")


if __name__ == "__main__":
    main()
