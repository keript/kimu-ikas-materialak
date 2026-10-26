import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FITXAK = ROOT / "contenido" / "fitxak"


def fitxa(ident):
    return json.loads((FITXAK / f"{ident}.json").read_text(encoding="utf-8"))


class GenerosTextualesTest(unittest.TestCase):
    def test_packak_eta_fitxa_kideak_daude(self):
        idazmena = json.loads(
            (ROOT / "contenido" / "secciones" / "idazmena.json").read_text(encoding="utf-8")
        )
        literatura = json.loads(
            (ROOT / "contenido" / "secciones" / "literatura.json").read_text(encoding="utf-8")
        )
        self.assertEqual(idazmena["tipo"], "pack")
        self.assertEqual(literatura["tipo"], "pack")
        self.assertEqual(literatura["arlo"], "euskara")

        parejas = [
            ("komikia", "komikia-idazten"),
            ("ipuinaren-egitura", "ipuin-hasieratik"),
            ("egunerokoa", "egunerokoa-idazten"),
            ("eskaera-gutuna", "eskaera-gutuna-idazten"),
            ("jarraibideak", "jarraibideak-idazten"),
            ("albistea", "albistea-idazten"),
            ("euskal-mitologia", "euskal-mitologia-galderak"),
            ("iturriaren-zubia", "iturriaren-zubia-galderak"),
        ]
        for teoria_id, ariketak_id in parejas:
            with self.subTest(teoria=teoria_id):
                teoria, ariketak = fitxa(teoria_id), fitxa(ariketak_id)
                self.assertEqual(teoria["lugar"], "teoria")
                self.assertEqual(ariketak["lugar"], "actividades")
                self.assertEqual(teoria["relacionada"], ariketak_id)
                self.assertEqual(teoria["arlo"], "euskara")
                self.assertEqual(ariketak["arlo"], "euskara")

    def test_ipuinak_hiru_fitxa_progresibo_ditu(self):
        for ident in ("ipuin-hasieratik", "ipuin-korapiloa", "ipuin-amaiera"):
            with self.subTest(fitxa=ident):
                ficha = fitxa(ident)
                hoja = ficha["hojas"][0]
                self.assertTrue(hoja["egokitua"])
                self.assertTrue(any(b["tipo"] == "idazketa" for b in hoja["bloques"]))
                ejercicios = [b for b in hoja["bloques"] if b["tipo"] == "ejercicio"]
                self.assertTrue(all(b.get("ejemplo") for b in ejercicios))
                for ejercicio in ejercicios:
                    elementos = next(
                        (ejercicio[campo] for campo in ("items", "frases", "izquierda", "palabras") if campo in ejercicio),
                        [],
                    )
                    self.assertLessEqual(len(elementos), 3)

    def test_mitologia_irakurgaia_txartelak_eta_irudiak(self):
        lectura = fitxa("euskal-mitologia")
        texto = next(
            b for h in lectura["hojas"] for b in h["bloques"] if b["tipo"] == "lectura"
        )
        self.assertEqual(len(texto["parrafos"]), 6)

        repaso = fitxa("euskal-mitologia-galderak")
        tarjetas = next(
            b for h in repaso["hojas"] for b in h["bloques"] if b["tipo"] == "txartelak"
        )
        self.assertEqual(len(tarjetas["items"]), 12)
        self.assertTrue(all(t.get("imagen") and t.get("atzea") for t in tarjetas["items"]))

        solicitudes = json.loads(
            (ROOT / "contenido" / "irudiak" / "hiztegia-irudiak.json").read_text(encoding="utf-8")
        )
        grupo = next(g for g in solicitudes["taldeak"] if g["id"] == "euskal-mitologia")
        self.assertEqual(set(grupo["hitzak"]), {"mari", "basajaun", "lamia", "olentzero"})

    def test_elezahar_originala_eta_gutun_lagunartekoaren_esteka(self):
        elezaharra = fitxa("iturriaren-zubia")
        self.assertIn("originala da", elezaharra["hojas"][0]["bloques"][-1]["texto"])
        self.assertEqual(
            len(next(b for h in elezaharra["hojas"] for b in h["bloques"] if b["tipo"] == "lectura")["parrafos"]),
            6,
        )
        self.assertEqual(fitxa("eskaera-gutuna-idazten")["relacionada"], "gutuna-idazten")
        self.assertTrue((FITXAK / "gutuna-idazten.json").is_file())


if __name__ == "__main__":
    unittest.main()
