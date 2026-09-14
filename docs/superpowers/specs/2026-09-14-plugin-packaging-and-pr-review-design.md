# Plugin packaging and pull-request review: design

Date: 2026-09-14. Extends the design in `2026-09-03-agent-skill-reviewer-design.md`; everything there stays in force unless this document says otherwise.

## 1. Goal

Make the existing `agent-skill-reviewer` installable as a GitHub Copilot CLI plugin and as a Claude Code plugin straight from this repository, without breaking the plain-clone layout, and give it the ability to review a pull request: in Claude Code when handed a PR, on github.com when the Copilot cloud agent is assigned to one, and deterministically in GitHub Actions on every PR that touches agent configuration.

### Non-goals
- No second copy of any agent or skill. The plugin manifests point at the files that already exist.
- No automatic posting. Comments on a PR are opt-in in both the subagent and the workflow.
- No review of code changes. The scope stays agent-configuration files; other files in a PR are ignored except as targets of references.
- No publication to third-party marketplaces; the repository is its own marketplace.

## 2. Approved decisions

| Decision | Choice |
|---|---|
| Layout | Manifests over the existing layout; nothing moves |
| Plugin name | `agent-reviewer` (repository name); Claude Code namespaces skills as `agent-reviewer:<skill>` and the agent as `agent-reviewer:agent-skill-reviewer` |
| Distribution | Copilot: `copilot plugin install goudiaby1224/agent-reviewer`; Claude Code: `/plugin marketplace add goudiaby1224/agent-reviewer` then `/plugin install agent-reviewer@agent-reviewer` |
| PR surfaces | Claude Code given a PR; GitHub Actions workflow; Copilot cloud agent on github.com; opt-in PR comment |
| Posting | Only when explicitly asked (subagent) or when a repository variable is set (workflow); one sticky comment per PR, never a review verdict |

## 3. Repository additions

```
.claude-plugin/
  plugin.json                       Claude Code plugin manifest
  marketplace.json                  one-entry marketplace sourcing ./
.github/plugin/
  plugin.json                       Copilot CLI plugin manifest
.github/workflows/
  agent-config-review.yml           PR check running the linter
.claude/skills/reviewing-pull-requests/
  SKILL.md                          PR procedure for both model-driven runtimes
  references/pr-comment-template.md sticky comment template
tests/
  test_changed_since.py             --changed-since behaviour
  test_report_formats.py            markdown and github formats
```

Modified: `agentlint_lib/{cli,api,discover,report}.py`, `linting-agent-config-files/SKILL.md`, both agent bodies, `writing-review-findings/SKILL.md` (PR header variant), `README.md`, `docs/reference/agent-file-formats.md` (plugin manifest facts already present; add the two paths used here to the Discovery table).

## 4. Plugin manifests

### 4.1 Claude Code, `.claude-plugin/plugin.json`
```json
{
  "name": "agent-reviewer",
  "version": "1.1.0",
  "description": "Reviews AI-agent configuration files (agents, skills, instructions, prompts, MCP, hooks, plugins) with a deterministic linter plus documented manual rules, and returns a findings report without editing anything.",
  "author": {"name": "Noel Goudiaby", "url": "https://github.com/goudiaby1224"},
  "repository": "https://github.com/goudiaby1224/agent-reviewer",
  "license": "MIT",
  "keywords": ["review", "lint", "agents", "skills", "copilot", "claude-code"],
  "agents": "./.claude/agents",
  "skills": "./.claude/skills"
}
```
- Paths start with `./` as the plugins reference requires. `skills` adds to the default `skills/` scan; `agents` replaces the default `agents/`.
- Plugin agents do not support `hooks`, `mcpServers` or `permissionMode`; the twin uses none.
- Open question to settle during implementation: whether a plugin agent's bare `skills:` names resolve to sibling plugin skills. If they do not, the twin's `skills:` entries become `agent-reviewer:linting-agent-config-files` and `agent-reviewer:writing-review-findings` only inside the plugin build, which would force a second copy. The fallback if bare names fail is to drop the `skills:` preload from the twin and rely on the body's "Load the skill" instructions, keeping one file.

### 4.2 Claude Code, `.claude-plugin/marketplace.json`
```json
{
  "name": "agent-reviewer",
  "owner": {"name": "Noel Goudiaby", "url": "https://github.com/goudiaby1224"},
  "metadata": {"description": "Marketplace for the agent-reviewer plugin", "version": "1.0.0"},
  "plugins": [{
    "name": "agent-reviewer",
    "source": "./",
    "description": "Agent and skill configuration reviewer for Copilot and Claude Code",
    "version": "1.1.0"
  }]
}
```
`source: "./"` denotes the marketplace root; `claude plugin validate .` confirms it. If validation rejects `./`, use `"."` with `metadata.pluginRoot` unset, and record which form worked in the README.

