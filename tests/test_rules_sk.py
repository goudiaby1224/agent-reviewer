import os
import shutil
import tempfile
import unittest

from tests.helpers import BAD, ids, run_lint


class SkRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_lint(root=BAD, collisions=False)
        cls.got = ids(cls.result)

    def expect(self, path, *rule_ids):
        for rid in rule_ids:
            self.assertIn((rid, path), self.got, "%s missing on %s" % (rid, path))

    def test_wrong_name_bundle(self):
        self.expect(".claude/skills/wrong-name/SKILL.md", "SK004", "SK014", "SK019", "SK010", "SK011", "SK009", "SK007")

    def test_sk007_counts_each_dead_path_once(self):
        n = [f for f in self.result["findings"] if f["id"] == "SK007" and f["file"] == ".claude/skills/wrong-name/SKILL.md"]
        self.assertEqual(len(n), 2)

    def test_name_and_description(self):
        self.expect(".claude/skills/bad-name/SKILL.md", "SK003", "SK004")
        self.expect(".claude/skills/no-name/SKILL.md", "SK002")
        self.expect(".claude/skills/no-description/SKILL.md", "SK005")
        self.expect(".claude/skills/no-frontmatter/SKILL.md", "SK001")

    def test_location_and_filename(self):
        self.expect(".github/skills/lowercase/skill.md", "SK012")
        self.expect("docs/stray/SKILL.md", "SK013")

    def test_scripts(self):
        self.expect(".claude/skills/bad-scripts/SKILL.md", "SK008")

    def test_alpha_skill_only_portability_note(self):
        got = {rid for rid, f in self.got if f == ".claude/skills/alpha-skill/SKILL.md" and rid.startswith("SK")}
        self.assertEqual(got, {"SK010"})

    def test_long_body_from_tempdir(self):
        root = tempfile.mkdtemp()
        try:
            d = os.path.join(root, ".claude", "skills", "long")
            os.makedirs(d)
            with open(os.path.join(d, "SKILL.md"), "w") as fh:
                fh.write("---\nname: long\ndescription: d\n---\n" + "line\n" * 501)
            self.assertIn(("SK006", ".claude/skills/long/SKILL.md"), ids(run_lint(root=root, collisions=False)))
        finally:
            shutil.rmtree(root)
