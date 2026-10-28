import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FITXAK = ROOT / "contenido" / "fitxak"


def fitxa(ident):
    return json.loads((FITXAK / f"{ident}.json").read_text(encoding="utf-8"))


class GosariPackTest(unittest.TestCase):
    def test_fitxak_borradoreak_eta_teoria_ariketak_lotuak_daude(self):
        ids = (
            "gosari-osasuntsua-teoria",
            "gosari-osasuntsua-ariketak",
            "gosari-irakurgaia",
            "gosari-irakurgaia-galderak",
            "gosari-estazioak",
            "gosari-errepasoa",
            "gosari-infografia",
            "gosari-irakaslearen-gida",
        )
        fichas = [fitxa(ident) for ident in ids]
        self.assertTrue(all(not f["publicado"] for f in fichas))
        self.assertTrue(all(f["curso"] == "LH 3" for f in fichas))
        self.assertEqual(
            fitxa("gosari-osasuntsua-teoria")["relacionada"],
            "gosari-osasuntsua-ariketak",
        )
        self.assertEqual(
            fitxa("gosari-osasuntsua-ariketak")["relacionada"],
            "gosari-osasuntsua-teoria",
        )

    def test_jolasak_estazioak_eta_errepaso_txartelak_osorik_daude(self):
        activities = fitxa("gosari-osasuntsua-ariketak")
        modes = {
            b["modo"]
            for hoja in activities["hojas"]
            for b in hoja["bloques"]
            if b["tipo"] == "ejercicio"
        }
        self.assertTrue(
            {"relacionar", "clasificar", "elegir", "verdadero_falso"} <= modes
        )

        stations = fitxa("gosari-estazioak")
        cards = stations["hojas"][0]["bloques"][1]["items"]
        passport = stations["hojas"][0]["bloques"][2]
        self.assertEqual(len(cards), 4)
        self.assertEqual(len(passport["filas"]), 4)
        self.assertTrue(all(len(card["texto"].split()) <= 20 for card in cards))
        self.assertTrue(
            all(
                (ROOT / "estatico" / "irudiak" / f'{card["imagen"]}.svg').exists()
                for card in cards
            )
        )
        self.assertTrue(stations["soluciones"])

        review = fitxa("gosari-errepasoa")
        cards = next(
            b["items"]
            for b in review["hojas"][0]["bloques"]
            if b["tipo"] == "txartelak"
        )
        self.assertEqual(len(cards), 12)
        self.assertTrue(all(card.get("atzea") and card.get("imagen") for card in cards))

    def test_infografia_eta_irudi_eskaera(self):
        infographic = fitxa("gosari-infografia")["hojas"][0]
        self.assertEqual(infographic["orientacion"], "horizontal")
        self.assertEqual(len(infographic["bloques"][0]["items"]), 6)
        self.assertTrue(
            any(b.get("titulo") == "FUNTSEZKOA" for b in infographic["bloques"])
        )

        groups = json.loads(
            (ROOT / "contenido" / "irudiak" / "hiztegia-irudiak.json").read_text(
                encoding="utf-8"
            )
        )["taldeak"]
        gosari = next(g for g in groups if g["id"] == "gosari-osasuntsua")
        self.assertEqual(len(gosari["hitzak"]), 4)

    def test_irakurgaiko_galderek_kalitate_irizpideak_betetzen_dituzte(self):
        questions = fitxa("gosari-irakurgaia-galderak")
        blocks = [
            block
            for sheet in questions["hojas"]
            for block in sheet["bloques"]
        ]
        exercises = [block for block in blocks if block["tipo"] == "ejercicio"]
        modes = {block["modo"] for block in exercises}
        self.assertGreaterEqual(len(modes), 4)

        items = [
            str(item)
            for block in exercises
            for item in (
                block.get("frases")
                or block.get("items")
                or block.get("palabras")
                or block.get("izquierda")
                or []
            )
        ]
        self.assertGreaterEqual(
            sum(bool(re.search(r":[a-z0-9-]{3,}:", item)) for item in items)
            / len(items),
            0.6,
        )
        self.assertTrue(any("⭐" in block.get("enunciado", "") for block in exercises))
        self.assertTrue(
            any(block["tipo"] == "gogoratu" for block in blocks)
            or any(block.get("ejemplo") for block in exercises)
        )
        self.assertEqual(questions["hojas"][-1]["bloques"][-1]["tipo"], "berrikusi")


if __name__ == "__main__":
    unittest.main()
