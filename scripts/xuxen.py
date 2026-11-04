#!/usr/bin/env python3
"""Revisa el vocabulario de los materiales en euskera con Hunspell y Xuxen."""

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
RUTAS_CONTENIDO = ("contenido/fitxak", "contenido/secciones", "contenido/arloak")
URL_API = "https://xuxenapi.elhuyar.eus"
MAX_CARACTERES_API = 5000
PAUSA_API = 1
PALABRAS = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", re.UNICODE)
URLS = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
ICONOS = re.compile(r":[\w-]+:")
MARCAS = re.compile(r"\{[^}]*\}")
SIGLAS = re.compile(r"(?<!\w)[A-ZÁÉÍÓÚÜÑ]{2,}[a-záéíóúüñ]*(?!\w)")
NUMEROS = re.compile(r"(?<!\w)\d+[^\W\d_]*", re.UNICODE)
IDENTIFICADORES = re.compile(r"(?<!\w)[\w-]*\d[\w-]*(?!\w)", re.UNICODE)
HUECOS = re.compile(r"\w*_{2,}\w*", re.UNICODE)
SILABAS = re.compile(r"(?<!\w)(?:[^\W\d_]+-){2,}[^\W\d_]+(?!\w)", re.UNICODE)
ORACIONES = re.compile(r"(?<=[.!?…])\s+|\n+")
CLAVES_NO_TEXTUALES = {
    "id",
    "arlo",
    "seccion",
    "tipo",
    "modo",
    "imagen",
    "color",
    "icono",
    "archivo",
    "dir",
    "idioma",
    "estado",
    "lugar",
    "curso",
    "orden",
    "tamano",
    "ancho",
    "simbolos",
    "ikonoa",
    "url",
    "src",
    "orientacion",
    "creditos_imagenes",
    "creditos",
}


def nombre_relativo(ruta):
    try:
        return ruta.resolve().relative_to(RAIZ).as_posix()
    except ValueError:
        return ruta.as_posix()


def archivos_contenido(paths=None):
    if paths is not None:
        return [Path(path) if Path(path).is_absolute() else RAIZ / path for path in paths]
    return sorted(
        ruta
        for carpeta in RUTAS_CONTENIDO
        for ruta in (RAIZ / carpeta).glob("*.json")
    )


def cargar_json(ruta, base_ref=None):
    ruta_relativa = nombre_relativo(ruta)
    if base_ref:
        resultado = subprocess.run(
            ["git", "show", f"{base_ref}:{ruta_relativa}"],
            cwd=RAIZ,
            capture_output=True,
            text=True,
            check=False,
        )
        if resultado.returncode:
            return None
        contenido = resultado.stdout
    else:
        try:
            contenido = ruta.read_text(encoding="utf-8")
        except OSError:
            return None
    try:
        return json.loads(contenido)
    except json.JSONDecodeError:
        return None


def extraer_textos(ruta, base_ref=None):
    """Devuelve fragmentos lingüísticos con el archivo y la frase de origen."""
    datos = cargar_json(ruta, base_ref)
    if not isinstance(datos, dict):
        return []
    if datos.get("arlo") == "gaztelera" or datos.get("id") == "gaztelera":
        return []

    fragmentos = []

    def recorrer(valor, clave=None):
        if clave in CLAVES_NO_TEXTUALES or (clave and clave.endswith("_es")):
            return
        if isinstance(valor, dict):
            for nombre, contenido in valor.items():
                recorrer(contenido, nombre)
        elif isinstance(valor, list):
            for contenido in valor:
                recorrer(contenido)
        elif isinstance(valor, str):
            if limpiar_texto(valor):
                fragmentos.append(valor)

    recorrer(datos)
    return fragmentos


def limpiar_texto(texto):
    texto = URLS.sub(" ", texto)
    texto = ICONOS.sub(" ", texto)
    texto = MARCAS.sub(lambda marca: marca.group(0)[1:-1], texto)
    texto = HUECOS.sub(" ", texto)
    texto = SILABAS.sub(" ", texto)
    texto = SIGLAS.sub(" ", texto)
    texto = IDENTIFICADORES.sub(" ", texto)
    texto = NUMEROS.sub(" ", texto)
    return texto.strip()


def tokens(texto):
    return PALABRAS.findall(limpiar_texto(texto))


