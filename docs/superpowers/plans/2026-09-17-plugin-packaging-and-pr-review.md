# Plugin packaging and pull-request review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `agent-skill-reviewer` installable as a Copilot CLI plugin and a Claude Code plugin from this repository, and let it review pull requests in Claude Code, on github.com and in a GitHub Actions check.

**Architecture:** Two plugin manifests point at the existing `.github/agents`, `.claude/agents` and `.claude/skills` directories, so nothing moves. The linter gains `--changed-since REF` plus `markdown` and `github` output formats; a new `reviewing-pull-requests` skill holds the PR procedure for the model-driven runtimes; a workflow runs the linter on PRs.

**Tech Stack:** Python 3.8+ standard library (linter), Markdown/YAML (skills, agents), JSON (manifests), GitHub Actions, `gh` CLI (used by the skill at review time, never by the linter).

**Spec:** `docs/superpowers/specs/2026-09-14-plugin-packaging-and-pr-review-design.md` (extends `docs/superpowers/specs/2026-09-03-agent-skill-reviewer-design.md`).

## Global Constraints

- Python floor 3.8; no third-party imports in the linter; `git` is invoked as a subprocess only for `--changed-since` and discovery; the linter never touches the network.
- No second copy of any agent or skill; manifests point at existing files.
- Nothing is posted to a PR unless explicitly asked (subagent) or `vars.AGENTLINT_PR_COMMENT == 'true'` (workflow); never a review verdict.
- Rule-ID families stay `GN`, `AG`, `SK`, `IN`, `CF`, `XF`; no new catalogue rules in this plan.
- Every `SKILL.md`: `name` equals its directory, `description` ≤ 1024 characters, third person, no workflow summary, no `: ` inside an unquoted description; body ≤ 500 lines; frontmatter keys `name`, `description`, `metadata` only.
- Both agent bodies stay byte-identical below the frontmatter (`tests/test_agent_files.py`).
- Plugin name `agent-reviewer`, version `1.1.0` in every manifest.
- Run tests with `python3 -m unittest discover -s tests` and again with `AGENTLINT_YAML=builtin`; lint the repository with `python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py --exclude 'tests/fixtures/**'` (expect `errors: 0, warnings: 0, info: 2`) before every commit.
- Commit after every task; commit messages end with:
  ```
  Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01HyFVLMJ8Mpq5xJ4Do1kMzv
  ```

---

## Deviations found while executing

- Task 3: `claude plugin validate` rejects a directory in `agents`; the field takes agent file paths (`["./.claude/agents/agent-skill-reviewer.md"]`). `skills` accepts the directory.
- Task 3: Copilot CLI 1.0.80 warns that direct installs are deprecated, so `.github/plugin/marketplace.json` was added and the documented install is `copilot plugin marketplace add` plus `copilot plugin install agent-reviewer@agent-reviewer`. `copilot plugin list` has no `--kind` flag in 1.0.80; components were verified with a `copilot -p` prompt from another directory.

## File structure

| Path | Responsibility |
|---|---|
| `.claude/skills/linting-agent-config-files/scripts/agentlint_lib/discover.py` | add `changed_files(root, ref)` |
| `.../agentlint_lib/api.py` | `lint(..., changed_since=None)`; `scope` in the result |
| `.../agentlint_lib/report.py` | add `to_markdown(result)`, `to_github(result)`; scope in `to_text` header |
| `.../agentlint_lib/cli.py` | `--changed-since`, `--format github`, `markdown` for results |
| `tests/test_changed_since.py` | `--changed-since` behaviour in a temporary git repository |
| `tests/test_report_formats.py` | markdown and github renderers, CLI dispatch |
| `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | Claude Code plugin and self-marketplace |
| `.github/plugin/plugin.json` | Copilot CLI plugin manifest |
| `.claude/skills/linting-agent-config-files/SKILL.md` | linter path relative to the skill directory |
| `.claude/skills/reviewing-pull-requests/SKILL.md`, `references/pr-comment-template.md` | PR procedure and sticky-comment template |
| `.claude/skills/writing-review-findings/SKILL.md` | PR variant of the report header |
| `.github/agents/agent-skill-reviewer.agent.md`, `.claude/agents/agent-skill-reviewer.md` | shared body: Step 1 wording, "Pull request mode" section |
| `.github/workflows/agent-config-review.yml` | PR check |
| `README.md` | install as plugin, reviewing a pull request, workflow reuse, verification log |
| `docs/reference/agent-file-formats.md` | two manifest paths in the Discovery table |
| `docs/superpowers/plans/2026-09-03-agent-skill-reviewer.md` | pointer to this plan under "Spec deltas" |

---

### Task 1: `--changed-since REF`

**Files:**
- Modify: `.claude/skills/linting-agent-config-files/scripts/agentlint_lib/discover.py` (after `_candidates`)
- Modify: `.claude/skills/linting-agent-config-files/scripts/agentlint_lib/api.py` (`lint`)
- Modify: `.claude/skills/linting-agent-config-files/scripts/agentlint_lib/report.py` (`to_text` header)
- Modify: `.claude/skills/linting-agent-config-files/scripts/agentlint_lib/cli.py`
- Test: `tests/test_changed_since.py`

**Interfaces:**
- Produces `discover.changed_files(root: str, ref: str) -> List[str]` (root-relative POSIX paths of existing files changed since `ref`, plus untracked files; raises `ValueError` when `git diff` fails).
- Produces `api.lint(root, paths, excludes, collisions=True, min_severity="info", force_kind=None, changed_since=None) -> dict`; the dict gains `"scope": {"paths": [...], "changed_since": <str or None>}`.
- CLI: `--changed-since REF`; exit 2 with a one-line stderr message when the ref is unknown or the root is not a git repository.

- [ ] **Step 1: Write the failing tests**

`tests/test_changed_since.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest tests.test_changed_since -v`
Expected: errors such as `AttributeError: module 'agentlint_lib.discover' has no attribute 'changed_files'` and `TypeError: lint() got an unexpected keyword argument 'changed_since'`.

- [ ] **Step 3: Add `changed_files` to `discover.py`**

Insert after `_candidates`:

```python
def changed_files(root: str, ref: str) -> List[str]:
    """Root-relative paths of existing files changed since REF (committed, staged or unstaged) plus untracked files."""
    def run(args):
        return subprocess.run(["git", "-C", root] + args, capture_output=True, text=True, timeout=30)
    try:
        p = run(["diff", "--name-only", "-z", ref, "--"])
    except (OSError, subprocess.SubprocessError) as e:
        raise ValueError("git diff against %r failed: %s" % (ref, e))
    if p.returncode != 0:
        raise ValueError("git diff against %r failed: %s" % (ref, p.stderr.strip().split("\n")[0] or "not a git repository"))
    rels = {x for x in p.stdout.split("\0") if x}
    untracked = run(["ls-files", "-z", "--others", "--exclude-standard"])
    if untracked.returncode == 0:
        rels |= {x for x in untracked.stdout.split("\0") if x}
    return sorted(r for r in rels if os.path.isfile(os.path.join(root, r)))
