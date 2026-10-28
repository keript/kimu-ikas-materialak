"""Cola de trabajo de Copilot: como máximo MAX tareas a la vez, para no gastar los créditos de golpe.

- Tarea activa = PR abierto de Copilot sin la etiqueta `pausa`.
- Si hay hueco: primero se reanuda un PR en `pausa` (ya está a medias) y, si no hay, se asigna el
  siguiente issue con la etiqueta `ilara`. Orden: `lehentasuna-1` primero, luego el número más bajo.
- Si en las últimas 3 h Copilot ha fallado por falta de créditos, no se hace nada (se espera).
- Para meter una tarea en la cola: etiqueta `ilara` (y `lehentasuna-1` si es urgente). No asignes a mano.
"""
import datetime as dt
import json
import os
import subprocess

REPO = os.environ["GITHUB_REPOSITORY"]
MAX = int(os.environ.get("COPILOT_MAX") or 4)
SIN_CREDITOS = "sufficient GitHub AI Credits"


def gh(*args, token=None, check=False):
    env = {**os.environ, "GH_TOKEN": token or os.environ["GH_TOKEN"]}
    r = subprocess.run(["gh", *args], capture_output=True, text=True, env=env)
    if check and r.returncode:
        raise SystemExit(r.stderr)
    return r.stdout


def j(*args):
    return json.loads(gh(*args, check=True) or "[]")


def etiquetas(x):
    return {l["name"] for l in x["labels"]}


def orden(x):
    return (0 if "lehentasuna-1" in etiquetas(x) else 1, x["number"])


def sin_creditos():
    """True si Copilot ha avisado de falta de créditos en las últimas 3 h."""
    desde = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
    coms = j("api", f"repos/{REPO}/issues/comments?since={desde}&per_page=100")
    return [c for c in coms if "copilot" in c["user"]["login"].lower() and SIN_CREDITOS in (c.get("body") or "")]


def main():
    for nombre, color, desc in [("ilara", "BFD4F2", "En cola para Copilot"), ("pausa", "D4C5F9", "PR de Copilot en espera (cola)"),
                                ("berrikusi", "FBCA04", "El revisor debe volver a revisarlo"),
                                ("lehentasuna-1", "B60205", "Urgente: primero en la cola")]:
        gh("label", "create", nombre, "--color", color, "--description", desc)

    fallos = sin_creditos()
    if fallos:
        # Devuelve a la cola los issues que no llegaron a empezar.
        for c in fallos:
            n = c["issue_url"].rsplit("/", 1)[-1]
            gh("api", f"repos/{REPO}/issues/{n}/assignees", "-X", "DELETE", "-f", "assignees[]=copilot-swe-agent[bot]",
               token=os.environ.get("COPILOT_TOKEN"))
            gh("issue", "edit", n, "--add-label", "ilara")
        print(f"Sin créditos de Copilot ({len(fallos)} avisos recientes): se espera.")
        return

    prs = [p for p in j("pr", "list", "--state", "open", "--limit", "200", "--json", "number,author,labels")
           if "copilot" in p["author"]["login"].lower()]
    activos = [p for p in prs if "pausa" not in etiquetas(p)]
    pausados = sorted([p for p in prs if "pausa" in etiquetas(p)], key=orden)
    cola = sorted(j("issue", "list", "--state", "open", "--label", "ilara", "--limit", "200", "--json", "number,labels"), key=orden)
    hueco = MAX - len(activos)
    print(f"Activos {len(activos)}/{MAX} · en pausa {len(pausados)} · en cola {len(cola)}")
    if not os.environ.get("COPILOT_TOKEN"):
        print("Falta el secret COPILOT_TOKEN: no se puede asignar a Copilot.")
        return
    reanudados = 0
    while hueco > 0 and (pausados or cola):
        # Un issue urgente pasa delante de los PR en pausa que no lo son.
        if pausados and not (cola and orden(cola[0]) < orden(pausados[0]) and orden(cola[0])[0] == 0):
            n = str(pausados.pop(0)["number"])
            gh("pr", "edit", n, "--remove-label", "pausa", "--add-label", "berrikusi")
            print(f"Reanudado PR #{n} (lo revisará el revisor)")
            reanudados += 1
        else:
            n = str(cola.pop(0)["number"])
            gh("api", f"repos/{REPO}/issues/{n}/assignees", "-X", "POST", "-f", "assignees[]=copilot-swe-agent[bot]",
               token=os.environ["COPILOT_TOKEN"], check=True)
            gh("issue", "edit", n, "--remove-label", "ilara")
            print(f"Asignado issue #{n} a Copilot")
        hueco -= 1
    if reanudados:
        gh("workflow", "run", "copilot-fusionar.yml", "--ref", "main")


if __name__ == "__main__":
    main()
