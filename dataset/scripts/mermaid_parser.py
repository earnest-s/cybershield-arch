"""Mermaid flowchart parser -> CyberShield architecture JSON.

Converts a subset of Mermaid diagram syntax into the application's node/edge
contract (``{"nodes": [{"id", "type"}], "edges": [{"source", "target",
"label"}]}``) used by ``backend/core/inference.py``.

Supported:
- headers: flowchart LR / TB / TD / RL / BT and legacy graph LR / TB
- node definitions: [label], [(label)], ((label)), {label}, ([label]),
  [[label]], >label], [/label/], [\\label\\]
- bare node references (implicit node creation)
- edges: -->, ---, ==> , -.->, --x, --o, <--> with |label| or " -- label --"
  inline labels, and chained arrows (A --> B --> C)
- subgraph blocks (title recorded; subgraph ids become nodes if referenced)
- comment lines (%%), classDef/style/class/linkStyle/click directives

Unsupported diagram types (sequenceDiagram, pie, etc.) raise
``UnsupportedMermaidError`` and are skipped gracefully by callers.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from backend.core.architecture_parser import (
    DEFAULT_EDGE_LABEL,
    derive_node_type,
    normalize_label,
)

_ID = r"[A-Za-z0-9_][A-Za-z0-9_-]*"

_HEADER_FLOWCHART = re.compile(r"^\s*(?:flowchart|graph)\s+(LR|RL|TB|BT|TD)\s*$", re.IGNORECASE)
_HEADER_OTHER = re.compile(r"^\s*([A-Za-z]+)\s*$")

_NODE_DEF = re.compile(
    rf"({_ID})\s*"
    r"(\[\[.+?\]\]|\(\(.+?\)\)|\[\(.+?\)\]|\(\[.+?\]\)|\{.+?\}|>.+?\]|\[/.+?/\]|\[\\\.+?\\\]|\[[^\[\]]*?\])"
)

_ARROW_TOKEN = re.compile(r"-->|---|-\.->|==>|--x|--o|<-->|<--")
_DASH_LABEL_EDGE = re.compile(
    rf"({_ID})\s*--\s*([^|<>=-]+?)\s*(?:-->|\.->|==>)\s*({_ID})"
)
_BARE_ID = re.compile(rf"(?<![\w-])({_ID})(?![\w-])")


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

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [{"id": n.id, "type": n.type} for n in self.nodes],
            "edges": [
                {"source": e.source, "target": e.target, "label": e.label} for e in self.edges
            ],
        }


def _clean_label(raw: str) -> str:
    return (
        raw.replace("#quot;", '"')
        .replace("#amp;", "&")
        .replace("#39;", "'")
        .strip()
    )


def _node_type_from_bracket(bracket: str) -> str | None:
    if bracket.startswith("[("):
        return "database"
    if bracket.startswith("[[") or bracket.startswith("(["):
        return "container"
    return None


def _label(raw: str) -> str:
    """Canonical label with the mermaid default fallback."""
    return normalize_label(raw) or DEFAULT_EDGE_LABEL


def _is_directive(line: str) -> bool:
    return bool(
        re.match(
            r"^\s*(classDef|class |style |linkStyle|click |direction )", line, re.IGNORECASE
        )
    )


def _extract_edges(line: str, edges: list[ParsedEdge], nodes_by_id: dict[str, ParsedNode]) -> bool:
    """Extract edges from a line, handling labels and chained arrows."""
    found = False

    # A -- label --> B
    for match in _DASH_LABEL_EDGE.finditer(line):
        _ensure_node(nodes_by_id, match.group(1))
        _ensure_node(nodes_by_id, match.group(3))
        edges.append(ParsedEdge(match.group(1), match.group(3), _label(match.group(2))))
        found = True
        line = line[: match.start()] + " " * (match.end() - match.start()) + line[match.end():]

    # A -->|label| B and plain arrows (chains resolve because each arrow is
    # scanned independently and the token before an arrow is its source)
    for arrow in _ARROW_TOKEN.finditer(line):
        prefix = line[: arrow.start()]
        suffix = line[arrow.end():]
        source_match = re.search(rf"({_ID})\s*$", prefix)
        target_match = re.match(rf"\s*(?:\|([^|]*)\|)?\s*({_ID})", suffix)
        if not source_match or not target_match:
            continue
        source, label_raw, target = source_match.group(1), target_match.group(1), target_match.group(2)
        _ensure_node(nodes_by_id, source)
        _ensure_node(nodes_by_id, target)
        edges.append(ParsedEdge(source, target, _label(label_raw)))
        found = True
    return found


def _ensure_node(nodes_by_id: dict[str, ParsedNode], node_id: str, force_type: str | None = None) -> ParsedNode:
    existing = nodes_by_id.get(node_id)
    if existing is None:
        node = ParsedNode(id=node_id, type=force_type or "service")
        nodes_by_id[node_id] = node
        return node
    if force_type and existing.type == "service":
        existing.type = force_type
    return existing


def parse_mermaid(text: str) -> MermaidGraph:
    """Parse a Mermaid flowchart; raises UnsupportedMermaidError otherwise."""
    graph = MermaidGraph()
    if not text or not text.strip():
        raise UnsupportedMermaidError("empty diagram")

    first_line = text.strip().splitlines()[0]
    header = _HEADER_FLOWCHART.match(first_line)
    if header:
        graph.diagram_type = f"flowchart {header.group(1).upper()}"
    else:
        other = _HEADER_OTHER.match(first_line)
        if other and other.group(1).lower() not in {"flowchart", "graph"}:
            raise UnsupportedMermaidError(f"unsupported diagram type: {other.group(1)!r}")
        for line in text.splitlines():
            m = _HEADER_FLOWCHART.match(line)
            if m:
                graph.diagram_type = f"flowchart {m.group(1).upper()}"
                break
        else:
            raise UnsupportedMermaidError("no flowchart or graph directive found")

    nodes_by_id: dict[str, ParsedNode] = {}
    edges: list[ParsedEdge] = []

    lines = text.splitlines()
    header_index = -1
    for idx, raw_line in enumerate(lines):
        if _HEADER_FLOWCHART.match(raw_line):
            header_index = idx
            break

    for idx, raw_line in enumerate(lines):
        if idx == header_index:
            continue
        line = raw_line.split("%%", 1)[0]
        if not line.strip() or _is_directive(line):
            continue

        sub_match = re.match(r"^\s*subgraph\b", line)
        if sub_match:
            rest = line[sub_match.end():].strip().strip('"')
            bracketed = re.search(r"\[([^\]]*)\]$", rest)
            graph.subgraphs.append((bracketed.group(1) if bracketed else rest).strip())
            continue
        if re.match(r"^\s*end\s*$", line):
            continue

        has_edges = _extract_edges(line, edges, nodes_by_id)
        has_defs = False
        for match in _NODE_DEF.finditer(line):
            node_id, bracket = match.group(1), match.group(2)
            label_text = _clean_label(bracket[1:-1])
            node_type = _node_type_from_bracket(bracket) or derive_node_type(node_id, label_text)
            _ensure_node(nodes_by_id, node_id, force_type=node_type)
            has_defs = True

        if not has_edges and not has_defs:
            for match in _BARE_ID.finditer(line):
                node_id = match.group(1)
                if node_id not in nodes_by_id:
                    _ensure_node(nodes_by_id, node_id)

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

    graph.nodes = list(nodes_by_id.values())
    graph.edges = final_edges
    return graph


def parse_to_json(text: str) -> dict[str, Any]:
    """Parse Mermaid text into application-compatible {nodes, edges}."""
    return parse_mermaid(text).to_dict()
