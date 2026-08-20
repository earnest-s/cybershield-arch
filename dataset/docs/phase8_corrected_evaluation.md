# Phase 8 Corrected Evaluation

**Status:** COMPLETE — final evaluation re-run against FULL (untruncated) canonical targets.
**Date:** 2026-08-20

> This report supersedes the structural-comparison metrics in `phase8_final_evaluation.md`.
> It does **not** replace that report; the earlier report remains the historical record of the
> originally-reported (truncated-target) numbers. No dataset, model, runtime, or frontend was
> changed to produce this report. See `dataset_artifact_reconciliation.md` for the audit that
> identified the measurement defect.

## 1. Why the original evaluation was distorted

The legacy eval (`phase8_generate_eval.py`) loaded **both** the canonical target and the generated
output through `parse_architecture()`, which silently caps node sets at `MAX_NODES=8` and edge sets
at `MAX_EDGES=10` (`backend/core/architecture_schema.py`). Consequences for the original report:

1. **Targets were truncated, not the dataset.** 2,518 of 2,575 test targets (97.8%) lost nodes to
   the 8-node cap — every 10-node target (2,503 records) and every 9-node target (15 records) was
   compared as if it had 8 nodes. Reported "target avg 7.93 nodes" was an artifact; the real mean is
   9.88. Target node distribution was reported as `{8: 2528, ...}` instead of
   `{10: 2503, 9: 15, 8: 10, 7: 11, 6: 9, 5: 7, 2: 20}`.
2. **Generated outputs were truncated too.** Reported "generated avg 8.0 nodes / 7.15 edges"
   (max 8/10) were the *runtime-parsed* sizes of outputs that actually contain 10.01 nodes / 9.21
   edges (max 11/14). Every single output (2,575/2,575) is truncated by the runtime parser.
3. **"Count conditioning works" was comparing two truncated numbers.** 8.0 vs 7.93 was a
   parser artifact; the model actually reproduces the ~10-node target distribution (10.01 vs 9.88)
   and even exceeds the 10-node hard limit in 31 outputs.
4. **`contract_valid_rate == 1.0` was also an artifact.** Truncated graphs can never exceed
   8/10, so "100% within contract" was guaranteed by construction. Against the full generated graph,
   the true contract-valid rate is **0.988** (31 outputs emit 11 nodes).

## 2. Corrected evaluation contract

| Concern | Method |
|---|---|
| Generated output parsing | `normalize_full` — mirrors runtime normalization **without** node/edge caps (`phase8_corrected_eval.py`) |
| Canonical target loading | `r["architecture"]` verbatim — **never parsed or truncated** |
| Structural comparison | Full generated graph vs full target graph (node-id set + directed edge-key set) |
| Schema validation | `architecture_validator.collect_issues` on the full generated graph |
| Runtime-faithful view | `parse_architecture` (capped) kept separately as `schema_valid_runtime` |
| Runtime contract | ≤10 nodes / ≤15 edges evaluated on the **full** generated graph |
| Structurally weak | not weakly connected OR has orphan node |

Identical generation settings to the legacy run: adapter `checkpoints/gemma_lora`, split `test`,
n = 2,575, seed 42, `max_new_tokens=768`, `gen_batch=3`, `repetition_penalty=1.1`,
`no_repeat_ngram=0`, EOS 106, base `unsloth/gemma-3-4b-it-bnb-4bit` (4-bit NF4, local cache).
Wall time 9,661 s; peak VRAM 3.41 GiB. Artifact: `dataset/docs/phase8_corrected_test_eval.json`.

**Generation determinism was verified**: per-record token counts, node counts, edge bounds,
connectedness, and orphan flags are byte-identical to the legacy run for all 2,575 records.
The only thing that changed is the comparison target.

## 3. Corrected results (n = 2,575) — old vs new

