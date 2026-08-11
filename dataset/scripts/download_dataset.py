"""Download Technical-Architectures-Large from HuggingFace.

Streams the dataset and snapshots samples as JSONL into dataset/raw/ for
resumable, offline use. Resume support: existing lines in the snapshot file
are skipped.

Usage:
    python -m dataset.scripts.download_dataset --limit 0    # all 293k samples
    python -m dataset.scripts.download_dataset --limit 1000 # quick test
"""

from __future__ import annotations

import argparse
import json
import sys
from itertools import islice
from pathlib import Path

from datasets import load_dataset_builder, load_dataset
from tqdm import tqdm

from dataset.scripts.common import DATASET_DIR, setup_logger

RAW_DIR = DATASET_DIR / "raw"
LOG = setup_logger("download_dataset")

HF_DATASET = "ajibawa-2023/Technical-Architectures-Large"
SPLIT = "train"
SNAPSHOT_FILE = RAW_DIR / "samples.jsonl"
META_FILE = RAW_DIR / "dataset_info.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download HF dataset into dataset/raw/")
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Number of samples to download (0 = all).",
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Stream offset (row index) to start from.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from existing snapshot (default: True).",
    )
    parser.add_argument(
        "--no-resume",
        action="store_false",
        dest="resume",
        help="Start fresh, overwrite snapshot.",
    )
    parser.set_defaults(resume=True)
    return parser.parse_args()


def write_metadata(info: dict) -> None:
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    with open(META_FILE, "w", encoding="utf-8") as fh:
        json.dump(info, fh, indent=2)


def download_samples(limit: int, resume: bool, offset: int = 0) -> int:
    LOG.info("Loading dataset builder info...")
    builder = load_dataset_builder(HF_DATASET)
    info = {
        "description": builder.info.description,
        "features": {k: str(v) for k, v in builder.info.features.items()},
        "splits": {s: ds.num_examples for s, ds in builder.info.splits.items()},
    }
    write_metadata(info)
    total_available = info["splits"].get(SPLIT, 0)
    LOG.info("Total available samples: %d", total_available)

    end = total_available
    if limit > 0:
        end = min(offset + limit, total_available)
    if end <= offset:
        LOG.info("Nothing to download (offset %d, end %d)", offset, end)
        return 0

    existing = set()
    written = 0
    mode = "a"
    if resume and SNAPSHOT_FILE.exists():
        with open(SNAPSHOT_FILE, "r", encoding="utf-8") as fh:
            for i, line in enumerate(fh):
                if line.strip():
                    existing.add(str(offset + i))
        written = len(existing)
        LOG.info("Resume: found %d existing samples in snapshot", written)
    else:
        SNAPSHOT_FILE.unlink(missing_ok=True)
        mode = "w"

    if written >= end - offset:
        LOG.info("Snapshot already complete (%d / %d)", written, end - offset)
        return written

    LOG.info("Streaming dataset (offset %d -> %d, resumable)...", offset, end)
    ds = load_dataset(HF_DATASET, streaming=True, split=SPLIT)

    with open(SNAPSHOT_FILE, mode, encoding="utf-8") as out:
        for i, row in enumerate(islice(ds, offset, end), start=offset):
            if resume and str(i) in existing:
                continue
            json.dump(row, out, ensure_ascii=False)
            out.write("\n")
            written += 1
            if written % 1000 == 0:
                LOG.info("Progress: %d / %d", written, end - offset)

    LOG.info("Download complete: %d samples written to %s", written, SNAPSHOT_FILE)
    return written


def main() -> int:
    args = parse_args()
    try:
        download_samples(args.limit, args.resume, args.offset)
        return 0
    except Exception as e:
        LOG.exception("Download failed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())