```

- [ ] **Step 4: Thread `changed_since` through `api.lint`**

Replace the signature and the discovery block in `api.py`:

```python
def lint(root: Optional[str], paths: List[str], excludes: List[str], collisions: bool = True,
         min_severity: str = "info", force_kind: Optional[str] = None,
         changed_since: Optional[str] = None) -> dict:
    _load_rule_modules()
    root = resolve_root(root)
    discovered = discover.discover(root, paths, excludes, force_kind)
    files = discovered
    if changed_since:
        changed = set(discover.changed_files(root, changed_since))  # ValueError -> exit 2 in the CLI
        files = [f for f in discovered if f.path in changed]
    # Explicit paths and --changed-since narrow what is reported, not what names resolve against: agents,
    # skills and prompts elsewhere in the repository still count when checking references from scoped files.
    universe = files
    if paths:
        in_scope = {f.path for f in files}
        universe = files + [f for f in discover.discover(root, [], excludes, None) if f.path not in in_scope]
    elif changed_since:
        universe = discovered
    ctx = Context(root=root, files=universe, yaml_parser=yamlfm.parser_name())
```

Keep the rest of the function unchanged and add to the returned dict, after `"root": root,`:

```python
        "scope": {"paths": list(paths), "changed_since": changed_since},
```

- [ ] **Step 5: Show the scope in the text header**

In `report.to_text`, replace the first `lines = [...]` statement with:

```python
    head = "agentlint %s  root=%s  yaml=%s  files=%d" % (
        result["agentlint_version"], result["root"], result["yaml_parser"], len(result["files"]))
    scope = result.get("scope") or {}
    if scope.get("changed_since"):
        head += "  scope=changed-since %s" % scope["changed_since"]
    lines = [head]
```

- [ ] **Step 6: Add the CLI flag**

In `cli.build_parser`, after the `--exclude` argument:

```python
    p.add_argument("--changed-since", metavar="REF", help="lint only configuration files changed since git REF")
```

In `cli.main`, replace the `try: result = api.lint(...)` block with:

```python
    try:
        result = api.lint(args.root, args.paths, args.exclude, not args.no_collisions, args.min_severity, args.kind,
                          changed_since=args.changed_since)
    except ValueError as e:  # bad --changed-since ref or not a git repository
        sys.stderr.write("agentlint: %s\n" % e)
        return 2
    except Exception:  # internal failure: report and exit 2
        traceback.print_exc()
        return 2
