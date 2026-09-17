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
