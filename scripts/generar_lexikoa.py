"""Generador de Lexikoa (vocabulario por temas) para LH 3.

Por cada tema de GAIAK genera tres fichas:
  lexikoa-<gaia>            Hiztegia (teoría): tarjetas imagen + palabra por categorías y mapa mental.
  lexikoa-<gaia>-ariketak   Ariketak ⭐→⭐⭐⭐: idatzi izena, lotu, sailkatu, osatu esaldiak, idatzi, hizki-zopa. Con zuzenketa.
  lexikoa-<gaia>-txartelak  Tarjetas recortables (imagen / palabra) para memoria; también salen en «Jolastu arbelean».

Añadir un tema = añadir una entrada en GAIAK (palabras con su imagen de estatico/irudiak y su categoría,
y unas frases con hueco). Los libros de texto solo orientan el temario: las listas y frases son propias.
Uso: python scripts/generar_lexikoa.py [--semilla N]
"""
import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generar_retos as R  # noqa: E402  (hizki-zopa)

RAIZ = Path(__file__).resolve().parent.parent
FITXAK = RAIZ / "contenido" / "fitxak"
SECCION = "lexikoa"
KOLOREAK = ["verde", "naranja", "azul", "morado", "rojo", "turquesa"]

GAIAK = {
    "animaliak": {
        "izena": "Animaliak", "icono": "🐾", "irudia": "paw-prints",
        "kategoriak": {"Etxekoak": "home", "Baserrikoak": "barn", "Basakoak": "forest"},
        "hitzak": [
            ("katua", "cat", "Etxekoak"), ("txakurra", "dog", "Etxekoak"), ("untxia", "rabbit", "Etxekoak"), ("arraina", "fish", "Etxekoak"),
            ("behia", "cow", "Baserrikoak"), ("oiloa", "chicken", "Baserrikoak"), ("ardia", "ewe", "Baserrikoak"), ("zaldia", "horse", "Baserrikoak"),
            ("txerria", "pig", "Baserrikoak"), ("ahatea", "duck", "Baserrikoak"),
            ("hartza", "bear", "Basakoak"), ("oreina", "deer", "Basakoak"), ("lehoia", "lion", "Basakoak"), ("elefantea", "elephant", "Basakoak"),
            ("tximinoa", "monkey", "Basakoak"), ("hontza", "owl", "Basakoak"),
        ],
        "esaldiak": [("___ esnea ematen digu.", "Behiak"), ("___ arrautzak jartzen ditu.", "Oiloak"), ("___ gauez ondo ikusten du.", "Hontzak"),
                     ("___ artilea ematen digu.", "Ardiak"), ("___ tronpa luzea du.", "Elefanteak"), ("___ miau egiten du.", "Katuak")],
        "idatzi": "Aukeratu bi animalia eta idatzi esaldi bat bakoitzarekin: non bizi da? zer jaten du?",
    },
    "janaria": {
        "izena": "Janaria", "icono": "🍎", "irudia": "red-apple",
        "kategoriak": {"Frutak": "red-apple", "Barazkiak": "carrot", "Beste elikagaiak": "bread"},
        "hitzak": [
            ("sagarra", "red-apple", "Frutak"), ("platanoa", "banana", "Frutak"), ("mahatsa", "grapes", "Frutak"), ("marrubia", "strawberry", "Frutak"),
            ("udarea", "pear", "Frutak"), ("anana", "pineapple", "Frutak"),
            ("azenarioa", "carrot", "Barazkiak"), ("tomatea", "tomato", "Barazkiak"), ("brokolia", "broccoli", "Barazkiak"), ("patata", "potato", "Barazkiak"),
            ("tipula", "onion", "Barazkiak"),
            ("ogia", "bread", "Beste elikagaiak"), ("gazta", "cheese-wedge", "Beste elikagaiak"), ("arrautza", "egg", "Beste elikagaiak"),
            ("esnea", "glass-of-milk", "Beste elikagaiak"), ("eztia", "honey-pot", "Beste elikagaiak"),
        ],
        "esaldiak": [("Erleek ___ egiten dute.", "eztia"), ("Untxiek ___ asko jaten dute.", "azenarioa"), ("___ esnearekin egiten da.", "Gazta"),
                     ("Tortilla ___ eta arrautzekin egiten da.", "patatarekin"), ("Okindegian ___ erosten dugu.", "ogia"),
                     ("___ horia eta luzea da.", "Platanoa")],
        "idatzi": "Idatzi zure gosari gogokoena: zer frutak, zer barazkik edo zer elikagaik dute?",
    },
    "eskola": {
        "izena": "Eskola", "icono": "🎒", "irudia": "backpack",
        "kategoriak": {"Idazteko eta marrazteko": "pencil", "Motxilan": "backpack", "Ikasgelan": "school"},
        "hitzak": [
            ("arkatza", "pencil", "Idazteko eta marrazteko"), ("boligrafoa", "pen", "Idazteko eta marrazteko"),
            ("margoak", "crayon", "Idazteko eta marrazteko"), ("pintzela", "paintbrush", "Idazteko eta marrazteko"),
            ("motxila", "backpack", "Motxilan"), ("liburua", "open-book", "Motxilan"), ("koadernoa", "notebook", "Motxilan"),
            ("guraizeak", "scissors", "Motxilan"), ("erregela", "straight-ruler", "Motxilan"),
            ("abakoa", "abacus", "Ikasgelan"), ("egutegia", "calendar", "Ikasgelan"), ("irakaslea", "teacher", "Ikasgelan"),
            ("ikaslea", "student", "Ikasgelan"), ("liburutegia", "books", "Ikasgelan"),
        ],
        "esaldiak": [("___ marrak zuzen egiteko erabiltzen dugu.", "Erregela"), ("___ papera mozteko erabiltzen ditugu.", "Guraizeak"),
                     ("___ azalpenak ematen ditu.", "Irakasleak"), ("___ data begiratzeko erabiltzen dugu.", "Egutegia"),
                     ("___ marrazkiak koloreztatzeko erabiltzen ditugu.", "Margoak"), ("___ liburuak hartzen ditugu.", "Liburutegian")],
        "idatzi": "Zer daramazu zure motxilan? Idatzi bi esaldi.",
    },
    "kirolak": {
        "izena": "Kirolak", "icono": "🏅", "irudia": "trophy",
        "kategoriak": {"Taldekoak": "soccer-ball", "Bakarkakoak": "person-running", "Uretakoak edo elurrekoak": "water-wave"},
        "hitzak": [
            ("futbola", "soccer-ball", "Taldekoak"), ("saskibaloia", "soccer-ball", "Taldekoak"),
            ("eskubaloia", "soccer-ball", "Taldekoak"), ("errugbia", "soccer-ball", "Taldekoak"),
            ("boleibola", "soccer-ball", "Taldekoak"), ("tenisa", "soccer-ball", "Bakarkakoak"),
            ("atletismoa", "person-running", "Bakarkakoak"), ("txirrindularitza", "bicycle", "Bakarkakoak"),
            ("gimnastika", "flexed-biceps", "Bakarkakoak"), ("pilota", "soccer-ball", "Bakarkakoak"),
            ("igeriketa", "water-wave", "Uretakoak edo elurrekoak"), ("surfa", "water-wave", "Uretakoak edo elurrekoak"),
            ("eskia", "snow-capped-mountain", "Uretakoak edo elurrekoak"), ("arraunketa", "water-wave", "Uretakoak edo elurrekoak"),
        ],
        "esaldiak": [("___ taldean, hamaika jokalarik jokatzen dute.", "Futbolean"),
                     ("___ pilota saskira sartzen saiatzen dira.", "Saskibaloian"),
                     ("___ uretan egiten dugu.", "Igeriketa"),
                     ("___ bizikletaz egiten dugu.", "Txirrindularitza"),
                     ("___ ateak eta eskuko pilota erabiltzen dira.", "Eskubaloian"),
                     ("___ erraketaz eta pilota txikiz jokatzen da.", "Tenisean")],
        "idatzi": "Aukeratu bi kirol eta idatzi esaldi bana: non egiten dira?",
    },
    "arropa": {
        "izena": "Arropa", "icono": "🧣", "irudia": "scarf",
        "kategoriak": {"Negukoa": "gloves", "Udakoa": "sun", "Oinetakoak eta osagarriak": "backpack"},
        "hitzak": [
            ("galtzak", "person-running", "Udakoa"), ("kamiseta", "sun", "Udakoa"),
            ("jertsea", "gloves", "Negukoa"), ("berokia", "scarf", "Negukoa"),
            ("txapela", "scarf", "Negukoa"), ("eskularruak", "gloves", "Negukoa"),
            ("bufanda", "scarf", "Negukoa"), ("zapatak", "person-running", "Oinetakoak eta osagarriak"),
            ("galtzerdiak", "person-running", "Oinetakoak eta osagarriak"), ("gona", "sun", "Udakoa"),
            ("soinekoa", "sun", "Udakoa"), ("sandaliak", "person-running", "Oinetakoak eta osagarriak"),
            ("botak", "person-running", "Oinetakoak eta osagarriak"), ("motxila", "backpack", "Oinetakoak eta osagarriak"),
            ("aterkia", "umbrella", "Oinetakoak eta osagarriak"),
        ],
        "esaldiak": [("___ hotzetik babesten gaitu.", "Berokiak"),
                     ("___ lepoan janzten dugu.", "Bufanda"),
                     ("___ eskuak berotzen dituzte.", "Eskularruek"),
                     ("___ oinetan janzten ditugu.", "Zapatak"),
                     ("___ oinetakoen barruan janzten ditugu.", "Galtzerdiak"),
                     ("___ udan janzten dugu.", "Kamiseta")],
        "idatzi": "Aukeratu bi arropa eta idatzi esaldi bana: noiz janzten dituzu?",
    },
    "lanbideak": {
        "izena": "Lanbideak", "icono": "🧑‍🔧", "irudia": "teacher",
        "kategoriak": {"Osasuna eta laguntza": "heart-hands", "Janaria": "cooking", "Artea eta beste": "artist-palette"},
        "hitzak": [
            ("irakaslea", "teacher", "Osasuna eta laguntza"), ("medikua", "tooth", "Osasuna eta laguntza"),
            ("suhiltzailea", "fire", "Osasuna eta laguntza"), ("ertzaina", "handshake", "Osasuna eta laguntza"),
            ("erizaina", "heart-hands", "Osasuna eta laguntza"), ("zaintzailea", "raising-hands", "Osasuna eta laguntza"),
            ("sukaldaria", "cooking", "Janaria"), ("nekazaria", "seedling", "Janaria"),
            ("okina", "baguette-bread", "Janaria"), ("arrantzalea", "fish", "Janaria"),
            ("dendaria", "shopping-cart", "Janaria"), ("artista", "artist-palette", "Artea eta beste"),
            ("musikaria", "musical-note", "Artea eta beste"), ("margolaria", "paintbrush", "Artea eta beste"),
            ("idazlea", "writing-hand", "Artea eta beste"),
        ],
        "esaldiak": [("___ gaixoei laguntzen die.", "Medikuak"),
                     ("___ suteak itzaltzen ditu.", "Suhiltzaileak"),
                     ("___ ogia prestatzen du.", "Okina"),
                     ("___ barazkiak landatzen ditu.", "Nekazariak"),
                     ("___ abestiak sortzen ditu.", "Musikariak"),
                     ("___ arrainak harrapatzen ditu.", "Arrantzaleak")],
        "idatzi": "Aukeratu bi lanbide eta idatzi esaldi bana: zer egiten dute?",
    },
    "etxea": {
        "izena": "Etxea", "icono": "🏠", "irudia": "house",
        "kategoriak": {"Gelak": "house", "Altzariak": "sleeping-face", "Beste gauzak": "door"},
        "hitzak": [
            ("sukaldea", "cooking", "Gelak"), ("egongela", "house", "Gelak"),
            ("logela", "sleeping-face", "Gelak"), ("komuna", "tooth", "Gelak"),
            ("jangela", "fork-and-knife-with-plate", "Gelak"), ("ohea", "sleeping-face", "Altzariak"),
            ("mahaia", "fork-and-knife-with-plate", "Altzariak"), ("aulkia", "house", "Altzariak"),
            ("sofa", "house", "Altzariak"), ("armairua", "house", "Altzariak"),
            ("atea", "door", "Beste gauzak"), ("leihoa", "house", "Beste gauzak"),
            ("lanpara", "light-bulb", "Beste gauzak"), ("ispilua", "magnifying-glass-tilted-right", "Beste gauzak"),
            ("zakarrontzia", "wastebasket", "Beste gauzak"),
        ],
        "esaldiak": [("___ janaria prestatzen dugu.", "Sukaldean"),
                     ("___ lo egiten dugu.", "Logelan"),
                     ("___ bazkaltzeko erabiltzen dugu.", "Mahaia"),
                     ("___ eseritzeko erabiltzen dugu.", "Aulkia"),
                     ("___ gela batean sartzeko erabiltzen dugu.", "Atea"),
                     ("___ argia sartzen uzten du.", "Leihoak")],
        "idatzi": "Aukeratu etxeko bi gauza eta idatzi esaldi bana: zertarako dira?",
    },
}


