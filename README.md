# agent-skill-reviewer

A read-only reviewer for AI-agent configuration files that runs as a GitHub Copilot custom agent and as a Claude Code subagent from one shared skills tree. It lints custom agents, `SKILL.md` skills, instruction and prompt files, `AGENTS.md`, `CLAUDE.md`, MCP, hooks and plugin manifests with a deterministic Python linter, then applies documented manual rules and returns a findings report without editing anything.

## Layout

```
.github/
  agents/agent-skill-reviewer.agent.md     Copilot custom agent (github.com, VS Code, Copilot CLI)
  prompts/review-agent-config.prompt.md    /review-agent-config shortcut (VS Code)
.claude/
  agents/agent-skill-reviewer.md           Claude Code subagent twin: same name, identical body
  skills/                                  one skills tree, read by Copilot and Claude Code
    linting-agent-config-files/            how to run the linter; scripts/agentlint.py and agentlint_lib/;
                                           references/rule-catalogue.md (generated)
    reviewing-agent-definitions/           manual AG rules; Copilot and Claude field tables; tool names
    reviewing-skill-files/                 manual SK rules; agentskills.io spec digest; runtime extensions
    reviewing-instruction-files/           manual IN rules; instruction, prompt and memory formats
    reviewing-mcp-and-hooks-config/        CF rules explained; four MCP dialects; hooks, setup steps, plugins
    detecting-cross-file-contradictions/   manual XF rules; discovery precedence; reference resolution
    writing-review-findings/               the report contract and template
docs/reference/agent-file-formats.md       verified format reference built from the official pages
docs/superpowers/                          design spec and implementation plan
tests/                                     unit tests, good and bad fixture repositories
```

Copilot discovers project skills in `.github/skills/`, `.agents/skills/` and `.claude/skills/`; Claude Code reads `.claude/skills/`. Keeping the skills only under `.claude/skills/` makes them visible to both runtimes without duplicates. Copilot surfaces prefer `.github/agents/` over `.claude/agents/`, so the twin agent is shadowed rather than listed twice.

## Using it in Copilot

- github.com cloud agent: assign the `agent-skill-reviewer` agent when creating a task from an issue or pull request. Its `tools` are `read`, `search` and `execute`; it has no `edit` tool, so it cannot modify files.
- VS Code: pick `agent-skill-reviewer` in the agents dropdown, or run `/review-agent-config` and pass a path or glob (default: whole repository). The `Apply the safe fixes` handoff switches to the default agent with a prompt that applies only findings marked `autofix_safe`.
- Copilot CLI: `copilot --agent agent-skill-reviewer`, or `/agent` inside a session.

## Using it in Claude Code

Ask for a review (`Use the agent-skill-reviewer subagent to review .claude/skills`) or let Claude delegate automatically after you create or change an agent, skill, instruction or MCP file. The subagent preloads `linting-agent-config-files` and `writing-review-findings` and loads the other five skills by name as needed. Its `tools` are `Read, Grep, Glob, Bash`; the body forbids editing.

## Install as a plugin

The repository doubles as a plugin for both runtimes; nothing is duplicated, the manifests point at the directories above.

Copilot CLI (manifest `.github/plugin/plugin.json`, marketplace `.github/plugin/marketplace.json`):

```
copilot plugin marketplace add goudiaby1224/agent-reviewer
copilot plugin install agent-reviewer@agent-reviewer
```

`copilot plugin install goudiaby1224/agent-reviewer` also works today, but the CLI warns that direct installs are deprecated in favour of `plugin@marketplace`.

Claude Code (manifest `.claude-plugin/plugin.json`, marketplace `.claude-plugin/marketplace.json`):

```
/plugin marketplace add goudiaby1224/agent-reviewer
/plugin install agent-reviewer@agent-reviewer
```

Both runtimes namespace the plugin's components: the agent is `agent-reviewer:agent-skill-reviewer` in Claude Code and in Copilot CLI (`--agent agent-skill-reviewer` is rejected with `No such agent`), and the Claude Code skills are `/agent-reviewer:linting-agent-config-files` and so on. For local development skip the install in either runtime: `claude --plugin-dir .` and `copilot --plugin-dir <abs-path-to-repo>` load the manifests straight from the working tree. A repository that already contains these files keeps its own copies alongside the namespaced ones.

