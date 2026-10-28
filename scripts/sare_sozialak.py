#!/usr/bin/env python3
"""Genera imágenes de Kimu para redes sociales y gestiona el issue semanal."""
from __future__ import annotations

import argparse
from datetime import date
import html
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

RAIZ = Path(__file__).resolve().parent.parent
DESTAKATUAK = RAIZ / "sare-sozialak" / "destakatuak"
BIO = "Kimu 🌱 | Fitxa bisualak euskaraz · LH · NEAE/PT | Doan 👇"
KATEGORIAK = [
    ("fitxak", "Fitxak", "📄", "#d9f7b0"),
    ("euskara", "Euskara", "🔤", "#d9eaff"),
    ("mate", "Mate", "🔢", "#fff0c2"),
    ("ingurunea", "Ingurunea", "🌍", "#d5f1e5"),
    ("jolasak", "Jolasak", "🎲", "#f0e3ff"),
    ("entzumenak", "Entzumenak", "🎧", "#ffe2d5"),
    ("lh-1", "LH 1", "🌱", "#e1f3c9"),
    ("doan", "Doan", "🎁", "#fff0c2"),
    ("bozketak", "Bozketak", "🗳️", "#e4e5ff"),
]


def svg_portada(titulua: str, ikonoa: str, kolorea: str, maskota: str, zirkulua: bool = False) -> str:
    titulua_svg = html.escape(titulua)
    ikonoa_svg = html.escape(ikonoa)
    if zirkulua:
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="320" height="320" viewBox="0 0 320 320" role="img" aria-label="{titulua_svg}">
<circle cx="160" cy="160" r="154" fill="{kolorea}"/><circle cx="160" cy="160" r="136" fill="#fff" opacity=".72"/>
<text x="160" y="174" text-anchor="middle" font-size="105">{ikonoa_svg}</text>
<text x="160" y="255" text-anchor="middle" font-family="Arial,sans-serif" font-size="28" font-weight="700" fill="#20241f">{titulua_svg}</text>
</svg>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920" role="img" aria-label="{titulua_svg}">
<rect width="1080" height="1920" fill="#f7f7f2"/><circle cx="540" cy="730" r="420" fill="{kolorea}"/>
<circle cx="540" cy="730" r="330" fill="#fff" opacity=".72"/>
<text x="540" y="830" text-anchor="middle" font-size="280">{ikonoa_svg}</text>
<text x="540" y="1320" text-anchor="middle" font-family="Arial,sans-serif" font-size="92" font-weight="800" fill="#20241f">{titulua_svg}</text>
<text x="540" y="1430" text-anchor="middle" font-family="Arial,sans-serif" font-size="38" font-weight="700" fill="#3f7a22">Baliabide bisualak euskaraz</text>
<image x="440" y="1530" width="200" height="284" href="data:image/svg+xml;base64,{maskota}"/>
</svg>'''


def sortu_portadak(destinoa: Path = DESTAKATUAK) -> list[Path]:
    maskota = (RAIZ / "estatico" / "kimu.svg").read_bytes()
    import base64

    maskota_data = base64.b64encode(maskota).decode("ascii")
    destinoa.mkdir(parents=True, exist_ok=True)
    sortutakoak = []
    for slug, titulua, ikonoa, kolorea in KATEGORIAK:
        for zirkulua in (False, True):
            neurria = "320x320" if zirkulua else "1080x1920"
            fitxategia = destinoa / f"{slug}-{neurria}.svg"
            fitxategia.write_text(svg_portada(titulua, ikonoa, kolorea, maskota_data, zirkulua), encoding="utf-8")
            sortutakoak.append(fitxategia)
            png = fitxategia.with_suffix(".png")
            svg_png(fitxategia, png, 320 if zirkulua else 1080, 320 if zirkulua else 1920)
            sortutakoak.append(png)
    return sortutakoak


def aukeratu_gaiak(issues: list[dict]) -> list[dict]:
    gaiak = []
    for issue in sorted(issues, key=lambda i: i.get("number", 0), reverse=True):
        if "pull_request" in issue or issue.get("state") != "open":
            continue
        izenburua = issue.get("title", "")
        if any(term in izenburua.casefold() for term in ("instagram", "facebook", "argitaratzeko prest")):
            continue
        if "material" not in {etiketa.get("name", "").casefold() for etiketa in issue.get("labels", [])}:
            continue
        gaiak.append(issue)
        if len(gaiak) == 2:
            break
    return gaiak


def github_json(repo: str, token: str, path: str, metodo: str = "GET", datuak: dict | None = None):
    url = f"https://api.github.com/repos/{repo}/{path}"
    edukia = json.dumps(datuak).encode() if datuak is not None else None
    eskaera = urllib.request.Request(
        url,
        data=edukia,
        method=metodo,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + token,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Kimu-social-kit",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(eskaera, timeout=30) as erantzuna:
        return json.loads(erantzuna.read().decode("utf-8")) if erantzuna.status != 204 else None


def svg_png(svg_path: Path, png_path: Path, width: int, height: int) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise RuntimeError("Playwright behar da irudiak PNG formatura bihurtzeko.") from error
    import base64

    data = base64.b64encode(svg_path.read_bytes()).decode("ascii")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
            page.set_content(
                f'<html><style>html,body{{margin:0;width:{width}px;height:{height}px;overflow:hidden}}</style>'
                f'<img src="data:image/svg+xml;base64,{data}" width="{width}" height="{height}">',
                wait_until="load",
            )
            page.screenshot(path=str(png_path), full_page=True)
        finally:
            browser.close()


def sortu_boza(repo: str, token: str, data: date = date.today(), issues: list[dict] | None = None) -> tuple[Path, list[dict]]:
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo):
        raise ValueError("GITHUB_REPOSITORY ez da baliozkoa.")
    if issues is None:
        issues = github_json(repo, token, "issues?state=open&labels=material&per_page=100")
    gaiak = aukeratu_gaiak(issues)
    if len(gaiak) < 2:
        raise ValueError("Bozketarako material-issue ireki bi behar dira gutxienez.")
    lehen, bigarren = gaiak
    izenak = [html.escape(lehen["title"]), html.escape(bigarren["title"])]
    edukia = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920" role="img" aria-label="Zer nahi duzu datorren astean?">
<rect width="1080" height="1920" fill="#f7f7f2"/><circle cx="900" cy="280" r="250" fill="#d9f7b0"/>
<text x="540" y="290" text-anchor="middle" font-family="Arial,sans-serif" font-size="46" font-weight="700" fill="#3f7a22">KIMU · ASTEKO BOZKETA</text>
<text x="540" y="580" text-anchor="middle" font-family="Arial,sans-serif" font-size="78" font-weight="800" fill="#20241f">Zer nahi duzu</text>
<text x="540" y="690" text-anchor="middle" font-family="Arial,sans-serif" font-size="78" font-weight="800" fill="#20241f">datorren astean?</text>
<rect x="100" y="830" width="880" height="290" rx="52" fill="#d9eaff"/><text x="150" y="915" font-family="Arial,sans-serif" font-size="36" font-weight="700" fill="#2563b0">1. AUKERA</text>
<foreignObject x="150" y="955" width="780" height="130"><div xmlns="http://www.w3.org/1999/xhtml" style="font-family:Arial,sans-serif;font-size:48px;font-weight:700;color:#20241f">{izenak[0]}</div></foreignObject>
<rect x="100" y="1190" width="880" height="290" rx="52" fill="#e5f3e2"/><text x="150" y="1275" font-family="Arial,sans-serif" font-size="36" font-weight="700" fill="#2f7d3a">2. AUKERA</text>
<foreignObject x="150" y="1315" width="780" height="130"><div xmlns="http://www.w3.org/1999/xhtml" style="font-family:Arial,sans-serif;font-size:48px;font-weight:700;color:#20241f">{izenak[1]}</div></foreignObject>
<text x="540" y="1640" text-anchor="middle" font-family="Arial,sans-serif" font-size="42" font-weight="700" fill="#20241f">Bozkatu Instagram-eko inkestan</text>
<text x="540" y="1745" text-anchor="middle" font-family="Arial,sans-serif" font-size="32" fill="#5d6472">Eskerrik asko Kimu hazten laguntzeagatik 🌱</text></svg>'''
    ruta = RAIZ / "sare-sozialak" / f"{data.isoformat()}-bozketa.svg"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(edukia, encoding="utf-8")
    svg_png(ruta, ruta.with_suffix(".png"), 1080, 1920)
    return ruta, gaiak


