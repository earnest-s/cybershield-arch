"""Human review gate for the dataset pipeline.

Loads validated samples, displays each one cleanly, and asks the reviewer to
mark it:

- ``a`` approve -> written to ``dataset/reviewed/`` with ``reviewed: true``
- ``r`` reject  -> logged as rejected (sample left untouched)
- ``e`` edit    -> edit the instruction inline, then re-approve
- ``s`` skip    -> leave for later
- ``q`` quit

A review log is written to ``dataset/docs/review_log.json`` so the pipeline
stays auditable.

Usage:
    python -m backend.dataset.review_dataset
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from backend.dataset.models import Metadata, Sample
from backend.dataset.schema import DOCS_DIR, REVIEWED_DIR, VALIDATED_DIR, load_json, load_samples_from_dir, write_json


def display_sample(sample: dict) -> None:
    print("=" * 78)
    print(f"ID: {sample.get('id')} | domain: {sample.get('domain')} | difficulty: {sample.get('difficulty')}")
    print("-" * 78)
    print("INSTRUCTION:")
    print(sample.get("instruction", ""))
    print("-" * 78)
    architecture = sample.get("architecture", {})
    print("NODES:")
    for node in architecture.get("nodes", []):
        print(f"  - {node.get('id'):<28} type={node.get('type')}")
    print("EDGES:")
    for edge in architecture.get("edges", []):
        print(f"  - {edge.get('source')} -> {edge.get('target')}  [{edge.get('label')}]")
    security = sample.get("security", {})
    print("-" * 78)
    print("SECURITY:")
    print(f"  score={security.get('security_score')} risk={security.get('risk_level')}")
    print(f"  missing={security.get('missing_controls')}")
    print(f"  threats={[t.get('name') for t in security.get('threats', [])]}")
    print(f"  recommendations={security.get('recommendations')}")
    print("=" * 78)


def review_one(sample: dict, auto: str | None) -> tuple[str, dict]:
    """Return (decision, maybe-edited sample)."""
    display_sample(sample)
    if auto:
        decision = auto
        print(f"(auto) decision: {decision}")
    else:
        decision = input("[a]pprove  [r]eject  [e]dit  [s]kip  [q]uit > ").strip().lower()
    if decision not in {"a", "r", "e", "s", "q"}:
        print(f"unknown decision: {decision!r}")
        return "s", sample
    if decision == "e":
        new_instruction = input("new instruction > ").strip()
        if new_instruction:
            sample["instruction"] = new_instruction
    return decision, sample


def run_review(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Human review of validated samples.")
    parser.add_argument("--source", type=Path, default=VALIDATED_DIR, help="Directory with validated samples.")
    parser.add_argument("--target", type=Path, default=REVIEWED_DIR, help="Directory for approved samples.")
    parser.add_argument("--auto", choices=["a", "r", "s"], default=None, help="Non-interactive decision (pipeline demos).")
    args = parser.parse_args(argv)

    paths = load_samples_from_dir(args.source)
    if not paths:
        print(f"[reviewer] no samples found in {args.source.relative_to(Path.cwd())}")
        return 0

    log: list[dict] = []
    approved = 0
    for path in paths:
        sample = load_json(path)
        decision, edited = review_one(sample, args.auto)
        log.append({"sample_id": sample.get("id"), "decision": decision})

        if decision == "q":
            break
        if decision == "a":
            edited["metadata"] = Metadata(
                source=edited.get("metadata", {}).get("source", "synthetic"),
                generated_by=edited.get("metadata", {}).get("generated_by", "unknown"),
                reviewed=True,
                version=edited.get("metadata", {}).get("version", "1.0"),
            ).to_dict()
            write_json(args.target / f"{sample.get('id')}.json", edited)
            approved += 1
            print(f"[reviewer] approved -> {args.target.relative_to(Path.cwd())}/{sample.get('id')}.json")

    write_json(DOCS_DIR / "review_log.json", log)
    print(f"[reviewer] done: {approved} approved, {len(log) - approved} not approved")
    return 0


if __name__ == "__main__":
    sys.exit(run_review())