def existe(irudia):
    return (RAIZ / "estatico" / "irudiak" / f"{irudia}.svg").is_file()


def ficha(fid, nombre, resalte, icono, resumen, meta, color, hojas, lugar, orden, soluciones=True, tipo="Ariketa-fitxa"):
    return {"id": fid, "arlo": "euskara", "seccion": SECCION, "orden": orden, "publicado": True, "curso": "LH 3",
            "tipo_material": tipo, "nombre": nombre[:40], "titulo_resalte": resalte[:40], "icono": icono,
            "resumen": resumen[:140], "descripcion_meta": meta[:160], "color": color, "lugar": lugar,
            "soluciones": soluciones, "generado": True, "hojas": hojas}


def hiztegia(clave, g, color, orden):
    cats = list(g["kategoriak"])
    col = {c: KOLOREAK[i % len(KOLOREAK)] for i, c in enumerate(cats)}
    bloques = []
    for c in cats:
        items = [{"titulo": h, "imagen": im, "color": col[c]} for h, im, k in g["hitzak"] if k == c]
        bloques.append({"tipo": "apartado", "titulo": c, "color": col[c], "imagen": g["kategoriak"][c] if existe(g["kategoriak"][c]) else items[0]["imagen"],
                        "texto": f"{len(items)} hitz. Irakurri ozen eta seinalatu irudia."})
        bloques.append({"tipo": "tarjetas", "columnas": 4, "items": items})
    hojas = [{"titulo": f"HIZTEGIA: {g['izena'].upper()}"[:34], "subtitulo": "Begiratu irudia, irakurri hitza eta esan ozen.",
              "datos": False, "bloques": bloques}]
    ramas = [{"titulo": c, "color": col[c], "texto": f"{sum(1 for x in g['hitzak'] if x[2] == c)} hitz",
              "imagen": next(im for h, im, k in g["hitzak"] if k == c),
              "ejemplos": [h for h, im, k in g["hitzak"] if k == c][:4]} for c in cats]
    hojas.append({"titulo": f"{g['izena'].upper()}: MAPA"[:34], "orientacion": "horizontal", "datos": False,
                  "bloques": [{"tipo": "mapa", "centro": {"titulo": g["izena"], "texto": "Lexikoa", "imagen": g["hitzak"][0][1]}, "ramas": ramas}]})
    return ficha(f"lexikoa-{clave}", f"Lexikoa: {g['izena']}", "hiztegia.", g["icono"],
                 f"{g['izena']}: {len(g['hitzak'])} hitz irudiekin, multzoka antolatuta, eta mapa mentala.",
                 f"Euskarazko lexikoa LH 3rako: {g['izena'].lower()}, irudi eta hitzekin, multzoka.", color, hojas, "teoria", orden,
                 soluciones=False, tipo="Gaiaren laburpena")