### 4.3 Copilot CLI, `.github/plugin/plugin.json`
```json
{
  "name": "agent-reviewer",
  "version": "1.1.0",
  "description": "Reviews AI-agent configuration files (agents, skills, instructions, prompts, MCP, hooks, plugins) with a deterministic linter plus documented manual rules, and returns a findings report without editing anything.",
  "author": {"name": "Noel Goudiaby", "url": "https://github.com/goudiaby1224"},
  "repository": "https://github.com/goudiaby1224/agent-reviewer",
  "license": "MIT",
  "keywords": ["review", "lint", "agents", "skills"],
  "agents": ".github/agents",
  "skills": ".claude/skills"
}
```
- Copilot checks `.github/plugin/plugin.json` before `.claude-plugin/plugin.json`, so each runtime reads its own manifest. Copilot paths need no `./` prefix.
- Copilot dedupes agents by filename-derived id (`agent-skill-reviewer`) and skills by `name`; a project that already has these files keeps its own copies and the plugin's are "silently ignored", which is the intended behaviour for this repository itself.
- No Copilot `marketplace.json`: `copilot plugin install OWNER/REPO` needs none.

### 4.4 Finding the linter after installation
The linting skill's Procedure changes from a repository-relative path to: "Run `python3 <skill-dir>/scripts/agentlint.py`, where `<skill-dir>` is the directory this SKILL.md was loaded from. In Claude Code that is `${CLAUDE_SKILL_DIR}`; in Copilot use the path the skill was read from." The agent bodies drop the literal `.claude/skills/...` path and say "run the linter as the skill describes". The `--root` flag makes the repository root explicit when the linter lives outside it: the agent passes `--root .` from the repository root.

## 5. Linter additions

CLI contract, new items only:
```
[--changed-since REF]   lint only configuration files changed between REF and the working tree
                        (git diff --name-only REF plus untracked files), names still resolve
                        against the whole repository; exit 2 if REF is unknown or not in a git repo
[--format markdown]     now valid for results too: the writing-review-findings report contract
[--format github]       one GitHub Actions workflow command per finding
                        (::error / ::warning / ::notice file=..,line=..,title=ID::message),
                        followed by the text summary line
```
- `--changed-since` and PATH arguments may combine; the result is the intersection. `--exclude` still applies. Deleted files are skipped.
- JSON gains `"scope": {"changed_since": "origin/main", "paths": [...]}` so the report header can say what was reviewed; text output prints `scope=changed-since origin/main` in the header line.
- `report.to_markdown(result)` renders: `# Agent configuration review`, the header line (`Scope`, `Files scanned`, `Linter`), counts, then `## Errors`, `## Warnings`, `## Info and portability notes` grouped by file with `- [ID] line N — message` and an indented `Source:` line, and `## Not checked`. Manual `Why`/`Fix` lines are absent because the linter has no judgement to add; the agent fills them when it produces the final report.
- `report.to_github(result)` renders the annotations. Severity maps error, warning, info to `::error`, `::warning`, `::notice`.
- `--list-rules --format markdown` keeps its meaning (catalogue).

## 6. Agent body changes

Both bodies (still byte-identical) gain one section after Scope:

```
## Pull request mode
When asked to review a pull request, or when you are running on one (a PR number or URL was given,
the current branch has an open PR, or GITHUB_BASE_REF is set), load `reviewing-pull-requests` and
follow it: the scope is the PR's changed configuration files plus the files they reference, the
report header says `Scope: PR #N`, and nothing is posted to the PR unless the request says to post
or comment.
```

Step 1 changes to "run the linter as `linting-agent-config-files` describes" instead of the literal path. The test that every skill directory is named in the body covers the new skill.

## 7. `reviewing-pull-requests` skill

Frontmatter: `name: reviewing-pull-requests`; description in third person with triggers ("Use when asked to review a pull request, when a PR number or URL is given, or when running inside a pull-request check"); `metadata` as the others. Sections follow the shared shape. Procedure:

1. Identify the PR: explicit number or URL; otherwise `gh pr view --json number,baseRefName,headRefName` for the current branch; in Actions, `GITHUB_BASE_REF` and `GITHUB_HEAD_REF`. If none resolves, say so and fall back to a whole-repository review.
2. Get the changed files: `gh pr diff <n> --name-only`, or `git diff --name-only origin/<base>...HEAD`. Keep the agent-configuration files (the linter's discovery patterns); list the rest under "Not checked" as out of scope by count.
3. Make sure the head revision is what is on disk (`gh pr checkout <n>` only if the working tree is clean and the user agreed; otherwise review the current checkout and say which commit).
4. Lint with `--changed-since origin/<base>` (or the PATH list) and `--format json`; run the per-kind and cross-file skills on those files only, but resolve references against the whole repository.
5. Report with `writing-review-findings`; header `Scope: PR #N (<k> configuration files of <m> changed)`.
6. Posting, only when asked: render the report, prefix the hidden marker `<!-- agent-skill-reviewer -->`, and if a comment with that marker exists update it (`gh api` to edit) else `gh pr comment <n> --body-file`. Never `gh pr review --approve` or `--request-changes`.
7. github.com cloud agent: the PR it was assigned to is the scope; the report is the reply; there is no separate posting step.

