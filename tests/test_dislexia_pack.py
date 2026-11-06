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
    def test_soinu_teoriak_lau_argazki_errenkada_ditu(self):
        fitxa = kargatu_fitxa("dislexia-soinuak")
        hoja = fitxa["hojas"][0]
        tarjetas = next(b for b in hoja["bloques"] if b["tipo"] == "tarjetas")

        self.assertEqual(hoja["tamano"], "grande")
        self.assertTrue(hoja["egokitua"])
        self.assertEqual(tarjetas["columnas"], 1)
        self.assertEqual(
            [
                (item["imagen"], item["grande"])
                for item in tarjetas["items"]
            ],
            [
                ("sagarra", "sa · ga · rra"),
                ("katua", "ka + tu + a = katua"),
                ("txakurra", "TX"),
                ("itsasoa", "-oa"),
            ],
        )
        self.assertTrue(all(item.get("foto") and item.get("ikonoa") for item in tarjetas["items"]))
        self.assertEqual([b["tipo"] for b in hoja["bloques"]], ["tarjetas", "gogoratu"])
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

        self.assertEqual(len(irakurketak), 10)
        self.assertEqual(len(audioak), 5)
        ohikoak = sum(
            b.get("titulo") == "Ohiko irakurketa"
            or any("Ohiko irakurketa" in p for p in b["parrafos"])
            for b in irakurketak
        )
        errazak = sum(
            b.get("titulo") == "Irakurketa erraza"
            or any("Irakurketa erraza" in p for p in b["parrafos"])
            for b in irakurketak
        )
        self.assertEqual(ohikoak, 6)
        self.assertEqual(errazak, 6)
        self.assertTrue(
            (RAIZ / "contenido" / "ilustraciones" / "dislexia-irakurketa-leihoa.svg").is_file()
        )

    def test_istorioek_argazki_txartelak_dituzte_kartela_izan_ezik(self):
        fitxa = kargatu_fitxa("dislexia-irakurgaiak")
        espero = {
            "1 · Arkatz gorria": ("irakurgai-arkatza", "Anek arkatza aurkitu du."),
            "2 · Landare berria": ("landare-beharrak", "Unaik landare txiki bat zaintzen du."),
            "3 · Eskularrua": ("irakurgai-eskularrua", "Iratik eskularru bat galdu du."),
            "4 · Liburutegian": ("irakurgai-liburutegia", "Anek liburu bat aukeratu du."),
            "6 · Euria": ("irakurgai-aterkia", "Aimarrek aterkia erabili du laguntzeko."),
        }

        for titulo, (imagen, grande) in espero.items():
            with self.subTest(titulo=titulo):
                tarjeta = next(
                    item
                    for bloque in blokeak(fitxa)
                    if bloque["tipo"] == "tarjetas" and bloque["columnas"] == 1
                    for item in bloque["items"]
                    if item["titulo"] == titulo
                )
                self.assertTrue(tarjeta["foto"])
                self.assertEqual(tarjeta["imagen"], imagen)
                self.assertEqual(tarjeta["grande"], grande)

        kartela = next(
            bloque
            for bloque in blokeak(fitxa)
            if bloque.get("tipo") == "apartado" and bloque.get("titulo") == "5 · Kartela"
        )
        self.assertEqual(kartela["imagen"], "memo")

    def test_jarduera_berriek_erantzunak_eta_pantailako_jolasak_dituzte(self):
        for identifikatzailea in (
            "dislexia-irakurmena-ariketak",
            "dislexia-soinuak-ariketak",
            "dislexia-letrak-ariketak",
        ):
            fitxa = kargatu_fitxa(identifikatzailea)
            ariketak = [b for b in blokeak(fitxa) if b["tipo"] == "ejercicio"]
            self.assertTrue(all("solucion" in b for b in ariketak))
            self.assertTrue(all(b.get("ejemplo") for b in ariketak))
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
                        self.assertLessEqual(ariketa.get("lineas", 3), 3)

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
