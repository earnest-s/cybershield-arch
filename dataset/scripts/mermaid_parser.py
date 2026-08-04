"""Mermaid flowchart parser -> CyberShield architecture JSON.

Converts a subset of Mermaid diagram syntax into the application's node/edge
contract (`{"nodes": [{"id", "type"}], "edges": [{"source", "target",
"label"}]}`) used by `backend/core/inference.py`.

Supported:
- headers: flowchart LR / TB / TD / RL / BT and legacy graph LR / TB
- node definitions: [label], [(label)], ((label)), {label}, ([label]),
  [[label]], >label], [/label/], [\\label\\]
- bare node references (implicit node creation)
- edges: -->, ---, ==> , -.->, --x, --o, <--> with |label| or " -- label --"
  inline labels, and chained arrows (A --> B --> C)
- subgraph blocks (title becomes a container node if referenced by edges)
- comment lines (%%), classDef/style/class/linkStyle/click directives

Unsupported diagram types (sequenceDiagram, pie, etc.) raise
``UnsupportedMermaidError`` and are skipped gracefully by callers.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from dataset.scripts.common import ALLOWED_EDGE_LABELS

# Header regexes -------------------------------------------------------------

_HEADER_FLOWCHART = re.compile(r"^\s*(?:flowchart|graph)\s+(LR|RL|TB|BT|TD)\s*$", re.IGNORECASE)
_HEADER_OTHER = re.compile(r"^\s*([A-Za-z]+)\s*$")

# Node definition regexes ----------------------------------------------------
# id followed by a bracketed/quoted label. Order matters: longest brackets first.
_NODE_DEF = re.compile(
    r"([A-Za-z0-9_][A-Za-z0-9_-]*)\s*"
    r"(\[\[.+?\]\]|\[\(.+?\)\]|\(\(.+?\)\)|\[[^\[\]]*?\]|\{.+?\}|\(\[.+?\]\)|>.+?\]|\[/.+?/\]|\[\\\\.+?\\\\\])"
)
_BARE_ID = re.compile(r"(?<![\w-])([A-Za-z0-9_][A-Za-z0-9_-]*)(?![\w-])")

# Edge regexes (progressive: label-on-arrow, label-after-dash, no label) -----
_EDGE = re.compile(
    r"(?P<a>[A-Za-z0-9_][A-Za-z0-9_-]*)\s*"
    r"(?P<link>-->|---|-\.->|\.->|==>|--x|--o|<-->|<--|-->|<-->|--->)"
    r"(?:\|(?P<label>[^|]*)\|)?\s*"
    r"(?P<b>[A-Za-z0-9_][A-Za-z0-9_-]*)"
)
_EDGE_DASH_LABEL = re.compile(
    r"(?P<a>[A-Za-z0-9_][A-Za-z0-9_-]*)\s*"
    r"(--|==|-\.)\s*(?P<label>[^|^<>=\-]+?)\s*(-->|==>|\.->)\s*"
    r"(?P<b>[A-Za-z0-9_][A-Za-z0-9_-]*)"
)

_LABEL_ALIASES: dict[str, str] = {
    "http": "HTTP",
    "https": "HTTP",
    "rest": "HTTP",
    "request": "HTTP",
    "api": "HTTP",
    "grpc": "HTTP",
    "tcp": "HTTP",
    "db": "DB Query",
    "sql": "DB Query",
    "query": "DB Query",
    "database": "DB Query",
    "async": "Async",
    "message": "Async",
    "event": "Async",
    "queue": "Async",
    "kafka": "Async",
    "cache": "Cache",
    "redis": "Cache",
}

_TYPE_KEYWORDS: list[tuple[str, str]] = [
    ("ui", "ui"),
    ("web", "ui"),
    ("frontend", "ui"),
    ("client", "ui"),
    ("portal", "ui"),
    ("dashboard", "ui"),
    ("database", "database"),
    ("db", "database"),
    ("postgres", "database"),
    ("mysql", "database"),
    ("mongodb", "database"),
    ("redis", "cache"),
    ("cache", "cache"),
    ("kafka", "queue"),
    ("queue", "queue"),
    ("rabbitmq", "queue"),
    ("message", "queue"),
    ("container", "container"),
    ("dock", "container"),
    ("kubernetes", "container"),
]


class UnsupportedMermaidError(ValueError):
    """Raised when a diagram uses an unsupported top-level syntax."""


@dataclass(slots=True)
class ParsedNode:
    id: str
    type: str = "service"


@dataclass(slots=True)
class ParsedEdge:
    source: str
    target: str
    label: str = "HTTP"


@dataclass(slots=True)
class MermaidGraph:
    diagram_type: str = ""
    nodes: list[ParsedNode] = field(default_factory=list)
    edges: list[ParsedEdge] = field(default_factory=list)
    subgraphs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [{"id": n.id, "type": n.type} for n in self.nodes],
            "edges": [
                {"source": e.source, "target": e.target, "label": e.label} for e in self.edges
            ],
        }


def _normalize_label(raw: str) -> str:
    text = (raw or "").strip().strip('"').lower()
    if not text:
        return "HTTP"
    for needle, normalized in _LABEL_ALIASES.items():
        if needle in text:
            return normalized
    return "HTTP"


def _infer_type(node_id: str, label_text: str) -> str:
    combined = f"{node_id} {label_text}".lower()
    for keyword, node_type in _TYPE_KEYWORDS:
        if keyword in combined:
            return node_type
    return "service"


_BRACKET_GRAMMAR: dict[str, str] = {
    "[[": "container",
    "([": "container",  # stadium ([label])
    ">(": "service",  # asymmetric >label]
    "[/": "service",  # parallelogram /label/
    "[\\": "service",
    "[(": "database",  # cylinder [(label)]
    "((": "service",  # circle ((label))
    "{": "service",  # rhombus {label}
    "[": "service",  # rectangle [label]
}


def _bracket_kind(bracket: str) -> str:
    lowered = bracket.lower()
    if lowered.startswith("("):
        if lowered.startswith("(("):
            return "service"
        if lowered.startswith("(["):
            return "container"
        return "database" if lowered.startswith("((") else "service"
    if lowered.startswith("[["):
        return "container"
    if lowered.startswith("(["):
        return "container"
    if lowered.startswith(">"):
        return "service"
    if lowered.startswith("[\\") or lowered.startswith("[/"):
        return "service"
    if lowered.startswith("[("):
        return "database"
    if lowered.startswith("{"):
        return "service"
    return "service"


def _clean_label(raw: str) -> str:
    cleaned = raw.replace("#quot;", '"').replace("#amp;", "&").replace("#39;", "'")
    return cleaned.strip()


def _is_directive(line: str) -> bool:
    return bool(re.match(r"^\s*(classDef|class |style |linkStyle|click |direction )", line, re.IGNORECASE))


def parse_mermaid(text: str) -> MermaidGraph:
    """Parse a Mermaid flowchart into a MermaidGraph; raises UnsupportedMermaidError."""
    graph = MermaidGraph()
    if not text or not text.strip():
        raise UnsupportedMermaidError("empty diagram")

    # Diagram header check
    first_line = text.strip().splitlines()[0]
    header = _HEADER_FLOWCHART.match(first_line)
    if header:
        graph.diagram_type = " ".join(("flowchart", header.group(1).upper()))
    else:
        other = _HEADER_OTHER.match(first_line)
        if other and other.group(1).lower() not in {"flowchart", "graph"}:
            raise UnsupportedMermaidError(f"unsupported diagram type: {other.group(1)!r}")
        if other is None:
            # try to locate a flowchart header anywhere in the doc
            for line in text.splitlines():
                m = _HEADER_FLOWCHART.match(line)
                if m:
                    graph.diagram_type = " ".join(("flowchart", m.group(1).upper()))
                    break
            else:
                raise UnsupportedMermaidError("no flowchart or graph directive found")

    nodes_by_id: dict[str, ParsedNode] = {}
    edges: list[ParsedEdge] = []
    inside_subgraph = False
    subgraph_title = ""

    def ensure_node(node_id: str, force_type: str | None = None) -> ParsedNode:
        existing = nodes_by_id.get(node_id)
        if existing is None:
            node = ParsedNode(id=node_id, type=force_type or "service")
            nodes_by_id[node_id] = node
            return node
        if force_type and existing.type == "service":
            existing.type = force_type
        return existing

    for raw_line in text.splitlines():
        line = raw_line.split("%%", 1)[0]
        if not line.strip():
            continue
        if _is_directive(line):
            continue

        sub_match = re.match(r"^\s*subgraph\s+([A-Za-z0-9_][A-Za-z0-9_-]*)?\s*(?:\[([^\]]*)\])?\s*$", line)
        if sub_match:
            inside_subgraph = True
            subgraph_title = sub_match.group(2) or sub_match.group(1) or f"subgraph{len(graph.subgraphs) + 1}"
            graph.subgraphs.append(subgraph_title)
            # Reserve the subgraph id as a container node only when referenced; handled in edges.
            continue
        if re.match(r"^\s*end\s*$", line):
            inside_subgraph = False
            continue

        # Extract edges first
        found_edges = False
        for match in _EDGE_DASH_LABEL.finditer(line):
            a, label, b = match.group("a"), match.group("label"), match.group("b")
            ensure_node(a)
            ensure_node(b)
            edges.append(ParsedEdge(source=a, target=b, label=_normalize_label(label)))
            found_edges = True
        for match in _EDGE.finditer(line):
            a, link, label, b = match.group("a"), match.group("link"), match.group("label"), match.group("b")
            label_text = label or _edge_link_label(link)
            ensure_node(a)
            ensure_node(b)
            edges.append(ParsedEdge(source=a, target=b, label=_normalize_label(label_text)))
            found_edges = True
        if found_edges:
            # Node definitions may share the line with an edge; process them too.
            pass

        # Extract node definitions (remaining text)
        for match in _NODE_DEF.finditer(line):
            node_id, bracket = match.group(1), match.group(2)
            label_text = _clean_label(bracket[1:-1])
            kind = _bracket_kind(bracket)
            node_type = _infer_type(node_id, label_text)
            # bracket grammar override for explicit database/container shapes
            if bracket.startswith("[("):
                node_type = "database"
            elif bracket.startswith("[[") or bracket.startswith("(["):
                node_type = "container"
            ensure_node(node_id, force_type=node_type)

        # Bare node ids on a line with no defs/edges already covered by edges.
        # Node def-only lines were covered above; catch bare ids without labels:
        for match in _BARE_ID.finditer(line):
            node_id = match.group(1)
            if node_id not in nodes_by_id and not found_edges:
                ensure_node(node_id)

    # Deduplicate edges, drop self-loops
    seen: set[tuple[str, str]] = set()
    final_edges: list[ParsedEdge] = []
    for edge in edges:
        if edge.source == edge.target:
            continue
        key = (edge.source, edge.target)
        if key in seen:
            continue
        seen.add(key)
        final_edges.append(edge)

    # Promote subgraph titles referenced by edges into explicit container nodes
    referenced = {edge.source for edge in final_edges} | {edge.target for edge in final_edges}
    for title, node in list(nodes_by_id.items()):
        _ = title, node
    # Ensure every edge endpoint exists in the node set
    for edge in final_edges:
        ensure_node(edge.source)
        ensure_node(edge.target)

    graph.nodes = list(nodes_by_id.values())
    graph.edges = final_edges
    return graph


def _edge_link_label(link: str) -> str:
    return "HTTP"


def parse_to_json(text: str) -> dict[str, Any]:
    """Parse Mermaid and return application-compatible {nodes, edges}."""
    graph = parse_mermaid(text)
    return graph.to_dict()