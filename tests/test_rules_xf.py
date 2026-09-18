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

    def test_scalar_skills_is_not_iterated_per_character(self):
        """A string `skills:` must not be walked character by character.

        bad-name.md carries `skills: alpha-skill`. AG027 already reports the
        scalar as the root cause, so XF003 must stay silent rather than raise
        one dangling-skill error per letter.
        """
        self.expect(".claude/agents/bad-name.md", "AG027")
        spurious = [f for f in self.result["findings"]
                    if f["id"] == "XF003" and f["file"] == ".claude/agents/bad-name.md"]
        self.assertEqual(spurious, [], "XF003 fired on a scalar skills value")

    def test_scalar_rule_paths_is_not_iterated_per_character(self):
        """A string `paths:` in .claude/rules must not become one glob per letter."""
        bogus = [f for f in self.result["findings"]
                 if f["id"] == "XF006" and "bad.md" in f["message"]]
        self.assertEqual([f["message"] for f in bogus], [],
                         "XF006 paired against single characters of a scalar paths value")

    def test_claude_and_agents_md_coexist(self):
        self.expect("CLAUDE.md", "XF010")
