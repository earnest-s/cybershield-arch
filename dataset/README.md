# Dataset

Cybersecurity architecture dataset for Gemma 3 fine-tuning, derived from
`ajibawa-2023/Technical-Architectures-Large` (293,640 enterprise Mermaid
diagrams) and enriched with the production security engine.

## Pipeline

```
raw/          downloaded source samples (JSONL snapshot of the HF dataset)
parsed/       Mermaid -> architecture JSON (app node/edge contract)
enriched/     + security engine analysis (controls, threats, score, risk)
validated/    passed automated validation gates
reviewed/     approved by a human reviewer
final/        training-ready JSONL exports (pilots + full-scale)
```

Staging directories (`parsed/`, `enriched/`, `validated/`, `reviewed/`),
raw snapshots, and `final/CyberShield_Dataset_*_FULL.jsonl` are **git-ignored**:
they are bulk, regenerable artifacts. The pipeline stages and reports are the
versioned record; rebuild any stage with the commands below.

## Run order

```bash
python -m dataset.scripts.download_dataset   # or: python dataset/scripts/download_dataset.py
python -m dataset.scripts.inspect_dataset
python -m dataset.scripts.convert_dataset
python -m dataset.scripts.enrich_dataset
python -m dataset.scripts.validate_dataset
python -m dataset.scripts.review_dataset
python -m dataset.scripts.export_jsonl
```

Every stage is resumable (existing ids are skipped) and logs to `logs/`.
Details: `docs/pipeline.md`.

Subsets: `--limit N` bounds work per stage; `download_dataset.py` also accepts
`--offset N` to stream a later slice of the source (e.g. rows 500-2499).

## Validation gates (FROZEN policy)

- Structural: JSON Schema (`schemas/architecture_schema.json`), node/edge
  vocabulary enforced by the pipeline constants.
- Semantic: duplicate ids/architectures, dangling node references, unsupported
  node types, empty threats/recommendations, and **component-level
  connectivity**: multiple connected components are allowed, completely
  isolated nodes are rejected (canonical `has_orphan_node` from
  `backend/core/architecture_validator.py`).
- Human: approve / reject / needs-edit in `review_dataset.py` (CI mode:
  `review_dataset.py --auto a`).

Policy history: `docs/validation_policy_analysis.md` (root cause and decision),
`docs/pilot_report.md` (Pilot v1), `docs/pilot_report_v2.md` (Pilot v2).

## Outputs

- `final/CyberShield_Dataset_Pilot_v1.jsonl` — 152 records (rows 0-499)
- `final/CyberShield_Dataset_Pilot_v2.jsonl` — 617 records (rows 500-2499)
- `final/CyberShield_Dataset_v1_FULL.jsonl` — full-scale output
  (see `docs/full_scale_report.md`)
- `final/CyberShield_Dataset_v1.jsonl` — legacy production artifact (1 record)

Pilot artifacts are preserved by every run; the full-scale export uses a new
versioned filename and never overwrites pilots or the production file.

## Alignment

Node types (`ui, service, database, cache, queue, container`) and edge labels
(`HTTP, DB Query, Async, Cache`) match `backend/core/inference.py`; security
labels are computed by `backend/security/*` — the same engine the production
/explain endpoint uses, so training labels equal runtime behaviour.

## Related tooling

The legacy template-based generator (`backend/dataset/`, `dataset/templates/`,
`dataset/prompts/`, `dataset/generated/`) has been removed. All records in
validated/reviewed/final originate from the HuggingFace pipeline in
`dataset/scripts/`. No synthetic, mock, or template records are produced.