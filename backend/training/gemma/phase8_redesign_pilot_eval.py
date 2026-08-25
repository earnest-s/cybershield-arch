#!/usr/bin/env python3
"""Redesign pilot evaluation — corrected methodology (NO 8-node truncation).

Applies the established corrected evaluation methodology
(backend/training/gemma/phase8_corrected_eval.py) to a pilot dataset artifact:

- targets are loaded VERBATIM from the record's ``architecture`` field (never
  parsed/truncated through the runtime parser);
- generated outputs are parsed with the non-truncating ``normalize_full`` for
  structural comparison AND with the runtime-faithful ``parse_architecture`` for
  the runtime view;
- runtime contract validation (≤10 nodes / ≤15 edges) is on the FULL generated
  graph;
- generation settings are identical to the final eval (greedy, seed 42,
  repetition_penalty 1.1, no_repeat_ngram 0, max_new_tokens 768, gen_batch 3).

In addition, per the redesign proposal §6.2 the eval reports DUAL metrics:

- STRUCTURE-level (primary): node F1 over the (type) inventory; edge F1 over the
  (source-type, target-type, label) multiset; canonical exact match. These are
  representation-independent and are the proposal's success-gate metrics.
- NAME-level (legacy, comparable to the 0.237/0.069 baseline): exact node-id set
  F1 and exact edge-key set F1 in the variant's own encoding; for canonical
  variants, ids are additionally mapped back to the original names via the
  record's id_map and scored against the original architecture (informational).

Read-only: loads a pilot dataset + adapter and writes a NEW eval JSON. Does not
modify the pilot dataset, source artifact, adapter, runtime, or any existing eval.

Usage:
    uv run python backend/training/gemma/phase8_redesign_pilot_eval.py \
        --artifact dataset/pilots/redesign_A.jsonl \
        --adapter checkpoints/redesign_pilot_A \
        --out dataset/docs/redesign_pilot_A_eval.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
os.environ.setdefault("HF_HOME", str(_REPO_ROOT / ".cache" / "huggingface"))

MODEL_ID = "unsloth/gemma-3-4b-it-bnb-4bit"
_HF_HUB_DIR = _REPO_ROOT / ".cache" / "huggingface" / "hub"
EOS_ID = 106
HARD_NODE_LIMIT = 10
HARD_EDGE_LIMIT = 15


def edge_key(edge: dict) -> tuple:
    return (edge.get("source"), edge.get("target"), edge.get("label"))


def normalize_full(raw: dict) -> dict:
    from backend.core.architecture_parser import normalize_node_type

    nodes = raw.get("nodes")
    edges = raw.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("Architecture JSON must contain 'nodes' and 'edges' arrays")
    if len(nodes) == 0 or len(edges) == 0:
        raise ValueError("Architecture JSON must include at least one node and one edge")

    normalized_nodes: list[dict] = []
    node_types_by_id: dict[str, str] = {}
    for node in nodes:
        if isinstance(node, dict):
            node_id, node_type = node.get("id"), node.get("type")
        elif isinstance(node, str):
            node_id, node_type = node, None
        else:
            node_id, node_type = None, None
        if not isinstance(node_id, str) or not node_id.strip():
            raise ValueError("Each node must include a non-empty string 'id'")
        normalized_id = node_id.strip()
        if len(normalized_id) > 64:
            raise ValueError("Node id exceeds limits")
        if normalized_id in node_types_by_id:
            continue
        node_types_by_id[normalized_id] = normalize_node_type(node_type, normalized_id)
        normalized_nodes.append({"id": normalized_id, "type": node_types_by_id[normalized_id]})

    allowed_ids = {nd["id"] for nd in normalized_nodes}
    normalized_edges: list[dict] = []
    seen: set[tuple] = set()
    for edge in edges:
        source, target, label = _split_edge(edge)
        if not isinstance(source, str) or not isinstance(target, str):
            raise ValueError("Each edge must include string 'source' and 'target'")
        source_id, target_id = source.strip(), target.strip()
        if source_id == target_id:
            continue
        if source_id not in allowed_ids or target_id not in allowed_ids:
            continue
        key = (source_id, target_id)
        if key in seen:
            continue
        seen.add(key)
        from backend.core.architecture_parser import infer_edge_label
        normalized_edges.append({
            "source": source_id,
            "target": target_id,
            "label": infer_edge_label(
                node_types_by_id[source_id], node_types_by_id[target_id],
                label if isinstance(label, str) else None,
            ),
        })

    if len(normalized_edges) == 0:
        raise ValueError("Architecture JSON must include at least one valid edge")
    return {"nodes": normalized_nodes, "edges": normalized_edges}


def _split_edge(edge) -> tuple:
    if isinstance(edge, dict):
        source = edge.get("source") if edge.get("source") is not None else edge.get("from")
        target = edge.get("target") if edge.get("target") is not None else edge.get("to")
        label = edge.get("label") if edge.get("label") is not None else edge.get("protocol")
        return source, target, label
    if isinstance(edge, (list, tuple)) and len(edge) >= 2:
        return edge[0], edge[1], edge[2] if len(edge) >= 3 else None
    return None, None, None


def classify_parse_failure(raw: str) -> str:
    if not raw or not raw.strip():
        return "EMPTY_OUTPUT"
    if "{" not in raw:
        return "NO_JSON"
    if raw.count("{") > raw.count("}"):
        return "INCOMPLETE_JSON"
    return "OTHER_PARSE"


def struct_f1(gen_types: Counter, tgt_types: Counter):
    tp = sum(min(gen_types[k], tgt_types[k]) for k in set(gen_types) | set(tgt_types))
    fp = sum(gen_types.values()) - tp
    fn = sum(tgt_types.values()) - tp
    p = tp / max(1e-9, tp + fp)
    r = tp / max(1e-9, tp + fn)
    f1 = 2 * p * r / max(1e-9, p + r)
    return tp, fp, fn, p, r, f1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", default="dataset/pilots/redesign_A.jsonl")
    parser.add_argument("--adapter", default="checkpoints/redesign_pilot_A")
    parser.add_argument("--split", choices=["train", "validation", "test"], default="validation")
    parser.add_argument("--n-gen", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-new-tokens", type=int, default=768)
    parser.add_argument("--gen-batch", type=int, default=3)
    parser.add_argument("--repetition-penalty", type=float, default=1.1)
    parser.add_argument("--no-repeat-ngram", type=int, default=0)
    parser.add_argument("--out", default="dataset/docs/redesign_pilot_A_eval.json")
    parser.add_argument("--ids", type=str, default="")
    args = parser.parse_args()

    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    from backend.core.architecture_parser import extract_json_object_comments, parse_architecture
    from backend.core.architecture_validator import collect_issues, has_orphan_node, is_weakly_connected

    torch.manual_seed(args.seed)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, local_files_only=True, cache_dir=str(_HF_HUB_DIR))
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    bnb_cfg = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)
    base = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, device_map="auto", quantization_config=bnb_cfg, local_files_only=True, cache_dir=str(_HF_HUB_DIR)
    )
    base.config.use_cache = True

    adapter_path = Path(args.adapter)
    model = PeftModel.from_pretrained(base, adapter_path) if adapter_path.exists() else base
    model.eval()
    print(f"[INFO] adapter: {args.adapter if adapter_path.exists() else 'NONE (base)'}")

    rows = []
    for line in open(Path(args.artifact), encoding="utf-8"):
        r = json.loads(line)
        if r["metadata"]["split"] == args.split:
            rows.append(r)
    if args.ids:
        wanted = set(args.ids.split(","))
        rows = [r for r in rows if r["id"] in wanted]
    rows = rows if args.n_gen <= 0 else rows[: args.n_gen]
    print(f"[INFO] evaluating {len(rows)} {args.split} records from {args.artifact} "
          f"(batch {args.gen_batch}, rep_penalty {args.repetition_penalty}, ngram {args.no_repeat_ngram})")

    chat_prompts = [
        tokenizer.apply_chat_template([{"role": "user", "content": r["instruction"]}],
                                      add_generation_prompt=True, tokenize=False)
        for r in rows
    ]

    def generate_batch(prompts: list[str]) -> tuple[list[str], list[int]]:
        enc = tokenizer(prompts, return_tensors="pt", padding="longest").to(model.device)
        with torch.inference_mode():
            out = model.generate(
                **enc, max_new_tokens=args.max_new_tokens, do_sample=False,
                repetition_penalty=args.repetition_penalty,
                no_repeat_ngram_size=args.no_repeat_ngram,
                eos_token_id=EOS_ID, pad_token_id=tokenizer.pad_token_id,
            )
        input_len = enc.input_ids.shape[1]
        decodes, gen_lens = [], []
        for row in out:
            gen_ids = row[input_len:]
            n_eos = int((gen_ids == EOS_ID).sum())
            if n_eos:
                gen_ids = gen_ids[: int((gen_ids == EOS_ID).nonzero()[0])]
            gen_lens.append(int(gen_ids.shape[0]))
            decodes.append(tokenizer.decode(gen_ids, skip_special_tokens=True).strip())
        return decodes, gen_lens

    results = {
        "config": {
            "artifact": args.artifact, "adapter": args.adapter, "split": args.split,
            "n_gen": len(rows), "max_new_tokens": args.max_new_tokens, "gen_batch": args.gen_batch,
            "repetition_penalty": args.repetition_penalty, "no_repeat_ngram": args.no_repeat_ngram,
            "seed": args.seed, "model": MODEL_ID,
            "target_source": "pilot artifact architecture field (FULL, untruncated)",
            "generated_full_parse": "non-truncating normalize_full",
            "metrics": "structure-level (types) + name-level (exact ids) per proposal §6.2",
            "contract": {"max_nodes": HARD_NODE_LIMIT, "max_edges": HARD_EDGE_LIMIT},
        },
        "generation_success": 0, "parse_ok": 0,
        "parse_failure_categories": Counter(),
        "schema_valid": 0, "schema_valid_runtime": 0, "contract_valid": 0,
        "connected": 0, "orphan": 0, "structurally_weak": 0, "within_guardrail": 0,
        "repeated_edge_outputs": 0, "repeated_directed_edge_total": 0,
        "eos_completed": 0, "hit_token_cap": 0, "runtime_truncation_outputs": 0,
        "issue_counts": Counter(),
        # structure-level (primary)
        "struct_node_tp": 0, "struct_node_fp": 0, "struct_node_fn": 0,
        "struct_edge_tp": 0, "struct_edge_fp": 0, "struct_edge_fn": 0,
        "canonical_exact_match": 0,
        # name-level (legacy, comparable to baseline)
        "node_tp": 0, "node_fp": 0, "node_fn": 0,
        "edge_tp": 0, "edge_fp": 0, "edge_fn": 0,
        "name_exact_match": 0,
        # informational: mapped-back original-name score for canonical variants
        "orig_node_tp": 0, "orig_node_fp": 0, "orig_node_fn": 0,
        "node_count_abs_err": [], "edge_count_abs_err": [],
        "gen_tokens": [], "prompt_tokens": [],
        "node_counts": [], "edge_counts": [],
        "target_node_counts": [], "target_edge_counts": [],
        "outputs": [], "wall_seconds": 0.0,
    }

    t0 = time.time()
    for start in range(0, len(rows), args.gen_batch):
        chunk = rows[start: start + args.gen_batch]
        decodes, gen_lens = generate_batch([chat_prompts[i] for i in range(start, start + len(chunk))])

        for r, raw, gen_len in zip(chunk, decodes, gen_lens):
            entry: dict = {"id": r["id"], "gen_tokens": gen_len}
            results["gen_tokens"].append(gen_len)
            prompt_len = len(tokenizer(chat_prompts[rows.index(r)], add_special_tokens=False)["input_ids"])
            results["prompt_tokens"].append(prompt_len)

            if gen_len >= args.max_new_tokens:
                results["hit_token_cap"] += 1
            else:
                results["eos_completed"] += 1
                entry["eos_completed"] = True

            if not raw:
                entry["failure"] = "EMPTY_OUTPUT"
                results["parse_failure_categories"]["EMPTY_OUTPUT"] += 1
                results["outputs"].append(entry)
                continue
            results["generation_success"] += 1

            try:
                raw_json = extract_json_object_comments(raw)
            except ValueError:
                cat = classify_parse_failure(raw)
                entry["failure"] = cat
                results["parse_failure_categories"][cat] += 1
                results["outputs"].append(entry)
                continue

            try:
                gen_full = normalize_full(raw_json)
                results["parse_ok"] += 1
            except ValueError:
                cat = classify_parse_failure(raw)
                entry["failure"] = cat
                results["parse_failure_categories"][cat] += 1
                results["outputs"].append(entry)
                continue

            gen_runtime = None
            try:
                gen_runtime = parse_architecture(raw_json)
            except ValueError:
                pass
            if gen_runtime is not None and (
                len(gen_runtime["nodes"]) < len(gen_full["nodes"])
                or len(gen_runtime["edges"]) < len(gen_full["edges"])
            ):
                results["runtime_truncation_outputs"] += 1
                entry["runtime_truncated"] = True

            target = r["architecture"]
            nodes, edges = gen_full["nodes"], gen_full["edges"]
            node_ids = [n["id"] for n in nodes]
            edge_keys = [edge_key(e) for e in edges]

            issues = list(collect_issues(gen_full))
            has_errors = any(i.severity == "error" for i in issues)
            conn = is_weakly_connected(nodes, edges)
            orphan = has_orphan_node(gen_full)
            for i in issues:
                results["issue_counts"][i.rule] += 1
            entry.update({
                "nodes": len(node_ids), "edges": len(edge_keys),
                "connected": conn, "orphan": orphan,
                "schema_valid": not has_errors, "issues": [f"{i.rule}" for i in issues],
            })
            results["node_counts"].append(len(node_ids))
            results["edge_counts"].append(len(edge_keys))
            if gen_runtime is not None:
                r_issues = list(collect_issues(gen_runtime))
                results["schema_valid_runtime"] += 0 if any(i.severity == "error" for i in r_issues) else 1
            if not has_errors:
                results["schema_valid"] += 1
            if len(node_ids) <= HARD_NODE_LIMIT and len(edge_keys) <= HARD_EDGE_LIMIT:
                results["contract_valid"] += 1
                results["within_guardrail"] += 1
            if conn:
                results["connected"] += 1
            if orphan:
                results["orphan"] += 1
            if not conn or orphan:
                results["structurally_weak"] += 1

            gen_edge_set = set(edge_keys)
            n_dup = len(edge_keys) - len(gen_edge_set)
            if n_dup:
                results["repeated_edge_outputs"] += 1
                results["repeated_directed_edge_total"] += n_dup
                entry["repeated_directed_edges"] = n_dup

            # ---------- STRUCTURE-LEVEL (primary) ----------
            gen_type_by_id = {n["id"]: n["type"] for n in nodes}
            gen_node_types = Counter(n["type"] for n in nodes)
            tgt_node_types = Counter(n["type"] for n in target["nodes"])
            stp, sfp, sfn, sp, sr, s1 = struct_f1(gen_node_types, tgt_node_types)
            results["struct_node_tp"] += stp
            results["struct_node_fp"] += sfp
            results["struct_node_fn"] += sfn

            def edge_struct_counter(g: dict, types_by_id: dict) -> Counter:
                c = Counter()
                for e in g["edges"]:
                    c[(types_by_id[e["source"]], types_by_id[e["target"]], e["label"])] += 1
                return c

            gen_edges_struct = edge_struct_counter(gen_full, gen_type_by_id)
            tgt_type_by_id = {n["id"]: n["type"] for n in target["nodes"]}
            tgt_edges_struct = edge_struct_counter(target, tgt_type_by_id)
            etp, efp, efn, ep, er, e1 = struct_f1(gen_edges_struct, tgt_edges_struct)
            results["struct_edge_tp"] += etp
            results["struct_edge_fp"] += efp
            results["struct_edge_fn"] += efn

            canon_exact = (stp == sum(gen_node_types.values()) == sum(tgt_node_types.values())
                           and etp == sum(gen_edges_struct.values()) == sum(tgt_edges_struct.values()))
            if canon_exact:
                results["canonical_exact_match"] += 1
                entry["canonical_exact_match"] = True

            # ---------- NAME-LEVEL (legacy, comparable to baseline) ----------
            tgt_node_ids = {n["id"] for n in target["nodes"]}
            tgt_edge_keys = {edge_key(e) for e in target["edges"]}
            results["target_node_counts"].append(len(tgt_node_ids))
            results["target_edge_counts"].append(len(tgt_edge_keys))

            gns, ens = set(node_ids), tgt_node_ids
            ges, ees = gen_edge_set, tgt_edge_keys
            ntp = len(gns & ens)
            nfp = len(gns - ens)
            nfn = len(ens - gns)
            etp2 = len(ges & ees)
            efp2 = len(ges - ees)
            efn2 = len(ees - ges)
            results["node_tp"] += ntp
            results["node_fp"] += nfp
            results["node_fn"] += nfn
            results["edge_tp"] += etp2
            results["edge_fp"] += efp2
            results["edge_fn"] += efn2
            results["node_count_abs_err"].append(abs(len(node_ids) - len(tgt_node_ids)))
            results["edge_count_abs_err"].append(abs(len(edge_keys) - len(tgt_edge_keys)))
            entry.update({
                "node_tp": ntp, "node_fp": nfp, "node_fn": nfn,
                "edge_tp": etp2, "edge_fp": efp2, "edge_fn": efn2,
            })
            name_exact = ntp == len(ens) == len(gns) and etp2 == len(ees) == len(ges)
            if name_exact:
                results["name_exact_match"] += 1
                entry["name_exact_match"] = True

            # ---------- INFORMATIONAL: original-name score via id_map ----------
            id_map = r["metadata"].get("canonicalization", {}).get("id_map")
            if id_map:
                rev = {v: k for k, v in id_map.items()}
                orig_arch = r["metadata"]["original_architecture"]
                o_target_ids = {n["id"] for n in orig_arch["nodes"]}
                o_gen_ids = {rev.get(i, i) for i in node_ids}
                otp = len(o_gen_ids & o_target_ids)
                ofp = len(o_gen_ids - o_target_ids)
                ofn = len(o_target_ids - o_gen_ids)
                results["orig_node_tp"] += otp
                results["orig_node_fp"] += ofp
                results["orig_node_fn"] += ofn

            results["outputs"].append(entry)

        done = start + len(chunk)
        if done % 20 == 0 or done == len(rows):
            print(f"[eval] {done}/{len(rows)} ({time.time() - t0:.0f}s)", flush=True)

    results["n"] = len(rows)
    results["wall_seconds"] = round(time.time() - t0, 1)
    n = len(rows)
    parsed = results["parse_ok"]

    def f1(tp, fp, fn):
        p = tp / max(1e-9, tp + fp)
        r = tp / max(1e-9, tp + fn)
        return p, r, 2 * p * r / max(1e-9, p + r)

    sp, sr, sf = f1(results["struct_node_tp"], results["struct_node_fp"], results["struct_node_fn"])
    sep_, ser, sef = f1(results["struct_edge_tp"], results["struct_edge_fp"], results["struct_edge_fn"])
    np_, nr, nf = f1(results["node_tp"], results["node_fp"], results["node_fn"])
    ep_, er_, ef = f1(results["edge_tp"], results["edge_fp"], results["edge_fn"])
    op, or_, of_ = f1(results["orig_node_tp"], results["orig_node_fp"], results["orig_node_fn"])

    results.update({
        "generation_success_rate": round(results["generation_success"] / n, 4),
        "parse_rate": round(parsed / n, 4),
        "schema_valid_rate": round(results["schema_valid"] / max(1, parsed), 4),
        "schema_valid_runtime_rate": round(results["schema_valid_runtime"] / max(1, parsed), 4),
        "contract_valid_rate": round(results["contract_valid"] / max(1, parsed), 4),
        "connected_rate": round(results["connected"] / max(1, parsed), 4),
        "orphan_rate": round(results["orphan"] / max(1, parsed), 4),
        "structurally_weak_rate": round(results["structurally_weak"] / max(1, parsed), 4),
        "guardrail_rate": round(results["within_guardrail"] / n, 4),
        "repetition_output_rate": round(results["repeated_edge_outputs"] / max(1, parsed), 4),
        "runtime_truncation_rate": round(results["runtime_truncation_outputs"] / max(1, parsed), 4),
        "eos_completion_rate": round(results["eos_completed"] / n, 4),
        "hit_cap_rate": round(results["hit_token_cap"] / n, 4),
        # structure-level (primary)
        "struct_node_precision": round(sp, 4), "struct_node_recall": round(sr, 4), "struct_node_f1": round(sf, 4),
        "struct_edge_precision": round(sep_, 4), "struct_edge_recall": round(ser, 4), "struct_edge_f1": round(sef, 4),
        "canonical_exact_match_rate": round(results["canonical_exact_match"] / n, 4),
        # name-level (legacy, comparable to baseline)
        "node_precision": round(np_, 4), "node_recall": round(nr, 4), "node_f1": round(nf, 4),
        "edge_precision": round(ep_, 4), "edge_recall": round(er_, 4), "edge_f1": round(ef, 4),
        "exact_match_rate": round(results["name_exact_match"] / n, 4),
        # informational
        "orig_node_precision": round(op, 4), "orig_node_recall": round(or_, 4), "orig_node_f1": round(of_, 4),
        "node_count_error": round(sum(results["node_count_abs_err"]) / max(1, len(results["node_count_abs_err"])), 4),
        "edge_count_error": round(sum(results["edge_count_abs_err"]) / max(1, len(results["edge_count_abs_err"])), 4),
        "avg_gen_tokens": round(sum(results["gen_tokens"]) / max(1, len(results["gen_tokens"])), 1),
        "avg_prompt_tokens": round(sum(results["prompt_tokens"]) / max(1, len(results["prompt_tokens"])), 1),
        "avg_nodes": round(sum(results["node_counts"]) / max(1, len(results["node_counts"])), 2),
        "avg_edges": round(sum(results["edge_counts"]) / max(1, len(results["edge_counts"])), 2),
        "avg_target_nodes": round(sum(results["target_node_counts"]) / max(1, len(results["target_node_counts"])), 2),
        "avg_target_edges": round(sum(results["target_edge_counts"]) / max(1, len(results["target_edge_counts"])), 2),
        "max_nodes": max(results["node_counts"]) if results["node_counts"] else 0,
        "max_edges": max(results["edge_counts"]) if results["edge_counts"] else 0,
        "parse_failure_categories": dict(results["parse_failure_categories"]),
        "issue_counts": dict(results["issue_counts"]),
    })
    for key in ("node_counts", "edge_counts", "target_node_counts", "target_edge_counts",
                "gen_tokens", "prompt_tokens", "node_count_abs_err", "edge_count_abs_err"):
        del results[key]

    print(json.dumps({k: v for k, v in results.items() if k != "outputs"}, indent=2))
    out_path = _REPO_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2))
    print(f"[INFO] written {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())