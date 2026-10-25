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
import json
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
    """Texto de fichas: {X} resaltado, **negrita**, _cursiva_, ___ hueco para escribir, [ ] casilla."""
    html = str(escape(str(texto)))
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


def partir_numero(n, columnas):
    """'38' con 2 columnas de cifras -> ['3','8']; rellena por la izquierda con ''."""
    cifras = list(str(n))
    return [""] * (columnas - len(cifras)) + cifras


BLOQUES = {
    "objetivos": ["items"], "apartado": ["titulo"], "tarjetas": ["items"], "tabla": ["cabecera", "filas"],
    "lectura": ["titulo", "parrafos"], "ejercicio": ["enunciado", "modo"], "idazketa": ["partes"],
    "pasos": ["items"], "ilustracion": ["archivo"], "parrafo": ["texto"], "mapa": ["centro", "ramas"], "reto": ["reto"], "gogoratu": ["texto"], "berrikusi": ["items"], "dibujo": [], "nota": ["texto"], "relleno": [],
}
MODOS = {
    "lineas": [], "completar": ["frases"], "elegir": ["items"], "verdadero_falso": ["items"], "preguntas": ["items"],
    "relacionar": ["izquierda", "derecha"], "corregir": ["frases"], "clasificar": ["columnas"], "operaciones": ["items"],
}


def imagenes_usadas(obj):
    """Todos los valores de campos "imagen" (y :nombre: en textos) de una ficha."""
    usadas = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "imagen" and isinstance(v, str):
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


def preparar_fitxa(f, idioma="eu"):
    """Numera apartados y ejercicios por hoja y añade la hoja de soluciones."""
    hojas = []
    soluciones = []
    n_ej = n_par = 0
    for hi, h in enumerate(f["hojas"], 1):
        h = dict(h)
        n_ap = 0
        if not f.get("numeracion_continua"):
            n_ej = 0
        bloques = []
        for b in h["bloques"]:
            b = dict(b)
            if b["tipo"] == "mapa":
                b["geo"] = geometria_mapa(b)
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
                    cab = b.get("cab") or ["", "H", "U"]
                    ncif = len(cab) - 1
                    b["ops"] = [{"cab": cab, "filas": [[""] + partir_numero(o["a"], ncif), [o["op"]] + partir_numero(o["b"], ncif)],
                                 "res": [""] * len(cab)} for o in b["items"]]
                if "solucion" in b:
                    sol = b["solucion"]
                    texto = " · ".join(sol) if isinstance(sol, list) else sol
                    ui = UI_FITXA[idioma]
                    pref = f"{hi}. {ui['orria']}, " if len(f["hojas"]) > 1 and not f.get("numeracion_continua") else ""
                    soluciones.append({"titulo": f"{pref}{n_ej}. {ui['ariketa']}:", "texto": texto})
            bloques.append(b)
        h["bloques"] = bloques
        hojas.append(h)
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


def formato_enlaces(texto: str) -> Markup:
    """[texto](https://...) -> enlace que abre en otra pestaña."""
    html = str(escape(texto))
    html = re.sub(
        r"\[([^\]]+)\]\((https?://[^\s]+?)\)(?=[.,;:!?]?(\s|$))",
        r'<a href="\2" target="_blank" rel="noreferrer">\1</a>',
        html,
    )
    return Markup(html)


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
        return f"valor fuera de rango: {e.instance} (debe estar entre 0 y {e.validator_value if v == 'maximum' else '...'})"
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
    fitxak_l = sorted((f for _, f in fitxak), key=lambda f: (f["orden"], f.get("lugar") == "actividades"))
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
    env.globals.update(ilustraciones_fitxa={k: Markup(v) for k, v in ilustraciones.items()}, kimu=kimu, etiqueta_ilustracion=etiqueta_ilustracion, imagen=imagen, nombre_en=nombre_en,
                       arlos=arlos_l, arlos_por_id=arlos_por_id)

    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    shutil.copytree(ESTATICO, SALIDA)
    paginas = []

    def escribir(nombre, plantilla, **datos):
        html = env.get_template(plantilla).render(**datos)
        (SALIDA / nombre).write_text(html, encoding="utf-8")
        paginas.append(nombre)

    escribir("index.html", "inicio.html")

    for a in arlos_l:
        if a["estado"] == "preparando":
            ui = UI[a["idioma"]]
            escribir(f'{a["id"]}.html', "arlo_preparando.html", a=a, ui=ui, ui_js=ui["js"])
            continue
        secs = [s for s in secciones_l if s["arlo"] == a["id"]
                and (s.get("tipo") != "pack" or any(f["seccion"] == s["id"] for f in fitxak_pub))]
        p = a["pagina"]
        escribir(f'{a["id"]}.html', "mosaico.html", idioma=a["idioma"], descripcion_meta=p["descripcion_meta"],
                 titulo_pestana=a.get("nombre_es", a["nombre"]) if a["idioma"] == "es" else a["nombre"], volver={"url": "index.html", "texto": "Áreas" if a["idioma"] == "es" else "Arloak"}, volver_abajo=None,
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
                hojas = preparar_fitxa(f, a["idioma"])
                f2 = dict(f, hojas_render=hojas, compa=fitxak_por_id.get(f.get("relacionada")))
                escribir(f'{f["id"]}.html', "fitxa.html", f=f2, arlo=a, seccion=s, idioma=a["idioma"], ui=UI_FITXA[a["idioma"]],
                         borrador=not f["publicado"], descripcion_meta=f["descripcion_meta"], titulo_pestana=f["nombre"],
                         volver=volver, volver_abajo=volver, hojas_alumno=sum(1 for h in hojas if not h.get("soluciones")),
                         hojas_docente=any(h.get("soluciones") for h in hojas))

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
    if borradores:
        print("  Borradores (vista previa sin enlaces): " + ", ".join(f"{b}.html" for b in borradores))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genera la web de Kimu.")
    parser.add_argument("--check", action="store_true", help="solo valida el contenido, no genera nada")
    construir(parser.parse_args().check)
