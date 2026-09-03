# agent-skill-reviewer — Design Spec

Date: 2026-09-03
Status: approved design, pending user spec review
Repo: `/Users/noelgoudiaby/SKILL_AND_AGENT_BUILDER` (becomes the reference repository for the reviewer; not yet a git repository)

## 1. Goal

Build a **read-only review agent** plus a **set of skills** that analyse AI-agent configuration files — custom agents, `SKILL.md` skills, instruction files, prompt files, MCP and hooks configuration — and report **syntax errors, spec violations, semantic contradictions, and bugs**, in the manner of a software code review.

The deliverable must be **fully compatible with GitHub Copilot** (Copilot cloud agent on github.com, Copilot CLI, VS Code Copilot Chat) and **also load in Claude Code**, from the same tree, without duplicated skills.

### Non-goals

- Editing or auto-fixing files (findings only; the report may mark a finding `autofix_safe` for a human or another agent).
- Posting PR review comments.
- Executing the reviewed skills or agents.
- Deep validation of Cursor, Codex, Gemini or Windsurf formats beyond the basic discoverability checks listed in the rule catalogue.
- Reviewing application source code (this reviewer only reviews agent-configuration files).

## 2. Approved decisions

| Decision | Choice |
|---|---|
| Runtimes | Copilot-first, Claude-readable (approach A) |
| Review targets | Copilot customization files, Claude Code files, generic agent files (AGENTS.md, MCP, plugin manifests), cross-file consistency |
| Output | Findings report only |
| Mechanics | LLM semantics + deterministic Python lint script (`agentlint.py`) |
| Agent name | `agent-skill-reviewer` |

## 3. Repository layout

```
SKILL_AND_AGENT_BUILDER/
├── .github/
│   ├── agents/
│   │   └── agent-skill-reviewer.agent.md        # Copilot custom agent (cloud agent, CLI, VS Code)
│   └── prompts/
│       └── review-agent-config.prompt.md        # /review-agent-config shortcut (VS Code, CLI)
├── .claude/
│   ├── agents/
│   │   └── agent-skill-reviewer.md              # Claude Code subagent twin, same name, same body
│   └── skills/                                  # ONE skills tree, read by Copilot AND Claude Code
│       ├── linting-agent-config-files/
│       │   ├── SKILL.md
│       │   ├── references/rule-catalogue.md     # every rule ID, severity, source
│       │   └── scripts/agentlint.py             # deterministic engine (stdlib, PyYAML optional)
│       ├── reviewing-agent-definitions/
│       │   ├── SKILL.md
│       │   └── references/{copilot-agent-fields.md, claude-subagent-fields.md, tool-names.md}
│       ├── reviewing-skill-files/
│       │   ├── SKILL.md
│       │   └── references/{skill-spec.md, runtime-extensions.md}
│       ├── reviewing-instruction-files/
│       │   ├── SKILL.md
│       │   └── references/instruction-formats.md
│       ├── reviewing-mcp-and-hooks-config/
│       │   ├── SKILL.md
│       │   └── references/{mcp-formats.md, hooks-and-environment.md}
│       ├── detecting-cross-file-contradictions/
│       │   └── SKILL.md
│       └── writing-review-findings/
│           ├── SKILL.md
│           └── references/report-template.md
├── tests/
│   ├── fixtures/
│   │   ├── good/                                # a valid mini-repo: zero errors/warnings, info findings asserted exactly
│   │   └── bad/                                 # one broken example per rule ID
│   ├── test_agentlint.py                        # unittest: expected rule IDs per fixture
│   ├── test_agent_bodies_in_sync.py             # Copilot and Claude agent bodies identical
│   └── test_self_review.py                      # dogfooding: this repo lints clean
├── docs/superpowers/specs/2026-09-03-agent-skill-reviewer-design.md
└── README.md
```

### Why this layout

