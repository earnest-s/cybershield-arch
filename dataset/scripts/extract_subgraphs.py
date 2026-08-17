"""Deterministic connected-subgraph extraction for CyberShield (Phase 6).

Extracts provenance-preserving connected subgraphs from the immutable
production corpus (dataset/final/CyberShield_Dataset_v1_FULL.jsonl). Every
extracted subgraph:

  * contains only node/edge dict objects taken verbatim from its parent
    record (no fabricated nodes/edges, no re-serialization drift),
  * retains both endpoints of every extracted edge,
  * is weakly connected (spanning-tree construction + independent
    re-verification with backend.core.architecture_validator),
  * respects the canonical runtime contract without inventing limits:
        HARD_NODE_LIMIT = 10, HARD_EDGE_LIMIT = 15
    (imported from backend.core.architecture_schema and enforced with the
    runtime's own raise_if_invalid),
  * carries complete provenance (parent id, transformation method/version,
    selected node/edge ids, retention ratios),
  * re-derives security semantics with the exact canonical engine used by
    the production pipeline (backend.core.response_builder.build_security_dict,
    same call enrich_dataset.py makes).

Determinism
-----------
Extraction is fully deterministic: no randomness anywhere. Bucket allocation,
component/root/candidate selection, spanning-tree construction and edge
pruning all use sorted ids and stable scoring. The only non-deterministic
upstream surfaces are set orders inside the security engine; the final
record is therefore canonicalized by stable sorting of those lists (threats,
recommendations), which changes ordering only and never content.

Source immutability
-------------------
The corpus file is opened read-only. Its SHA256 is computed before and
after processing and must be unchanged.

Verification
------------
For every accepted subgraph the script asserts (and records) the 7 proofs:
  1. extracted node ids are a subset of parent node ids
  2. extracted edges are exact parent edge dicts
  3. every extracted edge has both endpoints retained
  4. the subgraph is weakly connected
  5. the canonical runtime contract validation passes (raise_if_invalid)
  6. provenance fields are complete
  7. the output is deterministic (stable order, no timestamps/randomness)

Usage
-----
    uv run python dataset/scripts/extract_subgraphs.py \
        --input  dataset/final/CyberShield_Dataset_v1_FULL.jsonl \
        --output dataset/docs/phase6_pilot/subgraph_pilot.jsonl \
        --stats  dataset/docs/phase6_pilot/subgraph_pilot_stats.json \
        --sample-size 100
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.core.architecture_schema import HARD_EDGE_LIMIT, HARD_NODE_LIMIT  # noqa: E402
from backend.core.architecture_validator import (  # noqa: E402
    is_weakly_connected,
    raise_if_invalid,
)
from backend.core.response_builder import build_security_dict  # noqa: E402

SCRIPT_VERSION = "1.0.0"
TRANSFORMATION_METHOD = "sacce_connected_subgraph_v1"
TRANSFORMATION_VERSION = "1.0.0"

ENTRY_KEYWORDS = (
    "api-gateway", "apigw", "load-balancer", "loadbalancer", "ingress",
    "gateway", "waf", "cdn", "proxy", "frontend", "front", "edge", "public",
    "web", "ui", "portal", "dashboard", "client", "app",
)
DATA_KEYWORDS = (
    "database", "storage", "postgres", "postgresql", "mysql", "mongo",
    "mongodb", "cosmos", "dynamo", "redis", "warehouse", "lake", "s3",
    "blob", "cache", "queue", "kafka", "rabbit", "message", "stream", "db",
)
SECURITY_KEYWORDS = (
    "waf", "iam", "auth", "oauth", "oidc", "mfa", "2fa", "vault", "kms",
    "secret", "rbac", "siem", "ids", "ips", "firewall", "zero-trust",
    "guard", "policy", "audit", "sso", "trust", "pki", "cert", "keycloak",
)
TYPE_ROLE = {"ui": 6, "database": 6, "cache": 4, "queue": 4, "container": 2, "service": 1}
LABEL_WEIGHT = {"DB Query": 3, "Cache": 2, "Async": 2, "HTTP": 1}

# Node-count buckets used for the deterministic stratified pilot sample.
BUCKETS = [
    ("b1_02_10", 2, 10),
    ("b2_11_20", 11, 20),
    ("b3_21_30", 21, 30),
    ("b4_31_50", 31, 50),
    ("b5_51_100", 51, 100),
    ("b6_101_plus", 101, 10**9),
]


def sha256_file(path: Path) -> str:
    """Return the SHA256 of a file, computed in 1 MiB chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def bucket_for(node_count: int) -> str | None:
    for name, lo, hi in BUCKETS:
        if lo <= node_count <= hi:
            return name
    return None


def load_corpus_index(corpus_path: Path) -> dict[str, list[str]]:
    """One read-only pass over the corpus; per-bucket sorted id lists."""
    buckets: dict[str, list[str]] = defaultdict(list)
    with open(corpus_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
                rec_id = rec.get("id")
                arch = rec.get("architecture") or {}
                nodes = arch.get("nodes") or []
            except (json.JSONDecodeError, AttributeError):
                continue
            if not rec_id:
                continue
            bucket = bucket_for(len(nodes))
            if bucket:
                buckets[bucket].append(str(rec_id))
    for key in buckets:
        buckets[key] = sorted(set(buckets[key]))
    return dict(buckets)


def allocate_sample(buckets: dict[str, list[str]], sample_size: int) -> list[str]:
    """Deterministic proportional-with-minimum allocation across buckets."""
    sizes = {name: len(ids) for name, ids in buckets.items()}
    if not sizes:
        return []
    total = sum(sizes.values())
    alloc = {name: max(1, sample_size * size // total) for name, size in sizes.items()}
    alloc = {name: min(alloc[name], sizes[name]) for name in sizes}
    remaining = sample_size - sum(alloc.values())
    while remaining > 0:
        for name in sorted(sizes):
            if remaining == 0:
                break
            if alloc[name] < sizes[name]:
                alloc[name] += 1
                remaining -= 1
    picked: list[str] = []
    for name in sorted(sizes):
        picked.extend(buckets[name][: alloc[name]])
    return sorted(picked)


def classify(node_id: str, node_type: str) -> dict[str, int | bool]:
    """Keyword-based role classification of a single node (id/type only)."""
    low = node_id.lower()
    entry = 1 if node_type == "ui" else 0
    entry_matches = sum(1 for kw in ENTRY_KEYWORDS if kw in low)
    data_matches = sum(1 for kw in DATA_KEYWORDS if kw in low)
    sec_matches = sum(1 for kw in SECURITY_KEYWORDS if kw in low)
    is_data = node_type in ("database", "cache", "queue") or data_matches > 0
    is_security = sec_matches > 0
    return {
        "entry": entry,
        "entry_matches": entry_matches,
        "data_matches": data_matches,
        "sec_matches": sec_matches,
        "is_data": is_data,
        "is_security": is_security,
    }