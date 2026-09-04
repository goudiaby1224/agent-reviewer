---
name: writing-review-findings
description: Formats agent-configuration review findings into the standard report, grouped by severity then file, one finding per root cause, each with rule ID, location, why, fix, source and confidence, plus a mandatory not-checked section. Use when producing the final output of any agent, skill, instruction or MCP configuration review.
metadata:
  version: "1.0.0"
  family: agent-skill-reviewer
---

# Writing review findings

## Overview
Every review of agent configuration files ends in one report with a fixed shape, so that readers can compare runs and tools can parse it. This skill holds that contract: the header, the four sections, the per-finding fields, the severity and confidence taxonomy, and the noise-control rules. The full template with a worked example is in `references/report-template.md`.

The reviewer never edits files. The report describes what is wrong, why it matters, how to fix it and how sure the reviewer is.

## When to use
- Producing the final output of any agent, skill, instruction, prompt, MCP or hooks configuration review.
- Converting raw linter JSON plus manual observations into something a maintainer can act on.
- Deciding where a borderline observation belongs (severity, confidence, or "Not checked").

## Procedure
1. Collect inputs: the linter JSON (`findings`, `summary`, `not_checked`, `yaml_parser`), the manual findings from each reviewing skill, and the cross-file findings.
2. Merge duplicates. Two findings with the same rule ID on the same file and line are one finding; a linter finding and a manual finding describing the same root cause are one finding, keeping the more specific message.
3. Assign severity from the rule catalogue. Do not raise a rule's catalogue severity; lower it only with a stated reason (see false positives).
4. Assign confidence: `high` unless the linter ran with the builtin YAML parser on a nested structure, the check is heuristic, or the finding was produced by hand without the linter (`medium`); `low` only for observations that depend on runtime behaviour the documentation does not settle.
5. Group by severity (Errors, Warnings, Info and portability notes), then by file in path order, then by line.
6. Write each finding as: `- [ID] line N — message`, then indented `Why:` with the source URL, then `Fix:` with the confidence. Whole-file findings say `file` instead of `line N`.
7. Write the "Not checked" section: copy the linter's `not_checked` entries, add anything the review skipped (unfetchable sources, unreadable files, unresolved documentation questions) and why. When nothing was skipped, write `Nothing was skipped.`
8. Fill the header: scope, number of files scanned, linter version and YAML parser (or `manual fallback`), and the three counts. The counts must equal the number of bullets in each section.

## Severity and confidence taxonomy
| Severity | Meaning | Examples |
|---|---|---|
| Error | the file will not load, is silently ignored, or misbehaves in at least one runtime | missing required key, invalid YAML, name differs from directory, dangling `@import` |
| Warning | likely wrong, deprecated, or degrades the agent's behaviour | retired key, unknown tool name, `.chatmode.md`, description without triggers |
| Info | portability note or style; the file works in its own runtime | runtime-specific keys, `sse` transport in Copilot, twin agent defined in both trees |

| Confidence | When |
|---|---|
| high | linter finding with PyYAML, or a manual finding verified by reading the file and the source page |
| medium | builtin YAML parser on nested structures; heuristic checks; auto rules applied by hand |
| low | depends on undocumented runtime behaviour; say what would settle it |

Portability notes (anything whose only consequence is "ignored by the other runtime") never appear under Errors, whatever the linter or a skill table says.

## Noise control
- One finding per root cause. A missing frontmatter block produces one error, not one per missing key.
- Cap identical info-level findings per rule at five per report; add `(+N more)` to the last bullet with the remaining count.
- Do not repeat the linter's message verbatim when a manual observation adds context; extend it.
- Do not include speculative findings. If the reviewer cannot point to a rule ID and a source, it goes under "Not checked" as a question, not as a finding.
- Keep `Fix:` to the concrete change. When the fix is "review manually", say what to look at.

## Common false positives
- Secret-looking placeholders (`REPLACE_ME`, `your-token-here`) flagged as literal secrets: keep the finding, lower to Info, say it is a placeholder.
- A tool name newer than the catalogue: verify against the source URL; if valid, drop the finding and record the catalogue gap under "Not checked".
- Twin agents with identical bodies in `.github/agents` and `.claude/agents`: Info only; the layout is intentional.
- Skills kept outside discovery directories on purpose (templates, fixtures): Info with that context, or excluded from scope up front.

## References
- `references/report-template.md` — the report skeleton and a filled example with one finding per severity.
- Load `linting-agent-config-files` for the meaning of any rule ID.
