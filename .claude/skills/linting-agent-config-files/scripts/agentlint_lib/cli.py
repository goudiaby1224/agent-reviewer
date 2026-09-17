"""Command-line interface."""
import argparse
import sys
import traceback

from . import __version__, discover
from .model import SEVERITIES


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="agentlint", description="Lint AI agent configuration files.")
    p.add_argument("paths", nargs="*", help="files or directories (default: discover from root)")
    p.add_argument("--root", help="repository root (default: git toplevel or cwd)")
    p.add_argument("--format", choices=["text", "json", "markdown", "github"], default="text")
    p.add_argument("--kind", choices=discover.KINDS, help="force a kind for the given paths")
    p.add_argument("--exclude", action="append", default=[], metavar="GLOB", help="skip matching paths (repeatable)")
    p.add_argument("--changed-since", metavar="REF", help="lint only configuration files changed since git REF")
    p.add_argument("--no-collisions", action="store_true", help="skip cross-file (XF) checks")
    p.add_argument("--min-severity", choices=SEVERITIES, default="info")
    p.add_argument("--list-rules", action="store_true", help="print the rule catalogue and exit")
    p.add_argument("--version", action="version", version="agentlint %s" % __version__)
    return p


def main(argv=None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return 0 if e.code == 0 else 2
    from . import api, report
    if args.list_rules:
        api._load_rule_modules()
        sys.stdout.write(report.catalogue_markdown() if args.format == "markdown" else report.catalogue_text())
        return 0
    try:
        result = api.lint(args.root, args.paths, args.exclude, not args.no_collisions, args.min_severity, args.kind,
                          changed_since=args.changed_since)
    except ValueError as e:  # bad --changed-since ref or not a git repository
        sys.stderr.write("agentlint: %s\n" % e)
        return 2
    except Exception:  # internal failure: report and exit 2
        traceback.print_exc()
        return 2
    renderers = {"json": report.to_json, "markdown": report.to_markdown, "github": report.to_github}
    sys.stdout.write(renderers.get(args.format, report.to_text)(result))
    return 1 if result["summary"]["error"] else 0
