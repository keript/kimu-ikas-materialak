"""Generador de «Letraz letra» (LH 1 · Euskara): una colección fija por letra.

Por cada letra de LETRAK genera dos fichas (borrador, publicado: false):
  lh1-letra-<x>           Teoría: letra grande, 4 fotos que empiezan por ella, cómo se traza y mapa mental.
  lh1-letra-<x>-ariketak  Ariketak (egokitua): inguratu, aukeratu, trazatu, lotu, idatzi y berrikusi. Con zuzenketa.
y la sección pack contenido/secciones/lh1-letrak.json en el arlo lh1-euskara.

Las fotos salen SOLO de contenido/irudiak/hiztegia-irudiak.json (grupos «lh1-<x>», 4 palabras cada uno).
Añadir una letra = añadir su letra a LETRAK (y su grupo de 4 palabras a hiztegia-irudiak.json).
El orden de LETRAK es el orden de clase: bokalak eta h, luego una consonante por semana.
Uso: python scripts/generar_letrak.py
"""
import json
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FITXAK = RAIZ / "contenido" / "fitxak"
SECCIONES = RAIZ / "contenido" / "secciones"
HIZTEGIA = RAIZ / "contenido" / "irudiak" / "hiztegia-irudiak.json"
SECCION = "lh1-letrak"
LETRAK = ["a", "e", "i", "o", "u", "h"]
KOLOREAK = ["azul", "verde", "naranja", "morado", "rojo", "turquesa"]


def hitzak_de(letra):
    """Las 4 palabras del grupo lh1-<letra> (en el orden del JSON)."""
    for g in json.loads(HIZTEGIA.read_text(encoding="utf-8"))["taldeak"]:
        if g["id"] == f"lh1-{letra}":
            hitzak = list(g["hitzak"])
            if len(hitzak) != 4 or any(not h.startswith(letra) for h in hitzak):
                sys.exit(f"lh1-{letra}: el grupo necesita 4 palabras que empiecen por «{letra}»")
            return hitzak
    sys.exit(f"Falta el grupo «lh1-{letra}» en contenido/irudiak/hiztegia-irudiak.json")


def ficha(letra, sufijo, orden, color, nombre, resalte, resumen, meta, lugar, hojas, **extra):
    fid = f"lh1-letra-{letra}{sufijo}"
    return {"id": fid, "arlo": "lh1-euskara", "seccion": SECCION, "orden": orden, "publicado": False, "curso": "LH 1",
            "tipo_material": "Ariketa-fitxa" if lugar == "actividades" else "Gaiaren laburpena",
            "nombre": nombre, "titulo_resalte": resalte, "icono": "🔠", "resumen": resumen, "descripcion_meta": meta,
            "color": color, "lugar": lugar, "generado": True, **extra, "hojas": hojas}


def teoria(letra, i):
    L, hitzak = letra.upper(), hitzak_de(letra)
    h1 = {"titulo": f"{L} LETRA", "subtitulo": "Begiratu argazkiak eta esan ozen.", "datos": False, "tamano": "grande", "bloques": [
        {"tipo": "tarjetas", "columnas": 1, "items": [
            {"titulo": h, "grande": "{" + h[0] + "}" + h[1:], "imagen": h, "foto": True} for h in hitzak]},
    ]}
    h2 = {"titulo": f"NOLA TRAZATU {L}", "subtitulo": "Hasi 1 zenbakian. Jarraitu geziak.", "datos": False, "tamano": "grande", "bloques": [
        {"tipo": "tarjetas", "columnas": 1, "items": [
            {"titulo": f"{L} letra", "grande": f"{L} {letra}", "imagen": "pencil", "color": KOLOREAK[i % 6], "handia": True}]},
        {"tipo": "trazatu", "letra": letra, "lerroak": 1, "enunciado": f"✏️ {letra} txikia.", "solucion": "Geziak ordenan jarraitu ditu."},
        {"tipo": "trazatu", "letra": letra, "lerroak": 1, "maiuskula": True, "enunciado": f"✏️ {L} larria.", "solucion": "Geziak ordenan jarraitu ditu."},
        {"tipo": "gogoratu", "texto": f"{letra} hizkiarekin hasten dira: {', '.join(hitzak[:2])}…"},
    ]}
    h3 = {"titulo": f"{L}: MAPA", "orientacion": "horizontal", "datos": False, "bloques": [
        {"tipo": "mapa", "centro": {"titulo": f"{L} {letra}", "texto": "Letraz letra", "imagen": hitzak[0]},
         "ramas": [{"titulo": h, "texto": f"{letra} hizkiaz hasten da.", "imagen": h} for h in hitzak]}]}
    return ficha(letra, "", (i + 1) * 10 + 1, KOLOREAK[i % 6], f"{L} letra"[:40], "ezagutu eta trazatu.",
                 f"{L} {letra}: 4 argazki, trazatzeko geziak eta mapa.", f"Euskara LH 1: {L} {letra} letra, argazkiak eta nola trazatu.",
                 "teoria", [h1, h2, h3], relacionada=f"lh1-letra-{letra}-ariketak")


