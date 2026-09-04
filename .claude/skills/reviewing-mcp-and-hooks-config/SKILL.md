---
name: reviewing-mcp-and-hooks-config
description: Reviews MCP server configuration in its four dialects (Claude Code .mcp.json, VS Code .vscode/mcp.json, Copilot CLI mcp-config.json and the pasted Copilot cloud-agent JSON), Claude Code hooks in settings files and frontmatter, the Copilot copilot-setup-steps.yml environment workflow, and Claude plugin and marketplace manifests, for invalid JSON, wrong top-level keys, missing or deprecated transports, literal secrets, unknown hook events, unsupported workflow keys and misplaced plugin directories. Use when the review scope contains any of those files, or when an MCP server or hook is configured but never starts.
metadata:
  version: "1.0.0"
  family: agent-skill-reviewer
---

# Reviewing MCP and hooks configuration

## Overview
Covers eight linter kinds: `mcp-claude` (`.mcp.json`), `mcp-vscode` (`.vscode/mcp.json`), `mcp-copilot-cli` (`.github/mcp.json` and CLI config), `mcp-copilot-cloud` (pasted JSON, via `--kind`), `settings-hooks` (`.claude/settings*.json`), `copilot-setup-steps` (`.github/workflows/copilot-setup-steps.yml`), `plugin-manifest` (`.claude-plugin/plugin.json`) and `marketplace-manifest` (`.claude-plugin/marketplace.json`). Every rule in this family is automatic (CF001 to CF022); there is nothing to judge by hand except the false positives below and the explanations the report needs. The same hook checks also run on `hooks` blocks inside subagent and skill frontmatter.

## When to use
- Load when the scope contains files of any kind listed above.
- Load when asked why an MCP server does not appear, why a hook never fires, or why the cloud agent's environment setup failed.

## Procedure
1. Take the linter findings for these kinds. For each, use the Rules table to write the "Why" and the fix; the reference files give each dialect's schema.
2. Identify the dialect of each MCP file from its path and top-level key and check the entry against that dialect's column in the comparison table below. A file that mixes dialects (VS Code `inputs` inside `.mcp.json`, Copilot `tools` allowlists in a Claude file) is the usual root cause of several findings at once; report the root cause once.
3. For `.mcp.json` shared between Claude Code and Copilot CLI, state which findings concern which runtime (CF003 and CF004 are Claude; CF013 and CF022 are Copilot-facing).
4. For hooks, confirm each event name and handler against the reference; for `command` handlers with a relative path, the linter already checked the file exists and is executable (CF010).
5. For `copilot-setup-steps.yml`, confirm the single job name, the supported keys and the presence of an `on:` trigger for manual testing.
6. For plugins, confirm the layout: manifests inside `.claude-plugin/`, component directories at the plugin root.
7. If the repository uses the Copilot cloud agent and no MCP JSON was supplied, add to "Not checked" that the cloud-agent MCP configuration lives in repository settings and can be linted from a pasted copy with `--kind mcp-copilot-cloud`.
8. Hand the findings to `writing-review-findings`.

## The four MCP dialects
| Aspect | Claude `.mcp.json` | VS Code `.vscode/mcp.json` | Copilot CLI | Copilot cloud agent (settings) |
|---|---|---|---|---|
| Top-level key | `mcpServers` | `servers` (+ `inputs`) | `mcpServers` | `mcpServers` |
| `type` values | `stdio`, `http`, `sse` (deprecated) | `stdio`, `http`, `sse` | `local`/`stdio`, `http`, `sse` (legacy) | `local`, `stdio`, `http`, `sse` |
| `type` omitted | treated as stdio; a `url`-only entry is skipped (CF003) | inferred from `command` vs `url` | inferred | must be set (CF005) |
| `tools` allowlist | not documented (CF013) | no | yes | required (CF005) |
| Variables | `${VAR}`, `${VAR:-default}` | `${input:id}`, `${env:NAME}`, `${workspaceFolder}` | `${VAR}` | `COPILOT_MCP_*` secrets only (CF016) |
| Secrets | env references | `inputs` with `password: true` | env references | repository secrets named `COPILOT_MCP_*` |

