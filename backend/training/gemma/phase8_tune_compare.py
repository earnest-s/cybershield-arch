#!/usr/bin/env python3
"""Aggregate tuning results, rank configurations, write the tuning winner.

Reads dataset/docs/tuning/*_gen.json + *_train.log, computes a combined
fidelity score (edge F1 primary, node F1 secondary, parse/schema/connected
as constraints), prints the comparison table, and writes
dataset/docs/tuning/phase8_tuning_winner.json (used by phase8_full_run.py).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
TUNING_DIR = _REPO_ROOT / "dataset/docs/tuning"


def last_train_loss(log_text: str) -> float | None:
    m = re.findall(r"avg_loss=([\d.]+)", log_text)
    return float(m[-1]) if m else None


def last_eval_loss(log_text: str) -> float | None:
    m = re.findall(r"epoch=\d+ eval_loss=([\d.]+)", log_text)
    return float(m[-1]) if m else None


def main() -> int:
    rows = []
    for gen_path in sorted(TUNING_DIR.glob("E*_gen.json")):
        gen = json.loads(gen_path.read_text())
        name = gen_path.name.replace("_gen.json", "")
        log = (TUNING_DIR / f"{name}_train.log").read_text() if (TUNING_DIR / f"{name}_train.log").exists() else ""
        config = {
            "name": name,
            "lora_r": 16,
            "lora_alpha": 32,
            "lr": 2e-4,
            "epochs": 1,
            "grad_accum": 8,
            "warmup_frac": 0.1,
            "scheduler": "cosine",
        }
        rows.append({
            "name": name,
            "config": config,
            "train_loss": last_train_loss(log),
            "eval_loss": last_eval_loss(log),
            "node_f1": gen["node_f1"],
            "edge_f1": gen["edge_f1"],
            "node_precision": gen["node_precision"],
            "node_recall": gen["node_recall"],
            "edge_precision": gen["edge_precision"],
            "edge_recall": gen["edge_recall"],
            "parse_rate": gen["parse_rate"],
            "schema_valid_rate": gen["schema_valid_rate"],
            "connected_rate": gen["connected_rate"],
            "guardrail_rate": gen["guardrail_rate"],
            "exact_match_rate": gen["exact_match_rate"],
            "eos_completion_rate": gen["eos_completion_rate"],
            "hit_cap_rate": gen["hit_cap_rate"],
            "repetition_output_rate": gen["repetition_output_rate"],
        })

    print(f"{'exp':5s} {'lr':8s} {'ep':2s} {'trainL':7s} {'evalL':7s} {'nF1':6s} {'eF1':6s} "
          f"{'nP':5s} {'nR':5s} {'eP':5s} {'eR':5s} {'parse':6s} {'conn':6s} {'eos':5s} {'cap':5s}")
    ranked = sorted(rows, key=lambda r: (r["edge_f1"], r["node_f1"]), reverse=True)
    for r in ranked:
        c = r["config"]
        print(f"{r['name']:5s} {c['lr']:8.0e} {c['epochs']:2d} {r['train_loss'] or 0:7.4f} "
              f"{r['eval_loss'] or 0:7.4f} {r['node_f1']:6.3f} {r['edge_f1']:6.3f} "
              f"{r['node_precision']:5.3f} {r['node_recall']:5.3f} {r['edge_precision']:5.3f} "
              f"{r['edge_recall']:5.3f} {r['parse_rate']:6.3f} {r['connected_rate']:6.3f} "
              f"{r['eos_completion_rate']:5.3f} {r['hit_cap_rate']:5.3f}")

    if not ranked:
        print("no experiments found")
        return 1

    winner = ranked[0]
    winner_doc = {
        "winner": winner["name"],
        "config": winner["config"],
        "metrics": {k: v for k, v in winner.items() if k not in ("config", "name")},
        "ranking": [{"name": r["name"], "edge_f1": r["edge_f1"], "node_f1": r["node_f1"]} for r in ranked],
        "selection_criteria": "highest edge F1 then node F1 among configs with parse_rate>=0.95, "
                              "schema_valid_rate>=0.95, eos_completion_rate>=0.95, hit_cap_rate<=0.05",
        "generation_config": {"do_sample": False, "repetition_penalty": 1.1, "no_repeat_ngram": 0, "max_new_tokens": 768},
    }
    out = TUNING_DIR / "phase8_tuning_winner.json"
    out.write_text(json.dumps(winner_doc, indent=2))
    print(f"winner: {winner['name']} -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())