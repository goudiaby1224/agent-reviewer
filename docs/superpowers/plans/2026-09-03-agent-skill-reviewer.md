# agent-skill-reviewer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a read-only reviewer agent (Copilot custom agent + Claude Code subagent twin) and seven skills, backed by a deterministic Python linter, that find syntax errors, spec violations, contradictions and bugs in agent-configuration files.

**Architecture:** One skills tree in `.claude/skills/` is read natively by GitHub Copilot (cloud agent, CLI, VS Code) and Claude Code. The `linting-agent-config-files` skill ships `scripts/agentlint.py`, a stdlib-only CLI (PyYAML optional) organised as a small package `agentlint_lib/` next to it: discovery → per-kind rule modules → cross-file rules → JSON/text report. The six other skills carry the manual (semantic) rules and spec digests the model applies on top of the linter output. Two agent files with identical bodies wire it together; a prompt file adds a `/review-agent-config` shortcut.

**Tech Stack:** Python ≥ 3.8 standard library (`argparse`, `json`, `re`, `os`, `subprocess`, `unittest`), optional PyYAML; Markdown/YAML for agents and skills; git.

**Spec:** `docs/superpowers/specs/2026-09-03-agent-skill-reviewer-design.md`

## Global Constraints

- Python floor: 3.8 (no `match`, no `list[str]` generics at runtime, no `dataclass(slots=True)`); type hints via `typing`.
- No third-party imports except an optional `import yaml` guarded by `try/except ImportError` and the env var `AGENTLINT_YAML=builtin` forcing the fallback parser.
- No network access anywhere in the linter or skills.
- Agent name everywhere: `agent-skill-reviewer`. Skill names (= directory names): `linting-agent-config-files`, `reviewing-agent-definitions`, `reviewing-skill-files`, `reviewing-instruction-files`, `reviewing-mcp-and-hooks-config`, `detecting-cross-file-contradictions`, `writing-review-findings`.
- Every `SKILL.md`: `name` equals its directory, `description` ≤ 1024 chars, third person, no workflow summary; body ≤ 500 lines; frontmatter keys limited to `name`, `description`, `metadata`.
- Copilot agent body ≤ 30,000 characters; both agent bodies byte-identical below the frontmatter.
- Rule IDs are `<FAMILY><3 digits>`, families `GN`, `AG`, `SK`, `IN`, `CF`, `XF`; every rule has a severity (`error`|`warning`|`info`), a tag (`auto`|`manual`), a runtime (`copilot`|`claude`|`both`|`generic`) and a source URL. Rule IDs, once committed, are never renumbered.
- Linter exit codes: 0 no error-level findings, 1 at least one error, 2 usage/internal failure.
- All paths in findings are root-relative POSIX strings.
- Commit after every task with the message given in the task; commits end with the two trailer lines shown in Task 1.
- Run tests with `python3 -m unittest discover -s tests -v` from the repository root.

---

## File structure

| Path | Responsibility |
|---|---|
| `.claude/skills/linting-agent-config-files/scripts/agentlint.py` | Entrypoint; puts its own directory on `sys.path`, calls `agentlint_lib.cli.main()` |
| `.claude/skills/linting-agent-config-files/scripts/agentlint_lib/__init__.py` | `__version__ = "1.0.0"` |
| `.../agentlint_lib/model.py` | `Rule`, `RULES` registry + `rule()`, `Finding`, `ConfigFile`, `Context` |
| `.../agentlint_lib/catalogue.py` | `SRC` URL table and every `rule(...)` registration (auto and manual) — single source of truth |
| `.../agentlint_lib/yamlfm.py` | `split_frontmatter()`, `parse_yaml()`, `PARSER_NAME`, builtin YAML-subset parser |
| `.../agentlint_lib/discover.py` | `detect_kind()`, `discover()`, glob matching, file loading |
| `.../agentlint_lib/toolnames.py` | Copilot tool aliases, Claude tool names, validators |
| `.../agentlint_lib/rules_gn.py` | GN: BOM, CRLF, encoding, unreadable |
| `.../agentlint_lib/rules_ag.py` | AG: Copilot agents, Claude subagents, chatmodes |
| `.../agentlint_lib/rules_sk.py` | SK: SKILL.md |
| `.../agentlint_lib/rules_in.py` | IN: instructions, prompts, AGENTS.md, CLAUDE.md, rules, commands, cursor |
| `.../agentlint_lib/rules_cf.py` | CF: MCP, hooks, setup-steps, plugin/marketplace manifests; exports `check_hooks_object()` |
| `.../agentlint_lib/rules_xf.py` | XF: cross-file collisions and dangling references |
| `.../agentlint_lib/api.py` | `lint(root, paths, excludes, collisions, min_severity, force_kind) -> dict` |
| `.../agentlint_lib/report.py` | `to_json()`, `to_text()`, `catalogue_markdown()` |
| `.../agentlint_lib/cli.py` | argparse, exit codes |
| `.claude/skills/linting-agent-config-files/SKILL.md` + `references/rule-catalogue.md` | How to run and read the linter; generated catalogue |
| `.claude/skills/reviewing-agent-definitions/SKILL.md` + `references/*.md` | Manual AG rules and per-runtime field tables |
| `.claude/skills/reviewing-skill-files/SKILL.md` + `references/*.md` | Manual SK rules and spec digest |
| `.claude/skills/reviewing-instruction-files/SKILL.md` + `references/*.md` | Manual IN rules and format digest |
| `.claude/skills/reviewing-mcp-and-hooks-config/SKILL.md` + `references/*.md` | Manual CF rules and format digest |
| `.claude/skills/detecting-cross-file-contradictions/SKILL.md` | Manual XF rules |
| `.claude/skills/writing-review-findings/SKILL.md` + `references/report-template.md` | Report contract |
| `.github/agents/agent-skill-reviewer.agent.md` | Copilot agent |
| `.claude/agents/agent-skill-reviewer.md` | Claude Code twin |
| `.github/prompts/review-agent-config.prompt.md` | Prompt shortcut |
| `docs/reference/agent-file-formats.md` | Verified format reference (built from official sources in Task 0) |
| `tests/fixtures/good/**`, `tests/fixtures/bad/**` | Fixture mini-repos |
| `tests/helpers.py` | `run_lint()` helper used by every test module |
| `tests/test_yamlfm.py`, `tests/test_discover.py`, `tests/test_rules_*.py`, `tests/test_good_fixture.py`, `tests/test_catalogue_sync.py`, `tests/test_agent_files.py`, `tests/test_self_review.py` | Unit and integration tests |
| `README.md` | Usage in each runtime, copying into other repos, verification log |

---

### Task 0: Build the verified format reference

**Files:**
- Create: `docs/reference/agent-file-formats.md`

**Interfaces:**
- Produces: the section headings later tasks copy tables from (`## Discovery locations`, one `## <file kind>` section per kind, `## Cross-tool compatibility matrix`, `## Deprecated`, `## Unresolved questions`, `## Sources`).

- [ ] **Step 1: Build the reference from the official sources**

The scratchpad copy from the research pass no longer exists (verified 2026-09-03). Rebuild `docs/reference/agent-file-formats.md` directly from the pages listed in the spec §12 (the same URLs appear as `catalogue.SRC` in Task 2). For each file kind, fetch the page and record: discovery locations, required and optional frontmatter/JSON keys with types and allowed values, documented limits, deprecated forms, and the fetch date. Write the six sections listed under Interfaces. Every claim carries its source URL inline. If a page cannot be fetched, write `UNVERIFIED (<url>)` next to the claim rather than guessing; those items are also listed under `## Unresolved questions`.

This file is the only place the format facts live in prose; Task 10 copies its tables into each skill's `references/` folder.

- [ ] **Step 2: Sanity-check the headings exist**

```bash
grep -n '^## ' docs/reference/agent-file-formats.md
```
Expected: at least the six headings above plus one section per file kind (Copilot agent, SKILL.md, copilot-instructions, instructions.md, prompt.md, AGENTS.md, Claude subagent, Claude SKILL.md, CLAUDE.md/rules, hooks, .mcp.json, .vscode/mcp.json, cloud-agent MCP, copilot-setup-steps, plugin.json).

- [ ] **Step 3: Commit**

```bash
git add docs/reference/agent-file-formats.md
git commit -m "docs: add verified agent/skill file format reference

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_016TZTeGdK9WuTukJpPzZFxY"
```

---

### Task 1: Linter scaffold, data model, and YAML front-matter parser

**Files:**
- Create: `.claude/skills/linting-agent-config-files/scripts/agentlint.py`
- Create: `.claude/skills/linting-agent-config-files/scripts/agentlint_lib/__init__.py`
- Create: `.claude/skills/linting-agent-config-files/scripts/agentlint_lib/model.py`
- Create: `.claude/skills/linting-agent-config-files/scripts/agentlint_lib/yamlfm.py`
- Create: `tests/__init__.py` (empty), `tests/helpers.py`, `tests/test_yamlfm.py`

**Interfaces:**
- Produces `model.Rule(id, severity, tag, family, runtime, title, source)`, `model.RULES: Dict[str, Rule]`, `model.rule(...)`, `model.Finding(id, file, message, line=None, ...)`, `model.ConfigFile`, `model.Context`.
- Produces `yamlfm.split_frontmatter(text) -> (fm_text|None, body, body_start_line, error|None)`, `yamlfm.parse_yaml(text) -> (obj, error|None)`, `yamlfm.parser_name() -> "pyyaml"|"builtin"`.
- Produces `tests/helpers.py: SCRIPTS_DIR`, `import_lib()`.

- [ ] **Step 1: Write the failing tests**

`tests/__init__.py` is empty. `tests/helpers.py`:

```python
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(REPO_ROOT, ".claude", "skills", "linting-agent-config-files", "scripts")
FIXTURES = os.path.join(REPO_ROOT, "tests", "fixtures")
GOOD = os.path.join(FIXTURES, "good")
BAD = os.path.join(FIXTURES, "bad")


def import_lib():
    """Put the scripts dir on sys.path and return the agentlint_lib package."""
    if SCRIPTS_DIR not in sys.path:
        sys.path.insert(0, SCRIPTS_DIR)
    import agentlint_lib  # noqa: E402
    return agentlint_lib


def run_lint(paths=None, root=None, excludes=None, collisions=True, force_kind=None):
    """Run the linter in-process and return the result dict (same shape as --format json)."""
    import_lib()
    from agentlint_lib import api
    return api.lint(root=root or FIXTURES, paths=paths or [], excludes=excludes or [],
                    collisions=collisions, min_severity="info", force_kind=force_kind)


def ids(result, file=None):
    """Set of (rule id, file) pairs, optionally filtered to one file."""
    return {(f["id"], f["file"]) for f in result["findings"] if file is None or f["file"] == file}
```

`tests/test_yamlfm.py`:

```python
import os
import unittest
from unittest import mock

from tests.helpers import import_lib

lib = import_lib()
from agentlint_lib import yamlfm  # noqa: E402


class SplitFrontmatterTests(unittest.TestCase):
    def test_no_frontmatter(self):
        fm, body, line, err = yamlfm.split_frontmatter("# Title\nbody\n")
        self.assertIsNone(fm)
        self.assertEqual(body, "# Title\nbody\n")
        self.assertEqual(line, 1)
        self.assertIsNone(err)

    def test_basic_frontmatter(self):
        fm, body, line, err = yamlfm.split_frontmatter("---\nname: x\n---\n# T\n")
        self.assertEqual(fm, "name: x")
        self.assertEqual(body, "# T\n")
        self.assertEqual(line, 4)
        self.assertIsNone(err)

    def test_unterminated(self):
        fm, body, line, err = yamlfm.split_frontmatter("---\nname: x\nbody")
        self.assertIn("unterminated", err)


class BuiltinParserTests(unittest.TestCase):
    def setUp(self):
        self.env = mock.patch.dict(os.environ, {"AGENTLINT_YAML": "builtin"})
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_parser_name(self):
        self.assertEqual(yamlfm.parser_name(), "builtin")

    def test_scalars_and_types(self):
        obj, err = yamlfm.parse_yaml(
            'name: my-skill\ndescription: "Use when: x"\ncount: 3\nratio: 1.5\nflag: true\nnothing: ~\nquoted: \'it\'\'s\'\n')
        self.assertIsNone(err)
        self.assertEqual(obj, {"name": "my-skill", "description": "Use when: x", "count": 3,
                               "ratio": 1.5, "flag": True, "nothing": None, "quoted": "it's"})

    def test_flow_and_block_lists(self):
        obj, err = yamlfm.parse_yaml("tools: ['read', \"edit\", search]\nskills:\n  - a\n  - b\n")
        self.assertIsNone(err)
        self.assertEqual(obj, {"tools": ["read", "edit", "search"], "skills": ["a", "b"]})

    def test_nested_maps_and_list_of_maps(self):
        text = ("handoffs:\n  - label: Fix\n    agent: agent\n    send: false\n"
                "metadata:\n  version: \"1.0\"\n  family: x\n")
        obj, err = yamlfm.parse_yaml(text)
        self.assertIsNone(err)
        self.assertEqual(obj["handoffs"], [{"label": "Fix", "agent": "agent", "send": False}])
        self.assertEqual(obj["metadata"], {"version": "1.0", "family": "x"})

    def test_block_scalar_and_continuation(self):
        text = "description: |\n  line one\n  line two\nother: first\n  continued\n"
        obj, err = yamlfm.parse_yaml(text)
        self.assertIsNone(err)
        self.assertEqual(obj["description"], "line one\nline two\n")
        self.assertEqual(obj["other"], "first continued")

    def test_comments_and_hash_in_quotes(self):
        obj, err = yamlfm.parse_yaml("# top\nname: a # trailing\ntitle: \"a # b\"\n")
        self.assertIsNone(err)
        self.assertEqual(obj, {"name": "a", "title": "a # b"})

    def test_tab_indentation_is_error(self):
        obj, err = yamlfm.parse_yaml("a:\n\tb: 1\n")
        self.assertIsNone(obj)
        self.assertIn("tab", err)

    def test_unquoted_colon_space_in_value_is_error(self):
        # "key: a: b" is ambiguous in YAML; PyYAML raises, the builtin parser must too
        obj, err = yamlfm.parse_yaml("description: Use when: something\n")
        self.assertIsNone(obj)
        self.assertIsNotNone(err)

    def test_empty_document(self):
        obj, err = yamlfm.parse_yaml("\n# nothing\n")
        self.assertIsNone(err)
        self.assertIsNone(obj)


class PyYAMLParityTests(unittest.TestCase):
    """When PyYAML is installed, both parsers must agree on the frontmatter shapes used in this repo."""

    SAMPLES = [
        "name: x\ndescription: y\n",
        "tools: ['read', 'search']\nmodel: inherit\n",
        "handoffs:\n  - label: A\n    agent: agent\n    prompt: Do it\n    send: false\n",
        "metadata:\n  version: \"1.0.0\"\n",
        "description: >\n  folded\n  text\n",
    ]

    def test_parity(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")
        for s in self.SAMPLES:
            with mock.patch.dict(os.environ, {"AGENTLINT_YAML": "builtin"}):
                builtin, err = yamlfm.parse_yaml(s)
            self.assertIsNone(err, s)
            self.assertEqual(builtin, yaml.safe_load(s), s)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest tests.test_yamlfm -v`
Expected: FAIL / ERROR with `ModuleNotFoundError: No module named 'agentlint_lib'`.

- [ ] **Step 3: Write the entrypoint, package init and model**

`.claude/skills/linting-agent-config-files/scripts/agentlint.py` (make it executable with `chmod +x`):

```python
#!/usr/bin/env python3
"""agentlint — deterministic linter for AI agent configuration files.

Usage: python3 agentlint.py [PATH ...] [--root DIR] [--format json|text] [--kind KIND]
                            [--exclude GLOB]... [--no-collisions] [--min-severity LEVEL] [--list-rules]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentlint_lib.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

`agentlint_lib/__init__.py`:

```python
__version__ = "1.0.0"
```

`agentlint_lib/model.py`:

```python
"""Data model shared by every agentlint module."""
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

SEVERITIES = ("error", "warning", "info")
SEVERITY_RANK = {"error": 0, "warning": 1, "info": 2}
TAGS = ("auto", "manual")
RUNTIMES = ("copilot", "claude", "both", "generic")


@dataclass(frozen=True)
class Rule:
    id: str
    severity: str
    tag: str
    family: str
    runtime: str
    title: str
    source: str


RULES: Dict[str, Rule] = {}


def rule(id: str, severity: str, tag: str, family: str, runtime: str, title: str, source: str) -> Rule:
    """Register a rule. Duplicate ids and bad enum values are programming errors."""
    if id in RULES:
        raise ValueError("duplicate rule id %s" % id)
    if severity not in SEVERITIES or tag not in TAGS or runtime not in RUNTIMES:
        raise ValueError("bad rule definition %s" % id)
    if not id.startswith(family) or len(id) != len(family) + 3 or not id[len(family):].isdigit():
        raise ValueError("rule id %s does not match family %s" % (id, family))
    r = Rule(id, severity, tag, family, runtime, title, source)
    RULES[id] = r
    return r


@dataclass
class Finding:
    id: str
    file: str
    message: str
    line: Optional[int] = None
    severity: str = ""
    runtime: str = ""
    source: str = ""
    confidence: str = "high"
    autofix_safe: bool = False
    suggestion: str = ""

    def __post_init__(self):
        r = RULES.get(self.id)
        if r is None:
            raise KeyError("unknown rule id %s" % self.id)
        if r.tag != "auto":
            raise ValueError("manual rule %s cannot be emitted by the linter" % self.id)
        self.severity = self.severity or r.severity
        self.runtime = self.runtime or r.runtime
        self.source = self.source or r.source

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["title"] = RULES[self.id].title
        return d


@dataclass
class ConfigFile:
    path: str                      # root-relative POSIX path
    abs_path: str
    kind: str
    text: Optional[str] = None     # None when unreadable or binary
    body: str = ""
    frontmatter: Optional[Any] = None
    fm_present: bool = False
    fm_text: str = ""
    fm_error: Optional[str] = None
    body_line: int = 1             # 1-based line where the body starts
    data: Any = None               # parsed JSON/YAML for config kinds
    data_error: Optional[str] = None
    read_error: Optional[str] = None
    bom: bool = False
    crlf: bool = False

    @property
    def fm(self) -> Dict[str, Any]:
        """Frontmatter as a dict (empty when absent or not a mapping)."""
        return self.frontmatter if isinstance(self.frontmatter, dict) else {}

    @property
    def name(self) -> str:
        return os.path.basename(self.path)

    @property
    def dirname(self) -> str:
        return os.path.dirname(self.path)

    def key_line(self, key: str) -> Optional[int]:
        """1-based line of a top-level frontmatter key, or None."""
        if not self.fm_present:
            return None
        for i, ln in enumerate(self.fm_text.split("\n"), start=2):
            stripped = ln.lstrip()
            if ln == stripped and (stripped.startswith(key + ":") or stripped.startswith('"%s":' % key)
                                   or stripped.startswith("'%s':" % key)):
                return i
        return None

    def body_lines(self) -> int:
        return 0 if not self.body.strip() else self.body.count("\n") + (0 if self.body.endswith("\n") else 1)


@dataclass
class Context:
    root: str
    files: List[ConfigFile] = field(default_factory=list)
    yaml_parser: str = "pyyaml"
    not_checked: List[str] = field(default_factory=list)

    def exists(self, relpath: str) -> bool:
        return os.path.exists(os.path.join(self.root, relpath))

    def by_kind(self, *kinds: str) -> List[ConfigFile]:
        return [f for f in self.files if f.kind in kinds]
