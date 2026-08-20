#!/usr/bin/env python3
"""Phase 8 tuning experiment runner.

Trains a configuration on a fixed deterministic subset of the train split
(first N records in file order — the seeded DataLoader shuffle happens inside
lora_train.py with seed 42) and evaluates it on held-out validation prompts
with the rich fidelity metrics.

Per-experiment artifacts:
- adapter:            checkpoints/exp_<name>/
- training log:       dataset/docs/tuning/<name>_train.log
- generation metrics: dataset/docs/tuning/<name>_gen.json

Usage:
    uv run python backend/training/gemma/phase8_tune_experiment.py \
        --name E1 --lora-r 16 --lora-alpha 32 --lr 2e-4 --epochs 1 --n-train 800

No dataset/test-split modification. Seed 42 everywhere.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_N_TRAIN = 800
DEFAULT_N_EVAL_GEN = 100
EVAL_SPLIT = "validation"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--name", required=True)
    p.add_argument("--n-train", type=int, default=DEFAULT_N_TRAIN)
    p.add_argument("--n-eval-gen", type=int, default=DEFAULT_N_EVAL_GEN)
    p.add_argument("--epochs", type=int, default=1)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--lora-r", type=int, default=16)
    p.add_argument("--lora-alpha", type=int, default=32)
    p.add_argument("--grad-accum", type=int, default=8)
    p.add_argument("--warmup-frac", type=float, default=0.1)
    p.add_argument("--scheduler", choices=["cosine", "none"], default="cosine")
    p.add_argument("--eval-every-steps", type=int, default=100000)
    p.add_argument("--gen-batch", type=int, default=3)
    p.add_argument("--repetition-penalty", type=float, default=1.0)
    p.add_argument("--no-repeat-ngram", type=int, default=0)
    p.add_argument("--max-new-tokens", type=int, default=768)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--max-length", type=int, default=1024)
    return p.parse_args()


def run_live(cmd: list, log_path: Path) -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(_REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    t0 = time.time()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=env)
    with log_path.open("w") as f:
        for line in proc.stdout:
            f.write(line)
            f.flush()
            print(line, end="", flush=True)
    proc.wait()
    return {"returncode": proc.returncode, "wall_seconds": round(time.time() - t0, 1)}


def main() -> int:
    args = parse_args()
    out_dir = _REPO_ROOT / "dataset/docs/tuning"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {"name": args.name, "args": vars(args)}

    train_cmd = [
        sys.executable, "-u", str(_REPO_ROOT / "backend/training/gemma/lora_train.py"),
        "--dataset", str(_REPO_ROOT / "dataset/training/CyberShield_Gemma_SFT_v1.jsonl"),
        "--output", str(_REPO_ROOT / f"checkpoints/exp_{args.name}"),
        "--max-train-samples", str(args.n_train),
        "--max-eval-samples", "0",
        "--epochs", str(args.epochs),
        "--lr", str(args.lr),
        "--lora-r", str(args.lora_r),
        "--lora-alpha", str(args.lora_alpha),
        "--grad-accum", str(args.grad_accum),
        "--warmup-frac", str(args.warmup_frac),
        "--scheduler", args.scheduler,
        "--eval-every-steps", str(args.eval_every_steps),
        "--seed", str(args.seed),
        "--max-length", str(args.max_length),
    ]
    train_log = out_dir / f"{args.name}_train.log"
    print(f"=== EXPERIMENT {args.name}: n_train={args.n_train} epochs={args.epochs} "
          f"lr={args.lr} r={args.lora_r} alpha={args.lora_alpha} accum={args.grad_accum} "
          f"warmup={args.warmup_frac} sched={args.scheduler} ===")
    train_res = run_live(train_cmd, train_log)
    summary["training"] = train_res
    if train_res["returncode"] != 0:
        summary["training_error"] = train_log.read_text()[-2000:]
        (out_dir / f"{args.name}.json").write_text(json.dumps(summary, indent=2))
        return 1

    gen_cmd = [
        sys.executable, "-u", str(_REPO_ROOT / "backend/training/gemma/phase8_generate_eval.py"),
        "--adapter", str(_REPO_ROOT / f"checkpoints/exp_{args.name}"),
        "--split", EVAL_SPLIT,
        "--n-gen", str(args.n_eval_gen),
        "--gen-batch", str(args.gen_batch),
        "--repetition-penalty", str(args.repetition_penalty),
        "--no-repeat-ngram", str(args.no_repeat_ngram),
        "--max-new-tokens", str(args.max_new_tokens),
        "--seed", str(args.seed),
        "--out", f"dataset/docs/tuning/{args.name}_gen.json",
    ]
    print(f"=== GENERATION EVAL ({args.n_eval_gen} {EVAL_SPLIT} prompts) ===")
    gen_res = run_live(gen_cmd, out_dir / f"{args.name}_gen.log")
    summary["generation_eval"] = gen_res

    gen_path = out_dir / f"{args.name}_gen.json"
    if gen_path.exists():
        summary["metrics"] = json.loads(gen_path.read_text())
    else:
        summary["metrics"] = None

    (out_dir / f"{args.name}.json").write_text(json.dumps(summary, indent=2))
    print(f"=== EXPERIMENT {args.name} DONE: {json.dumps(summary.get('metrics') or {})[:400]} ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())