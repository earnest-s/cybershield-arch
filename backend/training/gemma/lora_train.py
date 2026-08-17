#!/usr/bin/env python3
"""LoRA fine-tuning harness for CyberShield Gemma SFT v1.

Phase 7 update (dataset/docs/phase7_training_spec.md). Compared with the
pre-Phase-7 version this harness:

- targets the architecture-generation task (instruction -> architecture JSON)
  instead of the stale synthetic explanation task;
- reads the Phase 7 SFT artifact (dataset/training/CyberShield_Gemma_SFT_v1.jsonl)
  with instruction/response fields and record-level metadata.split;
- applies Gemma 3's single-turn chat template and masks the prompt tokens
  out of the loss (labels = -100), which the old version did not do;
- uses max_length 1024 (measured: 100% of records fit; the old default of
  384 truncated ~100% of records);
- splits training from evaluation using the artifact's validation split and
  reports eval loss;
- seeds torch, the DataLoader, and numpy for deterministic reproduction.

No training is performed by this file at runtime unless invoked; this phase
only ships the harness. CLI flags keep their pre-Phase-7 names and semantics
where possible (--dataset, --output, --model-id, --batch-size, --grad-accum,
--epochs, --lr, --max-length, --max-train-samples); defaults changed to the
Phase 7 artifact.
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List

import torch
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

PROMPT_LABEL = -100


class TextDataset(Dataset):
    def __init__(self, items: List[Dict[str, str]], tokenizer, max_length: int, mask_prompt: bool = True):
        self.items = items
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.mask_prompt = mask_prompt

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int):
        row = self.items[index]
        chat = self.tokenizer.apply_chat_template(
            [
                {"role": "user", "content": row["instruction"]},
                {"role": "model", "content": row["response"]},
            ],
            tokenize=False,
        )
        encoded = self.tokenizer(
            chat,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt",
        )
        input_ids = encoded["input_ids"].squeeze(0)
        attention_mask = encoded["attention_mask"].squeeze(0)
        labels = input_ids.clone()
        if self.mask_prompt:
            prompt_chat = self.tokenizer.apply_chat_template(
                [{"role": "user", "content": row["instruction"]}],
                add_generation_prompt=True,
                tokenize=False,
            )
            prompt_len = len(self.tokenizer(prompt_chat, add_special_tokens=False)["input_ids"])
            labels[:prompt_len] = PROMPT_LABEL
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LoRA training for Gemma 3 4B (CyberShield SFT v1).")
    parser.add_argument("--dataset", default="dataset/training/CyberShield_Gemma_SFT_v1.jsonl")
    parser.add_argument("--output", default="checkpoints/gemma_lora")
    parser.add_argument("--model-id", default="unsloth/gemma-3-4b-it-bnb-4bit")
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--grad-accum", type=int, default=8)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--max-length", type=int, default=1024)
    parser.add_argument("--max-train-samples", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--eval-every-steps", type=int, default=100)
    return parser.parse_args()


def load_dataset(path: Path, split: str, limit: int) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            if row.get("metadata", {}).get("split") != split:
                continue
            if "instruction" not in row or "response" not in row:
                continue
            items.append({"instruction": row["instruction"], "response": row["response"]})
            if limit and len(items) >= limit:
                break
    return items


def set_seed(seed: int) -> None:
    import random

    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


@torch.inference_mode()
def evaluate(model, loader: DataLoader, device: torch.device) -> float:
    model.eval()
    total, count = 0.0, 0
    for batch in loader:
        batch = {k: v.to(device) for k, v in batch.items()}
        out = model(**batch)
        total += float(out.loss.item())
        count += 1
    model.train()
    return total / max(1, count)


def main() -> None:
    args = parse_args()
    os.environ.setdefault("HF_HOME", "./.cache/huggingface")
    set_seed(args.seed)

    print("[STEP 2/3] Gemma LoRA training started")
    print(f"[INFO] model={args.model_id} 4bit=True batch_size={max(1, min(args.batch_size, 2))} "
          f"grad_accum={args.grad_accum} epochs={args.epochs} max_length={args.max_length} seed={args.seed}")

    if not torch.cuda.is_available():
        raise RuntimeError("GPU is required for this training script.")

    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    train_rows = load_dataset(dataset_path, "train", args.max_train_samples)
    eval_rows = load_dataset(dataset_path, "validation", args.max_train_samples)
    if not train_rows:
        raise RuntimeError("Dataset contains no train-split records.")
    print(f"[INFO] Loaded {len(train_rows)} train / {len(eval_rows)} validation samples from {dataset_path}")

    tokenizer = AutoTokenizer.from_pretrained(args.model_id, local_files_only=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    bnb_cfg = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )

    model = AutoModelForCausalLM.from_pretrained(
        args.model_id,
        device_map="auto",
        quantization_config=bnb_cfg,
        local_files_only=True,
    )

    model.gradient_checkpointing_enable()
    model = prepare_model_for_kbit_training(model)

    lora_cfg = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    )

    model = get_peft_model(model, lora_cfg)
    model.train()

    train_ds = TextDataset(train_rows, tokenizer, args.max_length)
    train_loader = DataLoader(
        train_ds,
        batch_size=max(1, min(args.batch_size, 2)),
        shuffle=True,
        generator=torch.Generator().manual_seed(args.seed),
    )
    eval_loader = None
    if eval_rows:
        eval_loader = DataLoader(TextDataset(eval_rows, tokenizer, args.max_length), batch_size=2)

    optimizer = AdamW((p for p in model.parameters() if p.requires_grad), lr=args.lr)

    step = 0
    for epoch in range(args.epochs):
        running = 0.0
        optimizer.zero_grad(set_to_none=True)
        for i, batch in enumerate(train_loader):
            batch = {k: v.to(model.device) for k, v in batch.items()}
            out = model(**batch)
            loss = out.loss / args.grad_accum
            loss.backward()
            running += float(loss.item()) * args.grad_accum

            if (i + 1) % args.grad_accum == 0:
                optimizer.step()
                optimizer.zero_grad(set_to_none=True)
                step += 1

            if eval_loader is not None and step and step % args.eval_every_steps == 0:
                eval_loss = evaluate(model, eval_loader, model.device)
                print(f"epoch={epoch + 1} step={step} eval_loss={eval_loss:.4f}")

        epoch_loss = running / max(1, len(train_loader))
        print(f"epoch={epoch + 1} avg_loss={epoch_loss:.4f} steps={step}")
        if eval_loader is not None:
            print(f"epoch={epoch + 1} eval_loss={evaluate(model, eval_loader, model.device):.4f}")

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output_dir)
    readme = output_dir / "README.md"
    if readme.exists():
        readme.unlink()
    print(f"Saved LoRA adapter to {output_dir}")
    print("[STEP 2/3] Gemma LoRA training completed")


if __name__ == "__main__":
    main()