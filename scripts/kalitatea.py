"""Medidor automático de calidad Kimu 3.0 (0–10 por ficha), según docs/kalitatea.md.

Uso:  python scripts/kalitatea.py            → escribe docs/kalitatea-txostena.md (ranking y qué falta)
      python scripts/kalitatea.py --solo id1,id2 --min 7 → mide solo esas fichas y falla si alguna baja de 7
No mide el euskera ni la pedagogía fina: mide lo que se puede contar (imágenes, juegos, ejemplos, orden…).
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
ICONO = re.compile(r":[a-z0-9-]{3,}:")


def bloques(f):
    return [b for h in f.get("hojas", []) for b in h.get("bloques", [])]


def palabras(t):
    return len(re.sub(r"[*_{}:]", " ", str(t)).split())


def puntuar_adaptada(f):
    """Evalúa fichas enteramente adaptadas con una rúbrica compatible con su perfil."""
    hojas = f.get("hojas", [])
    bl = bloques(f)
    ejs = [b for b in bl if b["tipo"] == "ejercicio"]
    falta, p = [], 0.0
    if hojas and all(h.get("egokitua") for h in hojas):
        p += 1
    else:
        falta.append("todas las hojas marcadas como egokitua")
    if ejs and all(b.get("ejemplo") and b.get("solucion") for b in ejs):
        p += 2
    else:
        falta.append("ejemplo resuelto y soluciones en cada ejercicio")
    textos = [str(x) for b in ejs for x in (b.get("frases") or b.get("items") or b.get("palabras") or b.get("izquierda") or [])]
    r_ico = sum(1 for t in textos if ICONO.search(t)) / len(textos) if textos else 0
    p += 2 * r_ico
    if r_ico < 1:
        falta.append("icono/imagen en cada ítem")
    if f.get("publicado") is False and f.get("soluciones"):
        p += 1
    else:
        falta.append("ficha en borrador con soluciones")

    beharrak = set(f.get("beharrak", []))
    if "agnh" in beharrak:
        kontrolak = [
            all(len(b.get("frases", [])) <= 3 and all("[ ] Eginda ✓" in x for x in b.get("frases", [])) for b in ejs),
            all(b.get("enunciado") == "Zenbatu. Batu. Idatzi." for b in ejs),
            all(any("5 minutu" in b.get("texto", "") for b in h.get("bloques", [])) for h in hojas),
            all(len(re.findall(r"⭐", h.get("titulo", ""))) in (1, 2, 3) for h in hojas),
        ]
        etiquetas = [
            "gehienez hiru ariketa eta «Eginda» laukitxoa orriko",
            "agindu labur eta bera ariketa guztietan",
            "bost minutuko oharra orri guztietan",
            "maila bakarra orriko",
        ]
    elif "dislexia" in beharrak:
        kontrolak = [
            all(len(b.get("frases", [])) <= 4 for b in ejs),
            all(re.fullmatch(r"[\w\s]+", h.get("titulo", ""), re.UNICODE) for h in hojas),
            all(len(h.get("subtitulo", "").split()) <= 5 for h in hojas),
            all(h.get("tamano") == "grande" and h.get("egokitua") for h in hojas),
        ]
        etiquetas = [
            "gehienez lau ariketa orriko",
            "izenburu sinpleak, apaingarririk gabe",
            "bost hitz edo gutxiagoko azpitituluak",
            "letra handia orri guztietan",
        ]
    elif "tea" in beharrak:
        kontrolak = [
            all(
                len(h.get("bloques", [])) >= 3
                and h["bloques"][0].get("texto") == "HASI"
                and h["bloques"][-1].get("texto") == "BUKATU"
                for h in hojas
            ),
            len({h.get("subtitulo") for h in hojas}) == 1 and len({b.get("enunciado") for b in ejs}) == 1,
            bool(ejs) and all(b.get("ejemplo") for b in ejs),
            all(
                [b["tipo"] for b in h.get("bloques", [])] == ["nota", "ejercicio", "nota"]
                for h in hojas
            ),
        ]
        etiquetas = [
            "marka «HASI» eta «BUKATU» orri guztietan",
            "agindu bera leku berean orri guztietan",
            "eredu ebatzia ariketa guztietan",
            "diseinu bera orri guztietan",
        ]
    else:
        return None

    for kontrola, etiketa in zip(kontrolak, etiquetas):
        if kontrola:
            p += 1
        else:
            falta.append(etiketa)
    return round(min(10, p), 1), falta


def puntuar(f):
    bl = bloques(f)
    falta, p = [], 0.0
    if f.get("seccion") == "entzumenak" and f.get("lugar", "teoria") == "teoria":
        return entzumena(f, bl)
    if f.get("beharrak") and f.get("hojas") and all(h.get("egokitua") for h in f["hojas"]):
        adaptada = puntuar_adaptada(f)
        if adaptada is not None:
            return adaptada
    if f.get("lugar", "teoria") == "teoria":
        tarj = [i for b in bl if b["tipo"] == "tarjetas" for i in b.get("items", [])] + [b for b in bl if b["tipo"] == "apartado"]
        con_img = sum(1 for t in tarj if t.get("imagen")) / len(tarj) if tarj else 0
        p += 3 * con_img
        if con_img < .8: falta.append("imagen en cada tarjeta/apartado")
        if any(b["tipo"] in ("mapa",) for b in bl): p += 2
        else: falta.append("mapa mental al final")
        if any(b["tipo"] in ("tabla", "ilustracion", "pasos") for b in bl): p += 2
        else: falta.append("esquema visual (tabla, ilustración etiquetada o pasos)")
        if any(b["tipo"] == "gogoratu" for b in bl): p += 1
        else: falta.append("caja Gogoratu")
        largos = [t for t in tarj if palabras(t.get("texto", "")) > 20]
        if not largos: p += 1
        else: falta.append(f"{len(largos)} tarjeta(s) con más de 20 palabras")
        if f.get("relacionada"): p += 1
        else: falta.append("ficha de ariketak enlazada")
    else:
        ejs = [b for b in bl if b["tipo"] == "ejercicio"]
        mini = build.extraer_minijuegos(f)
        quiz = build.extraer_preguntas_jolasa(f)
        juegos = sum(bool(x) for x in (quiz, mini["lotu"], mini["sailkatu"], mini["memoria"], mini["margotu"]))
        p += min(3, juegos * 1.5)
        if juegos < 2: falta.append("más tipos de juego (relacionar / clasificar / elegir con solución)")
        textos = [str(x) for b in ejs for x in (b.get("frases") or b.get("items") or b.get("palabras") or b.get("izquierda") or [])]
        r_ico = sum(1 for t in textos if ICONO.search(t)) / len(textos) if textos else 0
        p += 2 * min(1, r_ico / .6)
        if r_ico < .6: falta.append("icono/imagen por ítem")
        modos = {b.get("modo") for b in ejs}
        p += min(2, len(modos) / 2)
        if len(modos) < 4: falta.append("más variedad de ejercicios")
        enun = " ".join(b.get("enunciado", "") for b in ejs) + " ".join(h.get("subtitulo", "") for h in f.get("hojas", []))
        if "⭐" in enun or f.get("generado"): p += 1
        else: falta.append("dificultad ⭐→⭐⭐⭐")
        if any(b["tipo"] in ("gogoratu", "pasos") for b in bl) or any(b.get("ejemplo") for b in ejs): p += 1
        else: falta.append("ejemplo resuelto")
        if any(b["tipo"] == "berrikusi" for b in bl): p += 1
        else: falta.append("Berrikusi al final")
    return round(min(10, p), 1), falta


def entzumena(f, bl):
    """Hoja del audio: «Hitz berriak» con imágenes antes, audio, texto con hilo y frases cortas."""
    falta, p = [], 0.0
    h1 = f.get("hojas", [{}])[0]
    tarj = [i for b in h1.get("bloques", []) if b["tipo"] == "tarjetas" for i in b.get("items", [])]
    if "HITZ BERRIAK" in h1.get("titulo", "").upper() and len(tarj) >= 4: p += 3
    else: falta.append("primera hoja «HITZ BERRIAK» con ≥ 4 tarjetas")
    if tarj and all(t.get("imagen") for t in tarj): p += 2
    else: falta.append("imagen en cada palabra nueva")
    if any(b["tipo"] == "ejercicio" and b.get("modo") == "relacionar" for b in h1.get("bloques", [])): p += 1
    else: falta.append("relacionar irudia ↔ hitza en «Hitz berriak»")
    if any(b["tipo"] == "entzun" for b in bl): p += 1
    else: falta.append("bloque entzun (audio)")
    parr = [x for b in bl if b["tipo"] == "lectura" for x in b.get("parrafos", [])]
    if 4 <= len(parr) <= 8: p += 1
    else: falta.append("texto de 4–8 párrafos")
    frases = [fr for x in parr for fr in re.split(r"[.!?]\s", re.sub(r":[a-z0-9-]+:", "", x)) if fr.strip()]
    if frases and max(palabras(fr) for fr in frases) <= 16: p += 1
    else: falta.append("frases de ≤ 16 palabras")
    if f.get("relacionada"): p += 1
    else: falta.append("ficha de galderak enlazada")
    return round(p, 1), falta


SOLO = set(sys.argv[sys.argv.index("--solo") + 1].split(",")) if "--solo" in sys.argv else None


def main():
    filas = []
    for ruta in sorted((RAIZ / "contenido" / "fitxak").glob("*.json")):
        f = json.loads(ruta.read_text(encoding="utf-8"))
        if (not f.get("publicado") and not SOLO) or f.get("generado") or not any(b["tipo"] in ("ejercicio", "tarjetas", "apartado", "entzun") for b in bloques(f)):
            continue
        if re.search(r"(irakaslearen-gida|infografia|estazioak)$", f["id"]) or f.get("arlo") == "gaztelera":
            continue  # guías, pósters y rincones tienen su propio formato
        if SOLO and f["id"] not in SOLO:
            continue
        nota, falta = puntuar(f)
        filas.append((nota, f["id"], f["arlo"], f.get("lugar", "teoria"), falta))
    filas.sort()
    if not filas:
        print("Ninguna ficha que medir."); return
    media = sum(n for n, *_ in filas) / len(filas)
    lineas = ["# Kalitatea 3.0 — txostena automatikoa", "",
              f"Fichas medidas: {len(filas)} · nota media **{media:.1f}/10** · por debajo de 7: **{sum(1 for n, *_ in filas if n < 7)}**", "",
              "| Nota | Ficha | Arloa | Tipo | Qué falta |", "|---|---|---|---|---|"]
    lineas += [f"| {n} | `{i}` | {a} | {l} | {'; '.join(fl) or '—'} |" for n, i, a, l, fl in filas]
    if SOLO:
        print("\n".join(f"{n}/10 {i}: {'; '.join(fl) or 'ondo'}" for n, i, a, l, fl in filas))
    else:
        (RAIZ / "docs" / "kalitatea-txostena.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"Media {media:.1f}/10 · {len(filas)} fichas · {sum(1 for n, *_ in filas if n < 7)} por debajo de 7 → docs/kalitatea-txostena.md")
    if "--min" in sys.argv:
        umbral = float(sys.argv[sys.argv.index("--min") + 1])
        if any(n < umbral for n, *_ in filas):
            sys.exit(1)


if __name__ == "__main__":
    main()
