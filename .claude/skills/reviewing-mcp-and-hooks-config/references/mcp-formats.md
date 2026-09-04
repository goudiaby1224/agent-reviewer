# MCP configuration: the four dialects

Sources (fetched 2026-09-04):
- CC = https://code.claude.com/docs/en/mcp
- VSC = https://code.visualstudio.com/docs/agents/reference/mcp-configuration
- CLI = https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers
- CA = https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/configure-mcp-servers

Quotations are verbatim. `UNVERIFIED` marks facts none of these pages states. Linter rule IDs in brackets.

## Side by side
| Aspect | Claude `.mcp.json` (kind `mcp-claude`) | VS Code `.vscode/mcp.json` (kind `mcp-vscode`) | Copilot CLI (kind `mcp-copilot-cli`) | Cloud agent (kind `mcp-copilot-cloud`) |
|---|---|---|---|---|
| Where | project root `.mcp.json` (project scope); `~/.claude.json` (local and user scopes); enterprise managed configuration | workspace `.vscode/mcp.json` or the user profile `mcp.json` | `~/.copilot/mcp-config.json`; project `.mcp.json` in any directory up to the repository root; `.github/mcp.json`; not `.vscode/mcp.json` | repository Settings, Copilot, MCP servers; not a file in the tree |
| Top-level key | `mcpServers` | `servers`, optional `inputs` and `sandbox` | `mcpServers`; project files may also be "the bare top-level format where each key is an MCP server name" | `mcpServers` |
| `type` values | `stdio`, `http`, `sse`, `ws`; `streamable-http` accepted as an alias of `http` in JSON | `stdio`, `http`, `sse` | `local`, `http` in the JSON examples; the `/mcp add` menu offers Local, STDIO, HTTP, SSE ("Both options work the same way"); `--transport stdio|http|sse` | `local`, `stdio`, `http`, `sse` |
| `type` omitted | "Claude Code reads an entry with no `type` as a stdio server"; a `url`-only entry "is a configuration error" and the server is skipped with `add "type": "http" (or "sse" / "ws")` | table marks `type` required, the minimal example omits it; default UNVERIFIED | UNVERIFIED | UNVERIFIED; `type` is listed under "Required keys" |
| Variables | `${VAR}`, `${VAR:-default}` in `command`, `args`, `env`, `url`, `headers`; an unset variable with no default keeps the literal text and warns in `claude mcp list` | `${input:<id>}`, `${workspaceFolder}`, `${userHome}` seen on the page; the full predefined-variable list is on another page | none documented | `$VAR`, `${VAR}`, `${VAR:-default}` in every string field except `tools` and `type`; "Referenced names must start with `COPILOT_MCP_`" |
| Secrets | variable expansion; `headersHelper` command; `oauth` object with the client secret prompted, never stored | `inputs[]` with `password: true`; `envFile` | literal values in the page examples; only `PATH` is inherited | Agents secrets and variables prefixed `COPILOT_MCP_`; remote servers using OAuth "not currently supported" |
| `tools` allowlist | not documented | not documented | `tools` array, default `*`, or the `--tools` flag | `tools` (string array), listed as required, `*` for all; the page's own Sentry example omits it |
| SSE | "The SSE (Server-Sent Events) transport is deprecated. Use HTTP servers instead, where available." | listed without deprecation wording; "VS Code first tries the HTTP Stream transport and falls back to SSE" | "deprecated in the MCP specification but still supported for backwards compatibility" | accepted, no deprecation wording |
| Precedence | local, project, user, plugin servers, claude.ai connectors; "The entire server entry from that source is used; fields are not merged across scopes" | not stated | files closer to the working directory win; `.mcp.json` beats `.github/mcp.json` in the same directory; project beats `~/.copilot/mcp-config.json` | single configuration |