def aste_izenburua(data: date = date.today()) -> str:
    astea = data.isocalendar()
    return f"Argitaratzeko prest · {astea.year}-W{astea.week:02d}"


def argitaratu_issue(repo: str, token: str, run_url: str, data: date = date.today(),
                     gaiak: list[dict] | None = None) -> int:
    if not run_url.startswith("https://github.com/"):
        raise ValueError("Workflow-aren URLak GitHub-ena izan behar du.")
    issues = github_json(repo, token, "issues?state=open&per_page=100")
    izenburua = aste_izenburua(data)
    issue = next((i for i in issues if not i.get("pull_request") and i.get("title") == izenburua), None)
    if issue is None:
        gaiak = gaiak or aukeratu_gaiak(github_json(repo, token, "issues?state=open&labels=material&per_page=100"))
        aukerak = "\n".join(f"- {g['title']}" for g in gaiak)
        body = f"Asteko sare sozialetako argitalpenak.\n\n**Bozketarako aukerak:**\n{aukerak}\n\n**Bio proposatua:** {BIO}"
        issue = github_json(repo, token, "issues", "POST", {"title": izenburua, "body": body, "labels": ["material"]})
    issue_number = issue["number"]
    github_json(repo, token, f"issues/{issue_number}/comments", "POST", {
        "body": f"📎 [Deskargatu aste honetako irudiak eta bideoak]({run_url})\n\n{BIO}"
    })
    return issue_number


def main() -> None:
    parser = argparse.ArgumentParser(description="Kimu-ren sare sozialetako irudiak sortu.")
    parser.add_argument("--portadak", action="store_true", help="sortu nabarmentzeko 9 portadak")
    parser.add_argument("--bozketa", action="store_true", help="sortu asteko bozketaren istorioa")
    parser.add_argument("--issue", action="store_true", help="lotu workflow-aren artifaktua asteko issue-ra")
    args = parser.parse_args()
    if not any(vars(args).values()):
        args.portadak = True
    if args.portadak:
        print(f"{len(sortu_portadak())} portada sortu dira.")
    gaiak = None
    if args.bozketa or args.issue:
        repo = os.environ.get("GITHUB_REPOSITORY", "")
        token = os.environ.get("GITHUB_TOKEN", "")
        if not token:
            raise SystemExit("GITHUB_TOKEN behar da issue-ak irakurtzeko.")
        if args.bozketa:
            ruta, gaiak = sortu_boza(repo, token)
            print(f"Bozketa sortu da: {ruta}")
        if args.issue:
            run_url = os.environ.get("GITHUB_RUN_URL", "")
            number = argitaratu_issue(repo, token, run_url, gaiak=gaiak)
            print(f"Artifaktua #{number} issue-ra estekatu da.")


if __name__ == "__main__":
    main()
