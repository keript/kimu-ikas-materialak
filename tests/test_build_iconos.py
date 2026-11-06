import unittest

from scripts.build import formato_marcado


class FormatoMarcadoTest(unittest.TestCase):
    def test_iconos_decorativos_se_cargan_de_forma_diferida(self):
        html = str(formato_marcado(":school:"))

        self.assertIn('src="irudiak/school.svg"', html)
        self.assertIn('loading="lazy"', html)

    def test_icono_inexistente_se_conserva_como_texto(self):
        self.assertEqual(str(formato_marcado(":icono-inexistente:")), ":icono-inexistente:")

    def test_colores_de_nork_y_nor(self):
        html = str(formato_marcado("{NORK:Anek} {NOR:sagarra}"))

        self.assertIn('<span class="marka-nork">Anek</span>', html)
        self.assertIn('<span class="marka-nor">sagarra</span>', html)

    def test_texto_de_nork_y_nor_se_escapa(self):
        html = str(formato_marcado("{NORK:<script>}"))

        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)


if __name__ == "__main__":
    unittest.main()
