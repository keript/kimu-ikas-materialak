#!/usr/bin/env python3
"""Genera la web de Kimu a partir de contenido/ y plantillas/.

Uso:
    pip install jinja2 jsonschema
    python scripts/build.py            # genera la web en _site/
    python scripts/build.py --check    # solo comprueba el contenido

Si algo está mal (falta un campo, una imagen no existe, una respuesta
correcta apunta a una opción que no existe...) el script se para y explica
qué arreglar. Nada se publica hasta que el contenido sea correcto.
"""
from __future__ import annotations

import argparse
import os
from datetime import date
import io
import json
import copy
import re
import shutil
import sys
from pathlib import Path

try:
    import jsonschema
    from jinja2 import Environment, FileSystemLoader
    from markupsafe import Markup, escape
except ImportError:
    sys.exit("Faltan librerías. Ejecuta: pip install jinja2 jsonschema")

RAIZ = Path(__file__).resolve().parent.parent
CONTENIDO = RAIZ / "contenido"
PLANTILLAS = RAIZ / "plantillas"
ESTATICO = RAIZ / "estatico"
SALIDA = RAIZ / "_site"

UI = {
    "eu": {
        "inicio_kimu": "Kimu-ren hasiera",
        "nav_principal": "Nabigazio nagusia",
        "todas_areas": "Arlo guztiak",
        "tema_oscuro": "Aldatu modu ilunera",
        "tema_titulo": "Aldatu itxura",
        "volver_inicio": "Kimu-ren hasierara",
        "otras_asignaturas": "Beste ikasgaiak",
        "estado_titulo": "Katalogoa prestatzen ari gara.",
        "estado_texto": "Laster gehituko ditugu deskargatzeko fitxak eta jarduera interaktiboak. Ez dugu oraindik argitaratu gabeko materialik deskargagarri gisa erakusten.",
        "js": {"claro": "Aldatu modu argira", "oscuro": "Aldatu modu ilunera"},
    },
    "es": {
        "inicio_kimu": "Inicio de Kimu",
        "nav_principal": "Navegación principal",
        "todas_areas": "Todas las áreas",
        "tema_oscuro": "Cambiar al modo oscuro",
        "tema_titulo": "Cambiar apariencia",
        "volver_inicio": "Volver al inicio de Kimu",
        "otras_asignaturas": "Otras asignaturas",
        "estado_titulo": "Estamos preparando el catálogo.",
        "estado_texto": "Pronto añadiremos fichas descargables y actividades interactivas. Aún no mostramos materiales como publicados si todavía no están listos.",
        "js": {"claro": "Cambiar al modo claro", "oscuro": "Cambiar al modo oscuro"},
    },
}


class ErrorContenido(Exception):
    pass


errores: list[str] = []


def error(archivo: Path, mensaje: str) -> None:
    errores.append(f"  ✗ {archivo.relative_to(RAIZ)}: {mensaje}")


def leer_json(ruta: Path) -> dict:
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        error(ruta, f"el JSON no es válido (línea {e.lineno}, columna {e.colno}): {e.msg}")
        return {}


def cargar(carpeta: str) -> list[tuple[Path, dict]]:
    return [(p, leer_json(p)) for p in sorted((CONTENIDO / carpeta).glob("*.json"))]


# ---------- Formato de textos ----------

def formato_ejemplo(texto: str) -> Markup:
    """{G}aur -> letra resaltada; _título_ -> cursiva."""
    html = str(escape(texto))
    html = re.sub(r"\{(.+?)\}", r'<span class="capital">\1</span>', html)
    html = re.sub(r"_(.+?)_", r"<em>\1</em>", html)
    return Markup(html)


def formato_marcado(texto) -> Markup:
    """Texto de fichas: {X} resaltado, **negrita**, _cursiva_, _____ línea larga, ___ hueco para escribir, [ ] casilla."""
    html = str(escape(str(texto)))
    html = html.replace("_____", '<span class="hueco linea"></span>')  # línea larga para escribir palabras
    html = html.replace("___", '<span class="hueco largo"></span>')
    html = html.replace("\n", "<br>")
    html = html.replace("[ ]", '<span class="hueco"></span>')
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"~(.+?)~", r"<s>\1</s>", html)
    html = re.sub(r":([a-z0-9]+(?:-[a-z0-9]+)*):", lambda m: f'<img class="irudi-txiki" src="irudiak/{m.group(1)}.svg" alt="">' if (ESTATICO / "irudiak" / f"{m.group(1)}.svg").is_file() else m.group(0), html)
    html = re.sub(r"\{(.+?)\}", r'<span class="res">\1</span>', html)
    html = re.sub(r"(?<![\w/])_(?!_)(.+?)(?<!_)_(?![\w])", r"<em>\1</em>", html)
    return Markup(html)


UI_FITXA = {
    "eu": {"objetivos": "Zer ikasiko dugu?", "vf": ["EGIA", "GEZURRA"], "gogoratu": "GOGORATU!", "berrikusi": "Berrikusi",
           "izena": "Izena:", "data": "Data:", "orria": "orria", "orri": "orri", "ariketa": "ariketa", "zuzenketa": "ZUZENKETA",
           "zuzenketa_sub": "Irakaslearentzat: ariketen erantzunak.", "imprimir": "Inprimatu / PDF", "con_soluciones": "Zuzenketarekin",
           "azalpena": "Azalpena", "ariketak_egin": "Ariketak egin", "hojas_aria": "Fitxaren orriak"},
    "es": {"objetivos": "¿Qué vamos a aprender?", "vf": ["VERDADERO", "FALSO"], "gogoratu": "¡RECUERDA!", "berrikusi": "Reviso",
           "izena": "Nombre:", "data": "Fecha:", "orria": "hoja", "orri": "hojas", "ariketa": "ejercicio", "zuzenketa": "SOLUCIONES",
           "zuzenketa_sub": "Para el profesorado: respuestas de los ejercicios.", "imprimir": "Imprimir / PDF", "con_soluciones": "Con soluciones",
           "azalpena": "Teoría", "ariketak_egin": "Hacer los ejercicios", "hojas_aria": "Hojas de la ficha"},
}

UI_JOLASA = {
    "eu": {
        "button": "🎮 Jolastu arbelean", "start": "Jolasa hasi", "teams": "Taldeak",
        "team_count": "Talde kopurua", "team_name": "Taldearen izena", "time": "Galderako denbora",
        "seconds": "segundo", "no_time": "Denborarik gabe", "question": "Galdera",
        "choose": "Aukeratu erantzuna", "show_answer": "Erantzun zuzena erakutsi",
        "correct": "Erantzun zuzena", "award": "Nori eman puntua?", "no_point": "Punturik ez",
        "next": "Hurrengoa", "score": "Puntuak", "finish": "Azken sailkapena",
        "play_again": "Berriro hasi", "back": "Fitxara itzuli", "fullscreen": "Pantaila osoa", "game_title": "Jolasa",
        "time_up": "Denbora amaitu da!", "team": "taldea", "points": "puntu",
        "sound": "Soinua", "well_done": ["Oso ondo!", "Bikain!", "Hori da!", "Zuzena!"],
        "try_again": "Ia-ia! Erantzun bat kendu dut. Saiatu berriro.", "show_after": "Hau da erantzun zuzena. Hurrengoan lortuko duzu!",
        "solo_result": "Zuzen erantzun dituzu",
    },
    "es": {
        "button": "🎮 Jugar en la pizarra", "start": "Empezar", "teams": "Equipos",
        "team_count": "Número de equipos", "team_name": "Nombre del equipo", "time": "Tiempo por pregunta",
        "seconds": "segundos", "no_time": "Sin límite", "question": "Pregunta",
        "choose": "Elige una respuesta", "show_answer": "Mostrar respuesta correcta",
        "correct": "Respuesta correcta", "award": "¿A quién dar el punto?", "no_point": "Sin punto",
        "next": "Siguiente", "score": "Puntos", "finish": "Clasificación final",
        "play_again": "Volver a empezar", "back": "Volver a la ficha", "fullscreen": "Pantalla completa", "game_title": "Juego",
        "time_up": "¡Se acabó el tiempo!", "team": "equipo", "points": "puntos",
        "sound": "Sonido", "well_done": ["¡Muy bien!", "¡Genial!", "¡Eso es!", "¡Correcto!"],
        "try_again": "¡Casi! He quitado una respuesta. Prueba otra vez.", "show_after": "Esta es la respuesta correcta. ¡La próxima la sacas!",
        "solo_result": "Respuestas correctas",
    },
}


