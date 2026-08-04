"""Schema and vocabulary helpers for the dataset pipeline.

The datasets path is the single source of truth for structural validation;
the security vocabulary constants are imported from the app's security engine
so the pipeline and the runtime share identical control/threat names.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

from backend.security.security_catalog import SECURITY_CATALOG
from backend.security.threat_detector import THREAT_KNOWLEDGE_BASE

ROOT = Path(__file__).resolve().parents[2]

SCHEMA_PATH = ROOT / "dataset" / "schemas" / "architecture_schema.json"
GENERATED_DIR = ROOT / "dataset" / "generated"
VALIDATED_DIR = ROOT / "dataset" / "validated"
REVIEWED_DIR = ROOT / "dataset" / "reviewed"
FINAL_DIR = ROOT / "dataset" / "final"
TEMPLATES_DIR = ROOT / "dataset" / "templates"
PROMPTS_DIR = ROOT / "dataset" / "prompts"
DOCS_DIR = ROOT / "dataset" / "docs"

CONTROLS: set[str] = set(SECURITY_CATALOG.keys())
THREAT_NAMES: set[str] = set(THREAT_KNOWLEDGE_BASE.keys())
ALLOWED_NODE_TYPES: set[str] = {"ui", "service", "database", "cache", "queue", "container"}
ALLOWED_EDGE_LABELS: set[str] = {"HTTP", "DB Query", "Async", "Cache"}
DIFFICULTIES: set[str] = {"easy", "medium", "hard"}
RISK_LEVELS: set[str] = {"LOW", "MEDIUM", "HIGH"}
SOURCES: set[str] = {"synthetic", "human", "model", "adapted"}


@lru_cache(maxsize=1)
def load_schema_document() -> dict[str, Any]:
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema not found: {SCHEMA_PATH}")
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _draft_validator() -> Draft7Validator:
    return Draft7Validator(load_schema_document())


def validate_schema(sample: dict[str, Any]) -> list[str]:
    """Return a sorted list of JSON Schema violations for a sample dict."""
    return sorted(error.message for error in _draft_validator().iter_errors(sample))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_samples_from_dir(directory: Path) -> list[Path]:
    """Return sorted paths to all *.json sample files in a directory."""
    if not directory.exists():
        return []
    return sorted(directory.glob("*.json"))