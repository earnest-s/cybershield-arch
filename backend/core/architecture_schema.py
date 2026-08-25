"""Canonical architecture vocabulary and structural constants.

Single source of truth for the node-type and edge-label contract shared by
the runtime (backend/core/inference.py), the API (backend/api/main.py), the
security engine, and the dataset pipeline (dataset/scripts/*).

Consumers must import these constants instead of redefining them.
"""

from __future__ import annotations

import json
from typing import Any

ALLOWED_NODE_TYPES: frozenset[str] = frozenset(
    {"ui", "service", "database", "cache", "queue", "container"}
)

ALLOWED_EDGE_LABELS: frozenset[str] = frozenset(
    {"HTTP", "DB Query", "Async", "Cache"}
)

NODE_TYPE_ALIASES: dict[str, str] = {
    "data": "database",
    "db": "database",
    "worker": "service",
}

# Ordered (keyword, node_type) pairs used to infer a node type from an id or
# label. First match wins; this merges the keyword tables previously kept in
# backend/core/inference.py and dataset/scripts/mermaid_parser.py. The rare
# substring "front" is intentionally excluded: labels like "Azure Front Door"
# must not flip a node to "ui".
NODE_TYPE_KEYWORDS: tuple[tuple[str, str], ...] = (
    # ui
    ("ui", "ui"),
    ("web", "ui"),
    ("frontend", "ui"),
    ("client", "ui"),
    ("portal", "ui"),
    ("dashboard", "ui"),
    # database
    ("database", "database"),
    ("postgres", "database"),
    ("mysql", "database"),
    ("mongodb", "database"),
    ("storage", "database"),
    ("db", "database"),
    # cache
    ("redis", "cache"),
    ("cache", "cache"),
    # queue
    ("kafka", "queue"),
    ("rabbitmq", "queue"),
    ("queue", "queue"),
    ("broker", "queue"),
    ("message", "queue"),
    # container
    ("container", "container"),
    ("docker", "container"),
    ("kubernetes", "container"),
    ("cluster", "container"),
    # service (fallback-adjacent; api/backend/service keywords)
    ("api", "service"),
    ("service", "service"),
    ("backend", "service"),
)

# Label normalization aliases (merged from inference.py and mermaid_parser.py).
LABEL_ALIASES: dict[str, str] = {
    "http": "HTTP",
    "https": "HTTP",
    "rest": "HTTP",
    "request": "HTTP",
    "api": "HTTP",
    "grpc": "HTTP",
    "tcp": "HTTP",
    "db query": "DB Query",
    "db": "DB Query",
    "sql": "DB Query",
    "query": "DB Query",
    "database": "DB Query",
    "select": "DB Query",
    "async": "Async",
    "message": "Async",
    "event": "Async",
    "queue": "Async",
    "kafka": "Async",
    "publish": "Async",
    "subscribe": "Async",
    "cache": "Cache",
    "redis": "Cache",
    "cached": "Cache",
}

# Canonical presentation metadata consumed by renderers. The UI must not
# redefine these tables; it reads ``icon`` / ``layer`` / ``dashed`` from the
# response produced by response_builder.build_response.
NODE_TYPE_LAYERS: dict[str, str] = {
    "ui": "ui",
    "service": "service",
    "database": "data",
    "cache": "data",
    "queue": "service",
    "container": "service",
}

# Canonical brand/technology icon names recognized from a node id. Merges the
# icon inference previously duplicated in frontend DiagramView.inferIconFromLabel.
NODE_ICON_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("postgres", "postgres"),
    ("redis", "redis"),
    ("kafka", "kafka"),
    ("docker", "docker"),
    ("nginx", "nginx"),
    ("react", "react"),
    ("node", "node"),
    ("aws", "aws"),
)

# Canonical edge-label presentation: which labels render as a dashed (async)
# connector. Mirrors the Async/label treatment previously hardcoded in the UI.
EDGE_DASHED_LABELS: frozenset[str] = frozenset({"Async"})

# Production guardrails enforced by the parser/validator.
# v2 canonical contract: the parser limit and the validator hard limit are ONE
# contract (10 nodes / 15 edges). Outputs within the limit pass through
# untouched; over-limit output fails explicitly (never silently truncated).
MAX_NODES = 10
MAX_EDGES = 15
HARD_NODE_LIMIT = 10
HARD_EDGE_LIMIT = 15


def derive_node_icon(node_id: str) -> str | None:
    """Infer a canonical technology icon name from a node id.

    Returns a member of the canonical icon vocabulary (postgres/redis/kafka/
    docker/nginx/react/node/aws) or None when no brand is recognizable; the
    renderer falls back to its type-based presentation icon.
    """
    lowered = node_id.lower()
    for keyword, icon in NODE_ICON_KEYWORDS:
        if keyword in lowered:
            return icon
    return None


def canonical_architecture(architecture: dict[str, Any]) -> str:
    """Order-invariant serialization used to detect duplicate architectures."""
    nodes = sorted(
        (node.get("id"), node.get("type")) for node in architecture.get("nodes", [])
    )
    edges = sorted(
        (edge.get("source"), edge.get("target"), edge.get("label"))
        for edge in architecture.get("edges", [])
    )
    return json.dumps({"nodes": nodes, "edges": edges}, sort_keys=True)
