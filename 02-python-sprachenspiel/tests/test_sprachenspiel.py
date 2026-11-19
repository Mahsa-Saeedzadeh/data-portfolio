"""Unit-Tests für das Sprachenspiel (ausführen mit: python -m unittest -v)."""

import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sprachenspiel import Sprachenspiel, load_words  # noqa: E402


class LoadWordsTests(unittest.TestCase):
    def test_laedt_vorhandene_liste(self):
        words = load_words("de", "leicht")
        self.assertGreater(len(words), 50)
        self.assertTrue(all(w == w.strip() and w for w in words))

    def test_fehlende_datei_wirft_filenotfound(self):
        with self.assertRaises(FileNotFoundError):
            load_words("xx", "leicht")


class SpielLogikTests(unittest.TestCase):
    def setUp(self):
        with patch("sprachenspiel.random.choice", return_value="haus"):
            self.game = Sprachenspiel("de", "leicht")

    def test_startzustand(self):
        self.assertEqual(self.game.display_word(), "_ _ _ _")
        self.assertEqual(self.game.remaining_attempts, 10)
        self.assertFalse(self.game.is_won())
        self.assertFalse(self.game.is_lost())

    def test_richtiger_buchstabe_kostet_keinen_versuch(self):
        self.game.guess_letter("h")
        self.assertEqual(self.game.display_word(), "h _ _ _")
        self.assertEqual(self.game.remaining_attempts, 10)

    def test_falscher_buchstabe_kostet_einen_versuch(self):
        self.game.guess_letter("z")
        self.assertEqual(self.game.remaining_attempts, 9)

    def test_doppelter_buchstabe_wird_ignoriert(self):
        self.game.guess_letter("z")
        self.game.guess_letter("z")
        self.assertEqual(self.game.remaining_attempts, 9)

    def test_gewonnen(self):
        for letter in "haus":
            self.game.guess_letter(letter)
        self.assertTrue(self.game.is_won())

    def test_verloren_bei_schwer(self):
        with patch("sprachenspiel.random.choice", return_value="haus"):
            game = Sprachenspiel("de", "schwer")
        for letter in "bcdfg":
            game.guess_letter(letter)
        self.assertTrue(game.is_lost())


if __name__ == "__main__":
    unittest.main()
