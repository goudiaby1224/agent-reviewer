import unittest

from tests.helpers import BAD, ids, run_lint


class CfRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_lint(root=BAD, collisions=False)
        cls.got = ids(cls.result)

    def expect(self, path, *rule_ids):
        for rid in rule_ids:
            self.assertIn((rid, path), self.got, "%s missing on %s" % (rid, path))

    def count(self, rid, path):
        return len([f for f in self.result["findings"] if f["id"] == rid and f["file"] == path])

    def test_claude_mcp(self):
        self.expect(".mcp.json", "CF003", "CF006", "CF004", "CF013", "CF014", "CF012", "CF011", "CF010")
        msgs = {f["id"]: f["message"] for f in self.result["findings"] if f["file"] == ".mcp.json"}
        self.assertTrue(msgs["CF003"].startswith("a:"))
        self.assertTrue(msgs["CF004"].startswith("b:"))
        self.assertTrue(msgs["CF012"].startswith("c:"))
        self.assertTrue(msgs["CF010"].startswith("d:"))

    def test_vscode_mcp(self):
        self.expect(".vscode/mcp.json", "CF002")
        self.expect("sub/.vscode/mcp.json", "CF015", "CF022")

    def test_invalid_json(self):
        self.expect(".github/mcp.json", "CF001")

    def test_cloud_mcp_via_force_kind(self):
        got = ids(run_lint(root=BAD, paths=["cloud-mcp.json"], force_kind="mcp-copilot-cloud", collisions=False))
        self.assertIn(("CF005", "cloud-mcp.json"), got)
        self.assertIn(("CF016", "cloud-mcp.json"), got)

    def test_hooks(self):
        self.expect(".claude/settings.json", "CF007", "CF018", "CF017", "CF010")
        self.assertEqual(self.count("CF007", ".claude/settings.json"), 2)
        self.expect(".claude/agents/hooky.md", "CF007")

    def test_setup_steps(self):
        p = ".github/workflows/copilot-setup-steps.yml"
        self.expect(p, "CF008", "CF019")
        self.assertEqual(self.count("CF008", p), 2)

    def test_manifests(self):
        self.expect(".claude-plugin/plugin.json", "CF020", "CF009")
        self.expect(".claude-plugin/marketplace.json", "CF020", "CF021")
