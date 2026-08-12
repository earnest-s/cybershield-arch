"""Phase 5 — training dataset readiness analysis for the immutable full corpus.

Reads ``dataset/final/CyberShield_Dataset_v1_FULL.jsonl`` (READ-ONLY) and writes
``dataset/docs/training_readiness_stats.json`` plus a console summary.

It reuses the canonical backend vocabulary and validator so that every check
mirrors the runtime contract:

- ``backend.core.architecture_schema`` — allowed node types / edge labels,
  canonical dedup fingerprint, production guardrails.
- ``backend.core.architecture_validator.collect_issues`` — unsupported types,
  unsupported labels, dangling edges, self-loops, duplicate edges, id
  collisions (size-guardrail issues are intentionally NOT treated as failures
  here: the corpus is a *source* corpus, not a runtime generation).

It does NOT modify the corpus, does NOT create training data, and does NOT
change any pipeline policy. The source row of each record is recovered from
its id (``CSA-<row>``, assigned by convert_dataset.py from the HF row id) so
the source-regime analysis is exact without needing the purged staging dirs.

Usage:
    uv run python -m dataset.scripts.training_readiness
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import networkx as nx

from backend.core.architecture_schema import (
    ALLOWED_EDGE_LABELS,
    ALLOWED_NODE_TYPES,
    HARD_EDGE_LIMIT,
    HARD_NODE_LIMIT,
    MAX_EDGES,
    MAX_NODES,
    canonical_architecture,
)
from backend.core.architecture_validator import collect_issues
from dataset.scripts.common import DATASET_DIR, setup_logger

CORPUS = DATASET_DIR / "final" / "CyberShield_Dataset_v1_FULL.jsonl"
OUT = DATASET_DIR / "docs" / "training_readiness_stats.json"

LOG = setup_logger("training_readiness")

# (label, lo, hi) source-row ranges used for the regime-shift analysis.
REGIME_RANGES = [
    ("0-49,999", 0, 50_000),
    ("50,000-99,999", 50_000, 100_000),
    ("100,000-149,999", 100_000, 150_000),
    ("150,000-199,999", 150_000, 200_000),
    ("200,000-249,999", 200_000, 250_000),
    ("250,000-293,640", 250_000, 293_643),
]

NODE_BUCKETS = [(0, 10), (11, 20), (21, 30), (31, 50), (51, 100), (101, 200), (201, 500), (501, None)]
EDGE_BUCKETS = [(0, 10), (11, 20), (21, 30), (31, 50), (51, 100), (101, 200), (201, 500), (501, None)]


def percentile(sorted_vals: list[float], p: float) -> float:
    """Linear-interpolation percentile matching numpy's default method."""
    if not sorted_vals:
        return 0.0
    n = len(sorted_vals)
    if n == 1:
        return float(sorted_vals[0])
    pos = (n - 1) * (p / 100.0)
    lo = int(pos)
    hi = min(lo + 1, n - 1)
    frac = pos - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def _bucket(key: int, buckets: list[tuple]) -> str:
    for lo, hi in buckets:
        if hi is None and key >= lo:
            return f"{lo}-+"
        if lo <= key <= hi:
            return f"{lo}-{hi}"
    return "other"


def _dist_summary(values: list[int]) -> dict:
    sv = sorted(values)
    return {
        "min": min(values),
        "max": max(values),
        "mean": round(sum(values) / len(values), 2),
        "median": percentile(sv, 50),
        "p50": percentile(sv, 50),
        "p75": percentile(sv, 75),
        "p90": percentile(sv, 90),
        "p95": percentile(sv, 95),
        "p99": percentile(sv, 99),
    }


def load_records() -> list[dict]:
    if not CORPUS.exists():
        raise FileNotFoundError(f"Corpus not found: {CORPUS}")
    records = []
    with CORPUS.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                records.append(json.loads(line))
    return records


