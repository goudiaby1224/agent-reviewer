---
name: linting-agent-config-files
description: Runs the deterministic agentlint linter over AI-agent configuration files (custom agents, SKILL.md skills, instruction and prompt files, AGENTS.md, CLAUDE.md, MCP, hooks and plugin manifests) and explains how to read its JSON output and rule IDs. Use at the start of every agent-configuration review, before any semantic judgement, and whenever a rule ID such as AG007 or SK004 needs its meaning, severity or source.
metadata:
  version: "1.0.0"
  family: agent-skill-reviewer
---

# Linting agent configuration files

## Overview
`scripts/agentlint.py` finds every agent-configuration file under a repository root, classifies it by kind, and applies the automatic (`auto`) rules from `references/rule-catalogue.md`. It never edits files and never touches the network. Manual rules (`manual` tag) are not emitted by the script; the per-kind reviewing skills describe how to judge them.

The linter is pure Python 3.8+ with no required dependencies. PyYAML is used when importable; otherwise a bundled YAML-subset parser takes over and the run header says so.

## When to use
- First step of any review: run the linter, then reason on top of its output.
- To look up what a rule ID means, its severity, which runtime it concerns and the documentation it comes from.
- To lint a pasted config that is not in the tree (for example the cloud-agent MCP JSON) with `--kind`.

## Procedure
1. From the repository root run
   `python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py --format json [PATH ...]`
   With no PATH the linter discovers every configuration file under the root. Add `--exclude 'tests/fixtures/**'` for repositories that ship broken fixtures on purpose.
2. Read the header: `yaml_parser` is `pyyaml` or `builtin`; with `builtin`, treat findings on nested structures as medium confidence.
3. Walk `findings`. Each has `id`, `title`, `severity`, `confidence`, `file`, `line`, `message`, `runtime`, `source`, `autofix_safe`, `suggestion`. `line` is `null` when the finding applies to the whole file.
4. Copy `not_checked` verbatim into the final report.
5. Exit code 1 means at least one error-level finding; 2 means the linter itself failed (traceback on stderr). Report a 2 under "Not checked" and fall back to the manual tables in the reviewing skills.
6. If `python3` is unavailable, apply the `auto` rules by hand from the catalogue and mark every such finding `confidence: medium`.

Useful variants:
- `--min-severity warning` hides info-level portability notes.
- Giving PATH arguments narrows what is reported, not what names resolve against: a prompt's `agent` or a subagent's `skills` are still checked against the whole repository.
- `--no-collisions` skips the cross-file (XF) checks when reviewing a single file in isolation.
- `--kind mcp-copilot-cloud path/to/pasted.json` lints a file the tree does not contain, with the kind forced.
- `--changed-since origin/main` lints only configuration files changed since that git ref (plus untracked files); names still resolve against the whole repository. Use it for pull requests.
- `--format markdown` prints the findings in the report contract of `writing-review-findings` (without the manual Why and Fix judgements); `--format github` prints one GitHub Actions annotation per finding.
- `--list-rules` prints the catalogue as text; `--list-rules --format markdown` regenerates `references/rule-catalogue.md`.

## Reading the output
| Field | Meaning |
|---|---|
| `severity` | `error`: file will not load or misbehaves; `warning`: likely wrong or deprecated; `info`: portability or style |
| `runtime` | `copilot`, `claude`, `both` or `generic` — which runtime the rule concerns |
| `confidence` | `high` by default; lowered to `medium` when the builtin YAML parser was used or the check is heuristic |
| `autofix_safe` | the `suggestion` can be applied mechanically without changing meaning |
| `suggestion` | a concrete replacement or command; empty when the fix needs judgement |
| `source` | the official documentation page the rule was derived from |

The text format (default) prints one line per finding as `SEV ID file:line message`, then a summary line and the not-checked list.

## Rules
The catalogue is grouped into six families. Only `auto` rules are emitted by the script; `manual` rules are judged by the reviewing skills named below.

| Family | Covers | Manual rules judged by |
|---|---|---|
| GN | encoding, byte-order marks, line endings, unreadable files | none |
| AG | Copilot `.agent.md`, Claude subagents, deprecated `.chatmode.md` | reviewing-agent-definitions |
| SK | `SKILL.md` files | reviewing-skill-files |
| IN | instructions, prompts, `AGENTS.md`, `CLAUDE.md`, rules, commands, Cursor rules | reviewing-instruction-files |
| CF | MCP configs, hooks, `copilot-setup-steps.yml`, plugin and marketplace manifests | reviewing-mcp-and-hooks-config |
| XF | name collisions, dangling references, overlapping globs across files | detecting-cross-file-contradictions |

## Common false positives
- `AG007` on a tool name that is valid for a newer runtime version than the catalogue knows — verify against the linked source before reporting.
- `CF006` on placeholder strings such as `REPLACE_ME` — downgrade to info if clearly a placeholder.
- `IN007` on an `@handle` that is prose, not an import — the linter already skips targets without `/` or `.`; anything it still reports should be checked by opening the file.
- `SK013` on a skill kept deliberately outside a discovery directory (for example a template) — report it as info with that context.
- `XF002` when the two agent bodies are identical — this is the intended twin layout; only the "bodies differ" variant needs attention.

## References
- `references/rule-catalogue.md` — generated by `agentlint.py --list-rules --format markdown`; do not edit by hand. A test fails when it drifts from the registry.
- Load `writing-review-findings` for the report format.
