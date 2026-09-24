# Qwen3.5-4B Zero-Shot Benchmark

Experimental, v3-oriented evaluation of `Qwen/Qwen3.5-4B` as a candidate base
for a future CyberShield v3 LoRA. Zero-shot only: no fine-tuning, not evaluated
for production use.

- Date: 2026-09-24
- Model: `Qwen/Qwen3.5-4B` (revision `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`)
- Location: project-isolated cache `{repo}/.cache/huggingface` (8.8 GB on disk)
- Hardware: NVIDIA GeForce RTX 4050 Laptop (5.7 GB VRAM), 24 GB RAM
- Load: 4-bit NF4 (bitsandbytes), compute float16, `device_map="auto"` → cuda:0
- Peak VRAM during inference: ~3.2-3.3 GB
- Generation: `max_new_tokens=2048`, `do_sample=True`, `temperature=0.3`, `top_p=0.9`
- Runner: `scripts/benchmark_qwen35.py` (isolated; does not touch production Gemma)

> Note: production Gemma v2 uses `max_new_tokens=512`. Qwen3.5-4B almost never
> terminates within a 512 limit (see "Token behavior"), so 2048 was used here to
> give the model a chance to emit. This is a benchmark configuration choice and
> is recorded in every raw result.

## Method

- **Prompts**: 10 fixed descriptions - TEST 1-8 positive (named technologies: React,
  FastAPI, PostgreSQL, React Native, Express, Node.js, MongoDB, Vue.js, Django,
  MySQL, Next.js, Redis, S3, SQS, RabbitMQ, Prometheus, OAuth, Kong,
  Elasticsearch), TEST 9 generic ("frontend/backend/database", no technologies),
  TEST 10 compatibility-phrasing ("PostgreSQL-compatible", "AWS-compatible").
- **Runs**: 3 per prompt with distinct seeds → 30 generations.
- **Schema contract** (v3-oriented, experimental): canonical ids `ui-1/service-1/...`;
  node `type` from `{ui, service, database, cache, queue, container}`; nullable
  `technology` (set only when the description explicitly names it); edge `protocol`
  from `{HTTPS, SQL, Redis Protocol, message}` or null; caps 10 nodes / 15 edges.
- **Extraction**: richest-structure selection. All fenced/balanced/regex JSON
  candidates are parsed; the candidate with the highest `(nodes, edges)` score is
  selected. Same-score ties → run is flagged `ambiguous` instead of silently
  choosing. Complete raw output, the selected JSON, the candidate text, and the
  reasoning text are stored separately for every run (see Artifacts).

## Results

### Emission reliability

| Metric | Value |
| --- | --- |
| Total runs | 30 |
| Valid JSON emitted | 13 / 30 (43.3%) |
| Positive tests (TEST 1-8) valid | 10 / 24 (41.7%) |
| Negative tests (TEST 9-10) valid | 3 / 6 (50.0%) |
| Runs that never emitted JSON (kept reasoning to the 2048-token cap) | 17 / 30 (56.7%) |
| Runs that hit the 2048-token cap | 28 / 30 |

### Per-test summary

| Test | Valid | Nodes | Technologies (when emitted) | Fabrications | Missing |
| --- | --- | --- | --- | --- | --- |
| TEST 1 React/FastAPI/PostgreSQL | 3/3 | 3 | React, FastAPI, PostgreSQL | none | none |
| TEST 2 React Native/Express/MongoDB | 0/3 | - | (no emission) | - | all |
| TEST 3 Vue.js/Django/MySQL | 3/3 | 3 | Vue.js, Django, MySQL | none | none |
| TEST 4 Next.js/Node.js/Redis/PostgreSQL | 3/3 | 4 | Next.js, Node.js, Redis, PostgreSQL | none | none |
| TEST 5 React/S3/SQS | 0/3 | - | (no emission) | - | all |
| TEST 6 RabbitMQ/Prometheus | 0/3 | - | (no emission) | - | all |
| TEST 7 React/FastAPI/PostgreSQL/Redis/OAuth/Kong | 0/3 | - | (no emission) | - | all |
| TEST 8 React/FastAPI/Elasticsearch | 1/3 | 3 | React, FastAPI, Elasticsearch | none | none (on the valid run) |
| TEST 9 generic (negative) | 3/3 | 3 | all `null` | none | none |
| TEST 10 PostgreSQL-compatible / AWS-compatible (negative) | 0/3 | - | (no emission; fabrication unverifiable) | unverifiable | - |

### Quality when JSON was emitted

Every one of the 13 valid outputs was contract-compliant:

- Node ids were always canonical (`ui-1`, `service-1`, `database-1`, `cache-1`); 3-4
  nodes, 2-3 edges; never exceeded caps.