```

- [ ] **Step 7: Run the tests**

Run: `python3 -m unittest tests.test_changed_since -v && python3 -m unittest discover -s tests && AGENTLINT_YAML=builtin python3 -m unittest discover -s tests`
Expected: all PASS.

- [ ] **Step 8: Commit**

```bash
git add .claude/skills/linting-agent-config-files/scripts/agentlint_lib tests/test_changed_since.py
git commit -m "feat(agentlint): --changed-since REF scopes the run to files changed in git

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01HyFVLMJ8Mpq5xJ4Do1kMzv"
```

---

### Task 2: `markdown` and `github` output formats

**Files:**
- Modify: `.claude/skills/linting-agent-config-files/scripts/agentlint_lib/report.py`
- Modify: `.claude/skills/linting-agent-config-files/scripts/agentlint_lib/cli.py`
- Modify: `tests/test_cli.py` (`test_list_rules` stays; add nothing there)
- Test: `tests/test_report_formats.py`

**Interfaces:**
- Consumes `result["scope"]` from Task 1.
- Produces `report.to_markdown(result) -> str` (the writing-review-findings report contract) and `report.to_github(result) -> str` (one workflow command per finding plus the summary line).
- CLI: `--format markdown` valid for results; `--format github` new; `--list-rules --format markdown` unchanged.

- [ ] **Step 1: Write the failing tests**

`tests/test_report_formats.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest tests.test_report_formats -v`
Expected: `AttributeError: module 'agentlint_lib.report' has no attribute 'to_markdown'` and the CLI cases failing with exit code 2 (`--format markdown is only valid with --list-rules`).

- [ ] **Step 3: Implement the renderers in `report.py`**

Append after `to_text`:

```python
_SECTIONS = (("error", "Errors"), ("warning", "Warnings"), ("info", "Info and portability notes"))
_GH_LEVEL = {"error": "error", "warning": "warning", "info": "notice"}


def _scope_label(result: dict) -> str:
    scope = result.get("scope") or {}
    paths = ", ".join(scope.get("paths") or [])
    if scope.get("changed_since"):
        return "changed since %s" % scope["changed_since"] + (" within %s" % paths if paths else "")
    return paths or "whole repository"


def to_markdown(result: dict) -> str:
    """The writing-review-findings report contract, without the manual Why/Fix judgement lines."""
    s = result["summary"]
    lines = ["# Agent configuration review",
             "Scope: %s      Files scanned: %d      Linter: agentlint %s (%s)" % (
                 _scope_label(result), len(result["files"]), result["agentlint_version"], result["yaml_parser"]),
             "Errors: %d   Warnings: %d   Info: %d" % (s["error"], s["warning"], s["info"]), ""]
    for severity, title in _SECTIONS:
        lines.append("## " + title)
        items = [f for f in result["findings"] if f["severity"] == severity]
        if not items:
            lines += ["- none", ""]
            continue
        current = None
        for f in items:
            if f["file"] != current:
                current = f["file"]
                lines.append("### " + current)
            loc = "line %d" % f["line"] if f.get("line") else "file"
            lines.append("- [%s] %s — %s" % (f["id"], loc, f["message"]))
            tail = "  Source: %s" % f["source"]
            if f.get("suggestion"):
                tail += "  Fix: %s" % f["suggestion"]
            lines.append(tail + "  Confidence: %s" % f["confidence"])
        lines.append("")
    lines.append("## Not checked")
    lines += ["- %s" % nc for nc in result["not_checked"]] or ["- Nothing was skipped."]
    return "\n".join(lines) + "\n"


def _gh_escape(value: str, prop: bool = False) -> str:
    value = value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    if prop:
        value = value.replace(":", "%3A").replace(",", "%2C")
    return value


def to_github(result: dict) -> str:
    """GitHub Actions workflow commands: one annotation per finding, then the summary line."""
    lines = []
    for f in result["findings"]:
        props = "file=%s" % _gh_escape(f["file"], prop=True)
        if f.get("line"):
            props += ",line=%d" % f["line"]
        props += ",title=%s" % f["id"]
        lines.append("::%s %s::%s" % (_GH_LEVEL[f["severity"]], props, _gh_escape(f["message"])))
    s = result["summary"]
    lines.append("errors: %d, warnings: %d, info: %d" % (s["error"], s["warning"], s["info"]))
    return "\n".join(lines) + "\n"
```

- [ ] **Step 4: Dispatch the formats in `cli.py`**

Change the `--format` argument to `choices=["text", "json", "markdown", "github"]`. Delete the block:

```python
    if args.format == "markdown":
        sys.stderr.write("--format markdown is only valid with --list-rules\n")
        return 2
```

Replace the final `sys.stdout.write(...)` with:

```python
    renderers = {"json": report.to_json, "markdown": report.to_markdown, "github": report.to_github}
    sys.stdout.write(renderers.get(args.format, report.to_text)(result))
```

- [ ] **Step 5: Run the tests**

Run: `python3 -m unittest tests.test_report_formats tests.test_cli -v && python3 -m unittest discover -s tests && AGENTLINT_YAML=builtin python3 -m unittest discover -s tests`
Expected: all PASS.

- [ ] **Step 6: Update the linting skill's flag list and commit**

In `.claude/skills/linting-agent-config-files/SKILL.md`, under "Useful variants", replace the `--list-rules` bullet with:

```markdown
- `--changed-since origin/main` lints only configuration files changed since that git ref (plus untracked files); names still resolve against the whole repository. Use it for pull requests.
- `--format markdown` prints the findings in the report contract of `writing-review-findings` (without the manual Why and Fix judgements); `--format github` prints one GitHub Actions annotation per finding.
- `--list-rules` prints the catalogue as text; `--list-rules --format markdown` regenerates `references/rule-catalogue.md`.
```

```bash
python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py --exclude 'tests/fixtures/**'
git add .claude/skills/linting-agent-config-files tests/test_report_formats.py
git commit -m "feat(agentlint): markdown report and GitHub annotation output formats

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01HyFVLMJ8Mpq5xJ4Do1kMzv"
```

---

### Task 3: Plugin manifests for Claude Code and Copilot CLI

**Files:**
- Create: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.github/plugin/plugin.json`
- Modify: `README.md` (new section "Install as a plugin" after "Using it in Claude Code"), `docs/reference/agent-file-formats.md` (Discovery table)
- Test: `tests/test_self_review.py` (existing; add one assertion)

