import os
import unittest

from tests.helpers import REPO_ROOT, ids, import_lib, run_lint

lib = import_lib()
from agentlint_lib import yamlfm  # noqa: E402

GH = os.path.join(REPO_ROOT, ".github", "agents", "agent-skill-reviewer.agent.md")
CL = os.path.join(REPO_ROOT, ".claude", "agents", "agent-skill-reviewer.md")
PROMPT = os.path.join(REPO_ROOT, ".github", "prompts", "review-agent-config.prompt.md")
SKILLS_DIR = os.path.join(REPO_ROOT, ".claude", "skills")


def load(path):
    with open(path, encoding="utf-8") as fh:
        fm_text, body, _, err = yamlfm.split_frontmatter(fh.read())
    assert err is None, err
    fm, err = yamlfm.parse_yaml(fm_text)
    assert err is None, err
    return fm, body


class AgentFileTests(unittest.TestCase):
    def test_bodies_identical(self):
        self.assertEqual(load(GH)[1], load(CL)[1])

    def test_copilot_frontmatter(self):
        fm, body = load(GH)
        self.assertEqual(fm["name"], "agent-skill-reviewer")
        self.assertEqual(fm["tools"], ["read", "search", "execute"])
        self.assertNotIn("edit", fm["tools"])
        self.assertNotIn("model", fm)
        self.assertLess(len(body), 30000)
        self.assertRegex(os.path.basename(GH), r"^[A-Za-z0-9._-]+$")

    def test_claude_frontmatter(self):
        fm, _ = load(CL)
        self.assertEqual(fm["name"], "agent-skill-reviewer")
        self.assertIsInstance(fm["tools"], str)
        for forbidden in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
            self.assertNotIn(forbidden, fm["tools"].split(", "))
        self.assertEqual(fm["model"], "inherit")
        for s in fm["skills"]:
            self.assertTrue(os.path.isfile(os.path.join(SKILLS_DIR, s, "SKILL.md")), s)

    def test_body_is_runtime_neutral_and_names_every_skill(self):
        _, body = load(GH)
        self.assertNotIn("#tool:", body)
        self.assertNotIn("$ARGUMENTS", body)
        for s in sorted(os.listdir(SKILLS_DIR)):
            self.assertIn(s, body, "body must name skill %s" % s)

    def test_prompt_targets_agent(self):
        fm, _ = load(PROMPT)
        self.assertEqual(fm["agent"], "agent-skill-reviewer")

    def test_linter_is_clean_on_agent_files(self):
        r = run_lint(root=REPO_ROOT, paths=[".github/agents", ".claude/agents", ".github/prompts"])
        self.assertEqual(r["summary"]["error"], 0, r["findings"])
        self.assertEqual(r["summary"]["warning"], 0, r["findings"])
        self.assertEqual(ids(r), {("AG012", ".github/agents/agent-skill-reviewer.agent.md"),
                                  ("XF002", ".claude/agents/agent-skill-reviewer.md")})
