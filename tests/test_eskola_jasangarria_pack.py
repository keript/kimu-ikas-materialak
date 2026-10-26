import json
import unittest
from pathlib import Path

from scripts.build import extraer_minijuegos, extraer_preguntas_jolasa


ROOT = Path(__file__).resolve().parents[1]
FITXAK = ROOT / "contenido" / "fitxak"
IDS = [
    "eskola-jasangarria-teoria",
    "eskola-jasangarria-ariketak",
    "eskola-jasangarria-estazioak",
    "eskola-jasangarria-txartelak",
    "eskola-jasangarria-infografia",
    "eskola-jasangarria-irakaslearen-gida",
]


def fitxa(ident):
    return json.loads((FITXAK / f"{ident}.json").read_text(encoding="utf-8"))


class EskolaJasangarriaPackTest(unittest.TestCase):
    def test_packa_eta_sei_fitxak_zirriborroak_dira(self):
        section = json.loads(
            (ROOT / "contenido" / "secciones" / "eskola-jasangarria.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(section["tipo"], "pack")
        self.assertEqual(section["arlo"], "ingurunea")

        fichas = [fitxa(ident) for ident in IDS]
        self.assertTrue(all(f["seccion"] == section["id"] for f in fichas))
        self.assertTrue(all(f["curso"] == "LH 3" and f["publicado"] is False for f in fichas))

        theory, activities = fitxa(IDS[0]), fitxa(IDS[1])
        self.assertEqual(theory["relacionada"], activities["id"])
        self.assertEqual(activities["relacionada"], theory["id"])
        self.assertEqual(theory["hojas"][-1]["bloques"][0]["tipo"], "mapa")

    def test_ariketak_lau_jolasak_eta_bost_mota_sortzen_ditu(self):
        activities = fitxa("eskola-jasangarria-ariketak")
        bloques = [
            b
            for hoja in activities["hojas"]
            for b in hoja["bloques"]
            if b["tipo"] == "ejercicio"
        ]
        self.assertTrue(
            {"clasificar", "relacionar", "elegir", "verdadero_falso", "completar"}
            <= {b["modo"] for b in bloques}
        )

        minijuegos = extraer_minijuegos(activities)
        self.assertTrue(minijuegos["lotu"])
        self.assertTrue(minijuegos["sailkatu"])
        self.assertTrue(minijuegos["memoria"])
        self.assertTrue(extraer_preguntas_jolasa(activities))

    def test_estazioak_txartelak_eta_infografia_osorik_daude(self):
        stations = fitxa("eskola-jasangarria-estazioak")
        station_cards = stations["hojas"][0]["bloques"][1]["items"]
        passport = stations["hojas"][0]["bloques"][2]
        self.assertEqual(len(station_cards), 4)
        self.assertEqual(len(passport["filas"]), 4)
        self.assertTrue(stations["soluciones"])

        cards = fitxa("eskola-jasangarria-txartelak")["hojas"][0]["bloques"][0]["items"]
        self.assertEqual(len(cards), 12)

        infographic = fitxa("eskola-jasangarria-infografia")["hojas"][0]
        self.assertEqual(infographic["orientacion"], "horizontal")
        self.assertEqual(len(infographic["bloques"][0]["items"]), 6)
        self.assertEqual(
            len(next(b for b in infographic["bloques"] if b.get("titulo") == "FUNTSEZKOA")["texto"].splitlines()),
            3,
        )
        self.assertTrue(
            any(b.get("titulo") == "GALDE ZURE BURUARI" for b in infographic["bloques"])
        )


if __name__ == "__main__":
    unittest.main()
