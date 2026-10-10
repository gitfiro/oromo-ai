import unittest

from training.tools.prepare_general_control import freeze_rows


class GeneralControlFreezeTest(unittest.TestCase):
    def test_preserves_text_and_skips_empty_rows(self):
        rows = [
            {"text": ""},
            {"text": "  \n"},
            {"text": "Exact text.\n"},
            {"text": "Second record"},
        ]
        out = freeze_rows(rows)
        self.assertEqual([r["text"] for r in out], ["Exact text.\n", "Second record"])
        self.assertEqual(out[0]["source_row"], 2)

    def test_exact_duplicates_are_removed(self):
        rows = [{"text": "same"}, {"text": "same"}, {"text": "different"}]
        out = freeze_rows(rows)
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0]["text"], "same")
        self.assertEqual(out[1]["text"], "different")

    def test_rejects_non_string_text(self):
        with self.assertRaises(ValueError):
            freeze_rows([{"text": None}])


if __name__ == "__main__":
    unittest.main()
