# Phase 8 Full Training Report

**Status:** COMPLETE — full approved run executed and adapter saved.

## 1. Approved configuration (tuning winner, E2b)

| Parameter | Value |
|---|---|
| Model | `unsloth/gemma-3-4b-it-bnb-4bit` (4-bit NF4, bf16 compute, checkpoint-baked quantization config) |
| LoRA | **r=24, α=48**, dropout 0.05, bias none, CAUSAL_LM, language-model-only regex target modules (vision tower / projector excluded) |
| Trainable params | ~44.7 M (0.69% class — exact count recorded in adapter_config.json) |
| Learning rate | **2e-4**, 8-bit AdamW (bitsandbytes) |
| Scheduler | linear warmup 10% (579/5,793 steps) + cosine decay |
| Batch | 1 (unpadded) × grad-accum 8 (effective 8) |
| Loss | chunked cross-entropy (64-token), prompt tokens masked (-100), Gemma chat template |
| Sequence | max_length 1024 (0 truncation; max real 605 tokens) |
| Data | train 46,348 / validation 2,575 (Phase 7 SFT artifact, seed 42) |
| Epochs | **1** (per tuning evidence: E5's 2-epoch arm showed no fidelity gain at fixed exposure) |

## 2. Execution (measured)

| Metric | Value |
|---|---|
| Wall time | **49,648 s ≈ 13.8 h** (1 epoch incl. 6 validation passes) |
| Optimizer steps | 5,793 |
| Target tokens processed | 10,627,045 |
| Peak VRAM | 3.53 GiB (of 5.66 GiB usable) |
| Final training loss | **0.2331** (epoch average) |
| Validation loss trajectory | 0.2440 → 0.2118 → 0.2008 → 0.1929 → **0.1912** (monotone) |
| Per-record throughput | ~1.0–1.1 s (measurement basis: 46,348 records + 6 × 2,575 eval records) |
| Environment | Python 3.12.13, torch 2.13.0+cu130, CUDA 13.0, transformers 5.14.1, peft 0.20.0, bitsandbytes 0.50.0, accelerate 1.14.0; git 4a49e614; RTX 4050 Laptop 6141 MiB (recorded in `dataset/docs/phase8_full_run_metrics.json`) |

## 3. Checkpoint

- **Adapter:** `checkpoints/gemma_lora/` → `adapter_config.json` + `adapter_model.safetensors` (178.9 MB)
- Loaded via `PeftModel.from_pretrained` over the frozen 4-bit base (verified in the final test evaluation)
- Production load path `backend/core/inference.py` probes `LORA_ADAPTER_PATH` (= `checkpoints/gemma_lora`) — satisfied
- The Phase 8 pilot adapter `checkpoints/gemma_lora_pilot/` was **not** overwritten
- Training log: `dataset/docs/phase8_full_run.log`; runner metrics: `dataset/docs/phase8_full_run_metrics.json`

## 4. Notes

- A benign peft warning ("Could not find a config file … vocabulary was not modified") was emitted at save time; the vocabulary is unchanged (same tokenizer), so the adapter is loadable as verified by the final evaluation.
- The full-run runner reads the tuning winner (`dataset/docs/tuning/phase8_tuning_winner.json`) and refuses to run without it unless `--override-config` is passed; it was not needed.

## 5. Final evaluation

See `dataset/docs/phase8_final_evaluation.md` and `dataset/docs/phase8_final_test_eval.json` (2,575-record untouched test split). Summary:

- Parse rate 1.0, schema-valid 1.0, contract-valid 1.0, connected 0.9996, repetition loops 0, EOS completion 1.0
- Node F1 0.224, edge F1 0.065, exact match 0.0 — **format/structure mastered, content fidelity not achieved**
- Phase 8 quality gates on this eval: OVERALL FAIL (2 strict-equality G5 gates fail on the single 0.04% disconnected output; 7/9 PASS)