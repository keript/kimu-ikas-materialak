"""Generador de Lexikoa (vocabulario por temas) para LH 3.

Por cada tema de GAIAK genera tres fichas:
  lexikoa-<gaia>            Hiztegia (teoría): tarjetas imagen + palabra por categorías y mapa mental.
  lexikoa-<gaia>-ariketak   Ariketak ⭐→⭐⭐⭐: idatzi izena, lotu, sailkatu, osatu esaldiak, idatzi, hizki-zopa. Con zuzenketa.
  lexikoa-<gaia>-txartelak  Tarjetas recortables (imagen / palabra) para memoria; también salen en «Jolastu arbelean».

Añadir un tema = añadir una entrada en GAIAK (palabras con su imagen de estatico/irudiak y su categoría,
y unas frases con hueco). Los libros de texto solo orientan el temario: las listas y frases son propias.
Uso: python scripts/generar_lexikoa.py [--semilla N]
     python scripts/generar_lexikoa.py --maila LH1
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
VOCABULARIO_LH1 = RAIZ / "contenido" / "irudiak" / "hiztegia-irudiak.json"

LH1_TEMAK = [
    {
        "id": "eguraldia",
        "izena": "Eguraldia",
        "icono": "🌤️",
        "hitzak": ["eguzkia", "euria", "haizea", "elurra", "hodeia", "ortzadarra", "lainoa", "trumoia"],
        "lotu": ["eguzkia", "euria", "haizea", "elurra"],
        "aukeratu": ["hodeia", "ortzadarra", "lainoa", "trumoia"],
        "sailkatu": {
            "Zeruan": ["eguzkia", "hodeia", "ortzadarra"],
            "Lurera erortzen da": ["euria", "elurra"],
        },
        "mapa": {
            "Eguzkia eta ortzadarra": ["eguzkia", "ortzadarra"],
            "Euria eta elurra": ["euria", "elurra"],
            "Haizea eta lainoa": ["haizea", "lainoa"],
            "Hodeiak eta trumoia": ["hodeia", "trumoia"],
        },
        "taula": [
            ("eguzkia", "Zeruan dago."),
            ("euria", "Uretatik erortzen da."),
            ("haizea", "Hostoak mugitzen ditu."),
            ("elurra", "Hotzean erortzen da."),
        ],
    },
    {
        "id": "urtaroak",
        "izena": "Urtaroak",
        "icono": "🍂",
        "hitzak": [
            "udazkena", "negua", "udaberria", "uda", "arbola", "hostoa",
            "sagarra", "udarea", "intxaurra", "mahatsa", "euria", "haizea",
        ],
        "lotu": ["udazkena", "negua", "udaberria", "uda"],
        "aukeratu": ["arbola", "hostoa", "sagarra", "mahatsa"],
        "sailkatu": {
            "Udazkenean": ["udazkena", "sagarra", "hostoa"],
            "Beste urtaroetan": ["negua", "uda"],
        },
        "mapa": {
            "Hostoak": ["arbola", "hostoa"],
            "Fruituak": ["sagarra", "udarea", "intxaurra", "mahatsa"],
            "Eguraldia": ["euria", "haizea", "udazkena"],
        },
        "azalpenak": {
            "arbola": "Hostoak berdeak, horiak, gorriak edo marroiak dira.",
            "hostoa": "Egunak laburtzean, hostoa erori egiten da.",
            "udazkena": "Zuhaitza negurako prestatzen da.",
        },
        "pasoak": [
            ("1. Garbitu", "Garbitu eskuak eta fruta.", "udarea"),
            ("2. Moztu", "Helduak fruta zatitan moztu.", "sagarra"),
            ("3. Prestatu", "Zatiak makilatxo kamutsean sartu.", "mahatsa"),
            ("4. Egiaztatu", "Irakasleak alergiak egiaztatu.", "intxaurra"),
        ],
        "taula": [
            ("arbola", "Negurako hostoak galtzen ditu."),
            ("hostoa", "Kolorez aldatzen da eta erori egiten da."),
            ("sagarra", "Udazkeneko fruta da."),
            ("euria", "Udazkenean euria eta haizea egiten du."),
        ],
    },
    {
        "id": "animaliak",
        "izena": "Animaliak",
        "icono": "🐾",
        "hitzak": [
            "astoa", "arraina", "elefantea", "erlea", "igela", "otsoa",
            "oilarra", "untxia", "urtxintxa", "usoa", "hartza",
        ],
        "lotu": ["astoa", "arraina", "elefantea", "erlea"],
        "aukeratu": ["igela", "otsoa", "oilarra", "untxia"],
        "sailkatu": {
            "Etxekoak": ["astoa", "oilarra", "untxia"],
            "Basakoak": ["elefantea", "otsoa"],
        },
        "mapa": {
            "Etxekoak": ["astoa", "arraina", "oilarra", "untxia"],
            "Basakoak": ["elefantea", "erlea", "igela", "otsoa", "urtxintxa", "usoa", "hartza"],
        },
        "taula": [
            ("astoa", "Etxeko animalia da."),
            ("arraina", "Uretan bizi da."),
            ("elefantea", "Basako animalia da."),
            ("erlea", "Loreetan ibiltzen da."),
        ],
    },
    {
        "id": "eskola-etxea",
        "izena": "Eskola eta etxea",
        "icono": "🏠",
        "hitzak": [
            "aulkia", "ohea", "etxea", "ogia", "ura",
            "motxila", "arkatza", "koadernoa", "liburua",
        ],
        "lotu": ["aulkia", "ohea", "etxea", "ogia"],
        "aukeratu": ["ura", "motxila", "arkatza", "koadernoa"],
        "sailkatu": {
            "Eskolan": ["arkatza", "koadernoa", "liburua"],
            "Etxean": ["ohea", "ogia"],
        },
        "mapa": {
            "Eskolan": ["aulkia", "motxila", "arkatza", "koadernoa", "liburua"],
            "Etxean": ["ohea", "etxea", "ogia", "ura"],
        },
        "taula": [
            ("aulkia", "Eseritzeko da."),
            ("ohea", "Lo egiteko da."),
            ("motxila", "Eskolara eramaten da."),
            ("ogia", "Jateko da."),
        ],
    },
    {
        "id": "bizidunak-bizigabeak",
        "izena": "Bizidunak eta bizigabeak",
        "icono": "🌱",
        "hitzak": [
            "baratzea", "landarea", "lurra", "harria", "igela", "ahatea",
            "arraina", "ihia", "nenufarra", "eguzkia", "ura", "arbola",
        ],
        "lotu": ["landarea", "igela", "ahatea", "harria"],
        "aukeratu": ["baratzea", "lurra", "nenufarra", "arraina"],
        "sailkatu": {
            "Bizidunak": ["landarea", "igela", "ahatea"],
            "Bizigabeak": ["harria", "ura"],
        },
        "mapa": {
            "Baratzea": ["baratzea", "landarea", "arbola", "lurra"],
            "Hezegunea": ["igela", "ahatea", "arraina", "ihia", "nenufarra"],
            "Beharrak": ["ura", "eguzkia", "lurra"],
        },
        "taula": [
            ("landarea", "Ura, eguzkia eta lurra behar ditu."),
            ("igela", "Hezegunean bizi da."),
            ("harria", "Bizigabea da."),
            ("baratzea", "Barazkiak hazten dira bertan."),
        ],
        "gogoratu": "Bizidunak zaindu. Ez bota zaborrik naturan.",
    },
    {
        "id": "gorputza",
        "izena": "Gorputza eta zentzumenak",
        "icono": "🖐️",
        "hitzak": [
            "burua", "besoa", "hanka", "oina", "begia", "belarria",
            "sudurra", "mihia", "eskua", "hortza", "xaboia", "eskuila",
        ],
        "lotu": ["begia", "belarria", "sudurra", "mihia"],
        "lotu_erantzunak": ["ikusmena", "entzumena", "usaimena", "dastamena"],
        "aukeratu": ["burua", "eskua", "hortza", "xaboia"],
        "sailkatu": {
            "Zentzumenekin": ["begia", "belarria", "eskua"],
            "Gorputzeko atalak": ["burua", "hanka"],
        },
        "mapa": {
            "Atalak": ["burua", "besoa", "hanka", "oina"],
            "Zentzumenak": ["begia", "belarria", "sudurra", "mihia", "eskua"],
            "Ohitura onak": ["hortza", "xaboia", "eskuila"],
        },
        "taula_goiburua": ["IRUDIA", "ORGANOA", "ZENTZUMENA", "ZERTARAKO?"],
        "taula": [
            ("begia", ["begia", "Ikusmena", "Ikusteko"]),
            ("belarria", ["belarria", "Entzumena", "Entzuteko"]),
            ("sudurra", ["sudurra", "Usaimena", "Usaintzeko"]),
            ("mihia", ["mihia", "Dastamena", "Dastatzeko"]),
            ("eskua", ["eskua", "Ukimena", "Ukitzen duguna sentitzeko"]),
        ],
        "gogoratu": "Garbitu eskuak. Garbitu hortzak. Edan ura.",
    },
]

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
        "kategoriak": {"Taldekoak": "soccer-ball", "Bakarkakoak": "person-running", "Uretakoak edo elurrekoak": "person-swimming"},
        "hitzak": [
            ("futbola", "soccer-ball", "Taldekoak"), ("saskibaloia", "basketball", "Taldekoak"),
            ("eskubaloia", "person-playing-handball", "Taldekoak"), ("errugbia", "rugby-football", "Taldekoak"),
            ("boleibola", "volleyball", "Taldekoak"), ("tenisa", "tennis", "Bakarkakoak"),
            ("atletismoa", "person-running", "Bakarkakoak"), ("txirrindularitza", "person-biking", "Bakarkakoak"),
            ("gimnastika", "person-cartwheeling", "Bakarkakoak"), ("pilota", "person-bouncing-ball", "Bakarkakoak"),
            ("igeriketa", "person-swimming", "Uretakoak edo elurrekoak"), ("surfa", "person-surfing", "Uretakoak edo elurrekoak"),
            ("eskia", "skier", "Uretakoak edo elurrekoak"), ("arraunketa", "person-rowing-boat", "Uretakoak edo elurrekoak"),
        ],
        "esaldiak": [("___ talde bakoitzean hamaika jokalari daude.", "Futbolean"),
                     ("___ pilota saskira sartzen saiatzen dira.", "Saskibaloian"),
                     ("___ uretan egiten dugu.", "Igeriketa"),
                     ("___ bizikletaz egiten dugu.", "Txirrindularitza"),
                     ("___ pilota eskuekin botatzen da atera.", "Eskubaloian"),
                     ("___ erraketaz eta pilota txikiz jokatzen da.", "Tenisean")],
        "idatzi": "Aukeratu bi kirol eta idatzi esaldi bana: non egiten dira?",
    },
    "arropa": {
        "izena": "Arropa", "icono": "🧣", "irudia": "scarf",
        "kategoriak": {"Negukoa": "gloves", "Udakoa": "sun", "Oinetakoak eta osagarriak": "backpack"},
        "hitzak": [
            ("galtzak", "jeans", "Udakoa"), ("kamiseta", "t-shirt", "Udakoa"),
            ("berokia", "coat", "Negukoa"),
            ("txapela", "billed-cap", "Negukoa"), ("eskularruak", "gloves", "Negukoa"),
            ("bufanda", "scarf", "Negukoa"), ("zapatak", "running-shoe", "Oinetakoak eta osagarriak"),
            ("galtzerdiak", "socks", "Oinetakoak eta osagarriak"), ("soinekoa", "dress", "Udakoa"), ("motxila", "backpack", "Oinetakoak eta osagarriak"),
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
            ("irakaslea", "teacher", "Osasuna eta laguntza"), ("medikua", "health-worker", "Osasuna eta laguntza"),
            ("suhiltzailea", "firefighter", "Osasuna eta laguntza"), ("ertzaina", "police-officer", "Osasuna eta laguntza"),
            ("zaintzailea", "raising-hands", "Osasuna eta laguntza"),
            ("sukaldaria", "cook", "Janaria"), ("nekazaria", "farmer", "Janaria"),
            ("okina", "baguette-bread", "Janaria"), ("arrantzalea", "fishing-pole", "Janaria"),
            ("dendaria", "shopping-cart", "Janaria"), ("artista", "artist", "Artea eta beste"),
            ("musikaria", "singer", "Artea eta beste"), ("margolaria", "paintbrush", "Artea eta beste"),
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
            ("sukaldea", "cooking", "Gelak"), ("komuna", "toilet", "Gelak"),
            ("ohea", "bed", "Altzariak"),
            ("mahaia", "fork-and-knife-with-plate", "Altzariak"), ("aulkia", "chair", "Altzariak"),
            ("sofa", "couch-and-lamp", "Altzariak"), ("atea", "door", "Beste gauzak"), ("leihoa", "window", "Beste gauzak"),
            ("lanpara", "light-bulb", "Beste gauzak"), ("ispilua", "mirror", "Beste gauzak"),
            ("bainuontzia", "bathtub", "Beste gauzak"), ("zakarrontzia", "wastebasket", "Beste gauzak"),
        ],
        "esaldiak": [("___ janaria prestatzen dugu.", "Sukaldean"),
                     ("___ lo egiten dugu.", "Ohean"),
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
        bloques.append({"tipo": "tarjetas", "columnas": 3, "items": items})
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


def temas_lh1():
    """Prepara los temas LH 1 usando las imágenes del vocabulario compartido."""
    lista = json.loads(VOCABULARIO_LH1.read_text(encoding="utf-8"))
    imagenes = {
        palabra: imagen
        for grupo in lista["taldeak"]
        for palabra, imagen in grupo["hitzak"].items()
    }
    temas = []
    for tema in LH1_TEMAK:
        faltan = [palabra for palabra in tema["hitzak"] if palabra not in imagenes]
        if faltan:
            raise ValueError(f'{tema["id"]}: faltan imágenes en hiztegia-irudiak.json: {faltan}')
        temas.append({
            **tema,
            "palabras": [(palabra, imagenes[palabra]) for palabra in tema["hitzak"]],
        })
    return temas


def ficha_lh1(fid, seccion, orden, nombre, titulo_resalte, resumen, color, lugar, hojas,
              soluciones=False, relacionada=None, tipo="Gaiaren laburpena", icono="🌱"):
    ficha = {
        "id": fid, "arlo": "lh1-ingurunea", "seccion": seccion, "orden": orden,
        "publicado": False, "curso": "LH 1", "tipo_material": tipo,
        "nombre": nombre[:40], "titulo_resalte": titulo_resalte[:40], "icono": icono,
        "resumen": resumen[:140],
        "descripcion_meta": f"{nombre} LH 1erako: hitzak, irudiak eta ariketak.".strip()[:160],
        "color": color, "lugar": lugar, "soluciones": soluciones,
        "generado": True, "hojas": hojas,
    }
    if relacionada:
        ficha["relacionada"] = relacionada
    return ficha


def hiztegia_lh1(tema, color, orden):
    palabras = tema["palabras"]
    hojas = []
    orri_kopurua = -(-len(palabras) // 6)
    oinarri, soberan = divmod(len(palabras), orri_kopurua)
    zatiak = []
    hasiera = 0
    for i in range(orri_kopurua):
        tamaina = oinarri + (i < soberan)
        zatiak.append(palabras[hasiera:hasiera + tamaina])
        hasiera += tamaina
    for i, items in enumerate(zatiak):
        bloques = [{"tipo": "tarjetas", "columnas": 2,
                    "items": [
                        {"titulo": h, "imagen": im, **({"texto": tema["azalpenak"][h]} if h in tema.get("azalpenak", {}) else {})}
                        for h, im in items
                    ]}]
        if i == len(zatiak) - 1:
            taulako_irudiak = dict(palabras)
            bloques.extend([
                {
                    "tipo": "tabla",
                    "cabecera": tema.get("taula_goiburua", ["IRUDIA", "HITZA", "ZER DA?"]),
                    "filas": [
                        [f":{taulako_irudiak[h]}:", *(testua if isinstance(testua, list) else [h, testua])]
                        for h, testua in tema["taula"]
                    ],
                },
                {
                    "tipo": "gogoratu",
                    "titulo": "Gogoratu",
                    "texto": tema.get("gogoratu", f"{tema['izena']}: irudi bakoitzak hitz bat du."),
                },
            ])
        hojas.append({
            "titulo": tema["izena"].upper()[:34],
            "subtitulo": "Begiratu irudia. Irakurri hitza.",
            "tamano": "grande",
            "egokitua": True,
            "datos": False,
            "bloques": bloques,
        })
    if tema.get("pasoak"):
        hojas.append({
            "titulo": "FRUTA-BROTXETA",
            "subtitulo": "Heldu batekin prestatu.",
            "tamano": "grande",
            "egokitua": True,
            "datos": False,
            "bloques": [{
                "tipo": "pasos",
                "columnas": 2,
                "items": [
                    {"titulo": titulo, "texto": texto, "imagen": imagen}
                    for titulo, texto, imagen in tema["pasoak"]
                ],
            }],
        })
    ramas = [
        {"titulo": titulo, "imagen": dict(palabras)[hitzak[0]], "ejemplos": hitzak}
        for titulo, hitzak in tema["mapa"].items()
    ]
    hojas.append({
        "titulo": f"{tema['izena'].upper()}: MAPA"[:34],
        "orientacion": "horizontal",
        "datos": False,
        "bloques": [{
            "tipo": "mapa",
            "centro": {"titulo": tema["izena"], "imagen": palabras[0][1]},
            "ramas": ramas,
        }],
    })
    ficha = ficha_lh1(
        f"lh1-{tema['id']}-teoria", f"lh1-{tema['id']}", orden,
        tema["izena"], "hitzak irudiekin.", f"{tema['izena']}: hiztegia irudiekin eta mapa.",
        color, "teoria", hojas, tipo="Gaiaren laburpena", icono=tema["icono"],
    )
    ficha["relacionada"] = f"lh1-{tema['id']}-ariketak"
    return ficha


def ariketak_lh1(tema, color, orden):
    imagenak = dict(tema["palabras"])
    lotu = tema["lotu"][1:]
    lotu_erantzunak = tema.get("lotu_erantzunak", tema["lotu"])
    erantzun_map = dict(zip(tema["lotu"], lotu_erantzunak))
    nahastu = lotu_erantzunak[1:] + lotu_erantzunak[:1]
    aukeratu = tema["aukeratu"][1:]
    sailkatu = tema["sailkatu"]
    adibide_sail = next(iter(sailkatu.values()))[0]
    sailkatzeko = {
        k: [h for h in hitzak if h != adibide_sail]
        for k, hitzak in sailkatu.items()
    }
    pal_sail = [h for hitzak in sailkatzeko.values() for h in hitzak]
    blokeak = [
        {
            "tipo": "ejercicio", "modo": "relacionar",
            "enunciado": "🔗 Lotu irudia eta hitza.",
            "ejemplo": f":{imagenak[tema['lotu'][0]]}: → {lotu_erantzunak[0]}",
            "izquierda": [f":{imagenak[h]}:" for h in lotu],
            "derecha": nahastu,
            "solucion": [f"{nahastu.index(erantzun_map[h]) + 1}. {erantzun_map[h]}" for h in lotu],
        },
        {
            "tipo": "ejercicio", "modo": "elegir",
            "enunciado": "⭕ Inguratu hitz zuzena.",
            "ejemplo": f":{imagenak[tema['aukeratu'][0]]}: → {tema['aukeratu'][0]}",
            "items": [
                {"texto": f":{imagenak[h]}:", "opciones": [h, aukeratu[(i + 1) % len(aukeratu)]]}
                for i, h in enumerate(aukeratu)
            ],
            "solucion": [h for h in aukeratu],
        },
        {
            "tipo": "ejercicio", "modo": "clasificar",
            "enunciado": "🖍️ Sailkatu irudiak.",
            "ejemplo": f":{imagenak[adibide_sail]}: → {next(k for k, v in sailkatu.items() if adibide_sail in v)}",
            "columnas": list(sailkatu),
            "filas": max(len(hitzak) for hitzak in sailkatzeko.values()),
            "palabras": [f":{imagenak[h]}: {h}" for h in pal_sail],
            "solucion": " · ".join(f"{k}: {', '.join(v)}" for k, v in sailkatzeko.items()),
        },
        {"tipo": "berrikusi", "items": ["Irudiak ezagutu ditut", "Hitzak irakurri ditut", "Ariketak egin ditut"]},
    ]
    if tema["id"] == "eguraldia":
        osatzeko = {
            "tipo": "ejercicio", "modo": "completar",
            "enunciado": "☑ Gaur zer eguraldi egiten du?",
            "ejemplo": ":eguzkia: [x] eguzkia",
            "frases": [
                ":eguzkia: [ ] eguzkia  :euria: [ ] euria",
                ":haizea: [ ] haizea  :elurra: [ ] elurra",
            ],
            "solucion": "Erantzun pertsonala.",
        }
    elif tema["id"] == "urtaroak":
        osatzeko = {
            "tipo": "ejercicio", "modo": "completar",
            "enunciado": "✏️ Ordenatu urtaroak.",
            "ejemplo": ":uda: → 4",
            "frases": [f":{imagenak[h]}: ___" for h in tema["lotu"]],
            "solucion": [f"{i}. {h}" for i, h in enumerate(tema["lotu"], 1)],
        }
    elif tema["id"] == "animaliak":
        osatzeko = {
            "tipo": "ejercicio", "modo": "completar",
            "enunciado": "✏️ Osatu hitzak.",
            "ejemplo": f":{imagenak['hartza']}: basako animalia da.",
            "frases": [
                f":{imagenak['elefantea']}: ___ animalia da.",
                f":{imagenak['oilarra']}: ___ animalia da.",
            ],
            "solucion": ["elefantea: basakoa", "oilarra: etxekoa"],
        }
    elif tema["id"] == "bizidunak-bizigabeak":
        osatzeko = {
            "tipo": "ejercicio", "modo": "completar",
            "enunciado": "✏️ Zaindu natura.",
            "ejemplo": ":harria: Bizigabea da.",
            "frases": [
                ":landarea: ___ eta eguzkia behar ditu.",
                ":baratzea: Ez bota ___ bertara.",
            ],
            "solucion": ["ura", "zaborrik"],
        }
    elif tema["id"] == "gorputza":
        osatzeko = {
            "tipo": "ejercicio", "modo": "completar",
            "enunciado": "☑ Aukeratu ohitura onak.",
            "ejemplo": ":eskua: [x] Xaboiarekin garbitu.",
            "frases": [
                ":hortza: [ ] Eskuilarekin garbitu.",
                ":ura: [ ] Ura edan.",
                ":belarria: [ ] Musika ozena entzun.",
            ],
            "solucion": ["hortza: garbitu", "ura: edan", "musika ozena: ez da ohitura ona"],
        }
    else:
        osatzeko = {
            "tipo": "ejercicio", "modo": "completar",
            "enunciado": "✏️ Markatu lekua.",
            "ejemplo": f":{imagenak['motxila']}: [x] eskolan",
            "frases": [
                f":{imagenak['arkatza']}: [ ] eskolan  [ ] etxean",
                f":{imagenak['ohea']}: [ ] eskolan  [ ] etxean",
            ],
            "solucion": ["arkatza: eskolan", "ohea: etxean"],
        }
    berrikusi = blokeak.pop()
    blokeak.append(osatzeko)
    hojas = [
        {
            "titulo": f"{tema['izena'].upper()}: ARIKETAK"[:34],
            "subtitulo": "Lotu eta aukeratu.",
            "egokitua": True,
            "datos": False,
            "bloques": blokeak[:2],
        },
        {
            "titulo": f"{tema['izena'].upper()}: SAILKATU"[:34],
            "subtitulo": "Sailkatu eta osatu.",
            "egokitua": True,
            "datos": False,
            "bloques": [blokeak[2], osatzeko, berrikusi],
        },
    ]
    return ficha_lh1(
        f"lh1-{tema['id']}-ariketak", f"lh1-{tema['id']}", orden,
        f"{tema['izena']}: ariketak", "lotu, inguratu, sailkatu.",
        f"{tema['izena']}: irudiak lotu, hitzak aukeratu eta sailkatu.",
        color, "actividades", hojas, soluciones=True,
        relacionada=f"lh1-{tema['id']}-teoria", tipo="Ariketa-fitxa", icono="✏️",
    )


def txartelak_lh1(tema, color, orden):
    items = [
        {"aurrea": "Zer da?", "atzea": hitza, "imagen": imagen}
        for hitza, imagen in tema["palabras"]
    ]
    hoja = {
        "titulo": f"{tema['izena'].upper()}: TXARTELAK"[:34],
        "subtitulo": "Moztu. Jolastu binaka edo arbelean.",
        "datos": False,
        "bloques": [{
            "tipo": "txartelak",
            "items": items,
            "erabilerak": ["binaka", "memoria-jokoa", "Jolastu arbelean"],
        }],
    }
    return ficha_lh1(
        f"lh1-{tema['id']}-txartelak", f"lh1-{tema['id']}", orden,
        f"{tema['izena']}: txartelak", "moztu eta jolastu.",
        f"{tema['izena']}: irudi eta hitz txartelak memoria-jokorako.",
        color, "actividades", [hoja], relacionada=f"lh1-{tema['id']}-teoria",
        tipo="Ariketa-fitxa", icono="🃏",
    )


def pack_lh1(tema, orden):
    clave = f"lh1-{tema['id']}"
    color = KOLOREAK[(orden // 10 - 1) % len(KOLOREAK)]
    seccion = {
        "id": clave, "arlo": "lh1-ingurunea", "tipo": "pack", "orden": orden,
        "icono": tema["icono"], "nombre": tema["izena"],
        "tarjeta_arlo": {
            "texto": f"{tema['izena']}: hiztegia, ariketak eta txartelak irudiekin.",
            "boton": "Ikusi fitxak",
        },
        "pagina": {
            "descripcion_meta": f"{tema['izena']} LH 1erako: hiztegia, ariketak eta txartelak.",
            "titulo": tema["izena"], "titulo_resalte": "ikasi eta jolastu.",
            "intro": "Begiratu irudiak. Irakurri hitzak. Egin ariketak.",
        },
    }
    fichas = [
        hiztegia_lh1(tema, color, orden + 1),
        ariketak_lh1(tema, color, orden + 2),
        txartelak_lh1(tema, color, orden + 3),
    ]
    return seccion, fichas


def generar_lh1():
    """Genera los cuatro packs de vocabulario LH 1 y sus fichas borrador."""
    temas = temas_lh1()
    for imagen in {im for tema in temas for _, im in tema["palabras"]}:
        if not existe(imagen):
            sys.exit(f"Falta imagen de vocabulario: {imagen}")
    for i, tema in enumerate(temas):
        seccion, fichas = pack_lh1(tema, 20 + i * 10)
        (RAIZ / "contenido" / "secciones" / f"{seccion['id']}.json").write_text(
            json.dumps(seccion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(seccion["id"])
        for f in fichas:
            (FITXAK / f"{f['id']}.json").write_text(
                json.dumps(f, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            print(f["id"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semilla", type=int, default=2026)
    ap.add_argument("--maila", choices=("LH1", "LH3"), default="LH3")
    a = ap.parse_args()
    if a.maila == "LH1":
        generar_lh1()
        return
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
