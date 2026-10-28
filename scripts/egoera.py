"""Parte diario de Kimu → un único issue «📋 Kimu: egoera» que se reescribe cada día.

Sirve para que Iker (y Claude, con una sola lectura) sepan cómo va todo sin gastar tiempo:
qué ha fusionado Copilot, qué está atascado, qué imágenes faltan y qué borradores esperan revisión.
Uso (en GitHub Actions):  python scripts/egoera.py   (necesita GH_TOKEN)
"""
import datetime as dt
import base64
from collections import Counter
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TITULO = "📋 Kimu: egoera"


def gh(*a):
    return subprocess.run(["gh", *a], capture_output=True, text=True, check=False).stdout


def j(*a):
    return json.loads(gh(*a) or "[]")


def resumir_estadisticas(datos):
    paginas = []
    juegos = Counter()
    for hit in datos.get("hits", []):
        ruta = str(hit.get("path", "")).lstrip("/")
        visitas = int(hit.get("count", hit.get("views", 0)) or 0)
        if ruta.startswith("jolasa-amaitu/"):
            juegos[ruta.removeprefix("jolasa-amaitu/")] += visitas
        elif ruta != "inprimatu" and ruta != "jolasa-amaitu" and ruta:
            paginas.append((ruta, visitas))
    return {
        "paginas": sorted(paginas, key=lambda x: x[1], reverse=True)[:10],
        "juegos": juegos.most_common(10),
    }


def obtener_estadisticas():
    token = os.environ.get("GOATCOUNTER_TOKEN")
    if not token:
        return None

    if str(RAIZ) not in sys.path:
        sys.path.insert(0, str(RAIZ))
    from scripts.build import estatistikak

    if not estatistikak:
        return {"paginas": [], "juegos": []}

    hoy = dt.datetime.now(dt.timezone.utc).date()
    inicio = hoy - dt.timedelta(days=6)
    consulta = urllib.parse.urlencode({"start": inicio.isoformat(), "end": hoy.isoformat(), "limit": 1000})
    url = f"https://{estatistikak}.goatcounter.com/api/v0/stats/hits?{consulta}"
    autenticacion = base64.b64encode(f":{token}".encode()).decode()
    peticion = urllib.request.Request(url, headers={"Authorization": f"Basic {autenticacion}"})
    try:
        with urllib.request.urlopen(peticion, timeout=15) as respuesta:
            return resumir_estadisticas(json.loads(respuesta.read().decode("utf-8")))
    except (OSError, ValueError, TypeError):
        return {"paginas": [], "juegos": []}


def hobekuntza_astero():
    """Los lunes: issue para Copilot con las 6 fichas peor medidas (si no hay ya uno abierto)."""
    import os
    import re
    if dt.date.today().weekday() != 0 or j("issue", "list", "--state", "open", "--label", "hobekuntza", "--json", "number"):
        return
    txosten = RAIZ / "docs" / "kalitatea-txostena.md"
    filas = [l for l in txosten.read_text(encoding="utf-8").splitlines() if re.match(r"^\| \d", l)][:6]
    if not filas:
        return
    gh("label", "create", "hobekuntza", "--color", "C2E0C6", "--description", "Mejora semanal automática")
    cuerpo = ("Mejora semanal automática: sube estas fichas a **≥ 9,8/10** siguiendo `docs/kalitatea.md` "
              "(sin cambiar su contenido curricular; revisa también el euskera y la regla de «Hitz berriak»).\n\n"
              "| Nota | Ficha | Arloa | Tipo | Qué falta |\n|---|---|---|---|---|\n" + "\n".join(filas))
    url = gh("issue", "create", "--title", f"Kimu hobekuntza {dt.date.today():%Y-%m-%d}: 6 fichas a 9,8", "--label", "hobekuntza", "--body", cuerpo).strip()
    n = url.rsplit("/", 1)[-1]
    if n.isdigit():  # entra en la cola de Copilot (scripts/ilara.py), no se asigna directamente
        gh("issue", "edit", n, "--add-label", "ilara")


