import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FITXAK = ROOT / "contenido" / "fitxak"


def json_file(path):
    return json.loads(path.read_text(encoding="utf-8"))


class IkusizkoakPackTest(unittest.TestCase):
    def test_packak_bost_teoria_eta_ariketa_pare_ditu(self):
        section = json_file(ROOT / "contenido" / "secciones" / "ikusizkoak.json")
        self.assertEqual(section["tipo"], "pack")
        self.assertEqual(section["arlo"], "euskara")

        for ident in ("hiztegia", "ekintzak", "deskribapenak", "asmakizunak", "esaldiak"):
            with self.subTest(materiala=ident):
                theory = json_file(FITXAK / f"ikusizko-{ident}.json")
                activities = json_file(FITXAK / f"ikusizko-{ident}-ariketak.json")
                self.assertEqual(theory["relacionada"], activities["id"])
                self.assertEqual(activities["relacionada"], theory["id"])
                self.assertEqual(theory["hojas"][-1]["bloques"][-1]["tipo"], "mapa")
                self.assertTrue(activities["soluciones"])

                exercises = [
                    block
                    for hoja in activities["hojas"]
                    for block in hoja["bloques"]
                    if block["tipo"] == "ejercicio"
                ]
                self.assertGreaterEqual(len({exercise["modo"] for exercise in exercises}), 4)
                self.assertTrue(any(block["tipo"] == "berrikusi" for hoja in activities["hojas"] for block in hoja["bloques"]))
                self.assertTrue(any(block["tipo"] == "txartelak" for hoja in activities["hojas"] for block in hoja["bloques"]))

    def test_irudi_errealen_eskaerak_fitxetan_erabiltzen_dira(self):
        manifest = json_file(ROOT / "contenido" / "irudiak" / "hiztegia-irudiak.json")
        asked_images = {
            image
            for group in manifest["taldeak"]
            for image in group["hitzak"]
            if group["id"] in {"hiztegia-eskola", "hiztegia-etxea", "hiztegia-janaria", "hiztegia-animaliak", "ekintzak", "ekintzak-2", "deskribatu", "asmakizunak", "esaldiak"}
        }
        self.assertEqual(len(asked_images), 36)

        for path in FITXAK.glob("ikusizko-*.json"):
            ficha = json_file(path)
            if ficha["seccion"] != "ikusizkoak":
                continue
            text = path.read_text(encoding="utf-8")
            for image in asked_images:
                if f'"{image}"' in text or f":{image}:" in text:
                    self.assertTrue((ROOT / "estatico" / "irudiak" / f"{image}.svg").is_file(), image)


if __name__ == "__main__":
    unittest.main()
