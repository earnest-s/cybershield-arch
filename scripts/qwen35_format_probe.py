"""Qwen3.5-4B response-format probe (isolated; no training, no production edits).

Conditions:
  A - current benchmark configuration (baseline prompt, sampling)
  B - explicit non-thinking mode (recorded as unsupported by current stack)
  C - concise JSON-only instruction (prompt-shape hypothesis)
  D - schema-shaped constrained decoding via a LogitsProcessor (decode hypothesis)
"""

from __future__ import annotations

import copy
import json
import os
import sys
import time
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["HF_HOME"] = str(ROOT / ".cache" / "huggingface")

from benchmark_qwen35 import (  # noqa: E402
    SYSTEM_PROMPT as BASE_SYSTEM,
    PROMPT_TEMPLATE,
    extract_architecture,
    validate_graph,
    audit_tech,
    load_model,
)

MAX_NEW_TOKENS = 2048
TEMPERATURE = 0.3
TOP_P = 0.9
TOP_K = 128
OUT_DIR = ROOT / "dataset" / "docs"

PROBE_PROMPTS = [
    {
        "probe_id": "P1",
        "description": (
            "A collaboration platform: customers open a React single-page "
            "application that talks to a FastAPI backend, which reads and "
            "writes customer data in a PostgreSQL database."
        ),
        "expected_tech": {"React", "FastAPI", "PostgreSQL"},
    },
    {
        "probe_id": "P2",
        "description": (
            "A multi-tier web application: a React frontend talks to a FastAPI "
            "service; the service persists customer data in PostgreSQL, uses "
            "Redis for session caching, and publishes background jobs to a "
            "RabbitMQ queue consumed by a worker service."
        ),
        "expected_tech": {"React", "FastAPI", "PostgreSQL", "Redis", "RabbitMQ"},
    },
    {
        "probe_id": "P3",
        "description": (
            "An AWS-based image upload pipeline: clients upload images to an S3 "
            "bucket, an SQS queue delivers upload events to a processing "
            "service, and a PostgreSQL (RDS) database stores image metadata."
        ),
        "expected_tech": {"AWS", "S3", "SQS", "PostgreSQL", "RDS"},
    },
]

C_SYSTEM = (
    "You output a single JSON object only. No analysis, no reasoning, "
    "no explanation, no markdown."
)
C_USER = (
    "Architecture graph as JSON. "
    'Schema: {"nodes":[{"id":"ui-1","type":"ui","technology":null}],'
    '"edges":[{"source":"ui-1","target":"service-1","protocol":null}]}. '
    "Types: ui, service, database, cache, queue, container. "
    "technology = the exact name if the text names it, else null. "
    "protocol = HTTPS, SQL, Redis Protocol or message, else null. "
    "Max 10 nodes, max 15 edges.\n\n"
    "Text:\n{description}\n\n"
    "JSON only."
)

CONDITIONS = {
    "A": {
        "name": "current configuration",
        "supported": True,
        "system": BASE_SYSTEM,
        "user": lambda d: PROMPT_TEMPLATE.format(description=d),
        "constraint": False,
        "notes": "Identical prompt + sampling to scripts/benchmark_qwen35.py.",
    },
    "B": {
        "name": "explicit non-thinking mode",
        "supported": False,
        "reason": (
            "Qwen3.5-4B (model_type qwen3_5) in transformers 5.14.1 has no "
            "thinking-mode configuration: no thinking special tokens, no "
            "enable_thinking generation flag, no generation_config.json on the "
            "model repo, and no reasoning handling in modeling_qwen3_5.py. "
            "'Thinking Process:' is free-form emitted text, not gated decoding. "
            "No explicit non-thinking toggle exists to test."
        ),
    },
    "C": {
        "name": "non-thinking + concise JSON-only instruction",
        "supported": True,
        "system": C_SYSTEM,
        "user": lambda d: C_USER.format(description=d),
        "constraint": False,
        "notes": "Prompt-shape hypothesis: short direct-answer instruction.",
    },
    "D": {
        "name": "schema-shaped constrained JSON decoding",
        "supported": True,
        "system": BASE_SYSTEM,
        "user": lambda d: PROMPT_TEMPLATE.format(description=d),
        "constraint": True,
        "notes": (
            "Baseline prompt + JsonSchemaConstrainedLogitsProcessor: token 1 "
            "must start JSON; decode forced to structural JSON with top-level "
            "keys exactly nodes then edges; object keys restricted to the "
            "schema vocabulary; EOS allowed only when complete. Same sampling "
            "params and same 2048 cap as A/C."
        ),
    },
}


