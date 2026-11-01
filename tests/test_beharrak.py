import json
import unittest
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from jsonschema import Draft202012Validator, ValidationError

from scripts.build import BEHARRAK, fitxak_beharren_arabera

ROOT = Path(__file__).resolve().parents[1]


class BeharrakTest(unittest.TestCase):
    def test_beharrak_es_opcional_y_acepta_solo_las_categorias_definidas(self):
        esquema = json.loads((ROOT / "contenido" / "esquema-fitxa.json").read_text(encoding="utf-8"))
        validador = Draft202012Validator(esquema)
        ficha = json.loads((ROOT / "contenido" / "fitxak" / "letra-larriak.json").read_text(encoding="utf-8"))

        validador.validate(ficha)
        sin_etiquetas = {clave: valor for clave, valor in ficha.items() if clave != "beharrak"}
        validador.validate(sin_etiquetas)
        with self.assertRaises(ValidationError):
            validador.validate({**ficha, "beharrak": ["necesidad-desconocida"]})

    def test_todas_las_categorias_tienen_fichas_publicadas(self):
        fichas = [
            json.loads(ruta.read_text(encoding="utf-8"))
            for ruta in (ROOT / "contenido" / "fitxak").glob("*.json")
        ]
        publicadas = [ficha for ficha in fichas if ficha["publicado"]]

        agrupadas = fitxak_beharren_arabera(publicadas)

        self.assertEqual([grupo["id"] for grupo in agrupadas], [grupo["id"] for grupo in BEHARRAK])
        self.assertTrue(all(grupo["fitxak"] for grupo in agrupadas))

    def test_pagina_lista_categorias_y_fichas(self):
        plantilla = Environment(
            loader=FileSystemLoader(ROOT / "plantillas"),
            autoescape=True,
        ).get_template("beharrak.html")
        grupos = [
            {
                **grupo,
                "fitxak": [{"id": f"fitxa-{grupo['id']}", "nombre": "Fitxa adibidea", "curso": "LH 3"}],
            }
            for grupo in BEHARRAK
        ]
        html = plantilla.render(
            idioma="eu",
            descripcion_meta="Beharren arabera",
            borrador=False,
            titulo_pestana="Beharren arabera",
            volver={"url": "index.html", "texto": "Hasiera"},
            volver_abajo=None,
            kimu="",
            estatistikak="",
            ver="",
            url_base="/",
            pagina_actual="beharren-arabera.html",
            kofi="",
            beharrak=grupos,
        )

        for grupo in BEHARRAK:
            self.assertIn(grupo["izena"], html)
            self.assertIn(f'fitxa-{grupo["id"]}.html', html)

    def test_portada_destaca_pt_neae_y_no_muestra_cursos_vacios(self):
        plantilla = Environment(
            loader=FileSystemLoader(ROOT / "plantillas"),
            autoescape=True,
        ).get_template("inicio.html")
        html = plantilla.render(
            kimu="",
            ver="",
            estatistikak="",
            arlos_lh1=[],
            arlos_lh3=[],
            n_fitxak=150,
            destacadas=[{"id": "ts-tz-tx", "nombre": "TS, TZ eta TX", "arloa": "Euskara"}],
        )

        self.assertIn("Euskarazko fitxa bisualak", html)
        self.assertIn("NEAE kontuan hartuta", html)
        self.assertIn('href="beharren-arabera.html"', html)
        self.assertIn("PT/HE irakasleentzat, tutoreentzat eta familientzat", html)
        self.assertEqual(html.count('class="maila-card activa"'), 1)
        # Sin «Laster»: la portada no anuncia cursos vacíos; enseña cuántas fichas hay y fichas de muestra.
        self.assertNotIn("Laster:", html)
        self.assertIn("<strong>150 fitxa</strong>", html)
        self.assertIn('src="miniaturak/ts-tz-tx.webp', html)
        self.assertNotIn("class=\"maila-card laster\"", html)


if __name__ == "__main__":
    unittest.main()
