# SKILL.md runtime extensions: GitHub Copilot and Claude Code

Sources (all fetched 2026-09-04):
- GH-SKILLS = https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills
- VSC-SKILLS = https://code.visualstudio.com/docs/copilot/customization/agent-skills
- GH-PUBLISH = https://cli.github.com/manual/gh_skill_publish
- GH-INSTALL = https://cli.github.com/manual/gh_skill_install
- CLI-REF = https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference
- CC-SKILLS = https://code.claude.com/docs/en/skills

`UNVERIFIED` marks a fact none of these pages states.

## Discovery directories

| Directory | Scope | Copilot (GH-SKILLS, VSC-SKILLS) | Claude Code (CC-SKILLS) |
|---|---|---|---|
| `.github/skills/<name>/SKILL.md` | project | yes | no |
| `.agents/skills/<name>/SKILL.md` | project | yes; shared with Cursor, Codex, Gemini CLI, Antigravity, Amp, Cline, OpenCode and Warp (GH-INSTALL) | no |
| `.claude/skills/<name>/SKILL.md` | project | yes | yes; also from every parent directory up to the repository root, from nested directories below the working directory (loaded when a file inside is read or edited, named `apps/web:deploy` on clash), and from `--add-dir` directories |
| `~/.copilot/skills/`, `~/.agents/skills/` | personal | yes | no |
| `~/.claude/skills/<name>/SKILL.md` | personal | VS Code lists it (VSC-SKILLS); the github.com page does not (GH-SKILLS) | yes |
| enterprise managed path (for example `/etc/claude-code/.claude/skills/`) | organisation | no | yes |
| `<plugin>/skills/<name>/SKILL.md` | plugin | VS Code shows plugin skills alongside local ones; Copilot CLI lists them with `copilot plugins list --kind skill` | yes, namespaced `plugin-name:skill-name` |
| VS Code `chat.agentSkillsLocations`, `chat.useCustomizationsInParentRepositories`, extension `chatSkills` contribution | VS Code only | yes | no |

Copilot surfaces: "Agent skills work with Copilot cloud agent, Copilot code review, the GitHub Copilot CLI, the GitHub Copilot app, and agent mode in Visual Studio Code" (GH-SKILLS). Neither Copilot page maps a directory to a surface. The Copilot CLI reference names no skill directory and has no `/skills` command; skills are managed with `copilot skill`, inspected with `/env`, and plugin-provided skills with `copilot plugins list` (CLI-REF).

## Precedence between copies of the same name
- Copilot: UNVERIFIED. None of GH-SKILLS, VSC-SKILLS or CLI-REF states which copy wins when the same skill name exists in more than one directory. The linter reports every copy after the first in the order `.github`, `.agents`, `.claude` (XF001) so that the reviewer can ask the author to keep one.
- Claude Code (CC-SKILLS): "enterprise overrides personal, and personal overrides project". A skill at any level overrides a bundled skill of the same name but not the bundled skill's aliases. Plugin skills are namespaced and never conflict. "If a skill and a command share the same name, the skill takes precedence" (XF005). Any of these overrides a skill synced from a claude.ai account.

## Frontmatter keys by runtime

| Key | Spec | github.com cloud agent (GH-SKILLS) | VS Code (VSC-SKILLS) | Claude Code (CC-SKILLS) |
|---|---|---|---|---|
| `name` | required, 1-64, matches directory | required; "must be lowercase, using hyphens for spaces"; no length stated | "Only lowercase letters, numbers, and hyphens"; "Must match the parent directory name"; "Maximum 64 characters"; invalid characters make the skill "silently fail to load" | optional; display label only for personal and project skills, the command comes from the directory name; sets the last command segment for plugin skills |
| `description` | required, 1-1024 | required | "Maximum 1024 characters" | "Recommended"; if omitted the first paragraph of the body is used; `description` plus `when_to_use` truncated at 1,536 characters in the listing |
| `license` | optional | optional | not mentioned | accepted, not acted on |
| `compatibility` | optional, up to 500 | not mentioned | not mentioned | "Accepts a string of up to 500 characters", not acted on |
| `metadata` | map of strings to strings | not mentioned | not mentioned | "Free-form YAML map"; a non-map value is dropped |
| `allowed-tools` | space-separated string | `allowed-tools: shell` example; "tools Copilot may use without asking for confirmation" | not mentioned | "Accepts a space- or comma-separated string, or a YAML list"; grant lasts for the invoking turn; `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PROJECT_DIR}` substituted inside `Bash(...)` rules |
| `argument-hint` | no | no | yes: hint shown when invoked as a slash command | yes: hint shown during autocomplete |
| `user-invocable` | no | no | yes: default `true`; `false` hides the slash command | yes: default `true`; `false` hides `/name` and blocks manual runs |
| `disable-model-invocation` | no | no | yes: default `false`; `true` requires manual `/` invocation | yes: default `false`; `true` also prevents preloading into subagents (XF004) and scheduled runs |
| `context` | no | no | yes: `fork` runs the skill in a dedicated subagent | yes: `fork` |
| `agent` | no | no | not mentioned (UNVERIFIED which subagent runs a fork) | subagent type for `context: fork`: `Explore`, `Plan`, `general-purpose` or a custom subagent from `.claude/agents/`; default `general-purpose` |
| `background` | no | no | no | boolean, default `true`, only with `context: fork` (v2.1.218+) |
| `when_to_use` | no | no | no | extra trigger text appended to the description in the listing |
| `arguments` | no | no | no | named positional arguments for `$name` substitution; space-separated string or YAML list |
| `disallowed-tools` | no | no | no | tools removed while the skill is active; string or YAML list |
| `model` | no | no | no | same values as `/model`, or `inherit`; with `context: fork` sets the subagent's model |
| `effort` | no | no | no | `low`, `medium`, `high`, `xhigh`, `max`; availability depends on the model |
| `hooks` | no | no | no | hooks registered when the skill is invoked; the `once` option is documented on the hooks page, not as a top-level key |
| `paths` | no | no | no | glob patterns limiting automatic activation; comma-separated string or YAML list; ignored in `.claude/commands/` files |
| `shell` | no | no | no | `bash` (default) or `powershell` for `!` command blocks |

