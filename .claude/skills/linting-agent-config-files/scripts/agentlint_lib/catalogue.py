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
rule("AG009", "error", "auto", "AG", "copilot", "Agents key set but agent tool not included in tools", SRC["vscode-subagents"])
rule("AG010", "error", "auto", "AG", "copilot", "Agent body exceeds 30,000 characters", SRC["gh-agent-create"])
rule("AG011", "info", "auto", "AG", "copilot", "Keys mcp-servers or metadata with target vscode (not used in IDEs)", SRC["gh-agent-ref"])
rule("AG012", "info", "auto", "AG", "copilot", "VS Code-only keys present (ignored on github.com)", SRC["gh-agent-ref"])
rule("AG013", "error", "auto", "AG", "copilot", "Agent filename contains characters outside . - _ a-z A-Z 0-9", SRC["gh-agent-create"])
rule("AG014", "warning", "auto", "AG", "both", "Model value belongs to the other runtime", SRC["gh-agent-ref"])
rule("AG015", "error", "auto", "AG", "claude", "Undocumented value for an enumerated Claude field", SRC["claude-subagents"])
rule("AG016", "warning", "auto", "AG", "both", "Empty agent body", SRC["gh-agent-ref"])
rule("AG017", "warning", "auto", "AG", "both", "Unknown frontmatter key for this runtime", SRC["gh-agent-ref"])
rule("AG018", "warning", "manual", "AG", "both", "Description gives no when-to-use triggers", SRC["claude-subagents"])
rule("AG019", "warning", "manual", "AG", "both", "Body instructs actions the tools list forbids, or claims read-only while granting edit", SRC["gh-agent-ref"])
rule("AG020", "warning", "manual", "AG", "both", "Body contradicts itself", SRC["gh-agent-ref"])
rule("AG021", "info", "manual", "AG", "both", "Body names skills or agents that do not exist in the repository", SRC["gh-agent-ref"])
rule("AG022", "warning", "auto", "AG", "copilot", "Target must be vscode or github-copilot", SRC["gh-agent-ref"])
rule("AG023", "info", "auto", "AG", "claude", "Tools given as a YAML list; docs specify a comma-separated string", SRC["vscode-agents"])
rule("AG024", "info", "auto", "AG", "copilot", "Copilot tools given as a comma-separated string (github.com accepts it; VS Code documents a YAML list)", SRC["gh-agent-ref"])
rule("AG025", "error", "auto", "AG", "copilot", "Handoffs entry missing label or agent", SRC["vscode-agents"])
rule("AG026", "warning", "auto", "AG", "both", "Boolean field has a non-boolean value", SRC["gh-agent-ref"])
rule("AG027", "error", "auto", "AG", "claude", "Skills must be a YAML list of skill names", SRC["claude-subagents"])
rule("AG028", "error", "auto", "AG", "copilot", "Mcp-servers entry missing tools/type or has an invalid type", SRC["gh-mcp"])

# ---- SK: skills
rule("SK001", "error", "auto", "SK", "both", "SKILL.md frontmatter missing or invalid", SRC["skills-spec"])
rule("SK002", "error", "auto", "SK", "both", "Name missing", SRC["skills-spec"])
rule("SK003", "error", "auto", "SK", "both", "Name must be 1-64 chars of lowercase letters, digits and single hyphens", SRC["skills-spec"])
rule("SK004", "error", "auto", "SK", "both", "Name differs from the parent directory name", SRC["skills-spec"])
rule("SK005", "error", "auto", "SK", "both", "Description missing, empty, or longer than 1024 characters", SRC["skills-spec"])
rule("SK006", "warning", "auto", "SK", "both", "Body longer than 500 lines", SRC["skills-spec"])
rule("SK007", "error", "auto", "SK", "both", "Relative path or link in the body points to a missing file", SRC["skills-spec"])
rule("SK008", "warning", "auto", "SK", "both", "Script lacks a shebang or the executable bit", SRC["skills-spec"])
rule("SK009", "error", "auto", "SK", "both", "Compatibility must be a string of at most 500 characters", SRC["skills-spec"])
rule("SK010", "info", "auto", "SK", "both", "Runtime-specific frontmatter keys present (portability note)", SRC["claude-skills"])
rule("SK011", "warning", "auto", "SK", "both", "Frontmatter key unknown to every runtime (possible typo)", SRC["skills-spec"])
rule("SK012", "error", "auto", "SK", "both", "File must be named exactly SKILL.md", SRC["skills-spec"])
rule("SK013", "warning", "auto", "SK", "both", "SKILL.md outside every documented discovery location", SRC["cli-ref"])
rule("SK014", "info", "auto", "SK", "both", "Metadata is not a map of string keys to string values", SRC["skills-spec"])
rule("SK015", "warning", "manual", "SK", "both", "Description gives no when-to-use triggers or is written in first person", SRC["vscode-skills"])
rule("SK016", "warning", "manual", "SK", "both", "Description summarises the workflow (agents may follow it instead of the body)", SRC["skills-spec"])
rule("SK017", "warning", "manual", "SK", "both", "Body contradicts itself or references tools/commands that do not exist", SRC["skills-spec"])
rule("SK018", "info", "manual", "SK", "both", "Body duplicates another skill instead of cross-referencing it", SRC["skills-spec"])
rule("SK019", "warning", "auto", "SK", "both", "Allowed-tools is a YAML list; spec wants a space-separated string (gh skill publish rejects lists)", SRC["gh-skill-publish"])

