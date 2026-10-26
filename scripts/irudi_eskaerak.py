"""Imágenes pendientes → un issue por grupo, con la orden para Gemini lista para copiar.

Iker genera la imagen 2×2 en Gemini (móvil u ordenador) y la sube como comentario en ese issue.
El workflow «Irudiak: jaso» la corta, crea los iconos, publica y cierra el issue. Sin Claude.

Uso (en GitHub Actions):  python scripts/irudi_eskaerak.py   (necesita GH_TOKEN)
"""
import json
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LISTA = RAIZ / "contenido" / "irudiak" / "hiztegia-irudiak.json"
FOTOS = RAIZ / "estatico" / "irudiak-errealak"
ETIQUETA = "irudia"


def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=False).stdout


def tiene_foto(id_):
    return any((FOTOS / f"{id_}{e}").is_file() for e in (".jpg", ".jpeg", ".png", ".webp"))


def main():
    gh("label", "create", ETIQUETA, "--color", "F9D0C4", "--description", "Imagen para generar en Gemini")
    abiertos = json.loads(gh("issue", "list", "--label", ETIQUETA, "--state", "open", "--json", "title,body", "--limit", "200") or "[]")
    ya = {b["body"].split("kimu-irudia:")[1].split(" ")[0] for b in abiertos if "kimu-irudia:" in b["body"]}
    for g in json.loads(LISTA.read_text(encoding="utf-8"))["taldeak"]:
        ids = list(g["hitzak"])
        if all(tiene_foto(i) for i in ids) or g["id"] in ya:
            continue
        n = len(ids)
        rejilla = "2×2 grid of four" if n == 4 else f"grid of {n}"
        orden = (f"A {rejilla} realistic photos, thin white space between them, no text, no letters, "
                 f"in this order (left to right, top to bottom): {g['edukia']}")
        cuerpo = (f"**Palabras** (en este orden): {', '.join(g['hitzak'].values())}\n\n"
                  f"### 1. Copia esto en Gemini\n```\n{orden}\n```\n"
                  f"### 2. Sube aquí la imagen como comentario (desde el móvil vale)\n"
                  f"GitHub la corta, crea los iconos, publica la web y cierra este issue solo.\n\n"
                  f"<!-- kimu-irudia:{g['id']} ids:{','.join(ids)} -->")
        print(gh("issue", "create", "--title", f"🖼️ Irudia: {g['izena']}", "--label", ETIQUETA, "--body", cuerpo).strip())


if __name__ == "__main__":
    main()
