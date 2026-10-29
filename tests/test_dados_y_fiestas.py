import json
import re
import unittest
from pathlib import Path

from scripts.build import extraer_minijuegos, extraer_preguntas_jolasa
from scripts.kalitatea import puntuar


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
ADAPTADAS = ("dadoak-agnh", "dadoak-dislexia", "dadoak-tea")


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

    def test_dadoak_neae_bertsioek_eragiketa_berak_eta_zuzenak_dituzte(self):
        jatorrizkoak = sorted(
            (tuple(r["caras"]), r["op"], r["resultado"])
            for r in retos(ficha("dadoak"))
            if r["tipo"] == "dados"
            for item in r["items"]
            for r in [item]
        )

        def eragiketa(testua, emaitza):
            zenbakiak = tuple(map(int, re.findall(r":keycap-(\d):", testua)))
            eragilea = "+" if "+" in testua else "−"
            return zenbakiak, eragilea, int(emaitza)

        for fitxa_id in ADAPTADAS:
            with self.subTest(fitxa=fitxa_id):
                fitxa = ficha(fitxa_id)
                self.assertEqual(fitxa["arlo"], "matematika")
                self.assertEqual(fitxa["seccion"], ficha("dadoak")["seccion"])
                self.assertEqual(fitxa["curso"], "LH 3")
                self.assertFalse(fitxa["publicado"])
                self.assertEqual(len(fitxa["hojas"]), 12)
                eragiketak = []
                for hoja in fitxa["hojas"]:
                    for bloque in hoja["bloques"]:
                        if bloque["tipo"] != "ejercicio":
                            continue
                        if fitxa_id == "dadoak-tea":
                            adibidea = bloque["ejemplo"].split(" = ")
                            eragiketak.append(eragiketa(adibidea[0], adibidea[1]))
                        eragiketak.extend(
                            eragiketa(frase, emaitza)
                            for frase, emaitza in zip(bloque["frases"], bloque["solucion"])
                        )
                self.assertEqual(sorted(eragiketak), jatorrizkoak)

    def test_dadoak_egokituen_orri_bakoitzak_betetzen_du_diseinua(self):
        agnh = ficha("dadoak-agnh")
        for hoja in agnh["hojas"]:
            with self.subTest(profila="agnh", orria=hoja["titulo"]):
                ariketa = next(b for b in hoja["bloques"] if b["tipo"] == "ejercicio")
                self.assertLessEqual(len(ariketa["frases"]), 3)
                self.assertTrue(all("[ ] Eginda ✓" in f for f in ariketa["frases"]))
                self.assertIn("Zenbatu. Batu. Idatzi.", ariketa["enunciado"])
                self.assertTrue(any("5 minutu" in b.get("texto", "") for b in hoja["bloques"]))
                self.assertTrue(hoja["egokitua"])

        dislexia = ficha("dadoak-dislexia")
        for hoja in dislexia["hojas"]:
            with self.subTest(profila="dislexia", orria=hoja["titulo"]):
                ariketa = next(b for b in hoja["bloques"] if b["tipo"] == "ejercicio")
                self.assertLessEqual(len(ariketa["frases"]), 4)
                self.assertLessEqual(len(hoja["subtitulo"].split()), 5)
                self.assertFalse(any(ord(c) > 0x1F000 for c in hoja["titulo"]))
                self.assertTrue(hoja["egokitua"])
                self.assertEqual(hoja["tamano"], "grande")

        tea = ficha("dadoak-tea")
        eredua = tea["hojas"][0]["bloques"]
        for hoja in tea["hojas"]:
            with self.subTest(profila="tea", orria=hoja["titulo"]):
                self.assertEqual([b["tipo"] for b in hoja["bloques"]], ["nota", "ejercicio", "nota"])
                self.assertEqual(hoja["bloques"][0]["texto"], "HASI")
                self.assertEqual(hoja["bloques"][-1]["texto"], "BUKATU")
                ariketa = hoja["bloques"][1]
                self.assertTrue(ariketa["ejemplo"])
                self.assertEqual(ariketa["enunciado"], eredua[1]["enunciado"])
                self.assertEqual(hoja["subtitulo"], tea["hojas"][0]["subtitulo"])
                self.assertTrue(hoja["egokitua"])

    def test_dadoak_neae_fitxek_kalitate_minimoa_lortzen_dute(self):
        for fitxa_id in ADAPTADAS:
            with self.subTest(fitxa=fitxa_id):
                nota, falta = puntuar(ficha(fitxa_id))
                self.assertGreaterEqual(nota, 9.8)
                self.assertFalse(falta)

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
