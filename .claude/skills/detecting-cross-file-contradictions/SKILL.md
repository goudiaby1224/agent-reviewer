---
name: detecting-cross-file-contradictions
description: Judges the relationships between agent-configuration files once each file has been reviewed on its own, covering name collisions across discovery directories, dangling references between agents, skills, prompts and commands, contradictory directives, overlapping applyTo and paths globs, and routing ambiguity between skills with near-identical triggers. Use in every review after the per-kind reviewing skills have run, and whenever two or more configuration files are in scope together.
metadata:
  version: "1.0.0"
  family: agent-skill-reviewer
---

# Detecting cross-file contradictions

## Overview
Single-file review cannot see that two skills share a name, that a subagent preloads a skill that does not exist, or that `CLAUDE.md` says "never run tests" while `AGENTS.md` says "always run tests". The linter's XF family resolves names and globs mechanically (XF001 to XF006, XF010). This skill covers those findings plus the three manual rules that need reading and judgement (XF007 to XF009).

## When to use
- Load after `reviewing-agent-definitions`, `reviewing-skill-files`, `reviewing-instruction-files` and `reviewing-mcp-and-hooks-config` have run on the files in scope.
- Load whenever the scope holds two or more configuration files, or one file that references another (a prompt's `agent`, a subagent's `skills`, a `CLAUDE.md` import).
- Linter kinds involved: every kind; the linter runs XF checks over the whole discovered set unless `--no-collisions` was given.

## Procedure
1. Read the linter's XF findings. Each already names both files involved; keep them as-is and add only what the linter cannot know (for example whether two colliding skills are byte-identical copies or divergent forks).
2. Build the reference map from the linter's `files` list: every agent name (frontmatter `name`, or the filename without `.agent.md`, `.chatmode.md` or `.md`), every skill name (frontmatter `name`, or the directory name) and the built-in Copilot agents `agent`, `ask`, `edit` and `plan`. Anything referenced that is not on this map is a dangling reference (XF003 if the linter missed the reference form).
3. Apply XF007: collect directives from every instruction-bearing file in scope (`copilot-instructions.md`, `*.instructions.md`, `AGENTS.md`, `CLAUDE.md`, `.claude/rules`, agent bodies). Pair statements about the same subject (tests, commits, formatting, languages, forbidden commands). Report a contradiction only when both sides are quoted and apply to the same paths or the same runtime.
4. Apply XF008: compare every pair of skill descriptions. Two skills are ambiguous when a plausible user request matches both triggers and the descriptions do not say which one to pick. Compare word by word; shared nouns alone are not enough.
5. Apply XF009: for every agent, list the skills its body names or its `skills` key preloads. Read each skill's description. Report when a preloaded skill's stated purpose has nothing to do with the agent's description, or when the agent's body promises a capability no listed skill provides.
6. Hand every finding to `writing-review-findings`. Cross-file findings are attached to the file that loses (the shadowed skill, the agent with the dangling reference, the later of two contradicting files) and name the other file in the message.

## Discovery precedence
Copilot reads project skills from three directories; its documentation does not say which copy wins when a name repeats, so the linter reports every copy after the first in the order below (`DISCOVERY_ORDER`) and the reviewer asks for one copy to remain. Claude Code reads only `.claude/skills/`.

| Order | Directory | Read by |
|---|---|---|
| 1 | `.github/skills/<name>/SKILL.md` | Copilot (github.com, VS Code, CLI, code review) |
| 2 | `.agents/skills/<name>/SKILL.md` | Copilot (github.com, VS Code, CLI) |
| 3 | `.claude/skills/<name>/SKILL.md` | Copilot (github.com, VS Code, CLI) and Claude Code |

For agents, `.github/agents/` wins over `.claude/agents/` on Copilot surfaces; Claude Code reads only `.claude/agents/`. Identical twins in both trees are the intended layout for a dual-runtime agent (XF002 is info); divergent twins need a manual finding because the two runtimes will behave differently.

## References the linter resolves (XF003)
| Referencing file | Key | Must name |
|---|---|---|
| `*.prompt.md` | `agent` | a built-in agent or a custom agent (also checked as IN006) |
| Copilot `.agent.md` | `handoffs[].agent` | a built-in agent or a custom agent |
| `SKILL.md` | `agent` (Claude-only key) | a Claude subagent or a custom agent |
| Claude subagent | `skills[]` | a skill directory in the tree; XF004 if that skill has `disable-model-invocation: true` |

Body text that names a skill or agent in prose is not resolved by the linter; that is AG021 in `reviewing-agent-definitions`.

## Rules
| ID | Severity | Tag | Check | How to judge (manual) / What the linter checked (auto) | Source |
|---|---|---|---|---|---|
| XF001 | warning | auto | Same skill name in more than one discovery directory | Skill names collected across `.github/skills`, `.agents/skills` and `.claude/skills`; every copy after the first in reporting order is reported with the other path; which copy Copilot loads is undocumented | https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills |
| XF002 | info | auto | Same agent name in `.github/agents` and `.claude/agents` | Reported on the Claude copy; message says "bodies differ" when the two bodies are not identical after trimming | https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference |
| XF003 | error | auto | Dangling reference to an agent or skill | `skills[]`, `handoffs[].agent` and skill `agent` resolved against the tree plus the built-in agents | https://code.claude.com/docs/en/sub-agents |
| XF004 | error | auto | Subagent preloads a skill with `disable-model-invocation: true` | Preloaded skill found, but its frontmatter forbids model invocation | https://code.claude.com/docs/en/sub-agents |
| XF005 | warning | auto | Skill and `.claude/commands` file share a name | Command filename without `.md` equals a skill name; Claude Code resolves the skill | https://code.claude.com/docs/en/skills |
| XF006 | info | auto | Overlapping `applyTo` / `paths` globs | Globs equal, or one of them is `**` or `**/*`; each file pair reported once | https://code.visualstudio.com/docs/agent-customization/custom-instructions |
| XF007 | warning | manual | Contradictory directives across files | Quote both statements with file and line; confirm they apply to the same paths and runtime; a repository-wide rule overridden by a narrower path rule is not a contradiction | https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions |
| XF008 | warning | manual | Two skills with near-identical triggers | Write one request that matches both descriptions; if neither description tells the agent which to choose, report both files and suggest the distinguishing trigger | https://agentskills.io/specification |
| XF009 | warning | manual | Agent composes skills whose descriptions do not match its purpose | Compare the agent description with each preloaded or named skill's description; report mismatches and capabilities the agent promises but no skill covers | https://docs.github.com/en/copilot/reference/custom-agents-configuration |
| XF010 | info | auto | `CLAUDE.md` and `AGENTS.md` coexist without importing each other | Same directory, and `CLAUDE.md` has no `@AGENTS.md` import and `AGENTS.md` does not mention `CLAUDE.md` | https://code.claude.com/docs/en/memory |

## Common false positives
- XF001 when the copies are byte-identical and deliberately mirrored for Copilot code review (which reads only `.github/skills`): keep as info with that context.
- XF006 between a repository-wide `**` file and narrower path files: overlap is expected; report only if the two files disagree.
- XF007 between a general rule and a scoped exception that names its scope ("in `tests/`, skip the linter").
- XF008 between a general skill and a specialised one whose description explicitly says "instead of <general skill> when ...".
- XF010 when the two files serve different tools on purpose and a comment in each says so: info, not warning.

## References
- Load `linting-agent-config-files` for the meaning of any XF rule ID and to rerun the linter on a narrower scope.
- Load `writing-review-findings` for the report format.