def main():
    ayer = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)).isoformat()
    prs = j("pr", "list", "--state", "all", "--limit", "100", "--json", "number,title,state,isDraft,author,mergedAt,comments,labels")
    cop = [p for p in prs if "copilot" in p["author"]["login"].lower()]
    fusion = [p for p in cop if p["mergedAt"] and p["mergedAt"] >= ayer]
    abiertos = [p for p in cop if p["state"] == "OPEN"]
    atasc = [p for p in abiertos if not p["isDraft"] and p["comments"] and "kimu-revision" in p["comments"][-1]["body"]]
    issues = j("issue", "list", "--state", "open", "--limit", "200", "--json", "number,title,assignees,labels")
    activos = [p for p in abiertos if not any(l["name"] == "pausa" for l in p["labels"])]
    cola = [i for i in issues if any(l["name"] == "ilara" for l in i["labels"])]
    sin_pr = [i for i in issues if any("copilot" in a["login"].lower() for a in i["assignees"])]
    irudiak = [i for i in issues if any(l["name"] == "irudia" for l in i["labels"])]
    borradores = []
    for r in sorted((RAIZ / "contenido" / "fitxak").glob("*.json")):
        f = json.loads(r.read_text(encoding="utf-8"))
        if f.get("publicado") is False and not f.get("publicar_desde") and not f.get("hobetzen"):
            borradores.append(f"`{f['id']}` ({f.get('arlo', '')})")
    txosten = RAIZ / "docs" / "kalitatea-txostena.md"
    media = next((l for l in txosten.read_text(encoding="utf-8").splitlines() if l.startswith("Fichas medidas")), "") if txosten.exists() else ""
    L = [f"_Actualizado: {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC_", "",
         f"## ✅ Fusionado en las últimas 24 h ({len(fusion)})"] + [f"- #{p['number']} {p['title']}" for p in fusion] + [
         "", f"## 🔧 Copilot trabajando ({len(activos)} activos · {len(abiertos) - len(activos)} PR en pausa · {len(cola)} issues en cola)"] + [
         f"- #{p['number']} {p['title']}{' · borrador' if p['isDraft'] else ''}" for p in activos] + [
         "", f"## ⚠️ Atascados: el revisor pidió cambios ({len(atasc)})"] + [f"- #{p['number']} {p['title']}" for p in atasc] + [
         "", f"## 🖼️ Imágenes para ti ({len(irudiak)}) — abre el issue, copia la orden en Gemini y sube la imagen"] + [
         f"- #{i['number']} {i['title']}" for i in irudiak] + [
         "", f"## 👀 Borradores esperando tu revisión de euskera ({len(borradores)})", ", ".join(borradores[:60]) or "—",
         "", "## 📊 Calidad", media or "—"]
    estadisticas = obtener_estadisticas()
    if estadisticas is not None:
        paginas = [f"- `/{ruta}`: {visitas}" for ruta, visitas in estadisticas["paginas"]] or ["—"]
        juegos = [f"- `{juego}`: {terminados}" for juego, terminados in estadisticas["juegos"]] or ["—"]
        L += ["", "## 📈 Gehien erabiliak (7 egun)", "Páginas más vistas:", *paginas, "Juegos más terminados:", *juegos]
    sin_asignar = [i for i in issues if not i["assignees"] and not any(l["name"] == "ilara" for l in i["labels"])
                   and any(l["name"] == "hobekuntza" for l in i["labels"])]
    if sin_asignar:
        L += ["", "## 👉 Asigna a Copilot (un toque: Assignees → Copilot)"] + [f"- #{i['number']} {i['title']}" for i in sin_asignar]
    cuerpo = "\n".join(L)
    exist = [i for i in j("issue", "list", "--state", "open", "--search", TITULO, "--json", "number,title") if i["title"] == TITULO]
    if exist:
        gh("issue", "edit", str(exist[0]["number"]), "--body", cuerpo)
    else:
        gh("issue", "create", "--title", TITULO, "--body", cuerpo)
    print(cuerpo)


if __name__ == "__main__":
    hobekuntza_astero()
    main()
