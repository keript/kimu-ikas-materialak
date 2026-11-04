import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MarkaGidaTest(unittest.TestCase):
    def test_brand_fonts_and_logos_are_present(self):
        assets = ROOT / "estatico"
        for font in (
            "andika-latin-400-normal.woff2",
            "andika-latin-700-normal.woff2",
        ):
            content = (assets / "fonts" / font).read_bytes()
            self.assertTrue(content.startswith(b"wOF2"))
        self.assertTrue((assets / "fonts" / "Andika-OFL.txt").is_file())
        for logo in (
            "kimu-logo-horizontala.svg",
            "kimu-logo-karratua.svg",
            "kimu-logo-zuribeltza.svg",
        ):
            self.assertTrue((assets / "logoak" / logo).is_file())

    def test_ficha_template_uses_area_level_and_print_logo(self):
        template = (ROOT / "plantillas" / "_hojas.html").read_text(encoding="utf-8")
        self.assertIn("h-maila", template)
        self.assertIn("arlo-{{ materia(f.arlo) }}", template)
        self.assertIn("logoak/kimu-logo-zuribeltza.svg", template)
        self.assertIn("f.id.startswith('lh1-')", template)

    def test_old_brand_colors_are_removed_except_math_notation(self):
        styles = (
            "area.css",
            "fitxa.css",
            "inicio.css",
            "jolasa.css",
            "bilaketa.css",
            "explicacion.css",
        )
        combined = "\n".join(
            (ROOT / "estatico" / filename).read_text(encoding="utf-8")
            for filename in styles
        ).lower()
        for old_color in ("#4f8a55", "#c46a12", "#b8783a"):
            self.assertNotIn(old_color, combined)
        math_green = [
            line for line in combined.splitlines() if "#38a64a" in line
        ]
        self.assertEqual(len(math_green), 2)
        self.assertTrue(all(".hoja.arlo-matematika" in line for line in math_green))


if __name__ == "__main__":
    unittest.main()
