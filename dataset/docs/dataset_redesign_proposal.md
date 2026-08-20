# Dataset Redesign Proposal — SFT Representation for Structural Fidelity

**Status:** PROPOSAL — read-only investigation complete; no pipeline, dataset, or model
changes have been made. Execution of anything proposed here requires separate approval.

**Date:** 2026-08-20

## 1. Summary

The Phase 8 final model (Gemma 3 4B + LoRA, `checkpoints/gemma_lora`) produces
structurally valid but content-inaccurate architectures: node F1 0.224, edge F1 0.065,
exact match 0.0. Phase 8 attributed the plateau to "arbitrary per-record naming
conventions in non-canonical emission order." This investigation re-measures the actual
SFT artifact and confirms that diagnosis is correct — and finds it is **understated**:

1. **Naming is nearly 100% arbitrary.** 94.4% of node-id occurrences appear in exactly
   one record (28,703 unique ids over 509,725 slots). No description→name mapping exists
   to learn.
2. **Emission order is nearly 100% arbitrary.** Only 1.0% of node lists and 3.0% of edge
   lists are sorted; 0.0% are in (type, id) order. Order is a Phase 6 score-priority
   artifact, different for every record.
3. **The target mapping is not even deterministic for 1.4% of records.** 358 duplicated
   instructions (723 records) map to >1 distinct architecture, and 428 node-set clusters
   (1,771 records, 3.4%) carry identical node ids with different edge sets.
4. **NEW — the shipped artifact contradicts its own prompt.** 100% of instructions say
   "Max nodes: 8 / Max edges: 10", but 97.8% of targets exceed 8 nodes (up to 10) and
   14.7% exceed 10 edges (up to 15). The prompt, the validator guardrail (≤10/≤15), and
   the target distribution are three different contracts.
5. **NEW — integrity finding: the baseline metrics are not reproducible from this repo.**
   The evaluation JSON's target statistics (avg 7.93 nodes) do not match the shipped
   artifact's test split (avg 9.884 nodes, 97.2% at 10 nodes), despite identical record
   ids and instructions. The training and evaluation were performed against an older
   8-node-era artifact that is no longer present anywhere in the repo.

**Recommendation (Section 6):** a hybrid representation redesign — fix the prompt/contract
mismatch, canonicalize the target representation (deterministic type-anchored ids + sorted
emission), preserve provenance via a documented id mapping, deduplicate cluster-wise, and
switch evaluation to dual name-level/structure-level metrics. **Before any retraining, the
artifact must be re-verified and a fresh baseline established**, because the current
reported numbers describe a different artifact than the one the repo ships.

Validate via a 3-variant pilot ablation (Section 7) before committing to a full rerun.

## 2. Scope and guardrails

This document is a proposal only. The investigation that produced it was strictly
read-only: no file in the repo was modified, no training was started, and the SFT
artifact was only read (and regenerated to `/tmp` for byte-comparison).

Boundaries for any approved execution:

| Layer | Status | Rationale |
|---|---|---|
| `dataset/final/*` (immutable corpus) | **Never touch** | Provenance root; all downstream artifacts derive from it |
| Phase 6 extraction (`extract_subgraphs.py`) | Never touch | Deterministic, verified, provenance-preserving; the graph *content* is correct — the problem is representation, not extraction |
| Backend runtime (`inference.py`, validator, security engine) | Never touch | The validator's ≤10/≤15 guardrail is the runtime contract; the security engine is type/label-driven and unaffected by id naming |
| Phase 7 SFT renderer (`format_sft.py` + `PROMPT_TEMPLATE`) | **Mutable (proposed)** | This is the redesign layer |
| SFT artifact (gitignored, regenerable) | **Mutable (proposed)** | Byte-deterministic output of the renderer; regenerable |
| Eval scripts + metric definitions | **Mutable (proposed)** | Need dual-metric (name-level + structure-level) evaluation and an artifact-hash preflight |

## 3. Current state — measured evidence

All numbers below were measured on 2026-08-20 directly from
`dataset/training/CyberShield_Gemma_SFT_v1.jsonl` (SHA-256 `2a0820104c676833cc65550eb5b1e70a6eae56e7`,
200,254,229 bytes), which was confirmed to be the **byte-identical** output of the current
pipeline (`format_sft.py` regeneration hash `227dcb5b…` matches).

