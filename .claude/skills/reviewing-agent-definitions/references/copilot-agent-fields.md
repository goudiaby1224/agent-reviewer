# Copilot custom agent fields (`.agent.md`)

Sources (fetched 2026-09-04):
- GH-REF = https://docs.github.com/en/copilot/reference/custom-agents-configuration
- GH-HOWTO = https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/create-custom-agents
- GH-CLI-ABOUT = https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents
- GH-CHEAT = https://docs.github.com/en/copilot/reference/customization-cheat-sheet
- VSC-AGENTS = https://code.visualstudio.com/docs/agent-customization/custom-agents
- VSC-SUB = https://code.visualstudio.com/docs/agents/run/subagents
- VSC-HOOKS = https://code.visualstudio.com/docs/agent-customization/hooks

Surfaces: GH = github.com cloud agent, VSC = VS Code, CLI = Copilot CLI. Quotations are verbatim. `UNVERIFIED` marks facts none of these pages states. Linter rule IDs in brackets.

## Discovery locations
| Location | GH | VSC | CLI | Notes |
|---|---|---|---|---|
| `.github/agents/NAME.agent.md` in the repository | yes | yes | yes ("Create `.github/agents/CUSTOM-AGENT-NAME.md`", GH-CLI-ABOUT) | GH-CHEAT writes the path as `.github/agents/AGENT-NAME.md`; VSC "detects any `.md` files in the `.github/agents` folder" |
| `agents/NAME.agent.md` at the root of the organisation's `.github` or `.github-private` repository | yes | yes (`github.copilot.chat.organizationCustomAgents.enabled`) | yes | organisation level |
| `agents/NAME.agent.md` in a designated `.github-private` repository | yes | UNVERIFIED | yes | enterprise level |
| `~/.copilot/agents` | UNVERIFIED | yes | UNVERIFIED | user level; Agent Host sessions read it |
| `.claude/agents/*.md` (Claude subagent format) | UNVERIFIED | yes | UNVERIFIED | VSC maps Claude tool names to its own |
| `chat.agentFilesLocations`, parent repositories | no | yes | no | VS Code settings |

- Filename: "may only contain the following characters: `.`, `-`, `_`, `a-z`, `A-Z`, `0-9`" (GH-HOWTO) [AG013]. The name minus `.md` or `.agent.md` "is used for deduplication" (GH-REF). Plain `NAME.md` is the CLI's documented pattern; on github.com it is implied, not stated (UNVERIFIED).
- Precedence between repository, organisation and enterprise copies, and between VS Code workspace, user and organisation agents: UNVERIFIED on every page.
- `name` allowed characters: UNVERIFIED.