def ignorar_palabra(palabra, permitidas):
    return len(palabra) >= 2 and palabra.isupper() or palabra.casefold() in permitidas


def _frase_con_palabra(fragmentos, palabra):
    for texto in fragmentos:
        for oracion in ORACIONES.split(texto):
            if any(token.casefold() == palabra.casefold() for token in tokens(oracion)):
                return oracion.strip()
    return palabra


def palabras_desconocidas_por_archivo(archivos, permitidas, base_ref=None):
    textos = {
        nombre_relativo(ruta): extraer_textos(ruta, base_ref)
        for ruta in archivos
    }
    entradas = [
        limpiar_texto(texto)
        for fragmentos in textos.values()
        for texto in fragmentos
    ]
    if not entradas:
        return {archivo: set() for archivo in textos}
    resultado = subprocess.run(
        ["hunspell", "-d", "eu_ES", "-l"],
        input="\n".join(entradas),
        capture_output=True,
        text=True,
        check=False,
    )
    if resultado.returncode:
        raise RuntimeError(resultado.stderr.strip() or "Hunspell no pudo revisar el contenido.")
    desconocidas = {
        palabra.strip().casefold()
        for palabra in resultado.stdout.splitlines()
        if palabra.strip() and not ignorar_palabra(palabra.strip(), permitidas)
    }
    return {
        archivo: {
            palabra.casefold()
            for texto in fragmentos
            for palabra in tokens(texto)
            if palabra.casefold() in desconocidas and not ignorar_palabra(palabra, permitidas)
        }
        for archivo, fragmentos in textos.items()
    }


def revisar_hunspell(archivos, permitidas):
    """Conserva el archivo y la frase de cada palabra desconocida."""
    desconocidas = palabras_desconocidas_por_archivo(archivos, permitidas)
    hallazgos = []
    for ruta in archivos:
        fragmentos = extraer_textos(ruta)
        for palabra in sorted(desconocidas.get(nombre_relativo(ruta), set())):
            hallazgos.append(
                {
                    "archivo": nombre_relativo(ruta),
                    "palabra": palabra,
                    "frase": _frase_con_palabra(fragmentos, palabra),
                }
            )
    return hallazgos


def filtrar_palabras_nuevas(hallazgos, palabras_base):
    return [
        hallazgo
        for hallazgo in hallazgos
        if hallazgo["palabra"].casefold() not in palabras_base.get(hallazgo["archivo"], set())
    ]


def archivos_cambiados(base_ref):
    resultado = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD", "--", *RUTAS_CONTENIDO],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        check=True,
    )
    return [RAIZ / linea for linea in resultado.stdout.splitlines() if linea.endswith(".json")]


def dividir_texto(texto, limite=MAX_CARACTERES_API):
    """Divide el texto en partes que respetan el máximo de caracteres de la API."""
    partes = []
    restante = texto
    while len(restante) > limite:
        corte = restante.rfind("\n", 0, limite + 1)
        if corte <= 0:
            corte = restante.rfind(" ", 0, limite + 1)
        if corte <= 0:
            corte = limite
        partes.append(restante[:corte])
        restante = restante[corte:].lstrip()
    if restante:
        partes.append(restante)
    return partes


def frase_en_offset(texto, offset, longitud):
    inicio = max(0, min(len(texto), offset))
    fin = min(len(texto), inicio + max(longitud, 1))
    antes = max((texto.rfind(marca, 0, inicio) for marca in ".!?\n"), default=-1)
    despues = min(
        (pos for marca in ".!?\n" if (pos := texto.find(marca, fin)) >= 0),
        default=len(texto),
    )
    return texto[antes + 1 : despues].strip() or texto[inicio:fin].strip()


def es_correccion_ortografica(tipo):
    tipo = str(tipo or "").casefold()
    return any(marca in tipo for marca in ("orto", "spelling", "orthograph"))


