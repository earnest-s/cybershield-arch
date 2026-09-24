"""Qwen3.5-4B zero-shot benchmark (experimental, v3-oriented schema).

Isolated runner: does NOT load or modify the production Gemma path. Loads
Qwen/Qwen3.5-4B in 4-bit via the project cache, runs 10 prompts (8 positive,
2 negative/ambiguity) x 3, and evaluates against a v3-oriented schema
(canonical ids, nullable technology, protocol edges).
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ["HF_HOME"] = str(ROOT / ".cache" / "huggingface")
os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "0")

from backend.core.architecture_schema import (  # noqa: E402
    ALLOWED_NODE_TYPES,
    MAX_EDGES,
    MAX_NODES,
)

MODEL_ID = "Qwen/Qwen3.5-4B"
OUT_DIR = ROOT / "dataset" / "docs"
MAX_NEW_TOKENS = 2048
TEMPERATURE = 0.3
TOP_P = 0.9

SYSTEM_PROMPT = (
    "You are a strict JSON generator for software architecture graphs. "
    "Answer with one valid JSON document only. No explanation, no analysis."
)

PROMPT_TEMPLATE = """
You are a senior software architect.

Convert the following system description into a CLEAN architecture graph.

RULES:
- Use only meaningful components
- No duplicate edges
- No redundant connections
- Keep architecture minimal and logical

JSON FORMAT:
{{
    "nodes": [
        {{"id": "ui-1", "type": "ui", "technology": "React"}},
        {{"id": "service-1", "type": "service", "technology": null}}
    ],
    "edges": [
        {{"source": "ui-1", "target": "service-1", "protocol": "HTTPS"}}
    ]
}}

CANONICAL IDS: ui-1, service-1, database-1, cache-1, queue-1, container-1.

NODE TYPES: ui, service, database, cache, queue, container.

TECHNOLOGY FIELD:
- Fill it with a specific technology ONLY when the description explicitly names
  it (for example React, FastAPI, PostgreSQL, Redis, React Native, Express,
  MongoDB, Vue.js, Django, MySQL, Next.js, Node.js, S3, SQS, RabbitMQ,
  Prometheus, OAuth, Elasticsearch).
- Otherwise set it to null. Never invent a technology that is not stated.

EDGE PROTOCOL FIELD:
- HTTPS for HTTP/API traffic, SQL for database queries, Redis Protocol for
  cache access, message for queue/broker traffic.
- Set it to null when the description does not indicate the protocol.

CONSTRAINTS:
- Each edge must be unique
- Do NOT repeat same connection
- Max nodes: 10
- Max edges: 15

Description:
{description}

