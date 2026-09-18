import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from tests.helpers import SCRIPTS_DIR, ids, import_lib

lib = import_lib()
from agentlint_lib import api, discover, report  # noqa: E402

ENTRY = os.path.join(SCRIPTS_DIR, "agentlint.py")
SKILL = "---\nname: alpha\ndescription: d\n---\nbody\n"
AGENT = "---\nname: a\ndescription: d\ntools: Read\nskills:\n  - alpha\n---\nbody\n"


def write(root, rel, content):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as fh:
        fh.write(content)


def git(root, *args):
    subprocess.run(["git", "-C", root] + list(args), check=True, capture_output=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                        "GIT_COMMITTER_EMAIL": "t@t"})


class ChangedSinceTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        git(self.root, "init", "-q")
        write(self.root, ".claude/skills/alpha/SKILL.md", SKILL)
        write(self.root, ".claude/agents/a.md", AGENT)
        write(self.root, "AGENTS.md", "# old\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-q", "-m", "base")
        write(self.root, ".claude/agents/a.md", AGENT.replace("description: d", "description: changed"))
        write(self.root, ".github/copilot-instructions.md", "# new\n")
        os.remove(os.path.join(self.root, "AGENTS.md"))

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_changed_files_lists_modified_and_untracked_not_deleted(self):
        self.assertEqual(discover.changed_files(self.root, "HEAD"),
                         [".claude/agents/a.md", ".github/copilot-instructions.md"])

    def test_lint_scopes_to_changed_files_but_resolves_against_repo(self):
        r = api.lint(self.root, [], [], True, "info", None, changed_since="HEAD")
        self.assertEqual([f["path"] for f in r["files"]], [".claude/agents/a.md", ".github/copilot-instructions.md"])
        self.assertNotIn("XF003", {i for i, _ in ids(r)})  # alpha exists in the unchanged tree
        self.assertEqual(r["scope"], {"paths": [], "changed_since": "HEAD"})
        self.assertIn("scope=changed-since HEAD", report.to_text(r).split("\n")[0])

    def test_paths_and_changed_since_intersect(self):
        r = api.lint(self.root, [".github"], [], True, "info", None, changed_since="HEAD")
        self.assertEqual([f["path"] for f in r["files"]], [".github/copilot-instructions.md"])

    def test_no_changes_lints_nothing(self):
        git(self.root, "add", ".")
        git(self.root, "commit", "-q", "-m", "all")
        r = api.lint(self.root, [], [], True, "info", None, changed_since="HEAD")
        self.assertEqual(r["files"], [])
        self.assertEqual(r["summary"], {"error": 0, "warning": 0, "info": 0})

    def test_unknown_ref_raises(self):
        with self.assertRaises(ValueError):
            discover.changed_files(self.root, "no-such-ref")

    def test_cli_exit_2_on_bad_ref_and_outside_git(self):
        p = subprocess.run([sys.executable, ENTRY, "--root", self.root, "--changed-since", "no-such-ref"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertIn("no-such-ref", p.stderr)
        plain = tempfile.mkdtemp()
        try:
            p = subprocess.run([sys.executable, ENTRY, "--root", plain, "--changed-since", "HEAD"],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 2)
        finally:
            shutil.rmtree(plain)
