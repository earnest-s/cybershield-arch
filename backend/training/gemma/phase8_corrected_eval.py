#!/usr/bin/env python3
"""Corrected Phase 8 final evaluation — fidelity vs FULL canonical targets.

Fixes the evaluation-correctness defect identified by the artifact
reconciliation (dataset/docs/dataset_artifact_reconciliation.md):

The legacy eval (phase8_generate_eval.py) parsed BOTH the generated output AND
the canonical target through ``parse_architecture``, which silently truncates
every graph to ``MAX_NODES=8 / MAX_EDGES=10``. Reported node/edge F1 therefore
measured fidelity against truncated targets, not the artifact's real targets
(97.2% of which have 10 nodes).

This script separates the four concerns (see reconciliation §II / STEP 2):

A. Generated-output parsing   — runtime-faithful parse (``parse_architecture``,
   caps 8/10) AND a non-truncating full normalization for structural comparison.
B. Canonical target loading   — the artifact's ``architecture`` field verbatim
   (FULL target, never truncated; no runtime parser involved).
C. Structural comparison      — generated FULL graph vs FULL canonical target.
D. Runtime contract validation— FULL generated graph vs the canonical hard
   limits ≤10 nodes / ≤15 edges (``HARD_NODE_LIMIT/HARD_EDGE_LIMIT``) via the
   canonical validator.
E. Schema & security validation — validator issue collection (schema) on both
   the full generated graph and the runtime-parsed graph.

Generation settings are IDENTICAL to the legacy final eval (greedy, seed 42,
rep_penalty 1.1, no_repeat_ngram 0, max_new_tokens 768, gen_batch 3) so outputs
are byte-for-byte reproducible; any metric change is caused by the corrected
target/comparison path alone.

Read-only: loads the artifact and adapter, writes a NEW eval JSON. Does not
modify the artifact, adapter, runtime, or any existing eval artifact.

Usage:
    uv run python backend/training/gemma/phase8_corrected_eval.py \
        --out dataset/docs/phase8_corrected_test_eval.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
os.environ.setdefault("HF_HOME", str(_REPO_ROOT / ".cache" / "huggingface"))

MODEL_ID = "unsloth/gemma-3-4b-it-bnb-4bit"
_HF_HUB_DIR = _REPO_ROOT / ".cache" / "huggingface" / "hub"
EOS_ID = 106  # <end_of_turn> for this tokenizer
ARTIFACT = _REPO_ROOT / "dataset/training/CyberShield_Gemma_SFT_v1.jsonl"

HARD_NODE_LIMIT = 10
HARD_EDGE_LIMIT = 15


def edge_key(edge: dict) -> tuple:
    return (edge.get("source"), edge.get("target"), edge.get("label"))


def split_edge(edge) -> tuple:
    if isinstance(edge, dict):
        source = edge.get("source") if edge.get("source") is not None else edge.get("from")
        target = edge.get("target") if edge.get("target") is not None else edge.get("to")
        label = edge.get("label") if edge.get("label") is not None else edge.get("protocol")
        return source, target, label
    if isinstance(edge, (list, tuple)) and len(edge) >= 2:
        label = edge[2] if len(edge) >= 3 else None
        return edge[0], edge[1], label
    return None, None, None


def normalize_full(raw: dict) -> dict:
    """Non-truncating normalization of a parsed JSON graph (evaluation only).

    Mirrors the runtime parser's normalization (dedupe node ids, canonical
    types/labels, drop self-loops/dangling edges, dedupe edges) but does NOT
    apply MAX_NODES/MAX_EDGES caps. Raises ValueError on the same contract
    violations as the runtime parser (missing arrays, empty graph, bad ids).
    """
    from backend.core.architecture_parser import infer_edge_label, normalize_node_type

    nodes = raw.get("nodes")
    edges = raw.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("Architecture JSON must contain 'nodes' and 'edges' arrays")
    if len(nodes) == 0 or len(edges) == 0:
        raise ValueError("Architecture JSON must include at least one node and one edge")

    normalized_nodes: list[dict] = []
    node_types_by_id: dict[str, str] = {}
    for node in nodes:
        if isinstance(node, dict):
            node_id = node.get("id")
            node_type = node.get("type")
        elif isinstance(node, str):
            node_id, node_type = node, None
        else:
            node_id, node_type = None, None
        if not isinstance(node_id, str) or not node_id.strip():
            raise ValueError("Each node must include a non-empty string 'id'")
        normalized_id = node_id.strip()
        if len(normalized_id) > 64:
            raise ValueError("Node id exceeds limits")
        if normalized_id in node_types_by_id:
            continue
        node_types_by_id[normalized_id] = normalize_node_type(node_type, normalized_id)
        normalized_nodes.append({"id": normalized_id, "type": node_types_by_id[normalized_id]})

    allowed_ids = {nd["id"] for nd in normalized_nodes}
    normalized_edges: list[dict] = []
    seen: set[tuple] = set()
    for edge in edges:
        source, target, label = split_edge(edge)
        if not isinstance(source, str) or not isinstance(target, str):
            raise ValueError("Each edge must include string 'source' and 'target'")
        source_id, target_id = source.strip(), target.strip()
        if source_id == target_id:
            continue
        if source_id not in allowed_ids or target_id not in allowed_ids:
            continue
        key = (source_id, target_id)
        if key in seen:
            continue
        seen.add(key)
        normalized_edges.append({
            "source": source_id,
            "target": target_id,
            "label": infer_edge_label(
                node_types_by_id[source_id],
                node_types_by_id[target_id],
                label if isinstance(label, str) else None,
            ),
        })

    if len(normalized_edges) == 0:
        raise ValueError("Architecture JSON must include at least one valid edge")
    return {"nodes": normalized_nodes, "edges": normalized_edges}


def classify_parse_failure(raw: str) -> str:
    if not raw or not raw.strip():
        return "EMPTY_OUTPUT"
    if "{" not in raw:
        return "NO_JSON"
    if raw.count("{") > raw.count("}"):
        return "INCOMPLETE_JSON"
    return "OTHER_PARSE"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter", default="checkpoints/gemma_lora")
    parser.add_argument("--split", choices=["validation", "test"], default="test")
    parser.add_argument("--n-gen", type=int, default=2575)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-new-tokens", type=int, default=768)
    parser.add_argument("--gen-batch", type=int, default=3)
    parser.add_argument("--repetition-penalty", type=float, default=1.1)
    parser.add_argument("--no-repeat-ngram", type=int, default=0)
    parser.add_argument("--out", default="dataset/docs/phase8_corrected_test_eval.json")
    parser.add_argument("--ids", type=str, default="")
    args = parser.parse_args()

    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    from backend.core.architecture_parser import extract_json_object_comments, parse_architecture
    from backend.core.architecture_validator import (
        collect_issues,
        has_orphan_node,
        is_weakly_connected,
    )

    torch.manual_seed(args.seed)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, local_files_only=True, cache_dir=str(_HF_HUB_DIR))
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    bnb_cfg = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)
    base = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, device_map="auto", quantization_config=bnb_cfg, local_files_only=True, cache_dir=str(_HF_HUB_DIR)
    )
    base.config.use_cache = True

    adapter_path = Path(args.adapter)
    model = PeftModel.from_pretrained(base, adapter_path) if adapter_path.exists() else base
    model.eval()
    print(f"[INFO] adapter: {args.adapter if adapter_path.exists() else 'NONE (base)'}")

    rows = []
    for line in open(ARTIFACT, encoding="utf-8"):
        r = json.loads(line)
        if r["metadata"]["split"] == args.split:
            rows.append(r)
    if args.ids:
        wanted = set(args.ids.split(","))
        rows = [r for r in rows if r["id"] in wanted]
    rows = rows[: args.n_gen]
    print(f"[INFO] evaluating {len(rows)} {args.split} prompts "
          f"(batch {args.gen_batch}, rep_penalty {args.repetition_penalty}, ngram {args.no_repeat_ngram})")

    chat_prompts = [
        tokenizer.apply_chat_template(
            [{"role": "user", "content": r["instruction"]}], add_generation_prompt=True, tokenize=False
        )
        for r in rows
    ]

    def generate_batch(prompts: list[str]) -> tuple[list[str], list[int]]:
        enc = tokenizer(prompts, return_tensors="pt", padding="longest").to(model.device)
        with torch.inference_mode():
            out = model.generate(
                **enc,
                max_new_tokens=args.max_new_tokens,
                do_sample=False,
                repetition_penalty=args.repetition_penalty,
                no_repeat_ngram_size=args.no_repeat_ngram,
                eos_token_id=EOS_ID,
                pad_token_id=tokenizer.pad_token_id,
            )
        input_len = enc.input_ids.shape[1]
        decodes, gen_lens = [], []
        for row in out:
            gen_ids = row[input_len:]
            n_eos = int((gen_ids == EOS_ID).sum())
            if n_eos:
                gen_ids = gen_ids[: int((gen_ids == EOS_ID).nonzero()[0])]
            gen_lens.append(int(gen_ids.shape[0]))
            decodes.append(tokenizer.decode(gen_ids, skip_special_tokens=True).strip())
        return decodes, gen_lens

    results = {
        "config": {
            "adapter": args.adapter,
            "split": args.split,
            "n_gen": len(rows),
            "max_new_tokens": args.max_new_tokens,
            "gen_batch": args.gen_batch,
            "repetition_penalty": args.repetition_penalty,
            "no_repeat_ngram": args.no_repeat_ngram,
            "seed": args.seed,
            "model": MODEL_ID,
            "target_source": "artifact architecture field (FULL, untruncated)",
            "generated_full_parse": "non-truncating normalize_full",
            "contract": {"max_nodes": HARD_NODE_LIMIT, "max_edges": HARD_EDGE_LIMIT},
        },
        "generation_success": 0,
        "parse_ok": 0,
        "parse_failure_categories": Counter(),
        "schema_valid": 0,           # full generated graph, validator errors (incl. ≤10/≤15 size)
        "schema_valid_runtime": 0,   # runtime-parsed graph (8/10 caps), validator errors
        "contract_valid": 0,         # full generated graph within ≤10 nodes / ≤15 edges
        "connected": 0,
        "orphan": 0,
        "structurally_weak": 0,
        "within_guardrail": 0,
        "exact_match": 0,
        "repeated_edge_outputs": 0,
        "repeated_directed_edge_total": 0,
        "eos_completed": 0,
        "hit_token_cap": 0,
        "runtime_truncation_outputs": 0,   # runtime parse dropped nodes/edges vs full
        "issue_counts": Counter(),
        "node_tp": 0, "node_fp": 0, "node_fn": 0,
        "edge_tp": 0, "edge_fp": 0, "edge_fn": 0,
        "node_count_abs_err": [], "edge_count_abs_err": [],
        "gen_tokens": [], "prompt_tokens": [],
        "node_counts": [], "edge_counts": [],          # full generated graph
        "node_counts_runtime": [], "edge_counts_runtime": [],  # runtime-parsed graph
        "target_node_counts": [], "target_edge_counts": [],
        "outputs": [],
        "wall_seconds": 0.0,
    }

    t0 = time.time()
    for start in range(0, len(rows), args.gen_batch):
        chunk = rows[start : start + args.gen_batch]
        decodes, gen_lens = generate_batch([chat_prompts[i] for i in range(start, start + len(chunk))])

        for r, raw, gen_len in zip(chunk, decodes, gen_lens):
            entry: dict = {"id": r["id"], "gen_tokens": gen_len}
            results["gen_tokens"].append(gen_len)
            prompt_len = len(tokenizer(chat_prompts[rows.index(r)], add_special_tokens=False)["input_ids"])
            results["prompt_tokens"].append(prompt_len)

            if gen_len >= args.max_new_tokens:
                results["hit_token_cap"] += 1
            else:
                results["eos_completed"] += 1
                entry["eos_completed"] = True

            if not raw:
                entry["failure"] = "EMPTY_OUTPUT"
                results["parse_failure_categories"]["EMPTY_OUTPUT"] += 1
                results["outputs"].append(entry)
                continue
            results["generation_success"] += 1

            try:
                raw_json = extract_json_object_comments(raw)
            except ValueError:
                cat = classify_parse_failure(raw)
                entry["failure"] = cat
                results["parse_failure_categories"][cat] += 1
                results["outputs"].append(entry)
                continue

            # A. generated parsing — full (structural) + runtime-faithful
            try:
                gen_full = normalize_full(raw_json)
                results["parse_ok"] += 1
            except ValueError:
                cat = classify_parse_failure(raw)
                entry["failure"] = cat
                results["parse_failure_categories"][cat] += 1
                results["outputs"].append(entry)
                continue

            gen_runtime = None
            try:
                gen_runtime = parse_architecture(raw_json)
            except ValueError:
                pass  # runtime parse can fail after full parse only when caps leave 0 edges
            if gen_runtime is not None and (
                len(gen_runtime["nodes"]) < len(gen_full["nodes"])
                or len(gen_runtime["edges"]) < len(gen_full["edges"])
            ):
                results["runtime_truncation_outputs"] += 1
                entry["runtime_truncated"] = True

            # B. canonical target loading (FULL, untruncated)
            target = r["architecture"]

            nodes, edges = gen_full["nodes"], gen_full["edges"]
            node_ids = [n["id"] for n in nodes]
            edge_keys = [edge_key(e) for e in edges]

            # D+E. runtime contract + schema validation on the FULL generated graph
            issues = list(collect_issues(gen_full))
            has_errors = any(i.severity == "error" for i in issues)
            conn = is_weakly_connected(nodes, edges)
            orphan = has_orphan_node(gen_full)
            for i in issues:
                results["issue_counts"][i.rule] += 1
            entry.update({
                "nodes": len(node_ids), "edges": len(edge_keys),
                "connected": conn, "orphan": orphan,
                "schema_valid": not has_errors,
                "issues": [f"{i.rule}" for i in issues],
            })
            results["node_counts"].append(len(node_ids))
            results["edge_counts"].append(len(edge_keys))
            if gen_runtime is not None:
                r_issues = list(collect_issues(gen_runtime))
                results["schema_valid_runtime"] += 0 if any(i.severity == "error" for i in r_issues) else 1
                results["node_counts_runtime"].append(len(gen_runtime["nodes"]))
                results["edge_counts_runtime"].append(len(gen_runtime["edges"]))
            if not has_errors:
                results["schema_valid"] += 1
            if len(node_ids) <= HARD_NODE_LIMIT and len(edge_keys) <= HARD_EDGE_LIMIT:
                results["contract_valid"] += 1
                results["within_guardrail"] += 1
            if conn:
                results["connected"] += 1
            if orphan:
                results["orphan"] += 1
            if not conn or orphan:
                results["structurally_weak"] += 1

            gen_edge_set = set(edge_keys)
            n_dup = len(edge_keys) - len(gen_edge_set)
            if n_dup:
                results["repeated_edge_outputs"] += 1
                results["repeated_directed_edge_total"] += n_dup
                entry["repeated_directed_edges"] = n_dup

            # C. structural comparison vs FULL target
            tgt_node_ids = {n["id"] for n in target["nodes"]}
            tgt_edge_keys = {edge_key(e) for e in target["edges"]}
            results["target_node_counts"].append(len(tgt_node_ids))
            results["target_edge_counts"].append(len(tgt_edge_keys))

            gns, ens = set(node_ids), tgt_node_ids
            ges, ees = gen_edge_set, tgt_edge_keys
            node_tp = len(gns & ens)
            node_fp = len(gns - ens)
            node_fn = len(ens - gns)
            edge_tp = len(ges & ees)
            edge_fp = len(ges - ees)
            edge_fn = len(ees - ges)
            results["node_tp"] += node_tp
            results["node_fp"] += node_fp
            results["node_fn"] += node_fn
            results["edge_tp"] += edge_tp
            results["edge_fp"] += edge_fp
            results["edge_fn"] += edge_fn
            results["node_count_abs_err"].append(abs(len(node_ids) - len(tgt_node_ids)))
            results["edge_count_abs_err"].append(abs(len(edge_keys) - len(tgt_edge_keys)))
            entry.update({
                "node_tp": node_tp, "node_fp": node_fp, "node_fn": node_fn,
                "edge_tp": edge_tp, "edge_fp": edge_fp, "edge_fn": edge_fn,
            })
            exact = node_tp == len(ens) == len(gns) and edge_tp == len(ees) == len(ges)
            if exact:
                results["exact_match"] += 1
                entry["exact_match"] = True

            results["outputs"].append(entry)

        done = start + len(chunk)
        if done % 60 == 0 or done == len(rows):
            print(f"[eval] {done}/{len(rows)} ({time.time() - t0:.0f}s)", flush=True)

    results["n"] = len(rows)
    results["wall_seconds"] = round(time.time() - t0, 1)
    n = len(rows)
    parsed = results["parse_ok"]
    node_prec = results["node_tp"] / max(1, results["node_tp"] + results["node_fp"])
    node_rec = results["node_tp"] / max(1, results["node_tp"] + results["node_fn"])
    edge_prec = results["edge_tp"] / max(1, results["edge_tp"] + results["edge_fp"])
    edge_rec = results["edge_tp"] / max(1, results["edge_tp"] + results["edge_fn"])

    node_count_err = sum(results["node_count_abs_err"]) / max(1, len(results["node_count_abs_err"]))
    edge_count_err = sum(results["edge_count_abs_err"]) / max(1, len(results["edge_count_abs_err"]))

    results.update({
        "generation_success_rate": round(results["generation_success"] / n, 4),
        "parse_rate": round(parsed / n, 4),
        "schema_valid_rate": round(results["schema_valid"] / max(1, parsed), 4),
        "schema_valid_runtime_rate": round(results["schema_valid_runtime"] / max(1, parsed), 4),
        "contract_valid_rate": round(results["contract_valid"] / max(1, parsed), 4),
        "connected_rate": round(results["connected"] / max(1, parsed), 4),
        "orphan_rate": round(results["orphan"] / max(1, parsed), 4),
        "structurally_weak_rate": round(results["structurally_weak"] / max(1, parsed), 4),
        "guardrail_rate": round(results["within_guardrail"] / n, 4),
        "exact_match_rate": round(results["exact_match"] / n, 4),
        "repetition_output_rate": round(results["repeated_edge_outputs"] / max(1, parsed), 4),
        "runtime_truncation_rate": round(results["runtime_truncation_outputs"] / max(1, parsed), 4),
        "eos_completion_rate": round(results["eos_completed"] / n, 4),
        "hit_cap_rate": round(results["hit_token_cap"] / n, 4),
        "node_precision": round(node_prec, 4),
        "node_recall": round(node_rec, 4),
        "node_f1": round(2 * node_prec * node_rec / max(1e-9, node_prec + node_rec), 4),
        "edge_precision": round(edge_prec, 4),
        "edge_recall": round(edge_rec, 4),
        "edge_f1": round(2 * edge_prec * edge_rec / max(1e-9, edge_prec + edge_rec), 4),
        "node_count_error": round(node_count_err, 4),
        "edge_count_error": round(edge_count_err, 4),
        "avg_gen_tokens": round(sum(results["gen_tokens"]) / max(1, len(results["gen_tokens"])), 1),
        "avg_prompt_tokens": round(sum(results["prompt_tokens"]) / max(1, len(results["prompt_tokens"])), 1),
        "avg_nodes": round(sum(results["node_counts"]) / max(1, len(results["node_counts"])), 2),
        "avg_edges": round(sum(results["edge_counts"]) / max(1, len(results["edge_counts"])), 2),
        "avg_nodes_runtime": round(sum(results["node_counts_runtime"]) / max(1, len(results["node_counts_runtime"])), 2),
        "avg_edges_runtime": round(sum(results["edge_counts_runtime"]) / max(1, len(results["edge_counts_runtime"])), 2),
        "avg_target_nodes": round(sum(results["target_node_counts"]) / max(1, len(results["target_node_counts"])), 2),
        "avg_target_edges": round(sum(results["target_edge_counts"]) / max(1, len(results["target_edge_counts"])), 2),
        "max_nodes": max(results["node_counts"]) if results["node_counts"] else 0,
        "max_edges": max(results["edge_counts"]) if results["edge_counts"] else 0,
        "parse_failure_categories": dict(results["parse_failure_categories"]),
        "issue_counts": dict(results["issue_counts"]),
    })
    for key in ("node_counts", "edge_counts", "node_counts_runtime", "edge_counts_runtime",
                "target_node_counts", "target_edge_counts", "gen_tokens", "prompt_tokens",
                "node_count_abs_err", "edge_count_abs_err"):
        del results[key]

    print(json.dumps({k: v for k, v in results.items() if k != "outputs"}, indent=2))
    out_path = _REPO_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2))
    print(f"[INFO] written {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())