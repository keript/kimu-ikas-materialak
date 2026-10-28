import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch
import xml.etree.ElementTree as ET

from scripts.sare_sozialak import aukeratu_gaiak, argitaratu_issue, sortu_boza, svg_portada


class SareSozialakTest(unittest.TestCase):
    def test_portadak_eskatu_karratua_eta_istorio_bertikala(self):
        karratua = ET.fromstring(svg_portada("Mate", "🔢", "#fff0c2", "", zirkulua=True))
        bertikala = ET.fromstring(svg_portada("Mate", "🔢", "#fff0c2", ""))

        self.assertEqual((karratua.attrib["width"], karratua.attrib["height"]), ("320", "320"))
        self.assertEqual((bertikala.attrib["width"], bertikala.attrib["height"]), ("1080", "1920"))

    def test_asteko_bozketak_azken_bi_issue_materiala_aukeratzen_ditu(self):
        issues = [
            {"number": 73, "title": "Animalien fitxak", "state": "open", "labels": [{"name": "material"}]},
            {"number": 72, "title": "Instagram/Facebook: reels", "state": "open", "labels": [{"name": "material"}]},
            {"number": 71, "title": "PR ez da gai bat", "state": "open", "pull_request": {}, "labels": [{"name": "material"}]},
            {"number": 70, "title": "Euskara", "state": "open", "labels": [{"name": "material"}]},
            {"number": 69, "title": "Akats teknikoa", "state": "open", "labels": [{"name": "bug"}]},
        ]

        self.assertEqual([issue["number"] for issue in aukeratu_gaiak(issues)], [73, 70])

    def test_istorioak_bi_gaiak_eta_data_izenean_sartzen_ditu(self):
        issues = [
            {"number": 9, "title": "Ingurunea", "state": "open", "labels": [{"name": "material"}]},
            {"number": 8, "title": "Euskara", "state": "open", "labels": [{"name": "material"}]},
        ]
        with tempfile.TemporaryDirectory() as tempdir:
            with patch("scripts.sare_sozialak.RAIZ", Path(tempdir)), patch(
                "scripts.sare_sozialak.svg_png"
            ):
                route, gaiak = sortu_boza("keript/kimu-ikas-materialak", "test-token", date(2026, 10, 26), issues)
                svg = route.read_text(encoding="utf-8")

        self.assertEqual(route.name, "2026-10-26-bozketa.svg")
        self.assertEqual([issue["number"] for issue in gaiak], [9, 8])
        self.assertIn("Ingurunea", svg)
        self.assertIn("Euskara", svg)

    def test_astetako_issueak_artifaktuaren_esteka_eta_bio_proposamena_biltzen_ditu(self):
        topics = [{"number": 73, "title": "Ingurunea"}, {"number": 70, "title": "Euskara"}]
        with patch(
            "scripts.sare_sozialak.github_json",
            side_effect=[[], {"number": 74}, None],
        ) as request:
            number = argitaratu_issue(
                "keript/kimu-ikas-materialak", "test-token",
                "https://github.com/keript/kimu-ikas-materialak/actions/runs/123",
                date(2026, 10, 26), topics,
            )

        self.assertEqual(number, 74)
        creation = request.call_args_list[1].args[4]
        comment = request.call_args_list[2].args[4]["body"]
        self.assertIn("Argitaratzeko prest · 2026-W44", creation["title"])
        self.assertIn("Kimu 🌱", creation["body"])
        self.assertIn("/actions/runs/123", comment)


if __name__ == "__main__":
    unittest.main()
