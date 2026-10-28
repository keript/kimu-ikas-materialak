import os
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.egoera import obtener_estadisticas, resumir_estadisticas


class EstadisticasTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
