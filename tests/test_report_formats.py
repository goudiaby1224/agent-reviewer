import os
import subprocess
import sys
import tempfile
import unittest

from tests.helpers import BAD, SCRIPTS_DIR, import_lib, run_lint

lib = import_lib()
from agentlint_lib import report  # noqa: E402

ENTRY = os.path.join(SCRIPTS_DIR, "agentlint.py")


class MarkdownTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_lint(root=BAD)
        cls.md = report.to_markdown(cls.result)

    def test_header_and_sections(self):
        lines = self.md.split("\n")
        self.assertEqual(lines[0], "# Agent configuration review")
        self.assertTrue(lines[1].startswith("Scope: whole repository      Files scanned: "))
        self.assertIn("Linter: agentlint 1.0.0 (", lines[1])
        s = self.result["summary"]
        self.assertEqual(lines[2], "Errors: %d   Warnings: %d   Info: %d" % (s["error"], s["warning"], s["info"]))
        for heading in ("## Errors", "## Warnings", "## Info and portability notes", "## Not checked"):
            self.assertIn(heading, self.md)

    def test_one_bullet_per_finding_grouped_by_file(self):
        bullets = [l for l in self.md.split("\n") if l.startswith("- [")]
        self.assertEqual(len(bullets), len(self.result["findings"]))
        self.assertIn("### .mcp.json", self.md)
        self.assertIn("- [SK004] line 2 — name 'other-name' differs from directory 'wrong-name'", self.md)
        self.assertIn("  Source: https://agentskills.io/specification  Fix: name: wrong-name  Confidence: high", self.md)

    def test_not_checked_copies_linter_entries(self):
        tail = self.md.split("## Not checked\n")[1]
        self.assertTrue(tail.startswith("- Copilot cloud-agent MCP configuration"))

    def test_empty_sections_and_nothing_skipped(self):
        r = {"agentlint_version": "1.0.0", "yaml_parser": "pyyaml", "files": [], "findings": [],
             "summary": {"error": 0, "warning": 0, "info": 0}, "not_checked": [], "scope": {"paths": ["x"], "changed_since": None}}
        md = report.to_markdown(r)
        self.assertIn("Scope: x      Files scanned: 0", md)
        self.assertEqual(md.count("- none"), 3)
        self.assertIn("## Not checked\n- Nothing was skipped.\n", md)

    def test_changed_since_scope_label(self):
        r = {"agentlint_version": "1.0.0", "yaml_parser": "pyyaml", "files": [], "findings": [],
             "summary": {"error": 0, "warning": 0, "info": 0}, "not_checked": [],
             "scope": {"paths": [".github"], "changed_since": "origin/main"}}
        self.assertIn("Scope: changed since origin/main within .github", report.to_markdown(r))


class GithubTests(unittest.TestCase):
    def test_one_command_per_finding(self):
        r = run_lint(root=BAD)
        out = report.to_github(r).split("\n")
        cmds = [l for l in out if l.startswith("::")]
        self.assertEqual(len(cmds), len(r["findings"]))
        s = r["summary"]
        self.assertEqual(len([l for l in cmds if l.startswith("::error ")]), s["error"])
        self.assertEqual(len([l for l in cmds if l.startswith("::warning ")]), s["warning"])
        self.assertEqual(len([l for l in cmds if l.startswith("::notice ")]), s["info"])
        self.assertIn("::error file=.claude/skills/wrong-name/SKILL.md,line=2,title=SK004::name 'other-name' differs from directory 'wrong-name'", out)
        self.assertEqual(out[-2], "errors: %d, warnings: %d, info: %d" % (s["error"], s["warning"], s["info"]))

    def test_escapes_message_and_properties(self):
        r = {"agentlint_version": "1.0.0", "yaml_parser": "pyyaml", "files": [], "not_checked": [],
             "summary": {"error": 1, "warning": 0, "info": 0}, "scope": {"paths": [], "changed_since": None},
             "findings": [{"id": "CF001", "severity": "error", "file": "a,b:c.json", "line": None,
                           "message": "100% bad\nsecond line", "source": "", "confidence": "high", "suggestion": ""}]}
        self.assertEqual(report.to_github(r).split("\n")[0],
                         "::error file=a%2Cb%3Ac.json,title=CF001::100%25 bad%0Asecond line")


class CliFormatTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        with open(os.path.join(self.root, "AGENTS.md"), "wb") as fh:
            fh.write(b"# hi\r\n")

    def run_cli(self, *args):
        return subprocess.run([sys.executable, ENTRY, "--root", self.root] + list(args), capture_output=True, text=True)

    def test_markdown_and_github_formats(self):
        p = self.run_cli("--format", "markdown")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(p.stdout.startswith("# Agent configuration review\n"))
        p = self.run_cli("--format", "github")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("::notice file=AGENTS.md,line=1,title=GN002::CRLF line endings; tools differ in how they detect the --- delimiters", p.stdout)
