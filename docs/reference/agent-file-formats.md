# Agent and skill file formats: verified reference

Built on 2026-09-04 from the official documentation pages listed under [Sources](#sources). Every claim carries its source inline; `UNVERIFIED (<url>)` marks a claim the cited page does not state. This file is the only place the format facts live in prose; each skill under `.claude/skills/*/references/` copies the tables it needs from here. The linter (`agentlint_lib/`) encodes the same keys and enumerations; where a page and the linter disagree, fix the linter and this file together.

Surface abbreviations: GH = github.com Copilot cloud agent and code review, VSC = VS Code, CLI = GitHub Copilot CLI, CC = Claude Code.

## Discovery locations

| File kind | Path pattern | GH | VSC | CLI | CC | Section |
|---|---|---|---|---|---|---|
| Copilot custom agent | `.github/agents/*.agent.md` (also `*.md`); org and enterprise `agents/` directories; `~/.copilot/agents` (VSC) | yes | yes | yes | no | Copilot custom agent |
| Claude Code subagent | `.claude/agents/**/*.md`, `~/.claude/agents/**/*.md`, plugin `agents/` | UNVERIFIED | yes (Claude format) | UNVERIFIED | yes | Claude Code subagent |
| Deprecated chat mode | `*.chatmode.md` | no | rename to `.agent.md` | no | no | Copilot custom agent, Deprecated |
| Skill | `.github/skills/<name>/SKILL.md`, `.agents/skills/<name>/SKILL.md`, `.claude/skills/<name>/SKILL.md`; personal `~/.copilot/skills`, `~/.agents/skills`, `~/.claude/skills`; plugin `skills/` | yes | yes | yes | `.claude/skills` and `~/.claude/skills` only | SKILL.md |
| Repository instructions | `.github/copilot-instructions.md` | yes | yes | yes | no (`/init` imports it) | `.github/copilot-instructions.md` |
| Path-specific instructions | `.github/instructions/**/*.instructions.md` | cloud agent and code review | yes (plus `.claude/rules`, `~/.copilot/instructions`) | UNVERIFIED | no | `*.instructions.md` |
| Prompt files | `.github/prompts/*.prompt.md` | no | yes | no | no | `*.prompt.md` |
| Agent instructions | `AGENTS.md` at the root and nested | yes | yes (nested experimental) | UNVERIFIED | no (import it from `CLAUDE.md`) | `AGENTS.md` |
| Claude memory | `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md`, `~/.claude/CLAUDE.md`, managed policy file | no | yes (`chat.useClaudeMdFile`) | UNVERIFIED | yes | Claude Code `CLAUDE.md` |
| Claude rules | `.claude/rules/**/*.md`, `~/.claude/rules/` | no | yes | UNVERIFIED | yes | Claude Code `CLAUDE.md` |
| Claude commands | `.claude/commands/**/*.md` | no | no | CLI plugin reference mentions `.claude/commands/` | yes (legacy, merged into skills) | Claude Code extensions (skills) |
| Cursor rules | `.cursor/rules/*.mdc` | no | no | no | no (`/init` imports them) | Cursor rules |
| Claude MCP | `.mcp.json` at the project root; `~/.claude.json` | no | forwarded via Agent Host | yes (walks up to the repository root) | yes | Claude Code `.mcp.json` |
| VS Code MCP | `.vscode/mcp.json`, user profile `mcp.json` | no | yes | "not read by Copilot CLI" | no | VS Code `.vscode/mcp.json` |
| Copilot CLI MCP | `~/.copilot/mcp-config.json`, `.github/mcp.json` | no | no | yes | no | Copilot CLI MCP config |
| Cloud-agent MCP | repository Settings, Copilot, MCP servers (not in the tree) | yes | no | no | no | Copilot cloud-agent MCP JSON |
| Setup steps | `.github/workflows/copilot-setup-steps.yml` | yes | no | no | no | `.github/workflows/copilot-setup-steps.yml` |
| Claude hooks | `.claude/settings.json`, `.claude/settings.local.json`, `~/.claude/settings.json`, plugin `hooks/hooks.json`, skill and subagent frontmatter | no | reads `.claude/settings.json` hooks with its own semantics | no | yes | Claude Code hooks |
| Claude plugin manifests | `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | no | no | accepted as one of four lookup paths | yes | Claude Code plugins |
| Copilot CLI plugin manifests | `.plugin/plugin.json`, `plugin.json`, `.github/plugin/plugin.json`, `.claude-plugin/plugin.json`; `marketplace.json` in the same four places | no | no | yes | no | Copilot CLI plugins |
| This repository's plugin manifests | `.claude-plugin/plugin.json` lists `agents` as agent file paths (`./.claude/agents/agent-skill-reviewer.md`; a directory fails `claude plugin validate`) and `skills` as `./.claude/skills`; `.github/plugin/plugin.json` points at `.github/agents` and `.claude/skills`; both trees carry a one-entry `marketplace.json` | no | no | yes | yes | Claude Code plugins, Copilot CLI plugins |

## Copilot custom agent (`.agent.md`)
Sources (fetched 2026-09-04):
- GH-REF = https://docs.github.com/en/copilot/reference/custom-agents-configuration
- GH-HOWTO = https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/create-custom-agents
- VSC-AGENTS = https://code.visualstudio.com/docs/agent-customization/custom-agents
- VSC-SUB = https://code.visualstudio.com/docs/agents/run/subagents
- VSC-HOOKS = https://code.visualstudio.com/docs/agent-customization/hooks
- GH-CHEAT = https://docs.github.com/en/copilot/reference/customization-cheat-sheet
- GH-CLI = https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference
- GH-CLI-ABOUT = https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents

Surface abbreviations: GH = github.com Copilot cloud (coding) agent; VSC = VS Code; CLI = GitHub Copilot CLI. All fetch dates 2026-09-04.

### Discovery locations
- **Repository `.github/agents/NAME.agent.md`** — read by GH (GH-HOWTO: "template agent profile called `my-agent.agent.md` in the `.github/agents` directory"), VSC (VSC-AGENTS: Workspace default location `.github/agents`), and CLI (GH-CLI-ABOUT: "Create `.github/agents/CUSTOM-AGENT-NAME.md` in your repository for project-specific agents."; GH-CHEAT: Copilot CLI listed as supported surface; GH-CLI: `/agent` "Browse and select from available agents (if any)"). GH-CHEAT writes the repo path as `.github/agents/AGENT-NAME.md`.
- **Organization level `agents/NAME.agent.md` at the root of the org's `.github` or `.github-private` repository** — GH (GH-HOWTO: "Organization owners can create organization-level custom agents in the organization's `.github` or `.github-private` repository"; "delete the `.github/` portion of the file path to move your template to the root `agents` directory"). GH-CHEAT: `/agents/AGENT-NAME.md` in the organization's `.github` or `.github-private` repository. VSC also discovers these: "VS Code automatically detects custom agents defined at the organization level to which your account has access" when `github.copilot.chat.organizationCustomAgents.enabled` is `true` (VSC-AGENTS). CLI: GH-CLI-ABOUT "Create `/agents/CUSTOM-AGENT-NAME.md` in the organization's `.github` or `.github-private` repository for broader availability within the organization."
- **Enterprise level `agents/NAME.agent.md` in the `.github-private` repository of an organization designated in enterprise settings** — GH (GH-HOWTO). GH-CHEAT: `/agents/AGENT-NAME.md` in a designated `.github-private` repository. CLI: GH-CLI-ABOUT "Create `/agents/CUSTOM-AGENT-NAME.md` in the `.github-private` repository of an organization that an enterprise owner has designated in enterprise settings for availability across all repositories in the enterprise." VSC: UNVERIFIED (VSC-AGENTS).
- **User level `~/.copilot/agents`** — VSC (VSC-AGENTS: "User profile" row = `~/.copilot/agents`; "For sessions that run on Agent Host, the agent reads user-level custom agents from `~/.copilot/agents` and not from VS Code profile user data."). GH-CHEAT lists a "user profile" level for custom agents with no path. CLI user-level location: UNVERIFIED (GH-CLI, GH-CLI-ABOUT — GH-CLI-ABOUT lists only repository, organization and enterprise locations).
- **Workspace `.claude/agents/*.md` (Claude sub-agents format)** — VSC only (VSC-AGENTS: "VS Code also detects `.md` files in the `.claude/agents` folder, following the Claude sub-agents format"). GH/CLI: UNVERIFIED (GH-REF, GH-CLI, GH-CLI-ABOUT — none mention `.claude/agents`).
- **Additional workspace locations** — VSC only, via setting `chat.agentFilesLocations` (VSC-AGENTS). Monorepo: `chat.useCustomizationsInParentRepositories` "to discover custom agents from the parent repository root" (VSC-AGENTS).
- **Precedence between locations** — repo vs org vs enterprise: UNVERIFIED (GH-HOWTO, GH-REF, GH-CHEAT, GH-CLI-ABOUT state no rule). GH-REF only says: "The configuration file's name (minus `.md` or `.agent.md`) is used for deduplication." VSC workspace vs user vs org precedence: UNVERIFIED (VSC-AGENTS: not present).
- **Filename rules** — GH-HOWTO: "the filename may only contain the following characters: `.`, `-`, `_`, `a-z`, `A-Z`, `0-9`". Agent name: GH-HOWTO "If unset, the name will default to the filename (without the `.md` or `.agent.md` suffix)"; VSC-AGENTS "If not specified, the file name is used."; GH-CLI-ABOUT "If omitted, the agent's filename is used as its identifier and default display name."
- **`.agent.md` suffix vs plain `NAME.md`** — VSC-AGENTS states both "Custom agent files are Markdown files and use the `.agent.md` extension." and "VS Code detects any `.md` files in the `.github/agents` folder of your workspace as custom agents." (both quoted; the page carries both). GH: acceptance of plain `NAME.md` is implied by "minus `.md` or `.agent.md`" (GH-REF) and "without the `.md` or `.agent.md` suffix" (GH-HOWTO) but never stated outright — UNVERIFIED (GH-HOWTO). CLI: plain `NAME.md` is the documented pattern — GH-CLI-ABOUT `.github/agents/CUSTOM-AGENT-NAME.md`, example file `readme-creator.md`; whether the CLI also accepts `.agent.md`: UNVERIFIED (GH-CLI-ABOUT never mentions that suffix).
- **CLI agent selection** — GH-CLI: `/agent` "Browse and select from available agents (if any)"; GH-HOWTO: "by using the `/agent` slash command or referencing the agent in a prompt or via a command-line argument"; GH-CLI-ABOUT: "Copilot will automatically use an appropriate built-in agent based on your prompt and the current context." Built-in CLI agents named by GH-CLI-ABOUT: `explore`, `task`, `general-purpose`, `code-review`, `research`, `rubber-duck` ("Unlike the other agents, the research agent can only be invoked by using the `/research` slash command."). Name of the command-line flag (`--agent` or similar): UNVERIFIED (GH-CLI, GH-CLI-ABOUT).
- **`name` allowed characters** — UNVERIFIED (GH-REF, GH-HOWTO, VSC-AGENTS: not present).

### Frontmatter keys
| Key | Type | Required | Allowed values / format | Surfaces that honour it | Notes and source |
|---|---|---|---|---|---|
| `name` | string | Optional | any text | GH, VSC, CLI | GH-REF "Display name for the custom agent. Optional."; GH-CLI-ABOUT "A display name for the custom agent. If omitted, the agent's filename is used as its identifier and default display name."; GH-HOWTO default = filename without `.md`/`.agent.md`; VSC-AGENTS "If not specified, the file name is used." |
| `description` | string | **Required** on GH; Optional on VSC; CLI not stated | any text | GH, VSC, CLI | GH-REF marks Required; GH-CLI-ABOUT "Explains the agent's purpose and capabilities." (required-ness on CLI: UNVERIFIED, GH-CLI-ABOUT); GH-HOWTO "Brief `description` (required)". VSC-AGENTS lists it as optional: "shown as placeholder text in the chat input field." Pages disagree on required-ness. |
| `tools` | list of strings, or comma-separated string (GH); array (VSC) | Optional | tool names/aliases; `<server>/<tool>`; `<server>/*`; `["*"]` (GH) | GH, VSC, CLI | GH-CLI-ABOUT "Specific tools the agent can access. By default, agents can access all available tools, including built-in tools, and MCP server tools." (CLI value list: UNVERIFIED, GH-CLI-ABOUT). GH-REF "Supports both a comma separated string and yaml string array"; "If unset, defaults to all tools"; enable all: "Omit the `tools` property entirely or use `tools: ["*"]`". VSC-AGENTS "A list of tool or tool set names ... Can include built-in tools, tool sets, MCP tools, or tools contributed by extensions"; "If a given tool is not available when using the custom agent, it is ignored." Prompt-file `tools` take precedence over agent `tools` (VSC-AGENTS). |
| `model` | string (GH); string or array (VSC) | Optional | see Model values | VSC, JetBrains, Eclipse, Xcode per GH-HOWTO; GH-REF lists it without surface restriction | GH-REF "Model to use when this custom agent executes. If unset, inherits the default model." VSC-AGENTS "single model name (string) or a prioritized list of models (array)"; default "the currently selected model in model picker". |
| `target` | string | Optional | `vscode` or `github-copilot` | GH, VSC | GH-REF "If unset, defaults to both environments." GH-HOWTO "The agent will be available in both environments if you omit the property." VSC-AGENTS "The target environment or context for the custom agent (`vscode` or `github-copilot`)." |
| `infer` | boolean | Optional, deprecated/retired | `true`/`false` | GH (retired), VSC (deprecated) | GH-REF "**Retired**. Use `disable-model-invocation` and `user-invocable` instead." VSC-AGENTS "**Deprecated.** Use `user-invocable` and `disable-model-invocation` instead." VSC-SUB same. |
| `user-invocable` | boolean | Optional | `true`/`false`; default `true` | GH, VSC | GH-REF "Controls whether this custom agent can be selected by a user. When `false`, the agent cannot be manually selected."; default `true`. VSC-AGENTS "whether the agent appears in the agents dropdown in chat (default is `true`)"; VSC-SUB "Set to `false` to create agents that are only accessible as subagents". |
| `disable-model-invocation` | boolean | Optional | `true`/`false`; default `false` | GH, VSC | GH-REF "Disables Copilot cloud agent from automatically using this custom agent based on task context. When `true`, the agent must be manually selected." VSC-AGENTS "prevent the agent from being invoked as a subagent by other agents (default is `false`)". VSC-SUB: "Explicitly listing an agent in the `agents` array overrides `disable-model-invocation: true`". |
| `argument-hint` | string | Optional | any text | VSC only | VSC-AGENTS "Optional hint text shown in the chat input field to guide users on how to interact with the custom agent." GH-REF: "`argument-hint` and `handoffs` properties from VS Code and other IDE custom agents are currently not supported for Copilot cloud agent on GitHub.com". CLI: UNVERIFIED (GH-CLI, GH-CLI-ABOUT). |
| `handoffs` | array of objects | Optional | list of handoff objects (sub-keys below) | VSC only | VSC-AGENTS "Optional list of suggested next actions or prompts to transition between custom agents." Not supported on GH (GH-REF, quoted above). CLI: UNVERIFIED (GH-CLI, GH-CLI-ABOUT). |
| `handoffs[].label` | string | Required when `handoffs` used | any text | VSC | VSC-AGENTS "The display text shown on the handoff button." |
| `handoffs[].agent` | string | Required when `handoffs` used | agent identifier (example uses `agent: agent`) | VSC | VSC-AGENTS "The target agent identifier to switch to." Identifier semantics: UNVERIFIED (VSC-AGENTS). |
| `handoffs[].prompt` | string | Optional | any text | VSC | VSC-AGENTS "The prompt text to send to the target agent." |
| `handoffs[].send` | boolean | Optional | `true`/`false`; default `false` | VSC | VSC-AGENTS "Optional boolean flag to auto-submit the prompt (default is `false`)". |
| `handoffs[].model` | string | Optional | `Model Name (vendor)`, e.g. `GPT-5 (copilot)`, `Claude Sonnet 4.5 (copilot)` | VSC | VSC-AGENTS "Optional language model to use when the handoff executes. Use the qualified model name in the format `Model Name (vendor)`". |
| `agents` | array | Optional | list of agent names (e.g. `['Edit', 'Search']`), `*` (all; default behaviour), or `[]` (none) | VSC only (GH: UNVERIFIED, GH-REF does not list it; CLI: UNVERIFIED, GH-CLI, GH-CLI-ABOUT) | VSC-AGENTS "A list of agent names that are available as subagents in this agent. Use `*` to allow all agents, or an empty array `[]` to prevent any subagent use." Requires `agent` tool in `tools` (VSC-AGENTS example `tools: ['agent']`). Self-reference needs `chat.subagents.allowInvocationsFromSubagents` (VSC-AGENTS). |
| `hooks` | object | Optional (Preview) | same format as hook configuration files: event name -> array of hook command objects | VSC only (GH: UNVERIFIED, GH-REF does not list it; CLI: UNVERIFIED, GH-CLI, GH-CLI-ABOUT) | VSC-AGENTS "`(Preview)` Optional hook commands scoped to this agent. Hooks defined here only run when this agent is active, either invoked by the user or as a subagent. Uses the same format as hook configuration files. Requires `chat.useCustomAgentHooks` to be enabled." See section below. |
| `mcp-servers` | object keyed by server name (GH); described as "list of ... config json" (VSC) | Optional | map of `<server-name>: {type, command, args, tools, env}` | GH, CLI (not VSC) | GH-CLI-ABOUT "Agent profiles can also include MCP server configurations using the `mcp-servers` property." (entry schema on CLI: UNVERIFIED, GH-CLI-ABOUT). GH-REF "Additional MCP servers and tools"; "`mcp-servers` property...is not used in VS Code and other IDE custom agents". VSC-AGENTS "Optional list of Model Context Protocol (MCP) server config json to use with custom agents in GitHub Copilot (target: `github-copilot`)." GH-HOWTO: configure MCP servers available only to this agent. |
| `mcp-servers.<name>.type` | string | UNVERIFIED (GH-REF does not mark) | `local`; `stdio` accepted and mapped to `local` | GH | GH-REF "For compatibility, the `stdio` type used by Claude Code and VS Code is mapped to cloud agent's `local` type." Other values (`http`, `sse`): UNVERIFIED (GH-REF). |
| `mcp-servers.<name>.command` | string | UNVERIFIED (GH-REF does not mark) | executable, e.g. `'some-command'` | GH | GH-REF example. |
| `mcp-servers.<name>.args` | array of strings | Optional | e.g. `['--arg1', '--arg2']` | GH | GH-REF example. |
| `mcp-servers.<name>.env` | object | Optional | `ENV_VAR_NAME: value`; value syntaxes documented: `$COPILOT_MCP_ENV_VAR_VALUE`, `${COPILOT_MCP_ENV_VAR_VALUE}`, `${COPILOT_MCP_ENV_VAR_VALUE:-default}`, `${{ secrets.COPILOT_MCP_ENV_VAR_VALUE }}`, `${{ vars.COPILOT_MCP_ENV_VAR_VALUE }}` | GH | GH-REF. |
| `mcp-servers.<name>.tools` | array of strings | Optional | tool names or `["*"]` | GH | GH-REF example `tools: ["*"]`. |
| `mcp-servers.<name>.url` | — | — | — | — | UNVERIFIED (GH-REF does not document `url`). |
| `mcp-servers.<name>.headers` | — | — | — | — | UNVERIFIED (GH-REF does not document `headers`). |
| `metadata` | object of string name/value pairs | Optional | `key: value`, both strings | GH only | GH-REF "object consisting of a name and value pair, both strings. Allows annotation of the agent with useful data."; "`metadata` property...is not used in VS Code and other IDE custom agents". |

CLI profile format (GH-CLI-ABOUT "Agent profile format"): `name` (optional), `description`, `prompt` ("Custom instructions that define the agent's behavior and expertise"), `tools` (optional), `mcp-servers`. In the page's example (`readme-creator.md`) the prompt is the Markdown body below the frontmatter, not a frontmatter key. `model`, `target`, `infer`, `user-invocable`, `disable-model-invocation`, `metadata`, `agents`, `hooks`, `argument-hint`, `handoffs` on CLI: UNVERIFIED (GH-CLI-ABOUT does not mention them).

Claude sub-agents format (`.claude/agents/*.md`, read by VSC only; VSC-AGENTS):
| Key | Type | Required | Allowed values / format | Surfaces | Notes and source |
|---|---|---|---|---|---|
| `name` | string | Required | any text | VSC | VSC-AGENTS "`name` Agent name (required)". |
| `description` | string | Optional | any text | VSC | VSC-AGENTS "What the agent does". |
| `tools` | comma-separated string | Optional | e.g. `"Read, Grep, Glob, Bash"` | VSC | VSC-AGENTS "Comma-separated string of allowed tools"; "VS Code maps Claude-specific tool names to the corresponding VS Code tools." |
| `disallowedTools` | comma-separated string | Optional | tool names | VSC | VSC-AGENTS "Comma-separated string of tools to block". |

Out-of-the-box MCP servers on GH (GH-REF): `github` — "All read-only tools are available by default, but the token the server receives is scoped to the source repository."; `playwright` — "All playwright tools are available by default, but the server is configured to only access localhost."

### Tool names
Case sensitivity: GH-REF "All aliases are case insensitive." VSC-AGENTS: UNVERIFIED (page silent). CLI: UNVERIFIED (GH-CLI, GH-CLI-ABOUT — no `tools` value list; GH-CLI-ABOUT only names `grep`, `glob`, `view` and `shell` tools in prose about the built-in `explore` agent).

| Tool name or alias | Meaning | Surfaces | Source |
|---|---|---|---|
| `execute` (primary) | "Execute a command in the appropriate shell for the operating system"; cloud agent mapping: shell tools `bash` or `powershell` | GH (VSC bare `execute`: UNVERIFIED, VSC-AGENTS) | GH-REF alias table |
| `shell`, `Bash`, `powershell` | compatible aliases of `execute` | GH | GH-REF |
| `read` (primary) | "Read file contents"; cloud agent mapping `view` | GH, VSC (VSC-SUB example `tools: ['agent', 'read', 'search']`) | GH-REF, VSC-SUB |
| `Read`, `NotebookRead` | compatible aliases of `read` | GH | GH-REF |
| `edit` (primary) | "Allow LLM to edit"; cloud agent mapping e.g. `str_replace`, `str_replace_editor` | GH, VSC | GH-REF, VSC-AGENTS |
| `Edit`, `MultiEdit`, `Write`, `NotebookEdit` | compatible aliases of `edit` | GH | GH-REF |
| `search` (primary) | "Search for files or text in files"; cloud agent mapping `search` | GH, VSC | GH-REF, VSC-AGENTS |
| `Grep`, `Glob` | compatible aliases of `search` | GH | GH-REF |
| `agent` (primary) | "Allows different custom agent invocation"; cloud agent mapping "Custom agent" tools | GH, VSC | GH-REF, VSC-AGENTS (`tools: ['agent']` required for `agents`) |
| `custom-agent`, `Task` | compatible aliases of `agent` | GH | GH-REF |
| `web` (primary) | "Fetching content and web search"; cloud agent: "Currently not applicable" | VSC; GH accepts alias but not applicable | GH-REF, VSC-AGENTS |
| `WebSearch`, `WebFetch` | compatible aliases of `web` | GH | GH-REF |
| `todo` (primary) | "Structured task lists"; cloud agent: "Currently not applicable" | GH alias table (VSC bare `todo`: UNVERIFIED, VSC-AGENTS) | GH-REF |
| `TodoWrite` | compatible alias of `todo` | GH | GH-REF |
| `*` (as `tools: ["*"]`) | enable all tools | GH (VSC `tools: ['*']`: UNVERIFIED, VSC-AGENTS not present) | GH-REF |
| `<server>/<tool>` (e.g. `some-mcp-server/some-tool`, `custom-mcp/tool-1`) | one tool from a named MCP server | GH, VSC | GH-REF, GH-HOWTO, VSC-AGENTS |
| `<server>/*` (e.g. `some-mcp-server/*`) | all tools from a named MCP server | GH, VSC | GH-REF "explicitly enable all tools from a specific MCP server using `some-mcp-server/*`"; VSC-AGENTS "use the `<server name>/*` format" |
| `web/fetch`, `search/codebase`, `search/usages`, `read/terminalLastCommand` | VS Code sub-tools of built-in tool groups (examples on page) | VSC | VSC-AGENTS example `tools: ['web/fetch', 'search/codebase', 'search/usages']`; `#tool:web/fetch` body syntax |
| `agent/runSubagent`, `runSubagent` | subagent invocation tool | VSC | VSC-SUB "make sure the `agent/runSubagent` tool is enabled"; prompt files: "`runSubagent` or `agent` tool" |
| tool set names | user-defined tool sets | VSC | VSC-AGENTS "tool or tool set names" |
| extension-contributed tools | tools contributed by VS Code extensions | VSC | VSC-AGENTS |
| `view`, `str_replace`, `str_replace_editor`, `bash`, `powershell`, `search` | cloud-agent-side tool names that the aliases map to | GH (as mapping targets) | GH-REF alias table. Use of these names in CLI agent files: UNVERIFIED (GH-CLI, GH-CLI-ABOUT) |
| `grep`, `glob`, `view`, `shell` (prose only) | tools of the CLI built-in `explore` agent: "uses code intelligence, grep, glob, view, and shell tools"; not documented as `tools`-key values | CLI | GH-CLI-ABOUT |
| Claude names `Read, Grep, Glob, Bash` (comma-separated) | Claude sub-agents format tools, mapped to VS Code tools | VSC (`.claude/agents`) | VSC-AGENTS |

### Model values
- GH (GH-REF): `model` = "Model to use when this custom agent executes. If unset, inherits the default model." No accepted values enumerated. Whether the github.com cloud agent itself honours `model`: UNVERIFIED (GH-REF lists it; GH-HOWTO only says "If you are creating and using the agent profile in VS Code, JetBrains IDEs, Eclipse, or Xcode, you can also use the `model` property").
- VSC (VSC-AGENTS): string or array; "When you specify an array, the system tries each model in order until an available one is found."; "If not specified, the currently selected model in model picker is used." Format `Model Name (vendor)`. Documented display names: `Claude Opus 4.5`, `GPT-5.2` (example `model: ['Claude Opus 4.5', 'GPT-5.2']`), `Claude Sonnet 4.5 (copilot)`, `GPT-5 (copilot)` (the latter two in `handoffs[].model`).
- CLI: UNVERIFIED (GH-CLI, GH-CLI-ABOUT — `model` not mentioned).

### Limits
- Prompt body: "The prompt can be a maximum of 30,000 characters." (GH-REF, GH-HOWTO). VSC-AGENTS: no body limit stated.
- Filename characters: `.`, `-`, `_`, `a-z`, `A-Z`, `0-9` (GH-HOWTO).
- Subagent nesting: with `chat.subagents.allowInvocationsFromSubagents` enabled (default `false`), "subagents can spawn their own subagents, up to a maximum nesting depth of 5" (VSC-SUB). By default subagents cannot invoke further subagents (VSC-SUB).
- Hook handler `timeout`/`timeoutSec`: integer seconds, default 30 (VSC-HOOKS).
- Count limits (agents per repo/org, handoffs, tools): UNVERIFIED (GH-REF, GH-HOWTO, VSC-AGENTS, GH-CHEAT — none stated).

### Deprecated forms
- `infer` — GH-REF: "**Retired**. Use `disable-model-invocation` and `user-invocable` instead."; VSC-AGENTS: "**Deprecated.** Use `user-invocable` and `disable-model-invocation` instead."; VSC-SUB: "The `infer` property is deprecated." Prior semantics (VSC-AGENTS): `infer: true` (default) = visible and available as subagent; `infer: false` = hidden from both.
- `.chatmode.md` / "custom chat modes" — VSC-AGENTS: "Custom agents were previously known as custom chat modes. ... If you have existing `.chatmode.md` files, rename them to `.agent.md` to convert them to the new custom agent format" and place them in a `chat.agentFilesLocations` location. GH pages: no mention of `.chatmode.md` (GH-REF, GH-HOWTO, GH-CHEAT).
- `stdio` MCP type — not deprecated, but compatibility-mapped: "the `stdio` type used by Claude Code and VS Code is mapped to cloud agent's `local` type" (GH-REF).
- Preview status (not deprecated): agent-scoped `hooks` "currently in preview" (VSC-AGENTS, VSC-HOOKS); agent hooks overall "currently in Preview. The configuration format and behavior might change" (VSC-HOOKS); custom agents "in public preview for JetBrains IDEs, Eclipse, and Xcode" (GH-HOWTO); GH-CHEAT marks JetBrains/Eclipse/Xcode as P (preview).

### VS Code hooks in agent files
- Key: `hooks` in `.agent.md` frontmatter (VSC-HOOKS lists "Custom agent: `hooks` field in `.agent.md` frontmatter" as a hook location). Status: "Agent-scoped hooks are currently in preview." Requires setting `chat.useCustomAgentHooks` = `true` (VSC-HOOKS, VSC-AGENTS).
- Scope: "Agent-scoped hooks only run when that custom agent is active, either selected by the user or invoked as a subagent. Agent-scoped hooks run in addition to any workspace or user-level hooks configured for the same event." (VSC-HOOKS)
- Schema: identical to the JSON hook configuration file format — event name -> array of hook command objects (VSC-HOOKS). Example on both pages:
  ```yaml
  hooks:
    PostToolUse:
      - type: command
        command: "./scripts/format-changed-files.sh"
  ```
- Events (exact spelling, VSC-HOOKS): `SessionStart` ("User submits the first prompt of a new session"), `UserPromptSubmit` ("User submits a prompt"), `PreToolUse` ("Before agent invokes any tool"), `PostToolUse` ("After tool completes successfully"), `PreCompact` ("Before conversation context is compacted"), `SubagentStart` ("Subagent is spawned"), `SubagentStop` ("Subagent completes"), `Stop` ("Agent session ends").
- Handler object fields (VSC-HOOKS): required `type` = `"command"`, `command` (string); optional `timeout` or `timeoutSec` (integer seconds, default 30), `cwd` (string), `env` (object), `windows` / `linux` / `osx` (OS-specific command override strings; "If no OS-specific command is defined, it falls back to the `command` property").
- Handler stdin (all events): `timestamp`, `cwd` (optional), `session_id` (optional), `hook_event_name`, `transcript_path` (optional). `PreToolUse` input adds `tool_name`, `tool_input` (VSC-HOOKS).
- Handler stdout (all events): `continue` (boolean, default `true`), `stopReason` (string, shown when `continue` is `false`), `systemMessage` (string, "always displayed"). `PreToolUse` supports `hookSpecificOutput` with `permissionDecision` = `allow` | `deny` | `ask`. "the most restrictive wins" when mechanisms combine (VSC-HOOKS). Full per-event schema is deferred to a separate hooks-reference page (not in scope) — UNVERIFIED here.
- Exit codes (VSC-HOOKS): `0` "Success: parse stdout as JSON"; `2` "Blocking error: stop processing and show error to model"; other "Non-blocking warning: show warning to user, continue processing".
- Claude-compat note (VSC-HOOKS): "Matchers are ignored: Hook matchers like `"Edit|Write"` are parsed but not applied. All hooks run on every matching event, regardless of the tool name in the matcher."
- Other hook locations/precedence (VSC-HOOKS): workspace `.github/hooks/*.json`, `.claude/settings.json`, `.claude/settings.local.json`; user `~/.copilot/hooks`, `~/.claude/settings.json`; plugin `hooks.json` or `hooks/hooks.json`; setting `chat.hookFilesLocations`. "Workspace hooks take precedence over user hooks for the same event type."
- GH/CLI support for `hooks` inside `.agent.md`: UNVERIFIED (GH-REF does not list `hooks`; GH-CLI and GH-CLI-ABOUT silent).

### Unresolved / UNVERIFIED
- CLI user-level agent directory (e.g. `~/.copilot/agents`) — UNVERIFIED (https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference; https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents documents only repository, organization and enterprise locations).
- Whether the CLI accepts the `.agent.md` suffix (page shows only `CUSTOM-AGENT-NAME.md` / `readme-creator.md`) — UNVERIFIED (https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents).
- Whether the CLI honours `model`, `target`, `infer`, `user-invocable`, `disable-model-invocation`, `metadata`, `agents`, `hooks`, `argument-hint`, `handoffs`, and the `mcp-servers` entry schema on CLI — UNVERIFIED (https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents mentions only `name`, `description`, `prompt`, `tools`, `mcp-servers`).
- CLI command-line flag for selecting an agent — UNVERIFIED (GH-HOWTO says "via a command-line argument" without naming it; https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference and https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents do not name it).
- CLI tool names usable in `tools` (`view`, `bash`, `str_replace`, `--allow-tool` syntax) — UNVERIFIED (https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference; https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents gives no `tools` value list, only prose naming `grep`, `glob`, `view`, `shell`; only GH-REF's cloud-agent mapping column names `view`/`bash`/`str_replace`).
- Precedence when the same agent name exists at repository, organization and enterprise level — UNVERIFIED (https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/create-custom-agents, https://docs.github.com/en/copilot/reference/custom-agents-configuration, https://docs.github.com/en/copilot/reference/customization-cheat-sheet, https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents).
- Precedence in VS Code between workspace, user and organization agents with the same name — UNVERIFIED (https://code.visualstudio.com/docs/agent-customization/custom-agents).
- Whether github.com accepts `NAME.md` without `.agent` suffix — implied, not stated — UNVERIFIED (https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/create-custom-agents).
- `mcp-servers.<name>.url`, `.headers`, and `type` values other than `local`/`stdio` — UNVERIFIED (https://docs.github.com/en/copilot/reference/custom-agents-configuration).
- Whether `mcp-servers.<name>.type` and `.command` are required — UNVERIFIED (https://docs.github.com/en/copilot/reference/custom-agents-configuration shows them only in an example).
- `tools: ['*']` on VS Code — UNVERIFIED (https://code.visualstudio.com/docs/agent-customization/custom-agents; only `<server name>/*` shown).
- Bare `execute` and `todo` as VS Code tool names — UNVERIFIED (https://code.visualstudio.com/docs/agent-customization/custom-agents shows `search`, `web`, `edit`, `agent` and sub-tools only).
- Case sensitivity of tool names in VS Code — UNVERIFIED (https://code.visualstudio.com/docs/agent-customization/custom-agents).
- Whether the github.com cloud agent honours `model` and which values it accepts — UNVERIFIED (https://docs.github.com/en/copilot/reference/custom-agents-configuration lists the key without values; https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/create-custom-agents scopes it to IDEs).
- Whether github.com/CLI ignore or reject `agents`, `hooks`, `argument-hint`, `handoffs` — GH-REF states only that `argument-hint` and `handoffs` are "currently not supported"; `agents`/`hooks` behaviour UNVERIFIED (https://docs.github.com/en/copilot/reference/custom-agents-configuration).
- `name` allowed characters and `handoffs[].agent` identifier rules — UNVERIFIED (https://code.visualstudio.com/docs/agent-customization/custom-agents, https://docs.github.com/en/copilot/reference/custom-agents-configuration).
- User-level ("user profile") agent path for github.com — UNVERIFIED (https://docs.github.com/en/copilot/reference/customization-cheat-sheet names the level without a path).
- Whether github.com or CLI read `.claude/agents/*.md` — UNVERIFIED (https://docs.github.com/en/copilot/reference/custom-agents-configuration, https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference, https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents).
- Per-event hook input/output fields beyond the common fields and `PreToolUse` — UNVERIFIED (https://code.visualstudio.com/docs/agent-customization/hooks defers to /docs/agents/reference/hooks-reference).
- Whether Visual Studio (marked supported in GH-CHEAT) honours the same key set — UNVERIFIED (https://docs.github.com/en/copilot/reference/customization-cheat-sheet).
- Any count limits (agents, handoffs, tools) — UNVERIFIED (all seven URLs; none stated).

Source abbreviations used inline: SA = https://code.claude.com/docs/en/sub-agents, HK = https://code.claude.com/docs/en/hooks, PR = https://code.claude.com/docs/en/plugins-reference, CP = https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference. All fetched 2026-09-04 (WebFetch plus the raw Markdown/HTML of the same URLs).

## Claude Code subagent (`.claude/agents/*.md`)
Sources: https://code.claude.com/docs/en/sub-agents, https://code.claude.com/docs/en/plugins-reference (plugin-shipped agents), https://code.claude.com/docs/en/hooks (frontmatter hooks) (fetched 2026-09-04)

### Discovery locations
- Priority table, highest first: (1) Managed settings, "Organization-wide", "Deployed via managed settings"; (2) `--agents` CLI flag, "Current session", "Pass JSON when launching Claude Code"; (3) `.claude/agents/`, "Current project"; (4) `~/.claude/agents/`, "All your projects"; (5) Plugin's `agents/` directory, "Where plugin is enabled" (SA).
- Managed: "Place markdown files in `.claude/agents/` inside the managed settings directory, using the same frontmatter format as project and user subagents. Managed definitions take precedence over project and user subagents with the same name." (SA)
- `--agents` JSON: "accepts JSON with a `prompt` field plus these frontmatter fields: `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `mcpServers`, `hooks`, `maxTurns`, `skills`, `initialPrompt`, `memory`, `effort`, `background`, and `isolation`. Use `prompt` for the system prompt ... Each top-level key in the JSON is the agent's name. Don't start a name with `-`." Example passes `"tools": ["Read", "Grep", "Glob", "Bash"]` as a JSON array (SA).
- `--agent <name>` runs a subagent definition as the main thread; `"agent": "<name>"` in `.claude/settings.json` makes it the default; "The CLI flag overrides the setting if both are present." (SA)
- Recursive scan: "Claude Code scans `.claude/agents/` and `~/.claude/agents/` recursively ... The subdirectory path doesn't affect how a subagent is identified or invoked, because identity comes only from the `name` frontmatter field." (SA)
- Plugin agents: "Plugin `agents/` directories are also scanned recursively. Unlike project and user scopes, a subfolder inside a plugin's `agents/` directory becomes part of the scoped identifier: a file at `agents/review/security.md` in plugin `my-plugin` registers as `my-plugin:review:security`." Scoped name form `my-plugin:code-reviewer` (SA, PR).
- `--add-dir` / `/add-dir` directories: their `.claude/agents/` are loaded alongside project subagents; not watched for changes (SA).
- Filename rule: "The filename doesn't have to match" the `name` (SA). Plugin agents only: "No `name`: Claude Code names the agent after the file, so `agents/reviewer.md` in a plugin named `my-plugin` loads as `my-plugin:reviewer`"; unparseable plugin-agent frontmatter loads with description `Agent from my-plugin plugin` and every field ignored (PR).
- `name` rules: "Unique identifier using lowercase letters and hyphens"; "Names can't contain `:`, which is reserved for plugin-scoped identifiers such as `my-plugin:reviewer`"; a `name` starting with `-` or containing `:` is skipped with a debug-log error; "Before v2.1.218, such names were accepted" (SA). Hooks receive `name` as `agent_type` (SA).
- Files Claude Code skips (project, user, managed, `--add-dir`): no `name` (treated as documentation); opening `---` not on first line (treated as documentation); `name` starting with `-` or containing `:`; `name` but no `description`; YAML that doesn't parse (SA). "By contrast" plugin agents still load in the no-`name`/unparseable cases (PR).
- Duplicate names in one directory: UNVERIFIED (https://code.claude.com/docs/en/sub-agents) — the first WebFetch summary claimed "filesystem read order" but the sentence was not found in the raw page.

### Frontmatter keys
| Key | Type | Required | Allowed values / format | Notes and source |
| --- | --- | --- | --- | --- |
| `name` | string | Yes | lowercase letters and hyphens; no leading `-`; no `:` | Used as `agent_type` in hooks (SA https://code.claude.com/docs/en/sub-agents) |
| `description` | string | Yes | free text | "When Claude should delegate to this subagent"; drives automatic delegation; "include phrases like 'use proactively'" (SA) |
| `tools` | string (comma-separated) | No | exact tool names; `mcp__<server>`; `mcp__<server>__*`; `Agent(agent_type, ...)`; `Agent` | Every example on the page is a comma-separated string, e.g. `tools: Read, Grep, Glob, Bash`, `tools: Agent(worker, researcher), Read, Bash`. YAML-list form: UNVERIFIED (https://code.claude.com/docs/en/sub-agents — no list-form example on the page; the `--agents` JSON form uses an array). "Inherits every tool available to subagents if omitted." "If no entry in the list resolves to a tool, the subagent usually fails to launch." "To preload Skills into context, use the `skills` field rather than listing `Skill` here" (SA) |
| `disallowedTools` | string (comma-separated) | No | exact names; `mcp__<server>`; `mcp__<server>__*`; `mcp__*` | "Tools to deny, removed from inherited or specified list"; "`disallowedTools` is applied first, then `tools` is resolved against the remaining pool. A tool listed in both is removed." Example `disallowedTools: mcp__github` (SA) |
| `model` | string | No | `sonnet`, `opus`, `haiku`, `fable`, full model ID such as `claude-opus-5`, or `inherit` | Omitted: resolution order (1) per-invocation `model` parameter, (2) frontmatter `model` (`inherit` = main model), (3) `CLAUDE_CODE_SUBAGENT_MODEL` env var, (4) main conversation's model (SA) |
| `permissionMode` | string | No | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`, `manual` (alias for `default`, v2.1.200+) | "Ignored for plugin subagents." Parent `bypassPermissions`/`acceptEdits` take precedence; parent auto mode makes frontmatter value ignored (SA) |
| `maxTurns` | number | No | integer | "Maximum number of agentic turns before the subagent stops"; output marked partial (marking requires v2.1.246+) (SA) |
| `skills` | list of strings | No | skill names | YAML list example `skills:\n  - api-conventions\n  - error-handling-patterns`; "The full skill content is injected, not only the description" (SA) |
| `mcpServers` | list | No | each entry a server-name string or an inline object keyed by server name with `.mcp.json`-style config; types `stdio`, `http`, `sse`, `ws` | "Ignored for plugin subagents." Inline servers in project `.claude/agents/` require trust (v2.1.238+) (SA) |
| `hooks` | map | No | `<EventName>: [ { matcher, hooks: [handler...] } ]`, same format as settings | "Ignored for plugin subagents." Subagent-frontmatter events table: `PreToolUse` (tool name), `PostToolUse` (tool name), `Stop` (none; "converted to `SubagentStop` at runtime") (SA). HK says of skill and subagent frontmatter hooks: "All hook events are supported." — record both (HK https://code.claude.com/docs/en/hooks) |
| `memory` | string | No | `user`, `project`, `local` | "Enables cross-session learning" (SA) |
| `background` | boolean | No | `true` | "keep this subagent in the background even when Claude asks to run it in the foreground" (SA) |
| `effort` | string | No | `low`, `medium`, `high`, `xhigh`, `max` | "Overrides the session effort level. Default: inherits from session ... available levels depend on the model" (SA) |
| `isolation` | string | No | `worktree` | temporary git worktree branched by default from the default branch, not parent `HEAD`; cleaned up if no changes (SA). PR: "The only valid `isolation` value is `\"worktree\"`" |
| `color` | string | No | `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan` | task list and transcript display (SA) |
| `initialPrompt` | string | No | free text | auto-submitted first user turn when run as main session via `--agent` or `agent` setting (SA) |
| `experimental` | map | No | `cacheTtl: 5m` or `cacheTtl: 1h` | "Claude Code ignores any other value"; `1h` ignored while using usage credits; v2.1.248+ (SA) |
| body (below frontmatter) | Markdown | — | — | "The body becomes the system prompt"; subagents get only this plus basic environment details, not the Claude Code system prompt (SA) |

Plugin-shipped agents: "Plugin agents support `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, and `isolation` frontmatter fields ... `hooks`, `mcpServers`, and `permissionMode` are not supported for plugin-shipped agents." (PR). SA lists `color`, `initialPrompt`, `experimental` for subagents generally; PR's plugin list does not name them — record both.

Built-in tool names documented (SA "Available tools"): removed from every subagent: `Agent` (at depth limit), `AskUserQuestion`, `EndConversation`, `EnterPlanMode`, `ExitPlanMode` (unless `permissionMode: plan`), `ScheduleWakeup`, `TaskOutput`, `WaitForMcpServers`, `Workflow`. Background subagents keep every MCP tool but only these built-ins: `Read`, `Grep`, `Glob`, `Bash`, `PowerShell`, `Edit`, `Write`, `NotebookEdit`, `WebFetch`, `WebSearch`, `TodoWrite`, `Skill`, `ToolSearch`, `EnterWorktree`, `ExitWorktree`, `Monitor`, `TaskStop`, `SendMessage`, `Artifact`. Teammates additionally keep `TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate`, `CronCreate`, `CronDelete`, `CronList`. Permission-rule patterns such as `Bash(git:*)` or `Edit(*.ts)` inside `tools`/`disallowedTools`: UNVERIFIED (https://code.claude.com/docs/en/sub-agents — none found on the page; the only parenthesised form is `Agent(agent_type)`).

### Enum values
| Key | Documented values | Source |
| --- | --- | --- |
| `permissionMode` | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`, `manual` (alias for `default`, v2.1.200+) | https://code.claude.com/docs/en/sub-agents |
| `memory` | `user` (`~/.claude/agent-memory/<name-of-agent>/`), `project` (`.claude/agent-memory/<name-of-agent>/`), `local` (`.claude/agent-memory-local/<name-of-agent>/`) | https://code.claude.com/docs/en/sub-agents |
| `effort` | `low`, `medium`, `high`, `xhigh`, `max` | https://code.claude.com/docs/en/sub-agents |
| `color` | `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan` | https://code.claude.com/docs/en/sub-agents |
| `isolation` | `worktree` | https://code.claude.com/docs/en/sub-agents, https://code.claude.com/docs/en/plugins-reference |
| `model` aliases | `sonnet`, `opus`, `haiku`, `fable`; special `inherit`; full IDs e.g. `claude-opus-5`, `claude-sonnet-5` | https://code.claude.com/docs/en/sub-agents |
| `experimental.cacheTtl` | `5m`, `1h` | https://code.claude.com/docs/en/sub-agents |
| `mcpServers[].<name>.type` | `stdio`, `http`, `sse`, `ws` | https://code.claude.com/docs/en/sub-agents |

### Limits
- Description budget: "When the combined descriptions of your subagents, except the built-in ones, exceed 15,000 tokens, Claude Code shows a warning at startup" and "still loads every subagent" (SA).
- Nesting depth: `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` sets layers below the main conversation (example caps at `"2"`); default value: UNVERIFIED (https://code.claude.com/docs/en/sub-agents — summary said 3, sentence not confirmed in raw text) (SA).
- Concurrency: "when 20 subagents are running in a session, spawning another with the Agent tool fails with `Concurrent subagent limit reached`"; change with `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`; ultracode sessions exempt; requires v2.1.217+ (SA).
- Memory file: system prompt includes "the first 200 lines or 25KB of `MEMORY.md` in the memory directory, whichever comes first" (SA).
- `maxTurns`: no default limit stated (SA table row).

### Deprecated forms
- "In version 2.1.63, the Task tool was renamed to Agent. Existing `Task(...)` references in settings and agent definitions still work as aliases." (SA)
- `permissionMode: manual` is an alias for `default` (v2.1.200+) (SA).
- `CLAUDE_CODE_SUBAGENT_MODEL=inherit` "is the same as leaving it unset. Before v2.1.196, that value forced subagents onto the main conversation's model" (SA).

## Claude Code hooks (settings files, plugin `hooks/hooks.json`, subagent and skill frontmatter)
Sources: https://code.claude.com/docs/en/hooks, https://code.claude.com/docs/en/plugins-reference, https://code.claude.com/docs/en/sub-agents (fetched 2026-09-04)

### Where hooks can be declared
- Hook locations table (HK): `~/.claude/settings.json` (All your projects; not shareable); `.claude/settings.json` (Single project; committable); `.claude/settings.local.json` (Single project; "gitignored when Claude Code saves a setting to it"); Managed policy settings (Organization-wide; admin-controlled); `[Plugin]/hooks/hooks.json` (when plugin enabled); Skill frontmatter (rest of session after skill invoked); Subagent frontmatter (while that subagent is running).
- Shape in settings: `"hooks": { "<EventName>": [ { "matcher": "...", "hooks": [ { handler } ] } ] }` (HK).
- Plugin: "Define plugin hooks in `hooks/hooks.json` with an optional top-level `description` field. When a plugin is enabled, its hooks merge with your user and project hooks." (HK). PR: "**Location**: `hooks/hooks.json` in plugin root, or inline in plugin.json"; PR example has only the top-level `hooks` key and does not mention `description` — record both (PR https://code.claude.com/docs/en/plugins-reference).
- Frontmatter (HK "Hooks in skills and agents"): same configuration format as settings; "Subagent hooks: Claude Code runs them only while that subagent is running ... converts a `Stop` hook here to `SubagentStop`"; "Skill hooks: ... registers them when you or Claude invoke the skill and keeps running them for the rest of the session"; "All hook events are supported." SA's subagent table lists only `PreToolUse`, `PostToolUse`, `Stop` — record both (https://code.claude.com/docs/en/sub-agents).
- `once`: "Only honored for hooks declared in skill frontmatter; ignored in settings files and agent frontmatter" (HK).
- Trust: project-subagent frontmatter hooks "run only after you accept the workspace trust dialog ... A `-p` session doesn't count"; project-skill frontmatter hooks follow the settings-file workspace trust rule and register "including in a `-p` run in a folder you haven't trusted" (HK).
- Merge: "Hook entries merge across settings levels rather than replacing each other"; "If you define the same handler in more than one settings file, it runs once. A plugin's or skill's copy of the same handler stays separate." (HK)
- Settings keys: `disableAllHooks` (a `false` in project settings overrides a `true` in user settings; cannot disable managed hooks unless set at managed level); `allowManagedHooksOnly` (enterprise; plugins force-enabled in managed `enabledPlugins` exempt); `allowedHttpHookUrls`; `httpHookAllowedEnvVars` (HK).
- `/hooks` menu sources: `User Settings`, `Project Settings`, `Local Settings`, `Plugin Hooks`, `Session Hooks` (HK).
- Cloud sessions "don't read your local `~/.claude/settings.json`" (HK).
- Plugin-bundled MCP servers in hooks: matchers and `if` use `mcp__plugin_<plugin-name>_<server-name>__<tool>`; `mcp_tool` `server` uses `plugin:<plugin-name>:<server-name>` (PR, HK).

### Event names
| Event | Fires when | Matcher applies to | Source |
| --- | --- | --- | --- |
| `SessionStart` | "When a session begins or resumes" | how the session started: `startup`, `resume`, `clear`, `compact`, `fork` | https://code.claude.com/docs/en/hooks |
| `Setup` | "When you start Claude Code with `--init-only`, or with `--init` or `--maintenance` in `-p` mode" | which CLI flag: `init`, `maintenance` | https://code.claude.com/docs/en/hooks |
| `UserPromptSubmit` | "When you submit a prompt, before Claude processes it" | no matcher support | https://code.claude.com/docs/en/hooks |
| `UserPromptExpansion` | "When a user-typed command expands into a prompt, before it reaches Claude. Can block the expansion" | command name ("your skill or command names") | https://code.claude.com/docs/en/hooks |
| `PreToolUse` | "Before a tool call executes. Can block it" | tool name (`tool_name`) | https://code.claude.com/docs/en/hooks |
| `PermissionRequest` | "When a tool call needs a permission decision" | tool name | https://code.claude.com/docs/en/hooks |
| `PermissionDenied` | "When auto mode denies a tool call, including denials without a classifier verdict" | tool name | https://code.claude.com/docs/en/hooks |
| `PostToolUse` | "After a tool call succeeds" | tool name | https://code.claude.com/docs/en/hooks |
| `PostToolUseFailure` | "After a tool call fails" | tool name | https://code.claude.com/docs/en/hooks |
| `PostToolBatch` | "After a full batch of parallel tool calls resolves, before the next model call" | no matcher support | https://code.claude.com/docs/en/hooks |
| `Notification` | "When Claude Code sends a notification" | notification type: `permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_dialog`, `elicitation_url_dialog`, `elicitation_complete`, `elicitation_response`, `agent_needs_input`, `agent_completed`, `quota_auto_resume_fired`, `quota_auto_resume_stale`, `quota_auto_resume_disabled` | https://code.claude.com/docs/en/hooks |
| `MessageDisplay` | "While assistant message text is displayed" | no matcher support | https://code.claude.com/docs/en/hooks |
| `SubagentStart` | "When a subagent is spawned" | agent type: `general-purpose`, `Explore`, `Plan`, custom agent names, plugin-scoped e.g. `^my-plugin:reviewer$` | https://code.claude.com/docs/en/hooks |
| `SubagentStop` | "When a subagent finishes" | agent type (same values as `SubagentStart`) | https://code.claude.com/docs/en/hooks |
| `TaskCreated` | "When a task is being created via `TaskCreate`" | no matcher support | https://code.claude.com/docs/en/hooks |
| `TaskCompleted` | "When a task is being marked as completed" | no matcher support | https://code.claude.com/docs/en/hooks |
| `Stop` | "When Claude finishes responding" | no matcher support | https://code.claude.com/docs/en/hooks |
| `StopFailure` | "When the turn ends due to an API error" | error type: `rate_limit`, `overloaded`, `authentication_failed`, `oauth_org_not_allowed`, `account_on_hold`, `billing_error`, `invalid_request`, `model_not_found`, `server_error`, `max_output_tokens`, `unknown` | https://code.claude.com/docs/en/hooks |
| `TeammateIdle` | "When an agent team teammate is about to go idle" | no matcher support | https://code.claude.com/docs/en/hooks |
| `InstructionsLoaded` | "When a CLAUDE.md or `.claude/rules/*.md` file is loaded into context" | load reason: `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact` | https://code.claude.com/docs/en/hooks |
| `ConfigChange` | "When a configuration file changes during a session" | configuration source: `user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills` | https://code.claude.com/docs/en/hooks |
| `CwdChanged` | "When the working directory changes" | no matcher support | https://code.claude.com/docs/en/hooks |
| `DirectoryAdded` | "When a working directory is added mid-session via `/add-dir` or the SDK `register_repo_root` control request" | how added: `slash_command`, `register_repo_root` | https://code.claude.com/docs/en/hooks |
| `FileChanged` | "When a watched file changes on disk" | literal filenames to watch, e.g. `.envrc\|.env` | https://code.claude.com/docs/en/hooks |
| `WorktreeCreate` | "When a worktree is being created via `--worktree`, `isolation: \"worktree\"`, or for a background session" | no matcher support | https://code.claude.com/docs/en/hooks |
| `WorktreeRemove` | "When a worktree is being removed at session exit, when a subagent finishes, or when you delete a background session" | no matcher support | https://code.claude.com/docs/en/hooks |
| `PreCompact` | "Before context compaction" | what triggered compaction: `manual`, `auto` | https://code.claude.com/docs/en/hooks |
| `PostCompact` | "After context compaction completes" | `manual`, `auto` | https://code.claude.com/docs/en/hooks |
| `PreModelSwitch` | "Before Claude Code applies a model switch that you or a client requested. Can block the switch" | canonical model name, e.g. `claude-opus-5`, `claude-opus-4-6\|claude-opus-5`, `.*opus.*` | https://code.claude.com/docs/en/hooks |
| `PostModelSwitch` | "After the session's model changes, including changes Claude Code makes on its own" | canonical model name (same as `PreModelSwitch`) | https://code.claude.com/docs/en/hooks |
| `Elicitation` | "When an MCP server requests user input during a tool call" | MCP server name | https://code.claude.com/docs/en/hooks |
| `ElicitationResult` | "After a user responds to an MCP elicitation, before the response is sent back to the server" | MCP server name | https://code.claude.com/docs/en/hooks |
| `SessionEnd` | "When a session terminates" | why ended: `clear`, `resume`, `logout`, `prompt_input_exit`, `other` | https://code.claude.com/docs/en/hooks |

PR reproduces the same event table for plugin hooks ("Plugin hooks respond to the same lifecycle events as user-defined hooks") (https://code.claude.com/docs/en/plugins-reference).

Matcher evaluation (HK): `"*"`, `""`, or omitted = match all; only letters, digits, `_`, `-`, spaces, `,`, `|` = exact string or `|`/`,`-separated list of exact strings (comma separators v2.1.191+; hyphens in exact set v2.1.195+); any other character = JavaScript regular expression, unanchored (`Edit.*` matches `NotebookEdit`; use `^Edit$`). `FileChanged` and `StopFailure` use a narrower exact set (letters, digits, `_`, `|`). MCP examples: `mcp__memory__.*`, `mcp__.*`. Case sensitivity: UNVERIFIED (https://code.claude.com/docs/en/hooks — not stated).

### Handler schema
| Field | Type | Required | Allowed values | Notes and source |
| --- | --- | --- | --- | --- |
| `matcher` (group object) | string | No | see matcher evaluation above | sibling of `hooks` array inside each `"<EventName>": [...]` entry (https://code.claude.com/docs/en/hooks) |
| `hooks` (group object) | array of handlers | Yes | — | handler objects below (HK) |
| `type` | string | Yes | `"command"`, `"http"`, `"mcp_tool"`, `"prompt"`, `"agent"` | "There are five types" (HK); PR lists the same five |
| `if` | string | No | permission rule syntax, e.g. `"Bash(git *)"`, `"Edit(*.ts)"` | "Only evaluated on tool events: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, and `PermissionDenied`. On other events, a hook with `if` set never runs." Best-effort for Bash (subcommands, `$()`, backticks checked; unexpandable `$VAR` runs the hook) (HK) |
| `timeout` | number (seconds) | No | — | Defaults: 600 for `command`, `http`, `mcp_tool`; 30 for `prompt`; 60 for `agent`; lowered to 30 on `UserPromptSubmit`, `PreModelSwitch`, `PostModelSwitch`, to 10 on `MessageDisplay`; `SessionEnd` hooks share a 1.5-second budget raised to match a longer per-hook `timeout` up to 60 s; not enforced on `async: true` command hooks (HK) |
| `statusMessage` | string | No | — | "Custom spinner message displayed while the hook runs" (HK) |
| `once` | boolean | No | `true` | removed after first successful run; skill frontmatter only (HK) |
| `command` | string | Yes for `command` | — | "Shell command to execute. With `args`, the executable to spawn directly" (HK) |
| `args` | array of strings | No (`command`) | — | present = exec form, no shell; absent = shell form (HK) |
| `async` | boolean | No (`command`) | `true` | "runs in the background without blocking" (HK) |
| `asyncRewake` | boolean | No (`command`) | `true` | background, "wakes Claude on exit code 2" (HK) |
| `shell` | string | No (`command`) | `"bash"`, `"powershell"` | default `"bash"`, or `"powershell"` on Windows when Git Bash isn't installed; ignored when `args` is set (HK) |
| `url` | string | Yes for `http` | — | "URL to send the POST request to" (HK) |
| `headers` | object | No (`http`) | values may use `$VAR_NAME` / `${VAR_NAME}` | only variables in `allowedEnvVars` resolved (HK) |
| `allowedEnvVars` | array of strings | No (`http`) | — | "Required for any env var interpolation to work" (HK) |
| `server` | string | Yes for `mcp_tool` | configured server name or `plugin:<plugin-name>:<server-name>` | "The server must already be connected" (HK) |
| `tool` | string | Yes for `mcp_tool` | — | tool name on that server (HK) |
| `input` | object | No (`mcp_tool`) | string values support `${path}` from hook input, e.g. `"${tool_input.file_path}"` | (HK) |
| `prompt` | string | Yes for `prompt` and `agent` | `$ARGUMENTS` placeholder for hook input JSON; escape as `\$` | "If `$ARGUMENTS` is not present, input JSON is appended to the prompt" (HK) |
| `model` | string | No (`prompt`, `agent`) | model id | "Defaults to a fast model" (HK) |
| `description` (plugin `hooks.json` top level) | string | No | — | HK: optional top-level field; PR: not mentioned (https://code.claude.com/docs/en/hooks, https://code.claude.com/docs/en/plugins-reference) |

### Environment variables and path conventions
- Path placeholders usable in all hook types: `${CLAUDE_PROJECT_DIR}` ("the project root where the session started"; also set for stdio MCP servers and plugin LSP servers), `${CLAUDE_PLUGIN_ROOT}` (plugin installation directory), `${CLAUDE_PLUGIN_DATA}` (plugin persistent data directory) (HK, PR).
- Exported to command-hook processes: `CLAUDE_PROJECT_DIR`, `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA` (HK).
- `$CLAUDE_CODE_REMOTE` is `"true"` in remote web environments, not set locally; `$CLAUDE_CODE_BRIDGE_SESSION_ID` set for Remote Control (v2.1.199+) (HK).
- `CLAUDE_ENV_FILE`: available to `SessionStart` hooks; append `export` lines to persist env vars for later Bash commands (HK).
- `$CLAUDE_PLUGIN_OPTION_<KEY>`: plugin user-config values for shell-form hooks; a shell-form plugin hook whose `command` references `${user_config.*}` fails with an error (HK). `${user_config.KEY}` substitution documented for MCP/LSP configs and hook commands (PR).
- Worktrees: `${CLAUDE_PROJECT_DIR}` "stays put" at the original project root when Claude enters a worktree (HK).
- Quoting: exec form with `args` passes each path as one argument; shell form should wrap variables in double quotes, e.g. `"\"${CLAUDE_PLUGIN_ROOT}\"/scripts/format-code.sh"` (PR).
- Plugin persistent data dir path `~/.claude/plugins/data/{id}/` (PR).

### Limits and exit-code semantics
- Exit 0: success; stdout parsed as JSON only if it starts with `{` and ends with `}` (ignoring whitespace); otherwise plain text. Plain-text stdout is added as context only on `UserPromptSubmit`, `UserPromptExpansion`, `SessionStart`, `PostModelSwitch`; elsewhere it goes to the debug log. Stderr on exit 0 goes to debug log only (HK).
- Exit 2: "blocking error"; blocks "whether or not you print JSON: even a JSON `permissionDecision` of `\"allow\"` can't override it". Per-event table (Can block? = Yes): `PreToolUse`, `UserPromptSubmit`, `UserPromptExpansion`, `Stop`, `SubagentStop`, `TeammateIdle`, `TaskCreated`, `TaskCompleted`, `ConfigChange` (except `policy_settings`), `PostToolBatch`, `PreCompact`, `PreModelSwitch`, `Elicitation`, `ElicitationResult`, `WorktreeCreate` ("Any non-zero exit code causes worktree creation to fail"). Not blocking: `PermissionRequest` (use `decision` object), `StopFailure` (only `terminalSequence` honoured), `PostToolUse` and `PostToolUseFailure` (stderr shown to Claude), `PermissionDenied`, `Notification`, `SubagentStart`, `SessionStart`, `Setup`, `SessionEnd`, `CwdChanged`, `DirectoryAdded`, `FileChanged`, `PostCompact`, `PostModelSwitch`, `WorktreeRemove`, `InstructionsLoaded`, `MessageDisplay` (HK).
- Other non-zero codes: non-blocking error; the action proceeds; the transcript shows a `<hook name> hook error` notice (HK).
- Timed-out `command`/`http`/`mcp_tool` hook "doesn't block the tool call"; an Agent SDK callback hook that exceeds its timeout blocks it (HK).
- Common JSON output fields (HK table): `continue` (default `true`; `false` stops processing, "Takes precedence over any event-specific decision fields"), `stopReason` (shown to user when `continue` is `false`), `suppressOutput` (default `false`; "Has no effect: Claude Code accepts the field but doesn't act on it"), `systemMessage` ("Warning message shown to the user"), `terminalSequence` (OSC `0`/`1`/`2`/`9`/`99`/`777` and BEL only).
- Decision control table (HK): top-level `decision: "block"` + `reason` for `UserPromptSubmit`, `UserPromptExpansion`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `Stop`, `SubagentStop`, `ConfigChange`, `PreCompact` (Stop/SubagentStop also accept `hookSpecificOutput.additionalContext`); `TeammateIdle`, `TaskCompleted`: exit code or `continue: false`; `TaskCreated`: exit code or `decision: "block"`; `PreToolUse`: `hookSpecificOutput.permissionDecision` (`allow`/`deny`/`ask`/`defer`) + `permissionDecisionReason`, `updatedInput`; `PreModelSwitch`: `permissionDecision` (`allow`/`deny`/`ask`) or `decision: "block"`; `PermissionRequest`: `hookSpecificOutput.decision.behavior` (`allow`/`deny`) with `updatedInput`; `PermissionDenied`: `retry: true`; `WorktreeCreate`: path on stdout or `hookSpecificOutput.worktreePath`; `Elicitation`/`ElicitationResult`: `action` (`accept`/`decline`/`cancel`), `content`; `MessageDisplay`: `displayContent`; `SessionStart`, `SubagentStart`, `PostModelSwitch`: `hookSpecificOutput.additionalContext` (SessionStart also `initialUserMessage`, `watchPaths`, `sessionTitle`); `PostToolUse`: `updatedToolOutput` replaces the tool result; no decision control: `Setup`, `WorktreeRemove`, `Notification`, `SessionEnd`, `PostCompact`, `InstructionsLoaded`, `StopFailure`, `CwdChanged`, `DirectoryAdded`, `FileChanged`.
- Deprecated JSON form: "PreToolUse previously used top-level `decision` and `reason` fields, but these are deprecated for this event. Use `hookSpecificOutput.permissionDecision` and `hookSpecificOutput.permissionDecisionReason` instead. The deprecated values `\"approve\"` and `\"block\"` map to `\"allow\"` and `\"deny\"` respectively." `allowedPrompts` (ExitPlanMode input) deprecated, ignored since v2.1.205; `team_name` input field deprecated (HK).
- Execution: "All matching hooks run in parallel." Async: "Hook output is delivered on the next conversation turn ... Exception: an `asyncRewake` hook that exits with code 2 wakes Claude immediately"; "no deduplication across multiple firings of the same async hook" (HK).
- Common input fields on stdin: `session_id`, `prompt_id` (v2.1.196+), `transcript_path`, `cwd`, `permission_mode` (`"default"`, `"plan"`, `"acceptEdits"`, `"auto"`, `"dontAsk"`, `"bypassPermissions"`), `effort` (object with `level`: `"low"`, `"medium"`, `"high"`, `"xhigh"`, `"max"`), `hook_event_name`; subagent fields `agent_id`, `agent_type`; tool events `tool_name`, `tool_input`, `tool_use_id` (HK).

## Claude Code plugins (`.claude-plugin/plugin.json`, `marketplace.json`)
Sources: https://code.claude.com/docs/en/plugins-reference, https://code.claude.com/docs/en/hooks (fetched 2026-09-04)

### Directory layout
- Rule (PR, verbatim): "The `.claude-plugin/` directory contains the `plugin.json` file. All other directories (commands/, agents/, skills/, workflows/, output-styles/, themes/, monitors/, hooks/) must be at the plugin root, not inside `.claude-plugin/`." Also: "Only `plugin.json` belongs in `.claude-plugin/`."
- Manifest optional: "The manifest is optional. If omitted, Claude Code auto-discovers components in default locations and derives the plugin name from the directory name." (PR)
- Default locations table (PR): Manifest `.claude-plugin/plugin.json` (optional); Skills `skills/` (`<name>/SKILL.md`); Commands `commands/` ("Skills as flat Markdown files. Use `skills/` for new plugins"); Agents `agents/`; Workflows `workflows/`; Output styles `output-styles/`; Themes `themes/`; Hooks `hooks/hooks.json`; MCP servers `.mcp.json`; LSP servers `.lsp.json`; Monitors `monitors/monitors.json`; Executables `bin/`; Settings `settings.json` ("Only the `agent` and `subagentStatusLine` keys are supported"). Skills may also be "a single `SKILL.md` file at the plugin root".
- Skill invocation name comes from `SKILL.md` frontmatter `name`, falling back to the directory basename (PR).
- Cache: marketplace plugins are copied to `~/.claude/plugins/cache` (except `command` sources in link mode); previous versions orphaned and swept "roughly 14 days later" (PR). Synced plugins load from `~/.claude/plugins/synced/` as `<name>@synced` (v2.1.239+); skills-dir plugins load as `<name>@skills-dir` (PR).
- Boolean frontmatter in plugin skills/commands accepts `yes`, `no`, `on`, `off`, `1`, `0` in any case as well as `true`/`false` (v2.1.218+) (PR).
- Node deps auto-install: `bun.lock`/`bun.lockb` → `bun install --frozen-lockfile --ignore-scripts`; `npm-shrinkwrap.json`/`package-lock.json` → `npm ci --ignore-scripts`; 60-second maximum (PR).

### plugin.json keys
| Key | Type | Required | Allowed values / format | Notes and source |
| --- | --- | --- | --- | --- |
| `name` | string | Yes | "kebab-case, with no spaces, control characters, or bidirectional-formatting characters" | if a marketplace entry lists a different name, "the marketplace entry name is what `enabledPlugins` keys and `/plugin` use" (https://code.claude.com/docs/en/plugins-reference) |
| `$schema` | string | No | JSON Schema URL, e.g. `https://json.schemastore.org/claude-code-plugin-manifest.json` | "Claude Code ignores this field at load time" (PR) |
| `displayName` | string | No | may contain spaces and any casing | falls back to `name`; not used for namespacing (PR) |
| `version` | string | No | "Semantic version" | "If also set in the marketplace entry, `plugin.json` wins"; version resolution: plugin.json `version` → marketplace entry `version` → git commit SHA (for `github`, `url`, `git-subdir`, relative-path sources) (PR) |
| `description` | string | No | free text | (PR) |
| `author` | object | No | sub-keys shown in example: `name`, `email`, `url` | table says only "Author information" (PR) |
| `homepage` | string | No | URL | (PR) |
| `repository` | string | No | URL | (PR) |
| `license` | string | No | identifier e.g. `"MIT"` | (PR) |
| `keywords` | array | No | strings | "Discovery tags" (PR) |
| `metadata` | object | No | free-form | "Claude Code doesn't read it"; non-object value ignored and warned by `claude plugin validate` (PR) |
| `defaultEnabled` | boolean | No | default `true` | (PR) |
| `skills` | string \| array | No | paths starting `./`, or `"."` (v2.1.221+) | "Adds to the default `skills/` scan" (PR) |
| `commands` | string \| array | No | `./` paths to flat `.md` files or dirs | "replaces default `commands/`" (PR) |
| `agents` | string \| array | No | `./` paths | "replaces default `agents/`" (PR) |
| `workflows` | string \| array | No | `./` paths | replaces default `workflows/` (PR) |
| `hooks` | string \| array \| object | No | hook config paths or inline config | own merge rules; "merge with your user and project hooks" (PR, HK) |
| `mcpServers` | string \| array \| object | No | MCP config paths or inline config | own merge rules (PR) |
| `outputStyles` | string \| array | No | `./` paths | replaces default `output-styles/` (PR) |
| `lspServers` | string \| array \| object | No | LSP configs, e.g. `"./.lsp.json"` | own merge rules (PR) |
| `experimental.themes` | string \| array | No | `./` paths | replaces default `themes/` (PR) |
| `experimental.monitors` | string \| array | No | `./` paths | replaces default `monitors/` (PR) |
| `userConfig` | object | No | per-option: `type` (Yes: `string`, `number`, `boolean`, `directory`, `file`), `title` (Yes), `description` (Yes), `sensitive`, `required`, `default`, `multiple` (string type), `min`/`max` (number type) | values substituted as `${user_config.KEY}` in MCP/LSP configs and hook commands; non-sensitive also in skill/agent content (PR) |
| `channels` | array | No | objects with `server` and `userConfig` | (PR) |
| `dependencies` | array | No | strings or `{ "name", "version" }` with semver constraints | e.g. `{ "name": "secrets-vault", "version": "~2.1.0" }` (PR) |

Path constraints: "All paths must be relative to the plugin root and start with `./`, except that the `skills` field also accepts `\".\"`"; `"."` and `"./"` both denote the plugin root (PR).

### marketplace.json keys
| Key | Type | Required | Allowed values / format | Notes and source |
| --- | --- | --- | --- | --- |
| (whole schema) | — | — | — | UNVERIFIED (https://code.claude.com/docs/en/plugins-reference — "no marketplace.json schema on this page"; it links to https://code.claude.com/docs/en/plugin-marketplaces, which was outside the allowed page set) |
| `plugins[].name` | string | — | — | Only fact on PR: the marketplace entry name, when it differs from plugin.json `name`, is what `enabledPlugins` keys and `/plugin` use (https://code.claude.com/docs/en/plugins-reference) |
| `plugins[].version` | string | — | — | Second in version resolution after plugin.json `version` (PR) |
| `plugins[].source` | string \| object | — | source types named on PR: `github`, `url`, `git-subdir`, relative path, `command` | only named in version-management and error text ("the `source` path in marketplace.json points to a non-existent directory"); shapes of `repo`/`url`/`ref`/`sha`/`path` for Claude Code: UNVERIFIED (https://code.claude.com/docs/en/plugins-reference) |
| `name`, `owner`, `metadata`, `plugins[].description`, `plugins[].strict`, etc. | — | — | — | UNVERIFIED (https://code.claude.com/docs/en/plugins-reference) |

## Copilot CLI plugins
Sources: https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference (fetched 2026-09-04)

### Layout and manifest
- Definition: "All plugins consist of a plugin directory containing, at minimum, a manifest file named `plugin.json` located at the root of the plugin directory." (CP)
- Manifest lookup: "`.plugin/plugin.json`, `plugin.json`, `.github/plugin/plugin.json`, or `.claude-plugin/plugin.json` (checked in this order)" (CP).
- File locations table (CP): Agents `agents/` (default, overridable); Skills `skills/` (default, overridable); Hooks configuration `hooks.json` or `hooks/hooks.json`; MCP configuration `.mcp.json`, `.github/mcp.json`; LSP configuration `lsp.json` or `.github/lsp.json` (also `lsp-config/servers.json` in the LSP section); Plugin data `${COPILOT_PLUGIN_DATA}` "(also available as `${CLAUDE_PLUGIN_DATA}`)"; Installed plugins `~/.copilot/installed-plugins/MARKETPLACE/PLUGIN-NAME` and `~/.copilot/installed-plugins/_direct/SOURCE-ID/`; Marketplace cache `~/.cache/copilot/marketplaces/` (Linux), `~/Library/Caches/copilot/marketplaces/` (macOS), overridable with `COPILOT_CACHE_HOME`.
- `${PLUGIN_ROOT}`: "Use `${PLUGIN_ROOT}` to reference paths within the plugin directory" (LSP config section; `cwd` "Supports ${PLUGIN_ROOT}") (CP).
- plugin.json fields (CP): required `name` (string; "Kebab-case plugin name (letters, numbers, hyphens only). Max 64 chars"; dots allowed for Open Plugin Spec plugins, e.g. `acme.tools`). Optional metadata: `$schema` (string; "Set to the canonical Agent Plugins (Open Plugin Spec) v1.0.0 schema URL to opt into spec semantics"), `description` (string; "Max 1024 chars"), `version` (string; "Semantic version (e.g., `1.0.0`)"), `author` (object; "`name` (required), `email` (optional), `url` (optional)"), `homepage`, `repository`, `license` (strings), `keywords` (string[]), `category` (string), `tags` (string[]). Component paths (all optional): `agents` (string | string[]; default `agents/`; "Path(s) to agent directories (`.agent.md` files)"), `skills` (string | string[]; default `skills/`; "Path(s) to skill directories (`SKILL.md` files)"), `commands` (string | string[]; no default; "Path(s) to command directories"), `hooks` (string | object; "Path to a hooks configuration file, or an inline hooks object"), `extensions` (string | string[] | object; "Use `{ paths: [...], exclusive: true }` to suppress built-in extensions"), `mcpServers` (string | object; e.g. `.mcp.json` or inline), `lspServers` (string | object). Example uses `"hooks": "hooks.json"` and `"skills": ["skills/", "extra-skills/"]` (paths without `./`).
- Open Plugin Spec: "Declaring the canonical `$schema` in `plugin.json` opts a plugin into the Agent Plugins (Open Plugin Spec) v1.0.0 format, additively on top of standard plugin loading" (CP). Schema URL string: UNVERIFIED (https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference — not printed in the extracted text).
- Discovery / dedupe (CP): "Agents and skills use first-found-wins precedence." "If you have a project-level custom agent or skill with the same name or ID as one in a plugin you install, the agent or skill in the plugin is silently ignored. The plugin cannot override project-level or personal configurations. Custom agents are deduplicated using their ID, which is derived from its file name (for example, if the file is named `reviewer.agent.md`, the agent ID is `reviewer`). Skills are deduplicated by their `name` field inside the `SKILL.md` file." "MCP servers use last-wins precedence." "Built-in tools and agents are always present and cannot be overridden by user-defined components."
- Precedence diagram order (CP): custom agents 1 `~/.copilot/agents/`, 2 `<project>/.github/agents/`, 3 `<parents>/.github/agents/`, 4 `<project>/.claude/agents/`, 5 `<parents>/.claude/agents/`, 6 `PLUGIN: agents/ dirs` (by install order), 7 remote org/enterprise agents. Skills 1 `<project>/.github/skills/`, 2 `<project>/.agents/skills/`, 3 `<project>/.claude/skills/`, 4 `<parents>/.github/skills/` etc., 5 `~/.copilot/skills/`, 6 `~/.agents/skills/`, 7 `PLUGIN: skills/ dirs`, 8 `COPILOT_SKILLS_DIRS` env + config; "then commands (.claude/commands/), skills override commands". MCP 1 `~/.copilot/mcp-config.json` (lowest), 2 plugin MCP configs, 3 `--additional-mcp-config` (highest).
- marketplace.json (CP): saved to `.github/plugin/` of a repo or a local path; lookup order "`marketplace.json`, `.plugin/marketplace.json`, `.github/plugin/marketplace.json`, or `.claude-plugin/marketplace.json` (checked in this order)". Top-level: `name` (string, required; kebab-case, max 64 chars), `owner` (object, required; `{ name, email? }`), `plugins` (array, required), `metadata` (object, optional; `{ description?, version?, pluginRoot? }`). Plugin entry: `name` (required), `source` (string | object, required; "relative path, GitHub, or URL"), `description` (max 1024 chars), `version`, `author` (`{ name, email?, url? }`), `homepage`, `repository`, `license`, `keywords`, `category`, `tags`, `commands`, `agents`, `skills`, `hooks` (string | object), `mcpServers` (string | object; "Used when the plugin source does not ship its own MCP configuration"), `lspServers`, `strict` (boolean; "When `true` (the default), plugins must conform to the full schema and validation rules. When `false`, relaxed validation is used"). Source object: `{ "source": "github", "repo": "owner/repo", "ref": "v1.0.0", "path": "plugins/my-plugin" }`; "Both the `github` and `url` source types accept an optional `sha` field ... `sha` must be a full 40-character commit SHA". Relative path: "It is not necessary to use `./` at the start of the path". `pluginRoot` meaning: UNVERIFIED (https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference — listed only as `pluginRoot?`).
- Hooks inside a Copilot plugin: file `hooks.json` or `hooks/hooks.json`, or inline object; hook JSON format and supported event names: UNVERIFIED (https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference — not documented on this page).
- CLI: `copilot plugin install SPECIFICATION` (forms `plugin@marketplace`, `OWNER/REPO`, `OWNER/REPO:PATH/TO/PLUGIN`, Git URL, `./my-plugin` or `/abs/path`), `uninstall NAME`, `list`, `update NAME` / `--all`, `enable NAME`, `disable NAME`, `marketplace add|list|browse|update|remove`; `copilot plugin` and `copilot plugins` interchangeable (CP).
- Policy: `enabledPlugins`, `extraKnownMarketplaces` managed values win; `autoUpdate` setting (`false`) or `COPILOT_AUTO_UPDATE=false` disables first-party auto-update; `--config-dir` deprecated in favour of `COPILOT_HOME` (CP).

### Unresolved items from this group
- Claude Code `marketplace.json` full schema (`name`, `owner`, `metadata`, `plugins[]` entry fields, `source` object forms): not on https://code.claude.com/docs/en/plugins-reference; page defers to https://code.claude.com/docs/en/plugin-marketplaces (not in allowed page set).
- YAML-list form for subagent `tools`/`disallowedTools`: no example on https://code.claude.com/docs/en/sub-agents (only comma-separated strings; JSON array in `--agents`).
- `Bash(git:*)`/`Edit(*.ts)`-style permission-rule patterns inside subagent `tools`/`disallowedTools`: none found on https://code.claude.com/docs/en/sub-agents.
- Default value of `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` and same-directory duplicate-`name` behaviour: not confirmed in raw text of https://code.claude.com/docs/en/sub-agents.
- Matcher case sensitivity: not stated on https://code.claude.com/docs/en/hooks.
- `CLAUDE_EFFORT` environment variable (claimed by a WebFetch summary): not present in the raw text of https://code.claude.com/docs/en/hooks; only the `effort` input field is documented.
- Subagent-frontmatter hook events: https://code.claude.com/docs/en/sub-agents lists `PreToolUse`, `PostToolUse`, `Stop`; https://code.claude.com/docs/en/hooks says "All hook events are supported" for skills and subagents — conflict recorded, not resolved.
- Plugin `hooks/hooks.json` top-level `description`: documented on https://code.claude.com/docs/en/hooks, absent from https://code.claude.com/docs/en/plugins-reference.
- Copilot plugin hooks JSON format and event names; Open Plugin Spec schema URL; `pluginRoot` semantics; `commands` default directory; config-file path for `enabledPlugins`/`autoUpdate`: not documented on https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference.
- Copilot page contains no statement about Claude Code plugin compatibility beyond accepting `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `${CLAUDE_PLUGIN_DATA}` (https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference).

## SKILL.md (agentskills.io specification)
Sources: https://agentskills.io/specification (fetched 2026-09-04)

### Directory contract
- "A skill is a directory containing, at minimum, a `SKILL.md` file" (https://agentskills.io/specification)
- Layout shown on the page (https://agentskills.io/specification):
  ```
  skill-name/
  ├── SKILL.md          # Required: metadata + instructions
  ├── scripts/          # Optional: executable code
  ├── references/       # Optional: documentation
  ├── assets/           # Optional: templates, resources
  └── ...               # Any additional files or directories
  ```
- `name` "Must match the parent directory name" (https://agentskills.io/specification, `name` field bullets)
- "The `SKILL.md` file must contain YAML frontmatter followed by Markdown content." (https://agentskills.io/specification)
- "A skill directory may contain any files and directories beyond the required `SKILL.md`. The conventions below are recommendations for organizing common types of content." (https://agentskills.io/specification)
- `scripts/`: "Contains executable code that agents can run. Scripts should: Be self-contained or clearly document dependencies; Include helpful error messages; Handle edge cases gracefully"; "Supported languages depend on the agent implementation. Common options include Python, Bash, and JavaScript." (https://agentskills.io/specification)
- `references/`: "Contains additional documentation that agents can read when needed" — examples `REFERENCE.md`, `FORMS.md`, "Domain-specific files (`finance.md`, `legal.md`, etc.)"; "Keep individual reference files focused. Agents load these on demand, so smaller files mean less use of context." (https://agentskills.io/specification)
- `assets/`: "Contains static resources: Templates (document templates, configuration templates); Images (diagrams, examples); Data files (lookup tables, schemas)" (https://agentskills.io/specification)
- Validation tool: `skills-ref validate ./my-skill` — "This checks that your `SKILL.md` frontmatter is valid and follows all naming conventions." (https://agentskills.io/specification)

### Frontmatter keys
The page's frontmatter table lists exactly six fields; no others are defined (https://agentskills.io/specification).

| Key | Type | Required | Allowed values / format / limits | Notes and source |
| --- | --- | --- | --- | --- |
| `name` | string | Yes | Table: "Max 64 characters. Lowercase letters, numbers, and hyphens only. Must not start or end with a hyphen." Field bullets: "Must be 1-64 characters"; "May only contain unicode lowercase alphanumeric characters (`a-z`, `0-9`) and hyphens (`-`)"; "Must not start or end with a hyphen (`-`)"; "Must not contain consecutive hyphens (`--`)"; "Must match the parent directory name" | No regex is printed on the page; rules are prose bullets only. Invalid examples given: `PDF-Processing` (uppercase), `-pdf` (leading hyphen), `pdf--processing` (consecutive hyphens). https://agentskills.io/specification |
| `description` | string | Yes | Table: "Max 1024 characters. Non-empty." Bullets: "Must be 1-1024 characters" | "Should describe both what the skill does and when to use it"; "Should include specific keywords that help agents identify relevant tasks". https://agentskills.io/specification |
| `license` | string | No | "License name or reference to a bundled license file." | "We recommend keeping it short (either the name of a license or the name of a bundled license file)"; example `license: Proprietary. LICENSE.txt has complete terms`. https://agentskills.io/specification |
| `compatibility` | string | No | Table: "Max 500 characters." Bullets: "Must be 1-500 characters if provided" | "Should only be included if your skill has specific environment requirements"; "Can indicate intended product, required system packages, network access needs, etc."; Note: "Most skills do not need the `compatibility` field." https://agentskills.io/specification |
| `metadata` | map (string keys → string values) | No | "Arbitrary key-value mapping for additional metadata (a map from string keys to string values)." | "Clients can use this to store additional properties not defined by the Agent Skills spec"; "We recommend making your key names reasonably unique to avoid accidental conflicts"; example keys `author`, `version: "1.0"`. https://agentskills.io/specification |
| `allowed-tools` | string (space-separated) | No | "Space-separated string of pre-approved tools the skill may use. (Experimental)"; bullets: "A space-separated string of tools that are pre-approved to run"; "Experimental. Support for this field may vary between agent implementations" | Documented form is a string, not a list. Example: `allowed-tools: Bash(git:*) Bash(jq:*) Read`. https://agentskills.io/specification |

### Body guidance and limits
- "The Markdown body after the frontmatter contains the skill instructions. There are no format restrictions." (https://agentskills.io/specification)
- Recommended sections: "Step-by-step instructions"; "Examples of inputs and outputs"; "Common edge cases" (https://agentskills.io/specification)
- "Note that the agent will load this entire file once it's decided to activate a skill. Consider splitting longer `SKILL.md` content into referenced files." (https://agentskills.io/specification)
- Progressive disclosure, verbatim (https://agentskills.io/specification): "1. **Metadata** (~100 tokens): The `name` and `description` fields are loaded at startup for all skills"; "2. **Instructions** (< 5000 tokens recommended): The full `SKILL.md` body is loaded when the skill is activated"; "3. **Resources** (as needed): Files (e.g. those in `scripts/`, `references/`, or `assets/`) are loaded only when required"
- Length: "Keep your main `SKILL.md` under 500 lines. Move detailed reference material to separate files." (https://agentskills.io/specification)
- File references: "When referencing other files in your skill, use relative paths from the skill root"; example `See [the reference guide](references/REFERENCE.md) for details.` and `scripts/extract.py`; "Keep file references one level deep from `SKILL.md`. Avoid deeply nested reference chains." (https://agentskills.io/specification)

## Copilot extensions (github.com cloud agent, VS Code, Copilot CLI, gh skill)
Sources: https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills ; https://code.visualstudio.com/docs/copilot/customization/agent-skills ; https://cli.github.com/manual/gh_skill ; https://cli.github.com/manual/gh_skill_publish ; https://cli.github.com/manual/gh_skill_install ; https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference (all fetched 2026-09-04)

### Discovery locations and precedence
Surface statement (github.com page): "Agent skills work with Copilot cloud agent, Copilot code review, the GitHub Copilot CLI, the GitHub Copilot app, and agent mode in Visual Studio Code." (https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills). Neither Copilot page attributes a specific directory to a specific surface.

- `.github/skills/` — project. github.com: "For project skills, specific to a single repository, create a `.github/skills`, `.claude/skills`, or `.agents/skills` directory in your repository." (https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills). VS Code: "Project skills, stored in your repository | `.github/skills/`, `.claude/skills/`, `.agents/skills/`" (https://code.visualstudio.com/docs/copilot/customization/agent-skills). VS Code "Use shared skills": "Copy the skill directory to your `.github/skills/` folder" (same URL).
- `.agents/skills/` — project. Listed on both pages above. `gh skill install`: "At project scope, several agents (including GitHub Copilot, Cursor, Codex, Gemini CLI, Antigravity, Amp, Cline, OpenCode, and Warp) share the `.agents/skills` directory." (https://cli.github.com/manual/gh_skill_install)
- `.claude/skills/` — project. Listed on both the github.com and VS Code pages above. `gh skill install --allow-hidden-dirs`: "Include skills in hidden directories (e.g. .claude/skills/, .agents/skills/)" (source-repo discovery, https://cli.github.com/manual/gh_skill_install).
- `~/.copilot/skills/` — personal. github.com: "For personal skills, shared across projects, create a `~/.copilot/skills` or `~/.agents/skills` directory in your local home directory." (https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills). VS Code: "Personal skills, stored in your user profile | `~/.copilot/skills/`, `~/.claude/skills/`, `~/.agents/skills/`" (https://code.visualstudio.com/docs/copilot/customization/agent-skills)
- `~/.agents/skills/` — personal. Listed on both pages above.
- `~/.claude/skills/` — personal. Listed by VS Code only (https://code.visualstudio.com/docs/copilot/customization/agent-skills); NOT listed on the github.com page (https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills). Pages disagree; both recorded.
- Additional VS Code locations: "You can configure additional file locations for project skills with the chat.agentSkillsLocations ... setting."; "In a monorepo, enable chat.useCustomizationsInParentRepositories ... to discover skills from the parent repository root." (https://code.visualstudio.com/docs/copilot/customization/agent-skills)
- VS Code extension-contributed skills: "Extensions can contribute skills using the `chatSkills` contribution point in their `package.json`. The path must point to a directory that contains a `SKILL.md` file, following the Agent Skills specification."; layout `extension-root/skills/my-skill/SKILL.md` with "Directory name must match the `name` field in SKILL.md"; `"contributes": { "chatSkills": [ { "path": "./skills/my-skill/SKILL.md" } ] }` (https://code.visualstudio.com/docs/copilot/customization/agent-skills)
- Plugin skills: VS Code: "Skills from installed plugins appear alongside your locally defined skills in the **Configure Skills** menu." (https://code.visualstudio.com/docs/copilot/customization/agent-skills). Copilot CLI: `copilot plugins list` — "Non-interactively inspect every plugin, MCP server, skill, instruction source, and language server discovered for the current working directory." with a `--kind skill` filter (https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)
- Copilot CLI reference page: names NO skill discovery directory; has no `/skills` slash command. Skill-related items present: `copilot skill` — "Manage agent skills from the command line (list, add, and remove skills)."; `copilot plugins enable|disable --skill` — "Target a skill."; `copilot plugins remove --skill` — "Remove a personal or project skill." and "With `--skill`, pass either a skill name or the path to a custom skill directory you added. A skill name deletes that skill's files; a custom directory path only unregisters the directory and leaves its files on disk. Only personal and project skills you added can be deleted—skills provided by a plugin or the builtin set can't be removed this way (disable them instead)."; `/env` — "Show loaded environment details (instructions, MCP servers, skills, agents, hooks, plugins, LSPs, extensions)."; `/chronicle <standup|tips|improve|reindex|skills create|skills review|skills status>` — "The `skills` subcommands draft, review, and track the status of repository skill proposals generated from observed usage." (https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)
- Precedence when the same skill name appears in more than one location: UNVERIFIED (https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills — no sentence containing "precedence", "priority", "override", "duplicate" or "same name"); UNVERIFIED (https://code.visualstudio.com/docs/copilot/customization/agent-skills — same words absent); UNVERIFIED (https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference — no directories named).

### Copilot-specific frontmatter keys or behaviours
| Key or behaviour | Documented by | Notes and source |
| --- | --- | --- |
| `name` | github.com; VS Code | github.com: "**name** (required): A unique identifier for the skill. This must be lowercase, using hyphens for spaces." — no length limit stated (https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills). VS Code: "Only lowercase letters, numbers, and hyphens are allowed (for example, `webapp-testing`). Do not use slashes, colons, dots, or namespace prefixes. Must match the parent directory name. Maximum 64 characters. Names with invalid characters cause the skill to silently fail to load." (https://code.visualstudio.com/docs/copilot/customization/agent-skills) |
| `description` | github.com; VS Code | github.com: "**description** (required): A description of what the skill does, and when Copilot should use it." — no length limit (same URL). VS Code: "Maximum 1024 characters." (https://code.visualstudio.com/docs/copilot/customization/agent-skills) |
| `license` | github.com only | "**license** (optional): A description of the license that applies to this skill." (https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills). The word "license" does not appear on the VS Code page (https://code.visualstudio.com/docs/copilot/customization/agent-skills). |
| `allowed-tools` | github.com only | "In your `SKILL.md` frontmatter, you can use the `allowed-tools` field to list the tools Copilot may use without asking for confirmation each time."; example line exactly `allowed-tools: shell` (a plain string) (https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills). Not mentioned on the VS Code page (https://code.visualstudio.com/docs/copilot/customization/agent-skills). `gh skill publish` validates "allowed-tools is a string, not an array" (https://cli.github.com/manual/gh_skill_publish). |
| `argument-hint` | VS Code only | "Hint text shown in the chat input field when the skill is invoked as a slash command. Helps users understand what additional information to provide (for example, `[test file] [options]`)." (https://code.visualstudio.com/docs/copilot/customization/agent-skills) |
| `user-invocable` | VS Code only | "Controls whether the skill appears as a slash command in the chat menu. Defaults to `true`. Set to `false` to hide the skill from the `/` menu while still allowing the agent to load it automatically." (https://code.visualstudio.com/docs/copilot/customization/agent-skills) |
| `disable-model-invocation` | VS Code only | "Controls whether the agent can automatically load the skill based on relevance. Defaults to `false`. Set to `true` to require manual invocation through the `/` slash command only." (https://code.visualstudio.com/docs/copilot/customization/agent-skills) |
| `context` | VS Code only | "Controls how the skill is loaded. Defaults to inline (the skill's instructions are added to the parent agent's context). Set to `fork` to run the skill in a dedicated subagent context."; "In a forked context, the skill executes in a dedicated subagent and only its final result is returned to the parent agent." No `agent` field documented → which subagent runs the fork is UNVERIFIED (https://code.visualstudio.com/docs/copilot/customization/agent-skills) |
| Visibility matrix | VS Code | "Default (both properties omitted) | Yes | Yes"; "`user-invocable: false` | No | Yes"; "`disable-model-invocation: true` | Yes | No"; "Both set | No | No | Disabled skills" (columns: Slash command / Auto-loaded by Copilot) (https://code.visualstudio.com/docs/copilot/customization/agent-skills) |
| Slash-command invocation | VS Code | "Skills are available as slash commands in chat, alongside prompt files. Type `/` in the chat input field to see a list of available skills and prompts, and select a skill to invoke it."; "You can add extra context after the slash command. For example, `/webapp-testing for the login page` or `/github-actions-debugging PR #42`." `$ARGUMENTS` not mentioned on the page. (https://code.visualstudio.com/docs/copilot/customization/agent-skills) |
| Automatic loading | github.com; VS Code | github.com: "Copilot will decide when to use your skills based on your prompt and the skill's description."; "When a skill is invoked, Copilot automatically discovers all of the files in the skill's directory and makes them available alongside the skill's instructions." (https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills). VS Code: "Skills load content progressively to keep your context efficient."; "Make sure to reference any additional files in your `SKILL.md` for them to be picked up by the agent."; relative-path example `[test script](./test-template.js)` (https://code.visualstudio.com/docs/copilot/customization/agent-skills) |
| Spec reference | github.com; VS Code | github.com: "validate your skills against the [Agent Skills specification](https://agentskills.io/specification)". VS Code: "Agent Skills is an open standard ([agentskills.io](https://agentskills.io)) that works across multiple AI agents." |
| `model`, `compatibility`, `metadata`, `hooks`, `paths`, `effort`, `agent` | neither Copilot page | UNVERIFIED (https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills ; https://code.visualstudio.com/docs/copilot/customization/agent-skills) |

Example SKILL.md frontmatter on github.com page (https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills):
```
name: github-actions-failure-debugging
description: Guide for debugging failing GitHub Actions workflows. Use this when asked to debug failing GitHub Actions workflows.
```

### `gh skill publish` / `gh skill install` constraints
- `gh skill`: "Install and manage agent skills from GitHub repositories."; subcommands `install`, `list`, `preview`, `publish`, `search`, `update`; alias `gh skills`; "Working with agent skills in the GitHub CLI is in preview and subject to change without notice." (https://cli.github.com/manual/gh_skill)
- `gh skill publish [<directory>] [flags]`: "Validate a local repository's skills against the Agent Skills specification and publish them by creating a GitHub release." Skill discovery conventions: `skills/*/SKILL.md`; `skills/{scope}/*/SKILL.md`; `*/SKILL.md` (root-level); `plugins/{scope}/skills/*/SKILL.md`. Validation checks (verbatim): "Skill names match the strict agentskills.io naming rules"; "Each skill name matches its directory name"; "Required frontmatter fields (name, description) are present"; "allowed-tools is a string, not an array"; "Install metadata (`metadata.github-*`) is stripped if present". Flags: `--dry-run` "Validate without publishing"; `--fix` "Auto-fix issues where possible without publishing (e.g. strip install metadata)"; `--tag <string>` "Version tag for the release (e.g. v1.0.0)". (https://cli.github.com/manual/gh_skill_publish)
- Exact regex enforced by gh for names: not restated on the gh pages ("strict agentskills.io naming rules" only) — UNVERIFIED (https://cli.github.com/manual/gh_skill_publish)
- `gh skill install <repository> [<skill[@version]>] [flags]`: "Install agent skills from a GitHub repository or local directory into your local environment. Skills are placed in a host-specific directory at either project scope (inside the current git repository) or user scope (in your home directory, available everywhere)."; "Skills are discovered automatically using the `skills/*/SKILL.md` convention defined by the Agent Skills specification, including when the `skills/` directory is nested under a prefix (e.g. `terraform/code-generation/skills/...`)."; version resolution: "1. Latest tagged release in the repository 2. Default branch HEAD"; repository format "OWNER/REPO format"; aliases `gh skills add`, `gh skill add`. (https://cli.github.com/manual/gh_skill_install)
- Install metadata: "Installed skills have source tracking metadata injected into their frontmatter. This metadata identifies the source repository and enables `gh skill update` to detect changes." Exact key names are NOT listed — UNVERIFIED (https://cli.github.com/manual/gh_skill_install); the only documented naming is the prefix `metadata.github-*` (https://cli.github.com/manual/gh_skill_publish). github.com page: "The `gh skill update` command uses this metadata to check for upstream changes." (https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
- `gh skill install` flags (https://cli.github.com/manual/gh_skill_install): `--agent <string>` "Target agent" (values listed on page include `github-copilot`, `claude-code`, `cursor`, … `zencoder`; full list not reproduced); `--all` "Install all skills without prompting for skill selection"; `--allow-hidden-dirs` "Include skills in hidden directories (e.g. .claude/skills/, .agents/skills/)"; `--dir <string>` "Install to a custom directory (overrides --agent and --scope)"; `-f, --force` "Overwrite existing skills without prompting"; `--from-local` "Treat the argument as a local directory path instead of a repository"; `--pin <string>` "Pin to a specific git tag or commit SHA"; `--scope <string>` (default "project") "Installation scope: {project|user}"; `--upstream` "Install from the upstream source when a re-published skill is detected"
- Destination directories: "At project scope, several agents (including GitHub Copilot, Cursor, Codex, Gemini CLI, Antigravity, Amp, Cline, OpenCode, and Warp) share the `.agents/skills` directory." (https://cli.github.com/manual/gh_skill_install). Per-agent mapping table (e.g. `claude-code` → `.claude/skills` / `~/.claude/skills`): UNVERIFIED (https://cli.github.com/manual/gh_skill_install — no such table). github.com: "Skills are automatically installed to the correct directory for your agent host. By default, skills are installed for Copilot at project scope."; "To install a skill for a specific agent host, use the `--agent` flag. To control the install scope, use `--scope`" (https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
- Example lines shown (https://cli.github.com/manual/gh_skill_install): `gh skill install`; `gh skill install github/awesome-copilot`; `gh skill install github/awesome-copilot | grep review`; `gh skill install github/awesome-copilot git-commit`; `gh skill install github/awesome-copilot --all`; `gh skill install github/awesome-copilot git-commit@v1.2.0`; `gh skill install github/awesome-copilot skills/monalisa/code-review`; `gh skill install monalisa/skills-repo packages/agent-skills/code-review`; `gh skill install ./my-skills-repo --from-local`; `gh skill install ./my-skills-repo git-commit --from-local`; `gh skill install github/awesome-copilot git-commit --agent claude-code --scope user` ("# Install for Claude Code at user scope"); `gh skill install github/awesome-copilot git-commit --pin v2.0.0`; `gh skill install owner/repo --allow-hidden-dirs`
- Commands shown on github.com page (https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills): `gh skill search TOPIC`; `gh skill preview OWNER/REPOSITORY SKILL`; `gh skill install OWNER/REPOSITORY`; `gh skill install OWNER/REPOSITORY SKILL`; `gh skill install github/awesome-copilot documentation-writer@v1.2.0`; `gh skill install github/awesome-copilot documentation-writer --pin v1.2.0`; `gh skill install github/awesome-copilot documentation-writer --agent claude-code --scope user`; `gh skill update`; `gh skill update SKILL`; `gh skill update --all`; `gh skill publish --dry-run`; `gh skill publish --fix`; `gh skill publish`

## Claude Code extensions
Sources: https://code.claude.com/docs/en/skills (fetched 2026-09-04)

### Discovery locations and precedence
Location table, verbatim (https://code.claude.com/docs/en/skills):

| Location | Path | Applies to |
| --- | --- | --- |
| Enterprise | See managed settings (example on page: `/etc/claude-code/.claude/skills/<skill-name>/` on Linux) | All users in your organization |
| Personal | `~/.claude/skills/<skill-name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<skill-name>/SKILL.md` | This project only |
| Plugin | `<plugin>/skills/<skill-name>/SKILL.md` | Where plugin is enabled |

Precedence ("When skills share the same name, Claude Code resolves the conflict by source", https://code.claude.com/docs/en/skills):
- "Across levels, enterprise overrides personal, and personal overrides project." Example: `deploy` in both `~/.claude/skills/` and `.claude/skills/` → "`/deploy` runs the personal one."
- "A skill at any of these levels also overrides a bundled skill with the same name, but not the bundled skill's aliases." Example: project `code-review` replaces bundled `/code-review`; alias `/review` never runs the custom skill.
- "Plugin skills use a `plugin-name:skill-name` namespace, so they can't conflict with other levels." Example: `my-plugin/skills/deploy/SKILL.md` → `/my-plugin:deploy`.
- "If you have files in `.claude/commands/`, those work the same way, but if a skill and a command share the same name, the skill takes precedence."
- "A skill or command from any of these sources overrides a skill synced from your claude.ai account with the same name."
- `.claude/commands/` relationship: "**Custom commands have been merged into skills.** A file at `.claude/commands/deploy.md` and a skill at `.claude/skills/deploy/SKILL.md` both create `/deploy` and work the same way."; "Files in `.claude/commands/` support the same frontmatter, except `name` and `paths`, which Claude Code ignores in a command file. You invoke a command file by its file name."
- Nested directories: "Skills also load from nested `.claude/skills/` directories below your working directory."; loaded "the first time Claude reads or edits a file inside that subdirectory"; name clash → "directory-qualified name, `apps/web:deploy`"; "Typing `/deploy` runs the project-root skill."
- Parent directories: "Project skills load from `.claude/skills/` in the directory where you start Claude Code and in every parent directory up to the repository root."
- Additional directories: `--add-dir` / `/add-dir` — "Claude Code loads `.claude/skills/` and `.claude/commands/` from each added directory automatically." `permissions.additionalDirectories` "grants file access only and doesn't load skills".
- Reserved folder: "The folder name `synced` is reserved in the enterprise, personal, and project skills locations, in any capitalization."; synced skills download to `~/.claude/skills/synced/` when `CLAUDE_CODE_SYNC_SKILLS` is set.
- Symlinks: "A `<skill-name>` entry in the enterprise, personal, or project locations can be a symlink to a directory elsewhere on disk."
- Skill folder as plugin: "Add a `.claude-plugin/plugin.json` to a skill folder and it loads as a plugin named `<name>@skills-dir`".
- Command name source table (https://code.claude.com/docs/en/skills): `.claude/skills/deploy-staging/SKILL.md` → `/deploy-staging` (directory name); `apps/web/.claude/skills/deploy/SKILL.md` → `/apps/web:deploy`; `.claude/commands/deploy.md` → `/deploy` (file name without extension); plugin `my-plugin/skills/review/SKILL.md` → `/my-plugin:review`, or `/my-plugin:fancy` with `name: fancy`; plugin root `my-plugin/SKILL.md` with `name: review` → `/my-plugin:review`.
- Frontmatter parsing: "Claude Code reads the frontmatter only when the opening `---` is the file's first line. Otherwise it treats the whole file, `---` markers included, as skill content."; "If the frontmatter YAML is malformed, Claude Code loads the skill body with empty metadata, so `/skill-name` still works". Validation: `claude plugin validate .claude/skills` (v2.1.233+).
- Live change detection: "When you add, edit, or remove a skill under `~/.claude/skills/`, the project `.claude/skills/`, or a `.claude/skills/` inside an `--add-dir` directory, Claude Code picks up the change within the current session".

### Claude-only frontmatter keys
"All fields are optional. Only `description` is recommended" (https://code.claude.com/docs/en/skills). "Boolean fields accept `yes`, `no`, `on`, `off`, `1`, and `0` in any letter case, in addition to `true` and `false`." Spec-vs-extension rule on the page: "Outside Claude Code, you can use only the fields in the Agent Skills spec" — `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`; for claude.ai uploads / Skills API / `package_skill.py`: "If you include any field the spec doesn't allow, packaging or upload fails with a hard error", message: `Unexpected key(s) in SKILL.md frontmatter: argument-hint. Allowed properties are: allowed-tools, compatibility, description, license, metadata, name`. The page does not state what Copilot does with these keys (cross-reference: VS Code documents `argument-hint`, `user-invocable`, `disable-model-invocation`, `context`; see Copilot section).

| Key | Type | Allowed values / format | Effect | Source |
| --- | --- | --- | --- | --- |
| `name` (spec key, Claude semantics differ) | string | any | "Display name shown in skill listings. Defaults to the directory name." In personal/project skills "`name` sets only the display label ... the command still comes from the directory name"; in plugin skills it "sets the last segment of the command". Not required in Claude Code. | https://code.claude.com/docs/en/skills |
| `description` (spec key) | string | "Recommended" | "If omitted, uses the first paragraph of markdown content. Put the key use case first: the combined `description` and `when_to_use` text is truncated at 1,536 characters in the skill listing" | https://code.claude.com/docs/en/skills |
| `when_to_use` | string | any | "Additional context for when Claude should invoke the skill, such as trigger phrases or example requests. Appended to `description` in the skill listing and counts toward the 1,536-character cap." | https://code.claude.com/docs/en/skills |
| `argument-hint` | string | e.g. `[issue-number]`, `[filename] [format]` | "Hint shown during autocomplete to indicate expected arguments." | https://code.claude.com/docs/en/skills |
| `arguments` | space-separated string or YAML list | e.g. `arguments: [issue, branch]` | "Named positional arguments for `$name` substitution in the skill content ... Names map to argument positions in order." | https://code.claude.com/docs/en/skills |
| `disable-model-invocation` | boolean | default `false` | "Set to `true` to prevent Claude from automatically loading this skill ... Also prevents the skill from being preloaded into subagents. As of v2.1.196, also prevents the skill from running when a scheduled task fires with the skill as its prompt." Effect table: You can invoke Yes / Claude No / "Description not in context, full skill loads when you invoke" | https://code.claude.com/docs/en/skills |
| `user-invocable` | boolean | default `true` | "Set to `false` when only Claude should invoke the skill: Claude Code hides it from the `/` menu and doesn't run it when you type `/name`." Effect table: You No / Claude Yes / "Description always in context, full skill loads when invoked" | https://code.claude.com/docs/en/skills |
| `allowed-tools` (spec key, wider form) | string or list | "Accepts a space- or comma-separated string, or a YAML list." Example `allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)` | "Tools Claude can use without asking permission during the turn that invokes this skill. The grant clears when you send your next message."; "It does not restrict which tools are available"; "Workspace trust doesn't gate this field."; `${CLAUDE_SKILL_DIR}`/`${CLAUDE_PROJECT_DIR}` (and plugin vars) are substituted inside Bash rules here. DISAGREEMENT: spec says "Space-separated string" (https://agentskills.io/specification); gh publish rejects arrays (https://cli.github.com/manual/gh_skill_publish). | https://code.claude.com/docs/en/skills |
| `disallowed-tools` | string or list | "Accepts a space- or comma-separated string, or a YAML list." | "Tools removed from Claude's available pool while this skill is active ... The restriction clears when you send your next message. Like deny rules, the field can't remove `EndConversation` while any other tool remains." | https://code.claude.com/docs/en/skills |
| `model` | string | "Accepts the same values as `/model`, or `inherit` to keep the active model." | "Model to use when this skill is active. The override applies for the rest of the current turn and is not saved to settings"; value excluded by `availableModels` "is not used"; "With `context: fork`, the value sets the forked subagent's model instead" | https://code.claude.com/docs/en/skills |
| `effort` | string | `low`, `medium`, `high`, `xhigh`, `max`; "available levels depend on the model" | "Effort level when this skill is active. Overrides the session effort level. Default: inherits from session." | https://code.claude.com/docs/en/skills |
| `context` | string | `fork` | "Set to `fork` to run in a forked subagent context."; "The skill content becomes the prompt that drives the subagent. It won't have access to your conversation history." | https://code.claude.com/docs/en/skills |
| `agent` | string | "built-in agents (`Explore`, `Plan`, `general-purpose`) or any custom subagent from `.claude/agents/`. If omitted, uses `general-purpose`." | "Which subagent type to use when `context: fork` is set."; "determines the execution environment (model, tools, and permissions)" | https://code.claude.com/docs/en/skills |
| `background` | boolean | default `true`; "Requires Claude Code v2.1.218 or later" | "Only applies with `context: fork`. Set to `false` to wait for the forked subagent's result in the turn that invoked the skill, instead of running it in the background." | https://code.claude.com/docs/en/skills |
| `hooks` | map (hooks config) | "See Hooks in skills and agents for the configuration format and the `once` option." | "Hooks that Claude Code registers when the skill is invoked and keeps running for the rest of the session." `once` is described only as an option inside `hooks`, defined on the hooks page — not a top-level skill key on this page: UNVERIFIED (https://code.claude.com/docs/en/skills) | https://code.claude.com/docs/en/skills |
| `paths` | comma-separated string or YAML list | glob patterns; "Uses the same format as path-specific rules" | "Glob patterns that limit when this skill is activated. When set, Claude loads the skill automatically only when working with files matching the patterns." Ignored in `.claude/commands/` files. | https://code.claude.com/docs/en/skills |
| `shell` | string | `bash` (default) or `powershell` | "Shell to use for `` !`command` `` and ` ```! ` blocks in this skill."; `powershell` needs the PowerShell tool enabled (`CLAUDE_CODE_USE_POWERSHELL_TOOL=1` on macOS/Linux/WSL and some cloud providers) | https://code.claude.com/docs/en/skills |
| `metadata` (spec key, wider type) | YAML map | "Free-form YAML map for your own key-value data ... Claude Code doesn't act on its contents, and drops a value that isn't a map. Don't reuse frontmatter field names such as `paths` as keys." DISAGREEMENT with spec's "map from string keys to string values" (https://agentskills.io/specification) | no runtime effect | https://code.claude.com/docs/en/skills |
| `license` (spec key) | string | any | "Part of the Agent Skills spec ... Claude Code accepts the field but doesn't act on it." | https://code.claude.com/docs/en/skills |
| `compatibility` (spec key) | string | "Accepts a string of up to 500 characters." | "Claude Code accepts the field but doesn't act on it." | https://code.claude.com/docs/en/skills |

