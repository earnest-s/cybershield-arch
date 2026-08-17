#!/usr/bin/env python3
"""Independent quality gate for the Phase 7 SFT artifact.

Standalone (no backend imports; reads backend/core/inference.py only to
extract the live prompt template for a drift check). Verifies:

  1. Structure: 51,498 records, sequential unique ids.
  2. Contract: every target parses to {nodes, edges}; canonical node types /
     edge labels; no dangling edges, self-loops, duplicate edges; within the
     hard guardrail (<= 10 nodes, <= 15 edges).
  3. Fidelity: response string parses to exactly the architecture object.
  4. Prompt drift: rendered instructions byte-match the prompt template
     currently in backend/core/inference.py (with the parent instruction
     substituted), and contain the parent instruction.
  5. Splits: exact 90/5/5 counts; cluster integrity (identical node-id sets
     never straddle splits).
  6. Provenance: every record carries parent_source_id, parent_architecture_id,
     Phase 6 transformation details; parents exist in the manifest.
  7. Sequence length: full scan with the real cached Gemma 3 4B tokenizer,
     chat template applied; assert 100% of records <= max_length (1024).

Exit code 0 only if every gate passes.

Usage:
    uv run python dataset/scripts/verify_sft.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from transformers import AutoTokenizer

ALLOWED_NODE_TYPES = {"ui", "service", "database", "cache", "queue", "container"}
ALLOWED_EDGE_LABELS = {"HTTP", "DB Query", "Async", "Cache"}
HARD_NODE_LIMIT = 10
HARD_EDGE_LIMIT = 15
EXPECTED_RECORDS = 51498
EXPECTED_SPLITS = {"train": 46348, "validation": 2575, "test": 2575}
MAX_LENGTH = 1024

failures: list[str] = []
checks: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    checks.append(name)
    status = "PASS" if ok else "FAIL"
    suffix = f" | {detail}" if detail else ""
    print(f"[{status}] {name}{suffix}")
    if not ok:
        failures.append(f"{name}: {detail}")


def extract_runtime_prompt(script: str) -> str:
    """Extract the prompt template source from inference.py.

    Rebuilds the exact string generate_architecture produces by evaluating
    the f-string with clean_text replaced, mimicking the runtime.
    """
    match = re.search(r'prompt = f"""(.*?)"""\n\n    stricter_prompt', script, re.S)
    if not match:
        raise RuntimeError("could not locate prompt template in inference.py")
    body = match.group(1)
    if "{clean_text}" not in body:
        raise RuntimeError("prompt template in inference.py has no {clean_text} slot")
    return body


def validate_architecture(arch: dict) -> tuple[bool, list[str]]:
    issues: list[str] = []
    nodes = arch.get("nodes", [])
    edges = arch.get("edges", [])
    if not isinstance(nodes, list) or not isinstance(edges, list):
        return False, ["nodes/edges must be lists"]
    ids = [n.get("id") for n in nodes]
    if len(ids) != len(set(ids)):
        issues.append("duplicate node ids")
    for n in nodes:
        if n.get("type") not in ALLOWED_NODE_TYPES:
            issues.append(f"bad node type {n.get('type')!r} for {n.get('id')!r}")
    edge_keys: set[tuple] = set()
    for e in edges:
        if e.get("label") not in ALLOWED_EDGE_LABELS:
            issues.append(f"bad edge label {e.get('label')!r}")
        if e.get("source") not in ids or e.get("target") not in ids:
            issues.append(f"dangling edge {e.get('source')}->{e.get('target')}")
        if e.get("source") == e.get("target"):
            issues.append("self-loop")
        key = (e.get("source"), e.get("target"), e.get("label"))
        if key in edge_keys:
            issues.append(f"duplicate edge {key}")
        edge_keys.add(key)
    if len(nodes) > HARD_NODE_LIMIT:
        issues.append(f"{len(nodes)} nodes > {HARD_NODE_LIMIT}")
    if len(edges) > HARD_EDGE_LIMIT:
        issues.append(f"{len(edges)} edges > {HARD_EDGE_LIMIT}")
    return (not issues), issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", default="dataset/training/CyberShield_Gemma_SFT_v1.jsonl")
    parser.add_argument("--input-dir", default="dataset/training/subgraphs")
    parser.add_argument("--model-cache", default=".cache/huggingface/hub")
    parser.add_argument("--max-length", type=int, default=MAX_LENGTH)
    args = parser.parse_args()

    artifact = Path(args.artifact)
    input_dir = Path(args.input_dir)
    manifest = json.loads((input_dir / "manifest.json").read_text(encoding="utf-8"))
    runtime_src = Path("backend/core/inference.py").read_text(encoding="utf-8")
    runtime_template = extract_runtime_prompt(runtime_src)
    runtime_template = runtime_template.replace("{clean_text}", "{instruction}")

    snapshots = sorted((Path(args.model_cache) / "models--unsloth--gemma-3-4b-it-bnb-4bit" / "snapshots").iterdir())
    if not snapshots:
        check("tokenizer available", False, "no cached Gemma snapshot found")
        return 1
    tokenizer = AutoTokenizer.from_pretrained(snapshots[0], local_files_only=True)

    records: list[dict] = []
    with artifact.open(encoding="utf-8") as fh:
        for line in fh:
            records.append(json.loads(line))

    check("record count", len(records) == EXPECTED_RECORDS, f"got {len(records)}")
    check("sequential unique ids", [r["id"] for r in records] == [f"SFT-{i:06d}" for i in range(1, len(records) + 1)])

    manifest_parents: dict[str, dict] = {}
    for rid in manifest["ranges"]:
        for line in (input_dir / f"subgraphs_{rid}.jsonl").open(encoding="utf-8"):
            parent = json.loads(line)
            parent_id = parent["metadata"]["phase6"]["parent_source_id"]
            manifest_parents[parent_id] = parent

    contract_issues: Counter = Counter()
    prompt_issues = 0
    instruction_missing = 0
    provenance_missing = 0
    parent_unknown = 0
    phase6_contract_mismatch = 0
    response_mismatch = 0
    parent_arch_mismatch = 0
    splits: Counter = Counter()
    clusters: dict[tuple[str, ...], set[str]] = {}

    for r in records:
        arch = r["architecture"]
        ok, issues = validate_architecture(arch)
        for issue in issues:
            contract_issues[issue] += 1
        if json.loads(r["response"]) != arch:
            response_mismatch += 1
        md = r["metadata"]
        p6 = md.get("phase6", {})
        parent = manifest_parents.get(md.get("parent_source_id"))
        if not md.get("parent_source_id") or not md.get("parent_architecture_id"):
            provenance_missing += 1
        if parent is None:
            parent_unknown += 1
            continue
        if p6.get("transformation_method") != "sacce_connected_subgraph_v1" or p6.get("contract") not in ("within_hard_limits", None):
            phase6_contract_mismatch += 1
        if parent["architecture"] != arch:
            parent_arch_mismatch += 1
        rendered = runtime_template.format(instruction=parent["instruction"].strip())
        if rendered != r["instruction"]:
            prompt_issues += 1
        key = tuple(sorted(n["id"] for n in arch["nodes"]))
        clusters.setdefault(key, set()).add(md["split"])
        splits[md["split"]] += 1

    check("contract issues", not contract_issues, dict(contract_issues) if contract_issues else "0 issues across 51,498 records")
    check("response fidelity", response_mismatch == 0, f"{response_mismatch} mismatches")
    check("parent architecture fidelity", parent_arch_mismatch == 0, f"{parent_arch_mismatch} mismatches")
    check("prompt drift (runtime template)", prompt_issues == 0, f"{prompt_issues} deviations from inference.py template")
    check("provenance present", provenance_missing == 0, f"{provenance_missing} missing")
    check("parents in manifest", parent_unknown == 0, f"{parent_unknown} unknown")
    check("phase6 contract", phase6_contract_mismatch == 0, f"{phase6_contract_mismatch} mismatches")

    check("split counts exact",
          dict(splits) == EXPECTED_SPLITS,
          f"got {dict(splits)}")
    straddle = [k for k, v in clusters.items() if len(v) > 1]
    check("cluster integrity (no split straddle)", not straddle, f"{len(straddle)} straddling node-set clusters")

    tokenizer.pad_token = tokenizer.eos_token
    max_seen = 0
    over = 0
    for r in records:
        chat = tokenizer.apply_chat_template(
            [{"role": "user", "content": r["instruction"]}, {"role": "model", "content": r["response"]}],
            tokenize=False,
        )
        length = len(tokenizer(chat, add_special_tokens=False)["input_ids"])
        max_seen = max(max_seen, length)
        if length > args.max_length:
            over += 1
    check("sequence length <= max_length",
          over == 0,
          f"max observed {max_seen} tokens (limit {args.max_length}); {over} records over")

    multi = sum(1 for v in clusters.values() if len(v) > 1)
    print(f"[INFO] node-set clusters: {len(clusters)}; multi-record: {multi}")
    print(f"[INFO] max observed sequence length (chat template): {max_seen} tokens")

    passed = not failures
    print("\nRESULT:", "PASS" if passed else "FAIL")
    print(f"checks: {len(checks)} | passed: {len(checks) - len(failures)} | failed: {len(failures)}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())