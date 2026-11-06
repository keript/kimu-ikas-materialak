import json
import unittest

from scripts.build import TRAZOS, trazatu_svg
from scripts.generar_letrak import FITXAK, LETRAK, ariketak, teoria


class TrazatuTest(unittest.TestCase):
    def test_hay_trazos_para_vocales_y_h(self):
        for letra in "aeiouh":
            self.assertIn(letra, TRAZOS)
            self.assertIn(letra.upper(), TRAZOS)

    def test_fila_con_flechas_numeradas_y_punteadas(self):
        svg = str(trazatu_svg("a"))
        self.assertIn("marker-end", svg)
        self.assertIn(">1</text>", svg)
        self.assertEqual(svg.count('stroke-dasharray="0.1 3.4"'), 5 * len(TRAZOS["a"]))

    def test_letra_sin_trazos_usa_la_letra_de_imprenta(self):
        self.assertIn("Andika", str(trazatu_svg("m")))


class LetrakTest(unittest.TestCase):
    def test_fichas_de_cada_letra_son_borrador_y_cumplen_el_formato(self):
        for i, letra in enumerate(LETRAK):
            teo, ej = teoria(letra, i), ariketak(letra, i)
            for f in (teo, ej):
                self.assertFalse(f["publicado"])
                self.assertEqual(f["arlo"], "lh1-euskara")
                self.assertTrue(f["id"].startswith("lh1-letra-"))
            self.assertEqual(teo["lugar"], "teoria")
            self.assertEqual(ej["lugar"], "actividades")
            self.assertTrue(ej["soluciones"])
            bloques = [b for h in ej["hojas"] for b in h["bloques"]]
            self.assertEqual(bloques[-1]["tipo"], "berrikusi")
            self.assertEqual(sum(b.get("lerroak", 0) for b in bloques if b["tipo"] == "trazatu"), 3)
            for h in ej["hojas"]:
                self.assertTrue(h["egokitua"])
                for b in h["bloques"]:
                    if b["tipo"] == "ejercicio":
                        self.assertTrue(b.get("ejemplo"))
                        self.assertLessEqual(len(b.get("frases") or b.get("items") or b.get("izquierda")), 3)
            fotos = [t for h in teo["hojas"] for b in h["bloques"] if b["tipo"] == "tarjetas" for t in b["items"] if t.get("foto")]
            self.assertEqual(len(fotos), 4)
            self.assertTrue(all(t["imagen"].startswith(letra) for t in fotos))

    def test_los_json_generados_estan_al_dia(self):
        for i, letra in enumerate(LETRAK):
            for f in (teoria(letra, i), ariketak(letra, i)):
                self.assertEqual(json.loads((FITXAK / f"{f['id']}.json").read_text(encoding="utf-8")), f)


if __name__ == "__main__":
    unittest.main()
