import random
import unittest

from scripts.generar_mate import PRESUPUESTO, RAIZ, TEORIA_MATE, UNITATEAK, teoria_fitxa


class UnidadesMateNuevasTest(unittest.TestCase):
    unidades = ("dirua", "luzera", "edukiera-masa", "geometria")

    def test_generan_cuatro_niveles_y_juegos_con_soluciones(self):
        for unidad in self.unidades:
            with self.subTest(unidad=unidad):
                self.assertIn(unidad, UNITATEAK)
                self.assertGreater(PRESUPUESTO[unidad], 0)
                _, niveles = UNITATEAK[unidad](random.Random(2026))
                self.assertEqual(len(niveles), 4)
                ejercicios = [
                    bloque
                    for hoja in niveles[1]
                    for bloque in hoja["bloques"]
                    if bloque.get("tipo") == "ejercicio"
                ]
                modos = {bloque["modo"] for bloque in ejercicios}
                self.assertIn("relacionar", modos)
                self.assertIn("clasificar", modos)
                for bloque in ejercicios:
                    if bloque["modo"] in ("relacionar", "clasificar"):
                        self.assertTrue(bloque.get("solucion"))
                relacionar = next(b for b in ejercicios if b["modo"] == "relacionar")
                clasificar = next(b for b in ejercicios if b["modo"] == "clasificar")
                self.assertGreaterEqual(len(relacionar["izquierda"]), 3)
                self.assertGreaterEqual(len(clasificar["palabras"]), 4)

    def test_teorias_tienen_mapa_y_assets_existentes(self):
        for unidad in self.unidades:
            with self.subTest(unidad=unidad):
                ficha = teoria_fitxa(unidad)
                self.assertEqual(ficha["relacionada"], f"mate-{unidad}-indartzeko")
                self.assertEqual(ficha["lugar"], "teoria")
                mapa = ficha["hojas"][-1]["bloques"][0]
                self.assertEqual(mapa["tipo"], "mapa")
                self.assertTrue(all(rama.get("imagen") for rama in mapa["ramas"]))
                imagenes = [item[3] for item in TEORIA_MATE[unidad]["txartelak"]]
                imagenes += [rama["imagen"] for rama in mapa["ramas"]]
                self.assertTrue(all((RAIZ / "estatico" / "irudiak" / f"{i}.svg").is_file() for i in imagenes))


if __name__ == "__main__":
    unittest.main()
