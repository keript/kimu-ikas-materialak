import unittest

from scripts.build import extraer_preguntas_jolasa
from scripts.kalitatea import puntuar
from scripts.generar_lexikoa import pack_lh1, temas_lh1


class LexikoaLH1Test(unittest.TestCase):
    def test_lau_packek_hiztegia_ariketak_eta_txartelak_sortzen_dituzte(self):
        temas = temas_lh1()
        self.assertEqual(
            [tema["id"] for tema in temas],
            ["eguraldia", "urtaroak", "animaliak", "eskola-etxea"],
        )

        for i, tema in enumerate(temas):
            with self.subTest(tema=tema["id"]):
                section, fichas = pack_lh1(tema, 20 + i * 10)
                self.assertEqual(section["id"], f'lh1-{tema["id"]}')
                self.assertEqual(section["tipo"], "pack")
                self.assertEqual(len(fichas), 3)
                self.assertTrue(all(not ficha["publicado"] for ficha in fichas))
                self.assertTrue(all(ficha["curso"] == "LH 1" for ficha in fichas))

                theory, activities, cards = fichas
                theory_pages = theory["hojas"][:-1]
                self.assertTrue(all(
                    4 <= len(hoja["bloques"][0]["items"]) <= 6
                    for hoja in theory_pages
                ))
                self.assertTrue(all(hoja["egokitua"] for hoja in theory_pages))
                self.assertEqual(theory["hojas"][-1]["bloques"][0]["tipo"], "mapa")
                self.assertLessEqual(
                    len(theory["hojas"][-1]["bloques"][0]["ramas"]), 4
                )

                exercise_blocks = [
                    block for page in activities["hojas"]
                    for block in page["bloques"]
                ]
                exercises = [
                    block for block in exercise_blocks if block["tipo"] == "ejercicio"
                ]
                self.assertTrue(all(block.get("ejemplo") for block in exercises))
                self.assertTrue(all(page["egokitua"] for page in activities["hojas"]))
                self.assertTrue(all(
                    sum(block["tipo"] == "ejercicio" for block in page["bloques"]) <= 2
                    for page in activities["hojas"]
                ))
                for block in exercises:
                    if block["modo"] == "relacionar":
                        self.assertLessEqual(len(block["izquierda"]), 3)
                    elif block["modo"] == "elegir":
                        self.assertLessEqual(len(block["items"]), 3)
                    elif block["modo"] == "clasificar":
                        self.assertLessEqual(len(block["palabras"]), 3)
                self.assertEqual(exercise_blocks[-1]["tipo"], "berrikusi")

                card_items = cards["hojas"][0]["bloques"][0]["items"]
                self.assertTrue(8 <= len(card_items) <= 12)
                self.assertTrue(all(
                    card["imagen"] and card["atzea"] for card in card_items
                ))
                self.assertGreaterEqual(
                    len(extraer_preguntas_jolasa(cards)), 8
                )
                self.assertGreaterEqual(
                    min(puntuar(ficha)[0] for ficha in fichas), 9.5
                )

    def test_animaliak_eta_gauzak_erabiltzen_dituzten_hitzak_daude(self):
        temas = {tema["id"]: {hitza for hitza, _ in tema["palabras"]} for tema in temas_lh1()}
        self.assertEqual(
            temas["animaliak"],
            {
                "astoa", "arraina", "elefantea", "erlea", "igela", "otsoa",
                "oilarra", "untxia", "urtxintxa", "usoa", "hartza",
            },
        )
        self.assertTrue({"aulkia", "ohea", "etxea", "ogia", "ura"} <= temas["eskola-etxea"])


if __name__ == "__main__":
    unittest.main()
