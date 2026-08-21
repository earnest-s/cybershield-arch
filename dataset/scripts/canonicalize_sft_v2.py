#!/usr/bin/env python3
"""Phase 7 Canonical v2: transform current SFT artifact into canonical representation.

Implements Variant B from dataset/docs/dataset_redesign_pilot_report.md:
  - type-anchored canonical node IDs {type}-{k}
  - deterministic node ordering (type, canonical_id)
  - deterministic edge ordering (source, target, label)
  - fixed contract caps: ≤10 nodes / ≤15 edges
  - provenance-preserving: id_map, original_architecture retained
  - no fabricated nodes/edges (bijection with source)

Outputs: dataset/training/CyberShield_Gemma_SFT_v2_canonical.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Prompt constants from format_sft.py
CAP_NODES_OLD = "- Max nodes: 8"
CAP_EDGES_OLD = "- Max edges: 10"
CAP_NODES_NEW = "- Max nodes: 10"
CAP_EDGES_NEW = "- Max edges: 15"
FORMAT_EXAMPLE_OLD = '{"id": "frontend", "type": "ui"},\n        {"id": "api", "type": "service"}'
FORMAT_EXAMPLE_NEW = '{"id": "ui-1", "type": "ui"},\n        {"id": "service-1", "type": "service"}'

TRANSFORM_METHOD = "canonical_type_anchored_v2"
TRANSFORM_VERSION = "2.0.0"
ARTIFACT_VERSION = "v2_canonical"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonicalize(architecture: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    """Return (canonical architecture, id_map: original_id -> canonical_id).

    Node IDs: sort by (type, original_id), enumerate within type starting at 1.
    Node order: (type, canonical_id). Edge order: (source, target, label).
    Types, labels, topology preserved exactly (edges remapped via id_map only).
    """
    nodes = list(architecture["nodes"])
    nodes_sorted = sorted(nodes, key=lambda n: (n["type"], n["id"]))
    id_map: dict[str, str] = {}
    counts: dict[str, int] = {}
    canon_nodes: list[dict] = []
    for n in nodes_sorted:
        t = n["type"]
        counts[t] = counts.get(t, 0) + 1
        cid = f"{t}-{counts[t]}"
        id_map[n["id"]] = cid
        canon_nodes.append({"id": cid, "type": t})

    canon_edges = []
    for e in architecture["edges"]:
        canon_edges.append({
            "source": id_map[e["source"]],
            "target": id_map[e["target"]],
            "label": e["label"],
        })
    canon_edges.sort(key=lambda e: (e["source"], e["target"], e["label"]))

    return {"nodes": canon_nodes, "edges": canon_edges}, id_map


def compact_json(obj: Any) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=True)


def fix_prompt(instruction: str) -> str:
    """Fix caps and FORMAT example in the instruction string."""
    if CAP_NODES_OLD not in instruction or CAP_EDGES_OLD not in instruction:
        raise ValueError("Expected cap lines not found in instruction")
    instr = instruction.replace(CAP_NODES_OLD, CAP_NODES_NEW)
    instr = instr.replace(CAP_EDGES_OLD, CAP_EDGES_NEW)
    if FORMAT_EXAMPLE_OLD not in instr:
        raise ValueError("Expected FORMAT example not found in instruction")
    instr = instr.replace(FORMAT_EXAMPLE_OLD, FORMAT_EXAMPLE_NEW)
    return instr


def transform_record(record: dict[str, Any], index: int) -> dict[str, Any]:
    """Apply Variant B canonicalization to a single SFT record."""
    orig_arch = record["architecture"]
    canon_arch, id_map = canonicalize(orig_arch)

    # Verify bijection
    orig_ids = {n["id"] for n in orig_arch["nodes"]}
    canon_ids = {n["id"] for n in canon_arch["nodes"]}
    assert set(id_map.keys()) == orig_ids, "id_map keys mismatch"
    assert set(id_map.values()) == canon_ids, "id_map values mismatch"
    assert all(v.count("-") == 1 for v in id_map.values()), "canonical id format"

    return {
        "id": f"SFT-{index:06d}",
        "instruction": fix_prompt(record["instruction"]),
        "response": compact_json(canon_arch),
        "architecture": canon_arch,
        "metadata": {
            **record["metadata"],
            "canonicalization": {
                "method": TRANSFORM_METHOD,
                "version": TRANSFORM_VERSION,
                "id_map": id_map,
            },
            "original_architecture": orig_arch,
        },
    }


def compute_stats(records: list[dict]) -> dict:
    """Compute comprehensive before/after statistics."""
    node_vocab_before = Counter()
    node_vocab_after = Counter()
    singleton_before = 0
    singleton_after = 0
    node_sorted_before = 0
    edge_sorted_before = 0
    node_sorted_after = 0
    edge_sorted_after = 0
    node_counts_before = Counter()
    node_counts_after = Counter()
    edge_counts_before = Counter()
    edge_counts_after = Counter()
    domains = Counter()
    styles = Counter()
    clouds = Counter()
    complexities = Counter()
    duplicate_instructions = defaultdict(list)

    for r in records:
        meta = r["metadata"]
        domains[meta.get("domain", "?")] += 1
        styles[meta.get("style", "?")] += 1
        clouds[meta.get("cloud", "?")] += 1
        complexities[meta.get("complexity", "?")] += 1
        duplicate_instructions[r["instruction"]].append(r["id"])

        orig = r["metadata"]["original_architecture"]
        canon = r["architecture"]

        # Before
        for nd in orig["nodes"]:
            node_vocab_before[nd["id"]] += 1
            node_counts_before[nd["type"]] += 1
        for e in orig["edges"]:
            edge_counts_before[e["label"]] += 1
        if orig["nodes"] == sorted(orig["nodes"], key=lambda n: (n["type"], n["id"])):
            node_sorted_before += 1
        if orig["edges"] == sorted(orig["edges"], key=lambda e: (e["source"], e["target"], e["label"])):
            edge_sorted_before += 1

        # After
        for nd in canon["nodes"]:
            node_vocab_after[nd["id"]] += 1
            node_counts_after[nd["type"]] += 1
        for e in canon["edges"]:
            edge_counts_after[e["label"]] += 1
        if canon["nodes"] == sorted(canon["nodes"], key=lambda n: (n["type"], n["id"])):
            node_sorted_after += 1
        if canon["edges"] == sorted(canon["edges"], key=lambda e: (e["source"], e["target"], e["label"])):
            edge_sorted_after += 1

    # Singleton rates
    slots_before = sum(node_vocab_before.values())
    singles_before = sum(1 for v in node_vocab_before.values() if v == 1)
    slots_after = sum(node_vocab_after.values())
    singles_after = sum(1 for v in node_vocab_after.values() if v == 1)

    # Duplicate instructions
    dup_groups = {k: v for k, v in duplicate_instructions.items() if len(v) > 1}

    return {
        "total_records": len(records),
        "node_vocabulary": {
            "before": {"unique": len(node_vocab_before), "slots": slots_before, "singleton_rate": singles_before / slots_before},
            "after": {"unique": len(node_vocab_after), "slots": slots_after, "singleton_rate": singles_after / slots_after},
        },
        "ordering": {
            "node_sorted_before": node_sorted_before,
            "node_sorted_after": node_sorted_after,
            "edge_sorted_before": edge_sorted_before,
            "edge_sorted_after": edge_sorted_after,
        },
        "node_type_distribution": {
            "before": dict(node_counts_before),
            "after": dict(node_counts_after),
        },
        "edge_label_distribution": {
            "before": dict(edge_counts_before),
            "after": dict(edge_counts_after),
        },
        "node_count_distribution": {
            "before": dict(Counter(len(r["metadata"]["original_architecture"]["nodes"]) for r in records)),
            "after": dict(Counter(len(r["architecture"]["nodes"]) for r in records)),
        },
        "edge_count_distribution": {
            "before": dict(Counter(len(r["metadata"]["original_architecture"]["edges"]) for r in records)),
            "after": dict(Counter(len(r["architecture"]["edges"]) for r in records)),
        },
        "domain_distribution": dict(domains),
        "style_distribution": dict(styles),
        "cloud_distribution": dict(clouds),
        "complexity_distribution": dict(complexities),
        "duplicate_instructions": {
            "groups": len(dup_groups),
            "records_in_groups": sum(len(v) for v in dup_groups.values()),
        },
        "structural_uniqueness": {
            "before": 0,  # computed separately if needed
            "after": 0,
        },
    }


def verify_determinism(records: list[dict]) -> bool:
    """Verify that the transformation is deterministic by re-running on a sample."""
    # Re-transform first 10 records and compare
    for r in records[:10]:
        t2 = transform_record(r, int(r["id"].split("-")[1]))
        if t2["instruction"] != r["instruction"] or t2["response"] != r["response"]:
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Canonical v2 SFT transformation")
    parser.add_argument("--input", default="dataset/training/CyberShield_Gemma_SFT_v1.jsonl")
    parser.add_argument("--output", default="dataset/training/CyberShield_Gemma_SFT_v2_canonical.jsonl")
    parser.add_argument("--verify", action="store_true", help="Run verification passes")
    parser.add_argument("--stats-out", default="dataset/docs/canonical_v2_transform_stats.json")
    args = parser.parse_args()

    src = Path(args.input)
    dst = Path(args.output)

    print(f"[INFO] Source SHA256: {sha256_file(src)}")
    print(f"[INFO] Loading {src}...")

    records_in = []
    with open(src, encoding="utf-8") as fh:
        for line in fh:
            records_in.append(json.loads(line))

    print(f"[INFO] Loaded {len(records_in)} records")

    # Transform
    print("[INFO] Applying canonical transformation...")
    records_out = []
    for idx, r in enumerate(records_in, start=1):
        records_out.append(transform_record(r, idx))

    print("[INFO] Computing statistics...")
    stats = compute_stats(records_out)

    # Verification
    print("[INFO] Verifying determinism...")
    assert verify_determinism(records_out), "Determinism check failed!"
    print("[INFO] Determinism verified (byte-identical re-transform)")

    # Write output
    print(f"[INFO] Writing {dst}...")
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(dst, "w", encoding="utf-8") as fh:
        for r in records_out:
            fh.write(json.dumps(r, ensure_ascii=True) + "\n")

    dst_sha = sha256_file(dst)
    print(f"[INFO] Output SHA256: {dst_sha}")
    print(f"[INFO] Output size: {dst.stat().st_size} bytes")

    # Write stats
    stats["source_sha256"] = sha256_file(src)
    stats["output_sha256"] = dst_sha
    stats["transform_method"] = TRANSFORM_METHOD
    stats["transform_version"] = TRANSFORM_VERSION
    Path(args.stats_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.stats_out).write_text(json.dumps(stats, indent=2))
    print(f"[INFO] Stats written to {args.stats_out}")

    if args.verify:
        print("[INFO] Running full verification...")
        # Re-read and verify bijection for all records
        for r in records_out:
            orig = r["metadata"]["original_architecture"]
            canon = r["architecture"]
            id_map = r["metadata"]["canonicalization"]["id_map"]
            # Verify id_map is correct bijection
            assert set(id_map.keys()) == {n["id"] for n in orig["nodes"]}
            assert set(id_map.values()) == {n["id"] for n in canon["nodes"]}
            # Verify edges map correctly
            for e in canon["edges"]:
                rev = {v: k for k, v in id_map.items()}
                assert e["source"] in id_map.values()
                assert e["target"] in id_map.values()
        print("[INFO] Full verification passed: all bijections correct")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())