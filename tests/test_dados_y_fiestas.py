import json
import unittest
from pathlib import Path

from scripts.build import extraer_minijuegos, extraer_preguntas_jolasa


ROOT = Path(__file__).resolve().parents[1]
FITXAK = ROOT / "contenido" / "fitxak"
IDS = (
    "lh1-euskararen-eguna",
    "lh1-gaztainak",
    "lh1-gaztainak-euskara",
    "gaztainak-udazkena",
    "gaztainak-euskara",
    "lh1-gabonak-euskara",
    "lh1-gabonak-mate",
    "lh1-dadoak",
    "dado-taulak",
    "dado-esaldiak-euskara",
    "dado-koloreak-udazkena",
)


def ficha(fitxa_id):
    return json.loads((FITXAK / f"{fitxa_id}.json").read_text(encoding="utf-8"))


def retos(fitxa):
    return [
        bloque["reto"]
        for hoja in fitxa["hojas"]
        for bloque in hoja["bloques"]
        if bloque["tipo"] == "reto"
    ]


class NuevosDadosYFiestasTest(unittest.TestCase):
    def test_fitxek_soluzioak_adaptazioa_eta_joko_pantailakoa_dituzte(self):
        for fitxa_id in IDS:
            with self.subTest(fitxa=fitxa_id):
                fitxa = ficha(fitxa_id)
                self.assertFalse(fitxa["publicado"])
                self.assertTrue(fitxa["soluciones"])
                self.assertTrue(any(hoja.get("egokitua") for hoja in fitxa["hojas"]))
                self.assertTrue(extraer_preguntas_jolasa(fitxa))
                minijokoak = extraer_minijuegos(fitxa)
                self.assertTrue(minijokoak["lotu"])
                self.assertTrue(minijokoak["memoria"])

    def test_dado_esaldiak_eta_koloreak_datu_osoz_renderizatzen_dira(self):
        esaldiak = [
            reto for fitxa_id in IDS for reto in retos(ficha(fitxa_id))
            if reto["tipo"] == "dado-esaldia"
        ]
        self.assertTrue(esaldiak)
        for dadoa in esaldiak:
            self.assertEqual(list(dadoa["dadoak"]), ["Izena", "Aditza", "Non"])
            self.assertTrue(all(len(aurpegiak) == 6 for aurpegiak in dadoa["dadoak"].values()))
            self.assertTrue(dadoa["adibidea"])

        koloreak = next(
            reto for reto in retos(ficha("dado-koloreak-udazkena"))
            if reto["tipo"] == "dado-koloreak"
        )
        self.assertEqual(len(koloreak["galderak"]), 6)
        self.assertEqual(len(koloreak["soluzioa"]), 6)

    def test_matematikako_dadoek_bi_eta_hiru_dado_erabiltzen_dituzte(self):
        for fitxa_id in ("lh1-dadoak", "lh1-gabonak-mate", "dado-taulak", "gaztainak-udazkena"):
            with self.subTest(fitxa=fitxa_id):
                dadoa = next(
                    reto for reto in retos(ficha(fitxa_id))
                    if reto["tipo"] == "dados"
                )
                self.assertTrue(all(len(item["caras"]) in (2, 3) for item in dadoa["items"]))

    def test_egokitutako_ariketek_hiru_item_gehienez_dituzte(self):
        for fitxa_id in IDS:
            with self.subTest(fitxa=fitxa_id):
                fitxa = ficha(fitxa_id)
                if fitxa["curso"] != "LH 1":
                    continue
                for hoja in fitxa["hojas"]:
                    if not hoja.get("egokitua"):
                        continue
                    for bloque in hoja["bloques"]:
                        if bloque["tipo"] == "ejercicio":
                            edukia = bloque.get(
                                "items",
                                bloque.get("frases", bloque.get("palabras", bloque.get("izquierda", []))),
                            )
                            self.assertLessEqual(len(edukia), 3)
                            self.assertTrue(bloque.get("ejemplo"))


if __name__ == "__main__":
    unittest.main()