def partir_numero(n, columnas):
    """'38' con 2 columnas de cifras -> ['3','8']; rellena por la izquierda con ''."""
    cifras = list(str(n))
    return [""] * (columnas - len(cifras)) + cifras


BLOQUES = {
    "objetivos": ["items"], "apartado": ["titulo"], "tarjetas": ["items"], "tabla": ["cabecera", "filas"],
    "lectura": ["titulo", "parrafos"], "ejercicio": ["enunciado", "modo"], "idazketa": ["partes"],
    "pasos": ["items"], "ilustracion": ["archivo"], "parrafo": ["texto"], "mapa": ["centro", "ramas"], "reto": ["reto"], "gogoratu": ["texto"], "berrikusi": ["items"], "dibujo": [], "nota": ["texto"], "relleno": [],
    "tablero": ["casillas", "arauak", "txartelak"], "flipbook": ["portada", "pestanas"], "txartelak": ["items"], "zuzena": ["hasiera", "pausoa"], "erlojuak": ["items"], "entzun": ["audio"],
}
MODOS = {
    "lineas": [], "completar": ["frases"], "elegir": ["items"], "verdadero_falso": ["items"], "preguntas": ["items"],
    "relacionar": ["izquierda", "derecha"], "corregir": ["frases"], "clasificar": ["columnas"], "operaciones": ["items"],
}


def imagenes_usadas(obj):
    """Todos los valores de campos de imagen (y :nombre: en textos) de una ficha."""
    usadas = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("imagen", "imagen_centro") and isinstance(v, str):
                usadas.add(v)
            else:
                usadas |= imagenes_usadas(v)
    elif isinstance(obj, list):
        for v in obj:
            usadas |= imagenes_usadas(v)
    elif isinstance(obj, str):
        usadas |= set(re.findall(r":([a-z0-9]+(?:-[a-z0-9]+)+|[a-z0-9]{3,}):", obj))
    return usadas


def validar_fitxa(ruta, f, ids_arlo, ids_seccion, validador):
    for nombre in sorted(imagenes_usadas(f)):
        if not (ESTATICO / "irudiak" / f"{nombre}.svg").is_file():
            error(ruta, f"la imagen «{nombre}» no existe en estatico/irudiak/ (mira la lista en docs/fichas.md)")
    for e in sorted(validador.iter_errors(f), key=lambda e: list(e.path)):
        donde = " → ".join(str(p) for p in e.path) or "(raíz)"
        error(ruta, f"{donde}: {traducir_error(e)}")
    if f.get("id") != ruta.stem:
        error(ruta, f'"id" debe ser "{ruta.stem}" (igual que el nombre del archivo)')
    if f.get("arlo") not in ids_arlo:
        error(ruta, f'"arlo" = "{f.get("arlo")}" no existe')
    if f.get("seccion") not in ids_seccion:
        error(ruta, f'"seccion" = "{f.get("seccion")}" no existe en contenido/secciones/')
    for hi, h in enumerate(f.get("hojas", [])):
        for bi, b in enumerate(h.get("bloques", [])):
            donde = f"hoja {hi + 1}, bloque {bi + 1}"
            tipo = b.get("tipo")
            if tipo not in BLOQUES:
                error(ruta, f"{donde}: tipo «{tipo}» no existe. Tipos: {', '.join(BLOQUES)}")
                continue
            for campo in BLOQUES[tipo]:
                if campo not in b:
                    error(ruta, f"{donde} ({tipo}): falta «{campo}»")
            if tipo in ("tablero", "flipbook") and h.get("orientacion") != "horizontal":
                error(ruta, f"{donde} ({tipo}): la hoja debe tener orientacion «horizontal»")
            if tipo == "ilustracion" and not (CONTENIDO / "ilustraciones" / f'{b.get("archivo")}.svg').is_file():
                error(ruta, f"{donde}: la ilustración «{b.get('archivo')}» no existe en contenido/ilustraciones/")
            if tipo == "ejercicio":
                modo = b.get("modo")
                if modo not in MODOS:
                    error(ruta, f"{donde}: modo «{modo}» no existe. Modos: {', '.join(MODOS)}")
                    continue
                for campo in MODOS[modo]:
                    if campo not in b:
                        error(ruta, f"{donde} (ejercicio {modo}): falta «{campo}»")
                if modo == "relacionar" and len(b.get("izquierda", [])) != len(b.get("derecha", [])):
                    error(ruta, f"{donde}: «izquierda» y «derecha» deben tener el mismo número de elementos")
                if f.get("soluciones") and "solucion" not in b:
                    error(ruta, f"{donde}: la ficha lleva soluciones, falta «solucion» en este ejercicio")
            for clave in ("texto", "titulo"):
                v = b.get(clave)
                if isinstance(v, str) and (v.count("{") != v.count("}") or v.count("**") % 2):
                    error(ruta, f"{donde}: llaves {{ }} o ** sin cerrar en «{v[:40]}…»")


def geometria_mapa(b):
    """Coloca el centro y las ramas de un mapa mental (en mm) y calcula las curvas que los unen."""
    W, H = 269.0, b.get("alto", 156.0)
    cw, ch = 64.0, 64.0
    bw = b.get("ancho_rama", 84.0)
    ramas = b["ramas"]
    n = len(ramas)
    izq = (n + 1) // 2
    lados = [("izq", i, izq) for i in range(izq)] + [("der", i, n - izq) for i in range(n - izq)]
    cx, cy = W / 2, H / 2
    geo = {"W": W, "H": H, "centro": {"x": cx - cw / 2, "y": cy - ch / 2, "w": cw, "h": ch}, "ramas": []}
    for r, (lado, i, k) in zip(ramas, lados):
        slot = H / k
        bh = slot - 5
        y = i * slot + 2.5
        x = 0 if lado == "izq" else W - bw
        ex = bw if lado == "izq" else W - bw
        ey = y + bh / 2
        sx = cx - cw / 2 if lado == "izq" else cx + cw / 2
        mx = (sx + ex) / 2
        curva = f"M{sx:.1f},{cy:.1f} C{mx:.1f},{cy:.1f} {mx:.1f},{ey:.1f} {ex:.1f},{ey:.1f}"
        geo["ramas"].append({**r, "x": x, "y": y, "w": bw, "h": bh, "curva": curva, "lado": lado})
    return geo