**Interfaces:**
- Produces plugin name `agent-reviewer`; Claude Code exposes `agent-reviewer:agent-skill-reviewer` and `/agent-reviewer:<skill>`; Copilot CLI exposes `agent-skill-reviewer` and the skills by name.

- [ ] **Step 1: Extend the self-review test**

In `tests/test_self_review.py`, add to `test_repository_lints_clean` after the `kinds` assertion:

```python
        self.assertTrue({"plugin-manifest", "marketplace-manifest"} <= kinds, kinds)
        paths = {f["path"] for f in r["files"]}
        self.assertTrue({".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", ".github/plugin/plugin.json"} <= paths)
```

Run: `python3 -m unittest tests.test_self_review -v`
Expected: FAIL on the `plugin-manifest` assertion.

- [ ] **Step 2: Write the three manifests**

`.claude-plugin/plugin.json`:

```json
{
  "name": "agent-reviewer",
  "version": "1.1.0",
  "description": "Reviews AI-agent configuration files (agents, skills, instructions, prompts, MCP, hooks, plugins) with a deterministic linter plus documented manual rules, and returns a findings report without editing anything.",
  "author": {"name": "Noel Goudiaby", "url": "https://github.com/goudiaby1224"},
  "repository": "https://github.com/goudiaby1224/agent-reviewer",
  "license": "MIT",
  "keywords": ["review", "lint", "agents", "skills", "copilot", "claude-code"],
  "agents": "./.claude/agents",
  "skills": "./.claude/skills"
}
```

`.claude-plugin/marketplace.json`:

```json
{
  "name": "agent-reviewer",
  "owner": {"name": "Noel Goudiaby", "url": "https://github.com/goudiaby1224"},
  "metadata": {"description": "Marketplace for the agent-reviewer plugin", "version": "1.0.0"},
  "plugins": [
    {
      "name": "agent-reviewer",
      "source": "./",
      "description": "Agent and skill configuration reviewer for Copilot and Claude Code",
      "version": "1.1.0"
    }
  ]
}
```

`.github/plugin/plugin.json`:

```json
{
  "name": "agent-reviewer",
  "version": "1.1.0",
  "description": "Reviews AI-agent configuration files (agents, skills, instructions, prompts, MCP, hooks, plugins) with a deterministic linter plus documented manual rules, and returns a findings report without editing anything.",
  "author": {"name": "Noel Goudiaby", "url": "https://github.com/goudiaby1224"},
  "repository": "https://github.com/goudiaby1224/agent-reviewer",
  "license": "MIT",
  "keywords": ["review", "lint", "agents", "skills"],
  "agents": ".github/agents",
  "skills": ".claude/skills"
}
```

- [ ] **Step 3: Validate with both runtimes**

```bash
python3 -m unittest tests.test_self_review -v
python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py .claude-plugin .github/plugin
claude plugin validate .
copilot plugin install ./ && copilot plugins list --kind agent && copilot plugins list --kind skill; copilot plugin uninstall agent-reviewer
```

Expected: test PASS; linter `errors: 0, warnings: 0`; `claude plugin validate` reports the manifest and marketplace valid (if it rejects `"source": "./"`, change it to `"."` and rerun; record the accepted form in the README step below); Copilot lists `agent-skill-reviewer` and the seven skills from the plugin, then uninstalls. Save the trimmed outputs to the scratchpad for the README.

- [ ] **Step 4: Document installation**

Insert into `README.md` after the "Using it in Claude Code" section:

```markdown
## Install as a plugin

The repository doubles as a plugin for both runtimes; nothing is duplicated, the manifests point at the directories above.

Copilot CLI (manifest `.github/plugin/plugin.json`):

```
copilot plugin install goudiaby1224/agent-reviewer
copilot plugins list --kind agent      # agent-skill-reviewer
copilot plugins list --kind skill      # the seven skills
```

Claude Code (manifest `.claude-plugin/plugin.json`, marketplace `.claude-plugin/marketplace.json`):

```
/plugin marketplace add goudiaby1224/agent-reviewer
/plugin install agent-reviewer@agent-reviewer
```

Inside the plugin the agent is `agent-reviewer:agent-skill-reviewer` and the skills are `/agent-reviewer:linting-agent-config-files` and so on. For local development use `claude --plugin-dir .` or `copilot plugin install ./`. A repository that already contains these files keeps its own copies; Copilot ignores the plugin's duplicates, Claude Code namespaces them.
```

Add one row to the Discovery table in `docs/reference/agent-file-formats.md`, directly after the "Copilot CLI plugin manifests" row:

