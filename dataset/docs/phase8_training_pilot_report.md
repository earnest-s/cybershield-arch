# Phase 8 Training Pilot Report

**Status:** PILOT COMPLETE — pipeline validated end-to-end. **FULL TRAINING STATUS: NOT STARTED** (requires explicit approval; 46,348-record run is NOT launched).

## 1. Environment (measured)

| Item | Value |
|---|---|
| GPU | NVIDIA GeForce RTX 4050 Laptop (Ada, cc 8.9), 5.66 GiB usable VRAM |
| Software | Python 3.12.13 (uv), torch 2.13.0+cu130, CUDA 13.0, transformers 5.14.1, peft 0.20.0, bitsandbytes 0.50.0, accelerate 1.14.0, datasets 5.0.1 |
| Base model | `unsloth/gemma-3-4b-it-bnb-4bit` (cached snapshot `eb03c885…`, offline) → `Gemma3ForConditionalGeneration` |
| Quantization | 4-bit NF4 (checkpoint-baked config), bf16 compute; 3.01 GiB after load |
| LoRA | r=16, α=32, dropout 0.05, bias none, CAUSAL_LM; language-model-only regex target modules (238 modules; vision_tower/projector excluded); 29,802,496 trainable params (0.6883%) |
| Optimizer | AdamW 8-bit, lr 2e-4 |
| Sequence | unpadded, batch size 1, grad-accum 8 (effective batch 8), max_length 1024 (0 truncation; max real 605 tokens) |
| Loss | chunked cross-entropy (64-token), prompt tokens masked (-100), Gemma chat template, seed 42 |

## 2. Pilot training results (400 train / 100 validation, 1 epoch, 50 optimizer steps)

- Final train loss: **0.2993** (avg over epoch 0.4389); final validation loss: **0.3103**
- Validation loss trajectory: 0.4779 → 0.3924 → 0.3639 → 0.3385 → 0.3241 → 0.3115 (monotone improvement)
- Peak VRAM: **3.43 GiB** (of 5.66 GiB); wall time **600.1 s**; tokens processed 93,172
- Checkpoint: `checkpoints/gemma_lora_pilot/` → `adapter_config.json` + `adapter_model.safetensors` (119 MB); reloaded successfully via `PeftModel.from_pretrained` in the evaluation harness (base frozen, 4-bit)

## 3. Harness bugs found and fixed during the pilot (root causes)

1. **Repeated evaluation at the same optimizer step.** In `lora_train.py` the eval condition was a sibling of the gradient-accumulation block: it was tested on every micro-batch while `step` increments only every 8 micro-batches, so at every step boundary divisible by `eval_every_steps` the full eval ran 8×. Fix: move the eval inside the step-increment block + `last_eval_step` guard. Verified by control-flow simulation: evals fire exactly once at steps 8,16,24,32,40,48, plus the final epoch-end eval.
2. **`ModuleNotFoundError: backend` in the generation eval.** The eval script ran with its own directory on `sys.path`, not the repo root. Fix: repo root inserted into `sys.path` in `phase8_pilot_eval.py` (+ PYTHONPATH in the runner subprocess env). Eval then ran on the existing adapter — no retraining, no adapter overwrite.

## 4. Generation evaluation (50 held-out validation prompts, greedy, seed 42)

| Metric | Result |
|---|---|
| Generation success | 50/50 (1.0) |
| Valid JSON parse rate | 46/50 (0.92) |
| Schema validity (validator, error-severity) | 46/50 (0.92) |
| Validator issue counts | **0** (no dangling edges, duplicates, self-loops, unsupported types/labels, collisions) |
| Connectedness | 100% of parsed graphs weakly connected |
| Structurally weak / orphan nodes | 0 / 0 |
| Node count | avg 7.13, max 8 (contract ≤ 10) |
| Edge count | avg 7.74, max 10 (contract ≤ 15) |
| Guardrail (≤10 nodes / ≤15 edges) | 46/46 of parsed (1.0) |
| Exact match vs expected target | 0/50 (0.0) |
| Fabricated nodes / rate | 237 total, 0.72 of generated nodes |
| Missing nodes (vs target) | 277 |
| Fabricated edges / rate | 334 total, 0.94 of generated edges |
| Missing edges (vs target) | 310 |
| Wall time / peak VRAM | 604.7 s / 3.23 GiB |
| Artifact | `dataset/docs/phase8_pilot_generation_eval.json` (n=50) |