def analyze(records: list[dict]) -> dict:
    total = len(records)

    node_counts: list[int] = []
    edge_counts: list[int] = []
    comp_counts: list[int] = []
    risk = Counter()
    threats_per_record = Counter()
    missing_per_record = Counter()
    required_per_record = Counter()
    severity = Counter()
    domains = Counter()
    styles = Counter()
    clouds = Counter()
    complexity = Counter()
    risk_by_domain: dict[str, Counter] = {}
    risk_by_style: dict[str, Counter] = {}
    risk_by_cloud: dict[str, Counter] = {}

    ids = set()
    canon_groups: dict[str, list[str]] = {}
    full_groups: dict[str, list[str]] = {}
    node_set_buckets: dict[frozenset, list[int]] = {}
    regime = Counter()
    regime_nodes = Counter()
    regime_edges = Counter()

    unsupported_node_types = Counter()
    unsupported_edge_labels = Counter()
    dangling_edges = 0
    self_loops = 0
    dup_edges = 0
    id_collisions = 0

    security_summary_present = 0
    security_missing_fields = Counter()
    node_extra_keys = 0
    edge_extra_keys = 0
    top_missing_fields = Counter()
    records_over_schema_max_nodes = 0
    records_over_schema_max_edges = 0

    le_8 = le_10 = le_15 = le_20 = le_30 = 0
    over_hard = 0

    for rec in records:
        rid = int(rec["id"].split("-")[1])
        ids.add(rid)
        for label, lo, hi in REGIME_RANGES:
            if lo <= rid < hi:
                regime[label] += 1
                break

        arch = rec.get("architecture", {})
        nodes = arch.get("nodes", [])
        edges = arch.get("edges", [])
        n, m = len(nodes), len(edges)
        node_counts.append(n)
        edge_counts.append(m)
        regime_nodes[label] += n
        regime_edges[label] += m

        # Application compatibility
        if n <= 8:
            le_8 += 1
        if n <= 10:
            le_10 += 1
        if n <= 15:
            le_15 += 1
        if n <= 20:
            le_20 += 1
        if n <= 30:
            le_30 += 1
        if n > HARD_NODE_LIMIT or m > HARD_EDGE_LIMIT:
            over_hard += 1
        if n > 100:
            records_over_schema_max_nodes += 1
        if m > 200:
            records_over_schema_max_edges += 1

        # Structural / schema checks via the canonical validator (size excluded)
        for issue in collect_issues(arch):
            if issue.rule == "unsupported_node_type":
                unsupported_node_types[issue.message] += 1
            elif issue.rule == "unsupported_edge_label":
                unsupported_edge_labels[issue.message] += 1
            elif issue.rule == "dangling_edge":
                dangling_edges += 1
            elif issue.rule == "self_loop":
                self_loops += 1
            elif issue.rule == "duplicate_edge":
                dup_edges += 1
            elif issue.rule == "node_id_collision":
                id_collisions += 1

        for node in nodes:
            extra = set(node.keys()) - {"id", "type"}
            node_extra_keys += len(extra)
        for edge in edges:
            extra = set(edge.keys()) - {"source", "target", "label"}
            edge_extra_keys += len(extra)

        # Components (weakly connected, undirected)
        G = nx.Graph()
        G.add_nodes_from(node["id"] for node in nodes)
        G.add_edges_from((e["source"], e["target"]) for e in edges)
        comp_counts.append(nx.number_connected_components(G))

        # Security
        sec = rec.get("security", {})
        rl = sec.get("risk_level")
        risk[rl] += 1
        threats = sec.get("threats", [])
        threats_per_record[len(threats)] += 1
        for t in threats:
            severity[t.get("severity")] += 1
        missing_per_record[len(sec.get("missing_controls", []))] += 1
        required_per_record[len(sec.get("required_controls", []))] += 1
        if sec.get("security_summary"):
            security_summary_present += 1
        if "security_score" not in sec:
            security_missing_fields["security_score_key_absent"] += 1
        elif sec["security_score"] == 0:
            security_missing_fields["security_score_zero"] += 1
        if "attack_surface" not in sec or not isinstance(sec.get("attack_surface"), dict):
            security_missing_fields["attack_surface_key_absent"] += 1
        for f in ("required_controls", "missing_controls", "threats", "recommendations",
                  "risk_level", "security_summary"):
            if not sec.get(f):
                security_missing_fields[f] += 1

        # Metadata / diversity
        meta = rec.get("metadata", {})
        for f in ("domain", "style", "cloud", "complexity", "source", "version"):
            if not meta.get(f):
                top_missing_fields[f] += 1
        domain = meta.get("domain", "")
        style = meta.get("style", "")
        cloud = meta.get("cloud", "")
        domains[domain] += 1
        styles[style] += 1
        clouds[cloud] += 1
        complexity[meta.get("complexity", "")] += 1
        risk_by_domain.setdefault(domain, Counter())[rl] += 1
        risk_by_style.setdefault(style, Counter())[rl] += 1
        risk_by_cloud.setdefault(cloud, Counter())[rl] += 1

        # Duplication fingerprints
        canon = canonical_architecture(arch)
        canon_groups.setdefault(canon, []).append(rec["id"])
        full_key = json.dumps({k: v for k, v in rec.items() if k != "id"}, sort_keys=True)
        full_groups.setdefault(full_key, []).append(rec["id"])
        node_set_buckets.setdefault(frozenset(node["id"] for node in nodes), []).append(rid)

    # --- Duplication rollups ---
    canon_dup_groups = {k: v for k, v in canon_groups.items() if len(v) > 1}
    full_dup_groups = {k: v for k, v in full_groups.items() if len(v) > 1}
    shared_buckets = {k: v for k, v in node_set_buckets.items() if len(v) > 1}
    node_set_shared = sum(len(v) for v in shared_buckets.values())

    # Structural near-duplicates: identical node sets, Jaccard(edge sets) >= 0.9,
    # excluding exact canonical duplicates.
    near_dup_ids: set[int] = set()
    near_dup_pairs = 0
    for bucket in shared_buckets.values():
        edges_by_row: dict[int, frozenset] = {}
        for rid in bucket:
            arch = next(
                r["architecture"]
                for r in records
                if int(r["id"].split("-")[1]) == rid
            )
            edges_by_row[rid] = frozenset(
                (e["source"], e["target"], e["label"]) for e in arch.get("edges", [])
            )
        rows = list(edges_by_row)
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                a, b = edges_by_row[rows[i]], edges_by_row[rows[j]]
                if not a and not b:
                    jac = 1.0
                else:
                    jac = len(a & b) / len(a | b)
                if jac >= 0.9:
                    ca = canonical_architecture(
                        next(r["architecture"] for r in records if int(r["id"].split("-")[1]) == rows[i])
                    )
                    cb = canonical_architecture(
                        next(r["architecture"] for r in records if int(r["id"].split("-")[1]) == rows[j])
                    )
                    if ca != cb:
                        near_dup_ids.update((rows[i], rows[j]))
                        near_dup_pairs += 1

    # --- Regime rollups ---
    regime_stats = {}
    for label, lo, hi in REGIME_RANGES:
        c = regime[label]
        regime_stats[label] = {
            "accepted": c,
            "node_mean": round(regime_nodes[label] / c, 1) if c else 0,
            "edge_mean": round(regime_edges[label] / c, 1) if c else 0,
        }

    single_component = sum(1 for c in comp_counts if c == 1)

    stats = {
        "total": total,
        "nodes": _dist_summary(node_counts),
        "edges": _dist_summary(edge_counts),
        "components": _dist_summary(comp_counts),
        "single_component_pct": round(100.0 * single_component / total, 1),
        "node_buckets": dict(Counter(_bucket(n, NODE_BUCKETS) for n in node_counts)),
        "edge_buckets": dict(Counter(_bucket(m, EDGE_BUCKETS) for m in edge_counts)),
        "compat": {
            "le_8": le_8,
            "le_10": le_10,
            "le_15": le_15,
            "le_20": le_20,
            "le_30": le_30,
            "pct_le_10": round(100.0 * le_10 / total, 2),
            "pct_le_15": round(100.0 * le_15 / total, 2),
            "pct_le_20": round(100.0 * le_20 / total, 2),
            "pct_le_30": round(100.0 * le_30 / total, 2),
            "pct_gt_30": round(100.0 * (total - le_30) / total, 2),
        },
        "guardrails": {
            "MAX_NODES_soft": MAX_NODES,
            "MAX_EDGES_soft": MAX_EDGES,
            "HARD_NODE_LIMIT": HARD_NODE_LIMIT,
            "HARD_EDGE_LIMIT": HARD_EDGE_LIMIT,
            "records_over_hard_limit": over_hard,
            "pct_over_hard_limit": round(100.0 * over_hard / total, 2),
        },
        "schema_compat": {
            "unsupported_node_type_records": len(unsupported_node_types),
            "unsupported_edge_label_records": len(unsupported_edge_labels),
            "dangling_edges": dangling_edges,
            "self_loops": self_loops,
            "duplicate_edges": dup_edges,
            "node_id_collisions": id_collisions,
            "node_extra_keys": node_extra_keys,
            "edge_extra_keys": edge_extra_keys,
            "records_over_schema_max_nodes_100": records_over_schema_max_nodes,
            "records_over_schema_max_edges_200": records_over_schema_max_edges,
            "top_missing_fields": dict(top_missing_fields),
        },
        "security": {
            "risk": dict(risk),
            "severity": dict(severity),
            "threats_per_record": dict(threats_per_record),
            "missing_per_record": dict(missing_per_record),
            "required_per_record": dict(required_per_record),
            "security_summary_present": security_summary_present,
            "missing_security_fields": dict(security_missing_fields),
        },
        "diversity": {
            "domains": dict(domains),
            "styles": dict(styles),
            "clouds": dict(clouds),
            "complexity": dict(complexity),
        },
        "risk_by_domain": {k: dict(v) for k, v in risk_by_domain.items()},
        "risk_by_style": {k: dict(v) for k, v in risk_by_style.items()},
        "risk_by_cloud": {k: dict(v) for k, v in risk_by_cloud.items()},
        "duplication": {
            "duplicate_ids": total - len(ids),
            "canonical_arch_dup_groups": len(canon_dup_groups),
            "canonical_arch_dup_records": sum(len(v) for v in canon_dup_groups.values()),
            "full_record_dup_groups": len(full_dup_groups),
            "node_set_shared_records": node_set_shared,
            "struct_near_dup_pairs": near_dup_pairs,
            "struct_near_dup_records": len(near_dup_ids),
        },
        "regime": regime_stats,
    }
    return stats


