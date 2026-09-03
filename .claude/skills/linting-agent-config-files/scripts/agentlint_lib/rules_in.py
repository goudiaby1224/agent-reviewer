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
