#!/usr/bin/env python3
"""Phase 7: transform Phase 6 contract-aligned subgraphs into the SFT artifact.

Deterministic, resumable, provenance-preserving transformation producing
``dataset/training/CyberShield_Gemma_SFT_v1.jsonl``.

Each output record is a single-turn Gemma chat sample:
  instruction  -> the EXACT runtime generation prompt from
                  backend/core/inference.py:generate_architecture, with the
                  parent record's instruction substituted for {description}
  response     -> compact architecture JSON ({nodes, edges}) only
  architecture -> parsed target object (for programmatic validation)
  metadata     -> provenance (parent ids, Phase 6 transformation details,
                  domain/style/cloud/complexity, compact security fingerprint)

The target is architecture JSON ONLY. Security data is computed
deterministically by the runtime security engine at inference time and is
never a training target (Phase 5 decision, training_readiness_report.md).

Splits (train/validation/test = 90/5/5) are assigned cluster-wise: records
are grouped by identical node-id sets (leakage-safe) and whole clusters are
allocated with a deterministic largest-first greedy fill. No random number
generation is used; output is byte-deterministic.

Usage:
    uv run python dataset/scripts/format_sft.py
    uv run python dataset/scripts/format_sft.py --dry-run
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PROMPT_TEMPLATE = """
You are a senior software architect.

Convert the following system description into a CLEAN architecture graph.

RULES:
- Use only meaningful components
- No duplicate edges
- No redundant connections
- Keep architecture minimal and logical

FORMAT:
{{
    "nodes": [
        {{"id": "frontend", "type": "ui"}},
        {{"id": "api", "type": "service"}}
    ],
    "edges": [
        {{"source": "frontend", "target": "api", "label": "HTTP"}}
    ]
}}

CONSTRAINTS:
- Each edge must be unique
- Do NOT repeat same connection
- Use proper labels: HTTP, DB Query, Async, Cache
- Max nodes: 8
- Max edges: 10

Description:
{description}