## 5. Quality diagnosis (honest, no configuration changes made to improve numbers)

1. **4/50 parse failures (8%)** — SFT-046354, SFT-046374, SFT-046379, SFT-046397. The model enters a **greedy edge-repetition loop** (e.g., repeated `WebUI→APIGW→LB→AuthZ→IAM→APIGW…` patterns) and never closes the JSON object. Verified NOT an output-cap artifact: rerun at 1024 new tokens still produced no complete object (4096 generated tokens total, parse 0/4); these targets are only 201–274 tokens long. Evidence: `dataset/docs/phase8_parse_fail_diagnostic.json`. This is a model-adherence failure of the pilot adapter on long-edge-list prompts.
2. **Fabrication is real component invention, not naming drift.** fab-vs-missing node-name similarity mean 0.43, only 18% near-matches; e.g. SFT-046349 generated `{EdgeLB, EdgeNet, IoTDevice, LB}` while the target has `{AdminPortal, CDN, FW, IAM, RBAC}`. The pilot adapter learned the **format** (valid JSON, allowed types/labels, connectivity, size limits — zero validator issues) but not **content fidelity** to the expected architecture inventory.
3. Interpretation: the 400-record / 1-epoch / 0.69%-params pilot is a pipeline-validation run, not a quality target. Format mastery is demonstrated; fidelity will be re-measured on the full run. No claims about full-run quality are made here; no dataset or training configuration was changed to influence these metrics.

## 6. Quality gates (Phase 8)

| Gate | Result |
|---|---|
| G1 corpus immutable (e3ee9810…) | PASS |
| G2 SFT artifact immutable (8c91e5cd…) | PASS |
| G3 pilot adapter exists | PASS |
| G4 generation eval JSON present (n=50) | PASS |
| G5 parse ≥ 0.80 / schema-valid ≥ 0.80 / connected == 1.0 / no structural weakness / guardrail on parsed == 1.0 | PASS |
| **OVERALL** | **PASS** |

## 7. Deliverables and artifacts

- `backend/training/gemma/lora_train.py` — fixed harness (eval-once per step)
- `backend/training/gemma/phase8_pilot_run.py` — streaming runner
- `backend/training/gemma/phase8_pilot_eval.py` — generation evaluation (repo-root import fix + full metric set)
- `backend/training/gemma/phase8_quality_gates.py` — gates, all PASS
- `dataset/docs/phase8_training_config.md` — configuration specification
- `dataset/docs/phase8_pilot_generation_eval.json` — per-output generation metrics (n=50)
- `dataset/docs/phase8_parse_fail_diagnostic.json` — parse-failure evidence
- `checkpoints/gemma_lora_pilot/` — LoRA adapter (119 MB), verified reload

## 8. Recommendation for the full run (pending approval)

- Configuration identical to the pilot (model, quantization, LoRA, loss, optimizer, seed policy, max_length 1024, eval on the full 2,575-record validation split).
- Expected scale: 46,348 train records, 2–3 epochs, ~5,793 optimizer steps/epoch; extrapolating pilot throughput (~600 s / 400 records incl. evals), roughly 1.5–2 h per epoch + eval passes on the RTX 4050.
- Expected risks: same 8%-class adherence failures may persist unless the larger dataset helps; fidelity to be re-measured post-training with the same eval harness and reported separately.
- **FULL TRAINING STATUS: NOT STARTED.** Awaiting explicit user approval.
