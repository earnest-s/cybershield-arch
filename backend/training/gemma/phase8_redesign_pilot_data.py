#!/usr/bin/env python3
"""Redesign pilot dataset generator — A/B/C representation variants.

Reads ONLY the immutable SFT artifact (dataset/training/CyberShield_Gemma_SFT_v1.jsonl),
selects a deterministic small subset (800 train / 100 validation, seed 42), and writes
three SEPARATE pilot artifacts under dataset/pilots/:

  redesign_A.jsonl  — current representation, verbatim (A = control)
  redesign_B.jsonl  — canonical type-anchored ids + deterministic ordering, fixed caps (B)
  redesign_C.jsonl  — B + explicit naming instruction + hybrid metadata (C)

Per the approved redesign proposal (dataset/docs/dataset_redesign_proposal.md §5–§7, §6.1):

  B encoding (canonical ID/order normalization):
    - node ids assigned as {type}-{k}: nodes sorted by (type, original id), k enumerates
      within type  (proposal §6.1.1)
    - emission order: nodes in (type, canonical-index) order; edges sorted by
      (source, target, label)  (proposal §6.1.2)
    - prompt caps fixed to the validator contract: "Max nodes: 10 / Max edges: 15"
      (proposal §6.1.3); FORMAT example updated to role+number style
    - node types, edge labels, topology preserved exactly; provenance via id_map
  C encoding (hybrid, proposal §6.1 E):
    - everything in B, PLUS an explicit naming-instruction line in CONSTRAINTS and full
      canonicalization metadata (method, version, id_map, original_architecture) enabling
      dual name-level / structure-level evaluation.
    - cluster-wise dedup is DEFERRED to full scale (this pilot keeps identical record sets
      across A/B/C so the comparison is controlled).

Deterministic: sampling uses random.Random(42); all transformations are pure functions of
the input record. No source artifact is modified. Read-only w.r.t. dataset/final/*,
the SFT artifact, Phase 6 artifacts, the trained adapter, runtime, and frontend.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE = _REPO_ROOT / "dataset/training/CyberShield_Gemma_SFT_v1.jsonl"
OUT_DIR = _REPO_ROOT / "dataset" / "pilots"
SEED = 42
N_TRAIN = 800
N_VAL = 100
TRANSFORM_VERSION = "canonical_type_anchored_v1"
PILOT_VERSION = "redesign_pilot_v1"

CAP_NODES_OLD = "- Max nodes: 8"
CAP_EDGES_OLD = "- Max edges: 10"
CAP_NODES_NEW = "- Max nodes: 10"
CAP_EDGES_NEW = "- Max edges: 15"
NAMING_LINE = "- Use the role+number naming style for components, e.g. service-1, database-2"
FORMAT_EXAMPLE_OLD = (
    '{"id": "frontend", "type": "ui"},\n        {"id": "api", "type": "service"}'
)
FORMAT_EXAMPLE_NEW = (
    '{"id": "ui-1", "type": "ui"},\n        {"id": "service-1", "type": "service"}'
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonicalize(graph: dict) -> tuple[dict, dict]:
    """Return (canonical graph, id_map). Types/labels/topology preserved exactly.

    Node ids: {type}-{k} with nodes sorted by (type, original id) and k enumerating
    within type (1-based). Nodes emitted in (type, canonical-index) order; edges sorted
    by (source, target, label).
    """
    nodes = list(graph["nodes"])
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
    for e in graph["edges"]:
        canon_edges.append({
            "source": id_map[e["source"]],
            "target": id_map[e["target"]],
            "label": e["label"],
        })
    canon_edges.sort(key=lambda e: (e["source"], e["target"], e["label"]))
    return {"nodes": canon_nodes, "edges": canon_edges}, id_map


def compact_json(obj) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


def fix_caps(instruction: str) -> str:
    assert CAP_NODES_OLD in instruction and CAP_EDGES_OLD in instruction, "cap lines not found"
    return instruction.replace(CAP_NODES_OLD, CAP_NODES_NEW).replace(CAP_EDGES_OLD, CAP_EDGES_NEW)


def variant_a(row: dict) -> dict:
    return {
        "instruction": row["instruction"],
        "response": row["response"],
        "architecture": row["architecture"],
    }


def variant_b(row: dict) -> dict:
    canon, id_map = canonicalize(row["architecture"])
    return {
        "instruction": fix_caps(row["instruction"]).replace(FORMAT_EXAMPLE_OLD, FORMAT_EXAMPLE_NEW),
        "response": compact_json(canon),
        "architecture": canon,
        "canonicalization": {
            "method": "type_anchored",
            "version": TRANSFORM_VERSION,
            "id_map": id_map,
        },
    }


def variant_c(row: dict) -> dict:
    b = variant_b(row)
    instr = b["instruction"]
    anchor = "- Max edges: 15"
    assert anchor in instr
    instr = instr.replace(anchor, anchor + "\n" + NAMING_LINE, 1)
    return {
        "instruction": instr,
        "response": b["response"],
        "architecture": b["architecture"],
        "canonicalization": {
            "method": "hybrid",
            "version": TRANSFORM_VERSION,
            "id_map": b["canonicalization"]["id_map"],
            "naming_instruction": NAMING_LINE,
            "dedup": "deferred_to_full_scale",
        },
    }


VARIANTS = {"A": variant_a, "B": variant_b, "C": variant_c}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--n-train", type=int, default=N_TRAIN)
    parser.add_argument("--n-val", type=int, default=N_VAL)
    parser.add_argument("--out", default=str(OUT_DIR))
    args = parser.parse_args()

    src_sha = sha256_file(SOURCE)
    print(f"[INFO] source {SOURCE.name} SHA-256 {src_sha[:16]}…")

    train, val = [], []
    with open(SOURCE, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            sp = r["metadata"]["split"]
            if sp == "train":
                train.append(r)
            elif sp == "validation":
                val.append(r)
    print(f"[INFO] source splits: train={len(train)} validation={len(val)}")

    rng = random.Random(args.seed)
    train_ids = sorted(r["id"] for r in train)
    val_ids = sorted(r["id"] for r in val)
    train_pick = set(rng.sample(train_ids, args.n_train))
    val_pick = set(rng.sample(val_ids, args.n_val))
    overlap = train_pick & val_pick
    assert not overlap, f"leakage between pilot train/val: {len(overlap)}"

    by_id = {r["id"]: r for r in train + val}
    train_recs = sorted((by_id[i] for i in train_pick), key=lambda r: r["id"])
    val_recs = sorted((by_id[i] for i in val_pick), key=lambda r: r["id"])
    print(f"[INFO] sampled {len(train_recs)} train / {len(val_recs)} validation records (seed {args.seed})")

    for variant, fn in VARIANTS.items():
        out_path = Path(args.out) / f"redesign_{variant}.jsonl"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        n = 0
        with open(out_path, "w", encoding="utf-8") as fh:
            for split, recs in (("train", train_recs), ("validation", val_recs)):
                for src in recs:
                    out = fn(src)
                    meta = {
                        "split": split,
                        "id": f"PILOT-{variant}-{src['id']}",
                        "source_id": src["id"],
                        "pilot_variant": variant,
                        "pilot_version": PILOT_VERSION,
                        "source_sha256": src_sha,
                        "source_split": src["metadata"]["split"],
                        "domain": src["metadata"]["domain"],
                        "style": src["metadata"]["style"],
                        "cloud": src["metadata"]["cloud"],
                        "complexity": src["metadata"]["complexity"],
                        "original_architecture": src["architecture"],
                    }
                    if "canonicalization" in out:
                        meta["canonicalization"] = out.pop("canonicalization")
                    fh.write(json.dumps({
                        "id": meta["id"],
                        "instruction": out["instruction"],
                        "response": out["response"],
                        "architecture": out["architecture"],
                        "metadata": meta,
                    }, ensure_ascii=False) + "\n")
                    n += 1
        print(f"[INFO] wrote {out_path} ({n} records)")

    # quick self-verification
    with open(Path(args.out) / "redesign_A.jsonl", encoding="utf-8") as fh:
        ra = json.loads(fh.readline())
    with open(Path(args.out) / "redesign_B.jsonl", encoding="utf-8") as fh:
        rb = json.loads(fh.readline())
    assert ra["architecture"] == ra["metadata"]["original_architecture"]
    canon, id_map = canonicalize(ra["architecture"])
    assert rb["architecture"] == canon
    orig_ids = {n["id"] for n in ra["architecture"]["nodes"]}
    assert set(id_map.keys()) == orig_ids
    assert {n["id"] for n in canon["nodes"]} == set(id_map.values())
    assert all(canon_id.count("-") == 1 for canon_id in id_map.values())
    print("[INFO] self-check passed: A verbatim, B canonicalization matches, id_map coherent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())