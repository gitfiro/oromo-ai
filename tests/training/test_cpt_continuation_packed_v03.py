import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "training"
    / "tools"
    / "prepare_cpt_continuation_packed_v03.py"
)
spec = importlib.util.spec_from_file_location("prepare_cpt_continuation_packed_v03", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load packer: {MODULE_PATH}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ContinuationPackingTest(unittest.TestCase):
    def test_frozen_hash_constants(self):
        self.assertEqual(
            module.TRAIN_EXPECTED,
            "814f52575f4e4e38ff64b98b01bbe3837d17129cc2628d43cd8e571d1d2b298d",
        )
        self.assertEqual(
            module.VALIDATION_EXPECTED,
            "cd1872643749992c7d4e22dad9b7dbe34907f0a5f96204c3040d428fc749a3d8",
        )

    def test_validation_is_original_frozen_holdout(self):
        self.assertEqual(
            str(module.VALIDATION),
            "training/data/oromocorpus-cpt-pilot-v0.1/validation.jsonl",
        )


if __name__ == "__main__":
    unittest.main()