```markdown
| This repository's plugin manifests | `.claude-plugin/plugin.json` points `agents` at `./.claude/agents` and `skills` at `./.claude/skills`; `.github/plugin/plugin.json` points at `.github/agents` and `.claude/skills` | no | no | yes | yes | Claude Code plugins, Copilot CLI plugins |
```

- [ ] **Step 5: Run everything and commit**

```bash
python3 -m unittest discover -s tests && AGENTLINT_YAML=builtin python3 -m unittest discover -s tests
python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py --exclude 'tests/fixtures/**'
git add .claude-plugin .github/plugin README.md docs/reference/agent-file-formats.md tests/test_self_review.py
git commit -m "feat(plugin): Claude Code and Copilot CLI plugin manifests over the existing layout

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01HyFVLMJ8Mpq5xJ4Do1kMzv"
```

---

### Task 4: PR review skill, agent bodies and skill path resolution

**Files:**
- Create: `.claude/skills/reviewing-pull-requests/SKILL.md`, `.claude/skills/reviewing-pull-requests/references/pr-comment-template.md`
- Modify: `.claude/skills/linting-agent-config-files/SKILL.md` (Procedure step 1), `.claude/skills/writing-review-findings/SKILL.md` (Procedure step 8)
- Modify: `.github/agents/agent-skill-reviewer.agent.md`, `.claude/agents/agent-skill-reviewer.md` (shared body)
- Test: `tests/test_agent_files.py` (existing loop over skill directories)

**Interfaces:**
- Consumes `--changed-since` and `--format markdown` from Tasks 1 and 2.
- Produces the skill name `reviewing-pull-requests` used by the agent body and README; the sticky-comment marker `<!-- agent-skill-reviewer -->` used by Task 5's workflow.

- [ ] **Step 1: Run the agent-file test to see it pass, then note what will fail**

Run: `python3 -m unittest tests.test_agent_files -v`
Expected: PASS now. After Step 2 creates the skill directory, `test_body_is_runtime_neutral_and_names_every_skill` FAILS until Step 4 names the skill in the body. That is the red state for this task.

- [ ] **Step 2: Write the PR skill and its template**

`.claude/skills/reviewing-pull-requests/SKILL.md`:

```markdown
---
name: reviewing-pull-requests
description: Scopes an agent-configuration review to a pull request, resolving the PR from an argument, the current branch or GitHub Actions variables, collecting its changed configuration files with gh or git, linting them with --changed-since, reviewing them with the per-kind and cross-file skills, and optionally posting the report as one sticky PR comment. Use when asked to review a pull request, when a PR number or URL is given, or when running inside a pull-request check.
metadata:
  version: "1.0.0"
  family: agent-skill-reviewer
---

# Reviewing pull requests

## Overview
A pull-request review is an ordinary review with a narrower scope: the configuration files the PR changes, plus the files they reference. The per-kind skills and `detecting-cross-file-contradictions` do the judging; this skill fixes how the scope is found, how the head revision is obtained, what the report header says, and when a comment may be posted. The linter's `--changed-since REF` flag does the file selection deterministically.

## When to use
- Asked to review a pull request, or given a PR number or URL.
- Running on a branch that has an open pull request, or inside GitHub Actions on a `pull_request` event.
- On github.com, when the Copilot cloud agent is assigned to or mentioned on a pull request.

## Procedure
1. Identify the PR. An explicit number or URL wins. Otherwise run `gh pr view --json number,baseRefName,headRefName,headRefOid` for the current branch. In GitHub Actions use `GITHUB_BASE_REF` and `GITHUB_HEAD_REF`. If nothing resolves, say so and review the whole repository instead.
2. Collect the changed files: `gh pr diff <n> --name-only`, or `git diff --name-only origin/<base>...HEAD`. Keep the agent-configuration files; count the rest and list them under "Not checked" as out of scope.
3. Review the revision that is on disk. Run `gh pr checkout <n>` only when the working tree is clean and the user asked for it; otherwise state which commit was reviewed (`git rev-parse --short HEAD`).
4. Lint with `--changed-since origin/<base> --format json` from the repository root (add `--exclude 'tests/fixtures/**'` when the repository ships broken fixtures on purpose). The linter resolves names against the whole repository even though it reports only the changed files.
5. Apply the per-kind skills and `detecting-cross-file-contradictions` to the changed files only. A finding on a file outside the PR is allowed only when that file is referenced by a changed file, and the finding must say so.
6. Write the report with `writing-review-findings`. The header reads `Scope: PR #<n> (<k> configuration files of <m> changed)`; the "Not checked" section names the out-of-scope files by count and the reviewed commit.
7. Post only when the request says to post or comment. Render the report from `references/pr-comment-template.md`, then: find an existing comment carrying `<!-- agent-skill-reviewer -->` with `gh api repos/{owner}/{repo}/issues/<n>/comments --paginate --jq '.[] | select(.body | startswith("<!-- agent-skill-reviewer -->")) | .id'`; if one exists, update it with `gh api -X PATCH repos/{owner}/{repo}/issues/comments/<id> -F body=@report.md`; otherwise `gh pr comment <n> --body-file report.md`. Never `gh pr review --approve` or `--request-changes`.
8. On github.com as the Copilot cloud agent: the pull request you were assigned to is the scope, its diff is the changed-file list, and the report is your reply; there is no separate posting step.

