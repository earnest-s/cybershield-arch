# Phase 6 — Subgraph Extraction Pilot: Resume Notes (PAUSED)

Paused for review. Everything below is the state at pause time. Resume here.

## What exists now

- `dataset/scripts/extract_subgraphs.py` — permanent Phase 6 script (v1.0.0).
  - Compiles, `--help` works. Canonical contract imported from
    `backend.core.architecture_schema` (HARD_NODE_LIMIT=10, HARD_EDGE_LIMIT=15).
  - Enforcement via runtime's own `raise_if_invalid` + `is_weakly_connected`.
  - No fabrication: nodes/edges are verbatim parent dicts.
  - Anchor-aware expansion: root + top-2 data anchors + top-2 security anchors,
    connected via deterministic shortest-path BFS, then infill to limit.
  - Security re-derived via canonical `build_security_dict` (same call as
    `enrich_dataset.py`); `security_summary` rebuilt deterministically with the
    canonical `build_security_summary` over sorted controls.
  - Full provenance (`metadata.phase6`): parent ids, method/version, selected
    node/edge ids, retention ratios, contract reference.
  - Read-only source access; SHA256 before/after computed and asserted.
- Pilot artifacts (run with `PYTHONHASHSEED=0`, sample-size 100):
  - `dataset/docs/phase6_pilot/subgraph_pilot.jsonl` (100 records)
  - `dataset/docs/phase6_pilot/subgraph_pilot_stats.json`
  - Seed-doubles kept in `/tmp/opencode/`: `subgraph_pilot_rerun.jsonl` (seed 0),
    `subgraph_pilot_seed42.jsonl` (seed 42), `subgraph_pilot_randomsalt.jsonl`,
    `subgraph_pilot_stats_randomsalt.json`.
- Source corpus SHA256: `e3ee9810e13ba660f6f39b93f35e318aa26f22eccf5b7ea59c57ef05f5a1b36b`
  (unchanged in every run, verified by the script).

## Pilot numbers (final code, 100 parents, seed 0 — GREEN so far)

- parents examined: 100  |  valid subgraphs: 100  |  rejected: 0
- node distribution: 10 nodes in 100/100 (all at contract headroom)
- edge distribution: min 9, max 14, mean 9.69
- connectedness: 100%  |  entry/root retention: 100%
- data/storage retention: 87% (up from 37% after anchor-aware expansion)
- security-node retention: 96%  |  provenance completeness: 100%
- duplicates: record_ids 0, edge_keys 0  |  fabricated nodes 0, fabricated edges 0
- rejection reasons: none (0 rejected)

## OPEN ISSUES (must fix before declaring the pilot final)

1. **Residual nondeterminism (HIGH)**: byte-identical output between seed 0 and
   seed 42, BUT the unseeded (random hash seed) run has a different SHA256
   (`5935cfe...` vs `11e1259...`). Diff shows `security.threats` ordering (or
   possibly content) differs in 8 records (e.g., CSA-000003#S1, CSA-000011#S1,
   CSA-000057#S1, CSA-000108#S1, CSA-000120#S1, CSA-000129#S1, CSA-000280#S1,
   CSA-000321#S1). First pause-time check: does the threats LIST CONTENT differ
   (different threat name sets) or only order? `_canonicalize_security` sorts by
   `(missing_control, name)` — if content differs, the engine's
   `detect_missing_security_components` / `analyze_architecture_security`
   (set-based, `missing_to_add`) must be returning different control SETS across
   hash seeds (could be `detect_architecture_types` ordering affecting
   `current_missing` merge). Then canonicalize the content-level source, and/or
   compare per-record threat name multisets between artifacts to confirm.
2. **Independent audit false positives (MEDIUM)**: my external audit flagged
   `edge_subset` on ~98 records — but that check used Python object identity
   (`e is pe`) across a JSON round-trip, which always fails post-serialization.
   Re-audit by VALUE (canonical edge key sets/frozensets:
   `(source, target, label)` membership in parent edge key multiset) — script's
   in-process `verify_subgraph` (identity-based) is correct by construction.
3. After fixing #1: regenerate the canonical artifact (seed 0), rerun the
   seeded double, rerun issue-1 salt check until all three SHA256s match, then
   rerun the value-based independent audit.

## Not done (per instructions — do NOT do without approval)

- No full-scale extraction (51,498 records), no SFT artifact, no splits,
  no `lora_train.py` changes, no backend limit changes, no training, no
  modification of the immutable FULL corpus.

## How to resume

1. `uv run python -m py_compile dataset/scripts/extract_subgraphs.py`
2. Inspect threats content diff per record (issue 1) and fix canonicalization.
3. Regenerate artifacts + rerun determinism triple-check (seed0 == seed42 == unseeded).
4. Rerun value-based independent audit (issue 2) until all proofs pass.
5. Deliver the PHASE 6 PILOT REPORT with final numbers.