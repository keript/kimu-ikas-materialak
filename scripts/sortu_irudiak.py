"""Genera con la API de Gemini las imágenes de contenido/irudiak/eskaerak.json que falten.

Se ejecuta en GitHub Actions (.github/workflows/irudiak.yml) con el secret GEMINI_API_KEY.
Guarda cada imagen como estatico/irudiak-errealak/<id>.jpg. Después hay que etiquetarla
(scripts/irudi_etiketatuak.py) mirando dónde está cada parte.
"""
import base64
import io
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
ESKAERAK = RAIZ / "contenido" / "irudiak" / "eskaerak.json"
SALIDA = RAIZ / "estatico" / "irudiak-errealak"

ESTILO = (
    "Realistic educational science illustration for 8-10 year old children, in the style of a modern school "
    "textbook: natural colors, clean outlines, soft shading, accurate and easy to recognise at first sight "
    "(suitable for pupils with special educational needs), centered subject, plain pure white background, "
    "generous empty space around the subject for labels. No text, no letters, no numbers, no labels, no arrows, "
    "no logos, no watermark. Subject: "
)
MODELOS = [m for m in os.environ.get("GEMINI_IMAGE_MODEL", "").split(",") if m] or [
    "gemini-3.1-flash-lite-image", "gemini-3.1-flash-image", "gemini-2.5-flash-image",
]


def generar(prompt, aspect, clave):
    cuerpo = json.dumps({
        "contents": [{"parts": [{"text": ESTILO + prompt}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"], "imageConfig": {"aspectRatio": aspect}},
    }).encode()
    ultimo = None
    for modelo in MODELOS:
        for version in ("v1beta", "v1"):
            url = f"https://generativelanguage.googleapis.com/{version}/models/{modelo}:generateContent"
            req = urllib.request.Request(url, data=cuerpo, headers={"x-goog-api-key": clave, "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    datos = json.load(r)
            except urllib.error.HTTPError as e:
                ultimo = f"{modelo} ({version}): HTTP {e.code} {e.read()[:300]!r}"
                print("  ·", ultimo); print(f"::warning::{ultimo}")
                continue
            for parte in datos.get("candidates", [{}])[0].get("content", {}).get("parts", []):
                if "inlineData" in parte and not parte.get("thought"):
                    print(f"  ✓ {modelo} ({version})")
                    return base64.b64decode(parte["inlineData"]["data"])
            ultimo = f"{modelo}: respuesta sin imagen"
            print("  ·", ultimo); print(f"::warning::{ultimo}")
    raise RuntimeError(ultimo)


def main():
    clave = os.environ.get("GEMINI_API_KEY")
    if not clave:
        print("Sin GEMINI_API_KEY: no se generan imágenes.")
        return 0
    eskaerak = json.loads(ESKAERAK.read_text(encoding="utf-8"))["irudiak"]
    SALIDA.mkdir(parents=True, exist_ok=True)
    fallos = 0
    for e in eskaerak:
        destino = SALIDA / f"{e['id']}.jpg"
        if destino.exists():
            continue
        print(f"Generando {e['id']}…")
        try:
            png = generar(e["prompt"], e.get("aspect", "16:9"), clave)
        except Exception as err:  # seguimos con las demás
            print(f"  ✗ {e['id']}: {err}"); print(f"::error::{e['id']}: {err}")
            fallos += 1
            continue
        img = Image.open(io.BytesIO(png)).convert("RGB")
        if img.width > 1600:
            img = img.resize((1600, round(img.height * 1600 / img.width)))
        img.save(destino, quality=88, optimize=True)
        print(f"  → {destino.relative_to(RAIZ)} {img.size}")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