def geometria_tablero(b):
    """Sitúa las casillas en una pista curva alrededor de la ilustración central."""
    cantidad = len(b["casillas"])
    pesos = [72, 28, 72, 28]
    reparto = [cantidad * peso / sum(pesos) for peso in pesos]
    lados = [int(cuenta) for cuenta in reparto]
    for i in sorted(range(4), key=lambda lado: reparto[lado] - lados[lado], reverse=True)[:cantidad - sum(lados)]:
        lados[i] += 1
    puntos = []
    for lado, cuenta in enumerate(lados):
        for i in range(cuenta):
            t = (i + 0.5) / cuenta
            if lado == 0:
                x, y = 4 + 84 * t, 10
            elif lado == 1:
                x, y = 93, 20 + 60 * t
            elif lado == 2:
                x, y = 88 - 84 * t, 90
            else:
                x, y = 7, 80 - 60 * t
            puntos.append((x, y))

    curvas = []
    for i, (x, y) in enumerate(puntos):
        siguiente = puntos[(i + 1) % cantidad]
        anterior = puntos[(i - 1) % cantidad]
        posterior = puntos[(i + 2) % cantidad]
        c1 = (x + (siguiente[0] - anterior[0]) / 6, y + (siguiente[1] - anterior[1]) / 6)
        c2 = (siguiente[0] - (posterior[0] - x) / 6, siguiente[1] - (posterior[1] - y) / 6)
        if not curvas:
            curvas.append(f"M{x * 10:.1f},{y * 6:.2f}")
        curvas.append(
            f"C{c1[0] * 10:.1f},{c1[1] * 6:.2f} "
            f"{c2[0] * 10:.1f},{c2[1] * 6:.2f} "
            f"{siguiente[0] * 10:.1f},{siguiente[1] * 6:.2f}"
        )

    return {
        "casillas": [
            {**casilla, "x": x, "y": y}
            for casilla, (x, y) in zip(b["casillas"], puntos)
        ],
        "camino": " ".join(curvas),
    }


# --- Matemáticas: colores fijos de posición (M amarillo, E verde, H rojo, B azul) -------------
_POS_PALABRA = re.compile(r"\b([Mm]ilako|[Ee]huneko|[Hh]amarreko|[Bb]ateko)([a-z]*)")
_POS_LETRA = re.compile(r"(?<=\d)( ?)(HM|[MEHB])(?![\wÀ-ÿ])|(?<![\wÀ-ÿ.])(HM|[MEHB])(?![\wÀ-ÿ.])")
_POS_COLOR = {"m": "amarillo", "e": "verde", "h": "rojo", "b": "azul"}
_POS_SALTAR = {"h2", "h4", "th", "script", "style", "title", "textarea", "svg", "b"}


def colorear_posiciones(html: str) -> str:
    """Envuelve milako/ehuneko/hamarreko/bateko y las letras M E H B tras un número en <span class="pv pv-x">.
    Solo toca texto (no etiquetas ni atributos) y salta títulos, cabeceras y scripts."""
    partes = re.split(r"(<[^>]+>)", html)
    pila = []
    cuerpo = False
    for i, t in enumerate(partes):
        if t.startswith("<"):
            m = re.match(r"</?\s*([a-zA-Z0-9]+)", t)
            nombre = m.group(1).lower() if m else ""
            if nombre == "body" and not t.startswith("</"):
                cuerpo = True
            if nombre in _POS_SALTAR:
                if t.startswith("</"):
                    if pila:
                        pila.pop()
                elif not t.endswith("/>"):
                    pila.append(nombre)
            continue
        if not cuerpo or pila or not t.strip():
            continue
        t = _POS_PALABRA.sub(lambda m: f'<span class="pv pv-{m.group(1)[0].lower()}">{m.group(0)}</span>', t)
        t = _POS_LETRA.sub(lambda m: (m.group(1) or "") + f'<span class="pv pv-{(m.group(2) or m.group(3)).lower()}">{m.group(2) or m.group(3)}</span>', t)
        partes[i] = t
    return "".join(partes)


def color_posicion(titulo):
    """Color fijo si el título habla de milakoak / ehunekoak / hamarrekoak / batekoak."""
    m = re.search(r"(milako|ehuneko|hamarreko|bateko)", str(titulo or "").lower())
    return _POS_COLOR[m.group(1)[0]] if m else None


def colorear_bloques_mate(f):
    """En matemáticas, tarjetas, apartados y ramas del mapa que nombran una posición toman su color."""
    for h in f["hojas"]:
        for b in h["bloques"]:
            objetivos = [b] + list(b.get("items", []) if isinstance(b.get("items"), list) else []) + list(b.get("ramas", []))
            for o in objetivos:
                if isinstance(o, dict):
                    c = color_posicion(o.get("titulo"))
                    if c:
                        o["color"] = c


def preparar_fitxa(f, idioma="eu"):
    """Numera apartados y ejercicios por hoja y añade la hoja de soluciones."""
    hojas = []
    soluciones = []
    n_ej = n_par = 0
    for hi, h in enumerate(f["hojas"], 1):
        h = dict(h)
        n_ap = 0
        hojas_extra = []
        if not f.get("numeracion_continua"):
            n_ej = 0
        bloques = []
        for b in h["bloques"]:
            b = dict(b)
            if b["tipo"] == "txartelak":
                if bloques:
                    hojas.append({**h, "bloques": bloques})
                    bloques = []
                for inicio in range(0, len(b["items"]), 8):
                    items = b["items"][inicio:inicio + 8]
                    for alde in ("aurrea", "atzea"):
                        subtitulo = h.get("subtitulo", "")
                        hojas.append({
                            **h,
                            "subtitulo": f'{subtitulo + " · " if subtitulo else ""}{alde}aldeak · {inicio + 1}-{inicio + len(items)}',
                            "bloques": [{**b, "items": items, "alde": alde, "numero_desde": inicio}],
                        })
                continue
            if b["tipo"] == "flipbook":
                if bloques:
                    hojas.append({**h, "bloques": bloques})
                    bloques = []
                for i, pestana in enumerate(b["pestanas"]):
                    hojas.append({
                        **h,
                        "titulo": pestana["titulo"],
                        "bloques": [{
                            **b,
                            "pestanas": [pestana],
                            "orri_index": i,
                            "orri_total": len(b["pestanas"]),
                        }],
                    })
                continue
            if b["tipo"] == "mapa":
                b["geo"] = geometria_mapa(b)
            elif b["tipo"] == "tablero":
                b["geo"] = geometria_tablero(b)
            if b["tipo"] == "parrafo":
                n_par += 1
                b["n_parrafo"] = n_par
            elif b["tipo"] == "reto":
                n_ej += 1
                soluciones.append({"titulo": h["titulo"], "reto": b["reto"]})
            elif b["tipo"] == "apartado":
                n_ap += 1
                b["n"] = n_ap
            elif b["tipo"] == "ejercicio":
                n_ej += 1
                b["n"] = n_ej
                if b.get("modo") == "operaciones":
                    cab = b.get("cab") or ["", "H", "B"]
                    ncif = len(cab) - 1
                    b["ops"] = [{"cab": cab, "filas": [[""] + partir_numero(o["a"], ncif), [o["op"]] + partir_numero(o["b"], ncif)],
                                 "res": [""] * len(cab)} for o in b["items"]]
                if "solucion" in b:
                    sol = b["solucion"]
                    texto = " · ".join(sol) if isinstance(sol, list) else sol
                    ui = UI_FITXA[idioma]
                    pref = f"{hi}. {ui['orria']}, " if len(f["hojas"]) > 1 and not f.get("numeracion_continua") else ""
                    soluciones.append({"titulo": f"{pref}{n_ej}. {ui['ariketa']}:", "texto": texto})
            elif b["tipo"] == "tablero":
                for ci, txartela in enumerate(b["txartelak"], 1):
                    soluciones.append({
                        "titulo": f'{h["titulo"]} · {ci}. txartela:',
                        "texto": txartela["solucion"],
                    })
                items = [
                    {"aurrea": txartela["reto"], "atzea": txartela["solucion"]}
                    for txartela in b["txartelak"]
                ]
                for inicio in range(0, len(items), 8):
                    grupo = items[inicio:inicio + 8]
                    for alde in ("aurrea", "atzea"):
                        hojas_extra.append({
                            **h,
                            "titulo": "ERRONKA-TXARTELAK",
                            "subtitulo": "Moztu puntuetatik eta erabili jolasean.",
                            "bloques": [{
                                "tipo": "txartelak",
                                "items": grupo,
                                "alde": alde,
                                "numero_desde": inicio,
                            }],
                        })
            bloques.append(b)
        if bloques:
            h["bloques"] = bloques
            hojas.append(h)
        hojas.extend(hojas_extra)
    if f.get("soluciones") and soluciones:
        retos = any("reto" in x for x in soluciones)
        if retos:
            # Soluciones visuales: 6 por hoja
            for k in range(0, len(soluciones), 6):
                hojas.append({"titulo": UI_FITXA[idioma]["zuzenketa"], "subtitulo": UI_FITXA[idioma]["zuzenketa_sub"], "datos": False,
                              "bloques": [], "soluciones": soluciones[k:k + 6], "soluciones_retos": True, "color": f["color"]})
            return hojas
        hojas.append({"titulo": UI_FITXA[idioma]["zuzenketa"], "subtitulo": UI_FITXA[idioma]["zuzenketa_sub"], "datos": False,
                      "bloques": [], "soluciones": soluciones, "color": f["color"]})
    return hojas