```

- [ ] **Step 4: Write the YAML front-matter module**

`agentlint_lib/yamlfm.py`:

```python
"""Front-matter splitting and YAML parsing with a stdlib fallback.

PyYAML is used when importable unless AGENTLINT_YAML=builtin. The builtin parser
covers the YAML subset found in agent/skill frontmatter: block and flow mappings
and sequences, quoted/plain scalars with continuation lines, block scalars (| >),
comments, booleans (YAML 1.1 set, matching PyYAML), ints, floats and nulls.
"""
import os
import re
from typing import Any, List, Optional, Tuple


class YAMLError(Exception):
    pass


def _use_pyyaml() -> bool:
    if os.environ.get("AGENTLINT_YAML", "").lower() == "builtin":
        return False
    try:
        import yaml  # noqa: F401
        return True
    except ImportError:
        return False


def parser_name() -> str:
    return "pyyaml" if _use_pyyaml() else "builtin"


def split_frontmatter(text: str) -> Tuple[Optional[str], str, int, Optional[str]]:
    """Return (frontmatter_text, body, body_start_line, error).

    Frontmatter must start on line 1 with '---' and end with '---' or '...'.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text, 1, None
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:]), i + 2, None
    return "\n".join(lines[1:]), "", len(lines) + 1, "unterminated frontmatter (no closing ---)"


def parse_yaml(text: str) -> Tuple[Any, Optional[str]]:
    if _use_pyyaml():
        import yaml
        try:
            return yaml.safe_load(text), None
        except yaml.YAMLError as e:  # pragma: no cover - depends on PyYAML
            return None, "invalid YAML: %s" % str(e).split("\n")[0]
    return builtin_load(text)


# ---------------------------------------------------------------- builtin parser

_BOOL_TRUE = {"true", "yes", "on"}
_BOOL_FALSE = {"false", "no", "off"}
_NULLS = {"", "~", "null"}
_INT_RE = re.compile(r"^[-+]?(0|[1-9][0-9_]*)$")
_FLOAT_RE = re.compile(r"^[-+]?([0-9][0-9_]*)?\.[0-9]*([eE][-+]?[0-9]+)?$|^[-+]?[0-9][0-9_]*[eE][-+]?[0-9]+$")


def builtin_load(text: str) -> Tuple[Any, Optional[str]]:
    p = _Parser(text.split("\n"))
    try:
        p.skip_blank()
        if p.eof():
            return None, None
        val = p.parse_node(p.indent())
        p.skip_blank()
        if not p.eof():
            raise YAMLError("unexpected content at line %d" % (p.i + 1))
        return val, None
    except YAMLError as e:
        return None, "invalid YAML (builtin parser): %s" % e


def _strip_comment(line: str) -> str:
    """Remove a trailing ' #...' comment that is outside quotes; a leading '#' is a full comment."""
    if line.lstrip().startswith("#"):
        return ""
    out, quote, prev = [], None, ""
    for ch in line:
        if quote:
            out.append(ch)
            if ch == quote and prev != "\\":
                quote = None
        elif ch in ("'", '"'):
            quote = ch
            out.append(ch)
        elif ch == "#" and (prev == " " or prev == "\t"):
            break
        else:
            out.append(ch)
        prev = ch
    return "".join(out).rstrip()


def _unquote(s: str, line_no: int) -> str:
    q = s[0]
    if len(s) < 2 or s[-1] != q:
        raise YAMLError("unterminated quoted string at line %d" % line_no)
    inner = s[1:-1]
    if q == "'":
        return inner.replace("''", "'")
    return (inner.replace("\\\\", "\x00").replace('\\"', '"').replace("\\n", "\n")
            .replace("\\t", "\t").replace("\x00", "\\"))


def _split_flow(inner: str, line_no: int) -> List[str]:
    """Split a flow collection body on commas outside quotes/brackets."""
    items, buf, depth, quote = [], [], 0, None
    for ch in inner:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
            buf.append(ch)
        elif ch in "[{":
            depth += 1
            buf.append(ch)
        elif ch in "]}":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            items.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if quote:
        raise YAMLError("unterminated quoted string at line %d" % line_no)
    tail = "".join(buf).strip()
    if tail:
        items.append(tail)
    return items


def _find_key_colon(s: str) -> int:
    """Index of the mapping colon (': ' or trailing ':') outside quotes/brackets, or -1."""
    depth, quote = 0, None
    for i, ch in enumerate(s):
        if quote:
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            if i == 0 or s[i - 1] in " ,[{":
                quote = ch
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        elif ch == ":" and depth == 0 and (i == len(s) - 1 or s[i + 1] in " \t"):
            return i
    return -1


def _is_mapping_line(s: str) -> bool:
    if s[:1] in ("[", "{", "'", '"') and not (s[:1] in ("'", '"') and _find_key_colon(s) > 0):
        return False
    return _find_key_colon(s) > 0


def _scalar(s: str, line_no: int) -> Any:
    s = s.strip()
    if s == "":
        return None
    if s[0] in ("'", '"'):
        return _unquote(s, line_no)
    if s[0] == "[":
        if s[-1] != "]":
            raise YAMLError("unterminated flow sequence at line %d" % line_no)
        return [_scalar(x, line_no) for x in _split_flow(s[1:-1], line_no)]
    if s[0] == "{":
        if s[-1] != "}":
            raise YAMLError("unterminated flow mapping at line %d" % line_no)
        result = {}
        for item in _split_flow(s[1:-1], line_no):
            c = _find_key_colon(item)
            if c < 0:
                raise YAMLError("bad flow mapping entry at line %d" % line_no)
            result[_scalar(item[:c], line_no)] = _scalar(item[c + 1:], line_no)
        return result
    if _find_key_colon(s) > 0:
        raise YAMLError("mapping values are not allowed here (unquoted ': ') at line %d" % line_no)
    low = s.lower()
    if low in _NULLS:
        return None
    if low in _BOOL_TRUE:
        return True
    if low in _BOOL_FALSE:
        return False
    if _INT_RE.match(s):
        return int(s.replace("_", ""))
    if _FLOAT_RE.match(s):
        try:
            return float(s.replace("_", ""))
        except ValueError:
            return s
    return s


class _Parser:
    def __init__(self, lines: List[str]):
        self.lines = lines
        self.i = 0
        for n, raw in enumerate(lines, start=1):
            lead = raw[: len(raw) - len(raw.lstrip())]
            if "\t" in lead and raw.strip():
                raise YAMLError("tab character in indentation at line %d" % n)

    def eof(self) -> bool:
        return self.i >= len(self.lines)

    def raw(self) -> str:
        return self.lines[self.i]

    def indent(self) -> int:
        r = self.raw()
        return len(r) - len(r.lstrip(" "))

    def content(self) -> str:
        return _strip_comment(self.raw()).strip()

    def skip_blank(self) -> None:
        while not self.eof() and self.content() == "":
            self.i += 1

    def parse_node(self, indent: int) -> Any:
        c = self.content()
        if c == "-" or c.startswith("- "):
            return self.parse_sequence(indent)
        if _is_mapping_line(c):
            return self.parse_mapping(indent)
        line_no = self.i + 1
        self.i += 1
        return _scalar(self._collect_continuation(c, indent), line_no)

    def _collect_continuation(self, first: str, indent: int) -> str:
        parts = [first]
        while not self.eof():
            if self.content() == "":
                self.i += 1
                continue
            if self.indent() <= indent:
                break
            c = self.content()
            if c == "-" or c.startswith("- ") or _is_mapping_line(c):
                break
            parts.append(c)
            self.i += 1
        return " ".join(parts)

    def parse_mapping(self, indent: int) -> dict:
        result = {}
        while True:
            self.skip_blank()
            if self.eof() or self.indent() < indent:
                break
            if self.indent() > indent:
                raise YAMLError("bad indentation at line %d" % (self.i + 1))
            c = self.content()
            line_no = self.i + 1
            if c == "-" or c.startswith("- "):
                raise YAMLError("sequence item where a mapping key was expected at line %d" % line_no)
            colon = _find_key_colon(c)
            if colon <= 0:
                raise YAMLError("expected 'key: value' at line %d" % line_no)
            key = _scalar(c[:colon], line_no)
            rest = c[colon + 1:].strip()
            self.i += 1
            if rest == "":
                self.skip_blank()
                if not self.eof() and self.indent() > indent:
                    result[key] = self.parse_node(self.indent())
                elif not self.eof() and self.indent() == indent and (self.content() == "-" or self.content().startswith("- ")):
                    result[key] = self.parse_sequence(indent)
                else:
                    result[key] = None
            elif rest in ("|", ">", "|-", ">-", "|+", ">+"):
                result[key] = self.parse_block_scalar(indent, rest)
            elif rest[0] in ("[", "{") and rest[-1] not in ("]", "}"):
                raise YAMLError("multi-line flow collections are not supported by the builtin parser (line %d)" % line_no)
            else:
                if rest[0] not in ("'", '"', "[", "{"):
                    rest = self._collect_continuation(rest, indent)
                result[key] = _scalar(rest, line_no)
        return result

    def parse_sequence(self, indent: int) -> list:
        items = []
        while True:
            self.skip_blank()
            if self.eof() or self.indent() < indent:
                break
            if self.indent() > indent:
                raise YAMLError("bad indentation at line %d" % (self.i + 1))
            c = self.content()
            if not (c == "-" or c.startswith("- ")):
                break
            line_no = self.i + 1
            rest = c[1:].strip()
            if rest == "":
                self.i += 1
                self.skip_blank()
                if not self.eof() and self.indent() > indent:
                    items.append(self.parse_node(self.indent()))
                else:
                    items.append(None)
            elif _is_mapping_line(rest) and rest[0] not in ("[", "{"):
                sub_indent = indent + (len(c) - len(rest))
                self.lines[self.i] = " " * sub_indent + rest
                items.append(self.parse_mapping(sub_indent))
            else:
                self.i += 1
                if rest[0] not in ("'", '"', "[", "{"):
                    rest = self._collect_continuation(rest, indent)
                items.append(_scalar(rest, line_no))
        return items

    def parse_block_scalar(self, indent: int, style: str) -> str:
        buf = []
        while not self.eof():
            raw = self.raw()
            if raw.strip() == "":
                buf.append("")
                self.i += 1
                continue
            ind = len(raw) - len(raw.lstrip(" "))
            if ind <= indent:
                break
            buf.append(raw)
            self.i += 1
        while buf and buf[-1] == "":
            buf.pop()
        non_blank = [len(b) - len(b.lstrip(" ")) for b in buf if b.strip()]
        base = min(non_blank) if non_blank else 0
        lines = [b[base:] if b.strip() else "" for b in buf]
        if style[0] == ">":
            out, para = [], []
            for ln in lines:
                if ln == "":
                    out.append(" ".join(para))
                    para = []
                else:
                    para.append(ln)
            out.append(" ".join(para))
            text = "\n".join(out)
        else:
            text = "\n".join(lines)
        if style.endswith("-"):
            return text
        return text + "\n"
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python3 -m unittest tests.test_yamlfm -v`
Expected: all tests PASS (the parity test is skipped only if PyYAML is absent).

- [ ] **Step 6: Commit**

```bash
chmod +x .claude/skills/linting-agent-config-files/scripts/agentlint.py
git add .claude/skills/linting-agent-config-files/scripts tests/__init__.py tests/helpers.py tests/test_yamlfm.py
git commit -m "feat(agentlint): scaffold, data model and YAML front-matter parser

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_016TZTeGdK9WuTukJpPzZFxY"
```

---

### Task 2: Rule catalogue, tool-name tables, and file discovery

**Files:**
- Create: `.../agentlint_lib/catalogue.py`, `.../agentlint_lib/toolnames.py`, `.../agentlint_lib/discover.py`
- Create: `tests/test_catalogue.py`, `tests/test_discover.py`

**Interfaces:**
- Consumes `model.rule`, `model.RULES`, `model.ConfigFile`, `yamlfm.split_frontmatter`, `yamlfm.parse_yaml`.
- Produces `catalogue.SRC: Dict[str, str]`, and registers every rule in `model.RULES` on import (`import agentlint_lib.catalogue` is the only side-effect entry point).
- Produces `toolnames.copilot_tool_problem(entry: str) -> Optional[str]`, `toolnames.claude_tool_problem(entry: str, allow_mcp_wildcard: bool) -> Optional[str]`, `toolnames.split_claude_tools(value) -> Tuple[List[str], bool]` (returns entries and `was_list`).
- Produces `discover.detect_kind(rel: str, root: str) -> Optional[str]`, `discover.discover(root, paths, excludes, force_kind) -> List[ConfigFile]`, `discover.glob_match(pattern, rel) -> bool`, `discover.KINDS` (tuple of all kind names), `discover.MARKDOWN_KINDS`, `discover.JSON_KINDS`, `discover.YAML_KINDS`.

- [ ] **Step 1: Write the failing tests**

`tests/test_catalogue.py`:

```python
import re
import unittest

from tests.helpers import import_lib

lib = import_lib()
from agentlint_lib import catalogue, model  # noqa: E402,F401


class CatalogueTests(unittest.TestCase):
    def test_every_rule_is_well_formed(self):
        self.assertGreaterEqual(len(model.RULES), 90)
        for rid, r in model.RULES.items():
            self.assertRegex(rid, r"^(GN|AG|SK|IN|CF|XF)\d{3}$")
            self.assertTrue(r.source.startswith("https://"), rid)
            self.assertTrue(r.title and r.title[0].isupper(), rid)

    def test_expected_ids_present(self):
        for rid in ["GN001", "AG001", "AG028", "SK001", "SK019", "IN001", "IN020",
                    "CF001", "CF022", "XF001", "XF010"]:
            self.assertIn(rid, model.RULES)

    def test_manual_rules_cannot_be_emitted(self):
        with self.assertRaises(ValueError):
            model.Finding("AG018", "x.md", "nope")
```

`tests/test_discover.py`:

```python
import os
import shutil
import tempfile
import unittest

from tests.helpers import import_lib

lib = import_lib()
from agentlint_lib import discover  # noqa: E402


def touch(root, rel, content="---\nname: x\ndescription: y\n---\nbody\n"):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    mode = "wb" if isinstance(content, bytes) else "w"
    with open(p, mode) as fh:
        fh.write(content)
    return p


class DetectKindTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_kinds(self):
        cases = {
            ".github/agents/a.agent.md": "copilot-agent",
            ".github/agents/b.md": "copilot-agent",
            "plugins/x/agents/c.agent.md": "copilot-agent",
            ".claude/agents/d.md": "claude-subagent",
            ".claude/agents/nested/e.md": "claude-subagent",
            ".claude/agents/f.agent.md": "claude-subagent",  # location wins over suffix
            ".github/chatmodes/f.chatmode.md": "chatmode",
            ".claude/skills/s/SKILL.md": "skill",
            ".github/skills/s/skill.md": "skill",
            ".github/copilot-instructions.md": "copilot-instructions",
            ".github/instructions/py.instructions.md": "path-instructions",
            "docs/odd.instructions.md": "path-instructions",
            ".github/prompts/p.prompt.md": "prompt-file",
            "AGENTS.md": "agents-md",
            "pkg/AGENT.md": "agents-md",
            "CLAUDE.md": "claude-md",
            ".claude/CLAUDE.md": "claude-md",
            "CLAUDE.local.md": "claude-md",
            ".claude/rules/r.md": "claude-rule",
            ".claude/commands/c.md": "claude-command",
            ".mcp.json": "mcp-claude",
            ".vscode/mcp.json": "mcp-vscode",
            ".github/mcp.json": "mcp-copilot-cli",
            ".claude/settings.json": "settings-hooks",
            ".claude/settings.local.json": "settings-hooks",
            "hooks/hooks.json": "settings-hooks",
            ".claude-plugin/plugin.json": "plugin-manifest",
            ".github/plugin/plugin.json": "plugin-manifest",
            ".claude-plugin/marketplace.json": "marketplace-manifest",
            ".github/workflows/copilot-setup-steps.yml": "copilot-setup-steps",
            ".cursor/rules/r.mdc": "cursor-rule",
            ".cursor/rules/r.md": "cursor-rule",
            "README.md": None,
            "src/app.py": None,
        }
        for rel, kind in cases.items():
            self.assertEqual(discover.detect_kind(rel, self.root), kind, rel)

    def test_plugin_root_agents_are_claude_subagents(self):
        touch(self.root, ".claude-plugin/plugin.json", "{}")
        touch(self.root, "agents/reviewer.md")
        self.assertEqual(discover.detect_kind("agents/reviewer.md", self.root), "claude-subagent")


class DiscoverTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        touch(self.root, ".github/agents/a.agent.md")
        touch(self.root, ".claude/skills/s/SKILL.md")
        touch(self.root, "tests/fixtures/bad/.claude/skills/t/SKILL.md")
        touch(self.root, "node_modules/x/SKILL.md")
        touch(self.root, ".mcp.json", '{"mcpServers": {}}')
        touch(self.root, "bin.md", b"---\x00\x01binary")
        touch(self.root, "crlf/AGENTS.md", b"\xef\xbb\xbf# hi\r\nline\r\n")

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_discover_all_with_exclude(self):
        files = discover.discover(self.root, [], ["tests/fixtures/**"], None)
        paths = sorted(f.path for f in files)
        self.assertEqual(paths, [".claude/skills/s/SKILL.md", ".github/agents/a.agent.md", ".mcp.json",
                                 "bin.md", "crlf/AGENTS.md"])

    def test_explicit_paths_and_force_kind(self):
        files = discover.discover(self.root, ["bin.md"], [], "mcp-copilot-cloud")
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].kind, "mcp-copilot-cloud")

    def test_loading_flags(self):
        by_path = {f.path: f for f in discover.discover(self.root, [], ["tests/**"], None)}
        self.assertIsNone(by_path["bin.md"].text)
        self.assertIsNotNone(by_path["bin.md"].read_error)
        self.assertTrue(by_path["crlf/AGENTS.md"].bom)
        self.assertTrue(by_path["crlf/AGENTS.md"].crlf)
        self.assertEqual(by_path["crlf/AGENTS.md"].text, "# hi\nline\n")
        skill = by_path[".claude/skills/s/SKILL.md"]
        self.assertTrue(skill.fm_present)
        self.assertEqual(skill.fm["name"], "x")
        self.assertEqual(skill.body_line, 5)
        self.assertEqual(by_path[".mcp.json"].data, {"mcpServers": {}})

    def test_glob_match(self):
        self.assertTrue(discover.glob_match("tests/fixtures/**", "tests/fixtures/a/b.md"))
        self.assertTrue(discover.glob_match("**/*.md", "a/b/c.md"))
        self.assertFalse(discover.glob_match("tests/*", "tests/a/b.md"))
        self.assertTrue(discover.glob_match("*.json", "x.json"))
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest tests.test_catalogue tests.test_discover -v`
Expected: ImportError for `catalogue` / `discover`.

- [ ] **Step 3: Write `catalogue.py`**

```python
"""Every agentlint rule, registered on import. This is the single source of truth for IDs,
severities, tags, runtimes and source URLs; `references/rule-catalogue.md` is generated from it."""
from .model import rule

SRC = {
    "gh-agent-ref": "https://docs.github.com/en/copilot/reference/custom-agents-configuration",
    "gh-agent-create": "https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/create-custom-agents",
    "vscode-agents": "https://code.visualstudio.com/docs/agent-customization/custom-agents",
    "vscode-subagents": "https://code.visualstudio.com/docs/agents/run/subagents",
    "vscode-hooks": "https://code.visualstudio.com/docs/agent-customization/hooks",
    "cli-ref": "https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference",
    "cli-plugins": "https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference",
    "cli-mcp": "https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers",
    "skills-spec": "https://agentskills.io/specification",
    "gh-skills": "https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills",
    "vscode-skills": "https://code.visualstudio.com/docs/copilot/customization/agent-skills",
    "gh-skill-publish": "https://cli.github.com/manual/gh_skill_publish",
    "claude-skills": "https://code.claude.com/docs/en/skills",
    "claude-subagents": "https://code.claude.com/docs/en/sub-agents",
    "claude-memory": "https://code.claude.com/docs/en/memory",
    "claude-hooks": "https://code.claude.com/docs/en/hooks",
    "claude-mcp": "https://code.claude.com/docs/en/mcp",
    "claude-plugins": "https://code.claude.com/docs/en/plugins-reference",
    "gh-instructions": "https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions",
    "gh-cheat": "https://docs.github.com/en/copilot/reference/customization-cheat-sheet",
    "gh-cr-tutorial": "https://docs.github.com/en/copilot/tutorials/customize-code-review",
    "vscode-instructions": "https://code.visualstudio.com/docs/agent-customization/custom-instructions",
    "vscode-prompts": "https://code.visualstudio.com/docs/agent-customization/prompt-files",
    "agents-md": "https://agents.md/",
    "vscode-mcp": "https://code.visualstudio.com/docs/agents/reference/mcp-configuration",
    "gh-mcp": "https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/configure-mcp-servers",
    "gh-env": "https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-environment",
    "cursor-rules": "https://cursor.com/docs/context/rules",
    "yaml": "https://yaml.org/spec/1.2.2/",
}

# ---- GN: general file hygiene
rule("GN001", "warning", "auto", "GN", "generic", "UTF-8 byte-order mark at start of file", SRC["yaml"])
rule("GN002", "info", "auto", "GN", "generic", "CRLF line endings", SRC["yaml"])
rule("GN003", "error", "auto", "GN", "generic", "File is not valid UTF-8", SRC["yaml"])
rule("GN004", "info", "auto", "GN", "generic", "File skipped (binary or unreadable)", SRC["yaml"])

# ---- AG: agent definitions
rule("AG001", "error", "auto", "AG", "both", "Frontmatter missing, unterminated, or invalid YAML", SRC["gh-agent-ref"])
rule("AG002", "error", "auto", "AG", "copilot", "Copilot agent missing required description", SRC["gh-agent-ref"])
rule("AG003", "error", "auto", "AG", "claude", "Claude subagent missing name or description", SRC["claude-subagents"])
rule("AG004", "error", "auto", "AG", "claude", "Claude subagent name must be lowercase letters and hyphens (no colon)", SRC["claude-subagents"])
rule("AG005", "warning", "auto", "AG", "copilot", "Retired key infer; use disable-model-invocation and user-invocable", SRC["gh-agent-ref"])
rule("AG006", "warning", "auto", "AG", "copilot", "Deprecated .chatmode.md file; rename to .agent.md", SRC["vscode-agents"])
rule("AG007", "warning", "auto", "AG", "copilot", "Unrecognised tool name in tools (silently ignored)", SRC["gh-agent-ref"])
rule("AG008", "error", "auto", "AG", "claude", "Unknown tool in Claude tools list", SRC["claude-subagents"])
rule("AG009", "error", "auto", "AG", "copilot", "agents set but agent tool not included in tools", SRC["vscode-subagents"])
rule("AG010", "error", "auto", "AG", "copilot", "Agent body exceeds 30,000 characters", SRC["gh-agent-create"])
rule("AG011", "info", "auto", "AG", "copilot", "mcp-servers or metadata with target vscode (not used in IDEs)", SRC["gh-agent-ref"])
rule("AG012", "info", "auto", "AG", "copilot", "VS Code-only keys present (ignored on github.com)", SRC["gh-agent-ref"])
rule("AG013", "error", "auto", "AG", "copilot", "Agent filename contains characters outside . - _ a-z A-Z 0-9", SRC["gh-agent-create"])
rule("AG014", "warning", "auto", "AG", "both", "model value belongs to the other runtime", SRC["gh-agent-ref"])
rule("AG015", "error", "auto", "AG", "claude", "Undocumented value for an enumerated Claude field", SRC["claude-subagents"])
rule("AG016", "warning", "auto", "AG", "both", "Empty agent body", SRC["gh-agent-ref"])
rule("AG017", "warning", "auto", "AG", "both", "Unknown frontmatter key for this runtime", SRC["gh-agent-ref"])
rule("AG018", "warning", "manual", "AG", "both", "Description gives no when-to-use triggers", SRC["claude-subagents"])
rule("AG019", "warning", "manual", "AG", "both", "Body instructs actions the tools list forbids, or claims read-only while granting edit", SRC["gh-agent-ref"])
rule("AG020", "warning", "manual", "AG", "both", "Body contradicts itself", SRC["gh-agent-ref"])
rule("AG021", "info", "manual", "AG", "both", "Body names skills or agents that do not exist in the repository", SRC["gh-agent-ref"])
rule("AG022", "warning", "auto", "AG", "copilot", "target must be vscode or github-copilot", SRC["gh-agent-ref"])
rule("AG023", "info", "auto", "AG", "claude", "tools given as a YAML list; docs specify a comma-separated string", SRC["vscode-agents"])
rule("AG024", "warning", "auto", "AG", "copilot", "Copilot tools must be a YAML list", SRC["gh-agent-ref"])
rule("AG025", "error", "auto", "AG", "copilot", "handoffs entry missing label or agent", SRC["vscode-agents"])
rule("AG026", "warning", "auto", "AG", "both", "Boolean field has a non-boolean value", SRC["gh-agent-ref"])
rule("AG027", "error", "auto", "AG", "claude", "skills must be a YAML list of skill names", SRC["claude-subagents"])
rule("AG028", "error", "auto", "AG", "copilot", "mcp-servers entry missing tools/type or has an invalid type", SRC["gh-mcp"])

# ---- SK: skills
rule("SK001", "error", "auto", "SK", "both", "SKILL.md frontmatter missing or invalid", SRC["skills-spec"])
rule("SK002", "error", "auto", "SK", "both", "name missing", SRC["skills-spec"])
rule("SK003", "error", "auto", "SK", "both", "name must be 1-64 chars of lowercase letters, digits and single hyphens", SRC["skills-spec"])
rule("SK004", "error", "auto", "SK", "both", "name differs from the parent directory name", SRC["skills-spec"])
rule("SK005", "error", "auto", "SK", "both", "description missing, empty, or longer than 1024 characters", SRC["skills-spec"])
rule("SK006", "warning", "auto", "SK", "both", "Body longer than 500 lines", SRC["skills-spec"])
rule("SK007", "error", "auto", "SK", "both", "Relative path or link in the body points to a missing file", SRC["skills-spec"])
rule("SK008", "warning", "auto", "SK", "both", "Script lacks a shebang or the executable bit", SRC["skills-spec"])
rule("SK009", "error", "auto", "SK", "both", "compatibility must be a string of at most 500 characters", SRC["skills-spec"])
rule("SK010", "info", "auto", "SK", "both", "Runtime-specific frontmatter keys present (portability note)", SRC["claude-skills"])
rule("SK011", "warning", "auto", "SK", "both", "Frontmatter key unknown to every runtime (possible typo)", SRC["skills-spec"])
rule("SK012", "error", "auto", "SK", "both", "File must be named exactly SKILL.md", SRC["skills-spec"])
rule("SK013", "warning", "auto", "SK", "both", "SKILL.md outside every documented discovery location", SRC["cli-ref"])
rule("SK014", "info", "auto", "SK", "both", "metadata is not a map of string keys to string values", SRC["skills-spec"])
rule("SK015", "warning", "manual", "SK", "both", "Description gives no when-to-use triggers or is written in first person", SRC["vscode-skills"])
rule("SK016", "warning", "manual", "SK", "both", "Description summarises the workflow (agents may follow it instead of the body)", SRC["skills-spec"])
rule("SK017", "warning", "manual", "SK", "both", "Body contradicts itself or references tools/commands that do not exist", SRC["skills-spec"])
rule("SK018", "info", "manual", "SK", "both", "Body duplicates another skill instead of cross-referencing it", SRC["skills-spec"])
rule("SK019", "warning", "auto", "SK", "both", "allowed-tools is a YAML list; spec wants a space-separated string (gh skill publish rejects lists)", SRC["gh-skill-publish"])

# ---- IN: instructions and prompts
rule("IN001", "error", "auto", "IN", "copilot", "Instruction or prompt file frontmatter invalid", SRC["vscode-instructions"])
rule("IN002", "warning", "auto", "IN", "copilot", ".instructions.md without applyTo", SRC["gh-instructions"])
rule("IN003", "warning", "auto", "IN", "copilot", "applyTo is documented as a comma-separated string, not a list", SRC["vscode-instructions"])
rule("IN004", "warning", "auto", "IN", "copilot", "excludeAgent must be code-review or cloud-agent", SRC["gh-instructions"])
rule("IN005", "info", "auto", "IN", "copilot", "Instruction file longer than 1,000 lines may be partly overlooked", SRC["gh-cr-tutorial"])
rule("IN006", "error", "auto", "IN", "copilot", "prompt file agent references an agent that does not exist", SRC["vscode-prompts"])
rule("IN007", "error", "auto", "IN", "claude", "CLAUDE.md @import target does not exist", SRC["claude-memory"])
rule("IN008", "error", "auto", "IN", "claude", ".claude/rules paths must be a YAML list of glob strings", SRC["claude-memory"])
rule("IN009", "info", "auto", "IN", "generic", "Nested AGENTS.md (VS Code requires chat.useNestedAgentsMdFiles)", SRC["agents-md"])
rule("IN010", "warning", "auto", "IN", "generic", "Legacy AGENT.md singular filename; rename to AGENTS.md", SRC["agents-md"])
rule("IN011", "warning", "auto", "IN", "copilot", ".instructions.md outside .github/instructions is not discovered on github.com", SRC["gh-instructions"])
rule("IN012", "info", "auto", "IN", "generic", "Frontmatter present in a file for which no fields are defined", SRC["gh-instructions"])
rule("IN013", "info", "auto", "IN", "generic", ".cursor/rules file without .mdc extension is ignored by Cursor", SRC["cursor-rules"])
rule("IN014", "warning", "auto", "IN", "copilot", "Unknown frontmatter key in instruction or prompt file", SRC["vscode-prompts"])
rule("IN015", "warning", "manual", "IN", "copilot", "Task-specific or one-off instructions in a repository-wide file", SRC["gh-instructions"])
rule("IN016", "warning", "manual", "IN", "generic", "Instruction demands a command, path or tool that does not exist in the repository", SRC["gh-instructions"])
rule("IN017", "warning", "auto", "IN", "generic", "Instruction or prompt file has an empty body", SRC["gh-instructions"])
rule("IN018", "warning", "auto", "IN", "copilot", "Prompt file uses legacy mode; use agent", SRC["vscode-prompts"])
rule("IN019", "warning", "auto", "IN", "copilot", "Prompt file tools must be a YAML list", SRC["vscode-prompts"])
rule("IN020", "info", "auto", "IN", "claude", "Legacy .claude/commands file; name and paths are ignored there and skills are recommended", SRC["claude-skills"])

# ---- CF: MCP, hooks, environment, manifests
rule("CF001", "error", "auto", "CF", "generic", "JSON or YAML is invalid", SRC["claude-mcp"])
rule("CF002", "error", "auto", "CF", "generic", "Wrong top-level key: .vscode/mcp.json needs servers, .mcp.json needs mcpServers", SRC["vscode-mcp"])
rule("CF003", "error", "auto", "CF", "claude", ".mcp.json entry has url but no type (read as stdio and skipped)", SRC["claude-mcp"])
rule("CF004", "warning", "auto", "CF", "claude", "type sse is deprecated; use http", SRC["claude-mcp"])
rule("CF005", "error", "auto", "CF", "copilot", "Cloud-agent MCP entry missing tools or type, or type not local/stdio/http/sse", SRC["gh-mcp"])
rule("CF006", "error", "auto", "CF", "generic", "Literal secret-looking value in env or headers", SRC["gh-mcp"])
rule("CF007", "error", "auto", "CF", "claude", "Hook event misspelled or handler missing a required field", SRC["claude-hooks"])
rule("CF008", "error", "auto", "CF", "copilot", "copilot-setup-steps.yml job must be named copilot-setup-steps and use only supported keys", SRC["gh-env"])
rule("CF009", "error", "auto", "CF", "claude", "plugin.json must be at .claude-plugin/plugin.json with components at the plugin root", SRC["claude-plugins"])
rule("CF010", "warning", "auto", "CF", "generic", "Hook or MCP command script path missing or not executable", SRC["claude-hooks"])
rule("CF011", "info", "auto", "CF", "generic", "${VAR} reference without a default", SRC["claude-mcp"])
rule("CF012", "error", "auto", "CF", "generic", "stdio server missing command, or remote server missing url", SRC["vscode-mcp"])
rule("CF013", "info", "auto", "CF", "claude", "Copilot-only tools allowlist inside a .mcp.json shared with Claude Code", SRC["claude-mcp"])
rule("CF014", "info", "auto", "CF", "generic", "Unknown key in MCP server entry", SRC["claude-mcp"])
rule("CF015", "error", "auto", "CF", "generic", "${input:id} used but not declared in inputs", SRC["vscode-mcp"])
rule("CF016", "warning", "auto", "CF", "copilot", "Cloud-agent env or header reference is not COPILOT_MCP_-prefixed", SRC["gh-mcp"])
rule("CF017", "info", "auto", "CF", "claude", "once is only honoured in skill frontmatter", SRC["claude-hooks"])
rule("CF018", "warning", "auto", "CF", "claude", "if is only evaluated on tool events; this hook never runs", SRC["claude-hooks"])
rule("CF019", "info", "auto", "CF", "copilot", "copilot-setup-steps.yml has no on triggers, so it cannot be self-tested as a workflow", SRC["gh-env"])
rule("CF020", "error", "auto", "CF", "generic", "Plugin manifest missing name", SRC["claude-plugins"])
rule("CF021", "error", "auto", "CF", "generic", "Marketplace entry missing name or source", SRC["claude-plugins"])
rule("CF022", "info", "auto", "CF", "copilot", "type sse is a legacy transport in Copilot CLI / MCP spec", SRC["cli-mcp"])

# ---- XF: cross-file
rule("XF001", "warning", "auto", "XF", "copilot", "Same skill name in more than one discovery directory (first-found-wins shadowing)", SRC["cli-ref"])
rule("XF002", "info", "auto", "XF", "both", "Same agent name in .github/agents and .claude/agents", SRC["cli-ref"])
rule("XF003", "error", "auto", "XF", "both", "Dangling reference to an agent or skill", SRC["claude-subagents"])
rule("XF004", "error", "auto", "XF", "claude", "Subagent preloads a skill that has disable-model-invocation: true", SRC["claude-subagents"])
rule("XF005", "warning", "auto", "XF", "claude", "Skill and .claude/commands file share a name (the skill wins)", SRC["claude-skills"])
rule("XF006", "info", "auto", "XF", "copilot", "Overlapping applyTo/paths globs across instruction files", SRC["vscode-instructions"])
rule("XF007", "warning", "manual", "XF", "generic", "Contradictory directives across files", SRC["gh-instructions"])
rule("XF008", "warning", "manual", "XF", "both", "Two skills with near-identical triggers (routing ambiguity)", SRC["skills-spec"])
rule("XF009", "warning", "manual", "XF", "both", "Agent composes skills whose descriptions do not match the claimed purpose", SRC["gh-agent-ref"])
rule("XF010", "info", "auto", "XF", "generic", "CLAUDE.md and AGENTS.md coexist without importing each other", SRC["claude-memory"])
```

- [ ] **Step 4: Write `toolnames.py`**

```python
"""Tool-name validation for Copilot and Claude Code agent definitions."""
import re
from typing import List, Optional, Tuple

# Copilot: aliases are case-insensitive. Sources: custom-agents-configuration reference (tools table),
# VS Code custom agents page (tool sets), Copilot CLI reference (view/bash/str_replace names).
COPILOT_TOOL_ALIASES = {
    "execute", "shell", "bash", "powershell", "read", "notebookread", "edit", "multiedit", "write",
    "notebookedit", "search", "grep", "glob", "agent", "custom-agent", "task", "web", "websearch",
    "webfetch", "todo", "todowrite", "browser", "view", "str_replace", "str_replace_editor",
    # legacy VS Code tool ids
    "codebase", "editfiles", "fetch", "runcommands", "runtasks", "usages", "problems", "changes",
    "testfailure", "terminallastcommand", "terminalselection", "findtestfiles", "githubrepo",
    "extensions", "vscodeapi", "opensimplebrowser", "runnotebooks", "new", "memory", "think", "todos",
    "runintterminal", "runinterminal",
}
_COPILOT_NAMESPACED = re.compile(r"^[A-Za-z0-9_.-]+/([A-Za-z0-9_.-]+|\*)$")

CLAUDE_TOOLS = {
    "Read", "Edit", "Write", "MultiEdit", "NotebookEdit", "NotebookRead", "Bash", "PowerShell", "Grep",
    "Glob", "LS", "WebFetch", "WebSearch", "Agent", "Task", "Skill", "TodoWrite", "AskUserQuestion",
    "SlashCommand", "BashOutput", "KillShell", "ExitPlanMode", "EnterPlanMode", "Monitor",
    "ListMcpResources", "ReadMcpResource", "ToolSearch", "TaskOutput", "TaskStop", "CronCreate",
    "CronDelete", "CronList", "EnterWorktree", "ExitWorktree", "ScheduleWakeup", "SendMessage",
    "EndConversation", "Artifact",
}
_CLAUDE_PATTERN = re.compile(r"^([A-Za-z]+)\((.*)\)$")
_CLAUDE_MCP = re.compile(r"^mcp__[A-Za-z0-9_-]+(__[A-Za-z0-9_-]+)?$")


def copilot_tool_problem(entry: str) -> Optional[str]:
    """Return None if the entry is a documented Copilot tool spelling, else a short reason."""
    if not isinstance(entry, str) or not entry.strip():
        return "empty tool name"
    e = entry.strip()
    if e == "*" or e.lower() in COPILOT_TOOL_ALIASES or _COPILOT_NAMESPACED.match(e):
        return None
    return "'%s' is not a documented tool alias, tool-set, <server>/<tool> or <server>/* pattern" % e


def claude_tool_problem(entry: str, allow_mcp_wildcard: bool = False) -> Optional[str]:
    """Return None if the entry is a valid Claude Code tool name or permission pattern."""
    if not isinstance(entry, str) or not entry.strip():
        return "empty tool name"
    e = entry.strip()
    if e in CLAUDE_TOOLS:
        return None
    if e == "mcp__*":
        return None if allow_mcp_wildcard else "mcp__* is only valid in disallowedTools"
    if _CLAUDE_MCP.match(e):
        return None
    m = _CLAUDE_PATTERN.match(e)
    if m and m.group(1) in CLAUDE_TOOLS:
        return None
    if e.lower() in COPILOT_TOOL_ALIASES:
        return "'%s' looks like a Copilot tool alias; Claude Code tool names are capitalised (e.g. Read, Bash)" % e
    return "'%s' is not a known Claude Code tool, Tool(pattern) rule or mcp__server__tool name" % e


def split_claude_tools(value) -> Tuple[List[str], bool]:
    """Normalise a Claude tools/disallowedTools value. Returns (entries, was_yaml_list)."""
    if value is None:
        return [], False
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()], True
    if isinstance(value, str):
        return _split_commas(value), False
    return [str(value)], False


def _split_commas(s: str) -> List[str]:
    """Split on commas that are outside parentheses, so Bash(a, b) stays intact."""
    out, buf, depth = [], [], 0
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        out.append(tail)
    return [o for o in out if o]
```

- [ ] **Step 5: Write `discover.py`**

```python
"""Find candidate files, classify them by kind, and load them into ConfigFile objects."""
import json
import os
import re
import subprocess
from typing import List, Optional

from .model import ConfigFile
from . import yamlfm

KINDS = (
    "copilot-agent", "claude-subagent", "chatmode", "skill", "copilot-instructions", "path-instructions",
    "prompt-file", "agents-md", "claude-md", "claude-rule", "claude-command", "mcp-claude", "mcp-vscode",
    "mcp-copilot-cli", "mcp-copilot-cloud", "settings-hooks", "copilot-setup-steps", "plugin-manifest",
    "marketplace-manifest", "cursor-rule",
)
MARKDOWN_KINDS = ("copilot-agent", "claude-subagent", "chatmode", "skill", "copilot-instructions",
                  "path-instructions", "prompt-file", "agents-md", "claude-md", "claude-rule",
                  "claude-command", "cursor-rule")
JSON_KINDS = ("mcp-claude", "mcp-vscode", "mcp-copilot-cli", "mcp-copilot-cloud", "settings-hooks",
              "plugin-manifest", "marketplace-manifest")
YAML_KINDS = ("copilot-setup-steps",)

SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", "__pycache__", ".venv", "venv"}


def _has(rel: str, segment: str) -> bool:
    return ("/" + rel).find("/" + segment + "/") >= 0


def detect_kind(rel: str, root: str) -> Optional[str]:
    rel = rel.replace(os.sep, "/")
    parts = rel.split("/")
    name = parts[-1]
    if name == "copilot-setup-steps.yml" and _has(rel, ".github/workflows"):
        return "copilot-setup-steps"
    if rel.endswith(".chatmode.md"):
        return "chatmode"
    if _has(rel, ".claude/agents") and rel.endswith(".md"):
        return "claude-subagent"
    if rel.endswith(".agent.md") or (_has(rel, ".github/agents") and rel.endswith(".md")):
        return "copilot-agent"
    if len(parts) >= 2 and parts[-2] == "agents" and rel.endswith(".md"):
        plugin_root = "/".join(parts[:-2])
        if os.path.exists(os.path.join(root, plugin_root, ".claude-plugin", "plugin.json")):
            return "claude-subagent"
    if name.lower() == "skill.md":
        return "skill"
    if rel == ".github/copilot-instructions.md" or rel.endswith("/.github/copilot-instructions.md"):
        return "copilot-instructions"
    if rel.endswith(".instructions.md"):
        return "path-instructions"
    if rel.endswith(".prompt.md"):
        return "prompt-file"
    if name in ("AGENTS.md", "AGENT.md"):
        return "agents-md"
    if name in ("CLAUDE.md", "CLAUDE.local.md"):
        return "claude-md"
    if _has(rel, ".claude/rules") and rel.endswith(".md"):
        return "claude-rule"
    if _has(rel, ".claude/commands") and rel.endswith(".md"):
        return "claude-command"
    if _has(rel, ".cursor/rules"):
        return "cursor-rule"
    if name == ".mcp.json":
        return "mcp-claude"
    if rel.endswith(".vscode/mcp.json"):
        return "mcp-vscode"
    if rel.endswith(".github/mcp.json") or rel.endswith(".copilot/mcp-config.json"):
        return "mcp-copilot-cli"
    if name in ("settings.json", "settings.local.json") and _has(rel, ".claude"):
        return "settings-hooks"
    if name == "hooks.json" and len(parts) >= 2 and parts[-2] == "hooks":
        return "settings-hooks"
    if rel.endswith(".claude-plugin/plugin.json") or rel.endswith(".github/plugin/plugin.json"):
        return "plugin-manifest"
    if rel.endswith(".claude-plugin/marketplace.json") or rel.endswith(".github/plugin/marketplace.json"):
        return "marketplace-manifest"
    return None


def _glob_to_regex(pattern: str) -> str:
    out, i = [], 0
    while i < len(pattern):
        ch = pattern[i]
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
            continue
        if pattern.startswith("**", i):
            out.append(".*")
            i += 2
            continue
        if ch == "*":
            out.append("[^/]*")
        elif ch == "?":
            out.append("[^/]")
        else:
            out.append(re.escape(ch))
        i += 1
    return "^" + "".join(out) + "$"


def glob_match(pattern: str, rel: str) -> bool:
    return re.match(_glob_to_regex(pattern.strip()), rel) is not None


def _git_files(root: str) -> Optional[List[str]]:
    try:
        out = subprocess.run(["git", "-C", root, "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                             capture_output=True, check=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    return [p.decode("utf-8", "replace") for p in out.split(b"\0") if p]


def _walk_files(root: str) -> List[str]:
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            found.append(os.path.relpath(os.path.join(dirpath, fn), root).replace(os.sep, "/"))
    return found


def _candidates(root: str, paths: List[str]) -> List[str]:
    if not paths:
        files = _git_files(root)
        if files is None:
            files = _walk_files(root)
        return [f for f in files if not any(seg in SKIP_DIRS for seg in f.split("/")[:-1])]
    rels = []
    for p in paths:
        ap = p if os.path.isabs(p) else os.path.join(root, p)
        if os.path.isdir(ap):
            for f in _walk_files(ap):
                rels.append(os.path.relpath(os.path.join(ap, f), root).replace(os.sep, "/"))
        elif os.path.exists(ap):
            rels.append(os.path.relpath(ap, root).replace(os.sep, "/"))
    return rels


def load(root: str, rel: str, kind: str) -> ConfigFile:
    cf = ConfigFile(path=rel, abs_path=os.path.join(root, rel), kind=kind)
    try:
        with open(cf.abs_path, "rb") as fh:
            raw = fh.read()
    except OSError as e:
        cf.read_error = "unreadable: %s" % e.strerror
        return cf
    if b"\x00" in raw[:8000]:
        cf.read_error = "binary content"
        return cf
    if raw.startswith(b"\xef\xbb\xbf"):
        cf.bom = True
        raw = raw[3:]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        cf.read_error = "not valid UTF-8 (byte %d)" % e.start
        return cf
    if "\r\n" in text:
        cf.crlf = True
        text = text.replace("\r\n", "\n")
    cf.text = text
    if kind in MARKDOWN_KINDS:
        fm_text, body, body_line, err = yamlfm.split_frontmatter(text)
        cf.body, cf.body_line = body, body_line
        if fm_text is not None:
            cf.fm_present, cf.fm_text = True, fm_text
            if err:
                cf.fm_error = err
            else:
                cf.frontmatter, cf.fm_error = yamlfm.parse_yaml(fm_text)
    elif kind in JSON_KINDS:
        try:
            cf.data = json.loads(text)
        except ValueError as e:
            cf.data_error = "invalid JSON: %s" % e
    elif kind in YAML_KINDS:
        cf.data, cf.data_error = yamlfm.parse_yaml(text)
    return cf


def discover(root: str, paths: List[str], excludes: List[str], force_kind: Optional[str]) -> List[ConfigFile]:
    root = os.path.abspath(root)
    result = []
    for rel in sorted(set(_candidates(root, paths))):
        if any(glob_match(x, rel) for x in excludes):
            continue
        kind = force_kind or detect_kind(rel, root)
        if kind is None:
            continue
        result.append(load(root, rel, kind))
    return result
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `python3 -m unittest tests.test_catalogue tests.test_discover -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add .claude/skills/linting-agent-config-files/scripts/agentlint_lib tests/test_catalogue.py tests/test_discover.py
git commit -m "feat(agentlint): rule catalogue, tool-name tables and file discovery

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_016TZTeGdK9WuTukJpPzZFxY"
```

---

### Task 3: General checks, API, report, and CLI

**Files:**
- Create: `.../agentlint_lib/rules_gn.py`, `.../agentlint_lib/api.py`, `.../agentlint_lib/report.py`, `.../agentlint_lib/cli.py`
- Create: `tests/test_cli.py`

**Interfaces:**
- Consumes `discover.discover`, `model.Context`, `model.Finding`, `catalogue` (import for side effect).
- Produces `api.lint(root, paths, excludes, collisions, min_severity, force_kind) -> dict` with keys `agentlint_version, root, python, yaml_parser, files, findings, summary, not_checked`; `api.RULE_MODULES` (filled by Tasks 4-8 through `api.register_checker(kinds, func)`); `report.to_json(result)`, `report.to_text(result)`, `report.catalogue_markdown()`; `cli.main(argv) -> int`.

- [ ] **Step 1: Write the failing tests**

`tests/test_cli.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest tests.test_cli -v`
Expected: ImportError for `api`.

- [ ] **Step 3: Write `rules_gn.py`**

```python
"""GN rules: encoding and line-ending hygiene applied to every discovered file."""
from typing import List

from .model import ConfigFile, Context, Finding


def check(cf: ConfigFile, ctx: Context) -> List[Finding]:
    out = []
    if cf.read_error:
        if "UTF-8" in cf.read_error:
            out.append(Finding("GN003", cf.path, cf.read_error, line=1))
        else:
            out.append(Finding("GN004", cf.path, "skipped: %s" % cf.read_error))
            ctx.not_checked.append("%s (%s)" % (cf.path, cf.read_error))
        return out
    if cf.bom:
        out.append(Finding("GN001", cf.path, "file starts with a UTF-8 BOM; frontmatter detection may fail in some tools",
                           line=1, autofix_safe=True, suggestion="save the file without a BOM"))
    if cf.crlf:
        out.append(Finding("GN002", cf.path, "CRLF line endings; tools differ in how they detect the --- delimiters",
                           line=1, autofix_safe=True, suggestion="convert to LF"))
    return out
```

- [ ] **Step 4: Write `api.py`**

```python
"""Programmatic entry point: lint(...) returns the result dict used by --format json."""
import os
import platform
import sys
from typing import Callable, Dict, List, Optional

from . import __version__, catalogue, discover, rules_gn, yamlfm  # noqa: F401 (catalogue registers rules)
from .model import SEVERITY_RANK, Context, Finding

# kind -> list of checker(cf, ctx) -> List[Finding]; filled by rules_* modules via register_checker
RULE_MODULES: Dict[str, List[Callable]] = {}
CROSS_FILE: List[Callable] = []


def register_checker(kinds, func):
    for k in kinds:
        RULE_MODULES.setdefault(k, []).append(func)


def register_cross_file(func):
    CROSS_FILE.append(func)


def _load_rule_modules():
    """Import rule modules lazily so a syntax error in one is reported, not hidden."""
    from . import rules_ag, rules_sk, rules_in, rules_cf, rules_xf  # noqa: F401


def resolve_root(root: Optional[str]) -> str:
    if root:
        return os.path.abspath(root)
    try:
        import subprocess
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                             check=True, timeout=10).stdout.strip()
        if top:
            return top
    except Exception:
        pass
    return os.getcwd()


def lint(root: Optional[str], paths: List[str], excludes: List[str], collisions: bool = True,
         min_severity: str = "info", force_kind: Optional[str] = None) -> dict:
    try:
        _load_rule_modules()
    except ImportError:
        pass  # during Tasks 3-8 some modules do not exist yet; later tasks make this import mandatory
    root = resolve_root(root)
    files = discover.discover(root, paths, excludes, force_kind)
    ctx = Context(root=root, files=files, yaml_parser=yamlfm.parser_name())
    findings: List[Finding] = []
    for cf in files:
        gn = rules_gn.check(cf, ctx)
        findings.extend(gn)
        if cf.read_error:
            continue
        for checker in RULE_MODULES.get(cf.kind, []):
            findings.extend(checker(cf, ctx))
    if collisions:
        for func in CROSS_FILE:
            findings.extend(func(ctx))
    if not any(f.kind == "mcp-copilot-cloud" for f in files):
        ctx.not_checked.append("Copilot cloud-agent MCP configuration lives in repository settings, not in the tree; "
                               "pass it with --kind mcp-copilot-cloud <file> to lint a pasted copy")
    threshold = SEVERITY_RANK[min_severity]
    findings = [f for f in findings if SEVERITY_RANK[f.severity] <= threshold]
    findings.sort(key=lambda f: (SEVERITY_RANK[f.severity], f.file, f.line or 0, f.id))
    summary = {"error": 0, "warning": 0, "info": 0}
    for f in findings:
        summary[f.severity] += 1
    return {
        "agentlint_version": __version__,
        "root": root,
        "python": platform.python_version(),
        "yaml_parser": ctx.yaml_parser,
        "files": [{"path": f.path, "kind": f.kind} for f in files],
        "findings": [f.to_dict() for f in findings],
        "summary": summary,
        "not_checked": ctx.not_checked,
    }
```

- [ ] **Step 5: Write `report.py`**

```python
"""Output formatting."""
import json

from .model import RULES


def to_json(result: dict) -> str:
    return json.dumps(result, indent=2, sort_keys=False) + "\n"


def to_text(result: dict) -> str:
    lines = ["agentlint %s  root=%s  yaml=%s  files=%d" % (
        result["agentlint_version"], result["root"], result["yaml_parser"], len(result["files"]))]
    for f in result["findings"]:
        loc = f["file"] + (":%d" % f["line"] if f.get("line") else "")
        lines.append("%-5s %s %s %s" % (f["severity"].upper(), f["id"], loc, f["message"]))
        if f.get("suggestion"):
            lines.append("      fix: %s" % f["suggestion"])
    s = result["summary"]
    lines.append("errors: %d, warnings: %d, info: %d" % (s["error"], s["warning"], s["info"]))
    for nc in result["not_checked"]:
        lines.append("not checked: %s" % nc)
    return "\n".join(lines) + "\n"


def catalogue_markdown() -> str:
    """Markdown catalogue, grouped by family, generated from the registry (kept in sync by a test)."""
    families = [("GN", "General file hygiene"), ("AG", "Agent definitions"), ("SK", "Skill files"),
                ("IN", "Instructions and prompt files"), ("CF", "MCP, hooks, environment, manifests"),
                ("XF", "Cross-file")]
    out = ["# agentlint rule catalogue", "",
           "Generated by `agentlint.py --list-rules --format markdown`. Do not edit by hand.", ""]
    for fam, title in families:
        out += ["## %s — %s" % (fam, title), "", "| ID | Severity | Tag | Runtime | Check | Source |", "|---|---|---|---|---|---|"]
        for rid in sorted(r for r in RULES if r.startswith(fam)):
            r = RULES[rid]
            out.append("| %s | %s | %s | %s | %s | %s |" % (rid, r.severity, r.tag, r.runtime, r.title, r.source))
        out.append("")
    return "\n".join(out)


def catalogue_text() -> str:
    return "\n".join("%s  %-7s %-6s %-7s %s" % (rid, r.severity, r.tag, r.runtime, r.title)
                     for rid, r in sorted(RULES.items())) + "\n"
```

- [ ] **Step 6: Write `cli.py`**

```python
"""Command-line interface."""
import argparse
import sys
import traceback

from . import __version__, discover
from .model import SEVERITIES


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="agentlint", description="Lint AI agent configuration files.")
    p.add_argument("paths", nargs="*", help="files or directories (default: discover from root)")
    p.add_argument("--root", help="repository root (default: git toplevel or cwd)")
    p.add_argument("--format", choices=["text", "json", "markdown"], default="text")
    p.add_argument("--kind", choices=discover.KINDS, help="force a kind for the given paths")
    p.add_argument("--exclude", action="append", default=[], metavar="GLOB", help="skip matching paths (repeatable)")
    p.add_argument("--no-collisions", action="store_true", help="skip cross-file (XF) checks")
    p.add_argument("--min-severity", choices=SEVERITIES, default="info")
    p.add_argument("--list-rules", action="store_true", help="print the rule catalogue and exit")
    p.add_argument("--version", action="version", version="agentlint %s" % __version__)
    return p


def main(argv=None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return 0 if e.code == 0 else 2
    from . import api, report
    if args.list_rules:
        api._load_rule_modules()
        sys.stdout.write(report.catalogue_markdown() if args.format == "markdown" else report.catalogue_text())
        return 0
    if args.format == "markdown":
        sys.stderr.write("--format markdown is only valid with --list-rules\n")
        return 2
    try:
        result = api.lint(args.root, args.paths, args.exclude, not args.no_collisions, args.min_severity, args.kind)
    except Exception:  # internal failure: report and exit 2
        traceback.print_exc()
        return 2
    sys.stdout.write(report.to_json(result) if args.format == "json" else report.to_text(result))
    return 1 if result["summary"]["error"] else 0
```

- [ ] **Step 7: Run the tests to verify they pass**

Run: `python3 -m unittest tests.test_cli -v`
Expected: PASS. Also run `python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py --list-rules | head -3` and confirm three rule lines print.

- [ ] **Step 8: Commit**

```bash
git add .claude/skills/linting-agent-config-files/scripts/agentlint_lib tests/test_cli.py
git commit -m "feat(agentlint): general checks, lint API, report formats and CLI

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_016TZTeGdK9WuTukJpPzZFxY"
```

---

## Rule-module conventions (Tasks 4–8)

Every `rules_*.py` module exposes `KINDS: Tuple[str, ...]` and `check(cf, ctx) -> List[Finding]` (for `rules_xf.py`: `check(ctx) -> List[Finding]`). `api._load_rule_modules()` registers them; rule modules never import `api` (avoids a circular import). Replace the Task 3 version of `_load_rule_modules` with:

```python
_RULE_MODULE_NAMES = ("rules_ag", "rules_sk", "rules_in", "rules_cf")


def _load_rule_modules():
    """Register per-kind and cross-file checkers once."""
    if RULE_MODULES or CROSS_FILE:
        return
    import importlib
    for name in _RULE_MODULE_NAMES:
        try:
            mod = importlib.import_module("." + name, __package__)
        except ImportError:
            continue  # TEMPORARY until Task 8: module not written yet
        register_checker(mod.KINDS, mod.check)
    try:
        from . import rules_xf
        register_cross_file(rules_xf.check)
    except ImportError:
        pass  # TEMPORARY until Task 8
```

and delete the `try/except ImportError` around the call in `lint()`. Task 8 removes both `TEMPORARY` guards so a missing module is a hard failure.

Fixture layout: `tests/fixtures/bad/` is one mini-repo containing every broken example; `tests/fixtures/good/` is one valid mini-repo. Tests run the linter with `root=BAD` or `root=GOOD` and assert `(rule id, root-relative path)` pairs. Rules whose trigger needs a very large or binary file (`GN003`, `GN004`, `AG010`, `SK006`, `IN005`) are tested from a temp directory instead of a committed fixture. Cloud-agent MCP (`CF005`, `CF016`) is tested by passing `force_kind="mcp-copilot-cloud"`.

---

### Task 4: AG rules — Copilot agents, Claude subagents, chatmodes

**Files:**
- Create: `.../agentlint_lib/rules_ag.py`
- Modify: `.../agentlint_lib/api.py` (`_load_rule_modules` as above)
- Create: `tests/test_rules_ag.py`, fixtures under `tests/fixtures/bad/` listed in Step 1

**Interfaces:**
- Consumes `toolnames.copilot_tool_problem`, `toolnames.claude_tool_problem`, `toolnames.split_claude_tools`, `model.Finding`, `ConfigFile.key_line`.
- Produces `rules_ag.KINDS`, `rules_ag.check`, constants `COPILOT_KEYS`, `VSCODE_ONLY_KEYS`, `CLAUDE_KEYS`, `CLAUDE_ENUMS`, `CLAUDE_MODEL_ALIASES` (reused by the `reviewing-agent-definitions` reference tables in Task 10).

- [ ] **Step 1: Write the fixtures**

| Path (under `tests/fixtures/bad/`) | Content | Expected IDs |
|---|---|---|
| `.github/agents/no-frontmatter.agent.md` | `# Just a body` | AG001 |
| `.github/agents/bad-yaml.agent.md` | `---\ndescription: x\n\tbad: tab\n---\nbody` | AG001 |
| `.github/agents/missing-description.agent.md` | `---\nname: md\ninfer: true\ntarget: web\ntool: read\n---\nbody` | AG002, AG005, AG022, AG017 |
| `.github/agents/bad name.agent.md` | `---\ndescription: d\ntools: Read, Grep\n---\n` (empty body) | AG013, AG024, AG016 |
| `.github/agents/bad-tools.agent.md` | `---\ndescription: d\ntools: ['read', 'nonsense', 'Bash']\nagents: ['x']\nmodel: sonnet\nhandoffs:\n  - label: only-label\nuser-invocable: "yes"\nmcp-servers:\n  srv:\n    command: npx\n---\nbody` | AG007 (×2), AG009, AG012, AG014, AG025, AG026, AG028 |
| `.github/agents/vscode-target.agent.md` | `---\ndescription: d\ntarget: vscode\nmetadata:\n  team: x\nmcp-servers:\n  srv:\n    type: local\n    command: npx\n    tools: ['*']\n---\nbody` | AG011 (×2) — and **no** AG012 |
| `.github/chatmodes/old.chatmode.md` | `---\ndescription: d\n---\nbody` | AG006 |
| `.claude/agents/bad-name.md` | `---\nname: Bad_Name\ndescription: d\ntools: Read, edit, nonsense\npermissionMode: yolo\nmodel: GPT-5\nbackground: "no"\nskills: alpha-skill\ntool-list: x\n---\nbody` | AG004, AG008 (warning), AG015, AG014, AG026, AG027, AG017 |
| `.claude/agents/no-name.md` | `---\ndescription: d\ntools:\n  - Read\n  - Grep\n---\nbody` | AG003, AG023 |
| `.claude/agents/no-tools-resolve.md` | `---\nname: no-tools-resolve\ndescription: d\ntools: read, edit\n---\nbody` | AG008 (error) |

- [ ] **Step 2: Write the failing tests**

`tests/test_rules_ag.py`:

```python
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
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `python3 -m unittest tests.test_rules_ag -v` — expected: assertions fail (no AG findings yet).

- [ ] **Step 4: Write `rules_ag.py`**

```python
"""AG rules: Copilot custom agents, Claude Code subagents and deprecated chatmodes."""
import re
from typing import Any, Dict, List

from . import toolnames
from .model import ConfigFile, Context, Finding

KINDS = ("copilot-agent", "claude-subagent", "chatmode")

COPILOT_KEYS = {"name", "description", "tools", "model", "target", "mcp-servers", "metadata", "argument-hint",
                "handoffs", "agents", "hooks", "user-invocable", "disable-model-invocation", "infer"}
VSCODE_ONLY_KEYS = ("handoffs", "argument-hint", "agents", "hooks")
COPILOT_BOOL_KEYS = ("user-invocable", "disable-model-invocation")
COPILOT_MCP_TYPES = {"local", "stdio", "http", "sse"}
COPILOT_FILENAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")
BODY_LIMIT = 30000

CLAUDE_KEYS = {"name", "description", "tools", "disallowedTools", "model", "permissionMode", "skills", "hooks",
               "memory", "effort", "color", "isolation", "background", "maxTurns", "mcpServers"}
CLAUDE_BOOL_KEYS = ("background",)
CLAUDE_ENUMS = {
    "permissionMode": {"default", "acceptEdits", "auto", "dontAsk", "bypassPermissions", "plan"},
    "memory": {"user", "project", "local"},
    "effort": {"low", "medium", "high", "max"},
    "color": {"red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"},
    "isolation": {"worktree"},
}
CLAUDE_MODEL_ALIASES = {"sonnet", "opus", "haiku", "inherit"}
CLAUDE_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
COPILOT_DISPLAY_MODEL_RE = re.compile(r"^(gpt|gemini|grok|o[0-9])", re.IGNORECASE)


def check(cf: ConfigFile, ctx: Context) -> List[Finding]:
    out: List[Finding] = []
    if cf.kind == "chatmode":
        out.append(Finding("AG006", cf.path, "deprecated .chatmode.md file", line=1, autofix_safe=True,
                           suggestion="rename to %s" % cf.name.replace(".chatmode.md", ".agent.md")))
    if not cf.fm_present:
        out.append(Finding("AG001", cf.path, "no YAML frontmatter block", line=1))
        return out
    if cf.fm_error or not isinstance(cf.frontmatter, dict):
        out.append(Finding("AG001", cf.path, cf.fm_error or "frontmatter is not a mapping", line=1))
        return out
    fm = cf.fm
    if not cf.body.strip():
        out.append(Finding("AG016", cf.path, "agent body is empty", line=cf.body_line))
    if cf.kind == "claude-subagent":
        out.extend(_claude(cf, fm, ctx))
    else:
        out.extend(_copilot(cf, fm))
    return out


def _bool_checks(cf: ConfigFile, fm: Dict[str, Any], keys) -> List[Finding]:
    return [Finding("AG026", cf.path, "%s must be true or false, got %r" % (k, fm[k]), line=cf.key_line(k))
            for k in keys if k in fm and not isinstance(fm[k], bool)]


def _copilot(cf: ConfigFile, fm: Dict[str, Any]) -> List[Finding]:
    out: List[Finding] = []
    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        out.append(Finding("AG002", cf.path, "description is required", line=cf.key_line("description") or 2))
    if not COPILOT_FILENAME_RE.match(cf.name):
        out.append(Finding("AG013", cf.path, "filename %r has characters outside . - _ a-z A-Z 0-9" % cf.name, line=1))
    if "infer" in fm:
        out.append(Finding("AG005", cf.path, "infer is retired", line=cf.key_line("infer"),
                           suggestion="replace with disable-model-invocation / user-invocable"))
    for k in fm:
        if k not in COPILOT_KEYS:
            out.append(Finding("AG017", cf.path, "unknown key %r for a Copilot agent" % k, line=cf.key_line(k)))
    target = fm.get("target")
    if target is not None and target not in ("vscode", "github-copilot"):
        out.append(Finding("AG022", cf.path, "target must be vscode or github-copilot, got %r" % target,
                           line=cf.key_line("target")))
    present = [k for k in VSCODE_ONLY_KEYS if k in fm]
    if present and target != "vscode":
        out.append(Finding("AG012", cf.path, "VS Code-only keys ignored on github.com: %s" % ", ".join(present),
                           line=cf.key_line(present[0])))
    if target == "vscode":
        for k in ("mcp-servers", "metadata"):
            if k in fm:
                out.append(Finding("AG011", cf.path, "%s is not used when target is vscode" % k, line=cf.key_line(k)))
    tools = fm.get("tools")
    if tools is not None and not isinstance(tools, list):
        hint = " (looks like a Claude subagent tools string)" if isinstance(tools, str) and "," in tools else ""
        out.append(Finding("AG024", cf.path, "tools must be a YAML list%s" % hint, line=cf.key_line("tools")))
        tools = []
    for t in tools or []:
        problem = toolnames.copilot_tool_problem(t)
        if problem:
            out.append(Finding("AG007", cf.path, problem, line=cf.key_line("tools")))
    if "agents" in fm:
        names = {str(t).lower() for t in (tools or [])}
        if not names & {"agent", "custom-agent", "*"}:
            out.append(Finding("AG009", cf.path, "agents is set but the agent tool is not in tools",
                               line=cf.key_line("agents"), suggestion="add 'agent' to tools"))
    if len(cf.body) > BODY_LIMIT:
        out.append(Finding("AG010", cf.path, "body is %d characters (limit %d)" % (len(cf.body), BODY_LIMIT),
                           line=cf.body_line))
    model = fm.get("model")
    if isinstance(model, str) and model.strip().lower() in CLAUDE_MODEL_ALIASES:
        out.append(Finding("AG014", cf.path, "model %r is a Claude Code alias; Copilot expects a model display name" % model,
                           line=cf.key_line("model")))
    handoffs = fm.get("handoffs")
    if isinstance(handoffs, list):
        for i, h in enumerate(handoffs):
            if not isinstance(h, dict) or not h.get("label") or not h.get("agent"):
                out.append(Finding("AG025", cf.path, "handoffs[%d] must have label and agent" % i,
                                   line=cf.key_line("handoffs")))
    elif handoffs is not None:
        out.append(Finding("AG025", cf.path, "handoffs must be a list", line=cf.key_line("handoffs")))
    out.extend(_bool_checks(cf, fm, COPILOT_BOOL_KEYS))
    servers = fm.get("mcp-servers")
    if isinstance(servers, dict):
        for sname, s in servers.items():
            problems = []
            if not isinstance(s, dict):
                problems.append("entry must be a mapping")
            else:
                if "tools" not in s:
                    problems.append("missing tools")
                if s.get("type") not in COPILOT_MCP_TYPES:
                    problems.append("type must be one of %s" % ", ".join(sorted(COPILOT_MCP_TYPES)))
            if problems:
                out.append(Finding("AG028", cf.path, "mcp-servers.%s: %s" % (sname, "; ".join(problems)),
                                   line=cf.key_line("mcp-servers")))
    elif servers is not None:
        out.append(Finding("AG028", cf.path, "mcp-servers must be a mapping of server name to config",
                           line=cf.key_line("mcp-servers")))
    return out


def _claude(cf: ConfigFile, fm: Dict[str, Any], ctx: Context) -> List[Finding]:
    out: List[Finding] = []
    name, desc = fm.get("name"), fm.get("description")
    if not isinstance(name, str) or not name.strip() or not isinstance(desc, str) or not desc.strip():
        out.append(Finding("AG003", cf.path, "name and description are required", line=2))
    elif not CLAUDE_NAME_RE.match(name):
        out.append(Finding("AG004", cf.path, "name %r must match ^[a-z0-9]+(-[a-z0-9]+)*$" % name, line=cf.key_line("name")))
    for k in fm:
        if k not in CLAUDE_KEYS:
            out.append(Finding("AG017", cf.path, "unknown key %r for a Claude subagent" % k, line=cf.key_line(k)))
    for key, allow_wild in (("tools", False), ("disallowedTools", True)):
        if key not in fm:
            continue
        entries, was_list = toolnames.split_claude_tools(fm[key])
        if was_list:
            out.append(Finding("AG023", cf.path, "%s is a YAML list; docs specify a comma-separated string" % key,
                               line=cf.key_line(key), autofix_safe=True,
                               suggestion="%s: %s" % (key, ", ".join(entries))))
        bad = [p for p in (toolnames.claude_tool_problem(e, allow_wild) for e in entries) if p]
        if bad:
            fatal = key == "tools" and len(bad) == len(entries)
            msg = "; ".join(bad)
            if fatal:
                msg = "no entry in tools resolves to a known tool (agent cannot launch): " + msg
            out.append(Finding("AG008", cf.path, msg, line=cf.key_line(key), severity="error" if fatal else "warning"))
    for field, allowed in CLAUDE_ENUMS.items():
        if field in fm and fm[field] not in allowed:
            out.append(Finding("AG015", cf.path, "%s must be one of %s, got %r" % (field, ", ".join(sorted(allowed)), fm[field]),
                               line=cf.key_line(field)))
    model = fm.get("model")
    if isinstance(model, str) and (" " in model.strip() or COPILOT_DISPLAY_MODEL_RE.match(model.strip())):
        out.append(Finding("AG014", cf.path, "model %r looks like a Copilot model name; Claude expects sonnet/opus/haiku/inherit or a full model id" % model,
                           line=cf.key_line("model")))
    out.extend(_bool_checks(cf, fm, CLAUDE_BOOL_KEYS))
    skills = fm.get("skills")
    if skills is not None and (not isinstance(skills, list) or not all(isinstance(s, str) for s in skills)):
        out.append(Finding("AG027", cf.path, "skills must be a YAML list of skill names", line=cf.key_line("skills")))
    # hooks in subagent frontmatter are validated by rules_cf.check_hooks_object (wired in Task 7)
    return out
```

- [ ] **Step 5: Update `api._load_rule_modules` as described in the conventions section, run the tests**

Run: `python3 -m unittest tests.test_rules_ag tests.test_cli -v` — expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/linting-agent-config-files/scripts/agentlint_lib tests/test_rules_ag.py tests/fixtures/bad
git commit -m "feat(agentlint): AG rules for Copilot agents, Claude subagents and chatmodes

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_016TZTeGdK9WuTukJpPzZFxY"
```

---

### Task 5: SK rules — SKILL.md files

**Files:**
- Create: `.../agentlint_lib/rules_sk.py`, `tests/test_rules_sk.py`, fixtures listed in Step 1

**Interfaces:**
- Produces `rules_sk.KINDS`, `rules_sk.check`, `rules_sk.SPEC_KEYS`, `rules_sk.CLAUDE_ONLY_KEYS`.

- [ ] **Step 1: Write the fixtures**

| Path (under `tests/fixtures/bad/`) | Content | Expected IDs |
|---|---|---|
| `.claude/skills/wrong-name/SKILL.md` | `---\nname: other-name\ndescription: d\nmetadata:\n  version: 1.0\nallowed-tools: [Read]\nargument-hint: x\nalowed_tools: x\ncompatibility: [a]\n---\nSee [ref](references/missing.md) and `scripts/gone.py`.` | SK004, SK014, SK019, SK010, SK011, SK009, SK007 (×2) |
| `.claude/skills/bad-name/SKILL.md` | `---\nname: Bad_Name\ndescription: d\n---\nbody` | SK003, SK004 |
| `.claude/skills/no-name/SKILL.md` | `---\ndescription: d\n---\nbody` | SK002 |
| `.claude/skills/no-description/SKILL.md` | `---\nname: no-description\n---\nbody` | SK005 |
| `.claude/skills/no-frontmatter/SKILL.md` | `# body only` | SK001 |
| `.github/skills/lowercase/skill.md` | `---\nname: lowercase\ndescription: d\n---\nbody` | SK012 |
| `docs/stray/SKILL.md` | `---\nname: stray\ndescription: d\n---\nbody` | SK013 |
| `.claude/skills/bad-scripts/SKILL.md` + `scripts/tool.py` (no shebang, mode 644) | valid frontmatter; script `print("x")\n` | SK008 |
| `.claude/skills/alpha-skill/SKILL.md` | `---\nname: alpha-skill\ndescription: d\ndisable-model-invocation: true\n---\nbody` (used by XF004/XF005/XF001 in Task 8) | SK010 only |

- [ ] **Step 2: Write the failing tests**

`tests/test_rules_sk.py` follows the same pattern as `test_rules_ag.py`: `setUpClass` runs `run_lint(root=BAD, collisions=False)`, an `expect()` helper, one test per row above, plus:

```python
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

    def test_sk007_counts_each_dead_path_once(self):
        n = [f for f in self.result["findings"] if f["id"] == "SK007" and f["file"] == ".claude/skills/wrong-name/SKILL.md"]
        self.assertEqual(len(n), 2)
```

- [ ] **Step 3: Run to verify failure, then write `rules_sk.py`**

```python
"""SK rules: SKILL.md files against agentskills.io plus the Copilot and Claude Code extensions."""
import os
import re
from typing import List

from .model import ConfigFile, Context, Finding

KINDS = ("skill",)
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SPEC_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
CLAUDE_ONLY_KEYS = {"disable-model-invocation", "user-invocable", "argument-hint", "hooks", "context", "agent",
                    "model", "paths", "effort", "once"}
LINK_RE = re.compile(r"\]\(([^)\s#?]+)")
PATH_RE = re.compile(r"`((?:scripts|references|assets)/[\w./-]+)`")
SCRIPT_EXTS = (".py", ".sh", ".bash", "")


def check(cf: ConfigFile, ctx: Context) -> List[Finding]:
    out: List[Finding] = []
    skill_dir = os.path.join(ctx.root, cf.dirname)
    dir_name = os.path.basename(cf.dirname)
    if cf.name != "SKILL.md":
        out.append(Finding("SK012", cf.path, "file must be named exactly SKILL.md (got %r)" % cf.name, line=1,
                           autofix_safe=True, suggestion="rename to SKILL.md"))
    parts = cf.path.split("/")
    if len(parts) < 3 or parts[-3] != "skills":
        out.append(Finding("SK013", cf.path, "not under <root>/skills/<name>/; no runtime discovers it here", line=1))
    if not cf.fm_present or cf.fm_error or not isinstance(cf.frontmatter, dict):
        msg = cf.fm_error or ("no YAML frontmatter" if not cf.fm_present else "frontmatter is not a mapping")
        out.append(Finding("SK001", cf.path, msg, line=1))
        return out
    fm = cf.fm
    name = fm.get("name")
    if name is None or (isinstance(name, str) and not name.strip()):
        out.append(Finding("SK002", cf.path, "name is required", line=2, autofix_safe=True, suggestion="name: %s" % dir_name))
    else:
        name = str(name)
        if len(name) > 64 or not NAME_RE.match(name):
            out.append(Finding("SK003", cf.path, "name %r must be 1-64 chars of lowercase letters, digits and single hyphens" % name,
                               line=cf.key_line("name")))
        if name != dir_name:
            out.append(Finding("SK004", cf.path, "name %r differs from directory %r" % (name, dir_name),
                               line=cf.key_line("name"), autofix_safe=True, suggestion="name: %s" % dir_name))
    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        out.append(Finding("SK005", cf.path, "description is required and must be a non-empty string",
                           line=cf.key_line("description") or 2))
    elif len(desc) > 1024:
        out.append(Finding("SK005", cf.path, "description is %d characters (limit 1024)" % len(desc), line=cf.key_line("description")))
    n_lines = cf.body_lines()
    if n_lines > 500:
        out.append(Finding("SK006", cf.path, "body is %d lines (recommended limit 500)" % n_lines, line=cf.body_line))
    compat = fm.get("compatibility")
    if compat is not None and (not isinstance(compat, str) or len(compat) > 500):
        out.append(Finding("SK009", cf.path, "compatibility must be a string of at most 500 characters", line=cf.key_line("compatibility")))
    claude_keys = [k for k in fm if k in CLAUDE_ONLY_KEYS]
    if claude_keys:
        out.append(Finding("SK010", cf.path, "Claude Code-only keys ignored by Copilot: %s" % ", ".join(claude_keys),
                           line=cf.key_line(claude_keys[0])))
    for k in fm:
        if k not in SPEC_KEYS and k not in CLAUDE_ONLY_KEYS:
            out.append(Finding("SK011", cf.path, "unknown key %r (possible typo)" % k, line=cf.key_line(k)))
    meta = fm.get("metadata")
    if meta is not None and (not isinstance(meta, dict)
                             or not all(isinstance(k, str) and isinstance(v, str) for k, v in meta.items())):
        out.append(Finding("SK014", cf.path, 'metadata should map strings to strings (quote numbers, e.g. version: "1.0")',
                           line=cf.key_line("metadata")))
    if isinstance(fm.get("allowed-tools"), list):
        out.append(Finding("SK019", cf.path, "allowed-tools is a YAML list; use a space-separated string",
                           line=cf.key_line("allowed-tools"), autofix_safe=True,
                           suggestion="allowed-tools: %s" % " ".join(str(x) for x in fm["allowed-tools"])))
    out.extend(_dead_paths(cf, skill_dir))
    out.extend(_scripts(cf, skill_dir))
    return out


def _dead_paths(cf: ConfigFile, skill_dir: str) -> List[Finding]:
    out, seen = [], set()
    for lineno, line in enumerate(cf.body.split("\n"), start=cf.body_line):
        for m in list(LINK_RE.finditer(line)) + list(PATH_RE.finditer(line)):
            target = m.group(1)
            if target.startswith(("http://", "https://", "mailto:", "/", "~")) or target in seen:
                continue
            seen.add(target)
            if not os.path.exists(os.path.normpath(os.path.join(skill_dir, target))):
                out.append(Finding("SK007", cf.path, "referenced path %r does not exist" % target, line=lineno))
    return out


def _scripts(cf: ConfigFile, skill_dir: str) -> List[Finding]:
    out = []
    sdir = os.path.join(skill_dir, "scripts")
    if not os.path.isdir(sdir):
        return out
    for fn in sorted(os.listdir(sdir)):
        p = os.path.join(sdir, fn)
        if not os.path.isfile(p) or os.path.splitext(fn)[1] not in SCRIPT_EXTS:
            continue
        try:
            with open(p, "rb") as fh:
                head = fh.read(2)
        except OSError:
            continue
        problems = []
        if head != b"#!":
            problems.append("no shebang")
        if not os.access(p, os.X_OK):
            problems.append("not executable")
        if problems:
            rel = "%s/scripts/%s" % (cf.dirname, fn)
            out.append(Finding("SK008", cf.path, "%s: %s" % (rel, ", ".join(problems)), autofix_safe=True,
                               suggestion="add a shebang and chmod +x %s" % rel))
    return out
```

- [ ] **Step 4: Run `python3 -m unittest tests.test_rules_sk -v`, expect PASS, commit**

```bash
git add .claude/skills/linting-agent-config-files/scripts/agentlint_lib/rules_sk.py tests/test_rules_sk.py tests/fixtures/bad
git commit -m "feat(agentlint): SK rules for SKILL.md files

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_016TZTeGdK9WuTukJpPzZFxY"
```

---

### Task 6: IN rules — instructions, prompts, AGENTS.md, CLAUDE.md, rules, commands, Cursor

**Files:**
- Create: `.../agentlint_lib/rules_in.py`, `tests/test_rules_in.py`, fixtures listed in Step 1

**Interfaces:**
- Produces `rules_in.KINDS`, `rules_in.check`, `rules_in.KNOWN_KEYS`, `rules_in.agent_names(ctx) -> Set[str]` (also used by `rules_xf`).

- [ ] **Step 1: Write the fixtures**

| Path (under `tests/fixtures/bad/`) | Content | Expected IDs |
|---|---|---|
| `.github/instructions/no-apply.instructions.md` | `---\ndescription: d\nfoo: bar\n---\nbody` | IN002, IN014 |
| `.github/instructions/list-apply.instructions.md` | `---\napplyTo: ["**/*.py"]\nexcludeAgent: reviewer\n---\nbody` | IN003, IN004 |
| `.github/instructions/broken.instructions.md` | `---\napplyTo: x\n\tbad: tab\n---\nbody` | IN001 |
| `.github/instructions/py-a.instructions.md` | `---\napplyTo: "**/*.py"\n---\nUse tabs.` | (XF006 in Task 8) |
| `.github/instructions/py-b.instructions.md` | `---\napplyTo: "**/*.py"\n---\nUse spaces.` | (XF006 in Task 8) |
| `docs/misplaced.instructions.md` | `---\napplyTo: "**"\n---\nbody` | IN011 |
| `.github/prompts/legacy.prompt.md` | `---\nmode: agent\ntools: read\n---\nbody` | IN018, IN019 |
| `.github/prompts/dangling.prompt.md` | `---\nagent: ghost\n---\nbody` | IN006 |
| `.github/copilot-instructions.md` | `---\ntitle: x\n---\n` (empty body) | IN012, IN017 |
| `pkg/AGENT.md` | `# rules` | IN010, IN009 |
| `AGENTS.md` | `# repo rules` | (XF010 in Task 8) |
| `CLAUDE.md` | `See @missing/file.md and email me at a@b.co.` | IN007 (×1) |
| `.claude/rules/bad.md` | `---\npaths: "src/**"\n---\nbody` | IN008 |
| `.claude/commands/alpha-skill.md` | `Run the thing.` | IN020 (XF005 in Task 8) |
| `.cursor/rules/old.md` | `body` | IN013 |

- [ ] **Step 2: Write `tests/test_rules_in.py`** (same pattern; one assertion group per row; `IN005` from a temp dir with `"x\n" * 1001` in `.github/copilot-instructions.md`; assert exactly one IN007 on `CLAUDE.md` so the e-mail address is not flagged).

- [ ] **Step 3: Write `rules_in.py`**

```python
"""IN rules: instruction files, prompt files, AGENTS.md, CLAUDE.md, Claude rules/commands and Cursor rules."""
import os
import re
from typing import List, Set

from .model import ConfigFile, Context, Finding

KINDS = ("copilot-instructions", "path-instructions", "prompt-file", "agents-md", "claude-md", "claude-rule",
         "claude-command", "cursor-rule")
FM_KINDS = ("path-instructions", "prompt-file", "claude-rule", "claude-command", "cursor-rule")
NO_FM_KINDS = ("copilot-instructions", "agents-md", "claude-md")
KNOWN_KEYS = {
    "path-instructions": {"applyTo", "description", "excludeAgent", "name"},
    "prompt-file": {"description", "name", "agent", "mode", "model", "tools", "argument-hint"},
    "claude-rule": {"paths"},
    "claude-command": {"description", "allowed-tools", "argument-hint", "model", "disable-model-invocation"},
    "cursor-rule": {"description", "globs", "alwaysApply"},
}
EXCLUDE_AGENTS = {"code-review", "cloud-agent"}
BUILTIN_AGENTS = {"agent", "ask", "edit", "plan"}
LONG_LINES = 1000
IMPORT_RE = re.compile(r"(?:^|(?<=\s))@((?:~|\.\.?)?/?[\w.-]+(?:/[\w.-]+)*)")


def agent_names(ctx: Context) -> Set[str]:
    """Names by which prompt files and handoffs can address custom agents."""
    names = set()
    for f in ctx.by_kind("copilot-agent", "claude-subagent", "chatmode"):
        n = f.fm.get("name")
        if isinstance(n, str) and n.strip():
            names.add(n.strip())
        names.add(re.sub(r"(\.agent|\.chatmode)?\.md$", "", f.name))
    return names


def check(cf: ConfigFile, ctx: Context) -> List[Finding]:
    out: List[Finding] = []
    kind = cf.kind
    if kind in FM_KINDS and cf.fm_present and (cf.fm_error or not isinstance(cf.frontmatter, dict)):
        out.append(Finding("IN001", cf.path, cf.fm_error or "frontmatter is not a mapping", line=1))
        return out
    if kind in NO_FM_KINDS and cf.fm_present:
        out.append(Finding("IN012", cf.path, "frontmatter present but no fields are defined for this file", line=1))
    if not cf.body.strip():
        out.append(Finding("IN017", cf.path, "file body is empty", line=cf.body_line))
    if cf.body_lines() > LONG_LINES:
        out.append(Finding("IN005", cf.path, "%d lines; long instruction files may be partly overlooked" % cf.body_lines(),
                           line=cf.body_line))
    fm = cf.fm
    for k in fm:
        if kind in KNOWN_KEYS and k not in KNOWN_KEYS[kind]:
            out.append(Finding("IN014", cf.path, "unknown key %r in a %s file" % (k, kind), line=cf.key_line(k)))
    if kind == "path-instructions":
        if not cf.path.startswith(".github/instructions/"):
            out.append(Finding("IN011", cf.path, "not under .github/instructions/; github.com will not discover it", line=1))
        if "applyTo" not in fm:
            out.append(Finding("IN002", cf.path, "no applyTo; the file is never attached automatically", line=2))
        elif isinstance(fm["applyTo"], list):
            out.append(Finding("IN003", cf.path, "applyTo is a YAML list; documented form is a comma-separated string",
                               line=cf.key_line("applyTo"), autofix_safe=True,
                               suggestion='applyTo: "%s"' % ", ".join(str(x) for x in fm["applyTo"])))
        elif not isinstance(fm["applyTo"], str):
            out.append(Finding("IN003", cf.path, "applyTo must be a string", line=cf.key_line("applyTo")))
        ex = fm.get("excludeAgent")
        if ex is not None and str(ex) not in EXCLUDE_AGENTS:
            out.append(Finding("IN004", cf.path, "excludeAgent must be code-review or cloud-agent, got %r" % ex,
                               line=cf.key_line("excludeAgent")))
    elif kind == "prompt-file":
        if "mode" in fm:
            out.append(Finding("IN018", cf.path, "mode is legacy; use agent", line=cf.key_line("mode"),
                               autofix_safe=True, suggestion="agent: %s" % fm["mode"]))
        if "tools" in fm and not isinstance(fm["tools"], list):
            out.append(Finding("IN019", cf.path, "tools must be a YAML list", line=cf.key_line("tools")))
        agent = fm.get("agent", fm.get("mode"))
        if isinstance(agent, str) and agent not in BUILTIN_AGENTS and agent not in agent_names(ctx):
            out.append(Finding("IN006", cf.path, "agent %r is neither built-in nor defined by a custom agent" % agent,
                               line=cf.key_line("agent") or cf.key_line("mode")))
    elif kind == "agents-md":
        if cf.name == "AGENT.md":
            out.append(Finding("IN010", cf.path, "legacy singular AGENT.md", line=1, autofix_safe=True, suggestion="rename to AGENTS.md"))
        if cf.dirname:
            out.append(Finding("IN009", cf.path, "nested AGENTS.md; VS Code needs chat.useNestedAgentsMdFiles", line=1))
    elif kind == "claude-md":
        out.extend(_imports(cf, ctx))
    elif kind == "claude-rule":
        paths = fm.get("paths")
        if "paths" in fm and (not isinstance(paths, list) or not all(isinstance(p, str) for p in paths)):
            out.append(Finding("IN008", cf.path, "paths must be a YAML list of glob strings", line=cf.key_line("paths")))
    elif kind == "claude-command":
        out.append(Finding("IN020", cf.path, "legacy .claude/commands file; prefer a skill", line=1))
    elif kind == "cursor-rule" and not cf.name.endswith(".mdc"):
        out.append(Finding("IN013", cf.path, "Cursor rules must use the .mdc extension", line=1))
    return out


def _imports(cf: ConfigFile, ctx: Context) -> List[Finding]:
    out, in_fence = [], False
    base = os.path.join(ctx.root, cf.dirname)
    for lineno, line in enumerate(cf.body.split("\n"), start=cf.body_line):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        clean = re.sub(r"`[^`]*`", "", line)
        for m in IMPORT_RE.finditer(clean):
            target = m.group(1)
            if "/" not in target and "." not in target:
                continue  # @handle mentions, not file imports
            p = os.path.expanduser(target) if target.startswith("~") else os.path.join(base, target)
            if not os.path.exists(p):
                out.append(Finding("IN007", cf.path, "@import target %r does not exist" % target, line=lineno))
    return out
```

- [ ] **Step 4: Run `python3 -m unittest tests.test_rules_in -v`, expect PASS, commit**

```bash
git add .claude/skills/linting-agent-config-files/scripts/agentlint_lib/rules_in.py tests/test_rules_in.py tests/fixtures/bad
git commit -m "feat(agentlint): IN rules for instruction, prompt and memory files

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_016TZTeGdK9WuTukJpPzZFxY"
```

---

### Task 7: CF rules — MCP, hooks, setup steps, plugin manifests

**Files:**
- Create: `.../agentlint_lib/rules_cf.py`, `tests/test_rules_cf.py`, fixtures listed in Step 1
- Modify: `rules_ag._claude` and `rules_sk.check` to call `rules_cf.check_hooks_object` when a `hooks` key is present

**Interfaces:**
- Produces `rules_cf.KINDS`, `rules_cf.check`, `rules_cf.check_hooks_object(hooks, path, root, in_settings=False, line=None) -> List[Finding]`, `rules_cf.HOOK_EVENTS`.

- [ ] **Step 1: Write the fixtures**

| Path (under `tests/fixtures/bad/`) | Content | Expected IDs |
|---|---|---|
| `.mcp.json` | servers `a` (`url` only, header `Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456`), `b` (`type: sse`, `url`, `tools: ["*"]`, `bogus: 1`), `c` (`type: stdio`, no command, `env: {"X": "${X}"}`), `d` (`type: stdio`, `command: ./bin/missing-server`) | CF003 a, CF006 a, CF004 b, CF013 b, CF014 b, CF012 c, CF011 c, CF010 d |
| `.vscode/mcp.json` | `{"mcpServers": {}}` | CF002 |
| `sub/.vscode/mcp.json` | `{"servers": {"s": {"type": "http", "url": "https://x", "headers": {"A": "${input:tok}"}}, "legacy": {"type": "sse", "url": "https://x/sse"}}}` | CF015, CF022 |
| `.github/mcp.json` | `{"mcpServers": ` (truncated) | CF001 |
| `cloud-mcp.json` (not auto-discovered) | `{"mcpServers": {"s": {"command": "npx", "env": {"API_TOKEN": "MY_TOKEN"}}}}` | CF005, CF016 via `force_kind` |
| `.claude/settings.json` | `{"hooks": {"OnSave": [], "PreToolUse": [{"hooks": [{"type": "command"}]}], "Stop": [{"hooks": [{"type": "command", "command": "./hooks/missing.sh", "if": "Bash", "once": true}]}]}}` | CF007 (×2), CF018, CF017, CF010 |
| `.github/workflows/copilot-setup-steps.yml` | `jobs:` with `copilot-setup-steps` (has `runs-on`, `steps`, `strategy`) and a second job `other`; no `on` | CF008 (×2), CF019 |
| `.claude-plugin/plugin.json` + `.claude-plugin/skills/x/SKILL.md` | `{}` | CF020, CF009 |
| `.claude-plugin/marketplace.json` | `{"plugins": [{"name": "p"}]}` | CF020, CF021 |
| `.claude/agents/hooky.md` | valid subagent with `hooks:\n  Nope:\n    - hooks:\n        - type: command\n          command: echo` | CF007 (via wiring) |

- [ ] **Step 2: Write `tests/test_rules_cf.py`** (same pattern; the cloud case is `run_lint(root=BAD, paths=["cloud-mcp.json"], force_kind="mcp-copilot-cloud", collisions=False)`).

- [ ] **Step 3: Write `rules_cf.py`**

```python
"""CF rules: MCP configs, Claude hooks, Copilot setup steps, plugin and marketplace manifests."""
import os
import re
from typing import Any, Dict, List, Optional

from .model import ConfigFile, Context, Finding

KINDS = ("mcp-claude", "mcp-vscode", "mcp-copilot-cli", "mcp-copilot-cloud", "settings-hooks",
         "copilot-setup-steps", "plugin-manifest", "marketplace-manifest")
MCP_KINDS = ("mcp-claude", "mcp-vscode", "mcp-copilot-cli", "mcp-copilot-cloud")
TOP_KEY = {"mcp-claude": "mcpServers", "mcp-vscode": "servers", "mcp-copilot-cli": "mcpServers",
           "mcp-copilot-cloud": "mcpServers"}
SERVER_KEYS = {"type", "command", "args", "env", "envFile", "url", "headers", "tools", "cwd", "dev", "gallery",
               "version", "timeout", "oauth"}
REMOTE_TYPES = {"http", "sse"}
CLOUD_TYPES = {"local", "stdio", "http", "sse"}
SECRET_KEY_RE = re.compile(r"(token|secret|password|passwd|api[_-]?key|authorization)", re.I)
SECRET_VALUE_RE = re.compile(
    r"^(sk-[A-Za-z0-9_-]{10,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|gh[ousr]_[A-Za-z0-9]{20,}"
    r"|xox[abp]-[A-Za-z0-9-]{10,}|AKIA[A-Z0-9]{16}|AIza[A-Za-z0-9_-]{30,}|Bearer\s+\S{20,})")
VAR_RE = re.compile(r"\$\{([^}]*)\}")
HOOK_EVENTS = {
    "PreToolUse", "PostToolUse", "PostToolUseFailure", "PermissionRequest", "Notification", "UserPromptSubmit",
    "Stop", "SubagentStart", "SubagentStop", "PreCompact", "SessionStart", "SessionEnd", "Setup", "TeammateIdle",
    "TaskCompleted", "ConfigChange", "WorktreeCreate", "WorktreeRemove", "InstructionsLoaded", "Elicitation",
    "ElicitationResult", "CwdChanged", "FileChanged",
}
TOOL_EVENTS = {"PreToolUse", "PostToolUse", "PostToolUseFailure", "PermissionRequest"}
HANDLER_REQUIRED = {"command": "command", "http": "url", "prompt": "prompt", "agent": "prompt"}
SETUP_JOB_KEYS = {"name", "runs-on", "steps", "permissions", "timeout-minutes", "services", "container", "snapshot", "env"}


def check(cf: ConfigFile, ctx: Context) -> List[Finding]:
    if cf.data_error:
        return [Finding("CF001", cf.path, cf.data_error, line=1)]
    if cf.kind in MCP_KINDS:
        return _mcp(cf, ctx)
    if cf.kind == "settings-hooks":
        data = cf.data if isinstance(cf.data, dict) else {}
        return check_hooks_object(data["hooks"], cf.path, ctx.root, in_settings=True) if "hooks" in data else []
    if cf.kind == "copilot-setup-steps":
        return _setup_steps(cf)
    if cf.kind == "plugin-manifest":
        return _plugin(cf, ctx)
    return _marketplace(cf)


def _mcp(cf: ConfigFile, ctx: Context) -> List[Finding]:
    out: List[Finding] = []
    data = cf.data
    if not isinstance(data, dict):
        return [Finding("CF001", cf.path, "top level must be a JSON object", line=1)]
    want = TOP_KEY[cf.kind]
    other = "servers" if want == "mcpServers" else "mcpServers"
    if want not in data:
        if other in data:
            out.append(Finding("CF002", cf.path, "uses %r; this file needs %r" % (other, want), line=1,
                               autofix_safe=True, suggestion="rename the key to %s" % want))
        else:
            out.append(Finding("CF002", cf.path, "missing top-level %r" % want, line=1))
        return out
    inputs = {i.get("id") for i in data.get("inputs", []) if isinstance(i, dict)}
    servers = data[want]
    if not isinstance(servers, dict):
        return [Finding("CF001", cf.path, "%s must be an object" % want, line=1)]
    cloud = cf.kind == "mcp-copilot-cloud"
    for name, s in servers.items():
        if not isinstance(s, dict):
            out.append(Finding("CF012", cf.path, "%s: server entry must be an object" % name))
            continue
        stype, has_url, has_cmd = s.get("type"), "url" in s, "command" in s
        if cf.kind == "mcp-claude" and has_url and stype is None:
            out.append(Finding("CF003", cf.path, "%s: url without type; Claude Code reads it as stdio and skips it" % name,
                               autofix_safe=True, suggestion='add "type": "http"'))
        if cloud:
            probs = []
            if "tools" not in s:
                probs.append("missing tools")
            if stype not in CLOUD_TYPES:
                probs.append("type must be one of %s" % ", ".join(sorted(CLOUD_TYPES)))
            if probs:
                out.append(Finding("CF005", cf.path, "%s: %s" % (name, "; ".join(probs))))
        is_remote = stype in REMOTE_TYPES or (stype is None and has_url and not has_cmd)
        if is_remote and not has_url:
            out.append(Finding("CF012", cf.path, "%s: remote server (%s) missing url" % (name, stype)))
        if not is_remote and not has_cmd:
            out.append(Finding("CF012", cf.path, "%s: stdio server missing command" % name))
        if stype == "sse":
            out.append(Finding("CF004" if cf.kind == "mcp-claude" else "CF022", cf.path,
                               "%s: type sse is deprecated; use http" % name))
        if cf.kind == "mcp-claude" and "tools" in s:
            out.append(Finding("CF013", cf.path, "%s: tools allowlist is a Copilot extension; Claude Code behaviour is undocumented" % name))
        for k in s:
            if k not in SERVER_KEYS:
                out.append(Finding("CF014", cf.path, "%s: unknown key %r" % (name, k)))
        out.extend(_secrets_and_vars(cf, name, s, inputs, cloud))
        cmd = s.get("command")
        if isinstance(cmd, str) and "/" in cmd and not os.path.isabs(cmd) and not cmd.startswith("$"):
            p = os.path.join(ctx.root, cmd)
            if not os.path.isfile(p) or not os.access(p, os.X_OK):
                out.append(Finding("CF010", cf.path, "%s: command %r is missing or not executable" % (name, cmd)))
    return out


def _secrets_and_vars(cf: ConfigFile, name: str, s: Dict[str, Any], inputs, cloud: bool) -> List[Finding]:
    out: List[Finding] = []
    for section in ("env", "headers"):
        m = s.get(section)
        if not isinstance(m, dict):
            continue
        for k, v in m.items():
            if not isinstance(v, str):
                continue
            is_ref = "$" in v or (cloud and "COPILOT_MCP_" in v)
            if not is_ref and (SECRET_VALUE_RE.match(v) or (SECRET_KEY_RE.search(k) and len(v) >= 8)):
                out.append(Finding("CF006", cf.path, "%s: %s.%s holds a literal secret-looking value" % (name, section, k),
                                   suggestion="reference a variable or input instead of the literal value"))
            if cloud and SECRET_KEY_RE.search(k) and "COPILOT_MCP_" not in v:
                out.append(Finding("CF016", cf.path, "%s: %s.%s must reference a COPILOT_MCP_-prefixed secret" % (name, section, k)))
            for ref in VAR_RE.findall(v):
                if ref.startswith("input:"):
                    if cf.kind == "mcp-vscode" and ref[6:] not in inputs:
                        out.append(Finding("CF015", cf.path, "%s: ${%s} is not declared in inputs" % (name, ref)))
                elif ref.startswith(("env:", "workspaceFolder", "userHome")):
                    continue
                elif ":-" not in ref and cf.kind in ("mcp-claude", "mcp-copilot-cli"):
                    out.append(Finding("CF011", cf.path, "%s: ${%s} has no default; the server fails to start when unset" % (name, ref)))
    return out


def check_hooks_object(hooks: Any, path: str, root: str, in_settings: bool = False,
                       line: Optional[int] = None) -> List[Finding]:
    """Validate a Claude Code hooks mapping (settings, plugin hooks.json, subagent or skill frontmatter)."""
    out: List[Finding] = []
    if not isinstance(hooks, dict):
        return [Finding("CF007", path, "hooks must be an object keyed by event name", line=line)]
    for event, groups in hooks.items():
        if event not in HOOK_EVENTS:
            out.append(Finding("CF007", path, "unknown hook event %r" % event, line=line))
            continue
        if not isinstance(groups, list):
            out.append(Finding("CF007", path, "%s must be a list of matcher groups" % event, line=line))
            continue
        for gi, g in enumerate(groups):
            if not isinstance(g, dict) or not isinstance(g.get("hooks"), list):
                out.append(Finding("CF007", path, "%s[%d] must be an object with a hooks list" % (event, gi), line=line))
                continue
            for hi, h in enumerate(g["hooks"]):
                where = "%s[%d].hooks[%d]" % (event, gi, hi)
                if not isinstance(h, dict):
                    out.append(Finding("CF007", path, "%s must be an object" % where, line=line))
                    continue
                t = h.get("type")
                if t not in HANDLER_REQUIRED:
                    out.append(Finding("CF007", path, "%s: type must be one of %s" % (where, ", ".join(sorted(HANDLER_REQUIRED))), line=line))
                    continue
                if not h.get(HANDLER_REQUIRED[t]):
                    out.append(Finding("CF007", path, "%s: type %s requires %s" % (where, t, HANDLER_REQUIRED[t]), line=line))
                if "if" in h and event not in TOOL_EVENTS:
                    out.append(Finding("CF018", path, "%s: if is only evaluated on tool events" % where, line=line))
                if "once" in h and in_settings:
                    out.append(Finding("CF017", path, "%s: once is only honoured in skill frontmatter hooks" % where, line=line))
                cmd = h.get("command")
                if t == "command" and isinstance(cmd, str) and cmd.split():
                    first = cmd.split()[0]
                    for prefix in ("$CLAUDE_PROJECT_DIR/", "${CLAUDE_PROJECT_DIR}/", "${CLAUDE_PLUGIN_ROOT}/"):
                        first = first.replace(prefix, "")
                    if "/" in first and not os.path.isabs(first) and not first.startswith("$"):
                        p = os.path.join(root, first)
                        if not os.path.isfile(p) or not os.access(p, os.X_OK):
                            out.append(Finding("CF010", path, "%s: script %r is missing or not executable" % (where, first), line=line))
    return out


def _setup_steps(cf: ConfigFile) -> List[Finding]:
    out: List[Finding] = []
    data = cf.data
    if not isinstance(data, dict):
        return [Finding("CF001", cf.path, "workflow must be a mapping", line=1)]
    if "on" not in data and True not in data:  # YAML 1.1 parses a bare `on` key as True
        out.append(Finding("CF019", cf.path, "no on: triggers; add workflow_dispatch to test the environment manually", line=1))
    jobs = data.get("jobs")
    if not isinstance(jobs, dict) or "copilot-setup-steps" not in jobs:
        out.append(Finding("CF008", cf.path, "jobs must contain a job named copilot-setup-steps", line=1))
        return out
    extra = [k for k in jobs if k != "copilot-setup-steps"]
    if extra:
        out.append(Finding("CF008", cf.path, "only the copilot-setup-steps job runs; extra jobs ignored: %s" % ", ".join(extra)))
    job = jobs["copilot-setup-steps"]
    if not isinstance(job, dict):
        return out + [Finding("CF008", cf.path, "copilot-setup-steps must be a mapping")]
    for k in job:
        if k not in SETUP_JOB_KEYS:
            out.append(Finding("CF008", cf.path, "unsupported job key %r (supported: %s)" % (k, ", ".join(sorted(SETUP_JOB_KEYS)))))
    if "steps" not in job:
        out.append(Finding("CF008", cf.path, "copilot-setup-steps has no steps"))
    return out


def _plugin(cf: ConfigFile, ctx: Context) -> List[Finding]:
    out: List[Finding] = []
    data = cf.data if isinstance(cf.data, dict) else {}
    if not data.get("name"):
        out.append(Finding("CF020", cf.path, "plugin manifest missing name", line=1))
    if cf.path.endswith(".claude-plugin/plugin.json"):
        mdir = os.path.join(ctx.root, cf.dirname)
        misplaced = [d for d in ("agents", "skills", "commands", "hooks") if os.path.isdir(os.path.join(mdir, d))]
        if misplaced:
            out.append(Finding("CF009", cf.path, "component directories inside .claude-plugin/: %s (move to the plugin root)" % ", ".join(misplaced)))
    return out


def _marketplace(cf: ConfigFile) -> List[Finding]:
    out: List[Finding] = []
    data = cf.data if isinstance(cf.data, dict) else {}
    if not data.get("name"):
        out.append(Finding("CF020", cf.path, "marketplace manifest missing name", line=1))
    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        return out + [Finding("CF021", cf.path, "plugins must be a list", line=1)]
    for i, p in enumerate(plugins):
        if not isinstance(p, dict) or not p.get("name") or not p.get("source"):
            out.append(Finding("CF021", cf.path, "plugins[%d] must have name and source" % i))
    return out
```

- [ ] **Step 4: Wire hooks validation into agents and skills**

In `rules_ag._claude`, replace the trailing comment with:

```python
    if "hooks" in fm:
        from . import rules_cf
        out.extend(rules_cf.check_hooks_object(fm["hooks"], cf.path, ctx.root, line=cf.key_line("hooks")))
```

In `rules_sk.check`, before `_dead_paths`:

```python
    if "hooks" in fm:
        from . import rules_cf
        out.extend(rules_cf.check_hooks_object(fm["hooks"], cf.path, ctx.root, line=cf.key_line("hooks")))
```

- [ ] **Step 5: Run `python3 -m unittest tests.test_rules_cf tests.test_rules_ag -v`, expect PASS, commit**

```bash
git add .claude/skills/linting-agent-config-files/scripts/agentlint_lib tests/test_rules_cf.py tests/fixtures/bad
git commit -m "feat(agentlint): CF rules for MCP, hooks, setup steps and plugin manifests

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_016TZTeGdK9WuTukJpPzZFxY"
```

---

### Task 8: XF rules, the good fixture, and rule-coverage test

**Files:**
- Create: `.../agentlint_lib/rules_xf.py`, `tests/test_rules_xf.py`, `tests/test_good_fixture.py`, `tests/fixtures/good/**`
- Modify: `api._load_rule_modules` (remove both `TEMPORARY` guards), `tests/fixtures/bad/` additions listed in Step 1

**Interfaces:**
- Produces `rules_xf.check(ctx)`, `rules_xf.DISCOVERY_ORDER`.

- [ ] **Step 1: Add the cross-file bad fixtures**

| Path (under `tests/fixtures/bad/`) | Content | Expected IDs |
|---|---|---|
| `.github/skills/alpha-skill/SKILL.md` | `---\nname: alpha-skill\ndescription: d\n---\nbody` | XF001 on `.claude/skills/alpha-skill/SKILL.md` (`.github` wins) |
| `.github/agents/twin.agent.md` | `---\ndescription: d\ntools: ['read']\nhandoffs:\n  - label: Go\n    agent: nobody\n---\nBody A` | XF003, (AG012) |
| `.claude/agents/twin.md` | `---\nname: twin\ndescription: d\ntools: Read\nskills:\n  - alpha-skill\n  - ghost-skill\n---\nBody B` | XF002 (message contains "bodies differ"), XF003, XF004 |
| `.claude/skills/beta-skill/SKILL.md` | `---\nname: beta-skill\ndescription: d\nagent: nobody\n---\nbody` | XF003 (and SK010) |
| already present: `.claude/commands/alpha-skill.md` | | XF005 |
| already present: `py-a` / `py-b` instruction files | | XF006 on `py-a` |
| already present: root `CLAUDE.md` + `AGENTS.md` | | XF010 on `CLAUDE.md` |

- [ ] **Step 2: Write the good fixture** (`tests/fixtures/good/`)

```
.github/agents/reviewer.agent.md          description + tools ['read','search','execute'] + handoffs → agent: agent; body B
.claude/agents/reviewer.md                name: reviewer, tools: Read, Grep, Glob, Bash(python3:*), model: inherit, skills: [alpha-skill]; body B (identical)
.claude/skills/alpha-skill/SKILL.md       name/description/metadata {version: "1.0.0"}; links references/notes.md and `scripts/run.sh`
.claude/skills/alpha-skill/references/notes.md
.claude/skills/alpha-skill/scripts/run.sh   "#!/bin/sh\necho ok\n", chmod +x
.claude/skills/beta-skill/SKILL.md
.claude/skills/gamma-skill/SKILL.md
.github/copilot-instructions.md           plain body, no frontmatter
.github/instructions/python.instructions.md   applyTo: "**/*.py"
.github/prompts/review.prompt.md          agent: reviewer
AGENTS.md                                 plain body
CLAUDE.md                                 "@AGENTS.md" on its own line
.mcp.json                                 {"mcpServers": {"fs": {"type": "stdio", "command": "npx", "args": ["-y", "x"], "env": {"LOG": "${LOG_LEVEL:-info}"}}}}
.vscode/mcp.json                          {"inputs": [{"id": "token", "type": "promptString", "password": true}], "servers": {"api": {"type": "http", "url": "https://example.com/mcp", "headers": {"Authorization": "Bearer ${input:token}"}}}}
.claude/settings.json                     {"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "echo checking"}]}]}}
.github/workflows/copilot-setup-steps.yml on: workflow_dispatch; one job copilot-setup-steps with runs-on, permissions, steps (checkout + setup-python)
```

- [ ] **Step 3: Write the tests**

`tests/test_rules_xf.py` (same `expect` pattern, `run_lint(root=BAD)` with collisions on) asserts the rows in Step 1 and that the XF002 message on `.claude/agents/twin.md` contains `"bodies differ"`.

`tests/test_good_fixture.py`:

```python
import os
import unittest
from unittest import mock

from tests.helpers import GOOD, ids, run_lint
from tests.helpers import import_lib

lib = import_lib()
from agentlint_lib import model  # noqa: E402

EXPECTED_INFO = {("AG012", ".github/agents/reviewer.agent.md"), ("XF002", ".claude/agents/reviewer.md")}
# rules exercised from temp dirs or with --kind rather than from tests/fixtures/bad
TEMP_TESTED = {"GN001", "GN002", "GN003", "GN004", "AG010", "SK006", "IN005", "CF005", "CF016"}


class GoodFixtureTests(unittest.TestCase):
    def check(self):
        r = run_lint(root=GOOD)
        self.assertEqual(r["summary"]["error"], 0, r["findings"])
        self.assertEqual(r["summary"]["warning"], 0, r["findings"])
        self.assertEqual(ids(r), EXPECTED_INFO)
        self.assertEqual(len(r["files"]), 15)

    def test_with_default_parser(self):
        self.check()

    def test_with_builtin_parser(self):
        with mock.patch.dict(os.environ, {"AGENTLINT_YAML": "builtin"}):
            self.check()


class CoverageTests(unittest.TestCase):
    def test_every_auto_rule_has_a_bad_fixture(self):
        from tests.helpers import BAD
        seen = {rid for rid, _ in ids(run_lint(root=BAD))}
        seen |= {rid for rid, _ in ids(run_lint(root=BAD, paths=["cloud-mcp.json"], force_kind="mcp-copilot-cloud"))}
        auto = {rid for rid, r in model.RULES.items() if r.tag == "auto"}
        self.assertEqual(auto - seen - TEMP_TESTED, set())
```

- [ ] **Step 4: Write `rules_xf.py`**

```python
"""XF rules: name collisions, dangling references and coexistence problems across files."""
import os
import re
from collections import defaultdict
from typing import List

from .model import ConfigFile, Context, Finding
from .rules_in import BUILTIN_AGENTS, agent_names

DISCOVERY_ORDER = {".github": 0, ".agents": 1, ".claude": 2}  # Copilot skill precedence, first found wins


def _skill_name(f: ConfigFile) -> str:
    n = f.fm.get("name")
    return n.strip() if isinstance(n, str) and n.strip() else os.path.basename(f.dirname)


def _skill_root(f: ConfigFile) -> str:
    return "/".join(f.path.split("/")[:-3])


def _agent_name(f: ConfigFile) -> str:
    n = f.fm.get("name")
    return n.strip() if isinstance(n, str) and n.strip() else re.sub(r"(\.agent|\.chatmode)?\.md$", "", f.name)


def check(ctx: Context) -> List[Finding]:
    out: List[Finding] = []
    skills = ctx.by_kind("skill")
    agents = ctx.by_kind("copilot-agent", "claude-subagent", "chatmode")
    by_skill = defaultdict(list)
    for f in skills:
        by_skill[_skill_name(f)].append(f)
    for name, fs in by_skill.items():
        if len({_skill_root(f) for f in fs}) > 1:
            order = sorted(fs, key=lambda f: (DISCOVERY_ORDER.get(_skill_root(f), 99), f.path))
            for f in order[1:]:
                out.append(Finding("XF001", f.path, "skill %r is also defined at %s, which is found first and wins" % (name, order[0].path), line=1))
    by_agent = defaultdict(list)
    for f in agents:
        by_agent[_agent_name(f)].append(f)
    for name, fs in by_agent.items():
        gh = [f for f in fs if f.kind == "copilot-agent"]
        cl = [f for f in fs if f.kind == "claude-subagent"]
        if gh and cl:
            same = gh[0].body.strip() == cl[0].body.strip()
            out.append(Finding("XF002", cl[0].path, "agent %r is also defined at %s; Copilot surfaces use the .github copy%s"
                               % (name, gh[0].path, "" if same else " — bodies differ, review manually"), line=1))
    skill_names = set(by_skill)
    all_agents = agent_names(ctx) | BUILTIN_AGENTS
    disabled = {n for n, fs in by_skill.items() if any(f.fm.get("disable-model-invocation") is True for f in fs)}
    for f in agents:
        if f.kind == "claude-subagent":
            for s in f.fm.get("skills") or []:
                if not isinstance(s, str):
                    continue
                if s not in skill_names:
                    out.append(Finding("XF003", f.path, "skills preloads %r but no such skill exists" % s, line=f.key_line("skills")))
                elif s in disabled:
                    out.append(Finding("XF004", f.path, "skills preloads %r which has disable-model-invocation: true" % s, line=f.key_line("skills")))
        else:
            for h in f.fm.get("handoffs") or []:
                if isinstance(h, dict) and isinstance(h.get("agent"), str) and h["agent"] not in all_agents:
                    out.append(Finding("XF003", f.path, "handoff targets agent %r which does not exist" % h["agent"], line=f.key_line("handoffs")))
    for f in skills:
        a = f.fm.get("agent")
        if isinstance(a, str) and a not in all_agents:
            out.append(Finding("XF003", f.path, "agent %r does not exist" % a, line=f.key_line("agent")))
    for c in ctx.by_kind("claude-command"):
        if c.name[:-3] in skill_names:
            out.append(Finding("XF005", c.path, "command %r shares its name with a skill; the skill wins" % c.name[:-3], line=1))
    globs = []
    for f in ctx.by_kind("path-instructions"):
        a = f.fm.get("applyTo")
        if isinstance(a, str):
            globs += [(g.strip(), f.path) for g in a.split(",") if g.strip()]
    for f in ctx.by_kind("claude-rule"):
        globs += [(g.strip(), f.path) for g in (f.fm.get("paths") or []) if isinstance(g, str)]
    reported = set()
    for i, (g1, p1) in enumerate(globs):
        for g2, p2 in globs[i + 1:]:
            if p1 != p2 and (g1 == g2 or g1 in ("**", "**/*") or g2 in ("**", "**/*")) and (p1, p2) not in reported:
                reported.add((p1, p2))
                out.append(Finding("XF006", p1, "applyTo/paths %r overlaps %r in %s; check the two files agree" % (g1, g2, p2)))
    claude_by_dir = {f.dirname: f for f in ctx.by_kind("claude-md") if f.name == "CLAUDE.md"}
    for a in ctx.by_kind("agents-md"):
        c = claude_by_dir.get(a.dirname)
        if c is not None and "@AGENTS.md" not in c.body and "@./AGENTS.md" not in c.body and "CLAUDE.md" not in a.body:
            out.append(Finding("XF010", c.path, "CLAUDE.md and AGENTS.md coexist in %s without importing each other" % (a.dirname or "the root"), line=1))
    return out
```

- [ ] **Step 5: Make rule-module loading strict**

In `api._load_rule_modules`, remove the `try/except ImportError` around both the loop and the `rules_xf` import (a missing module is now a bug, surfaced as exit code 2).

- [ ] **Step 6: Run the whole suite twice**

```bash
python3 -m unittest discover -s tests -v
AGENTLINT_YAML=builtin python3 -m unittest discover -s tests -v
```
Expected: all PASS in both runs.

- [ ] **Step 7: Commit**

```bash
git add .claude/skills/linting-agent-config-files/scripts/agentlint_lib tests
git commit -m "feat(agentlint): cross-file rules, good fixture and rule-coverage test

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_016TZTeGdK9WuTukJpPzZFxY"
```

---

### Task 9: The two always-loaded skills and the generated rule catalogue

**Files:**
- Create: `.claude/skills/linting-agent-config-files/SKILL.md`, `.claude/skills/linting-agent-config-files/references/rule-catalogue.md`
- Create: `.claude/skills/writing-review-findings/SKILL.md`, `.claude/skills/writing-review-findings/references/report-template.md`
- Create: `tests/test_catalogue_sync.py`

**Interfaces:**
- Consumes `report.catalogue_markdown()`.
- Produces the report contract every later skill and the agent body refer to by name.

- [ ] **Step 1: Write the failing sync test**

```python
import os
import unittest

from tests.helpers import REPO_ROOT, import_lib

lib = import_lib()
from agentlint_lib import api, report  # noqa: E402

CATALOGUE = os.path.join(REPO_ROOT, ".claude", "skills", "linting-agent-config-files", "references", "rule-catalogue.md")


class CatalogueSyncTests(unittest.TestCase):
    def test_reference_matches_registry(self):
        api._load_rule_modules()
        with open(CATALOGUE, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), report.catalogue_markdown())
```

- [ ] **Step 2: Generate the catalogue**

```bash
python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py --list-rules --format markdown \
  > .claude/skills/linting-agent-config-files/references/rule-catalogue.md
```

- [ ] **Step 3: Write `linting-agent-config-files/SKILL.md`**

```markdown
---
name: linting-agent-config-files
description: Runs the deterministic agentlint linter over AI-agent configuration files (custom agents, SKILL.md skills, instruction and prompt files, AGENTS.md, CLAUDE.md, MCP, hooks and plugin manifests) and explains how to read its JSON output and rule IDs. Use at the start of every agent-configuration review, before any semantic judgement, and whenever a rule ID such as AG007 or SK004 needs its meaning, severity or source.
metadata:
  version: "1.0.0"
  family: agent-skill-reviewer
---

# Linting agent configuration files

## Overview
`scripts/agentlint.py` finds every agent-configuration file under a repository root, classifies it by kind, and applies the automatic (`auto`) rules from `references/rule-catalogue.md`. It never edits files and never touches the network. Manual rules (`manual` tag) are not emitted by the script; the per-kind reviewing skills describe how to judge them.

## When to use
- First step of any review: run the linter, then reason on top of its output.
- To look up what a rule ID means, its severity, which runtime it concerns and the documentation it comes from.
- To lint a pasted config that is not in the tree (for example the cloud-agent MCP JSON) with `--kind`.

## Procedure
1. From the repository root run
   `python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py --format json [PATH ...]`
   Add `--exclude 'tests/fixtures/**'` for repositories that ship broken fixtures on purpose.
2. Read the header: `yaml_parser` is `pyyaml` or `builtin`; with `builtin`, treat findings on nested structures as medium confidence.
3. Walk `findings`. Each has `id`, `severity`, `confidence`, `file`, `line`, `message`, `runtime`, `source`, `autofix_safe`, `suggestion`.
4. Copy `not_checked` verbatim into the final report.
5. Exit code 1 means at least one error; 2 means the linter itself failed — report that and fall back to the manual tables in the reviewing skills.
6. If `python3` is unavailable, apply the `auto` rules by hand from the catalogue and mark every such finding `confidence: medium`.

## Reading the output
| Field | Meaning |
|---|---|
| `severity` | `error`: file will not load or misbehaves; `warning`: likely wrong or deprecated; `info`: portability or style |
| `runtime` | `copilot`, `claude`, `both` or `generic` — which runtime the rule concerns |
| `autofix_safe` | the suggestion can be applied mechanically without changing meaning |
| `confidence` | lowered when the builtin YAML parser was used or the check is heuristic |

## Common false positives
- `AG007` on a tool name that is valid for a newer runtime version than the catalogue knows — verify against the linked source before reporting.
- `CF006` on placeholder strings such as `REPLACE_ME` — downgrade to info if clearly a placeholder.
- `IN007` on an `@handle` that is prose, not an import — the linter already skips targets without `/` or `.`.

## References
- `references/rule-catalogue.md` — generated by `agentlint.py --list-rules --format markdown`; do not edit by hand.
- Load `writing-review-findings` for the report format.
```

- [ ] **Step 4: Write `writing-review-findings/SKILL.md` and `references/report-template.md`**

The SKILL.md frontmatter follows the same shape (name `writing-review-findings`; description: "Formats agent-configuration review findings into the standard report: grouped by severity then file, one finding per root cause, each with rule ID, location, why, fix, source and confidence, plus a mandatory not-checked section. Use when producing the final output of any agent, skill, instruction or MCP configuration review."). Body sections: Overview, When to use, Procedure, Severity and confidence taxonomy, Noise control (merge duplicates; cap identical info findings per rule at five with a count; portability notes never under Errors), Common false positives, References. `references/report-template.md` is the spec §8 block verbatim plus a filled example with one finding per severity.

- [ ] **Step 5: Run the sync test and the SK rules on the repo itself**

```bash
python3 -m unittest tests.test_catalogue_sync -v
python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py .claude/skills --min-severity warning
```
Expected: sync test passes; the second command prints `errors: 0, warnings: 0`.

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/linting-agent-config-files .claude/skills/writing-review-findings tests/test_catalogue_sync.py
git commit -m "feat(skills): linting-agent-config-files and writing-review-findings

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_016TZTeGdK9WuTukJpPzZFxY"
```

---

### Task 10: The five reviewing skills

**Files:**
- Create: `.claude/skills/reviewing-agent-definitions/{SKILL.md, references/copilot-agent-fields.md, references/claude-subagent-fields.md, references/tool-names.md}`
- Create: `.claude/skills/reviewing-skill-files/{SKILL.md, references/skill-spec.md, references/runtime-extensions.md}`
- Create: `.claude/skills/reviewing-instruction-files/{SKILL.md, references/instruction-formats.md}`
- Create: `.claude/skills/reviewing-mcp-and-hooks-config/{SKILL.md, references/mcp-formats.md, references/hooks-and-environment.md}`
- Create: `.claude/skills/detecting-cross-file-contradictions/SKILL.md`

**Interfaces:**
- Consumes `docs/reference/agent-file-formats.md` (Task 0) for the reference tables and the constants in `rules_ag.py`, `rules_sk.py`, `rules_in.py`, `rules_cf.py` (the tables must list exactly the same keys and enums the linter uses).

Shared shape for each `SKILL.md` (body ≤ 500 lines, frontmatter keys `name`, `description`, `metadata` only, description in third person with explicit triggers and no workflow summary):

```
# <Title>
## Overview            what file kinds this covers and what the linter already did
## When to use         "Load when the scope contains <kinds>" + the linter kinds it maps to
## Procedure           numbered: read linter findings for these kinds → apply each manual rule → hand results to writing-review-findings
## Rules               table: ID | Severity | Tag | Check | How to judge (manual) / What the linter checked (auto) | Source
## Common false positives
## References          bullets to files in references/ by relative path; other skills by name only
```

Per-skill content requirements:

| Skill | Manual rules it must explain how to judge | Reference files (copied from `docs/reference/agent-file-formats.md`) |
|---|---|---|
| `reviewing-agent-definitions` | AG018 (description has no when-to-use), AG019 (body vs tools contradiction; read-only claim vs `edit`/`Write`), AG020 (self-contradiction), AG021 (body names non-existent skills/agents — cross-check with `files` in the linter output) | `copilot-agent-fields.md`: every Copilot key, type, surfaces (github.com / VS Code / CLI), limits; `claude-subagent-fields.md`: every Claude key + enums from `CLAUDE_ENUMS`; `tool-names.md`: `COPILOT_TOOL_ALIASES`, `CLAUDE_TOOLS`, pattern forms |
| `reviewing-skill-files` | SK015 (no triggers / first person), SK016 (description summarises the workflow), SK017 (body contradicts itself or cites non-existent commands), SK018 (duplicates another skill) | `skill-spec.md`: agentskills.io fields, limits, directory contract; `runtime-extensions.md`: Copilot-specific behaviour (discovery dirs and precedence, `gh skill publish` constraints) and Claude-only keys from `CLAUDE_ONLY_KEYS` |
| `reviewing-instruction-files` | IN015 (task-specific content in a repo-wide file), IN016 (demands a command/path/tool that does not exist — verify with the file list) | `instruction-formats.md`: `copilot-instructions.md`, `*.instructions.md` (`applyTo`, `excludeAgent`), `*.prompt.md`, `AGENTS.md`, `CLAUDE.md` + `@import` semantics, `.claude/rules` + `paths`, `.claude/commands`, `.cursor/rules` |
| `reviewing-mcp-and-hooks-config` | none manual; explains every CF auto rule's intent, the four MCP dialects side by side, and what to say when the cloud-agent config is not in the tree | `mcp-formats.md`: `.mcp.json` vs `.vscode/mcp.json` vs CLI vs cloud-agent JSON (top key, `type` values, variable syntax); `hooks-and-environment.md`: `HOOK_EVENTS`, handler types, `copilot-setup-steps.yml` constraints, `plugin.json` / `marketplace.json` layout |
| `detecting-cross-file-contradictions` | XF007 (contradictory directives — quote both sides), XF008 (two skills with near-identical triggers — compare descriptions word by word), XF009 (agent composes skills whose descriptions do not match its stated purpose) | none; the body includes the discovery-precedence table (`DISCOVERY_ORDER`) and the list of reference kinds the linter resolves (XF003) |

- [ ] **Step 1: Write the five `SKILL.md` files and their references**

- [ ] **Step 2: Lint the skills tree and run the suite**

```bash
python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py .claude/skills
python3 -m unittest discover -s tests -v
```
Expected: `errors: 0, warnings: 0`; SK007 must not fire (every `references/` path exists); all tests PASS.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills
git commit -m "feat(skills): reviewing skills for agents, skills, instructions, MCP/hooks and cross-file checks

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_016TZTeGdK9WuTukJpPzZFxY"
```

---

### Task 11: The agent pair and the prompt file

**Files:**
- Create: `.github/agents/agent-skill-reviewer.agent.md`, `.claude/agents/agent-skill-reviewer.md`, `.github/prompts/review-agent-config.prompt.md`
- Create: `tests/test_agent_files.py`

**Interfaces:**
- Frontmatter exactly as spec §4.1 and §4.2; body shared and runtime-neutral (spec §4.3).

- [ ] **Step 1: Write the failing tests**

```python
import os
import re
import unittest

from tests.helpers import REPO_ROOT, import_lib, run_lint, ids

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
```

- [ ] **Step 2: Write the shared body** (used verbatim below both frontmatters)

```markdown
# Agent and skill configuration reviewer

You review AI-agent configuration files and report what is wrong. You never edit, create, move or delete files, and you never execute the agents or skills you review.

## Hard rules
- Every finding cites a rule ID from the agentlint catalogue and the documentation source that backs it.
- Runtime-specific fields are portability notes (info), never errors, unless the file is unambiguously for one runtime and the field is documented as invalid there.
- No speculative findings. If you cannot verify a claim from the file contents, the linter output or the reference tables, put the question under "Not checked".
- Say what you did not check, always.

## Scope
- With an argument: review the given path or glob. `all` means the whole repository.
- Without an argument: the whole repository from its root.
- In a pull-request context: changed configuration files first, then every file they reference (skills a subagent preloads, agents a prompt targets, imports in CLAUDE.md).

## Step 1 — Discover and lint
Load the skill `linting-agent-config-files`. From the repository root run
`python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py --format json <scope>`.
Keep the JSON. If Python is not available, follow the skill's manual-mode instructions and mark those findings medium confidence.

## Step 2 — Semantic review per file kind
For each kind present in the linter's `files` list, load the matching skill and apply its manual rules to every file of that kind:
- agents, subagents, chatmodes → `reviewing-agent-definitions`
- SKILL.md → `reviewing-skill-files`
- copilot-instructions.md, *.instructions.md, *.prompt.md, AGENTS.md, CLAUDE.md, .claude/rules, .claude/commands → `reviewing-instruction-files`
- MCP JSON, hooks, copilot-setup-steps.yml, plugin and marketplace manifests → `reviewing-mcp-and-hooks-config`

## Step 3 — Cross-file analysis
Load `detecting-cross-file-contradictions`. Start from the linter's XF findings, then apply the manual XF rules across everything in scope.

## Step 4 — Report
Load `writing-review-findings` and emit the report exactly in its contract. Copy the linter's `not_checked` entries into the "Not checked" section and add anything you skipped.

## Noise control
- One finding per root cause; merge duplicates that share a fix.
- At most five identical info-level findings per rule; state the total count.
- Never repeat a linter finding in different words; add only what the linter cannot know.
```

- [ ] **Step 3: Write the three files** with the frontmatter from spec §4.1, §4.2 and §4.4 and the body above.

- [ ] **Step 4: Run the tests and lint the repository**

```bash
python3 -m unittest tests.test_agent_files -v
python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py --exclude 'tests/fixtures/**'
```
Expected: PASS; linter output ends with `errors: 0, warnings: 0, info: 2`.

- [ ] **Step 5: Commit**

```bash
git add .github/agents .claude/agents .github/prompts tests/test_agent_files.py
git commit -m "feat(agent): agent-skill-reviewer for Copilot and Claude Code, plus /review-agent-config prompt

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_016TZTeGdK9WuTukJpPzZFxY"
```

---

### Task 12: Self-review, runtime discovery checks, and README

**Files:**
- Create: `tests/test_self_review.py`, `README.md`

- [ ] **Step 1: Write the self-review test**

```python
import unittest

from tests.helpers import REPO_ROOT, run_lint


class SelfReviewTests(unittest.TestCase):
    def test_repository_lints_clean(self):
        r = run_lint(root=REPO_ROOT, excludes=["tests/fixtures/**"])
        self.assertEqual(r["summary"]["error"], 0, r["findings"])
        self.assertEqual(r["summary"]["warning"], 0, r["findings"])
        kinds = {f["kind"] for f in r["files"]}
        self.assertTrue({"copilot-agent", "claude-subagent", "skill", "prompt-file"} <= kinds, kinds)
```

Run `python3 -m unittest tests.test_self_review -v` — expected PASS (if not, fix the offending file, never the test).

- [ ] **Step 2: Copilot CLI discovery check**

From the repository root, with Copilot CLI ≥ 1.0.80:

```bash
copilot --help | head -5
copilot -p "List the custom agents and skills available in this repository, names only." --allow-all-tools 2>&1 | tee /tmp/copilot-discovery.txt
```
Expected: the output names `agent-skill-reviewer` and the seven skills. If the non-interactive flag differs in the installed version, use the one `copilot --help` documents and record the exact command. Paste the command and the trimmed output into the README "Verification log".

- [ ] **Step 3: Claude Code behavioural check (RED/GREEN)**

```bash
claude -p "Use the agent-skill-reviewer subagent to review tests/fixtures/bad and return its report." > /tmp/claude-green.txt
mv .claude/skills /tmp/skills-hidden
claude -p "Use the agent-skill-reviewer subagent to review tests/fixtures/bad and return its report." > /tmp/claude-red.txt
mv /tmp/skills-hidden .claude/skills
```
Expected: the green run cites rule IDs (`SK004`, `CF002`, `AG008`, …) with sources; the red run either reports no rule IDs or invents them. Summarise both in the README verification log. Restore `.claude/skills` before continuing (`git status` must show it present).

- [ ] **Step 4: Write `README.md`**

Sections: What it is (two sentences); Layout (the tree from spec §3); Using it in Copilot (github.com: assign the agent on an issue or PR; VS Code: pick the agent or run `/review-agent-config`; CLI: `/agent agent-skill-reviewer`); Using it in Claude Code (`@agent-skill-reviewer` or automatic delegation); Running the linter alone (the CLI contract from spec §7); Copying into another repository (copy `.github/agents/`, `.github/prompts/`, `.claude/agents/`, `.claude/skills/`; optional `.github/skills/` copy for Copilot code review); Adding a rule (register in `catalogue.py`, implement in the matching `rules_*.py`, add a `bad/` fixture, regenerate the catalogue, update the skill table); Tests (`python3 -m unittest discover -s tests -v`, twice with `AGENTLINT_YAML=builtin`); Verification log (Steps 2–3 outputs with dates); Unresolved questions (spec §11 list).

- [ ] **Step 5: Final full run and commit**

```bash
python3 -m unittest discover -s tests -v
AGENTLINT_YAML=builtin python3 -m unittest discover -s tests -v
python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py --exclude 'tests/fixtures/**'
git add tests/test_self_review.py README.md
git commit -m "test: self-review, runtime discovery checks and README

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_016TZTeGdK9WuTukJpPzZFxY"
```

---

## Spec deltas introduced by this plan

The plan is the more detailed document; the spec was reconciled to it on 2026-09-03. Items where the plan deliberately differs from the first draft of the spec:

- New `GN` rule family (GN001–GN004) and additional auto rules AG023–AG028, SK019, IN017–IN020, CF014–CF022.
- `IN003` is a warning (list form of `applyTo` is tolerated by VS Code) and `IN005` measures lines (> 1,000) rather than characters.
- `CF009` only reports component directories inside `.claude-plugin/`; a manifest at any other path is simply not discovered.
- `--format markdown` exists for `--list-rules` only; `--version` added.
- Tests are split per module (`test_yamlfm`, `test_catalogue`, `test_discover`, `test_cli`, `test_rules_*`, `test_good_fixture`, `test_catalogue_sync`, `test_agent_files`, `test_self_review`) instead of the three files named in the first spec draft.
- The linter is a package (`agentlint_lib/`) next to the `agentlint.py` entrypoint.
- `docs/reference/agent-file-formats.md` is rebuilt from the official sources (the research scratchpad no longer exists).

Deltas introduced while executing Tasks 0, 8 and 10 on 2026-09-04, after fetching the official pages:

- The Claude twin's `tools` is `Read, Grep, Glob, Bash`; `Bash(pattern)` rules inside subagent `tools` are undocumented.
- XF001 no longer claims first-found-wins precedence between Copilot skill directories (undocumented); its source is the github.com skills page.
- AG024 is info, not warning: github.com documents both a comma-separated string and a YAML list for Copilot `tools`.
- CF008 reports unsupported setup-steps job keys as warnings (the docs say they are ignored) and uses the six documented keys.
- Key sets, enum values and hook events in `rules_*.py` follow the pages fetched 2026-09-04 (see the `fix(agentlint)` commits).
- Explicit PATH arguments narrow what the linter reports, not what names resolve against.
- `sub/.vscode/mcp.json` in the bad fixture also carries an `sse` server so CF022 has a fixture.

- Plugin packaging and pull-request review are specified in `docs/superpowers/specs/2026-09-14-plugin-packaging-and-pr-review-design.md` and planned in `docs/superpowers/plans/2026-09-17-plugin-packaging-and-pr-review.md`.

---
