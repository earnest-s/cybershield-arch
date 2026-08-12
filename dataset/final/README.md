# Final

Consolidated, reviewed dataset exported to training-ready JSONL via
`dataset/scripts/export_jsonl.py` with an explicit `--output` path.

Artifacts in this folder:

| File | Records | Origin |
|---|---|---|
| `CyberShield_Dataset_Pilot_v1.jsonl` | 152 | HF rows 0-499 (Pilot v1) |
| `CyberShield_Dataset_Pilot_v2.jsonl` | 617 | HF rows 500-2499 (Pilot v2) |
| `CyberShield_Dataset_v1_FULL.jsonl` | full-scale | HF rows 0-293639 (see `docs/full_scale_report.md`) |
| `CyberShield_Dataset_v1.jsonl` | 1 | legacy production artifact (kept for compatibility) |

Pilot and production files are never overwritten by pipeline runs; new exports
use versioned filenames (`--output`). This folder (plus the dataset splits) is
the source for LoRA fine-tuning. Bulk exports (`*_FULL.jsonl`) are git-ignored
and rebuildable via `dataset/scripts/export_jsonl.py`.