class JsonSchemaFSM:
    """Incremental JSON-prefix state machine with schema-shaped key limits."""

    TOP_KEYS = ("nodes", "edges")
    SUB_KEYS = ("id", "type", "technology", "source", "target", "protocol")
    LITERALS = ("true", "false", "null")

    def __init__(self) -> None:
        self.stack: list[dict] = [
            {"kind": "obj", "phase": "before", "top": True, "seen": []}
        ]
        self.mode = "frame"
        self.started = False
        self.str_ctx: str | None = None
        self.key_buf = ""
        self.lit_buf = ""
        self.num_buf = ""
        self.esc = False
        self.hex_left = 0
        self.done = False

    def clone(self) -> "JsonSchemaFSM":
        return copy.deepcopy(self)

    def _allowed_keys(self, frame: dict) -> tuple[str, ...]:
        if frame["top"]:
            seen = frame["seen"]
            if "nodes" not in seen:
                return ("nodes",)
            if "edges" not in seen:
                return ("edges",)
            return ()
        return self.SUB_KEYS

    def _finish_value(self) -> None:
        frame = self.stack[-1]
        frame["phase"] = "after" if frame["kind"] == "arr" else "after_val"

    def _close_frame(self) -> bool:
        self.stack.pop()
        if not self.stack:
            self.done = True
            self.mode = "frame"
            return True
        top = self.stack[-1]
        top["phase"] = "after" if top["kind"] == "arr" else "after_val"
        self.mode = "frame"
        return True

    def _step(self, ch: str) -> bool:
        if self.done:
            return ch in " \t\n\r"

        if not self.started:
            if ch == "{":
                self.started = True
                return True
            return False

        if self.mode == "str":
            if self.str_ctx == "key":
                if self.esc:
                    return False
                if ch == "\\":
                    return False
                if ch == '"':
                    allowed = self._allowed_keys(self.stack[-1])
                    if self.key_buf not in allowed:
                        return False
                    if self.stack[-1]["top"] and self.key_buf not in self.stack[-1]["seen"]:
                        self.stack[-1]["seen"].append(self.key_buf)
                    self.stack[-1]["phase"] = "after_key"
                    self.mode = "frame"
                    self.str_ctx = None
                    return True
                if ch in "\t\n\r":
                    return False
                self.key_buf += ch
                return any(
                    k.startswith(self.key_buf)
                    for k in self._allowed_keys(self.stack[-1])
                )
            else:
                if self.hex_left > 0:
                    if ch not in "0123456789abcdefABCDEF":
                        return False
                    self.hex_left -= 1
                    if self.hex_left == 0:
                        self.mode = "frame"
                        self._finish_value()
                    return True
                if self.esc:
                    if ch == "u":
                        self.hex_left = 4
                        self.esc = False
                        return True
                    if ch in '"\\/bfnrt':
                        self.esc = False
                        return True
                    return False
                if ch == "\\":
                    self.esc = True
                    return True
                if ch == '"':
                    self.mode = "frame"
                    self._finish_value()
                    return True
                if ord(ch) < 0x20:
                    return False
                return True

        if self.mode == "lit":
            self.lit_buf += ch
            if not any(l.startswith(self.lit_buf) for l in self.LITERALS):
                return False
            if self.lit_buf in self.LITERALS:
                self.mode = "frame"
                self._finish_value()
            return True

        if self.mode == "num":
            if ch in " \t\n\r,]}":
                if not _number_complete(self.num_buf):
                    return False
                self.mode = "frame"
                self._finish_value()
                return self._step(ch)
            self.num_buf += ch
            return _number_prefix(self.num_buf)

        if ch in " \t\n\r":
            return True

        frame = self.stack[-1]
        if frame["kind"] == "obj":
            if frame["phase"] == "before":
                if ch == "}":
                    if frame["top"]:
                        return False
                    return self._close_frame()
                if ch != '"':
                    return False
                self.mode = "str"
                self.str_ctx = "key"
                self.key_buf = ""
                return True
            if frame["phase"] == "after_key":
                if ch != ":":
                    return False
                frame["phase"] = "val"
                return True
            if frame["phase"] == "val":
                return self._value_start(ch)
            if frame["phase"] == "after_val":
                if ch == ",":
                    if frame["top"] and "edges" in frame["seen"]:
                        return False
                    frame["phase"] = "before"
                    return True
                if ch == "}":
                    if frame["top"]:
                        if frame["seen"] != ["nodes", "edges"]:
                            return False
                    return self._close_frame()
                return False
        else:
            if frame["phase"] == "before":
                if ch == "]":
                    return self._close_frame()
                return self._value_start(ch)
            if frame["phase"] == "after":
                if ch == ",":
                    frame["phase"] = "before"
                    return True
                if ch == "]":
                    return self._close_frame()
                return False
        return False

    def _value_start(self, ch: str) -> bool:
        if ch == "{":
            self.stack.append(
                {"kind": "obj", "phase": "before", "top": False, "seen": []}
            )
            self.mode = "frame"
            return True
        if ch == "[":
            self.stack.append(
                {"kind": "arr", "phase": "before", "top": False, "seen": []}
            )
            self.mode = "frame"
            return True
        if ch == '"':
            self.mode = "str"
            self.str_ctx = "val"
            self.esc = False
            self.hex_left = 0
            return True
        if ch in "tfn":
            self.mode = "lit"
            self.lit_buf = ch
            return any(l.startswith(self.lit_buf) for l in self.LITERALS)
        if ch == "-" or ch.isdigit():
            self.mode = "num"
            self.num_buf = ch
            return True
        return False

    def feed(self, text: str) -> bool:
        for ch in text:
            if not self._step(ch):
                return False
        return True


