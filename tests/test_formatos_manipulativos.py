import unittest

from scripts.build import geometria_tablero, imagenes_usadas, preparar_fitxa


class FormatosManipulativosTest(unittest.TestCase):
    def test_tablero_coloca_casillas_en_un_camino_curvo(self):
        bloque = {
            "casillas": [{"texto": str(i), "tipo": "galdera"} for i in range(28)],
        }

        geometria = geometria_tablero(bloque)

        self.assertEqual(len(geometria["casillas"]), 28)
        self.assertIn("C", geometria["camino"])
        self.assertEqual(len({(c["x"], c["y"]) for c in geometria["casillas"]}), 28)

    def test_imagen_central_se_incluye_en_la_validacion_de_imagenes(self):
        self.assertEqual(imagenes_usadas({"tipo": "tablero", "imagen_centro": "potted-plant"}), {"potted-plant"})

    def test_flipbook_genera_una_hoja_por_pestana(self):
        ficha = {
            "color": "verde",
            "hojas": [{
                "titulo": "FLIPBOOK",
                "orientacion": "horizontal",
                "bloques": [{
                    "tipo": "flipbook",
                    "portada": {"titulo": "Landareak", "imagen": "potted-plant"},
                    "pestanas": [
                        {"titulo": f"Atala {i}", "ideia": "Ideia", "imagen": "leafy-green", "color": "verde"}
                        for i in range(4)
                    ],
                }],
            }],
        }

        hojas = preparar_fitxa(ficha)

        self.assertEqual(len(hojas), 4)
        self.assertEqual([h["bloques"][0]["orri_index"] for h in hojas], [0, 1, 2, 3])
        self.assertEqual([h["bloques"][0]["orri_total"] for h in hojas], [4] * 4)

    def test_tablero_saca_las_tarjetas_a_hojas_aparte(self):
        ficha = {
            "color": "verde",
            "soluciones": True,
            "hojas": [{
                "titulo": "TABLERO",
                "orientacion": "horizontal",
                "bloques": [{
                    "tipo": "tablero",
                    "imagen_centro": "potted-plant",
                    "casillas": [{"texto": str(i), "tipo": "galdera"} for i in range(24)],
                    "arauak": ["Jolastu."],
                    "txartelak": [{"reto": "Erronka", "solucion": "Erantzuna"}],
                }],
            }],
        }

        hojas = preparar_fitxa(ficha)

        tarjetas = [h for h in hojas if h["titulo"] == "ERRONKA-TXARTELAK"]
        self.assertEqual(len(tarjetas), 2)
        self.assertEqual({h["bloques"][0]["alde"] for h in tarjetas}, {"aurrea", "atzea"})
        self.assertIn("geo", hojas[0]["bloques"][0])


if __name__ == "__main__":
    unittest.main()
