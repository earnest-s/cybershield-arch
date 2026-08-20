# Raw

Seed material: JSONL snapshot of `ajibawa-2023/Technical-Architectures-Large` (293,640 enterprise Mermaid diagrams) downloaded from HuggingFace Hub.

Files:
- `samples.jsonl` — streamed JSONL snapshot (one record per line)
- `dataset_info.json` — HF dataset builder metadata (features, splits, description)

This folder is the single source of truth for the raw dataset. Nothing here is automatically trusted; all samples pass through the canonical pipeline (convert → enrich → validate → review → export).