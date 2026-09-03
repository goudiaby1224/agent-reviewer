import os
import shutil
import tempfile
import unittest

from tests.helpers import BAD, ids, run_lint


class InRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_lint(root=BAD, collisions=False)
        cls.got = ids(cls.result)

    def expect(self, path, *rule_ids):
        for rid in rule_ids:
            self.assertIn((rid, path), self.got, "%s missing on %s" % (rid, path))

    def test_path_instructions(self):
        self.expect(".github/instructions/no-apply.instructions.md", "IN002", "IN014")
        self.expect(".github/instructions/list-apply.instructions.md", "IN003", "IN004")
        self.expect(".github/instructions/broken.instructions.md", "IN001")
        self.expect("docs/misplaced.instructions.md", "IN011")

    def test_prompt_files(self):
        self.expect(".github/prompts/legacy.prompt.md", "IN018", "IN019")
        self.expect(".github/prompts/dangling.prompt.md", "IN006")

    def test_copilot_instructions(self):
        self.expect(".github/copilot-instructions.md", "IN012", "IN017")

    def test_agents_md(self):
        self.expect("pkg/AGENT.md", "IN010", "IN009")

    def test_claude_md_imports(self):
        self.expect("CLAUDE.md", "IN007")
        n = [f for f in self.result["findings"] if f["id"] == "IN007" and f["file"] == "CLAUDE.md"]
        self.assertEqual(len(n), 1, "e-mail address must not be treated as an import")

    def test_claude_rules_and_commands(self):
        self.expect(".claude/rules/bad.md", "IN008")
        self.expect(".claude/commands/alpha-skill.md", "IN020")

    def test_cursor(self):
        self.expect(".cursor/rules/old.md", "IN013")

    def test_long_file_from_tempdir(self):
        root = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(root, ".github"))
            with open(os.path.join(root, ".github", "copilot-instructions.md"), "w") as fh:
                fh.write("x\n" * 1001)
            self.assertIn(("IN005", ".github/copilot-instructions.md"), ids(run_lint(root=root, collisions=False)))
        finally:
            shutil.rmtree(root)