### 3.1 Artifact composition (n = 51,498; splits 46,348 / 2,575 / 2,575)

| Property | Measurement |
|---|---|
| Node-count distribution | 2:58, 3:104, 4:175, 5:191, 6:165, 7:229, 8:207, 9:297, **10: 50,072 (97.2%)**; avg 9.898 |
| Edge-count distribution | mode **9 (31,324, 60.8%)**, avg 9.514, max 15 |
| Duplicate instructions | 358 groups (723 records, 1.4%); **all 358 map to >1 distinct architecture and >1 distinct edge set** |
| Node-id vocabulary | 28,703 unique ids over 509,725 slots → **94.4% of id occurrences are singletons**; 10,557 ids reused (36.8% of vocab) |
| Id case styles (by id) | other 42.3%, ALL_CAPS 30.1%, camelCase 19.2%, lower_underscore 8.5%; 81% of records contain ≥1 ALL_CAPS id, 49% ≥1 "other" |
| Node-list sorted | 1.0% (alphabetical); **0.0% by (type, id)** |
| Edge-list sorted | 3.0% |
| Node-set clusters | 49,975 distinct; 530 multi-record (2,053 records); 398 clusters (1,684 rec.) share ids with >1 **ordering**; 428 clusters (1,771 rec., 3.4%) share ids with >1 **edge set** |
| WL-1 canonical structures | 41,370 distinct / 51,498 (80.3% uniqueness); top-10 cover 4.4%; 172 structures ≥10 occurrences (11.2% of records) |
| Node types | service 61.0%, ui 17.4%, database 13.3%, queue 4.7%, container 1.9%, cache 1.8% |
| Edge labels | **HTTP 95.4%**, Async 2.9%, Cache 1.1%, **DB Query 0.5%** (2,589 edges vs 67,531 database nodes) |
| Domains / styles / clouds / complexity | 42 / 8 / 6 / 4 tiers, near-uniform (max domain share 2.6%) |

### 3.2 Contract inconsistency (artifact-internal bug)

| Claimant | Node cap | Edge cap |
|---|---|---|
| `PROMPT_TEMPLATE` (100% of instructions) | Max **8** | Max **10** |
| Actual targets | 97.8% have >8 (up to 10) | 14.7% have >10 (up to 15) |
| Validator guardrail (`architecture_validator.py`, runtime) | ≤10 | ≤15 |
| Phase 6/7 docs (spec, reports) | 10 | 15 |

The model is prompted with "Max nodes: 8" and trained on 97.2% ten-node targets. Its
generated outputs (eval avg 8.0 nodes, max 8) show it **obeyed the prompt**, not the
targets. Any evaluation or training on the current artifact inherits this contradiction.

### 3.3 Baseline reproducibility (integrity finding)

Proof chain, all measured:

1. `phase8_final_test_eval.json` (config: adapter `checkpoints/gemma_lora`, split `test`,
   n=2,575) reports `avg_target_nodes 7.93`, `avg_target_edges 7.26`, and node_tp+node_fn
   = 20,430 total target nodes.
2. The current test split contains 25,445 target nodes (avg 9.884; 2,503/2,575 records
   with exactly 10 nodes).
3. All 2,575 eval output ids exist in the current test split (identical records and
   prompts), but **2,518/2,575 have a different target node count** than the eval's
   per-record (tp+fn).
4. `git diff backup/pre-rewrite-4f026755` shows **no changes** to `format_sft.py`,
   `extract_subgraphs.py`, any phase7/8 doc, `lora_train.py`, or `phase8_generate_eval.py`
   — the pipeline and its reports were carried into the current history unchanged.
5. The artifact is gitignored (regenerable), so the swap is invisible to git; no other
   copy of any SFT artifact exists anywhere on disk.
6. The pre-rewrite history contains the trained adapter at
   `release/huggingface/adapter_model.safetensors` (178,885,992 bytes = the
   `checkpoints/gemma_lora` adapter, trained 2026-08-19 09:15).

