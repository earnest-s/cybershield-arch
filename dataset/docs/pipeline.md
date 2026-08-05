# CyberShield Dataset Pipeline

End-to-end pipeline to convert the HuggingFace dataset
`ajibawa-2023/Technical-Architectures-Large` (293,640 enterprise Mermaid diagrams)
into `CyberShield_Dataset_v1.jsonl` — a training-ready corpus for Gemma 3 LoRA
fine-tuning.

## Folder Structure

```
dataset/
├── raw/           # JSONL snapshot of the HF dataset (293k samples)
├── parsed/        # Mermaid -> CyberShield architecture JSON
├── enriched/      # + security engine analysis
├── validated/     # passed automated gates
├── reviewed/      # human-approved samples
├── final/         # CyberShield_Dataset_v1.jsonl
├── schemas/       # architecture_schema.json (app vocabulary)
├── scripts/       # pipeline scripts (see below)
├── docs/          # statistics, pipeline.md, charts
└── logs/          # per-script logs + review audit trail
```

## Pipeline Scripts (run in order)

| Stage | Script | Input | Output | Description |
|-------|--------|-------|--------|-------------|
| 1 | `download_dataset.py` | HF Hub | `raw/samples.jsonl` + `dataset_info.json` | Streams HF dataset, snapshots as JSONL (resumable) |
| 2 | `inspect_dataset.py` | `raw/` | `docs/dataset_statistics.md` + charts | Domain/style/cloud/complexity stats, node/edge histograms |
| 3 | `convert_dataset.py` | `raw/` | `parsed/` | Mermaid -> architecture JSON (app node/edge contract) |
| 4 | `enrich_dataset.py` | `parsed/` | `enriched/` | Security engine: controls, threats, score, risk, attack surface |
| 5 | `validate_dataset.py` | `enriched/` | `validated/` | Schema, graph integrity, duplicate detection, security completeness |
| 6 | `review_dataset.py` | `validated/` | `reviewed/` | Human approve/reject/edit; audit log |
| 7 | `export_jsonl.py` | `reviewed/` | `final/CyberShield_Dataset_v1.jsonl` | Training-ready JSONL with full record shape |

All scripts are **idempotent** and **resumable**: existing outputs are skipped unless `--force` is passed.

## Running the Pipeline

```bash
# Quick test (10 samples each stage)
python -m dataset.scripts.download_dataset --limit 10
python -m dataset.scripts.inspect_dataset --limit 10
python -m dataset.scripts.convert_dataset --limit 10
python -m dataset.scripts.enrich_dataset --limit 10
python -m dataset.scripts.validate_dataset --limit 10
python -m dataset.scripts.review_dataset --limit 10 --auto a
python -m dataset.scripts.export_jsonl --limit 10

# Full production run (293k samples)
python -m dataset.scripts.download_dataset
python -m dataset.scripts.inspect_dataset
python -m dataset.scripts.convert_dataset
python -m dataset.scripts.enrich_dataset
python -m dataset.scripts.validate_dataset
python -m dataset.scripts.review_dataset
python -m dataset.scripts.export_jsonl
```

## Resume & Recovery

- Every stage writes incrementally; interrupt with Ctrl+C and re-run to resume.
- `--force` overwrites existing outputs for that stage.
- Logs are written to `dataset/logs/<script>.log`.

## Data Alignment with the Application

The pipeline emits architecture JSON that **exactly matches** the runtime contract:

- **Node types**: `ui, service, database, cache, queue, container` (from `backend/core/inference.py:_ALLOWED_NODE_TYPES`)
- **Edge labels**: `HTTP, DB Query, Async, Cache` (from `backend/core/inference.py:_LABEL_ALIASES`)
- **Security fields**: computed by `backend/security/*` (same engine as `/explain` endpoint)
  - `required_controls`, `missing_controls`, `threats`, `recommendations`
  - `risk_level` (LOW/MEDIUM/HIGH), `security_score` (0-100)
  - `attack_surface`, `security_summary`

Training labels are **identical** to production labels — no drift.

## Output Record Shape (`final/CyberShield_Dataset_v1.jsonl`)

