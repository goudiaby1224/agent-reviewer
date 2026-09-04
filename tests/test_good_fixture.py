import os
import unittest
from unittest import mock

from tests.helpers import BAD, GOOD, ids, import_lib, run_lint

lib = import_lib()
from agentlint_lib import model  # noqa: E402

EXPECTED_INFO = {("AG012", ".github/agents/reviewer.agent.md"), ("XF002", ".claude/agents/reviewer.md")}
# rules exercised from temp dirs or with --kind rather than from tests/fixtures/bad
TEMP_TESTED = {"GN001", "GN002", "GN003", "GN004", "AG010", "SK006", "IN005", "CF005", "CF016"}


class GoodFixtureTests(unittest.TestCase):
    def check(self):
        r = run_lint(root=GOOD)
        self.assertEqual(r["summary"]["error"], 0, r["findings"])
        self.assertEqual(r["summary"]["warning"], 0, r["findings"])
        self.assertEqual(ids(r), EXPECTED_INFO)
        self.assertEqual(len(r["files"]), 14)

    def test_with_default_parser(self):
        self.check()

    def test_with_builtin_parser(self):
        with mock.patch.dict(os.environ, {"AGENTLINT_YAML": "builtin"}):
            self.check()


class CoverageTests(unittest.TestCase):
    def test_every_auto_rule_has_a_bad_fixture(self):
        seen = {rid for rid, _ in ids(run_lint(root=BAD))}
        seen |= {rid for rid, _ in ids(run_lint(root=BAD, paths=["cloud-mcp.json"], force_kind="mcp-copilot-cloud"))}
        auto = {rid for rid, r in model.RULES.items() if r.tag == "auto"}
        self.assertEqual(auto - seen - TEMP_TESTED, set())