def _number_prefix(buf: str) -> bool:
    import re

    return bool(re.match(r"^-?(0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?$|^-$|^\.$", buf)) or bool(
        re.match(r"^-?(\d+)?(\.\d*)?([eE][+-]?\d*)?$", buf)
    )


def _number_complete(buf: str) -> bool:
    import re

    return bool(re.fullmatch(r"-?(0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?", buf))


class JsonSchemaConstrainedLogitsProcessor:
    """Forces schema-shaped JSON decoding (structural + key vocabulary)."""

    def __init__(self, tokenizer, top_k: int = TOP_K):
        self.tokenizer = tokenizer
        self.top_k = top_k
        self.prompt_len = 0
        self._state = JsonSchemaFSM()
        self._cached_gen: list[int] = []
        self.fallback_count = 0
        self.degraded = False
        self._vocab_cache: dict[int, str] = {}

    def vocab_text(self, tid: int) -> str:
        if tid not in self._vocab_cache:
            self._vocab_cache[tid] = self.tokenizer.decode([tid])
        return self._vocab_cache[tid]

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor):
        gen = input_ids[0, self.prompt_len :].tolist()
        if gen != self._cached_gen:
            state = JsonSchemaFSM()
            for tid in gen:
                if not state.feed(self.vocab_text(tid)):
                    self.degraded = True
                    return scores
            self._state = state
            self._cached_gen = gen
        st = self._state
        if st.done:
            eos_id = self.tokenizer.eos_token_id
            mask = torch.full_like(scores[0], float("-inf"))
            if eos_id is not None:
                mask[eos_id] = scores[0, eos_id]
            scores[0] = mask
            return scores
        k = min(self.top_k, scores.shape[-1])
        top = torch.topk(scores[0], k)
        allowed: list[int] = []
        for idx in top.indices.tolist():
            text = self.vocab_text(idx)
            if not text:
                continue
            if st.clone().feed(text):
                allowed.append(idx)
        if not allowed:
            allowed = [top.indices[0].item()]
            self.fallback_count += 1
        mask = torch.full_like(scores[0], float("-inf"))
        idx_t = torch.tensor(allowed, device=scores.device)
        mask[idx_t] = scores[0][idx_t]
        scores[0] = mask
        return scores