- **Copilot discovery.** Copilot custom agents are discovered in `.github/agents/*.agent.md` on every Copilot surface. Copilot reads project skills from `.github/skills/`, `.agents/skills/` and `.claude/skills/` with first-found-wins precedence by name. Placing the skills only in `.claude/skills/` makes them visible to Copilot with no duplicate entries, and to Claude Code natively.
- **Claude Code discovery.** Claude Code reads subagents from `.claude/agents/**/*.md` and skills from `.claude/skills/*/SKILL.md`. It does not read `.github/`.
- **No duplicate agent in VS Code or Copilot CLI.** Both also scan `.claude/agents/` for Claude-format agents, and `.github/agents/` takes precedence over `.claude/agents/` at the same level, so the twin is shadowed rather than duplicated on Copilot surfaces.
- **Copilot code review** only picks up skills from `.github/skills/`. That surface is not a target of this design; the README documents how to add a copy there if a team wants it.

## 4. The agent

### 4.1 Copilot definition — `.github/agents/agent-skill-reviewer.agent.md`

```yaml
---
name: agent-skill-reviewer
description: Reviews AI agent configuration files — custom agents (.agent.md, Claude subagents), SKILL.md skills, copilot-instructions.md, *.instructions.md, *.prompt.md, AGENTS.md, CLAUDE.md, MCP and hooks config — for syntax errors, spec violations, contradictions and bugs, and returns a findings report without editing anything. Use when asked to review, audit, lint, validate or check agents, skills, instructions or prompts.
tools: ['read', 'search', 'execute']
argument-hint: Path, glob or "all" (default: whole repository)
handoffs:
  - label: Apply the safe fixes
    agent: agent
    prompt: Apply only the findings marked autofix_safe in the review above, one file at a time, and show a diff for each.
    send: false
---
```

Field rationale:
- `description` is required by Copilot and drives automatic selection; it states both what and when.
- `tools`: `read` and `search` for inspection, `execute` to run `agentlint.py`. No `edit`: the agent is read-only by construction on every Copilot surface.
- `model` omitted so it inherits the session model (the cloud agent ignores `model` anyway).
- `argument-hint` and `handoffs` are VS Code-only and are documented as ignored on github.com; they are harmless there.
- Nothing deprecated (`infer`, `.chatmode.md`) is used.
- Body limit: 30,000 characters on github.com; the body targets under 12,000.

### 4.2 Claude Code twin — `.claude/agents/agent-skill-reviewer.md`

```yaml
---
name: agent-skill-reviewer
description: Reviews AI agent configuration files (custom agents, SKILL.md skills, copilot-instructions.md, *.instructions.md, *.prompt.md, AGENTS.md, CLAUDE.md, .claude/rules, MCP and hooks config) for syntax errors, spec violations, contradictions and bugs, and returns a findings report without editing anything. Use proactively after any of those files is created or changed, or when asked to review, audit, lint or validate agents, skills, instructions or prompts.
tools: Read, Grep, Glob, Bash(python3:*), Bash(python:*), Bash(ls:*), Bash(find:*), Bash(git diff:*), Bash(git status:*), Bash(git ls-files:*)
model: inherit
skills:
  - linting-agent-config-files
  - writing-review-findings
---
```

Field rationale:
- `tools` is a comma-separated string (Claude format). No Edit/Write: read-only by construction.
- `skills` preloads only the two skills every review needs; the other five are loaded on demand by name.
- `model: inherit` keeps the parent conversation's model.

### 4.3 Shared body (identical in both files, runtime-neutral)

Sections, in order:
1. **Role and hard rules** — reviewer, never editor; every finding cites a rule ID and source; runtime-specific fields are portability notes, not errors; no speculative findings; say what was not checked.
2. **Scope resolution** — argument given: path, glob or "all"; none: whole repository; in a PR context: changed files first, then the files they reference.
3. **Step 1 – Discover and lint** — run `python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py --format json <scope>` from the repository root; if Python is unavailable, use the manual rule tables in each skill and lower confidence.
4. **Step 2 – Semantic review per file kind** — load the matching skill by name (`reviewing-agent-definitions`, `reviewing-skill-files`, `reviewing-instruction-files`, `reviewing-mcp-and-hooks-config`) and apply its manual rules to each file of that kind.
5. **Step 3 – Cross-file analysis** — load `detecting-cross-file-contradictions`; use the linter's collision output plus the manual rules.
6. **Step 4 – Report** — load `writing-review-findings`; emit the report exactly in its contract; end with the "not checked" list.
7. **Noise control** — merge duplicate findings, cap identical info-level findings per rule at five with a count, prefer one finding per root cause.

