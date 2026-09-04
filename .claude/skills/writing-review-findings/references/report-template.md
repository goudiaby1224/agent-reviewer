# Report template

Source: design spec, section 8 "Report contract". The skeleton below is the contract; the example after it shows one finding per severity.

## Skeleton

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

## Field reference

| Part | Content |
|---|---|
| `Scope` | the argument the reviewer was given, or `whole repository` |
| `Files scanned` | the `files` count from the linter JSON, or the number of files read by hand |
| `Linter` | `agentlint <version> (<yaml_parser>)`, or `manual fallback` when Python was unavailable |
| counts | number of bullets under each of the three finding sections |
| `[ID]` | rule ID from the catalogue; manual rules use their catalogue ID too |
| location | `line N` from the finding, or `file` for whole-file findings |
| `Why:` | one or two sentences on the consequence, then `Source: <url>` from the rule |
| `Fix:` | the concrete change, then `Confidence: high|medium|low` |

## Filled example

```
# Agent configuration review
Scope: .github/agents .claude/skills      Files scanned: 6      Linter: agentlint 1.0.0 (pyyaml)
Errors: 1   Warnings: 1   Info: 1

## Errors
### .claude/skills/deploy-service/SKILL.md
- [SK004] line 2 — name 'deploy' differs from directory 'deploy-service'
  Why: both runtimes key the skill on the directory name; a mismatch makes the skill unreachable by name.  Source: https://agentskills.io/specification
  Fix: set `name: deploy-service`.  Confidence: high

## Warnings
### .github/agents/release-manager.agent.md
- [AG007] line 4 — unrecognised tool name 'shell' in tools (silently ignored)
  Why: Copilot drops unknown tool names without an error, so the agent runs without shell access.  Source: https://docs.github.com/en/copilot/reference/custom-agents-configuration
  Fix: use `execute` (alias `bash`).  Confidence: high

## Info and portability notes
### .claude/skills/deploy-service/SKILL.md
- [SK010] line 6 — Claude Code-only keys ignored by Copilot: disable-model-invocation
  Why: the key is honoured by Claude Code and skipped by Copilot; behaviour differs between runtimes but nothing breaks.  Source: https://code.claude.com/docs/en/skills
  Fix: none required; document the Copilot behaviour if the skill is shared.  Confidence: high

## Not checked
- Copilot cloud-agent MCP configuration lives in repository settings, not in the tree; pass it with --kind mcp-copilot-cloud <file> to lint a pasted copy.
- Maximum length of a Copilot agent name and description is not documented; long values were not flagged.
```

When nothing was skipped:

```
## Not checked
- Nothing was skipped.
```
