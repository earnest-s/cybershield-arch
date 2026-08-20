#!/usr/bin/env python3
import json
import os
import time
from pathlib import Path

# Set HF_HOME before importing transformers: huggingface_hub freezes the cache
# path at import time, so setting it later inside _load_model_once is too late
# and causes "does not appear to have a file named ..." startup failures when
# the env var is not already exported. Use an absolute, CWD-independent path.
_HF_CACHE_DIR = Path(__file__).resolve().parents[2] / ".cache" / "huggingface"
_HF_HUB_DIR = _HF_CACHE_DIR / "hub"
os.environ.setdefault("HF_HOME", str(_HF_CACHE_DIR))

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from backend.core.architecture_parser import (
    extract_json_object_comments,
    parse_architecture,
)
from backend.core.architecture_validator import is_structurally_weak, raise_if_invalid

_MODEL = None
_TOKENIZER = None
_MODEL_DEVICE = None


def _tokenize_prompt(prompt: str) -> object:
    try:
        chat_prompt = _TOKENIZER.apply_chat_template(
            [
                {
                    "role": "system",
                    "content": "You are a strict JSON generator for software architecture graphs.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            tokenize=False,
            add_generation_prompt=True,
        )
        return _TOKENIZER(chat_prompt, return_tensors="pt").to(_MODEL_DEVICE)
    except Exception:  # noqa: BLE001
        return _TOKENIZER(prompt, return_tensors="pt").to(_MODEL_DEVICE)


def _load_model_once() -> None:
    global _MODEL, _TOKENIZER, _MODEL_DEVICE

    if _MODEL is not None and _TOKENIZER is not None and _MODEL_DEVICE is not None:
        return

    if not torch.cuda.is_available():
        raise RuntimeError("GPU is required for inference")

    model_id = os.getenv("MODEL_ID", "unsloth/gemma-3-4b-it-bnb-4bit")
    adapter_path = Path(os.getenv("LORA_ADAPTER_PATH", "checkpoints/gemma_lora"))

    print("Loading tokenizer...")
    _TOKENIZER = AutoTokenizer.from_pretrained(
        model_id, local_files_only=True, cache_dir=_HF_HUB_DIR
    )
    if _TOKENIZER.pad_token is None:
        _TOKENIZER.pad_token = _TOKENIZER.eos_token

    print("Loading base model in 4-bit...")
    bnb_cfg = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )

    base_model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        quantization_config=bnb_cfg,
        local_files_only=True,
        cache_dir=_HF_HUB_DIR,
    )

    if adapter_path.exists():
        print("Loading LoRA adapter...")
        _MODEL = PeftModel.from_pretrained(base_model, adapter_path)
    else:
        print(f"LoRA adapter not found at {adapter_path}; using base Gemma model")
        _MODEL = base_model
    _MODEL.eval()

    adapter_config = getattr(_MODEL, "peft_config", None)
    adapter_names = list(adapter_config.keys()) if adapter_config else []
    if adapter_names:
        print(f"LoRA adapters loaded: {adapter_names}")

    _MODEL_DEVICE = next(_MODEL.parameters()).device
    print("CUDA AVAILABLE:", torch.cuda.is_available())
    print("MODEL DEVICE:", _MODEL_DEVICE)
    print("GPU NAME:", torch.cuda.get_device_name(0))
    if "cuda" not in str(_MODEL_DEVICE):
        raise RuntimeError("Model is NOT using GPU")


def preload_model() -> None:
    _load_model_once()


def run_startup_smoke_test() -> None:
    _load_model_once()
    prompt = "Return exactly this JSON and nothing else: {\"status\":\"ready\"}"
    inputs = _TOKENIZER(prompt, return_tensors="pt").to(_MODEL_DEVICE)
    with torch.inference_mode():
        outputs = _MODEL.generate(
            **inputs,
            max_new_tokens=40,
            do_sample=False,
            eos_token_id=_TOKENIZER.eos_token_id,
            pad_token_id=_TOKENIZER.eos_token_id,
        )
    input_len = inputs.input_ids.shape[1]
    generated_ids = outputs[:, input_len:]
    smoke = _TOKENIZER.decode(generated_ids[0], skip_special_tokens=True).strip()
    if not smoke:
        raise RuntimeError("Startup smoke inference returned empty output")


