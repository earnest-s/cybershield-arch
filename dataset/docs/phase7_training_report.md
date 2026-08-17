# Phase 7 Training Report — CyberShield Gemma SFT v1

**Date:** 2026-08-17
**Phase:** 7 — SFT artifact construction (data + training spec; **no training performed**)
**Environment:** `uv run python` (Python 3.12.x); Gemma 3 4B tokenizer offline/cached; transformers 5.14.1
**Pool decision (explicit):** the SFT pool is the **full Phase 6 subgraph set (51,498)**, approved in
preference to the pre-Phase-6 Phase 5 recommendation (≤30-node tier, 5,748) because Phase 6 delivered
hard-guardrail-aligned subgraphs for 100% of parents (every record ≤10 nodes / ≤15 edges).

---

## PHASE 7 STATUS: COMPLETE (data + specification + harness)

### What was done

1. Audited Phase 6 output (52 shards, 51,498 subgraphs, 0 skipped) and confirmed 1 subgraph per parent,
   42 domains, 8 styles, 6 clouds, 4 complexity tiers, complete provenance.
2. Audited the canonical contract (`backend/core/architecture_schema.py`), the runtime prompt
   (`backend/core/inference.py:generate_architecture`), the response path
   (`backend/core/response_builder.py`), the cached Gemma 3 model + tokenizer, and the stale
   `backend/training/gemma/lora_train.py`.
3. Built `dataset/scripts/format_sft.py` (deterministic; reruns byte-identical) → produced
   `dataset/training/CyberShield_Gemma_SFT_v1.jsonl` (51,498 records).
4. Built `dataset/scripts/verify_sft.py` (independent quality gate) → **12/12 gates PASS, exit 0**.
5. Replaced the stale training harness per the Phase 5 debt list (chat template, prompt masking,
   `max_length` 1024, eval split, seed) — harness only, **no training run**.
6. Wrote `dataset/docs/phase7_training_spec.md` and `dataset/docs/phase7_lineage.md`.

### Source lineage

HF `ajibawa-2023/Technical-Architectures-Large` (AI-generated; **not** "real-world architecture data")
→ Phase 1-4 pipeline → `CyberShield_Dataset_v1_FULL.jsonl` (51,498, immutable) → Phase 6
`sacce_connected_subgraph_v1` (1 subgraph per parent, verbatim node/edge content) → Phase 7 SFT records.
Every SFT record carries `metadata.phase6` (transformation method/version/contract, retention ratios,
selected node/edge ids) and `metadata.parent_source_id`/`parent_architecture_id`. Full chain:
`dataset/docs/phase7_lineage.md`.

### Candidate records

- 51,498 Phase 6 subgraphs were candidates; **0 excluded** (contract-aligned by construction).
- 365 records (0.71%) share an instruction with different targets (max reuse 3) — retained deliberately.
- 0 duplicate architectures, 0 fabricated nodes/edges, 0 missing provenance (Phase 6 verified; this
  phase re-verified per-record against the shards).

### Final SFT records

51,498 records in `dataset/training/CyberShield_Gemma_SFT_v1.jsonl` (200,254,229 bytes;
SHA256 `8c91e5cd017df9490f24b5c9f016f01c871e5531b4072c7f83d6959301b851ec`). Schema: `id`,
`instruction` (rendered runtime prompt), `response` (target JSON string), `architecture` (target
object), `metadata` (domain/style/cloud/complexity/source/provenance/security fingerprint/split).

### Filtering criteria

None applied beyond Phase 6's contract alignment (≤10 nodes, ≤15 edges, connected, anchor-aware
subgraph). No truncation anywhere; no record altered after Phase 6.

### Sequence-length statistics (measured on the real cached Gemma 3 4B tokenizer, full chat template, 100% of records)

| Measure | min | p50 | p90 | p95 | p99 | max |
|---|---|---|---|---|---|---|
| Prompt (user turn) | 203 | 215 | 225 | 227 | 231 | 237 |
| Target (model turn) | 44 | 234 | 264 | 276 | 302 | 388 |
| **Full sequence** | **249** | **450** | **481** | **492** | **519** | **605** |

0 records > 1,024 tokens → **`max_length = 1024` truncates nothing** (old default 384 truncated ~100%).
Model context 131,072; not a constraint.

### Train/validation/test split

| Split | Records | % | MEDIUM-risk % | Domains/Styles/Clouds/Complexity |
|---|---|---|---|---|
| train | 46,348 | 90.00 | 11.1 | 42 / 8 / 6 / 4 |
| validation | 2,575 | 5.00 | 11.8 | 42 / 8 / 6 / 4 |
| test | 2,575 | 5.00 | 10.6 | 42 / 8 / 6 / 4 |

Method: deterministic, **size-tier-stratified largest-deficit greedy** over node-id-set clusters
(49,975 clusters; 530 multi-record; max 62). Small-graph tiers (2–9 nodes: 1,426 records) are
distributed ~90/5/5 across splits by size (chunky near-dup clusters — e.g. a 53-record cluster —
cannot be subdivided without leaking; residual wobble at tiers 2–5 is reported: validation 72, test 72,
train 1,282). No random numbers; seed-independent by construction. Phase 5 reference totals
(46,348/2,575/2,575) reproduced exactly.

### Leakage analysis

