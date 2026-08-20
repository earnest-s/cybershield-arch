"""Human review gate for validated samples.

Interactive CLI to approve/reject/needs-edit. Approved samples move to
dataset/reviewed/ with metadata.reviewed=true. All decisions logged.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dataset.scripts.common import DATASET_DIR, sample_paths, setup_logger, write_json

VALIDATED_DIR = DATASET_DIR / "validated"
REVIEWED_DIR = DATASET_DIR / "reviewed"
LOGS_DIR = DATASET_DIR / "logs"

LOG = setup_logger("review_dataset")

DECISION_LOG = LOGS_DIR / "review_decisions.jsonl"


def _load_log() -> dict[str, str]:
    if not DECISION_LOG.exists():
        return {}
    decisions = {}
    with open(DECISION_LOG, "r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rec = json.loads(line)
                decisions[rec["sample_id"]] = rec["decision"]
    return decisions


def _log_decision(sample_id: str, decision: str) -> None:
    DECISION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(DECISION_LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"sample_id": sample_id, "decision": decision}) + "\n")


def _display_sample(sample: dict) -> None:
    print("=" * 80)
    print(f"ID: {sample['id']} | Domain: {sample['metadata'].get('domain')} | "
          f"Style: {sample['metadata'].get('style')} | "
          f"Cloud: {sample['metadata'].get('cloud')} | "
          f"Complexity: {sample['metadata'].get('complexity')}")
    print("-" * 80)
    print("INSTRUCTION:")
    print(sample["instruction"])
    print("-" * 80)
    print("ARCHITECTURE:")
    for n in sample["architecture"]["nodes"]:
        print(f"  - {n['id']:<30} [{n['type']}]")
    for e in sample["architecture"]["edges"]:
        print(f"  - {e['source']} -> {e['target']}  [{e['label']}]")
    sec = sample["security"]
    print("-" * 80)
    print("SECURITY:")
    print(f"  Score: {sec['security_score']} | Risk: {sec['risk_level']}")
    print(f"  Required: {sec.get('required_controls', [])}")
    print(f"  Missing:  {sec.get('missing_controls', [])}")
    print(f"  Threats:  {[t.get('name') for t in sec.get('threats', [])]}")
    print(f"  Recs:     {sec.get('recommendations', [])}")
    print("-" * 80)


def review(limit: int = 0, auto: str | None = None) -> int:
    if not VALIDATED_DIR.exists():
        LOG.error("Validated directory not found. Run validate_dataset.py first.")
        return 1

    already = _load_log()
    REVIEWED_DIR.mkdir(parents=True, exist_ok=True)

    paths = sample_paths(VALIDATED_DIR)
    approved = 0
    rejected = 0
    edited = 0
    skipped = 0

    for path in paths:
        if limit and (approved + rejected + edited) >= limit:
            break

        sample_id = path.stem
        if sample_id in already:
            LOG.info("%s: already reviewed (%s), skipping", sample_id, already[sample_id])
            continue

        try:
            sample = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            LOG.warning("%s: load failed: %s", sample_id, e)
            continue

        _display_sample(sample)

        if auto:
            decision = auto
            print(f"(auto) Decision: {decision}")
        else:
            while True:
                decision = input("[a]pprove  [r]eject  [e]dit  [s]kip  [q]uit > ").strip().lower()
                if decision in {"a", "r", "e", "s", "q"}:
                    break
                print("Invalid choice.")

        if decision == "q":
            break

        if decision == "e":
            new_inst = input("New instruction > ").strip()
            if new_inst:
                sample["instruction"] = new_inst
            # After edit, treat as approved
            decision = "a"
            edited += 1

        if decision == "a":
            sample["metadata"]["reviewed"] = True
            out_path = REVIEWED_DIR / f"{sample_id}.json"
            write_json(out_path, sample)
            approved += 1
            print(f"  ✓ Approved -> {out_path}")
        elif decision == "r":
            rejected += 1
            print("  ✗ Rejected")
        elif decision == "s":
            skipped += 1
            print("  ⊘ Skipped")

        _log_decision(sample_id, decision)

    LOG.info("Review complete: %d approved, %d rejected, %d edited, %d skipped",
             approved, rejected, edited, skipped)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Human review of validated samples.")
    parser.add_argument("--limit", type=int, default=0, help="Max samples to review (0 = all).")
    parser.add_argument("--auto", choices=["a", "r", "s"], default=None,
                        help="Non-interactive mode for CI/demos.")
    args = parser.parse_args()
    try:
        return review(args.limit, args.auto)
    except Exception as e:
        LOG.exception("Review failed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())