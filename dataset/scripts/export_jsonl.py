"""Export reviewed samples to training-ready JSONL.

Produces CyberShield_Dataset_v1.jsonl in dataset/final/ with the exact
record shape required for Gemma LoRA fine-tuning.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dataset.scripts.common import DATASET_DIR, sample_paths, setup_logger

REVIEWED_DIR = DATASET_DIR / "reviewed"
FINAL_DIR = DATASET_DIR / "final"
OUTPUT_FILE = FINAL_DIR / "CyberShield_Dataset_v1.jsonl"

LOG = setup_logger("export_jsonl")


def export(limit: int = 0) -> int:
    if not REVIEWED_DIR.exists():
        LOG.error("Reviewed directory not found. Run review_dataset.py first.")
        return 1

    paths = sample_paths(REVIEWED_DIR)
    if not paths:
        LOG.error("No reviewed samples found.")
        return 1

    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    exported = 0

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for path in paths:
            if limit and exported >= limit:
                break

            try:
                sample = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as e:
                LOG.warning("%s: load failed: %s", path.stem, e)
                continue

            if not sample.get("metadata", {}).get("reviewed", False):
                LOG.warning("%s: not marked reviewed, skipping", path.stem)
                continue

            record = {
                "id": sample["id"],
                "instruction": sample["instruction"],
                "architecture": sample["architecture"],
                "security": {
                    "required_controls": sample["security"].get("required_controls", []),
                    "missing_controls": sample["security"].get("missing_controls", []),
                    "threats": sample["security"].get("threats", []),
                    "recommendations": sample["security"].get("recommendations", []),
                    "risk_level": sample["security"].get("risk_level", "HIGH"),
                    "security_score": sample["security"].get("security_score", 0),
                    "attack_surface": sample["security"].get("attack_surface", {}),
                    "security_summary": sample["security"].get("security_summary", ""),
                },
                "metadata": {
                    "domain": sample["metadata"].get("domain", ""),
                    "style": sample["metadata"].get("style", ""),
                    "cloud": sample["metadata"].get("cloud", ""),
                    "complexity": sample["metadata"].get("complexity", ""),
                    "source": sample["metadata"].get("source", "Technical-Architectures-Large"),
                    "reviewed": True,
                    "version": "1.0",
                },
            }
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            exported += 1

            if exported % 1000 == 0:
                LOG.info("Progress: %d records written", exported)

    LOG.info("Export complete: %d records written to %s", exported, OUTPUT_FILE)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Export reviewed samples to training JSONL.")
    parser.add_argument("--limit", type=int, default=0, help="Max records to export (0 = all).")
    args = parser.parse_args()
    try:
        return export(args.limit)
    except Exception as e:
        LOG.exception("Export failed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())