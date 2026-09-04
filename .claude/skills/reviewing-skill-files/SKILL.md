---
name: reviewing-skill-files
description: Reviews SKILL.md skill files against the agentskills.io specification and the GitHub Copilot and Claude Code extensions to it, checking the directory contract, name and description limits, frontmatter keys per runtime, dead links to scripts and references, script hygiene, discovery locations, and the quality of the description as a trigger for automatic selection. Use when the review scope contains any SKILL.md file, a skills directory, or a question about whether a skill will be discovered and selected by Copilot or Claude Code.
metadata:
  version: "1.0.0"
  family: agent-skill-reviewer
---

# Reviewing skill files

## Overview
Covers the linter kind `skill`, which is every `SKILL.md` (and misnamed `skill.md`) in the tree. The linter has already checked the directory contract, `name` and `description` limits, the key set, `compatibility`, `metadata` value types, `allowed-tools` form, body length, dead relative paths, script shebangs and permissions, discovery location and Claude-only keys (SK001 to SK014, SK019). This skill adds the four manual judgements about the description and the body (SK015 to SK018).

## When to use
- Load when the scope contains files of kind `skill`.
- Load when asked whether a skill will be discovered by Copilot (github.com, VS Code, CLI) or Claude Code, or why an agent never selects it.

## Procedure
1. Take the linter findings for kind `skill`. Use the Rules table to explain each and the reference files for the exact limits.
2. Read the description (SK015). It must be third person, state what the skill does and when to load it, and give triggers a model can match against a request.
3. Check the description does not summarise the procedure (SK016). A description that lists the steps invites the agent to follow the summary and skip the body.
4. Read the body (SK017). List every command, script, path and tool it tells the agent to use; confirm each exists in the skill directory or the repository (the linter already resolved backticked `scripts/`, `references/` and `assets/` paths and Markdown links, so focus on prose mentions and commands).
5. Compare the body with the other skills in scope (SK018). Report when a section is a near-copy of another skill instead of a one-line cross-reference by skill name.
6. For Claude-only keys reported as SK010, state what Copilot does without them (for example `disable-model-invocation` is ignored, so Copilot may auto-select the skill).
7. Hand the findings to `writing-review-findings`.

## Rules
| ID | Severity | Tag | Check | How to judge (manual) / What the linter checked (auto) | Source |
|---|---|---|---|---|---|
| SK001 | error | auto | Frontmatter missing or invalid | No `---` block, YAML did not parse, or not a mapping; nothing else is checked for that file | https://agentskills.io/specification |
| SK002 | error | auto | `name` missing | Key absent or empty; suggestion is the directory name | https://agentskills.io/specification |
| SK003 | error | auto | `name` format | 1 to 64 characters matching `^[a-z0-9]+(-[a-z0-9]+)*$` | https://agentskills.io/specification |
| SK004 | error | auto | `name` differs from the directory | Both runtimes key the skill on the directory; the suggestion is the directory name | https://agentskills.io/specification |
| SK005 | error | auto | `description` missing, empty or over 1024 characters | Length measured on the raw string | https://agentskills.io/specification |
| SK006 | warning | auto | Body over 500 lines | Counted below the frontmatter | https://agentskills.io/specification |
| SK007 | error | auto | Dead relative path or link | Markdown link targets and backticked `scripts/`, `references/`, `assets/` paths resolved from the skill directory; `http`, `mailto`, absolute and `~` targets skipped | https://agentskills.io/specification |
| SK008 | warning | auto | Script hygiene | Files in `scripts/` with `.py`, `.sh`, `.bash` or no extension need a `#!` first line and the executable bit | https://agentskills.io/specification |
| SK009 | error | auto | `compatibility` shape | String of at most 500 characters | https://agentskills.io/specification |
| SK010 | info | auto | Keys outside the Agent Skills spec | Claude Code keys (`when_to_use`, `arguments`, `disallowed-tools`, `model`, `effort`, `agent`, `background`, `hooks`, `paths`, `shell`) and the four VS Code also honours (`argument-hint`, `user-invocable`, `disable-model-invocation`, `context`); the message says which runtimes read them | https://code.claude.com/docs/en/skills |
| SK011 | warning | auto | Key unknown to every runtime | Not in the spec set (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`) nor the Claude Code set; usually a typo such as `allowed_tools`, or `once` placed at top level instead of inside `hooks` | https://agentskills.io/specification |
| SK012 | error | auto | File not named `SKILL.md` | Case matters; suggestion is a rename | https://agentskills.io/specification |
| SK013 | warning | auto | Outside a discovery location | Path is not `<root>/skills/<name>/SKILL.md` for any skills root; no runtime finds it | https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference |
| SK014 | info | auto | `metadata` value types | Must map strings to strings; an unquoted `version: 1.0` becomes a float | https://agentskills.io/specification |
| SK015 | warning | manual | Description without triggers or in first person | Report when the description names only a topic ("Helps with deployments"), uses "I" or "you", or lists no situations that should load the skill | https://code.visualstudio.com/docs/copilot/customization/agent-skills |
| SK016 | warning | manual | Description summarises the workflow | Report when the description enumerates the steps of the procedure; the fix is to state purpose and triggers only | https://agentskills.io/specification |
| SK017 | warning | manual | Body contradicts itself or cites missing tools and commands | Quote both sides of a contradiction; for a missing command or file, name it and where it was expected | https://agentskills.io/specification |
| SK018 | info | manual | Body duplicates another skill | Name the other skill and the duplicated section; suggest replacing it with "Load <skill>" | https://agentskills.io/specification |
| SK019 | warning | auto | `allowed-tools` is a YAML list | The spec and `gh skill publish` want a space-separated string; the suggestion joins the entries | https://cli.github.com/manual/gh_skill_publish |

Skill `hooks` frontmatter is validated with the CF007, CF010, CF017 and CF018 checks described in `reviewing-mcp-and-hooks-config`; note that `once` is honoured only here.

## Common false positives
- SK007 on a path that is created at runtime (a generated report under `assets/`): keep the finding but say the file is expected to be generated, and lower to warning.
- SK010 on a skill that lives under `.claude/skills/` and is never read by Copilot in that repository: info stays info; mention the key is harmless there.
- SK013 on templates or fixtures kept out of discovery on purpose: exclude them from scope up front or report as info.
- SK015 on a skill with `disable-model-invocation: true` that is only invoked explicitly: triggers matter less; lower to info.
- SK018 when two skills share a short common preamble (a hard-rules block) that must be visible in each: not duplication.

## References
- `references/skill-spec.md` — agentskills.io fields, limits and the directory contract.
- `references/runtime-extensions.md` — Copilot discovery directories and precedence, `gh skill publish` constraints, Claude-only keys.
- Load `detecting-cross-file-contradictions` for name collisions and routing ambiguity; load `writing-review-findings` for the report format.
