# Dataset

Cybersecurity architecture dataset for LoRA fine-tuning of Gemma 3.

This directory is the canonical data engineering workspace for the
CyberShield-Arch fine-tuning milestone. It follows a staged pipeline in which
samples only move forward after automated and human quality gates.

## Pipeline

```
raw/        ->  generated/   ->  validated/   ->  reviewed/   ->  final/
(seed       (generator       (schema +        (human          (training-ready
 inputs)     output)          semantic checks) approval)        JSONL export)
```

1. `raw/` - seed instructions, requirements, and reference material used to
   drive generation.
2. `generated/` - candidate samples produced by `backend/dataset/dataset_generator.py`.
3. `validated/` - samples that passed `backend/dataset/dataset_validator.py`.
4. `reviewed/` - samples approved by `backend/dataset/review_dataset.py`.
5. `final/` - consolidated dataset in training-ready JSONL format.

## Validation gates

- Structural: JSON Schema compliance (`schemas/architecture_schema.json`).
- Semantic: duplicate ids/architectures, valid nodes/edges, control
  consistency with the security engine, known threat names.
- Human: interactive approve / reject / needs-edit review.

## Tooling

| Stage | Tool |
| --- | --- |
| Generation | `backend/dataset/dataset_generator.py` |
| Validation | `backend/dataset/dataset_validator.py` |
| Review | `backend/dataset/review_dataset.py` |
| Export | `backend/dataset/export_jsonl.py` |

Design rationale and provenance documentation live in `docs/` and in
`docs/dataset_design.md` at the repository root.