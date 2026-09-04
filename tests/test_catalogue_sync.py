import os
import unittest

from tests.helpers import REPO_ROOT, import_lib

lib = import_lib()
from agentlint_lib import api, report  # noqa: E402

CATALOGUE = os.path.join(REPO_ROOT, ".claude", "skills", "linting-agent-config-files", "references", "rule-catalogue.md")


class CatalogueSyncTests(unittest.TestCase):
    def test_reference_matches_registry(self):
        api._load_rule_modules()
        with open(CATALOGUE, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), report.catalogue_markdown())
