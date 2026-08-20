# ArchitectAI

ArchitectAI is a local-first architecture generation and editing workspace.

It combines:
- A FastAPI backend that runs local model inference and returns architecture JSON.
- A React + React Flow frontend that renders, edits, styles, and exports diagrams.

## What It Does

- Generates architecture graphs from plain-language prompts.
- Validates and normalizes model output into safe graph structures.
- Opens results in an interactive editor with:
	- node and edge editing
	- drag-and-drop node creation
	- theme toggle (light/dark)
	- PNG export
	- local persistence for prompt + latest architecture

## Tech Stack

- Backend: FastAPI, PyTorch, Transformers, PEFT (LoRA), BitsAndBytes
- Frontend: React 18, TypeScript, Vite 5, React Flow

## Project Structure

```text
backend/
	api/main.py            # FastAPI app and endpoints
	core/inference.py      # Model loading, inference, output validation
frontend/
	src/App.tsx            # Prompt UI, API call, persisted app state
	src/components/        # Diagram editor and interaction logic
	src/index.css          # Theme and editor styling
requirements.txt         # Python dependencies
```

## Prerequisites

- Linux with NVIDIA GPU + CUDA available to PyTorch
- Python 3.10+
- Node.js 18+ and npm

The backend is GPU-only and fails fast if CUDA is unavailable.

## Quick Start

### 1. Set up Python environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional (recommended) local cache paths:

```bash
export HF_HOME=./.cache/huggingface
export TRANSFORMERS_CACHE=./.cache/huggingface
export TORCH_HOME=./.cache/torch
```

### 2. Start backend

From project root:

```bash
uvicorn backend.api.main:app --host 127.0.0.1 --port 8000
```

Model initialization occurs at startup (`preload_model` + smoke test).

### 3. Start frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

## URLs

- Frontend: http://localhost:5173
- Backend: http://127.0.0.1:8000

## Dataset Pipeline

Training data is built from `ajibawa-2023/Technical-Architectures-Large`
(real records only — no synthetic/template data) through the staged pipeline in
`dataset/scripts/` (download -> convert -> enrich -> validate -> review -> export),
with the production security engine as the label source.

- See `dataset/README.md` for the run order and the frozen validation policy.
- Reports: `dataset/docs/validation_policy_analysis.md`, `dataset/docs/pilot_report.md`,
  `dataset/docs/pilot_report_v2.md`, `dataset/docs/full_scale_report.md`.
- Bulk pipeline artifacts (staging directories, raw snapshot, full-scale exports)
  are git-ignored; see `.gitignore`.

## Trained Model

ArchitectAI ships with a trained LoRA adapter for **Gemma 3 4B**:

- Base model: `unsloth/gemma-3-4b-it-bnb-4bit` (4-bit NF4, frozen)
- Adapter: `checkpoints/gemma_lora` (LoRA r=24, alpha=48, 44.7 M trainable parameters)
- Model name: **CyberShield-Arch — Gemma 3 4B LoRA** (experimental research/project-review model)

Pipeline:

```
Natural-language architecture/security requirements
→ Gemma 3 4B LoRA
→ architecture JSON (nodes + edges)
→ validation/runtime contract (parser + validator, retry loop, ≤10 nodes / ≤15 edges)
→ security analysis (production security engine)
→ threat visualization/rendering (React Flow editor, PNG export)
```

The runtime loading path is `backend/core/inference.py`: base model in 4-bit (NF4, bf16
compute), LoRA adapter applied via PEFT, greedy decoding with `repetition_penalty=1.1`,
`max_new_tokens=768`. The model is loaded once at backend startup and used by
`POST /explain`.

## Training

The adapter was trained on the Phase 7 SFT artifact
(`dataset/training/CyberShield_Gemma_SFT_v1.jsonl`, SHA256
`8c91e5cd017df9490f24b5c9f016f01c871e5531b4072c7f83d6959301b851ec`), derived from real
records of `ajibawa-2023/Technical-Architectures-Large` through the staged dataset
pipeline, with the production security engine as the label source.

- Split: 46,348 train / 2,575 validation / 2,575 test (test records never seen during
  training or tuning)
- 1 epoch, 5,793 steps, 10,627,045 target tokens; seed 42
- LoRA r=24, alpha=48, dropout 0.05, language tower only (238 modules)
- 8-bit AdamW, lr 2e-4, cosine schedule with 10% warmup, gradient accumulation 8
- Chunked cross-entropy (64-token chunks), prompt masking, `max_length` 1024
- Duration ~13.8 h on a single NVIDIA RTX 4050 Laptop GPU (~5.66 GiB usable VRAM,
  peak 3.53 GiB)
- Final train loss **0.2331**; final validation loss **0.1912**

Training harness and Phase 8 reports: `backend/training/gemma/` and
`dataset/docs/phase8_*.md`.

## Evaluation

Measured on the untouched 2,575-record test split (greedy, `repetition_penalty=1.1`):

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

The model learned to produce **valid architecture structures reliably**, while
**structural fidelity to the canonical target remains limited** (node F1 0.224, edge F1
0.065, exact match 0%). Do not rely on it to reproduce a specified architecture.
See `dataset/docs/phase8_final_evaluation.md` for the full breakdown.

## Hugging Face

A release package for the trained adapter is prepared at `release/huggingface/`
(adapter weights + `adapter_config.json` + model card).

Hugging Face model: <https://huggingface.co/earnest-s/CyberShield-Gemma-4B>

## Limitations

- Experimental research/project-review model — **not production-ready**, not
  state-of-the-art.
- Low structural fidelity: node F1 0.224, edge F1 0.065, exact match 0% — generated
  graphs are valid and plausible but only partially match the expected canonical
  inventory.
- Validator-clean output does not imply a semantically correct architecture.
- 0.04% of test outputs are disconnected (covered by the runtime retry loop).
- Trained on a small purpose-built dataset; domain coverage is narrow.

## Backend API

### `GET /healthz`
Returns service health.

Example response:

```json
{ "status": "ok" }
```

### `POST /explain`
Generates an architecture graph from input text.

Request body:

```json
{ "text": "A frontend calls an API that writes to postgres and publishes jobs." }
```

Successful response shape:

```json
{
	"architecture": {
		"nodes": [{ "id": "frontend", "type": "ui" }],
		"edges": [{ "source": "frontend", "target": "api", "label": "HTTP" }]
	},
	"raw_model_output": "..."
}
```

## Frontend Behavior Notes

- The app calls `http://127.0.0.1:8000/explain`.
- Prompt input and the latest generated architecture are saved in localStorage.
- Theme preference is saved in localStorage.
- PNG export captures the React Flow viewport.

## Troubleshooting

- Backend startup fails with GPU/CUDA errors:
	- Verify CUDA visibility and PyTorch GPU support.
	- Confirm your model checkpoint path exists: `checkpoints/gemma_lora`.

- Frontend cannot reach backend:
	- Ensure backend runs on `127.0.0.1:8000`.
	- Check browser network errors for `/explain`.

- PNG export warns about remote stylesheet access:
	- This is commonly caused by cross-origin CSS/font rules in the browser.
	- Current export logic avoids inlining remote font CSS.

- Chrome console shows message channel/extension runtime errors:
	- These are often browser extension-originated, not app runtime faults.

## Development Commands

From `frontend/`:

```bash
npm run dev
npm run build
npm run preview
```

From project root:

```bash
uvicorn backend.api.main:app --host 127.0.0.1 --port 8000
```