## Server entry keys the linter recognises
The linter accepts the union of documented keys across dialects (CF014 flags anything else): `type`, `command`, `args`, `env`, `envFile`, `url`, `headers`, `tools`, `cwd`, `dev`, `gallery`, `version`, `timeout`, `oauth`, `headersHelper`, `alwaysLoad`, `sandboxEnabled`.

| Key | Documented by | Notes |
|---|---|---|
| `command`, `args`, `env` | all four | stdio/local servers; CC sets `CLAUDE_PROJECT_DIR` in the server's environment; CLI inherits only `PATH` |
| `url`, `headers` | all four | remote servers; `wss://` for `ws` (CC) |
| `headersHelper` | CC | command whose JSON stdout becomes headers; 10-second limit; dynamic headers override static ones |
| `oauth` | CC (`clientId`, `callbackPort`, `authServerMetadataUrl`, `scopes`), VSC (`clientId`) | |
| `timeout` | CC (milliseconds, values below 1000 ignored); CLI has only a `--timeout MS` flag, JSON key UNVERIFIED | |
| `alwaysLoad` | CC (named for `ws` entries; semantics UNVERIFIED) | |
| `envFile`, `cwd`, `dev`, `sandboxEnabled` | VSC | `dev` has `watch` and `debug` |
| `tools` | CLI, CA | Copilot allowlist; undocumented for Claude Code [CF013] |
| `gallery`, `version` | none of the fetched pages | kept in the accepted set to avoid false positives; UNVERIFIED |

## VS Code `inputs[]` entries (VSC)
| Key | Required | Values |
|---|---|---|
| `type` | yes | `promptString`, `pickString`, `command` |
| `id` | yes | referenced as `${input:<id>}` [CF015 checks the reference exists] |
| `description` | promptString, pickString | prompt text |
| `password` | no | hide typed input, default `false` |
| `default` | no | default value |
| `options` | pickString | array of strings |
| `command`, `args` | command | VS Code command id and its arguments |

## Cloud-agent entry (CA)
- "Required keys for local and remote MCP servers": `tools`, `type` [CF005].
- Local: `command` (required), `args` (required), `env` (optional). Remote: `url` (required), `headers` (optional) [CF012].
- `env` and `headers` values are "A substitution reference to a secret or variable in your Copilot environment, such as `$COPILOT_MCP_API_KEY` or `${COPILOT_MCP_API_KEY}`" or "A literal string value" [CF006, CF016].
- "Copilot cloud agent and Copilot code review only support MCP tools"; no resources or prompts.
- Lint a pasted copy with `agentlint.py --kind mcp-copilot-cloud <file>`.

## Rule mapping
| Finding | Dialects | Documented basis |
|---|---|---|
| CF002 wrong top-level key | all | VSC `servers`; the others `mcpServers`; CLI bare map accepted |
| CF003 `url` without `type` | Claude | CC error text quoted above |
| CF004 / CF022 `sse` | Claude / Copilot | CC deprecation; CLI "legacy" wording; MCP specification |
| CF005 missing `tools` or `type`, bad `type` | cloud agent | CA required keys and value list |
| CF006 literal secret | all | CA and CC recommend references |
| CF011 `${VAR}` without default | Claude, CLI | CC: unexpanded text kept and warned |
| CF012 missing `command` or `url` | all | per-dialect required keys |
| CF013 `tools` in `.mcp.json` | Claude | not documented by CC |
| CF015 undeclared `${input:id}` | VS Code | VSC `inputs` |
| CF016 non-`COPILOT_MCP_` secret | cloud agent | CA naming rule |

## Unresolved
- Claude Code enterprise `managed-mcp.json` paths and precedence; `alwaysLoad` semantics; a `disabled` key.
- VS Code default `type` and the full predefined-variable list.
- Copilot CLI: whether `stdio` and `sse` are valid JSON `type` values; `timeout` and `tools` in JSON; substitution syntax.
- Cloud agent: whether `tools` is truly required given the page's own example without it.
