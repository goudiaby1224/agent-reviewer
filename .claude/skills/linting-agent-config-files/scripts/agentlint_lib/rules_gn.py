"""GN rules: encoding and line-ending hygiene applied to every discovered file."""
from typing import List

from .model import ConfigFile, Context, Finding


def check(cf: ConfigFile, ctx: Context) -> List[Finding]:
    out = []
    if cf.read_error:
        if "UTF-8" in cf.read_error:
            out.append(Finding("GN003", cf.path, cf.read_error, line=1))
        else:
            out.append(Finding("GN004", cf.path, "skipped: %s" % cf.read_error))
            ctx.not_checked.append("%s (%s)" % (cf.path, cf.read_error))
        return out
    if cf.bom:
        out.append(Finding("GN001", cf.path, "file starts with a UTF-8 BOM; frontmatter detection may fail in some tools",
                           line=1, autofix_safe=True, suggestion="save the file without a BOM"))
    if cf.crlf:
        out.append(Finding("GN002", cf.path, "CRLF line endings; tools differ in how they detect the --- delimiters",
                           line=1, autofix_safe=True, suggestion="convert to LF"))
    return out
