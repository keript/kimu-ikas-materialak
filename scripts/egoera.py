"""Parte diario de Kimu → un único issue «📋 Kimu: egoera» que se reescribe cada día.

Sirve para que Iker (y Claude, con una sola lectura) sepan cómo va todo sin gastar tiempo:
qué ha fusionado Copilot, qué está atascado, qué imágenes faltan y qué borradores esperan revisión.
Uso (en GitHub Actions):  python scripts/egoera.py   (necesita GH_TOKEN)
"""
import datetime as dt
import json
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TITULO = "📋 Kimu: egoera"


def gh(*a):
    return subprocess.run(["gh", *a], capture_output=True, text=True, check=False).stdout


def j(*a):
    return json.loads(gh(*a) or "[]")


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
    cuerpo = ("Mejora semanal automática: sube estas fichas a **≥ 9,5/10** siguiendo `docs/kalitatea.md` "
              "(sin cambiar su contenido curricular; revisa también el euskera y la regla de «Hitz berriak»).\n\n"
              "| Nota | Ficha | Arloa | Tipo | Qué falta |\n|---|---|---|---|---|\n" + "\n".join(filas))
    url = gh("issue", "create", "--title", f"Kimu hobekuntza {dt.date.today():%Y-%m-%d}: 6 fichas a 9,5", "--label", "hobekuntza", "--body", cuerpo).strip()
    n = url.rsplit("/", 1)[-1]
    if os.environ.get("COPILOT_TOKEN") and n.isdigit():  # asignar a Copilot necesita un token personal
        subprocess.run(["gh", "api", f"repos/{os.environ['GITHUB_REPOSITORY']}/issues/{n}/assignees", "-X", "POST",
                        "-f", "assignees[]=copilot-swe-agent[bot]"], env={**os.environ, "GH_TOKEN": os.environ["COPILOT_TOKEN"]}, check=False)


def main():
    ayer = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)).isoformat()
    prs = j("pr", "list", "--state", "all", "--limit", "100", "--json", "number,title,state,isDraft,author,mergedAt,comments")
    cop = [p for p in prs if "copilot" in p["author"]["login"].lower()]
    fusion = [p for p in cop if p["mergedAt"] and p["mergedAt"] >= ayer]
    abiertos = [p for p in cop if p["state"] == "OPEN"]
    atasc = [p for p in abiertos if not p["isDraft"] and p["comments"] and "kimu-revision" in p["comments"][-1]["body"]]
    issues = j("issue", "list", "--state", "open", "--limit", "200", "--json", "number,title,assignees,labels")
    sin_pr = [i for i in issues if any("copilot" in a["login"].lower() for a in i["assignees"])]
    irudiak = [i for i in issues if any(l["name"] == "irudia" for l in i["labels"])]
    borradores = []
    for r in sorted((RAIZ / "contenido" / "fitxak").glob("*.json")):
        f = json.loads(r.read_text(encoding="utf-8"))
        if f.get("publicado") is False and not f.get("publicar_desde"):
            borradores.append(f"`{f['id']}` ({f.get('arlo', '')})")
    txosten = RAIZ / "docs" / "kalitatea-txostena.md"
    media = next((l for l in txosten.read_text(encoding="utf-8").splitlines() if l.startswith("Fichas medidas")), "") if txosten.exists() else ""
    L = [f"_Actualizado: {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC_", "",
         f"## ✅ Fusionado en las últimas 24 h ({len(fusion)})"] + [f"- #{p['number']} {p['title']}" for p in fusion] + [
         "", f"## 🔧 Copilot trabajando ({len(abiertos)} PR abiertos · {len(sin_pr)} issues asignados)"] + [
         f"- #{p['number']} {p['title']}{' · borrador' if p['isDraft'] else ''}" for p in abiertos] + [
         "", f"## ⚠️ Atascados: el revisor pidió cambios ({len(atasc)})"] + [f"- #{p['number']} {p['title']}" for p in atasc] + [
         "", f"## 🖼️ Imágenes para ti ({len(irudiak)}) — abre el issue, copia la orden en Gemini y sube la imagen"] + [
         f"- #{i['number']} {i['title']}" for i in irudiak] + [
         "", f"## 👀 Borradores esperando tu revisión de euskera ({len(borradores)})", ", ".join(borradores[:60]) or "—",
         "", "## 📊 Calidad", media or "—"]
    sin_asignar = [i for i in issues if not i["assignees"] and any(l["name"] == "hobekuntza" for l in i["labels"])]
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
