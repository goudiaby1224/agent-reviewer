---
name: reviewing-agent-definitions
description: Reviews custom agent definition files, meaning GitHub Copilot .agent.md files, Claude Code subagent Markdown files under .claude/agents, and deprecated .chatmode.md files, for invalid frontmatter, unknown or misspelled keys, unrecognised tool names, wrong enum values, portability problems between runtimes, and bodies whose instructions contradict their tools or themselves. Use when the review scope contains any agent, subagent or chatmode file, or when asked whether an agent file is valid for github.com, VS Code, Copilot CLI or Claude Code.
metadata:
  version: "1.0.0"
  family: agent-skill-reviewer
---

# Reviewing agent definitions

## Overview
Covers three linter kinds: `copilot-agent` (`.github/agents/*.agent.md` and any `*.agent.md`), `claude-subagent` (`.claude/agents/**/*.md`) and `chatmode` (`*.chatmode.md`). The linter has already validated frontmatter syntax, required keys, key names per runtime, tool names, enum values, boolean fields, handoff and `mcp-servers` schemas, body length and the VS Code-only and deprecated forms (AG001 to AG017, AG022 to AG028). This skill adds the four manual judgements about the description and the body (AG018 to AG021) and explains each automatic finding so the report can say why it matters.

A file under `.claude/agents/` is always linted as a Claude subagent even with an `.agent.md` suffix; a Claude-format file under `.github/agents/` is linted as a Copilot agent and its Claude-only keys show up as AG017 plus AG024 on the comma-string `tools`.

## When to use
- Load when the scope contains files of kind `copilot-agent`, `claude-subagent` or `chatmode`.
- Load when asked whether an agent will be discovered or behave the same on github.com, in VS Code, in Copilot CLI or in Claude Code.

## Procedure
1. Take the linter findings for these kinds. For each AG finding, use the Rules table below to write the "Why" and the fix; the reference tables give the exact allowed values.
2. Read the description (AG018). It must say what the agent does and when to use it, in third person, with concrete triggers a model can match against a request.
3. Read the body against the `tools` list (AG019). List every action the body asks for (edit, run, commit, browse, delegate) and check each has a tool that permits it; check the reverse for read-only claims.
4. Read the body for internal contradictions (AG020): two instructions that cannot both be followed, a step order that conflicts with a stated hard rule, or a scope statement that excludes the agent's own main task.
5. List every skill and agent the body names in prose (AG021) and check them against the linter's `files` list; the linter only resolves `skills:` and `handoffs`, not prose.
6. For dual-runtime twins (same name in both trees), compare the two bodies; if they differ, say how, on top of the linter's XF002 note.
7. Hand the findings to `writing-review-findings`.

