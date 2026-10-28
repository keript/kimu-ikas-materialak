import json
import unittest
from pathlib import Path

from scripts.build import extraer_minijuegos, extraer_preguntas_jolasa


ROOT = Path(__file__).resolve().parents[1]
FITXAK = ROOT / "contenido" / "fitxak"
SECCIONES = ROOT / "contenido" / "secciones"


def leer_json(ruta):
    return json.loads(ruta.read_text(encoding="utf-8"))


class LH1MatematikaTest(unittest.TestCase):
    def test_hiru_packek_teoria_eta_ariketak_zirriborroan_lotzen_dituzte(self):
        for hiruhilekoa in range(1, 4):
            with self.subTest(hiruhilekoa=hiruhilekoa):
                sekzio_id = f"lh1-mate-{hiruhilekoa}-hiruhilekoa"
                sekzioa = leer_json(SECCIONES / f"{sekzio_id}.json")
                teoria = leer_json(FITXAK / f"lh1-mate-{hiruhilekoa}-teoria.json")
                ariketak = leer_json(FITXAK / f"lh1-mate-{hiruhilekoa}-ariketak.json")

                self.assertEqual(sekzioa["tipo"], "pack")
                self.assertEqual(sekzioa["arlo"], "lh1-matematika")
                self.assertEqual(teoria["seccion"], sekzio_id)
                self.assertEqual(ariketak["seccion"], sekzio_id)
                self.assertEqual(teoria["relacionada"], ariketak["id"])
                self.assertEqual(ariketak["relacionada"], teoria["id"])
                for ficha in (teoria, ariketak):
                    self.assertEqual(ficha["arlo"], "lh1-matematika")
                    self.assertEqual(ficha["curso"], "LH 1")
                    self.assertFalse(ficha["publicado"])
                mapa = teoria["hojas"][-1]["bloques"][0]
                self.assertEqual(mapa["tipo"], "mapa")
                self.assertTrue(all(rama.get("imagen") for rama in mapa["ramas"]))

    def test_gai_bakoitzak_lau_jolasak_eta_ariketa_moldatuak_ditu(self):
        for hiruhilekoa in range(1, 4):
            with self.subTest(hiruhilekoa=hiruhilekoa):
                teoria = leer_json(FITXAK / f"lh1-mate-{hiruhilekoa}-teoria.json")
                ariketak = leer_json(FITXAK / f"lh1-mate-{hiruhilekoa}-ariketak.json")
                fitxa = {**ariketak, "hojas": teoria["hojas"] + ariketak["hojas"]}

                minijokoak = extraer_minijuegos(fitxa)
                galderak = extraer_preguntas_jolasa(fitxa)
                self.assertTrue(minijokoak["lotu"])
                self.assertTrue(minijokoak["sailkatu"])
                self.assertTrue(minijokoak["memoria"])
                self.assertTrue(galderak)

                for hoja in ariketak["hojas"]:
                    self.assertTrue(hoja["egokitua"])
                    for bloque in hoja["bloques"]:
                        if bloque["tipo"] != "ejercicio":
                            continue
                        self.assertTrue(bloque.get("ejemplo"))
                        cantidad = bloque.get("items", bloque.get("frases", bloque.get("palabras", bloque.get("izquierda", []))))
                        self.assertLessEqual(len(cantidad), 3)

    def test_hiruhileko_bakoitzak_eskatutako_gaiak_biltzen_ditu(self):
        gaiak = {
            1: ["0tik 20ra", "0tik 50era", "sukaldean", "hirian", "goian", "behean", "aurrean", "atzean",
                "artean", "hurbil", "urrun", "zirkulua", "karratua", "triangelua", "laukizuzena", "patroia"],
            2: ["0–99", "hamarrekoak", "batekoak", "baratzean", "ringed-planet", "jostailu-blokeekin",
                "txanpon", "billete", "astelehena", "otsaila", "udaberria", "4:30", "zilindroa", "konoa"],
            3: ["100 arte", "kanpalekuan", "baserriko", "basoko", "eskua", "oina", "metroa",
                "kiloa", "litroa", "astunagoa", "arinagoa", "gutxi gorabehera", "piktograma", "barra-grafikoa"],
        }
        for hiruhilekoa, hitzak in gaiak.items():
            with self.subTest(hiruhilekoa=hiruhilekoa):
                teoria = leer_json(FITXAK / f"lh1-mate-{hiruhilekoa}-teoria.json")
                ariketak = leer_json(FITXAK / f"lh1-mate-{hiruhilekoa}-ariketak.json")
                edukia = json.dumps([teoria, ariketak], ensure_ascii=False).casefold()
                for hitza in hitzak:
                    with self.subTest(hitza=hitza):
                        self.assertIn(hitza.casefold(), edukia)

    def test_argazki_eskaera_berrien_irudiak_fitxetan_erabiltzen_dira(self):
        fitxa_edukia = " ".join(
            ruta.read_text(encoding="utf-8")
            for ruta in FITXAK.glob("lh1-mate-*.json")
        )
        hiztegia = leer_json(ROOT / "contenido" / "irudiak" / "hiztegia-irudiak.json")
        talde_ids = {
            "lh1-posizioak",
            "lh1-posizioak-2",
            "lh1-irudi-lauak",
            "lh1-dirua",
            "lh1-gorputz-geometrikoak",
            "lh1-luzera",
            "lh1-pisua-edukiera",
        }
        taldeak = [t for t in hiztegia["taldeak"] if t["id"] in talde_ids]
        self.assertEqual({t["id"] for t in taldeak}, talde_ids)
        for taldea in taldeak:
            for irudi_id in taldea["hitzak"]:
                with self.subTest(irudi=irudi_id):
                    self.assertIn(irudi_id, fitxa_edukia)


if __name__ == "__main__":
    unittest.main()
