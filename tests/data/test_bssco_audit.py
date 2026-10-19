"""Routing boundaries and Unicode handling for candidate-only BSSCO auditing."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "audit_bssco.py"
spec = importlib.util.spec_from_file_location("bssco_audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

OROMO = "Mootummaan naannoo kana keessatti hojii misooma uummata irrattii hojjechuu qaba. Akkasumas akka seera kana keessatti tumameetti aangoo fi mirga uummata eeguuf yeroo hunda hojii raawwata."
ENGLISH = "The government of the region shall respect the rights of the people and shall have the duty to implement the policy of this chapter."


class BsscoAuditTests(unittest.TestCase):
    def test_clean_oromo_is_only_a_candidate(self):
        self.assertEqual(audit.route(audit.evidence(OROMO, 80)), "oromo_candidate")

    def test_english_and_mixed_page_do_not_pass(self):
        self.assertEqual(audit.route(audit.evidence(ENGLISH, 90)), "english")
        self.assertNotEqual(audit.route(audit.evidence(OROMO + ENGLISH, 90)), "oromo_candidate")

    def test_low_confidence_and_repeated_marker_do_not_pass(self):
        self.assertEqual(audit.route(audit.evidence(OROMO, 28)), "unknown")
        self.assertEqual(audit.route(audit.evidence("fi " * 50, 90)), "unknown")

    def test_amharic_ocr_words_are_counted_as_words(self):
        tsv = "level\tpage_num\tblock_num\tpar_num\tline_num\tconf\ttext\n5\t1\t1\t1\t1\t88\tመንግሥት\n5\t1\t1\t1\t1\t90\tክልሉ\n"
        text, conf, count = audit.tsv_result(tsv)
        self.assertEqual(count, 2)
        self.assertGreater(conf, 88)
        self.assertEqual(audit.evidence(text)["ethiopic_rate"], 1)
        self.assertEqual(audit.route(audit.evidence(text, conf)), "unknown")

    def test_region_isolation_can_recover_mixed_page(self):
        import xml.etree.ElementTree as ET
        page = ET.Element("page", width="1000")
        for x, text in [(10, OROMO), (700, ENGLISH)]:
            line = ET.SubElement(page, "line")
            for token in text.split():
                word = ET.SubElement(line, "word", xMin=str(x), xMax=str(x + 20))
                word.text = token
        attempts = audit.direct_attempts(page)
        self.assertEqual(attempts[0]["decision"], "unknown")
        chosen = audit.choose(attempts)
        self.assertEqual(chosen["region"], "left38")
        self.assertNotIn("government", chosen["text"])

    def test_normalization_preserves_apostrophes_and_hyphens(self):
        self.assertEqual(audit.normalize("  ta’u\nbar-\nnoota  "), "ta’u\nbar-\nnoota")


if __name__ == "__main__":
    unittest.main()
