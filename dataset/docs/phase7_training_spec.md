# Phase 7 Training Specification — CyberShield Gemma SFT v1

**Status:** SPECIFICATION ONLY. No training is performed in this phase; this
document specifies how `dataset/training/CyberShield_Gemma_SFT_v1.jsonl` is
consumed by the training harness (`backend/training/gemma/lora_train.py`).
Values are labelled **repository-established** (already fixed by the project's
docs/code: `docs/training_plan.md`, `backend/core/inference.py`) or
**recommendation** (Phase 7 decision, justified below).

---

## 1. Task definition

Single-task supervised fine-tuning:

- **Input (user turn):** the production generation prompt from
  `backend/core/inference.py:generate_architecture`, rendered with the
  record's instruction substituted for the system description. The prompt is
  byte-identical to what the deployed runtime sends to the base model
  (verified per-record by `dataset/scripts/verify_sft.py`).
- **Output (model turn, loss-masked):** the canonical architecture graph as
  compact JSON — `{"nodes": [...], "edges": [...]}` — using only the
  canonical vocabulary (node types `ui, service, database, cache, queue,
  container`; edge labels `HTTP, DB Query, Async, Cache`).

**Decision D1 (target scope, architecture-only):** the target is architecture
JSON ONLY. Security JSON (`required_controls`, `missing_controls`, `threats`,
`recommendations`, `risk_level`, `security_score`, `attack_surface`,
`security_summary`) is computed deterministically by the production security
engine at inference time (`backend/core/response_builder.py`). Making it a
training target would teach the model to duplicate a deterministic pipeline
stage, creating a second, divergent source of truth. Established in Phase 5
(`dataset/docs/training_readiness_report.md`, STEP 3) and unchanged here.

**Decision D2 (explanation objective, deferred):** the corpus contains no
human-written explanations; `security.security_summary` is engine-derived
text. Explanation SFT is deferred until real explanations exist. The stale
explanation template in `lora_train.py` (pre-Phase-7) and the comment in
`backend/core/inference.py:generate_explanation` referencing the old training
format are known doc debt, tracked in the Phase 7 report.

## 2. Chat template

Gemma 3 uses a single-turn chat template with no system role
(`chat_template.jinja` in the cached model). Every record is formatted as:

```
<bos><start_of_turn>user
{prompt}<end_of_turn>
<start_of_turn>model
{response}<end_of_turn><eos>
```

- `{prompt}` = `instruction` field of the record (already rendered at
  dataset build time).
- `{response}` = `response` field (compact architecture JSON string).
- Applied at tokenization time with `tokenizer.apply_chat_template`.

## 3. Prompt masking (labels)

`labels` must be `-100` for every prompt token; only the model-turn tokens
(the architecture JSON) contribute to the loss. This is **required**: the
pre-Phase-7 `lora_train.py` trained on the full sequence including the prompt,
which is the documented defect this specification fixes.

## 4. Sequence length

**Recommendation: `max_length = 1024`.** Measured over all 51,498 records with
the real cached Gemma 3 4B tokenizer, full chat template applied:

| Measure | min | p50 | p90 | p95 | p99 | max |
|---|---|---|---|---|---|---|
| Prompt (user turn) | 203 | 215 | 225 | 227 | 231 | 237 |
| Target (model turn) | 44 | 234 | 264 | 276 | 302 | 388 |
| **Full sequence** | **249** | **450** | **481** | **492** | **519** | **605** |

Zero records exceed 1,024 tokens; `max_length = 1024` truncates nothing. The
pre-Phase-7 default of 384 truncates ~100% of records. Model context
(131,072 tokens) is not a constraint. Recommended maximum new tokens at
inference: 512 (unchanged from `inference.py`).

## 5. Dataset

- **Artifact:** `dataset/training/CyberShield_Gemma_SFT_v1.jsonl`
  (51,498 records, SHA256 `8c91e5cd017df9490f24b5c9f016f01c871e5531b4072c7f83d6959301b851ec`).
- **Schema per record:** `id` (SFT-000001..), `instruction` (rendered prompt),
  `response` (target JSON string), `architecture` (target object), `metadata`
  (domain, style, cloud, complexity, source, parent ids, phase6 provenance,
  compact security fingerprint, split).
- **Splits (record-level):** train 46,348 (90.00%), validation 2,575 (5.00%),
  test 2,575 (5.00%). Allocation is deterministic, leakage-safe
  (node-id-set clusters never straddle splits), size-tier-stratified.
  **Recommendation:** train on `metadata.split == "train"`; evaluate on
  `validation`; reserve `test` for final evaluation only.