## Rules
This skill adds no catalogue rules; every finding comes from the per-kind and cross-file skills. Its own rules are about procedure:
- The scope is the PR's configuration files plus the files they reference; nothing else is reviewed.
- A finding on a file outside the PR names the changed file that references it.
- Nothing is posted unless the request says to post or comment, and then exactly one comment is kept per PR.
- The reviewer never approves, requests changes or merges.
- When `gh` is missing or not authenticated, say so under "Not checked", fall back to `git diff` for the scope, and skip posting.

## Common false positives
- XF001 or XF002 on twins where only one copy is in the PR: report on the changed copy and name the other.
- IN007 on an `@import` whose target is added in the same PR but not yet on disk because the head was not checked out: say which commit was reviewed.
- Findings on generated files such as `references/rule-catalogue.md`: keep them, note the generator.

## References
- `references/pr-comment-template.md` — the sticky comment skeleton.
- Load `linting-agent-config-files` for `--changed-since` and the output formats; load `writing-review-findings` for the report contract.
```

`.claude/skills/reviewing-pull-requests/references/pr-comment-template.md`:

```markdown
# Sticky PR comment template

The first line is the marker the reviewer and the workflow search for; keep it exactly.

```
<!-- agent-skill-reviewer -->
## Agent configuration review
Scope: PR #<n> (<k> configuration files of <m> changed)   Commit: <short sha>   Linter: agentlint <version> (<parser>)
Errors: <e>   Warnings: <w>   Info: <i>

<details><summary>Errors (<e>)</summary>

### <file>
- [ID] line N — message
  Why: ...  Source: <url>
  Fix: ...  Confidence: high

</details>
<details><summary>Warnings (<w>)</summary>

...

</details>
<details><summary>Info and portability notes (<i>)</summary>

...

</details>

**Not checked**
- <out-of-scope file count> changed files outside the agent-configuration set
- <anything else skipped>

<sub>Posted by agent-skill-reviewer; one comment per pull request, updated on each run.</sub>
```

Empty sections say `- none` inside the details block. The workflow (`.github/workflows/agent-config-review.yml`) posts the linter's `--format markdown` output under the same marker, without the Why and Fix lines.
```

- [ ] **Step 3: Point the linting skill at its own directory**

In `.claude/skills/linting-agent-config-files/SKILL.md`, replace Procedure step 1:

```markdown
1. From the repository root run the linter that ships with this skill:
   `python3 <skill-dir>/scripts/agentlint.py --format json [PATH ...]`
   where `<skill-dir>` is the directory this SKILL.md was loaded from: `${CLAUDE_SKILL_DIR}` in Claude Code, the path the skill was read from in Copilot, and `.claude/skills/linting-agent-config-files` in a plain clone of this repository. Pass `--root .` when the linter lives outside the repository (installed as a plugin). With no PATH the linter discovers every configuration file under the root. Add `--exclude 'tests/fixtures/**'` for repositories that ship broken fixtures on purpose.
```

- [ ] **Step 4: Update the shared agent body**

Apply to both agent files with one script so the bodies stay identical:

```python
import re
for p in (".github/agents/agent-skill-reviewer.agent.md", ".claude/agents/agent-skill-reviewer.md"):
    s = open(p).read()
    old_step = ("Load the skill `linting-agent-config-files`. From the repository root run\n"
                "`python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py --format json <scope>`.\n")
    new_step = ("Load the skill `linting-agent-config-files` and run the linter the way it describes, from the repository root, "
                "with `--format json` and the scope as PATH arguments (or `--changed-since` for a pull request).\n")
    assert old_step in s, p
    s = s.replace(old_step, new_step)
    old_scope_end = "- In a pull-request context: changed configuration files first, then every file they reference (skills a subagent preloads, agents a prompt targets, imports in CLAUDE.md).\n"
    new_scope_end = old_scope_end + """
## Pull request mode
When asked to review a pull request, or when you are running on one (a PR number or URL was given, the current branch has an open pull request, or `GITHUB_BASE_REF` is set), load `reviewing-pull-requests` and follow it: the scope is the PR's changed configuration files plus the files they reference, the report header says `Scope: PR #N`, and nothing is posted to the PR unless the request says to post or comment.
"""
    assert old_scope_end in s, p
    s = s.replace(old_scope_end, new_scope_end)
    open(p, "w").write(s)
