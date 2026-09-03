import os
import shutil
import tempfile
import unittest

from tests.helpers import BAD, ids, run_lint


class AgRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_lint(root=BAD, collisions=False)
        cls.got = ids(cls.result)

    def expect(self, path, *rule_ids):
        for rid in rule_ids:
            self.assertIn((rid, path), self.got, "%s missing on %s" % (rid, path))

    def test_copilot_agents(self):
        self.expect(".github/agents/no-frontmatter.agent.md", "AG001")
        self.expect(".github/agents/bad-yaml.agent.md", "AG001")
        self.expect(".github/agents/missing-description.agent.md", "AG002", "AG005", "AG022", "AG017")
        self.expect(".github/agents/bad name.agent.md", "AG013", "AG024", "AG016")
        self.expect(".github/agents/bad-tools.agent.md", "AG007", "AG009", "AG012", "AG014", "AG025", "AG026", "AG028")
        self.expect(".github/agents/vscode-target.agent.md", "AG011")
        self.assertNotIn(("AG012", ".github/agents/vscode-target.agent.md"), self.got)
        self.expect(".github/chatmodes/old.chatmode.md", "AG006")
        ag007 = [f for f in self.result["findings"] if f["id"] == "AG007" and f["file"] == ".github/agents/bad-tools.agent.md"]
        self.assertEqual(len(ag007), 2)

    def test_claude_subagents(self):
        self.expect(".claude/agents/bad-name.md", "AG004", "AG008", "AG015", "AG014", "AG026", "AG027", "AG017")
        self.expect(".claude/agents/no-name.md", "AG003", "AG023")
        self.expect(".claude/agents/no-tools-resolve.md", "AG008")
        sev = {f["file"]: f["severity"] for f in self.result["findings"] if f["id"] == "AG008"}
        self.assertEqual(sev[".claude/agents/bad-name.md"], "warning")
        self.assertEqual(sev[".claude/agents/no-tools-resolve.md"], "error")

    def test_body_limit_from_tempdir(self):
        root = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(root, ".github", "agents"))
            with open(os.path.join(root, ".github", "agents", "big.agent.md"), "w") as fh:
                fh.write("---\ndescription: d\n---\n" + "x" * 30001)
            got = ids(run_lint(root=root, collisions=False))
            self.assertIn(("AG010", ".github/agents/big.agent.md"), got)
        finally:
            shutil.rmtree(root)
