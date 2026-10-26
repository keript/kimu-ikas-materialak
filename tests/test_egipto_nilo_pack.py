import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FITXAK = ROOT / "contenido" / "fitxak"


def fitxa(ident):
    return json.loads((FITXAK / f"{ident}.json").read_text(encoding="utf-8"))


class EgiptoNiloPackTest(unittest.TestCase):
    def test_packak_teoria_ariketak_eta_mapak_ditu(self):
        section = json.loads(
            (ROOT / "contenido" / "secciones" / "egipto-nilo.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(section["tipo"], "pack")
        self.assertEqual(section["arlo"], "ingurunea")

        theory = fitxa("egipto-nilo-teoria")
        activities = fitxa("egipto-nilo-ariketak")
        self.assertEqual(theory["relacionada"], activities["id"])
        self.assertEqual(activities["relacionada"], theory["id"])
        self.assertEqual(theory["curso"], "LH 3")
        self.assertTrue(theory["publicado"])
        self.assertTrue(activities["publicado"])
        self.assertEqual(theory["hojas"][-1]["bloques"][0]["tipo"], "mapa")

        exercise_modes = {
            block["modo"]
            for page in activities["hojas"]
            for block in page["bloques"]
            if block["tipo"] == "ejercicio"
        }
        self.assertTrue({"relacionar", "clasificar"} <= exercise_modes)
        self.assertTrue(activities["soluciones"])

    def test_kitak_estazioak_12_txartel_infografia_eta_gida_ditu(self):
        stations = fitxa("egipto-nilo-estazioak")
        cards = next(
            block
            for block in stations["hojas"][0]["bloques"]
            if block["tipo"] == "tarjetas"
        )
        passport = next(
            block
            for block in stations["hojas"][0]["bloques"]
            if block["tipo"] == "tabla"
        )
        self.assertEqual(len(cards["items"]), 4)
        self.assertEqual(len(passport["filas"]), 4)
        self.assertTrue(stations["soluciones"])

        review = fitxa("egipto-nilo-errepasoa")
        review_cards = review["hojas"][0]["bloques"][1]["items"]
        answers = review["hojas"][1]["bloques"][0]["solucion"]
        self.assertEqual(len(review_cards), 12)
        self.assertTrue(all(card.get("imagen") for card in review_cards))
        self.assertEqual(len(answers), 12)

        infographic = fitxa("egipto-nilo-infografia")["hojas"][0]
        self.assertEqual(infographic["orientacion"], "horizontal")
        self.assertEqual(len(infographic["bloques"][0]["items"]), 4)
        self.assertTrue(
            any(block.get("titulo") == "FUNTSEZKOA" for block in infographic["bloques"])
        )
        self.assertTrue(
            any(
                block.get("titulo") == "GALDE ZURE BURUARI"
                for block in infographic["bloques"]
            )
        )

        guide = fitxa("egipto-nilo-irakaslearen-gida")
        self.assertFalse(guide["hojas"][0]["datos"])
        self.assertEqual(len(guide["hojas"][0]["bloques"][1]["filas"]), 5)


if __name__ == "__main__":
    unittest.main()