def ariketak(clave, g, color, orden, r):
    hitzak = g["hitzak"][:]
    r.shuffle(hitzak)
    idatzi = hitzak[:8]
    lotu = hitzak[8:14] if len(hitzak) >= 14 else hitzak[:6]
    der = [h for h, _, _ in lotu]
    r.shuffle(der)
    cats = list(g["kategoriak"])
    pal_sail = [h for h, _, _ in hitzak[:9]]
    esal = g["esaldiak"][:]
    r.shuffle(esal)
    banku = " · ".join(sorted(e[1].lower() for e in esal))
    zopa = [(h, im) for h, im, _ in hitzak if len(h) <= 9][:8]
    h1 = {"titulo": "IDATZI ETA LOTU", "subtitulo": f"{g['izena']}: hitzak eta irudiak.", "bloques": [
        {"tipo": "ejercicio", "modo": "completar", "enunciado": "⭐ Begiratu irudia eta idatzi bere izena.",
         "frases": [f":{im}: ___" for _, im, _ in idatzi], "solucion": [h for h, _, _ in idatzi], "columnas": 2},
        {"tipo": "ejercicio", "modo": "relacionar", "enunciado": "⭐ Lotu irudia eta hitza.",
         "izquierda": [f":{im}:" for _, im, _ in lotu], "derecha": der,
         "solucion": [f"{i}. {h}" for i, (h, _, _) in enumerate(lotu, 1)]},
    ]}
    h2 = {"titulo": "SAILKATU ETA OSATU", "subtitulo": "Pentsatu multzoan eta esaldian.", "bloques": [
        {"tipo": "ejercicio", "modo": "clasificar", "enunciado": "⭐⭐ Sailkatu hitzak bere multzoan.", "columnas": cats, "filas": max(sum(1 for _, _, k in hitzak[:9] if k == c) for c in cats),
         "palabras": pal_sail, "solucion": " · ".join(f"{c}: {', '.join(h for h, _, k in hitzak[:9] if k == c)}" for c in cats)},
        {"tipo": "ejercicio", "modo": "completar", "enunciado": f"⭐⭐ Osatu esaldiak. Hitz-bankua: {banku}",
         "frases": [e[0] for e in esal], "solucion": [e[0].replace("___", e[1]) for e in esal]},
        {"tipo": "ejercicio", "modo": "lineas", "lineas": 2, "enunciado": f"⭐⭐⭐ {g['idatzi']}",
         "solucion": "Erantzun irekia. Egiaztatu: letra larriz hasi, puntuz amaitu, gaiko hitzak erabili."},
        {"tipo": "berrikusi", "items": ["Hitzak ondo idatzi ditut", "Multzoak bereizi ditut", "Esaldiak puntuz amaitu ditut"]},
    ]}
    h3 = R.sopa_tarjeta(r, f"{g['izena'].upper()}: HIZKI-ZOPA", 1, zopa, 11, [(0, 1), (1, 0)], "eu", color)
    return ficha(f"lexikoa-{clave}-ariketak", f"Lexikoa: {g['izena']} (ariketak)", "idatzi, lotu, sailkatu.", "✏️",
                 f"{g['izena']}: idatzi izena, lotu, sailkatu, osatu esaldiak, idatzi eta hizki-zopa. Zuzenketarekin.",
                 f"Euskarazko lexikoa LH 3rako: {g['izena'].lower()} ariketak, zuzenketarekin.", color, [h1, h2, h3], "actividades", orden)


