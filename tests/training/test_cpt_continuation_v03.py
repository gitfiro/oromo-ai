import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "training"
    / "tools"
    / "prepare_cpt_continuation_v03.py"
)
spec = importlib.util.spec_from_file_location("prepare_cpt_continuation_v03", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load builder: {MODULE_PATH}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ContinuationSelectionTest(unittest.TestCase):
    def test_proportional_targets_sum_exactly(self):
        got = module.proportional_targets({"a": 3, "b": 7}, 5)
        self.assertEqual(sum(got.values()), 5)
        self.assertEqual(got, {"a": 2, "b": 3})

    def test_proportional_targets_reject_oversubscription(self):
        with self.assertRaises(ValueError):
            module.proportional_targets({"a": 3}, 4)

    def test_selection_is_rank_deterministic_and_meets_target(self):
        rows = [
            {"rank": "c", "text_sha256": "3", "words": 4},
            {"rank": "a", "text_sha256": "1", "words": 3},
            {"rank": "b", "text_sha256": "2", "words": 5},
        ]
        selected, words = module.select_to_word_target(rows, 6)
        self.assertEqual([x["rank"] for x in selected], ["a", "b"])
        self.assertEqual(words, 8)

    def test_rank_is_source_scoped(self):
        self.assertNotEqual(
            module.rank_key("source-a", "same text"),
            module.rank_key("source-b", "same text"),
        )


if __name__ == "__main__":
    unittest.main()