Each line is a complete training record:

```json
{
  "id": "CSA-000001",
  "instruction": "Design a ...",
  "architecture": {
    "nodes": [{"id": "WebUI", "type": "ui"}, ...],
    "edges": [{"source": "WebUI", "target": "API_GW", "label": "HTTP"}, ...]
  },
  "security": {
    "required_controls": [...],
    "missing_controls": [...],
    "threats": [...],
    "recommendations": [...],
    "risk_level": "MEDIUM",
    "security_score": 65,
    "attack_surface": {...},
    "security_summary": "..."
  },
  "metadata": {
    "domain": "MLOps",
    "style": "Event-Driven",
    "cloud": "On-Premises",
    "complexity": "Enterprise",
    "source": "Technical-Architectures-Large",
    "reviewed": true,
    "version": "1.0"
  }
}
```

## Security Enrichment Details

The enrichment step uses **only** the production security engine (no logic duplication):

| Engine Module | Function | Output |
|---------------|----------|--------|
| `security_analyzer.analyze_architecture_security` | Rule-based missing control detection | `missing_controls`, `recommendations`, `risk_level`, `security_score`, `security_summary` |
| `threat_detector.detect_threats` | Threat mapping from missing controls | `threats`, `node_threats`, `edge_threats` |
| `threat_detector.calculate_attack_surface` | Exposed endpoints, DBs, services | `attack_surface` |
| `security_catalog.SECURITY_CATALOG` | 12 controls with risk levels | `required_controls` (present ∪ missing) |

## Validation Gates

A sample is **validated** iff:

1. **Schema**: all required fields present, enums respected.
2. **Graph integrity**: unique node IDs, edges reference existing nodes, no self-loops, no duplicate edges, weakly connected.
3. **Vocabulary**: node types and edge labels are from the allowed sets.
3. **Security completeness**: `threats` and `recommendations` are non-empty.
4. **Deduplication**: no duplicate sample IDs, no duplicate architecture topologies (canonical serialization).

## Review Workflow

Interactive CLI (or `--auto a|r|s` for CI):

```
[ID] | Domain | Style | Cloud | Complexity
INSTRUCTION: ...
ARCHITECTURE: nodes + edges
SECURITY: score, risk, missing, threats, recommendations
[a]pprove  [r]eject  [e]dit  [s]kip  [q]uit >
```

- **Approve**: writes to `reviewed/` with `metadata.reviewed=true`.
- **Reject**: skips, logged.
- **Edit**: inline instruction edit, then auto-approves.
- **Skip**: leaves in `validated/` for later.

Decisions logged to `dataset/logs/review_decisions.jsonl` (append-only, auditable).

## Export Format

`export_jsonl.py` reads `reviewed/`, deduplicates by ID, writes one JSON object per line to `final/CyberShield_Dataset_v1.jsonl`. Each record carries the exact fields listed above — ready for `transformers` `SFTTrainer` with Gemma 3's single-turn chat template.

## Future: Gemma 3 LoRA Fine-Tuning

1. `CyberShield_Dataset_v1.jsonl` → `SFTTrainer` with `instruction`/`response` (architecture JSON).
2. Prompt mask: only compute loss on `response` tokens (Gemma 3 single-turn chat template: `<bos><start_of_turn>user\n{instruction}<end_of_turn>\n<start_of_turn>model\n{response}<end_of_turn><eos>`).
3. LoRA: r=16, alpha=32, NF4 quant, target modules `q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj`.
4. Validation: structural validity, security-score delta, missing-control recall.

## Reproducibility

- Every script logs to `dataset/logs/`.
- `review_decisions.jsonl` provides an immutable audit trail.
- `dataset/docs/dataset_statistics.md` captures source statistics.
- `final/split_manifest.json` (if generated with `--split-ratio`) records train/val split.

## Extending the Pipeline

- Add new HF datasets: modify `download_dataset.py` HF_DATASET constant.
- New diagram types: extend `mermaid_parser.py` with new handlers.
- New security rules: they live in `backend/security/*` — enrichment picks them up automatically.
- Custom validation: add checks in `validate_dataset.py` without touching other stages.