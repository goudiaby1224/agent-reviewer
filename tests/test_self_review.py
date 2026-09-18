import unittest

from tests.helpers import REPO_ROOT, run_lint


class SelfReviewTests(unittest.TestCase):
    def test_repository_lints_clean(self):
        r = run_lint(root=REPO_ROOT, excludes=["tests/fixtures/**"])
        self.assertEqual(r["summary"]["error"], 0, r["findings"])
        self.assertEqual(r["summary"]["warning"], 0, r["findings"])
        kinds = {f["kind"] for f in r["files"]}
        self.assertTrue({"copilot-agent", "claude-subagent", "skill", "prompt-file"} <= kinds, kinds)
        self.assertTrue({"plugin-manifest", "marketplace-manifest"} <= kinds, kinds)
        paths = {f["path"] for f in r["files"]}
        self.assertTrue({".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", ".github/plugin/plugin.json"} <= paths)
