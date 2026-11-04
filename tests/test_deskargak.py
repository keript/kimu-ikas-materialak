import unittest

from scripts.build import ruta_asset, tamano_archivo


class DescargasTest(unittest.TestCase):
    def test_tamano_de_archivo_se_muestra_en_unidades_legibles(self):
        self.assertEqual(tamano_archivo(1024), "1,0 kB")
        self.assertEqual(tamano_archivo(1024 * 1024), "1,0 MB")

    def test_ruta_asset_solo_acepta_archivos_dentro_de_assets(self):
        self.assertIsNotNone(ruta_asset("lh1-alfabetoa/kimu-alfabetoa-posterra-a4.pdf"))
        self.assertIsNone(ruta_asset("../README.md"))
        self.assertIsNone(ruta_asset("no-existe.pdf"))


if __name__ == "__main__":
    unittest.main()
