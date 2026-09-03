import unittest

from tests.helpers import import_lib

lib = import_lib()
from agentlint_lib import catalogue, model  # noqa: E402,F401


class CatalogueTests(unittest.TestCase):
    def test_every_rule_is_well_formed(self):
        self.assertGreaterEqual(len(model.RULES), 90)
        for rid, r in model.RULES.items():
            self.assertRegex(rid, r"^(GN|AG|SK|IN|CF|XF)\d{3}$")
            self.assertTrue(r.source.startswith("https://"), rid)
            self.assertTrue(r.title and r.title[0].isupper(), rid)

    def test_expected_ids_present(self):
        for rid in ["GN001", "AG001", "AG028", "SK001", "SK019", "IN001", "IN020",
                    "CF001", "CF022", "XF001", "XF010"]:
            self.assertIn(rid, model.RULES)

    def test_manual_rules_cannot_be_emitted(self):
        with self.assertRaises(ValueError):
            model.Finding("AG018", "x.md", "nope")
