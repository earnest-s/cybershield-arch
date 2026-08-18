#!/usr/bin/env python3
"""Phase 8 STEP 6: pilot checkpoint generation evaluation.

Reloads the pilot LoRA adapter over the 4-bit base and generates architecture
JSON for held-out instructions (validation split), then scores every output:

- generation success (non-empty decode)
- valid JSON rate (canonical extraction pipeline)
- schema validity (backend.core.architecture_validator, error-severity issues)
- structurally weak / disconnected / orphan rates
- node/edge counts vs the <=10 nodes / <=15 edges production contract
- duplicate node / duplicate edge rates (validator rules)
- fabricated nodes/edges and missing nodes/edges vs the expected target
  architecture (the SFT artifact's canonical response for the same record)
- exact match rate vs expected target

Writes dataset/docs/phase8_pilot_generation_eval.json.

Import fix (Phase 8): the script inserts the repository root into sys.path
before importing `backend.*` so it also runs standalone from any CWD.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
os.environ.setdefault("HF_HOME", str(_REPO_ROOT / ".cache" / "huggingface"))

MODEL_ID = "unsloth/gemma-3-4b-it-bnb-4bit"
_HF_HUB_DIR = _REPO_ROOT / ".cache" / "huggingface" / "hub"
MAX_NEW_TOKENS = 512


def edge_key(edge: dict) -> tuple:
    return (edge.get("source"), edge.get("target"), edge.get("label"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter", default="checkpoints/gemma_lora_pilot")
    parser.add_argument("--n-gen", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--compare-base", action="store_true")
    parser.add_argument("--max-new-tokens", type=int, default=MAX_NEW_TOKENS)
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

    bnb_cfg = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)
    base = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, device_map="auto", quantization_config=bnb_cfg, local_files_only=True, cache_dir=str(_HF_HUB_DIR)
    )
    base.config.use_cache = True

    adapter_path = Path(args.adapter)
    model = PeftModel.from_pretrained(base, adapter_path) if adapter_path.exists() else base
    model.eval()
    print(f"[INFO] model: {'adapter ' + args.adapter if adapter_path.exists() else 'BASE (no adapter)'}")

    rows = []
    for line in open(_REPO_ROOT / "dataset/training/CyberShield_Gemma_SFT_v1.jsonl"):
        r = json.loads(line)
        if r["metadata"]["split"] == "validation":
            rows.append(r)
    if args.ids:
        wanted = set(args.ids.split(","))
        rows = [r for r in rows if r["id"] in wanted]
    else:
        rows = rows[: args.n_gen]
    print(f"[INFO] evaluating {len(rows)} held-out validation prompts")

    def generate(prompt: str) -> str:
        chat = tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}], add_generation_prompt=True, tokenize=False
        )
        inputs = tokenizer(chat, return_tensors="pt").to(model.device)
        with torch.inference_mode():
            out = model.generate(
                **inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
            )
        return tokenizer.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()

    results = {
        "n": len(rows),
        "generation_success": 0,
        "parse_ok": 0,
        "schema_valid": 0,
        "structurally_weak": 0,
        "disconnected": 0,
        "orphan_nodes": 0,
        "within_guardrail": 0,
        "exact_match": 0,
        "issue_counts": {},
        "node_counts": [],
        "edge_counts": [],
        "fabricated_nodes_total": 0,
        "fabricated_edges_total": 0,
        "missing_nodes_total": 0,
        "missing_edges_total": 0,
        "outputs": [],
        "wall_seconds": 0.0,
        "tokens_generated": 0,
    }

    def expected_from(row: dict) -> dict:
        return parse_architecture(extract_json_object_comments(row["response"]))

    t0 = time.time()
    for idx, r in enumerate(rows):
        raw = generate(r["instruction"])
        results["tokens_generated"] += len(tokenizer(raw, add_special_tokens=False)["input_ids"])
        entry: dict = {"id": r["id"], "raw": raw[:400]}

        if not raw:
            results["outputs"].append(entry)
            continue
        results["generation_success"] += 1

        try:
            arch = parse_architecture(extract_json_object_comments(raw))
        except ValueError as exc:
            entry["parse_error"] = str(exc)[:200]
            results["outputs"].append(entry)
            continue
        results["parse_ok"] += 1

        nodes = arch.get("nodes", [])
        edges = arch.get("edges", [])
        node_ids = [n["id"] for n in nodes if isinstance(n, dict) and isinstance(n.get("id"), str)]
        edge_keys = [edge_key(e) for e in edges if isinstance(e, dict)]

        issues = list(collect_issues(arch))
        connected = is_weakly_connected(nodes, edges)
        if not connected:
            issues.append(type("I", (), {"rule": RULE_CONNECTED, "severity": "warning", "message": ""})())
        orphan = has_orphan_node(arch)
        has_errors = any(i.severity == "error" for i in issues)

        entry["nodes"] = len(node_ids)
        entry["edges"] = len(edge_keys)
        entry["connected"] = connected
        entry["orphan"] = orphan
        entry["schema_valid"] = not has_errors
        entry["structurally_weak"] = (not connected) or orphan
        entry["issues"] = [f"{i.rule}" for i in issues]

        results["node_counts"].append(len(node_ids))
        results["edge_counts"].append(len(edge_keys))
        if not has_errors:
            results["schema_valid"] += 1
        if entry["structurally_weak"]:
            results["structurally_weak"] += 1
        if not connected:
            results["disconnected"] += 1
        if orphan:
            results["orphan_nodes"] += 1
        if len(node_ids) <= 10 and len(edge_keys) <= 15:
            results["within_guardrail"] += 1
        for i in issues:
            results["issue_counts"][i.rule] = results["issue_counts"].get(i.rule, 0) + 1

        try:
            expected = expected_from(r)
            exp_nodes = {n["id"] for n in expected["nodes"] if isinstance(n, dict) and isinstance(n.get("id"), str)}
            exp_edges = {edge_key(e) for e in expected["edges"] if isinstance(e, dict)}
            gen_nodes = set(node_ids)
            gen_edges = set(edge_keys)
            fab_nodes = gen_nodes - exp_nodes
            fab_edges = gen_edges - exp_edges
            miss_nodes = exp_nodes - gen_nodes
            miss_edges = exp_edges - gen_edges
            entry["fabricated_nodes"] = sorted(fab_nodes)
            entry["fabricated_edges"] = sorted(fab_edges)
            entry["missing_nodes"] = sorted(miss_nodes)
            entry["missing_edges"] = sorted(miss_edges)
            entry["expected_nodes"] = len(exp_nodes)
            entry["expected_edges"] = len(exp_edges)
            entry["exact_match"] = not fab_nodes and not fab_edges and not miss_nodes and not miss_edges
            results["fabricated_nodes_total"] += len(fab_nodes)
            results["fabricated_edges_total"] += len(fab_edges)
            results["missing_nodes_total"] += len(miss_nodes)
            results["missing_edges_total"] += len(miss_edges)
            if entry["exact_match"]:
                results["exact_match"] += 1
        except ValueError:
            entry["expected_parse_error"] = True

        results["outputs"].append(entry)
        if (idx + 1) % 10 == 0:
            print(f"[eval] generated {idx + 1}/{len(rows)} ({time.time() - t0:.0f}s)", flush=True)

    results["wall_seconds"] = round(time.time() - t0, 1)
    n = len(rows)
    results["generation_success_rate"] = round(results["generation_success"] / n, 4)
    results["parse_rate"] = round(results["parse_ok"] / n, 4)
    results["schema_valid_rate"] = round(results["schema_valid"] / n, 4)
    results["structurally_weak_rate"] = round(results["structurally_weak"] / n, 4)
    results["connected_rate"] = round(1 - results["disconnected"] / n, 4)
    results["guardrail_rate"] = round(results["within_guardrail"] / n, 4)
    results["exact_match_rate"] = round(results["exact_match"] / n, 4)
    results["avg_nodes"] = round(sum(results["node_counts"]) / max(1, len(results["node_counts"])), 2)
    results["avg_edges"] = round(sum(results["edge_counts"]) / max(1, len(results["edge_counts"])), 2)
    results["max_nodes"] = max(results["node_counts"]) if results["node_counts"] else 0
    results["max_edges"] = max(results["edge_counts"]) if results["edge_counts"] else 0
    results["fabricated_node_rate"] = round(
        results["fabricated_nodes_total"] / max(1, sum(results["node_counts"])), 4
    )
    results["fabricated_edge_rate"] = round(
        results["fabricated_edges_total"] / max(1, sum(results["edge_counts"])), 4
    )

    summary = {k: v for k, v in results.items() if k != "outputs"}
    print(json.dumps(summary, indent=2))
    out_path = _REPO_ROOT / "dataset/docs/phase8_pilot_generation_eval.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(f"[INFO] written {out_path} | peak VRAM {torch.cuda.max_memory_allocated() / 1024**3:.2f} GiB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())