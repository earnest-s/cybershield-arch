"""Canonical architecture parser.

Unifies the node-type / edge-label inference previously duplicated across
backend/core/inference.py and dataset/scripts/mermaid_parser.py:
- ``derive_node_type`` merges inference._derive_type_from_id and the mermaid
  ``_TYPE_KEYWORDS`` table.
- ``normalize_edge_label`` merges inference._normalize_label/_infer_edge_label
  and the mermaid ``_LABEL_ALIASES`` table.
- ``parse_architecture`` turns raw LLM/JSON output into the canonical
  ``{nodes, edges}`` contract (dedupes, drops self-loops/dangling edges and
  caps sizes). Raises ValueError on contract violations exactly like the
  legacy ``_validate_architecture`` so retry logic is preserved.
"""

from __future__ import annotations

import json
import re
from typing import Any

from backend.core.architecture_schema import (
    MAX_EDGES,
    MAX_NODES,
    NODE_TYPE_ALIASES,
    NODE_TYPE_KEYWORDS,
    LABEL_ALIASES,
)

DEFAULT_NODE_TYPE = "service"
DEFAULT_EDGE_LABEL = "HTTP"


def derive_node_type(node_id: str, label_text: str = "") -> str:
    """Infer a canonical node type from an id and optional label text."""
    combined = f"{node_id} {label_text}".lower()
    for keyword, node_type in NODE_TYPE_KEYWORDS:
        if keyword in combined:
            return node_type
    return DEFAULT_NODE_TYPE


def normalize_node_type(raw_type: Any, node_id: str = "") -> str:
    """Return a canonical node type for a raw type string (id fallback)."""
    if not isinstance(raw_type, str) or not raw_type.strip():
        return derive_node_type(node_id)
    normalized = raw_type.strip().lower()
    candidate = NODE_TYPE_ALIASES.get(normalized, normalized)
    if candidate == "component":
        return derive_node_type(node_id)
    if candidate not in {"ui", "service", "database", "cache", "queue", "container"}:
        return derive_node_type(node_id)
    return candidate


def normalize_label(label: str | None) -> str | None:
    """Map a raw edge label to a canonical label; None if unmapped/empty.

    Unmapped labels return None so callers can apply a type-pair heuristic or
    the default edge label (preserving mermaid's fallback-to-HTTP behavior).
    """
    if not isinstance(label, str) or not label.strip():
        return None
    lowered = label.strip().lower()
    for alias, canonical in LABEL_ALIASES.items():
        if alias in lowered:
            return canonical
    return None


def infer_edge_label(
    source_type: str,
    target_type: str,
    current: str | None = None,
) -> str:
    """Best-effort canonical label based on the current label then type pairs."""
    normalized = normalize_label(current)
    if normalized:
        return normalized
    if source_type == "ui" and target_type == "service":
        return "HTTP"
    if source_type == "service" and target_type == "database":
        return "DB Query"
    if source_type == "service" and target_type == "queue":
        return "Async"
    if source_type == "service" and target_type == "cache":
        return "Cache"
    return DEFAULT_EDGE_LABEL


def _split_edge(edge: Any) -> tuple[Any, Any, Any]:
    """Return (source, target, label) from dict or positional-list edge."""
    if isinstance(edge, dict):
        source = edge.get("source") if edge.get("source") is not None else edge.get("from")
        target = edge.get("target") if edge.get("target") is not None else edge.get("to")
        label = edge.get("label") if edge.get("label") is not None else edge.get("protocol")
        return source, target, label
    if isinstance(edge, (list, tuple)) and len(edge) >= 2:
        label = edge[2] if len(edge) >= 3 else None
        return edge[0], edge[1], label
    return None, None, None


