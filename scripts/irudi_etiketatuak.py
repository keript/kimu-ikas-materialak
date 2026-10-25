"""Genera ilustraciones etiquetadas a partir de imágenes reales (estatico/irudiak-errealak/).

Para cada imagen crea dos SVG en contenido/ilustraciones/:
  <id>.svg         → con los nombres en las etiquetas (teoría)
  <id>-hutsik.svg  → con casillas vacías numeradas (ariketak: etiketatu)
y devuelve en pantalla las soluciones (número → nombre) para la zuzenketa.

Uso: python scripts/irudi_etiketatuak.py
Para añadir una imagen nueva: guárdala en estatico/irudiak-errealak/ (fondo blanco,
sin texto) y añade su entrada en IRUDIAK con las coordenadas en píxeles de la imagen.
"""
from pathlib import Path
from xml.sax.saxutils import escape

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "contenido" / "ilustraciones"

# etiqueta: (texto, punto señalado x,y, lado "l"/"r"/"c", y de la caja [, x de la caja si lado "c"])
IRUDIAK = {
    "tomate-atalak": {
        "imagen": "tomate-landarea.jpg", "w": 1024, "h": 559,
        "aria": "Tomate-landarearen atalak: loreak, hostoak, zurtoina, sustraiak, fruituak eta haziak",
        "etiketak": [
            ("Loreak", (466, 140), "l", 95),
            ("Hostoak", (352, 185), "l", 205),
            ("Zurtoina", (514, 330), "l", 315),
            ("Sustraiak", (505, 455), "l", 440),
            ("Fruituak", (596, 230), "r", 150),
            ("Haziak", (545, 262), "r", 300),
        ],
    },
    "lorea-atalak-erreala": {
        "imagen": "lorea-ebakia.jpg", "w": 1024, "h": 559,
        "aria": "Lore baten atalak ebaketan: petaloak, estameak, sepaloak, pistiloa, polena eta obulutegia",
        "etiketak": [
            ("Petaloak", (300, 165), "l", 100),
            ("Estameak", (432, 215), "l", 230),
            ("Sepaloak", (372, 340), "l", 360),
            ("Pistiloa", (512, 112), "r", 70),
            ("Polena", (630, 195), "r", 200),
            ("Obulutegia", (520, 360), "r", 360),
        ],
    },
    "gosari-orekatua": {
        "imagen": "gosari-orekatua.jpg", "w": 1024, "h": 559,
        "aria": "Gosari orekatua: ogi integrala tomatearekin, oloa, sagarra, platanoa, esnea, ura eta jogurta",
        "etiketak": [
            ("Ogia", (230, 170), "c", 285, 230),
            ("Oloa", (568, 170), "c", 285, 568),
            ("Sagarra", (840, 110), "c", 30, 840),
            ("Platanoa", (900, 210), "c", 285, 900),
            ("Esnea", (137, 425), "c", 506, 137),
            ("Ura", (382, 425), "c", 506, 382),
            ("Jogurta", (640, 425), "c", 506, 640),
        ],
    },
    "hazia-ernetzen": {
        "imagen": "babarruna-ernetzen.jpg", "w": 1024, "h": 559,
        "aria": "Babarrun hazia ernetzen lau urratsetan: hazia lurrean, sustraia ateratzen, kimua eta landare gaztea",
        "etiketak": [
            ("1. Hazia", (143, 470), "c", 506, 143),
            ("2. Sustraia", (389, 470), "c", 506, 389),
            ("3. Kimua", (635, 470), "c", 506, 635),
            ("4. Landarea", (880, 470), "c", 506, 880),
        ],
    },
}

CAJA_W, CAJA_H, MARGEN = 200, 44, 24


def svg(id_, d, hutsik):
    w, h = d["w"], d["h"]
    partes = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{escape(d["aria"])}">',
              f'<image href="irudiak-errealak/{d["imagen"]}" x="0" y="0" width="{w}" height="{h}" style="mix-blend-mode: multiply"/>']
    for n, e in enumerate(d["etiketak"], 1):
        texto, (px, py), lado, cy = e[0], e[1], e[2], e[3]
        if lado == "l":
            bx = MARGEN; ax = bx + CAJA_W
        elif lado == "r":
            bx = w - MARGEN - CAJA_W; ax = bx
        else:
            cw = 150
            bx = e[4] - cw / 2; ax = e[4]
        cw = CAJA_W if lado in "lr" else 150
        ay = cy + CAJA_H / 2 if lado in "lr" else (cy if cy > py else cy + CAJA_H)
        if lado in "lr":
            partes.append(f'<path d="M{ax} {ay} L{px} {py}" stroke="#262b36" stroke-width="3" fill="none"/>'
                          f'<circle cx="{px}" cy="{py}" r="6" fill="#262b36"/>')
        partes.append(f'<rect x="{bx}" y="{cy}" width="{cw}" height="{CAJA_H}" rx="12" fill="#fff" stroke="#262b36" stroke-width="3"/>')
        if hutsik:
            partes.append(f'<circle cx="{bx + 2}" cy="{cy + 2}" r="16" fill="#ffd96a" stroke="#262b36" stroke-width="2.5"/>'
                          f'<text x="{bx + 2}" y="{cy + 9}" text-anchor="middle" font-family="Nunito, sans-serif" font-weight="900" font-size="20" fill="#262b36">{n}</text>')
        else:
            partes.append(f'<text x="{bx + cw / 2}" y="{cy + 30}" text-anchor="middle" font-family="Nunito, sans-serif" font-weight="900" font-size="25" fill="#262b36">{escape(texto)}</text>')
    partes.append("</svg>")
    return "".join(partes)


if __name__ == "__main__":
    for id_, d in IRUDIAK.items():
        (SALIDA / f"{id_}.svg").write_text(svg(id_, d, False), encoding="utf-8")
        (SALIDA / f"{id_}-hutsik.svg").write_text(svg(id_, d, True), encoding="utf-8")
        print(id_, "→", " · ".join(f"{n}. {e[0]}" for n, e in enumerate(d["etiketak"], 1)))
