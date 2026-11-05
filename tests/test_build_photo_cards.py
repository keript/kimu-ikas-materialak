import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import build


class PhotoCardsBuildTest(unittest.TestCase):
    def test_real_photos_reserve_space_and_defer_nonpriority_images(self):
        with tempfile.TemporaryDirectory() as temporal:
            salida = Path(temporal) / "_site"
            with patch.object(build, "SALIDA", salida):
                build.construir(False)

            html = (salida / "zatiketa-teoria.html").read_text(encoding="utf-8")
            suma_html = (salida / "gehiketa-kenketa-eramanekin.html").read_text(encoding="utf-8")
            elikadura_html = (salida / "elikadura-osasuntsua.html").read_text(encoding="utf-8")
            css = (salida / "fitxa.css").read_text(encoding="utf-8")

        self.assertIn("min(100vw - 28px, 480px)", css)
        self.assertIn("min(100vw - 40px, 920px)", css)
        self.assertIn('class="pie-logo" src="logoak/kimu-logo-zuribeltza.svg" alt="Kimu" width="446" height="166"', html)
        expectations = {
            "zatiketa-12-arkatz": ('width="827" height="478"', 'loading="eager"', 'fetchpriority="high"'),
            "zatiketa-3-estutxe": ('width="961" height="435"', 'loading="lazy"'),
            "zatiketa-5-plater": ('width="1016" height="275"', 'loading="lazy"'),
            "zatiketa-hondarra": ('width="1016" height="472"', 'loading="lazy"'),
        }
        for image, attrs in expectations.items():
            with self.subTest(image=image):
                start = html.index(f'src="irudiak-errealak/{image}.jpg"')
                tag = html[html.rfind("<img", 0, start):html.index(">", start) + 1]
                for attr in attrs:
                    self.assertIn(attr, tag)

        expectations = {
            "eramana-38": ('srcset="irudiak-errealak/eramana-38-480.jpg 480w, irudiak-errealak/eramana-38.jpg 965w"', 'width="965" height="450"', 'loading="lazy"'),
            "eramana-25": ('srcset="irudiak-errealak/eramana-25-480.jpg 480w, irudiak-errealak/eramana-25.jpg 954w"', 'width="954" height="387"', 'loading="lazy"'),
            "eramana-13": ('srcset="irudiak-errealak/eramana-13-480.jpg 480w, irudiak-errealak/eramana-13.jpg 926w"', 'width="926" height="345"', 'loading="lazy"'),
            "eramana-63": ('srcset="irudiak-errealak/eramana-63-480.jpg 480w, irudiak-errealak/eramana-63.jpg 890w"', 'width="890" height="484"', 'loading="lazy"'),
        }
        for image, attrs in expectations.items():
            with self.subTest(image=image):
                start = suma_html.index(f'src="irudiak-errealak/{image}.jpg"')
                tag = suma_html[suma_html.rfind("<img", 0, start):suma_html.index(">", start) + 1]
                for attr in attrs:
                    self.assertIn(attr, tag)

        expectations = {
            "elikadura-barazkiak": ('srcset="irudiak-errealak/elikadura-barazkiak-480.jpg 480w, irudiak-errealak/elikadura-barazkiak.jpg 872w"', 'width="872" height="515"', 'loading="eager"', 'fetchpriority="high"'),
            "elikadura-proteinak": ('srcset="irudiak-errealak/elikadura-proteinak-480.jpg 480w, irudiak-errealak/elikadura-proteinak.jpg 619w"', 'width="619" height="551"', 'loading="lazy"'),
            "elikadura-esnekiak": ('srcset="irudiak-errealak/elikadura-esnekiak-480.jpg 480w, irudiak-errealak/elikadura-esnekiak.jpg 914w"', 'width="914" height="422"', 'loading="lazy"'),
            "elikadura-platera": ('srcset="irudiak-errealak/elikadura-platera-480.jpg 480w, irudiak-errealak/elikadura-platera.jpg 695w"', 'width="695" height="544"', 'loading="lazy"'),
        }
        for image, attrs in expectations.items():
            with self.subTest(image=image):
                start = elikadura_html.index(f'src="irudiak-errealak/{image}.jpg"')
                tag = elikadura_html[elikadura_html.rfind("<img", 0, start):elikadura_html.index(">", start) + 1]
                for attr in attrs:
                    self.assertIn(attr, tag)


if __name__ == "__main__":
    unittest.main()
