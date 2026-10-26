import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FITXAK = ROOT / "contenido" / "fitxak"
UNITATEAK = (
    "biderketa-zifra-bat",
    "zatiketa-luzea",
    "zatikiak",
    "estatistika",
    "buruketak-lh3",
    "buruzko-kalkulua",
)
MAILAK = ("indartzeko", "sendotzeko", "sakontzeko", "berrikusketa")


def fitxa(unitatea, maila):
    ident = f"mate-{unitatea}-{maila}"
    return json.loads((FITXAK / f"{ident}.json").read_text(encoding="utf-8"))


def ejercicios(f):
    return [
        bloque
        for hoja in f["hojas"]
        for bloque in hoja["bloques"]
        if bloque["tipo"] == "ejercicio"
    ]


class GenerarMateLH3Test(unittest.TestCase):
    def test_las_seis_unidades_tienen_cuatro_niveles_generados(self):
        for unidad in UNITATEAK:
            with self.subTest(unidad=unidad):
                for maila in MAILAK:
                    f = fitxa(unidad, maila)
                    self.assertEqual(f["curso"], "LH 3")
                    self.assertTrue(f["generado"])
                    self.assertTrue(f["soluciones"])
                    self.assertLessEqual(len(f["hojas"]), 6)
                egokitua = fitxa(unidad, "indartzeko")
                self.assertTrue(all(h["egokitua"] for h in egokitua["hojas"]))
                self.assertTrue(all(b.get("ejemplo") for b in ejercicios(egokitua)))

    def test_multiplicacion_y_division_tienen_resultados_correctos(self):
        multiplicaciones = [
            item
            for maila in MAILAK
            for bloque in ejercicios(fitxa("biderketa-zifra-bat", maila))
            if bloque["modo"] == "operaciones"
            for item in bloque["items"]
        ]
        self.assertTrue(multiplicaciones)
        hay_traslado, sin_traslado = False, False
        for item in multiplicaciones:
            a, b = int(item["a"]), int(item["b"])
            self.assertLess(a * b, 10_000)
            lleva = any((a // 10**p % 10) * b >= 10 for p in range(3))
            hay_traslado |= lleva
            sin_traslado |= not lleva
        self.assertTrue(hay_traslado and sin_traslado)

        for maila in MAILAK:
            for bloque in ejercicios(fitxa("zatiketa-luzea", maila)):
                soluciones = bloque.get("solucion", [])
                soluciones = [soluciones] if isinstance(soluciones, str) else soluciones
                for solucion in soluciones:
                    encontrado = re.search(r"(\d+) : (\d+) = (\d+)(?:, hondarra (\d+))?", solucion)
                    if encontrado:
                        zatikizuna, zatitzailea, zatidura, hondarra = encontrado.groups()
                        hondarra = int(hondarra or 0)
                        self.assertEqual(int(zatikizuna), int(zatitzailea) * int(zatidura) + hondarra)
                        self.assertLess(hondarra, int(zatitzailea))

    def test_unidades_incluyen_las_actividades_del_temario(self):
        zatikiak = [fitxa("zatikiak", maila) for maila in MAILAK]
        archivos = {
            bloque.get("archivo")
            for ficha in zatikiak
            for hoja in ficha["hojas"]
            for bloque in hoja["bloques"]
            if bloque["tipo"] == "ilustracion"
        }
        self.assertIn("zatiki-zirkulua-herenak", archivos)
        self.assertIn("zatiki-laukizuzena-laurdenak", archivos)
        self.assertEqual(len(archivos), 5)
        for archivo in archivos:
            svg = (ROOT / "contenido" / "ilustraciones" / f"{archivo}.svg").read_text()
            self.assertIn('role="img"', svg)
            self.assertIn("aria-label", svg)

        estatistika = fitxa("estatistika", "sendotzeko")
        modos = {b["modo"] for b in ejercicios(estatistika)}
        self.assertIn("preguntas", modos)
        self.assertTrue(any(b["tipo"] == "tabla" for h in estatistika["hojas"] for b in h["bloques"]))
        self.assertTrue(any("barra-diagrama" in str(b) for h in estatistika["hojas"] for b in h["bloques"]))

        problemas = fitxa("buruketak-lh3", "sendotzeko")
        texto = str(problemas)
        self.assertIn("hurbilenera", texto)
        self.assertIn("Asmatu buruketa", texto)
        self.assertIn("Jarduera", texto)

        buruz = str(fitxa("buruzko-kalkulua", "sakontzeko"))
        for estrategia in ("bikoitza", "erdia", "hamar", "osatu"):
            self.assertIn(estrategia, buruz)

    def test_egokitua_hiru_item_gehienez_eta_kalitate_baimenduta(self):
        for unidad in UNITATEAK:
            f = fitxa(unidad, "indartzeko")
            for bloque in ejercicios(f):
                for campo in ("frases", "items", "izquierda", "palabras"):
                    if campo in bloque:
                        self.assertLessEqual(len(bloque[campo]), 3, (unidad, campo))

        ids = ",".join(f"mate-{unidad}-{maila}" for unidad in UNITATEAK for maila in MAILAK)
        resultado = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "kalitatea.py"),
                "--solo",
                ids,
                "--min",
                "9.5",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        self.assertNotIn("Ninguna ficha", resultado.stdout)
        self.assertIn("24 fichas", resultado.stdout)


if __name__ == "__main__":
    unittest.main()