- Types always in `{ui, service, database, cache, queue, container}`.
- `technology` matched the description exactly on positive tests:
  - TEST 1: React / FastAPI / PostgreSQL; TEST 3: Vue.js / Django / MySQL;
    TEST 4: Next.js / Node.js / Redis / PostgreSQL; TEST 8: React / FastAPI / Elasticsearch.
  - **Zero fabricated technologies** anywhere. TEST 9 (generic) kept every node's
    `technology = null` - no invented frontend/backend/database technology.
- Protocols used: `HTTPS`, `SQL`, `Redis Protocol` - all within contract.

So: **given an emission, the output is clean.** The failure mode is *emission
itself*, not semantic corruption.

### Reasoning inflation and token behavior

- Average output length ~1,986 tokens per positive run; ~2,048 for negative runs.
  Only 2/30 runs stopped before the cap (TEST 1 runs 2-3 at 1,206 / 1,394 tokens).
- Average reasoning text ≈ 7.4-7.8 KB per run - the model writes a "Thinking
  Process:" essay (often several hundred words) before reaching the JSON.
- In 17/30 runs it never reaches the JSON at all: it enters a self-referential
  loop ("Wait, I need to check X... maybe I should use... I will output the JSON
  string directly...") and burns the whole 2048-token budget.
- Example (TEST 7 run 1, tail): planning to emit a `container-1` for Kong, then
  re-checking constraints; the JSON is never output before the cap.

### Timing

| Group | Avg generation | Avg tok/s |
| --- | --- | --- |
| Positive tests | 62.1 s | ~31.9 |
| Negative tests | 65.0 s | ~31.5 |

First token latency is dominated by the reasoning preamble; for a ~60 s/run cost,
up to 100% of tokens are reasoning in the failed runs.

## Comparison with Gemma v2 (production baseline)

| Dimension | Gemma v2 (prod) | Qwen3.5-4B (zero-shot) |
| --- | --- | --- |
| Emission reliability | Always emits JSON | 13/30 (43%) under 2048 cap |
| Token budget | 512 (never exceeded) | Nearly always needs >1,200; almost never stops early |
| Gen time per answer | ~12-47 s (≤512 tok) | ~62-65 s (≤2048 tok) |
| Throughput | ~20-21 tok/s warm | ~31-32 tok/s |
| Semantic identifiers | Never emitted (generic locked ids; 18/18 probe) | Emitted correctly whenever JSON appears |
| Technology field | v3 not present | Correct + zero fabrication when emitted |
| Correctness when emitted | Correct structure, generic ids | Correct structure, semids + tech, no fabrication |

The decision criteria specified for this benchmark were: (1) do not declare Qwen
superior merely because outputs look nicer, and (2) judge only whether Qwen3.5-4B
is a sufficiently strong base for a v3 fine-tune. By those criteria:

- **Not a production substitute** at any budget comparable to Gemma's: unchecked
  reasoning inflation makes it unusable unchanged at `max_new_tokens=512`.
- **No fabrication / solid semantics** when it does emit - the strongest point in
  favor of the base's factual grounding.
- **Emission instability** (56.7% no-emission due to reasoning loops) is the
  dominant risk if fine-tuning aims for tight structured output.

## Verdict: GO / NO-GO

- **Zero-shot production use: NO-GO.** 
- **v3 fine-tune base decision: CONDITIONAL / NOT CONFIRMED.** The benchmark does
  provide evidence the base *understands* component extraction and technology
  assignment precisely (zero fabrication, zero missing tech on every emitted
  graph). It equally demonstrates the base does not emit reliably under a bounded
  decode without further constraint. A v3 LoRA on Qwen is not ruled out by this
  data, but the go decision requires a small SFT/response-format probe before
  commitment - **not run here; this benchmark stops at reporting.** Without such a
  probe, v3-on-Qwen cannot be recommended over the current path.

## Nuances recorded (not scored as failures)

- TEST 9 (generic): `technology` correctly stayed `null`, but edge `protocol` was
  defaulted to HTTPS/SQL although the description gave no protocol. Benign inferred
  defaults, but a deviation from the strict "null when not indicated" rule.
- TEST 8 run 2: the FastAPI→Elasticsearch edge used `HTTPS` (Elasticsearch is
  served over HTTP); contract-conformant value, acceptable.
- TEST 5/6/7 sometimes discussed composing the graph (queue/S3/OAuth modeling)
  without emitting; the design choices in the verbal plan looked reasonable, which
  supports the "capability present, emission unstable" reading.

## Artifacts

- `dataset/docs/qwen35_zero_shot_benchmark.md` - this report
- `dataset/docs/qwen35_zero_shot_benchmark_raw.json` - aggregated results + all 30 run records
- `dataset/docs/qwen35_zero_shot_runs.jsonl` - full per-run records (complete raw
  output, `selected_json`, `candidate_raw`, `reasoning_text`, `selection` meta)
- `scripts/benchmark_qwen35.py` - isolated runner (no changes to production code,
  prompts, or model configuration)