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
    if "hooks" in fm:
        from . import rules_cf
        out.extend(rules_cf.check_hooks_object(fm["hooks"], cf.path, ctx.root, line=cf.key_line("hooks")))
    return out
