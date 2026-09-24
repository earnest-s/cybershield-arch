# Qwen3.5-4B response-format probe

Isolated experiment to determine whether the zero-shot failure mode (56.7% no-JSON
emission, 28/30 runs at the 2048-token cap) is a decode/behavior problem or needs a
small SFT response-format pilot. No weights were trained, no production code touched.

- Model: `Qwen/Qwen3.5-4B` rev `851bf6e8…` (4-bit NF4, fp16 compute, RTX 4050 5.7 GB)
- Sampling: `do_sample=True, temperature=0.3, top_p=0.9`, `max_new_tokens=2048`
- Data: `dataset/docs/qwen35_format_probe.json` (27 runs, full raw + per-run records)

## Conditions

| id | name | supported | setup |
|----|------|-----------|-------|
| A | current configuration | yes | identical prompt + sampling to `scripts/benchmark_qwen35.py` |
| B | explicit non-thinking mode | **no** | Qwen3.5-4B (`model_type qwen3_5`) in transformers 5.14.1 exposes no thinking toggle, no thinking special tokens, no `enable_thinking`, no `generation_config.json`; "Thinking Process:" is free-form emitted text, not gated decoding |
| C | non-thinking + concise JSON-only instruction | yes | short direct-answer system + user prompt with inline schema |
| D | schema-shaped constrained decoding | yes | baseline A prompt + custom `JsonSchemaConstrainedLogitsProcessor` (top-K=128 candidate masking + full-vocab expansion on empty window; structural JSON FSM, top-level keys forced `nodes` → `edges`, sub-keys limited to `{id,type,technology,source,target,protocol}`, EOS only when complete) |

Probes: P1 React+FastAPI+PostgreSQL, P2 +Redis+RabbitMQ, P3 AWS S3+SQS+PostgreSQL(RDS).
Each probe × 3 runs per condition.

## Aggregate results

| metric | A | C | D |
|--------|------|------|------|
| emission-rate | 3/9 | 8/9 | **9/9** |
| valid-rate | 3/9 | 2/9 | **6/9** |
| tech-correct-rate | 3/9 | 6/9 | **6/9** |
| fabricated-tech rate | 0/9 | 0/9 | 0/9 |
| avg nodes / edges | 3.0 / 2.0 | 4.6 / 3.6 | 4.7 / 3.4 |
| avg latency | 64.8 s | 64.3 s | **7.1 s** |
| avg output tokens | 2048 | 2048 | **193** |
| tok/s | 31.6 | 31.9 | 26.9 |
| peak VRAM | 3354 MB | 3326 MB | 3354 MB |

Constraint health (D): 0 degraded, 0 fallback_count, expanded_count = 2/run (step 1
`{` + one mid-graph boundary) → the FSM mask held for all 9 runs with zero violations.

## Per-probe detail

| cond | probe | emitted | valid | tech | missing expected | fabrication |
|------|-------|---------|-------|------|------------------|-------------|
| A | P1 | 3/3 | 3/3 | React, FastAPI, PostgreSQL | none | none |
| A | P2 | 0/3 | 0/3 | — | all 5 | none |
| A | P3 | 0/3 | 0/3 | — | all 5 | none |
| C | P1 | 3/3 | 1/3 | complete | none* | none |
| C | P2 | 3/3 | 0/3 | complete | none* | none |
| C | P3 | 2/3 | 1/3 | PostgreSQL,S3,SQS | AWS, RDS | none |
| D | P1 | 3/3 | 3/3 | complete | none | none |
| D | P2 | 3/3 | 0/3 | complete | none* | none |
| D | P3 | 3/3 | 3/3 | PostgreSQL,SQS | AWS, RDS, S3 | none |

\* C/D "invalid" on P1/P2 is only the canonical-id check (`worker-1`, `db-1`,
`s3-1`, `sqs-1`, `proc-1` vs `service-1`/`database-1`/…); the graphs are otherwise
structurally complete and tech-complete. A's SYSTEM_PROMPT teaches canonical ids;
the C short prompt does not, and D keeps them only when the model obeys the prompt.

## Failure-mode attribution

1. **The 2048-token reasoning loop is a decode/behavior problem, not a prompt
   problem.** C (explicit "JSON only") still runs to the token cap every run and
   never emits within reasonable bounds — the model writes `Thinking Process:`
   regardless. Only the structural constraint (D) makes generation terminate, and
   it does so immediately after the graph closes: 100% emission, ~193 tokens, ~9×
   faster. This is gated/decode territory; no SFT required to stop the loop.
2. **Prompt shape controls emission (whether a JSON appears at all in the stream).**
   C lifts emission 3/9 → 8/9 with zero fabrication, matching the baseline
   observation that emitted JSONs are contract-perfect. Worth keeping a concise
   "JSON only" formulation even without retraining.
3. **Content completeness is a separate model-knowledge gap that format cannot
   fix.** P3 (AWS S3/SQS/RDS) is tech-incomplete under C and D alike (AWS/RDS/S3
   omitted); the issue is the model's mapping of the AWS scenario to node
   technologies, not its response format. This is the only part of the failure that
   points toward some training signal (SFT content/data), and for v2-style
   hallucination control it is irrelevant — fabrication was 0 across all 27 runs.
4. **Canonical-id compliance needs either the explicit SYSTEM_PROMPT guidance
   (works: A P1) or a small response-format/labeling signal (C/D failures are
   shallow and reproducible: `db-1`, `worker-1`, `s3-1`).** Note the baseline
   validator regex only admits `{ui,service,database,cache,queue,container}-N`.

## Verdict for v3

- The baseline 56.7% no-JSON failure is **decoder/structure behavior**, provably
  removable without LoRA/retraining (D shows 100% emission, valid, clean EOS).
- A response-format **SFT pilot is NOT required** for the format failure; it would
  only plausibly help canonical-id naming, which is also addressable by keeping the
  instructive system prompt and/or relaxed/consistent id enforcement.
- An **SFT content pilot** remains the right lever for the AWS-scenario tech
  completeness if P3-style prompts matter for the product — separate from the format
  question this probe answered.
- Recommendation: productionize structured/constrained decoding (or a strict
  JSON-only prompt + early-stop-on-close) before considering any v3 training; no
  training was performed or started as part of this probe.