def _normalizar_respuesta(texto):
    texto = re.sub(r"[*_]", "", str(texto)).strip().casefold()
    return re.sub(r"[.!?;:,]+$", "", texto).strip()


def _respuesta_literal(texto):
    texto = re.sub(r"[*_]", "", str(texto)).strip()
    return re.sub(r"[.!?;:,]+$", "", texto).strip()


def _coincide_respuesta(opcion, solucion):
    opcion_norm = _respuesta_literal(opcion)
    solucion_norm = _respuesta_literal(re.sub(r"^\s*[a-z]\)\s*", "", str(solucion), flags=re.IGNORECASE))
    return (solucion_norm == opcion_norm
            or solucion_norm.startswith(opcion_norm + " ("))


def _solucion_item(soluciones, item, indice, cantidad):
    if not isinstance(soluciones, list):
        return soluciones
    etiqueta = re.match(r"\s*([a-z]\))", str(item.get("texto", "")), re.IGNORECASE)
    if etiqueta:
        for solucion in soluciones:
            if str(solucion).strip().lower().startswith(etiqueta.group(1).lower()):
                return solucion
    if len(soluciones) == cantidad:
        return soluciones[indice]
    if len(soluciones) == 1:
        return soluciones[0]
    return None


def extraer_preguntas_jolasa(f, idioma="eu"):
    """Extrae preguntas con respuesta verificable para el juego de pizarra."""
    preguntas = []

    def añadir(pregunta, opciones, correcta, imagen=None):
        if not pregunta or not 2 <= len(opciones) <= 4 or correcta not in opciones:
            return
        pregunta = re.sub(r"[⭐★]+", "", pregunta)
        pregunta = re.sub(r"(^|\s)[a-h]\)(?=\s|$)", " ", pregunta)
        pregunta = re.sub(r"\s{2,}", " ", pregunta).strip()
        preguntas.append({
            "pregunta": pregunta,
            "opciones": opciones,
            "correcta": opciones.index(correcta),
            "imagen": imagen,
        })

    for hoja in f.get("hojas", []):
        for bloque in hoja.get("bloques", []):
            if bloque.get("tipo") == "txartelak":
                tarjetas = bloque.get("items", [])
                erantzunak = list(dict.fromkeys(t.get("atzea", "").strip() for t in tarjetas if t.get("atzea", "").strip()))
                for tarjeta in tarjetas:
                    zuzena = tarjeta.get("atzea", "").strip()
                    distractoreak = [e for e in erantzunak if _normalizar_respuesta(e) != _normalizar_respuesta(zuzena)][:3]
                    aukerak = [zuzena, *distractoreak]
                    gehitu = len(aukerak) >= 2
                    if gehitu:
                        añadir(tarjeta.get("aurrea", "").strip(), aukerak, zuzena, tarjeta.get("imagen"))
                continue
            if bloque.get("tipo") != "ejercicio":
                continue

            modo = bloque.get("modo")
            enuntziapena = bloque.get("enunciado", "").strip()
            if modo == "elegir":
                items = bloque.get("items", [])
                for i, item in enumerate(items):
                    texto = item.get("texto", "").strip()
                    pregunta = " ".join(x for x in (enuntziapena, texto) if x).strip()
                    solucion = _solucion_item(bloque.get("solucion"), item, i, len(items))
                    correcta = next((op for op in item.get("opciones", []) if solucion and _coincide_respuesta(op, solucion)), None)
                    añadir(pregunta, item.get("opciones", []), correcta, item.get("imagen"))
            elif modo == "verdadero_falso":
                etiquetas = bloque.get("etiquetas") or (["EGIA", "GEZURRA"] if idioma == "eu" else ["VERDADERO", "FALSO"])
                items = bloque.get("items", [])
                for i, item in enumerate(items):
                    solucion = _solucion_item(bloque.get("solucion"), {"texto": item}, i, len(items))
                    if not solucion:
                        continue
                    egia = re.search(r"\b(egia|verdadero)\b", str(solucion), re.IGNORECASE)
                    gezurra = re.search(r"\b(gezurra|falso)\b", str(solucion), re.IGNORECASE)
                    zuzena = etiquetas[0] if egia and not gezurra else etiquetas[1] if gezurra and not egia else None
                    añadir(" ".join(x for x in (enuntziapena, str(item).strip()) if x), etiquetas, zuzena)
            elif modo == "relacionar":
                ezkerra = bloque.get("izquierda", [])
                eskuina = bloque.get("derecha", [])
                soluzioak = bloque.get("solucion", [])
                loturak = {}
                if isinstance(soluzioak, str):
                    soluzioak = [soluzioak]
                for soluzioa in soluzioak:
                    aldeak = re.split(r"\s*(?:→|->)\s*", str(soluzioa), maxsplit=1)
                    if len(aldeak) == 2:
                        loturak[_normalizar_respuesta(aldeak[0])] = aldeak[1].strip()
                aukerak = list(dict.fromkeys(x.strip() for x in eskuina if x.strip()))
                for item in ezkerra:
                    zuzena = loturak.get(_normalizar_respuesta(item))
                    if zuzena not in aukerak:
                        continue
                    galderako_aukerak = [zuzena, *[x for x in aukerak if _normalizar_respuesta(x) != _normalizar_respuesta(zuzena)][:3]]
                    añadir(" — ".join(x for x in (enuntziapena, item.strip()) if x), galderako_aukerak, zuzena)

    # Matemáticas: operaciones y huecos numéricos → elegir entre 3 resultados cercanos.
    def num(t):
        t = str(t).strip().replace(".", "").replace(" ", "")
        return int(t) if re.fullmatch(r"-?\d+", t) else None

    def fmt(v):
        return f"{v:,}".replace(",", ".")

    def cercanos(v):
        opciones = [v]
        for d in ((10, -10, 100, -100, 1, -1) if abs(v) >= 100 else (1, -1, 10, -10, 2)):
            if len(opciones) == 3:
                break
            if v + d >= 0 and v + d not in opciones:
                opciones.append(v + d)
        return [fmt(o) for o in opciones]

    if materia(f.get("arlo", "")) == "matematika":
        for hoja in f.get("hojas", []):
            for bloque in hoja.get("bloques", []):
                if bloque.get("tipo") != "ejercicio":
                    continue
                if bloque.get("modo") == "operaciones":
                    for it in bloque.get("items", [])[:4]:
                        a_, b_ = num(it.get("a")), num(it.get("b"))
                        op = it.get("op")
                        if a_ is None or b_ is None or op not in ("+", "−", "-", "×", "x"):
                            continue
                        r = a_ + b_ if op == "+" else a_ - b_ if op in ("−", "-") else a_ * b_
                        ops = cercanos(r)
                        añadir(f"{fmt(a_)} {op} {fmt(b_)} = ?", ops, fmt(r))
                elif bloque.get("modo") == "completar":
                    sol = bloque.get("solucion")
                    frases = bloque.get("frases", [])
                    if not isinstance(sol, list) or len(sol) != len(frases):
                        continue
                    for fr, so in list(zip(frases, sol))[:4]:
                        v = num(so)
                        if v is None or str(fr).count("[ ]") + str(fr).count("___") != 1:
                            continue
                        pregunta = re.sub(r"\[ \]|___", "?", str(fr))
                        if not re.search(r"\d", pregunta):
                            continue
                        añadir(pregunta, cercanos(v), fmt(v))
    return preguntas


