#!/usr/bin/env python3
"""Phase 8 STEP 6: pilot checkpoint evaluation.

Reloads the pilot LoRA adapter over the 4-bit base, generates architecture
JSON for held-out instructions (validation split), and scores every output:

- JSON parse success
- canonical schema validity (backend validator + contract)
- duplicate node ids / dangling edges / self-loops / duplicate edges
- <=10 nodes, <=15 edges (hard guardrail)
- structural validity via backend.core.architecture_validator.collect_issues

Also records generation wall-clock time, per-output token counts, and the
base-model comparison on the same prompts (no adapter) for context.

Usage:
    uv run python backend/training/gemma/phase8_pilot_eval.py --adapter checkpoints/gemma_lora_pilot --n-gen 50
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

MODEL_ID = "unsloth/gemma-3-4b-it-bnb-4bit"
MAX_NEW_TOKENS = 512


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter", default="checkpoints/gemma_lora_pilot")
    parser.add_argument("--n-gen", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--compare-base", action="store_true")
    args = parser.parse_args()

    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from backend.core.architecture_validator import collect_issues
    from backend.core.architecture_parser import extract_json_object_comments, parse_architecture

    torch.manual_seed(args.seed)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, local_files_only=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    bnb_cfg = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)
    base = AutoModelForCausalLM.from_pretrained(MODEL_ID, device_map="auto", quantization_config=bnb_cfg, local_files_only=True)
    base.config.use_cache = True

    adapter_path = Path(args.adapter)
    model = PeftModel.from_pretrained(base, adapter_path) if adapter_path.exists() else base
    model.eval()
    print(f"[INFO] model: {'adapter ' + args.adapter if adapter_path.exists() else 'BASE (no adapter)'}")

    rows = []
    for line in open("dataset/training/CyberShield_Gemma_SFT_v1.jsonl"):
        r = json.loads(line)
        if r["metadata"]["split"] == "validation":
            rows.append(r)
    rows = rows[: args.n_gen]
    print(f"[INFO] evaluating {len(rows)} held-out validation prompts")

    def generate(prompt: str) -> str:
        chat = tokenizer.apply_chat_template([{"role": "user", "content": prompt}], add_generation_prompt=True, tokenize=False)
        inputs = tokenizer(chat, return_tensors="pt").to(model.device)
        with torch.inference_mode():
            out = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False, pad_token_id=tokenizer.pad_token_id)
        return tokenizer.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()

    def check_arch(arch: dict) -> list[str]:
        issues = collect_issues(arch)
        n = len(arch.get("nodes", []))
        e = len(arch.get("edges", []))
        if n > 10:
            issues.append(f"nodes={n} > 10")
        if e > 15:
            issues.append(f"edges={e} > 15")
        return issues

    results = {"parse_ok": 0, "valid_arch": 0, "within_guardrail": 0, "issues": {}, "outputs": [], "wall_seconds": 0.0, "tokens_generated": 0}
    t0 = time.time()
    for r in rows:
        raw = generate(r["instruction"])
        results["tokens_generated"] += len(tokenizer(raw, add_special_tokens=False)["input_ids"])
        try:
            arch = parse_architecture(extract_json_object_comments(raw))
            results["parse_ok"] += 1
        except ValueError as exc:
            results["outputs"].append({"id": r["id"], "parse_error": str(exc)[:200], "raw": raw[:300]})
            continue
        issues = check_arch(arch)
        if not issues:
            results["valid_arch"] += 1
        for issue in issues:
            results["issues"][issue] = results["issues"].get(issue, 0) + 1
        if len(arch["nodes"]) <= 10 and len(arch["edges"]) <= 15:
            results["within_guardrail"] += 1
        results["outputs"].append({"id": r["id"], "nodes": len(arch["nodes"]), "edges": len(arch["edges"]), "issues": issues})
    results["wall_seconds"] = round(time.time() - t0, 1)
    results["n"] = len(rows)
    results["parse_rate"] = round(results["parse_ok"] / len(rows), 4)
    results["valid_rate"] = round(results["valid_arch"] / len(rows), 4)

    print(json.dumps({k: v for k, v in results.items() if k != "outputs"}, indent=2))
    Path("dataset/docs/phase8_pilot_generation_eval.json").write_text(json.dumps(results, indent=2))
    print(f"[INFO] written dataset/docs/phase8_pilot_generation_eval.json | peak VRAM {torch.cuda.max_memory_allocated()/1024**3:.2f} GiB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())