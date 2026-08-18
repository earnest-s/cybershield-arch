#!/usr/bin/env python3
"""Phase 8 STEP 5/6: pilot run + checkpoint verification + generation eval.

Runs the production harness (backend/training/gemma/lora_train.py) on a small
REAL pilot subset, then verifies the checkpoint: reload, generate, decode,
parse, canonical validation. Step 6 metrics are written to
dataset/docs/phase8_pilot_metrics.json.

Usage:
    uv run python backend/training/gemma/phase8_pilot_run.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

MODEL_ID = "unsloth/gemma-3-4b-it-bnb-4bit"
DATASET = "dataset/training/CyberShield_Gemma_SFT_v1.jsonl"
PILOT_ADAPTER = "checkpoints/gemma_lora_pilot"
N_TRAIN = 400
N_VAL = 100
EPOCHS = 1
GRAD_ACCUM = 8
EVAL_EVERY = 8
SEED = 42
MAX_LENGTH = 1024
N_GEN = 50


def run_cmd_live(cmd: list) -> dict:
    """Run a subprocess streaming stdout/stderr to the terminal in real time."""
    t0 = time.time()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    lines: list[str] = []
    for line in proc.stdout:
        lines.append(line)
        print(line, end="", flush=True)
    proc.wait()
    wall = time.time() - t0
    return {"wall_seconds": round(wall, 1), "returncode": proc.returncode, "log_tail": "".join(lines)[-2000:]}


def run_training() -> dict:
    cmd = [
        sys.executable, "-u", "backend/training/gemma/lora_train.py",
        "--dataset", DATASET,
        "--output", PILOT_ADAPTER,
        "--model-id", MODEL_ID,
        "--max-train-samples", str(N_TRAIN),
        "--max-eval-samples", str(N_VAL),
        "--epochs", str(EPOCHS),
        "--grad-accum", str(GRAD_ACCUM),
        "--eval-every-steps", str(EVAL_EVERY),
        "--seed", str(SEED),
        "--max-length", str(MAX_LENGTH),
    ]
    return run_cmd_live(cmd)


def main() -> int:
    metrics: dict = {}
    print(f"=== PILOT TRAINING: {N_TRAIN} train / {N_VAL} validation, {EPOCHS} epoch ===")
    train_metrics = run_training()
    metrics["training"] = train_metrics
    if train_metrics["returncode"] != 0:
        print("PILOT TRAINING FAILED")
        json.dump(metrics, open("dataset/docs/phase8_pilot_metrics.json", "w"), indent=2)
        return 1
    metrics["adapter_path"] = PILOT_ADAPTER
    print(f"=== TRAINING DONE in {train_metrics['wall_seconds']}s ===")

    eval_script = Path("backend/training/gemma/phase8_pilot_eval.py")
    if eval_script.exists():
        print("=== GENERATION EVAL ===")
        eval_metrics = run_cmd_live(
            [sys.executable, "-u", str(eval_script),
             "--adapter", PILOT_ADAPTER, "--n-gen", str(N_GEN), "--seed", str(SEED)]
        )
        metrics["generation_eval_wall_seconds"] = eval_metrics["wall_seconds"]
        metrics["generation_eval_returncode"] = eval_metrics["returncode"]
        if eval_metrics["returncode"] != 0:
            print("GENERATION EVAL FAILED")
            json.dump(metrics, open("dataset/docs/phase8_pilot_metrics.json", "w"), indent=2)
            return 1

    json.dump(metrics, open("dataset/docs/phase8_pilot_metrics.json", "w"), indent=2)
    print("Metrics written to dataset/docs/phase8_pilot_metrics.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())