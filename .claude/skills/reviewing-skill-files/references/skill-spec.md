# SKILL.md: the Agent Skills specification

Source: https://agentskills.io/specification (fetched 2026-09-04). Quotations are verbatim from that page. The linter rules that enforce each point are given in brackets.

## Directory contract
- "A skill is a directory containing, at minimum, a `SKILL.md` file". The file name is exactly `SKILL.md` [SK012].
- `name` "Must match the parent directory name" [SK004].
- "The `SKILL.md` file must contain YAML frontmatter followed by Markdown content." [SK001]
- Optional conventional subdirectories, all recommendations rather than requirements:

| Directory | Purpose (spec wording) |
|---|---|
| `scripts/` | "Contains executable code that agents can run." Scripts should "Be self-contained or clearly document dependencies", "Include helpful error messages", "Handle edge cases gracefully". Supported languages "depend on the agent implementation. Common options include Python, Bash, and JavaScript." [SK008 checks shebang and executable bit] |
| `references/` | "Contains additional documentation that agents can read when needed". "Keep individual reference files focused. Agents load these on demand, so smaller files mean less use of context." |
| `assets/` | "Contains static resources: Templates ..., Images ..., Data files ..." |

- "A skill directory may contain any files and directories beyond the required `SKILL.md`."
- Validation tool named by the spec: `skills-ref validate ./my-skill`.

## Frontmatter fields
The spec defines exactly six fields.

| Key | Type | Required | Limits and format | Linter |
|---|---|---|---|---|
| `name` | string | yes | "Must be 1-64 characters"; "May only contain unicode lowercase alphanumeric characters (`a-z`, `0-9`) and hyphens (`-`)"; "Must not start or end with a hyphen (`-`)"; "Must not contain consecutive hyphens (`--`)"; "Must match the parent directory name". Invalid examples on the page: `PDF-Processing`, `-pdf`, `pdf--processing`. The page gives prose rules, not a regex; the linter uses `^[a-z0-9]+(-[a-z0-9]+)*$`, which encodes the same rules. | SK002, SK003, SK004 |
| `description` | string | yes | "Must be 1-1024 characters"; "Should describe both what the skill does and when to use it"; "Should include specific keywords that help agents identify relevant tasks". | SK005 (length), SK015 and SK016 (quality, manual) |
| `license` | string | no | "License name or reference to a bundled license file." Example: `license: Proprietary. LICENSE.txt has complete terms`. | none |
| `compatibility` | string | no | "Must be 1-500 characters if provided"; "Should only be included if your skill has specific environment requirements"; "Most skills do not need the `compatibility` field." | SK009 |
| `metadata` | map of string keys to string values | no | "Arbitrary key-value mapping for additional metadata (a map from string keys to string values)." Recommended to make key names "reasonably unique". Example keys `author`, `version: "1.0"`. | SK014 |
| `allowed-tools` | space-separated string | no | "Space-separated string of pre-approved tools the skill may use. (Experimental)"; "Support for this field may vary between agent implementations". Example: `allowed-tools: Bash(git:*) Bash(jq:*) Read`. | SK019 (list form) |

Any other key is outside the spec. Claude Code defines extra keys (see `runtime-extensions.md`); the linter reports keys unknown to every runtime as SK011.

## Body guidance
- "The Markdown body after the frontmatter contains the skill instructions. There are no format restrictions."
- Recommended content: "Step-by-step instructions", "Examples of inputs and outputs", "Common edge cases".
- "Keep your main `SKILL.md` under 500 lines. Move detailed reference material to separate files." [SK006]
- Progressive disclosure, verbatim: "**Metadata** (~100 tokens): The `name` and `description` fields are loaded at startup for all skills"; "**Instructions** (< 5000 tokens recommended): The full `SKILL.md` body is loaded when the skill is activated"; "**Resources** (as needed): Files (e.g. those in `scripts/`, `references/`, or `assets/`) are loaded only when required".
- "When referencing other files in your skill, use relative paths from the skill root"; example `See [the reference guide](references/REFERENCE.md) for details.` "Keep file references one level deep from `SKILL.md`. Avoid deeply nested reference chains." [SK007 resolves links and backticked `scripts/`, `references/`, `assets/` paths]

## What the spec does not say
- Nothing about discovery directories, precedence between copies, slash-command invocation or argument substitution. Those are runtime extensions; see `runtime-extensions.md`.
- No maximum body size in bytes, only the 500-line recommendation.
