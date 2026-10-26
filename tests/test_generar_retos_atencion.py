import unittest

from scripts.generar_retos import (
    buscar_igual,
    diferencias,
    generar_atencion,
    laberinto,
    mandala,
    serie_colores,
)


class RetosAtencionTest(unittest.TestCase):
    def test_laberinto_generado_tiene_camino_completo_y_reproducible(self):
        import random

        primero = laberinto(random.Random(11), 5, 4)
        segundo = laberinto(random.Random(11), 5, 4)

        self.assertEqual(primero, segundo)
        self.assertEqual(primero["camino"][0], [20, 20])
        self.assertEqual(primero["camino"][-1], [180, 140])
        self.assertTrue(all(
            abs(a[0] - b[0]) + abs(a[1] - b[1]) == 40
            for a, b in zip(primero["camino"], primero["camino"][1:])
        ))
        paredes = {tuple(pared) for pared in primero["paredes"]}
        for a, b in zip(primero["camino"], primero["camino"][1:]):
            if a[0] != b[0]:
                x, y = max(a[0], b[0]) - 20, a[1] - 20
                pared = (x, y, x, y + 40)
            else:
                x, y = a[0] - 20, max(a[1], b[1]) - 20
                pared = (x, y, x + 40, y)
            self.assertNotIn(pared, paredes)

    def test_buscar_igual_tiene_una_unica_respuesta_correcta(self):
        import random

        reto = buscar_igual(random.Random(7))
        objetivo = reto["objetivo"]
        coincidencias = [
            i for i, opcion in enumerate(reto["opciones"])
            if opcion == objetivo
        ]

        self.assertEqual(coincidencias, [reto["correcta"]])

    def test_diferencias_y_series_tienen_soluciones_verificables(self):
        import random

        escenas = diferencias(random.Random(13))
        cambios = [
            campo for campo in ("rayos", "gotas", "frutos", "petalos")
            if escenas["escena_a"][campo] != escenas["escena_b"][campo]
        ]
        serie = serie_colores(random.Random(19))

        self.assertEqual(len(cambios), 4)
        self.assertEqual(serie["huecos"], [6, 7])
        self.assertEqual(serie["solucion"], serie["koloreak"][6:])

    def test_mandalas_y_pack_generan_versiones_por_nivel(self):
        import random

        self.assertIn(mandala(random.Random(5), "udazkena")["petaloak"], [8, 10, 12])
        lh3, lh1 = generar_atencion(2026)

        self.assertEqual(lh3["curso"], "LH 3")
        self.assertEqual(lh1["curso"], "LH 1")
        self.assertEqual(lh1["id"], "lh1-arreta-kontzentrazioa")
        self.assertTrue(all(hoja["egokitua"] for hoja in lh1["hojas"]))
        self.assertTrue(all(hoja["bloques"][0].get("ejemplo") for hoja in lh1["hojas"]))
        retos_lh1 = [hoja["bloques"][0]["reto"] for hoja in lh1["hojas"]]
        self.assertEqual(len(retos_lh1[1]["opciones"]), 3)
        self.assertEqual(len(retos_lh1[2]["diferentes"]), 3)
        self.assertEqual(len(retos_lh1[3]["koloreak"]), 4)
        self.assertEqual(retos_lh1[3]["solucion"], retos_lh1[3]["koloreak"][-1:])
        self.assertEqual(
            {reto["tipo"] for reto in retos_lh1},
            {"laberinto", "buscar_igual", "diferencias", "serie_colores", "mandala"},
        )
        self.assertEqual(generar_atencion(2026), generar_atencion(2026))
        self.assertNotEqual(generar_atencion(2026), generar_atencion(2027))


if __name__ == "__main__":
    unittest.main()