Manifest notes: Claude Code's `agents` field lists agent files, not directories (`["./.claude/agents/agent-skill-reviewer.md"]`), while its `skills` field accepts the directory; Copilot's fields take directories without a `./` prefix.

`copilot plugin list` names the plugin and its version, not its components; there is no `--kind` flag. To see what a plugin contributes, ask the CLI (`copilot -p "List the custom agents and skills available"`) or try the namespaced agent directly.

## Reviewing a pull request

- Claude Code: `Use the agent-skill-reviewer subagent to review pull request 42` (a URL works too), or just ask for a review on a branch that has an open PR. Add `and post the report as a comment` to have it post; it keeps one sticky comment per PR and never approves or requests changes.
- github.com: assign `agent-skill-reviewer` to the pull request; the report is its reply.
- GitHub Actions: `.github/workflows/agent-config-review.yml` runs the linter with `--changed-since origin/<base>` on every PR that touches agent-configuration files, writes the report to the job summary, annotates the diff, and fails on errors (warnings do not fail it). Set the repository variable `AGENTLINT_PR_COMMENT` to `true` to also post the report as a sticky comment.
- Any shell: `python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py --changed-since origin/main --format markdown`.

## Running the linter alone

```
python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py [PATH ...]
    [--root DIR]                  repository root (default: git toplevel, else cwd)
    [--format text|json|markdown] text by default; json for tooling; markdown only with --list-rules
    [--kind KIND]                 force a kind for the given paths (e.g. mcp-copilot-cloud for pasted config)
    [--no-collisions]             skip the cross-file (XF) checks
    [--exclude GLOB]              skip matching paths (repeatable; e.g. 'tests/fixtures/**')
    [--min-severity LEVEL]        error|warning|info (default info)
    [--list-rules]                print the catalogue and exit
    [--version]
```

Exit code 0 means no error-level findings, 1 at least one error, 2 a usage or internal failure. PATH arguments narrow what is reported, not what names resolve against. Python 3.8 or newer; PyYAML is optional (`AGENTLINT_YAML=builtin` forces the bundled parser). The linter never edits files and never uses the network.

## Copying into another repository

Copy `.github/agents/`, `.github/prompts/`, `.claude/agents/` and `.claude/skills/`. Copilot code review reads skills only from `.github/skills/`; if you want that surface too, copy `.claude/skills/` to `.github/skills/` as well and accept the XF001 note the linter will raise about the duplicate.

Copy `.github/workflows/agent-config-review.yml` as well; it uses the repository's own linter when present and otherwise clones this repository at `PLUGIN_REF` to borrow it.

## Adding a rule

1. Register it in `agentlint_lib/catalogue.py` with an ID in an existing family (`GN`, `AG`, `SK`, `IN`, `CF`, `XF`), a severity, `auto` or `manual`, a runtime and a source URL. IDs are never renumbered.
2. For `auto` rules, implement the check in the matching `rules_*.py` and add a fixture under `tests/fixtures/bad/` that triggers it; `tests/test_good_fixture.py` fails until every `auto` rule has one.
3. Regenerate the catalogue: `python3 .claude/skills/linting-agent-config-files/scripts/agentlint.py --list-rules --format markdown > .claude/skills/linting-agent-config-files/references/rule-catalogue.md`.
4. Add the rule to the Rules table of the reviewing skill that owns the family, with "how to judge" for `manual` rules.
5. Update `docs/reference/agent-file-formats.md` if the rule rests on a fact not yet recorded there.

## Tests

```
python3 -m unittest discover -s tests -v
AGENTLINT_YAML=builtin python3 -m unittest discover -s tests -v
```

The second run exercises the bundled YAML parser. `tests/test_self_review.py` lints this repository itself (fixtures excluded) and requires zero errors and warnings.

## Verification log

### Copilot CLI discovery (2026-09-04, GitHub Copilot CLI 1.0.80)

```
$ copilot -p "List the custom agents and skills available in this repository, names only." --allow-all-tools
**Custom agents:**
- agent-skill-reviewer (`.github/agents/` and `.claude/agents/`)

**Skills** (`.claude/skills/`):
- linting-agent-config-files
- reviewing-agent-definitions
- reviewing-skill-files
- reviewing-instruction-files
- reviewing-mcp-and-hooks-config
- detecting-cross-file-contradictions
- writing-review-findings
```

The agent and all seven skills were found; the CLI excluded `tests/fixtures/` on its own.