The bodies contain no `#tool:` references and no `$ARGUMENTS`-style substitutions, so they read identically in both runtimes. A unit test asserts the two bodies are byte-identical below the frontmatter.

### 4.4 Prompt file — `.github/prompts/review-agent-config.prompt.md`

```yaml
---
description: Review the repository's agent, skill, instruction, prompt and MCP configuration files and report findings.
agent: agent-skill-reviewer
argument-hint: Path or glob to review (default: whole repository)
---
Review ${input:scope:all} using the agent-skill-reviewer workflow and return the findings report.
```

## 5. The skills

Common conventions for all seven `SKILL.md` files:
- Frontmatter: `name` (equals directory name, lowercase-hyphen, ≤ 64 chars), `description` (third person, states what the skill does and when to load it, no workflow summary, ≤ 1024 chars), `metadata: { version: "1.0.0", family: agent-skill-reviewer }`. No runtime-specific keys, so each file is clean in both runtimes.
- Body ≤ 500 lines, sections: Overview, When to use, Procedure, Rules (table: ID, severity, auto/manual, check, source), Common false positives, References.
- Supporting material in `references/` (spec digests with source URLs) and `scripts/` (only in the lint skill).
- Cross-references use skill names only (`Load reviewing-skill-files`), never `@` file links.

| Skill | Purpose | Loaded |
|---|---|---|
| `linting-agent-config-files` | How to run `agentlint.py`, read its JSON, and what each rule family means; holds the rule catalogue | always (preloaded in Claude; first step in body) |
| `reviewing-agent-definitions` | Copilot `.agent.md`, Claude subagent `.md`, deprecated `.chatmode.md`; per-runtime field tables; tool-name validity; body quality; portability | when agent files are in scope |
| `reviewing-skill-files` | `SKILL.md` against agentskills.io + Copilot + Claude extensions; name/dir match; description triggering quality; dead references; script hygiene | when skills are in scope |
| `reviewing-instruction-files` | `copilot-instructions.md`, `*.instructions.md` (`applyTo`, `excludeAgent`), `AGENTS.md`, `CLAUDE.md` + `@imports`, `.claude/rules` + `paths`, `*.prompt.md`, `.claude/commands` | when instruction/prompt files are in scope |
| `reviewing-mcp-and-hooks-config` | `.mcp.json`, `.vscode/mcp.json`, Copilot cloud-agent MCP JSON, settings hooks, `copilot-setup-steps.yml`, `plugin.json`, `marketplace.json` | when config files are in scope |
| `detecting-cross-file-contradictions` | Name collisions across discovery dirs, dangling references, contradictory directives, tools-vs-body mismatch, overlapping globs, routing ambiguity | always after per-kind review |
| `writing-review-findings` | The report contract, severity and confidence taxonomy, false-positive discipline | always (preloaded in Claude) |

## 6. Rule catalogue (initial)

Severity: **error** = the file will not load, is ignored, or behaves wrongly; **warning** = likely wrong, deprecated, or contradictory; **info** = style, portability, or an observation for the reader. Tag: **auto** = implemented in `agentlint.py`; **manual** = judged by the model with the skill's guidance. Every rule carries a source URL in `references/rule-catalogue.md`.

