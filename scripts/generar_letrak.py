"""Generador de «Letraz letra» (LH 1 · Euskara): una colección fija por letra.

Por cada letra de LETRAK genera dos fichas (publicado: false, el autor las revisa):
  lh1-letra-<x>            Teoría: letra gigante (A a), 4 imágenes que empiezan por ella, cómo se traza y gogoratu.
  lh1-letra-<x>-ariketak   Ariketak (egokitua): inguratu, lotu irudia eta letra, trazatu y berrikusi. Con zuzenketa.
y la sección pack contenido/secciones/lh1-letrak.json.

Las palabras salen de contenido/irudiak/hiztegia-irudiak.json (grupo «lh1-<x>»).
Añadir una letra = añadir una línea a LETRAK (y sus trazos en TRAZOS de build.py si no los tiene).
Uso: python scripts/generar_letrak.py [--semilla N]
"""
import argparse
import json
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FITXAK = RAIZ / "contenido" / "fitxak"
SECCION = "lh1-letrak"
ARLOA = "lh1-euskara"
# letra -> color de la ficha. En el orden de clase; una línea más = una letra nueva.
LETRAK = {"a": "rojo", "e": "azul", "i": "verde", "o": "naranja", "u": "morado", "h": "turquesa"}


def hitzak_taldea():
    datos = json.loads((RAIZ / "contenido" / "irudiak" / "hiztegia-irudiak.json").read_text(encoding="utf-8"))
    return {g["id"]: list(g["hitzak"]) for g in datos["taldeak"] if g["id"].startswith("lh1-")}


def ficha(fid, nombre, resalte, icono, resumen, meta, color, hojas, lugar, orden, soluciones, tipo, relacionada):
    return {"id": fid, "arlo": ARLOA, "seccion": SECCION, "orden": orden, "publicado": False, "curso": "LH 1",
            "tipo_material": tipo, "nombre": nombre[:40], "titulo_resalte": resalte[:40], "icono": icono,
            "resumen": resumen[:140], "descripcion_meta": meta[:160], "color": color, "lugar": lugar,
            "soluciones": soluciones, "relacionada": relacionada, "hojas": hojas}


def teoria(x, color, hitzak, orden):
    X = x.upper()
    tarjetas = [{"titulo": "{" + h[0].upper() + "}" + h[1:], "imagen": h, "color": color} for h in hitzak]
    pausoak = [{"titulo": "Hasi", "texto": "Jarri arkatza 1 zenbakian."}, {"titulo": "Jarraitu", "texto": "Segi geziak zenbakiz zenbaki."},
               {"titulo": "Bukatu", "texto": "Altxatu arkatza eta errepikatu."}]
    ramak = [{"titulo": h.capitalize(), "texto": f"{X} letraz hasten da.", "imagen": h, "color": color, "ejemplos": [h]} for h in hitzak]
    hojas = [{"titulo": f"{X} LETRA", "subtitulo": "Begiratu, esan ozen eta trazatu.", "color": color, "tamano": "grande", "bloques": [
        {"tipo": "tarjetas", "columnas": 1, "items": [{"grande": f"{X} {x}", "color": color, "gigante": True, "imagen": "pencil"}]},
        {"tipo": "tarjetas", "columnas": 2, "items": tarjetas},
        {"tipo": "pasos", "columnas": 3, "items": pausoak},
        {"tipo": "trazatu", "letra": x, "lerroak": 1},
        {"tipo": "gogoratu", "texto": f"{hitzak[0].capitalize()}, {hitzak[1]}, {hitzak[2]} eta {hitzak[3]} {X} letraz hasten dira."},
    ]}, {"titulo": f"{X} LETRA: MAPA", "orientacion": "horizontal", "datos": False, "color": color, "bloques": [
        {"tipo": "mapa", "centro": {"titulo": f"{X} {x}", "texto": "Letra", "imagen": "pencil"}, "ramas": ramak}]}]
    return ficha(f"lh1-letra-{x}", f"Letra {X}", "ezagutu eta trazatu.", "🔤",
                 f"{X} letra: mayúscula y minúscula, 4 imágenes que empiezan por ella y cómo se traza.",
                 f"LH 1 · Euskara: {X} letra. Letra handia, lau irudi eta trazatzeko pauta.", color, hojas, "teoria", orden * 10 + 1,
                 False, "Gaiaren laburpena", f"lh1-letra-{x}-ariketak")


