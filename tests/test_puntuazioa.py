import json
import unittest
from pathlib import Path

from scripts.build import extraer_minijuegos


ROOT = Path(__file__).resolve().parents[1]
FITXAK = ROOT / "contenido" / "fitxak"


def fitxa(ident):
    return json.loads((FITXAK / f"{ident}.json").read_text(encoding="utf-8"))


class PuntuazioaTest(unittest.TestCase):
    def test_teoria_eta_ariketak_argitaratuta_eta_elkarri_lotuak_daude(self):
        teoria = fitxa("puntuazioa")
        ariketak = fitxa("puntuazioa-ariketak")

        self.assertTrue(teoria["publicado"])
        self.assertTrue(ariketak["publicado"])
        self.assertEqual(teoria["curso"], "LH 3")
        self.assertEqual(ariketak["curso"], "LH 3")
        self.assertEqual(teoria["relacionada"], ariketak["id"])
        self.assertEqual(ariketak["relacionada"], teoria["id"])
        self.assertEqual(teoria["hojas"][-1]["orientacion"], "horizontal")
        self.assertEqual(teoria["hojas"][-1]["bloques"][-1]["tipo"], "mapa")
        self.assertTrue(
            all(rama.get("imagen") for rama in teoria["hojas"][-1]["bloques"][-1]["ramas"])
        )
        self.assertTrue(ariketak["soluciones"])
        self.assertTrue(
            all(
                bloque.get("ejemplo")
                for hoja in ariketak["hojas"]
                for bloque in hoja["bloques"]
                if bloque["tipo"] == "ejercicio"
            )
        )

    def test_lotu_eta_sailkatu_minijokoak_sortzen_dira(self):
        minijokoak = extraer_minijuegos(fitxa("puntuazioa-ariketak"))

        self.assertTrue(minijokoak["lotu"])
        self.assertTrue(minijokoak["sailkatu"])
        self.assertGreaterEqual(len(minijokoak["lotu"][0]["pares"]), 3)
        self.assertGreaterEqual(len(minijokoak["sailkatu"][0]["items"]), 4)


if __name__ == "__main__":
    unittest.main()
