"""Calendario semanal de Kimu: 6 materiales por semana (uno por curso), con visto bueno de Iker.

  python scripts/astekoa.py proponer   → (domingo) abre el issue «👀 Asteko berrikuspena» con los borradores
                                          de la semana que viene: lunes LH 1 … sábado LH 6, con enlaces.
  python scripts/astekoa.py erantzun   → (cuando Iker comenta en ese issue) procesa la respuesta:
        ok            → programa todos para su día (publicado: true + publicar_desde)
        ok 1,3,5      → solo esos; el resto vuelve a la cola
        zuzendu 2: …  → abre un encargo a Copilot para corregirlo (puede haber varias líneas)
Sin respuesta no se publica nada. Necesita GH_TOKEN (y COPILOT_TOKEN para asignar las correcciones).
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FITXAK = RAIZ / "contenido" / "fitxak"
WEB = "https://keript.github.io/kimu-ikas-materialak/"
ETIQUETA = "berrikuspena"
DIAS = ["Astelehena", "Asteartea", "Asteazkena", "Osteguna", "Ostirala", "Larunbata"]
CURSOS = ["LH 1", "LH 2", "LH 3", "LH 4", "LH 5", "LH 6"]
REPO = os.environ.get("GITHUB_REPOSITORY", "keript/kimu-ikas-materialak")


def gh(*a, token=None):
    env = {**os.environ, **({"GH_TOKEN": token} if token else {})}
    return subprocess.run(["gh", *a], capture_output=True, text=True, check=False, env=env).stdout


def curso(f):
    m = re.match(r"lh(\d)-", f.get("arlo", ""))
    return f"LH {m.group(1)}" if m else f.get("curso", "LH 3")


def cargar():
    return {p.stem: (p, json.loads(p.read_text(encoding="utf-8"))) for p in sorted(FITXAK.glob("*.json"))}


def unidades(todas):
    """Borradores agrupados en «materiales»: la ficha de teoría + su ficha de ariketak (relacionada)."""
    usados, res = set(), []
    pendientes = [f for _, f in todas.values() if f.get("publicado") is False and not f.get("publicar_desde")
                  and not f.get("generado")]
    pendientes.sort(key=lambda f: (f.get("lugar", "teoria") != "teoria", f.get("orden", 999), f["id"]))
    for f in pendientes:
        if f["id"] in usados:
            continue
        grupo = [f["id"]]
        rel = f.get("relacionada")
        if rel in todas and todas[rel][1].get("publicado") is False and not todas[rel][1].get("publicar_desde"):
            grupo.append(rel)
        usados.update(grupo)
        res.append((curso(f), f["nombre"], grupo))
    return res


def proponer():
    abiertos = json.loads(gh("issue", "list", "--label", ETIQUETA, "--state", "open", "--json", "number") or "[]")
    if abiertos:
        print("Ya hay una revisión abierta: no se abre otra."); return
    hoy = dt.date.today()
    lunes = hoy + dt.timedelta(days=(7 - hoy.weekday()) % 7 or 7)
    cola = unidades(cargar())
    elegidos = []
    for i, c in enumerate(CURSOS):
        u = next((u for u in cola if u[0] == c), None)
        if u:
            elegidos.append((len(elegidos) + 1, (lunes + dt.timedelta(days=i)).isoformat(), DIAS[i], u))
    if not elegidos:
        print("No hay borradores pendientes esta semana."); return
    gh("label", "create", ETIQUETA, "--color", "BFD4F2", "--description", "Revisión semanal de Iker")
    lineas = [f"@keript 👋 Revisión de la semana. Borradores para la semana del **{lunes:%d-%m-%Y}**. Ábrelos, mira el euskera y responde aquí:",
              "", "- `ok` → se publican todos, cada uno en su día", "- `ok 1,3,5` → solo esos",
              "- `zuzendu 2: …` → Copilot lo corrige (una línea por cada uno)", ""]
    for n, fecha, dia, (c, nombre, ids) in elegidos:
        enlaces = " · ".join(f"[{i}]({WEB}{i}.html)" for i in ids)
        lineas.append(f"**{n}. {dia} ({c})** — {nombre}: {enlaces}")
    plan = ";".join(f"{n}={fecha}={'+'.join(ids)}" for n, fecha, _, (_, _, ids) in elegidos)
    lineas += ["", f"<!-- kimu-astekoa:{plan} -->"]
    print(gh("issue", "create", "--title", f"👀 Asteko berrikuspena {lunes:%Y-%m-%d}", "--label", ETIQUETA,
             "--body", "\n".join(lineas)).strip())


def erantzun():
    cuerpo, texto, n = os.environ["CUERPO_ISSUE"], os.environ["COMENTARIO"].strip(), os.environ["N"]
    m = re.search(r"kimu-astekoa:([^ ]+) -->", cuerpo)
    if not m:
        return
    plan = {int(k): (fecha, ids.split("+")) for k, fecha, ids in (x.split("=") for x in m.group(1).split(";"))}
    todas, hechos, avisos = cargar(), [], []
    for linea in texto.splitlines():
        lz = linea.strip().lower()
        z = re.match(r"zuzendu\s+(\d+)\s*:?\s*(.*)", linea.strip(), re.I)
        if z and int(z.group(1)) in plan:
            k = int(z.group(1)); ids = plan[k][1]
            body = (f"Corrección pedida por Iker en #{n} para `{', '.join(ids)}`:\n\n> {z.group(2)}\n\n"
                    "Corrige solo eso (mantén `\"publicado\": false`) y comprueba `docs/kalitatea.md` (≥ 9,5).")
            url = gh("issue", "create", "--title", f"Zuzendu: {', '.join(ids)}", "--body", body).strip()
            num = url.rsplit("/", 1)[-1]
            if num.isdigit():  # correcciones de Iker: primeras en la cola de Copilot
                gh("issue", "edit", num, "--add-label", "ilara", "--add-label", "lehentasuna-1")
            avisos.append(f"🔧 {k}: encargado a Copilot ({url})")
        elif re.match(r"^ok\b", lz):
            nums = [int(x) for x in re.findall(r"\d+", lz)] or list(plan)
            for k in nums:
                if k not in plan:
                    continue
                fecha, ids = plan[k]
                for i in ids:
                    if i in todas:
                        ruta, f = todas[i]
                        f["publicado"], f["publicar_desde"] = True, fecha
                        ruta.write_text(json.dumps(f, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                hechos.append(f"✅ {k}: {', '.join(ids)} → {fecha}")
    if not hechos and not avisos:
        gh("issue", "comment", n, "--body", "No he entendido la respuesta. Escribe `ok`, `ok 1,3` o `zuzendu 2: …`.")
        return
    Path(RAIZ / ".astekoa-resumen.txt").write_text("\n".join(hechos + avisos), encoding="utf-8")
    print("\n".join(hechos + avisos))


if __name__ == "__main__":
    {"proponer": proponer, "erantzun": erantzun}[sys.argv[1]]()
