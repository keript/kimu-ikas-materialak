"""Generador de fichas de matemáticas por unidad (4 niveles + berrikusketa), con números
aleatorios, soluciones comprobadas y ejercicios originales.

Niveles por unidad:
  indartzeko  (⭐, egokitua: letra grande, ejemplo en cada ejercicio, menos ítems → NEAE)
  sendotzeko  (⭐⭐)
  sakontzeko  (⭐⭐⭐)
  berrikusketa (repaso mixto; incluye test y egia/gezurra → sale también en «Jolastu arbelean»)

Uso:
  python scripts/generar_mate.py                      # todas las unidades, versión A
  python scripts/generar_mate.py --unitatea 1.2 --bertsioa B
Cada versión usa otra semilla: mismos tipos de ejercicio, números distintos.
También se lanza desde GitHub (Actions → «Sortu mate fitxak»).
"""
import argparse
import json
import os
import random
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FITXAK = RAIZ / "contenido" / "fitxak"
SECCION = "unitateak-mate"

IZENAK = ["Ane", "Unai", "Irati", "Jon", "Aimar", "Nahia", "Oihan", "Izaro", "Markel", "Lucía", "Yassine", "Ibai", "Maialen", "Eneko"]
HERRIAK = ["Elantxobe", "Lekeitio", "Mundaka", "Bakio", "Orozko", "Zeanuri", "Dima", "Ubide", "Otxandio", "Aramaio", "Elorrio", "Zestoa"]

def erg(izena):
    """Ergatiboa: Ane → Anek, Oihan → Oihanek, Aimar → Aimarrek."""
    if izena[-1].lower() in "aeiouáéíóú":
        return izena + "k"
    return izena + ("rek" if izena.endswith("r") else "ek")


def gen(izena):
    """Genitiboa: Ane → Aneren, Oihan → Oihanen, Aimar → Aimarren."""
    if izena[-1].lower() in "aeiouáéíóú":
        return izena + "ren"
    return izena + ("ren" if izena.endswith("r") else "en")


# ------------------------------------------------------------------ euskarazko zenbakiak
_BAT = ["zero", "bat", "bi", "hiru", "lau", "bost", "sei", "zazpi", "zortzi", "bederatzi", "hamar", "hamaika", "hamabi",
        "hamahiru", "hamalau", "hamabost", "hamasei", "hamazazpi", "hemezortzi", "hemeretzi"]
_HOGEI = {20: "hogei", 40: "berrogei", 60: "hirurogei", 80: "laurogei"}
_EHUN = ["", "ehun", "berrehun", "hirurehun", "laurehun", "bostehun", "seiehun", "zazpiehun", "zortziehun", "bederatziehun"]


def _txiki(n):  # 1..99
    if n < 20:
        return _BAT[n]
    oina, hondarra = n // 20 * 20, n % 20
    return _HOGEI[oina] if hondarra == 0 else f"{_HOGEI[oina]}ta {_BAT[hondarra]}"