def txartelak(clave, g, color, orden):
    items = [{"aurrea": "Zer da?", "atzea": h.capitalize(), "imagen": im} for h, im, _ in g["hitzak"][:16]]
    hojas = []
    for i in range(0, len(items), 8):
        trozo = items[i:i + 8]
        hojas.append({"titulo": f"{g['izena'].upper()}: TXARTELAK"[:34], "subtitulo": "Inprimatu bi aldeetatik. Moztu eta jolastu: memoria, binaka, talde-erronka.",
                      "datos": False, "bloques": [{"tipo": "txartelak", "items": trozo,
                                                   "erabilerak": ["bakarka", "binaka", "memoria-jokoa", "talde-erronka"]}]})
    return ficha(f"lexikoa-{clave}-txartelak", f"Lexikoa: {g['izena']} (txartelak)", "moztu eta jolastu.", "🃏",
                 f"{g['izena']}: irudi eta hitz txartelak bi aldeetatik inprimatzeko, memoria-jokorako eta arbelerako jokorako.",
                 f"Euskarazko lexikoa LH 3rako: {g['izena'].lower()} txartelak, irudia eta hitza.", color, hojas, "actividades", orden,
                 soluciones=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semilla", type=int, default=2026)
    a = ap.parse_args()
    for i, (clave, g) in enumerate(GAIAK.items()):
        faltan = [im for _, im, _ in g["hitzak"] if not existe(im)]
        if faltan:
            sys.exit(f"{clave}: faltan imágenes {faltan}")
        r = random.Random(f"{a.semilla}-{clave}")
        color = KOLOREAK[i % len(KOLOREAK)]
        base = (i + 1) * 10
        for f in (hiztegia(clave, g, color, base + 1), ariketak(clave, g, color, base + 2, r), txartelak(clave, g, color, base + 3)):
            (FITXAK / f"{f['id']}.json").write_text(json.dumps(f, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f["id"])


if __name__ == "__main__":
    main()
