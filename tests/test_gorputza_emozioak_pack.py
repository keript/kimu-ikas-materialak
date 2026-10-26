import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FITXAK = ROOT / "contenido" / "fitxak"
IDS = (
    "gorputza-emozioak-teoria",
    "gorputza-emozioak-ariketak",
    "gorputza-emozioak-estazioak",
    "gorputza-emozioak-txartelak",
    "gorputza-emozioak-infografia",
    "gorputza-emozioak-irakaslearen-gida",
)


def fitxa(ident):
    return json.loads((FITXAK / f"{ident}.json").read_text(encoding="utf-8"))


class GorputzaEmozioakPackTest(unittest.TestCase):
    def test_packa_lh3koa_da_eta_fichak_zirriborroak_dira(self):
        section = json.loads(
            (ROOT / "contenido" / "secciones" / "gorputza-emozioak.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(section["tipo"], "pack")
        self.assertEqual(section["arlo"], "ingurunea")
        for ident in IDS:
            self.assertFalse(fitxa(ident)["publicado"])
            self.assertEqual(fitxa(ident)["curso"], "LH 3")

        theory = fitxa("gorputza-emozioak-teoria")
        exercises = fitxa("gorputza-emozioak-ariketak")
        self.assertEqual(theory["relacionada"], exercises["id"])
        self.assertEqual(exercises["relacionada"], theory["id"])
        self.assertEqual(theory["hojas"][-1]["bloques"][0]["tipo"], "mapa")

    def test_estazioak_txartelak_eta_infografia(self):
        stations = fitxa("gorputza-emozioak-estazioak")
        station_cards = stations["hojas"][0]["bloques"][1]["items"]
        passport = stations["hojas"][0]["bloques"][2]
        self.assertEqual(len(station_cards), 4)
        self.assertEqual(len(passport["filas"]), 4)
        self.assertTrue(stations["soluciones"])

        cards = fitxa("gorputza-emozioak-txartelak")
        review_cards = cards["hojas"][0]["bloques"][1]["items"]
        self.assertEqual(len(review_cards), 12)
        self.assertTrue(
            all(card.get("atzea") and card.get("imagen") for card in review_cards)
        )
        answer_counts = [
            len(sheet["bloques"][0]["solucion"]) for sheet in cards["hojas"][3:]
        ]
        self.assertEqual(answer_counts, [6, 6])

        infographic = fitxa("gorputza-emozioak-infografia")["hojas"][0]
        self.assertEqual(infographic["orientacion"], "horizontal")
        self.assertEqual(len(infographic["bloques"][0]["items"]), 4)
        self.assertTrue(
            any(block.get("titulo") == "FUNTSEZKOA" for block in infographic["bloques"])
        )

    def test_ariketek_taupadak_emozioak_eta_pantaila_egunkaria_lantzen_dituzte(self):
        exercises = fitxa("gorputza-emozioak-ariketak")
        blocks = [
            block
            for sheet in exercises["hojas"]
            for block in sheet["bloques"]
        ]
        self.assertTrue(any(block.get("modo") == "relacionar" for block in blocks))
        self.assertTrue(any(block.get("modo") == "clasificar" for block in blocks))
        self.assertTrue(any(block.get("modo") == "elegir" for block in blocks))
        self.assertTrue(any(block.get("modo") == "verdadero_falso" for block in blocks))
        self.assertTrue(any(block.get("tipo") == "tabla" for block in blocks))
        self.assertTrue(
            any(sheet["titulo"] == "PANTAILA-EGUNKARIA" for sheet in exercises["hojas"])
        )
        self.assertTrue(
            any(sheet["titulo"] == "TAUPADAK ETA GRAFIKOA" for sheet in exercises["hojas"])
        )


if __name__ == "__main__":
    unittest.main()
