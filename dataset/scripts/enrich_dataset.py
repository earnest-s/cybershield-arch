"""Security enrichment for parsed architectures.

Uses the canonical security layer (backend.core.architecture_enricher /
response_builder) to compute required_controls, missing_controls, threats,
recommendations, risk_level, security_score, attack_surface, and
security_summary.

Output written to dataset/enriched/CSA-######.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dataset.scripts.common import DATASET_DIR, existing_ids, sample_paths, setup_logger, write_json

PARSED_DIR = DATASET_DIR / "parsed"
ENRICHED_DIR = DATASET_DIR / "enriched"

LOG = setup_logger("enrich_dataset")

# Canonical security enrichment shared with the runtime pipeline.
from backend.core.response_builder import build_security_dict


def enrich(limit: int = 0, force: bool = False) -> int:
    if not PARSED_DIR.exists():
        LOG.error("Parsed directory not found: %s. Run convert_dataset.py first.", PARSED_DIR)
        return 1

    existing = existing_ids(ENRICHED_DIR)
    ENRICHED_DIR.mkdir(parents=True, exist_ok=True)

    paths = sample_paths(PARSED_DIR)
    enriched = 0
    skipped = 0
    failed = 0

    for path in paths:
        if limit and enriched >= limit:
            break

        sample_id = path.stem
        if not force and sample_id in existing:
            skipped += 1
            continue

        try:
            sample = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            LOG.warning("%s: load failed: %s", sample_id, e)
            failed += 1
            continue

        architecture = sample.get("architecture", {})
        nodes = architecture.get("nodes", [])
        edges = architecture.get("edges", [])

        if not nodes or not edges:
            LOG.warning("%s: empty architecture, skipping", sample_id)
            failed += 1
            continue

        # Compute security using the canonical engine layer
        try:
            security = build_security_dict(nodes, edges)

            enriched_sample = {
                "id": sample["id"],
                "instruction": sample["instruction"],
                "architecture": architecture,
                "security": {
                    "required_controls": security.get("required_controls", []),
                    "missing_controls": security.get("missing_controls", []),
                    "threats": security.get("threats", []),
                    "recommendations": security.get("recommendations", []),
                    "risk_level": security.get("risk_level", "HIGH"),
                    "security_score": security.get("security_score", 0),
                    "attack_surface": security.get("attack_surface", {}),
                    "security_summary": security.get("security_summary", ""),
                },
                "metadata": sample["metadata"],
            }
            out_path = ENRICHED_DIR / f"{sample_id}.json"
            write_json(out_path, enriched_sample)
            enriched += 1

            if enriched % 500 == 0:
                LOG.info("Progress: %d enriched, %d skipped, %d failed", enriched, skipped, failed)
        except Exception as e:
            LOG.warning("%s: enrichment failed: %s", sample_id, e)
            failed += 1

    LOG.info("Done: %d enriched, %d skipped, %d failed", enriched, skipped, failed)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich parsed architectures with security analysis.")
    parser.add_argument("--limit", type=int, default=0, help="Max samples to enrich (0 = all).")
    parser.add_argument("--force", action="store_true", help="Overwrite existing enriched samples.")
    args = parser.parse_args()
    try:
        return enrich(args.limit, args.force)
    except Exception as e:
        LOG.exception("Enrichment failed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())