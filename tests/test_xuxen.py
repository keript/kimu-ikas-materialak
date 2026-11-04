import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts import xuxen


class XuxenTest(unittest.TestCase):
    def escribir_json(self, directorio, nombre, datos):
        ruta = Path(directorio, nombre)
        ruta.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
        return ruta

    def test_extrae_textos_y_omite_castellano_metadatos_y_urls(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = self.escribir_json(
                directorio,
                "ficha.json",
                {
                    "id": "test-eu",
                    "arlo": "euskara",
                    "nombre": "Ane, idatzi 42 hitz.",
                    "url": "https://example.test/akats",
                    "arlo2": "www.example.test",
                    "hojas": [{"bloques": [{"tipo": "texto", "texto": "Kimu dator."}]}],
                },
            )
            texto = " ".join(xuxen.extraer_textos(ruta))

            self.assertIn("Ane, idatzi", texto)
            self.assertNotIn("42", xuxen.tokens(texto))
            self.assertIn("Kimu dator.", texto)
            self.assertNotIn("test-eu", texto)
            self.assertNotIn("https://", texto)
            self.assertNotIn("www.", texto)
            self.assertNotIn("school", xuxen.tokens(":school: LH 3rako NEAE"))

            ruta_es = self.escribir_json(
                directorio, "ficha-es.json", {"id": "ficha-es", "arlo": "gaztelera", "nombre": "Texto"}
            )
            self.assertEqual(xuxen.extraer_textos(ruta_es), [])

    def test_ignora_siglas_y_lista_blanca(self):
        self.assertTrue(xuxen.ignorar_palabra("NEAE", set()))
        self.assertTrue(xuxen.ignorar_palabra("Kimu", {"kimu"}))
        self.assertFalse(xuxen.ignorar_palabra("zuhaitza", set()))
        self.assertNotIn("NEAErako", xuxen.tokens("LH 3rako NEAErako"))
        self.assertIn("Haizearen", xuxen.tokens("{H}aizearen orrazia"))

    def test_hunspell_hallazgo_conserva_archivo_y_frase(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = self.escribir_json(
                directorio, "ficha.json", {"arlo": "euskara", "texto": "Kaixo. Ezezagun hitza."}
            )
            resultado = SimpleNamespace(returncode=0, stdout="ezezagun\nAne\n", stderr="")
            with patch.object(xuxen.subprocess, "run", return_value=resultado) as run:
                hallazgos = xuxen.revisar_hunspell([ruta], {"ane"})

        self.assertEqual(len(hallazgos), 1)
        self.assertEqual(hallazgos[0]["palabra"], "ezezagun")
        self.assertEqual(hallazgos[0]["frase"], "Ezezagun hitza.")
        self.assertEqual(run.call_args.args[0], ["hunspell", "-d", "eu_ES", "-l"])

    def test_compara_palabras_desconocidas_con_la_version_base(self):
        hallazgos = [
            {"archivo": "contenido/fitxak/a.json", "palabra": "lehena"},
            {"archivo": "contenido/fitxak/a.json", "palabra": "berria"},
        ]
        base = {"contenido/fitxak/a.json": {"lehena"}}

        self.assertEqual(xuxen.filtrar_palabras_nuevas(hallazgos, base), [hallazgos[1]])

    def test_api_respeta_limite_de_caracteres(self):
        partes = xuxen.dividir_texto("a" * 5001)

        self.assertEqual([len(parte) for parte in partes], [5000, 1])
        self.assertTrue(all(len(parte) <= xuxen.MAX_CARACTERES_API for parte in partes))

    def test_clasifica_solo_ortografia_como_bloqueante(self):
        self.assertTrue(xuxen.es_correccion_ortografica("ORTOGRAFIA"))
        self.assertFalse(xuxen.es_correccion_ortografica("GUTC"))


if __name__ == "__main__":
    unittest.main()
