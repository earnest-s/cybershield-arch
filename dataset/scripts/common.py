"""Shared helpers for the dataset pipeline scripts.

Provides path conventions, logging setup, JSON I/O with resume support, and
re-exports the canonical vocabulary from backend.core.architecture_schema so
the pipeline stays aligned with the runtime (backend/core/*).
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

from backend.core.architecture_schema import (
    ALLOWED_EDGE_LABELS,
    ALLOWED_NODE_TYPES,
    canonical_architecture,
)

ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = ROOT / "dataset"
LOGS_DIR = DATASET_DIR / "logs"

ID_PREFIX = "CSA"


def setup_logger(name: str) -> logging.Logger:
    """Create a logger writing to both logs/<name>.log and the console."""
    logger = logging.getLogger(f"dataset.{name}")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s")

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(LOGS_DIR / f"{name}.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)
    return logger


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, payload: Any, *, pretty: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    indent = 2 if pretty else None
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=indent, ensure_ascii=False)


def sample_paths(directory: Path) -> list[Path]:
    """Return sorted *.json sample paths in a directory."""
    if not directory.exists():
        return []
    return sorted(directory.glob("*.json"))


def existing_ids(directory: Path) -> set[str]:
    """Ids already processed in a directory, for resume support."""
    ids: set[str] = set()
    for path in sample_paths(directory):
        try:
            payload = load_json(path)
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(payload, dict) and isinstance(payload.get("id"), str):
            ids.add(payload["id"])
    return ids
