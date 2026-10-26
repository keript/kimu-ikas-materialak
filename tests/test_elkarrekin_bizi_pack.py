import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FITXAK = ROOT / "contenido" / "fitxak"
IDS = (
    "teoria",
    "ariketak",
    "estazioak",
    "txartelak",
    "infografia",
    "irakaslearen-gida",
)


def fitxa(ident):
    return json.loads((FITXAK / f"elkarrekin-bizi-{ident}.json").read_text(encoding="utf-8"))


class ElkarrekinBiziPackTest(unittest.TestCase):
    def test_packak_sei_borradorekin_eta_teoria_ariketak_lotuta_ditu(self):
        section = json.loads(
            (ROOT / "contenido" / "secciones" / "elkarrekin-bizi.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(section["tipo"], "pack")
        self.assertEqual(section["arlo"], "ingurunea")

        fichas = [fitxa(ident) for ident in IDS]
        self.assertTrue(all(not ficha["publicado"] for ficha in fichas))
        self.assertTrue(all(ficha["curso"] == "LH 3" for ficha in fichas))
        self.assertTrue(all(ficha["seccion"] == section["id"] for ficha in fichas))
        self.assertEqual(fichas[0]["relacionada"], fichas[1]["id"])
        self.assertEqual(fichas[1]["relacionada"], fichas[0]["id"])

    def test_teoriak_maparekin_eta_ariketek_lau_modu_dituzte(self):
        theory = fitxa("teoria")
        mental_map = theory["hojas"][-1]["bloques"][0]
        self.assertEqual(mental_map["tipo"], "mapa")
        self.assertTrue(all(branch.get("imagen") for branch in mental_map["ramas"]))

        activities = fitxa("ariketak")
        exercises = [
            block
            for sheet in activities["hojas"]
            for block in sheet["bloques"]
            if block["tipo"] == "ejercicio"
        ]
        self.assertGreaterEqual(
            len({exercise["modo"] for exercise in exercises}), 4
        )
        self.assertTrue(all(exercise.get("solucion") for exercise in exercises))
        self.assertEqual(activities["hojas"][-1]["bloques"][-1]["tipo"], "berrikusi")

    def test_estazioak_txartelak_infografia_eta_gida_osorik_daude(self):
        stations = fitxa("estazioak")
        station_cards = stations["hojas"][0]["bloques"][1]["items"]
        passport = stations["hojas"][0]["bloques"][2]
        self.assertEqual(len(station_cards), 4)
        self.assertEqual(len(passport["filas"]), 4)
        self.assertTrue(stations["soluciones"])

        review = fitxa("txartelak")
        cards = review["hojas"][0]["bloques"][1]["items"]
        self.assertEqual(len(cards), 12)
        self.assertTrue(all(card.get("atzea") and card.get("imagen") for card in cards))
        self.assertEqual(len(review["hojas"][1]["bloques"][0]["solucion"]), 12)

        infographic = fitxa("infografia")["hojas"][0]
        self.assertEqual(infographic["orientacion"], "horizontal")
        self.assertEqual(len(infographic["bloques"][0]["items"]), 5)
        guide = fitxa("irakaslearen-gida")["hojas"][0]
        sessions = next(block for block in guide["bloques"] if block["tipo"] == "tabla")
        self.assertEqual(len(sessions["filas"]), 6)


if __name__ == "__main__":
    unittest.main()
