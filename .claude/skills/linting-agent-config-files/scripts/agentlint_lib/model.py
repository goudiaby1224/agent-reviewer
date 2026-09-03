"""Data model shared by every agentlint module."""
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

SEVERITIES = ("error", "warning", "info")
SEVERITY_RANK = {"error": 0, "warning": 1, "info": 2}
TAGS = ("auto", "manual")
RUNTIMES = ("copilot", "claude", "both", "generic")


@dataclass(frozen=True)
class Rule:
    id: str
    severity: str
    tag: str
    family: str
    runtime: str
    title: str
    source: str


RULES: Dict[str, Rule] = {}


def rule(id: str, severity: str, tag: str, family: str, runtime: str, title: str, source: str) -> Rule:
    """Register a rule. Duplicate ids and bad enum values are programming errors."""
    if id in RULES:
        raise ValueError("duplicate rule id %s" % id)
    if severity not in SEVERITIES or tag not in TAGS or runtime not in RUNTIMES:
        raise ValueError("bad rule definition %s" % id)
    if not id.startswith(family) or len(id) != len(family) + 3 or not id[len(family):].isdigit():
        raise ValueError("rule id %s does not match family %s" % (id, family))
    r = Rule(id, severity, tag, family, runtime, title, source)
    RULES[id] = r
    return r


@dataclass
class Finding:
    id: str
    file: str
    message: str
    line: Optional[int] = None
    severity: str = ""
    runtime: str = ""
    source: str = ""
    confidence: str = "high"
    autofix_safe: bool = False
    suggestion: str = ""

    def __post_init__(self):
        r = RULES.get(self.id)
        if r is None:
            raise KeyError("unknown rule id %s" % self.id)
        if r.tag != "auto":
            raise ValueError("manual rule %s cannot be emitted by the linter" % self.id)
        self.severity = self.severity or r.severity
        self.runtime = self.runtime or r.runtime
        self.source = self.source or r.source

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["title"] = RULES[self.id].title
        return d


@dataclass
class ConfigFile:
    path: str                      # root-relative POSIX path
    abs_path: str
    kind: str
    text: Optional[str] = None     # None when unreadable or binary
    body: str = ""
    frontmatter: Optional[Any] = None
    fm_present: bool = False
    fm_text: str = ""
    fm_error: Optional[str] = None
    body_line: int = 1             # 1-based line where the body starts
    data: Any = None               # parsed JSON/YAML for config kinds
    data_error: Optional[str] = None
    read_error: Optional[str] = None
    bom: bool = False
    crlf: bool = False

    @property
    def fm(self) -> Dict[str, Any]:
        """Frontmatter as a dict (empty when absent or not a mapping)."""
        return self.frontmatter if isinstance(self.frontmatter, dict) else {}

    @property
    def name(self) -> str:
        return os.path.basename(self.path)

    @property
    def dirname(self) -> str:
        return os.path.dirname(self.path)

    def key_line(self, key: str) -> Optional[int]:
        """1-based line of a top-level frontmatter key, or None."""
        if not self.fm_present:
            return None
        for i, ln in enumerate(self.fm_text.split("\n"), start=2):
            stripped = ln.lstrip()
            if ln == stripped and (stripped.startswith(key + ":") or stripped.startswith('"%s":' % key)
                                   or stripped.startswith("'%s':" % key)):
                return i
        return None

    def body_lines(self) -> int:
        return 0 if not self.body.strip() else self.body.count("\n") + (0 if self.body.endswith("\n") else 1)


@dataclass
class Context:
    root: str
    files: List[ConfigFile] = field(default_factory=list)
    yaml_parser: str = "pyyaml"
    not_checked: List[str] = field(default_factory=list)

    def exists(self, relpath: str) -> bool:
        return os.path.exists(os.path.join(self.root, relpath))

    def by_kind(self, *kinds: str) -> List[ConfigFile]:
        return [f for f in self.files if f.kind in kinds]