Boolean fields in Claude Code also accept `yes`, `no`, `on`, `off`, `1`, `0` in any case (CC-SKILLS).

Portability rule stated by Claude Code: "Outside Claude Code, you can use only the fields in the Agent Skills spec". Uploads to claude.ai, the Skills API and `package_skill.py` fail with `Unexpected key(s) in SKILL.md frontmatter` for any non-spec key (CC-SKILLS). The linter reports non-spec keys as SK010 (info) and says which runtimes honour them.

## Copilot visibility matrix (VSC-SKILLS)
| Frontmatter | Slash command | Auto-loaded |
|---|---|---|
| both omitted | yes | yes |
| `user-invocable: false` | no | yes |
| `disable-model-invocation: true` | yes | no |
| both set | no | no (disabled) |

## `gh skill publish` and `gh skill install` (GH-PUBLISH, GH-INSTALL)
- `gh skill publish` validates "Skill names match the strict agentskills.io naming rules", "Each skill name matches its directory name", "Required frontmatter fields (name, description) are present", "allowed-tools is a string, not an array" [SK019], and strips "Install metadata (`metadata.github-*`)". Flags: `--dry-run`, `--fix`, `--tag`.
- Discovery conventions for publishing: `skills/*/SKILL.md`, `skills/{scope}/*/SKILL.md`, `*/SKILL.md`, `plugins/{scope}/skills/*/SKILL.md`.
- `gh skill install` places skills "in a host-specific directory at either project scope ... or user scope"; `--agent` selects the host (values include `github-copilot`, `claude-code`, `cursor` and many more), `--scope {project|user}`, `--dir` overrides both, `--allow-hidden-dirs` includes `.claude/skills/` and `.agents/skills/` in the source repository, `--pin` pins a tag or commit.
- Installed skills get "source tracking metadata injected into their frontmatter" under `metadata.github-*`; the exact key names are UNVERIFIED (not listed on either page).
- Per-agent destination table: UNVERIFIED beyond "several agents ... share the `.agents/skills` directory".

## Claude Code invocation and substitution (CC-SKILLS)
- `/skill-name` invokes a skill; the directory name is the command. Up to six skills can be stacked in one message; trailing text becomes `$ARGUMENTS` for each.
- Substitutions: `$ARGUMENTS`, `$ARGUMENTS[N]`, `$N`, `$name` (from `arguments`), `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}`, `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` (plugin skills only).
- `` !`command` `` and fenced ` ```! ` blocks run shell commands before the content is sent; a failing command aborts the invocation; `disableSkillShellExecution` turns the feature off.
- `.claude/commands/<name>.md` files "support the same frontmatter, except `name` and `paths`" and create `/<name>` from the file name (IN020 marks them legacy).
- Frontmatter is read only when the opening `---` is the first line; malformed YAML loads the body with empty metadata.
- Reserved folder name `synced` in every skills location; `<skill-name>` entries may be symlinks; a skill folder with `.claude-plugin/plugin.json` loads as a plugin.

## Unresolved
- Copilot precedence between `.github/skills`, `.agents/skills` and `.claude/skills` copies of one name.
- Which Copilot surface reads which directory, and whether github.com or Copilot CLI read `~/.claude/skills/`.
- Exact `metadata.github-*` keys written by `gh skill install`, and the per-agent install directory table.
- Whether VS Code honours `agent` for `context: fork`.
