import os
import shutil
import tempfile
import unittest

from tests.helpers import import_lib

lib = import_lib()
from agentlint_lib import discover  # noqa: E402


def touch(root, rel, content="---\nname: x\ndescription: y\n---\nbody\n"):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    mode = "wb" if isinstance(content, bytes) else "w"
    with open(p, mode) as fh:
        fh.write(content)
    return p


class DetectKindTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_kinds(self):
        cases = {
            ".github/agents/a.agent.md": "copilot-agent",
            ".github/agents/b.md": "copilot-agent",
            "plugins/x/agents/c.agent.md": "copilot-agent",
            ".claude/agents/d.md": "claude-subagent",
            ".claude/agents/nested/e.md": "claude-subagent",
            ".claude/agents/f.agent.md": "claude-subagent",  # location wins over suffix
            ".github/chatmodes/f.chatmode.md": "chatmode",
            ".claude/skills/s/SKILL.md": "skill",
            ".github/skills/s/skill.md": "skill",
            ".github/copilot-instructions.md": "copilot-instructions",
            ".github/instructions/py.instructions.md": "path-instructions",
            "docs/odd.instructions.md": "path-instructions",
            ".github/prompts/p.prompt.md": "prompt-file",
            "AGENTS.md": "agents-md",
            "pkg/AGENT.md": "agents-md",
            "CLAUDE.md": "claude-md",
            ".claude/CLAUDE.md": "claude-md",
            "CLAUDE.local.md": "claude-md",
            ".claude/rules/r.md": "claude-rule",
            ".claude/commands/c.md": "claude-command",
            ".mcp.json": "mcp-claude",
            ".vscode/mcp.json": "mcp-vscode",
            ".github/mcp.json": "mcp-copilot-cli",
            ".claude/settings.json": "settings-hooks",
            ".claude/settings.local.json": "settings-hooks",
            "hooks/hooks.json": "settings-hooks",
            ".claude-plugin/plugin.json": "plugin-manifest",
            ".github/plugin/plugin.json": "plugin-manifest",
            ".claude-plugin/marketplace.json": "marketplace-manifest",
            ".github/workflows/copilot-setup-steps.yml": "copilot-setup-steps",
            ".cursor/rules/r.mdc": "cursor-rule",
            ".cursor/rules/r.md": "cursor-rule",
            "README.md": None,
            "src/app.py": None,
        }
        for rel, kind in cases.items():
            self.assertEqual(discover.detect_kind(rel, self.root), kind, rel)

    def test_plugin_root_agents_are_claude_subagents(self):
        touch(self.root, ".claude-plugin/plugin.json", "{}")
        touch(self.root, "agents/reviewer.md")
        self.assertEqual(discover.detect_kind("agents/reviewer.md", self.root), "claude-subagent")


class DiscoverTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        touch(self.root, ".github/agents/a.agent.md")
        touch(self.root, ".claude/skills/s/SKILL.md")
        touch(self.root, "tests/fixtures/bad/.claude/skills/t/SKILL.md")
        touch(self.root, "node_modules/x/SKILL.md")
        touch(self.root, ".mcp.json", '{"mcpServers": {}}')
        touch(self.root, "bin.agent.md", b"---\x00\x01binary")
        touch(self.root, "crlf/AGENTS.md", b"\xef\xbb\xbf# hi\r\nline\r\n")

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_discover_all_with_exclude(self):
        files = discover.discover(self.root, [], ["tests/fixtures/**"], None)
        paths = sorted(f.path for f in files)
        self.assertEqual(paths, [".claude/skills/s/SKILL.md", ".github/agents/a.agent.md", ".mcp.json",
                                 "bin.agent.md", "crlf/AGENTS.md"])

    def test_explicit_paths_and_force_kind(self):
        files = discover.discover(self.root, ["bin.agent.md"], [], "mcp-copilot-cloud")
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].kind, "mcp-copilot-cloud")

    def test_loading_flags(self):
        by_path = {f.path: f for f in discover.discover(self.root, [], ["tests/**"], None)}
        self.assertIsNone(by_path["bin.agent.md"].text)
        self.assertIsNotNone(by_path["bin.agent.md"].read_error)
        self.assertTrue(by_path["crlf/AGENTS.md"].bom)
        self.assertTrue(by_path["crlf/AGENTS.md"].crlf)
        self.assertEqual(by_path["crlf/AGENTS.md"].text, "# hi\nline\n")
        skill = by_path[".claude/skills/s/SKILL.md"]
        self.assertTrue(skill.fm_present)
        self.assertEqual(skill.fm["name"], "x")
        self.assertEqual(skill.body_line, 5)
        self.assertEqual(by_path[".mcp.json"].data, {"mcpServers": {}})

    def test_glob_match(self):
        self.assertTrue(discover.glob_match("tests/fixtures/**", "tests/fixtures/a/b.md"))
        self.assertTrue(discover.glob_match("**/*.md", "a/b/c.md"))
        self.assertFalse(discover.glob_match("tests/*", "tests/a/b.md"))
        self.assertTrue(discover.glob_match("*.json", "x.json"))
