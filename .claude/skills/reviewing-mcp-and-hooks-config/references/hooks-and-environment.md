# Claude Code hooks, Copilot setup steps, plugin and marketplace manifests

Sources (fetched 2026-09-04):
- HK = https://code.claude.com/docs/en/hooks
- SA = https://code.claude.com/docs/en/sub-agents
- PR = https://code.claude.com/docs/en/plugins-reference
- PM = https://code.claude.com/docs/en/plugin-marketplaces
- ENV = https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-environment
- CP = https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference
- VSC-HOOKS = https://code.visualstudio.com/docs/agent-customization/hooks

Quotations are verbatim. `UNVERIFIED` marks facts none of these pages states. Linter rule IDs in brackets.

## Claude Code hooks
### Where they live (HK)
`~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json`, managed policy settings, `<plugin>/hooks/hooks.json` (optional top-level `description`), skill frontmatter, subagent frontmatter. Shape everywhere:

```json
{"hooks": {"<EventName>": [{"matcher": "...", "hooks": [{"type": "command", "command": "..."}]}]}}
```

- Subagent hooks run only while that subagent runs and `Stop` becomes `SubagentStop`; skill hooks register on invocation and stay for the session; "All hook events are supported" in both (HK). SA's subagent table lists only `PreToolUse`, `PostToolUse`, `Stop`; both statements recorded.
- `once`: "Only honored for hooks declared in skill frontmatter; ignored in settings files and agent frontmatter" [CF017].
- Entries merge across settings levels; identical handlers in several settings files run once.

### Events (HK, 33) [CF007 rejects anything else]
| Event | Fires | Matcher |
|---|---|---|
| `SessionStart` | session begins or resumes | `startup`, `resume`, `clear`, `compact`, `fork` |
| `Setup` | `--init-only`, or `--init` / `--maintenance` in `-p` mode | `init`, `maintenance` |
| `UserPromptSubmit` | prompt submitted | none |
| `UserPromptExpansion` | a typed command expands into a prompt | skill or command name |
| `PreToolUse` | before a tool call; can block | tool name |
| `PermissionRequest` | a tool call needs a permission decision | tool name |
| `PermissionDenied` | auto mode denies a tool call | tool name |
| `PostToolUse` | after a tool call succeeds | tool name |
| `PostToolUseFailure` | after a tool call fails | tool name |
| `PostToolBatch` | after a batch of parallel tool calls | none |
| `Notification` | a notification is sent | notification type (`permission_prompt`, `idle_prompt`, ...) |
| `MessageDisplay` | assistant text is displayed | none |
| `SubagentStart` / `SubagentStop` | subagent spawned / finished | agent type |
| `TaskCreated` / `TaskCompleted` | task created / completed | none |
| `Stop` | Claude finishes responding | none |
| `StopFailure` | turn ends on an API error | error type (`rate_limit`, `overloaded`, ...) |
| `TeammateIdle` | a teammate is about to go idle | none |
| `InstructionsLoaded` | a CLAUDE.md or rules file is loaded | `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact` |
| `ConfigChange` | a configuration file changes | `user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills` |
| `CwdChanged` | working directory changes | none |
| `DirectoryAdded` | `/add-dir` or `register_repo_root` | `slash_command`, `register_repo_root` |
| `FileChanged` | a watched file changes | literal filenames |
| `WorktreeCreate` / `WorktreeRemove` | worktree created / removed | none |
| `PreCompact` / `PostCompact` | before / after compaction | `manual`, `auto` |
| `PreModelSwitch` / `PostModelSwitch` | before / after a model switch | canonical model name |
| `Elicitation` / `ElicitationResult` | MCP server requests input / user responds | MCP server name |
| `SessionEnd` | session terminates | `clear`, `resume`, `logout`, `prompt_input_exit`, `other` |

Matcher rules: `*`, empty or omitted match everything; plain names or `|`/`,` lists are exact; anything else is an unanchored JavaScript regular expression (HK). The linter does not validate matcher values.

### Handler fields (HK) [CF007 checks `type` and the field its type requires]
| `type` | Required | Optional |
|---|---|---|
| `command` | `command` | `args` (exec form, no shell), `async`, `asyncRewake`, `shell` (`bash`, `powershell`) |
| `http` | `url` | `headers` (values may use `$VAR` / `${VAR}`), `allowedEnvVars` |
| `mcp_tool` | `server`, `tool` | `input` (values may use `${tool_input.file_path}`-style paths) |
| `prompt` | `prompt` | `model` |
| `agent` | `prompt` | `model` |

Common optional fields: `if` (permission-rule syntax such as `Bash(git *)`; "Only evaluated on tool events: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, and `PermissionDenied`. On other events, a hook with `if` set never runs") [CF018]; `timeout` (seconds; defaults 600 for command/http/mcp_tool, 30 for prompt, 60 for agent); `statusMessage`; `once`.

Path conventions: `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}` are usable in all hook types (HK, PR) [CF010 strips these prefixes before checking that a relative script exists and is executable].

Exit codes: 0 success (stdout parsed as JSON when it is a JSON object); 2 blocking error on the events that can block; other codes are non-blocking errors (HK).

### VS Code hooks (VSC-HOOKS)
Copilot's own hook format lives in `.github/hooks/*.json`, `.claude/settings.json`, `~/.copilot/hooks`, plugin `hooks.json`, and the `hooks` key of a `.agent.md` file (preview, `chat.useCustomAgentHooks`). Events: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PreCompact`, `SubagentStart`, `SubagentStop`, `Stop`. Handler: `type: command`, `command`, `timeout` or `timeoutSec`, `cwd`, `env`, `windows`/`linux`/`osx`. "Matchers are ignored" in VS Code. The linter does not validate Copilot agent `hooks`.