Keys in the task list not found as top-level keys on the page: `once` (only as a `hooks` option) — UNVERIFIED (https://code.claude.com/docs/en/skills).

### Invocation and substitution
- Direct invocation: "you can invoke one directly with `/skill-name`"; "The directory name becomes the command you type" (https://code.claude.com/docs/en/skills)
- Stacking: "Typing `/write-tests /fix-issue 123` loads both skills and passes the trailing text `123` as `$ARGUMENTS` to each of them."; "Claude Code expands the first skill plus up to five more stacked after it." (https://code.claude.com/docs/en/skills)
- Substitution table, verbatim descriptions (https://code.claude.com/docs/en/skills): `$ARGUMENTS` "All arguments passed when invoking the skill. When no placeholder receives an argument, Claude Code appends them as `ARGUMENTS: <value>`."; `$ARGUMENTS[N]` "Access a specific argument by 0-based index, such as `$ARGUMENTS[0]` for the first argument."; `$N` "Shorthand for `$ARGUMENTS[N]`, such as `$0` for the first argument or `$1` for the second."; `$name` "Named argument declared in the `arguments` frontmatter list."; `${CLAUDE_SESSION_ID}` "The current session ID."; `${CLAUDE_EFFORT}` "The current effort level: `low`, `medium`, `high`, `xhigh`, or `max`."; `${CLAUDE_SKILL_DIR}` "The directory containing the skill's `SKILL.md` file. For plugin skills, this is the skill's subdirectory within the plugin, not the plugin root."; `${CLAUDE_PROJECT_DIR}` "The project root directory." (v2.1.196+); `${CLAUDE_PLUGIN_ROOT}` "The plugin's installation directory. Substituted only in plugin skills."; `${CLAUDE_PLUGIN_DATA}` "The plugin's persistent data directory ... Substituted only in plugin skills."
- "Claude Code substitutes `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PROJECT_DIR}` in two places: the skill's markdown content, and Bash rules in the `allowed-tools` frontmatter." Example `allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/render.sh *)` (https://code.claude.com/docs/en/skills)
- Argument rules: "Indexed arguments use shell-style quoting, so wrap multi-word values in quotes"; "An indexed placeholder with no corresponding argument, such as `$2` when only one argument was passed, stays in the content unchanged. A named placeholder ... with no matching argument expands to an empty string."; argument values containing `$1`/`$ARGUMENTS` are inserted literally; escape with a single backslash `\$1.00` (https://code.claude.com/docs/en/skills)
- Dynamic context injection: "The `` !`<command>` `` syntax runs shell commands before the skill content is sent to Claude. The command output replaces the placeholder"; inline form recognised only when `!` is at line start or after whitespace; multi-line form is a fenced block opened with ` ```! `; "Substitution runs once over the original file"; disable with `"disableSkillShellExecution": true` → `[shell command execution disabled by policy]`; "A failed command aborts the entire skill invocation" (`Shell command failed for pattern "..."`); "Injected commands never prompt for permission" — non-allow permission result aborts (`Shell command permission check failed for pattern "..."`); exit code 1 carveout for search/comparison commands (https://code.claude.com/docs/en/skills)
- Forked execution: `context: fork` + `agent` + `background` as in the table; comparison table: "Skill with `context: fork` | From agent type | SKILL.md content | CLAUDE.md, except when the agent is Explore or Plan"; "Subagent with `skills` field | Subagent's markdown body | Claude's delegation message | Preloaded skills + CLAUDE.md" (https://code.claude.com/docs/en/skills)
- Preloading into subagents: this page only states "Subagents with preloaded skills work differently: the full skill content is injected at startup." and that `disable-model-invocation: true` "prevents the skill from being preloaded into subagents"; the `skills:` field format is on the sub-agents page, not fetched — UNVERIFIED (https://code.claude.com/docs/en/skills)
- Skill content lifecycle: "the rendered `SKILL.md` content enters the conversation as a single message and stays there across later turns"; "an `allowed-tools` grant clears when you send your next message"; re-invocation with identical content adds "a short note that the skill is already loaded"; compaction "keeping the first 5,000 tokens of each. Re-attached skills share a combined budget of 25,000 tokens." (https://code.claude.com/docs/en/skills)
- Permission control: deny `Skill` tool; `Skill(name)` "for exact match", `Skill(name *)` "for prefix match with any arguments" (https://code.claude.com/docs/en/skills)
- `skillOverrides` setting values: `"on"`, `"name-only"`, `"user-invocable-only"`, `"off"`; "Plugin skills are not affected by `skillOverrides`." (https://code.claude.com/docs/en/skills)
- Listing budget: "The budget scales at 1% of the model's context window."; raise via `skillListingBudgetFraction` (e.g. `0.02`) or `SLASH_COMMAND_TOOL_CHAR_BUDGET` "to a fixed character count"; per-entry cap 1,536 characters, configurable with `skillListingMaxDescChars` (https://code.claude.com/docs/en/skills)
- Body/supporting files: "Keep `SKILL.md` under 500 lines. Move detailed reference material to separate files."; example tree uses flat `reference.md`, `examples.md`, `scripts/helper.py` (not the spec's `references/` folder); "Reference supporting files from `SKILL.md` so Claude knows what each file contains and when to load it" (https://code.claude.com/docs/en/skills)
- Settings mentioned: `disableBundledSkills` (disables all bundled skills except `/doctor`), `DISABLE_DOCTOR_COMMAND`, `CLAUDE_CODE_SYNC_SKILLS`, `CLAUDE_CODE_SYNC_SKILLS_WAIT_TIMEOUT_MS`, `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` (https://code.claude.com/docs/en/skills)

### Unresolved items from this group
- Copilot precedence when the same skill name exists in `.github/skills/`, `.agents/skills/`, `.claude/skills/` or user-level dirs — not stated (https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills ; https://code.visualstudio.com/docs/copilot/customization/agent-skills ; https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)
- Which Copilot surface reads which directory — the github.com page gives one surface list for all skills and no per-directory mapping (https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
- Whether `~/.claude/skills/` is read by github.com cloud agent / Copilot CLI — listed only by VS Code (https://code.visualstudio.com/docs/copilot/customization/agent-skills), absent from https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills and https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference
- Copilot CLI `/skills` slash command — not present on https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference (only `copilot skill`, `--skill`, `/env`, `/chronicle skills ...`)
- Copilot CLI skill discovery directories and config keys — not present on https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference
- Exact `metadata.github-*` key names written by `gh skill install` — not listed (https://cli.github.com/manual/gh_skill_install ; https://cli.github.com/manual/gh_skill_publish)
- Per-agent install directory mapping for `gh skill install --agent` (e.g. `claude-code` → `.claude/skills`) — no table on https://cli.github.com/manual/gh_skill_install; only `.agents/skills` shared-directory sentence
- Exact count and full list of `--agent` values — page lists many agents (`github-copilot` … `zencoder`); not reproduced in full (https://cli.github.com/manual/gh_skill_install)
- Regex for `name` — agentskills.io gives prose rules only, no regex (https://agentskills.io/specification); gh pages say only "strict agentskills.io naming rules" (https://cli.github.com/manual/gh_skill_publish)
- `name`/`description` length limits on github.com page — none stated (https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills); VS Code and spec both say 64 / 1024
- Directory-name-must-match-`name` on github.com page — not stated (https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills); stated by spec, VS Code, gh publish
- Copilot support for `agent` (with `context: fork`), `model`, `compatibility`, `metadata`, `hooks`, `paths`, `effort`, `$ARGUMENTS` — not mentioned (https://code.visualstudio.com/docs/copilot/customization/agent-skills ; https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
- `once` as a skill frontmatter key — Claude page mentions it only as a `hooks` option defined on the hooks page (https://code.claude.com/docs/en/skills)
- Subagent `skills:` preload field format — on the sub-agents page, not in the fetch list (https://code.claude.com/docs/en/skills only cross-references it)
- Whether the Claude Code page states that Copilot ignores Claude-only keys — it does not; it says only that non-spec keys fail claude.ai upload / Skills API / `package_skill.py` (https://code.claude.com/docs/en/skills)
- `gh skill list`, `gh skill search`, `gh skill preview`, `gh skill update` manual pages — not in the assigned URL list; not fetched (https://cli.github.com/manual/gh_skill lists them)

Fetch date: 2026-09-04. Every claim carries its source URL. `UNVERIFIED (<url>)` marks items the fetched page did not state.

Abbreviations for source URLs used inline:
- GH-REPO = https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions
- GH-CR = https://docs.github.com/en/copilot/tutorials/customize-code-review
- VSC-INSTR = https://code.visualstudio.com/docs/agent-customization/custom-instructions
- VSC-PROMPT = https://code.visualstudio.com/docs/agent-customization/prompt-files
- AGENTSMD = https://agents.md/
- CC-MEM = https://code.claude.com/docs/en/memory
- CURSOR = https://cursor.com/docs/context/rules (final URL; see Cursor section for redirect chain)
- GH-CHEAT = https://docs.github.com/en/copilot/reference/customization-cheat-sheet

## `.github/copilot-instructions.md`
Sources: GH-REPO, GH-CR, VSC-INSTR, GH-CHEAT (fetched 2026-09-04)

### Discovery and surfaces
- Path: "a `copilot-instructions.md` file in the `.github` directory" (GH-REPO); cheat sheet spells it `.github/copilot-instructions.md` "(repo-wide)" (GH-CHEAT).
- Activation: "The instructions in the file(s) are available for use by Copilot as soon as you save the file(s)" (GH-REPO).
- GH-REPO enumerates "three types of repository custom instructions": "Repository-wide custom instructions apply to all requests made in the context of a repository", "Path-specific custom instructions apply to requests made in the context of files that match a specified path", "Agent instructions are used by AI agents" (GH-REPO).
- Copilot Chat on github.com: "In Copilot Chat (github.com/copilot), you can start a conversation that uses repository custom instructions by adding, as an attachment, the repository that contains the instructions file" (GH-REPO). "Whenever repository custom instructions are used by Copilot Chat, the instructions file is added as a reference for the response that's generated" (GH-REPO).
- Copilot code review: "Custom instructions are enabled for Copilot code review by default but you can disable, or re-enable, them in the repository settings on GitHub.com" (GH-REPO). "When reviewing a pull request, Copilot reads repository custom instructions, agent instructions, and agent skills from the head branch (the branch with your changes), not the base branch" (GH-CR).
- Per-feature support matrix: GH-REPO defers to "About customizing GitHub Copilot responses" (not in the fetched set) — UNVERIFIED (GH-REPO).
- IDE/surface support row (GH-CHEAT), header "| Feature | VS Code | Visual Studio | JetBrains IDEs | Eclipse | Xcode | GitHub .com | Copilot CLI |": "| Custom instructions | ✓ | ✓ | P | P | P | ✓ | ✓ |" (P = preview) (GH-CHEAT). Cheat-sheet definition: "Custom instructions | Always-on context that automatically applies to every interaction within its defined scope | `.github/copilot-instructions.md` (repo-wide), `.github/instructions/*.instructions.md` (path-specific)" (GH-CHEAT).
- VS Code: "VS Code automatically detects a `.github/copilot-instructions.md` Markdown file in the root of your workspace and applies the instructions in this file to all chat requests within this workspace" (VSC-INSTR). Listed under "Always-on instructions" together with `AGENTS.md`, organization-level instructions and `CLAUDE.md` (VSC-INSTR). No enabling setting for this file is named on VSC-INSTR — UNVERIFIED (VSC-INSTR). Monorepo: "In a monorepo, enable chat.useCustomizationsInParentRepositories to discover instructions from the parent repository root" (VSC-INSTR).
- Combination with path-specific files: "If the path you specify matches a file that Copilot is working on, and a repository-wide custom instructions file also exists, then the instructions from both files are used" (GH-REPO).
- Precedence across scopes: "Personal instructions take the highest priority. Repository instructions come next, and then organization instructions are prioritized last" (GH-REPO; same order restated on VSC-INSTR). Within a workspace: "If you have multiple instruction files in your project, VS Code combines and adds them to the chat context, no specific order is guaranteed" (VSC-INSTR).
- Organization instructions: set via "personal/org settings via UI on GitHub" (GH-CHEAT); VS Code discovery setting `github.copilot.chat.organizationInstructions.enabled` (VSC-INSTR).

### Frontmatter
- None documented. GH-REPO introduces a frontmatter block only for path-specific `*.instructions.md` files; no frontmatter for `copilot-instructions.md` (GH-REPO). VSC-INSTR example shows no YAML header (VSC-INSTR). GH-CR documents no frontmatter for it (GH-CR). GH-CHEAT: not mentioned (GH-CHEAT).

### Limits and guidance
- Format: "natural language instructions to the file, in Markdown format" (GH-REPO). "Whitespace between instructions is ignored, so the instructions can be written as a single paragraph, each on a new line, or separated by blank lines for legibility" (GH-REPO).
- Length (two pages differ): "Instructions must be no longer than 2 pages" (GH-REPO) vs "Best practice: Limit any single instruction file to a maximum of about 1,000 lines. Beyond this, the quality of responses may deteriorate" (GH-CR). VS Code: "Keep them concise and focused for optimal results"; no numeric limit (VSC-INSTR).
- Content: "Instructions must not be task specific" (GH-REPO). GH-CR lists instruction categories that are not supported: "Change the user experience or formatting" (e.g. `Use bold text for critical issues`, `Add emoji to comments`); "Modify the pull request overview comment"; "Change GitHub Copilot's core function" (e.g. `Block a PR from merging unless all Copilot code review comments are addressed`); "Follow external links" (e.g. `Review this code according to the standards at https://example.com/standards`; workaround: copy content into the file); "Vague quality improvements" (e.g. `Be more accurate`) (GH-CR).
- Recommended content (GH-CR): "General team standards and guidelines", "Universal security requirements", "Cross-cutting concerns", "Documentation expectations" (GH-CR). VSC-INSTR suggests coding style, naming conventions, technology stack, architectural patterns, security, documentation standards (VSC-INSTR).
- A list of things that "may not work" on GH-REPO: NOT FOUND — UNVERIFIED (GH-REPO).

## `*.instructions.md` (path-specific instructions)
Sources: GH-REPO, GH-CR, VSC-INSTR, GH-CHEAT (fetched 2026-09-04)

### Discovery locations and surfaces
- github.com: "Create the `.github/instructions` directory"; "Create one or more `NAME.instructions.md` files, where `NAME` indicates the purpose of the instructions. The file name must end with `.instructions.md`"; "Optionally, create subdirectories of `.github/instructions` to organize your instruction files" (GH-REPO). Cheat-sheet pattern: `.github/instructions/*.instructions.md` "(path-specific)" (GH-CHEAT).
- github.com surfaces: "Currently, on GitHub.com, path-specific custom instructions are only supported for Copilot cloud agent and Copilot code review" (GH-REPO). GH-CR examples: `.github/instructions/python.instructions.md`, `.github/instructions/frontend.instructions.md` (GH-CR).
- VS Code default locations (VSC-INSTR): workspace `.github/instructions`; workspace `.claude/rules` (Claude format); user profile `~/.copilot/instructions` or `~/.claude/rules`. "You can configure additional file locations for workspace instructions files with the chat.instructionsFilesLocations setting" (VSC-INSTR). "VS Code searches these folders recursively, to enable you to organize instructions files in subdirectories" (VSC-INSTR). Parent repo: `chat.useCustomizationsInParentRepositories` (VSC-INSTR). Setting `chat.includeApplyingInstructions` reported as controlling pattern-based instructions (VSC-INSTR; exact sentence not captured verbatim).
- VS Code application: "based on the file patterns specified in the `applyTo` property in the instructions file header or semantic matching" (VSC-INSTR). Markdown links may reference other files, e.g. "Apply the [general coding guidelines](./general-coding.instructions.md) to all code." (VSC-INSTR).
- Other discovery paths on github.com beyond `.github/instructions` and its subdirectories: none documented — UNVERIFIED (GH-REPO).

### Frontmatter keys
| Key | Type | Required | Allowed values / format | Surfaces | Notes and source |
|---|---|---|---|---|---|
| `applyTo` | string (glob; several globs comma-separated inside one string) | github.com: documented step is "create a frontmatter block containing the `applyTo` keyword" (word "required" not used) (GH-REPO). VS Code: "No" (VSC-INSTR) | "Use glob syntax to specify what files or directories the instructions apply to" (GH-REPO). "You can specify multiple patterns by separating them with commas" (GH-REPO). Examples: `applyTo: "app/models/**/*.rb"`, `applyTo: "**/*.ts,**/*.tsx"`, `applyTo: "**"` (GH-REPO); `applyTo: "**/*.py"`, `applyTo: "src/components/**/*.{tsx,jsx}"` (GH-CR); `applyTo: '**/*.py'`, `"**/*.ts,**/*.tsx"` (VSC-INSTR). No YAML-list form shown on any page. | github.com (cloud agent, code review) (GH-REPO); VS Code (VSC-INSTR) | VS Code: "Glob pattern that defines which files the instructions apply to automatically, relative to the workspace root. Use `**` to apply to all files"; "If not specified, the instructions are not applied automatically, but you can still add them manually to a chat request" (VSC-INSTR). GH glob list: "`*` - will all match all files in the current directory. `**` or `**/*` - will all match all files in all directories. `*.py` - will match all `.py` files in the current directory. `**/*.py` - will recursively match all `.py` files in all directories. `src/*.py` - will match all `.py` files in the `src` directory. `src/**/*.py` - will recursively match all `.py` files in the `src` directory. `**/subdir/**/*.py` - will recursively match all `.py` files in any `subdir` directory." (GH-REPO) |
| `excludeAgent` | string | Optional (GH-REPO) | `"code-review"` or `"cloud-agent"` (GH-REPO) | github.com only | "Optionally, to prevent the file from being used by either Copilot cloud agent or Copilot code review, add the `excludeAgent` keyword to the frontmatter block. Use either `"code-review"` or `"cloud-agent"`" (GH-REPO). Example: `applyTo: "**"` / `excludeAgent: "code-review"` (GH-REPO). Not mentioned on VSC-INSTR (NOT FOUND) nor GH-CR (NOT FOUND). |
| `name` | string | No (VSC-INSTR) | free text | VS Code | "Display name shown in the UI. Defaults to the file name." (VSC-INSTR). Example `name: 'Python Standards'` (VSC-INSTR). Not on GH-REPO (NOT FOUND) or GH-CR (NOT FOUND). |
| `description` | string | No (VSC-INSTR) | free text | VS Code | "Short description shown on hover in the Chat view." (VSC-INSTR). Example `description: 'Coding conventions for Python files'` (VSC-INSTR). Not on GH-REPO (NOT FOUND) or GH-CR (NOT FOUND). |
| `paths` | array of glob strings | No | globs; default `**` when omitted | VS Code, for files under `.claude/rules` only | "For `.claude/rules` instructions files, VS Code uses a `paths` property instead of `applyTo` for glob patterns, following the Claude Rules format. The `paths` property accepts an array of glob patterns and defaults to `**` (all files) when omitted." (VSC-INSTR) |

Full VS Code example (VSC-INSTR):
```
name: 'Python Standards'
description: 'Coding conventions for Python files'
applyTo: '**/*.py'
```

### Limits
- Repository-wide + path-specific both used when both match (GH-REPO). No explicit size limit for path-specific files on GH-REPO — UNVERIFIED (GH-REPO). "Limit any single instruction file to a maximum of about 1,000 lines" applies to any instruction file (GH-CR). Number-of-files limit: not documented — UNVERIFIED (GH-REPO, GH-CR, VSC-INSTR).

## `*.prompt.md` (prompt files)
Sources: VSC-PROMPT, GH-CHEAT (fetched 2026-09-04)

### Discovery locations and surfaces
- Workspace: "`.github/prompts` folder" (VSC-PROMPT); cheat sheet: `.github/prompts/*.prompt.md` (GH-CHEAT). User: "Your user data (specific to your VS Code profile)" (VSC-PROMPT). Additional: "You can configure additional file locations for workspace prompt files with the chat.promptFilesLocations setting" (VSC-PROMPT). Monorepo: "enable chat.useCustomizationsInParentRepositories to discover prompt files from the parent repository root" (VSC-PROMPT). Subfolder recursion: NOT FOUND — UNVERIFIED (VSC-PROMPT). Master toggle `chat.promptFiles`: NOT FOUND — UNVERIFIED (VSC-PROMPT).
- Invocation: type `/` followed by the prompt name in chat; **Chat: Run Prompt** command; play button in the editor title area (VSC-PROMPT).
- Surface row (GH-CHEAT, same header as above): "| Prompt files | ✓ | ✓ | P | ✗ | P | ✗ | ✗ |" i.e. VS Code ✓, Visual Studio ✓, JetBrains P, Eclipse ✗, Xcode P, GitHub.com ✗, Copilot CLI ✗ (GH-CHEAT). Definition: "Prompt files | Reusable, standalone prompt template with input variables | `.github/prompts/*.prompt.md`" (GH-CHEAT).
- "Agents running on the Agent Host don't use prompt files." (VSC-PROMPT). Migration: "The Agent Customizations editor offers a one-time migration that converts your prompt files to skills (experimental, enable chat.customizations.promptMigration.enabled)" (VSC-PROMPT). Settings Sync: "Prompts and Instructions" via **Settings Sync: Configure** (VSC-PROMPT).

### Frontmatter keys
| Key | Type | Required | Allowed values / format | Notes and source |
|---|---|---|---|---|
| `description` | string | No | free text | "A short description of the prompt." (VSC-PROMPT) |
| `name` | string | No | free text | "The name of the prompt, used after typing `/` in chat. If not specified, the file name is used." (VSC-PROMPT) |
| `argument-hint` | string | No | free text | "Hint text shown in the chat input field to guide users on how to interact with the prompt." (VSC-PROMPT) |
| `agent` | string | No | `ask`, `agent`, `plan`, or the name of a custom agent | "The agent used for running the prompt: `ask`, `agent`, `plan`, or the name of a custom agent. By default, the current agent is used. If tools are specified, the default agent is `agent`." (VSC-PROMPT). Examples `agent: 'agent'`, `agent: 'ask'` (VSC-PROMPT) |
| `model` | string | No | model display name, e.g. `GPT-4o`, `Claude Sonnet 4` | "The language model used when running the prompt. If not specified, the currently selected model in model picker is used." (VSC-PROMPT). Behaviour when model unavailable: NOT FOUND — UNVERIFIED (VSC-PROMPT) |
| `tools` | list (YAML array) | No | tool names, tool set names, MCP tools (`<server name>/*` for all tools of a server), extension tools | "A list of tool or tool set names that are available for this prompt. Can include built-in tools, tool sets, MCP tools, or tools contributed by extensions. To include all tools of an MCP server, use the `<server name>/*` format." "If a given tool is not available when running the prompt, it is ignored." (VSC-PROMPT). Example `tools: ['search/codebase', 'vscode/askQuestions']` (VSC-PROMPT). Priority: tools in prompt file > tools of referenced custom agent > default tools of selected agent (VSC-PROMPT) |
| `mode` | — | — | — | NOT FOUND anywhere on VSC-PROMPT; legacy/deprecated status UNVERIFIED (VSC-PROMPT). GH-CHEAT lists no prompt-file frontmatter (GH-CHEAT) |

Example (VSC-PROMPT):
```
agent: 'agent'
model: GPT-4o
tools: ['search/codebase', 'vscode/askQuestions']
description: 'Generate a new React form component'
```

### Variables and substitution
- Listed on VSC-PROMPT: `${selection}`, `${input:variableName}`, `${input:variableName:placeholder}`. Introducing sentence: "Take advantage of built-in variables like `${selection}` and input variables to make prompts more flexible." (VSC-PROMPT)
- NOT FOUND on VSC-PROMPT: `${workspaceFolder}`, `${workspaceFolderBasename}`, `${selectedText}`, `${file}`, `${fileBasename}`, `${fileDirname}`, `${fileBasenameNoExtension}` — UNVERIFIED (VSC-PROMPT).
- File references: "You can reference other workspace files by using Markdown links. Use relative paths to reference these files, and ensure that the paths are correct based on the location of the prompt file." (VSC-PROMPT). Tip: "Use Markdown links to reference custom instructions rather than duplicating guidelines in each prompt" (VSC-PROMPT).

## `AGENTS.md`
Sources: AGENTSMD, GH-REPO, GH-CR, VSC-INSTR, GH-CHEAT, CC-MEM, CURSOR (fetched 2026-09-04)

### Discovery (root, nested, which tools read it, VS Code experimental status if stated)
- agents.md: "Create an AGENTS.md file at the root of the repository." Nested: "Place another AGENTS.md inside each package. Agents automatically read the nearest file in the directory tree, so the closest one takes precedence." "Explicit user chat prompts override everything." (AGENTSMD)
- Tools listed as reading it (AGENTSMD): Codex, Jules, Factory, Aider, goose, opencode, Zed, Warp, VS Code, Devin, Autopilot & Coded Agents, Junie, Amp, Cursor, RooCode, Gemini CLI, Kilo Code, Phoenix, Semgrep, Coding agent (GitHub Copilot), Ona, Windsurf, Augment Code. Stewardship: "AGENTS.md is now stewarded by the Agentic AI Foundation under the Linux Foundation" (AGENTSMD).
- GitHub Copilot: "Agent instructions are used by AI agents. You can create one or more `AGENTS.md` files, stored anywhere within the repository." "When Copilot is working, the nearest `AGENTS.md` file in the directory tree will take precedence." "Alternatively, you can use a single `CLAUDE.md` or `GEMINI.md` file stored in the root of the repository." (GH-REPO). Which Copilot features read it: not enumerated on GH-REPO — UNVERIFIED (GH-REPO). Cheat sheet lists "`AGENTS.md` (third-party agents)" under custom instructions (GH-CHEAT). Code review: reads "agent instructions ... from the head branch"; "Use `AGENTS.md` for instructions that apply to specific custom agents in your repository ... including shaping Copilot code review feedback"; example file has a `## Code Review` section (GH-CR).
- VS Code: "VS Code automatically detects an `AGENTS.md` Markdown file in the root of your workspace and applies the instructions in this file to all chat requests within this workspace." "To enable or disable support for `AGENTS.md` files, configure the chat.useAgentsMdFile setting." Nested: "Use the chat.useNestedAgentsMdFiles setting to enable or disable support for nested `AGENTS.md` files in your workspace." "Nested AGENTS.md files is experimental and might change or be removed." (VSC-INSTR)
- Cursor: "Cursor supports AGENTS.md in the project root and subdirectories." "Instructions from nested `AGENTS.md` files are combined with parent directories, with more specific instructions taking precedence." "Place it in your project root as an alternative to `.cursor/rules`." (CURSOR)
- Claude Code: "Claude Code reads `CLAUDE.md`, not `AGENTS.md`." (CC-MEM) — see Claude section.

### Format (frontmatter? plain Markdown?)
- "AGENTS.md is just standard Markdown. Use any headings you like; the agent simply parses the text you provide." No required sections; suggested sections listed under "Cover what matters" (AGENTSMD). No size limit stated (AGENTSMD).
- No frontmatter documented on GH-REPO, GH-CR, VSC-INSTR (all NOT FOUND). Cursor: "`AGENTS.md` is a plain markdown file without metadata or complex configurations." (CURSOR)

### Legacy `AGENT.md` singular (if documented anywhere; else UNVERIFIED)
- AGENTSMD: "Rename existing files to AGENTS.md and create symbolic links for backward compatibility: `mv AGENT.md AGENTS.md && ln -s AGENTS.md AGENT.md`" (AGENTSMD).
- Not mentioned on GH-REPO, VSC-INSTR, GH-CHEAT, CC-MEM, CURSOR — UNVERIFIED for those tools (GH-REPO, VSC-INSTR, GH-CHEAT, CC-MEM, CURSOR).

## Claude Code `CLAUDE.md`, `CLAUDE.local.md`, `.claude/rules/`, `.claude/commands/`
Sources: CC-MEM; cross-reference VSC-INSTR (fetched 2026-09-04)

### Memory file locations and precedence
- Load order table, "from broadest scope to most specific" (CC-MEM):
  - Managed policy: macOS `/Library/Application Support/ClaudeCode/CLAUDE.md`; Linux and WSL `/etc/claude-code/CLAUDE.md`; Windows `C:\Program Files\ClaudeCode\CLAUDE.md`. "This file cannot be excluded by individual settings." Alternative: `claudeMd` key in `managed-settings.json` ("Loads before user and project CLAUDE.md"; honored in managed/policy settings only) (CC-MEM).
  - User instructions: `~/.claude/CLAUDE.md` (CC-MEM).
  - Project instructions: `./CLAUDE.md` or `./.claude/CLAUDE.md` (CC-MEM).
  - Local instructions: `./CLAUDE.local.md` — "Personal project-specific preferences; add to `.gitignore`" (CC-MEM). "It loads alongside `CLAUDE.md` and is treated the same way. Add `CLAUDE.local.md` to your `.gitignore` so it isn't committed. With `CLAUDE_CODE_NEW_INIT=1` set, running `/init` and choosing the personal option does this for you." (CC-MEM) — not auto-gitignored by default.
- Parent walk: "Claude Code loads `CLAUDE.md` and `CLAUDE.local.md` from your current working directory and every directory above it." "All discovered files are concatenated into context rather than overriding each other. Across the directory tree, content is ordered from the filesystem root down to your working directory." "Within each directory, `CLAUDE.local.md` is appended after `CLAUDE.md`" (CC-MEM).
- Subdirectories: "Files in subdirectories load on demand when Claude reads files in those directories." (CC-MEM)
- Exclusion: `claudeMdExcludes` setting (array of absolute-path globs, any settings layer, arrays merge; managed policy files cannot be excluded) (CC-MEM). `--add-dir` directories: CLAUDE.md not loaded unless `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`, which loads `CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/*.md`, `CLAUDE.local.md` from those dirs; `CLAUDE.local.md` skipped if `local` excluded from `--setting-sources` (CC-MEM).
- Size: "target under 200 lines per CLAUDE.md file"; "Claude Code loads a CLAUDE.md file of up to 4 MiB in full and skips a larger file." (CC-MEM). "Block-level HTML comments (`<!-- maintainer notes -->`) in CLAUDE.md files are stripped before the content is injected"; "Comments inside code blocks are preserved." (CC-MEM). Delivered "as a user message after the system prompt" (CC-MEM). Project-root CLAUDE.md is re-read after `/compact` (CC-MEM).
- VS Code cross-reference: "VS Code automatically detects a `CLAUDE.md` file and applies it as always-on instructions, similar to `AGENTS.md`." Locations searched: `CLAUDE.md` (workspace root), `.claude/CLAUDE.md`, `~/.claude/CLAUDE.md`, `CLAUDE.local.md`; setting `chat.useClaudeMdFile` (VSC-INSTR).

### `@import` syntax
- "CLAUDE.md files can import additional files using `@path/to/import` syntax. Imported files are expanded and loaded into context at launch alongside the CLAUDE.md that references them." (CC-MEM)
- Paths: "Both relative and absolute paths are allowed. Relative paths resolve relative to the file containing the import, not the working directory." (CC-MEM). Home: example `- @~/.claude/my-project-instructions.md` (CC-MEM).
- Depth: "Imported files can recursively import other files, with a maximum depth of four hops." (CC-MEM)
- Code spans/fences: "Import parsing skips Markdown code spans and fenced code blocks. To mention a path in your CLAUDE.md without importing it, wrap it in backticks" (CC-MEM).
- Examples: `See @README for project overview and @package.json for available npm commands for this project.`; `- git workflow @docs/git-instructions.md` (CC-MEM).
- External imports: "An import in a project-level memory file is external when its path resolves outside your working directory ... The first time Claude Code encounters external imports in a project, it shows an approval dialog listing the files. If you decline, the imports stay disabled and the dialog doesn't appear again." User-scope files load imports without the dialog, except in Cowork sessions (CC-MEM).
- Context: "imported files still load and enter the context window at launch" (CC-MEM).

### `.claude/rules/*.md`
| Key | Type | Allowed values / format | Notes and source |
|---|---|---|---|
| `paths` | YAML list of glob strings | e.g. `- "src/api/**/*.ts"`, `- "src/**/*.{ts,tsx}"`, `- "lib/**/*.ts"`, `- "tests/**/*.test.ts"`; pattern table: `**/*.ts` (all TS files in any directory), `src/**/*` (all files under `src/`), `*.md` (Markdown files in project root), `src/components/*.tsx` (CC-MEM) | "Rules can be scoped to specific files using YAML frontmatter with the `paths` field." "Rules without a `paths` field are loaded unconditionally and apply to all files." "Rules without `paths` frontmatter are loaded at launch with the same priority as `.claude/CLAUDE.md`." "Path-scoped rules trigger when Claude reads files matching the pattern, not on every tool use." Brace expansion supported; "a rule's whole `paths` list shares one budget of 1,000 expanded patterns and 4 MiB, and patterns without braces don't count against it"; over-budget pattern used unexpanded. `[` starts a bracket expression; invalid bracket pattern matches nothing; escape as `\[` (CC-MEM). VS Code reads the same files: "`paths` property accepts an array of glob patterns and defaults to `**` (all files) when omitted" (VSC-INSTR). |

- Location/discovery: project `.claude/rules/` — "All `.md` files are discovered recursively, so you can organize rules into subdirectories"; symlinked files and directories supported, circular symlinks handled (CC-MEM). User-level `~/.claude/rules/` — "User-level rules are loaded before project rules, giving project rules higher priority." (CC-MEM). Project rules skipped if `project` excluded from `--setting-sources` (CC-MEM). Other frontmatter keys for rules: none documented — UNVERIFIED (CC-MEM).

### `.claude/commands/*.md`
- Status: CC-MEM does not describe `.claude/commands/` at all; only mention is that `/import` "carries over MCP servers, commands, subagents, and skills" (CC-MEM). Legacy-vs-skills status: UNVERIFIED (CC-MEM). Frontmatter keys: UNVERIFIED (CC-MEM). `$ARGUMENTS`: UNVERIFIED (CC-MEM).
- Related statement on CC-MEM: "For task-specific instructions that don't need to be in context all the time, use skills instead, which only load when you invoke them or when Claude determines they're relevant to your prompt." (CC-MEM)

### Relationship between `CLAUDE.md` and `AGENTS.md`
- "Claude Code reads `CLAUDE.md`, not `AGENTS.md`. If your repository already uses `AGENTS.md` for other coding agents, create a `CLAUDE.md` that imports it so both tools read the same instructions without duplicating them." Example file body: `@AGENTS.md` followed by `## Claude Code` section (CC-MEM).
- Symlink alternative: `ln -s AGENTS.md CLAUDE.md`; "On Windows, creating a symlink requires Administrator privileges or Developer Mode, so use the `@AGENTS.md` import instead." (CC-MEM)
- `/init` "reads Cursor rules, in `.cursor/rules/` or `.cursorrules`, and Copilot rules, in `.github/copilot-instructions.md`, and incorporates the relevant parts into the generated `CLAUDE.md`. With `CLAUDE_CODE_NEW_INIT=1` set, `/init` also reads `AGENTS.md`, `.devin/rules/`, `.windsurf/rules/` or `.windsurfrules`, and `.clinerules`." (CC-MEM)
- `/import` "appends a one-time copy of instruction files such as `AGENTS.md` to the matching `CLAUDE.md` and carries over MCP servers, commands, subagents, and skills. Requires Claude Code v2.1.213 or later." (CC-MEM)

## Cursor rules
Sources: https://docs.cursor.com/context/rules → HTTP 308 Permanent Redirect → https://cursor.com/docs (docs landing page; does not document rules); current rules page fetched at https://cursor.com/docs/context/rules (fetched 2026-09-04). Cross-reference CC-MEM.

### Location and file extension
- Project Rules live in `.cursor/rules/`: "Each rule is an `.mdc` file that you can name anything you want." "Project rules must use the `.mdc` extension." "A plain `.md` file in `.cursor/rules` is ignored by the rules system because it has no frontmatter." (CURSOR)
- Nested `.cursor/rules` directories in subdirectories: NOT FOUND on CURSOR — UNVERIFIED (CURSOR). (Nesting is documented only for `AGENTS.md`: "Cursor supports AGENTS.md in the project root and subdirectories." (CURSOR))
- Legacy `.cursorrules`: NOT FOUND on CURSOR — UNVERIFIED (CURSOR). Only external mention: Claude Code `/init` "reads Cursor rules, in `.cursor/rules/` or `.cursorrules`" (CC-MEM).
- User Rules: "User Rules are global preferences defined in **Customize → Rules** that apply across all projects." (CURSOR). Team Rules: "Team and Enterprise plans can create and enforce rules across their entire organization from the Cursor dashboard." "Team Rules work alongside other rule types and take precedence to ensure organizational standards are maintained." "Team Rules are free‑form text. They do not use the folder structure of Project Rules." "Team Rules support glob patterns for file-scoped application." (CURSOR)
- `AGENTS.md` alternative: "`AGENTS.md` is a simple markdown file for defining agent instructions. Place it in your project root as an alternative to `.cursor/rules`." "Unlike Project Rules, `AGENTS.md` is a plain markdown file without metadata or complex configurations." (CURSOR)
- Generation: "`/create-rule` in chat: Type `/create-rule` in Agent and describe what you want." (CURSOR). `/Generate Cursor Rules`: NOT FOUND (CURSOR).
- Guidance: "Keep rules under 500 lines"; "Use `@filename.ts` to include files in your rule's context."; "Reference files instead of copying their contents—this keeps rules short."; "You can also @mention rules in chat to apply them manually." (CURSOR). `CLAUDE.md`: NOT FOUND (CURSOR). "Memories": NOT FOUND (CURSOR).

### Frontmatter keys
| Key | Type | Allowed values | Notes and source |
|---|---|---|---|
| `description` | string | free text | Drives the "Apply Intelligently" type: "When Agent decides it's relevant based on description". Example `description: RPC service conventions and patterns for the backend` with `alwaysApply: false` (CURSOR) |
| `globs` | string (glob pattern, unquoted in the example) | e.g. `globs: src/components/**/*.tsx` | Drives "Apply to Specific Files": "When file matches a specified pattern". Only a single-pattern example is shown; comma-separated or list form UNVERIFIED (CURSOR) |
| `alwaysApply` | boolean | `true` / `false` | `true` → "Always Apply" ("Apply to every chat session"); `false` with neither `description` nor `globs` → "Apply Manually" ("When @-mentioned in chat (e.g., `@my-rule`)") (CURSOR) |

Rule types exactly as written (CURSOR): `Always Apply` — "Apply to every chat session"; `Apply Intelligently` — "When Agent decides it's relevant based on description"; `Apply to Specific Files` — "When file matches a specified pattern"; `Apply Manually` — "When @-mentioned in chat (e.g., `@my-rule`)". Other keys: none documented — UNVERIFIED (CURSOR).

### Unresolved items from this group
- Cursor original URL https://docs.cursor.com/context/rules returned HTTP 308 to https://cursor.com/docs; that landing page has no rules content. Data taken from https://cursor.com/docs/context/rules instead.
- Per-Copilot-feature support matrix (Chat / coding agent / code review / CLI) for `.github/copilot-instructions.md`: GH-REPO defers to a concept page not in the fetched set — UNVERIFIED (https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions).
- Whether GH-REPO has IDE tool tabs (VS Code / Visual Studio / JetBrains / Xcode / Eclipse) and IDE-specific enabling settings: NOT FOUND in fetched content — UNVERIFIED (https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions).
- VS Code setting that enables `.github/copilot-instructions.md` (e.g. `github.copilot.chat.codeGeneration.useInstructionFiles`): not named — UNVERIFIED (https://code.visualstudio.com/docs/agent-customization/custom-instructions).
- Exact sentence for `chat.includeApplyingInstructions`: reported by fetch but not captured verbatim (https://code.visualstudio.com/docs/agent-customization/custom-instructions).
- Explicit "required" status of `applyTo` on github.com; size limit and file-count limit for path-specific files — UNVERIFIED (https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions).
- Prompt files: `mode` key (legacy or otherwise), `chat.promptFiles` setting, subfolder recursion, behaviour when `model` is unavailable, `${workspaceFolder}`/`${file}`-family variables — all NOT FOUND (https://code.visualstudio.com/docs/agent-customization/prompt-files).
- Which GitHub Copilot features read `AGENTS.md` (beyond code review and "AI agents"); precedence of `AGENTS.md` vs `.github/copilot-instructions.md` — UNVERIFIED (https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions, https://docs.github.com/en/copilot/reference/customization-cheat-sheet).
- Legacy `AGENT.md` singular: documented only at https://agents.md/; UNVERIFIED for GitHub, VS Code, Claude Code and Cursor (https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions, https://code.visualstudio.com/docs/agent-customization/custom-instructions, https://code.claude.com/docs/en/memory, https://cursor.com/docs/context/rules).
- `.claude/commands/*.md` status, frontmatter keys and `$ARGUMENTS`: not covered — UNVERIFIED (https://code.claude.com/docs/en/memory).
- `.claude/rules/*.md` frontmatter keys other than `paths`: none documented — UNVERIFIED (https://code.claude.com/docs/en/memory).
- Cursor: legacy `.cursorrules` support status, nested `.cursor/rules` directories, comma-separated/list form of `globs`, `CLAUDE.md` handling, "Memories", page "Last updated" date — all NOT FOUND (https://cursor.com/docs/context/rules).
- Cheat sheet: frontmatter keys, size limits, precedence and per-surface support of `AGENTS.md` — NOT FOUND (https://docs.github.com/en/copilot/reference/customization-cheat-sheet).

All claims below come from the five pages listed per section, fetched 2026-09-04 via WebFetch. Quoted text is verbatim from the page. Items the pages do not state are marked `UNVERIFIED (<url>)`.

Source abbreviations used in tables:
- CC = https://code.claude.com/docs/en/mcp
- VSC = https://code.visualstudio.com/docs/agents/reference/mcp-configuration
- CLI = https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers
- CA = https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/configure-mcp-servers
- ENV = https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-environment


## Claude Code `.mcp.json`
Sources: https://code.claude.com/docs/en/mcp (fetched 2026-09-04)

### Locations and scopes

Page table "MCP installation scopes" (verbatim columns/rows):

| Scope | Loads in | Shared with team | Stored in |
|---|---|---|---|
| Local | Current project only | No | `~/.claude.json` |
| Project | Current project only | Yes, via version control | `.mcp.json` in project root |
| User | All your projects | No | `~/.claude.json` |

- Local scope is written to `~/.claude.json` under `"projects"` → `"/path/to/your/project"` → `"mcpServers"` (page example). User scope is written to `~/.claude.json` at top level. (CC)
- Project scope: "Project-scoped servers enable team collaboration by storing configurations in a `.mcp.json` file at your project's root directory." "When you add a project-scoped server, Claude Code automatically creates or updates this file with the appropriate configuration structure." "Check `.mcp.json` into version control so everyone on your team gets the same MCP tools and services." (CC)
- Enterprise: "Administrators can also deploy servers at the enterprise level via managed configuration." The page mentions `managed-mcp.json` only in passing ("Claude Code drops the delivered connectors when a `managed-mcp.json` is present on the host that runs the session"; "See Exclusive control with managed-mcp.json ... for what the flag does under a managed MCP file"). File paths, format and precedence of the enterprise scope: UNVERIFIED (https://code.claude.com/docs/en/mcp — details live on /docs/en/managed-mcp, not in scope).
- Precedence ("Scope hierarchy and precedence", verbatim): "When the same server is defined in more than one place, Claude Code connects to it once, using the definition from the highest-precedence source. The entire server entry from that source is used; fields are not merged across scopes." Order: 1. Local scope, 2. Project scope, 3. User scope, 4. Plugin-provided servers, 5. claude.ai connectors. "The three scopes match duplicates by name. Plugins and connectors match by endpoint, so one that points at the same URL or command as a server above is treated as a duplicate." (CC)
- `claude mcp add` scope flag (verbatim): "Use the `-s` or `--scope` flag to specify where the configuration is stored: `local` (default): available only to you in the current project; `project`: shared with everyone in the project via the `.mcp.json` file; `user`: available to you across all projects". "Local scope is the default." (CC)
- Example commands: `claude mcp add --transport http stripe https://mcp.stripe.com` (local); `claude mcp add --transport http shared-server --scope project https://example.com/mcp` (writes `.mcp.json`); `claude mcp add --transport http hubspot --scope user https://mcp.hubspot.com/anthropic`. (CC)
- Stdio via CLI: "For stdio servers, the `--` (double dash) separates Claude's own options, such as `--transport`, `--env`, and `--scope`, from the command and arguments that run the server. Everything after `--` is passed to the server untouched." `--env` "accepts multiple `KEY=value` pairs"; short form `-e`. (CC)
- JSON via CLI: `claude mcp add-json <name> '<json>'` (accepts `--scope`); `--transport` values documented: `http`, `sse`, `stdio`; "The `claude mcp add --transport` flag doesn't accept `ws`." — `ws` requires `claude mcp add-json` or a JSON file. (CC)
- Approval: "For security reasons, Claude Code prompts for approval in interactive sessions before using project-scoped servers from `.mcp.json` files." Reset with `claude mcp reset-project-choices`. Settings keys `enabledMcpjsonServers` / `disabledMcpjsonServers` "control approval of servers defined in a project's `.mcp.json` file"; `enableAllProjectMcpServers` approves all. "A cloned repository can't approve its own servers: `enableAllProjectMcpServers` or `enabledMcpjsonServers` committed to the project's `.claude/settings.json` is ignored in an untrusted folder". (CC)
- Per-project toggles in `~/.claude.json`: `disabledMcpServers` ("an opt-out list for user-configured servers, plugin servers, the claude.ai connectors ... and built-in servers that default to on") and `enabledMcpServers` ("an opt-in list for built-in servers that default to off, such as `computer-use`"); these "are unrelated to `enabledMcpjsonServers` and `disabledMcpjsonServers`". (CC)

### Top-level key and server entry schema

| Key | Type | Required | Allowed values / format | Notes and source |
|---|---|---|---|---|
| `mcpServers` | object | yes (top level) | map of server name → entry | Top-level key in `.mcp.json` and inside `~/.claude.json` (CC page examples). |
| `type` | string | no (see notes) | `stdio`, `http`, `sse`, `ws`; JSON also accepts `streamable-http` as alias for `http` | "When configuring MCP servers via JSON in `.mcp.json`, `~/.claude.json`, or `claude mcp add-json`, the `type` field accepts `streamable-http` as an alias for `http`." Default when omitted: "Claude Code reads an entry with no `type` as a stdio server." `url`-only entry without `type`: "A JSON entry that has a `url` but no `type` is a configuration error ... Claude Code skips that server and reports `MCP server "<name>" has a "url" but no "type"; add "type": "http" (or "sse" / "ws") to this entry`. Before v2.1.202, Claude Code reported this misconfiguration as `command: expected string, received undefined`." (CC) |
| `command` | string | for stdio | executable path | Page examples use `"command": "npx"`. "Claude Code sets `CLAUDE_PROJECT_DIR` in the spawned server's environment to the project root". (CC) |
| `args` | array of string | no | command-line arguments | (CC) |
| `env` | object | no | string → string | Environment variables passed to the stdio server. (CC) |
| `url` | string | for `http`/`sse`/`ws` | endpoint URL (`wss://` for ws in example) | (CC) |
| `headers` | object | no | header name → value | Static HTTP headers; example `"Authorization": "Bearer YOUR_TOKEN"`. (CC) |
| `headersHelper` | string | no | shell command | "use `headersHelper` to generate request headers at connection time. Claude Code runs the command and merges its output into the connection headers." "The command must write a JSON object of string key-value pairs to stdout"; "Claude Code runs the command in a shell and gives up on it after 10 seconds"; "Dynamic headers override any static `headers` with the same name." For project/local-scope servers it runs only after the folder trust dialog is accepted. (CC) |
| `oauth` | object | no | sub-keys `clientId`, `callbackPort`, `authServerMetadataUrl`, `scopes` | "Include the `oauth` object in the JSON config and pass `--client-secret` as a separate flag"; "Set `authServerMetadataUrl` in the `oauth` object of your server's config in `.mcp.json`" ("The URL must use `https://`."); "Set `oauth.scopes` to pin the scopes ... The value is a single space-separated string". `callbackPort` shown in page example (`"callbackPort": 8080`) and set via `--callback-port`. Client secret is never stored in JSON: "The `--client-secret` flag prompts for the secret with masked input". (CC) |
| `timeout` | number (ms) | no | integer ≥ 1000 | "Set a per-server tool execution timeout by adding a `timeout` field in milliseconds to that server's `.mcp.json` entry, for example `"timeout": 600000` for ten minutes. This overrides the `MCP_TOOL_TIMEOUT` environment variable for that server only". "Values below 1000 are ignored and fall through to `MCP_TOOL_TIMEOUT`, or to its default of about 28 hours when that variable is unset." (CC) |
| `alwaysLoad` | UNVERIFIED | no | UNVERIFIED | Named only in: "The `type: "ws"` entry accepts the same `url`, `headers`, `headersHelper`, `timeout`, and `alwaysLoad` fields as `http`." Type and semantics: UNVERIFIED (https://code.claude.com/docs/en/mcp). |
| `_meta` | n/a | n/a | n/a | Not a server-entry key on this page. `_meta["anthropic/maxResultSizeChars"]` and `_meta["anthropic/requiresUserInteraction"]` are annotations "in the tool's `tools/list` response entry" set by the server author. (CC) |
| `disabled` | — | — | — | NOT ON PAGE. UNVERIFIED (https://code.claude.com/docs/en/mcp). |

Page example (verbatim, `.mcp.json`):
```json
{
  "mcpServers": {
    "shared-server": {
      "type": "http",
      "url": "https://example.com/mcp"
    }
  }
}
```
WebSocket example (verbatim): `{"mcpServers": {"events-server": {"type": "ws", "url": "wss://mcp.example.com/socket", "headers": {"Authorization": "Bearer YOUR_TOKEN"}}}}`. "Authentication is header-only, so pass a static token in `headers` or generate one at connect time with `headersHelper`." (CC)

Related environment variables (CC): `MCP_TIMEOUT` (server startup timeout, e.g. `MCP_TIMEOUT=10000 claude`); `MCP_TOOL_TIMEOUT` (tool execution, default "about 28 hours"); `MAX_MCP_OUTPUT_TOKENS` (default limit 25,000 tokens; warning at 10,000 is fixed).

### Variable expansion

Section "Environment variable expansion in `.mcp.json`" (verbatim):
- "**Supported syntax:** `${VAR}`: expands to the value of environment variable `VAR`; `${VAR:-default}`: expands to `VAR` if set, otherwise uses `default`"
- "**Expansion locations:** Environment variables can be expanded in: `command`: the server executable path; `args`: command-line arguments; `env`: environment variables passed to the server; `url`: for HTTP server types; `headers`: for HTTP server authentication"
- Missing variable: "If a referenced environment variable isn't set and has no default value, the config still loads: Claude Code reports a missing-variable warning for that server in `claude mcp list` output and uses the unexpanded `${VAR}` text as-is."
- Page example: `"url": "${API_BASE_URL:-https://api.example.com}/mcp"`, `"Authorization": "Bearer ${API_KEY}"`. A plugin example also uses `${CLAUDE_PLUGIN_ROOT}` in `command`/`args`.
- `$VAR` (no braces): not documented on this page. UNVERIFIED (https://code.claude.com/docs/en/mcp).

### Deprecated transports

- Heading "Option 2: Add a remote SSE server", warning box (verbatim): "The SSE (Server-Sent Events) transport is deprecated. Use HTTP servers instead, where available." Example: `claude mcp add --transport sse asana https://mcp.asana.com/sse`. (CC)
- `sse` remains an accepted `type` value (it appears in the error text `add "type": "http" (or "sse" / "ws")`). (CC)


## VS Code `.vscode/mcp.json`
Sources: https://code.visualstudio.com/docs/agents/reference/mcp-configuration (fetched 2026-09-04)

### Locations

- "MCP server configuration is stored in the `mcp.json` JSON file. This file can be in your workspace (`.vscode/mcp.json`) or in your user profile." (VSC)
- Commands (verbatim descriptions): "**MCP: Open User Configuration** - Open the `mcp.json` file in your user profile."; "**MCP: Open Remote User Configuration** - Open the `mcp.json` file for the remote environment."; "**MCP: Open Workspace Folder MCP Configuration** - Open the `.vscode/mcp.json` file in your workspace."; also "MCP: Add Server", "MCP: Install Server from Manifest", "MCP: List Servers", "MCP: Reset Cached Tools", "MCP: Reset Trust", "MCP: Show Installed Servers", "MCP: Browse MCP Servers", "MCP: Browse Resources". (VSC)
- Discovery setting: `chat.mcp.discovery.enabled` — "Configure automatic discovery of MCP server configuration from other applications." Which applications: NOT ON PAGE. UNVERIFIED (VSC). Other settings listed: `chat.mcp.access`, `chat.mcp.autostart`, `chat.mcp.serverSampling`, `chat.mcp.apps.enabled`. (VSC)
- Agent Host interplay (verbatim): "VS Code forwards the servers you configure to the Agent Host, except servers that require interactive input. The Agent Host doesn't read `.vscode/mcp.json` directly; for portable configuration, use a workspace `.mcp.json` or user `~/.copilot/mcp-config.json` file, which the Agent Host reads natively." (VSC)
- `devcontainer.json` / `customizations.vscode.mcp`: NOT ON PAGE. UNVERIFIED (https://code.visualstudio.com/docs/agents/reference/mcp-configuration).

### Schema

| Key | Type | Required | Allowed values / format | Notes and source |
|---|---|---|---|---|
| `servers` | object | yes | server name → entry | "`"servers": {}`: an object that maps server names to their configurations." (VSC) |
| `inputs` | array | no | input definitions | "`"inputs": []`: an optional array of input variable definitions for sensitive information like API keys." (VSC) |
| `sandbox` | object | no | `filesystem` (`allowWrite`, `denyRead`), `network` (`allowedDomains`) | "an optional object that defines file system and network access rules for sandboxed servers ... Only applies on macOS and Linux." (VSC) |
| server.`type` | string | table says "Yes" (see notes) | stdio servers: `"stdio"`; HTTP servers: `"http"`, `"sse"` | Description "Server connection type". The page's minimal example ("This example shows the minimal configuration for a basic, local MCP server using `npx`") omits `type`: `{"servers": {"memory": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-memory"]}}}`. Default when `type` omitted: NOT ON PAGE. UNVERIFIED (VSC). "VS Code first tries the HTTP Stream transport and falls back to SSE if HTTP is not supported." (VSC) |
| server.`command` | string | yes (stdio) | executable | "Command to start the server executable. Must be available on your system path or contain its full path." (VSC) |
| server.`args` | array | no | strings | "Array of arguments passed to the command" (VSC) |
| server.`cwd` | string | no | path | "Working directory for the server command. Defaults to the workspace folder when run in a workspace." Example `"${workspaceFolder}"`. (VSC) |
| server.`env` | object | no | values "strings, numbers, or null" | "Environment variables for the server. Values can be strings, numbers, or null." Example `{"API_KEY": "${input:api-key}"}`. (VSC) |
| server.`envFile` | string | no | path | "Path to an environment file to load more variables". Example `"${workspaceFolder}/.env"`. (VSC) |
| server.`dev` | object | no | `watch`, `debug` | "Development mode settings to watch for file changes and debug the server." `watch`: "A glob pattern, or an array of glob patterns, to watch for file changes that restart the MCP server." `debug`: "Enables you to set up a debugger with the MCP server. Currently, VS Code supports debugging Node.js and Python MCP servers. Available for stdio servers only." Sub-keys of `debug`: NOT ON PAGE. UNVERIFIED (VSC). |
| server.`sandboxEnabled` | boolean | no | `true`/`false` | "Run the server in a sandboxed environment. Only supported on macOS and Linux." (VSC) |
| server.`url` | string | yes (http/sse) | URL | "URL of the server" (VSC) |
| server.`headers` | object | no | header → value | "HTTP headers for authentication or configuration". Example `{"Authorization": "Bearer ${input:api-token}"}`. (VSC) |
| server.`oauth` | object | no | e.g. `{"clientId": "example-client-id"}` | "OAuth configuration for authenticating with the server" (VSC) |
| server.`gallery` | — | — | — | NOT ON PAGE. UNVERIFIED (VSC). |
| server.`version` | — | — | — | NOT ON PAGE. UNVERIFIED (VSC). |
| inputs[].`type` | string | yes | `promptString`, `pickString`, `command` | (VSC) |
| inputs[].`id` | string | yes | identifier referenced as `${input:<id>}` | "Unique identifier to reference in server config" (VSC) |
| inputs[].`description` | string | promptString/pickString (per page table) | text | "User-friendly prompt text" (VSC) |
| inputs[].`password` | boolean | no | default `false` | "Hide typed input (default: false)" (VSC) |
| inputs[].`default` | string | no | value | "Default value for the input" (VSC) |
| inputs[].`options` | array | pickString (per page table) | strings | "Array of options to choose from" (VSC) |
| inputs[].`command` | string | command type (per page table) | VS Code command ID | "Command ID to run to obtain the input value" (VSC) |
| inputs[].`args` | string/array/object | no | passed to command | "Arguments passed to the command" (VSC) |

Page example (verbatim):
```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "perplexity-key",
      "description": "Perplexity API Key",
      "password": true
    }
  ],
  "servers": {
    "perplexity": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "server-perplexity-ask"],
      "env": {
        "PERPLEXITY_API_KEY": "${input:perplexity-key}"
      }
    }
  }
}
```
SSE deprecation statement: NOT ON PAGE — `"sse"` is listed as a valid `type` without deprecation wording. (VSC)

### Variable syntax

- Stated on page: "You can use predefined variables in the server configuration, for example to refer to the workspace folder (`${workspaceFolder}`)." and "You can use predefined variables, such as `${workspaceFolder}`, in file system path values." (VSC)
- Occurrences on page: `${workspaceFolder}`, `${input:variable-id}` (e.g. `${input:api-key}`, `${input:perplexity-key}`, `${input:api-token}`), `${userHome}` (in sandbox example `"denyRead": ["${userHome}/.ssh"]`). (VSC)
- The page links to `/docs/reference/variables-reference` for the full list; `${env:NAME}`, `${config:...}`, `${command:...}`, `${workspaceFolderBasename}`, `${pathSeparator}` do not appear on this page. UNVERIFIED (https://code.visualstudio.com/docs/agents/reference/mcp-configuration).


## Copilot CLI MCP config
Sources: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers (fetched 2026-09-04)

### Location(s) and how `/mcp add` writes them

- User file: "The server is added to the user configuration at `~/.copilot/mcp-config.json`." "You can also add MCP servers by editing the configuration file at `~/.copilot/mcp-config.json`." (CLI)
- Project files: "Copilot CLI looks for project-level configuration in the following locations: `.mcp.json` (in any directory from your working directory up to the repository root)" and "`.github/mcp.json`". "When you start Copilot CLI inside a Git repository, the CLI walks from your current working directory up to the repository root, loading MCP configuration files along the way." (CLI)
- Precedence: "If both `.mcp.json` and `.github/mcp.json` exist in the same directory, `.mcp.json` takes precedence." "When server names conflict, definitions in files closer to your working directory take precedence." "Project-level definitions also take precedence over those in `~/.copilot/mcp-config.json`." (CLI)
- "The `.vscode/mcp.json` file for VS Code is not read by Copilot CLI." (CLI)
- `/mcp add` interactive form, fields in order (CLI): **Server Name** ("enter a unique name for the MCP server"); **Server Type** (select by number: **Local**, **STDIO**, **HTTP**, **SSE**); if Local/STDIO: **Command** ("enter the command to start the server, including any arguments"), **Environment Variables** ("as JSON key-value pairs"; "The `PATH` variable is automatically inherited from your environment. All other environment variables must be configured here."); if HTTP/SSE: **URL** ("paste the remote server URL"), **HTTP Headers** ("optionally specify HTTP headers as JSON"); **Tools** ("Enter `*` to include all tools, or provide a comma-separated list of tool names (no quotes needed). The default is `*`."); save with `Ctrl+S`. Result is written to `~/.copilot/mcp-config.json`.
- Non-interactive: `copilot mcp add SERVER-NAME -- COMMAND [ARGS...]` (stdio) and `copilot mcp add --transport http SERVER-NAME URL` (remote). Flags (verbatim): "`--env KEY=VALUE`: Set environment variables for the server. Repeat for multiple variables."; "`--header "HEADER: VALUE"`: Set HTTP headers for remote servers. Repeat for multiple headers."; "`--transport TRANSPORT`: Set the transport type (`stdio`, `http`, or `sse`). The default is `stdio`."; "`--tools TOOLS`: Specify which tools to enable. Use `*` for all tools (default), a comma-separated list, or `""` for none."; "`--timeout MS`: Set a timeout in milliseconds." (CLI)
- Management: `/mcp`, `/mcp list`, `/mcp show SERVER-NAME`, `/mcp edit SERVER-NAME`, `/mcp delete SERVER-NAME`, `/mcp disable SERVER-NAME`, `/mcp enable SERVER-NAME`; terminal `copilot mcp list [--json]`, `copilot mcp get SERVER-NAME [--json]`, `copilot mcp remove SERVER-NAME`. (CLI)

### Schema

| Key | Type | Required | Allowed values / format | Notes and source |
|---|---|---|---|---|
| `mcpServers` | object | yes in `~/.copilot/mcp-config.json`; optional in project files | server name → entry | "Project-level files can use either the `mcpServers` top-level object shown in `~/.copilot/mcp-config.json`, or the bare top-level format where each key is an MCP server name." Bare example: `{"playwright": {"type": "local", "command": "npx", "args": ["@playwright/mcp@latest"]}}`. (CLI) |
| `type` | string | present in all examples | `"local"`, `"http"` shown in JSON examples | Page has no sentence enumerating JSON `type` values. Menu labels are Local/STDIO ("Both options work the same way."; "**STDIO** is the standard MCP protocol type name") and HTTP/SSE; `--transport` accepts `stdio`, `http`, `sse`. Whether `"stdio"` and `"sse"` are accepted as JSON `type` values: UNVERIFIED (CLI). Default when omitted: UNVERIFIED (CLI). |
| `command` | string | local | executable | Example `"command": "npx"`. (CLI) |
| `args` | array of string | no | arguments | Example `["@playwright/mcp@latest"]`. (CLI) |
| `env` | object | no | string → string | Example `"env": {}`. Only `PATH` is inherited automatically. (CLI) |
| `url` | string | http/sse | URL | Example `"https://mcp.context7.com/mcp"`. (CLI) |
| `headers` | object | no | header → value | Example `{"CONTEXT7_API_KEY": "YOUR-API-KEY"}` (literal value). (CLI) |
| `tools` | array of string | present in user-file example; absent in project-file example | `["*"]` or tool names | Default `*` (form and `--tools`). Requiredness in JSON: NOT ON PAGE. UNVERIFIED (CLI). |
| `timeout` | — | — | — | Only `--timeout MS` flag documented; JSON key name: NOT ON PAGE. UNVERIFIED (CLI). |

Page example (verbatim, `~/.copilot/mcp-config.json`):
```json
{
  "mcpServers": {
    "playwright": {
      "type": "local",
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "env": {},
      "tools": ["*"]
    },
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "YOUR-API-KEY"
      },
      "tools": ["*"]
    }
  }
}
```
Secret/variable substitution syntax (`$VAR`, `${VAR}`, `COPILOT_MCP_`): NOT ON PAGE. UNVERIFIED (https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers).

### Legacy transports

- Verbatim: "**HTTP** uses the Streamable HTTP transport." "**SSE** uses the legacy HTTP with Server-Sent Events transport, which is deprecated in the MCP specification but still supported for backwards compatibility." (CLI)


## Copilot cloud-agent MCP JSON (repository settings)
Sources: https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/configure-mcp-servers (fetched 2026-09-04)

### Where it lives

- Not a file in the repository tree. "You enter the JSON configuration directly into the settings for the repository on GitHub.com." (CA)
- Navigation (verbatim): "On GitHub, navigate to the main page of the repository. Under your repository name, click **Settings**. In the sidebar, under "Code, planning, and automation", click **Copilot** then **MCP servers**." Then "Click **Save MCP configuration**. Your configuration will be validated to ensure proper syntax." (CA)
- "Repository administrators can configure MCP servers by following these steps." (CA)
- "This repository-level MCP configuration is shared by Copilot cloud agent and Copilot code review." (CA)
- "The GitHub MCP server and Playwright MCP server are enabled by default. You can add your own MCP servers alongside these defaults." (CA)
- "Once you've configured an MCP server, Copilot will be able to use the tools provided by the server autonomously, and will not ask for your approval before using them." (CA)
- Limits: "Copilot cloud agent and Copilot code review only support MCP tools. They do not currently support resources or prompts provided by the MCP server." "Copilot cloud agent and Copilot code review do not currently support remote MCP servers that leverage OAuth for authentication and authorization." (CA)
- Dependencies: "If your MCP servers require any dependencies not installed by default, such as `uv` and `pipx`, or need special setup, you may need to create a `copilot-setup-steps.yml` workflow file." Validation: check the session log step **Start MCP Servers**. (CA)
- Organization/enterprise policy for MCP: NOT ON PAGE. UNVERIFIED (CA).

### Schema

| Key | Type | Required | Allowed values / format | Notes and source |
|---|---|---|---|---|
| `mcpServers` | object | yes | server name → entry | Top-level key in all page examples. (CA) |
| `tools` | `string[]` | listed under "Required keys for local and remote MCP servers" | tool names, or `*` | "The tools from the MCP server to enable"; "We strongly recommend that you allowlist specific read-only tools"; "You can also enable all tools by including `*` in the array." Note: the page's Sentry example omits `tools` despite the "Required" heading — recorded as-is. (CA) |
| `type` | `string` | listed under "Required keys for local and remote MCP servers" | `"local"`, `"stdio"`, `"http"`, `"sse"` | Verbatim: "Copilot cloud agent accepts `"local"`, `"stdio"`, `"http"`, or `"sse"`." Default when omitted: NOT ON PAGE. UNVERIFIED (CA). |
| `command` | `string` | Required (local) | executable | "Required. The command to run to start the MCP server." (CA) |
| `args` | `string[]` | Required (local) | arguments | "Required. The arguments to pass to the `command`." (CA) |
| `env` | `object` | Optional (local) | var name → substitution reference or literal | "The environment variables to pass to the server. This object should map the name of the environment variable that should be exposed to your MCP server to one of the following: A substitution reference to a secret or variable in your Copilot environment, such as `$COPILOT_MCP_API_KEY` or `${COPILOT_MCP_API_KEY}`. Referenced names must start with `COPILOT_MCP_`.; A literal string value." (CA) |
| `url` | `string` | Required (remote) | URL | "Required. The MCP server's URL." (CA) |
| `headers` | `object` | Optional (remote) | header → substitution reference or literal | "The headers to attach to requests to the server. This object should map the name of header keys to one of the following: A substitution reference to a secret or variable in your Copilot environment, such as `$COPILOT_MCP_API_KEY` or `${COPILOT_MCP_API_KEY}`. Referenced names must start with `COPILOT_MCP_`.; A literal string value." (CA) |

Secret-naming rule (verbatim): "If your MCP server requires a variable, key, or secret, add an Agents secret or variable with a name prefixed with `COPILOT_MCP_`. Only Agents secrets and variables with names prefixed with `COPILOT_MCP_` will be available to your MCP configuration." (CA) The literal environment name `copilot`: NOT ON PAGE. UNVERIFIED (CA).

Substitution syntax table (verbatim): "The following syntax patterns are supported for referencing environment variables configured in your Copilot environment:"

| Syntax | Example |
|---|---|
| `$VAR` | `$COPILOT_MCP_API_KEY` |
| `${VAR}` | `${COPILOT_MCP_API_KEY}` |
| `${VAR:-default}` | `${COPILOT_MCP_API_KEY:-fallback_value}` |

"Note that all `string` and `string[]` fields besides `tools` and `type` support substitution with a variable or secret you have configured in your Copilot environment." (CA)

Page examples (verbatim):
```json
{
  "mcpServers": {
    "sentry": {
      "type": "local",
      "command": "npx",
      "args": ["@sentry/mcp-server@latest", "--host=$SENTRY_HOST"],
      "env": {
        "SENTRY_HOST": "https://contoso.sentry.io",
        "SENTRY_ACCESS_TOKEN": "$COPILOT_MCP_SENTRY_ACCESS_TOKEN"
      }
    }
  }
}
```
```json
{
  "mcpServers": {
    "cloudflare": {
      "type": "sse",
      "url": "https://docs.mcp.cloudflare.com/sse",
      "tools": ["*"]
    }
  }
}
```


## `.github/workflows/copilot-setup-steps.yml`
Sources: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-environment (fetched 2026-09-04)

### Purpose and location

- "You can customize Copilot's environment by creating a special GitHub Actions workflow file, located at `.github/workflows/copilot-setup-steps.yml` within your repository." (ENV)
- "While working on a task, Copilot has access to its own ephemeral development environment, powered by GitHub Actions". "You can use a Copilot setup steps file to deterministically install tools or dependencies before Copilot starts work." "The steps in this job will be executed in GitHub Actions before Copilot starts working." (ENV)
- "Copilot code review also runs in an ephemeral development environment, and you can customize it in the same ways described in this article." (ENV)

### Constraints

| Item | Documented rule | Source |
|---|---|---|
| Job name | "The job MUST be called `copilot-setup-steps` or it will not be picked up by Copilot." | ENV |
| Single job | "A `copilot-setup-steps.yml` file looks like a normal GitHub Actions workflow file, but must contain a single `copilot-setup-steps` job." | ENV |
| Supported job keys | "In your `copilot-setup-steps.yml` file, you can only customize the following settings of the `copilot-setup-steps` job. If you try to customize other settings, your changes will be ignored." List (verbatim): `steps`, `permissions`, `runs-on`, `services`, `snapshot`, `timeout-minutes` (maximum value: `59`). `container` is not in the list. | ENV |
| `on:` triggers | Not stated as required. Page example uses `workflow_dispatch:`, `push:` with `paths: [.github/workflows/copilot-setup-steps.yml]`, `pull_request:` with the same `paths`, with the YAML comment "Automatically run the setup steps when they are changed to allow for easy validation, and allow manual testing through the repository's 'Actions' tab". "Your `copilot-setup-steps.yml` file will automatically be run as a normal GitHub Actions workflow when changes are made, so you can see if it runs successfully." | ENV |
| Default branch | "The `copilot-setup-steps.yml` workflow won't trigger unless it's present on your default branch." "Once you have merged the yml file into your default branch, you can manually run the workflow from the repository's **Actions** tab at any time to check that everything works as expected." | ENV |
| `runs-on` default | Example uses `runs-on: ubuntu-latest`. "By default, Copilot works in a standard GitHub Actions runner." "By default, Copilot uses an Ubuntu Linux-based development environment." | ENV |
| `runs-on` larger runners | "Set the `runs-on` step of the `copilot-setup-steps` job to the label and/or group for the larger runners you want Copilot to use." Example `runs-on: ubuntu-4-core`. | ENV |
| `runs-on` self-hosted | Example `runs-on: arc-scale-set-name` (ARC-managed scale set). "Disable Copilot cloud agent's integrated firewall in your repository settings. The firewall is not compatible with self-hosted runners." Proxy variables for self-hosted: `https_proxy`, `http_proxy`, `no_proxy`, `ssl_cert_file`, `node_extra_ca_certs` — "You can set these environment variables by creating Agents variables or secrets, or by setting them on the runner directly." | ENV |
| OS support | "Copilot cloud agent is only compatible with Ubuntu x64 and Windows 64-bit runners. Runners with macOS or other operating systems are not supported." ARM: NOT ON PAGE. UNVERIFIED (ENV). | ENV |
| Windows | "Copilot cloud agent's integrated firewall is not compatible with Windows, so we recommend that you only use self-hosted runners or larger GitHub-hosted runners with Azure private networking where you can implement your own network controls." Use "the label for your Windows runners" via the self-hosted or larger-runner instructions; no `windows-latest` example on page. | ENV |
| `timeout-minutes` | "`timeout-minutes` (maximum value: `59`)" | ENV |
| `permissions` | "Set the permissions to the lowest permissions possible needed for your steps. Copilot will be given its own token for its operations." "If you want to clone the repository as part of your setup steps, for example to install dependencies, you'll need the `contents: read` permission." "If you don't clone the repository in your setup steps, Copilot will do this for you automatically after the steps complete." | ENV |
| `actions/checkout` `fetch-depth` | "Any value that is set for the `fetch-depth` option of the `actions/checkout` action will be overridden to allow the agent to rollback commits upon request." | ENV |
| Step failure | "If any setup step fails by returning a non-zero exit code, Copilot will skip the remaining setup steps and begin working with the current state of its development environment." | ENV |
| `services`, `snapshot` | Listed as customizable; no further description on page. | ENV |
| Git LFS | Example: `actions/checkout@v6` with `with: lfs: true`. | ENV |

Page example (verbatim):
```yaml
name: "Copilot Setup Steps"

on:
  workflow_dispatch:
  push:
    paths:
      - .github/workflows/copilot-setup-steps.yml
  pull_request:
    paths:
      - .github/workflows/copilot-setup-steps.yml

jobs:
  copilot-setup-steps:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - name: Checkout code
        uses: actions/checkout@v6
      - name: Set up Node.js
        uses: actions/setup-node@v7
        with:
          node-version: "20"
          cache: "npm"
      - name: Install JavaScript dependencies
        run: npm ci
```


## Cross-dialect comparison

| Aspect | Claude `.mcp.json` | VS Code `.vscode/mcp.json` | Copilot CLI | Cloud agent |
|---|---|---|---|---|
| Top-level key | `mcpServers` (CC) | `servers` (+ optional `inputs`, `sandbox`) (VSC) | `mcpServers` in `~/.copilot/mcp-config.json`; project files may also use bare top-level server map (CLI) | `mcpServers` (CA) |
| `type` values | `stdio`, `http`, `sse`, `ws`; `streamable-http` alias for `http` (CC) | `"stdio"`, `"http"`, `"sse"` (VSC) | `"local"`, `"http"` in JSON examples; `--transport` `stdio`/`http`/`sse`; `"stdio"`/`"sse"` as JSON values UNVERIFIED (CLI) | `"local"`, `"stdio"`, `"http"`, `"sse"` (CA) |
| Default type when omitted | stdio ("Claude Code reads an entry with no `type` as a stdio server"); `url` without `type` is a skipped configuration error (CC) | `type` marked required, yet minimal example omits it; default UNVERIFIED (VSC) | UNVERIFIED (CLI) | UNVERIFIED (CA) |
| Variable syntax | `${VAR}`, `${VAR:-default}` in `command`, `args`, `env`, `url`, `headers` (CC) | `${workspaceFolder}`, `${input:<id>}`, `${userHome}` seen on page; full list UNVERIFIED (VSC) | none documented; UNVERIFIED (CLI) | `$VAR`, `${VAR}`, `${VAR:-default}` in all `string`/`string[]` fields except `tools` and `type` (CA) |
| Secret handling | env-var expansion; `headersHelper` command; `oauth` with `--client-secret` prompted, not stored (CC) | `inputs[]` with `password: true`, referenced via `${input:id}`; `envFile` (VSC) | literal values in `env`/`headers` per examples; only `PATH` inherited (CLI) | Agents secrets/variables prefixed `COPILOT_MCP_`; OAuth remote servers not supported (CA) |
| `tools` allowlist support | not a config key on page; UNVERIFIED (CC) | not a config key on page; UNVERIFIED (VSC) | `tools` array, default `*`; `--tools` flag (CLI) | `tools` `string[]`, listed as required; `*` enables all (CA) |
| SSE status | "deprecated. Use HTTP servers instead, where available." (CC) | valid; no deprecation wording; HTTP Stream tried first, falls back to SSE (VSC) | "legacy ... deprecated in the MCP specification but still supported for backwards compatibility." (CLI) | accepted value; no deprecation wording on page (CA) |


### Unresolved items from this group

- Claude Code enterprise/managed scope: file name paths, format and precedence of `managed-mcp.json` (only mentioned in passing) — https://code.claude.com/docs/en/mcp
- Claude Code `alwaysLoad` field type and semantics (only named in the `ws` sentence) — https://code.claude.com/docs/en/mcp
- Claude Code `disabled` per-server key (not on page) — https://code.claude.com/docs/en/mcp
- Claude Code `$VAR` (brace-less) expansion (not on page) — https://code.claude.com/docs/en/mcp
- VS Code default `type` when omitted (table says required; minimal example omits it) — https://code.visualstudio.com/docs/agents/reference/mcp-configuration
- VS Code full predefined-variable list (`${env:...}`, `${config:...}`, `${command:...}`, `${workspaceFolderBasename}`, `${pathSeparator}`) — page defers to /docs/reference/variables-reference — https://code.visualstudio.com/docs/agents/reference/mcp-configuration
- VS Code `gallery`, `version` server keys; `dev.debug` sub-keys; `devcontainer.json` MCP customization; which applications `chat.mcp.discovery.enabled` discovers — https://code.visualstudio.com/docs/agents/reference/mcp-configuration
- Copilot CLI: whether `"stdio"` and `"sse"` are accepted JSON `type` values (page shows only `"local"`, `"http"` in JSON) — https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers
- Copilot CLI: `timeout` as a JSON key (only `--timeout MS` flag documented); `tools` requiredness in JSON; default `type` when omitted; any secret/variable substitution syntax — https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers
- Cloud agent: literal environment name `copilot` (page says "Agents secret or variable" / "your Copilot environment"); default `type` when omitted; organization/enterprise MCP policy — https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/configure-mcp-servers
- Cloud agent: `tools` listed under "Required keys" but the Sentry example omits it — recorded, not resolved — https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/configure-mcp-servers
- Setup steps: ARM runner support; detailed semantics of `services` and `snapshot`; whether any `on:` trigger is mandatory — https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-environment

## Claude Code `marketplace.json` (verified separately)
Source: https://code.claude.com/docs/en/plugin-marketplaces (fetched 2026-09-04). Location `.claude-plugin/marketplace.json`. Required top-level keys: `name` (string, kebab-case, "no spaces, control characters, or bidirectional-formatting characters"; reserved names such as `claude-plugins-official` are refused), `owner` (object with required `name`, optional `email`, `url`), `plugins` (array). Optional: `$schema`, `description`, `version`, `metadata` (`pluginRoot`, `description`, `version`), `allowCrossMarketplaceDependenciesOn`, `renames`. Each `plugins[]` entry requires `name` (kebab-case, unique in the array) and `source`; it may carry any plugin-manifest field plus `strict` (default `true`), `relevance`, `headers`, `headersHelper`. `source` forms: relative path string starting with `./` (or a bare name under `metadata.pluginRoot`); objects with `source` = `github` (`repo`, `ref`, `sha`), `url` (`url`, `ref`, `sha`), `git-subdir` (`url`, `path`, `ref`, `sha`), `npm` (`package`, `version`, `registry`), `archive` (`url`, `sha256`), `command` (`command`, `timeout`, `mode`). The page does not say the entry `name` must equal `plugin.json`'s `name`; with `strict: true` both definitions merge.

## Cross-tool compatibility matrix

| Concern | GH cloud agent | VS Code | Copilot CLI | Claude Code |
|---|---|---|---|---|
| Agent file | `.github/agents/*.agent.md`; `description` required; `tools` list or comma string; `mcp-servers`, `metadata` honoured; `argument-hint`, `handoffs` "not supported" | same file plus `argument-hint`, `handoffs`, `agents`, `hooks`; also reads `.claude/agents` Claude-format files | `.github/agents/NAME.md`; `name`, `description`, `tools`, `mcp-servers`; other keys UNVERIFIED | `.claude/agents/*.md`; `name` and `description` required; `tools` comma string; own key set (`permissionMode`, `skills`, `memory`, ...) |
| Tool names | case-insensitive aliases (`read`, `edit`, `search`, `execute`, `agent`, `web`, `todo`), `<server>/<tool>`, `<server>/*`, `*` | same plus `<group>/<tool>` sub-tools, tool sets, `runSubagent` | UNVERIFIED value list | capitalised names (`Read`, `Bash`), `mcp__server__tool`, `Agent(type)` |
| Skills | `.github/skills`, `.agents/skills`, `.claude/skills`; spec keys plus `allowed-tools: shell`; precedence UNVERIFIED | same directories plus `~/.claude/skills`; honours `argument-hint`, `user-invocable`, `disable-model-invocation`, `context` | same project directories per the plugin reference; first-found-wins across project, personal, plugin | `.claude/skills` and `~/.claude/skills`; 14 extra keys; enterprise beats personal beats project; skill beats command |
| Instructions | `copilot-instructions.md`, `.github/instructions/*.instructions.md` (`applyTo`, `excludeAgent`), `AGENTS.md` nearest-wins | same plus `.claude/rules` with `paths`, `CLAUDE.md`, `AGENTS.md` root (nested experimental) | `copilot-instructions.md`; others UNVERIFIED | `CLAUDE.md` tree with `@imports` (four hops), `.claude/rules` with `paths`; does not read `AGENTS.md` |
| Prompt files | not supported | `.github/prompts/*.prompt.md` with `agent`, `tools`, `model` | not supported | `.claude/commands` and skills instead |
| MCP | repository settings JSON: `mcpServers`, `type` in `local`/`stdio`/`http`/`sse`, `tools` required, `COPILOT_MCP_*` secrets | `.vscode/mcp.json`: `servers`, `inputs`, `type` in `stdio`/`http`/`sse`, `${input:id}` | `~/.copilot/mcp-config.json`, `.mcp.json`, `.github/mcp.json`; `mcpServers` or bare map; `local`/`http` (`sse` legacy); `tools` allowlist | `.mcp.json`: `mcpServers`, `type` in `stdio`/`http`/`sse` (deprecated)/`ws`, `${VAR:-default}`; `url` without `type` is skipped |
| Hooks | not documented | `.github/hooks/*.json`, `.claude/settings.json`, agent `hooks` (preview); 8 events; matchers ignored | not documented | settings files, plugin `hooks/hooks.json`, skill and subagent frontmatter; 33 events; five handler types |
| Environment | `copilot-setup-steps.yml`: single job, six customisable keys, Ubuntu or Windows runners | not applicable | not applicable | not applicable |
| Plugins | not documented | plugin skills shown alongside local ones | `plugin.json` in four lookup paths; first-found-wins for agents and skills, last-wins for MCP | `.claude-plugin/plugin.json` with components at the plugin root; `marketplace.json` with `name`, `owner`, `plugins` |

## Deprecated

| Item | Status | Replacement | Source |
|---|---|---|---|
| `infer` in Copilot agents | GH "Retired", VSC "Deprecated" | `user-invocable`, `disable-model-invocation` | GH-REF, VSC-AGENTS |
| `.chatmode.md` files | "previously known as custom chat modes" | rename to `.agent.md` | VSC-AGENTS |
| `Task` tool name in Claude Code | renamed in v2.1.63, alias kept | `Agent` | SA |
| `permissionMode: manual` | alias | `default` | SA |
| `type: sse` (Claude Code) | "deprecated. Use HTTP servers instead" | `http` | CC MCP |
| `type: sse` (Copilot CLI, MCP spec) | "legacy ... deprecated in the MCP specification but still supported" | `http` | CLI MCP |
| Prompt-file `mode` | no longer on the prompt-files page | `agent` | VSC-PROMPT |
| `.claude/commands/*.md` | "Custom commands have been merged into skills" | `.claude/skills/<name>/SKILL.md` | CC skills |
| `AGENT.md` singular | rename target at agents.md | `AGENTS.md` | AGENTSMD |
| Cursor `.md` rules in `.cursor/rules` | "ignored by the rules system" | `.mdc` | CURSOR |
| PreToolUse hook top-level `decision`/`reason` | deprecated for that event | `hookSpecificOutput.permissionDecision` | HK |
| Copilot `stdio` MCP type in agent `mcp-servers` | not deprecated; mapped to `local` | `local` | GH-REF |

## Unresolved questions

Consolidated from the per-group lists above; the reviewer reports these under "Not checked" rather than inventing rules.

- Copilot precedence when the same skill name exists in `.github/skills`, `.agents/skills` and `.claude/skills` (the CLI plugin reference gives a first-found order for the CLI only); which surface reads `~/.claude/skills`.
- Precedence between repository, organisation and enterprise Copilot agents, and between VS Code workspace, user and organisation agents.
- Whether github.com accepts `NAME.md` agent files without `.agent`, whether the CLI accepts `.agent.md`, and whether github.com or the CLI read `.claude/agents`.
- Whether github.com honours `model` in agent files and what values it accepts; maximum length of a Copilot agent `name` or `description`.
- How github.com and the CLI treat `agents`, `hooks`, `argument-hint` and `handoffs`; `mcp-servers` entry schema on the CLI; `url`, `headers`, `http`, `sse` in agent-level `mcp-servers`.
- Whether Claude Code accepts a YAML list for subagent `tools`, and permission-rule patterns such as `Bash(git:*)` inside subagent `tools`.
- Which hook events subagent frontmatter supports (three listed on the subagent page, "all" on the hooks page).
- Whether `hooks` inside skill frontmatter accepts the full settings-file schema (the linter assumes it does).
- Whether Claude Code errors on unknown keys such as Copilot's `tools` allowlist inside a shared `.mcp.json`; default VS Code `type`; Copilot CLI JSON `type` values beyond `local` and `http`.
- Exact `metadata.github-*` keys written by `gh skill install`; per-agent install directory table.
- Whether `tools` is truly required in cloud-agent MCP entries (the page's own example omits it).
- Prompt-file `mode` key status and the complete prompt-variable list; whether `applyTo` is formally required on github.com.
- Cursor `.cursorrules` support, nested `.cursor/rules`, list-form `globs`.
- Copilot plugin hook format and events; `pluginRoot` semantics on the CLI.

## Sources

Fetched 2026-09-04. The short names match `catalogue.SRC` in `agentlint_lib/catalogue.py` where one exists.

| Short name | URL |
|---|---|
| gh-agent-ref | https://docs.github.com/en/copilot/reference/custom-agents-configuration |
| gh-agent-create | https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/create-custom-agents |
| gh-cli-about-agents | https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents |
| vscode-agents | https://code.visualstudio.com/docs/agent-customization/custom-agents |
| vscode-subagents | https://code.visualstudio.com/docs/agents/run/subagents |
| vscode-hooks | https://code.visualstudio.com/docs/agent-customization/hooks |
| cli-ref | https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference |
| cli-plugins | https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference |
| cli-mcp | https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers |
| skills-spec | https://agentskills.io/specification |
| gh-skills | https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills |
| vscode-skills | https://code.visualstudio.com/docs/copilot/customization/agent-skills |
| gh-skill-publish | https://cli.github.com/manual/gh_skill_publish |
| gh-skill | https://cli.github.com/manual/gh_skill |
| gh-skill-install | https://cli.github.com/manual/gh_skill_install |
| claude-skills | https://code.claude.com/docs/en/skills |
| claude-subagents | https://code.claude.com/docs/en/sub-agents |
| claude-memory | https://code.claude.com/docs/en/memory |
| claude-hooks | https://code.claude.com/docs/en/hooks |
| claude-mcp | https://code.claude.com/docs/en/mcp |
| claude-plugins | https://code.claude.com/docs/en/plugins-reference |
| claude-marketplaces | https://code.claude.com/docs/en/plugin-marketplaces |
| gh-instructions | https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions |
| gh-cheat | https://docs.github.com/en/copilot/reference/customization-cheat-sheet |
| gh-cr-tutorial | https://docs.github.com/en/copilot/tutorials/customize-code-review |
| vscode-instructions | https://code.visualstudio.com/docs/agent-customization/custom-instructions |
| vscode-prompts | https://code.visualstudio.com/docs/agent-customization/prompt-files |
| agents-md | https://agents.md/ |
| cursor-rules | https://cursor.com/docs/context/rules (the old `docs.cursor.com/context/rules` redirects to the docs landing page) |
| vscode-mcp | https://code.visualstudio.com/docs/agents/reference/mcp-configuration |
| gh-mcp | https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/configure-mcp-servers |
| gh-env | https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-environment |
