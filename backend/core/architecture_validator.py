"""Canonical architecture validator.

Structural and quality checks over a parsed ``{nodes, edges}`` dict. Replaces
the ad-hoc checks previously spread across:
- backend/core/inference.py (_validate_architecture, _is_structurally_weak_graph)
- dataset/scripts/validate_dataset.py (duplicate ids, dangling edges,
  connectedness, allowed types/labels)

Graph is weakly connected when every node is reachable from any other
(undirected). Hard structural violations raise ValueError (drives the runtime
retry loop); quality violations are reported as ValidationIssues.
"""

from __future__ import annotations

from typing import Any

from backend.core.architecture_models import ValidationIssue, ValidationResult
from backend.core.architecture_schema import (
    ALLOWED_EDGE_LABELS,
    ALLOWED_NODE_TYPES,
    HARD_EDGE_LIMIT,
    HARD_NODE_LIMIT,
)

RULE_COLLISION = "node_id_collision"
RULE_DANGLING = "dangling_edge"
RULE_UNSUPPORTED_TYPE = "unsupported_node_type"
RULE_UNSUPPORTED_LABEL = "unsupported_edge_label"
RULE_DUPLICATE_EDGE = "duplicate_edge"
RULE_SELF_LOOP = "self_loop"
RULE_CONNECTED = "connectedness"
RULE_SIZE = "size_guardrail"


def is_weakly_connected(nodes: list[dict], edges: list[dict]) -> bool:
    """True when the graph is connected when edge direction is ignored."""
    if not nodes:
        return False
    node_ids = {node.get("id") for node in nodes}
    adjacency: dict[str, set[str]] = {node_id: set() for node_id in node_ids}
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source in adjacency and target in adjacency:
            adjacency[source].add(target)
            adjacency[target].add(source)

    start = next(iter(node_ids))
    visited = {start}
    stack = [start]
    while stack:
        node_id = stack.pop()
        for neighbor in adjacency[node_id]:
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append(neighbor)
    return visited == node_ids


def has_orphan_node(architecture: dict) -> bool:
    """True when a node has no incident edge (degree == 0)."""
    nodes = architecture.get("nodes", [])
    edges = architecture.get("edges", [])
    if not nodes or not edges:
        return True

    degrees: dict[str, int] = {
        node["id"]: 0
        for node in nodes
        if isinstance(node, dict) and isinstance(node.get("id"), str)
    }
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        source = edge.get("source")
        target = edge.get("target")
        if isinstance(source, str) and source in degrees:
            degrees[source] += 1
        if isinstance(target, str) and target in degrees:
            degrees[target] += 1

    return any(degree == 0 for degree in degrees.values())


def is_structurally_weak(architecture: dict) -> bool:
    """True when the graph is empty, disconnected, or has orphan nodes."""
    if has_orphan_node(architecture):
        return True
    return not is_weakly_connected(architecture.get("nodes", []), architecture.get("edges", []))


def collect_issues(architecture: dict) -> list[ValidationIssue]:
    """Collect quality issues; does not raise."""
    nodes = architecture.get("nodes", [])
    edges = architecture.get("edges", [])

    node_ids: list[str] = []
    for node in nodes:
        if not isinstance(node, dict) or not isinstance(node.get("id"), str):
            continue
        node_id = node["id"]
        node_ids.append(node_id)
        node_type = node.get("type", "")
        if node_type not in ALLOWED_NODE_TYPES:
            yield ValidationIssue(
                rule=RULE_UNSUPPORTED_TYPE,
                severity="error",
                message=f"Node {node_id!r} has unsupported type {node_type!r}",
            )

    seen_ids: set[str] = set()
    for node_id in node_ids:
        if node_id in seen_ids:
            yield ValidationIssue(
                rule=RULE_COLLISION,
                severity="error",
                message=f"Duplicate node id {node_id!r}",
            )
        seen_ids.add(node_id)

    seen_edges: set[tuple[str, str]] = set()
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        source = edge.get("source")
        target = edge.get("target")
        label = edge.get("label", "")

        if source not in seen_ids or target not in seen_ids:
            yield ValidationIssue(
                rule=RULE_DANGLING,
                severity="error",
                message=f"Edge {source!r} -> {target!r} references a missing node",
            )
        if source == target:
            yield ValidationIssue(
                rule=RULE_SELF_LOOP,
                severity="warning",
                message=f"Self-loop edge {source!r} -> {source!r}",
            )
        edge_key = (source, target)
        if edge_key in seen_edges:
            yield ValidationIssue(
                rule=RULE_DUPLICATE_EDGE,
                severity="warning",
                message=f"Duplicate edge {source!r} -> {target!r}",
            )
        seen_edges.add(edge_key)

        if label not in ALLOWED_EDGE_LABELS:
            yield ValidationIssue(
                rule=RULE_UNSUPPORTED_LABEL,
                severity="warning",
                message=f"Edge {source!r} -> {target!r} has unsupported label {label!r}",
            )

    if len(node_ids) > HARD_NODE_LIMIT or len(edges) > HARD_EDGE_LIMIT:
        yield ValidationIssue(
            rule=RULE_SIZE,
            severity="error",
            message="Graph exceeds production limits",
        )


def validate_architecture(architecture: dict) -> ValidationResult:
    """Full validation: issues + connectivity + structural weakness."""
    issues = list(collect_issues(architecture))

    connected = is_weakly_connected(architecture.get("nodes", []), architecture.get("edges", []))
    if not connected:
        issues.append(
            ValidationIssue(rule=RULE_CONNECTED, severity="warning", message="Graph is disconnected")
        )

    structurally_weak = not connected or has_orphan_node(architecture)
    has_errors = any(issue.severity == "error" for issue in issues)
    return ValidationResult(
        valid=not has_errors,
        issues=issues,
        structurally_weak=structurally_weak,
    )


def raise_if_invalid(architecture: dict) -> None:
    """Raise ValueError on hard structural violations (runtime retry flow)."""
    if not isinstance(architecture.get("nodes"), list) or not isinstance(architecture.get("edges"), list):
        raise ValueError("Architecture JSON must contain 'nodes' and 'edges' arrays")
    if not architecture["nodes"] or not architecture["edges"]:
        raise ValueError("Architecture JSON must include at least one node and one edge")
    if len(architecture["nodes"]) > HARD_NODE_LIMIT or len(architecture["edges"]) > HARD_EDGE_LIMIT:
        raise ValueError("Generated graph exceeds production limits")

    for issue in collect_issues(architecture):
        if issue.severity == "error":
            raise ValueError(issue.message)
