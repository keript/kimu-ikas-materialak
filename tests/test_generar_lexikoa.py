import unittest

from scripts.generar_lexikoa import GAIAK, RAIZ


class TemasLexikoaTest(unittest.TestCase):
    def test_los_nuevos_temas_cumplen_los_requisitos(self):
        nuevos = {
            "kirolak": {"Taldekoak", "Bakarkakoak", "Uretakoak edo elurrekoak"},
            "arropa": {"Negukoa", "Udakoa", "Oinetakoak eta osagarriak"},
            "lanbideak": {"Osasuna eta laguntza", "Janaria", "Artea eta beste"},
            "etxea": {"Gelak", "Altzariak", "Beste gauzak"},
        }

        for clave, categorias in nuevos.items():
            with self.subTest(tema=clave):
                tema = GAIAK[clave]
                self.assertTrue(14 <= len(tema["hitzak"]) <= 16)
                self.assertEqual(set(tema["kategoriak"]), categorias)
                self.assertEqual({categoria for _, _, categoria in tema["hitzak"]}, categorias)
                self.assertEqual(len(tema["esaldiak"]), 6)
                for palabra, imagen, _ in tema["hitzak"]:
                    self.assertTrue(palabra.endswith(("a", "ak")))
                    self.assertTrue((RAIZ / "estatico" / "irudiak" / f"{imagen}.svg").is_file())
                for frase, respuesta in tema["esaldiak"]:
                    self.assertTrue(frase.startswith("___"))
                    self.assertTrue(frase.endswith("."))
                    self.assertTrue(respuesta[0].isupper())


if __name__ == "__main__":
    unittest.main()