| Metric | OLD (truncated targets) | NEW (full targets) | Δ |
|---|---|---|---|
| Parse rate | 1.0 | 1.0 | — |
| Schema-valid rate (full graph) | 1.0* | **0.988** | −0.012 |
| Schema-valid rate (runtime view) | 1.0 | 1.0 | — |
| Contract-valid rate (≤10/≤15, full graph) | 1.0* | **0.988** | −0.012 |
| Connectedness rate | 0.9996 | 0.9996 | — |
| Orphan rate | 0.0004 | 0.0004 | — |
| Structurally-weak rate | 0.0004 | 0.0004 | — |
| Repetition-loop rate | 0.0 | 0.0 | — |
| EOS completion rate | 1.0 | 1.0 | — |
| **Node F1** | 0.2242 | **0.2370** | +0.013 |
| Node precision / recall | 0.2233 / 0.2252 | 0.2355 / 0.2385 | +0.012 / +0.013 |
| **Edge F1** | 0.0647 | **0.0688** | +0.004 |
| Edge precision / recall | 0.0652 / 0.0642 | 0.0699 / 0.0678 | +0.005 / +0.004 |
| Exact match rate | 0.0 | 0.0 | — |
| Generated nodes (full) | 8.0* (max 8)* | **10.01 (max 11)** | — |
| Generated edges (full) | 7.15* (max 10)* | **9.21 (max 14)** | — |
| Target nodes | 7.93* | **9.88 (10: 2503, 9: 15, 8: 10)** | — |
| Target edges | 7.26* | **9.51** | — |
| Node count error (mean \|Δ\|) | — | 0.1282 | — |
| Edge count error (mean \|Δ\|) | — | 0.819 | — |
| Avg prompt / generated tokens | 222.7 / 220.0 | 222.7 / 220.0 | — |

\* OLD value was computed on parser-truncated graphs and is an artifact.

### Failure inventory (full-graph view)
- Parse failures: 0. Repetition loops: 0. Token-cap truncations: 0.
- Disconnected / orphan: 1 (same output as before, `SFT-050933`).
- **Size guardrail violations: 31** (`issue_counts.size_guardrail = 31`) — 28 outputs at
  11 nodes / 10 edges, 3 at 11 nodes / 11 edges. All other validator issue classes: 0.

## 4. Interpretation

1. **The corrected comparison does not change the overall conclusion.** Fidelity to canonical
   targets is still low: node F1 0.237, edge F1 0.069, exact match 0.0. The model produces valid,
   plausible graphs whose component inventory only partially matches the target, exactly as
   previously reported.
2. **The magnitude of the correction is modest** (node F1 +0.013, edge F1 +0.004) because the
   fundamental bottleneck is node *naming*: the extra 2 nodes the model emits (10.01 vs the old
   truncated count of 8.0) rarely use the target's per-record arbitrary names, so true recall only
   edges up from 0.225 to 0.239.
3. **A real defect this surfaces:** every generated output (2,575/2,575) is silently truncated by
   the runtime parser at serve time (`MAX_NODES=8`/`MAX_EDGES=10` vs a model trained on 10-node
   targets). 31 outputs even exceed the 10-node hard limit; the runtime drops the 11th node.
   `runtime_truncation_outputs = 2575`. This is a runtime-contract mismatch beyond eval correctness
   and is gated behind the runtime-freeze decision.
4. **Count conditioning was better than reported** — the model reproduces the ~10-node target
   distribution (10.01 vs 9.88; mean node-count error 0.128). The old "8.0 vs 7.93" match was a
   truncation artifact, not evidence of saturation at 8.
5. **Gate result:** the quality gates' structural metrics (connected, structurally-weak) are
   unchanged and still fail G5 on the single 0.04% disconnected output. No thresholds were changed.

## 5. Verdict

- The corrected evaluation confirms the pilot finding at full scale: **the model is valid-but-only-
  partially-correct** against full canonical targets (exact match 0%, edge F1 0.069, node F1 0.237).
  The original report's qualitative conclusion stands; its quantitative figures were slightly
  depressed by the truncated-target comparison.
- **Retraining was not performed and is not warranted by this correction.** No dataset or model
  change was needed to fix the measurement; the corrected baseline simply measures the same model
  against the true targets.
- **Re. the redesign proposal** (`dataset_redesign_proposal.md` §5–§7, canonical-ID/order
  normalization): the corrected baseline does **not** invalidate the proposal's motivation — per-
  record arbitrary naming remains the identified cause of the node/edge-F1 plateau — but it does
  correct the baseline it would be compared against: **node F1 0.2370 / edge F1 0.0688 / exact 0%**
  measured against full targets (not 0.2242 / 0.0647). The proposal may proceed as the next decision,
  now with an accurate baseline.