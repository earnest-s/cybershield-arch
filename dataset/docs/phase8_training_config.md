# Phase 8 Training Configuration — CyberShield Gemma SFT v1

**Status:** SPECIFICATION for the Phase 8 pilot (and, after separate approval,
the full run). Every value below is either repository-established or a Phase 8
decision justified by the Step 4 dry-run measurements on the target hardware.

## Environment (measured)

| Item | Value |
|---|---|
| GPU | NVIDIA GeForce RTX 4050 Laptop (Ada, cc 8.9) |
| VRAM | 5.66 GiB usable of 6,141 MiB (6141 MiB per nvidia-smi) |
| Driver / CUDA UMD | nvidia-smi 610.57.04, CUDA 13.3 UMD |
| torch | 2.13.0+cu130 |
| transformers | 5.14.1 |
| peft | 0.20.0 |
| bitsandbytes | 0.50.0 |
| accelerate | 1.14.0 |
| datasets | 5.0.1 |
| Python / uv | 3.12.13 via `uv run` |
| Model cache | repo-local `.cache/huggingface/hub` (offline, `local_files_only=True`) |

## Base model (repository-established)

`unsloth/gemma-3-4b-it-bnb-4bit` — cached snapshot `eb03c885…`, 3.01 GiB.
Resolves to **`Gemma3ForConditionalGeneration`** (multimodal) via
`AutoModelForCausalLM.from_pretrained` (verified: loads in ~1 s, no error).
Weights on disk: language model linears pre-quantized 8-bit (1 byte/elem),
embeddings bf16 (1,280 MiB, tied to lm_head — no separate lm_head tensor).
The checkpoint carries its own `quantization_config` (load_in_4bit, nf4,
`bnb_4bit_compute_dtype=bfloat16`, double quant, uint8 storage) which takes
precedence over any passed config (transformers warning observed; harmless).

## Quantization (repository-established, confirmed)

