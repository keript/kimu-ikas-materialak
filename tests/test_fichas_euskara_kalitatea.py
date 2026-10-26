import json
import unittest
from pathlib import Path

from scripts.kalitatea import puntuar


ROOT = Path(__file__).resolve().parents[1]
IDS = (
    "ibaiaren-eguna-galderak",
    "euskararen-eguna-galderak",
    "zazpi-lurralde-ariketak",
    "nire-errezeta",
    "zazpi-lurralde",
    "galdera-harridura-ikurrak-ariketak",
    "aneren-larunbata-galderak",
    "erleak-galderak",
    "jonen-irteera-galderak",
    "galdera-harridura-ikurrak",
    "letra-larriak",
    "letra-larriak-ariketak",
    "nork-kasua",
    "s-z-x",
    "silabak",
    "ts-tz-tx",
    "nork-kasua-ariketak",
    "silabak-ariketak",
    "s-z-x-ariketak",
    "ts-tz-tx-ariketak",
)


class FichasEuskaraKalitateaTest(unittest.TestCase):
    def test_todas_las_fichas_objetivo_sacan_al_menos_nueve(self):
        for ident in IDS:
            with self.subTest(ficha=ident):
                ruta = ROOT / "contenido" / "fitxak" / f"{ident}.json"
                ficha = json.loads(ruta.read_text(encoding="utf-8"))
                nota, faltas = puntuar(ficha)
                self.assertGreaterEqual(nota, 9, "; ".join(faltas))


if __name__ == "__main__":
    unittest.main()