```

- [ ] **Step 5: Add the PR header variant to `writing-review-findings`**

In `.claude/skills/writing-review-findings/SKILL.md`, replace Procedure step 8 with:

```markdown
8. Fill the header: scope, number of files scanned, linter version and YAML parser (or `manual fallback`), and the three counts. The counts must equal the number of bullets in each section. For a pull request the scope reads `PR #N (<k> configuration files of <m> changed)` and "Not checked" names the reviewed commit.
```

- [ ] **Step 6: Run the tests and lint**

```bash
python3 -m unittest tests.test_agent_files tests.test_self_review -v
python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py .claude/skills .github/agents .claude/agents
python3 -m unittest discover -s tests && AGENTLINT_YAML=builtin python3 -m unittest discover -s tests
```

Expected: PASS; skills lint `errors: 0, warnings: 0` (SK007 must not fire: `references/pr-comment-template.md` exists); the body test finds `reviewing-pull-requests` in the body.

- [ ] **Step 7: Commit**

```bash
git add .claude/skills .github/agents .claude/agents
git commit -m "feat(skills): reviewing-pull-requests skill, PR mode in the agent body, linter path via the skill directory

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01HyFVLMJ8Mpq5xJ4Do1kMzv"
```

---

### Task 5: GitHub Actions PR check and documentation

**Files:**
- Create: `.github/workflows/agent-config-review.yml`
- Modify: `README.md` (new section "Reviewing a pull request", note in "Copying into another repository"), `docs/superpowers/plans/2026-09-03-agent-skill-reviewer.md` (pointer under "Spec deltas")

**Interfaces:**
- Consumes `--changed-since`, `--format markdown`, `--format github` (Tasks 1 and 2) and the marker `<!-- agent-skill-reviewer -->` (Task 4).

- [ ] **Step 1: Write the workflow**

`.github/workflows/agent-config-review.yml`:

```yaml
name: Agent configuration review

on:
  pull_request:
    paths:
      - ".github/agents/**"
      - ".github/instructions/**"
      - ".github/prompts/**"
      - ".github/copilot-instructions.md"
      - ".github/mcp.json"
      - ".github/plugin/**"
      - ".github/workflows/copilot-setup-steps.yml"
      - ".claude/**"
      - ".claude-plugin/**"
      - ".cursor/rules/**"
      - ".vscode/mcp.json"
      - ".mcp.json"
      - "**/SKILL.md"
      - "**/*.agent.md"
      - "**/*.chatmode.md"
      - "**/*.instructions.md"
      - "**/*.prompt.md"
      - "**/AGENTS.md"
      - "**/AGENT.md"
      - "**/CLAUDE.md"

permissions:
  contents: read
  pull-requests: write

jobs:
  agentlint:
    runs-on: ubuntu-latest
    env:
      # Set the repository variable AGENTLINT_PR_COMMENT to "true" to post a sticky comment with the report.
      POST_COMMENT: ${{ vars.AGENTLINT_PR_COMMENT }}
      LOCAL_LINTER: .claude/skills/linting-agent-config-files/scripts/agentlint.py
      PLUGIN_REPO: https://github.com/goudiaby1224/agent-reviewer
      PLUGIN_REF: main
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Locate the linter
        run: |
          if [ -f "$LOCAL_LINTER" ]; then
            echo "LINTER=$LOCAL_LINTER" >> "$GITHUB_ENV"
          else
            git clone --depth 1 --branch "$PLUGIN_REF" "$PLUGIN_REPO" /tmp/agent-reviewer
            echo "LINTER=/tmp/agent-reviewer/$LOCAL_LINTER" >> "$GITHUB_ENV"
          fi
      - name: Report (job summary)
        run: |
          python3 "$LINTER" --root . --changed-since "origin/${{ github.base_ref }}" --exclude 'tests/fixtures/**' \
            --format markdown > agentlint-report.md || true
          cat agentlint-report.md >> "$GITHUB_STEP_SUMMARY"
      - name: Annotate and gate
        run: |
          python3 "$LINTER" --root . --changed-since "origin/${{ github.base_ref }}" --exclude 'tests/fixtures/**' --format github
      - name: Post sticky comment
        if: ${{ always() && env.POST_COMMENT == 'true' }}
        env:
          GH_TOKEN: ${{ github.token }}
          PR: ${{ github.event.pull_request.number }}
        run: |
          { echo "<!-- agent-skill-reviewer -->"; cat agentlint-report.md; } > comment.md
          id=$(gh api "repos/${{ github.repository }}/issues/$PR/comments" --paginate \
                --jq '.[] | select(.body | startswith("<!-- agent-skill-reviewer -->")) | .id' | head -n1)
          if [ -n "$id" ]; then
            gh api -X PATCH "repos/${{ github.repository }}/issues/comments/$id" -F body=@comment.md > /dev/null
          else
            gh pr comment "$PR" --body-file comment.md
          fi
```

- [ ] **Step 2: Dry-run the workflow steps locally**

From the repository root on a scratch branch:

```bash
git checkout -b wf-dryrun
printf -- '---\nname: wf-check\ndescription: d\ntools: Read\nskills:\n  - ghost\n---\nbody\n' > .claude/agents/wf-check.md
python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py --root . --changed-since main --exclude 'tests/fixtures/**' --format markdown
python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py --root . --changed-since main --exclude 'tests/fixtures/**' --format github; echo "exit=$?"
rm .claude/agents/wf-check.md && git checkout main && git branch -D wf-dryrun
```

Expected: the markdown report lists `.claude/agents/wf-check.md` under Errors with `XF003` (ghost skill), the github run prints `::error file=.claude/agents/wf-check.md,line=5,title=XF003::...` and exits 1. The workflow file itself is not an agent-configuration file, so the linter ignores it.

- [ ] **Step 3: Document pull-request review**

Insert into `README.md` after "Install as a plugin":

```markdown
## Reviewing a pull request

