# Phase 8 Final Evaluation

**Status:** COMPLETE — final evaluation on the untouched 2,575-record test split.

## 1. Setup

- Adapter: `checkpoints/gemma_lora` (full run, E2b config: r24/α48, lr 2e-4, 1 epoch)
- Base: `unsloth/gemma-3-4b-it-bnb-4bit` (4-bit NF4, frozen)
- Test split: 2,575 records of `dataset/training/CyberShield_Gemma_SFT_v1.jsonl` — **untouched by training and tuning**
- Generation: greedy, `repetition_penalty=1.1`, no ngram, `max_new_tokens=768`, batch 3, seed 42
- Wall time: 9,761 s (~2.7 h); peak VRAM 3.41 GiB
- Artifact: `dataset/docs/phase8_final_test_eval.json` (per-output detail included)

## 2. Results (n = 2,575)

| Metric | Value |
|---|---|
| Generation success rate | 1.0 |
| **Parse rate** | **1.0** (0 parse failures) |
| **Schema-valid rate** (canonical validator) | **1.0** (0 issues of any kind except 1 connectedness) |
| Contract-valid rate (≤10 nodes / ≤15 edges) | **1.0** |
| Connectedness rate | 0.9996 (1 disconnected output) |
| Orphan rate | 0.0004 (same single output) |
| **Repetition-loop rate** (repeated edges) | **0.0** (loop class eliminated) |
| EOS completion rate | 1.0 (no token-cap truncations) |
| Node precision / recall / **F1** | 0.2233 / 0.2252 / **0.2242** |
| Edge precision / recall / **F1** | 0.0652 / 0.0642 / **0.0647** |
| Exact architecture match rate | **0.0** |
| Generated node counts | avg 8.0, max 8 (target avg 7.93) |
| Generated edge counts | avg 7.15, max 10 (target avg 7.26) |
| Avg prompt / generated tokens | 222.7 / 220.0 |
| Validator issue inventory | `connectedness: 1` only |

### Failure-category breakdown (2,575 outputs)
- EMPTY output: 0 — NO_JSON: 0 — INCOMPLETE_JSON: 0 — OTHER_PARSE: 0
- Disconnected: 1 (`SFT-050933`, 8 nodes / 7 edges)
- Orphan nodes: 1 (same output)
- Repetition loops: 0 — Token-cap truncation: 0

### Examples
- **Good (highest fidelity):** `SFT-050688` — 8 nodes / 7 edges, 7/8 nodes and 5/7 edges matching the target (215 gen tokens). `SFT-049886` — 6/8 nodes, 5/7 edges (211 gen tokens).
- **Failure:** `SFT-050933` — the only disconnected output; structurally valid JSON, all types/labels supported, within limits, but its graph is not weakly connected (runtime retry loop in `inference.py` covers this class).

## 3. Interpretation (honest)

1. **Format and structure are mastered.** 100% parse, 100% schema-valid, 100% within contract, 99.96% connected, zero repetition loops, 100% EOS-completed. The pilot's ~8% repetition-loop failure class is **completely eliminated** (by the repetition-penalty inference setting and the larger training corpus). The model will essentially never trigger the runtime retry/fallback path on format grounds.
2. **Content fidelity is NOT mastered.** Node F1 0.224, edge F1 0.065, exact match 0.0. The model produces *plausible, valid* architectures whose component inventory only partially matches the canonical Phase 6 targets. Best-case outputs match 7/8 nodes and 5/7 edges; typical outputs share only ~22% of node names and ~6.5% of edge keys with the expected target.
3. **Count conditioning works despite saturation**: generated counts (8.0 nodes / 7.15 edges) track targets (7.93 / 7.26) closely — the model learned the target distribution even though 98.2% of targets have exactly 8 nodes.
4. **Why fidelity plateaus (~0.22 node F1):** the SFT targets encode *arbitrary per-record naming conventions* (53% ALL-CAPS, 44% camelCase, mixed per record) for semantically identical components, in non-canonical emission order. A LoRA adapter (44.7 M trainable params on a 4-bit 4B base, 1 epoch) can memorize format but cannot generalize an arbitrary description→invented-name mapping. Node F1 was already 0.24 at 800 training records and did **not** improve at 46,348 — the bottleneck is the data's naming arbitrariness, not exposure (see `phase8_training_tuning_report.md` §5 and §6).
5. **Gate result:** the Phase 8 quality gates run on this eval report **OVERALL FAIL** — G5 strict-equality gates (`connected_rate == 1.0`, `structurally_weak_rate == 0.0`) fail on the single 0.04% disconnected output. All 7 other gates PASS. This is reported as-is; no thresholds were weakened.

## 4. Verdict

- **The final model produces valid-but-only-partially-correct architectures.** It is NOT a faithful reproduction of the canonical Phase 6 targets (exact match 0%, edge F1 0.065). Training is NOT declared successful on fidelity grounds; the pilot finding persists at full scale.
- **Readiness for inference:** the model is safe to serve behind the existing runtime pipeline (valid JSON guaranteed in practice, retry loop covers the 0.04% disconnected class, contract always respected), and produces usable plausible architecture graphs. It cannot be relied on to reproduce the expected canonical inventory. This limitation is the same class the tuning report predicted; the required per-record fidelity improvement did not materialize with the full corpus.
- Per requirement 13 the evidence is reported rather than papered over: the Phase 6→SFT naming scheme (arbitrary, per-record, non-canonical) is the identified structural cause; changing it would require a Phase 6/SFT re-transformation, which is outside Phase 8's mandate.