**Conclusion:** the reported node/edge F1 baseline, the adapter weights, and the eval
JSON describe an **8-node-era artifact** (98.2% @ 8 nodes, mode 7 edges — matching the
Phase 8 tuning report's characterization). The repo currently ships a **10-node artifact
that has never been trained on or evaluated**. The baseline is not reproducible from this
repo, and no current claim of model quality can be made against the shipped artifact.

## 4. Root-cause analysis (ranked)

| # | Cause | Magnitude (measured) | Effect |
|---|---|---|---|
| 1 | Arbitrary emission order | 99% of targets non-sorted; 0% in (type,id) order | Model must memorize an order it can never predict; order noise dominates edge learning (edge F1 0.065) |
| 2 | Arbitrary id naming | 94.4% singleton occurrences; 5 case styles mixed per record | No learnable description→name mapping; node F1 ceiling ≈ type-matching rate (~0.22 observed) |
| 3 | Prompt/contract/target mismatch | 97.8% targets >8 nodes vs prompt cap 8; 14.7% >10 edges | Model caps output at 8 nodes; count conditioning actively misled |
| 4 | Non-deterministic targets | 1.4% duplicate instructions → different targets; 3.4% identical id-sets → different edge sets | Irreducible noise floor for exact match even with a perfect model |
| 5 | Label/type skew | HTTP 95.4%, DB Query 0.5% | Rare labels (DB Query, Cache) underlearned; edge label diversity collapses |
| 6 | Saturation + low redundancy | 97.2% @ 10 nodes; 80.3% structural uniqueness | No distribution to learn beyond "10 nodes"; dedup alone cannot rescue the corpus |
| 7 | (Integrity) Baseline vs shipped artifact mismatch | 2,518/2,575 records differ | Any reported metric is unverifiable against the repo state |

Causes 1–2 were identified by Phase 8; causes 3 and 7 are new findings of this
investigation. Causes 1, 3 are **fully removable**. Cause 2 is **unlearnable by
construction** (ids are invented per record and never appear in the prompt) — the only
rational response is to stop asking the model to reproduce invented names and instead
evaluate structure. Cause 4 is a hard floor that must be quantified and reported.

## 5. Representation strategies

| Strategy | Ids | Emission order | Fixes | Fidelity ceiling | Runtime/provenance impact |
|---|---|---|---|---|---|
| **A. Current** (verbatim Phase 6 target) | original, arbitrary | Phase 6 score order | — | node F1 ~0.22 (name-level), edge F1 ~0.065, exact 0% | none |
| **B. Order-canonicalized** (ids preserved) | original | sorted (type, id); edges sorted (s,t,label) | cause 1 | name-level ceiling unchanged (~0.22); edge F1 improves (order noise removed); exact match still ~0 (names unlearnable) | none; ids still display-valid |
| **C. Type-anchored canonical** | `{type}-{n}` derived deterministically from the graph (e.g. `ui-1`, `service-2`, `database-1`) | sorted by (type, id) | causes 1, 2 | node F1 measures **type fidelity** (learnable; target 0.6+); edge F1 measures **structure fidelity** (target 0.25+); exact match = structure match (target 10%+) | none in backend: validator checks types/labels/connectivity only; security engine is type/label-driven (id used for display + a weak keyword heuristic — canonical ids slightly *reduce* false keyword hits); id→original mapping kept in metadata for provenance + name-level eval |
| **D. Two-stage generation** (nodes block, then edges block; explicit count conditioning) | as B or C | as B or C | causes 1, 2, 6 | potentially highest (explicit count + structure decomposition) | **requires backend changes** (prompt/parse/runtime contract); out of scope here |
| **E. Hybrid = C + prompt fix + cluster-wise dedup + dual metrics** (recommended) | type-anchored | sorted | causes 1, 2, 3; mitigates 5, 6, 7 | as C, plus: dedup removes ~20% redundant exposure; prompt fix unblocks count conditioning; dual metrics make gains measurable | backend untouched; renderer + eval scripts only |

Notes:
- **Names are display-only in the product.** The validator, security engine, and
  threat analysis operate on node types, edge labels, and connectivity. Nothing in the
  runtime consumes id semantics (verified in `backend/core/architecture_validator.py`,
  `backend/security/threat_detector.py`). Canonical ids therefore carry zero information
  loss for every downstream consumer; the frontend renders ids as labels (cosmetic; a
  future mapping-back is trivial via the metadata id-map).
- Strategy D is the only one with a plausibly higher ceiling than C, but it changes the
  runtime contract and is intentionally deferred (Section 8, future work).
- Rebalancing (cause 5) is **not** proposed: altering target labels/edges would
  fabricate structure absent from the immutable corpus. Label skew is instead mitigated
  by prompt emphasis and reported as a known distribution property.

## 6. Recommendation — Hybrid redesign (E)

### 6.1 Target encoding (canonical form)

For each subgraph (graph content unchanged, ordering + naming only):

1. **Node ids**: assign `{type}-{k}` where nodes are first sorted by (type, id) and `k`
   enumerates within type, e.g. `ui-1`, `service-1`, `service-2`, `database-1`. The
   mapping `{original_id -> canonical_id}` is stored in the record's metadata.
2. **Emission order**: nodes in (type, canonical-index) order; edges sorted by
   (source, target, label).
3. **Prompt**: keep the exact runtime template but fix the caps to the validator
   contract — "Max nodes: 10 / Max edges: 15" — and add one line: *"Use the
   role+number naming style for components, e.g. service-1, database-2."*
4. **Dedup**: cluster-wise exact dedup on (instruction, canonical target) — clusters of
   identical records collapse to one representative (expected reduction ~20%, preserving
   split structure and leakage safety). The phase7 spec's cluster-wise 90/5/5 split
   logic is reused unchanged.
5. **Metadata**: add `canonicalization` = {method, version, id_map} to each record for
   full provenance and to enable name-level evaluation and display mapping.

### 6.2 Evaluation (dual metrics)

| Metric | Definition | Meaning |
|---|---|---|
| Name-level node F1 / edge F1 (legacy) | F1 vs the *original* target ids via id_map | retained for continuity; expected to stay low (0.2-ish) — names are unlearnable by design |
| **Structure-level node F1** | F1 over (type, count) inventory: node matches = same type | primary fidelity metric; measures component inventory |
| **Structure-level edge F1** | F1 over edge (source-type, target-type, label) multiset, matched greedily on canonical ids | primary fidelity metric; measures topology+labels |
| Canonical exact match | exact canonical graph equality | the new "exact" gate |
| Contract validity / connectedness / parse / repetition | unchanged | runtime-quality gates |
| Artifact hash preflight | eval refuses to run unless the artifact hash matches the trained/evaluated artifact | prevents recurrence of §3.3 |

### 6.3 Integrity remediation (prerequisite, not optional)

Because the shipped artifact was never the trained/evaluated artifact:

1. Pin the artifact: record its hash in the phase7 spec and in `verify_sft.py` output
   (`verify_sft.py` already exists — add hash pinning).
2. Re-baseline: evaluate the **existing** adapter against the *current* artifact (test
   split) and publish the result before any redesign work is judged. Expect it to
   differ materially from the reported 0.224/0.065 (prompt caps at 8 nodes; targets
   have 10).
3. If the existing adapter is ever re-uploaded or re-evaluated, do it against the
   pinned artifact only.

## 7. Pilot experiment design (approval-gated)

Purpose: measure whether canonicalization moves fidelity before committing to a ~13 h
full rerun. Cost: 3 short LoRA runs + evals (≈1–2 h each on the RTX 4050-class GPU).

**Sample** (deterministic, leakage-safe): reuse the split machinery — 800 train-cluster
records + 200 held-out test-cluster records from the current artifact.

| Variant | Target encoding | Prompt |
|---|---|---|
| A (control) | current, verbatim | current (max 8/10) |
| B | original ids, sorted emission | fixed caps (max 10/15) |
| C | type-anchored canonical ids, sorted emission | fixed caps + naming instruction |

**Training config:** identical to the final run (E2b: r24/α48, lr 2e-4, 1 epoch,
4-bit base, same seed/split logic) — isolates representation as the only variable.

**Metrics per variant:** parse rate, contract validity, connectedness, repetition,
structure-level node F1 / edge F1, canonical exact match, name-level F1 (informational),
plus a label-coverage breakdown (HTTP / Async / Cache / DB Query).

**Success gates for recommending C at full scale:**

| Metric | A (expected) | C (required) |
|---|---|---|
| Structure-level node F1 | ~0.22–0.3 | ≥ 0.6 |
| Structure-level edge F1 | ~0.1–0.15 | ≥ 0.25 |
| Canonical exact match | ~0 | ≥ 0.10 |
| Contract validity | 1.0 | ≥ 0.999 |
| Connectedness | 0.9996 | ≥ 0.999 |

**Determinism:** renderer must remain byte-deterministic (no RNG); artifact hash
recorded before and after the pilot transformation.

**Deliverables of the pilot:** a short report (`dataset/docs/redesign_pilot.md`) with
the three variant tables, the gate results, and the go/no-go recommendation. No
full-scale training without a passing gate.

## 8. Full-scale execution plan (post-approval, post-pilot)

1. Fix `PROMPT_TEMPLATE` caps (10/15) + naming instruction in `format_sft.py`.
2. Implement canonicalization + id-map metadata + cluster-wise dedup in `format_sft.py`
   (new transform version, e.g. `canonical_v2`), keeping the old renderer behind a flag.
3. Regenerate artifact; verify with `verify_sft.py` + hash pinning; document the diff
   (record counts, structure counts) in the phase7 spec.
4. Re-baseline existing adapter against the new artifact (per §6.3).
5. Train full run (E2b config, 1 epoch) on the canonical artifact; evaluate with dual
   metrics + hash preflight; update phase8 docs with structure-level results and
   explicit name-level caveats.
6. Update README metrics with the new, reproducible numbers.
7. Future work (not in this scope): Strategy D two-stage generation; display
   mapping-back of canonical ids via the metadata id-map; label rebalancing *only* if a
   future corpus (not the immutable Phase 6 pool) is introduced.

## 9. Risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Canonicalization does not lift structure-level F1 above gates | Medium | Pilot gates gate the full run; A/B/C design makes the failure informative and cheap |
| id_map metadata inflates artifact size / slows load | Low | id_map is small (≤10 pairs/record); only stored on original, name-level eval optional |
| Dedup changes distribution enough to affect convergence | Low | Cluster-wise dedup keeps all distinct structures; count of unique structures (41,370) unchanged |
| The 1.4% / 3.4% non-deterministic-target noise floor caps exact match | Certain (floor exists) | Quantify and report it as a documented ceiling in eval docs; exact-match gate set accordingly |
| Label skew (DB Query 0.5%) keeps edge-label recall low | High | Prompt emphasis; report label breakdown; consider minor up-weighting of DB Query examples *if* done without fabricating content |
| New artifact/training/eval drift recurs (integrity finding) | High | Artifact hash pinning + eval preflight (§6.3) become mandatory repo practice |

## 10. References

- `dataset/scripts/format_sft.py` (renderer; prompt template caps to fix)
- `dataset/scripts/extract_subgraphs.py` (Phase 6 extraction — content source, untouched)
- `dataset/scripts/verify_sft.py` (verification entry point; add hash pinning)
- `dataset/docs/phase7_training_spec.md`, `phase7_training_report.md`
- `dataset/docs/phase8_training_tuning_report.md`, `phase8_final_evaluation.md`,
  `phase8_final_test_eval.json` (baseline claims; §3.3 shows they describe the 8-node era)
- `backend/core/architecture_validator.py`, `backend/security/threat_detector.py`
  (type/label-driven runtime — names are display-only)
- `backend/training/gemma/phase8_generate_eval.py` (add hash preflight + dual metrics)
- Measurement scripts (analysis performed read-only; artifacts outside the repo):
  `/tmp/opencode/analyze_sft.py`, `/tmp/opencode/check_test_split.py`,
  `/tmp/opencode/check_response2.py`, `/tmp/opencode/check_prompt_contract.py`,
  `/tmp/opencode/sft_regen.jsonl` (byte-identical regeneration check)

---

*End of proposal. No repository files were modified by this investigation.*