### AG — agent definitions
| ID | Sev | Tag | Check |
|---|---|---|---|
| AG001 | error | auto | Frontmatter missing, unterminated, or invalid YAML |
| AG002 | error | auto | Copilot agent missing `description` |
| AG003 | error | auto | Claude subagent missing `name` or `description` |
| AG004 | error | auto | Claude subagent `name` not `^[a-z0-9]+(-[a-z0-9]+)*$` or contains `:` |
| AG005 | warning | auto | `infer` used (retired); suggest `disable-model-invocation` / `user-invocable` |
| AG006 | warning | auto | `.chatmode.md` file (deprecated); rename to `.agent.md` |
| AG007 | warning | auto | Copilot `tools` entry not a known alias, `<server>/<tool>`, `<server>/*`, or `*` (silently ignored) |
| AG008 | error/warning | auto | Claude `tools` entry not a known tool or valid pattern; error if no entry resolves (agent fails to launch) |
| AG009 | error | auto | `agents:` set but `agent` not in `tools` |
| AG010 | error | auto | Body exceeds 30,000 characters |
| AG011 | info | auto | `mcp-servers` / `metadata` present with `target: vscode` (not used in IDEs) |
| AG012 | info | auto | VS Code-only keys (`handoffs`, `argument-hint`, `agents`, `hooks`) present; ignored on github.com |
| AG013 | error | auto | Copilot agent filename has characters outside `. - _ a-z A-Z 0-9` |
| AG014 | warning | auto | `model` value is a Claude alias in a Copilot agent, or a Copilot display name in a Claude subagent |
| AG015 | error | auto | Claude enum fields (`permissionMode`, `memory`, `effort`, `color`, `isolation`) hold an undocumented value |
| AG016 | warning | auto | Empty body |
| AG017 | warning | auto | Unknown frontmatter key for the file's runtime (possible typo) |
| AG018 | warning | manual | Description lacks when-to-use triggers (weak auto-selection) |
| AG019 | warning | manual | Body instructs actions the `tools` list forbids, or claims read-only while `edit`/`Write` is granted |
| AG020 | warning | manual | Body contradicts itself |
| AG021 | info | manual | Body names skills or agents that do not exist in the repository |
| AG022 | warning | auto | `target` not `vscode` or `github-copilot` |

### SK — skill files
| ID | Sev | Tag | Check |
|---|---|---|---|
| SK001 | error | auto | Frontmatter missing or invalid |
| SK002 | error | auto | `name` missing (required by the spec and Copilot) |
| SK003 | error | auto | `name` not `^[a-z0-9]+(-[a-z0-9]+)*$` or longer than 64 |
| SK004 | error | auto | `name` differs from the parent directory name |
| SK005 | error | auto | `description` missing, empty, or longer than 1024 |
| SK006 | warning | auto | Body longer than 500 lines |
| SK007 | error | auto | Relative path or link in the body points to a missing file |
| SK008 | warning | auto | Script in `scripts/` lacks a shebang or the executable bit |
| SK009 | error | auto | `compatibility` longer than 500 characters |
| SK010 | info | auto | Runtime-specific keys present (portability note, listing which runtime ignores them) |
| SK011 | warning | auto | Unknown frontmatter key in every runtime (possible typo, e.g. `allowed_tools`) |
| SK012 | error | auto | File not named exactly `SKILL.md` |
| SK013 | warning | auto | `SKILL.md` outside every documented discovery location |
| SK014 | info | auto | `metadata` value is not a string (e.g. unquoted `version: 1.0`) |
| SK015 | warning | manual | Description gives no when-to-use triggers or is written in first person |
| SK016 | warning | manual | Description summarises the workflow (agents may follow it instead of the body) |
| SK017 | warning | manual | Body contradicts itself or references tools/commands that do not exist |
| SK018 | info | manual | Body duplicates content of another skill instead of cross-referencing it |