Rules section: this skill adds no catalogue rules; every finding it reports comes from the per-kind and cross-file skills. Its "Rules" section instead lists the procedure rules as plain bullets (scope is the PR's configuration files plus their references; a finding on a file outside the PR names why it is in scope; nothing is posted unless asked; never a review verdict). The rule-ID families stay `GN`, `AG`, `SK`, `IN`, `CF`, `XF`.

References: `references/pr-comment-template.md` holds the comment skeleton (marker, collapsible details per severity, footer naming the linter version and commit).

## 8. Workflow

`.github/workflows/agent-config-review.yml`:
- `on: pull_request` with `paths` covering the linter's discovery patterns (`.github/agents/**`, `.claude/**`, `**/SKILL.md`, `**/*.agent.md`, `**/*.chatmode.md`, `**/*.instructions.md`, `**/*.prompt.md`, `**/AGENTS.md`, `**/CLAUDE.md`, `.mcp.json`, `.vscode/mcp.json`, `.github/mcp.json`, `.github/workflows/copilot-setup-steps.yml`, `.claude-plugin/**`, `.github/plugin/**`, `.cursor/rules/**`).
- `permissions: contents: read, pull-requests: write` (write only used when commenting).
- Steps: checkout with `fetch-depth: 0`; setup-python 3.12; run the linter with `--changed-since origin/${{ github.base_ref }} --format markdown` into `$GITHUB_STEP_SUMMARY` (ignoring its exit code); run it again with `--format github` so annotations appear and its exit code decides the job result; if `vars.AGENTLINT_PR_COMMENT == 'true'`, post or update the sticky comment with `gh` from the saved markdown, using the same marker as the skill.
- The job fails on exit code 1 (errors) and 2 (linter failure); warnings do not fail it.
- The linter is run from the repository's own copy; a consumer repository that installs the plugin instead of cloning copies this workflow and points it at the installed path or vendors the `scripts/` directory. The README documents both.

## 9. Documentation

README: "Install as a plugin" (both runtimes, commands, what gets namespaced), "Reviewing a pull request" (Claude Code prompt forms, github.com assignment, the workflow, enabling comments), and a note in "Copying into another repository" about the workflow. The spec deltas section of the 2026-09-03 plan gets a pointer to this document.

## 10. Testing

- `tests/test_changed_since.py`: temporary git repository with a committed config file, one modified, one added, one deleted; `--changed-since HEAD` reports only the modified and added files, still resolves a subagent's `skills:` against an unchanged skill, exit 2 on an unknown ref and outside git.
- `tests/test_report_formats.py`: `to_markdown` on the bad fixture contains the four section headings and one bullet per finding; `to_github` emits one command per finding with the right severity keyword; `--format markdown` without `--list-rules` no longer errors.
- `tests/test_agent_files.py`: unchanged assertions plus the new skill being named in the body (existing loop covers it).
- `tests/test_self_review.py`: the manifests and workflow lint clean; expected info set unchanged.
- Verification log entries: `claude plugin validate .`; `copilot plugin install ./` followed by `copilot plugins list --kind skill` and `--kind agent`; a `claude --plugin-dir . -p` run answering whether bare `skills:` names resolve; a dry run of the workflow steps locally (`act` is not required: run the same commands in a shell against a branch).

## 11. Error handling

| Situation | Behaviour |
|---|---|
| `--changed-since` outside a git repository or unknown ref | exit 2 with a one-line message |
| `gh` missing or unauthenticated in PR mode | the skill says so under "Not checked" and falls back to `git diff` against `origin/<base>`; posting is skipped with a message |
| Posting requested but no PR resolved | report printed, posting skipped, reason stated |
| Existing sticky comment cannot be edited | a new comment is posted and the duplicate is mentioned |
| Plugin installed without Python | manual-mode instructions from the linting skill apply unchanged |

## 12. Unresolved questions

- Whether bare `skills:` names in a plugin agent resolve to sibling plugin skills (settled by the verification run; fallback in 4.1).
- Whether Copilot CLI loads a Claude-format agent found through a plugin `agents` path (not relied on: the Copilot manifest points at `.github/agents`).
- Whether `source: "./"` is accepted by `claude plugin validate` (fallback in 4.2).
- Whether github.com's cloud agent exposes the PR's changed-file list to a custom agent beyond the diff in context; the skill instructs the agent to derive scope from the diff it is shown.

## 13. Sources

- https://code.claude.com/docs/en/plugins-reference (manifest keys, `./` paths, plugin agent limits)
- https://code.claude.com/docs/en/plugin-marketplaces (marketplace schema, `source` forms)
- https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference (manifest lookup order, dedupe rules, `agents`/`skills` paths)
- https://code.claude.com/docs/en/skills (`${CLAUDE_SKILL_DIR}`)
- https://cli.github.com/manual/gh_pr_diff, https://cli.github.com/manual/gh_pr_comment, https://cli.github.com/manual/gh_pr_view
- https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/workflow-commands-for-github-actions (annotations, step summary)
