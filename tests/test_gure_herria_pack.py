import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FITXAK = ROOT / "contenido" / "fitxak"


def fitxa(ident):
    return json.loads((FITXAK / f"{ident}.json").read_text(encoding="utf-8"))


class GureHerriaPackTest(unittest.TestCase):
    def test_packak_teoria_erronka_eta_mapak_ditu(self):
        section = json.loads(
            (ROOT / "contenido" / "secciones" / "gure-herria.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(section["tipo"], "pack")
        self.assertEqual(section["arlo"], "ingurunea")

        theory = fitxa("gure-herria-teoria")
        mental_map = theory["hojas"][-1]["bloques"][0]
        self.assertEqual(mental_map["tipo"], "mapa")
        self.assertTrue(all(branch.get("imagen") for branch in mental_map["ramas"]))

        activities = fitxa("gure-herria-ariketak")
        self.assertEqual(
            activities["hojas"][-1]["titulo"], "ERRONKA: GURE AUZOA"
        )
        self.assertEqual(activities["hojas"][-1]["bloques"][-1]["tipo"], "berrikusi")

    def test_estazioak_eta_errepaso_txartelak_osorik_daude(self):
        stations = fitxa("gure-herria-estazioak")
        station_cards = stations["hojas"][0]["bloques"][1]["items"]
        passport = stations["hojas"][0]["bloques"][2]
        self.assertEqual(len(station_cards), 4)
        self.assertEqual(len(passport["filas"]), 4)
        self.assertTrue(stations["soluciones"])

        review = fitxa("gure-herria-errepasoa")
        cards = review["hojas"][0]["bloques"][0]["items"]
        self.assertEqual(len(cards), 12)
        self.assertTrue(all(card.get("atzea") and card.get("imagen") for card in cards))
        self.assertEqual(len(review["hojas"][1]["bloques"][0]["solucion"]), 12)

    def test_infografia_horizontalak_bost_pauso_eta_autoebaluazioa_ditu(self):
        infographic = fitxa("gure-herria-infografia")["hojas"][0]
        self.assertEqual(infographic["orientacion"], "horizontal")
        cards = infographic["bloques"][0]["items"]
        self.assertEqual(len(cards), 5)
        self.assertTrue(all("→" in card["titulo"] for card in cards[:4]))

        key_ideas = next(
            block["texto"]
            for block in infographic["bloques"]
            if block.get("titulo") == "FUNTSEZKOA"
        )
        self.assertEqual(len(key_ideas.splitlines()), 3)
        self.assertTrue(any(block.get("titulo") == "GALDE ZURE BURUARI" for block in infographic["bloques"]))


if __name__ == "__main__":
    unittest.main()
