# V2 Runtime Integration Report

**Status:** COMPLETE — runtime contract fixed, v2 adapter verified end-to-end through the
real backend API and the built frontend bundle. No retraining, no dataset changes, no
publication.
**Date:** 2026-08-25

## 1. Old vs new runtime contract

| Contract holder | Old | New |
|---|---|---|
| `architecture_schema.MAX_NODES` | 8 | **10** |
| `architecture_schema.MAX_EDGES` | 10 | **15** |
| `HARD_NODE_LIMIT / HARD_EDGE_LIMIT` (validator) | 10 / 15 | 10 / 15 (unchanged) |
| Parser behavior over limit | **silent truncation** (nodes sliced to 8, edge loop broken at 10) | **explicit ValueError** — output rejected, never silently dropped |
| `/explain` prompt caps | "Max nodes: 8 / Max edges: 10" + arbitrary-id FORMAT example (`frontend`/`api`) | "Max nodes: 10 / Max edges: 15" + canonical FORMAT example (`ui-1`/`service-1`) — matches the v2 training prompt exactly |
| Effective contract count | three conflicting contracts (prompt 8/10, parser 8/10, validator 10/15) | ONE contract: ≤10 nodes / ≤15 edges everywhere |

The dual-contract design (`MAX_*` vs `HARD_*`) is now intentionally collapsed into a single
contract; `raise_if_invalid` remains as defense-in-depth for architectures constructed
without the parser.

## 2. Every changed runtime location

1. `backend/core/architecture_schema.py` — `MAX_NODES = 10`, `MAX_EDGES = 15` (+ comment).
2. `backend/core/architecture_parser.py` — removed silent node slice (`[:MAX_NODES]`) and the
   mid-loop edge break; added explicit raises:
   - `Architecture exceeds node limit: N nodes > 10`
   - `Architecture exceeds edge limit: N edges > 15`
   Docstring updated. Normalization (dedupe ids, drop self-loops/dangling/duplicate directed
   edges) is unchanged — it is not truncation of valid content.
3. `backend/core/inference.py` — generation prompt caps 8/10 → 10/15 and FORMAT example
   `frontend/api` → `ui-1/service-1`, aligning the served prompt byte-for-byte with the v2
   adapter's training distribution.

Not changed (verified clean): `architecture_validator.py` (already 10/15), security engine
(`threat_detector.py`, `response_builder.py`, `architecture_enricher.py` — type/label-driven,
zero size references), `/healthz` and `/explain` handlers, frontend source.

## 3. Test adapter wiring

- v2 is the TEST adapter via env var only — no code default changed:
  `LORA_ADAPTER_PATH=checkpoints/gemma_lora_v2_canonical uvicorn backend.api.main:app`
- Default remains `checkpoints/gemma_lora` (untouched, sha256 `5ad8f378…`).
- Server startup: model load + smoke test OK; log at `dataset/docs/v2_runtime_server.log`.

## 4. Integration-test results (real v2 inference)

Unit-level parser contract checks:

| Case | Result |
|---|---|
| 10 nodes / 15 unique edges | passes untouched → returns exactly 10/15 |
| 11 nodes | explicit `ValueError: exceeds node limit` |
| 16 edges | explicit `ValueError: exceeds edge limit` |
| 8 nodes / 9 edges | parses normally |

Live API suite (`/tmp/opencode/v2_integration_test.py` against `127.0.0.1:8000`):

| Check | Result |
|---|---|
| `GET /healthz` | 200 `{"status":"ok"}` |
| `POST /explain` × 3 diverse prompts | all 200 |
| Returned graph size | **10 nodes every time** (raw model JSON counts == returned counts) |
| Edges returned | 9–12 (full set, never cut at 10) |
| `validation.valid` | true on all |
| Connectedness | `structurally_weak=false` on all; zero disconnected/orphan |
| Security object | produced on all: score/risk, aggregated threats, per-node `node_threats`, per-edge `edge_threats`, recommendations, missing_components, attack_surface, required_controls |
| Empty input | rejected explicitly (HTTP 422 by request validation) |
| **runtime_truncation_rate** | **0 / 3 requests = 0.0** (was 1.0 for v2 outputs before the fix) |

