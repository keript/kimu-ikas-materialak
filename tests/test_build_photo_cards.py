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
            css = (salida / "fitxa.css").read_text(encoding="utf-8")

        self.assertIn("min(100vw - 28px, 480px)", css)
        self.assertIn("min(100vw - 40px, 920px)", css)
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


if __name__ == "__main__":
    unittest.main()