def ariketak(x, color, hitzak, besteak, orden, r):
    X = x.upper()
    # ⭕ inguratu: 4 filas de 4 letras; cada fila lleva 1-2 de la letra buscada y el resto distractores
    distraktoreak = [c for c in LETRAK if c != x]
    filas = []
    for _ in range(4):
        fila = [x] * r.choice([1, 2]) + [r.choice(distraktoreak) for _ in range(4)]
        fila = fila[:4]
        r.shuffle(fila)
        filas.append([c.upper() if r.random() < .3 else c for c in fila])
    inguratu_sol = [f"{i}. lerroa: {sum(c.lower() == x for c in f)} ({X}/{x})" for i, f in enumerate(filas, 1)]
    # 🔗 lotu: 1 imagen de la letra + 3 de otras; ejemplo resuelto en la primera
    otras = r.sample(distraktoreak, 3)
    irudiak = [(hitzak[0], x)] + [(besteak[o][0], o) for o in otras]
    der = [l for _, l in irudiak]
    r.shuffle(der)
    h1 = {"titulo": f"{X}: INGURATU ETA LOTU", "color": color, "egokitua": True, "bloques": [
        {"tipo": "ejercicio", "modo": "completar", "grande": True, "enunciado": f"⭕ Inguratu {x} ⭐", "ejemplo": f"b {x} c → ⭕ {x}",
         "frases": [" ".join(f) for f in filas], "solucion": inguratu_sol},
        {"tipo": "ejercicio", "modo": "relacionar", "grande": True, "enunciado": "🔗 Lotu irudia eta letra ⭐", "ejemplo": f"{hitzak[0]} → {x}",
         "izquierda": [f":{h}:" for h, _ in irudiak], "derecha": der,
         "solucion": [f"{i}. {l}" for i, (h, l) in enumerate(irudiak, 1)]},
    ]}
    # 👀 elegir: letra inicial de 3 imágenes; ✅ egia/gezurra con una pareja imagen-letra
    aukerak = []
    for h, l in irudiak[:3]:
        ops = [l] + r.sample([c for c in LETRAK if c != l], 2)
        r.shuffle(ops)
        aukerak.append({"texto": f":{h}:", "opciones": ops})
    vf = [(hitzak[1], x, True), (besteak[otras[0]][1], x, False), (hitzak[2], x, True), (besteak[otras[1]][1], x, False)]
    h2 = {"titulo": f"{X}: AUKERATU", "color": color, "egokitua": True, "bloques": [
        {"tipo": "ejercicio", "modo": "elegir", "enunciado": "👀 Aukeratu hasierako letra ⭐⭐", "ejemplo": f"{hitzak[0]} → {x}",
         "items": aukerak, "solucion": [l for _, l in irudiak[:3]]},
        {"tipo": "ejercicio", "modo": "verdadero_falso", "enunciado": "✅ Egia ala gezurra? ⭐⭐⭐", "ejemplo": f"{hitzak[0]} → {x}: egia",
         "items": [f":{h}: → {l}" for h, l, _ in vf], "solucion": ["Egia" if ok else "Gezurra" for _, _, ok in vf]},
    ]}
    h3 = {"titulo": f"{X}: TRAZATU", "color": color, "egokitua": True, "bloques": [
        {"tipo": "apartado", "color": color, "titulo": "✏️ Trazatu", "texto": "Jarraitu geziak, gero idatzi bakarrik.", "imagen": "pencil"},
        {"tipo": "trazatu", "letra": x, "lerroak": 1, "maiuskula": True},
        {"tipo": "trazatu", "letra": x, "lerroak": 2},
        {"tipo": "berrikusi", "items": ["Ezagutu dut", "Trazatu dut", "Irakurri dut"]},
    ]}
    return ficha(f"lh1-letra-{x}-ariketak", f"Letra {X} (ariketak)", "inguratu, lotu, trazatu.", "✏️",
                 f"{X} letra: inguratu, lotu, aukeratu, egia/gezurra, trazatu eta berrikusi. Zuzenketarekin.",
                 f"LH 1 · Euskara: {X} letra, ariketak: inguratu, lotu, aukeratu eta trazatu. Zuzenketarekin.", color, [h1, h2, h3], "actividades", orden * 10 + 2,
                 True, "Ariketa-fitxa", f"lh1-letra-{x}")


def seccion():
    return {"id": SECCION, "arlo": ARLOA, "tipo": "pack", "orden": 1, "icono": "🔤", "nombre": "Letraz letra",
            "tarjeta_arlo": {"texto": "Bokalak eta H: ezagutu, inguratu eta trazatu, letra banan-banan.", "boton": "Ikusi letrak"},
            "pagina": {"descripcion_meta": "LH 1 · Euskara: Letraz letra. Bokalak eta H: letra handia, irudiak, trazatzeko pauta eta ariketak.",
                       "titulo": "Letraz letra", "titulo_resalte": "letrak banan-banan.",
                       "intro": "Letra bakoitzean: teoria (irudiak eta trazua) eta ariketak (inguratu, lotu, trazatu)."}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semilla", type=int, default=2026)
    a = ap.parse_args()
    taldeak = hitzak_taldea()
    for x in LETRAK:
        if f"lh1-{x}" not in taldeak:
            sys.exit(f"Falta el grupo «lh1-{x}» en contenido/irudiak/hiztegia-irudiak.json")
    besteak = {x: taldeak[f"lh1-{x}"] for x in LETRAK}
    (RAIZ / "contenido" / "secciones" / f"{SECCION}.json").write_text(json.dumps(seccion(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for i, (x, color) in enumerate(LETRAK.items(), 1):
        r = random.Random(f"{a.semilla}-{x}")
        for f in (teoria(x, color, besteak[x], i), ariketak(x, color, besteak[x], besteak, i, r)):
            (FITXAK / f"{f['id']}.json").write_text(json.dumps(f, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f["id"])


if __name__ == "__main__":
    main()