def _parte(texto):
    """«:fish:» → {"img": "fish"}; texto normal → {"txt": texto} (sin marcado)."""
    t = str(texto).strip()
    m = re.fullmatch(r":([a-z0-9-]+):", t)
    if m:
        return {"img": m.group(1)}
    icono = re.match(r":([a-z0-9-]+):\s*", t)
    limpio = re.sub(r":[a-z0-9-]+:\s*", "", t)
    limpio = re.sub(r"\*\*(.+?)\*\*", r"\1", limpio).replace("{", "").replace("}", "")
    limpio = re.sub(r"[⭐★]+", "", limpio).strip()
    d = {"txt": limpio}
    if icono:
        d["img"] = icono.group(1)
    return d


def _limpio_enunciado(t):
    return re.sub(r"\s{2,}", " ", re.sub(r"[⭐★]+|\*\*|[{}]", "", str(t))).strip()


def extraer_minijuegos(f):
    """Juegos «tocar y emparejar» para NEAE a partir de los ejercicios de la ficha:
    lotu (relacionar), sailkatu (clasificar) y memoria (imagen ↔ palabra)."""
    lotu, sailkatu, memoria = [], [], []
    n = _normalizar_respuesta

    def sin_icono(t):
        return re.sub(r"^\s*:[a-z0-9-]+:\s*", "", str(t))
    for hoja in f.get("hojas", []):
        for b in hoja.get("bloques", []):
            if b.get("tipo") == "txartelak":
                for t in b.get("items", []):
                    if t.get("imagen") and t.get("atzea") and len(t["atzea"].split()) <= 3:
                        memoria.append([t["imagen"], t["atzea"].strip()])
                continue
            if b.get("tipo") == "tarjetas":
                its = [t for t in b.get("items", []) if t.get("imagen") and t.get("titulo") and len(t["titulo"].split()) <= 2]
                if len(its) >= 4:
                    memoria += [[t["imagen"], re.sub(r"[{}*]", "", t["titulo"])] for t in its]
                continue
            if b.get("tipo") != "ejercicio":
                continue
            if b.get("modo") == "relacionar":
                izq, der, sol = b.get("izquierda", []), b.get("derecha", []), b.get("solucion", [])
                sol = [sol] if isinstance(sol, str) else sol
                pares = []
                for i, x in enumerate(izq):
                    destino = None
                    for sx in sol:
                        sx = str(sx).strip()
                        m = re.match(r"^(\d+)\.\s*(.+)$", sx)
                        if m and int(m.group(1)) == i + 1:
                            destino = m.group(2)
                        else:
                            lados = re.split(r"\s*(?:→|->)\s*", sx, maxsplit=1)
                            if len(lados) != 2:
                                lados = re.split(r":\s+", sx, maxsplit=1)
                            if len(lados) == 2 and n(sin_icono(lados[0])) == n(sin_icono(x)):
                                destino = lados[1]
                    match = next((d for d in der if destino and n(d) == n(destino)), None)
                    if match is None and destino:
                        import difflib
                        mejor = max(der, key=lambda d: difflib.SequenceMatcher(None, n(d), n(destino)).ratio(), default=None)
                        if mejor and difflib.SequenceMatcher(None, n(mejor), n(destino)).ratio() >= 0.6:
                            match = mejor
                    if match is None:
                        pares = []
                        break
                    pares.append([_parte(x), _parte(match)])
                if len(pares) >= 3:
                    lotu.append({"enunciado": _limpio_enunciado(b.get("enunciado", "")), "pares": pares[:6]})
                    for a_, d_ in pares:
                        if a_.get("img") and not a_.get("txt") and len(d_["txt"].split()) <= 3:
                            memoria.append([a_["img"], d_["txt"]])
            elif b.get("modo") == "clasificar":
                cols, sol = b.get("columnas", []), str(b.get("solucion", ""))
                trozos = re.findall(r"(?:^|[.·]\s+)([^:.·]+?):\s*([^·]+?)(?=(?:[.·]\s+[^:.·]+?:)|[.·]?\s*$)", sol)
                items = []
                for etiqueta, lista in trozos:
                    def comun(x, y):
                        k = 0
                        while k < min(len(x), len(y)) and x[k] == y[k]:
                            k += 1
                        return k
                    puntos = [comun(n(c), n(etiqueta)) for c in cols]
                    mejor = max(puntos) if puntos else 0
                    ci = puntos.index(mejor) if mejor >= min(3, len(n(etiqueta))) and puntos.count(mejor) == 1 else None
                    if ci is None:
                        continue
                    for w in re.split(r",\s*|\s+eta\s+|\s+y\s+", lista.strip(" .")):
                        if w.strip():
                            items.append([w.strip(), ci])
                palabras = {n(_parte(p)["txt"]): _parte(p) for p in b.get("palabras", [])}
                if palabras:
                    def buscar(w):
                        if n(w) in palabras:
                            return palabras[n(w)]
                        cand = [k for k in palabras if n(w) in k or k in n(w)]
                        return palabras[cand[0]] if len(cand) == 1 else None
                    items = [[buscar(w), c] for w, c in items]
                    vistos_p = set()
                    items = [it for it in items if it[0] and not (id(it[0]) in vistos_p or vistos_p.add(id(it[0])))]
                else:
                    items = [[{"txt": w}, c] for w, c in items]
                if len(items) >= 4 and len({c for _, c in items}) >= 2:
                    sailkatu.append({"enunciado": _limpio_enunciado(b.get("enunciado", "")),
                                     "columnas": [re.sub(r"[{}*]", "", c) for c in cols], "items": items[:9]})
    vistos, mem = set(), []
    for img, w in memoria:
        if n(w) not in vistos:
            vistos.add(n(w)); mem.append([img, w])
    return {"lotu": lotu, "sailkatu": sailkatu, "memoria": mem[:8] if len(mem) >= 4 else []}


def formato_enlaces(texto: str) -> Markup:
    """[texto](https://...) -> enlace que abre en otra pestaña."""
    html = str(escape(texto))
    html = re.sub(
        r"\[([^\]]+)\]\((https?://[^\s]+?)\)(?=[.,;:!?]?(\s|$))",
        r'<a href="\2" target="_blank" rel="noreferrer">\1</a>',
        html,
    )
    return Markup(html)


MAILAK_ACTIVAS = ("LH 1", "LH 3")


def materia(id_arlo: str) -> str:
    """«lh1-matematika» → «matematika»: mismo estilo y colores para todos los cursos."""
    return re.sub(r"^lh\d-", "", id_arlo or "")


def maila(a: dict) -> str:
    return a.get("maila", "LH 3")


# ---------- Validación ----------