## Frontmatter keys
| Key | Type | Required | Values / format | Surfaces | Notes | Linter |
|---|---|---|---|---|---|---|
| `name` | string | no | display name; defaults to the filename without `.md` / `.agent.md` | GH, VSC, CLI | | none |
| `description` | string | GH: "Required"; VSC: optional; CLI: not stated | free text | GH, VSC, CLI | drives automatic selection on GH; placeholder text in VSC | AG002 (error, github.com rule); AG018 (manual) |
| `tools` | GH: "Supports both a comma separated string and yaml string array"; VSC: array | no | aliases, `<server>/<tool>`, `<server>/*`, `["*"]`; "If unset, defaults to all tools" (GH) | GH, VSC, CLI | VSC: "If a given tool is not available when using the custom agent, it is ignored"; prompt-file `tools` override agent `tools` (VSC) | AG007 (unknown alias), AG024 (comma string, info) |
| `model` | GH: string; VSC: string or prioritised array | no | VSC display names such as `Claude Opus 4.5`, `GPT-5.2`; `Model Name (vendor)` in handoffs | VSC, JetBrains, Eclipse, Xcode (GH-HOWTO); GH honours it: UNVERIFIED; CLI: UNVERIFIED | "If unset, inherits the default model" (GH) | AG014 (Claude alias) |
| `target` | string | no | `vscode`, `github-copilot`; "If unset, defaults to both environments" | GH, VSC | | AG022 |
| `infer` | boolean | retired | | GH "Retired", VSC "Deprecated" | replace with `user-invocable` and `disable-model-invocation` | AG005 |
| `user-invocable` | boolean | no | default `true` | GH, VSC | `false` hides the agent from manual selection; VSC: subagent-only agents | AG026 |
| `disable-model-invocation` | boolean | no | default `false` | GH, VSC | GH: stops automatic use by task context; VSC: prevents use as a subagent; an explicit `agents` entry overrides it (VSC-SUB) | AG026 |
| `argument-hint` | string | no | | VSC only; "currently not supported for Copilot cloud agent on GitHub.com" (GH-REF); CLI UNVERIFIED | | AG012 (info) |
| `handoffs` | array of objects | no | each: `label` (required), `agent` (required), `prompt`, `send` (default `false`), `model` (`Model Name (vendor)`) | VSC only (GH-REF quote above); CLI UNVERIFIED | | AG012, AG025 |
| `agents` | array | no | agent names, `*`, or `[]` | VSC only; GH and CLI UNVERIFIED | needs the `agent` tool in `tools` | AG009, AG012 |
| `hooks` | object | no (preview) | same format as VS Code hook files; needs `chat.useCustomAgentHooks` | VSC only; GH and CLI UNVERIFIED | events `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PreCompact`, `SubagentStart`, `SubagentStop`, `Stop`; handler `type: command`, `command`, `timeout`/`timeoutSec`, `cwd`, `env`, `windows`/`linux`/`osx`; "Matchers are ignored" (VSC-HOOKS) | AG012; not validated further |
| `mcp-servers` | object keyed by server name | no | per server: `type` (`local`; `stdio` "is mapped to cloud agent's `local` type"), `command`, `args`, `env`, `tools`; `url` and `headers` UNVERIFIED; `http`/`sse` UNVERIFIED | GH, CLI ("Agent profiles can also include MCP server configurations using the `mcp-servers` property", GH-CLI-ABOUT); "not used in VS Code" (GH-REF) | `env` values may be `$COPILOT_MCP_X`, `${COPILOT_MCP_X}`, `${COPILOT_MCP_X:-default}`, `${{ secrets.COPILOT_MCP_X }}`, `${{ vars.COPILOT_MCP_X }}` | AG011 (with `target: vscode`), AG028 (the linter accepts `local`, `stdio`, `http`, `sse`) |
| `metadata` | object of string pairs | no | | GH only; "not used in VS Code" | | AG011 (with `target: vscode`) |

Any other key is unknown [AG017]. The body below the frontmatter is the prompt; on the CLI the page calls it `prompt` but shows it as the Markdown body.

## Limits
- "The prompt can be a maximum of 30,000 characters." (GH-REF, GH-HOWTO) [AG010].
- Filename character set as above [AG013].
- VS Code subagent nesting depth 5 with `chat.subagents.allowInvocationsFromSubagents`; VS Code hook timeout default 30 seconds.
- Count limits for agents, tools or handoffs: UNVERIFIED.

## Deprecated forms
- `infer` (GH "Retired", VSC "Deprecated") [AG005].
- `.chatmode.md`: "Custom agents were previously known as custom chat modes ... rename them to `.agent.md`" (VSC-AGENTS) [AG006]. GitHub pages never mention `.chatmode.md`.
- `stdio` in `mcp-servers` is not deprecated but is mapped to `local` (GH-REF).

## Built-in agents
- VS Code and prompt files: `ask`, `agent`, `plan` (VSC-AGENTS, prompt files page) [handoff and prompt `agent` values the linter accepts without a custom agent].
- Copilot CLI: `explore`, `task`, `general-purpose`, `code-review`, `research` (only via `/research`), `rubber-duck` (GH-CLI-ABOUT).

## Unresolved
- Whether github.com accepts `NAME.md` without `.agent`, and whether the CLI accepts `.agent.md`.
- Precedence between agent locations on every surface.
- Whether github.com honours `model`, and which values it accepts.
- How github.com and the CLI treat `agents`, `hooks`, `argument-hint` and `handoffs` beyond "not supported".
- `mcp-servers` entry schema on the CLI; `url`, `headers`, `http`, `sse` in agent-level `mcp-servers`.
- Tool-name case sensitivity in VS Code; bare `execute` and `todo` in VS Code; `tools: ['*']` in VS Code.
