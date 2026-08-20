# CyberShield-Arch Dataset Manifest

**Version:** 1.0
**Pipeline:** `download → inspect → convert → enrich → validate → review → export`
**Canonical Export:** `dataset/final/CyberShield_Dataset_v1.jsonl`
**Source Dataset:** `ajibawa-2023/Technical-Architectures-Large` (293,640 samples)

---

## Folder Structure

```
dataset/
├── raw/                # HF dataset snapshot (JSONL)
│   ├── samples.jsonl
│   └── dataset_info.json
├── parsed/             # Mermaid → architecture JSON (CSA-######.json)
├── enriched/           # + security engine analysis (CSA-######.json)
├── validated/          # Passed automated validation gates (CSA-######.json)
├── reviewed/           # Human-approved samples (CSA-######.json)
├── final/              # CyberShield_Dataset_v1.jsonl (training-ready)
├── schemas/            # architecture_schema.json (canonical schema)
├── scripts/            # Pipeline scripts (8 scripts, see below)
├── docs/               # Statistics, pipeline.md, charts/
│   ├── dataset_statistics.md
│   ├── pipeline.md
│   └── charts/
└── logs/               # Per-script logs + review_decisions.jsonl
```

---

## Pipeline Stages

| Stage | Script | Input | Output | Description |
|-------|--------|-------|--------|-------------|
| 1 | `download_dataset.py` | HF Hub | `raw/samples.jsonl`, `raw/dataset_info.json` | Streams HF dataset, snapshots as JSONL (resumable) |
| 2 | `inspect_dataset.py` | `raw/` | `docs/dataset_statistics.md` + `docs/charts/*.png` | Domain/style/cloud/complexity stats, node/edge histograms |
| 3 | `convert_dataset.py` | `raw/` | `parsed/` | Mermaid → architecture JSON (app node/edge contract) |
| 4 | `enrich_dataset.py` | `parsed/` | `enriched/` | Security engine: controls, threats, score, risk, attack surface |
| 5 | `validate_dataset.py` | `enriched/` | `validated/` | Schema, graph integrity, duplicate detection, security completeness |
| 6 | `review_dataset.py` | `validated/` | `reviewed/` | Human approve/reject/edit; audit log |
| 7 | `export_jsonl.py` | `reviewed/` | `final/CyberShield_Dataset_v1.jsonl` | Training-ready JSONL with full record shape |

All scripts are **idempotent** and **resumable**: existing outputs are skipped unless `--force` is passed.

---

## Expected Inputs

- **Stage 1:** Internet access to HuggingFace Hub (`ajibawa-2023/Technical-Architectures-Large`)
- **Stage 2:** `raw/samples.jsonl` (from Stage 1)
- **Stage 3:** `raw/samples.jsonl` (from Stage 1)
- **Stage 4:** `parsed/CSA-######.json` (from Stage 3)
- **Stage 5:** `enriched/CSA-######.json` (from Stage 4)
- **Stage 6:** `validated/CSA-######.json` (from Stage 5)
- **Stage 7:** `reviewed/CSA-######.json` (from Stage 6)

---

## Expected Outputs

- **Stage 1:** `raw/samples.jsonl` (293,640 lines), `raw/dataset_info.json`
- **Stage 2:** `docs/dataset_statistics.md`, `docs/charts/{domains,styles,clouds,complexities,diagram_types,node_counts,edge_counts}.png`
- **Stage 3:** `parsed/CSA-######.json` (one per successfully parsed sample)
- **Stage 4:** `enriched/CSA-######.json` (one per successfully enriched sample)
- **Stage 5:** `validated/CSA-######.json` (subset passing all gates)
- **Stage 6:** `reviewed/CSA-######.json` (subset approved by human)
- **Stage 7:** `final/CyberShield_Dataset_v1.jsonl` (one JSON object per line)

---

## Canonical Record Schema (`CyberShield_Dataset_v1.jsonl`)

