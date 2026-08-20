"""Independent post-generation verification for Phase 6 subgraph artifacts.

Standalone verifier: it does NOT import or reuse any assertion code from
extract_subgraphs.py. It reloads the generated shards and the immutable
parent corpus from disk, reconstructs the parent lookup, and re-verifies
every extracted subgraph from scratch (value-based, full-dict semantics):

  1. extracted node ids are a subset of parent node ids
  2. extracted edges are actual parent edges (full dict value equality:
     source/target/label plus any other edge metadata, direction preserved)
  3. every extracted edge has both endpoints retained
  4. the subgraph is weakly connected
  5. the canonical runtime contract passes (raise_if_invalid)
  6. provenance is complete and matches the actual parent graph
  7. no duplicate record ids / node ids / edge keys
  8. no fabricated content (nodes or edges not present in the parent)

Usage
-----
    uv run python dataset/scripts/verify_subgraphs.py \
        --outdir  dataset/training/subgraphs \
        --corpus  dataset/final/CyberShield_Dataset_v1_FULL.jsonl \
        --report  dataset/training/subgraphs/verification_report.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.core.architecture_validator import (  # noqa: E402
    is_weakly_connected,
    raise_if_invalid,
)

SECURITY_KEYS = ("required_controls", "missing_controls", "threats",
                 "recommendations", "risk_level", "security_score",
                 "attack_surface", "security_summary")
PROVENANCE_KEYS = ("parent_source_id", "parent_architecture_id",
                   "transformation_method", "transformation_version",
                   "selected_node_ids", "selected_edge_ids",
                   "node_retention_ratio", "edge_retention_ratio")


def canon(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True)


def verify_record(record: dict, parent: dict) -> tuple[bool, list[str]]:
    problems: list[str] = []
    pid = record.get("parent_id")
    if str(pid) != str(parent.get("id")):
        problems.append("parent_id_mismatch")

    parent_arch = parent.get("architecture") or {}
    parent_nodes = parent_arch.get("nodes") or []
    parent_edges = parent_arch.get("edges") or []
    parent_node_canon = {n.get("id"): canon(n) for n in parent_nodes}
    parent_edge_counter = Counter(canon(e) for e in parent_edges)

    arch = record.get("architecture") or {}
    nodes = arch.get("nodes") or []
    edges = arch.get("edges") or []
    node_ids = [n.get("id") for n in nodes]
    node_id_set = set(node_ids)

    # 1. node subset (full dict equality against parent nodes)
    for n in nodes:
        if n.get("id") not in parent_node_canon:
            problems.append(f"fabricated_node:{n.get('id')}")
        elif canon(n) != parent_node_canon[n["id"]]:
            problems.append(f"node_value_mismatch:{n.get('id')}")

    # 2. edge subset (full dict value equality; direction/label/metadata intact)
    extracted_edge_counter = Counter(canon(e) for e in edges)
    if not (extracted_edge_counter <= parent_edge_counter):
        problems.append("fabricated_edge_or_mismatch")
        for key, count in (extracted_edge_counter - parent_edge_counter).items():
            problems.append(f"edge_not_in_parent:{key}")

    # 3. endpoint integrity
    for e in edges:
        if e.get("source") not in node_id_set or e.get("target") not in node_id_set:
            problems.append("edge_endpoint_not_retained")

    # 4. connectedness
    if not is_weakly_connected(nodes, edges):
        problems.append("disconnected")

    # 5. canonical runtime contract
    try:
        raise_if_invalid(arch)
    except ValueError as exc:
        problems.append(f"contract_violation:{exc}")

    # 6. provenance completeness and consistency
    prov = (record.get("metadata") or {}).get("phase6") or {}
    for key in PROVENANCE_KEYS:
        if key not in prov or prov[key] in (None, ""):
            problems.append(f"provenance_missing:{key}")
    if prov.get("selected_node_ids") != node_ids:
        problems.append("provenance_node_ids_mismatch")
    expected_edge_keys = [f"{e.get('source')}->{e.get('target')}[{e.get('label')}]"
                          for e in edges]
    if prov.get("selected_edge_ids") != expected_edge_keys:
        problems.append("provenance_edge_ids_mismatch")
    if str(prov.get("parent_source_id")) != str(parent.get("id")):
        problems.append("provenance_parent_mismatch")
    exp_node_ratio = round(len(node_ids) / max(1, len(parent_nodes)), 4)
    exp_edge_ratio = round(len(edges) / max(1, len(parent_edges)), 4)
    if prov.get("node_retention_ratio") != exp_node_ratio:
        problems.append("provenance_node_ratio_mismatch")
    if prov.get("edge_retention_ratio") != exp_edge_ratio:
        problems.append("provenance_edge_ratio_mismatch")

    # 7. no duplicates inside the record
    if len(node_ids) != len(node_id_set):
        problems.append("duplicate_node_ids")
    if len(edges) != len(extracted_edge_counter):
        problems.append("duplicate_edges")

    # 8. security record shape (content itself is produced by the canonical
    # engine at extraction time; this verifies the artifact schema is intact)
    sec = record.get("security") or {}
    for key in SECURITY_KEYS:
        if key not in sec:
            problems.append(f"security_missing:{key}")

    return len(problems) == 0, problems


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Independent verification of Phase 6 subgraph artifacts.")
    parser.add_argument("--outdir", default="dataset/training/subgraphs")
    parser.add_argument("--corpus", default="dataset/final/CyberShield_Dataset_v1_FULL.jsonl")
    parser.add_argument("--report", default=None,
                        help="Report path (default: <outdir>/verification_report.json).")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    corpus_path = Path(args.corpus)
    manifest_path = outdir / "manifest.json"
    report_path = Path(args.report) if args.report else outdir / "verification_report.json"
    if not manifest_path.is_file():
        print(f"ERROR: manifest not found: {manifest_path}", file=sys.stderr)
        return 1
    if not corpus_path.is_file():
        print(f"ERROR: corpus not found: {corpus_path}", file=sys.stderr)
        return 1

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Reconstruct the parent lookup from the immutable corpus.
    parents: dict[str, dict] = {}
    source_count = 0
    with open(corpus_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            source_count += 1
            parents[str(rec.get("id"))] = rec
    print(f"corpus loaded: {source_count} records", flush=True)

    shard_checksums: dict[str, str] = {}
    verified_records = 0
    failures: list[dict] = []
    seen_record_ids: Counter = Counter()

    ranges = {rid: e for rid, e in manifest.get("ranges", {}).items()
              if e.get("status") == "complete"}
    for rid in sorted(ranges):
        shard = outdir / ranges[rid]["shard"]
        if not shard.is_file():
            failures.append({"range": rid, "shard": str(shard), "error": "shard_missing"})
            continue
        import hashlib
        h = hashlib.sha256()
        with open(shard, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        shard_checksums[rid] = h.hexdigest()
        if shard_checksums[rid] != ranges[rid].get("shard_sha256"):
            failures.append({"range": rid, "error": "shard_checksum_mismatch"})
            continue
        with open(shard, "r", encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)
                verified_records += 1
                seen_record_ids[str(record.get("id"))] += 1
                parent = parents.get(str(record.get("parent_id")))
                if parent is None:
                    failures.append({"record": record.get("id"),
                                     "error": "parent_not_found"})
                    continue
                ok, problems = verify_record(record, parent)
                if not ok:
                    failures.append({"record": record.get("id"),
                                     "parent": str(parent.get("id")),
                                     "problems": problems})

    dup_record_ids = [rid for rid, c in seen_record_ids.items() if c > 1]
    report = {
        "corpus": {
            "path": str(corpus_path),
            "record_count": source_count,
            "manifest_record_count": manifest.get("source", {}).get("record_count"),
        },
        "manifest_source_sha256_unchanged": manifest.get("source", {}).get(
            "sha256_unchanged"),
        "shards_checked": {rid: ranges[rid]["shard"] for rid in sorted(ranges)},
        "shard_checksums": {rid: ranges[rid]["shard_sha256"] for rid in sorted(ranges)},
        "shard_checksums_recomputed": shard_checksums,
        "shard_checksum_mismatches": [
            rid for rid in ranges if shard_checksums.get(rid) != ranges[rid].get("shard_sha256")
        ],
        "records_verified": verified_records,
        "records_failing": len(failures),
        "failures": failures[:50],
        "failure_sample_count": len(failures),
        "duplicate_record_ids": dup_record_ids,
        "overall_pass": (verified_records > 0 and len(failures) == 0
                         and not dup_record_ids
                         and manifest.get("source", {}).get("sha256_unchanged") is True),
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["overall_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())