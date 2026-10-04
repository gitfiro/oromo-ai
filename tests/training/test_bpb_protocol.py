import importlib.util
import math
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('bpb', Path(__file__).resolve().parents[2] / 'training/tools/evaluate_bpb.py')
bpb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bpb)

class ProtocolTest(unittest.TestCase):
    def test_every_target_once_with_bounded_context(self):
        for size in [2,3,8,9,17,100]:
            for context in [2,4,8]:
                for stride in range(1,context):
                    scored=[]
                    for segment, first in bpb.windows(list(range(size)),context,stride):
                        self.assertLessEqual(len(segment),context)
                        self.assertGreaterEqual(first,1)
                        scored.extend(segment[first:])
                    self.assertEqual(scored,list(range(1,size)))
    def test_byte_normalization_not_token_average(self):
        a=bpb.summarize(12*math.log(2),6,12,10,1)
        b=bpb.summarize(12*math.log(2),3,12,10,1)
        self.assertAlmostEqual(a['bits_per_byte'],1)
        self.assertEqual(a['bits_per_byte'],b['bits_per_byte'])
    def test_invalid_windows(self):
        with self.assertRaises(ValueError):list(bpb.windows([0,1],4,4))

if __name__=='__main__':unittest.main()
