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
