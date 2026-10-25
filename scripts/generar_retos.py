#!/usr/bin/env python3
"""Genera las tarjetas «Bukatu dut!» (para los que terminan antes) como fichas en contenido/fitxak/.

Cada tarjeta es una hoja A4 que cabe en una funda reutilizable. Hay 3 niveles (⭐, ⭐⭐, ⭐⭐⭐)
y la hoja de soluciones se añade sola al final.

Uso:
    python scripts/generar_retos.py            # genera/actualiza todos los packs
    python scripts/generar_retos.py --semilla 7  # otra tanda distinta de tarjetas

Las tarjetas salen siempre iguales con la misma semilla, así que se pueden regenerar sin miedo.
"""
from __future__ import annotations

import argparse
import json
import random
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FITXAK = RAIZ / "contenido" / "fitxak"
IRUDIAK = RAIZ / "estatico" / "irudiak"

NIVELES = ["⭐", "⭐⭐", "⭐⭐⭐"]
PIE = {"eu": "Funda batean sartu eta errotulagailu ezabagarriarekin idatzi.",
       "es": "Mételo en una funda y escribe con rotulador borrable."}


# ---------------------------------------------------------------- sudoku

def sudoku_completo(rng, bh, bw):
    n = bh * bw
    patron = lambda r, c: (bw * (r % bh) + r // bh + c) % n
    bandas = rng.sample(range(bw), bw)  # número de bandas = n / bh = bw
    filas = [b * bh + r for b in bandas for r in rng.sample(range(bh), bh)]
    pilas = rng.sample(range(bh), bh)  # número de pilas = n / bw = bh
    cols = [p * bw + c for p in pilas for c in rng.sample(range(bw), bw)]
    nums = rng.sample(range(1, n + 1), n)
    return [[nums[patron(r, c)] for c in cols] for r in filas]


def contar_soluciones(g, bh, bw, limite=2):
    n = bh * bw
    for r in range(n):
        for c in range(n):
            if not g[r][c]:
                total = 0
                for v in range(1, n + 1):
                    if valido(g, r, c, v, bh, bw):
                        g[r][c] = v
                        total += contar_soluciones(g, bh, bw, limite - total)
                        g[r][c] = 0
                        if total >= limite:
                            return total
                return total
    return 1


def valido(g, r, c, v, bh, bw):
    n = bh * bw
    if v in g[r] or any(g[i][c] == v for i in range(n)):
        return False
    r0, c0 = r - r % bh, c - c % bw
    return all(g[i][j] != v for i in range(r0, r0 + bh) for j in range(c0, c0 + bw))


def sudoku(rng, bh, bw, pistas):
    sol = sudoku_completo(rng, bh, bw)
    n = bh * bw
    g = [fila[:] for fila in sol]
    celdas = [(r, c) for r in range(n) for c in range(n)]
    rng.shuffle(celdas)
    quedan = n * n
    for r, c in celdas:
        if quedan <= pistas:
            break
        v, g[r][c] = g[r][c], 0
        if contar_soluciones([f[:] for f in g], bh, bw) != 1:
            g[r][c] = v
        else:
            quedan -= 1
    return g, sol


# ---------------------------------------------------------------- pirámide

def piramide(rng, nivel):
    filas_n, maximo = [(3, 9), (4, 9), (4, 12)][nivel]
    base = [rng.randint(1, maximo) for _ in range(filas_n)]
    filas = [base]
    while len(filas[-1]) > 1:
        a = filas[-1]
        filas.append([a[i] + a[i + 1] for i in range(len(a) - 1)])
    filas = filas[::-1]  # de arriba (1) a abajo
    huecos = [[False] * len(f) for f in filas]
    if nivel < 2:
        for r in range(len(filas) - 1):
            huecos[r] = [True] * len(filas[r])
        if nivel == 1:
            huecos[1][rng.randrange(2)] = False
    else:
        # faltan números de abajo: hay que restar
        for r in range(len(filas) - 1):
            huecos[r] = [True] * len(filas[r])
        huecos[0][0] = False
        abajo = len(filas) - 1
        for i in rng.sample(range(len(filas[abajo])), 2):
            huecos[abajo][i] = True
        for i in range(len(filas[abajo - 1])):
            if huecos[abajo][i] or huecos[abajo][i + 1]:
                huecos[abajo - 1][i] = False
        if not resoluble(filas, huecos):
            return piramide(rng, nivel)
    vista = [["" if huecos[r][i] else filas[r][i] for i in range(len(filas[r]))] for r in range(len(filas))]
    return vista, filas


def resoluble(filas, huecos):
    h = [f[:] for f in huecos]
    cambio = True
    while cambio:
        cambio = False
        for r in range(len(filas) - 1):
            for i in range(len(filas[r])):
                trio = [(r, i), (r + 1, i), (r + 1, i + 1)]
                faltan = [p for p in trio if h[p[0]][p[1]]]
                if len(faltan) == 1:
                    h[faltan[0][0]][faltan[0][1]] = False
                    cambio = True
    return not any(any(f) for f in h)


# ---------------------------------------------------------------- series

def serie(rng, nivel, idioma):
    if nivel == 0:
        paso = rng.choice([2, 5, 10]); ini = rng.randint(0, 20) * (1 if paso == 2 else paso // 5)
        vals = [ini + paso * i for i in range(7)]; regla = f"+{paso}"
    elif nivel == 1:
        paso = rng.choice([3, 4, -2, -5, -10])
        ini = rng.randint(60, 90) if paso < 0 else rng.randint(1, 20)
        vals = [ini + paso * i for i in range(7)]; regla = f"{paso:+d}"
    else:
        tipo = rng.choice(["grande", "doble", "alterna"])
        if tipo == "grande":
            paso = rng.choice([25, 50, 100]); ini = paso * rng.randint(0, 3)
            vals = [ini + paso * i for i in range(7)]; regla = f"+{paso}"
        elif tipo == "doble":
            ini = rng.choice([1, 2, 3]); vals = [ini * 2 ** i for i in range(7)]; regla = "×2"
        else:
            a, b = rng.choice([(3, 1), (5, 2), (10, 5)]); vals = [rng.randint(1, 10)]
            for i in range(6):
                vals.append(vals[-1] + (a if i % 2 == 0 else -b))
            regla = f"+{a}, −{b}"
    huecos = rng.sample(range(2, 7), 2 + (nivel > 0))
    return {"valores": ["" if i in huecos else v for i, v in enumerate(vals)], "solucion": vals,
            "pista": (f"Araua: {regla}" if idioma == "eu" else f"Regla: {regla}") if nivel == 0 else ""}


# ---------------------------------------------------------------- aurrekoa eta ondorengoa

def aurrekoa(rng, nivel):
    if nivel == 0:
        ns, d = rng.sample(range(2, 99), 6), 1
    elif nivel == 1:
        ns, d = rng.sample(range(101, 999), 6), 1
    else:
        ns, d = rng.sample(range(110, 990), 6), 10
    return [{"n": n, "antes": n - d, "despues": n + d} for n in ns], d


# ---------------------------------------------------------------- dados

def dados(rng, nivel):
    items = []
    for _ in range(5):
        if nivel == 0:
            c = [rng.randint(1, 6), rng.randint(1, 6)]; op = "+"; res = sum(c)
        elif nivel == 1:
            c = [rng.randint(1, 6) for _ in range(3)]; op = "+"; res = sum(c)
        else:
            c = sorted([rng.randint(1, 6), rng.randint(1, 6)], reverse=True); op = "−"; res = c[0] - c[1]
        items.append({"caras": c, "op": op, "resultado": res})
    return items


# ---------------------------------------------------------------- palabras

def sin_tildes(p):
    p = p.upper().replace("Ñ", "\x00")
    limpio = "".join(ch for ch in unicodedata.normalize("NFD", p) if unicodedata.category(ch) != "Mn")
    return unicodedata.normalize("NFC", limpio).replace("\x00", "Ñ").replace(" ", "")


VOCAB = {
    "eu": {
        "Animaliak": [("katua", "cat"), ("txakurra", "dog"), ("behia", "cow"), ("ahatea", "duck"), ("ardia", "ewe"), ("zaldia", "horse"),
                      ("txerria", "pig"), ("untxia", "rabbit"), ("igela", "frog"), ("hartza", "bear"), ("txoria", "bird"), ("oiloa", "chicken")],
        "Janaria": [("ogia", "bread"), ("arraina", "fish"), ("tomatea", "tomato"), ("arrautza", "egg"), ("gazta", "cheese-wedge"), ("esnea", "glass-of-milk"),
                    ("tipula", "onion"), ("gaileta", "cookie"), ("eztia", "honey-pot"), ("azenarioa", "carrot"), ("pizza", "pizza"), ("pastela", "birthday-cake")],
        "Udazkena": [("gaztaina", "chestnut"), ("hostoa", "maple-leaf"), ("onddoa", "mushroom"), ("aterkia", "umbrella"), ("trikua", "hedgehog"),
                     ("hontza", "owl"), ("kuia", "jack-o-lantern"), ("hodeia", "cloud"), ("urtxintxa", "chipmunk"), ("euria", "cloud-with-rain")],
        "Eskola": [("motxila", "backpack"), ("arkatza", "pencil"), ("liburua", "open-book"), ("eskola", "school"), ("guraizeak", "scissors"),
                   ("erregela", "straight-ruler"), ("koadernoa", "notebook"), ("erlojua", "alarm-clock"), ("kanpaia", "bell")],
        "Garraioak": [("autobusa", "bus"), ("bizikleta", "bicycle"), ("autoa", "automobile"), ("trena", "train"), ("hegazkina", "airplane"), ("itsasontzia", "ship")],
        "Fruitak": [("sagarra", "red-apple"), ("madaria", "pear"), ("marrubia", "strawberry"), ("mahatsa", "grapes"), ("limoia", "lemon"),
                    ("sandia", "watermelon"), ("gereziak", "cherries"), ("mertxika", "peach"), ("meloia", "melon"), ("platanoa", "banana")],
    },
    "es": {
        "Animales": [("gato", "cat"), ("perro", "dog"), ("vaca", "cow"), ("pato", "duck"), ("oveja", "ewe"), ("caballo", "horse"),
                     ("cerdo", "pig"), ("conejo", "rabbit"), ("rana", "frog"), ("oso", "bear"), ("pájaro", "bird"), ("gallina", "chicken")],
        "Comida": [("pan", "bread"), ("pescado", "fish"), ("tomate", "tomato"), ("huevo", "egg"), ("queso", "cheese-wedge"), ("leche", "glass-of-milk"),
                   ("cebolla", "onion"), ("galleta", "cookie"), ("miel", "honey-pot"), ("zanahoria", "carrot"), ("pizza", "pizza"), ("tarta", "birthday-cake")],
        "Otoño": [("castaña", "chestnut"), ("hoja", "maple-leaf"), ("seta", "mushroom"), ("paraguas", "umbrella"), ("erizo", "hedgehog"),
                  ("búho", "owl"), ("calabaza", "jack-o-lantern"), ("nube", "cloud"), ("ardilla", "chipmunk"), ("lluvia", "cloud-with-rain")],
        "Escuela": [("mochila", "backpack"), ("lápiz", "pencil"), ("libro", "open-book"), ("escuela", "school"), ("tijeras", "scissors"),
                    ("regla", "straight-ruler"), ("cuaderno", "notebook"), ("reloj", "alarm-clock"), ("campana", "bell")],
        "Transportes": [("autobús", "bus"), ("bicicleta", "bicycle"), ("coche", "automobile"), ("tren", "train"), ("avión", "airplane"), ("barco", "ship")],
        "Frutas": [("manzana", "red-apple"), ("pera", "pear"), ("fresa", "strawberry"), ("uvas", "grapes"), ("limón", "lemon"),
                   ("sandía", "watermelon"), ("cerezas", "cherries"), ("melocotón", "peach"), ("melón", "melon"), ("plátano", "banana")],
    },
}
ABC = {"eu": "ABDEFGHIJKLMNOPRSTUXZ", "es": "ABCDEFGHIJLMNOPRSTUVZ"}


def sopa(rng, palabras, tam, direcciones, idioma):
    for _ in range(400):
        g = [[None] * tam for _ in range(tam)]
        marcadas, ok = set(), True
        for texto, _img in sorted(palabras, key=lambda p: -len(p[0])):
            w = sin_tildes(texto)
            sitios = []
            for dr, dc in direcciones:
                for r in range(tam):
                    for c in range(tam):
                        er, ec = r + dr * (len(w) - 1), c + dc * (len(w) - 1)
                        if not (0 <= er < tam and 0 <= ec < tam):
                            continue
                        if all(g[r + dr * i][c + dc * i] in (None, w[i]) for i in range(len(w))):
                            sitios.append((r, c, dr, dc))
            if not sitios:
                ok = False
                break
            r, c, dr, dc = rng.choice(sitios)
            for i, ch in enumerate(w):
                g[r + dr * i][c + dc * i] = ch
                marcadas.add(f"{r + dr * i},{c + dc * i}")
        if ok:
            for r in range(tam):
                for c in range(tam):
                    g[r][c] = g[r][c] or rng.choice(ABC[idioma])
            return g, sorted(marcadas)
    raise RuntimeError("No caben las palabras en la sopa")


def crucigrama(rng, palabras):
    mejor = None
    for _ in range(200):
        orden = sorted(palabras, key=lambda p: -len(p[0]))
        orden = orden[:1] + rng.sample(orden[1:], len(orden) - 1)
        letras, colocadas = {}, []
        w0 = sin_tildes(orden[0][0])
        for i, ch in enumerate(w0):
            letras[(0, i)] = ch
        colocadas.append((orden[0], 0, 0, "h"))
        for p in orden[1:]:
            w = sin_tildes(p[0])
            opciones = []
            for (r, c), ch in list(letras.items()):
                for i, wc in enumerate(w):
                    if wc != ch:
                        continue
                    for d in ("h", "v"):
                        r0, c0 = (r, c - i) if d == "h" else (r - i, c)
                        if encaja(letras, w, r0, c0, d):
                            opciones.append((r0, c0, d))
            if not opciones:
                continue
            r0, c0, d = rng.choice(opciones)
            for i, ch in enumerate(w):
                letras[(r0, c0 + i) if d == "h" else (r0 + i, c0)] = ch
            colocadas.append((p, r0, c0, d))
        rs = [k[0] for k in letras]; cs = [k[1] for k in letras]
        alto, ancho = max(rs) - min(rs) + 1, max(cs) - min(cs) + 1
        puntos = len(colocadas) * 100 - alto * ancho - abs(alto - ancho) * 3
        if ancho <= 13 and alto <= 13 and (mejor is None or puntos > mejor[0]):
            mejor = (puntos, letras, colocadas, min(rs), min(cs), alto, ancho)
    _, letras, colocadas, mr, mc, alto, ancho = mejor
    inicios = sorted({(r - mr, c - mc) for _, r, c, _ in colocadas})
    numeros = {f"{r},{c}": i + 1 for i, (r, c) in enumerate(inicios)}
    pistas = [{"n": numeros[f"{r - mr},{c - mc}"], "dir": d, "imagen": p[1], "texto": p[2] if len(p) > 2 else None,
               "longitud": f"({len(sin_tildes(p[0]))})", "palabra": p[0]}
              for p, r, c, d in colocadas]
    pistas.sort(key=lambda x: (x["dir"], x["n"]))
    return {"ancho": ancho, "alto": alto, "letras": {f"{r - mr},{c - mc}": ch for (r, c), ch in letras.items()},
            "numeros": numeros, "pistas": pistas}


def encaja(letras, w, r0, c0, d):
    cruces = 0
    for i, ch in enumerate(w):
        r, c = (r0, c0 + i) if d == "h" else (r0 + i, c0)
        actual = letras.get((r, c))
        if actual is not None:
            if actual != ch:
                return False
            cruces += 1
            continue
        vecinos = [(r - 1, c), (r + 1, c)] if d == "h" else [(r, c - 1), (r, c + 1)]
        if any(v in letras for v in vecinos):
            return False
    antes = (r0, c0 - 1) if d == "h" else (r0 - 1, c0)
    despues = (r0, c0 + len(w)) if d == "h" else (r0 + len(w), c0)
    return cruces >= 1 and antes not in letras and despues not in letras


# ---------------------------------------------------------------- fichas

def ficha(id_, arlo, seccion, orden, nombre, resalte, icono, resumen, meta, color, hojas, idioma, desde=None):
    extra = {"publicar_desde": desde} if desde else {}
    return {**extra, "id": id_, "arlo": arlo, "seccion": seccion, "orden": orden, "publicado": True, "curso": "LH 3",
            "tipo_material": "Ariketa-fitxa", "nombre": nombre, "titulo_resalte": resalte, "icono": icono,
            "resumen": resumen, "descripcion_meta": meta, "color": color, "lugar": "actividades", "soluciones": True,
            "generado": True, "hojas": hojas}


def tarjeta(titulo, nivel, instruccion, reto, idioma, color=None):
    h = {"titulo": f"{titulo} {NIVELES[nivel]}", "subtitulo": instruccion, "datos": False,
         "bloques": [{"tipo": "reto", "reto": reto}, {"tipo": "nota", "texto": f"✏️ {PIE[idioma]}"}]}
    if color:
        h["color"] = color
    return h


def generar(semilla):
    rng = random.Random(semilla)
    fichas = []

    # --- Matematika
    hs = []
    simbolos = [["red-apple", "banana", "strawberry", "grapes"], ["cat", "dog", "rabbit", "duck"], ["sun", "star", "full-moon", "cloud"]]
    for k in range(2):
        g, s = sudoku(rng, 2, 2, 9)
        hs.append(tarjeta("SUDOKUA", 0, "Marraztu edo idatzi irudi bakoitza: errenkada, zutabe eta lauki bakoitzean, irudi bakoitza behin.",
                          {"tipo": "sudoku", "n": 4, "cajas": [2, 2], "celdas": g, "solucion_celdas": s, "simbolos": simbolos[k]}, "eu"))
    for k in range(2):
        g, s = sudoku(rng, 2, 2, 6)
        hs.append(tarjeta("SUDOKUA", 1, "Idatzi 1etik 4ra: errenkada, zutabe eta lauki bakoitzean, zenbaki bakoitza behin.",
                          {"tipo": "sudoku", "n": 4, "cajas": [2, 2], "celdas": g, "solucion_celdas": s}, "eu"))
    for k in range(2):
        g, s = sudoku(rng, 2, 3, 16)
        hs.append(tarjeta("SUDOKUA", 2, "Idatzi 1etik 6ra: errenkada, zutabe eta lauki bakoitzean, zenbaki bakoitza behin.",
                          {"tipo": "sudoku", "n": 6, "cajas": [2, 3], "celdas": g, "solucion_celdas": s}, "eu"))
    fichas.append(ficha("sudokuak", "matematika", "bukatu-dut-mate", 2, "Sudokuak", "irudiekin eta zenbakiekin.", "🧩",
                        "6 sudoku-txartel: irudiekin (4×4), zenbakiekin (4×4) eta 6×6. Fundan erabiltzeko. Zuzenketarekin.",
                        "Sudokuak LH 3rako, hiru mailatan, fundan eta errotulagailu ezabagarriarekin erabiltzeko.", "morado", hs, "eu"))

    hs = []
    for nivel in range(3):
        for _ in range(2):
            v, s = piramide(rng, nivel)
            instr = ["Batu ondoko bi zenbakiak eta idatzi emaitza goiko adreiluan.",
                     "Batu ondoko bi zenbakiak eta idatzi emaitza goiko adreiluan.",
                     "Batu goraka. Behean zenbakiren bat falta bada, egin kenketa!"][nivel]
            hs.append(tarjeta("PIRAMIDEA", nivel, instr, {"tipo": "piramide", "filas": v, "solucion_filas": s}, "eu"))
    fichas.append(ficha("piramideak", "matematika", "bukatu-dut-mate", 3, "Zenbaki-piramideak", "batu eta kendu.", "🔺",
                        "6 piramide-txartel hiru mailatan: goraka batu eta, azkenean, kenketak. Zuzenketarekin.",
                        "Zenbaki-piramideak LH 3rako, hiru mailatan, fundan erabiltzeko.", "naranja", hs, "eu"))

    hs = []
    for nivel in range(3):
        for _ in range(2):
            items = [serie(rng, nivel, "eu") for _ in range(4)]
            hs.append(tarjeta("SERIAZIOAK", nivel, "Aurkitu araua eta idatzi falta diren zenbakiak.", {"tipo": "series", "items": items}, "eu"))
    fichas.append(ficha("seriazioak", "matematika", "bukatu-dut-mate", 4, "Seriazioak", "aurkitu araua.", "🔢",
                        "6 txartel: +2, +5, +10, kenketak, ×2 eta serie alternoak. Zuzenketarekin.",
                        "Zenbaki-serieak LH 3rako, hiru mailatan, fundan erabiltzeko.", "azul", hs, "eu"))

    hs = []
    for nivel in range(3):
        for _ in range(2):
            items, d = aurrekoa(rng, nivel)
            instr = "Idatzi aurreko eta ondorengo zenbakia." if d == 1 else "Idatzi 10 gutxiago eta 10 gehiago."
            cab = ["Aurrekoa", "Zenbakia", "Ondorengoa"] if d == 1 else ["−10", "Zenbakia", "+10"]
            hs.append(tarjeta("AURREKOA ETA ONDORENGOA", nivel, instr, {"tipo": "aurrekoa", "items": items, "cab": cab}, "eu"))
    fichas.append(ficha("aurrekoa-ondorengoa", "matematika", "bukatu-dut-mate", 5, "Aurrekoa eta ondorengoa", "zenbakiak ordenan.", "↔️",
                        "6 txartel: 1-99, 100-999 eta ±10. Zuzenketarekin.",
                        "Aurrekoa eta ondorengoa LH 3rako, hiru mailatan, fundan erabiltzeko.", "verde", hs, "eu"))

    hs = []
    for nivel in range(3):
        for _ in range(2):
            instr = ["Zenbatu puntuak eta batu bi dadoak.", "Batu hiru dadoak.", "Kendu: handienari txikiena."][nivel]
            hs.append(tarjeta("DADOAK", nivel, instr, {"tipo": "dados", "items": dados(rng, nivel)}, "eu"))
    fichas.append(ficha("dadoak", "matematika", "bukatu-dut-mate", 6, "Dadoak", "batu eta kendu.", "🎲",
                        "6 txartel dadoekin: bi dado batu, hiru dado batu eta kendu. Zuzenketarekin.",
                        "Dadoekin gehiketak eta kenketak LH 3rako, fundan erabiltzeko.", "rojo", hs, "eu"))

    # --- Hizkuntzak: sopas y crucigramas
    for idioma, arlo, seccion, nom_sopa, nom_cruci in [("eu", "euskara", "bukatu-dut-euskara", "Hizki-zopak", "Gurutzegramak"),
                                                         ("es", "gaztelera", "ya-he-terminado", "Sopas de letras", "Crucigramas")]:
        temas = list(VOCAB[idioma].items())
        hs = []
        conf = [(0, 9, [(0, 1), (1, 0)], 6), (1, 11, [(0, 1), (1, 0)], 8), (2, 12, [(0, 1), (1, 0), (1, 1), (-1, 1)], 9)]
        for i, (nivel, tam, dirs, npal) in enumerate(c for c in conf for _ in range(2)):
            tema, pals = temas[i]
            pals = [p for p in rng.sample(pals, min(npal, len(pals))) if len(sin_tildes(p[0])) <= tam]
            g, marcadas = sopa(rng, pals, tam, dirs, idioma)
            reto = {"tipo": "sopa", "cuadricula": g, "marcadas": marcadas,
                    "palabras": [{"texto": sin_tildes(t), "imagen": im} for t, im in pals]}
            instr = {"eu": ["Bilatu hitzak: ezkerretik eskuinera eta goitik behera.", "Bilatu hitzak: ezkerretik eskuinera eta goitik behera.",
                            "Bilatu hitzak: zuzen, behera eta zeharka."],
                     "es": ["Busca las palabras: de izquierda a derecha y de arriba abajo.", "Busca las palabras: de izquierda a derecha y de arriba abajo.",
                            "Busca las palabras: en horizontal, vertical y diagonal."]}[idioma][nivel]
            hs.append(tarjeta(("HIZKI-ZOPA" if idioma == "eu" else "SOPA DE LETRAS") + f": {tema.upper()}", nivel, instr, reto, idioma))
        fichas.append(ficha("hizki-zopak" if idioma == "eu" else "sopas-de-letras", arlo, seccion, 2, nom_sopa,
                            "bilatu hitzak." if idioma == "eu" else "busca las palabras.", "🔎",
                            ("6 hizki-zopa irudiekin: animaliak, janaria, udazkena, eskola, garraioak eta fruitak. Zuzenketarekin." if idioma == "eu"
                             else "6 sopas de letras con dibujos: animales, comida, otoño, escuela, transportes y frutas. Con soluciones."),
                            ("Hizki-zopak LH 3rako, irudiekin eta hiru mailatan, fundan erabiltzeko." if idioma == "eu"
                             else "Sopas de letras para 3.º y 4.º de Primaria, con dibujos y tres niveles."), "turquesa", hs, idioma))
        hs = []
        for i in range(6):
            nivel = i // 2
            tema, pals = temas[i]
            n = [5, 6, 7][nivel]
            reto = crucigrama(rng, rng.sample(pals, min(n, len(pals))))
            reto["tipo"] = "gurutzegrama"
            instr = {"eu": "Begiratu irudiei eta idatzi bere izena. → ezkerretik eskuinera, ↓ goitik behera.",
                     "es": "Mira los dibujos y escribe su nombre. → de izquierda a derecha, ↓ de arriba abajo."}[idioma]
            hs.append(tarjeta(("GURUTZEGRAMA" if idioma == "eu" else "CRUCIGRAMA") + f": {tema.upper()}", nivel, instr, reto, idioma))
        fichas.append(ficha("gurutzegramak" if idioma == "eu" else "crucigramas", arlo, seccion, 3, nom_cruci,
                            "irudiekin." if idioma == "eu" else "con dibujos.", "✏️",
                            ("6 gurutzegrama, pistak irudiak dira: hitzak ikasi eta idatzi. Zuzenketarekin." if idioma == "eu"
                             else "6 crucigramas en los que las pistas son dibujos. Con soluciones."),
                            ("Gurutzegramak LH 3rako, irudiekin eta hiru mailatan." if idioma == "eu"
                             else "Crucigramas con dibujos para 3.º y 4.º de Primaria, tres niveles."), "verde", hs, idioma))
    return fichas


TEMAS = {
    "halloween": {
        "desde": None, "eu": "Halloween", "es": "Halloween", "color": "naranja", "icono": "🎃",
        "simbolos": [["jack-o-lantern", "ghost", "bat", "spider"], ["candy", "lollipop", "owl", "black-cat"]],
        "vocab": {"eu": [("kuia", "jack-o-lantern"), ("mamua", "ghost"), ("saguzarra", "bat"), ("armiarma", "spider"), ("amarauna", "spider-web"),
                         ("sorgina", "woman-mage"), ("erratza", "broom"), ("gozokiak", "candy"), ("piruleta", "lollipop"), ("kandela", "candle"),
                         ("hontza", "owl"), ("ilargia", "full-moon")],
                  "es": [("calabaza", "jack-o-lantern"), ("fantasma", "ghost"), ("murciélago", "bat"), ("araña", "spider"), ("telaraña", "spider-web"),
                         ("bruja", "woman-mage"), ("escoba", "broom"), ("caramelo", "candy"), ("piruleta", "lollipop"), ("vela", "candle"),
                         ("búho", "owl"), ("luna", "full-moon")]},
    },
    "gabonak": {
        "desde": "2026-12-10", "eu": "Gabonak", "es": "Navidad", "color": "rojo", "icono": "🎄",
        "simbolos": [["christmas-tree", "wrapped-gift", "star", "snowflake"], ["bell", "candle", "deer", "sled"]],
        "vocab": {"eu": [("zuhaitza", "christmas-tree"), ("oparia", "wrapped-gift"), ("izarra", "star"), ("elurra", "snowflake"), ("kanpaia", "bell"),
                         ("kandela", "candle"), ("txokolatea", "chocolate-bar"), ("eskularruak", "gloves"), ("lepokoa", "scarf"), ("oreina", "deer"),
                         ("lera", "sled"), ("gaztainak", "chestnut"), ("gaileta", "cookie"), ("xingola", "ribbon")],
                  "es": [("árbol", "christmas-tree"), ("regalo", "wrapped-gift"), ("estrella", "star"), ("nieve", "snowflake"), ("campana", "bell"),
                         ("vela", "candle"), ("chocolate", "chocolate-bar"), ("guantes", "gloves"), ("bufanda", "scarf"), ("reno", "deer"),
                         ("trineo", "sled"), ("castañas", "chestnut"), ("galleta", "cookie"), ("lazo", "ribbon")]},
    },
}


def generar_temas(semilla):
    fichas = []
    for clave, t in TEMAS.items():
        rng = random.Random(f"{semilla}-{clave}")
        hs = []
        for k in range(2):
            g, s = sudoku(rng, 2, 2, 9)
            hs.append(tarjeta(f"{t['eu'].upper()}: SUDOKUA", 0, "Marraztu edo idatzi irudi bakoitza: errenkada, zutabe eta lauki bakoitzean, irudi bakoitza behin.",
                              {"tipo": "sudoku", "n": 4, "cajas": [2, 2], "celdas": g, "solucion_celdas": s, "simbolos": t["simbolos"][k]}, "eu"))
        for k in range(2):
            g, s = sudoku(rng, 2, 2, 6)
            hs.append(tarjeta(f"{t['eu'].upper()}: SUDOKUA", 1, "Marraztu edo idatzi irudi bakoitza: errenkada, zutabe eta lauki bakoitzean, irudi bakoitza behin.",
                              {"tipo": "sudoku", "n": 4, "cajas": [2, 2], "celdas": g, "solucion_celdas": s, "simbolos": t["simbolos"][k]}, "eu"))
        for nivel in (0, 1):
            hs.append(tarjeta(f"{t['eu'].upper()}: DADOAK", nivel, ["Zenbatu puntuak eta batu bi dadoak.", "Batu hiru dadoak."][nivel],
                              {"tipo": "dados", "items": dados(rng, nivel)}, "eu"))
        fichas.append(ficha(f"{clave}-mate", "matematika", "bukatu-dut-mate", 1, f"{t['eu']}: sudokuak eta dadoak", "jai-giroan.", t["icono"],
                            f"{t['eu']}eko txartelak: irudi-sudokuak eta dadoak, bi mailatan. Zuzenketarekin.",
                            f"{t['eu']}eko sudokuak eta dadoak LH 3rako, fundan erabiltzeko.", t["color"], hs, "eu", t["desde"]))
        for idioma, arlo, seccion in [("eu", "euskara", "bukatu-dut-euskara"), ("es", "gaztelera", "ya-he-terminado")]:
            pals = t["vocab"][idioma]
            hs = []
            for nivel, tam, dirs, npal in [(0, 10, [(0, 1), (1, 0)], 7), (2, 12, [(0, 1), (1, 0), (1, 1), (-1, 1)], 10)]:
                elegidas = rng.sample(pals, npal)
                g, marcadas = sopa(rng, elegidas, tam, dirs, idioma)
                instr = {"eu": ["Bilatu hitzak: ezkerretik eskuinera eta goitik behera.", "", "Bilatu hitzak: zuzen, behera eta zeharka."],
                         "es": ["Busca las palabras: de izquierda a derecha y de arriba abajo.", "", "Busca las palabras: en horizontal, vertical y diagonal."]}[idioma][nivel]
                hs.append(tarjeta(("HIZKI-ZOPA" if idioma == "eu" else "SOPA DE LETRAS") + f": {t[idioma].upper()}", nivel, instr,
                                  {"tipo": "sopa", "cuadricula": g, "marcadas": marcadas,
                                   "palabras": [{"texto": sin_tildes(x), "imagen": im} for x, im in elegidas]}, idioma, t["color"]))
            for nivel, n in [(0, 5), (2, 7)]:
                reto = crucigrama(rng, rng.sample(pals, n)); reto["tipo"] = "gurutzegrama"
                instr = {"eu": "Begiratu irudiei eta idatzi bere izena. → ezkerretik eskuinera, ↓ goitik behera.",
                         "es": "Mira los dibujos y escribe su nombre. → de izquierda a derecha, ↓ de arriba abajo."}[idioma]
                hs.append(tarjeta(("GURUTZEGRAMA" if idioma == "eu" else "CRUCIGRAMA") + f": {t[idioma].upper()}", nivel, instr, reto, idioma, t["color"]))
            nombre = f"{t[idioma]}: " + ("hizki-zopak eta gurutzegramak" if idioma == "eu" else "sopas y crucigramas")
            fichas.append(ficha(f"{clave}-{'euskara' if idioma == 'eu' else 'castellano'}", arlo, seccion, 1, nombre,
                                "jai-giroan." if idioma == "eu" else "con dibujos.", t["icono"],
                                (f"{t['eu']}eko hiztegia: 2 hizki-zopa eta 2 gurutzegrama irudiekin. Zuzenketarekin." if idioma == "eu"
                                 else f"Vocabulario de {t['es']}: 2 sopas de letras y 2 crucigramas con dibujos. Con soluciones."),
                                (f"{t['eu']}eko hizki-zopak eta gurutzegramak LH 3rako, irudiekin." if idioma == "eu"
                                 else f"Sopas de letras y crucigramas de {t['es']} para 3.º y 4.º de Primaria."), t["color"], hs, idioma, t["desde"]))
    return fichas


def sopa_tarjeta(rng, titulo, nivel, pals, tam, dirs, idioma, color):
    g, marcadas = sopa(rng, [(p[0], p[1]) for p in pals], tam, dirs, idioma)
    instr = {"eu": ["Bilatu hitzak: ezkerretik eskuinera eta goitik behera.", "Bilatu hitzak: ezkerretik eskuinera eta goitik behera.",
                    "Bilatu hitzak: zuzen, behera eta zeharka."],
             "es": ["Busca las palabras: de izquierda a derecha y de arriba abajo.", "Busca las palabras: de izquierda a derecha y de arriba abajo.",
                    "Busca las palabras: en horizontal, vertical y diagonal."]}[idioma][nivel]
    return tarjeta(titulo, nivel, instr, {"tipo": "sopa", "cuadricula": g, "marcadas": marcadas,
                                          "palabras": [{"texto": sin_tildes(p[0]), "imagen": p[1]} for p in pals]}, idioma, color)


def cruci_tarjeta(rng, titulo, nivel, pals, idioma, color, asmakizunak=False):
    reto = crucigrama(rng, pals); reto["tipo"] = "gurutzegrama"
    if asmakizunak:
        instr = {"eu": "Irakurri asmakizunak eta idatzi erantzuna. → ezkerretik eskuinera, ↓ goitik behera.",
                 "es": "Lee las adivinanzas y escribe la respuesta. → de izquierda a derecha, ↓ de arriba abajo."}[idioma]
    else:
        instr = {"eu": "Begiratu irudiei eta idatzi bere izena. → ezkerretik eskuinera, ↓ goitik behera.",
                 "es": "Mira los dibujos y escribe su nombre. → de izquierda a derecha, ↓ de arriba abajo."}[idioma]
    return tarjeta(titulo, nivel, instr, reto, idioma, color)


EUSKARAREN_EGUNA = {
    "hiztegia": [("hizkuntza", "speech-balloon"), ("kanta", "musical-note"), ("liburua", "open-book"), ("gutuna", "envelope"),
                 ("eskola", "school"), ("jaia", "party-popper"), ("ipuina", "books"), ("bihotza", "yellow-heart"), ("mendia", "mountain"),
                 ("itsasoa", "water-wave"), ("herria", "houses"), ("lagunak", "handshake")],
    "lurraldeak": [("araba", None), ("bizkaia", None), ("gipuzkoa", None), ("nafarroa", None), ("lapurdi", None), ("zuberoa", None), ("euskara", None)],
    "hiriburuak": [("bilbo", None, "Bizkaiko hiriburua"), ("donostia", None, "Gipuzkoako hiriburua"), ("gasteiz", None, "Arabako hiriburua"),
                   ("iruñea", None, "Nafarroa Garaiko hiriburua"), ("baiona", None, "Lapurdiko hiriburua"), ("maule", None, "Zuberoako hiriburua")],
    "eguna": [("xabier", None, "Abenduaren 3an hil zen Frantzisko …"), ("arantzazu", None, "Euskara batuaren lehen urratsak eman ziren tokia"),
              ("euskalkia", None, "Tokian tokiko euskara egiteko modua"), ("euskalduna", None, "Euskaraz hitz egiten duen pertsona"),
              ("zazpi", None, "Zenbat lurraldetan hitz egiten da euskara?"), ("abendua", None, "Euskararen Eguna … hilabetean da"),
              ("batua", None, "Euskaldun guztiok idazteko euskara")],
}

HALLOWEEN_ASMAKIZUNAK = {
    "eu": [("saguzarra", None, "Gauez hegan egiten du eta buruz behera lo egiten du."), ("armiarma", None, "Zortzi hanka ditu eta sareak egiten ditu."),
           ("kuia", None, "Laranja da, eta barruan kandela bat jartzen diogu."), ("mamua", None, "Izara zuriz jantzita dago."),
           ("sorgina", None, "Erratzean hegan egiten du."), ("hontza", None, "Gauez esna dago eta begi handiak ditu."),
           ("ilargia", None, "Gauez zeruan argi egiten du.")],
    "es": [("murciélago", None, "Vuela de noche y duerme boca abajo."), ("araña", None, "Tiene ocho patas y teje telarañas."),
           ("calabaza", None, "Es naranja y le ponemos una vela dentro."), ("fantasma", None, "Va vestido con una sábana blanca."),
           ("bruja", None, "Vuela en una escoba."), ("búho", None, "Está despierto de noche y tiene los ojos grandes."),
           ("luna", None, "Brilla en el cielo por la noche.")],
}


def generar_extra(semilla):
    fichas = []
    rng = random.Random(f"{semilla}-euskararen-eguna")
    E = EUSKARAREN_EGUNA
    hs = [
        sopa_tarjeta(rng, "HIZKI-ZOPA: EUSKARA", 0, rng.sample(E["hiztegia"], 8), 10, [(0, 1), (1, 0)], "eu", "turquesa"),
        cruci_tarjeta(rng, "GURUTZEGRAMA: EUSKARA", 0, rng.sample(E["hiztegia"], 6), "eu", "turquesa"),
        sopa_tarjeta(rng, "HIZKI-ZOPA: HIRIBURUAK", 1, [(p[0], None) for p in E["hiriburuak"]], 10, [(0, 1), (1, 0)], "eu", "azul"),
        cruci_tarjeta(rng, "GURUTZEGRAMA: ABENDUAREN 3A", 1, E["eguna"], "eu", "azul", True),
        sopa_tarjeta(rng, "HIZKI-ZOPA: 7 LURRALDE", 2, E["lurraldeak"], 12, [(0, 1), (1, 0), (1, 1), (-1, 1)], "eu", "morado"),
        cruci_tarjeta(rng, "GURUTZEGRAMA: HIRIBURUAK", 2, E["hiriburuak"], "eu", "morado", True),
    ]
    fichas.append(ficha("euskararen-eguna-jolasak", "euskara", "euskararen-eguna", 4, "Hizki-zopak eta gurutzegramak",
                        "jolastu eta ikasi.", "🔎",
                        "6 txartel: euskararen hiztegia irudiekin, hiriburuak, zazpi lurraldeak eta abenduaren 3ko asmakizunak. Zuzenketarekin.",
                        "Euskararen Egunerako hizki-zopak eta gurutzegramak LH 3rako, fundan erabiltzeko.", "turquesa", hs, "eu"))
    for idioma, arlo, seccion, idf in [("eu", "euskara", "bukatu-dut-euskara", "euskara"), ("es", "gaztelera", "ya-he-terminado", "castellano")]:
        rng = random.Random(f"{semilla}-halloween-extra-{idioma}")
        vocab = TEMAS["halloween"]["vocab"][idioma]
        nom = "Halloween"
        hs = [
            sopa_tarjeta(rng, ("HIZKI-ZOPA" if idioma == "eu" else "SOPA DE LETRAS") + ": HALLOWEEN", 1, rng.sample(vocab, 8), 11, [(0, 1), (1, 0)], idioma, "naranja"),
            cruci_tarjeta(rng, ("GURUTZEGRAMA" if idioma == "eu" else "CRUCIGRAMA") + ": HALLOWEEN", 1, rng.sample(vocab, 6), idioma, "naranja"),
            cruci_tarjeta(rng, ("ASMAKIZUNAK" if idioma == "eu" else "ADIVINANZAS") + ": HALLOWEEN", 2, HALLOWEEN_ASMAKIZUNAK[idioma], idioma, "morado", True),
            sopa_tarjeta(rng, ("HIZKI-ZOPA" if idioma == "eu" else "SOPA DE LETRAS") + ": HALLOWEEN", 2, rng.sample(vocab, 10), 12,
                         [(0, 1), (1, 0), (1, 1), (-1, 1)], idioma, "morado"),
        ]
        fichas.append(ficha(f"halloween-{idf}-2", arlo, seccion, 1,
                            "Halloween (2): " + ("asmakizunak eta gehiago" if idioma == "eu" else "adivinanzas y más"),
                            "jai-giroan." if idioma == "eu" else "con dibujos.", "🦇",
                            ("4 txartel gehiago: hizki-zopak, gurutzegrama eta asmakizunen gurutzegrama. Zuzenketarekin." if idioma == "eu"
                             else "4 tarjetas más: sopas de letras, crucigrama y crucigrama de adivinanzas. Con soluciones."),
                            ("Halloweeneko txartel gehiago LH 3rako: hizki-zopak eta asmakizunak." if idioma == "eu"
                             else "Más tarjetas de Halloween para 3.º y 4.º: sopas de letras y adivinanzas."), "naranja", hs, idioma))
    return fichas


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--semilla", type=int, default=2026)
    args = ap.parse_args()
    for f in generar(args.semilla) + generar_temas(args.semilla) + generar_extra(args.semilla):
        for h in f["hojas"]:
            for b in h["bloques"]:
                r = b.get("reto", {})
                for img in ([p["imagen"] for p in r.get("palabras", []) if p["imagen"]] + [p["imagen"] for p in r.get("pistas", []) if p["imagen"]] + (r.get("simbolos") or [])):
                    assert (IRUDIAK / f"{img}.svg").is_file(), img
        (FITXAK / f"{f['id']}.json").write_text(json.dumps(f, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"✓ {f['id']}: {len(f['hojas'])} tarjetas")


if __name__ == "__main__":
    main()