### Claude Code behavioural check (2026-09-04, Claude Code 2.1.260)

Not completed. Both non-interactive runs returned the account's usage limit instead of a review:

```
$ claude -p "Use the agent-skill-reviewer subagent to review tests/fixtures/bad and return its report." \
    --allowedTools "Agent,Read,Grep,Glob,Bash(python3:*),Bash(python:*),Bash(ls:*),Bash(find:*),Bash(git ls-files:*)" \
    --output-format text
You've hit your session limit · resets 5:50am (America/Toronto)
```

The skills tree was moved aside for the red run and restored afterwards (`git status` clean). To complete the check after the limit resets, run from the repository root:

```
claude -p "Use the agent-skill-reviewer subagent to review tests/fixtures/bad and return its report." \
    --allowedTools "Agent,Read,Grep,Glob,Bash(python3:*)" --output-format text > /tmp/claude-green.txt
mv .claude/skills /tmp/skills-hidden
claude -p "Use the agent-skill-reviewer subagent to review tests/fixtures/bad and return its report." \
    --allowedTools "Agent,Read,Grep,Glob,Bash(python3:*)" --output-format text > /tmp/claude-red.txt
mv /tmp/skills-hidden .claude/skills
```

Expected: the green run cites rule IDs such as `SK004`, `CF002` and `AG008` with source URLs and ends with a "Not checked" section; the red run reports no rule IDs or invents them. Paste both summaries here.

The subagent is discovered by Claude Code: after the agent file was created, this session's tool list gained an `agent-skill-reviewer` agent type with tools `Read, Grep, Glob, Bash`, and the seven skills appeared as loadable skills.

The green half of this check was completed on 2026-09-18 through the plugin run below; the red run (skills tree moved aside) is still pending.


### Plugin installs (2026-09-18)

- Claude Code 2.1.276, `claude --plugin-dir . -p "Use the agent-reviewer:agent-skill-reviewer subagent to review tests/fixtures/good ..."`: passed. The namespaced subagent resolved, preloaded `linting-agent-config-files` and `writing-review-findings` by their bare names (so no `skills:` fallback is needed inside a plugin), ran the linter, and reported `XF002`, `AG012` and `IN016` with source URLs and a "Not checked" section.
- Copilot CLI 1.0.85, `copilot --plugin-dir <repo> --agent agent-reviewer:agent-skill-reviewer -p "Review tests/fixtures/good ..."`: passed with one caveat. `copilot plugin list` showed `agent-reviewer (v1.1.0)` under "External Plugins"; the agent loaded all seven skills and cited `XF002`, `AG012` and `IN016`. The bare name `agent-skill-reviewer` was rejected (`No such agent ..., available: agent-reviewer:agent-skill-reviewer`), so Copilot namespaces plugin agents just as Claude Code does. Shell execution was denied in that non-interactive run despite `--allow-all-tools`, so the agent fell back to applying the auto rules by hand and marked those findings medium confidence — the fallback path works, but the linter itself was not exercised through the Copilot plugin.

## Unresolved questions

Collected from the official pages on 2026-09-04 (details in `docs/reference/agent-file-formats.md`, "Unresolved questions"). The reviewer reports these under "Not checked" instead of inventing rules.

- Copilot precedence when the same skill name exists in `.github/skills`, `.agents/skills` and `.claude/skills`; the CLI plugin reference gives a first-found order for the CLI only.
- Precedence between repository, organisation and enterprise Copilot agents.
- Whether github.com accepts `NAME.md` agent files without `.agent`, and whether the CLI accepts `.agent.md`.
- Whether github.com honours `model` in agent files; maximum length of a Copilot agent `name` or `description`.
- How github.com and the CLI treat the VS Code-only `agents`, `hooks`, `argument-hint` and `handoffs` keys.
- Whether Claude Code accepts a YAML list for subagent `tools`, and permission-rule patterns such as `Bash(git:*)` inside subagent `tools` (the twin uses plain tool names for that reason).
- Which hook events subagent frontmatter supports, and whether skill-frontmatter `hooks` accept the full settings schema.
- Whether Claude Code errors on unknown keys such as Copilot's `tools` allowlist inside a shared `.mcp.json`.
- Exact `metadata.github-*` keys written by `gh skill install`.
- Whether `tools` is truly required in cloud-agent MCP entries, given the documentation's own example omits it.