4-bit NF4 via bitsandbytes, applied at load. VRAM after load: **3.01 GiB**.
Parameter dtypes present: `torch.uint8` (quantized linears) + `torch.bfloat16`
(embeddings). Compute dtype: bfloat16 (from the checkpoint's config).

## LoRA configuration (repository-established with one Phase 8 correction)

| Parameter | Value | Source |
|---|---|---|
| r | 16 | repository-established (training_plan.md) |
| lora_alpha | 32 | repository-established |
| lora_dropout | 0.05 | repository-established |
| bias | none | repository-established |
| task_type | CAUSAL_LM | repository-established |
| **target_modules** | `model\.language_model\..*(q_proj\|k_proj\|v_proj\|o_proj\|gate_proj\|up_proj\|down_proj)` | **Phase 8 correction (see below)** |
| trainable | 29,802,496 (0.688%) | measured |

**Correction justification:** with plain module names (`q_proj`, …) PEFT's
suffix matching attached adapters to the **vision tower** (81 modules) too.
The SFT task is text-only; the regex scopes LoRA to the language model
exclusively (measured: 238 modules, vision_tower=0, projector=0). This is a
harness configuration fix, not a training-target change.

## Training preparation (Phase 8 correction — concrete, measured)

`peft.prepare_model_for_kbit_training` is **not used**. It casts every bf16
parameter to fp32 unconditionally; the tied 262,208×2,560 bf16 embeddings
require a 2.50 GiB fp32 allocation, which OOMs at load (measured). Manual
equivalent used instead:

```python
model.config.use_cache = False
model.gradient_checkpointing_enable()
for p in model.parameters(): p.requires_grad_(False)
model.enable_input_require_grads()
```

Identical semantics for LoRA-only training: base frozen, gradient
checkpointing on, embeddings frozen (standard QLoRA for a 6 GB budget).

## Loss (Phase 8 correction — concrete, measured)

**Chunked cross-entropy** (64-token chunks, `reduction="sum"` normalised by
the non-masked count). Mathematically identical to the standard mean CE over
non-ignored tokens. The full-sequence fp32 softmax over the 262,208-token
vocabulary OOMs at the longest real records (measured: 606 MiB allocation
fails with 527 MiB free). Chunked loss fits comfortably.

**Prompt masking:** labels = -100 for all prompt tokens (chat template
`<start_of_turn>model\n` boundary), so only the target JSON tokens contribute.
Verified in the dry run (e.g. 236 prompt tokens masked, 370 active targets).

## Optimizer (Phase 8 recommendation)

**AdamW 8-bit** (bitsandbytes) at lr 2e-4. Base AdamW fp32 states for 29.8 M
trainable params cost ~238 MiB; 8-bit ~60 MiB. Measured with 8-bit AdamW:
peak 4.49 GiB on the 606-token worst case (vs OOM without). 8-bit AdamW is
the standard QLoRA memory-optimizer choice and is numerically equivalent in
practice for LoRA-scale parameter counts.

## Scheduler / decay / clipping (repository-established guidance)

| Parameter | Value | Source |
|---|---|---|
| Scheduler | linear warmup 10% steps + cosine decay | training_plan.md |
| Weight decay | 0.01 | training_plan.md |
| Gradient clipping | 1.0 (recommendation; max norm) | standard guard, cheap |
| Epochs | 2–3 | training_plan.md; pilot uses 1–2 |
| Batch size | 1 | training_plan.md (6 GB VRAM) |
| Gradient accumulation | 8 (effective batch 8) | training_plan.md |
| Sequence length | max_length 1024 (truncation cap only; **no padding**, measured max real 605 tokens → 0 truncation) | Phase 7 measurement + Phase 8 unpadded batch |
| Eval | validation split, batch 1, greedy, no dropout | Phase 7 artifact + harness |
| Save | `checkpoints/gemma_lora/` (adapter only) at end; loader at `backend/core/inference.py` probes `LORA_ADAPTER_PATH` | repository-established |
| Seed | 42 (random, torch, cuda, DataLoader generator) | Phase 8 decision |

**No padding:** the harness tokenizes without `padding="max_length"` and
trains at batch size 1, so every batch is exactly the record's real length.
This removes ~41% of sequence-level memory at the median (450 vs 1024
tokens) and was decisive for fitting 6 GB (measured).

## VRAM budget (measured on the 606-token worst-case record)

| Stage | VRAM |
|---|---|
| After 4-bit load | 3.01 GiB |
| After LoRA + prep | ~3.6 GiB |
| **Peak during backward** | **4.49 GiB** (with 8-bit AdamW + chunked CE) |
| Headroom | ~1.2 GiB |

## Pilot configuration (Step 5)

- ~400 training records (train split, seeded)
- ~100 validation records (validation split, seeded)
- epochs 1; grad_accum 8; eval every 8 steps; everything else as above
- Purpose: verify the pipeline (start, loss descent, eval, save/reload,
  generation, validation), NOT final quality.

## Full-run configuration (for the separate Phase 8 approval)

- All 46,348 train records; 2,575 validation records; 2–3 epochs
- Estimated cost: ~5.4–8.1 minutes/epoch at the measured ~1.7 s/step
  (batch 1 × 8 accum = 5,793 optimizer steps/epoch) plus eval passes →
  **~15–35 minutes wall-clock total** (dominated by CPU dataset loading and
  eval); token throughput ~40–60 target tokens/s
- Same model, quantization, LoRA, loss, optimizer, seed policy
- Resume support is a noted gap (no mid-run checkpointing in the harness);
  acceptable for a ~30 min run, to be added only if required

## Validation gates (post-pilot)

Structural validity, JSON parse rate, schema/validator compliance (≤10 nodes,
≤15 edges, canonical types/labels, no dangling edges), security-score delta,
checkpoint reload + generation decode. Full list in
`phase8_training_pilot_report.md`.
