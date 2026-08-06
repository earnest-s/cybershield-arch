"""Validation gate for enriched samples.

Rejects samples with:
- invalid JSON / schema
- duplicate IDs / duplicate architectures
- disconnected graphs
- invalid node references in edges
- unsupported node types
- empty threats / empty recommendations

Valid samples written to dataset/validated/.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dataset.scripts.common import (
    ALLOWED_EDGE_LABELS,
    ALLOWED_NODE_TYPES,
    DATASET_DIR,
    canonical_architecture,
    existing_ids,
    sample_paths,
    setup_logger,
    write_json,
)
from backend.core.architecture_validator import is_weakly_connected

ENRICHED_DIR = DATASET_DIR / "enriched"
VALIDATED_DIR = DATASET_DIR / "validated"
LOGS_DIR = DATASET_DIR / "logs"

LOG = setup_logger("validate_dataset")


def validate(limit: int = 0, force: bool = False) -> int:
    if not ENRICHED_DIR.exists():
        LOG.error("Enriched directory not found: %s. Run enrich_dataset.py first.", ENRICHED_DIR)
        return 1

    existing = existing_ids(VALIDATED_DIR)
    VALIDATED_DIR.mkdir(parents=True, exist_ok=True)

    paths = sample_paths(ENRICHED_DIR)
    valid = 0
    rejected = 0

    seen_ids: set[str] = set()
    seen_archs: dict[str, str] = {}

    for path in paths:
        if limit and valid >= limit:
            break

        sample_id = path.stem
        if not force and sample_id in existing:
            LOG.info("%s: already validated, skipping", sample_id)
            continue

        try:
            sample = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            LOG.warning("%s: load failed: %s", sample_id, e)
            rejected += 1
            continue

        # Duplicate ID check
        if sample_id in seen_ids:
            LOG.warning("%s: duplicate ID in batch", sample_id)
            rejected += 1
            continue
        seen_ids.add(sample_id)

        architecture = sample.get("architecture", {})
        nodes = architecture.get("nodes", [])
        edges = architecture.get("edges", [])
        security = sample.get("security", {})

        # Basic structure
        if not isinstance(nodes, list) or not isinstance(edges, list):
            LOG.warning("%s: missing nodes/edges", sample_id)
            rejected += 1
            continue
        if not nodes or not edges:
            LOG.warning("%s: empty graph", sample_id)
            rejected += 1
            continue

        node_ids = {n.get("id") for n in nodes if isinstance(n, dict) and n.get("id")}
        if len(node_ids) != len(nodes):
            LOG.warning("%s: duplicate node IDs", sample_id)
            rejected += 1
            continue

        # Node type validation
        for n in nodes:
            if n.get("type") not in ALLOWED_NODE_TYPES:
                LOG.warning("%s: invalid node type %s", sample_id, n.get("type"))
                rejected += 1
                break
        else:
            # Edge validation
            edge_refs_ok = True
            for e in edges:
                src = e.get("source")
                tgt = e.get("target")
                if src not in node_ids or tgt not in node_ids:
                    LOG.warning("%s: dangling edge %s->%s", sample_id, src, tgt)
                    edge_refs_ok = False
                    break
                if e.get("label") not in ALLOWED_EDGE_LABELS:
                    LOG.warning("%s: invalid edge label %s", sample_id, e.get("label"))
                    edge_refs_ok = False
                    break
            if not edge_refs_ok:
                rejected += 1
                continue

            # Connectedness
            if not is_weakly_connected(nodes, edges):
                LOG.warning("%s: disconnected graph", sample_id)
                rejected += 1
                continue

            # Security completeness
            if not security.get("threats"):
                LOG.warning("%s: empty threats", sample_id)
                rejected += 1
                continue
            if not security.get("recommendations"):
                LOG.warning("%s: empty recommendations", sample_id)
                rejected += 1
                continue

            # Duplicate architecture check
            canon = canonical_architecture(architecture)
            if canon in seen_archs:
                LOG.warning("%s: duplicate architecture (same as %s)", sample_id, seen_archs[canon])
                rejected += 1
                continue
            seen_archs[canon] = sample_id

            # All checks passed
            out_path = VALIDATED_DIR / f"{sample_id}.json"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(sample, indent=2, ensure_ascii=False), encoding="utf-8")
            valid += 1
            seen_ids.add(sample_id)

            if valid % 500 == 0:
                LOG.info("Progress: %d valid, %d rejected", valid, rejected)

    LOG.info("Validation complete: %d valid, %d rejected", valid, rejected)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate enriched samples.")
    parser.add_argument("--limit", type=int, default=0, help="Max samples to validate (0 = all).")
    parser.add_argument("--force", action="store_true", help="Re-validate already validated samples.")
    args = parser.parse_args()
    try:
        return validate(args.limit, args.force)
    except Exception as e:
        LOG.exception("Validation failed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())