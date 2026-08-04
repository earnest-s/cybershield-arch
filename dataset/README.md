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
final/        CyberShield_Dataset_v1.jsonl (training-ready)
```

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

## Validation gates

- Structural: JSON Schema (`schemas/architecture_schema.json`), node/edge
  vocabulary enforced by the pipeline constants.
- Semantic: duplicate ids/architectures, disconnected graphs, dangling node
  references, unsupported node types, empty threats/recommendations.
- Human: approve / reject / needs-edit in `review_dataset.py`.

## Alignment

Node types (`ui, service, database, cache, queue, container`) and edge labels
(`HTTP, DB Query, Async, Cache`) match `backend/core/inference.py`; security
labels are computed by `backend/security/*` — the same engine the production
/explain endpoint uses, so training labels equal runtime behaviour.

## Related tooling

An earlier template-based generator lives in `backend/dataset/` (outputs in
`generated/`, `templates/`, `prompts/`); its artifacts feed the same
validated/reviewed/final stages.