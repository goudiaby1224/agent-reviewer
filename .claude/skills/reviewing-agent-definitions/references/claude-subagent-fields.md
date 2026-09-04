# Claude Code subagent fields

Sources (fetched 2026-09-04): SA = https://code.claude.com/docs/en/sub-agents, PR = https://code.claude.com/docs/en/plugins-reference, HK = https://code.claude.com/docs/en/hooks. Quotations are verbatim. `UNVERIFIED` marks facts none of these pages states. Linter rule IDs in brackets.

## Discovery and identity
| Location | Scope | Notes (SA) |
|---|---|---|
| managed settings directory `.claude/agents/` | organisation | "Managed definitions take precedence over project and user subagents with the same name" |
| `--agents` CLI flag (JSON) | session | JSON keyed by agent name with a `prompt` field plus the frontmatter fields |
| `.claude/agents/**/*.md` | project | scanned recursively; "identity comes only from the `name` frontmatter field" |
| `~/.claude/agents/**/*.md` | user | same |
| `<plugin>/agents/` | plugin | scanned recursively; subfolders become part of the scoped id (`my-plugin:review:security`) |
| `--add-dir` directories | session | their `.claude/agents/` load alongside project subagents |

- Priority, highest first: managed, `--agents`, project, user, plugin (SA).
- "The filename doesn't have to match" the `name` (SA). The linter still keys the twin check (XF002) on `name`, falling back to the filename.
- Files Claude Code skips: no `name` (treated as documentation); opening `---` not on the first line; `name` starting with `-` or containing `:`; `name` without `description`; YAML that does not parse (SA) [AG001, AG003, AG004]. Plugin agents are the exception: they load without `name` (named after the file) and with unparseable frontmatter (PR).
- Duplicate names inside one directory: UNVERIFIED (SA).

## Frontmatter keys
| Key | Type | Required | Allowed values / format | Notes | Linter |
|---|---|---|---|---|---|
| `name` | string | yes | "lowercase letters and hyphens"; no leading `-`; no `:` (reserved for `plugin:agent` ids) | used as `agent_type` in hooks | AG003, AG004 (`^[a-z0-9]+(-[a-z0-9]+)*$`) |
| `description` | string | yes | free text | "When Claude should delegate to this subagent"; "include phrases like 'use proactively'" | AG003; AG018 (manual) |
| `tools` | comma-separated string | no | exact tool names; `mcp__<server>`; `mcp__<server>__*`; `Agent(agent_type, ...)`; `Agent` | every example is a comma string, e.g. `tools: Read, Grep, Glob, Bash`; "Inherits every tool available to subagents if omitted"; "If no entry in the list resolves to a tool, the subagent usually fails to launch"; preload skills with `skills`, not `Skill` here. YAML-list form: UNVERIFIED (SA). Permission-rule patterns such as `Bash(git:*)` inside `tools`: UNVERIFIED (SA); the linter accepts them without a finding | AG008 (error when nothing resolves), AG023 (list form) |
| `disallowedTools` | comma-separated string | no | exact names; `mcp__<server>`; `mcp__<server>__*`; `mcp__*` | "applied first, then `tools` is resolved against the remaining pool" | AG008 |
| `model` | string | no | `sonnet`, `opus`, `haiku`, `fable`, a full model id such as `claude-opus-5`, or `inherit` | resolution when omitted: per-invocation parameter, frontmatter, `CLAUDE_CODE_SUBAGENT_MODEL`, main model | AG014 (Copilot display names) |
| `permissionMode` | string | no | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`, `manual` (alias of `default`, v2.1.200+) | "Ignored for plugin subagents" | AG015 |
| `maxTurns` | number | no | integer | stops the subagent and marks output partial | none |
| `skills` | YAML list of strings | no | skill names | "The full skill content is injected, not only the description" | AG027; XF003, XF004 |
| `mcpServers` | list | no | server-name strings or inline objects with `.mcp.json`-style config; types `stdio`, `http`, `sse`, `ws` | "Ignored for plugin subagents"; inline servers in project agents need trust (v2.1.238+) | none |
| `hooks` | map | no | same shape as settings hooks | "Ignored for plugin subagents"; `Stop` is converted to `SubagentStop`; SA lists `PreToolUse`, `PostToolUse`, `Stop`, HK says "All hook events are supported" (both recorded) | CF007, CF010, CF017, CF018 |
| `memory` | string | no | `user`, `project`, `local` | cross-session memory directory per value | AG015 |
| `background` | boolean | no | `true` | keep in the background even when asked to run in the foreground | AG026 |
| `effort` | string | no | `low`, `medium`, `high`, `xhigh`, `max` | "available levels depend on the model" | AG015 |
| `isolation` | string | no | `worktree` | temporary git worktree from the default branch; PR: "The only valid `isolation` value is `\"worktree\"`" | AG015 |
| `color` | string | no | `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan` | display only | AG015 |
| `initialPrompt` | string | no | free text | auto-submitted first turn when run as the main session via `--agent` | AG017 (known key) |
| `experimental` | map | no | `cacheTtl: 5m` or `1h` (v2.1.248+) | other values ignored | AG017 (known key) |
| body | Markdown | | | "The body becomes the system prompt"; subagents do not get the Claude Code system prompt | AG016 (empty) |

Plugin-shipped agents support `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `isolation`; "`hooks`, `mcpServers`, and `permissionMode` are not supported for plugin-shipped agents" (PR).

## Limits
- Combined subagent descriptions over 15,000 tokens produce a startup warning; all still load (SA).
- 20 concurrent subagents per session (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`, v2.1.217+) (SA).
- Nesting depth via `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`; default UNVERIFIED (SA).
- No documented body-length limit; the linter's 30,000-character check (AG010) is Copilot's rule and is applied only to Copilot agents.

## Deprecated and renamed forms
- "In version 2.1.63, the Task tool was renamed to Agent. Existing `Task(...)` references ... still work as aliases" (SA). The linter accepts both.
- `permissionMode: manual` is an alias for `default` (SA).
- Names starting with `-` or containing `:` were accepted before v2.1.218 and are now skipped (SA).

## Built-in tool names (SA "Available tools")
Removed from every subagent: `Agent` (at depth limit), `AskUserQuestion`, `EndConversation`, `EnterPlanMode`, `ExitPlanMode` (unless `permissionMode: plan`), `ScheduleWakeup`, `TaskOutput`, `WaitForMcpServers`, `Workflow`. Background subagents keep every MCP tool and these built-ins: `Read`, `Grep`, `Glob`, `Bash`, `PowerShell`, `Edit`, `Write`, `NotebookEdit`, `WebFetch`, `WebSearch`, `TodoWrite`, `Skill`, `ToolSearch`, `EnterWorktree`, `ExitWorktree`, `Monitor`, `TaskStop`, `SendMessage`, `Artifact`. See `tool-names.md` for the full list the linter recognises.
