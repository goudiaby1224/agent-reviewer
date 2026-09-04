import unittest

from tests.helpers import BAD, ids, run_lint


class XfRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_lint(root=BAD)
        cls.got = ids(cls.result)

    def expect(self, path, *rule_ids):
        for rid in rule_ids:
            self.assertIn((rid, path), self.got, "%s missing on %s" % (rid, path))

    def test_skill_shadowing(self):
        self.expect(".claude/skills/alpha-skill/SKILL.md", "XF001")
        self.assertNotIn(("XF001", ".github/skills/alpha-skill/SKILL.md"), self.got)

    def test_agent_twin_with_diverging_bodies(self):
        self.expect(".claude/agents/twin.md", "XF002")
        msg = [f["message"] for f in self.result["findings"] if f["id"] == "XF002" and f["file"] == ".claude/agents/twin.md"][0]
        self.assertIn("bodies differ", msg)

    def test_dangling_references(self):
        self.expect(".github/agents/twin.agent.md", "XF003")
        self.expect(".claude/agents/twin.md", "XF003", "XF004")
        self.expect(".claude/skills/beta-skill/SKILL.md", "XF003")

    def test_command_and_skill_collision(self):
        self.expect(".claude/commands/alpha-skill.md", "XF005")

    def test_overlapping_globs(self):
        self.expect(".github/instructions/py-a.instructions.md", "XF006")

    def test_claude_and_agents_md_coexist(self):
        self.expect("CLAUDE.md", "XF010")
