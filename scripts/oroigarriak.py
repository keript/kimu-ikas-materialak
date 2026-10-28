"""Recordatorios para Iker (para que no se le olvide dar el visto bueno).

`python scripts/oroigarriak.py gogoratu`  (cada tarde)
  1. Si el issue de la revisión semanal («berrikuspena») sigue sin respuesta de Iker → le menciona (1 vez al día).
  2. Si hay fichas en borrador esperando su visto bueno → las lista en el issue «✅ Oniritzia» y le menciona
     (como mucho cada 2 días, o enseguida si hay fichas nuevas).
`python scripts/oroigarriak.py erantzun`  (cuando Iker comenta en «✅ Oniritzia»)
  - `ok` → publica todas · `ok id1, id2` → publica esas · `zuzendu id: qué cambiar` → encargo urgente a Copilot.
Las menciones las hace el bot, así a Iker le llega aviso (correo y app de GitHub).
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
WEB = "https://keript.github.io/kimu-ikas-materialak/"
IKER = os.environ.get("IKER", "keript")
TITULO = "✅ Oniritzia: fitxak zure begiradaren zain"
AHORA = dt.datetime.now(dt.timezone.utc)


def gh(*a):
    return subprocess.run(["gh", *a], capture_output=True, text=True, check=False).stdout


def j(*a):
    return json.loads(gh(*a) or "[]")


def borradores():
    out = []
    for r in sorted((RAIZ / "contenido" / "fitxak").glob("*.json")):
        f = json.loads(r.read_text(encoding="utf-8"))
        if f.get("publicado") is False and not f.get("publicar_desde") and not f.get("hobetzen"):
            out.append((f["id"], f.get("titulo") or f.get("izenburua") or f["id"], f.get("curso", ""), r))
    return out


def fecha(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def comentarios(n):
    return j("api", f"repos/{os.environ['GITHUB_REPOSITORY']}/issues/{n}/comments?per_page=100")


def ultimo_aviso(coms):
    avisos = [fecha(c["created_at"]) for c in coms if "<!-- oroigarria -->" in (c.get("body") or "")]
    return max(avisos) if avisos else None


def gogoratu():
    # 1. Revisión semanal sin respuesta
    for i in j("issue", "list", "--state", "open", "--label", "berrikuspena", "--json", "number,createdAt"):
        if AHORA - fecha(i["createdAt"]) < dt.timedelta(hours=10):
            continue
        coms = comentarios(i["number"])
        if any(c["user"]["login"] == IKER for c in coms):
            continue
        ult = ultimo_aviso(coms)
        if ult and AHORA - ult < dt.timedelta(hours=20):
            continue
        gh("issue", "comment", str(i["number"]), "--body",
           f"@{IKER} 👋 Gogorarazpena: asteko berrikuspena zure erantzunaren zain dago. "
           "Erantzun `ok`, `ok 1,3` edo `zuzendu 2: …` (5 minutu). Erantzunik gabe ez da ezer argitaratzen.\n<!-- oroigarria -->")
        print(f"Aviso en revisión semanal #{i['number']}")

    # 2. Borradores esperando visto bueno
    b = borradores()
    exist = [i for i in j("issue", "list", "--state", "open", "--search", "Oniritzia in:title", "--json", "number,title")
             if i["title"] == TITULO]
    if not b:
        for i in exist:
            gh("issue", "close", str(i["number"]), "--comment", "Ez dago fitxarik zain. Eskerrik asko! 🎉")
        return
    ids = ", ".join(x[0] for x in b)
    lista = "\n".join(f"- [ ] **{t}** ({c}) · `{i}` → {WEB}{i}.html" for i, t, c, _ in b[:40])
    cuerpo = (f"Hauek dira zure oniritziaren zain dauden fitxak ({len(b)}). Ireki mugikorrean, begiratu euskara eta erantzun hemen:\n\n"
              "- `ok` → denak argitaratu\n- `ok id1, id2` → horiek bakarrik\n- `zuzendu id: zer aldatu` → Copilot-i agindu (premiazkoa)\n\n"
              f"{lista}\n\n<!-- ids: {ids} -->")
    if exist:
        n = str(exist[0]["number"])
        anterior = re.search(r"<!-- ids: (.*?) -->", gh("issue", "view", n, "--json", "body", "-q", ".body") or "")
        nuevos = set(ids.split(", ")) - set((anterior.group(1) if anterior else "").split(", "))
        gh("issue", "edit", n, "--body", cuerpo)
        ult = ultimo_aviso(comentarios(n))
        if nuevos or not ult or AHORA - ult > dt.timedelta(hours=44):
            gh("issue", "comment", n, "--body",
               f"@{IKER} 👀 {len(b)} fitxa zure oniritziaren zain" + (f" ({len(nuevos)} berri)" if nuevos else "") +
               ". 10–20 minutu nahikoa dira. <!-- oroigarria -->")
    else:
        gh("label", "create", "oniritzia", "--color", "0E8A16", "--description", "Fichas esperando el visto bueno de Iker")
        url = gh("issue", "create", "--title", TITULO, "--label", "oniritzia", "--body", cuerpo).strip()
        gh("issue", "comment", url.rsplit("/", 1)[-1], "--body", f"@{IKER} 👀 {len(b)} fitxa zure oniritziaren zain. <!-- oroigarria -->")
    print(f"{len(b)} borradores avisados")


def erantzun():
    texto = os.environ["COMENTARIO"].strip()
    n = os.environ["N"]
    b = {x[0]: x for x in borradores()}
    hechos = []
    for linea in texto.splitlines():
        l = linea.strip()
        z = re.match(r"zuzendu\s+([\w-]+)\s*:?\s*(.+)", l, re.I)
        if z and z.group(1) in b:
            url = gh("api", f"repos/{os.environ['GITHUB_REPOSITORY']}/issues", "-f", f"title=Zuzendu: {z.group(1)}",
                     "-f", f"body=Corrección pedida por Iker en #{n} para `{z.group(1)}`:\n\n> {z.group(2)}\n\n"
                           "Corrige solo eso (mantén `\"publicado\": false`) y comprueba `docs/kalitatea.md` (≥ 9,8).",
                     "-f", "labels[]=ilara", "-f", "labels[]=lehentasuna-1", "--jq", ".html_url").strip()
            hechos.append(f"🔧 `{z.group(1)}` → {url}")
        elif re.match(r"^ok\b", l, re.I):
            pedidos = [x.strip() for x in re.split(r"[,\s]+", l[2:]) if x.strip()] or list(b)
            for i in pedidos:
                if i in b:
                    r = b[i][3]
                    f = json.loads(r.read_text(encoding="utf-8"))
                    f["publicado"] = True
                    r.write_text(json.dumps(f, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                    hechos.append(f"✅ `{i}` argitaratuta")
    Path(RAIZ / ".oniritzia.txt").write_text("\n".join(hechos) or "Ez dut ulertu. Idatzi `ok`, `ok id1, id2` edo `zuzendu id: …`.",
                                            encoding="utf-8")


if __name__ == "__main__":
    {"gogoratu": gogoratu, "erantzun": erantzun}[sys.argv[1]]()
