# Sticky PR comment template

The first line is the marker the reviewer and the workflow search for; keep it exactly.

```
<!-- agent-skill-reviewer -->
## Agent configuration review
Scope: PR #<n> (<k> configuration files of <m> changed)   Commit: <short sha>   Linter: agentlint <version> (<parser>)
Errors: <e>   Warnings: <w>   Info: <i>

<details><summary>Errors (<e>)</summary>

### <file>
- [ID] line N — message
  Why: ...  Source: <url>
  Fix: ...  Confidence: high

</details>
<details><summary>Warnings (<w>)</summary>

...

</details>
<details><summary>Info and portability notes (<i>)</summary>

...

</details>

**Not checked**
- <out-of-scope file count> changed files outside the agent-configuration set
- <anything else skipped>

<sub>Posted by agent-skill-reviewer; one comment per pull request, updated on each run.</sub>
```

Empty sections say `- none` inside the details block. The workflow (`.github/workflows/agent-config-review.yml`) posts the linter's `--format markdown` output under the same marker, without the Why and Fix lines.