def validar(arlos, secciones, materiales, ilustraciones):
    esquema = json.loads((CONTENIDO / "esquema-material.json").read_text(encoding="utf-8"))
    validador = jsonschema.Draft202012Validator(esquema)

    ids_arlo = {a["id"] for _, a in arlos if a}
    ids_seccion = {s["id"] for _, s in secciones if s}

    for ruta, a in arlos:
        if not a:
            continue
        if a.get("id") != ruta.stem:
            error(ruta, f'"id" debe ser "{ruta.stem}" (igual que el nombre del archivo)')
        if maila(a) not in MAILAK_ACTIVAS:
            error(ruta, f'"maila" debe ser uno de: {", ".join(MAILAK_ACTIVAS)}')
        if a.get("estado") not in ("activo", "preparando"):
            error(ruta, '"estado" debe ser "activo" o "preparando"')
        if a.get("estado") == "preparando":
            menu = a.get("pagina", {}).get("enlace_menu")
            if menu not in ids_arlo:
                error(ruta, f'"pagina.enlace_menu" = "{menu}" no es un arlo existente')

    for ruta, s in secciones:
        if not s:
            continue
        if s.get("tipo") != "pack" and not ("teoria" in s and "actividades" in s):
            error(ruta, 'una sección normal necesita "teoria" y "actividades" (o "tipo": "pack")')
        if s.get("id") != ruta.stem:
            error(ruta, f'"id" debe ser "{ruta.stem}"')
        if s.get("arlo") not in ids_arlo:
            error(ruta, f'"arlo" = "{s.get("arlo")}" no existe en contenido/arloak/')

    vistos = {}
    for ruta, m in materiales:
        if not m:
            continue
        for e in sorted(validador.iter_errors(m), key=lambda e: list(e.path)):
            donde = " → ".join(str(p) for p in e.path) or "(raíz)"
            error(ruta, f"{donde}: {traducir_error(e)}")
        if m.get("id") != ruta.stem:
            error(ruta, f'"id" debe ser "{ruta.stem}" (igual que el nombre del archivo)')
        if m.get("id") in vistos:
            error(ruta, f'el id "{m["id"]}" ya lo usa {vistos[m["id"]]}')
        vistos[m.get("id")] = ruta.name
        if m.get("arlo") not in ids_arlo:
            error(ruta, f'"arlo" = "{m.get("arlo")}" no existe')
        if m.get("seccion") not in ids_seccion:
            error(ruta, f'"seccion" = "{m.get("seccion")}" no existe en contenido/secciones/')

        for gi, g in enumerate(m.get("explicacion", {}).get("grupos", [])):
            for ri, r in enumerate(g.get("reglas", [])):
                for img in r.get("imagenes", []):
                    archivo = img.get("archivo", "")
                    if archivo.startswith("ilustracion:"):
                        if archivo.split(":", 1)[1] not in ilustraciones:
                            error(ruta, f"grupo {gi + 1}, regla {ri + 1}: la ilustración «{archivo}» no existe en contenido/ilustraciones/")
                    elif not (ESTATICO / "assets" / archivo).is_file():
                        error(ruta, f"grupo {gi + 1}, regla {ri + 1}: la imagen «{archivo}» no está en estatico/assets/")
                for ej in r.get("ejemplos", []):
                    if ej.count("{") != ej.count("}") or ej.count("_") % 2:
                        error(ruta, f"ejemplo «{ej}»: llaves {{ }} o guiones bajos _ sin cerrar")

        ids_juego = set()
        for juego in m.get("juegos", {}).get("lista", []):
            if juego.get("id") in ids_juego:
                error(ruta, f'dos juegos con el mismo id "{juego.get("id")}"')
            ids_juego.add(juego.get("id"))
            for pi, p in enumerate(juego.get("preguntas", [])):
                if p.get("ilustracion") not in ilustraciones:
                    error(ruta, f'juego "{juego.get("id")}", pregunta {pi + 1}: la ilustración «{p.get("ilustracion")}» no existe en contenido/ilustraciones/')


def traducir_error(e) -> str:
    v = e.validator
    if v == "required":
        return f"falta un campo obligatorio: {e.message.split(chr(39))[1]}"
    if v == "additionalProperties":
        return f"hay un campo que no existe en el esquema ({e.message.split('(')[-1].rstrip(')')})"
    if v == "maxLength":
        return f"texto demasiado largo (máximo {e.validator_value} caracteres): «{e.instance}»"
    if v == "minLength":
        return f"texto demasiado corto (mínimo {e.validator_value} caracteres)"
    if v in ("minItems", "maxItems"):
        return f"número de elementos fuera de rango ({v}: {e.validator_value}, hay {len(e.instance)})"
    if v == "enum":
        return f"valor no permitido «{e.instance}». Opciones: {', '.join(e.validator_value)}"
    if v == "pattern":
        return f"«{e.instance}» debe ir en minúsculas, sin espacios ni tildes (usa guiones)"
    if v == "uniqueItems":
        return "las opciones no pueden repetirse"
    if v in ("maximum", "minimum"):
        return f"valor fuera de rango: {e.instance} ({'máximo' if v == 'maximum' else 'mínimo'} {e.validator_value})"
    return e.message


# ---------- Generación ----------