# ---- IN: instructions and prompts
rule("IN001", "error", "auto", "IN", "copilot", "Instruction or prompt file frontmatter invalid", SRC["vscode-instructions"])
rule("IN002", "warning", "auto", "IN", "copilot", "Instructions file without applyTo", SRC["gh-instructions"])
rule("IN003", "warning", "auto", "IN", "copilot", "ApplyTo is documented as a comma-separated string, not a list", SRC["vscode-instructions"])
rule("IN004", "warning", "auto", "IN", "copilot", "ExcludeAgent must be code-review or cloud-agent", SRC["gh-instructions"])
rule("IN005", "info", "auto", "IN", "copilot", "Instruction file longer than 1,000 lines may be partly overlooked", SRC["gh-cr-tutorial"])
rule("IN006", "error", "auto", "IN", "copilot", "Prompt file agent references an agent that does not exist", SRC["vscode-prompts"])
rule("IN007", "error", "auto", "IN", "claude", "CLAUDE.md @import target does not exist", SRC["claude-memory"])
rule("IN008", "error", "auto", "IN", "claude", "Claude rules paths must be a YAML list of glob strings", SRC["claude-memory"])
rule("IN009", "info", "auto", "IN", "generic", "Nested AGENTS.md (VS Code requires chat.useNestedAgentsMdFiles)", SRC["agents-md"])
rule("IN010", "warning", "auto", "IN", "generic", "Legacy AGENT.md singular filename; rename to AGENTS.md", SRC["agents-md"])
rule("IN011", "warning", "auto", "IN", "copilot", "Instructions file outside .github/instructions is not discovered on github.com", SRC["gh-instructions"])
rule("IN012", "info", "auto", "IN", "generic", "Frontmatter present in a file for which no fields are defined", SRC["gh-instructions"])
rule("IN013", "info", "auto", "IN", "generic", "Cursor rules file without .mdc extension is ignored by Cursor", SRC["cursor-rules"])
rule("IN014", "warning", "auto", "IN", "copilot", "Unknown frontmatter key in instruction or prompt file", SRC["vscode-prompts"])
rule("IN015", "warning", "manual", "IN", "copilot", "Task-specific or one-off instructions in a repository-wide file", SRC["gh-instructions"])
rule("IN016", "warning", "manual", "IN", "generic", "Instruction demands a command, path or tool that does not exist in the repository", SRC["gh-instructions"])
rule("IN017", "warning", "auto", "IN", "generic", "Instruction or prompt file has an empty body", SRC["gh-instructions"])
rule("IN018", "warning", "auto", "IN", "copilot", "Prompt file uses legacy mode; use agent", SRC["vscode-prompts"])
rule("IN019", "warning", "auto", "IN", "copilot", "Prompt file tools must be a YAML list", SRC["vscode-prompts"])
rule("IN020", "info", "auto", "IN", "claude", "Legacy .claude/commands file; skills are recommended", SRC["claude-skills"])

