import datetime as dt
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jinja2 import Environment, FileSystemLoader
from jsonschema import Draft202012Validator

from scripts import build, oroigarriak


ROOT = Path(__file__).resolve().parents[1]


class GelanProbatuaTest(unittest.TestCase):
    def test_fecha_valida_en_esquema_y_build(self):
        esquema = json.loads((ROOT / "contenido/esquema-fitxa.json").read_text(encoding="utf-8"))
        validador = Draft202012Validator(esquema)
        ficha = json.loads((ROOT / "contenido/fitxak/letra-larriak.json").read_text(encoding="utf-8"))

        for fecha in ("2026-01", "2026-10", "2026-12"):
            self.assertTrue(validador.is_valid({**ficha, "gelan_probatua": fecha}))
        for fecha in ("2026-00", "2026-13", "2026-1", "2026-10-01"):
            self.assertFalse(validador.is_valid({**ficha, "gelan_probatua": fecha}))
        self.assertTrue(validador.is_valid(ficha))

        build.errores.clear()
        build.validar_fitxa(
            ROOT / "contenido/fitxak/letra-larriak.json",
            {**ficha, "gelan_probatua": "2026-13"},
            {ficha["arlo"]},
            {ficha["seccion"]},
            validador,
        )
        self.assertTrue(any("gelan_probatua" in mensaje for mensaje in build.errores))
        build.errores.clear()

    def test_indice_incluye_mes_de_prueba(self):
        recurso = {
            "id": "proba",
            "arlo": "euskara",
            "nombre": "Proba",
            "curso": "LH 3",
            "gelan_probatua": "2026-10",
        }

        indice = build.crear_indice_busqueda([recurso], {"euskara": {"nombre": "Euskara"}})

        self.assertEqual(indice[0]["gelan_probatua"], "2026-10")

    def test_ficha_y_mosaico_muestran_el_sello(self):
        env = Environment(loader=FileSystemLoader(ROOT / "plantillas"))
        env.filters.update(
            marcado=build.formato_marcado,
            cos_=lambda x: round(math.cos(x), 3),
            sin_=lambda x: round(math.sin(x), 3),
        )
        ficha = {
            "id": "proba",
            "curso": "LH 3",
            "nombre": "Proba",
            "titulo_resalte": "",
            "resumen": "Test summary",
            "tipo_material": "Ariketa-fitxa",
            "hojas_render": [],
            "gelan_probatua": "2026-10",
        }
        contexto_base = {
            "idioma": "eu",
            "volver": {"url": "index.html", "texto": "Hasiera"},
            "volver_abajo": None,
            "descripcion_meta": "Test description",
            "titulo_pestana": "Proba",
            "ver": "test",
            "kimu": "",
        }

        html_ficha = env.get_template("fitxa.html").render(
            **contexto_base,
            f=ficha,
            arlo={"nombre": "Euskara"},
            seccion={"nombre": "Proba"},
            hojas_alumno=1,
            hojas_docente=False,
            ui={"orri": "orri", "imprimir": "Inprimatu", "hojas_aria": "Orriak"},
            ui_jolasa={"button": "Jolastu"},
        )
        html_mosaico = env.get_template("mosaico.html").render(
            **contexto_base,
            titulo="Proba",
            titulo_resalte="",
            antetitulo="",
            intro="",
            etiqueta_grupo="section",
            etiqueta_accesible="Fitxak",
            tarjetas=[{
                "url": "proba.html",
                "icono": "✓",
                "nombre": "Proba",
                "texto": "Fitxa",
                "boton": "Ikusi",
                "gelan_probatua": "2026-10",
            }],
        )

        for html in (html_ficha, html_mosaico):
            self.assertIn("Gelan probatua ✓", html)
            self.assertIn('datetime="2026-10"', html)

    def test_comando_probatua_escribe_el_mes_actual_sin_publicar(self):
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            fichas = []
            for ficha_id in ("proba-1", "proba-2"):
                archivo = raiz / f"{ficha_id}.json"
                archivo.write_text(json.dumps({"id": ficha_id, "publicado": False}), encoding="utf-8")
                fichas.append((ficha_id, ficha_id, "LH 3", archivo))

            ahora = dt.datetime(2026, 10, 29, tzinfo=dt.timezone.utc)
            with (
                patch.object(oroigarriak, "RAIZ", raiz),
                patch.object(oroigarriak, "AHORA", ahora),
                patch.object(oroigarriak, "borradores", return_value=fichas),
                patch.dict("os.environ", {"COMENTARIO": "probatua proba-1, proba-2", "N": "142"}),
            ):
                oroigarriak.erantzun()

            for _, _, _, archivo in fichas:
                ficha = json.loads(archivo.read_text(encoding="utf-8"))
                self.assertEqual(ficha["gelan_probatua"], "2026-10")
                self.assertFalse(ficha["publicado"])
            self.assertIn("Gelan probatua 2026-10", (raiz / ".oniritzia.txt").read_text(encoding="utf-8"))

    def test_comando_probatua_sin_ids_indica_el_formato_esperado(self):
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            with (
                patch.object(oroigarriak, "RAIZ", raiz),
                patch.object(oroigarriak, "borradores", return_value=[]),
                patch.dict("os.environ", {"COMENTARIO": "probatua", "N": "142"}),
            ):
                oroigarriak.erantzun()

            mensaje = (raiz / ".oniritzia.txt").read_text(encoding="utf-8")
            self.assertIn("probatua id1, id2", mensaje)


if __name__ == "__main__":
    unittest.main()