## Rules
| ID | Severity | Tag | Check | What the linter checked | Source |
|---|---|---|---|---|---|
| CF001 | error | auto | JSON or YAML invalid | Parser error reported with position; nothing else is checked for that file | https://code.claude.com/docs/en/mcp |
| CF002 | error | auto | Wrong top-level key | `.vscode/mcp.json` needs `servers`; the other dialects need `mcpServers`; the rename is autofix-safe | https://code.visualstudio.com/docs/agents/reference/mcp-configuration |
| CF003 | error | auto | `.mcp.json` entry with `url` but no `type` | Claude Code reads it as stdio and skips it; suggestion adds `"type": "http"` | https://code.claude.com/docs/en/mcp |
| CF004 | warning | auto | `type: sse` in `.mcp.json` | Deprecated in Claude Code; use `http` | https://code.claude.com/docs/en/mcp |
| CF005 | error | auto | Cloud-agent entry shape | Needs `tools` and a `type` in `local`, `stdio`, `http`, `sse` | https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/configure-mcp-servers |
| CF006 | error | auto | Literal secret-looking value | `env` or `headers` value matching a known token pattern, or a secret-named key with a literal of 8+ characters and no `$` reference | https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/configure-mcp-servers |
| CF007 | error | auto | Hook event or handler invalid | Event not in the documented set, or handler missing `type`, or missing the field its type requires (`command`, `url`, `prompt`) | https://code.claude.com/docs/en/hooks |
| CF008 | error | auto | Setup-steps job | Only a job named `copilot-setup-steps` runs; extra jobs and unsupported job keys are reported | https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-environment |
| CF009 | error | auto | Component directories inside `.claude-plugin/` | `agents/`, `skills/`, `commands/`, `hooks/` must sit at the plugin root | https://code.claude.com/docs/en/plugins-reference |
| CF010 | warning | auto | Script path missing or not executable | Relative `command` paths in MCP entries and hook handlers resolved from the root (or `$CLAUDE_PROJECT_DIR`, `${CLAUDE_PLUGIN_ROOT}` prefixes) | https://code.claude.com/docs/en/hooks |
| CF011 | info | auto | `${VAR}` without a default | The server fails to start when the variable is unset; `${VAR:-default}` avoids that | https://code.claude.com/docs/en/mcp |
| CF012 | error | auto | Transport fields missing | stdio server without `command`; `http`/`sse` server without `url` | https://code.visualstudio.com/docs/agents/reference/mcp-configuration |
| CF013 | info | auto | Copilot `tools` allowlist in `.mcp.json` | Claude Code behaviour for the key is undocumented | https://code.claude.com/docs/en/mcp |
| CF014 | info | auto | Unknown key in a server entry | Not in the union of documented keys across dialects | https://code.claude.com/docs/en/mcp |
| CF015 | error | auto | `${input:id}` not declared | VS Code `inputs` array lacks an entry with that `id` | https://code.visualstudio.com/docs/agents/reference/mcp-configuration |
| CF016 | warning | auto | Cloud-agent secret not `COPILOT_MCP_`-prefixed | Secret-named `env` or `headers` key whose value does not reference a `COPILOT_MCP_` secret | https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/configure-mcp-servers |
| CF017 | info | auto | `once` outside skill frontmatter | Honoured only in skill hooks; ignored in settings and plugin hooks | https://code.claude.com/docs/en/hooks |
| CF018 | warning | auto | `if` on a non-tool event | Only evaluated on `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`; elsewhere the hook never runs | https://code.claude.com/docs/en/hooks |
| CF019 | info | auto | No `on:` in `copilot-setup-steps.yml` | Add `workflow_dispatch` to test the environment manually | https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-environment |
| CF020 | error | auto | Manifest missing `name` | Plugin or marketplace manifest | https://code.claude.com/docs/en/plugins-reference |
| CF021 | error | auto | Marketplace `plugins` entry shape | `plugins` must be a list; each entry needs `name` and `source` | https://code.claude.com/docs/en/plugins-reference |
| CF022 | info | auto | `type: sse` in a Copilot MCP config | Legacy transport in Copilot CLI and the MCP spec; `http` is current | https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers |

## Common false positives
- CF006 on obvious placeholders (`REPLACE_ME`, `your-token-here`, `xxx`): keep the finding, lower to info, say it is a placeholder.
- CF006 on a header value that is a `${...}` reference the pattern did not recognise (a `$(command)` substitution): verify and drop.
- CF010 on a script that is installed by `copilot-setup-steps.yml` or a package manager at runtime: say where it comes from and lower to info.
- CF011 when the variable is documented as always present in the runtime (`CLAUDE_PROJECT_DIR`, `GITHUB_TOKEN` on Actions): info stays info; mention the source.
- CF014 on a key documented by a runtime release newer than the catalogue: verify against the source URL and record the gap under "Not checked".

## References
- `references/mcp-formats.md` — the four dialects side by side with each server key, `type` value and variable syntax.
- `references/hooks-and-environment.md` — hook events and handler schema, `copilot-setup-steps.yml` constraints, plugin and marketplace layout.
- Load `writing-review-findings` for the report format.
