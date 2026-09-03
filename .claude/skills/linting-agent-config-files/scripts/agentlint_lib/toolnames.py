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
    "runinterminal",
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
