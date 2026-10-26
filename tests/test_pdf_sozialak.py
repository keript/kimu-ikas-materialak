import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import sare_sozialak  # noqa: E402

try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as _p:
        _p.chromium.launch().close()
    HAY_NAVEGADOR = True
except Exception:  # noqa: BLE001
    HAY_NAVEGADOR = False


class FitxaBerriakTest(unittest.TestCase):
    def test_lehen_aldian_azken_astekoak_bakarrik(self):
        fichas = [{"id": "zaharra"}, {"id": "berria", "publicar_desde": "2026-10-24"},
                  {"id": "mate", "publicar_desde": "2026-10-24", "generado": True}]
        ids = [f["id"] for f in sare_sozialak.fitxa_berriak(fichas, set(), "2026-10-26", True)]
        self.assertEqual(ids, ["berria"])

    def test_ikusiak_baztertzen_dira(self):
        fichas = [{"id": "a"}, {"id": "b"}]
        ids = [f["id"] for f in sare_sozialak.fitxa_berriak(fichas, {"a"}, "2026-10-26", False)]
        self.assertEqual(ids, ["b"])

    def test_testuak_bost_hashtag_ditu(self):
        f = {"id": "x", "icono": "📘", "nombre": "Izena", "curso": "LH 3", "resumen": "Laburpena."}
        t = sare_sozialak.testua(f)
        self.assertEqual(sum(1 for w in t.split() if w.startswith("#")), 5)
        self.assertIn("x.html", t)


@unittest.skipUnless(HAY_NAVEGADOR, "Playwright/Chromium no disponible")
class PdfEtaKarruselaTest(unittest.TestCase):
    def test_pdf_eta_karrusela(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            env = dict(os.environ, KIMU_FECHA="2026-10-26")
            subprocess.run([sys.executable, "scripts/build.py"], cwd=ROOT, check=True, env=env, capture_output=True)
            site = ROOT / "_site"
            self.assertIn('href="pdf/gure-herria.pdf"', (site / "gure-herria.html").read_text(encoding="utf-8"))
            subprocess.run([sys.executable, "scripts/generar_pdf.py", "--solo", "gure-herria", "--cache", str(tmp / "c")],
                           cwd=ROOT, check=True, env=env, capture_output=True)
            pdf = (site / "pdf" / "gure-herria.pdf").read_bytes()
            conzuz = (site / "pdf" / "gure-herria-zuzenketa.pdf").read_bytes()
            self.assertTrue(pdf.startswith(b"%PDF"))
            self.assertGreater(len(conzuz), len(pdf))
            salida = tmp / "ss"
            subprocess.run([sys.executable, "scripts/sare_sozialak.py", "--irteera", str(salida)], cwd=ROOT, check=True,
                           env=env, capture_output=True)
            (salida / "ikusiak.json").write_text('["gure-herria-teoria"]', encoding="utf-8")
            subprocess.run([sys.executable, "scripts/sare_sozialak.py", "--irteera", str(salida), "--max", "1"], cwd=ROOT,
                           check=True, env=env, capture_output=True)
            carpeta = next(d for d in salida.iterdir() if d.is_dir())
            for i in range(1, 5):
                cabecera = (carpeta / f"{i}.png").read_bytes()[16:24]
                self.assertEqual(struct.unpack(">II", cabecera), (1080, 1350))
            self.assertTrue((carpeta / "testua.txt").is_file())


if __name__ == "__main__":
    unittest.main()
