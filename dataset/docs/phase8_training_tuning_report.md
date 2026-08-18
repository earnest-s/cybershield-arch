# Phase 8 Training Tuning Report

**Status:** COMPLETE — configuration selected by measured held-out architecture fidelity.

## 1. Motivation

The Phase 8 pilot (400 records, r16, 1 epoch) learned the JSON **format** perfectly
(100% of parseable outputs validator-clean, connected, within limits) but showed
0% exact match and poor content fidelity (node F1 0.30, edge F1 0.09 on 30 held-out
prompts; fabricated-node rate 0.72), plus a ~8% parse-failure class caused by greedy
edge-repetition loops. This report documents the controlled experiments used to
improve the training objective before committing to the full 46,348-record run.

## 2. Data characterization (quantified, not guessed)

| Fact | Value |
|---|---|
| Node-count saturation | **98.2%** of all 51,498 targets have exactly 8 nodes (mode 7 edges, 74.3%; 8–10 edges 25%) |
| Consequence | node-count conditioning is **unlearnable** — the label is nearly constant; count-based exact matching cannot improve |
| Target ordering | NOT canonical: only 2.6% of node lists and 4.7% of edge lists are sorted; emission order is arbitrary |
| Consequence | exact architecture match is nearly impossible even with perfect fidelity; F1 against the target set is the correct metric |
| ID conventions | mixed per record (53% ALL-CAPS, 44% camelCase, 3% upper_underscore) — style must be inferred per prompt |
| Template vs data | instruction template "Max nodes: 8 / Max edges: 10" is **consistent** with target distribution (max observed 8 nodes / 10 edges) |
| Duplicate edges in targets | 0 (targets clean) |

## 3. Harness upgrades (before experiments)

- `lora_train.py`: `--lora-r`, `--lora-alpha`, `--warmup-frac`, `--scheduler`
  (cosine with linear warmup via `get_cosine_schedule_with_warmup`, default 10%);
  per-step live progress; eval exactly once per optimizer step (bug fixed earlier).
- `phase8_generate_eval.py` (new): rich fidelity metrics — node/edge precision,
  recall, F1 vs target; exact match; parse-failure categories; EOS vs token-cap
  completion; repeated-edge (repetition-loop) detection; deterministic greedy
  generation with optional `repetition_penalty` / `no_repeat_ngram_size`;
  batched generation (`--gen-batch`) with per-sequence EOS stop.
- `phase8_tune_experiment.py` (new): reproducible per-experiment runner
  (fixed 800-record train subset, seed 42, held-out 100-record validation eval).
- `phase8_tune_compare.py` (new): aggregates results, ranks by fidelity,
  writes `phase8_tuning_winner.json` consumed by the full-run runner.

## 4. Generation-side experiments (pilot adapter, 30 held-out prompts)

| Config | parse | hit-cap (loop class) | node F1 | edge F1 | verdict |
|---|---|---|---|---|---|
| greedy, rep 1.0 | 0.933 | 0.067 | 0.296 | 0.091 | baseline |
| greedy, **rep 1.1** | 0.967 | 0.033 | 0.289 | 0.110 | **selected** — kills loop class, no fidelity loss |
| rep 1.1 + ngram 4 | 0.267 | 0.000 | 0.057 | 0.000 | **rejected** — ngram bans JSON structure tokens |

**Final inference generation config:** greedy decoding, `repetition_penalty=1.1`,
no ngram ban, `max_new_tokens=768`. Deterministic and reproducible; no sampling used.

## 5. Training experiments (800-record subsets, 1–2 epochs, seed 42)

| Exp | r/α | lr | epochs | train loss | val loss | node F1 | edge F1 | parse | connected | EOS |
|---|---|---|---|---|---|---|---|---|---|---|
| E1 | 16/32 | 2e-4 | 1 | 0.4461 | 0.3248 | 0.226 | 0.067 | 1.000 | 0.860 | 1.000 |
| E2 | 32/64 | 2e-4 | 1 | — | — | — | — | — | — | — | **OOM** (256 MiB alloc fail; 4.41 GiB allocated — r32 infeasible on 5.66 GiB) |
| E2b | **24/48** | 2e-4 | 1 | 0.4287 | 0.3174 | 0.239 | **0.084** | 1.000 | **0.910** | 1.000 |
| E3 | 16/32 | 1e-4 | 1 | 0.4991 | 0.3529 | 0.201 | 0.062 | 1.000 | 0.720 | 1.000 |
| E4 | 16/32 | 5e-4 | 1 | 0.3985 | 0.2997 | **0.241** | 0.078 | 1.000 | 0.840 | 1.000 |
| E5 | 16/32 | 2e-4 | **2** | 0.2575 | 0.2922 | 0.228 | 0.069 | 1.000 | 0.740 | 1.000 |

Notes:
- All parsed outputs were validator-clean (0 issues) and within the ≤10/≤15 contract;
  with rep 1.1 + 768 cap, **no repetition-loop failures occurred in any experiment**.
- E2 (r32) answers the capacity axis: infeasible on this GPU with this pipeline.
- E5 (2 epochs) provides **no fidelity gain** over E1 at fixed 800 records
  (0.228/0.069 vs 0.226/0.067) → exposure breadth, not repetition, is the limiter.
- LR effect is modest but consistent: 5e-4 ≥ 2e-4 > 1e-4 on edge F1.

## 6. Selection

**Winner: E2b — LoRA r=24, α=48, lr 2e-4, grad-accum 8, cosine warmup 10%, 1 epoch**
(seed 42, max_length 1024, chunked CE, 8-bit AdamW, language-model-only target
modules, prompt masking, Gemma chat template).

Why it won: best **edge F1 (0.084)** and best **connectedness (0.910)** among
all feasible configurations, with perfect parse/schema/EOS and zero repetition
failures; r24 fits the 6 GB budget (r32 does not); 1 epoch is supported by E5's
null result for epoch count; 5e-4 lr (E4) trails on edge F1 and connectedness.

The full run uses `dataset/docs/tuning/phase8_tuning_winner.json`
(r24/α48/2e-4/1 epoch) — written by `phase8_tune_compare.py`.

## 7. Expected full-run scale (honest)

Measured ~1.2–1.4 s per record (batch 1, no padding) → 46,348 records ≈
**16–18 h/epoch** + 6 validation passes (2,575 records each ≈ 13 min) ≈
**~17–19 h total for the selected 1-epoch configuration**. Earlier config-spec
estimates ("5–8 min/epoch") were based on a misread of step timing and are
superseded by these measured numbers.

## 8. Artifacts

- `dataset/docs/tuning/E{1,2b,3,4,5}_gen.json` + `*_train.log` + `<exp>.json`
- `dataset/docs/tuning/pilotgen_G{0,1,2}.json` (generation-side experiments)
- `dataset/docs/tuning/phase8_tuning_winner.json` (selected config)
- `checkpoints/exp_{E1,E2b,E3,E4,E5}/` (experiment adapters, preserved)
- `backend/training/gemma/phase8_{tune_experiment,tune_compare,generate_eval,full_run}.py`
