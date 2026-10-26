import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FITXAK = ROOT / "contenido" / "fitxak"
sys.path.insert(0, str(ROOT / "scripts"))
import build  # noqa: E402


def fitxa(ident):
    return json.loads((FITXAK / f"{ident}.json").read_text(encoding="utf-8"))


class HistoriaurreaPackTest(unittest.TestCase):
    def test_packak_borradoreak_eta_teoria_ariketak_lotuta_ditu(self):
        section = json.loads(
            (ROOT / "contenido" / "secciones" / "historiaurrea.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(section["tipo"], "pack")
        self.assertFalse(section["publicado"])
        self.assertEqual(section["arlo"], "ingurunea")

        ids = [
            "historiaurrea-teoria",
            "historiaurrea-ariketak",
            "historiaurrea-estazioak",
            "historiaurrea-txartelak",
            "historiaurrea-infografia",
            "historiaurrea-irakaslearen-gida",
        ]
        for ident in ids:
            ficha = fitxa(ident)
            self.assertFalse(ficha["publicado"])
            self.assertEqual(ficha["curso"], "LH 3")

        theory = fitxa("historiaurrea-teoria")
        activities = fitxa("historiaurrea-ariketak")
        self.assertEqual(theory["relacionada"], activities["id"])
        self.assertEqual(activities["relacionada"], theory["id"])
        self.assertEqual(theory["hojas"][-1]["orientacion"], "horizontal")
        self.assertEqual(theory["hojas"][-1]["bloques"][0]["tipo"], "mapa")

    def test_jolasak_irakurketa_eta_irteerako_gidoia_daude(self):
        activities = fitxa("historiaurrea-ariketak")
        blocks = [
            block
            for sheet in activities["hojas"]
            for block in sheet["bloques"]
        ]
        modes = {block.get("modo") for block in blocks if block["tipo"] == "ejercicio"}
        self.assertTrue({"relacionar", "clasificar", "elegir", "verdadero_falso"} <= modes)
        self.assertTrue(
            all(
                block.get("solucion")
                for block in blocks
                if block["tipo"] == "ejercicio"
            )
        )
        minigames = build.extraer_minijuegos(activities)
        self.assertTrue(minigames["lotu"])
        self.assertTrue(minigames["sailkatu"])
        self.assertTrue(build.extraer_preguntas_jolasa(activities))

        cards = fitxa("historiaurrea-txartelak")
        self.assertTrue(build.extraer_minijuegos(cards)["memoria"])
        reading = next(block for block in blocks if block["tipo"] == "lectura")
        self.assertEqual(len(reading["parrafos"]), 5)
        self.assertTrue(
            any(
                "atapuerca" in sheet["titulo"].lower()
                for sheet in activities["hojas"]
            )
        )

    def test_estazioak_hamabi_txartel_infografia_eta_gida_osorik_daude(self):
        stations = fitxa("historiaurrea-estazioak")
        station_cards = stations["hojas"][0]["bloques"][1]["items"]
        passport = stations["hojas"][0]["bloques"][2]
        self.assertEqual(len(station_cards), 4)
        self.assertEqual(len(passport["filas"]), 4)

        cards = fitxa("historiaurrea-txartelak")
        self.assertEqual(len(cards["hojas"][0]["bloques"][0]["items"]), 12)
        self.assertEqual(
            sum(
                len(sheet["bloques"][0]["solucion"])
                for sheet in cards["hojas"][1:3]
            ),
            12,
        )

        infographic = fitxa("historiaurrea-infografia")["hojas"][0]
        self.assertEqual(infographic["orientacion"], "horizontal")
        self.assertEqual(len(infographic["bloques"][0]["items"]), 5)
        key_ideas = next(
            block["texto"]
            for block in infographic["bloques"]
            if block.get("titulo") == "FUNTSEZKOA"
        )
        self.assertEqual(len(key_ideas.splitlines()), 3)
        self.assertTrue(
            any(
                block.get("titulo") == "GALDE ZURE BURUARI"
                for block in infographic["bloques"]
            )
        )

        guide = fitxa("historiaurrea-irakaslearen-gida")
        schedule = next(
            block
            for block in guide["hojas"][0]["bloques"]
            if block["tipo"] == "tabla"
        )
        self.assertEqual(len(schedule["filas"]), 6)

    def test_historiaurrea_irudien_taldea_eskatuta_dago(self):
        requests = json.loads(
            (ROOT / "contenido" / "irudiak" / "hiztegia-irudiak.json").read_text(
                encoding="utf-8"
            )
        )
        group = next(
            group for group in requests["taldeak"] if group["id"] == "historiaurrea"
        )
        self.assertEqual(
            set(group["hitzak"]),
            {"kobazuloa", "harrizko-tresna", "sua", "labar-pintura"},
        )


if __name__ == "__main__":
    unittest.main()
