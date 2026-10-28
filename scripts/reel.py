#!/usr/bin/env python3
"""Genera un reel vertical de 12–15 segundos a partir de una ficha."""
from __future__ import annotations

import argparse
from datetime import date
import html
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

RAIZ = Path(__file__).resolve().parent.parent
Gehienezko_tamaina = 15 * 1024 * 1024
IRAUPENA = 2.4


def fitxak_kargatu(ids: list[str], edukien_bidea: Path = RAIZ / "contenido" / "fitxak") -> list[dict]:
    gaur = date.fromisoformat(os.environ.get("KIMU_FECHA", date.today().isoformat()))
    fitxak = []
    for id_fitxa in ids:
        if not id_fitxa.replace("-", "").isalnum():
            raise ValueError(f"Fitxaren ID baliogabea: {id_fitxa}")
        path = edukien_bidea / f"{id_fitxa}.json"
        if not path.is_file():
            raise FileNotFoundError(f"Ez da fitxa aurkitu: {path}")
        fitxa = json.loads(path.read_text(encoding="utf-8"))
        argitaratzeko_data = fitxa.get("publicar_desde", "")
        if fitxa.get("publicado") and (not argitaratzeko_data or argitaratzeko_data <= gaur.isoformat()):
            fitxak.append(fitxa)
    return fitxak


def aukeratu_orriak(fitxa: dict) -> list[int]:
    orriak = [
        index for index, hoja in enumerate(fitxa.get("hojas", []))
        if not hoja.get("soluciones")
    ]
    return orriak[:4]


def iraupena(orri_kopurua: int) -> float:
    return max(3, min(orri_kopurua, 4)) * IRAUPENA + 2 * IRAUPENA


def _datu_html(data: bytes, mota: str) -> str:
    import base64
    return f"data:{mota};base64,{base64.b64encode(data).decode('ascii')}"


def _prestatu_diak(browser, fitxa: dict, html_path: Path, temp_path: Path) -> list[Path]:
    orriak = aukeratu_orriak(fitxa)
    if not orriak:
        raise ValueError(f"{fitxa.get('id')} fitxak ez du ikaslearentzako orririk.")
    page = browser.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
    page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
    page.evaluate("document.fonts.ready")
    capturak = [page.locator(".hoja:not(.soluciones)").nth(i).screenshot(type="png") for i in range(len(orriak))]
    page.close()
    while len(capturak) < 3:
        capturak.append(capturak[-1])
    maskota = (RAIZ / "estatico" / "kimu.svg").read_bytes()
    titulu = html.escape(fitxa["nombre"])
    slides = []
    edukia = [
        ("cover", None),
        *[("sheet", capture) for capture in capturak],
        ("outro", None),
    ]
    for index, (mota, capture) in enumerate(edukia):
        if mota == "sheet":
            irudia = _datu_html(capture, "image/png")
            edukia_slide = f'<img class="sheet" src="{irudia}" alt="Fitxaren ariketa-orria">'
            label = f"Fitxa · {index}"
        else:
            edukia_slide = f'<img class="mascota" src="{_datu_html(maskota, "image/svg+xml")}" alt="">'
            label = "Kimu"
        encabezado = (f'<p class="eyebrow">KIMU · FITXA BISUALAK</p><h1>{titulu}</h1>'
                      if mota == "cover" else
                      '<h1>Ikasi, jolastu<br>eta hazi.</h1><p>Ikusi fitxa osoa gure webgunean</p>'
                      if mota == "outro" else "")
        page = browser.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        page.set_content(f'''<!doctype html><html lang="eu"><meta charset="utf-8"><style>
*{{box-sizing:border-box}}body{{margin:0;width:1080px;height:1920px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:40px;padding:100px 80px;background:linear-gradient(155deg,#f7f7f2,#e8f4e3);font-family:Arial,sans-serif;color:#20241f;text-align:center}}
.eyebrow{{font-size:34px;letter-spacing:5px;color:#3f7a22;font-weight:700}}h1{{font-size:84px;line-height:1.12;margin:10px 0}}p{{font-size:42px;line-height:1.3}}.sheet{{width:880px;height:1245px;object-fit:contain;border-radius:20px;box-shadow:0 16px 44px #20241f30}}.mascota{{width:300px;height:420px}}
.url{{position:absolute;bottom:100px;font-size:38px;font-weight:700;color:#3f7a22}}
</style><body>{encabezado}{edukia_slide}<p class="url">keript.github.io/kimu-ikas-materialak</p></body></html>''', wait_until="load")
        page.evaluate("document.fonts.ready")
        path = temp_path / f"slide-{index:02}.png"
        page.screenshot(path=str(path))
        slides.append(path)
        page.close()
    return slides


def _ffmpeg_args(slides: list[Path], output: Path, ffmpeg: str = "ffmpeg") -> list[str]:
    cmd = [ffmpeg, "-y"]
    for slide in slides:
        cmd.extend(["-i", str(slide)])
    filters = []
    for index in range(len(slides)):
        filters.append(
            f"[{index}:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,zoompan=z='min(zoom+0.0005,1.04)':"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={round(IRAUPENA * 30)}:"
            "s=1080x1920:fps=30,setsar=1[v" + str(index) + "]"
        )
    joined = "".join(f"[v{i}]" for i in range(len(slides)))
    filters.append(f"{joined}concat=n={len(slides)}:v=1:a=0,format=yuv420p[out]")
    cmd.extend([
        "-filter_complex", ";".join(filters), "-map", "[out]", "-an",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "27",
        "-movflags", "+faststart", str(output),
    ])
    return cmd


def sortu_reel(fitxa: dict, gunekoa: date = date.today(), site_path: Path = RAIZ / "_site",
               output_root: Path = RAIZ / "sare-sozialak", ffmpeg: str = "ffmpeg") -> Path:
    html_path = site_path / f"{fitxa['id']}.html"
    if not html_path.is_file():
        raise FileNotFoundError(f"Web-orria falta da; lehenik sortu webgunea: {html_path}")
    if shutil.which(ffmpeg) is None:
        raise RuntimeError("ffmpeg behar da reel-a sortzeko.")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise RuntimeError("Playwright behar da: pip install -r requirements-social.txt") from error
    output_dir = output_root / f"{gunekoa.isoformat()}-{fitxa['id']}"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "reel.mp4"
    with tempfile.TemporaryDirectory(prefix="kimu-reel-") as temp:
        temp_path = Path(temp)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                slides = _prestatu_diak(browser, fitxa, html_path, temp_path)
            finally:
                browser.close()
        subprocess.run(_ffmpeg_args(slides, output, ffmpeg), check=True, capture_output=True, text=True)
    iraupen_segundoak = iraupena(len(aukeratu_orriak(fitxa)))
    if not 12 <= iraupen_segundoak <= 15:
        raise RuntimeError("Reel-aren iraupena 12–15 segundo artekoa izan behar da.")
    if output.stat().st_size >= Gehienezko_tamaina:
        output.unlink()
        raise RuntimeError("Reel-ak 15 MB gainditzen ditu.")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Sortu reel bertikalak fitxetatik.")
    parser.add_argument("--ids", required=True, help="Fitxen IDak, koma bidez bereizita.")
    args = parser.parse_args()
    ids = [id_fitxa.strip() for id_fitxa in args.ids.split(",") if id_fitxa.strip()]
    for fitxa in fitxak_kargatu(ids):
        print(f"Sortzen: {fitxa['id']}")
        print(sortu_reel(fitxa))


if __name__ == "__main__":
    main()
