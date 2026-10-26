import json
import runpy
import unittest
from pathlib import Path

from scripts.build import extraer_minijuegos


ROOT = Path(__file__).resolve().parents[1]
FITXAK = ROOT / "contenido" / "fitxak"


def fitxa(ident):
    return json.loads((FITXAK / f"{ident}.json").read_text(encoding="utf-8"))


class KontinenteakPackTest(unittest.TestCase):
    def test_pack_teoria_eta_mapamundia(self):
        section = json.loads(
            (ROOT / "contenido" / "secciones" / "kontinenteak-eta-ozeanoak.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(section["tipo"], "pack")
        self.assertEqual(section["arlo"], "ingurunea")

        theory = fitxa("kontinenteak-teoria")
        self.assertEqual(theory["curso"], "LH 3")
        self.assertTrue(theory["publicado"])
        self.assertEqual(theory["relacionada"], "kontinenteak-ariketak")
        self.assertEqual(len(theory["hojas"][0]["bloques"][0]["items"]), 7)
        self.assertEqual(len(theory["hojas"][1]["bloques"][0]["items"]), 5)
        mental_map = theory["hojas"][-1]["bloques"][0]
        self.assertEqual(mental_map["tipo"], "mapa")
        self.assertTrue(all(branch.get("imagen") for branch in mental_map["ramas"]))

        requests = json.loads(
            (ROOT / "contenido" / "irudiak" / "eskaerak.json").read_text(encoding="utf-8")
        )
        self.assertIn("mapamundia-kontinenteak", {image["id"] for image in requests["irudiak"]})
        labeling = runpy.run_path(str(ROOT / "scripts" / "irudi_etiketatuak.py"))
        labels = labeling["IRUDIAK"]
        self.assertEqual(len(labels["mapamundia-kontinenteak"]["etiketak"]), 12)
        empty_map = labeling["svg"](
            "mapamundia-kontinenteak", labels["mapamundia-kontinenteak"], True
        )
        self.assertIn('href="irudiak/world-map.svg"', empty_map)
        self.assertIn('href="irudiak-errealak/mapamundia-kontinenteak.jpg"', empty_map)

    def test_ariketek_lotu_sailkatu_eta_mapa_dituzte(self):
        activities = fitxa("kontinenteak-ariketak")
        self.assertTrue(activities["soluciones"])
        self.assertEqual(activities["relacionada"], "kontinenteak-teoria")
        modes = {
            block.get("modo")
            for sheet in activities["hojas"]
            for block in sheet["bloques"]
        }
        self.assertIn("relacionar", modes)
        self.assertIn("clasificar", modes)
        games = extraer_minijuegos(activities)
        self.assertTrue(games["lotu"])
        self.assertTrue(games["sailkatu"])
        map_sheet = next(sheet for sheet in activities["hojas"] if "ETIKETATU" in sheet["titulo"])
        self.assertTrue(
            any(
                block.get("archivo") == "mapamundia-kontinenteak-hutsik"
                for block in map_sheet["bloques"]
            )
        )

    def test_estazioak_txartelak_infografia_eta_gida(self):
        stations = fitxa("kontinenteak-estazioak")
        self.assertTrue(stations["soluciones"])
        self.assertEqual(len(stations["hojas"][0]["bloques"][1]["items"]), 4)
        self.assertEqual(len(stations["hojas"][0]["bloques"][2]["filas"]), 4)

        review = fitxa("kontinenteak-errepasoa")
        cards = review["hojas"][0]["bloques"][0]["items"]
        self.assertEqual(len(cards), 12)
        self.assertTrue(all(card.get("atzea") and card.get("imagen") for card in cards))
        self.assertEqual(
            sum(len(sheet["bloques"][0]["solucion"]) for sheet in review["hojas"][1:]),
            12,
        )

        infographic = fitxa("kontinenteak-infografia")["hojas"][0]
        self.assertEqual(infographic["orientacion"], "horizontal")
        self.assertEqual(len(infographic["bloques"][0]["items"]), 5)
        key_ideas = next(block["texto"] for block in infographic["bloques"] if block.get("titulo") == "FUNTSEZKOA")
        self.assertEqual(len(key_ideas.splitlines()), 3)
        self.assertTrue(any(block.get("titulo") == "GALDE ZURE BURUARI" for block in infographic["bloques"]))
        self.assertTrue(fitxa("kontinenteak-irakaslearen-gida")["hojas"][0]["datos"] is False)


if __name__ == "__main__":
    unittest.main()
