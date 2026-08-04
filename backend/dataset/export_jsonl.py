"""Export reviewed samples into training-ready JSONL.

Reads all approved samples from ``dataset/reviewed/``, deduplicates, sorts,
and writes one JSON object per line. Optionally produces a deterministic
train/validation split (JSONL files) for later LoRA fine-tuning.

The exported records carry the canonical keys consumed by the future
instruction-tuning harness:

- id, domain, difficulty
- instruction (the model prompt)
- response (the architecture JSON as a compact string)
- architecture, security, metadata (full structured payload)

Usage:
    python -m backend.dataset.export_jsonl
    python -m backend.dataset.export_jsonl --split-ratio 0.85
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from backend.dataset.schema import FINAL_DIR, REVIEWED_DIR, load_json, load_samples_from_dir, write_json

DATASET_NAME = "cybershield_arch"


def _canonical_id(sample_id: str) -> str:
    return hashlib.sha256(sample_id.encode("utf-8")).hexdigest()


def to_training_record(sample: dict) -> dict:
    architecture = sample.get("architecture", {})
    return {
        "id": sample.get("id"),
        "domain": sample.get("domain"),
        "difficulty": sample.get("difficulty"),
        "instruction": sample.get("instruction"),
        "response": json.dumps(architecture, ensure_ascii=False, sort_keys=True),
        "architecture": architecture,
        "security": sample.get("security", {}),
        "metadata": sample.get("metadata", {}),
    }


def write_split(records: list[dict], split_ratio: float | None) -> list[Path]:
    out_path = FINAL_DIR / f"{DATASET_NAME}.jsonl"
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    written = [out_path]

    if split_ratio is not None:
        hashed = [(_canonical_id(r["id"]), r) for r in records]
        hashed.sort(key=lambda item: item[0])
        pivot = max(1, int(len(hashed) * split_ratio))
        train_records = [record for _, record in hashed[:pivot]]
        valid_records = [record for _, record in hashed[pivot:]]

        train_path = FINAL_DIR / f"{DATASET_NAME}_train.jsonl"
        valid_path = FINAL_DIR / f"{DATASET_NAME}_validation.jsonl"
        for path, subset in ((train_path, train_records), (valid_path, valid_records)):
            with path.open("w", encoding="utf-8") as fh:
                for record in subset:
                    fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        written.extend([train_path, valid_path])

        manifest = {
            "dataset": DATASET_NAME,
            "total": len(records),
            "split_ratio": split_ratio,
            "train": len(train_records),
            "validation": len(valid_records),
        }
        write_json(FINAL_DIR / "split_manifest.json", manifest)

    return written


def export_jsonl(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export reviewed samples to training-ready JSONL.")
    parser.add_argument("--source", type=Path, default=REVIEWED_DIR, help="Directory with approved samples.")
    parser.add_argument("--split-ratio", type=float, default=None, help="Deterministic train/validation split (0..1).")
    args = parser.parse_args(argv)

    paths = load_samples_from_dir(args.source)
    if not paths:
        print(f"[export] no samples found in {args.source.relative_to(Path.cwd())}")
        return 1

    seen_ids: set[str] = set()
    records: list[dict] = []
    for path in paths:
        sample = load_json(path)
        sample_id = str(sample.get("id", ""))
        if not sample.get("metadata", {}).get("reviewed", False):
            print(f"[export] skipping unreviewed sample: {sample_id}")
            continue
        if sample_id in seen_ids:
            print(f"[export] skipping duplicate id: {sample_id}")
            continue
        seen_ids.add(sample_id)
        records.append(to_training_record(sample))

    written = write_split(records, args.split_ratio)
    print(
        f"[export] {len(records)} records written to "
        + ", ".join(str(path.relative_to(Path.cwd())) for path in written)
    )
    return 0


if __name__ == "__main__":
    sys.exit(export_jsonl())