- Claude Code: `Use the agent-skill-reviewer subagent to review pull request 42` (a URL works too), or just ask for a review on a branch that has an open PR. Add `and post the report as a comment` to have it post; it keeps one sticky comment per PR and never approves or requests changes.
- github.com: assign `agent-skill-reviewer` to the pull request; the report is its reply.
- GitHub Actions: `.github/workflows/agent-config-review.yml` runs the linter with `--changed-since origin/<base>` on every PR that touches agent-configuration files, writes the report to the job summary, annotates the diff, and fails on errors (warnings do not fail it). Set the repository variable `AGENTLINT_PR_COMMENT` to `true` to also post the report as a sticky comment.
- Any shell: `python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py --changed-since origin/main --format markdown`.
```

In "Copying into another repository" append:

```markdown
Copy `.github/workflows/agent-config-review.yml` as well; it uses the repository's own linter when present and otherwise clones this repository at `PLUGIN_REF` to borrow it.
```

Append to the 2026-09-03 plan's "Spec deltas" section:

```markdown
- Plugin packaging and pull-request review are specified in `docs/superpowers/specs/2026-09-14-plugin-packaging-and-pr-review-design.md` and planned in `docs/superpowers/plans/2026-09-17-plugin-packaging-and-pr-review.md`.
```

- [ ] **Step 4: Run everything and commit**

```bash
python3 -m unittest discover -s tests && AGENTLINT_YAML=builtin python3 -m unittest discover -s tests
python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py --exclude 'tests/fixtures/**'
git add .github/workflows/agent-config-review.yml README.md docs/superpowers/plans/2026-09-03-agent-skill-reviewer.md
git commit -m "ci: agent configuration review workflow for pull requests, with PR review docs

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01HyFVLMJ8Mpq5xJ4Do1kMzv"
```

---

### Task 6: Verify the plugin in both runtimes and record the results

**Files:**
- Modify: `README.md` ("Verification log")
- Modify: `.claude/agents/agent-skill-reviewer.md` only if the fallback in spec section 4.1 is needed

**Interfaces:**
- Consumes everything above. Produces the verification log entries and the answer to the open question about bare `skills:` names inside a Claude plugin.

- [ ] **Step 1: Claude Code plugin run**

```bash
SP=/private/tmp/claude-501/-Users-noelgoudiaby-SKILL-AND-AGENT-BUILDER/61d88dfd-49fc-4825-920d-81a26d26d3ca/scratchpad
env -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT claude --plugin-dir . --debug -p \
  "Use the agent-reviewer:agent-skill-reviewer subagent to review tests/fixtures/good and return its report. Before the report, state which skills were preloaded into it." \
  --allowedTools "Agent,Read,Grep,Glob,Bash(python3:*)" --output-format text > $SP/plugin-green.txt 2> $SP/plugin-green.err; echo "exit=$?"
grep -iE "skill|preload|not found|agent-reviewer" $SP/plugin-green.err | head -20
head -60 $SP/plugin-green.txt
```

Expected: the reply cites rule IDs (`AG012`, `XF002` on the good fixture) and names `linting-agent-config-files` and `writing-review-findings` as preloaded. If the debug log shows the preload failing to resolve the bare names, apply the spec's fallback: remove the `skills:` block from `.claude/agents/agent-skill-reviewer.md`, rerun `python3 -m unittest tests.test_agent_files`, and record the change. If the account usage limit interrupts the run, record the limit message and the exact command, as the earlier log does.

- [ ] **Step 2: Copilot CLI plugin run**

```bash
copilot plugin install ./ && copilot plugins list --kind agent | tee $SP/plugin-copilot.txt && copilot plugins list --kind skill | tee -a $SP/plugin-copilot.txt
copilot -p "Using the agent-skill-reviewer agent, review tests/fixtures/good and return the report." --agent agent-skill-reviewer --allow-all-tools 2>&1 | tail -40 | tee -a $SP/plugin-copilot.txt
copilot plugin uninstall agent-reviewer
```

Expected: the agent and seven skills listed with the plugin as their source; the review cites `AG012` and `XF002`.

- [ ] **Step 3: Record both runs in the README**

Add under "Verification log", after the existing entries:

```markdown
### Plugin installs (2026-09-17)

- Claude Code 2.1.260, `claude --plugin-dir . -p ...`: <one line: skills preloaded yes/no, rule IDs cited, or the limit message>.
- Copilot CLI 1.0.80, `copilot plugin install ./`: <one line: agent and skills listed, review outcome>.
```

Replace the angle-bracket placeholders with what actually happened; do not paraphrase a failure as a pass.

- [ ] **Step 4: Final run, commit, push**

```bash
python3 -m unittest discover -s tests && AGENTLINT_YAML=builtin python3 -m unittest discover -s tests
python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py --exclude 'tests/fixtures/**'
git add README.md .claude/agents
git commit -m "docs: plugin verification log for Claude Code and Copilot CLI

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01HyFVLMJ8Mpq5xJ4Do1kMzv"
git push origin main
```

The push goes to the remote the user configured on 2026-09-04; the workflow then runs on the next pull request.
