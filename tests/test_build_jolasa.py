import unittest

from scripts.build import extraer_preguntas_jolasa, formato_marcado


class ExtraerPreguntasJolasaTest(unittest.TestCase):
    def test_formato_marcado_admite_enlaces_locales_y_rechaza_esquemas(self):
        enlace = formato_marcado('[Entzun «Erleak»](erleak.html)')
        inseguro = formato_marcado("[Kanpoko esteka](javascript:alert(1))")

        self.assertEqual(str(enlace), '<a href="erleak.html">Entzun «Erleak»</a>')
        self.assertNotIn("<a ", str(inseguro))
        self.assertIn("javascript:alert(1)", str(inseguro))

    def test_elegir_asocia_soluciones_por_etiqueta_y_admite_aclaraciones(self):
        ficha = {
            "hojas": [{
                "bloques": [{
                    "tipo": "ejercicio",
                    "modo": "elegir",
                    "enunciado": "Aukeratu erantzun zuzena.",
                    "items": [
                        {"texto": "a)", "opciones": ["Bizkaiko udaletan", "Bizkaiko Udaletan"]},
                        {"texto": "b)", "opciones": ["Euskararen eguna", "Euskararen Eguna"]},
                        {"texto": "c)", "opciones": ["Bilbo", "Bilboko udala"]},
                    ],
                    "solucion": ["a) Bizkaiko udaletan", "b) Euskararen Eguna", "c) Bilboko udala"],
                }],
            }],
        }

        questions = extraer_preguntas_jolasa(ficha)

        self.assertEqual(len(questions), 3)
        self.assertEqual(questions[0]["correcta"], 0)
        self.assertEqual(questions[1]["correcta"], 1)
        self.assertEqual(questions[2]["correcta"], 1)

    def test_verdagarriak_y_relacionar_generan_respuestas_correctas(self):
        ficha = {
            "hojas": [{
                "bloques": [
                    {
                        "tipo": "ejercicio",
                        "modo": "verdadero_falso",
                        "enunciado": "¿Verdadero o falso?",
                        "items": ["a) «Sol» es monosílaba.", "b) «Mariposa» tiene tres sílabas."],
                        "solucion": ["a) Verdadero", "b) Falso (tiene cuatro)"],
                    },
                    {
                        "tipo": "ejercicio",
                        "modo": "relacionar",
                        "enunciado": "Lotu.",
                        "izquierda": ["Araba", "Bizkaia"],
                        "derecha": ["Bilbo", "Gasteiz"],
                        "solucion": ["Araba → Gasteiz", "Bizkaia → Bilbo"],
                    },
                ],
            }],
        }

        questions = extraer_preguntas_jolasa(ficha, "es")

        self.assertEqual(len(questions), 4)
        self.assertEqual(questions[0]["opciones"], ["VERDADERO", "FALSO"])
        self.assertEqual(questions[0]["correcta"], 0)
        self.assertEqual(questions[1]["correcta"], 1)
        self.assertEqual(questions[2]["opciones"][questions[2]["correcta"]], "Gasteiz")
        self.assertEqual(questions[3]["opciones"][questions[3]["correcta"]], "Bilbo")

    def test_txartelak_usa_distractores_del_mismo_bloque_y_su_imagen(self):
        ficha = {
            "hojas": [{
                "bloques": [{
                    "tipo": "txartelak",
                    "items": [
                        {"aurrea": "Galdera 1", "atzea": "Erantzuna 1", "imagen": "carrot"},
                        {"aurrea": "Galdera 2", "atzea": "Erantzuna 2"},
                        {"aurrea": "Galdera 3", "atzea": "Erantzuna 3"},
                        {"aurrea": "Galdera 4", "atzea": "Erantzuna 4"},
                    ],
                }],
            }],
        }

        questions = extraer_preguntas_jolasa(ficha)

        self.assertEqual(len(questions), 4)
        self.assertEqual(len(questions[0]["opciones"]), 4)
        self.assertEqual(questions[0]["opciones"][questions[0]["correcta"]], "Erantzuna 1")
        self.assertEqual(questions[0]["imagen"], "carrot")

    def test_omite_ejercicios_sin_solucion_verificable(self):
        ficha = {
            "hojas": [{
                "bloques": [{
                    "tipo": "ejercicio",
                    "modo": "elegir",
                    "enunciado": "Aukeratu.",
                    "items": [{"texto": "", "opciones": ["A", "B"]}],
                }],
            }],
        }

        self.assertEqual(extraer_preguntas_jolasa(ficha), [])


if __name__ == "__main__":
    unittest.main()
