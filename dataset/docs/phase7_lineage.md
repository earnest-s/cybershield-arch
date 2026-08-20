# Phase 7 Data Lineage — CyberShield Gemma SFT v1

Every record in `dataset/training/CyberShield_Gemma_SFT_v1.jsonl` traces to a
real source row. This document records the chain; **no record is project
fabricated**.

## Chain

```
ajibawa-2023/Technical-Architectures-Large (HuggingFace, train split, 293,640 rows)
  (AI-generated source dataset — NOT real-world architecture data)
  |
  | Phase 1-4 pipeline (parsed 285,561 -> enriched 284,686 -> validated 51,498)
  v
dataset/final/CyberShield_Dataset_v1_FULL.jsonl        (immutable, 51,498 records)
  |
  | Phase 6: extract_subgraphs.py v1.0.0  (sacce_connected_subgraph_v1)
  v
dataset/training/subgraphs/subgraphs_r0000..r0051.jsonl (51,498 subgraphs, 1 per parent)
  |
  | Phase 7: format_sft.py (this phase)
  v
dataset/training/CyberShield_Gemma_SFT_v1.jsonl         (51,498 SFT records, THIS ARTIFACT)
```

## Provenance fields carried into each SFT record (`metadata`)

| Field | Meaning |
|---|---|
| `source` | Fixed string naming the HF source and the pipeline stages |
| `parent_source_id` | `CSA-<HF row>` of the source record in `v1_FULL` |
| `parent_architecture_id` | Architecture id of the parent (same id value) |
| `phase6.transformation_method` | `sacce_connected_subgraph_v1` |
| `phase6.transformation_version` | `1.0.0` |
| `phase6.contract` | `{"HARD_NODE_LIMIT": 10, "HARD_EDGE_LIMIT": 15}` (canonical) |
| `phase6.node_retention_ratio` / `edge_retention_ratio` | Fraction of parent retained |
| `phase6.selected_node_ids` / `selected_edge_ids` | Exact node/edge ids drawn from the parent |
| `domain`, `style`, `cloud`, `complexity` | Parent classification (source metadata) |
| `security.risk_level`, `security.security_score` | Compact fingerprint, engine-computed on the SUBGRAPH (not the parent) |

## Transformation guarantees (verified, not asserted)

- Every node id and edge in a target appears verbatim in the parent record
  (Phase 6 guarantee; `verify_sft.py` additionally byte-compares the SFT
  target against the parent's subgraph architecture: 0 mismatches).
- Every SFT instruction is byte-identical to the runtime prompt in
  `backend/core/inference.py` rendered with the parent's instruction:
  0 drift across all 51,498 records.
- `instruction` text originates from genuine source metadata fields
  (domain/style/cloud/constraints); template grammar imperfections are
  documented, not altered.
- Security content is NOT a training target (engine-computed at runtime).
- No record deleted, truncated, or augmented; 365 instruction reuses (0.71%)
  are retained because the prompt→target mapping stays truthful.

## Identity & integrity (Step 11 verification)

| Artifact | SHA256 |
|---|---|
| Source corpus `dataset/final/CyberShield_Dataset_v1_FULL.jsonl` | `e3ee9810e13ba660f6f39b93f35e318aa26f22eccf5b7ea59c57ef05f5a1b36b` (verified unchanged this phase) |
| Subgraph shards (52) | Per-shard SHA256 in `dataset/training/subgraphs/manifest.json` (Phase 6, re-verified by `verify_sft.py` parent lookups) |
| `dataset/training/CyberShield_Gemma_SFT_v1.jsonl` | `8c91e5cd017df9490f24b5c9f016f01c871e5531b4072c7f83d6959301b851ec` |
| `format_sft.py` | see `git log` (versioned) |
| `verify_sft.py` | see `git log` (versioned) |

The corpus hash was computed before and after this phase and is unchanged;
Phase 6 shards and manifest were not regenerated during this phase.