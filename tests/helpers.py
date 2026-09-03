import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(REPO_ROOT, ".claude", "skills", "linting-agent-config-files", "scripts")
FIXTURES = os.path.join(REPO_ROOT, "tests", "fixtures")
GOOD = os.path.join(FIXTURES, "good")
BAD = os.path.join(FIXTURES, "bad")


def import_lib():
    """Put the scripts dir on sys.path and return the agentlint_lib package."""
    if SCRIPTS_DIR not in sys.path:
        sys.path.insert(0, SCRIPTS_DIR)
    import agentlint_lib  # noqa: E402
    return agentlint_lib


def run_lint(paths=None, root=None, excludes=None, collisions=True, force_kind=None):
    """Run the linter in-process and return the result dict (same shape as --format json)."""
    import_lib()
    from agentlint_lib import api
    return api.lint(root=root or FIXTURES, paths=paths or [], excludes=excludes or [],
                    collisions=collisions, min_severity="info", force_kind=force_kind)


def ids(result, file=None):
    """Set of (rule id, file) pairs, optionally filtered to one file."""
    return {(f["id"], f["file"]) for f in result["findings"] if file is None or f["file"] == file}
