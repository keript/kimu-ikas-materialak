import json
import unittest
from pathlib import Path

from scripts.kalitatea import puntuar


ROOT = Path(__file__).resolve().parents[1]
FITXAK = ROOT / "contenido" / "fitxak"


def fitxa(ident):
    return json.loads((FITXAK / f"{ident}.json").read_text(encoding="utf-8"))


class LandareakPackTest(unittest.TestCase):
    def test_teoria_zikloa_fotosintesia_eta_polinizazioa_ditu(self):
        theory = fitxa("landareen-mundua")
        texts = json.dumps(theory, ensure_ascii=False)

        for term in (
            "Zuhaitzak",
            "Zuhaixkak",
            "Belarrak",
            "Hazia → kimua → landarea → lorea → fruitua",
            "Argia + ura + airea → janaria + oxigenoa",
            "erleak.html",
            "Azenarioa",
            "Apioa",
            "Letxuga",
            "Brokolia",
            "Sagarra",
            "Babarrunak",
        ):
            self.assertIn(term, texts)
        self.assertEqual(theory["relacionada"], "landareen-mundua-ariketak")

    def test_pack_osatzen_duten_fitxak_borradoreak_dira(self):
        expected = (
            "landareak-estazioak",
            "landareak-infografia",
            "landareak-irakaslearen-gida",
            "landareak-lapbook",
        )
        for ident in expected:
            ficha = fitxa(ident)
            self.assertFalse(ficha["publicado"])
            self.assertEqual(ficha["arlo"], "ingurunea")
            self.assertEqual(ficha["curso"], "LH 3")
            self.assertEqual(ficha["seccion"], "landareak")

        stations = fitxa("landareak-estazioak")
        self.assertEqual(len(stations["hojas"][0]["bloques"][1]["items"]), 4)
        self.assertEqual(len(stations["hojas"][0]["bloques"][2]["filas"]), 4)
        self.assertTrue(stations["soluciones"])

        cards = fitxa("landareak-txartelak")
        self.assertEqual(len(cards["hojas"][0]["bloques"][1]["items"]), 12)
        self.assertEqual(len(cards["hojas"][0]["bloques"][5]["solucion"]), 12)

        infographic = fitxa("landareak-infografia")["hojas"][0]
        self.assertEqual(infographic["orientacion"], "horizontal")
        self.assertEqual(len(infographic["bloques"][0]["items"]), 6)

    def test_irudi_eskaerak_eta_kalitate_puntuazioa(self):
        vocabulary = json.loads(
            (ROOT / "contenido" / "irudiak" / "hiztegia-irudiak.json").read_text(
                encoding="utf-8"
            )
        )
        request = next(g for g in vocabulary["taldeak"] if g["id"] == "landareak-lh3")
        self.assertEqual(set(request["hitzak"]), {"zuhaixka", "belarra", "apioa", "babarrunak"})

        for ident in (
            "landareen-mundua",
            "landareen-mundua-ariketak",
            "landareen-atalak-irudiak",
            "landareen-atalak-etiketatu",
            "landareak-txartelak",
        ):
            score, missing = puntuar(fitxa(ident))
            self.assertGreaterEqual(score, 9.5, f"{ident}: {missing}")


if __name__ == "__main__":
    unittest.main()