ONLY return JSON. No explanation.
"""

HARD_NODE_LIMIT = 10
HARD_EDGE_LIMIT = 15

SPLIT_RATIOS = {"train": 0.90, "validation": 0.05, "test": 0.05}


def render_prompt(instruction: str) -> str:
    """Render the runtime generation prompt with the instruction substituted.

    Verbatim copy of the template in backend/core/inference.py
    (generate_architecture). Keep both in sync; a drift check is part of
    dataset/scripts/verify_sft.py.
    """
    return PROMPT_TEMPLATE.format(description=instruction.strip())


def load_subgraphs(input_dir: Path, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for rid in sorted(manifest["ranges"]):
        shard = input_dir / f"subgraphs_{rid}.jsonl"
        if not shard.exists():
            raise FileNotFoundError(f"Missing shard: {shard}")
        for line in shard.open(encoding="utf-8"):
            records.append(json.loads(line))
    return records


def node_set_key(architecture: dict[str, Any]) -> tuple[str, ...]:
    """Deterministic cluster key: sorted node ids (identical sets group)."""
    return tuple(sorted(node["id"] for node in architecture["nodes"]))


def build_clusters(records: list[dict[str, Any]]) -> list[list[int]]:
    buckets: dict[tuple[str, ...], list[int]] = {}
    for idx, record in enumerate(records):
        key = node_set_key(record["architecture"])
        buckets.setdefault(key, []).append(idx)
    clusters = sorted(
        buckets.values(),
        key=lambda members: (-len(members), members[0]),
    )
    return clusters


def assign_splits(clusters: list[list[int]], records: list[dict[str, Any]]) -> dict[int, str]:
    """Deterministic size-tier-stratified greedy split allocation.

    Clusters are grouped by node count (identical node sets imply identical
    node counts) and processed smallest tiers first, clusters largest-first
    within a tier. Each cluster is allocated to the split with the largest
    relative deficit (remaining / target), ties broken by split order
    (train, validation, test). This reproduces the exact 90/5/5 totals while
    keeping the risk profile of every split close to the artifact overall
    (small graphs are MEDIUM-risk-heavy; an unstratified fill concentrates
    them in validation, documented in phase7_training_report.md).

    Perfection is impossible at the smallest tiers (a 53-record near-dup
    cluster cannot be subdivided without leaking), so tiers 2-5 wobble by a
    few percent; this is reported, not hidden.
    """
    order = ["train", "validation", "test"]
    tiers: dict[int, list[list[int]]] = {}
    for members in clusters:
        node_count = len(records[members[0]]["architecture"]["nodes"])
        tiers.setdefault(node_count, []).append(members)
    total = sum(len(members) for members in clusters)
    targets = {name: round(total * SPLIT_RATIOS[name]) for name in order}
    assigned = {name: 0 for name in order}
    allocation: dict[int, str] = {}
    for node_count in sorted(tiers):
        for members in sorted(tiers[node_count], key=lambda c: (-len(c), c[0])):
            target_split = max(
                order,
                key=lambda name: (
                    (targets[name] - assigned[name]) / targets[name],
                    order.index(name),
                ),
            )
            for idx in members:
                allocation[idx] = target_split
            assigned[target_split] += len(members)
    return allocation


def build_record(index: int, record: dict[str, Any], split: str) -> dict[str, Any]:
    architecture = record["architecture"]
    metadata = record.get("metadata", {})
    phase6 = metadata.get("phase6", {})
    security = record.get("security", {})
    return {
        "id": f"SFT-{index:06d}",
        "instruction": render_prompt(record.get("instruction", "")),
        "response": json.dumps(architecture, ensure_ascii=True, separators=(",", ":")),
        "architecture": architecture,
        "metadata": {
            "domain": metadata.get("domain"),
            "style": metadata.get("style"),
            "cloud": metadata.get("cloud"),
            "complexity": metadata.get("complexity"),
            "source": (
                "ajibawa-2023/Technical-Architectures-Large (HuggingFace) via "
                "CyberShield_Dataset_v1_FULL -> Phase 6 subgraph (sacce_connected_subgraph_v1)"
            ),
            "parent_source_id": phase6.get("parent_source_id"),
            "parent_architecture_id": phase6.get("parent_architecture_id"),
            "phase6": {
                "transformation_method": phase6.get("transformation_method"),
                "transformation_version": phase6.get("transformation_version"),
                "contract": phase6.get("contract"),
                "node_retention_ratio": phase6.get("node_retention_ratio"),
                "edge_retention_ratio": phase6.get("edge_retention_ratio"),
                "selected_node_ids": phase6.get("selected_node_ids"),
                "selected_edge_ids": phase6.get("selected_edge_ids"),
            },
            "security": {
                "risk_level": security.get("risk_level"),
                "security_score": security.get("security_score"),
            },
            "split": split,
        },
    }


def write_artifact(records: list[dict[str, Any]], allocation: dict[int, str], output: Path) -> None:
    order = ["train", "validation", "test"]
    ordered = sorted(
        range(len(records)),
        key=lambda idx: (order.index(allocation[idx]), records[idx]["metadata"]["phase6"]["parent_source_id"]),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as fh:
        for pos, idx in enumerate(ordered, start=1):
            fh.write(json.dumps(build_record(pos, records[idx], allocation[idx]), ensure_ascii=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", default="dataset/training/subgraphs")
    parser.add_argument("--output", default="dataset/training/CyberShield_Gemma_SFT_v1.jsonl")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    manifest = json.loads((input_dir / "manifest.json").read_text(encoding="utf-8"))

    records = load_subgraphs(input_dir, manifest)
    print(f"[INFO] loaded {len(records)} subgraph records")

    clusters = build_clusters(records)
    print(f"[INFO] node-set clusters: {len(clusters)} (multi-record clusters: "
          f"{sum(1 for c in clusters if len(c) > 1)})")

    allocation = assign_splits(clusters, records)
    from collections import Counter
    counts = Counter(allocation.values())
    for name in ("train", "validation", "test"):
        print(f"[INFO] split {name}: {counts[name]} ({counts[name] / len(records) * 100:.2f}%)")

    if args.dry_run:
        print("[INFO] dry run complete; no artifact written")
        return 0

    output = Path(args.output)
    write_artifact(records, allocation, output)
    print(f"[INFO] wrote {output} ({output.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())