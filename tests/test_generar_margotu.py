import re
import unittest

from scripts.build import extraer_minijuegos, preparar_fitxa
from scripts.generar_margotu import aukerak, cargar, sortu_fitxa, MARGOTU


def calcular(op):
    a, signo, b = re.match(r"^(\d+)([+−×])(\d+)$", op).groups()
    a, b = int(a), int(b)
    return {"+": a + b, "−": a - b, "×": a * b}[signo]


class GenerarMargotuTest(unittest.TestCase):
    def test_aukerak_respetan_reglas(self):
        self.assertTrue(all(calcular(o) == 7 for o in aukerak(7, {"batuketa": 10})))
        self.assertEqual(aukerak(12, {"batuketa": 10}), [])
        self.assertTrue(all(calcular(o) == 14 and int(o.split("−")[0]) <= 20 for o in aukerak(14, {"kenketa": 20})))
        self.assertTrue(all(calcular(o) == 20 for o in aukerak(20, {"biderketa": [2, 5, 10]})))
        sin = aukerak(35, {"batuketa": 100, "kenketa": 100, "eramanik_gabe": True})
        self.assertNotIn("19+16", sin)
        self.assertNotIn("41−6", sin)
        self.assertIn("20+15", sin)

    def test_todos_los_dibujos_tienen_la_operacion_correcta(self):
        dibujos = sorted(MARGOTU.glob("*.json"))
        self.assertGreaterEqual(len(dibujos), 6)
        for ruta in dibujos:
            d, claves = cargar(ruta)
            f = sortu_fitxa(d, claves)
            bloque = f["hojas"][0]["bloques"][0]
            for fila, texto in zip(bloque["filas"], d["marrazkia"]):
                for celda, ch in zip(fila, texto):
                    if ch == ".":
                        self.assertIsNone(celda)
                    else:
                        self.assertEqual(calcular(celda["op"]), claves[ch]["emaitza"], f"{ruta.stem}: {celda}")

    def test_ficha_con_hoja_de_soluciones_y_juego(self):
        d, claves = cargar(MARGOTU / "kuia.json")
        f = sortu_fitxa(d, claves)
        self.assertFalse(f["publicado"])
        hojas = preparar_fitxa(f)
        self.assertEqual(len(hojas), 2)
        self.assertTrue(hojas[1]["bloques"][0]["solucion"])
        juego = extraer_minijuegos(f)["margotu"]
        self.assertEqual(len(juego), 1)
        self.assertEqual(juego[0]["leyenda"], f["hojas"][0]["bloques"][0]["leyenda"])


if __name__ == "__main__":
    unittest.main()
