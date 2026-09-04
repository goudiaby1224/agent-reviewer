# Tool names in agent definitions

Sources (fetched 2026-09-04): GH-REF = https://docs.github.com/en/copilot/reference/custom-agents-configuration, VSC-AGENTS = https://code.visualstudio.com/docs/agent-customization/custom-agents, VSC-SUB = https://code.visualstudio.com/docs/agents/run/subagents, GH-CLI-ABOUT = https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents, SA = https://code.claude.com/docs/en/sub-agents. The linter's tables live in `agentlint_lib/toolnames.py`; this file records where each entry comes from.

## Copilot `tools` (AG007)
"All aliases are case insensitive." (GH-REF). The linter lowercases entries before matching.

| Primary alias | Compatible aliases (GH-REF) | Cloud-agent tool it maps to | Notes |
|---|---|---|---|
| `execute` | `shell`, `Bash`, `powershell` | `bash`, `powershell` | shell commands |
| `read` | `Read`, `NotebookRead` | `view` | |
| `edit` | `Edit`, `MultiEdit`, `Write`, `NotebookEdit` | `str_replace`, `str_replace_editor` | |
| `search` | `Grep`, `Glob` | `search` | |
| `agent` | `custom-agent`, `Task` | custom agent tools | required in `tools` when `agents` is set (VSC) [AG009] |
| `web` | `WebSearch`, `WebFetch` | "Currently not applicable" on the cloud agent | |
| `todo` | `TodoWrite` | "Currently not applicable" on the cloud agent | |
| `*` | | all tools | `tools: ["*"]` or omit `tools` (GH-REF) |
| `<server>/<tool>` | | one MCP tool | e.g. `some-mcp-server/some-tool` |
| `<server>/*` | | every tool of one MCP server | (GH-REF, VSC-AGENTS) |

VS Code additions (VSC-AGENTS, VSC-SUB): built-in sub-tools written as `<group>/<tool>` such as `web/fetch`, `search/codebase`, `search/usages`, `read/terminalLastCommand`, `agent/runSubagent`; the bare `runSubagent`; user-defined tool set names; extension-contributed tools. The linter accepts any `<name>/<tool>` pair and `runsubagent`; tool set names cannot be validated, so an AG007 on an unknown bare word may be a tool set (see the skill's false positives).

Cloud-agent-side names (`view`, `str_replace`, `str_replace_editor`, `bash`, `powershell`, `search`) and the legacy VS Code tool ids (`codebase`, `editFiles`, `fetch`, `runCommands`, `runTasks`, `usages`, `problems`, `changes`, `testFailure`, `terminalLastCommand`, `terminalSelection`, `findTestFiles`, `githubRepo`, `extensions`, `vscodeAPI`, `openSimpleBrowser`, `runNotebooks`, `new`, `memory`, `think`, `todos`, `runInTerminal`) are accepted by the linter to avoid false positives on older files; their use as `tools` values today is UNVERIFIED on the fetched pages. Copilot CLI documents no `tools` value list (GH-CLI-ABOUT names `grep`, `glob`, `view`, `shell` only in prose).

## Claude Code `tools` and `disallowedTools` (AG008)
Documented forms (SA): exact built-in tool names, `mcp__<server>` (all tools of a server), `mcp__<server>__*`, `mcp__<server>__<tool>`, `mcp__*` (in `disallowedTools` only), `Agent(agent_type, ...)` and `Agent`. Every example is a comma-separated string [AG023 notes a YAML list]. `Task(...)` still works as an alias of `Agent` since v2.1.63.

Permission-rule patterns such as `Bash(git:*)` or `Edit(*.ts)` inside `tools`: UNVERIFIED (SA shows none). The linter accepts `Tool(pattern)` for any known tool without a finding; a reviewer should mention the uncertainty under "Not checked" when a file relies on it.

Built-in tool names the linter recognises (union of the SA "Available tools" lists and the tools Claude Code exposes): `Read`, `Edit`, `Write`, `MultiEdit`, `NotebookEdit`, `NotebookRead`, `Bash`, `PowerShell`, `Grep`, `Glob`, `LS`, `WebFetch`, `WebSearch`, `Agent`, `Task`, `Skill`, `TodoWrite`, `AskUserQuestion`, `SlashCommand`, `BashOutput`, `KillShell`, `ExitPlanMode`, `EnterPlanMode`, `Monitor`, `ListMcpResources`, `ReadMcpResource`, `ToolSearch`, `TaskOutput`, `TaskStop`, `CronCreate`, `CronDelete`, `CronList`, `EnterWorktree`, `ExitWorktree`, `ScheduleWakeup`, `SendMessage`, `EndConversation`, `Artifact`.

Names Claude Code removes from every subagent (SA): `Agent` (at depth limit), `AskUserQuestion`, `EndConversation`, `EnterPlanMode`, `ExitPlanMode` (unless `permissionMode: plan`), `ScheduleWakeup`, `TaskOutput`, `WaitForMcpServers`, `Workflow`. Listing them is not an error, just ineffective.

AG008 severity: error when no entry in `tools` resolves ("If no entry in the list resolves to a tool, the subagent usually fails to launch", SA), warning when only some are unknown. A lowercase Copilot alias such as `read` gets a hint that Claude names are capitalised.

## Cross-runtime pitfalls
- A Claude comma string in a Copilot agent is accepted by github.com but not documented for VS Code [AG024, info]; a YAML list in a Claude subagent is undocumented [AG023, info].
- `Bash` is a valid alias on both sides; `bash` lowercase is Copilot-only; `Read` is valid on both sides; `read` is Copilot-only.
- MCP tools are `<server>/<tool>` for Copilot and `mcp__<server>__<tool>` for Claude Code; each runtime ignores the other's form.