Each line is a complete training record:

```json
{
  "id": "CSA-000001",
  "instruction": "Design a Media architecture using a CQRS style deployed on Multi-Cloud satisfying: Strict Network Segmentation, Rate Limiting, AI/ML Inference Integration, Zero Trust Architecture, Data Lakehouse Pattern.",
  "architecture": {
    "nodes": [
      {"id": "WebUI", "type": "ui"},
      {"id": "API_GW", "type": "service"},
      {"id": "Postgres", "type": "database"}
    ],
    "edges": [
      {"source": "WebUI", "target": "API_GW", "label": "HTTP"},
      {"source": "API_GW", "target": "Postgres", "label": "DB Query"}
    ]
  },
  "security": {
    "required_controls": ["Authentication", "RBAC", "API Gateway", "Audit Logging", "Monitoring", "Secrets Manager", "SIEM", "WAF", "IDS", "IPS", "Encryption Service", "MFA"],
    "missing_controls": ["Encryption Service", "Monitoring", "API Gateway", "Audit Logging", "Authentication", "RBAC", "SIEM", "IDS", "IPS"],
    "threats": [
      {"name": "Data Leakage", "severity": "CRITICAL", "description": "Sensitive data is exposed in transit or at rest.", "missing_control": "Encryption Service"},
      {"name": "Unauthorized Access", "severity": "CRITICAL", "description": "Attackers can access systems or data without proper identity verification.", "missing_control": "Authentication"}
    ],
    "recommendations": [
      "Encrypt sensitive data at rest and in transit.",
      "Add Authentication service to protect user access."
    ],
    "risk_level": "HIGH",
    "security_score": 10,
    "attack_surface": {"attack_surface_score": 100, "public_endpoints": 3, "databases": 4, "services": 28},
    "security_summary": "Architecture contains a frontend, an API service and a database but lacks Encryption Service, Monitoring, API Gateway, Audit Logging, Authentication, RBAC, SIEM, IDS and IPS. Overall security posture is HIGH RISK and requires immediate remediation."
  },
  "metadata": {
    "domain": "Media",
    "style": "CQRS",
    "cloud": "Multi-Cloud",
    "complexity": "Small",
    "source": "Technical-Architectures-Large",
    "reviewed": true,
    "version": "1.0"
  }
}
```

