import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import build


ROOT = Path(__file__).resolve().parents[1]


class BingoBuildTest(unittest.TestCase):
    def test_build_supports_bingo_without_legacy_card_lists(self):
        with tempfile.TemporaryDirectory() as temporal:
            salida = Path(temporal) / "_site"
            leer_json = build.leer_json

            def bingo_sin_cartoiak(ruta):
                bingo = leer_json(ruta)
                if ruta.name == "bingoa-euskararen-eguna.json":
                    bingo.pop("kartoiak", None)
                    bingo.pop("kartoi_errazak", None)
                return bingo

            with patch.object(build, "SALIDA", salida), patch.object(build, "leer_json", side_effect=bingo_sin_cartoiak):
                build.construir(False)

            game = (salida / "bingoa-euskararen-eguna.html").read_text(encoding="utf-8")
            self.assertIn('option value="EE-4x4-0001"', game)
            self.assertIn('option value="EE-3x3-0001"', game)

    def test_build_generates_game_and_campaign_links_until_euskararen_eguna(self):
        with tempfile.TemporaryDirectory() as temporal:
            salida = Path(temporal) / "_site"
            with patch.object(build, "SALIDA", salida), patch.dict(os.environ, {"KIMU_FECHA": "2026-11-11"}):
                build.construir(False)

            game = (salida / "bingoa-euskararen-eguna.html").read_text(encoding="utf-8")
            sortzailea = (salida / "jolas-sortzailea.html").read_text(encoding="utf-8")
            portada = (salida / "index.html").read_text(encoding="utf-8")
            euskara = (salida / "euskara.html").read_text(encoding="utf-8")
            self.assertIn('href="deskargak/kimu-bingoa-euskararen-eguna-LH3.pdf"', game)
            self.assertIn("EE-4x4-0007", game)
            self.assertIn('href="jolas-sortzailea.html"', portada)
            self.assertIn("sortzaile-kopurua", sortzailea)
            self.assertIn("Inprimatu kartoiak", sortzailea)
            self.assertIn('id="mode-caller"', game)
            self.assertIn('id="mode-check"', game)
            self.assertIn('id="mode-card"', game)
            self.assertIn('href="bingoa-euskararen-eguna.html"', portada)
            self.assertIn('href="bingoa-euskararen-eguna.html"', euskara)
            self.assertIn('data-bilaketa', game)

            with patch.object(build, "SALIDA", salida), patch.dict(os.environ, {"KIMU_FECHA": "2026-12-04"}):
                build.construir(False)

            portada = (salida / "index.html").read_text(encoding="utf-8")
            euskara = (salida / "euskara.html").read_text(encoding="utf-8")
            self.assertNotIn('href="bingoa-euskararen-eguna.html"', portada)
            self.assertNotIn('href="bingoa-euskararen-eguna.html"', euskara)
            self.assertTrue((salida / "bingoa-euskararen-eguna.html").is_file())


if __name__ == "__main__":
    unittest.main()
