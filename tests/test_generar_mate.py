import random
import unittest

from scripts import generar_mate


class GenerarMateTest(unittest.TestCase):
    def test_todas_las_fitxak_indartzeko_tienen_ejemplo_y_maximo_tres_items(self):
        for unidad, generar in generar_mate.UNITATEAK.items():
            with self.subTest(unidad=unidad):
                _, niveles = generar(random.Random(f"2026-{unidad}-A"))
                for hoja in generar_mate.egokitu(niveles[0]):
                    for bloque in hoja["bloques"]:
                        if bloque.get("tipo") != "ejercicio":
                            continue
                        self.assertTrue(bloque.get("ejemplo"))
                        items = bloque.get("frases", bloque.get("items", []))
                        self.assertLessEqual(len(items), generar_mate.MAX_EGOK)

    def test_ejemplo_embebido_se_separa_de_los_items_de_completar(self):
        _, niveles = generar_mate.UNITATEAK["1.1"](random.Random("2026-1.1-A"))
        hoja = generar_mate.egokitu(niveles[0])[0]
        ejercicio = next(b for b in hoja["bloques"] if b.get("tipo") == "ejercicio")

        self.assertIn("8.660", ejercicio["ejemplo"])
        self.assertEqual(len(ejercicio["frases"]), 3)
        self.assertEqual(len(ejercicio["solucion"]), 3)

    def test_lineas_usa_la_primera_respuesta_como_ejemplo_y_la_quita_del_apoyo(self):
        _, niveles = generar_mate.UNITATEAK["ordua"](random.Random("2026-ordua-A"))
        hojas = generar_mate.egokitu(niveles[0])
        ejercicios = [
            bloque
            for hoja in hojas
            for bloque in hoja["bloques"]
            if bloque.get("tipo") == "ejercicio" and bloque.get("modo") == "lineas"
        ]
        ejercicio = ejercicios[0]
        hoja = next(h for h in hojas if ejercicio in h["bloques"])
        relojes = next(b for b in hoja["bloques"] if b.get("tipo") == "erlojuak")

        self.assertTrue(ejercicio["ejemplo"].startswith("a)"))
        self.assertTrue(ejercicio["solucion"][0].startswith("b)"))
        self.assertEqual(len(relojes["items"]), 3)
        self.assertEqual(relojes["columnas"], 5)
        self.assertEqual(relojes["items"][0]["letra"], "b")

    def test_completar_respeta_el_ejemplo_ya_resuelto(self):
        _, niveles = generar_mate.UNITATEAK["taulak"](random.Random("2026-taulak-A"))
        hoja = generar_mate.egokitu(niveles[0])[0]
        ejercicio = next(b for b in hoja["bloques"] if b.get("tipo") == "ejercicio")

        self.assertEqual(ejercicio["ejemplo"], "2 × 1 = **2**")
        self.assertEqual(len(ejercicio["frases"]), 3)


if __name__ == "__main__":
    unittest.main()