def generate_architecture(text: str, deterministic: bool = False) -> tuple[dict, str]:
    _load_model_once()
    clean_text = text.strip()
    if not clean_text:
        raise ValueError("Input text is required")
    print("INPUT:", clean_text)
    print("RUNNING REAL MODEL")

    prompt = f"""
You are a senior software architect.

Convert the following system description into a CLEAN architecture graph.

RULES:
- Use only meaningful components
- No duplicate edges
- No redundant connections
- Keep architecture minimal and logical

FORMAT:
{{
    "nodes": [
        {{"id": "frontend", "type": "ui"}},
        {{"id": "api", "type": "service"}}
    ],
    "edges": [
        {{"source": "frontend", "target": "api", "label": "HTTP"}}
    ]
}}

CONSTRAINTS:
- Each edge must be unique
- Do NOT repeat same connection
- Use proper labels: HTTP, DB Query, Async, Cache
- Max nodes: 8
- Max edges: 10

Description:
{clean_text}

ONLY return JSON. No explanation.
"""

    stricter_prompt = prompt + "\nGenerate a connected architecture graph. All nodes must be part of a valid flow."

    attempts = 1 if deterministic else 3
    last_error = ""
    last_result = ""
    started_at = time.perf_counter()

    def _run_attempts(prompt_text: str, attempt_count: int) -> tuple[dict, str] | None:
        nonlocal last_error, last_result
        for attempt in range(1, attempt_count + 1):
            inputs = _tokenize_prompt(prompt_text)
            generation_kwargs = {
                "max_new_tokens": 512,
                "do_sample": not deterministic,
                "eos_token_id": _TOKENIZER.eos_token_id,
                "pad_token_id": _TOKENIZER.eos_token_id,
            }
            if not deterministic:
                generation_kwargs.update({"temperature": 0.3, "top_p": 0.9})

            with torch.inference_mode():
                outputs = _MODEL.generate(**inputs, **generation_kwargs)

            input_len = inputs.input_ids.shape[1]
            generated_ids = outputs[:, input_len:]
            result = _TOKENIZER.decode(generated_ids[0], skip_special_tokens=True).strip()
            last_result = result
            print(f"RAW MODEL OUTPUT [attempt {attempt}/{attempt_count}]:", result[:500])

            try:
                raw_json = extract_json_object_comments(result)
                architecture = parse_architecture(raw_json)
                raise_if_invalid(architecture)
                if is_structurally_weak(architecture):
                    raise ValueError("Generated graph is structurally weak")

                elapsed_ms = int((time.perf_counter() - started_at) * 1000)
                print("INFERENCE TIME MS:", elapsed_ms)
                print("NODE COUNT:", len(architecture["nodes"]))
                print("EDGE COUNT:", len(architecture["edges"]))
                print("OUTPUT LENGTH:", len(result))
                print("GPU MEMORY:", torch.cuda.memory_allocated() / 1024**2, "MB")
                return architecture, result
            except ValueError as exc:
                last_error = str(exc)
                continue
        return None

    primary_result = _run_attempts(prompt, attempts)
    if primary_result is not None:
        return primary_result

    connected_result = _run_attempts(stricter_prompt, 1)
    if connected_result is not None:
        return connected_result

    raise ValueError(f"Architecture generation failed after {attempts + 1} attempts: {last_error}. Last output: {last_result[:300]}")


def generate_explanation(architecture: dict) -> str:
    """Explain an architecture using the same prompt format as LoRA training
    and evaluation, so a fine-tuned adapter at checkpoints/gemma_lora applies
    consistently. Uses plain tokenization to match the training script."""
    _load_model_once()
    if not isinstance(architecture, dict):
        raise ValueError("architecture must be a dict")

    prompt = (
        "You are an AI architecture assistant. Explain clearly using exactly these sections:\n"
        "Components:\n"
        "Data flow:\n"
        "Architecture type:\n"
        f"Architecture JSON: {json.dumps(architecture, ensure_ascii=True)}\n"
        "Explanation:"
    )

    inputs = _TOKENIZER(prompt, return_tensors="pt").to(_MODEL_DEVICE)
    with torch.inference_mode():
        outputs = _MODEL.generate(
            **inputs,
            max_new_tokens=150,
            do_sample=False,
            eos_token_id=_TOKENIZER.eos_token_id,
            pad_token_id=_TOKENIZER.eos_token_id,
        )

    input_len = inputs.input_ids.shape[1]
    generated_ids = outputs[:, input_len:]
    result = _TOKENIZER.decode(generated_ids[0], skip_special_tokens=True).strip()
    for prefix in ("Explanation:", "Answer:"):
        if result.startswith(prefix):
            result = result[len(prefix):].strip()
    return result