- Node-id-set clusters never straddle splits: **0 straddles** (verified by re-clustering the artifact).
- One subgraph per parent ⇒ no parent-grouping leaks possible.
- Exact-duplicate architectures: 0 (Phase 6 verify; artifact re-verified byte-level against parents).
- 365 shared instructions are within-split only; no cross-split instruction duplication (verified by
  construction: cluster integrity + single instruction per record mapping).

### Security-target decision

**D1 (architecture-only target):** security JSON is computed deterministically by the runtime engine;
making it a target would duplicate a deterministic pipeline stage. **D2 (explanation deferred):** no
human-written explanations exist; `security_summary` is engine-derived and is not treated as ground
truth. Compact security fingerprint (`risk_level`, `security_score`) is carried in metadata for audit
and stratification only. Risk prior of the pool (88.8% HIGH / 11.1% MEDIUM / 0.07% LOW) reflects
security-recomputation on subgraphs and differs from the Phase 5 parent-corpus prior (98.75% HIGH).

### Training format

Single-turn Gemma 3 chat (`<bos><start_of_turn>user …<end_of_turn>\n<start_of_turn>model
{json}<end_of_turn><eos>`); prompt tokens masked (labels = -100); input byte-identical to the
deployment prompt (0 drift across all records, verified). Target = compact `{nodes, edges}` JSON in
the canonical vocabulary.

### Training specification

`dataset/docs/phase7_training_spec.md` — model `unsloth/gemma-3-4b-it-bnb-4bit` (NF4, cached),
LoRA r=16/α=32/dropout 0.05, target modules `q/k/v/o_proj + gate/up/down_proj`, batch 1 × grad-accum 8,
lr 2e-4 AdamW, warmup 10% + cosine, weight decay 0.01, epochs 2–3, `max_length` 1024, seed 42,
adapter to `checkpoints/gemma_lora/`. Established values marked repository-established; additions
marked recommendations with justification.

### Verification results

`dataset/scripts/verify_sft.py` (standalone; reads `inference.py` only to extract the live prompt
template for the drift check): **12/12 PASS, exit 0** — record count & ids; target contract (types,
labels, refs, self-loops, duplicate edges, hard limits); response/architecture fidelity; parent
architecture fidelity (against shards); prompt drift vs runtime template; provenance present; parents
in manifest; phase6 contract; exact split counts; cluster integrity; full-corpus tokenizer scan ≤ 1024
(max observed 605). Transformation determinism: reruns byte-identical (SHA256 stable).

### Files created/modified

| File | Action |
|---|---|
| `dataset/training/CyberShield_Gemma_SFT_v1.jsonl` | created (51,498 records) |
| `dataset/scripts/format_sft.py` | created |
| `dataset/scripts/verify_sft.py` | created |
| `dataset/docs/phase7_training_spec.md` | created |
| `dataset/docs/phase7_lineage.md` | created |
| `dataset/docs/phase7_training_report.md` | created (this file) |
| `backend/training/gemma/lora_train.py` | updated (chat template + masking + eval split + max_length 1024 + seed; CLI surface preserved) |

### Immutable artifacts verified

| Artifact | SHA256 | Status |
|---|---|---|
| `dataset/final/CyberShield_Dataset_v1_FULL.jsonl` | `e3ee9810e13ba660f6f39b93f35e318aa26f22eccf5b7ea59c57ef05f5a1b36b` | unchanged (recomputed this phase) |
| 52 Phase 6 shards | per manifest `shard_sha256` | 52/52 match (not regenerated) |
| SFT artifact | `8c91e5cd017df9490f24b5c9f016f01c871e5531b4072c7f83d6959301b851ec` | new, deterministic |

### Known limitations

1. **Size saturation:** 97.2% of targets have exactly 10 nodes (extractor fills to the hard cap);
   60.8% have exactly 9 edges. The model will predominantly emit ~10-node graphs. Diversity is in
   composition (42 domains × 8 styles × 6 clouds), not size.
2. **Prompt soft-target mismatch:** the runtime prompt states "Max nodes: 8 / Max edges: 10"; 97.2% of
   targets hit 10 nodes. Both are runtime-legal (hard guardrail 10/15); retained for deployment
   fidelity; may induce retries for >8-node outputs.
3. **Risk prior:** 88.8% HIGH — strongly imbalanced; split stratification keeps each split near the
   overall prior (11.1 / 11.8 / 10.6 MEDIUM%).
4. **Template grammar:** instructions are source-derived with documented imperfections
   ("Design a E-Commerce architecture."); content is genuine, style is template-constructed and kept
   verbatim.
5. **Security summary not human supervision:** engine-derived; not a target (D1).
6. **Source is AI-generated** HF data; never described as real-world.
7. **Stale comment debt:** `backend/core/inference.py:generate_explanation` still references the old
   training prompt format; runtime behaviour is unaffected, doc comment should be refreshed during the
   training milestone.

### What remains for Phase 8

- Training execution requires **explicit separate approval**; harness and spec are ready
  (`uv run python backend/training/gemma/lora_train.py`).
- Post-training evaluation per `training_plan.md` §9 (structural validity, size compliance,
  security-score delta, missing-control recall, risk distribution, determinism, latency/VRAM).
- Optional: stratified re-split by risk within clusters if downstream evaluation requires it.
- Optional: explanation SFT after real explanations exist (D2).
- Refresh the stale `generate_explanation` comment; document adapter deployment path.