## Rules
| ID | Severity | Tag | Check | How to judge (manual) / What the linter checked (auto) | Source |
|---|---|---|---|---|---|
| AG001 | error | auto | Frontmatter missing, unterminated or invalid YAML | No `---` block, or the YAML did not parse, or it is not a mapping; nothing else is checked for that file | https://docs.github.com/en/copilot/reference/custom-agents-configuration |
| AG002 | error | auto | Copilot agent missing `description` | Key absent or empty string | https://docs.github.com/en/copilot/reference/custom-agents-configuration |
| AG003 | error | auto | Claude subagent missing `name` or `description` | Either key absent or empty | https://code.claude.com/docs/en/sub-agents |
| AG004 | error | auto | Claude subagent `name` format | Must match `^[a-z0-9]+(-[a-z0-9]+)*$`; a colon or uppercase fails | https://code.claude.com/docs/en/sub-agents |
| AG005 | warning | auto | Retired key `infer` | Suggests `disable-model-invocation` / `user-invocable` | https://docs.github.com/en/copilot/reference/custom-agents-configuration |
| AG006 | warning | auto | Deprecated `.chatmode.md` | Fix is a rename to `.agent.md`; the rest of the file is checked as a Copilot agent | https://code.visualstudio.com/docs/agent-customization/custom-agents |
| AG007 | warning | auto | Unrecognised Copilot tool name | Entry is not a documented alias (case-insensitive), `<server>/<tool>`, `<server>/*` or `*`; Copilot ignores it silently | https://docs.github.com/en/copilot/reference/custom-agents-configuration |
| AG008 | error or warning | auto | Unknown Claude tool | Entry is not a built-in tool, `Tool(pattern)` rule or `mcp__server__tool`; error when no entry resolves (the subagent cannot launch), warning otherwise; a lowercase Copilot alias gets a specific hint | https://code.claude.com/docs/en/sub-agents |
| AG009 | error | auto | `agents` set without the `agent` tool | `tools` lacks `agent`, `custom-agent` or `*` | https://code.visualstudio.com/docs/agents/run/subagents |
| AG010 | error | auto | Body over 30,000 characters | Measured on the body below the frontmatter | https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/create-custom-agents |
| AG011 | info | auto | `mcp-servers` or `metadata` with `target: vscode` | These keys are only used by the cloud agent | https://docs.github.com/en/copilot/reference/custom-agents-configuration |
| AG012 | info | auto | VS Code-only keys present | `handoffs`, `argument-hint`, `agents`, `hooks` without `target: vscode`; ignored on github.com, harmless | https://docs.github.com/en/copilot/reference/custom-agents-configuration |
| AG013 | error | auto | Copilot agent filename characters | Only `. - _ a-z A-Z 0-9` are allowed | https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/create-custom-agents |
| AG014 | warning | auto | `model` belongs to the other runtime | Claude alias (`sonnet`, `opus`, `haiku`, `inherit`) in a Copilot agent, or a display name with spaces or a `gpt`/`gemini`/`grok`/`o<n>` prefix in a Claude subagent | https://docs.github.com/en/copilot/reference/custom-agents-configuration |
| AG015 | error | auto | Undocumented Claude enum value | `permissionMode`, `memory`, `effort`, `color`, `isolation` checked against the documented sets in `references/claude-subagent-fields.md` | https://code.claude.com/docs/en/sub-agents |
| AG016 | warning | auto | Empty body | Nothing but whitespace after the frontmatter | https://docs.github.com/en/copilot/reference/custom-agents-configuration |
| AG017 | warning | auto | Unknown key for this runtime | Key not in the Copilot or Claude key set for the file's kind; usually a typo or a key from the other runtime | https://docs.github.com/en/copilot/reference/custom-agents-configuration |
| AG018 | warning | manual | Description gives no when-to-use triggers | Ask "would a model pick this agent from the description alone for a matching request?"; report when the description only names a role, is first person, or lists no situations | https://code.claude.com/docs/en/sub-agents |
| AG019 | warning | manual | Body vs `tools` contradiction | Body tells the agent to edit, write, commit or run commands with no `edit`/`Write`/`Edit`/`execute`/`Bash` tool, or claims to be read-only while such a tool is granted; quote the sentence and the tools line | https://docs.github.com/en/copilot/reference/custom-agents-configuration |
| AG020 | warning | manual | Body contradicts itself | Two instructions that cannot both hold; quote both with line numbers | https://docs.github.com/en/copilot/reference/custom-agents-configuration |
| AG021 | info | manual | Body names non-existent skills or agents | Check every skill or agent named in prose against the linter's `files` list; the `skills:` key is already covered by XF003 | https://docs.github.com/en/copilot/reference/custom-agents-configuration |
| AG022 | warning | auto | `target` value | Must be `vscode` or `github-copilot` | https://docs.github.com/en/copilot/reference/custom-agents-configuration |
| AG023 | info | auto | Claude `tools` as a YAML list | Docs specify a comma-separated string; the suggestion joins the entries | https://code.visualstudio.com/docs/agent-customization/custom-agents |
| AG024 | info | auto | Copilot `tools` as a comma-separated string | github.com documents both forms; VS Code documents a list; the suggestion rewrites it as a list. A value that is neither string nor list is a warning | https://docs.github.com/en/copilot/reference/custom-agents-configuration |
| AG025 | error | auto | `handoffs` entry shape | Must be a list; each entry needs `label` and `agent` | https://code.visualstudio.com/docs/agent-customization/custom-agents |
| AG026 | warning | auto | Boolean field not boolean | `user-invocable`, `disable-model-invocation` (Copilot) and `background` (Claude) | https://docs.github.com/en/copilot/reference/custom-agents-configuration |
| AG027 | error | auto | Claude `skills` shape | Must be a YAML list of strings | https://code.claude.com/docs/en/sub-agents |
| AG028 | error | auto | `mcp-servers` entry shape | Mapping of name to config; each needs `tools` and a `type` in `local`, `stdio`, `http`, `sse` | https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/configure-mcp-servers |

Claude `hooks` inside subagent frontmatter are validated with the CF007, CF010, CF017 and CF018 checks described in `reviewing-mcp-and-hooks-config`.

## Common false positives
- AG007 on a tool name added by a newer runtime release: check the source page; if documented, drop the finding and note the catalogue gap under "Not checked".
- AG012 on a file that is only ever used in VS Code: keep as info; the message already says the keys are ignored elsewhere, not broken.
- AG014 when a Copilot agent uses a full model id that happens to start with a Claude vendor prefix: the linter only flags the four aliases, so verify before reporting anything further.
- AG019 when the body says "do not edit" and `tools` grants `edit` for a narrow explicit purpose the body also states: no contradiction.
- AG021 for skills that live in a user-level directory (`~/.claude/skills`, `~/.copilot/skills`) rather than the repository: say so and lower to info.

## References
- `references/copilot-agent-fields.md` — every Copilot frontmatter key, type, surface and limit.
- `references/claude-subagent-fields.md` — every Claude subagent key and the enum values the linter enforces.
- `references/tool-names.md` — Copilot tool aliases, Claude tool names, and the pattern forms both accept.
- Load `detecting-cross-file-contradictions` for twins, handoffs and preloaded skills; load `writing-review-findings` for the report format.