def hitzez(n):
    """1..9999 euskaraz: 2148 → «bi mila ehun eta berrogeita zortzi»."""
    if n == 0:
        return "zero"
    zatiak = []
    if n >= 1000:
        zatiak.append("mila" if n // 1000 == 1 else f"{_BAT[n // 1000]} mila")
    if n % 1000 >= 100:
        zatiak.append(_EHUN[n % 1000 // 100])
    if n % 100:
        zatiak.append(_txiki(n % 100))
    if len(zatiak) > 1:
        zatiak[-1] = "eta " + zatiak[-1]
    return " ".join(zatiak)


def z(n):
    """Formato con punto de millar (4.507). Hasta 9.999 se escribe con punto, como en clase."""
    return f"{n:,}".replace(",", ".")


def posizioa(n):
    d = [n // 1000, n // 100 % 10, n // 10 % 10, n % 10]
    letras = ["M", "E", "H", "B"]
    inicio = 0 if n >= 1000 else 1
    return " + ".join(f"{d[i]} {letras[i]}" for i in range(inicio, 4))


def balioa(n):
    d = [n // 1000 * 1000, n // 100 % 10 * 100, n // 10 % 10 * 10, n % 10]
    inicio = 0 if n >= 1000 else 1
    return " + ".join(z(x) for x in d[inicio:])


def biribildu(n, base):
    return (n + base // 2) // base * base


# ------------------------------------------------------------------ bloques
def ej(modo, enunciado, **kw):
    return {"tipo": "ejercicio", "modo": modo, "enunciado": enunciado, **kw}


def berrikusi(*items):
    return {"tipo": "berrikusi", "items": list(items)}


def gogoratu(texto):
    return {"tipo": "gogoratu", "texto": texto}


def hoja(titulo, subtitulo, bloques, **kw):
    return {"titulo": titulo, "subtitulo": subtitulo, "bloques": bloques, **kw}


CAB_DESK = [{"texto": "M", "color": "amarillo"}, {"texto": "E", "color": "verde"},
            {"texto": "H", "color": "rojo"}, {"texto": "B", "color": "azul"}]


# ------------------------------------------------------------------ 1.1 Zenbakiak 9.999 arte
def _num(r, lo, hi, distintos=None):
    while True:
        n = r.randint(lo, hi)
        if not distintos or n not in distintos:
            return n


def u11_hitzez(r, k, lo=1000, hi=9999, ejemplo=False):
    ns = sorted({_num(r, lo, hi) for _ in range(k * 3)}, key=lambda _: r.random())[:k]
    frases = [f"{z(n)} → _____" for n in ns]
    sol = [f"{z(n)} = {hitzez(n)}" for n in ns]
    if ejemplo:
        e = _num(r, lo, hi)
        frases.insert(0, f"_Adibidea:_ {z(e)} → **{hitzez(e)}**")
    return ej("completar", "Idatzi zenbakiak hitzez.", frases=frases, solucion=sol)


def u11_zifraz(r, k):
    ns = [_num(r, 1000, 9999) for _ in range(k)]
    return ej("completar", "Idatzi zenbakiak zifraz.", frases=[f"{hitzez(n).capitalize()} → [ ]" for n in ns],
              solucion=[z(n) for n in ns])


def u11_taula(r, k):
    """Tabla M E H B con unos datos dados y otros por completar."""
    filas, sol = [], []
    for i in range(k):
        n = _num(r, 1000, 9999)
        d = [str(n // 1000), str(n // 100 % 10), str(n // 10 % 10), str(n % 10)]
        if i % 2 == 0:
            filas.append([z(n), "", "", "", ""])
        else:
            filas.append(["", *d])
        sol.append(f"{z(n)} = {posizioa(n)}")
    return [ej("lineas", "Osatu taula: zenbakia eta bere zifrak (M, E, H, B).", lineas=0, solucion=sol),
            {"tipo": "tabla", "cabecera": ["Zenbakia", *CAB_DESK], "filas": filas}]


def u11_deskonposatu(r, k):
    ns = [_num(r, 1000, 9999) for _ in range(k)]
    frases = []
    for n in ns:
        frases.append(f"{z(n)} = ___ M + ___ E + ___ H + ___ B")
        frases.append(f"{z(n)} = ___ + ___ + ___ + ___")
    sol = [f"{z(n)} = {posizioa(n)} = {balioa(n)}" for n in ns]
    return ej("completar", "Deskonposatu bi modutan: posizioaren eta balioaren arabera.", frases=frases, solucion=sol)


def u11_balioa(r, k):
    items, sol = [], []
    for _ in range(k):
        n = _num(r, 1000, 9999)
        pos = r.choice([0, 1, 2])
        dig = int(str(n)[pos])
        if dig == 0:
            pos, dig = 0, int(str(n)[0])
        nombre = ["milakoen", "ehunekoen", "hamarrekoen"][pos]
        val = dig * [1000, 100, 10][pos]
        items.append(f"{z(n)} zenbakian, zer balio du {dig} zifrak?")
        sol.append(f"{z(val)} ({nombre} lekuan dago)")
    return ej("preguntas", "Erantzun.", items=items, lineas=1, solucion=sol)


def u11_alderatu(r, k):
    frases, sol = [], []
    for _ in range(k):
        a = _num(r, 1000, 9999)
        modo = r.choice(["swap", "near", "rand"])
        if modo == "swap":
            s = list(str(a)); i = r.choice([1, 2]); s[i], s[i + 1] = s[i + 1], s[i]; b = int("".join(s))
        elif modo == "near":
            b = a + r.choice([-100, -10, 10, 100, -1000, 1000])
        else:
            b = _num(r, 1000, 9999)
        if b == a or not 1000 <= b <= 9999:
            b = a + 9 if a < 9990 else a - 9
        frases.append(f"{z(a)} [ ] {z(b)}")
        sol.append(f"{z(a)} {'<' if a < b else '>'} {z(b)}")
    return ej("completar", "Alderatu. Idatzi < edo >.", frases=frases, solucion=sol, columnas=2)


def u11_ordenatu(r, k, handienetik=False):
    base = _num(r, 1000, 8000)
    ns = list({base + r.choice([0, 1, 10, 100, 1000, -1, -10, -100]) * r.randint(1, 3) for _ in range(k * 3)})[:k]
    while len(ns) < k:
        ns.append(_num(r, 1000, 9999, ns))
    r.shuffle(ns)
    orden = sorted(ns, reverse=handienetik)
    signo = " > " if handienetik else " < "
    txt = "handienetik txikienera" if handienetik else "txikienetik handienera"
    return ej("completar", f"Ordenatu {txt}: {' · '.join(z(n) for n in ns)}",
              frases=[signo.join(["___"] * k)], solucion=signo.join(z(n) for n in orden))


def u11_aurrekoa(r, k):
    ns = [_num(r, 1001, 9998) for _ in range(k)]
    if r.random() < .7:
        ns[0] = r.randint(1, 9) * 1000  # 3.000 → 2.999 / 3.001
    return [ej("lineas", "Idatzi aurrekoa eta ondorengoa.", lineas=0,
               solucion=[f"{z(n - 1)} · {z(n)} · {z(n + 1)}" for n in ns]),
            {"tipo": "tabla", "cabecera": ["Aurrekoa", "Zenbakia", "Ondorengoa"], "filas": [["", z(n), ""] for n in ns]}]


def u11_zuzena(r, pausoa, letras="ABC"):
    hasiera = {100: 0, 10: r.randint(1, 9) * 100, 1000: 0}[pausoa] if pausoa != 100 or r.random() < .5 else r.randint(1, 9) * 1000
    if pausoa == 100 and hasiera:
        pass
    puntos = r.sample(range(1, 10), len(letras))
    pts = [{"balioa": hasiera + i * pausoa, "letra": l} for i, l in zip(puntos, letras)]
    return [ej("lineas", f"Zer zenbaki daude zuzenean? (tarte bakoitza {z(pausoa)}ekoa da)", lineas=0,
               solucion=[f"{p['letra']} = {z(p['balioa'])}" for p in pts]),
            {"tipo": "zuzena", "hasiera": hasiera, "pausoa": pausoa, "zatiak": 10, "puntuak": pts}]


def u11_kokatu(r):
    hasiera = r.randint(1, 8) * 1000
    ns = sorted(r.sample(range(1, 10), 3))
    vals = [hasiera + i * 100 for i in ns]
    return [ej("lineas", f"Kokatu zuzenean: {', '.join(z(v) for v in vals)}. Marraztu puntu bat eta idatzi zenbakia gainean.", lineas=0,
               solucion=", ".join(f"{z(v)}: {i}. marran" for v, i in zip(vals, ns))),
            {"tipo": "zuzena", "hasiera": hasiera, "pausoa": 100, "zatiak": 10}]


def u11_biribildu(r, k):
    ns = [_num(r, 1000, 9999) for _ in range(k)]
    return [ej("lineas", "Biribildu hamarrekora (H) eta ehunekora (E). Gogoratu: 0–4 beherantz, 5–9 gorantz.", lineas=0,
               solucion=[f"{z(n)} → H: {z(biribildu(n, 10))} · E: {z(biribildu(n, 100))}" for n in ns]),
            {"tipo": "tabla", "cabecera": ["Zenbakia", {"texto": "Hamarrekora (H)", "color": "rojo"}, {"texto": "Ehunekora (E)", "color": "verde"}],
             "filas": [[z(n), "", ""] for n in ns]}]


def u11_herriak(r):
    herriak = r.sample(HERRIAK, 3)
    bizt = r.sample(range(1000, 9999), 3)
    izena = r.choice(IZENAK)
    txikiena = herriak[bizt.index(min(bizt))]
    obj = r.choice(range(3))
    n = bizt[obj]
    pos = r.choice([1, 2])
    dig = int(str(n)[pos])
    while dig == 0:
        obj = (obj + 1) % 3; n = bizt[obj]; dig = int(str(n)[pos])
    val = dig * [1000, 100, 10][pos]
    datos = " · ".join(f"**{h}**: {z(b)} biztanle" for h, b in zip(herriak, bizt))
    return ej("preguntas", f"Begiratu herrien biztanleak: {datos}.", lineas=1, items=[
        "Zein herritan bizi da jende gutxien?",
        f"{gen(izena)} herrian, {dig} zifraren balioa {z(val)} da. Zein herritan bizi da?",
        "Ordenatu herriak biztanle gehienetik gutxienera.",
    ], solucion=[txikiena, herriak[obj], " > ".join(h for _, h in sorted(zip(bizt, herriak), reverse=True))])


def u11_asmatu(r):
    n = _num(r, 1000, 9999)
    d = [int(c) for c in str(n)]
    pistak = [f"Lau zifrako zenbakia da.", f"Batekoen zifra {d[3]} da.",
              f"Ehunekoen zifra milakoena baino {'handiagoa' if d[1] > d[0] else 'txikiagoa' if d[1] < d[0] else 'berdina'} da.",
              f"Hamarrekoen zifra {d[2]} da.", f"Zifren batura {sum(d)} da.", f"{z(n - n % 1000)} eta {z(n - n % 1000 + 1000)} artean dago."]
    return ej("preguntas", "Zein zenbaki da? Irakurri pistak: " + " ".join(f"{i}) {p}" for i, p in enumerate(pistak, 1)),
              items=["Zenbakia:"], lineas=1, solucion=f"{z(n)} (beste zenbaki batzuk ere bete ditzakete pistak; egiaztatu)")


def u11_zifrak(r):
    ds = r.sample(range(0, 10), 4)
    if 0 not in ds and r.random() < .6:
        ds[r.randrange(4)] = 0
    handiena = int("".join(map(str, sorted(ds, reverse=True))))
    ord_ = sorted(ds)
    if ord_[0] == 0:
        primero = next(x for x in ord_ if x)
        ord_.remove(primero); ord_.insert(0, primero)
    txikiena = int("".join(map(str, ord_)))
    return ej("preguntas", f"Erabili zifra hauek behin bakarrik: **{' · '.join(map(str, ds))}**.", lineas=1,
              items=["Idatzi ahalik eta zenbaki handiena.", "Idatzi ahalik eta zenbaki txikiena (lau zifrakoa).", "Zenbat da bien arteko kenketa?"],
              solucion=[z(handiena), z(txikiena), z(handiena - txikiena)])


def u11_test(r, k):
    items, vf, solvf = [], [], []
    sol = []
    for _ in range(k):
        n = _num(r, 1000, 9999)
        malos = set()
        while len(malos) < 2:
            m = n + r.choice([-1000, 1000, -100, 100, -90, 90, -9, 9])
            if 1000 <= m <= 9999 and m != n:
                malos.add(m)
        ops = [z(n)] + [z(m) for m in malos]
        r.shuffle(ops)
        items.append({"texto": f"{hitzez(n).capitalize()}", "opciones": ops})
        sol.append(z(n))
    for _ in range(4):
        n = _num(r, 1000, 9999)
        if r.random() < .5:
            vf.append(f"{z(n)} = {posizioa(n)}"); solvf.append("Egia")
        else:
            m = n + r.choice([10, 100, -10, -100])
            vf.append(f"{z(n)} = {posizioa(m)}"); solvf.append("Gezurra")
    return [ej("elegir", "Inguratu zenbaki zuzena.", items=items, solucion=sol),
            ej("verdadero_falso", "Egia ala gezurra?", items=vf, solucion=solvf)]


def unitatea_1_1(r):
    ind = [
        hoja("IRAKURRI ETA IDATZI", "Zenbakiak 9.999 arte. Begiratu adibidea eta egin ariketak.", [
            gogoratu("2.148 = **2 M + 1 E + 4 H + 8 B** = 2.000 + 100 + 40 + 8 → _bi mila ehun eta berrogeita zortzi_"),
            u11_hitzez(r, 3, ejemplo=True), *u11_taula(r, 3), u11_alderatu(r, 4)], tamano="grande"),
        hoja("ZUZENA ETA ORDENA", "Begiratu tarteak: zenbat egiten du jauzi bakoitzak?", [
            *u11_zuzena(r, 100, "AB"), *u11_aurrekoa(r, 3), u11_ordenatu(r, 4),
            berrikusi("Zenbakiak hitzez idatzi ditut", "M, E, H eta B ondo jarri ditut", "Zuzena irakurri dut", "Ordenatu eta egiaztatu dut")], tamano="grande"),
    ]
    send = [
        hoja("IDATZI ETA DESKONPOSATU", "⭐⭐ Zenbakiak 9.999 arte.", [u11_hitzez(r, 4), u11_zifraz(r, 2), u11_deskonposatu(r, 2), u11_balioa(r, 2), u11_alderatu(r, 4)]),
        hoja("ZUZENA ETA BIRIBILDU", "⭐⭐ Kokatu, alderatu eta biribildu.", [
            *u11_zuzena(r, 10), *u11_biribildu(r, 3), u11_herriak(r),
            berrikusi("Tarteen balioa begiratu dut", "0–4 beherantz, 5–9 gorantz", "Erantzunak egiaztatu ditut")]),
    ]
    sak = [
        hoja("ERRONKAK ZENBAKIEKIN", "⭐⭐⭐ Pentsatu, probatu eta egiaztatu.", [
            u11_kokatu(r)[0], u11_kokatu(r)[1], u11_zifrak(r), u11_asmatu(r), *u11_zuzena(r, 1000 if r.random() < .3 else 100, "ABC")]),
        hoja("BIRIBILDU ETA ARRAZOITU", "⭐⭐⭐ Azaldu nola egin duzun.", [
            *u11_biribildu(r, 4), u11_herriak(r), u11_ordenatu(r, 4, handienetik=True),
            ej("lineas", "Idatzi ehunekora biribiltzean 4.500 ematen duten bi zenbaki. Azaldu zergatik.", lineas=2,
               solucion="Adibidez: 4.460 eta 4.549 (4.450 eta 4.549 artekoak)."),
            berrikusi("Pistak banan-banan egiaztatu ditut", "Nire arrazoiak idatzi ditut")]),
    ]
    berr = [
        hoja("BERRIKUSKETA (1)", "Zenbakiak 9.999 arte: errepasoa.", [*u11_test(r, 4), u11_deskonposatu(r, 1), u11_alderatu(r, 4)]),
        hoja("BERRIKUSKETA (2)", "Zenbakiak 9.999 arte: errepasoa.", [
            *u11_zuzena(r, 100, "ABC"), *u11_biribildu(r, 3), u11_herriak(r),
            berrikusi("Badakit zenbakiak irakurtzen eta idazten", "Badakit deskonposatzen", "Badakit alderatzen eta biribiltzen")]),
    ]
    return "Zenbakiak 9.999 arte", [ind, send, sak, berr]


# ------------------------------------------------------------------ 1.2 Gehiketak eta kenketak
def _gehiketa(r, cifras, eramanekin=True):
    lo, hi = 10 ** (cifras - 1), 10 ** cifras - 1
    while True:
        a, b = r.randint(lo, hi), r.randint(lo // 2 if cifras > 3 else lo, hi)
        if a + b > 9999:
            continue
        lleva = any((a // 10 ** i % 10) + (b // 10 ** i % 10) >= 10 for i in range(cifras))
        if lleva == eramanekin:
            return a, b


def _kenketa(r, cifras, eramanekin=True):
    lo, hi = 10 ** (cifras - 1), 10 ** cifras - 1
    while True:
        a, b = sorted([r.randint(lo, hi), r.randint(lo, hi)], reverse=True)
        if a == b:
            continue
        lleva = any((a // 10 ** i % 10) < (b // 10 ** i % 10) for i in range(cifras))
        if lleva == eramanekin:
            return a, b


def u12_ops(r, tipo, cifras, k):
    cab = ["", "M", "E", "H", "B"][-(cifras + 1):] if cifras < 4 else ["", "M", "E", "H", "B"]
    if cifras < 4:
        cab = [""] + ["M", "E", "H", "B"][-cifras:]
    items, sol = [], []
    for i in range(k):
        a, b = (_gehiketa if tipo == "+" else _kenketa)(r, cifras)
        items.append({"a": str(a), "b": str(b), "op": "+" if tipo == "+" else "−"})
        sol.append(f"{'abcdefgh'[i]}) {z(a + b if tipo == '+' else a - b)}")
    verbo = "gehiketak" if tipo == "+" else "kenketak"
    return ej("operaciones", f"Egin {verbo} taulan. Ez ahaztu eramandakoak!", items=items, cab=cab, columnas=4, solucion=sol)


def u12_egiaztatu(r, k):
    frases, sol = [], []
    for _ in range(k):
        a, b = _kenketa(r, 4 if r.random() < .5 else 3)
        frases.append(f"{z(a)} − {z(b)} = ___ → egiaztatu: ___ + {z(b)} = ___")
        sol.append(f"{z(a)} − {z(b)} = {z(a - b)} → {z(a - b)} + {z(b)} = {z(a)}")
    return ej("completar", "Kalkulatu kenketa eta egiaztatu gehiketa eginez.", frases=frases, solucion=sol)


def u12_falta(r, k):
    frases, sol = [], []
    for _ in range(k):
        a, b = _gehiketa(r, r.choice([3, 4]))
        s = a + b
        forma = r.choice(["a+_=s", "_+b=s", "s-_=a", "_-b=a"])
        if forma == "a+_=s":
            frases.append(f"{z(a)} + [ ] = {z(s)}"); sol.append(z(b))
        elif forma == "_+b=s":
            frases.append(f"[ ] + {z(b)} = {z(s)}"); sol.append(z(a))
        elif forma == "s-_=a":
            frases.append(f"{z(s)} − [ ] = {z(a)}"); sol.append(z(b))
        else:
            frases.append(f"[ ] − {z(b)} = {z(a)}"); sol.append(z(s))
    return ej("completar", "Osatu falta den zenbakia.", frases=frases, solucion=sol, columnas=2)


def u12_kromoak(r):
    izenak = r.sample(IZENAK, 4)
    k = r.sample(range(310, 890), 4)
    a, b = izenak[0], izenak[1]
    return ej("preguntas", "Kromo-bildumak: " + " · ".join(f"**{i}**: {n}" for i, n in zip(izenak, k)) + ". Idatzi eragiketa eta erantzuna.",
              lineas=2, items=[f"Zenbat kromo dituzte {erg(a)} eta {erg(b)} guztira?",
                                f"{erg(izenak[2])} {erg(izenak[3])} baino zenbat {'gehiago' if k[2] > k[3] else 'gutxiago'} ditu?",
                                "Zenbat kromo dituzte lauren artean?"],
              solucion=[f"{k[0]} + {k[1]} = {k[0] + k[1]}", f"{max(k[2], k[3])} − {min(k[2], k[3])} = {abs(k[2] - k[3])}", f"{sum(k)} kromo"])


def u12_buruketa(r):
    izena = r.choice(IZENAK)
    tipo = r.choice(["puxtarri", "lasterketa", "liburuak", "txirrindu"])
    if tipo == "puxtarri":
        t = r.randint(700, 999); a = r.randint(250, t - 200)
        return ej("preguntas", f"{erg(izena)} {t} puxtarri ditu. {a} urdinak dira eta gainerakoak gorriak.", lineas=2,
                  items=["Zenbat puxtarri gorri ditu?", "Zein kolorekoak dira gehienak?"],
                  solucion=[f"{t} − {a} = {t - a}", "Urdinak" if a > t - a else "Gorriak"])
    if tipo == "lasterketa":
        tot = r.randint(4000, 9000); hecho = r.randint(1200, tot - 800)
        return ej("preguntas", f"Lasterketa solidarioa {z(tot)} metrokoa da. {erg(izena)} {z(hecho)} metro egin ditu.", lineas=2,
                  items=["Zenbat metro falta zaizkio helmugara iristeko?"], solucion=f"{z(tot)} − {z(hecho)} = {z(tot - hecho)} metro")
    if tipo == "liburuak":
        a, b = r.randint(1200, 3900), r.randint(800, 2900)
        return ej("preguntas", f"Liburutegian {z(a)} liburu zeuden. Aurten {z(b)} liburu berri erosi dituzte.", lineas=2,
                  items=["Zenbat liburu daude orain?"], solucion=f"{z(a)} + {z(b)} = {z(a + b)} liburu")
    a, b, c = r.randint(300, 500), r.randint(20, 60), r.randint(150, 320)
    return ej("preguntas", f"Txirrindularitza-lasterketan {a} haurrek eman zuten izena. Azken egunean {b} gehiago animatu ziren.", lineas=2,
              items=["Zenbat haur zeuden lasterketa hasi zenean?", f"{c} haur iritsi dira helmugara. Zenbat falta dira?"],
              solucion=[f"{a} + {b} = {a + b}", f"{a + b} − {c} = {a + b - c}"])


def u12_bi_urrats(r):
    izena = r.choice(IZENAK)
    a, b, c = r.randint(1200, 2500), r.randint(900, 2000), r.randint(1500, 3000)
    tot = a + b
    return ej("preguntas", f"{erg(izena)} bizikletan {z(a)} metro egin ditu goizean eta {z(b)} metro arratsaldean. Bere arrebak {z(c)} metro egin ditu egun osoan.",
              lineas=2, items=[f"Zenbat metro egin ditu {erg(izena)} guztira?", "Nork egin ditu metro gehiago? Zenbat gehiago?"],
              solucion=[f"{z(a)} + {z(b)} = {z(tot)} m", f"{izena if tot > c else 'Arrebak'}: {z(max(tot, c))} − {z(min(tot, c))} = {z(abs(tot - c))} m"])


def u12_propietateak(r):
    a, b, c = r.randint(15, 95), r.randint(5, 45), r.randint(10, 85)
    items = [{"texto": f"{a} + {b} = {b} + {a}", "opciones": ["trukatze-propietatea", "elkartze-propietatea"]},
             {"texto": f"({a} + {b}) + {c} = {a} + ({b} + {c})", "opciones": ["trukatze-propietatea", "elkartze-propietatea"]}]
    return ej("elegir", "Zein propietate da? Inguratu.", items=items, solucion=["trukatze-propietatea", "elkartze-propietatea"])


def u12_hiru(r, k):
    frases, sol = [], []
    for _ in range(k):
        a, b, c = r.randint(1000, 4000), r.randint(100, 999), r.randint(100, 3000)
        frases.append(f"{z(a)} + {z(b)} + {z(c)} = ___")
        sol.append(z(a + b + c))
    return ej("completar", "Batu hiru zenbaki. Lehenik, bilatu errazen batzen direnak.", frases=frases, solucion=sol)


def u12_test(r):
    items, sol = [], []
    for _ in range(3):
        a, b = _gehiketa(r, 3)
        bien = a + b
        ops = [z(bien), z(bien + 10), z(bien - 100)]
        r.shuffle(ops)
        items.append({"texto": f"{a} + {b}", "opciones": ops}); sol.append(z(bien))
    vf, solvf = [], []
    for _ in range(4):
        a, b = _kenketa(r, 3)
        if r.random() < .5:
            vf.append(f"{a} − {b} = {a - b}"); solvf.append("Egia")
        else:
            vf.append(f"{a} − {b} = {a - b + 10}"); solvf.append("Gezurra")
    return [ej("elegir", "Inguratu emaitza zuzena.", items=items, solucion=sol),
            ej("verdadero_falso", "Egia ala gezurra?", items=vf, solucion=solvf)]


def unitatea_1_2(r):
    ind = [
        hoja("GEHIKETAK", "Hiru zifrako zenbakiak. Begiratu adibidea.", [
            gogoratu("Hasi **B** zutabetik. 10 edo gehiago bada, idatzi batekoa eta **eraman 1** hurrengo zutabera."),
            u12_ops(r, "+", 3, 4), u12_buruketa(r), u12_buruketa(r)], tamano="grande"),
        hoja("KENKETAK", "Hiru zifrako zenbakiak. Begiratu adibidea.", [
            gogoratu("Goiko zifra txikiagoa bada, **hartu 1** ezkerreko zutabetik: 10 gehiago dituzu."),
            u12_ops(r, "−", 3, 4), u12_egiaztatu(r, 3), u12_buruketa(r),
            berrikusi("B zutabetik hasi naiz", "Eramandakoak idatzi ditut", "Kenketa egiaztatu dut")], tamano="grande"),
    ]
    send = [
        hoja("GEHITU ETA KENDU", "⭐⭐ Lau zifrako zenbakiak.", [u12_ops(r, "+", 4, 4), u12_ops(r, "−", 4, 4), u12_falta(r, 4), u12_egiaztatu(r, 2)]),
        hoja("BURUKETAK", "⭐⭐ Irakurri, pentsatu eta kalkulatu.", [u12_kromoak(r), u12_buruketa(r),
                                                                   berrikusi("Datuak azpimarratu ditut", "Eragiketa idatzi dut", "Erantzuna esaldi osoz idatzi dut")]),
    ]
    sak = [
        hoja("KALKULU ERRONKAK", "⭐⭐⭐ Pentsatu bide onena.", [u12_hiru(r, 4), u12_propietateak(r), u12_falta(r, 6), u12_ops(r, "−", 4, 4)]),
        hoja("BI URRATSEKO BURUKETAK", "⭐⭐⭐ Lehenik zer kalkulatu behar duzun pentsatu.", [
            u12_bi_urrats(r), u12_bi_urrats(r),
            ej("lineas", "Asmatu zuk buruketa bat 4.250 − 1.375 eragiketarekin. Idatzi eta ebatzi.", lineas=3,
               solucion="Erantzun irekia. Emaitza: 4.250 − 1.375 = 2.875."),
            berrikusi("Urratsak ordenan egin ditut", "Emaitza zentzuzkoa den begiratu dut")]),
    ]
    berr = [
        hoja("BERRIKUSKETA (1)", "Gehiketak eta kenketak: errepasoa.", [*u12_test(r), u12_ops(r, "+", 4, 4)]),
        hoja("BERRIKUSKETA (2)", "Gehiketak eta kenketak: errepasoa.", [u12_ops(r, "−", 4, 4), u12_falta(r, 4), u12_buruketa(r),
                                                                         berrikusi("Badakit eramanekin batzen", "Badakit eramanekin kentzen", "Badakit buruketak ebazten")]),
    ]
    return "Gehiketak eta kenketak", [ind, send, sak, berr]


# ------------------------------------------------------------------ 1.3 Biderketak
OBJ = ["red-apple", "star", "pencil", "soccer-ball", "strawberry", "cookie", "carrot", "butterfly"]


def u13_multzoak(r, k):
    """Irudiak: multzoak → batuketa eta biderketa."""
    frases, sol = [], []
    for _ in range(k):
        m, n, ob = r.randint(2, 4), r.randint(2, 5), r.choice(OBJ)
        talde = "  ·  ".join(" ".join(f":{ob}:" for _ in range(n)) for _ in range(m))
        frases.append(f"{talde}\n" + " + ".join(["[ ]"] * m) + " = [ ]  →  [ ] × [ ] = [ ]")
        sol.append(f"{' + '.join([str(n)] * m)} = {m} × {n} = {m * n}")
    return ej("completar", "Zenbat multzo daude? Zenbat bakoitzean? Idatzi batuketa eta biderketa.", frases=frases, solucion=sol)


def u13_marraztu(r):
    m, n = r.randint(2, 4), r.randint(3, 5)
    return {"tipo": "dibujo", "alto": 42, "texto": f"⭐ Marraztu {m} multzo; multzo bakoitzean {n} izar. Idatzi biderketa: [ ] × [ ] = [ ]"}


def u13_batuketatik(r, k):
    frases, sol = [], []
    for _ in range(k):
        m, n = r.randint(2, 6), r.randint(2, 9)
        frases.append(f"{' + '.join([str(n)] * m)} = [ ] × [ ] = ___")
        sol.append(f"{m} × {n} = {m * n}")
    return ej("completar", "Idatzi biderketa gisa eta kalkulatu.", frases=frases, solucion=sol)


def u13_biderketatik(r, k):
    frases, sol = [], []
    for _ in range(k):
        m, n = r.randint(2, 5), r.randint(2, 9)
        frases.append(f"{m} × {n} = ___ = ___")
        sol.append(f"{m} × {n} = {' + '.join([str(n)] * m)} = {m * n}")
    return ej("completar", "Idatzi batuketa gisa eta kalkulatu.", frases=frases, solucion=sol)


def u13_gaiak(r):
    m, n = r.randint(2, 9), r.randint(2, 9)
    return ej("completar", f"Begiratu: **{m} × {n} = {m * n}**. Idatzi gai bakoitzaren izena.",
              frases=[f"{m} eta {n} → ___", f"{m * n} → ___"], solucion=["biderkagaiak", "biderkadura"])


def u13_taula(r, k):
    tablas = r.sample(range(2, 11), k)
    filas, sol = [], []
    for t in tablas:
        ocultos = set(r.sample(range(1, 11), 5))
        filas.append([f"× {t}"] + ["" if i in ocultos else str(i * t) for i in range(1, 11)])
        sol.append(f"{t}ren taula: " + ", ".join(str(i * t) for i in range(1, 11)))
    return [ej("lineas", "Osatu biderketa-taulak.", lineas=0, solucion=sol),
            {"tipo": "tabla", "cabecera": ["", *[f"× {i}" for i in range(1, 11)]], "filas": filas}]


def u13_kalkulatu(r, k):
    frases, sol = [], []
    for _ in range(k):
        m, n = r.randint(2, 10), r.randint(2, 10)
        frases.append(f"{m} × {n} = [ ]"); sol.append(str(m * n))
    return ej("completar", "Kalkulatu buruz.", frases=frases, solucion=sol, columnas=3)


def u13_falta(r, k):
    frases, sol = [], []
    for _ in range(k):
        m, n = r.randint(2, 10), r.randint(2, 10)
        if r.random() < .5:
            frases.append(f"[ ] × {n} = {m * n}"); sol.append(str(m))
        else:
            frases.append(f"{m} × [ ] = {m * n}"); sol.append(str(n))
    return ej("completar", "Zein da falta den biderkagaia?", frases=frases, solucion=sol, columnas=3)


def u13_propietateak(r):
    a, b, c = r.randint(2, 9), r.randint(2, 9), r.randint(2, 5)
    return [ej("completar", "Trukatzea: biderkagaien ordenak ez du biderkadura aldatzen. Osatu.",
               frases=[f"{a} × {b} = {b} × [ ] = [ ]", f"{c} × {a} = [ ] × {c} = [ ]"], solucion=[f"{a}; {a * b}", f"{a}; {a * c}"]),
            ej("completar", "Elkartzea: berdin dio zein biderkatzen dugun lehenik. Kalkulatu bi modutan.",
               frases=[f"({a} × {c}) × 2 = [ ] × 2 = [ ]", f"{a} × ({c} × 2) = {a} × [ ] = [ ]"],
               solucion=[f"{a * c} × 2 = {a * c * 2}", f"{a} × {c * 2} = {a * c * 2}"])]


def u13_ops(r, k):
    items, sol = [], []
    for i in range(k):
        a, b = r.randint(12, 49), r.randint(2, 5)
        items.append({"a": str(a), "b": str(b), "op": "×"}); sol.append(f"{'abcdefgh'[i]}) {a * b}")
    return ej("operaciones", "Biderkatu taulan. Hasi B zutabetik eta ez ahaztu eramandakoa.", items=items, cab=["", "E", "H", "B"], columnas=4, solucion=sol)


def u13_buruketa(r):
    izena = r.choice(IZENAK)
    tipo = r.choice(["kaxak", "mahaiak", "astea", "pegatinak"])
    if tipo == "kaxak":
        k, n = r.randint(3, 9), r.choice([6, 8, 10, 12])
        return ej("preguntas", f"{erg(izena)} {k} kaxa ditu. Kaxa bakoitzean {n} arrautza daude.", lineas=2,
                  items=["Zenbat arrautza daude guztira? Idatzi biderketa."], solucion=f"{k} × {n} = {k * n} arrautza")
    if tipo == "mahaiak":
        k, n = r.randint(4, 9), r.choice([4, 5, 6])
        return ej("preguntas", f"Jangelan {k} mahai daude eta mahai bakoitzean {n} ikasle esertzen dira.", lineas=2,
                  items=["Zenbat ikasle eser daitezke?"], solucion=f"{k} × {n} = {k * n} ikasle")
    if tipo == "astea":
        n = r.randint(2, 9)
        return ej("preguntas", f"{erg(izena)} {n} orri irakurtzen ditu egunero.", lineas=2,
                  items=["Zenbat orri irakurtzen ditu astebetean (7 egun)?"], solucion=f"7 × {n} = {7 * n} orri")
    k, n, d = r.randint(3, 8), r.randint(5, 9), r.randint(5, 15)
    return ej("preguntas", f"{erg(izena)} {k} orri ditu pegatinekin. Orri bakoitzean {n} pegatina daude. {d} oparitu ditu.", lineas=2,
              items=["Zenbat pegatina zituen hasieran?", "Zenbat geratzen zaizkio?"], solucion=[f"{k} × {n} = {k * n}", f"{k * n} − {d} = {k * n - d}"])


def u13_test(r):
    items, sol = [], []
    for _ in range(3):
        m, n = r.randint(2, 9), r.randint(2, 9)
        ops = list({m * n, m * n + m, m + n})
        while len(ops) < 3:
            ops.append(m * n + n + 1)
        r.shuffle(ops)
        items.append({"texto": f"{m} × {n}", "opciones": [str(o) for o in ops]}); sol.append(str(m * n))
    vf, svf = [], []
    for _ in range(4):
        m, n = r.randint(2, 9), r.randint(2, 9)
        tipo = r.choice(["ok", "mal", "suma"])
        if tipo == "ok":
            vf.append(f"{m} × {n} = {n} × {m}"); svf.append("Egia")
        elif tipo == "mal":
            vf.append(f"{m} × {n} = {m * n + 1}"); svf.append("Gezurra")
        else:
            vf.append(f"{' + '.join([str(n)] * m)} = {m} × {n}"); svf.append("Egia")
    return [ej("elegir", "Inguratu biderkadura zuzena.", items=items, solucion=sol),
            ej("verdadero_falso", "Egia ala gezurra?", items=vf, solucion=svf)]


def unitatea_1_3(r):
    ind = [
        hoja("BIDERKETA ZER DA?", "Zenbaki berdinen batuketa. Begiratu adibidea.", [
            gogoratu("**3 aldiz 5** = 5 + 5 + 5 = **3 × 5 = 15**. 3 eta 5 **biderkagaiak** dira; 15 **biderkadura**."),
            u13_multzoak(r, 3), u13_batuketatik(r, 3), u13_marraztu(r)], tamano="grande"),
        hoja("BIDERKATU", "Lasai, pausoz pauso.", [u13_biderketatik(r, 2), u13_gaiak(r), u13_kalkulatu(r, 6),
                                                  berrikusi("Multzoak zenbatu ditut", "Batuketa eta biderketa idatzi ditut", "Biderkagaiak eta biderkadura bereizten ditut")], tamano="grande"),
    ]
    send = [
        hoja("BIDERKETA-TAULAK", "⭐⭐ Taulak eta buruzko kalkulua.", [*u13_taula(r, 4), u13_kalkulatu(r, 6), u13_falta(r, 6)]),
        hoja("PROPIETATEAK ETA BURUKETAK", "⭐⭐ Trukatzea, elkartzea eta buruketak.", [*u13_propietateak(r), u13_buruketa(r), u13_buruketa(r),
                                                                                      berrikusi("Taulak errepasatu ditut", "Propietateak erabili ditut", "Erantzuna esaldi osoz idatzi dut")]),
    ]
    sak = [
        hoja("BIDERKATU TAULAN", "⭐⭐⭐ Bi zifrako zenbakiak bider zifra bat.", [u13_ops(r, 8), u13_falta(r, 6), *u13_taula(r, 2)]),
        hoja("ERRONKAK", "⭐⭐⭐ Pentsatu eta arrazoitu.", [
            u13_propietateak(r)[1], u13_buruketa(r), u13_buruketa(r),
            ej("lineas", "Idatzi 24 biderkadura ematen duten biderketa guztiak.", lineas=2, solucion="1 × 24, 2 × 12, 3 × 8, 4 × 6 (eta alderantziz)."),
            berrikusi("Bide guztiak probatu ditut", "Emaitza egiaztatu dut")]),
    ]
    berr = [
        hoja("BERRIKUSKETA (1)", "Biderketak: errepasoa.", [*u13_test(r), u13_batuketatik(r, 2), u13_kalkulatu(r, 6)]),
        hoja("BERRIKUSKETA (2)", "Biderketak: errepasoa.", [u13_falta(r, 6), *u13_propietateak(r)[:1], u13_buruketa(r),
                                                            berrikusi("Badakit zer den biderketa", "Badakit taulak", "Badakit buruketak ebazten")]),
    ]
    return "Biderketak", [ind, send, sak, berr]


# ------------------------------------------------------------------ Zatiketa (sarrera)
def u_zat_banatu(r, k):
    frases, sol = [], []
    for _ in range(k):
        n, d = r.randint(2, 4), r.randint(2, 4)
        ob = r.choice(OBJ)
        t = n * d
        irudiak = " ".join(f":{ob}:" for _ in range(t))
        frases.append(f"{irudiak}\nBanatu {t} {n} lagunen artean: {t} : {n} = [ ]")
        sol.append(f"{t} : {n} = {d}")
    return ej("completar", "Banatu berdin. Marraztu taldeak eta idatzi zatiketa.", frases=frases, solucion=sol)


def u_zat_taulatik(r, k):
    frases, sol = [], []
    for _ in range(k):
        a, b = r.randint(2, 9), r.randint(2, 9)
        frases.append(f"{a} × [ ] = {a * b}  →  {a * b} : {a} = [ ]")
        sol.append(f"{a} × {b} = {a * b} → {a * b} : {a} = {b}")
    return ej("completar", "Erabili biderketa-taula zatitzeko.", frases=frases, solucion=sol, columnas=2)


def u_zat_buruz(r, k):
    frases, sol = [], []
    for _ in range(k):
        a, b = r.randint(2, 10), r.randint(2, 10)
        frases.append(f"{a * b} : {a} = [ ]"); sol.append(str(b))
    return ej("completar", "Kalkulatu buruz.", frases=frases, solucion=sol, columnas=3)


def u_zat_gaiak(r):
    d, q, rest = r.randint(3, 9), r.randint(3, 9), 0
    D = d * q
    return ej("completar", f"Begiratu: **{D} : {d} = {q}**. Idatzi gai bakoitzaren izena (zatikizuna, zatitzailea, zatidura).",
              frases=[f"{D} → ___", f"{d} → ___", f"{q} → ___"], solucion=["zatikizuna", "zatitzailea", "zatidura"])


def u_zat_hondarra(r, k):
    frases, sol = [], []
    for _ in range(k):
        d = r.randint(2, 9); q = r.randint(2, 9); h = r.randint(1, d - 1); D = d * q + h
        frases.append(f"{D} : {d} = [ ]  hondarra: [ ]  → egiaztatu: {d} × ___ + ___ = {D}")
        sol.append(f"{D} : {d} = {q}, hondarra {h} → {d} × {q} + {h} = {D}")
    return ej("completar", "Zatitu. Zenbat geratzen da (hondarra)? Egiaztatu.", frases=frases, solucion=sol)


def u_zat_zehatza(r, k):
    vf, sol = [], []
    for _ in range(k):
        d = r.randint(2, 9); q = r.randint(2, 9)
        D = d * q + (0 if r.random() < .5 else r.randint(1, d - 1))
        vf.append(f"{D} : {d} zatiketa zehatza da (hondarra 0)."); sol.append("Egia" if D % d == 0 else "Gezurra")
    return ej("verdadero_falso", "Egia ala gezurra?", items=vf, solucion=sol)


def u_zat_luzea(r, k):
    frases, sol = [], []
    for _ in range(k):
        d = r.randint(2, 6); q = r.randint(12, 49); D = d * q
        frases.append(f"{D} : {d} = ___"); sol.append(f"{D} : {d} = {q}")
    return ej("completar", "Zatitu (bi zifrako zatidura). Egiaztatu biderketa eginez.", frases=frases, solucion=sol, columnas=2)


def u_zat_buruketa(r):
    izena = r.choice(IZENAK)
    tipo = r.choice(["kromoak", "taldeak", "autoak", "gozokiak"])
    if tipo == "kromoak":
        d, q = r.randint(2, 6), r.randint(4, 9)
        return ej("preguntas", f"{erg(izena)} {d * q} kromo ditu eta {d} lagunen artean berdin banatu nahi ditu.", lineas=2,
                  items=["Zenbat kromo emango dio lagun bakoitzari?"], solucion=f"{d * q} : {d} = {q} kromo")
    if tipo == "taldeak":
        d, q = r.choice([4, 5, 6]), r.randint(4, 6)
        return ej("preguntas", f"Gelan {d * q} ikasle daude. {d} kideko taldeak egin nahi ditugu.", lineas=2,
                  items=["Zenbat talde egingo ditugu?"], solucion=f"{d * q} : {d} = {q} talde")
    if tipo == "autoak":
        d = 4; q = r.randint(3, 9); h = r.randint(1, 3)
        return ej("preguntas", f"Txangora {d * q + h} lagun doaz. Auto bakoitzean {d} lagun sartzen dira.", lineas=2,
                  items=["Zenbat auto bete daitezke?", "Zenbat lagun geratzen dira autorik gabe? Zer egingo zenuke?"],
                  solucion=[f"{d * q + h} : {d} = {q}, hondarra {h} → {q} auto bete", f"{h} lagun; beste auto bat behar da ({q + 1} guztira)"])
    d, q = r.randint(3, 6), r.randint(5, 9)
    return ej("preguntas", f"Gozoki-poltsa batean {d * q} gozoki daude. {d} anai-arreben artean banatu dituzte.", lineas=2,
              items=["Zenbat gozoki jan ditu bakoitzak?"], solucion=f"{d * q} : {d} = {q} gozoki")


def u_zat_test(r):
    items, sol = [], []
    for _ in range(3):
        a, b = r.randint(2, 9), r.randint(2, 9)
        ops = list({b, b + 1, a})
        while len(ops) < 3:
            ops.append(b + 2)
        r.shuffle(ops)
        items.append({"texto": f"{a * b} : {a}", "opciones": [str(o) for o in ops]}); sol.append(str(b))
    return ej("elegir", "Inguratu zatidura zuzena.", items=items, solucion=sol)


def unitatea_zatiketa(r):
    ind = [
        hoja("BANATU BERDIN", "Zatitzea = berdin banatzea. Begiratu adibidea.", [
            gogoratu("12 sagar 3 lagunen artean: **12 : 3 = 4**. Lagun bakoitzak 4. 12 **zatikizuna**, 3 **zatitzailea**, 4 **zatidura**."),
            u_zat_banatu(r, 3), u_zat_gaiak(r), u_zat_buruz(r, 3)], tamano="grande"),
        hoja("BIDERKETAREKIN ZATITU", "Biderketa-taulak laguntzen digu.", [
            gogoratu("**3 × 4 = 12** badakit → **12 : 3 = 4** eta **12 : 4 = 3**."),
            u_zat_taulatik(r, 4), u_zat_buruz(r, 6), u_zat_buruketa(r),
            berrikusi("Berdin banatu dut", "Taula erabili dut", "Zatiketaren gaiak bereizten ditut")], tamano="grande"),
    ]
    send = [
        hoja("ZATITU ETA EGIAZTATU", "⭐⭐ Zatiketa zehatza eta hondarrarekin.", [u_zat_buruz(r, 9), u_zat_taulatik(r, 4), u_zat_hondarra(r, 3), u_zat_buruketa(r)]),
        hoja("BURUKETAK", "⭐⭐ Irakurri, pentsatu eta zatitu.", [u_zat_zehatza(r, 4), u_zat_buruketa(r), u_zat_buruketa(r),
                                                               berrikusi("Hondarra begiratu dut", "Biderketaz egiaztatu dut", "Erantzuna esaldi osoz idatzi dut")]),
    ]
    sak = [
        hoja("ZATIKETA LUZEAGOAK", "⭐⭐⭐ Bi zifrako zatidurak.", [u_zat_luzea(r, 6), u_zat_hondarra(r, 4), u_zat_buruketa(r), u_zat_zehatza(r, 4)]),
        hoja("ERRONKAK", "⭐⭐⭐ Pentsatu eta arrazoitu.", [u_zat_buruketa(r), u_zat_buruketa(r),
            ej("lineas", "Idatzi 36 zatikizuna eta hondarrik gabeko zatiketa guztiak (zatitzailea 2–9).", lineas=2,
               solucion="36 : 2 = 18 · 36 : 3 = 12 · 36 : 4 = 9 · 36 : 6 = 6 · 36 : 9 = 4"),
            berrikusi("Bide guztiak probatu ditut", "Emaitza egiaztatu dut")]),
    ]
    berr = [
        hoja("BERRIKUSKETA (1)", "Zatiketa: errepasoa.", [u_zat_test(r), u_zat_zehatza(r, 4), u_zat_buruz(r, 6), u_zat_taulatik(r, 4)]),
        hoja("BERRIKUSKETA (2)", "Zatiketa: errepasoa.", [u_zat_hondarra(r, 3), u_zat_luzea(r, 4), u_zat_buruketa(r), u_zat_buruketa(r),
                                                          berrikusi("Badakit berdin banatzen", "Badakit taula erabiltzen", "Badakit hondarra zer den")]),
    ]
    return "Zatiketa", [ind, send, sak, berr]


# ------------------------------------------------------------------ Ordua
_ORDU = ["", "ordu bata", "ordu biak", "hirurak", "laurak", "bostak", "seiak", "zazpiak", "zortziak", "bederatziak", "hamarrak", "hamaikak", "hamabiak"]
_MIN = {5: "eta bost", 10: "eta hamar", 15: "eta laurden", 20: "eta hogei", 25: "eta hogeita bost", 30: "eta erdiak",
        35: "hogeita bost gutxi", 40: "hogei gutxi", 45: "laurden gutxi", 50: "hamar gutxi", 55: "bost gutxi"}


def ordua_hitzez(h, m):
    h12 = (h - 1) % 12 + 1
    if m == 0:
        return _ORDU[h12]
    if m <= 30:
        return f"{_ORDU[h12]} {_MIN[m]}"
    sig = h12 % 12 + 1
    return f"{_ORDU[sig]} {_MIN[m]}"


def digitala(h, m):
    return f"{h:02d}:{m:02d}"


def _ordu(r, minutuak):
    return r.randint(1, 12), r.choice(minutuak)


def u_ord_irakurri(r, k, minutuak):
    items, sol = [], []
    for i in range(k):
        h, m = _ordu(r, minutuak)
        items.append({"h": h, "m": m, "letra": "abcdefgh"[i]}); sol.append(f"{'abcdefgh'[i]}) {ordua_hitzez(h, m)} ({digitala(h, m)})")
    return [ej("lineas", "Zer ordu da? Idatzi hitzez.", lineas=0, solucion=sol), {"tipo": "erlojuak", "columnas": 4, "items": items}]


def u_ord_marraztu(r, k, minutuak):
    items, sol = [], []
    for i in range(k):
        h, m = _ordu(r, minutuak)
        items.append({"h": h, "m": m, "orratzak": False, "letra": "abcdefgh"[i], "texto": f"**{ordua_hitzez(h, m)}**"})
        sol.append(f"{'abcdefgh'[i]}) {digitala(h, m)}")
    return [ej("lineas", "Marraztu orratzak: txikia (orduak) gorriz, handia (minutuak) urdinez.", lineas=0, solucion=sol),
            {"tipo": "erlojuak", "columnas": 4, "items": items}]


def u_ord_digitala(r, k, minutuak):
    frases, sol = [], []
    for _ in range(k):
        h, m = _ordu(r, minutuak)
        if r.random() < .5:
            frases.append(f"{digitala(h, m)} → _____"); sol.append(ordua_hitzez(h, m))
        else:
            frases.append(f"{ordua_hitzez(h, m).capitalize()} → [ ]:[ ]"); sol.append(digitala(h, m))
    return ej("completar", "Erloju digitala ↔ hitzez.", frases=frases, solucion=sol, columnas=2)


def u_ord_iraupena(r, k):
    items, sol = [], []
    for _ in range(k):
        h = r.randint(8, 18); m = r.choice([0, 15, 30]); dur = r.choice([15, 30, 45, 60, 90])
        t = h * 60 + m + dur
        izena = r.choice(["Igeriketa-saioa", "Filma", "Futbol-partida", "Musika-klasea", "Txangoa"])
        items.append(f"{izena}: hasiera {digitala(h, m)} · amaiera {digitala(t // 60, t % 60)}. Zenbat denbora iraun du?")
        sol.append(f"{dur} minutu" + (f" (ordu {'bat' if dur == 60 else 'eta erdi'})" if dur in (60, 90) else ""))
    return ej("preguntas", "Kalkulatu zenbat iraun duen.", items=items, lineas=1, solucion=sol)


def u_ord_test(r):
    items, sol = [], []
    for _ in range(3):
        h, m = _ordu(r, [0, 15, 30, 45])
        bien = ordua_hitzez(h, m)
        malos = {ordua_hitzez(h % 12 + 1, m), ordua_hitzez(h, (m + 30) % 60 if m in (0, 30) else 60 - m)}
        malos.discard(bien)
        ops = [bien] + list(malos)[:2]
        r.shuffle(ops)
        items.append({"texto": digitala(h, m), "opciones": ops}); sol.append(bien)
    return ej("elegir", "Zein da ordu zuzena?", items=items, solucion=sol)


def unitatea_ordua(r):
    oso = [0, 30]; laur = [0, 15, 30, 45]; bost = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
    ind = [
        hoja("ERLOJUA IRAKURRI", "Orratz txikia = orduak · orratz handia = minutuak.", [
            gogoratu("Orratz handia **12an**: ordu justua (_hirurak_). Orratz handia **6an**: _eta erdiak_ (_hirurak eta erdiak_)."),
            *u_ord_irakurri(r, 4, oso), *u_ord_marraztu(r, 4, oso)], tamano="grande"),
        hoja("LAURDENAK", "Eta laurden · laurden gutxi.", [
            gogoratu("Handia **3an**: _eta laurden_. Handia **9an**: _laurden gutxi_ (hurrengo ordua!)."),
            *u_ord_irakurri(r, 4, laur), *u_ord_marraztu(r, 4, laur), berrikusi("Orratzak bereizi ditut", "Erdiak eta laurdenak irakurri ditut")], tamano="grande"),
    ]
    send = [
        hoja("ORDUAK ETA MINUTUAK", "⭐⭐ Bost minututik bost minutura.", [*u_ord_irakurri(r, 8, bost), u_ord_digitala(r, 6, bost)]),
        hoja("MARRAZTU ETA KALKULATU", "⭐⭐ Orratzak eta iraupena.", [*u_ord_marraztu(r, 4, laur), u_ord_iraupena(r, 3), u_ord_digitala(r, 4, bost),
                                                                   berrikusi("Minutuak 5ka zenbatu ditut", "Digitala eta hitzez lotu ditut")]),
    ]
    sak = [
        hoja("DENBORA KALKULATU", "⭐⭐⭐ Hasiera, amaiera eta iraupena.", [u_ord_iraupena(r, 4), u_ord_digitala(r, 6, bost), *u_ord_irakurri(r, 4, bost)]),
        hoja("NIRE EGUNA", "⭐⭐⭐ Antolatu zure eguna.", [*u_ord_marraztu(r, 4, bost), u_ord_iraupena(r, 2),
            ej("lineas", "Idatzi zure eguneko 4 une eta orduak (esnatu, eskolara iritsi, bazkaldu, oheratu).", lineas=3,
               solucion="Erantzun irekia. Egiaztatu orduak hitzez eta digitalez ondo idatzita daudela."),
            berrikusi("Iraupenak kalkulatu ditut", "Nire eguna antolatu dut")]),
    ]
    berr = [
        hoja("BERRIKUSKETA (1)", "Ordua: errepasoa.", [u_ord_test(r), *u_ord_irakurri(r, 4, laur), u_ord_digitala(r, 4, laur)]),
        hoja("BERRIKUSKETA (2)", "Ordua: errepasoa.", [*u_ord_marraztu(r, 4, laur), u_ord_digitala(r, 4, bost), u_ord_iraupena(r, 2),
                                                       berrikusi("Badakit erlojua irakurtzen", "Badakit orratzak marrazten", "Badakit iraupena kalkulatzen")]),
    ]
    return "Ordua", [ind, send, sak, berr]


# ------------------------------------------------------------------ LH 1
def _lh1_completar(enuntziatua, esaldiak, soluzioak, adibidea=None):
    if adibidea is None:
        adibidea = esaldiak[0]
        hutsunea = "[ ]" if "[ ]" in adibidea else "___"
        adibidea = adibidea.replace(hutsunea, f"**{soluzioak[0]}**", 1)
    return ej("completar", enuntziatua, frases=esaldiak, solucion=soluzioak, ejemplo=adibidea)


def _lh1_zenbatu(r, k, goi):
    esaldiak, soluzioak = [], []
    for _ in range(k):
        n, irudia = r.randint(1, goi), r.choice(OBJ)
        esaldiak.append(f"✏️ {' '.join([f':{irudia}:'] * n)} → [ ]")
        soluzioak.append(str(n))
    return _lh1_completar("✏️ Kontatu eta idatzi.", esaldiak, soluzioak)


def _lh1_aurrekoa(r, k, goi):
    esaldiak, soluzioak = [], []
    for _ in range(k):
        n = r.randint(1, goi - 1)
        if r.choice([True, False]):
            esaldiak.append(f"✏️ Aurrekoa: {n} → [ ]")
            soluzioak.append(str(n - 1))
        else:
            esaldiak.append(f"✏️ Ondorengoa: {n} → [ ]")
            soluzioak.append(str(n + 1))
    return _lh1_completar("✏️ Idatzi auzoko zenbakia.", esaldiak, soluzioak)


def _lh1_alderatu(r, k, goi):
    esaldiak, soluzioak = [], []
    for _ in range(k):
        a, b = r.randint(0, goi), r.randint(0, goi)
        esaldiak.append(f"⭕ {a} ___ {b}")
        soluzioak.append("<" if a < b else ">" if a > b else "=")
    return _lh1_completar("⭕ Konparatu zenbakiak.", esaldiak, soluzioak)


def unitatea_lh1_zenbakiak_20(r):
    maila_gorenak = [10, 20, 20, 20]
    mailak = []
    for goi in maila_gorenak:
        mailak.append([hoja("ZENBAKIAK 20 ARTE", "Ikusi adibidea.", [
            _lh1_zenbatu(r, 4, goi), {"tipo": "dibujo", "alto": 32, "texto": "✏️ Marraztu puntu bana."},
            _lh1_aurrekoa(r, 4, goi), _lh1_alderatu(r, 4, goi),
        ], tamano="grande")])
    return "Zenbakiak 20 arte", mailak


def _lh1_konposatu(r, k, zatia):
    esaldiak, soluzioak = [], []
    for _ in range(k):
        osoa = r.randint(10, 20)
        lehen_zatia = zatia if zatia == 10 else r.randint(5, min(9, osoa - 1)) if zatia == 5 else r.randint(1, osoa - 1)
        esaldiak.append(f":house: {osoa} = {lehen_zatia} + [ ]")
        soluzioak.append(str(osoa - lehen_zatia))
    return _lh1_completar("✏️ Osatu etxetxoa.", esaldiak, soluzioak)


def unitatea_lh1_konposaketa(r):
    mailak = []
    for _ in range(4):
        mailak.append([hoja("KONPOSAKETA", "Osatu 10etik 20ra.", [
            _lh1_konposatu(r, 4, 10), _lh1_konposatu(r, 4, 5), _lh1_konposatu(r, 4, None),
        ], tamano="grande")])
    return "Konposaketa 20 arte", mailak


def _lh1_batuketa(r, eramana):
    while True:
        a, b = r.randint(0, 19), r.randint(0, 19)
        if a + b > 20:
            continue
        darama = a % 10 + b % 10 >= 10
        if eramana is None or darama == eramana:
            return a, b


def _lh1_batuketa_eragiketak(r, k, eramana):
    itemak, soluzioak = [], []
    for i in range(k):
        a, b = _lh1_batuketa(r, eramana)
        itemak.append({"a": str(a), "b": str(b), "op": "+"})
        soluzioak.append(f"{'abcd'[i]}) {a + b}")
    adibideko_a, adibideko_b = _lh1_batuketa(r, eramana)
    return ej("operaciones", "✏️ Batu zenbakiak.", items=itemak, cab=["", "H", "B"], columnas=2,
              solucion=soluzioak, ejemplo=f"{adibideko_a} + {adibideko_b} = **{adibideko_a + adibideko_b}**")


def _lh1_batuketa_hutsunea(r, k, eramana):
    esaldiak, soluzioak = [], []
    for _ in range(k):
        a, b = _lh1_batuketa(r, eramana)
        osoa = a + b
        if r.choice([True, False]):
            esaldiak.append(f"✏️ {a} + [ ] = {osoa}")
            soluzioak.append(str(b))
        else:
            esaldiak.append(f"✏️ [ ] + {b} = {osoa}")
            soluzioak.append(str(a))
    return _lh1_completar("✏️ Osatu batuketa.", esaldiak, soluzioak)


def _lh1_zenbaki_zuzena(r, eramana):
    a, b = _lh1_batuketa(r, eramana)
    return [
        ej("completar", "➡️ Marraztu jauziak.", frases=[f"{a} + {b} = [ ]"],
           solucion=[str(a + b)], ejemplo=f"{a} + {b} = **{a + b}**"),
        {"tipo": "zuzena", "hasiera": 0, "pausoa": 1, "zatiak": 20,
         "puntuak": [{"balioa": a, "letra": "A"}, {"balioa": a + b, "letra": "B"}]},
    ]


def unitatea_lh1_batuketak_20(r):
    eramateak = [False, False, True, None]
    mailak = []
    for eramana in eramateak:
        mailak.append([hoja("BATUKETAK 20 ARTE", "Marraztu jauziak zenbaki-zuzenan.", [
            _lh1_batuketa_eragiketak(r, 4, eramana), *_lh1_zenbaki_zuzena(r, eramana),
            _lh1_batuketa_hutsunea(r, 4, eramana),
        ], tamano="grande")])
    return "Batuketak 20 arte", mailak


def _lh1_kenketa(r, goi=20):
    while True:
        a, b = r.randint(1, goi), r.randint(0, goi)
        if b <= a and a // 10 >= b // 10 and a % 10 >= b % 10:
            return a, b


def _lh1_kenketa_irudiekin(r, k):
    esaldiak, soluzioak = [], []
    for _ in range(k):
        a, b = _lh1_kenketa(r, 10)
        irudia = r.choice(OBJ)
        geratzen = [f":{irudia}:" for _ in range(a - b)]
        kendu = [f"~:{irudia}:~" for _ in range(b)]
        esaldiak.append(f"✏️ {' '.join(kendu + geratzen)} = [ ]")
        soluzioak.append(str(a - b))
    return _lh1_completar("✏️ Marratu eta kendu.", esaldiak, soluzioak)


def _lh1_kenketa_ariketak(r, k, goi=20, ezezaguna=False):
    esaldiak, soluzioak = [], []
    for _ in range(k):
        a, b = _lh1_kenketa(r, goi)
        if ezezaguna:
            esaldiak.append(f"✏️ {a} − [ ] = {a - b}")
            soluzioak.append(str(b))
        else:
            esaldiak.append(f"✏️ {a} − {b} = [ ]")
            soluzioak.append(str(a - b))
    enuntziatua = "✏️ Osatu kenketa." if ezezaguna else "✏️ Egin kenketak."
    return _lh1_completar(enuntziatua, esaldiak, soluzioak)


def unitatea_lh1_kenketak_20(r):
    mailak = []
    for goi in (10, 20, 20, 20):
        mailak.append([hoja("KENKETAK 20 ARTE", "Ez da hamarrekoa hartu behar.", [
            _lh1_kenketa_irudiekin(r, 4), _lh1_kenketa_ariketak(r, 4, goi),
            _lh1_kenketa_ariketak(r, 4, goi, ezezaguna=True),
        ], tamano="grande")])
    return "Kenketak 20 arte", mailak


def _lh1_hb_zenbakiak(r, k):
    esaldiak, soluzioak = [], []
    for _ in range(k):
        h, b = r.randint(1, 9), r.randint(0, 9)
        hamarrekoak = " ".join(["🟥"] * h)
        batekoak = " ".join(["🟦"] * b)
        esaldiak.append(f"✏️ {hamarrekoak} H · {batekoak} B = [ ]")
        soluzioak.append(str(h * 10 + b))
    return _lh1_completar("✏️ Idatzi zenbakia.", esaldiak, soluzioak)


def _lh1_hb_zifra(r, k, posizioa):
    esaldiak, soluzioak = [], []
    for _ in range(k):
        h, b = r.randint(1, 9), r.randint(0, 9)
        zifra = h if posizioa == "H" else b
        bestea = b if posizioa == "H" else h
        esaldiak.append(f"✏️ {h * 10 + b} = ___ {posizioa} + {bestea} {'B' if posizioa == 'H' else 'H'}")
        soluzioak.append(str(zifra))
    return _lh1_completar(f"✏️ Osatu {posizioa} zifra.", esaldiak, soluzioak)


def unitatea_lh1_zenbakiak_100(r):
    mailak = []
    for _ in range(4):
        mailak.append([hoja("ZENBAKIAK 100 ARTE", "🟥 H = 10 · 🟦 B = 1", [
            gogoratu("🟥 Barra bakoitzak 10 balio du. 🟦 Kubo bakoitzak 1."),
            _lh1_hb_zenbakiak(r, 4), _lh1_hb_zifra(r, 4, "H"), _lh1_hb_zifra(r, 4, "B"),
        ], tamano="grande")])
    return "Zenbakiak 100 arte", mailak


# ------------------------------------------------------------------ Adaptación NEAE / PT (fichas indartzeko)
MAX_EGOK = 3
# Espacio por hoja (calibrado midiendo el PDF real; unidad nueva → empezar por 200 y comprobar)
PRESUPUESTO = {"1.1": 200, "1.2": 220, "1.3": 255, "zatiketa": 220, "ordua": 285,
               "lh1-zenbakiak-20": 300, "lh1-konposaketa": 300, "lh1-batuketak-20": 300,
               "lh1-kenketak-20": 300, "lh1-zenbakiak-100": 300}
_UNIDAD_ACTUAL = None


def _txt(x):
    return x.get("texto", "") if isinstance(x, dict) else str(x)


def egokitu(hojas):
    """Versión realmente adaptada: el 1.er ítem de cada ejercicio sale resuelto como ejemplo,
    máximo 3 ítems por ejercicio, tablas de 3 filas y la hoja marcada como «egokitua»."""
    for h in hojas:
        h["egokitua"] = True
        h.pop("tamano", None)
        prev = None
        for b in h["bloques"]:
            if b.get("tipo") == "tabla" and prev is not None and isinstance(prev.get("solucion"), list):
                n = min(MAX_EGOK, len(b["filas"]))
                b["filas"] = b["filas"][:n]
                prev["solucion"] = prev["solucion"][:n]
            if b.get("tipo") == "erlojuak":
                b["items"] = b["items"][:MAX_EGOK]
                b["columnas"] = MAX_EGOK
                if prev is not None and isinstance(prev.get("solucion"), list):
                    prev["solucion"] = prev["solucion"][:MAX_EGOK]
            if b.get("tipo") != "ejercicio":
                prev = b
                continue
            sol = b.get("solucion")
            modo = b.get("modo")
            if modo == "completar" and isinstance(sol, list) and len(sol) == len(b.get("frases", [])) and len(sol) > 1:
                f0, s0 = b["frases"][0], str(sol[0])
                if "\n" in f0:
                    b["ejemplo"] = f0.split("\n")[0] + " → " + s0
                elif "=" in s0 or "→" in s0:
                    b["ejemplo"] = s0
                else:
                    ph = "[ ]" if "[ ]" in f0 else "___"
                    b["ejemplo"] = f0.replace(ph, f"**{s0}**", 1).replace("[ ]", "").replace("___", "")
                b["frases"], b["solucion"] = b["frases"][1:MAX_EGOK + 1], sol[1:MAX_EGOK + 1]
                if b.get("columnas"):
                    b["columnas"] = min(b["columnas"], 2)
            elif modo in ("elegir", "verdadero_falso", "preguntas") and isinstance(sol, list) and len(sol) == len(b.get("items", [])) and len(sol) > 1:
                b["ejemplo"] = f"{_txt(b['items'][0])} → **{sol[0]}**"
                b["items"], b["solucion"] = b["items"][1:MAX_EGOK + 1], sol[1:MAX_EGOK + 1]
            elif modo == "operaciones" and len(b.get("items", [])) > 1:
                o = b["items"][0]
                a, c = int(o["a"]), int(o["b"])
                r = a + c if o["op"] == "+" else a - c if o["op"] == "−" else a * c
                b["ejemplo"] = f"{o['a']} {o['op']} {o['b']} = **{r}**"
                b["items"] = b["items"][1:MAX_EGOK + 1]
                b["columnas"] = MAX_EGOK
                if isinstance(sol, list):
                    b["solucion"] = [f"{'abc'[i]}) {x.split(') ', 1)[-1]}" for i, x in enumerate(sol[1:MAX_EGOK + 1])]
            prev = b
    # reparto por espacio (mm aproximados con letra egokitua): hojas llenas pero sin apretar
    def alto(b):
        t, m = b.get("tipo"), b.get("modo")
        if t == "ejercicio":
            h = 16 + (14 if b.get("ejemplo") else 0)
            if m == "completar":
                h += sum(30 if "\n" in f else 15 for f in b.get("frases", [])) // (b.get("columnas") or 1)
            elif m in ("elegir", "verdadero_falso"):
                h += 15 * len(b.get("items", [])) + (10 if m == "verdadero_falso" else 0)
            elif m == "preguntas":
                h += (12 + 13 * b.get("lineas", 1)) * len(b.get("items", []))
            elif m == "lineas":
                h += 13 * b.get("lineas", 0)
            elif m == "operaciones":
                h += 50
            else:
                h += 45
            return h
        return {"tabla": 14 + 14 * len(b.get("filas", [])), "erlojuak": 62, "zuzena": 38, "gogoratu": 26,
                "berrikusi": 30, "apartado": 34}.get(t, b.get("alto", 40))
    presupuesto = int(os.environ.get("KIMU_PRESUPUESTO") or PRESUPUESTO.get(_UNIDAD_ACTUAL, 200))
    unidades = []  # (hoja de origen, bloques)
    for h in hojas:
        pendiente = []
        for b in h["bloques"]:
            t = b.get("tipo")
            if t == "gogoratu":
                pendiente.append(b)
            elif t in ("tabla", "erlojuak", "zuzena", "dibujo") and unidades and unidades[-1][0] is h:
                unidades[-1][1].append(b)
            else:
                unidades.append((h, pendiente + [b])); pendiente = []
        if pendiente:
            unidades.append((h, pendiente))
    berr = [u for u in unidades if u[1][-1].get("tipo") == "berrikusi"]
    unidades = [u for u in unidades if u not in berr] + berr[-1:]
    def repartir(limite):
        nuevas, actual, usado, origen, usos = [], [], 0, None, []
        for h, u in unidades:
            hu = sum(alto(x) for x in u)
            if actual and usado + hu > limite and u[-1].get("tipo") != "berrikusi":
                nuevas.append(dict(origen, bloques=actual)); usos.append(usado); actual, usado, origen = [], 0, None
            if origen is None:
                origen = h if not nuevas or h is not nuevas[-1].get("_o") else dict(h, subtitulo="Jarraitu lasai. Begiratu adibidea.")
            actual += u; usado += hu
        if actual:
            nuevas.append(dict(origen, bloques=actual)); usos.append(usado)
        return nuevas, usos

    nuevas, usos = repartir(presupuesto)
    # Sin hojas medio vacías: si la última queda floja, se reparte el contenido a partes iguales.
    if len(nuevas) > 1 and usos[-1] < .5 * presupuesto:
        objetivo = sum(usos) / len(nuevas)
        for factor in (1.0, 1.05, 1.1, 1.15, 1.2, 1.3):
            n2, u2 = repartir(min(presupuesto, objetivo * factor))
            if len(n2) == len(nuevas):
                nuevas, usos = n2, u2
                break
    for n in nuevas:
        n.pop("_o", None)
    return nuevas


UNITATEAK = {"1.1": unitatea_1_1, "1.2": unitatea_1_2, "1.3": unitatea_1_3, "zatiketa": unitatea_zatiketa,
             "ordua": unitatea_ordua, "lh1-zenbakiak-20": unitatea_lh1_zenbakiak_20,
             "lh1-konposaketa": unitatea_lh1_konposaketa, "lh1-batuketak-20": unitatea_lh1_batuketak_20,
             "lh1-kenketak-20": unitatea_lh1_kenketak_20, "lh1-zenbakiak-100": unitatea_lh1_zenbakiak_100}
MAILAK = [("indartzeko", "Indartzeko fitxa (egokitua)", "⭐ NEAE/PT: ariketa bakoitzean adibide ebatzia, gehienez 3 item, letra handia eta lauki handiak."),
          ("sendotzeko", "Sendotzeko fitxa", "⭐⭐ Unitateko eduki guztiak lantzeko ariketak."),
          ("sakontzeko", "Sakontzeko fitxa", "⭐⭐⭐ Erronkak eta bi urratseko buruketak, azkarrenentzat."),
          ("berrikusketa", "Berrikusketa", "Unitateko errepasoa: testa, egia/gezurra, kalkulua eta buruketak.")]
KOLOREAK = ["azul", "verde", "morado", "naranja"]


def generar(unidad, version, semilla_base=2026):
    global _UNIDAD_ACTUAL
    _UNIDAD_ACTUAL = unidad
    r = random.Random(f"{semilla_base}-{unidad}-{version}")
    gaia, niveles = UNITATEAK[unidad](r)
    u = unidad.replace(".", "-")
    salida = []
    for i, ((clave, nombre, resumen), hojas) in enumerate(zip(MAILAK, niveles)):
        if clave == "indartzeko":
            hojas = egokitu(hojas)
        fid = f"mate-{u}-{clave}" + ("" if version == "A" else f"-{version.lower()}")
        lh1 = unidad.startswith("lh1-")
        nivel_nombre = ("indartzeko egokitua" if clave == "indartzeko" else clave) if lh1 else nombre
        curso = "LH 1" if lh1 else "LH 3"
        f = {
            "id": fid, "arlo": "lh1-matematika" if lh1 else "matematika",
            "seccion": "lh1-unitateak-mate" if lh1 else SECCION,
            "orden": (int(unidad.split(".")[1]) if unidad[0].isdigit() else 10 + list(UNITATEAK).index(unidad)) * 10 + i + 1,
            "publicado": not lh1, "curso": curso, "tipo_material": "Ariketa-fitxa",
            "nombre": (f"{gaia}: {nivel_nombre}" if lh1 else f"{unidad} {nombre}" if unidad[0].isdigit() else f"{gaia}: {nombre}")[:40],
            "titulo_resalte": f"{gaia.lower()}." if version == "A" else f"{gaia.lower()} ({version}).",
            "icono": ["🧩", "✏️", "🚀", "🔁"][i], "resumen": f"{gaia}: {resumen}"[:140],
            "descripcion_meta": f"{gaia} {curso}: {nombre.lower()}, zuzenketarekin. {unidad} unitatea."[:160],
            "color": KOLOREAK[i], "lugar": "actividades", "soluciones": True, "generado": True, "hojas": hojas,
        }
        TEORIA = {"ordua": "ordua-teoria", "1.3": "biderketak-teoria", "zatiketa": "zatiketa-teoria"}
        if unidad in TEORIA and clave == "indartzeko" and version == "A":
            f["relacionada"] = TEORIA[unidad]
        (FITXAK / f"{fid}.json").write_text(json.dumps(f, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        salida.append(fid)
    return salida


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--unitatea", choices=list(UNITATEAK) + ["denak"], default="denak")
    ap.add_argument("--bertsioa", default="A", help="A, B, C… (cada letra = números distintos)")
    a = ap.parse_args()
    for un in (UNITATEAK if a.unitatea == "denak" else [a.unitatea]):
        print(un, "→", ", ".join(generar(un, a.bertsioa.upper())))