### IN — instructions and prompt files
| ID | Sev | Tag | Check |
|---|---|---|---|
| IN001 | error | auto | `*.instructions.md` / `*.prompt.md` frontmatter invalid |
| IN002 | warning | auto | `*.instructions.md` without `applyTo` |
| IN003 | error | auto | `applyTo` not a string of comma-separated globs |
| IN004 | warning | auto | `excludeAgent` not `code-review` or `cloud-agent` |
| IN005 | info | auto | `copilot-instructions.md` longer than two pages (> 8,000 characters) |
| IN006 | error | auto | `*.prompt.md` `agent:` references an agent that does not exist |
| IN007 | error | auto | `CLAUDE.md` `@import` target missing (imports inside code spans are skipped) |
| IN008 | error | auto | `.claude/rules` `paths` is not a YAML list of strings |
| IN009 | info | auto | Nested `AGENTS.md` (VS Code treats as experimental) |
| IN010 | warning | auto | Legacy `AGENT.md` singular filename |
| IN011 | warning | auto | `*.instructions.md` outside `.github/instructions/` (not discovered on github.com) |
| IN012 | info | auto | Frontmatter present in `copilot-instructions.md` (none is documented) |
| IN013 | info | auto | `.cursor/rules/*.md` without `.mdc` extension (ignored by Cursor) |
| IN014 | warning | auto | Unknown frontmatter key in an instruction or prompt file |
| IN015 | warning | manual | Task-specific or one-off instructions in a repository-wide file |
| IN016 | warning | manual | Instruction demands something impossible in the repo (a command, path, or tool that does not exist) |

### CF — MCP, hooks, environment, plugin manifests
| ID | Sev | Tag | Check |
|---|---|---|---|
| CF001 | error | auto | JSON or YAML invalid |
| CF002 | error | auto | `.vscode/mcp.json` uses `mcpServers` (needs `servers`), or `.mcp.json` uses `servers` (needs `mcpServers`) |
| CF003 | error | auto | `.mcp.json` entry has `url` but no `type` (read as stdio, then skipped) |
| CF004 | warning | auto | `type: sse` (deprecated in Claude Code) |
| CF005 | error | auto | Copilot cloud-agent MCP entry missing `tools` or `type`, or `type` not `local`/`stdio`/`http`/`sse` |
| CF006 | error | auto | Literal secret-looking value in `env` or `headers` (should be a variable reference) |
| CF007 | error | auto | Hook event name misspelled, or handler missing `type` / `command` / `url` |
| CF008 | error | auto | `copilot-setup-steps.yml` job not named `copilot-setup-steps`, or uses unsupported job keys |
| CF009 | error | auto | `plugin.json` not at `.claude-plugin/plugin.json`, or component dirs placed inside `.claude-plugin/` |
| CF010 | warning | auto | Hook or MCP command script path missing or not executable |
| CF011 | info | auto | `${VAR}` reference with no default |
| CF012 | error | auto | stdio server missing `command`; http/sse server missing `url` |
| CF013 | info | auto | Copilot-only `tools` allowlist inside a `.mcp.json` shared with Claude Code (behaviour undocumented) |

### XF — cross-file
| ID | Sev | Tag | Check |
|---|---|---|---|
| XF001 | warning | auto | Same skill name in more than one discovery dir (first-found-wins shadowing) |
| XF002 | info | auto | Same agent name in `.github/agents` and `.claude/agents` (states precedence); escalate manually if bodies diverge |
| XF003 | error | auto | Dangling reference: prompt `agent:`, handoff `agent`, skill `agent:`, subagent `skills:` |
| XF004 | error | auto | Subagent `skills:` preloads a skill with `disable-model-invocation: true` |
| XF005 | warning | auto | Skill and `.claude/commands/<name>.md` with the same name (skill wins) |
| XF006 | info | auto | Overlapping `applyTo` / `paths` globs across instruction files (pairs listed for manual review) |
| XF007 | warning | manual | Contradictory directives across files (e.g. "never run tests" vs "always run tests") |
| XF008 | warning | manual | Two skills with near-identical triggers (routing ambiguity) |
| XF009 | warning | manual | Agent body composes skills whose descriptions do not match the claimed purpose |
| XF010 | info | auto | Both `CLAUDE.md` and `AGENTS.md` present and neither imports the other (divergence risk) |

## 7. `agentlint.py` contract

