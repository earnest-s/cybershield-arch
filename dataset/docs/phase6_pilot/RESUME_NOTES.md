# Phase 6 — Subgraph Extraction Pilot: Status (COMPLETED)

## Final artifacts

- `dataset/scripts/extract_subgraphs.py` — permanent Phase 6 extraction script (v1.0.0).
  Canonical contract imported from `backend.core.architecture_schema`
  (HARD_NODE_LIMIT=10, HARD_EDGE_LIMIT=15), enforced with the runtime's own
  `raise_if_invalid` + `is_weakly_connected`. Nodes/edges are verbatim parent
  dicts (zero fabrication). Anchor-aware expansion (root + top-2 data anchors +
  top-2 security anchors connected via deterministic shortest-path BFS, then
  deterministic infill). Security re-derived via canonical
  `build_security_dict`; threats/attribution re-derived deterministically
  (`_deterministic_threats`) with the engine's own catalogs; `security_summary`
  rebuilt deterministically with canonical `build_security_summary`. Full
  provenance in `metadata.phase6`. Source opened read-only; SHA256 before/after.
- `dataset/docs/phase6_pilot/subgraph_pilot.jsonl` — 100 extracted records.
- `dataset/docs/phase6_pilot/subgraph_pilot_stats.json` — full pilot statistics.

## Pilot results (100 parents, deterministic stratified sample)

parents examined 100 | valid subgraphs 100 | rejected 0
node dist: 10/10 (all at contract headroom) | edge dist: 9–14, mean 9.70
connectedness 100% | entry/root retention 100% | data/storage retention 87% |
security-node retention 96% | provenance completeness 100%
duplicates 0/0 | fabricated 0 nodes / 0 edges | rejection reasons: none
source SHA256 unchanged: `e3ee9810e13ba660f6f39b93f35e318aa26f22eccf5b7ea59c57ef05f5a1b36b`

## Determinism

5 runs (PYTHONHASHSEED=0, =42, and 3 unseeded/random) all byte-identical:
SHA256 `dfa50bac405c719e257883e346a2e6e874e7104cee24b7472890778a5abf4af7`.

Resolved issue: engine's `build_threat_node_mapping` attributes threats
first-wins over a set-ordered control list (DDoS -> API Gateway vs WAF flip).
Fixed in the extraction layer via `_deterministic_threats` (sorted control
iteration, engine catalogs verbatim, no engine modification).

## Independent audit (value-based, external script)

All 7 proofs pass for 100/100 records: node subset, edge subset (multiset),
endpoint retention, weak connectivity, canonical contract validation,
provenance completeness (incl. selected_node_ids/edge_ids matching the graph),
determinism. Security record shape verified (all 8 corpus fields present).

## Not done (per instructions)

No full-scale extraction, no SFT artifact, no splits, no lora_train.py changes,
no backend limit changes, no training, immutable FULL corpus untouched.