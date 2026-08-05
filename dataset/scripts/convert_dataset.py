"""Convert raw HuggingFace samples into parsed CyberShield architecture JSON.

Reads dataset/raw/samples.jsonl, parses Mermaid diagrams, and writes
dataset/parsed/CSA-######.json with the application node/edge contract.

Resume support: existing parsed ids are skipped unless --force is passed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dataset.scripts.common import (
    ALLOWED_EDGE_LABELS,
    ALLOWED_NODE_TYPES,
    DATASET_DIR,
    ID_PREFIX,
    existing_ids,
    sample_paths,
    setup_logger,
    write_json,
)
from dataset.scripts.mermaid_parser import parse_to_json, UnsupportedMermaidError

PARSED_DIR = DATASET_DIR / "parsed"
RAW_SNAPSHOT = DATASET_DIR / "raw" / "samples.jsonl"

LOG = setup_logger("convert_dataset")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert raw samples to parsed architecture JSON.")
    parser.add_argument("--limit", type=int, default=0, help="Max samples to convert (0 = all).")
    parser.add_argument("--force", action="store_true", help="Overwrite existing parsed samples.")
    return parser.parse_args()


def _instruction_from_metadata(meta: dict) -> str:
    domain = meta.get("domain", "")
    style = meta.get("style", "")
    cloud = meta.get("cloud", "")
    constraints = meta.get("constraints", [])
    parts = []
    if domain:
        parts.append(f"Design a {domain} architecture")
    if style:
        parts.append(f"using a {style} style")
    if cloud:
        parts.append(f"deployed on {cloud}")
    if constraints:
        parts.append(f"satisfying: {', '.join(constraints)}")
    return ". ".join(parts) + "."


def convert(limit: int = 0, force: bool = False) -> int:
    if not RAW_SNAPSHOT.exists():
        LOG.error("Raw snapshot not found: %s. Run download_dataset.py first.", RAW_SNAPSHOT)
        return 1

    existing = existing_ids(PARSED_DIR)
    PARSED_DIR.mkdir(parents=True, exist_ok=True)

    converted = 0
    skipped = 0
    failed = 0

    with open(RAW_SNAPSHOT, "r", encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if limit and converted >= limit:
                break
            if not line.strip():
                continue

            raw = json.loads(line)
            raw_id = raw.get("id")
            sample_id = f"{ID_PREFIX}-{raw_id:06d}"

            if not force and sample_id in existing:
                skipped += 1
                continue

            mermaid = raw.get("mermaid", "")
            if not mermaid:
                LOG.warning("Sample %s: missing mermaid, skipping", sample_id)
                failed += 1
                continue

            try:
                arch = parse_to_json(mermaid)
            except Exception as e:
                LOG.warning("Sample %s: parse failed: %s", sample_id, e)
                failed += 1
                continue

            nodes = arch.get("nodes", [])
            edges = arch.get("edges", [])

            # Validate node/edge contract
            for n in nodes:
                if n.get("type") not in ALLOWED_NODE_TYPES:
                    LOG.warning("Sample %s: invalid node type %s, skipping", sample_id, n.get("type"))
                    failed += 1
                    break
            else:
                for e in edges:
                    if e.get("label") not in ALLOWED_EDGE_LABELS:
                        LOG.warning("Sample %s: invalid edge label %s, skipping", sample_id, e.get("label"))
                        failed += 1
                        break
                else:
                    # All good
                    out = {
                        "id": sample_id,
                        "instruction": _instruction_from_metadata(raw),
                        "architecture": {"nodes": nodes, "edges": edges},
                        "metadata": {
                            "domain": raw.get("domain", ""),
                            "style": raw.get("style", ""),
                            "cloud": raw.get("cloud", ""),
                            "complexity": raw.get("target_complexity", ""),
                            "constraints": raw.get("constraints", []),
                            "diagram_type": raw.get("diagram_type", ""),
                            "source_nodes": raw.get("nodes", 0),
                            "source_edges": raw.get("edges", 0),
                            "source": "Technical-Architectures-Large",
                            "version": "1.0",
                        },
                    }
                    out_path = PARSED_DIR / f"{sample_id}.json"
                    write_json(out_path, out)
                    converted += 1

                    if converted % 500 == 0:
                        LOG.info("Progress: %d converted, %d skipped, %d failed", converted, skipped, failed)

    LOG.info("Done: %d converted, %d skipped, %d failed", converted, skipped, failed)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert raw HF samples to parsed architecture JSON.")
    parser.add_argument("--limit", type=int, default=0, help="Max samples to convert (0 = all).")
    parser.add_argument("--force", action="store_true", help="Overwrite existing parsed samples.")
    args = parser.parse_args()
    try:
        return convert(args.limit, args.force)
    except Exception as e:
        LOG.exception("Conversion failed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())