import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.reel import _ffmpeg_args, aukeratu_orriak, fitxak_kargatu, iraupena


class ReelTest(unittest.TestCase):
    def test_soilik_argitaratutako_eta_programatu_gabeko_fitxak_erabiltzen_ditu(self):
        with tempfile.TemporaryDirectory() as tempdir:
            fitxa_dir = Path(tempdir)
            (fitxa_dir / "argitaratua.json").write_text(json.dumps({"id": "argitaratua", "publicado": True}))
            (fitxa_dir / "zirriborroa.json").write_text(json.dumps({"id": "zirriborroa", "publicado": False}))
            (fitxa_dir / "programatua.json").write_text(
                json.dumps({"id": "programatua", "publicado": True, "publicar_desde": "2026-12-01"})
            )
            (fitxa_dir / "argitaratu-da.json").write_text(
                json.dumps({"id": "argitaratu-da", "publicado": True, "publicar_desde": "2026-10-20"})
            )

            with patch.dict("os.environ", {"KIMU_FECHA": "2026-10-26"}):
                fitxak = fitxak_kargatu(
                    ["argitaratua", "zirriborroa", "programatua", "argitaratu-da"], fitxa_dir
                )
            self.assertEqual([f["id"] for f in fitxak], ["argitaratua", "argitaratu-da"])

    def test_lau_orri_hartu_eta_soluzioak_baztertzen_ditu(self):
        fitxa = {"hojas": [{"soluciones": False} for _ in range(5)] + [{"soluciones": True}]}

        self.assertEqual(aukeratu_orriak(fitxa), [0, 1, 2, 3])

    def test_reelak_12_edo_14_4_segundo_irauten_du(self):
        self.assertEqual(iraupena(1), 12)
        self.assertEqual(iraupena(3), 12)
        self.assertAlmostEqual(iraupena(4), 14.4)

    def test_ffmpegek_bideoa_bakarrik_sortzen_du_1080x1920an(self):
        komandoa = _ffmpeg_args([Path("bat.png"), Path("bi.png"), Path("hiru.png")], Path("reel.mp4"))
        filtroak = komandoa[komandoa.index("-filter_complex") + 1]

        self.assertIn("s=1080x1920", filtroak)
        self.assertIn("fps=30", filtroak)
        self.assertIn("-an", komandoa)
        self.assertIn("-preset", komandoa)
        self.assertIn("veryfast", komandoa)


if __name__ == "__main__":
    unittest.main()
