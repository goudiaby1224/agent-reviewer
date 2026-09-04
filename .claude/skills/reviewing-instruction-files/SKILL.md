---
name: reviewing-instruction-files
description: Reviews instruction, prompt and memory files, meaning copilot-instructions.md, path-specific *.instructions.md with applyTo and excludeAgent, *.prompt.md prompt files, AGENTS.md, Claude Code CLAUDE.md with @imports, .claude/rules with paths, legacy .claude/commands and Cursor rules, for invalid frontmatter, undiscoverable locations, dangling imports and agent references, deprecated forms, and content that is task-specific or impossible to follow in the repository. Use when the review scope contains any of those files or when asked why an instruction is not being applied.
metadata:
  version: "1.0.0"
  family: agent-skill-reviewer
---

# Reviewing instruction files

## Overview
Covers eight linter kinds: `copilot-instructions` (`.github/copilot-instructions.md`), `path-instructions` (`*.instructions.md`), `prompt-file` (`*.prompt.md`), `agents-md` (`AGENTS.md`, legacy `AGENT.md`), `claude-md` (`CLAUDE.md`, `CLAUDE.local.md`), `claude-rule` (`.claude/rules/**/*.md`), `claude-command` (`.claude/commands/**/*.md`) and `cursor-rule` (`.cursor/rules/**`). The linter has already checked frontmatter validity and key sets, `applyTo` and `excludeAgent`, prompt `agent` resolution and legacy `mode`, `@import` targets, `paths` shape, discovery locations, empty bodies, length and the deprecated forms (IN001 to IN014, IN017 to IN020). This skill adds the two manual judgements about content (IN015, IN016).

## When to use
- Load when the scope contains files of any kind listed above.
- Load when asked why Copilot or Claude Code is not following an instruction, or whether a prompt file will run.

## Procedure
1. Take the linter findings for these kinds and explain each with the Rules table; the reference file gives the exact frontmatter forms per file type.
2. Read each repository-wide file (`copilot-instructions.md`, root `AGENTS.md`, root `CLAUDE.md`) for IN015. Report instructions that apply to one task, one ticket, one date or one person ("fix the login bug", "until Friday", "ask Sam"); they belong in a prompt file, an issue or a path-specific file.
3. Read every instruction for IN016. List each command, path, tool, script or service the text demands and verify it exists in the repository (use the linter's `files` list, the directory tree and package manifests). Report what does not exist and where the text expects it.
4. For `applyTo` globs, check they match at least one file in the tree; a glob that matches nothing means the instruction never applies (report as IN016).
5. For prompt files, check the body's `${input:...}` variables have a sensible default or are clearly required, and that the body does not restate the target agent's whole workflow.
6. For `CLAUDE.md` and `AGENTS.md` in the same directory, read both and say whether they agree; the linter's XF010 only notes that neither imports the other.
7. Hand the findings to `writing-review-findings`.

## Rules
| ID | Severity | Tag | Check | How to judge (manual) / What the linter checked (auto) | Source |
|---|---|---|---|---|---|
| IN001 | error | auto | Frontmatter invalid | Applies to `*.instructions.md`, `*.prompt.md`, `.claude/rules`, `.claude/commands` and Cursor rules when a block is present but does not parse | https://code.visualstudio.com/docs/agent-customization/custom-instructions |
| IN002 | warning | auto | `*.instructions.md` without `applyTo` | The file is never attached automatically | https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions |
| IN003 | warning | auto | `applyTo` not a string | A YAML list is tolerated by VS Code but the documented form is a comma-separated string; suggestion joins the globs | https://code.visualstudio.com/docs/agent-customization/custom-instructions |
| IN004 | warning | auto | `excludeAgent` value | Must be `code-review` or `cloud-agent` | https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions |
| IN005 | info | auto | Over 1,000 lines | Long files may be partly overlooked | https://docs.github.com/en/copilot/tutorials/customize-code-review |
| IN006 | error | auto | Prompt `agent` does not exist | Neither a built-in (`agent`, `ask`, `edit`, `plan`) nor a custom agent by `name` or filename | https://code.visualstudio.com/docs/agent-customization/prompt-files |
| IN007 | error | auto | `CLAUDE.md` `@import` target missing | Resolved from the file's directory or `~`; imports inside code spans and fences are skipped, as are bare `@handles` without `/` or `.` | https://code.claude.com/docs/en/memory |
| IN008 | error | auto | `.claude/rules` `paths` shape | Must be a YAML list of glob strings | https://code.claude.com/docs/en/memory |
| IN009 | info | auto | Nested `AGENTS.md` | VS Code needs `chat.useNestedAgentsMdFiles` | https://agents.md/ |
| IN010 | warning | auto | Legacy singular `AGENT.md` | Suggestion is a rename | https://agents.md/ |
| IN011 | warning | auto | `*.instructions.md` outside `.github/instructions/` | github.com does not discover it; VS Code may, depending on settings | https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions |
| IN012 | info | auto | Frontmatter in a file with no defined fields | `copilot-instructions.md`, `AGENTS.md`, `CLAUDE.md` | https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions |
| IN013 | info | auto | Cursor rule without `.mdc` | Cursor ignores `.md` rules | https://cursor.com/docs/context/rules |
| IN014 | warning | auto | Unknown frontmatter key | Checked against the per-kind key sets in `references/instruction-formats.md` | https://code.visualstudio.com/docs/agent-customization/prompt-files |
| IN015 | warning | manual | Task-specific content in a repository-wide file | Report sentences tied to one task, ticket, date or person; suggest a prompt file or issue | https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions |
| IN016 | warning | manual | Demands something that does not exist | Name the command, path or tool and where it was expected; include `applyTo` globs that match no file | https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions |
| IN017 | warning | auto | Empty body | Nothing but whitespace below the frontmatter | https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions |
| IN018 | warning | auto | Prompt file uses legacy `mode` | Suggestion rewrites it as `agent` | https://code.visualstudio.com/docs/agent-customization/prompt-files |
| IN019 | warning | auto | Prompt file `tools` not a list | Prompt files take a YAML list | https://code.visualstudio.com/docs/agent-customization/prompt-files |
| IN020 | info | auto | Legacy `.claude/commands` file | Skills are recommended; XF005 fires if a skill shares the name | https://code.claude.com/docs/en/skills |

## Common false positives
- IN007 on an `@` that is an email address or a package scope (`@scope/pkg`) in prose: the linter only skips code spans, so verify and drop.
- IN009 when the team uses nested `AGENTS.md` deliberately and has the VS Code setting on: info stays info.
- IN011 on a VS Code-only workspace that keeps instructions elsewhere on purpose: report as info with the github.com caveat.
- IN015 for a stable convention phrased with a person's name as an example ("ask the owner listed in CODEOWNERS"): not task-specific.
- IN016 for a tool installed by `copilot-setup-steps.yml` or documented in the README as a prerequisite: say where it is provided instead of reporting.

## References
- `references/instruction-formats.md` — every file type, its discovery locations, frontmatter keys and substitution syntax.
- Load `detecting-cross-file-contradictions` for overlapping globs and contradictory directives; load `writing-review-findings` for the report format.
