import json
import unittest
from pathlib import Path

from scripts.build import extraer_minijuegos, extraer_preguntas_jolasa


ROOT = Path(__file__).resolve().parents[1]
FITXAK = ROOT / "contenido" / "fitxak"


def fitxa(ident):
    return json.loads((FITXAK / f"{ident}.json").read_text(encoding="utf-8"))


class EsaldiMotakTest(unittest.TestCase):
    def test_fitxak_gramatika_packean_eta_elkarri_lotuta_daude(self):
        theory = fitxa("esaldi-motak")
        activities = fitxa("esaldi-motak-ariketak")
        section = json.loads(
            (ROOT / "contenido" / "secciones" / "gramatika.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(section["tipo"], "pack")
        self.assertEqual(theory["seccion"], "gramatika")
        self.assertEqual(activities["seccion"], "gramatika")
        self.assertEqual(theory["relacionada"], activities["id"])
        self.assertEqual(activities["relacionada"], theory["id"])

    def test_teoriak_lau_esaldi_motak_baiezkoak_eta_mapa_ditu(self):
        theory = fitxa("esaldi-motak")
        cards = [
            item
            for block in theory["hojas"][0]["bloques"]
            if block["tipo"] == "tarjetas"
            for item in block["items"]
        ]
        mental_map = theory["hojas"][-1]["bloques"][0]
        labels = {card["titulo"] for card in cards}

        self.assertTrue(
            {
                "Adierazpenezkoa",
                "Galderazkoa",
                "Harridurazkoa",
                "Aginduzkoa",
                "Baiezkoa",
                "Ezezkoa",
            }.issubset(labels)
        )
        self.assertTrue(all(card.get("imagen") for card in cards))
        self.assertEqual(mental_map["tipo"], "mapa")
        self.assertTrue(all(branch.get("imagen") for branch in mental_map["ramas"]))
        self.assertIn(
            "Galdera- eta harridura-ikurrak",
            theory["hojas"][0]["bloques"][-1]["texto"],
        )

    def test_ariketek_adibidea_jokoak_izar_guztiak_eta_zuzenketa_dituzte(self):
        activities = fitxa("esaldi-motak-ariketak")
        blocks = [
            block
            for hoja in activities["hojas"]
            for block in hoja["bloques"]
        ]
        exercises = [block for block in blocks if block["tipo"] == "ejercicio"]

        self.assertTrue(activities["soluciones"])
        self.assertEqual(blocks[0]["tipo"], "gogoratu")
        self.assertTrue({"relacionar", "clasificar", "elegir"}.issubset(
            {block["modo"] for block in exercises}
        ))
        self.assertTrue(all("⭐" in block["enunciado"] for block in exercises))
        self.assertEqual(blocks[-1]["tipo"], "berrikusi")
        minigames = extraer_minijuegos(activities)
        self.assertEqual(len(minigames["lotu"]), 1)
        self.assertEqual(len(minigames["sailkatu"]), 1)
        self.assertTrue(
            any(question["pregunta"].startswith("Aukeratu") for question in
                extraer_preguntas_jolasa(activities))
        )


if __name__ == "__main__":
    unittest.main()
