# Instruction, prompt and memory file formats

Sources (fetched 2026-09-04):
- GH-REPO = https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions
- GH-CR = https://docs.github.com/en/copilot/tutorials/customize-code-review
- GH-CHEAT = https://docs.github.com/en/copilot/reference/customization-cheat-sheet
- VSC-INSTR = https://code.visualstudio.com/docs/agent-customization/custom-instructions
- VSC-PROMPT = https://code.visualstudio.com/docs/agent-customization/prompt-files
- AGENTSMD = https://agents.md/
- CC-MEM = https://code.claude.com/docs/en/memory
- CC-SKILLS = https://code.claude.com/docs/en/skills (for `.claude/commands`)
- CURSOR = https://cursor.com/docs/context/rules (the old `docs.cursor.com/context/rules` URL redirects to the docs landing page)

Quotations are verbatim. `UNVERIFIED` marks facts none of these pages states. Linter rule IDs in brackets.

## `.github/copilot-instructions.md` (kind `copilot-instructions`)
- Location: "a `copilot-instructions.md` file in the `.github` directory" (GH-REPO). Read on github.com (Copilot Chat with the repository attached, cloud agent, code review), in Copilot CLI, VS Code and Visual Studio; JetBrains, Eclipse and Xcode in preview (GH-CHEAT).
- Frontmatter: none documented on any page [IN012 reports one if present].
- Length: "Instructions must be no longer than 2 pages" (GH-REPO) and "Limit any single instruction file to a maximum of about 1,000 lines" (GH-CR) [IN005].
- Content: "Instructions must not be task specific" (GH-REPO) [IN015]. GH-CR lists unsupported categories: changing formatting or user experience, modifying the pull request overview comment, changing Copilot's core function, following external links, vague quality demands [IN016 for demands the repository cannot satisfy].
- Precedence: "Personal instructions take the highest priority. Repository instructions come next, and then organization instructions" (GH-REPO). Within a workspace VS Code combines all instruction files with "no specific order" (VSC-INSTR). When a path-specific file matches, "the instructions from both files are used" (GH-REPO).

## `*.instructions.md` (kind `path-instructions`)
- github.com: `.github/instructions/NAME.instructions.md`, subdirectories allowed; "The file name must end with `.instructions.md`" (GH-REPO). "Currently, on GitHub.com, path-specific custom instructions are only supported for Copilot cloud agent and Copilot code review" (GH-REPO) [IN011 for other locations].
- VS Code: workspace `.github/instructions`, workspace `.claude/rules` (Claude format), user `~/.copilot/instructions` or `~/.claude/rules`, plus `chat.instructionsFilesLocations`; folders searched recursively (VSC-INSTR).

| Key | Type | Surfaces | Documented form | Linter |
|---|---|---|---|---|
| `applyTo` | string of one or more globs, comma-separated | github.com, VS Code | `applyTo: "**/*.ts,**/*.tsx"`, `applyTo: "**"`; GH glob table: `*`, `**` or `**/*`, `*.py`, `**/*.py`, `src/*.py`, `src/**/*.py`, `**/subdir/**/*.py`. VS Code: "If not specified, the instructions are not applied automatically". No YAML-list form on any page | IN002 (missing), IN003 (list or non-string) |
| `excludeAgent` | string | github.com only | `"code-review"` or `"cloud-agent"` | IN004 |
| `name` | string | VS Code | "Display name shown in the UI. Defaults to the file name." | IN014 (known) |
| `description` | string | VS Code | "Short description shown on hover in the Chat view." | IN014 (known) |

Any other key is unknown to both surfaces [IN014].

## `*.prompt.md` (kind `prompt-file`)
- Location: `.github/prompts/*.prompt.md` and the VS Code user profile; `chat.promptFilesLocations` adds more (VSC-PROMPT). Surfaces: VS Code and Visual Studio; JetBrains and Xcode in preview; not github.com, not Copilot CLI, not Eclipse (GH-CHEAT). "Agents running on the Agent Host don't use prompt files" (VSC-PROMPT).
- Invocation: `/` plus the prompt name, the Chat: Run Prompt command, or the editor play button (VSC-PROMPT).

| Key | Type | Documented form | Linter |
|---|---|---|---|
| `description` | string | "A short description of the prompt." | known |
| `name` | string | slash-command name; "If not specified, the file name is used." | known |
| `argument-hint` | string | input-field hint | known |
| `agent` | string | `ask`, `agent`, `plan`, or a custom agent name; "If tools are specified, the default agent is `agent`" | IN006 (dangling), XF003 |
| `model` | string | display name such as `GPT-4o`, `Claude Sonnet 4` | known |
| `tools` | YAML list | tool names, tool sets, `<server name>/*`, extension tools; "If a given tool is not available when running the prompt, it is ignored." Priority: prompt `tools`, then the referenced agent's `tools`, then the selected agent's defaults | IN019 (non-list) |
| `mode` | not on the page | earlier versions used `mode` where `agent` now stands; the current page does not mention it | IN018 (legacy, autofix to `agent`) |

Variables on the page: `${selection}`, `${input:variableName}`, `${input:variableName:placeholder}` (VSC-PROMPT). Others such as `${workspaceFolder}` or `${file}`: UNVERIFIED (VSC-PROMPT). Other files are referenced with relative Markdown links.

