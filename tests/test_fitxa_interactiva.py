import json
import unittest
from html.parser import HTMLParser
from pathlib import Path

from scripts.build import SALIDA, construir


class FichaInteractivaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tiene_boton = False
        self.tiene_panel = False
        self.ejercicios = []

    def handle_starttag(self, tag, attrs):
        atributos = dict(attrs)
        self.tiene_boton |= tag == "button" and "data-egin-pantailan" in atributos
        self.tiene_panel |= "data-pantaila-ariketak" in atributos
        if "data-ejercicio" in atributos:
            self.ejercicios.append(json.loads(atributos["data-ejercicio"]))


class FichaInteractivaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        construir(False)

    def leer_ficha(self, identificador):
        parser = FichaInteractivaParser()
        parser.feed((Path(SALIDA) / f"{identificador}.html").read_text(encoding="utf-8"))
        return parser

    def test_fichas_de_actividades_incluyen_boton_panel_y_datos_de_autocorreccion(self):
        parsers = [
            self.leer_ficha("gure-herria-ariketak"),
            self.leer_ficha("mate-1-1-berrikusketa"),
        ]

        self.assertTrue(all(parser.tiene_boton and parser.tiene_panel for parser in parsers))
        ejercicios = [item for parser in parsers for item in parser.ejercicios]
        self.assertTrue(any(item.get("solucion") for item in ejercicios))
        self.assertTrue(
            {"completar", "elegir", "verdadero_falso", "relacionar", "clasificar"}
            <= {item["modo"] for item in ejercicios}
        )

    def test_fichas_de_teoria_no_muestran_el_modo_interactivo(self):
        parser = self.leer_ficha("gure-herria-teoria")

        self.assertFalse(parser.tiene_boton)
        self.assertFalse(parser.tiene_panel)


if __name__ == "__main__":
    unittest.main()
