import json
import unittest
from pathlib import Path

from scripts.build import extraer_minijuegos, extraer_preguntas_jolasa


ROOT = Path(__file__).resolve().parents[1]
FITXAK = ROOT / "contenido" / "fitxak"


def fitxa(ident):
    return json.loads((FITXAK / f"{ident}.json").read_text(encoding="utf-8"))


class LanbideakPackTest(unittest.TestCase):
    def test_kitak_sei_fitxak_eta_teoria_ariketak_lotura_ditu(self):
        section = json.loads(
            (ROOT / "contenido" / "secciones" / "lanbideak.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(section["tipo"], "pack")
        self.assertEqual(section["arlo"], "ingurunea")

        ids = [
            "lanbideak-teoria",
            "lanbideak-ariketak",
            "lanbideak-estazioak",
            "lanbideak-txartelak",
            "lanbideak-infografia",
            "lanbideak-irakaslearen-gida",
        ]
        fichas = [fitxa(ident) for ident in ids]
        self.assertTrue(all(not ficha["publicado"] for ficha in fichas))
        self.assertEqual(fitxa(ids[0])["relacionada"], ids[1])
        self.assertEqual(fitxa(ids[1])["relacionada"], ids[0])
        self.assertTrue(all(ficha["curso"] == "LH 3" for ficha in fichas))

    def test_teoriak_mapa_eta_ariketek_jokoak_eta_erronka_dituzte(self):
        theory = fitxa("lanbideak-teoria")
        self.assertEqual(theory["hojas"][-1]["bloques"][0]["tipo"], "mapa")
        self.assertTrue(
            all(rama.get("imagen") for rama in theory["hojas"][-1]["bloques"][0]["ramas"])
        )

        activities = fitxa("lanbideak-ariketak")
        modes = {
            block.get("modo")
            for hoja in activities["hojas"]
            for block in hoja["bloques"]
            if block["tipo"] == "ejercicio"
        }
        self.assertTrue({"relacionar", "clasificar", "elegir", "verdadero_falso"} <= modes)
        self.assertEqual(activities["hojas"][-1]["bloques"][-1]["tipo"], "berrikusi")
        self.assertTrue(activities["soluciones"])
        activity_games = extraer_minijuegos(activities)
        self.assertTrue(activity_games["lotu"])
        self.assertTrue(activity_games["sailkatu"])
        self.assertTrue(extraer_preguntas_jolasa(activities))

        card_file = fitxa("lanbideak-txartelak")
        mini_games = extraer_minijuegos(card_file)
        self.assertTrue(mini_games["lotu"])
        self.assertTrue(mini_games["sailkatu"])
        self.assertTrue(mini_games["memoria"])
        self.assertTrue(extraer_preguntas_jolasa(card_file))
        self.assertEqual(
            card_file["hojas"][-1]["bloques"][-1]["tipo"], "berrikusi"
        )

    def test_estazioak_txartelak_eta_infografia_osorik_daude(self):
        stations = fitxa("lanbideak-estazioak")
        station_cards = stations["hojas"][0]["bloques"][1]["items"]
        self.assertEqual(len(station_cards), 4)
        self.assertEqual(len(stations["hojas"][0]["bloques"][2]["filas"]), 4)

        cards = fitxa("lanbideak-txartelak")
        review_cards = cards["hojas"][0]["bloques"][0]["items"]
        self.assertEqual(len(review_cards), 12)
        self.assertTrue(all(card.get("imagen") for card in review_cards))
        vocabulary_table = next(
            block
            for sheet in cards["hojas"]
            for block in sheet["bloques"]
            if block.get("tipo") == "tabla"
            and block.get("cabecera") == ["Euskara", "Gaztelania", "Etxeko hizkuntza"]
        )
        self.assertTrue(all(row[2] == "" for row in vocabulary_table["filas"]))

        infographic = fitxa("lanbideak-infografia")["hojas"][0]
        self.assertEqual(infographic["orientacion"], "horizontal")
        self.assertEqual(len(infographic["bloques"][0]["items"]), 5)
        self.assertTrue(any(block.get("titulo") == "FUNTSEZKOA" for block in infographic["bloques"]))


if __name__ == "__main__":
    unittest.main()