def revisar_api(archivos):
    """Consulta Xuxen solo para los textos cambiados; sus fallos son informativos."""
    errores = []
    avisos = []
    bloqueos = []
    llamadas = 0
    for ruta in archivos:
        fragmentos = extraer_textos(ruta)
        texto_ficha = "\n".join(limpiar_texto(fragmento) for fragmento in fragmentos)
        for parte in dividir_texto(texto_ficha):
            if llamadas:
                time.sleep(PAUSA_API)
            peticion = urllib.request.Request(
                URL_API,
                data=json.dumps(
                    {"text": parte, "conf": {"GENC": True, "AIC": True}}
                ).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(peticion, timeout=15) as respuesta:
                    datos = json.loads(respuesta.read().decode("utf-8"))
            except (OSError, TimeoutError, ValueError, urllib.error.URLError) as error:
                errores.append(f"No se pudo consultar la API de Xuxen ({error}); se continúa con Hunspell.")
                return bloqueos, avisos, errores
            llamadas += 1
            for correccion in datos.get("corrections", []):
                texto = str(correccion.get("text", ""))
                try:
                    offset = int(correccion.get("offset", 0))
                except (TypeError, ValueError):
                    offset = 0
                tipo = str(correccion.get("type", ""))
                hallazgo = {
                    "archivo": nombre_relativo(ruta),
                    "palabra": texto or "—",
                    "tipo": tipo or "sin tipo",
                    "descripcion": str(correccion.get("description", "")),
                    "frase": frase_en_offset(parte, offset, len(texto)),
                }
                (bloqueos if es_correccion_ortografica(tipo) else avisos).append(hallazgo)
    return bloqueos, avisos, errores


def leer_lista_blanca(ruta):
    return {
        linea.strip().casefold()
        for linea in ruta.read_text(encoding="utf-8").splitlines()
        if linea.strip() and not linea.lstrip().startswith("#")
    }


def renderizar_informe(nuevas, api_avisos, api_errores):
    if not nuevas and not api_avisos and not api_errores:
        return ""
    lineas = ["## Revisión de Xuxen"]
    if nuevas:
        lineas.extend(["", "Palabras ortográficas desconocidas nuevas:"])
        for hallazgo in nuevas:
            lineas.append(
                f'- **{hallazgo["archivo"]}** — «{hallazgo["palabra"]}»: '
                f'“{hallazgo["frase"]}”'
            )
    if api_avisos:
        lineas.extend(["", "Avisos gramaticales o de estilo de la API (no bloquean):"])
        for hallazgo in api_avisos:
            linea = (
                f'- **{hallazgo["archivo"]}** — «{hallazgo["palabra"]}» '
                f'({hallazgo["tipo"]}): “{hallazgo["frase"]}”'
            )
            if hallazgo["descripcion"]:
                linea += f' — {hallazgo["descripcion"]}'
            lineas.append(linea)
    if api_errores:
        lineas.extend([""] + [f"Aviso: {error}" for error in api_errores])
    return "\n".join(lineas)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", help="SHA de la base; limita la revisión a los JSON cambiados.")
    parser.add_argument("--pull-request", action="store_true", help="Consulta además la API de Xuxen.")
    parser.add_argument("--files", nargs="*", help="Limita la revisión a estos archivos.")
    parser.add_argument("--report-file", help="Escribe el informe de PR en esta ruta si hay avisos.")
    args = parser.parse_args(argv)
    if args.pull_request and not args.base_ref:
        parser.error("--pull-request requiere --base-ref")

    lista_blanca = leer_lista_blanca(RAIZ / "docs/xuxen-hitzak.txt")
    if args.files is not None:
        archivos = archivos_contenido(args.files)
    elif args.base_ref:
        archivos = archivos_cambiados(args.base_ref)
    else:
        archivos = archivos_contenido()
    archivos = [ruta for ruta in archivos if ruta.is_file()]
    actuales = revisar_hunspell(archivos, lista_blanca)
    palabras_base = {}
    if args.base_ref:
        palabras_base = palabras_desconocidas_por_archivo(archivos, lista_blanca, args.base_ref)
    nuevas = filtrar_palabras_nuevas(actuales, palabras_base)

    api_ortografia = []
    api_avisos = []
    api_errores = []
    if args.pull_request:
        api_ortografia, api_avisos, api_errores = revisar_api(archivos)
    bloqueos = nuevas + api_ortografia
    informe = renderizar_informe(bloqueos, api_avisos, api_errores)
    if args.report_file:
        Path(args.report_file).write_text(informe, encoding="utf-8")
    if informe:
        print(informe)
    else:
        print("Xuxen: sin palabras desconocidas nuevas.")
    return 1 if bloqueos else 0


if __name__ == "__main__":
    sys.exit(main())
