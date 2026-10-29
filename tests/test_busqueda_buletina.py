import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import build


ROOT = Path(__file__).resolve().parents[1]


class BusquedaYBoletinaTest(unittest.TestCase):
    def test_formulario_se_oculta_sin_nombre_de_boletin(self):
        from jinja2 import Environment, FileSystemLoader

        plantilla = Environment(loader=FileSystemLoader(ROOT / "plantillas")).get_template("_buletina.html")

        self.assertEqual(plantilla.render(buletina=""), "")

    def test_indice_incluye_metadatos_y_palabras_de_las_fichas(self):
        recurso = {
            "id": "ibaiaren-eguna",
            "arlo": "euskara",
            "nombre": "Ibaiaren eguna",
            "curso": "LH 3",
            "tipo_material": "Irakurmena",
            "beharrak": ["dislexia"],
            "hojas": [{"bloques": [{"texto": "Nerbioi ibaia"}]}],
        }

        indice = build.crear_indice_busqueda(
            [recurso],
            {"euskara": {"nombre": "Euskara", "idioma": "eu"}},
        )

        self.assertEqual(indice[0]["id"], "ibaiaren-eguna")
        self.assertEqual(indice[0]["area"], "Euskara")
        self.assertEqual(indice[0]["curso"], "LH 3")
        self.assertEqual(indice[0]["tipo"], "Irakurmena")
        self.assertEqual(indice[0]["beharrak"], ["dislexia"])
        self.assertIn("nerbioi", indice[0]["palabras_clave"])
        self.assertIn("ibaia", indice[0]["palabras_clave"])

    def test_build_publica_indice_privacidad_y_formularios(self):
        with tempfile.TemporaryDirectory() as temporal:
            salida = Path(temporal) / "_site"
            with patch.object(build, "SALIDA", salida):
                build.construir(False)

            indice = json.loads((salida / "bilaketa.json").read_text(encoding="utf-8"))
            ids = {recurso["id"] for recurso in indice}
            self.assertIn("letra-larriak", ids)
            self.assertNotIn("buruketak-ariketak", ids)

            redirecciones = {"maiuskulak.html", "maiuskulak-jolasak.html"}
            for pagina in salida.glob("*.html"):
                if pagina.name not in redirecciones:
                    self.assertIn("data-bilaketa", pagina.read_text(encoding="utf-8"), pagina.name)

            portada = (salida / "index.html").read_text(encoding="utf-8")
            ficha = (salida / "letra-larriak.html").read_text(encoding="utf-8")
            privacidad = (salida / "pribatutasuna.html").read_text(encoding="utf-8")
            for html in (portada, ficha):
                self.assertIn('action="https://buttondown.com/api/emails/embed-subscribe/kimu"', html)
                self.assertIn('name="email"', html)
                self.assertIn('type="checkbox" name="consent" value="yes" required', html)
                self.assertIn('data-bilaketa', html)
            self.assertIn("Kimu proiektua (Iker)", privacidad)
            self.assertIn("Buttondown", privacidad)


if __name__ == "__main__":
    unittest.main()
