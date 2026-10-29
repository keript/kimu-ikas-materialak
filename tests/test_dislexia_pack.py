import json
import unittest
from pathlib import Path

from scripts.build import extraer_minijuegos, extraer_preguntas_jolasa


RAIZ = Path(__file__).resolve().parents[1]
FITXAK = RAIZ / "contenido" / "fitxak"
PACK_IDAK = {
    "dislexia-irakurgaiak",
    "dislexia-irakurmena-ariketak",
    "dislexia-soinuak",
    "dislexia-soinuak-ariketak",
    "dislexia-letrak",
    "dislexia-letrak-ariketak",
    "dislexia-irakaslearen-gida",
}


def kargatu_fitxa(identifikatzailea):
    return json.loads((FITXAK / f"{identifikatzailea}.json").read_text(encoding="utf-8"))


def blokeak(fitxa):
    return [b for h in fitxa["hojas"] for b in h["bloques"]]


class DislexiaPackTest(unittest.TestCase):
    def test_paketeak_ficha_berriak_eta_beharrak_biltzen_ditu(self):
        sekzioa = json.loads(
            (RAIZ / "contenido" / "secciones" / "dislexia-irakurketa.json").read_text(encoding="utf-8")
        )

        self.assertEqual(sekzioa["id"], "dislexia-irakurketa")
        self.assertEqual(sekzioa["tipo"], "pack")
        for identifikatzailea in PACK_IDAK:
            fitxa = kargatu_fitxa(identifikatzailea)
            self.assertEqual(fitxa["seccion"], sekzioa["id"])
            self.assertIn("dislexia", fitxa["beharrak"])
            self.assertFalse(fitxa["publicado"])

    def test_irakurgaiak_sei_bikotetan_eta_audioarekin_daude(self):
        fitxa = kargatu_fitxa("dislexia-irakurgaiak")
        irakurketak = [b for b in blokeak(fitxa) if b["tipo"] == "lectura"]
        audioak = [b for b in blokeak(fitxa) if b["tipo"] == "entzun"]

        self.assertEqual(len(irakurketak), 12)
        self.assertEqual(len(audioak), 6)
        self.assertEqual(
            {b["titulo"] for b in irakurketak},
            {"Ohiko irakurketa", "Irakurketa erraza"},
        )
        self.assertTrue(
            (RAIZ / "contenido" / "ilustraciones" / "dislexia-irakurketa-leihoa.svg").is_file()
        )

    def test_jarduera_berriek_erantzunak_eta_pantailako_jolasak_dituzte(self):
        for identifikatzailea in (
            "dislexia-irakurmena-ariketak",
            "dislexia-soinuak-ariketak",
            "dislexia-letrak-ariketak",
        ):
            fitxa = kargatu_fitxa(identifikatzailea)
            ariketak = [b for b in blokeak(fitxa) if b["tipo"] == "ejercicio"]
            self.assertTrue(all("solucion" in b for b in ariketak))
            self.assertTrue(extraer_minijuegos(fitxa)["lotu"])
            self.assertTrue(extraer_preguntas_jolasa(fitxa))
            for hoja in fitxa["hojas"]:
                if hoja.get("egokitua"):
                    for ariketa in (b for b in hoja["bloques"] if b["tipo"] == "ejercicio"):
                        elementuak = (
                            ariketa.get("frases")
                            or ariketa.get("items")
                            or ariketa.get("palabras")
                            or ariketa.get("izquierda")
                            or []
                        )
                        self.assertLessEqual(len(elementuak), 3)

    def test_soinu_eta_letra_jarduerak_eskatutako_moduak_lantzen_ditu(self):
        soinuak = kargatu_fitxa("dislexia-soinuak-ariketak")
        letrak = kargatu_fitxa("dislexia-letrak-ariketak")
        soinu_moduak = {b["modo"] for b in blokeak(soinuak) if b["tipo"] == "ejercicio"}
        letra_moduak = {b["modo"] for b in blokeak(letrak) if b["tipo"] == "ejercicio"}

        self.assertTrue({"completar", "elegir", "preguntas", "relacionar"} <= soinu_moduak)
        self.assertTrue({"elegir", "completar", "lineas", "relacionar"} <= letra_moduak)
        self.assertTrue(extraer_minijuegos(soinuak)["memoria"])
        self.assertTrue(extraer_minijuegos(letrak)["memoria"])


if __name__ == "__main__":
    unittest.main()