ONLY return JSON. No explanation.
"""

TESTS: list[dict] = [
    {
        "test_id": "TEST 1",
        "prompt": (
            "A collaboration platform: customers open a React single-page "
            "application that talks to a FastAPI backend, which reads and "
            "writes customer data in a PostgreSQL database."
        ),
        "expected_tech": {"React", "FastAPI", "PostgreSQL"},
        "negative": False,
    },
    {
        "test_id": "TEST 2",
        "prompt": (
            "A mobile app: a React Native client for an Express (Node.js) API "
            "server backed by MongoDB."
        ),
        "expected_tech": {"React Native", "Express", "Node.js", "MongoDB"},
        "negative": False,
    },
    {
        "test_id": "TEST 3",
        "prompt": (
            "An e-commerce platform: a Vue.js storefront served by a Django "
            "application backed by MySQL."
        ),
        "expected_tech": {"Vue.js", "Django", "MySQL"},
        "negative": False,
    },
    {
        "test_id": "TEST 4",
        "prompt": (
            "A typical web architecture: a Next.js frontend, a Node.js API "
            "server, a Redis cache, and PostgreSQL as the source of truth."
        ),
        "expected_tech": {"Next.js", "Node.js", "Redis", "PostgreSQL"},
        "negative": False,
    },
    {
        "test_id": "TEST 5",
        "prompt": (
            "A media processing pipeline: a React admin panel uploads files to "
            "an S3 bucket, an SQS queue carries work from an upload service to "
            "a worker service that renders thumbnails."
        ),
        "expected_tech": {"React", "S3", "SQS"},
        "negative": False,
    },
    {
        "test_id": "TEST 6",
        "prompt": (
            "An order processing system: an API service submits orders to a "
            "RabbitMQ broker consumed by a worker service, while Prometheus "
            "monitors both services."
        ),
        "expected_tech": {"RabbitMQ", "Prometheus"},
        "negative": False,
    },
    {
        "test_id": "TEST 7",
        "prompt": (
            "A multi-user SaaS: a React UI, a FastAPI service, a PostgreSQL "
            "database, a Redis cache, OAuth 2.0-based role-based access control, "
            "and a Kong ingress gateway in front."
        ),
        "expected_tech": {"React", "FastAPI", "PostgreSQL", "Redis", "OAuth", "Kong"},
        "negative": False,
    },
    {
        "test_id": "TEST 8",
        "prompt": (
            "A searchable documentation platform: a React frontend, a FastAPI "
            "backend, and an Elasticsearch index for full-text search."
        ),
        "expected_tech": {"React", "FastAPI", "Elasticsearch"},
        "negative": False,
    },
    {
        "test_id": "TEST 9",
        "prompt": (
            "Design a web application with a frontend, a backend API, and a "
            "database."
        ),
        "expected_tech": set(),
        "negative": True,
        "note": "generic architecture; must NOT invent any technology",
    },
    {
        "test_id": "TEST 10",
        "prompt": (
            "Deploy the service stack on a PostgreSQL-compatible hosted "
            "database endpoint and AWS-compatible object storage. The backend "
            "speaks to the database and the storage service."
        ),
        "expected_tech": set(),
        "negative": True,
        "note": "compatibility phrasing; must NOT resolve to PostgreSQL/S3",
    },
]

RUNS_PER_PROMPT = 3
RUNS_JSONL = OUT_DIR / "qwen35_zero_shot_runs.jsonl"


def load_run_state() -> set[tuple[str, int]]:
    done: set[tuple[str, int]] = set()
    if RUNS_JSONL.exists():
        for line in RUNS_JSONL.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
                done.add((rec["test_id"], rec["run"]))
            except json.JSONDecodeError:
                continue
    return done


def load_model():
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID, local_files_only=True
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("Loading model in 4-bit nf4...")
    bnb_cfg = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        device_map="auto",
        quantization_config=bnb_cfg,
        local_files_only=True,
    )
    model.eval()
    print("Model device:", next(model.parameters()).device)
    return model, tokenizer


def build_prompt(description: str) -> str:
    return PROMPT_TEMPLATE.format(description=description.strip())


def strip_thinking(text: str) -> str:
    text = re.sub(r"<\|?thinking.*?</\|?response>", "", text, flags=re.S)
    if re.search(r"\bresponse\b", text, flags=re.I):
        parts = re.split(r"\bresponse\b", text, flags=re.I)
        text = parts[-1]
    return text


def extract_json(text: str) -> tuple[dict | None, str, str]:
    blocks = re.findall(r"```(?:json)?\s*(.*?)```", text, flags=re.S)
    if blocks:
        for candidate in blocks:
            parsed = try_parse(candidate)
            if parsed is not None:
                return parsed, candidate, "fenced"
    parsed = _last_balanced_json(text)
    if parsed is not None:
        return parsed, "", "balanced"
    m = re.search(r"\{.*\}", text, flags=re.S)
    if m:
        parsed = try_parse(m.group(0))
        if parsed is not None:
            return parsed, m.group(0), "regex"
    return None, text, "none"


def _last_balanced_json(text: str) -> dict | None:
    best = None
    for start, ch in enumerate(text):
        if ch != "{":
            continue
        depth = 0
        for i in range(start, len(text)):
            c = text[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    parsed = try_parse(text[start : i + 1])
                    if parsed is not None:
                        best = parsed
                    break
    return best


def try_parse(s: str) -> dict | None:
    try:
        value = json.loads(s)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass
    return None


def validate_graph(graph: dict) -> dict:
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    if not isinstance(nodes, list) or not isinstance(edges, list):
        return {"valid": False, "reason": "nodes/edges not lists"}
    node_ids: list[str] = []
    node_types: list[str] = []
    technologies: list[str | None] = []
    for node in nodes:
        if not isinstance(node, dict):
            return {"valid": False, "reason": "non-dict node"}
        node_ids.append(node.get("id"))
        node_types.append(node.get("type"))
        technologies.append(node.get("technology"))
    edge_list: list[tuple] = []
    for edge in edges:
        if not isinstance(edge, dict):
            return {"valid": False, "reason": "non-dict edge"}
        edge_list.append((edge.get("source"), edge.get("target"), edge.get("protocol")))
    issues: list[str] = []
    if len(nodes) > MAX_NODES:
        issues.append(f"nodes exceed {MAX_NODES}")
    if len(edges) > MAX_EDGES:
        issues.append(f"edges exceed {MAX_EDGES}")
    for node_id, node_type, tech in zip(node_ids, node_types, technologies):
        if not isinstance(node_id, str) or not re.match(r"^(ui|service|database|cache|queue|container)-\d+$", str(node_id)):
            issues.append(f"non-canonical id {node_id!r}")
        if node_type not in ALLOWED_NODE_TYPES:
            issues.append(f"unknown type {node_type!r}")
        if tech is not None and not isinstance(tech, str):
            issues.append(f"non-string technology {tech!r}")
    if len(set(node_ids)) != len(node_ids):
        issues.append("duplicate node ids")
    for src, tgt, proto in edge_list:
        if src not in node_ids or tgt not in node_ids:
            issues.append(f"edge references missing node ({src!r}->{tgt!r})")
        if src == tgt:
            issues.append(f"self-loop edge ({src!r})")
        if proto is not None and not isinstance(proto, str):
            issues.append(f"non-string protocol {proto!r}")
    if len(set(edge_list)) != len(edge_list):
        issues.append("duplicate edges")
    allowed_protocols = {"HTTPS", "SQL", "Redis Protocol", "message"}
    for _, _, proto in edge_list:
        if proto is not None and proto not in allowed_protocols:
            issues.append(f"non-contract protocol {proto!r}")
    return {"valid": not issues, "issues": issues, "node_ids": node_ids,
            "types": node_types, "technologies": technologies,
            "protocols": [e[2] for e in edge_list]}


def audit_tech(technologies: list, expected: set[str]) -> dict:
    present = {t for t in technologies if t}
    missing = sorted(expected - present)
    fabricated = sorted(
        t for t in present if t not in expected
    )
    return {
        "expected_tech": sorted(expected),
        "present_tech": sorted(present),
        "missing_expected_tech": missing,
        "fabricated_tech": fabricated,
        "null_technology_count": technologies.count(None),
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--only",
        nargs="*",
        default=None,
        help="subset of test_ids (e.g. --only 'TEST 1' 'TEST 2')",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="skip runs already recorded in the runs JSONL",
    )
    args = parser.parse_args()

    results: list[dict] = []
    model, tokenizer = load_model()
    device = next(model.parameters()).device
    input_len_ref = {"v": 0}

    start_load = time.time()

    done_runs = load_run_state() if args.resume else set()

    for test in TESTS:
        if args.only and test["test_id"] not in args.only:
            continue
        print("\n" + "=" * 70)
        print(f"{test['test_id']}: {test['prompt'][:80]}...", flush=True)
        run_records = []
        for run in range(1, RUNS_PER_PROMPT + 1):
            if (test["test_id"], run) in done_runs:
                continue
            torch.manual_seed(1000 * run + len(results))
            chat = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_prompt(test["prompt"])},
            ]
            chat_text = tokenizer.apply_chat_template(
                chat, tokenize=False, add_generation_prompt=True
            )
            inputs = tokenizer(chat_text, return_tensors="pt").to(device)
            input_len_ref["v"] = inputs.input_ids.shape[1]
            gen_cfg = {
                "max_new_tokens": MAX_NEW_TOKENS,
                "do_sample": True,
                "temperature": TEMPERATURE,
                "top_p": TOP_P,
                "eos_token_id": tokenizer.eos_token_id,
                "pad_token_id": tokenizer.eos_token_id,
            }
            torch.cuda.reset_peak_memory_stats()
            start_gen = time.time()
            with torch.inference_mode():
                outputs = model.generate(**inputs, **gen_cfg)
            gen_elapsed = time.time() - start_gen
            generated = outputs[0][inputs.input_ids.shape[1]:]
            decoded = tokenizer.decode(generated, skip_special_tokens=True).strip()
            raw = decoded
            cleaned = strip_thinking(decoded)
            graph, extracted, parse_method = extract_json(cleaned)
            out_tokens = int(generated.shape[0])
            in_tokens = int(input_len_ref["v"])
            validation = validate_graph(graph) if graph is not None \
                else {"valid": False, "reason": "no JSON extracted",
                      "node_ids": [], "types": [], "technologies": [], "protocols": []}
            audit = audit_tech(validation.get("technologies", []), test["expected_tech"]) \
                if validation.get("technologies") is not None else {}
            record = {
                "test_id": test["test_id"],
                "run": run,
                "negative": test["negative"],
                "input_tokens": in_tokens,
                "output_tokens": out_tokens,
                "gen_seconds": round(gen_elapsed, 3),
                "tok_per_sec": round(out_tokens / gen_elapsed, 2) if gen_elapsed else None,
                "json_valid": validation.get("valid", False),
                "parse_method": parse_method,
                "fabricated_tech": audit.get("fabricated_tech", []),
                "missing_expected_tech": audit.get("missing_expected_tech", []),
                "technologies": audit.get("present_tech", []),
                "null_technology_count": audit.get("null_technology_count", 0),
                "node_ids": validation.get("node_ids", []),
                "types": validation.get("types", []),
                "protocols": validation.get("protocols", []),
                "issues": validation.get("issues", []),
                "node_count": len(validation.get("node_ids", [])),
                "edge_count": lines_count(graph) if graph else 0,
                "raw_output": raw[:800],
            }
            print(f"  run {run}: json_valid={record['json_valid']} "
                  f"tok/s={record['tok_per_sec']} nodes={record['node_count']} "
                  f"tech={record['technologies']}", flush=True)
            run_records.append(record)

            runs_jsonl = Path(OUT_DIR) / "qwen35_zero_shot_runs.jsonl"
            runs_jsonl.parent.mkdir(parents=True, exist_ok=True)
            with runs_jsonl.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")

        try:
            json_ok = sum(1 for r in run_records if r["json_valid"])
            all_same = len({r["node_ids"] for r in run_records}) <= 1
            summary = {
                "test_id": test["test_id"],
                "note": test.get("note", ""),
                "negative": test["negative"],
                "runs": RUNS_PER_PROMPT,
                "json_valid_ratio": f"{json_ok}/{RUNS_PER_PROMPT}",
                "consistent_nodes_across_runs": all_same,
                "fabrications_any_run": sorted({t for r in run_records for t in r["fabricated_tech"]}),
                "missing_expected_any_run": sorted({t for r in run_records for t in r["missing_expected_tech"]}),
                "avg_tok_per_sec": round(sum(r["tok_per_sec"] for r in run_records if r["tok_per_sec"]) / max(1, json_ok), 2),
            }
            results.append(summary | {"runs_detail": run_records})
        except Exception as exc:  # noqa: BLE001
            summary = {"test_id": test["test_id"], "error": str(exc)}
            results.append(summary | {"runs_detail": run_records})

    load_duration = time.time() - start_load
    out_json = Path(OUT_DIR) / "qwen35_zero_shot_benchmark_raw.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "model": MODEL_ID,
        "revision": os.environ.get("QWEN_REVISION", "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a"),
        "generation": {
            "max_new_tokens": MAX_NEW_TOKENS,
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
        },
        "load_seconds": round(load_duration, 2),
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "peak_vram_mb": round(torch.cuda.max_memory_allocated() / 1024**2, 1)
        if torch.cuda.is_available() else None,
        "results": results,
    }
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("\nWrote:", out_json, flush=True)
    print("Peak VRAM MB:", payload["peak_vram_mb"], flush=True)


def lines_count(graph: dict) -> int:
    if not isinstance(graph, dict):
        return 0
    return len(graph.get("edges", []))


if __name__ == "__main__":
    main()