```
python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py [PATH ...]
    [--root DIR]               repository root (default: cwd; git toplevel if inside a repo)
    [--format json|text]       default text; json for the agent
    [--kind KIND]              force a kind for the given paths (e.g. mcp-copilot-cloud for pasted config)
    [--no-collisions]          skip the XF checks
    [--exclude GLOB]           skip matching paths (repeatable; e.g. 'tests/fixtures/**')
    [--min-severity LEVEL]     error|warning|info (default info)
    [--list-rules]             print the catalogue and exit
```

- **Discovery** (when no PATH): via `git ls-files` if available, else `os.walk` skipping `.git`, `node_modules`, `vendor`, `dist`, `build`; `--exclude` globs are applied after discovery. Environment variable `AGENTLINT_YAML=builtin` forces the fallback parser (used by the tests). Patterns: `.github/agents/*.md`, `.claude/agents/**/*.md`, `**/*.agent.md`, `**/*.chatmode.md`, `**/SKILL.md`, `.github/copilot-instructions.md`, `**/*.instructions.md`, `**/*.prompt.md`, `**/AGENTS.md`, `**/AGENT.md`, `**/CLAUDE.md`, `CLAUDE.local.md`, `.claude/rules/**/*.md`, `.claude/commands/**/*.md`, `.mcp.json`, `.vscode/mcp.json`, `.github/mcp.json`, `.claude/settings*.json`, `.claude-plugin/*.json`, `.github/plugin/*.json`, `.github/workflows/copilot-setup-steps.yml`, `.cursor/rules/**`.
- **Kinds**: `copilot-agent`, `claude-subagent`, `chatmode`, `skill`, `copilot-instructions`, `path-instructions`, `prompt-file`, `agents-md`, `claude-md`, `claude-rule`, `claude-command`, `mcp-claude`, `mcp-vscode`, `mcp-copilot-cli`, `mcp-copilot-cloud`, `settings-hooks`, `copilot-setup-steps`, `plugin-manifest`, `marketplace-manifest`, `cursor-rule`. A file under `.github/agents/` is `copilot-agent`; under `.claude/agents/` is `claude-subagent`; a Claude-format file (`name` + comma-string `tools`) found under `.github/agents/` is still linted as `copilot-agent` with a portability note.
- **YAML**: PyYAML when importable; otherwise a bundled parser supporting scalars, quoted strings, flow lists, block lists, one level of nested maps, and block scalars. When the fallback is used, findings that depend on nested structures are emitted with `confidence: medium` and the run header says `yaml_parser: builtin`.
- **Output JSON**:

```json
{
  "agentlint_version": "1.0.0",
  "root": "/abs/path",
  "python": "3.14.6",
  "yaml_parser": "pyyaml",
  "files": [{"path": ".claude/skills/x/SKILL.md", "kind": "skill"}],
  "findings": [{
    "id": "SK004", "severity": "error", "confidence": "high",
    "file": ".claude/skills/x/SKILL.md", "line": 2,
    "message": "name 'y' differs from directory 'x'",
    "runtime": "both", "source": "https://agentskills.io/specification",
    "autofix_safe": true, "suggestion": "set name: x"
  }],
  "summary": {"error": 1, "warning": 0, "info": 0},
  "not_checked": ["Copilot cloud-agent MCP config lives in repository settings, not in the tree"]
}
```

- **Exit codes**: 0 no error-level findings; 1 at least one error; 2 usage or internal failure (traceback to stderr, partial JSON still printed when possible).
- **Text format**: one line per finding `SEV ID file:line message`, followed by the summary.

## 8. Report contract (`writing-review-findings`)

```
# Agent configuration review
Scope: <argument or "whole repository">      Files scanned: N      Linter: agentlint 1.0.0 (pyyaml) | manual fallback
Errors: n   Warnings: n   Info: n

## Errors
### <file>
- [SK004] line 2 — name 'y' differs from directory 'x'
  Why: agentskills.io spec requires the directory name to equal `name`; Copilot and Claude Code key the skill on it.  Source: <url>
  Fix: set `name: x`.  Confidence: high

## Warnings
...
## Info and portability notes
...
## Not checked
- <what the review could not verify and why>
```

