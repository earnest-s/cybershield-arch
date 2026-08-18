#!/usr/bin/env python3
"""Phase 8 quality gates — run AFTER pilot evaluation.

Gates (all must PASS for Phase 8 pilot to be considered complete):

G1  Dataset corpus immutable        — dataset/final SHA256 == e3ee9810e13ba66…  (manifest value)
G2  SFT artifact immutable          — dataset/training SHA256 == 8c91e5cd017df949… (Phase 7 value)
G3  Pilot adapter exists            — checkpoints/gemma_lora_pilot/{adapter_config.json,adapter_model.safetensors}
G4  Generation eval JSON present    — dataset/docs/phase8_pilot_generation_eval.json, n==50
G5  Format gates (pilot measured)   — parse_rate >= 0.80, schema_valid_rate >= 0.80,
                                      connected_rate == 1.0, structurally_weak_rate == 0.0,
                                      guardrail rate on parsed outputs == 1.0
                                      (no semantic-fidelity gates: fabrication is reported
                                      as a diagnostic, not gated, at pilot stage)

Exit 0 if all gates pass, 1 otherwise. Prints a per-gate report.

Semantic fidelity is intentionally NOT gated here: the pilot is a pipeline
validation run (400 records / 1 epoch). Fabrication/missing metrics are
reported in phase8_training_pilot_report.md as diagnostics.

Usage:
    uv run python backend/training/gemma/phase8_quality_gates.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]

CORPUS_SHA = "e3ee9810e13ba660f6f39b93f35e318aa26f22eccf5b7ea59c57ef05f5a1b36b"
SFT_SHA = "8c91e5cd017df9490f24b5c9f016f01c871e5531b4072c7f83d6959301b851ec"

CORPUS_PATH = _REPO_ROOT / "dataset/final/CyberShield_Dataset_v1_FULL.jsonl"
SFT_PATH = _REPO_ROOT / "dataset/training/CyberShield_Gemma_SFT_v1.jsonl"
ADAPTER_DIR = _REPO_ROOT / "checkpoints/gemma_lora_pilot"
EVAL_JSON = _REPO_ROOT / "dataset/docs/phase8_pilot_generation_eval.json"

GATES = [
    ("G1 corpus immutable", CORPUS_SHA, CORPUS_PATH),
    ("G2 SFT artifact immutable", SFT_SHA, SFT_PATH),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    results: list[tuple[str, bool, str]] = []

    for name, expected, path in GATES:
        actual = sha256(path) if path.exists() else "MISSING"
        ok = actual == expected
        results.append((name, ok, f"{path.name} sha256 {actual[:12]}… (expected {expected[:12]}…)"))

    adapter_files = {"adapter_config.json", "adapter_model.safetensors"}
    present = {p.name for p in ADAPTER_DIR.iterdir()} if ADAPTER_DIR.is_dir() else set()
    ok = adapter_files.issubset(present)
    results.append(("G3 pilot adapter exists", ok, f"files: {sorted(present)}"))

    eval_data = None
    if EVAL_JSON.exists():
        eval_data = json.loads(EVAL_JSON.read_text())
    ok = eval_data is not None and eval_data.get("n") == 50 and "parse_rate" in eval_data
    results.append(("G4 generation eval JSON present", ok, f"n={eval_data.get('n') if eval_data else None}"))

    if eval_data:
        parsed = eval_data["parse_ok"]
        checks = {
            "parse_rate >= 0.80": eval_data["parse_rate"] >= 0.80,
            "schema_valid_rate >= 0.80": eval_data["schema_valid_rate"] >= 0.80,
            "connected_rate == 1.0": eval_data["connected_rate"] == 1.0,
            "structurally_weak_rate == 0.0": eval_data["structurally_weak_rate"] == 0.0,
            "guardrail on parsed == 1.0": eval_data["within_guardrail"] == parsed,
        }
        for label, passed in checks.items():
            results.append(("G5 " + label, passed, ""))
    else:
        results.append(("G5 format gates", False, "no eval data"))

    width = max(len(name) for name, _, _ in results)
    all_ok = True
    print("PHASE 8 QUALITY GATES")
    print("=" * (width + 14))
    for name, ok, detail in results:
        all_ok = all_ok and ok
        print(f"{name.ljust(width)}  {'PASS' if ok else 'FAIL'}  {detail}")
    print("=" * (width + 14))
    print(f"OVERALL: {'PASS' if all_ok else 'FAIL'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())