**Required fields:**
- `id` (CSA-######)
- `instruction` (string)
- `architecture` (nodes[], edges[])
- `security` (required_controls, missing_controls, threats[], recommendations[], risk_level, security_score, attack_surface, security_summary)
- `metadata` (domain, style, cloud, complexity, source, reviewed, version)

---

## Version

**1.0** — Initial canonical schema aligned with:
- `backend/core/inference.py` node types & edge labels
- `backend/security/*` security engine output
- `backend/core/response_builder.py` response shape

---

## Current Dataset Statistics (Test Run: 5 samples)

| Stage | Input | Output | Pass Rate |
|-------|-------|--------|-----------|
| Download | HF Hub | 5 samples | 100% |
| Inspect | 5 samples | stats + charts | 100% |
| Convert | 5 samples | 5 parsed | 100% |
| Enrich | 5 samples | 5 enriched | 100% |
| Validate | 5 samples | 1 validated | 20% |
| Review | 1 sample | 1 reviewed | 100% |
| Export | 1 sample | 1 record | 100% |

**Validation rejection reasons (4/5):**
- Disconnected graphs (3)
- Invalid node types / edge references (1)

**Final export:** `CyberShield_Dataset_v1.jsonl` — 1 record (CSA-000004)

---

## Validation Statistics

Automated gates (from `validate_dataset.py`):
1. **Schema**: All required fields present, enums respected
2. **Graph integrity**: Unique node IDs, edges reference existing nodes, no self-loops, no duplicate edges, weakly connected
3. **Vocabulary**: Node types ∈ {ui, service, database, cache, queue, container}; Edge labels ∈ {HTTP, DB Query, Async, Cache}
4. **Security completeness**: `threats` and `recommendations` non-empty
5. **Deduplication**: No duplicate sample IDs, no duplicate architecture topologies (canonical serialization)

Human review gate (from `review_dataset.py`):
- Interactive CLI: [a]pprove / [r]eject / [e]dit / [s]kip / [q]uit
- `--auto a|r|s` for CI
- Decisions logged to `logs/review_decisions.jsonl` (append-only)

---

## Known Limitations

1. **Mermaid parser coverage**: Only flowchart diagrams (LR/TB/RL/BT) are supported. Sequence diagrams, class diagrams, etc. are rejected at convert stage.
2. **Node/edge limits**: Parser enforces max 50 nodes / 100 edges per sample (schema limits). Very large diagrams may be truncated.
3. **Validation pass rate**: Current test run shows ~20% pass rate due to disconnected graphs in source data. Full 293k run may yield different rate.
4. **Security engine assumptions**: `build_security_dict` infers required controls from node/edge patterns. Edge cases may produce false positives/negatives.
5. **No train/val split**: `export_jsonl.py` does not split; downstream training code handles splitting.
6. **No difficulty field**: Source dataset uses `target_complexity` (Small/Medium/Enterprise) rather than easy/medium/hard.

---

## Future Dataset Workflow

### Production Run (293k samples)

```bash
# 1. Download full dataset (resumable)
python -m dataset.scripts.download_dataset

# 2. Generate statistics
python -m dataset.scripts.inspect_dataset

# 3. Convert Mermaid → architecture JSON
python -m dataset.scripts.convert_dataset

# 4. Enrich with security analysis
python -m dataset.scripts.enrich_dataset

# 5. Validate all gates
python -m dataset.scripts.validate_dataset

# 6. Human review (interactive or --auto)
python -m dataset.scripts.review_dataset

# 7. Export training-ready JSONL
python -m dataset.scripts.export_jsonl
```

### Extending the Pipeline

- **New HF datasets**: Modify `HF_DATASET` constant in `download_dataset.py`
- **New diagram types**: Extend `mermaid_parser.py` with new handlers
- **New security rules**: They live in `backend/security/*` — enrichment picks them up automatically
- **Custom validation**: Add checks in `validate_dataset.py` without touching other stages

### Reproducibility

- Every script logs to `dataset/logs/`
- `review_decisions.jsonl` provides immutable audit trail
- `docs/dataset_statistics.md` captures source statistics
- Pipeline is fully deterministic given same HF dataset snapshot

---

## Files Modified in Phase 3

- `dataset/schemas/architecture_schema.json` — Updated to match actual pipeline output
- `dataset/raw/README.md` — Removed legacy generator references
- `dataset/logs/README.md` — Documented expected log files
- `dataset/docs/dataset_manifest.md` — **Created** (this file)
- `dataset/logs/*.log` — Cleaned obsolete temporary logs

---

## Files Removed in Phase 3

- `dataset/logs/c.log`, `cv.log`, `cv2.log`, `cv3.log`, `cv4.log`, `e.log`, `en.log`, `r.log`, `v.log`, `va.log`, `x.log`, `z.log`, `z2.log` — Temporary test logs
- `dataset/scripts/__pycache__/` — Python bytecode cache

---

## Confirmation

✅ **Canonical pipeline verified**: Single pipeline `download → inspect → convert → enrich → validate → review → export`  
✅ **Canonical export verified**: Only `CyberShield_Dataset_v1.jsonl` in `final/`  
✅ **Schema alignment verified**: `architecture_schema.json` now matches pipeline output  
✅ **No duplicate pipelines**: Only one set of scripts in `dataset/scripts/`  
✅ **No legacy references**: All documentation updated to reflect current HF-based pipeline  
✅ **Repository ready for Phase 4**: Generate CyberShield Dataset