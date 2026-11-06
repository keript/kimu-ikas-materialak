import json
import unittest
from pathlib import Path

from scripts.build import sortu_bingo_kartoiak


ROOT = Path(__file__).resolve().parents[1]


class BingoSortzaileaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bingo = json.loads((ROOT / "contenido" / "bingoa-euskararen-eguna.json").read_text(encoding="utf-8"))

    def test_same_code_always_returns_same_card(self):
        lehenengoa = sortu_bingo_kartoiak(self.bingo)
        bigarrena = sortu_bingo_kartoiak(self.bingo)
        self.assertEqual(lehenengoa["4x4"]["EE-4x4-0007"], bigarrena["4x4"]["EE-4x4-0007"])
        self.assertEqual(lehenengoa["3x3"]["EE-3x3-0007"], bigarrena["3x3"]["EE-3x3-0007"])

    def test_missing_code_is_derived_from_the_topic_id(self):
        bingo = {key: value for key, value in self.bingo.items() if key != "kodea"}
        lehenengoa = sortu_bingo_kartoiak(bingo)
        bigarrena = sortu_bingo_kartoiak({key: value for key, value in bingo.items() if key != "kodea"})
        self.assertEqual(bingo["kodea"], "EE")
        self.assertEqual(lehenengoa["4x4"]["EE-4x4-0007"], bigarrena["4x4"]["EE-4x4-0007"])

    def test_cards_are_unique_and_3x3_uses_easy_words(self):
        kartoiak = sortu_bingo_kartoiak(self.bingo)
        hitz_errazak = set(self.bingo["erraza"])
        hitz_guztiak = {item["hitza"] for item in self.bingo["hitzak"]}
        for tamaina, espero_kop, hitz_iturri in (
            ("3x3", 9, hitz_errazak),
            ("4x4", 16, hitz_guztiak),
        ):
            taulak = list(kartoiak[tamaina].values())
            self.assertEqual(len(taulak), 40)
            self.assertEqual(len({tuple(taula) for taula in taulak}), 40)
            self.assertTrue(all(len(taula) == espero_kop and set(taula) <= hitz_iturri for taula in taulak))

    def test_photo_bingo_codes_identify_each_card_mode(self):
        bingo = json.loads((ROOT / "contenido" / "bingoa-olentzero-lh1.json").read_text(encoding="utf-8"))
        kartoiak = sortu_bingo_kartoiak(bingo)
        for tamaina, espero_kop in (("3x3", 9), ("4x4", 16)):
            for modua in ("A", "B", "H"):
                with self.subTest(tamaina=tamaina, modua=modua):
                    kodeak = [code for code in kartoiak[tamaina] if f"-{modua}-" in code]
                    self.assertEqual(len(kodeak), 40)
                    self.assertIn(f"OL1-{tamaina}-{modua}-0007", kodeak)
                    self.assertTrue(all(len(kartoiak[tamaina][code]) == espero_kop for code in kodeak))
            self.assertEqual(
                kartoiak[tamaina]["OL1-" + tamaina + "-A-0007"],
                kartoiak[tamaina]["OL1-" + tamaina + "-B-0007"],
            )
            self.assertEqual(
                kartoiak[tamaina]["OL1-" + tamaina + "-A-0007"],
                kartoiak[tamaina]["OL1-" + tamaina + "-H-0007"],
            )


if __name__ == "__main__":
    unittest.main()
