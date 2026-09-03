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
    if "hooks" in fm:
        from . import rules_cf
        out.extend(rules_cf.check_hooks_object(fm["hooks"], cf.path, ctx.root, line=cf.key_line("hooks")))
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