def run_condition(model, tokenizer, cond: dict, prompt: dict, run: int) -> dict:
    desc = prompt["description"]
    chat = [
        {"role": "system", "content": cond["system"]},
        {"role": "user", "content": cond["user"](desc)},
    ]
    text = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(next(model.parameters()).device)
    prompt_len = inputs.input_ids.shape[1]

    processor = None
    logits_processors = None
    if cond.get("constraint"):
        processor = JsonSchemaConstrainedLogitsProcessor(tokenizer)
        processor.prompt_len = prompt_len
        logits_processors = [processor]

    gen_kwargs = dict(
        max_new_tokens=MAX_NEW_TOKENS,
        do_sample=True,
        temperature=TEMPERATURE,
        top_p=TOP_P,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id,
    )
    if logits_processors is not None:
        gen_kwargs["logits_processor"] = logits_processors

    torch.cuda.reset_peak_memory_stats()
    t0 = time.time()
    with torch.inference_mode():
        outputs = model.generate(**inputs, **gen_kwargs)
    latency = time.time() - t0
    peak_mb = torch.cuda.max_memory_allocated() / 1024**2

    generated = outputs[0][prompt_len:]
    raw = tokenizer.decode(generated, skip_special_tokens=True).strip()
    out_tokens = int(generated.shape[0])

    graph, selection = extract_architecture(raw)
    if graph is not None:
        span = selection["span_offset"]
        candidate_raw = raw[span["start"] : span["end"]]
    else:
        candidate_raw = None
    validation = (
        validate_graph(graph)
        if graph is not None
        else {
            "valid": False,
            "reason": "no JSON extracted",
            "node_ids": [],
            "types": [],
            "technologies": [],
            "protocols": [],
            "issues": [],
        }
    )
    audit = audit_tech(validation.get("technologies", []), prompt["expected_tech"])
    emitted = graph is not None
    valid = bool(validation.get("valid", False))
    record = {
        "probe_id": prompt["probe_id"],
        "condition": None,
        "run": run,
        "emitted": emitted,
        "valid": valid,
        "node_count": len(validation.get("node_ids", [])),
        "edge_count": len(validation.get("protocols", [])),
        "technologies": audit.get("present_tech", []),
        "missing_expected_tech": audit.get("missing_expected_tech", []),
        "fabricated_tech": audit.get("fabricated_tech", []),
        "tech_correct": emitted and not audit.get("missing_expected_tech", []) and not audit.get("fabricated_tech", []),
        "protocol_count": len(validation.get("protocols", [])),
        "latency_s": round(latency, 3),
        "tokens_per_sec": round(out_tokens / latency, 2) if latency else None,
        "output_tokens": out_tokens,
        "peak_vram_mb": round(peak_mb, 1),
        "issues": validation.get("issues", []),
        "selection": selection,
        "constraint": {
            "active": bool(cond.get("constraint")),
            "fallback_count": processor.fallback_count if processor else 0,
            "degraded": processor.degraded if processor else False,
        },
        "raw_output": raw,
        "candidate_raw": candidate_raw,
        "selected_json": graph,
    }
    return record


