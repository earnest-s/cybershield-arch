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

# Production guardrails enforced by the parser/validator.
MAX_NODES = 8
MAX_EDGES = 10
HARD_NODE_LIMIT = 10
HARD_EDGE_LIMIT = 15


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
