import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FITXAK = ROOT / "contenido" / "fitxak"


def fitxa(ident):
    return json.loads((FITXAK / f"{ident}.json").read_text(encoding="utf-8"))


class GelaAntolatuPackTest(unittest.TestCase):
    def test_packak_agenda_lehenengo_gero_arauak_eta_emozioak_ditu(self):
        section = json.loads(
            (ROOT / "contenido" / "secciones" / "gela-antolatu.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(section["tipo"], "pack")
        self.assertEqual(section["arlo"], "euskara")
        fitxa_ids = {
            path.stem
            for path in FITXAK.glob("*.json")
            if json.loads(path.read_text(encoding="utf-8"))["seccion"]
            == "gela-antolatu"
        }
        self.assertEqual(
            fitxa_ids,
            {
                "gela-antolatu-agenda",
                "gela-antolatu-lehenengo-gero",
                "gela-antolatu-arauak-infografia",
                "gela-antolatu-emozioak",
            },
        )

    def test_agendak_lau_leku_eta_zortzi_mozteko_txartel_ditu(self):
        agenda = fitxa("gela-antolatu-agenda")
        self.assertEqual(
            sum(
                block["tipo"] == "dibujo"
                for block in agenda["hojas"][0]["bloques"]
            ),
            4,
        )
        cards = agenda["hojas"][1]["bloques"][0]["items"]
        self.assertEqual(len(cards), 8)
        self.assertTrue(all(card.get("imagen") for card in cards))
        self.assertIn("✂", agenda["hojas"][1]["subtitulo"])

    def test_lehenengo_gero_txantiloiak_adibidea_eta_idazteko_espazioa_ditu(self):
        template = fitxa("gela-antolatu-lehenengo-gero")["hojas"][0]
        self.assertTrue(any(block["tipo"] == "gogoratu" for block in template["bloques"]))
        self.assertEqual(
            sum(block["tipo"] == "dibujo" for block in template["bloques"]), 2
        )

    def test_arauak_horizontalean_sei_irudi_ditu(self):
        poster = fitxa("gela-antolatu-arauak-infografia")["hojas"][0]
        self.assertEqual(poster["orientacion"], "horizontal")
        cards = poster["bloques"][0]["items"]
        self.assertEqual(len(cards), 6)
        self.assertTrue(all(card.get("imagen") for card in cards))

    def test_emozio_txartelek_bost_argazki_eskatzen_ditu(self):
        emotions = fitxa("gela-antolatu-emozioak")
        cards = emotions["hojas"][1]["bloques"][0]["items"]
        self.assertEqual(
            {card["imagen"] for card in cards},
            {
                "emozioa-pozik",
                "emozioa-triste",
                "emozioa-haserre",
                "emozioa-beldurra",
                "emozioa-lasai",
            },
        )
        requests = json.loads(
            (ROOT / "contenido" / "irudiak" / "eskaerak.json").read_text(
                encoding="utf-8"
            )
        )["irudiak"]
        groups = json.loads(
            (ROOT / "contenido" / "irudiak" / "hiztegia-irudiak.json").read_text(
                encoding="utf-8"
            )
        )["taldeak"]
        self.assertEqual(
            {group["id"] for group in groups if group["id"].startswith("emozioak-")},
            {request["id"] for request in requests if request["id"].startswith("emozioak-")},
        )
        self.assertTrue(
            all("2 by 2 grid" in request["prompt"] for request in requests if request["id"].startswith("emozioak-"))
        )


if __name__ == "__main__":
    unittest.main()
