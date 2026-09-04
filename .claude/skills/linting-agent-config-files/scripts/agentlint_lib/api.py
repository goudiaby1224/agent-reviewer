"""Programmatic entry point: lint(...) returns the result dict used by --format json."""
import importlib
import os
import platform
import subprocess
from typing import Callable, Dict, List, Optional

from . import __version__, catalogue, discover, rules_gn, yamlfm  # noqa: F401 (catalogue registers rules)
from .model import SEVERITY_RANK, Context, Finding

# kind -> list of checker(cf, ctx) -> List[Finding]; filled by _load_rule_modules
RULE_MODULES: Dict[str, List[Callable]] = {}
CROSS_FILE: List[Callable] = []

_RULE_MODULE_NAMES = ("rules_ag", "rules_sk", "rules_in", "rules_cf")


def register_checker(kinds, func):
    for k in kinds:
        RULE_MODULES.setdefault(k, []).append(func)


def register_cross_file(func):
    CROSS_FILE.append(func)


def _load_rule_modules():
    """Register per-kind and cross-file checkers once."""
    if RULE_MODULES or CROSS_FILE:
        return
    for name in _RULE_MODULE_NAMES:
        mod = importlib.import_module("." + name, __package__)
        register_checker(mod.KINDS, mod.check)
    from . import rules_xf
    register_cross_file(rules_xf.check)


def resolve_root(root: Optional[str]) -> str:
    if root:
        return os.path.abspath(root)
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                             check=True, timeout=10).stdout.strip()
        if top:
            return top
    except Exception:
        pass
    return os.getcwd()


def lint(root: Optional[str], paths: List[str], excludes: List[str], collisions: bool = True,
         min_severity: str = "info", force_kind: Optional[str] = None) -> dict:
    _load_rule_modules()
    root = resolve_root(root)
    files = discover.discover(root, paths, excludes, force_kind)
    ctx = Context(root=root, files=files, yaml_parser=yamlfm.parser_name())
    findings: List[Finding] = []
    for cf in files:
        findings.extend(rules_gn.check(cf, ctx))
        if cf.read_error:
            continue
        for checker in RULE_MODULES.get(cf.kind, []):
            findings.extend(checker(cf, ctx))
    if collisions:
        for func in CROSS_FILE:
            findings.extend(func(ctx))
    if not any(f.kind == "mcp-copilot-cloud" for f in files):
        ctx.not_checked.append("Copilot cloud-agent MCP configuration lives in repository settings, not in the tree; "
                               "pass it with --kind mcp-copilot-cloud <file> to lint a pasted copy")
    threshold = SEVERITY_RANK[min_severity]
    findings = [f for f in findings if SEVERITY_RANK[f.severity] <= threshold]
    findings.sort(key=lambda f: (SEVERITY_RANK[f.severity], f.file, f.line or 0, f.id))
    summary = {"error": 0, "warning": 0, "info": 0}
    for f in findings:
        summary[f.severity] += 1
    return {
        "agentlint_version": __version__,
        "root": root,
        "python": platform.python_version(),
        "yaml_parser": ctx.yaml_parser,
        "files": [{"path": f.path, "kind": f.kind} for f in files],
        "findings": [f.to_dict() for f in findings],
        "summary": summary,
        "not_checked": ctx.not_checked,
    }
