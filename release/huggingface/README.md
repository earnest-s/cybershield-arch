---
base_model: unsloth/gemma-3-4b-it-bnb-4bit
language:
  - en
license: unknown
tags:
  - peft
  - lora
  - gemma-3
  - architecture-generation
  - json
  - experimental
datasets:
  - CyberShield_Gemma_SFT_v1
---

# CyberShield-Arch — Gemma 3 4B LoRA

**This is an experimental research/project-review model.** It is a LoRA adapter for
`unsloth/gemma-3-4b-it-bnb-4bit` that generates software architecture JSON graphs
(nodes + edges) from natural-language architecture/security requirements.

It is **not** production-ready, **not** state-of-the-art, and **does not** reproduce
canonical architectures exactly. See [Evaluation](#evaluation) and [Limitations](#limitations)
for the measured behavior.

## Model Description

- **Base model:** `unsloth/gemma-3-4b-it-bnb-4bit` (Gemma 3 4B, 4-bit NF4 quantized, frozen)
- **Adapter type:** LoRA (PEFT), causal language modeling
- **Task:** given a natural-language prompt describing a software architecture and its
  security requirements, emit a JSON object with `nodes` and `edges` (schema below)
- **Domain:** software architecture graph generation with a strict validation contract

Output contract (enforced at runtime by the project validator):

```json
{
  "nodes": [{ "id": "string", "type": "string" }],
  "edges": [{ "source": "string", "target": "string", "label": "string" }]
}
```

Limits: at most 10 nodes and 15 edges; edges must reference existing nodes; no duplicate
edges, self-loops, dangling edges, or orphan nodes; the graph must be weakly connected.

## Intended Use

- **Experimental/project-review demonstrations** of instruction-tuned LoRA training on a
  small, purpose-built dataset.
- Producing **structurally plausible** architecture drafts that a human reviews/edits in
  the ArchitectAI interactive editor.
- **Not** intended for: production planning, security-critical decisions, exact
  architecture reconstruction, or any use where fidelity to a specified canonical
  architecture matters.

## Architecture

- Base: Gemma 3 4B (4-bit NF4, `BitsAndBytesConfig`, frozen)
- PEFT LoRA applied to `model.language_model` projection/MLP matrices only:
  `q_proj | k_proj | v_proj | o_proj | gate_proj | up_proj | down_proj` (238 modules,
  language tower only — vision tower untouched)
- r = 24, alpha = 48, dropout 0.05, bias none
- Task type: `CAUSAL_LM`

## Training

- Framework: PyTorch + Transformers + PEFT + BitsAndBytes
- Optimizer: 8-bit AdamW, lr 2e-4
- Scheduler: cosine with 10% linear warmup
- Gradient accumulation: 8 micro-batches (effective batch 8)
- Loss: chunked cross-entropy (64-token chunks, mean over valid tokens), prompt-masked
  (`labels[:prompt_len] = -100`), `max_length` 1024 (no truncation; longest record 605 tokens)
- Seed: 42 (deterministic run)
- 1 epoch, 5,793 steps, 10,627,045 target tokens
- Duration: ~13.8 h; peak VRAM 3.53 GiB of ~5.66 GiB usable
- Final train loss 0.2331; final validation loss 0.1912 (monotone 0.2440 → 0.1912 across
  6 validation passes)

## Dataset

- **Source:** `dataset/training/CyberShield_Gemma_SFT_v1.jsonl`
  (SHA256 `8c91e5cd017df9490f24b5c9f016f01c871e5531b4072c7f83d6959301b851ec`, 51,498 records)
- Built from real records of `ajibawa-2023/Technical-Architectures-Large` (no synthetic
  template data) through the project's staged pipeline (download → convert → enrich →
  validate → review → export → security-engine enrichment → subgraph extraction → SFT
  formatting)
- Split: 46,348 train / 2,575 validation / 2,575 test (held out; test records never seen
  in training or tuning)

## Training Configuration

