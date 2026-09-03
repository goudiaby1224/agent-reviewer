"""Front-matter splitting and YAML parsing with a stdlib fallback.

PyYAML is used when importable unless AGENTLINT_YAML=builtin. The builtin parser
covers the YAML subset found in agent/skill frontmatter: block and flow mappings
and sequences, quoted/plain scalars with continuation lines, block scalars (| >),
comments, booleans (YAML 1.1 set, matching PyYAML), ints, floats and nulls.
"""
import os
import re
from typing import Any, List, Optional, Tuple


class YAMLError(Exception):
    pass


def _use_pyyaml() -> bool:
    if os.environ.get("AGENTLINT_YAML", "").lower() == "builtin":
        return False
    try:
        import yaml  # noqa: F401
        return True
    except ImportError:
        return False


def parser_name() -> str:
    return "pyyaml" if _use_pyyaml() else "builtin"


def split_frontmatter(text: str) -> Tuple[Optional[str], str, int, Optional[str]]:
    """Return (frontmatter_text, body, body_start_line, error).

    Frontmatter must start on line 1 with '---' and end with '---' or '...'.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text, 1, None
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:]), i + 2, None
    return "\n".join(lines[1:]), "", len(lines) + 1, "unterminated frontmatter (no closing ---)"


def parse_yaml(text: str) -> Tuple[Any, Optional[str]]:
    if _use_pyyaml():
        import yaml
        try:
            return yaml.safe_load(text), None
        except yaml.YAMLError as e:  # pragma: no cover - depends on PyYAML
            return None, "invalid YAML: %s" % str(e).split("\n")[0]
    return builtin_load(text)


# ---------------------------------------------------------------- builtin parser

_BOOL_TRUE = {"true", "yes", "on"}
_BOOL_FALSE = {"false", "no", "off"}
_NULLS = {"", "~", "null"}
_INT_RE = re.compile(r"^[-+]?(0|[1-9][0-9_]*)$")
_FLOAT_RE = re.compile(r"^[-+]?([0-9][0-9_]*)?\.[0-9]*([eE][-+]?[0-9]+)?$|^[-+]?[0-9][0-9_]*[eE][-+]?[0-9]+$")


def builtin_load(text: str) -> Tuple[Any, Optional[str]]:
    try:
        p = _Parser(text.split("\n"))
        p.skip_blank()
        if p.eof():
            return None, None
        val = p.parse_node(p.indent())
        p.skip_blank()
        if not p.eof():
            raise YAMLError("unexpected content at line %d" % (p.i + 1))
        return val, None
    except YAMLError as e:
        return None, "invalid YAML (builtin parser): %s" % e


def _strip_comment(line: str) -> str:
    """Remove a trailing ' #...' comment that is outside quotes; a leading '#' is a full comment."""
    if line.lstrip().startswith("#"):
        return ""
    out, quote, prev = [], None, ""
    for ch in line:
        if quote:
            out.append(ch)
            if ch == quote and prev != "\\":
                quote = None
        elif ch in ("'", '"'):
            quote = ch
            out.append(ch)
        elif ch == "#" and (prev == " " or prev == "\t"):
            break
        else:
            out.append(ch)
        prev = ch
    return "".join(out).rstrip()


def _unquote(s: str, line_no: int) -> str:
    q = s[0]
    if len(s) < 2 or s[-1] != q:
        raise YAMLError("unterminated quoted string at line %d" % line_no)
    inner = s[1:-1]
    if q == "'":
        return inner.replace("''", "'")
    return (inner.replace("\\\\", "\x00").replace('\\"', '"').replace("\\n", "\n")
            .replace("\\t", "\t").replace("\x00", "\\"))


def _split_flow(inner: str, line_no: int) -> List[str]:
    """Split a flow collection body on commas outside quotes/brackets."""
    items, buf, depth, quote = [], [], 0, None
    for ch in inner:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
            buf.append(ch)
        elif ch in "[{":
            depth += 1
            buf.append(ch)
        elif ch in "]}":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            items.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if quote:
        raise YAMLError("unterminated quoted string at line %d" % line_no)
    tail = "".join(buf).strip()
    if tail:
        items.append(tail)
    return items


def _find_key_colon(s: str) -> int:
    """Index of the mapping colon (': ' or trailing ':') outside quotes/brackets, or -1."""
    depth, quote = 0, None
    for i, ch in enumerate(s):
        if quote:
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            if i == 0 or s[i - 1] in " ,[{":
                quote = ch
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        elif ch == ":" and depth == 0 and (i == len(s) - 1 or s[i + 1] in " \t"):
            return i
    return -1


def _is_mapping_line(s: str) -> bool:
    if s[:1] in ("[", "{"):
        return False
    return _find_key_colon(s) > 0


def _scalar(s: str, line_no: int) -> Any:
    s = s.strip()
    if s == "":
        return None
    if s[0] in ("'", '"'):
        return _unquote(s, line_no)
    if s[0] == "[":
        if s[-1] != "]":
            raise YAMLError("unterminated flow sequence at line %d" % line_no)
        return [_scalar(x, line_no) for x in _split_flow(s[1:-1], line_no)]
    if s[0] == "{":
        if s[-1] != "}":
            raise YAMLError("unterminated flow mapping at line %d" % line_no)
        result = {}
        for item in _split_flow(s[1:-1], line_no):
            c = _find_key_colon(item)
            if c < 0:
                raise YAMLError("bad flow mapping entry at line %d" % line_no)
            result[_scalar(item[:c], line_no)] = _scalar(item[c + 1:], line_no)
        return result
    if _find_key_colon(s) > 0:
        raise YAMLError("mapping values are not allowed here (unquoted ': ') at line %d" % line_no)
    low = s.lower()
    if low in _NULLS:
        return None
    if low in _BOOL_TRUE:
        return True
    if low in _BOOL_FALSE:
        return False
    if _INT_RE.match(s):
        return int(s.replace("_", ""))
    if _FLOAT_RE.match(s):
        try:
            return float(s.replace("_", ""))
        except ValueError:
            return s
    return s


class _Parser:
    def __init__(self, lines: List[str]):
        self.lines = lines
        self.i = 0
        for n, raw in enumerate(lines, start=1):
            lead = raw[: len(raw) - len(raw.lstrip())]
            if "\t" in lead and raw.strip():
                raise YAMLError("tab character in indentation at line %d" % n)

    def eof(self) -> bool:
        return self.i >= len(self.lines)

    def raw(self) -> str:
        return self.lines[self.i]

    def indent(self) -> int:
        r = self.raw()
        return len(r) - len(r.lstrip(" "))

    def content(self) -> str:
        return _strip_comment(self.raw()).strip()

    def skip_blank(self) -> None:
        while not self.eof() and self.content() == "":
            self.i += 1

    def parse_node(self, indent: int) -> Any:
        c = self.content()
        if c == "-" or c.startswith("- "):
            return self.parse_sequence(indent)
        if _is_mapping_line(c):
            return self.parse_mapping(indent)
        line_no = self.i + 1
        self.i += 1
        return _scalar(self._collect_continuation(c, indent), line_no)

    def _collect_continuation(self, first: str, indent: int) -> str:
        parts = [first]
        while not self.eof():
            if self.content() == "":
                self.i += 1
                continue
            if self.indent() <= indent:
                break
            c = self.content()
            if c == "-" or c.startswith("- ") or _is_mapping_line(c):
                break
            parts.append(c)
            self.i += 1
        return " ".join(parts)

    def parse_mapping(self, indent: int) -> dict:
        result = {}
        while True:
            self.skip_blank()
            if self.eof() or self.indent() < indent:
                break
            if self.indent() > indent:
                raise YAMLError("bad indentation at line %d" % (self.i + 1))
            c = self.content()
            line_no = self.i + 1
            if c == "-" or c.startswith("- "):
                raise YAMLError("sequence item where a mapping key was expected at line %d" % line_no)
            colon = _find_key_colon(c)
            if colon <= 0:
                raise YAMLError("expected 'key: value' at line %d" % line_no)
            key = _scalar(c[:colon], line_no)
            rest = c[colon + 1:].strip()
            self.i += 1
            if rest == "":
                self.skip_blank()
                if not self.eof() and self.indent() > indent:
                    result[key] = self.parse_node(self.indent())
                elif not self.eof() and self.indent() == indent and (self.content() == "-" or self.content().startswith("- ")):
                    result[key] = self.parse_sequence(indent)
                else:
                    result[key] = None
            elif rest in ("|", ">", "|-", ">-", "|+", ">+"):
                result[key] = self.parse_block_scalar(indent, rest)
            elif rest[0] in ("[", "{") and rest[-1] not in ("]", "}"):
                raise YAMLError("multi-line flow collections are not supported by the builtin parser (line %d)" % line_no)
            else:
                if rest[0] not in ("'", '"', "[", "{"):
                    rest = self._collect_continuation(rest, indent)
                result[key] = _scalar(rest, line_no)
        return result

    def parse_sequence(self, indent: int) -> list:
        items = []
        while True:
            self.skip_blank()
            if self.eof() or self.indent() < indent:
                break
            if self.indent() > indent:
                raise YAMLError("bad indentation at line %d" % (self.i + 1))
            c = self.content()
            if not (c == "-" or c.startswith("- ")):
                break
            line_no = self.i + 1
            rest = c[1:].strip()
            if rest == "":
                self.i += 1
                self.skip_blank()
                if not self.eof() and self.indent() > indent:
                    items.append(self.parse_node(self.indent()))
                else:
                    items.append(None)
            elif _is_mapping_line(rest):
                # rewrite "- key: v" as an indented mapping line so parse_mapping handles the block
                sub_indent = indent + (len(c) - len(rest))
                self.lines[self.i] = " " * sub_indent + rest
                items.append(self.parse_mapping(sub_indent))
            else:
                self.i += 1
                if rest[0] not in ("'", '"', "[", "{"):
                    rest = self._collect_continuation(rest, indent)
                items.append(_scalar(rest, line_no))
        return items

    def parse_block_scalar(self, indent: int, style: str) -> str:
        buf = []
        while not self.eof():
            raw = self.raw()
            if raw.strip() == "":
                buf.append("")
                self.i += 1
                continue
            ind = len(raw) - len(raw.lstrip(" "))
            if ind <= indent:
                break
            buf.append(raw)
            self.i += 1
        while buf and buf[-1] == "":
            buf.pop()
        non_blank = [len(b) - len(b.lstrip(" ")) for b in buf if b.strip()]
        base = min(non_blank) if non_blank else 0
        lines = [b[base:] if b.strip() else "" for b in buf]
        if style[0] == ">":
            out, para = [], []
            for ln in lines:
                if ln == "":
                    out.append(" ".join(para))
                    para = []
                else:
                    para.append(ln)
            out.append(" ".join(para))
            text = "\n".join(out)
        else:
            text = "\n".join(lines)
        if style.endswith("-"):
            return text
        return text + "\n"
