import os
import unittest
from unittest import mock

from tests.helpers import import_lib

lib = import_lib()
from agentlint_lib import yamlfm  # noqa: E402


class SplitFrontmatterTests(unittest.TestCase):
    def test_no_frontmatter(self):
        fm, body, line, err = yamlfm.split_frontmatter("# Title\nbody\n")
        self.assertIsNone(fm)
        self.assertEqual(body, "# Title\nbody\n")
        self.assertEqual(line, 1)
        self.assertIsNone(err)

    def test_basic_frontmatter(self):
        fm, body, line, err = yamlfm.split_frontmatter("---\nname: x\n---\n# T\n")
        self.assertEqual(fm, "name: x")
        self.assertEqual(body, "# T\n")
        self.assertEqual(line, 4)
        self.assertIsNone(err)

    def test_unterminated(self):
        fm, body, line, err = yamlfm.split_frontmatter("---\nname: x\nbody")
        self.assertIn("unterminated", err)


class BuiltinParserTests(unittest.TestCase):
    def setUp(self):
        self.env = mock.patch.dict(os.environ, {"AGENTLINT_YAML": "builtin"})
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_parser_name(self):
        self.assertEqual(yamlfm.parser_name(), "builtin")

    def test_scalars_and_types(self):
        obj, err = yamlfm.parse_yaml(
            'name: my-skill\ndescription: "Use when: x"\ncount: 3\nratio: 1.5\nflag: true\nnothing: ~\nquoted: \'it\'\'s\'\n')
        self.assertIsNone(err)
        self.assertEqual(obj, {"name": "my-skill", "description": "Use when: x", "count": 3,
                               "ratio": 1.5, "flag": True, "nothing": None, "quoted": "it's"})

    def test_flow_and_block_lists(self):
        obj, err = yamlfm.parse_yaml("tools: ['read', \"edit\", search]\nskills:\n  - a\n  - b\n")
        self.assertIsNone(err)
        self.assertEqual(obj, {"tools": ["read", "edit", "search"], "skills": ["a", "b"]})

    def test_nested_maps_and_list_of_maps(self):
        text = ("handoffs:\n  - label: Fix\n    agent: agent\n    send: false\n"
                "metadata:\n  version: \"1.0\"\n  family: x\n")
        obj, err = yamlfm.parse_yaml(text)
        self.assertIsNone(err)
        self.assertEqual(obj["handoffs"], [{"label": "Fix", "agent": "agent", "send": False}])
        self.assertEqual(obj["metadata"], {"version": "1.0", "family": "x"})

    def test_block_scalar_and_continuation(self):
        text = "description: |\n  line one\n  line two\nother: first\n  continued\n"
        obj, err = yamlfm.parse_yaml(text)
        self.assertIsNone(err)
        self.assertEqual(obj["description"], "line one\nline two\n")
        self.assertEqual(obj["other"], "first continued")

    def test_comments_and_hash_in_quotes(self):
        obj, err = yamlfm.parse_yaml("# top\nname: a # trailing\ntitle: \"a # b\"\n")
        self.assertIsNone(err)
        self.assertEqual(obj, {"name": "a", "title": "a # b"})

    def test_tab_indentation_is_error(self):
        obj, err = yamlfm.parse_yaml("a:\n\tb: 1\n")
        self.assertIsNone(obj)
        self.assertIn("tab", err)

    def test_unquoted_colon_space_in_value_is_error(self):
        # "key: a: b" is ambiguous in YAML; PyYAML raises, the builtin parser must too
        obj, err = yamlfm.parse_yaml("description: Use when: something\n")
        self.assertIsNone(obj)
        self.assertIsNotNone(err)

    def test_empty_document(self):
        obj, err = yamlfm.parse_yaml("\n# nothing\n")
        self.assertIsNone(err)
        self.assertIsNone(obj)


class PyYAMLParityTests(unittest.TestCase):
    """When PyYAML is installed, both parsers must agree on the frontmatter shapes used in this repo."""

    SAMPLES = [
        "name: x\ndescription: y\n",
        "tools: ['read', 'search']\nmodel: inherit\n",
        "handoffs:\n  - label: A\n    agent: agent\n    prompt: Do it\n    send: false\n",
        "metadata:\n  version: \"1.0.0\"\n",
        "description: >\n  folded\n  text\n",
    ]

    def test_parity(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")
        for s in self.SAMPLES:
            with mock.patch.dict(os.environ, {"AGENTLINT_YAML": "builtin"}):
                builtin, err = yamlfm.parse_yaml(s)
            self.assertIsNone(err, s)
            self.assertEqual(builtin, yaml.safe_load(s), s)


if __name__ == "__main__":
    unittest.main()
