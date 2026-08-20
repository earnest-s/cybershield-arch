# Training Plan: Gemma 3 LoRA Fine-Tuning

This document specifies how the curated dataset produced by the data
engineering pipeline (`dataset/`) is turned into a fine-tuned architecture
generation model. **No training is performed in this phase** — this plan
guides the subsequent, explicitly approved training milestone.

## 1. Model

| Item | Choice | Rationale |
| --- | --- | --- |
| Base model | `unsloth/gemma-3-4b-it-bnb-4bit` | Ungated NF4 mirror of `google/gemma-3-4b-it`; already integrated in `backend/core/inference.py`. |
| Transformers | `>= 4.51` | Gemma 3 architecture support. |
| Quantization | NF4, `double_quant=True`, compute `float16` | Fits 6 GB VRAM (RTX 4050 Laptop, 6141 MiB). |
| Precision | bf16/fp16 mixed | Native on Ampere+; matches existing generation path. |

Gemma 3 uses a single-turn chat template with no system role; fine-tuning
data must therefore use `user -> model` turns only.

## 2. Instruction tuning format

One training record is an instruction with a structured JSON response:

```
user:
You are a senior software architect.

Convert the following system description into a CLEAN architecture graph.
...
Description:
{instruction}
ONLY return JSON. No explanation.

model:
{"nodes": [{"id": "web", "type": "ui"}, ...], "edges": [...]}
```

Formalization for training:

```
<bos><start_of_turn>user
{prompt}<end_of_turn>
<start_of_turn>model
{response}<end_of_turn><eos>
```

- `{prompt}` = the rendered prompt from `dataset/prompts/`
  (`{{instruction}}` substituted with the sample instruction).
- `{response}` = `architecture` from the sample, serialized compactly.
- Prompt tokens are masked out of the loss (labels = -100 for the prompt
  prefix) — this differs from the legacy `lora_train.py`, which did not mask.

## 3. JSONL conversion

`backend/dataset/export_jsonl.py` reads `dataset/reviewed/*.json` and writes:

- `dataset/final/cybershield_arch.jsonl` (full set)
- `dataset/final/cybershield_arch_train.jsonl`
- `dataset/final/cybershield_arch_validation.jsonl`
- `dataset/final/split_manifest.json`

Each line is one record:

```json
{
  "id": "banking-hard-hardened",
  "domain": "banking",
  "difficulty": "hard",
  "instruction": "<prompt text>",
  "response": "{\"nodes\": [...], \"edges\": [...]}",
  "architecture": {...},
  "security": {...},
  "metadata": {...}
}
```

The training harness reads `instruction`/`response` and applies the chat
template at tokenization time.

## 4. LoRA configuration

| Hyperparameter | Value | Notes |
| --- | --- | --- |
| Method | LoRA (PEFT) | Adapter only; base weights frozen. |
| `r` | 16 | |
| `lora_alpha` | 32 | |
| `lora_dropout` | 0.05 | |
| `bias` | `none` | |
| Target modules | `q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj` | Gemma 3 names; matches `backend/training/gemma/lora_train.py`. |
| Task type | `CAUSAL_LM` | |

Adapter output: `checkpoints/gemma_lora/` (this is the path
`backend/core/inference.py` already probes via `LORA_ADAPTER_PATH`).

## 5. Training hyperparameters

| Hyperparameter | Value | Rationale |
| --- | --- | --- |
| Epochs | 2-3 | Small dataset; watch validation loss for overfitting. |
| Batch size | 1 | 6 GB VRAM. |
| Gradient accumulation | 8 | Effective batch 8. |
| Learning rate | 2e-4 | Standard for LoRA on 4-bit bases. |
| Optimizer | AdamW | |
| Scheduler | Linear warmup (10% steps), cosine decay | |
| Max sequence length | 512-768 | Prompt (~350 tok) + JSON response (~250-400 tok). |
| Warmup steps | 10% of total | |
| Weight decay | 0.01 | |

## 6. Expected GPU memory

| Phase | Peak VRAM (estimate) |
| --- | --- |
| Base model inference (4-bit) | ~3.1 GB (measured) |
| LoRA training (4-bit + gradient checkpointing) | ~4.2-4.6 GB |
| Validation / eval | ~3.1 GB |

RTX 4050 Laptop (6 GB) is sufficient; `gradient_checkpointing_enable()`
followed by `prepare_model_for_kbit_training()` is required.

## 7. Estimated dataset size

- Minimum viable: **500 reviewed samples** (10 domains x 50).
- Target: **1000-1500 samples** covering all 12 domains, 3 difficulty tiers,
  and both insecure/hardened variants.
- At 1000 samples the split below yields 850 train / 150 validation samples.

## 8. Train / validation split

- **Ratio**: 85% train / 15% validation (deterministic, SHA-256 of sample id
  — implemented in `export_jsonl.py --split-ratio 0.85`).
- Stratification recommendation: keep domain and difficulty balanced in each
  split when the dataset grows past 1000 samples.

## 9. Evaluation metrics

| Metric | What it measures | Instrument |
| --- | --- | --- |
| Structural validity | % outputs parse to `{nodes, edges}` with valid types/labels/references | `dataset_validator.py` checks |
| Security-score delta | Mean engine `security_score` of generated graphs | `backend/security` (production engine) |
| Missing-control recall | Fraction of required controls embedded | Engine `missing_components` |
| Risk-level distribution | LOW/MEDIUM/HIGH balance vs dataset prior | `dataset/docs/` reports |
| Graph size compliance | Nodes <= 8, edges <= 10 per prompt contract | `_validate_architecture` |
| Determinism | P(identical output for same input) | greedy decode, n=50 runs |
| Latency / VRAM | Generation time, peak memory | `torch.cuda` instrumentation |

Note: the legacy BLEU/ROUGE explanation metrics (`run_evaluation.py`) apply to
the explanation task only; architecture generation is scored with the metrics
above.

## 10. Milestones

1. Dataset reaches 500+ validated, 100% reviewed samples (data phase).
2. Split exported via `export_jsonl.py`.
3. Training harness implemented against `backend/training/gemma/lora_train.py`
   with prompt masking and the chat template (training phase, separate
   approval).
4. Adapter evaluated with the metrics in section 9 against the base model;
   manual spot-check through the app UI.
