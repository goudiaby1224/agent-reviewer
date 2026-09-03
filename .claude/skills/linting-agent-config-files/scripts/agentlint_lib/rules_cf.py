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