## `AGENTS.md` (kind `agents-md`)
- "Create an AGENTS.md file at the root of the repository"; nested files allowed, "the closest one takes precedence" (AGENTSMD). GitHub: "one or more `AGENTS.md` files, stored anywhere within the repository"; "the nearest `AGENTS.md` file in the directory tree will take precedence"; alternatively a single root `CLAUDE.md` or `GEMINI.md` (GH-REPO). Code review reads it from the head branch (GH-CR).
- VS Code: root file applied to all chat requests (`chat.useAgentsMdFile`); nested files behind `chat.useNestedAgentsMdFiles`, "experimental and might change or be removed" (VSC-INSTR) [IN009].
- Cursor: root and subdirectories, nested instructions combined with parents (CURSOR).
- Claude Code: "Claude Code reads `CLAUDE.md`, not `AGENTS.md`" (CC-MEM) [XF010].
- Format: "just standard Markdown"; no frontmatter (AGENTSMD, CURSOR) [IN012].
- Legacy singular `AGENT.md`: documented only at agents.md as a rename target (`mv AGENT.md AGENTS.md && ln -s AGENTS.md AGENT.md`) [IN010].

## `CLAUDE.md`, `CLAUDE.local.md` (kind `claude-md`)
- Load order, broadest first: managed policy file (`/Library/Application Support/ClaudeCode/CLAUDE.md`, `/etc/claude-code/CLAUDE.md`, `C:\Program Files\ClaudeCode\CLAUDE.md`), `~/.claude/CLAUDE.md`, `./CLAUDE.md` or `./.claude/CLAUDE.md`, `./CLAUDE.local.md` (CC-MEM). Files from the working directory and every parent are concatenated, root first; within a directory `CLAUDE.local.md` follows `CLAUDE.md`; subdirectory files load on demand (CC-MEM).
- `CLAUDE.local.md` is not gitignored automatically: "Add `CLAUDE.local.md` to your `.gitignore`" (CC-MEM).
- Size: "target under 200 lines per CLAUDE.md file"; a file over 4 MiB is skipped (CC-MEM). Block-level HTML comments are stripped before injection (CC-MEM).
- VS Code also reads `CLAUDE.md`, `.claude/CLAUDE.md`, `~/.claude/CLAUDE.md` and `CLAUDE.local.md` when `chat.useClaudeMdFile` is on (VSC-INSTR).
- Frontmatter: none documented [IN012].

### `@import` syntax (CC-MEM)
- `@path/to/import`; "Both relative and absolute paths are allowed. Relative paths resolve relative to the file containing the import"; `@~/...` for the home directory [IN007 resolves both].
- "maximum depth of four hops".
- "Import parsing skips Markdown code spans and fenced code blocks" [IN007 skips them too]. Bare `@handle` mentions without `/` or `.` are not imports [IN007 skips them].
- Imports in a project file that resolve outside the working directory trigger a one-time approval dialog.
- Recommended bridge to other tools: a `CLAUDE.md` containing `@AGENTS.md`, or `ln -s AGENTS.md CLAUDE.md` (CC-MEM) [XF010].

## `.claude/rules/**/*.md` (kind `claude-rule`)
| Key | Type | Documented form | Linter |
|---|---|---|---|
| `paths` | YAML list of glob strings | `- "src/api/**/*.ts"`; brace expansion supported; "Rules without a `paths` field are loaded unconditionally"; a rule's list shares a budget of 1,000 expanded patterns and 4 MiB | IN008 |

Discovered recursively in project `.claude/rules/` and user `~/.claude/rules/` (user rules load first, project rules take priority); symlinks supported (CC-MEM). VS Code reads the same files and defaults `paths` to `**` (VSC-INSTR). Other keys: none documented [IN014].

## `.claude/commands/**/*.md` (kind `claude-command`)
- "Custom commands have been merged into skills"; a command file and a skill of the same name "both create `/deploy` and work the same way"; "if a skill and a command share the same name, the skill takes precedence" (CC-SKILLS) [IN020, XF005].
- Frontmatter: "the same frontmatter" as skills "except `name` and `paths`, which Claude Code ignores in a command file" (CC-SKILLS). The linter therefore accepts every skill key except those two [IN014].
- The memory page does not describe command files at all; the facts above come from the skills page.

## Cursor rules (kind `cursor-rule`)
- Location `.cursor/rules/`; "Project rules must use the `.mdc` extension"; "A plain `.md` file in `.cursor/rules` is ignored" (CURSOR) [IN013].
- Legacy `.cursorrules` and nested `.cursor/rules`: UNVERIFIED (CURSOR); Claude Code's `/init` mentions reading `.cursorrules` (CC-MEM).

| Key | Type | Documented form | Linter |
|---|---|---|---|
| `description` | string | drives "Apply Intelligently" | known |
| `globs` | string | `globs: src/components/**/*.tsx`; list form UNVERIFIED | known |
| `alwaysApply` | boolean | `true` = "Always Apply"; `false` without `description` or `globs` = "Apply Manually" | known |

## Unresolved
- Whether `applyTo` is formally required on github.com (the how-to only says to create a frontmatter block containing it).
- Which Copilot features read `AGENTS.md`, and its precedence relative to `copilot-instructions.md`.
- Prompt-file `mode` key status and the full prompt-variable list.
- Cursor `.cursorrules` support, nested rule directories, and list-form `globs`.