Sample live output (E-Commerce/Microservices/AWS): nodes
`database-1, database-2, service-1..7, ui-1`; validation clean; risk HIGH, score 25,
node/edge-level threat mapping present for every affected element.

### Over-limit failure safety

The model cannot be forced on demand to emit >15 edges, so the over-limit path was verified
at the parser unit level plus code path: `parse_architecture` raises → `generate_architecture`
retry loop treats it as a failed attempt → after retries a final `ValueError` → `/explain`
returns HTTP 422 with the explicit limit message. No silent drop path exists any more.

## 5. Before / after truncation behavior

| Scenario (v2 output) | Before fix | After fix |
|---|---|---|
| 10-node / 15-edge graph | truncated to 8 nodes / 10 edges, validator sees trimmed graph and passes | **delivered intact: 10 / 15** |
| 9-edge graph | nodes still cut to 8 | delivered intact |
| 11th node in raw JSON | silently dropped, no error | explicit failure (retry → 422 if persistent) |
| Corrected-eval metric `runtime_truncation_rate` | 1.0 (all 2,575 eval outputs were being cut at serve time) | **0.0** for valid ≤10/≤15 outputs |

This closes the last mismatch flagged in `canonical_v2_final_evaluation.md` §14.

## 6. Security-engine verification

- Engine untouched (no diff). Behavior re-verified live: `build_response` runs the canonical
  analyzer; `node_threats` maps each threat-affected node to its threat list (e.g.
  `database-1`: Log Evasion / Data Leakage / Data Tampering …), `edge_threats` likewise;
  risk level and score computed as before.
- Observed pre-existing semantics (NOT a regression): `node_threats` contains only
  *threat-affected* nodes — e.g. a `queue` node matched by no missing control gets no entry.
  Identical behavior for v1-style graphs; documented to avoid misreading the dict.

## 7. Frontend verification

- `npm run build` (tsc -b && vite build): **clean**, 2176 modules, dist emitted.
- Real browser E2E: unavailable in this environment (no Playwright/Cypress/browser binaries).
- Contract-level verification instead: the exact `/explain` payload satisfies the frontend's
  mirrored types — `architecture.nodes[]` with id/type (plus enricher icon/layer),
  `edges[]` with source/target/label (plus dashed), full `validation` and `security` blocks.
  All 10 nodes and all edges are present in the client-bound JSON, so ReactFlow receives the
  complete graph.
- Static serve smoke: built app + JS bundle return 200 via `vite preview`; app defaults to
  `http://127.0.0.1:8000` (the tested backend).

## 8. Remaining limitations

- True click-through browser E2E not executed (tooling absent); data-contract + build +
  static-serve verification substituted.
- Over-limit rejection exercised at parser/unit level; a live >15-edge model emission is rare
  (~0.04% during eval) and would surface as an explicit 422 after retries.
- The runtime system message ("strict JSON generator") differs slightly from the bare
  user-turn template used in training/eval; left as-is deliberately (pre-existing for both
  adapters), no fidelity issue observed across live calls.
- Non-deterministic sampling at runtime (temperature 0.3) means occasional retries can occur;
  all observed attempts succeeded within the existing retry budget.

## 9. Files touched (runtime only)

| File | Change |
|---|---|
| `backend/core/architecture_schema.py` | MAX_NODES 8→10, MAX_EDGES 10→15 |
| `backend/core/architecture_parser.py` | silent truncation → explicit ValueError ×2; docstring |
| `backend/core/inference.py` | prompt caps + FORMAT example aligned to v2 contract |

Artifacts: `dataset/docs/canonical_v2_final_test_eval.json` (eval baseline),
`dataset/docs/v2_runtime_server.log`, integration script preserved at
`/tmp/opencode/v2_integration_test.py`.

**STOP.** No publication, no pushes, no retraining. Awaiting review.