def ariketak(letra, i):
    L, hitzak = letra.upper(), hitzak_de(letra)
    otras = [LETRAK[(i + 1) % len(LETRAK)], LETRAK[(i + 2) % len(LETRAK)]]
    ordena = [letra] + otras  # la letra de la ficha y otras dos
    hw = {x: hitzak_de(x) for x in otras}
    hw[letra] = hitzak
    r = random.Random(f"letrak-{letra}")

    def barajada(lista):
        lista = list(lista)
        while True:
            r.shuffle(lista)
            if lista != sorted(lista, key=ordena.index):
                return lista

    # 1. Inguratu: 3 filas de 5 letras grandes, con 5 letras objetivo en total (mayúscula o minúscula).
    filas = []
    for k in (2, 1, 2):
        fila = [r.choice([letra, L]) for _ in range(k)] + [r.choice([x, x.upper()]) for x in r.sample([x for x in LETRAK if x != letra], 5 - k)]
        r.shuffle(fila)
        filas.append(fila)
    soluciones = [" eta ".join(f"{k + 1}." for k, c in enumerate(f) if c.lower() == letra) for f in filas]
    ej1 = {"tipo": "ejercicio", "modo": "completar", "grande": True, "enunciado": f"⭐ ⭕ Inguratu {letra}.",
           "ejemplo": f"o {L} e {letra} u", "frases": [" ".join(f) for f in filas], "solucion": soluciones}
    # 2. Aukeratu: lehen hizkia.
    items = []
    for x in ordena:
        ops = r.sample(ordena, 3)
        items.append({"texto": f":{hw[x][1]}:", "opciones": ops})
    ej2 = {"tipo": "ejercicio", "modo": "elegir", "enunciado": "⭐⭐ ⭕ Aukeratu lehen hizkia.",
           "ejemplo": f":{hitzak[2]}: → {letra}", "items": items, "solucion": list(ordena)}
    h1 = {"titulo": f"INGURATU: {L}", "subtitulo": "Begiratu eredua. Egin zuk.", "datos": False, "tamano": "grande", "egokitua": True,
          "bloques": [ej1, ej2]}
    # 3. Trazatu: 3 filas (2 minúsculas + 1 mayúscula).
    h2 = {"titulo": f"TRAZATU: {L}", "subtitulo": "Hasi 1 zenbakian. Jarraitu geziak.", "datos": False, "tamano": "grande", "egokitua": True,
          "bloques": [
              {"tipo": "trazatu", "letra": letra, "lerroak": 2, "enunciado": f"⭐ ✏️ Trazatu {letra}.", "solucion": f"{letra} txikia ondo trazatu du."},
              {"tipo": "trazatu", "letra": letra, "lerroak": 1, "maiuskula": True, "enunciado": f"⭐⭐ ✏️ Trazatu {L}.", "solucion": f"{L} larria ondo trazatu du."},
          ]}
    # 4. Lotu irudia eta hasierako hizkia + idatzi lehen hizkia.
    izq = [hw[x][0] for x in ordena]
    der = barajada(ordena)
    ej3 = {"tipo": "ejercicio", "modo": "relacionar", "enunciado": "⭐⭐ 🔗 Lotu irudia eta hizkia.",
           "ejemplo": f":{hitzak[1]}: → {letra}", "izquierda": [f":{w}:" for w in izq], "derecha": der,
           "solucion": [f"{n}. {x}" for n, x in enumerate(ordena, 1)]}
    orden_w = [(x, hw[x][2]) for x in barajada(ordena)]
    ej4 = {"tipo": "ejercicio", "modo": "completar", "enunciado": "⭐⭐⭐ ✏️ Idatzi lehen hizkia.",
           "ejemplo": f":{hitzak[3]}: {letra}", "frases": [f":{w}: ___" for _, w in orden_w], "solucion": [x for x, _ in orden_w]}
    h3 = {"titulo": f"LOTU ETA IDATZI: {L}", "subtitulo": "Begiratu irudiak. Jarri hizkia.", "datos": False, "tamano": "grande", "egokitua": True,
          "bloques": [ej3, ej4, {"tipo": "berrikusi", "items": ["Ezagutu dut", "Trazatu dut", "Irakurri dut"]}]}
    return ficha(letra, "-ariketak", (i + 1) * 10 + 2, KOLOREAK[i % 6], f"{L} letra: ariketak", "inguratu, trazatu, lotu.",
                 f"{L} {letra}: inguratu, trazatu, lotu irudiak eta idatzi lehen hizkia.", f"Euskara LH 1: {L} {letra} letraren ariketak, zuzenketarekin.",
                 "actividades", [h1, h2, h3], relacionada=f"lh1-letra-{letra}", soluciones=True)


def seccion():
    return {"id": SECCION, "arlo": "lh1-euskara", "tipo": "pack", "orden": 2, "icono": "🔠", "nombre": "Letraz letra",
            "tarjeta_arlo": {"texto": "Letra bat bakoitzean: ezagutu, inguratu, trazatu eta lotu.", "boton": "Ikusi"},
            "pagina": {"descripcion_meta": "Letraz letra LH 1en: bokalak eta H. Argazkiak, trazatzeko geziak eta ariketak.",
                       "titulo": "Letraz letra", "titulo_resalte": "letra bakoitza.",
                       "intro": "Letra bakoitzak bi fitxa ditu: teoria eta ariketak. Ezagutu, inguratu, trazatu eta lotu."}}


def main():
    for i, letra in enumerate(LETRAK):
        for f in (teoria(letra, i), ariketak(letra, i)):
            (FITXAK / f"{f['id']}.json").write_text(json.dumps(f, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f["id"])
    (SECCIONES / f"{SECCION}.json").write_text(json.dumps(seccion(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
