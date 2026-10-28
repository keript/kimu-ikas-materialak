"""Boletín mensual de Kimu en Buttondown (usuario «kimu»).

`python scripts/buletina.py proba`   → comprueba que el secret BUTTONDOWN_API_KEY funciona.
`python scripts/buletina.py zirriborroa` → crea el BORRADOR del mes con las fichas publicadas en los últimos
   ~31 días y avisa a Iker en un issue. Nunca envía nada: Iker lo revisa y pulsa «Send» en Buttondown.
"""
import datetime as dt
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
WEB = "https://keript.github.io/kimu-ikas-materialak/"
API = "https://api.buttondown.com/v1"
IKER = os.environ.get("IKER", "keript")
HILABETEAK = ["urtarrila", "otsaila", "martxoa", "apirila", "maiatza", "ekaina", "uztaila", "abuztua",
              "iraila", "urria", "azaroa", "abendua"]


def api(metodo, ruta, datos=None):
    req = urllib.request.Request(f"{API}{ruta}", method=metodo,
                                 data=json.dumps(datos).encode() if datos is not None else None,
                                 headers={"Authorization": f"Token {os.environ['BUTTONDOWN_API_KEY']}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read() or "{}")


def nuevas(dias=31):
    """Fichas publicadas cuyo JSON se añadió en los últimos `dias` días, o con publicar_desde en ese periodo."""
    hoy = dt.date.today(); desde = hoy - dt.timedelta(days=dias)
    añadidos = set(subprocess.run(["git", "log", f"--since={desde}", "--diff-filter=A", "--name-only", "--format=",
                                   "--", "contenido/fitxak/"], capture_output=True, text=True, cwd=RAIZ).stdout.split())
    out = []
    for r in sorted((RAIZ / "contenido" / "fitxak").glob("*.json")):
        f = json.loads(r.read_text(encoding="utf-8"))
        if f.get("publicado") is not True:
            continue
        pd = f.get("publicar_desde")
        reciente = f"contenido/fitxak/{r.name}" in añadidos or (pd and desde.isoformat() <= pd <= hoy.isoformat())
        if reciente:
            out.append(f)
    return out


def zirriborroa():
    fitxak = nuevas()
    hil = HILABETEAK[dt.date.today().month - 1]
    por_curso = {}
    for f in fitxak:
        por_curso.setdefault(f.get("curso") or "LH", []).append(f)
    lineas = []
    for curso in sorted(por_curso):
        lineas.append(f"\n## {curso}\n")
        for f in por_curso[curso][:12]:
            t = f.get("titulo") or f.get("izenburua") or f["id"]
            lineas.append(f"- **[{t}]({WEB}{f['id']}.html)**")
    cuerpo = (f"Kaixo!\n\nHona hemen {hil}ko material berriak, doan eta euskaraz, PT eta NEAE kontuan hartuta 🌱\n"
              + ("\n".join(lineas) if lineas else "\nHilabete honetan fitxa zaharrak hobetu ditugu.")
              + f"\n\n👉 Material guztiak: {WEB}\n\nIdeiaren bat edo eskaeraren bat? Erantzun mezu honi.\n\nLaster arte!\nKimu 🌱")
    e = api("POST", "/emails", {"subject": f"Kimu · {hil.capitalize()}ko material berriak 🌱", "body": cuerpo,
                                 "status": "draft"})
    print("Borrador creado:", e.get("id"))
    aviso = (f"@{IKER} 📬 **{hil.capitalize()}ko buletina** prest dago zirriborro gisa Buttondown-en ({len(fitxak)} fitxa berri).\n\n"
             "1. Ireki https://buttondown.com/emails\n2. Irakurri (2 min) eta zuzendu nahi duzuna.\n3. Sakatu **Send**.\n\n"
             "Bidaltzen ez baduzu, ez da ezer bidaltzen.")
    subprocess.run(["gh", "issue", "create", "--title", f"📬 Buletina: {hil}", "--body", aviso], check=False)


def proba():
    r = api("GET", "/newsletters")
    nombres = [n.get("username") for n in r.get("results", [])]
    print("Buttondown OK:", nombres)


if __name__ == "__main__":
    {"proba": proba, "zirriborroa": zirriborroa}[sys.argv[1]]()
