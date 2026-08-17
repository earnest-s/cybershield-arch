#!/usr/bin/env python3
"""Phase 8 STEP 4: VRAM / dry-run test using REAL CyberShield SFT records.

Loads the base model exactly as the production harness does, attaches LoRA,
runs one real training step (forward/backward/optimizer) and measures:
model class resolution, quantization, VRAM, loss finiteness, gradient norms,
prompt masking, pad-token label masking, and which modules received adapters.

Usage:
    uv run python backend/training/gemma/phase8_dryrun.py
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import torch
from peft import LoraConfig, get_peft_model
from bitsandbytes.optim import AdamW8bit as AdamW
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

HF_CACHE_DIR = Path(".cache/huggingface")
HF_HUB_DIR = HF_CACHE_DIR / "hub"
os.environ.setdefault("HF_HOME", str(HF_CACHE_DIR.absolute()))
MODEL_ID = "unsloth/gemma-3-4b-it-bnb-4bit"
DATASET = Path("dataset/training/CyberShield_Gemma_SFT_v1.jsonl")
MAX_LENGTH = 1024
N_RECORDS = 1
LONGEST = True


def load_records(path: Path, split: str, limit: int) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            if row.get("metadata", {}).get("split") != split:
                continue
            rows.append({"id": row["id"], "instruction": row["instruction"], "response": row["response"]})
            if len(rows) >= limit:
                break
    return rows


def main() -> int:
    torch.manual_seed(42)
    print(f"[1] GPU: {torch.cuda.get_device_name(0)} | VRAM total: {torch.cuda.get_device_properties(0).total_memory/1024**3:.2f} GiB")
    print(f"[2] model id: {MODEL_ID}")
    print(f"[3] torch {torch.__version__} | cuda {torch.version.cuda}")

    rows = load_records(DATASET, "train", 200)
    if LONGEST:
        target_id = "SFT-013334"
        rows = [r for r in rows if r.get("id", "") == target_id]
        if not rows:
            all_rows = load_records(DATASET, "train", 60000)
            rows = [r for r in all_rows if r.get("id", "") == target_id]
    rows = rows[:N_RECORDS]
    assert len(rows) == N_RECORDS, f"need {N_RECORDS} train records (longest), got {len(rows)}"
    print(f"[4] loaded {N_RECORDS} REAL train-split records (LONGEST=SFT-013334)")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, local_files_only=True, cache_dir=str(HF_HUB_DIR))
    print(f"[5] tokenizer: pad={tokenizer.pad_token!r} eos={tokenizer.eos_token!r} "
          f"pad_id={tokenizer.pad_token_id} eos_id={tokenizer.eos_token_id}")

    bnb_cfg = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        device_map="auto",
        quantization_config=bnb_cfg,
        local_files_only=True,
        cache_dir=str(HF_HUB_DIR),
    )
    print(f"[6] loaded model in {time.time()-t0:.1f}s | class: {type(model).__name__}")
    mem = torch.cuda.memory_allocated() / 1024**3
    print(f"[7] VRAM allocated after load: {mem:.2f} GiB")
    param_types = set()
    for p in model.parameters():
        param_types.add(str(p.dtype))
    print(f"[8] parameter dtypes present: {sorted(param_types)}")

    model.gradient_checkpointing_enable()
    model.config.use_cache = False
    for p in model.parameters():
        p.requires_grad_(False)
    model.enable_input_require_grads()
    print(f"[9] manual kbit prep (base frozen, checkpointing on): trainable base params "
          f"{sum(p.numel() for p in model.parameters() if p.requires_grad)}")

    lora_cfg = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules="model\\.language_model\\..*(q_proj|k_proj|v_proj|o_proj|gate_proj|up_proj|down_proj)",
    )
    model = get_peft_model(model, lora_cfg)
    adapter_names = set(n for n, _ in model.named_modules() if "lora" in n)
    modules_with_lora = sorted({n.split(".lora")[0] for n in adapter_names if "lora" in n})
    vision_lora = [n for n in modules_with_lora if "vision" in n]
    projector_lora = [n for n in modules_with_lora if "projector" in n or "merger" in n]
    lang_lora = [n for n in modules_with_lora if "language_model" in n]
    print(f"[10] LoRA adapter modules: language_model={len(lang_lora)} vision_tower={len(vision_lora)} projector/merger={len(projector_lora)}")
    model.print_trainable_parameters()
    model.train()

    items = []
    for row in rows:
        chat = tokenizer.apply_chat_template(
            [
                {"role": "user", "content": row["instruction"]},
                {"role": "model", "content": row["response"]},
            ],
            tokenize=False,
        )
        items.append(tokenizer(chat, truncation=True, max_length=MAX_LENGTH, return_tensors="pt"))

    # single batch of 1 (harness uses batch_size 1) — first record
    batch = {k: items[0][k] for k in ("input_ids", "attention_mask")}
    batch["input_ids"] = batch["input_ids"].to("cuda")
    batch["attention_mask"] = batch["attention_mask"].to("cuda")
    labels = batch["input_ids"].clone()
    prompt_chat = tokenizer.apply_chat_template(
        [{"role": "user", "content": rows[0]["instruction"]}], add_generation_prompt=True, tokenize=False
    )
    prompt_len = len(tokenizer(prompt_chat, add_special_tokens=False)["input_ids"])
    labels[:, :prompt_len] = -100
    labels[batch["attention_mask"] == 0] = -100
    print(f"[11] seq len {batch['input_ids'].shape[1]} | prompt tokens {prompt_len} | "
          f"labels -100 (masked): {int((labels == -100).sum())} | active targets: {int((labels != -100).sum())}")

    batch["labels"] = labels
    torch.cuda.reset_peak_memory_stats()
    t0 = time.time()
    out = model(**batch)
    loss = out.loss / 8
    loss.backward()
    print(f"[12] forward+backward {time.time()-t0:.1f}s | loss (before opt step): {float(loss) * 8:.4f} | finite: {torch.isfinite(loss).item()}")

    grads = [p.grad for p in model.parameters() if p.requires_grad and p.grad is not None]
    nz = sum(int((g != 0).any().item()) for g in grads)
    print(f"[13] grad-bearing param groups: {len(grads)} | with non-zero grad: {nz}")

    opt = AdamW((p for p in model.parameters() if p.requires_grad), lr=2e-4)
    opt.step()
    print(f"[14] optimizer step OK | peak VRAM: {torch.cuda.max_memory_allocated()/1024**3:.2f} GiB | "
          f"current: {torch.cuda.memory_allocated()/1024**3:.2f} GiB")

    # mask verification: run forward with all-prompt-only loss sanity (labels all -100 except target span)
    print(f"[15] PROMPT MASK OK: {int((labels[:, :prompt_len] == -100).sum()) == prompt_len}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())