# ---- CF: MCP, hooks, environment, manifests
rule("CF001", "error", "auto", "CF", "generic", "JSON or YAML is invalid", SRC["claude-mcp"])
rule("CF002", "error", "auto", "CF", "generic", "Wrong top-level key: .vscode/mcp.json needs servers, .mcp.json needs mcpServers", SRC["vscode-mcp"])
rule("CF003", "error", "auto", "CF", "claude", "MCP entry has url but no type (read as stdio and skipped)", SRC["claude-mcp"])
rule("CF004", "warning", "auto", "CF", "claude", "Type sse is deprecated; use http", SRC["claude-mcp"])
rule("CF005", "error", "auto", "CF", "copilot", "Cloud-agent MCP entry missing tools or type, or type not local/stdio/http/sse", SRC["gh-mcp"])
rule("CF006", "error", "auto", "CF", "generic", "Literal secret-looking value in env or headers", SRC["gh-mcp"])
rule("CF007", "error", "auto", "CF", "claude", "Hook event misspelled or handler missing a required field", SRC["claude-hooks"])
rule("CF008", "error", "auto", "CF", "copilot", "Setup-steps job must be named copilot-setup-steps and use only supported keys", SRC["gh-env"])
rule("CF009", "error", "auto", "CF", "claude", "Plugin component directories must sit at the plugin root, not inside .claude-plugin/", SRC["claude-plugins"])
rule("CF010", "warning", "auto", "CF", "generic", "Hook or MCP command script path missing or not executable", SRC["claude-hooks"])
rule("CF011", "info", "auto", "CF", "generic", "Variable reference ${VAR} without a default", SRC["claude-mcp"])
rule("CF012", "error", "auto", "CF", "generic", "Stdio server missing command, or remote server missing url", SRC["vscode-mcp"])
rule("CF013", "info", "auto", "CF", "claude", "Copilot-only tools allowlist inside a .mcp.json shared with Claude Code", SRC["claude-mcp"])
rule("CF014", "info", "auto", "CF", "generic", "Unknown key in MCP server entry", SRC["claude-mcp"])
rule("CF015", "error", "auto", "CF", "generic", "Input reference ${input:id} used but not declared in inputs", SRC["vscode-mcp"])
rule("CF016", "warning", "auto", "CF", "copilot", "Cloud-agent env or header reference is not COPILOT_MCP_-prefixed", SRC["gh-mcp"])
rule("CF017", "info", "auto", "CF", "claude", "Once is only honoured in skill frontmatter hooks", SRC["claude-hooks"])
rule("CF018", "warning", "auto", "CF", "claude", "If is only evaluated on tool events; this hook never runs", SRC["claude-hooks"])
rule("CF019", "info", "auto", "CF", "copilot", "Setup-steps workflow has no on triggers, so it cannot be self-tested", SRC["gh-env"])
rule("CF020", "error", "auto", "CF", "generic", "Plugin or marketplace manifest missing name", SRC["claude-plugins"])
rule("CF021", "error", "auto", "CF", "generic", "Marketplace entry missing name or source", SRC["claude-plugins"])
rule("CF022", "info", "auto", "CF", "copilot", "Type sse is a legacy transport in Copilot CLI / MCP spec", SRC["cli-mcp"])

# ---- XF: cross-file
rule("XF001", "warning", "auto", "XF", "copilot", "Same skill name in more than one discovery directory (which copy wins is undocumented)", SRC["gh-skills"])
rule("XF002", "info", "auto", "XF", "both", "Same agent name in .github/agents and .claude/agents", SRC["cli-ref"])
rule("XF003", "error", "auto", "XF", "both", "Dangling reference to an agent or skill", SRC["claude-subagents"])
rule("XF004", "error", "auto", "XF", "claude", "Subagent preloads a skill that has disable-model-invocation: true", SRC["claude-subagents"])
rule("XF005", "warning", "auto", "XF", "claude", "Skill and .claude/commands file share a name (the skill wins)", SRC["claude-skills"])
rule("XF006", "info", "auto", "XF", "copilot", "Overlapping applyTo/paths globs across instruction files", SRC["vscode-instructions"])
rule("XF007", "warning", "manual", "XF", "generic", "Contradictory directives across files", SRC["gh-instructions"])
rule("XF008", "warning", "manual", "XF", "both", "Two skills with near-identical triggers (routing ambiguity)", SRC["skills-spec"])
rule("XF009", "warning", "manual", "XF", "both", "Agent composes skills whose descriptions do not match the claimed purpose", SRC["gh-agent-ref"])
rule("XF010", "info", "auto", "XF", "generic", "CLAUDE.md and AGENTS.md coexist without importing each other", SRC["claude-memory"])
