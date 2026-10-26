import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import generar_mate
import kalitatea


UNITATEAK = (
    "lh1-zenbakiak-20",
    "lh1-konposaketa",
    "lh1-batuketak-20",
    "lh1-kenketak-20",
    "lh1-zenbakiak-100",
)
MAILAK = ("indartzeko", "sendotzeko", "sakontzeko", "berrikusketa")


class GenerarMateLH1Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directorio = tempfile.TemporaryDirectory()
        cls.fitxak_originalak = generar_mate.FITXAK
        generar_mate.FITXAK = Path(cls.directorio.name)
        for unitatea in UNITATEAK:
            generar_mate.generar(unitatea, "A")
        cls.fichas = {
            path.stem: json.loads(path.read_text(encoding="utf-8"))
            for path in Path(cls.directorio.name).glob("*.json")
        }

    @classmethod
    def tearDownClass(cls):
        generar_mate.FITXAK = cls.fitxak_originalak
        cls.directorio.cleanup()

    def test_genera_los_cinco_packs_con_cuatro_niveles_en_borrador(self):
        self.assertEqual(len(self.fichas), len(UNITATEAK) * len(MAILAK))
        for unitatea in UNITATEAK:
            for maila in MAILAK:
                with self.subTest(unitatea=unitatea, maila=maila):
                    ficha = self.fichas[f"mate-{unitatea}-{maila}"]
                    self.assertEqual(ficha["arlo"], "lh1-matematika")
                    self.assertEqual(ficha["seccion"], "lh1-unitateak-mate")
                    self.assertEqual(ficha["curso"], "LH 1")
                    self.assertFalse(ficha["publicado"])
                    self.assertTrue(ficha["generado"])
                    if maila == "indartzeko":
                        self.assertIn("egokitua", ficha["nombre"])

    def test_todas_las_fichas_superan_el_minimo_de_calidad(self):
        for ficha in self.fichas.values():
            with self.subTest(ficha=ficha["id"]):
                nota, faltas = kalitatea.puntuar(ficha)
                self.assertGreaterEqual(nota, 9.5, faltas)

    def test_hojas_y_ejercicios_cumplen_los_limites_lh1(self):
        for ficha in self.fichas.values():
            for hoja in ficha["hojas"]:
                ejercicios = [b for b in hoja["bloques"] if b["tipo"] == "ejercicio"]
                self.assertTrue(2 <= len(ejercicios) <= 3)
                self.assertLessEqual(len(hoja["titulo"]), 24)
                self.assertTrue(hoja.get("tamano") == "grande" or hoja.get("egokitua"))
                for ejercicio in ejercicios:
                    n = len(ejercicio.get("frases", ejercicio.get("items", [])))
                    self.assertLessEqual(n, 4)
                    self.assertTrue(ejercicio.get("ejemplo"))
                    self.assertRegex(ejercicio["enunciado"], r"^[^\w\s]")

        for unitatea in UNITATEAK:
            ficha = self.fichas[f"mate-{unitatea}-indartzeko"]
            for hoja in ficha["hojas"]:
                self.assertTrue(hoja["egokitua"])
                for bloque in hoja["bloques"]:
                    if bloque["tipo"] == "ejercicio":
                        self.assertLessEqual(len(bloque.get("frases", bloque.get("items", []))), 3)

    def test_batuketek_20ko_muga_eta_eramateen_mailak_errespetatzen_dituzte(self):
        for maila in MAILAK:
            ficha = self.fichas[f"mate-lh1-batuketak-20-{maila}"]
            for hoja in ficha["hojas"]:
                for bloque in hoja["bloques"]:
                    if bloque.get("modo") != "operaciones":
                        continue
                    for item in bloque["items"]:
                        a, b = int(item["a"]), int(item["b"])
                        self.assertLessEqual(a + b, 20)
                        if maila in ("indartzeko", "sendotzeko"):
                            self.assertLess(a % 10 + b % 10, 10)
                        if maila == "sakontzeko":
                            self.assertGreaterEqual(a % 10 + b % 10, 10)

    def test_unidades_incluyen_los_recursos_visuales_especificos(self):
        count = self.fichas["mate-lh1-zenbakiak-20-sendotzeko"]
        self.assertTrue(any(":red-apple:" in frase or ":pencil:" in frase
                            for hoja in count["hojas"] for bloque in hoja["bloques"]
                            for frase in bloque.get("frases", [])))
        self.assertTrue(any(b["tipo"] == "dibujo" for hoja in count["hojas"] for b in hoja["bloques"]))

        konposaketa = self.fichas["mate-lh1-konposaketa-sendotzeko"]
        self.assertTrue(any(":house:" in frase for hoja in konposaketa["hojas"]
                            for bloque in hoja["bloques"] for frase in bloque.get("frases", [])))

        batuketak = self.fichas["mate-lh1-batuketak-20-sendotzeko"]
        self.assertTrue(any(b["tipo"] == "zuzena" for hoja in batuketak["hojas"] for b in hoja["bloques"]))

        kenketak = self.fichas["mate-lh1-kenketak-20-sendotzeko"]
        self.assertTrue(any("~:" in frase for hoja in kenketak["hojas"] for bloque in hoja["bloques"]
                            for frase in bloque.get("frases", [])))

        zenbakiak = self.fichas["mate-lh1-zenbakiak-100-sendotzeko"]
        frases = [frase for hoja in zenbakiak["hojas"] for bloque in hoja["bloques"]
                  for frase in bloque.get("frases", [])]
        self.assertTrue(any("🟥" in frase and "🟦" in frase for frase in frases))
        self.assertTrue(any("━━━━" in frase for frase in frases))
        self.assertTrue(any("H" in frase and "B" in frase for frase in frases))


if __name__ == "__main__":
    unittest.main()