def main() -> int:
    LOG.info("Loading corpus %s ...", CORPUS)
    records = load_records()
    LOG.info("Loaded %d records", len(records))

    LOG.info("Analyzing ...")
    stats = analyze(records)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2, ensure_ascii=False)
    LOG.info("Wrote %s", OUT)

    # Console summary
    print(f"\nTotal records: {stats['total']:,}")
    print("Nodes:", json.dumps(stats["nodes"]))
    print("Edges:", json.dumps(stats["edges"]))
    print("Components:", json.dumps(stats["components"]),
          f"| single-component {stats['single_component_pct']}%")
    print("Compat:", json.dumps(stats["compat"]))
    print("Over hard guardrail:", stats["guardrails"]["records_over_hard_limit"],
          f"({stats['guardrails']['pct_over_hard_limit']}%)")
    print("Risk:", json.dumps(stats["security"]["risk"]))
    print("Severity:", json.dumps(stats["security"]["severity"]))
    print("Dup ids:", stats["duplication"]["duplicate_ids"],
          "| canon dup groups:", stats["duplication"]["canonical_arch_dup_groups"],
          "| full-record dup groups:", stats["duplication"]["full_record_dup_groups"],
          "| node-set shared:", stats["duplication"]["node_set_shared_records"],
          "| struct near-dup records:", stats["duplication"]["struct_near_dup_records"])
    print("Regime:")
    for label, rs in stats["regime"].items():
        print(f"  {label:>18}: accepted={rs['accepted']:>6} node_mean={rs['node_mean']:.1f} edge_mean={rs['edge_mean']:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