## `.github/workflows/copilot-setup-steps.yml` (ENV)
| Item | Rule | Linter |
|---|---|---|
| Job name | "The job MUST be called `copilot-setup-steps` or it will not be picked up by Copilot." | CF008 (error) |
| Single job | "must contain a single `copilot-setup-steps` job" | CF008 (error, extra jobs listed) |
| Job keys | "you can only customize the following settings ... If you try to customize other settings, your changes will be ignored": `steps`, `permissions`, `runs-on`, `services`, `snapshot`, `timeout-minutes` (maximum `59`) | CF008 (warning for other keys) |
| `on:` | not required; the page example uses `workflow_dispatch`, `push` and `pull_request` filtered to the file's own path so it "can be manually tested" | CF019 (info when absent) |
| Default branch | "won't trigger unless it's present on your default branch" | none |
| Runners | Ubuntu x64 and Windows 64-bit only; larger runners and self-hosted (ARC) supported; firewall incompatible with Windows and self-hosted | none |
| `permissions` | "lowest permissions possible"; `contents: read` to clone in the steps | none |
| `actions/checkout` | `fetch-depth` is overridden | none |
| Step failure | remaining steps skipped, Copilot starts anyway | none |

## Claude Code plugins
### Layout (PR)
"The `.claude-plugin/` directory contains the `plugin.json` file. All other directories (commands/, agents/, skills/, workflows/, output-styles/, themes/, monitors/, hooks/) must be at the plugin root, not inside `.claude-plugin/`." [CF009]. The manifest is optional; without it the plugin name is the directory name. Default component locations: `skills/<name>/SKILL.md` (or a single `SKILL.md` at the plugin root), `commands/`, `agents/`, `workflows/`, `output-styles/`, `themes/`, `hooks/hooks.json`, `.mcp.json`, `.lsp.json`, `monitors/monitors.json`, `bin/`, `settings.json` (`agent` and `subagentStatusLine` only).

### `plugin.json` (PR)
| Key | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | "kebab-case, with no spaces, control characters, or bidirectional-formatting characters" [CF020] |
| `version` | string | no | semantic version; wins over the marketplace entry's version |
| `description`, `displayName`, `author` (`name`, `email`, `url`), `homepage`, `repository`, `license`, `keywords`, `metadata`, `defaultEnabled`, `$schema` | various | no | metadata; `metadata` is free-form and unread |
| `skills`, `commands`, `agents`, `workflows`, `outputStyles`, `hooks`, `mcpServers`, `lspServers`, `experimental.themes`, `experimental.monitors` | string or array (or inline object for hooks, MCP, LSP) | no | "All paths must be relative to the plugin root and start with `./`", except `skills` also accepts `"."` |
| `userConfig`, `channels`, `dependencies` | object / array | no | user options substituted as `${user_config.KEY}`; dependency constraints in semver |

### `marketplace.json` (PM)
Location `.claude-plugin/marketplace.json`. Required top-level keys: `name` (kebab-case, reserved names such as `claude-plugins-official` refused), `owner` (object with required `name`), `plugins` (array) [CF020 checks `name`; `owner` is not checked]. Optional: `$schema`, `description`, `version`, `metadata` (`pluginRoot`, `description`, `version`), `allowCrossMarketplaceDependenciesOn`, `renames`.

Each `plugins[]` entry requires `name` (kebab-case, unique in the array) and `source` [CF021]. `source` forms: a relative path string starting with `./` (or a bare name under `metadata.pluginRoot`); an object with `source` set to `github` (`repo`, optional `ref`, `sha`), `url` (`url`, optional `ref`, `sha`), `git-subdir` (`url`, `path`, optional `ref`, `sha`), `npm` (`package`, optional `version`, `registry`), `archive` (`url`, optional `sha256`) or `command` (`command`, optional `timeout`, `mode`). Entries may carry any plugin-manifest field plus `strict` (default `true`), `relevance`, `headers`, `headersHelper`.

## Copilot CLI plugins (CP)
- Manifest lookup order: `.plugin/plugin.json`, `plugin.json`, `.github/plugin/plugin.json`, `.claude-plugin/plugin.json`. Required `name` (kebab-case, max 64 characters). Component paths `agents`, `skills`, `commands`, `hooks`, `extensions`, `mcpServers`, `lspServers`; paths need no `./` prefix.
- `marketplace.json` lookup order: `marketplace.json`, `.plugin/marketplace.json`, `.github/plugin/marketplace.json`, `.claude-plugin/marketplace.json`. Required `name`, `owner` (`{ name, email? }`), `plugins`; entries require `name` and `source`; `strict` defaults to `true`.
- Precedence: agents and skills "use first-found-wins precedence" and a plugin cannot override project or personal components; "MCP servers use last-wins precedence". Copilot's documented skill order is `<project>/.github/skills/`, `<project>/.agents/skills/`, `<project>/.claude/skills/`, parent directories, `~/.copilot/skills/`, `~/.agents/skills/`, plugin skills.
- Hook file format and events inside a Copilot plugin: UNVERIFIED (CP).

## Unresolved
- Which hook events subagent frontmatter really supports (SA lists three, HK says all).
- Whether plugin `hooks.json` accepts a top-level `description` (HK yes, PR silent).
- Semantics of `services` and `snapshot` in setup steps; ARM runner support.
- Copilot plugin hook format.
