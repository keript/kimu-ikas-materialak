import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build import extraer_minijuegos


def fitxa(ident):
    return json.loads(
        (ROOT / "contenido" / "fitxak" / f"{ident}.json").read_text(encoding="utf-8")
    )


class DeklinabideaPackTest(unittest.TestCase):
    def test_sei_kasuak_eta_mapak_singular_mugatua_azaltzen_dituzte(self):
        theory = fitxa("nork-kasua")
        table = theory["hojas"][0]["bloques"][0]
        self.assertEqual(
            [row[0].split(" · ")[1] for row in table["filas"]],
            ["NOR", "NORK", "NORI", "NON", "NORA", "NONDIK"],
        )
        self.assertEqual(
            [row[1] for row in table["filas"]],
            ["-a", "-ak", "-ari", "-an", "-ra", "-tik"],
        )
        self.assertTrue(all(":" in row[2] for row in table["filas"]))
        mental_map = theory["hojas"][-1]["bloques"][0]
        self.assertEqual(mental_map["tipo"], "mapa")
        self.assertEqual(len(mental_map["ramas"]), 6)
        self.assertTrue(all(branch.get("imagen") for branch in mental_map["ramas"]))

    def test_ariketak_lau_moduak_eta_lotu_sailkatu_minijokoak_dituzte(self):
        theory = fitxa("nork-kasua")
        activities = fitxa("nork-kasua-ariketak")
        self.assertEqual(activities["relacionada"], theory["id"])
        self.assertEqual(activities["curso"], "LH 3")
        self.assertTrue(activities["publicado"])
        self.assertTrue(activities["soluciones"])

        exercises = [
            block
            for sheet in activities["hojas"]
            for block in sheet["bloques"]
            if block["tipo"] == "ejercicio"
        ]
        self.assertEqual(
            {exercise["modo"] for exercise in exercises},
            {"completar", "elegir", "clasificar", "relacionar"},
        )
        minigames = extraer_minijuegos(activities)
        self.assertEqual(len(minigames["lotu"][0]["pares"]), 6)
        self.assertEqual(len(minigames["sailkatu"][0]["items"]), 9)


if __name__ == "__main__":
    unittest.main()