def summarize(records: list[dict]) -> dict:
    if not records:
        return {}
    n = len(records)
    emitted = [r for r in records if r["emitted"]]
    valid = [r for r in records if r["valid"]]
    fabricated_runs = [r for r in records if r["fabricated_tech"]]
    tech_correct_runs = [r for r in records if r["tech_correct"]]
    return {
        "runs": n,
        "emission_rate": f"{len(emitted)}/{n}",
        "validity_rate": f"{len(valid)}/{n}",
        "tech_correct_rate": f"{len(tech_correct_runs)}/{n}",
        "fabricated_run_rate": f"{len(fabricated_runs)}/{n}",
        "avg_nodes": round(sum(r["node_count"] for r in emitted) / max(1, len(emitted)), 2),
        "avg_edges": round(sum(r["edge_count"] for r in emitted) / max(1, len(emitted)), 2),
        "avg_latency_s": round(sum(r["latency_s"] for r in records) / n, 2),
        "avg_tokens_per_sec": round(
            sum(r["tokens_per_sec"] or 0 for r in records) / n, 2
        ),
        "avg_output_tokens": round(sum(r["output_tokens"] for r in records) / n, 1),
        "peak_vram_mb": round(max(r["peak_vram_mb"] for r in records), 1),
        "fabricated_tech_all": sorted({t for r in records for t in r["fabricated_tech"]}),
        "missing_tech_all": sorted({t for r in records for t in r["missing_expected_tech"]}),
    }


def main() -> None:
    print("Loading model...", flush=True)
    model, tokenizer = load_model()
    all_records: list[dict] = []

    for cond_id in ("A", "B", "C", "D"):
        cond = CONDITIONS[cond_id]
        print(f"\n=== CONDITION {cond_id}: {cond['name']} ===", flush=True)
        if not cond["supported"]:
            print("  unsupported:", cond.get("reason", ""), flush=True)
            continue
        for prompt in PROBE_PROMPTS:
            print(f"  {prompt['probe_id']}:", flush=True)
            for run in range(1, 4):
                rec = run_condition(model, tokenizer, cond, prompt, run)
                rec["condition"] = cond_id
                all_records.append(rec)
                print(
                    f"    run {run}: emitted={rec['emitted']} valid={rec['valid']} "
                    f"tech={rec['technologies']} fab={rec['fabricated_tech']} "
                    f"nodes={rec['node_count']} edges={rec['edge_count']} "
                    f"{rec['latency_s']}s {rec['tokens_per_sec']}tok/s "
                    f"out_tok={rec['output_tokens']} vram={rec['peak_vram_mb']}MB",
                    flush=True,
                )
                out = OUT_DIR / "qwen35_format_probe.json"
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(
                    json.dumps(
                        {
                            "meta": {
                                "model": "Qwen/Qwen3.5-4B",
                                "revision": "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a",
                                "max_new_tokens": MAX_NEW_TOKENS,
                                "temperature": TEMPERATURE,
                                "top_p": TOP_P,
                                "top_k_constraint": TOP_K,
                                "runs_per_condition_prompt": 3,
                                "gpu": torch.cuda.get_device_name(0),
                            },
                            "conditions": {
                                k: {kk: vv for kk, vv in v.items() if kk != "user"}
                                for k, v in CONDITIONS.items()
                            },
                            "prompts": [
                                {k: v for k, v in p.items() if k != "description"}
                                | {"description": p["description"]}
                                for p in PROBE_PROMPTS
                            ],
                            "runs": all_records,
                            "summary_by_condition": {
                                cid: summarize(
                                    [r for r in all_records if r["condition"] == cid]
                                )
                                for cid in ("A", "C", "D")
                                if any(r["condition"] == cid for r in all_records)
                            },
                        },
                        indent=2,
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )

    print("\nWrote dataset/docs/qwen35_format_probe.json", flush=True)


if __name__ == "__main__":
    main()