def construir(solo_comprobar: bool) -> None:
    arlos = cargar("arloak")
    secciones = cargar("secciones")
    materiales = cargar("materiales")
    fitxak = cargar("fitxak") if (CONTENIDO / "fitxak").is_dir() else []
    ilustraciones = {p.stem: p.read_text(encoding="utf-8").strip() for p in sorted((CONTENIDO / "ilustraciones").glob("*.svg"))}

    validar(arlos, secciones, materiales, ilustraciones)
    validador_fitxa = jsonschema.Draft202012Validator(json.loads((CONTENIDO / "esquema-fitxa.json").read_text(encoding="utf-8")))
    ids_usados = {m.get("id") for _, m in materiales}
    for ruta, f in fitxak:
        if f:
            validar_fitxa(ruta, f, {a.get("id") for _, a in arlos}, {s.get("id") for _, s in secciones}, validador_fitxa)
            if f.get("relacionada") and f["relacionada"] not in {x.get("id") for _, x in fitxak}:
                error(ruta, f'"relacionada" = "{f["relacionada"]}" no es ninguna ficha de contenido/fitxak/')
            if f.get("id") in ids_usados:
                error(ruta, f'el id "{f["id"]}" ya lo usa otro material o ficha')
            ids_usados.add(f.get("id"))
    if errores:
        print("\nHay que arreglar el contenido antes de publicar:\n")
        print("\n".join(errores))
        print(f"\n{len(errores)} problema(s). No se ha publicado nada.\n")
        sys.exit(1)

    arlos_l = sorted((a for _, a in arlos), key=lambda a: a["orden"])
    arlos_por_id = {a["id"]: a for a in arlos_l}
    secciones_l = sorted((s for _, s in secciones), key=lambda s: s["orden"])
    publicados = sorted((m for _, m in materiales if m["publicado"]), key=lambda m: m["orden"])
    borradores = [m["id"] for _, m in materiales if not m["publicado"]]
    hoy = os.environ.get("KIMU_FECHA") or date.today().isoformat()
    programadas = [f["id"] for _, f in fitxak if f.get("publicar_desde", "") > hoy]
    fitxak_l = sorted((f for _, f in fitxak if f.get("publicar_desde", "") <= hoy), key=lambda f: (f["orden"], f.get("lugar") == "actividades"))
    fitxak_pub = [f for f in fitxak_l if f["publicado"]]
    fitxak_por_id = {f["id"]: f for f in fitxak_l}
    borradores += [f["id"] for f in fitxak_l if not f["publicado"]]

    if solo_comprobar:
        print(f"✓ Contenido correcto: {len(arlos_l)} arlo, {len(secciones_l)} sección(es), "
              f"{len(publicados)} material(es) publicado(s), {len(borradores)} borrador(es).")
        return

    env = Environment(loader=FileSystemLoader(PLANTILLAS), autoescape=True,
                      keep_trailing_newline=True)
    env.filters["ejemplo"] = formato_ejemplo
    env.filters["enlaces"] = formato_enlaces
    env.filters["marcado"] = formato_marcado

    def etiqueta_ilustracion(nombre):
        m = re.search(r'aria-label="([^"]+)"', ilustraciones[nombre])
        return m.group(1) if m else nombre

    def imagen(img, perezosa=False):
        archivo = img["archivo"]
        if archivo.startswith("ilustracion:"):
            return Markup(ilustraciones[archivo.split(":", 1)[1]])
        estilo = f' style="object-position: {escape(img["encuadre"])}"' if img.get("encuadre") else ""
        lazy = ' loading="lazy"' if perezosa else ""
        return Markup(f'<img src="assets/{escape(archivo)}" alt="{escape(img["alt"])}"{estilo}{lazy} decoding="async">')

    def nombre_en(arlo, idioma):
        return arlo.get("nombre_es", arlo["nombre"]) if idioma == "es" else arlo["nombre"]

    kimu = Markup((ESTATICO / "kimu.svg").read_text(encoding="utf-8").strip())
    import hashlib
    ver = hashlib.sha1(b''.join(f.read_bytes() for f in sorted(ESTATICO.glob('*.*')) if f.suffix in ('.css', '.js'))).hexdigest()[:8]
    import math
    env.filters['cos_'] = lambda x: round(math.cos(x), 3)
    env.filters['sin_'] = lambda x: round(math.sin(x), 3)
    import segno

    def qr(url):
        """Código QR en SVG (negro sobre blanco) para imprimir en las fichas."""
        buf = io.BytesIO()
        segno.make(url, error="m").save(buf, kind="svg", scale=4, border=1, xmldecl=False, svgns=True, nl=False)
        return Markup(buf.getvalue().decode())

    def audio_existe(nombre):
        return (ESTATICO / "audioak" / f"{nombre}.mp3").is_file()

    env.globals.update(qr=qr, audio_existe=audio_existe)
    env.globals.update(kofi="",  # Ko-fi en pausa (pendiente). Para activarlo: kofi="https://ko-fi.com/ikeribarretxe"
                        url_base="https://keript.github.io/kimu-ikas-materialak/", ver=ver, ilustraciones_fitxa={k: Markup(v) for k, v in ilustraciones.items()}, kimu=kimu, etiqueta_ilustracion=etiqueta_ilustracion, imagen=imagen, nombre_en=nombre_en,
                       arlos=arlos_l, arlos_por_id=arlos_por_id, materia=materia, maila=maila,
                       arlos_lh3=[a for a in arlos_l if maila(a) == "LH 3"],
                       arlos_lh1=[a for a in arlos_l if maila(a) == "LH 1"])

    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    shutil.copytree(ESTATICO, SALIDA)
    paginas = []

    def escribir(nombre, plantilla, **datos):
        html = env.get_template(plantilla).render(pagina_actual=nombre, **datos)
        if plantilla == "fitxa.html" and materia(datos.get("arlo", {}).get("id", "")) == "matematika":
            html = colorear_posiciones(html)
        (SALIDA / nombre).write_text(html, encoding="utf-8")
        paginas.append(nombre)

    escribir("index.html", "inicio.html")
    lh1 = [a for a in arlos_l if maila(a) == "LH 1"]
    if lh1:
        escribir("lh-1.html", "mosaico.html", idioma="eu", descripcion_meta="Kimu LH 1: euskarazko fitxa bisualak 1. mailarako (letrak, zenbakiak, ingurunea), NEAE ikasleak kontuan hartuta.",
                 titulo_pestana="LH 1", volver={"url": "index.html#mailak", "texto": "Mailak"}, volver_abajo=None,
                 antetitulo="Kimu · Lehen Hezkuntza", titulo="LH 1", titulo_resalte="1. maila.",
                 intro="Letrak banan-banan, zenbakiak 100 arte eta gure ingurunea. Irudi errealak, letra handia eta adibide bat ariketa bakoitzean.",
                 etiqueta_grupo="nav", etiqueta_accesible="LH 1 arloak",
                 tarjetas=[{"url": f'{a["id"]}.html', "icono": a["icono"], "nombre": a["nombre"],
                            "texto": a["tarjeta_inicio"]["texto"] + (" 🌱 Prestatzen." if a["estado"] == "preparando" else ""),
                            "boton": a["tarjeta_inicio"]["boton"]} for a in lh1])

    for a in arlos_l:
        if a["estado"] == "preparando":
            ui = UI[a["idioma"]]
            escribir(f'{a["id"]}.html', "arlo_preparando.html", a=a, ui=ui, ui_js=ui["js"])
            continue
        secs = [s for s in secciones_l if s["arlo"] == a["id"]
                and (s.get("tipo") != "pack" or any(f["seccion"] == s["id"] for f in fitxak_pub))]
        p = a["pagina"]
        escribir(f'{a["id"]}.html', "mosaico.html", idioma=a["idioma"], descripcion_meta=p["descripcion_meta"],
                 titulo_pestana=a.get("nombre_es", a["nombre"]) if a["idioma"] == "es" else a["nombre"],
                 volver={"url": "lh-1.html", "texto": "LH 1"} if maila(a) == "LH 1" else {"url": "index.html", "texto": "Áreas" if a["idioma"] == "es" else "Arloak"}, volver_abajo=None,
                 antetitulo=p["antetitulo"], titulo=p["titulo"], titulo_resalte=p["titulo_resalte"], intro=p["intro"],
                 etiqueta_grupo="nav", etiqueta_accesible=f'{a["nombre"]} atal nagusiak',
                 tarjetas=[{"url": f'{s["id"]}.html', "icono": s["icono"], "nombre": s["nombre"],
                            "texto": s["tarjeta_arlo"]["texto"], "boton": s["tarjeta_arlo"]["boton"]} for s in secs])

    TIPO_ES = {"Gaiaren laburpena": "Resumen del tema", "Pausoz pauso": "Paso a paso", "Idazketa-txantiloia": "Plantilla de escritura",
               "Horma-irudia": "Póster", "Ariketa-fitxa": "Ficha de ejercicios", "Irakurmena": "Comprensión lectora"}

    def tarjeta_fitxa(f, idioma="eu"):
        tipo = TIPO_ES.get(f["tipo_material"], f["tipo_material"]) if idioma == "es" else f["tipo_material"]
        return {"url": f'{f["id"]}.html', "icono": f["icono"], "nombre": f["nombre"],
                "texto": f'{tipo} · {f["curso"]}. {f["resumen"]}', "boton": "Ver ficha" if idioma == "es" else "Ikusi fitxa"}

    for s in secciones_l:
        a = arlos_por_id[s["arlo"]]
        mats = [m for m in publicados if m["seccion"] == s["id"]]
        fx_sec = [f for f in fitxak_pub if f["seccion"] == s["id"]]
        volver_arlo = {"url": f'{a["id"]}.html', "texto": a["nombre"]}
        volver_sec = {"url": f'{s["id"]}.html', "texto": s["nombre"]}

        def escribir_fitxak(volver, lista):
            for f in lista:
                if materia(f["arlo"]) == "matematika":
                    f = copy.deepcopy(f)
                    colorear_bloques_mate(f)
                hojas = preparar_fitxa(f, a["idioma"])
                preguntas_jolasa = extraer_preguntas_jolasa(f, a["idioma"])
                mini = extraer_minijuegos(f) if a["idioma"] == "eu" else {"lotu": [], "sailkatu": [], "memoria": []}
                hay_juego = bool(preguntas_jolasa or mini["lotu"] or mini["sailkatu"] or mini["memoria"])
                f2 = dict(f, hojas_render=hojas, compa=fitxak_por_id.get(f.get("relacionada")),
                          jolasa=hay_juego)
                escribir(f'{f["id"]}.html', "fitxa.html", f=f2, arlo=a, seccion=s, idioma=a["idioma"], ui=UI_FITXA[a["idioma"]],
                         ui_jolasa=UI_JOLASA[a["idioma"]], borrador=not f["publicado"], descripcion_meta=f["descripcion_meta"], titulo_pestana=f["nombre"],
                         volver=volver, volver_abajo=volver, hojas_alumno=sum(1 for h in hojas if not h.get("soluciones")),
                         hojas_docente=any(h.get("soluciones") for h in hojas))
                if hay_juego:
                    escribir(f'{f["id"]}-jolasa.html', "jolasa.html", idioma=a["idioma"], borrador=not f["publicado"],
                             descripcion_meta=f["descripcion_meta"], titulo_pestana=f'{f["nombre"]}: {UI_JOLASA[a["idioma"]]["game_title"]}',
                             volver={"url": f'{f["id"]}.html', "texto": f["nombre"]},
                             f=f, ui_jolasa=UI_JOLASA[a["idioma"]],
                             mini=mini, datos_juego={"titulo": f["nombre"], "preguntas": preguntas_jolasa, "ui": UI_JOLASA[a["idioma"]], **mini})

        fx_todas = [f for f in fitxak_l if f["seccion"] == s["id"]]
        if s.get("tipo") == "pack":
            # Sección-pack: su página lista directamente las fichas.
            escribir(f'{s["id"]}.html', "mosaico.html", idioma=a["idioma"], descripcion_meta=s["pagina"]["descripcion_meta"],
                     titulo_pestana=s["nombre"], volver=volver_arlo,
                     volver_abajo={"url": volver_arlo["url"], "texto": f'{a["nombre"]} arlora'},
                     antetitulo=f'{a["nombre"]} · {s["nombre"]}', titulo=s["pagina"]["titulo"],
                     titulo_resalte=s["pagina"]["titulo_resalte"], intro=s["pagina"]["intro"],
                     etiqueta_grupo="section", etiqueta_accesible=f'{s["nombre"]}: fitxak',
                     tarjetas=[tarjeta_fitxa(f, a["idioma"]) for f in fx_sec])
            escribir_fitxak(volver_sec, fx_todas)
            continue

        teo, act = s["teoria"], s["actividades"]
        escribir_fitxak({"url": teo["archivo"], "texto": teo["nombre"]}, fx_todas)
        escribir(f'{s["id"]}.html', "mosaico.html", idioma=a["idioma"], descripcion_meta=s["pagina"]["descripcion_meta"],
                 titulo_pestana=s["nombre"], volver=volver_arlo,
                 volver_abajo={"url": volver_arlo["url"], "texto": f'{a["nombre"]} arlora'},
                 antetitulo=f'{a["nombre"]} · {s["nombre"]}', titulo=s["pagina"]["titulo"],
                 titulo_resalte=s["pagina"]["titulo_resalte"], intro=s["pagina"]["intro"],
                 etiqueta_grupo="nav", etiqueta_accesible=f'{s["nombre"]} aukerak',
                 tarjetas=[{"url": teo["archivo"], "icono": teo["icono"], "nombre": teo["nombre"], "texto": teo["texto"], "boton": teo["boton"]},
                           {"url": act["archivo"], "icono": act["icono"], "nombre": act["nombre"], "texto": act["texto"], "boton": act["boton"]}])
        escribir(teo["archivo"], "mosaico.html", idioma=a["idioma"], descripcion_meta=teo["descripcion_meta"],
                 titulo_pestana=teo["nombre"], volver=volver_sec, volver_abajo=volver_sec,
                 antetitulo=f'{a["nombre"]} · {teo["nombre"]}', titulo=teo["nombre"], titulo_resalte=teo["titulo_resalte"],
                 intro=teo["intro"], etiqueta_grupo="section", etiqueta_accesible=f'{s["nombre"]}-arauak',
                 tarjetas=[tarjeta_fitxa(f, a["idioma"]) for f in fx_sec if f.get("lugar", "teoria") == "teoria"] +
                          [{"url": f'{m["id"]}.html', "icono": m["icono"], "nombre": m["nombre"], "texto": m["resumen"],
                            "boton": "Ikusi araua"} for m in mats])
        escribir(act["archivo"], "mosaico.html", idioma=a["idioma"], descripcion_meta=act["descripcion_meta"],
                 titulo_pestana=act["nombre"], volver=volver_sec, volver_abajo=volver_sec,
                 antetitulo=f'{s["nombre"]} · {act["nombre"]}', titulo=act["titulo"], titulo_resalte=act["titulo_resalte"],
                 intro=act["intro"], etiqueta_grupo="section", etiqueta_accesible=f'{s["nombre"]}: jarduerak',
                 tarjetas=[tarjeta_fitxa(f, a["idioma"]) for f in fx_sec if f.get("lugar") == "actividades"] +
                          [{"url": f'{m["id"]}-jolasak.html', "icono": m["icono"], "nombre": m["nombre"],
                            "texto": f'{len(m["juegos"]["lista"])} jolas eta inprimatzeko fitxak.', "boton": "Jolastu"} for m in mats])

        # Los borradores (publicado: false) también se generan, pero sin enlaces desde
        # ningún menú y ocultos a los buscadores: sirven de vista previa para revisarlos.
        mats_borrador = sorted((m for _, m in materiales if not m["publicado"] and m["seccion"] == s["id"]),
                               key=lambda m: m["orden"])
        for m in mats + mats_borrador:
            borrador = not m["publicado"]
            escribir(f'{m["id"]}.html', "explicacion.html", m=m, idioma=a["idioma"], borrador=borrador,
                     descripcion_meta=m["explicacion"]["descripcion_meta"], titulo_pestana=m["nombre"],
                     volver={"url": teo["archivo"], "texto": teo["nombre"]},
                     volver_abajo={"url": teo["archivo"], "texto": teo["nombre"]})
            usadas = sorted({p["ilustracion"] for j in m["juegos"]["lista"] for p in j["preguntas"]})
            datos_juego = {"material": m["id"], "ilustraciones": {n: ilustraciones[n] for n in usadas},
                           "juegos": [{k: j[k] for k in ("id", "tipo", "acierto", "error", "preguntas")} for j in m["juegos"]["lista"]]}
            escribir(f'{m["id"]}-jolasak.html', "juegos.html", m=m, j=m["juegos"], idioma=a["idioma"], borrador=borrador,
                     descripcion_meta=m["juegos"]["descripcion_meta"], titulo_pestana=f'{m["nombre"]}: jolasak',
                     volver={"url": f'{m["id"]}.html', "texto": m["nombre"]},
                     volver_abajo={"url": act["archivo"], "texto": act["nombre"]}, datos_juego=datos_juego)

    print(f"✓ Web generada en _site/ ({len(paginas)} páginas, {len(publicados) + len(fitxak_pub)} material(es) publicados).")
    if programadas:
        print("  Programadas (aún no se publican): " + ", ".join(programadas))
    if borradores:
        print("  Borradores (vista previa sin enlaces): " + ", ".join(f"{b}.html" for b in borradores))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genera la web de Kimu.")
    parser.add_argument("--check", action="store_true", help="solo valida el contenido, no genera nada")
    construir(parser.parse_args().check)
