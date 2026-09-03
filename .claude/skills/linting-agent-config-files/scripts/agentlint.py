#!/usr/bin/env python3
"""agentlint — deterministic linter for AI agent configuration files.

Usage: python3 agentlint.py [PATH ...] [--root DIR] [--format json|text] [--kind KIND]
                            [--exclude GLOB]... [--no-collisions] [--min-severity LEVEL] [--list-rules]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentlint_lib.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
