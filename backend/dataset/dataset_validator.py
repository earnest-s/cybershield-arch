"""Validation gate for the dataset pipeline.

Checks performed per sample:

- JSON Schema compliance (dataset/schemas/architecture_schema.json)
- Node validity: allowed types, non-empty unique ids
- Edge validity: source/target reference existing nodes, no self-loops,
  allowed labels, no duplicate edges
- Security-label consistency: stored missing/required controls, score, risk
  level, and threat names must match a fresh run of the production security
  engine (no stale or invented labels)

Batch-level checks:

- Duplicate sample ids
- Duplicate architectures (canonical serialization)

Only fully valid samples are moved into ``dataset/validated/``; invalid
samples are left in place and reported. A machine-readable report is written
to ``dataset/docs/validation_report.json``.

Usage:
    python -m backend.dataset.dataset_validator
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from backend.core.architecture_schema import canonical_architecture
from backend.dataset.schema import (
    ALLOWED_EDGE_LABELS,
    ALLOWED_NODE_TYPES,
    DOCS_DIR,
    GENERATED_DIR,
    VALIDATED_DIR,
    load_json,
    load_samples_from_dir,
    validate_schema,
    write_json,
)
from backend.dataset.security import assert_security_consistency


@dataclass(slots=True)
class ValidationIssue:
    sample_id: str
    field: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"sample_id": self.sample_id, "field": self.field, "message": self.message}


@dataclass(slots=True)
class ValidationResult:
    valid: list[Path] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)


def validate_sample(sample: dict[str, Any]) -> list[ValidationIssue]:
    """Validate one sample dict; returns an empty list when fully valid."""
    issues: list[ValidationIssue] = []
    sample_id = str(sample.get("id", ""))

    for message in validate_schema(sample):
        issues.append(ValidationIssue(sample_id, "schema", message))

    architecture = sample.get("architecture", {})
    nodes = architecture.get("nodes", [])
    edges = architecture.get("edges", [])

    node_ids: list[str] = []
    for node in nodes:
        node_id = str(node.get("id", ""))
        node_type = str(node.get("type", ""))
        if not node_id.strip():
            issues.append(ValidationIssue(sample_id, "node", "node with empty id"))
        if node_id in node_ids:
            issues.append(ValidationIssue(sample_id, "node", f"duplicate node id: {node_id}"))
        node_ids.append(node_id)
        if node_type not in ALLOWED_NODE_TYPES:
            issues.append(ValidationIssue(sample_id, "node", f"invalid node type: {node_type}"))

    allowed_ids = set(node_ids)
    seen_edges: set[tuple[str, str]] = set()
    for edge in edges:
        source = str(edge.get("source", ""))
        target = str(edge.get("target", ""))
        label = str(edge.get("label", ""))
        if source not in allowed_ids:
            issues.append(ValidationIssue(sample_id, "edge", f"source references unknown node: {source}"))
        if target not in allowed_ids:
            issues.append(ValidationIssue(sample_id, "edge", f"target references unknown node: {target}"))
        if source == target and source:
            issues.append(ValidationIssue(sample_id, "edge", f"self-loop: {source} -> {source}"))
        if label not in ALLOWED_EDGE_LABELS:
            issues.append(ValidationIssue(sample_id, "edge", f"invalid edge label: {label}"))
        key = (source, target)
        if key in seen_edges:
            issues.append(ValidationIssue(sample_id, "edge", f"duplicate edge: {source} -> {target}"))
        seen_edges.add(key)

    for message in assert_security_consistency(nodes, edges, sample.get("security", {})):
        issues.append(ValidationIssue(sample_id, "security", message))

    return issues


def validate_samples(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate generated samples and promote valid ones.")
    parser.add_argument("--source", type=Path, default=GENERATED_DIR, help="Directory with candidate samples.")
    parser.add_argument("--target", type=Path, default=VALIDATED_DIR, help="Directory for valid samples.")
    parser.add_argument("--move", action="store_true", help="Move valid samples into target (default: copy).")
    args = parser.parse_args(argv)

    paths = load_samples_from_dir(args.source)
    result = ValidationResult()
    seen_ids: set[str] = set()
    seen_architectures: dict[str, str] = {}

    for path in paths:
        sample = load_json(path)
        sample_id = str(sample.get("id", ""))

        if sample_id in seen_ids:
            result.issues.append(ValidationIssue(sample_id, "batch", "duplicate sample id across batch"))
            continue
        seen_ids.add(sample_id)

        canonical = canonical_architecture(sample.get("architecture", {}))
        if canonical in seen_architectures:
            result.issues.append(
                ValidationIssue(sample_id, "batch", f"duplicate architecture with {seen_architectures[canonical]}")
            )
            continue
        seen_architectures[canonical] = sample_id

        issues = validate_sample(sample)
        if issues:
            result.issues.extend(issues)
            continue
        result.valid.append(path)

    for path in result.valid:
        if args.move:
            path.rename(args.target / path.name)
        else:
            write_json(args.target / path.name, load_json(path))

    report = {
        "checked": len(paths),
        "valid": len(result.valid),
        "invalid": len(paths) - len(result.valid),
        "issues": [issue.to_dict() for issue in result.issues],
    }
    write_json(DOCS_DIR / "validation_report.json", report)

    print(
        f"[validator] {len(result.valid)}/{len(paths)} samples valid -> {args.target.relative_to(Path.cwd())}; "
        f"{len(result.issues)} issues (see {DOCS_DIR / 'validation_report.json'})"
    )
    for issue in result.issues[:20]:
        print(f"  - [{issue.sample_id}] {issue.field}: {issue.message}")
    return 1 if result.issues else 0


if __name__ == "__main__":
    sys.exit(validate_samples())