def extract_json_object(raw_text: str) -> dict:
    """Extract the first JSON object with 'nodes' and 'edges' from text."""
    cleaned = raw_text.strip()
    cleaned = cleaned.replace("```json", "").replace("```JSON", "").replace("```", "").strip()

    decoder = json.JSONDecoder()
    for start in (idx for idx, ch in enumerate(cleaned) if ch == "{"):
        try:
            parsed, _ = decoder.raw_decode(cleaned[start:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict) and "nodes" in parsed and "edges" in parsed:
            return parsed
    raise ValueError("Model output did not contain a complete architecture JSON object")


def _strip_json_line_comments(text: str) -> str:
    """Remove // comments outside of JSON strings and trailing commas."""
    out: list[str] = []
    in_string = False
    escape = False
    i = 0
    while i < len(text):
        ch = text[i]
        if in_string:
            out.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < len(text) and text[i + 1] == "/":
            i += 2
            while i < len(text) and text[i] != "\n":
                i += 1
            continue
        out.append(ch)
        i += 1
    return re.sub(r",\s*([}\]])", r"\1", "".join(out))


def extract_json_object_comments(raw_text: str) -> dict:
    """Like extract_json_object but tolerant of // comments and trailing commas."""
    cleaned = _strip_json_line_comments(raw_text)
    decoder = json.JSONDecoder()
    for start in (idx for idx, ch in enumerate(cleaned) if ch == "{"):
        try:
            parsed, _ = decoder.raw_decode(cleaned[start:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict) and "nodes" in parsed and "edges" in parsed:
            return parsed
    raise ValueError("Model output did not contain a complete architecture JSON object")


def parse_architecture(raw_payload: Any) -> dict[str, Any]:
    """Normalize raw JSON output into the canonical {nodes, edges} dict.

    Raises ValueError when the payload is missing the required structure or
    yields an empty graph (preserves the legacy inference retry flow).
    """
    if not isinstance(raw_payload, dict):
        raise ValueError("Architecture JSON must be an object")

    nodes = raw_payload.get("nodes")
    edges = raw_payload.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("Architecture JSON must contain 'nodes' and 'edges' arrays")
    if len(nodes) == 0 or len(edges) == 0:
        raise ValueError("Architecture JSON must include at least one node and one edge")

    normalized_nodes: list[dict[str, str]] = []
    node_types_by_id: dict[str, str] = {}

    for node in nodes:
        node_id: Any = None
        node_type: Any = None
        if isinstance(node, dict):
            node_id = node.get("id")
            node_type = node.get("type")
        elif isinstance(node, str):
            node_id = node

        if not isinstance(node_id, str) or not node_id.strip():
            raise ValueError("Each node must include a non-empty string 'id'")
        normalized_id = node_id.strip()
        if len(normalized_id) > 64:
            raise ValueError("Node id exceeds limits")

        if normalized_id in node_types_by_id:
            continue
        node_types_by_id[normalized_id] = normalize_node_type(node_type, normalized_id)
        normalized_nodes.append({"id": normalized_id, "type": node_types_by_id[normalized_id]})

    normalized_nodes = normalized_nodes[:MAX_NODES]
    allowed_ids = {node["id"] for node in normalized_nodes}
    node_types_by_id = {node["id"]: node["type"] for node in normalized_nodes}

    normalized_edges: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for edge in edges:
        source, target, label = _split_edge(edge)
        if not isinstance(source, str) or not isinstance(target, str):
            raise ValueError("Each edge must include string 'source' and 'target'")

        source_id = source.strip()
        target_id = target.strip()

        if source_id == target_id:
            continue
        if source_id not in allowed_ids or target_id not in allowed_ids:
            continue

        key = (source_id, target_id)
        if key in seen:
            continue
        seen.add(key)

        normalized_edges.append({
            "source": source_id,
            "target": target_id,
            "label": infer_edge_label(
                node_types_by_id[source_id],
                node_types_by_id[target_id],
                label if isinstance(label, str) else None,
            ),
        })
        if len(normalized_edges) >= MAX_EDGES:
            break

    if len(normalized_edges) == 0:
        raise ValueError("Architecture JSON must include at least one valid edge")

    return {"nodes": normalized_nodes, "edges": normalized_edges}