## 6. LoRA configuration (repository-established)

| Hyperparameter | Value | Source |
|---|---|---|
| Base model | `unsloth/gemma-3-4b-it-bnb-4bit` (NF4, cached locally) | `docs/training_plan.md`, `backend/core/inference.py` |
| Quantization | NF4, `bnb_4bit_quant_type="nf4"`, compute `float16` | `lora_train.py`, `training_plan.md` |
| Method | LoRA (PEFT), adapter only | `training_plan.md` |
| `r` / `lora_alpha` / `lora_dropout` / `bias` | 16 / 32 / 0.05 / `none` | `training_plan.md`, `lora_train.py` |
| Target modules | `q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj` | Gemma 3 names; `training_plan.md` |
| Task type | `CAUSAL_LM` | `lora_train.py` |
| Batch size / grad accum | 1 / 8 (effective 8) | 6 GB VRAM budget |
| Optimizer | AdamW | `lora_train.py` |
| LR | 2e-4 | `training_plan.md` |

## 7. Recommended additions (not repository-established)

| Item | Recommendation | Justification |
|---|---|---|
| `max_length` | **1024** | Section 4: zero truncation on the actual artifact |
| Epochs | 2–3, watch validation loss | `training_plan.md` guidance |
| Scheduler | Linear warmup 10% of steps, cosine decay | `training_plan.md` guidance |
| Weight decay | 0.01 | `training_plan.md` guidance |
| Seed | 42 (torch + dataloader generator) | deterministic reproduction |
| Prompt masking | labels = -100 for prompt tokens | Section 3 (Phase 5 debt) |
| Eval split | validation records, no dropout, greedy | early stopping on real held-out data |
| Gradient checkpointing | enabled | `training_plan.md` |
| Output | `checkpoints/gemma_lora/` (adapter only) | `inference.py` probes this path via `LORA_ADAPTER_PATH` |

## 8. Evaluation metrics (repository-established, `training_plan.md` §9)

| Metric | Instrument |
|---|---|
| Structural validity | % outputs parse to `{nodes, edges}` with valid types/labels/references (`backend/core/architecture_validator.py`) |
| Graph size compliance | nodes ≤ 10, edges ≤ 15 (hard guardrail); soft target 8/10 tracked separately |
| Security-score delta | mean engine `security_score` of generated graphs vs dataset prior (per split: train/val/test ≈ 24.8/43.1/23.6 mean) |
| Missing-control recall | engine `missing_components` on generated graphs |
| Risk-level distribution | LOW/MEDIUM/HIGH balance vs split priors |
| Determinism | greedy decode, P(identical output) over n runs |
| Latency / VRAM | `torch.cuda` instrumentation |

Note: legacy BLEU/ROUGE explanation metrics apply to the deferred explanation
task only.

## 9. Known limitations (must be stated in any training run report)

1. Size diversity: 97.2% of records have exactly 10 nodes / 60.8% exactly 9
   edges (subgraph extraction saturates at the hard guardrail). The model will
   predominantly emit ~10-node graphs; size diversity lives in node/edge
   composition, not counts.
2. Risk prior: 88.8% HIGH / 11.1% MEDIUM / 0.07% LOW overall (subgraph
   recomputation, not the Phase-5 parent-corpus prior of 98.75% HIGH). Per
   split: 11.1% / 11.8% / 10.6% MEDIUM — near-identical, by construction.
3. Instructions are source-derived and template-constructed; the grammar has
   documented imperfections ("Design a E-Commerce architecture."). Content is
   genuine source metadata; the prompt is used verbatim for deployment
   fidelity.
4. The prompt states "Max nodes: 8 / Max edges: 10" (soft target) while
   97.2% of targets have 10 nodes (hard guardrail). Targets are
   hard-guardrail-legal; the mismatch is intentional (runtime prompt fidelity)
   and may induce occasional retries for >8-node outputs at inference.
5. 365 of 51,498 records (0.71%) share an instruction with different targets
   (max reuse 3). Kept deliberately: same prompt, multiple valid graphs is
   benign for SFT and matches deployment behaviour.
6. Near-duplicate node sets exist (530 multi-record clusters, max 62 records);
   the split guarantees they never straddle splits (verified, 0 straddles).
7. `security_summary` is engine-derived, not human supervision; it is not a
   target (D1).
8. Source of the corpus is an AI-generated HF dataset
   (`ajibawa-2023/Technical-Architectures-Large`); the data is NOT
   "real-world architecture data" — provenance and this label must be
   preserved in any downstream publication.