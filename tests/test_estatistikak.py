import base64
import io
import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from jinja2 import Environment, FileSystemLoader
from scripts.egoera import obtener_estadisticas, resumir_estadisticas

RAIZ = Path(__file__).resolve().parents[1]


class EstadisticasTest(unittest.TestCase):
    def test_base_carga_el_script_solo_con_codigo(self):
        plantilla = Environment(loader=FileSystemLoader(RAIZ / "plantillas")).get_template("base.html")
        contexto = {
            "descripcion_meta": "",
            "borrador": False,
            "titulo_pestana": "Kimu",
            "volver": {"url": "index.html", "texto": "Inicio"},
            "kimu": "",
            "volver_abajo": None,
            "url_base": "/",
            "pagina_actual": "index.html",
            "kofi": "",
        }

        desactivado = plantilla.render(**contexto, estatistikak="")
        activado = plantilla.render(**contexto, estatistikak="kimu")

        self.assertNotIn("gc.zgo.at/count.js", desactivado)
        self.assertIn('data-goatcounter="https://kimu.goatcounter.com/count"', activado)

    def test_resumen_separa_pantallas_eventos_y_limita_paginas(self):
        hits = [
            {"path": "/inicio", "count": 12},
            {"path": "/inprimatu", "count": 8},
            {"path": "/jolasa-amaitu/fitxa-a/lotu", "count": 4},
            {"path": "/jolasa-amaitu/fitxa-a/galderak", "count": 3},
            *[{"path": f"/pagina-{i}", "count": i} for i in range(12)],
        ]

        resumen = resumir_estadisticas({"hits": hits})

        self.assertEqual(len(resumen["paginas"]), 10)
        self.assertNotIn(("inprimatu", 8), resumen["paginas"])
        self.assertEqual(resumen["juegos"], [("fitxa-a/lotu", 4), ("fitxa-a/galderak", 3)])

    @patch("scripts.egoera.urllib.request.urlopen")
    @patch.dict(os.environ, {}, clear=True)
    def test_sin_token_no_consulta_la_api(self, urlopen):
        self.assertIsNone(obtener_estadisticas())
        urlopen.assert_not_called()

    def test_consulta_los_siete_dias_con_el_token_de_api(self):
        respuesta = {"hits": [{"path": "/jolasa-amaitu/fitxa-a/lotu", "count": 5}]}
        with (
            patch.dict(os.environ, {"GOATCOUNTER_TOKEN": "token-prueba"}, clear=True),
            patch("scripts.build.estatistikak", "kimu"),
            patch("scripts.egoera.urllib.request.urlopen", return_value=io.BytesIO(json.dumps(respuesta).encode())) as urlopen,
        ):
            resumen = obtener_estadisticas()

        self.assertEqual(resumen["juegos"], [("fitxa-a/lotu", 5)])
        peticion = urlopen.call_args.args[0]
        self.assertIn("start=", peticion.full_url)
        self.assertIn("end=", peticion.full_url)
        self.assertIn("limit=1000", peticion.full_url)
        self.assertEqual(peticion.get_header("Authorization"), f"Basic {base64.b64encode(b':token-prueba').decode()}")


if __name__ == "__main__":
    unittest.main()
