#!/usr/bin/env python3
"""Phase 8 FULL training runner (46,348 records, approved configuration).

- Training: backend/training/gemma/lora_train.py with the approved Phase 8
  configuration (config values from the tuning winner are injected via flags).
- Adapter: checkpoints/gemma_lora (production path used by inference.py).
- Records environment/package/GPU versions and run metrics.
- Streams output to dataset/docs/phase8_full_run.log

The FULL run must not start before the tuning stage selects a configuration
(phase8_tuning_winner.json) unless --override-config is provided.

Usage:
    uv run python backend/training/gemma/phase8_full_run.py [--epochs 2]
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]

APPROVED_DEFAULTS = {
    "epochs": 2,
    "lr": 2e-4,
    "lora_r": 16,
    "lora_alpha": 32,
    "grad_accum": 8,
    "warmup_frac": 0.1,
    "scheduler": "cosine",
    "max_length": 1024,
    "max_train_samples": 46348,
    "max_eval_samples": 2575,
    "seed": 42,
}


def record_environment() -> dict:
    info = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "git_rev": subprocess.run(
            ["git", "-C", str(_REPO_ROOT), "rev-parse", "HEAD"], capture_output=True, text=True
        ).stdout.strip(),
    }
    import accelerate
    import bitsandbytes
    import peft
    import torch
    import transformers

    info["torch"] = torch.__version__
    info["transformers"] = transformers.__version__
    info["peft"] = peft.__version__
    info["bitsandbytes"] = bitsandbytes.__version__
    info["accelerate"] = accelerate.__version__
    info["cuda"] = torch.version.cuda
    gpu = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"], capture_output=True, text=True)
    info["gpu"] = gpu.stdout.strip() if gpu.returncode == 0 else "nvidia-smi unavailable"
    return info


def main() -> int:
    parser = argparse.ArgumentParser()
    for key, default in APPROVED_DEFAULTS.items():
        parser.add_argument(f"--{key}", type=float if isinstance(default, float) else int, default=default)
    parser.add_argument("--override-config", action="store_true", help="allow run even without tuning winner")
    args = parser.parse_args()

    winner_path = _REPO_ROOT / "dataset/docs/tuning/phase8_tuning_winner.json"
    if winner_path.exists():
        winner = json.loads(winner_path.read_text())
        for key in ("epochs", "lr", "lora_r", "lora_alpha", "grad_accum", "warmup_frac"):
            setattr(args, key, winner.get("config", {}).get(key, getattr(args, key)))
        print(f"[INFO] using tuning winner config: {winner['config']}")
    elif not args.override_config:
        raise SystemExit("no phase8_tuning_winner.json — refuse to start FULL run without a selected config")

    env_info = record_environment()
    print(f"[INFO] environment: {json.dumps(env_info, indent=2)}")

    log_path = _REPO_ROOT / "dataset/docs/phase8_full_run.log"
    cmd = [
        sys.executable, "-u", str(_REPO_ROOT / "backend/training/gemma/lora_train.py"),
        "--dataset", str(_REPO_ROOT / "dataset/training/CyberShield_Gemma_SFT_v1.jsonl"),
        "--output", str(_REPO_ROOT / "checkpoints/gemma_lora"),
        "--max-train-samples", str(args.max_train_samples),
        "--max-eval-samples", str(args.max_eval_samples),
        "--epochs", str(args.epochs),
        "--lr", str(args.lr),
        "--lora-r", str(args.lora_r),
        "--lora-alpha", str(args.lora_alpha),
        "--grad-accum", str(args.grad_accum),
        "--warmup-frac", str(args.warmup_frac),
        "--scheduler", args.scheduler,
        "--eval-every-steps", "1000",
        "--seed", str(args.seed),
        "--max-length", str(args.max_length),
    ]
    t0 = time.time()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    with log_path.open("w") as f:
        for line in proc.stdout:
            f.write(line)
            f.flush()
            print(line, end="", flush=True)
    proc.wait()
    wall = time.time() - t0

    metrics = {
        "returncode": proc.returncode,
        "wall_seconds": round(wall, 1),
        "environment": env_info,
        "config": vars(args),
        "adapter_path": "checkpoints/gemma_lora",
        "log_path": "dataset/docs/phase8_full_run.log",
    }
    out = _REPO_ROOT / "dataset/docs/phase8_full_run_metrics.json"
    out.write_text(json.dumps(metrics, indent=2))
    print(f"[INFO] metrics written to {out}")
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())