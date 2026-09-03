import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from tests.helpers import SCRIPTS_DIR, import_lib

lib = import_lib()
from agentlint_lib import api, report  # noqa: E402

ENTRY = os.path.join(SCRIPTS_DIR, "agentlint.py")


def write(root, rel, content):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    mode = "wb" if isinstance(content, bytes) else "w"
    with open(p, mode) as fh:
        fh.write(content)


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_result_shape_and_gn_rules(self):
        write(self.root, "AGENTS.md", b"\xef\xbb\xbf# hi\r\n")
        write(self.root, "bad.agent.md", b"\xff\xfe\x00\x00binary")
        write(self.root, "CLAUDE.md", b"caf\xe9\n")
        r = api.lint(root=self.root, paths=[], excludes=[], collisions=False, min_severity="info", force_kind=None)
        for key in ("agentlint_version", "root", "python", "yaml_parser", "files", "findings", "summary", "not_checked"):
            self.assertIn(key, r)
        got = {(f["id"], f["file"]) for f in r["findings"]}
        self.assertIn(("GN001", "AGENTS.md"), got)
        self.assertIn(("GN002", "AGENTS.md"), got)
        self.assertIn(("GN004", "bad.agent.md"), got)
        self.assertIn(("GN003", "CLAUDE.md"), got)
        self.assertEqual(r["summary"]["error"], 1)

    def test_min_severity_filters(self):
        write(self.root, "AGENTS.md", b"# hi\r\n")
        r = api.lint(self.root, [], [], False, "warning", None)
        self.assertEqual(r["findings"], [])
        self.assertEqual(r["summary"], {"error": 0, "warning": 0, "info": 0})

    def test_text_report(self):
        write(self.root, "AGENTS.md", b"# hi\r\n")
        r = api.lint(self.root, [], [], False, "info", None)
        text = report.to_text(r)
        self.assertIn("INFO  GN002 AGENTS.md:1", text)
        self.assertIn("errors: 0, warnings: 0, info: 1", text)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root)

    def run_cli(self, *args):
        return subprocess.run([sys.executable, ENTRY, "--root", self.root] + list(args),
                              capture_output=True, text=True)

    def test_exit_codes(self):
        write(self.root, "AGENTS.md", "# ok\n")
        self.assertEqual(self.run_cli().returncode, 0)
        write(self.root, "CLAUDE.md", b"caf\xe9\n")
        p = self.run_cli("--format", "json")
        self.assertEqual(p.returncode, 1)
        data = json.loads(p.stdout)
        self.assertEqual(data["summary"]["error"], 1)

    def test_usage_error(self):
        self.assertEqual(self.run_cli("--kind", "nonsense").returncode, 2)

    def test_list_rules(self):
        p = self.run_cli("--list-rules")
        self.assertEqual(p.returncode, 0)
        self.assertIn("AG001", p.stdout)
        p = self.run_cli("--list-rules", "--format", "markdown")
        self.assertIn("| AG001 |", p.stdout)
        self.assertEqual(p.stdout, report.catalogue_markdown())
