#!/usr/bin/env python3
"""Phase 8 generation evaluation — rich fidelity metrics (tuning + final).

Evaluates a LoRA adapter over the 4-bit base on held-out prompts with:

- generation success, JSON parse rate, parse-failure categories
- schema validity (canonical validator), connectedness, orphan rate
- node/edge count validity vs contract (<=10 nodes / <=15 edges)
- node precision/recall/F1 and edge precision/recall/F1 vs the target
  architecture (canonical response in the SFT artifact)
- exact architecture match rate (same node ids + same edge keys)
- repeated-edge / repetition-loop detection within generated output
- EOS completion rate (did decoding stop at <end_of_turn> or hit the cap)
- token-length stats (prompt, generated)

Generation is deterministic greedy decoding with optional repetition_penalty
and no_repeat_ngram_size (deterministic inference settings — never sampling).
Batched generation (--gen-batch) uses HF generate with per-sequence EOS stop.

Imports backend.* via an explicit repo-root sys.path insertion so the script
runs standalone from any CWD. Does not modify any dataset or artifact.

Usage:
    uv run python backend/training/gemma/phase8_generate_eval.py \
        --adapter checkpoints/exp_E1 --split validation --n-gen 100 \
        --out dataset/docs/tuning/exp_E1.json
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


def edge_key(edge: dict) -> tuple:
    return (edge.get("source"), edge.get("target"), edge.get("label"))


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
    parser.add_argument("--split", choices=["validation", "test"], default="validation")
    parser.add_argument("--n-gen", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-new-tokens", type=int, default=768)
    parser.add_argument("--gen-batch", type=int, default=2)
    parser.add_argument("--repetition-penalty", type=float, default=1.0)
    parser.add_argument("--no-repeat-ngram", type=int, default=0)
    parser.add_argument("--out", default="dataset/docs/phase8_generate_eval.json")
    parser.add_argument("--ids", type=str, default="")
    args = parser.parse_args()

    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    from backend.core.architecture_parser import extract_json_object_comments, parse_architecture
    from backend.core.architecture_validator import (
        RULE_COLLISION,
        RULE_CONNECTED,
        RULE_DANGLING,
        RULE_DUPLICATE_EDGE,
        RULE_SELF_LOOP,
        RULE_SIZE,
        RULE_UNSUPPORTED_LABEL,
        RULE_UNSUPPORTED_TYPE,
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
    for line in open(_REPO_ROOT / "dataset/training/CyberShield_Gemma_SFT_v1.jsonl"):
        r = json.loads(line)
        if r["metadata"]["split"] == args.split:
            rows.append(r)
    if args.ids:
        wanted = set(args.ids.split(","))
        rows = [r for r in rows if r["id"] in wanted]
    rows = rows[: args.n_gen]
    print(f"[INFO] evaluating {len(rows)} {args.split} prompts (batch {args.gen_batch}, "
          f"rep_penalty {args.repetition_penalty}, ngram {args.no_repeat_ngram})")

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
        decodes = []
        gen_lens = []
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
        },
        "generation_success": 0,
        "parse_ok": 0,
        "parse_failure_categories": Counter(),
        "schema_valid": 0,
        "connected": 0,
        "orphan": 0,
        "within_guardrail": 0,
        "exact_match": 0,
        "repeated_edge_outputs": 0,
        "repeated_directed_edge_total": 0,
        "eos_completed": 0,
        "hit_token_cap": 0,
        "issue_counts": Counter(),
        "node_tp": 0, "node_fp": 0, "node_fn": 0,
        "edge_tp": 0, "edge_fp": 0, "edge_fn": 0,
        "gen_tokens": [],
        "prompt_tokens": [],
        "node_counts": [],
        "edge_counts": [],
        "target_node_counts": [],
        "target_edge_counts": [],
        "outputs": [],
        "wall_seconds": 0.0,
    }

    def expected_from(row: dict) -> dict:
        return parse_architecture(extract_json_object_comments(row["response"]))

    t0 = time.time()
    for start in range(0, len(rows), args.gen_batch):
        chunk = rows[start : start + args.gen_batch]
        decodes, gen_lens = generate_batch([chat_prompts[r_idx] for r_idx in range(start, start + len(chunk))])

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
                arch = parse_architecture(extract_json_object_comments(raw))
            except ValueError:
                cat = classify_parse_failure(raw)
                entry["failure"] = cat
                results["parse_failure_categories"][cat] += 1
                results["outputs"].append(entry)
                continue
            results["parse_ok"] += 1

            nodes = arch.get("nodes", [])
            edges = arch.get("edges", [])
            node_ids = [n["id"] for n in nodes if isinstance(n, dict) and isinstance(n.get("id"), str)]
            edge_keys = [edge_key(e) for e in edges if isinstance(e, dict)]

            issues = list(collect_issues(arch))
            conn = is_weakly_connected(nodes, edges)
            if not conn:
                issues.append(type("I", (), {"rule": RULE_CONNECTED, "severity": "warning", "message": ""})())
            orphan = has_orphan_node(arch)
            has_errors = any(i.severity == "error" for i in issues)

            entry.update({
                "nodes": len(node_ids),
                "edges": len(edge_keys),
                "connected": conn,
                "orphan": orphan,
                "schema_valid": not has_errors,
                "issues": [f"{i.rule}" for i in issues],
            })
            for i in issues:
                results["issue_counts"][i.rule] += 1

            results["node_counts"].append(len(node_ids))
            results["edge_counts"].append(len(edge_keys))
            if not has_errors:
                results["schema_valid"] += 1
            if conn:
                results["connected"] += 1
            if orphan:
                results["orphan"] += 1
            if len(node_ids) <= 10 and len(edge_keys) <= 15:
                results["within_guardrail"] += 1

            gen_edge_set = set(edge_keys)
            n_dup = len(edge_keys) - len(gen_edge_set)
            if n_dup:
                results["repeated_edge_outputs"] += 1
                results["repeated_directed_edge_total"] += n_dup
                entry["repeated_directed_edges"] = n_dup

            try:
                expected = expected_from(r)
                exp_node_ids = {n["id"] for n in expected["nodes"] if isinstance(n, dict) and isinstance(n.get("id"), str)}
                exp_edge_keys = {edge_key(e) for e in expected["edges"] if isinstance(e, dict)}
                results["target_node_counts"].append(len(exp_node_ids))
                results["target_edge_counts"].append(len(exp_edge_keys))

                gns, ens = set(node_ids), exp_node_ids
                ges, ees = gen_edge_set, exp_edge_keys
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
                entry.update({
                    "node_tp": node_tp, "node_fp": node_fp, "node_fn": node_fn,
                    "edge_tp": edge_tp, "edge_fp": edge_fp, "edge_fn": edge_fn,
                })
                exact = node_tp == len(ens) == len(gns) and edge_tp == len(ees) == len(ges)
                if exact:
                    results["exact_match"] += 1
                    entry["exact_match"] = True
            except ValueError:
                entry["expected_parse_error"] = True

            results["outputs"].append(entry)

        done = start + len(chunk)
        if done % 20 == 0 or done == len(rows):
            print(f"[eval] {done}/{len(rows)} ({time.time() - t0:.0f}s, vram {torch.cuda.max_memory_allocated() / 1024**3:.2f} GiB)", flush=True)

    results["wall_seconds"] = round(time.time() - t0, 1)
    n = len(rows)
    parsed = results["parse_ok"]
    node_prec = results["node_tp"] / max(1, results["node_tp"] + results["node_fp"])
    node_rec = results["node_tp"] / max(1, results["node_tp"] + results["node_fn"])
    edge_prec = results["edge_tp"] / max(1, results["edge_tp"] + results["edge_fp"])
    edge_rec = results["edge_tp"] / max(1, results["edge_tp"] + results["edge_fn"])

    results.update({
        "generation_success_rate": round(results["generation_success"] / n, 4),
        "parse_rate": round(parsed / n, 4),
        "schema_valid_rate": round(results["schema_valid"] / n, 4),
        "connected_rate": round(results["connected"] / n, 4),
        "orphan_rate": round(results["orphan"] / n, 4),
        "guardrail_rate": round(results["within_guardrail"] / n, 4),
        "exact_match_rate": round(results["exact_match"] / n, 4),
        "repetition_output_rate": round(results["repeated_edge_outputs"] / max(1, parsed), 4),
        "eos_completion_rate": round(results["eos_completed"] / n, 4),
        "hit_cap_rate": round(results["hit_token_cap"] / n, 4),
        "node_precision": round(node_prec, 4),
        "node_recall": round(node_rec, 4),
        "node_f1": round(2 * node_prec * node_rec / max(1e-9, node_prec + node_rec), 4),
        "edge_precision": round(edge_prec, 4),
        "edge_recall": round(edge_rec, 4),
        "edge_f1": round(2 * edge_prec * edge_rec / max(1e-9, edge_prec + edge_rec), 4),
        "avg_gen_tokens": round(sum(results["gen_tokens"]) / max(1, len(results["gen_tokens"])), 1),
        "avg_prompt_tokens": round(sum(results["prompt_tokens"]) / max(1, len(results["prompt_tokens"])), 1),
        "avg_nodes": round(sum(results["node_counts"]) / max(1, len(results["node_counts"])), 2),
        "avg_edges": round(sum(results["edge_counts"]) / max(1, len(results["edge_counts"])), 2),
        "avg_target_nodes": round(sum(results["target_node_counts"]) / max(1, len(results["target_node_counts"])), 2),
        "avg_target_edges": round(sum(results["target_edge_counts"]) / max(1, len(results["target_edge_counts"])), 2),
        "max_nodes": max(results["node_counts"]) if results["node_counts"] else 0,
        "max_edges": max(results["edge_counts"]) if results["edge_counts"] else 0,
        "peak_vram_gib": round(torch.cuda.max_memory_allocated() / 1024**3, 2),
        "parse_failure_categories": dict(results["parse_failure_categories"]),
        "issue_counts": dict(results["issue_counts"]),
    })
    for key in ("node_counts", "edge_counts", "target_node_counts", "target_edge_counts", "gen_tokens", "prompt_tokens"):
        del results[key]

    print(json.dumps({k: v for k, v in results.items() if k not in ("outputs",)}, indent=2))
    out_path = _REPO_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2))
    print(f"[INFO] written {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())