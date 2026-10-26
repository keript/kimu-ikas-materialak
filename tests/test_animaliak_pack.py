import json
import unittest
from pathlib import Path

from scripts.build import extraer_minijuegos, extraer_preguntas_jolasa


ROOT = Path(__file__).resolve().parents[1]
FITXAK = ROOT / "contenido" / "fitxak"


def fitxa(ident):
    return json.loads((FITXAK / f"{ident}.json").read_text(encoding="utf-8"))


def blokeak(f):
    return [b for h in f["hojas"] for b in h["bloques"]]


class AnimaliakPackTest(unittest.TestCase):
    def test_packa_eta_teoria_oinarrizkoak_osorik_daude(self):
        section = json.loads(
            (ROOT / "contenido" / "secciones" / "animaliak.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual((section["tipo"], section["arlo"]), ("pack", "ingurunea"))

        ids = [
            "animaliak-teoria",
            "animaliak-ariketak",
            "animaliak-estazioak",
            "animaliak-txartelak",
            "animaliak-infografia",
            "animaliak-irakaslearen-gida",
        ]
        fichas = [fitxa(ident) for ident in ids]
        self.assertTrue(all(f["publicado"] is False for f in fichas))
        self.assertTrue(all(f["arlo"] == "ingurunea" and f["curso"] == "LH 3" for f in fichas))

        theory = fitxa("animaliak-teoria")
        activities = fitxa("animaliak-ariketak")
        self.assertEqual(theory["relacionada"], activities["id"])
        self.assertEqual(activities["relacionada"], theory["id"])
        games = extraer_minijuegos(activities)
        self.assertTrue(games["lotu"])
        self.assertTrue(games["sailkatu"])
        self.assertTrue(games["memoria"])
        self.assertTrue(extraer_preguntas_jolasa(activities))
        table = next(b for b in blokeak(theory) if b["tipo"] == "tabla")
        self.assertEqual(len(table["filas"]), 5)
        self.assertEqual(len(table["cabecera"]), 5)
        self.assertTrue(any(b["tipo"] == "mapa" for b in blokeak(theory)))

    def test_estazioak_txartelak_eta_infografia_beteak_daude(self):
        stations = fitxa("animaliak-estazioak")
        station_blocks = stations["hojas"][0]["bloques"]
        station_cards = next(b for b in station_blocks if b["tipo"] == "tarjetas")
        passport = next(b for b in station_blocks if b["tipo"] == "tabla")
        self.assertEqual(len(station_cards["items"]), 4)
        self.assertEqual(len(passport["filas"]), 4)
        self.assertTrue(stations["soluciones"])

        cards = fitxa("animaliak-txartelak")
        deck = next(b for b in blokeak(cards) if b["tipo"] == "txartelak")
        self.assertEqual(len(deck["items"]), 12)
        answer_sheets = [
            b for b in blokeak(cards)
            if b["tipo"] == "ejercicio" and b["modo"] == "preguntas"
        ]
        self.assertEqual(sum(len(b["solucion"]) for b in answer_sheets), 12)

        infographic = fitxa("animaliak-infografia")["hojas"][0]
        self.assertEqual(infographic["orientacion"], "horizontal")
        essentials = next(b for b in infographic["bloques"] if b.get("titulo") == "FUNTSEZKOA")
        self.assertEqual(len(essentials["texto"].splitlines()), 3)
        self.assertTrue(any(b.get("titulo") == "AUTOEBALUAZIOA" for b in infographic["bloques"]))

    def test_irakaslearen_gidak_saioak_eta_checklista_ditu(self):
        guide = fitxa("animaliak-irakaslearen-gida")
        self.assertFalse(guide["hojas"][0]["datos"])
        table = next(b for b in blokeak(guide) if b["tipo"] == "tabla")
        self.assertEqual(len(table["filas"]), 6)
        self.assertTrue(any(b["tipo"] == "berrikusi" for b in blokeak(guide)))

        words = json.loads(
            (ROOT / "contenido" / "irudiak" / "hiztegia-irudiak.json").read_text(
                encoding="utf-8"
            )
        )
        group = next(g for g in words["taldeak"] if g["id"] == "animaliak-hezegunea")
        self.assertEqual(len(group["hitzak"]), 4)


if __name__ == "__main__":
    unittest.main()
