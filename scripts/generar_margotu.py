"""Generador de «Margotu zenbakien arabera» (colorear por números con operaciones).

Lee `contenido/margotu/<id>.json` (dibujo en cuadrícula + reglas de operaciones) y escribe la ficha
`contenido/fitxak/<fitxa>.json` (hoja A4 + hoja de soluciones). El juego en pantalla sale solo al
construir la web (`python scripts/build.py`): bloque `margotu` → minijuego «Margotu».

Formato de `contenido/margotu/<id>.json`:
  fitxa, nivel (LH 1 / LH 2 / LH 3), arlo, seccion, orden, izena, icono, kolorea (color de la hoja),
  deskribapena, eragiketak, koloreak, marrazkia.
  eragiketak: {"batuketa": 10}            sumas con resultado ≤ 10
              {"kenketa": 20}             restas con minuendo ≤ 20
              {"biderketa": [2, 5, 10]}   tablas de multiplicar
              "eramanik_gabe": true       sin llevadas (sumas y restas hasta 100)
  koloreak:   [{"gakoa": "O", "izena": "laranja", "kolorea": "#ef8a1f", "marka": "●", "emaitza": 8}, …]
              (el resultado de cada color es único; el color se distingue también por nombre y marca)
  marrazkia:  filas de texto; cada letra es el `gakoa` de un color y «.» es una casilla vacía.

Uso:  python scripts/generar_margotu.py            # todos los dibujos
      python scripts/generar_margotu.py kuia etxea # solo algunos
Si el área (`arlo`) todavía no existe (p. ej. LH 2), el dibujo se salta: queda preparado.
"""
import json
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MARGOTU = RAIZ / "contenido" / "margotu"
FITXAK = RAIZ / "contenido" / "fitxak"
ARLOAK = RAIZ / "contenido" / "arloak"

ARGIBIDEA = "Egin eragiketa eta margotu laukia emaitzaren kolorearekin"
IZENBURUA = "MARGOTU ZENBAKIEN ARABERA"


def aukerak(emaitza, e):
    """Todas las operaciones («3+4») cuyo resultado es `emaitza` según las reglas `e`."""
    sin = e.get("eramanik_gabe", False)
    ops = []
    if "batuketa" in e and emaitza <= e["batuketa"]:
        for a in range(1, emaitza):
            b = emaitza - a
            if not sin or (a % 10 + b % 10 <= 9):
                ops.append(f"{a}+{b}")
    if "kenketa" in e:
        for a in range(emaitza + 1, e["kenketa"] + 1):
            b = a - emaitza
            if not sin or (a % 10 >= b % 10):
                ops.append(f"{a}−{b}")
    for t in e.get("biderketa", []):
        for b in range(2, 11):
            if t * b == emaitza:
                ops.append(f"{t}×{b}")
                if b != t:
                    ops.append(f"{b}×{t}")
    return ops


def cargar(ruta):
    d = json.loads(ruta.read_text(encoding="utf-8"))
    claves = {c["gakoa"]: c for c in d["koloreak"]}
    if len({c["emaitza"] for c in d["koloreak"]}) != len(d["koloreak"]):
        raise ValueError(f"{ruta.name}: dos colores con el mismo resultado")
    if len({len(f) for f in d["marrazkia"]}) != 1:
        raise ValueError(f"{ruta.name}: las filas del dibujo no miden lo mismo")
    for f in d["marrazkia"]:
        for ch in f:
            if ch != "." and ch not in claves:
                raise ValueError(f"{ruta.name}: la letra «{ch}» no está en `koloreak`")
    for c in d["koloreak"]:
        if not aukerak(c["emaitza"], d["eragiketak"]):
            raise ValueError(f"{ruta.name}: no hay operaciones con resultado {c['emaitza']}")
    return d, claves


def sortu_fitxa(d, claves):
    r = random.Random(f'margotu-{d["fitxa"]}')
    # una bolsa mezclada por color: las operaciones se repiten solo cuando se agotan
    poltsak = {k: [] for k in claves}
    filas = []
    for fila in d["marrazkia"]:
        zutabeak = []
        for ch in fila:
            if ch == ".":
                zutabeak.append(None)
                continue
            if not poltsak[ch]:
                poltsak[ch] = aukerak(claves[ch]["emaitza"], d["eragiketak"])
                r.shuffle(poltsak[ch])
            zutabeak.append({"op": poltsak[ch].pop(), "n": claves[ch]["emaitza"]})
        filas.append(zutabeak)
    leyenda = [{"n": c["emaitza"], "color": c["kolorea"], "nombre": c["izena"], "marka": c["marka"]} for c in d["koloreak"]]
    lh1 = d["nivel"] == "LH 1"
    bloque = {"tipo": "margotu", "filas": filas, "leyenda": leyenda}
    if lh1:
        bloque["grande"] = True
    hoja = {"titulo": IZENBURUA, "subtitulo": ARGIBIDEA, "bloques": [bloque]}
    if lh1:
        hoja["tamano"] = "grande"
    desk = d["deskribapena"]
    return {
        "id": d["fitxa"], "arlo": d["arlo"], "seccion": d["seccion"], "orden": d["orden"],
        "publicado": False, "curso": d["nivel"], "tipo_material": "Ariketa-fitxa",
        "nombre": f'Margotu: {d["izena"]}'[:40], "titulo_resalte": "eragiketak eta koloreak.",
        "icono": d["icono"], "resumen": f"{desk}. Egin eragiketak, margotu laukiak eta marrazkia agertuko da."[:140],
        "descripcion_meta": f'Margotu zenbakien arabera ({d["nivel"]}): {desk.lower()}. Fitxa inprimagarria eta pantailako jolasa.'[:160],
        "color": d["kolorea"], "lugar": "actividades", "soluciones": True, "generado": True, "hojas": [hoja],
    }


def main(argv):
    aukeratuak = set(argv)
    for ruta in sorted(MARGOTU.glob("*.json")):
        if aukeratuak and ruta.stem not in aukeratuak:
            continue
        d, claves = cargar(ruta)
        if not (ARLOAK / f'{d["arlo"]}.json').is_file():
            print(f'{ruta.stem}: «{d["arlo"]}» arloa ez dago oraindik ({d["nivel"]}). Prest dago, baina ez da fitxarik sortzen.')
            continue
        f = sortu_fitxa(d, claves)
        (FITXAK / f'{f["id"]}.json').write_text(json.dumps(f, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f'{ruta.stem} → {f["id"]}')


if __name__ == "__main__":
    main(sys.argv[1:])