Rules for the writer: one finding per root cause; every finding has ID, location, why, fix, confidence; group by severity then file; portability notes never appear under Errors; the "Not checked" section is mandatory even when empty ("Nothing was skipped").

## 9. Error handling

| Situation | Behaviour |
|---|---|
| `python3` missing | Agent reports "manual mode", applies the auto rules by hand from the tables, sets confidence to medium on those findings |
| PyYAML missing | Fallback parser; header says `builtin`; nested-structure findings at medium confidence |
| Binary or unreadable file matched | Skipped with an info line in "Not checked" |
| Very large repository | Agent scopes by argument; the linter still completes because discovery is pattern-based, not full-tree content scanning |
| Rule source page has moved | Rule stays; the catalogue keeps the URL and the fetch date; the reviewer never blocks on network access (no network calls at all) |
| Unresolved spec questions (see §11) | Reported under "Not checked" with the specific question, never as a finding |

## 10. Testing

1. **Unit tests** (`tests/test_agentlint.py`, stdlib `unittest`): for every auto rule there is at least one `bad/` fixture that triggers it and the assertion checks the exact rule ID and file; the `good/` fixture tree (a complete mini-repo with a valid agent pair, three skills, instructions, prompt, `.mcp.json`, `.vscode/mcp.json`, hooks, `copilot-setup-steps.yml`) produces zero errors and zero warnings, and exactly the expected info findings (AG012 for the VS Code-only keys, XF002 for the agent twin). Both YAML paths are tested by running the suite twice, the second time with `AGENTLINT_YAML=builtin`.
2. **Sync test**: the two agent bodies are identical below the frontmatter.
3. **Self-review test**: running the linter on this repository with `--exclude 'tests/fixtures/**'` yields zero errors and zero warnings.
4. **Copilot discovery check** (Copilot CLI 1.0.80 is installed locally): from the repo root, run the CLI in non-interactive mode to list agents and skills and confirm `agent-skill-reviewer` and the seven skills are discovered; record the command and output in the README.
5. **Claude Code behavioural check**: dispatch the reviewer as a Claude Code subagent on `tests/fixtures/bad/` (a) with the skills present and (b) with `.claude/skills` temporarily renamed, and confirm that (a) reports the expected rule IDs with sources while (b) misses or mislabels them. This is the writing-skills RED/GREEN check.
6. **Copilot cloud agent**: cannot be executed locally; compatibility is asserted structurally (every frontmatter key used is documented for github.com, body under the 30,000-character limit, filename charset valid) and by the CLI discovery check, which shares the file format.

## 11. Assumptions and unresolved questions

Assumptions:
- Reviews run from the repository root (all paths in the skills are root-relative).
- Python 3.8+ is available where the reviewer runs (true on GitHub-hosted cloud-agent runners and on this machine); the manual fallback covers the rest.
- The user will decide separately whether to `git init` this folder; the spec and files are written regardless.

Unresolved in the official docs (surfaced by the research pass; the reviewer reports them under "Not checked" rather than inventing rules):
- Maximum length of a Copilot agent `name`/`description`.
- Whether github.com accepts `.github/agents/NAME.md` without the `.agent.md` suffix.
- How the cloud agent treats the VS Code-only `agents` and `hooks` keys.
- Whether Claude Code accepts a YAML list for subagent `tools` (docs say comma-separated string; the twin uses the string form).
- Whether Claude Code errors on unknown keys such as Copilot's `tools` allowlist inside a shared `.mcp.json`.
- Exact `metadata.github-*` keys written by `gh skill install`.

## 12. Sources

Verified against official documentation on 2026-09-02/03: docs.github.com (custom agents reference, cloud-agent skills, custom instructions, MCP, environment), code.visualstudio.com (custom agents, agent skills, custom instructions, prompt files, MCP servers), agentskills.io/specification, code.claude.com (sub-agents, skills, memory, hooks, plugins reference, MCP), agents.md. The full per-field digest with URLs is reproduced in each skill's `references/` folder.