| Parameter | Value |
|---|---|
| LoRA r / alpha / dropout | 24 / 48 / 0.05 |
| Target modules | `model.language_model.*(q_proj\|k_proj\|v_proj\|o_proj\|gate_proj\|up_proj\|down_proj)` |
| Learning rate | 2e-4 (8-bit AdamW) |
| Scheduler | cosine, 10% warmup |
| Gradient accumulation | 8 |
| Epochs / steps | 1 / 5,793 |
| Seed | 42 |
| Quantization | base 4-bit NF4, bf16 compute, fp16 embeddings |

## Evaluation

Measured on the untouched 2,575-record test split (greedy decoding,
`repetition_penalty=1.1`, `max_new_tokens=768`):

| Metric | Value |
|---|---|
| Parse rate | 100% (2,575/2,575) |
| Contract-valid rate | 100% |
| Schema-valid rate | 100% |
| Connected rate | 99.96% |
| Repetition failure rate | 0% |
| Node F1 | 0.224 |
| Edge F1 | 0.065 |
| Exact architecture match | 0% |

Interpretation: the adapter learned to produce **valid architecture structures
reliably** — parseable JSON, within the node/edge contract, connected in 99.96% of cases,
with zero repetition-loop failures. Structural fidelity to the canonical target
architectures remains **limited** (node F1 0.224, edge F1 0.065, exact match 0%):
generated graphs are plausible and well-formed but their component inventory only
partially matches the expected target. Reported numbers are exact; do not reinterpret.

## Limitations

- **Low structural fidelity**: node F1 0.224, edge F1 0.065, exact match 0% — do not
  rely on it to reproduce a specified architecture.
- Validator-clean output does not imply semantically correct architecture.
- 0.04% of test outputs are disconnected (covered at runtime by the project's
  parse/validate retry loop).
- Trained on a small purpose-built dataset (51,498 records); domain coverage is narrow.
- One epoch of LoRA training on a 4-bit 4B base; 44.7 M trainable parameters.
- Experimental/research quality. Not audited for any safety-critical or production use.

## Inference

Requirements: Python, `transformers`, `peft`, `bitsandbytes`, `accelerate`, CUDA-capable GPU.

```python
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

base_id = "unsloth/gemma-3-4b-it-bnb-4bit"
adapter = "path/to/release/huggingface"

tokenizer = AutoTokenizer.from_pretrained(base_id)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                         bnb_4bit_compute_dtype=torch.float16)
model = AutoModelForCausalLM.from_pretrained(base_id, device_map="auto",
                                             quantization_config=bnb)
model = PeftModel.from_pretrained(model, adapter)
model.eval()

prompt = tokenizer.apply_chat_template([
    {"role": "system", "content": "You are a strict JSON generator for software architecture graphs."},
    {"role": "user", "content": "A frontend calls an API that writes to postgres."},
], tokenize=False, add_generation_prompt=True)
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
out = model.generate(**inputs, do_sample=False, repetition_penalty=1.1,
                     max_new_tokens=768)
print(tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True))
```

## Hardware

- Training: single NVIDIA RTX 4050 Laptop GPU, ~5.66 GiB usable VRAM (peak 3.53 GiB)
- Base model loaded 4-bit (NF4) with bf16 compute

## Reproducibility

- Deterministic training run: seed 42, fixed split, frozen base model, no data
  augmentation, no re-sampling
- Training/eval harness: `backend/training/gemma/lora_train.py`,
  `phase8_generate_eval.py`, `phase8_quality_gates.py`
- Full reports: `dataset/docs/phase8_training_config.md`,
  `phase8_training_tuning_report.md`, `phase8_full_training_report.md`,
  `phase8_final_evaluation.md`
- Evaluation numbers above are reproducible from `dataset/docs/phase8_final_test_eval.json`

## Citation / Project Information

Part of the **ArchitectAI / CyberShield-Arch** project: a local-first architecture
generation and editing workspace (FastAPI + React/React Flow) with a staged dataset
pipeline and a production security engine used as the label source for training data.
See the project repository for the full pipeline: natural-language architecture/security
requirements → Gemma 3 4B LoRA → architecture JSON → validation/runtime contract →
security analysis → threat visualization/rendering.

No license has been established for this adapter in this repository. The base model
`unsloth/gemma-3-4b-it-bnb-4bit` is subject to its own upstream terms (Google Gemma
license); the training data is derived from `ajibawa-2023/Technical-Architectures-Large`
(see that dataset's terms).
