---
name: reviewing-pull-requests
description: Scopes an agent-configuration review to a pull request, resolving the PR from an argument, the current branch or GitHub Actions variables, collecting its changed configuration files with gh or git, linting them with --changed-since, reviewing them with the per-kind and cross-file skills, and optionally posting the report as one sticky PR comment. Use when asked to review a pull request, when a PR number or URL is given, or when running inside a pull-request check.
metadata:
  version: "1.0.0"
  family: agent-skill-reviewer
---

# Reviewing pull requests

## Overview
A pull-request review is an ordinary review with a narrower scope: the configuration files the PR changes, plus the files they reference. The per-kind skills and `detecting-cross-file-contradictions` do the judging; this skill fixes how the scope is found, how the head revision is obtained, what the report header says, and when a comment may be posted. The linter's `--changed-since REF` flag does the file selection deterministically.

## When to use
- Asked to review a pull request, or given a PR number or URL.
- Running on a branch that has an open pull request, or inside GitHub Actions on a `pull_request` event.
- On github.com, when the Copilot cloud agent is assigned to or mentioned on a pull request.

## Procedure
1. Identify the PR. An explicit number or URL wins. Otherwise run `gh pr view --json number,baseRefName,headRefName,headRefOid` for the current branch. In GitHub Actions use `GITHUB_BASE_REF` and `GITHUB_HEAD_REF`. If nothing resolves, say so and review the whole repository instead.
2. Collect the changed files: `gh pr diff <n> --name-only`, or `git diff --name-only origin/<base>...HEAD`. Keep the agent-configuration files; count the rest and list them under "Not checked" as out of scope.
3. Review the revision that is on disk. Run `gh pr checkout <n>` only when the working tree is clean and the user asked for it; otherwise state which commit was reviewed (`git rev-parse --short HEAD`).
4. Lint with `--changed-since origin/<base> --format json` from the repository root (add `--exclude 'tests/fixtures/**'` when the repository ships broken fixtures on purpose). The linter resolves names against the whole repository even though it reports only the changed files.
5. Apply the per-kind skills and `detecting-cross-file-contradictions` to the changed files only. A finding on a file outside the PR is allowed only when that file is referenced by a changed file, and the finding must say so.
6. Write the report with `writing-review-findings`. The header reads `Scope: PR #<n> (<k> configuration files of <m> changed)`; the "Not checked" section names the out-of-scope files by count and the reviewed commit.
7. Post only when the request says to post or comment. Render the report from `references/pr-comment-template.md`, then: find an existing comment carrying `<!-- agent-skill-reviewer -->` with `gh api repos/{owner}/{repo}/issues/<n>/comments --paginate --jq '.[] | select(.body | startswith("<!-- agent-skill-reviewer -->")) | .id'`; if one exists, update it with `gh api -X PATCH repos/{owner}/{repo}/issues/comments/<id> -F body=@report.md`; otherwise `gh pr comment <n> --body-file report.md`. Never `gh pr review --approve` or `--request-changes`.
8. On github.com as the Copilot cloud agent: the pull request you were assigned to is the scope, its diff is the changed-file list, and the report is your reply; there is no separate posting step.

## Rules
This skill adds no catalogue rules; every finding comes from the per-kind and cross-file skills. Its own rules are about procedure:
- The scope is the PR's configuration files plus the files they reference; nothing else is reviewed.
- A finding on a file outside the PR names the changed file that references it.
- Nothing is posted unless the request says to post or comment, and then exactly one comment is kept per PR.
- The reviewer never approves, requests changes or merges.
- When `gh` is missing or not authenticated, say so under "Not checked", fall back to `git diff` for the scope, and skip posting.

## Common false positives
- XF001 or XF002 on twins where only one copy is in the PR: report on the changed copy and name the other.
- IN007 on an `@import` whose target is added in the same PR but not yet on disk because the head was not checked out: say which commit was reviewed.
- Findings on generated files such as the rule catalogue that `linting-agent-config-files` ships: keep them, note the generator.

## References
- `references/pr-comment-template.md` — the sticky comment skeleton.
- Load `linting-agent-config-files` for `--changed-since` and the output formats; load `writing-review-findings` for the report contract.
