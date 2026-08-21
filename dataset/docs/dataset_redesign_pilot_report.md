# Dataset Redesign Pilot Report

**Status:** PILOT COMPLETE — experimental A/B/C ablation on 800 train / 100 validation
records. No full-scale training performed. No source artifact, adapter, runtime, or
frontend was modified.
**Date:** 2026-08-20

## 1. Objective

Test whether the proposed canonicalized SFT representation (redesign proposal §5–§7)
improves structural fidelity enough to justify a future full dataset redesign and
retraining — before spending the ~13 h full run. The pilot measures the *relative*
effect of representation (A/B/C) under otherwise identical training conditions, and
compares the results against the trustworthy corrected full-run baseline.

## 2. Baseline (trustworthy, corrected)

Measured in `dataset/docs/phase8_corrected_test_eval.json` (same generation settings,
FULL untruncated targets; see `dataset/docs/phase8_corrected_evaluation.md`):

| Metric | Full-run baseline (2,575 test) |
|---|---|
| Parse rate | 1.0 |
| Contract-valid (≤10/≤15) | 0.988 |
| Connected | 0.9996 |
| **Node F1** (name-level, exact ids) | **0.2370** |
| **Edge F1** (name-level, exact keys) | **0.0688** |
| Exact match | 0.0 |
| Repetition | 0.0 |
| Mean generated / target nodes | 10.01 / 9.88 |
| Mean generated / target edges | 9.21 / 9.51 |

## 3. A/B/C definitions

| Variant | Representation | Prompt | Purpose |
|---|---|---|---|
| **A (control)** | current, verbatim (original arbitrary ids, Phase 6 emission order) | current template (Max nodes: 8 / Max edges: 10) | reproduce the current pipeline on the pilot subset |
| **B (canonical ID/order normalization)** | type-anchored canonical ids `{type}-{k}`, deterministic node + edge ordering, types/labels/topology preserved, provenance via id_map | caps fixed to 10/15; FORMAT example uses role+number ids | isolate the effect of canonicalization + contract fix |
| **C (hybrid)** | identical to B | B + explicit naming-instruction line in CONSTRAINTS | isolate the marginal effect of explicit naming guidance (proposal §6.1.3 E) |

Cluster-wise dedup (part of proposal E) is **deferred to full scale** — the pilot keeps
identical record sets across A/B/C so the only variable is representation.

## 4. Exact transformation rules

Same 900 source records (800 train + 100 validation) for all three variants; only the
encoding differs.

**A**: `instruction`, `response`, `architecture` copied verbatim from the source artifact.

**B** (pure function of the record; no RNG):
1. Node ids: sort nodes by `(type, original_id)`; within each type enumerate 1-based →
   `{type}-{k}` (e.g. `service-1`, `service-2`, `database-1`). Original id→canonical id
   stored as `metadata.canonicalization.id_map`.
2. Node emission order: `(type, canonical_id)` (i.e., enumeration order).
3. Edge emission order: sorted by `(source, target, label)` after id remapping.
4. Types, labels, topology unchanged (edges remapped only through id_map).
5. Prompt: `- Max nodes: 8`→`- Max nodes: 10`; `- Max edges: 10`→`- Max edges: 15`;
   FORMAT example `frontend/ui`→`ui-1`, `api/service`→`service-1`.

**C**: everything in B, plus a CONSTRAINTS line
`- Use the role+number naming style for components, e.g. service-1, database-2`
inserted after `- Max edges: 15`.

## 5. Dataset / provenance guarantees

- Source artifact read-only; SHA-256 `8c91e5cd017df949…` recorded in every pilot record's
  `metadata.source_sha256`.
- Subset selection: `random.Random(42)` sampling of sorted id lists (800 from train,
  100 from validation); cross-split instruction-cluster leakage = 0 (verified); the three
  variants share the exact same 900 `source_id`s (verified).
- Pilot artifacts (separate files, never overwriting the source SFT):
  - `dataset/pilots/redesign_A.jsonl`
  - `dataset/pilots/redesign_B.jsonl`
  - `dataset/pilots/redesign_C.jsonl`
- Each record carries: `source_id`, `pilot_variant`, `pilot_version`, `source_sha256`,
  `original_architecture` (for name-level eval and provenance), and for B/C the full
  `id_map`. No fabricated nodes or edges: B/C only relabel and reorder the source graph
  (bijection verified: `set(id_map.keys()) == original node ids`,
  `set(id_map.values()) == canonical node ids`).
- Transformations are deterministic pure functions (verified by regeneration equality).

## 6. Training configuration

Identical across variants; matches the final E2b run per proposal §7:

- Base: `unsloth/gemma-3-4b-it-bnb-4bit` (4-bit NF4, frozen), LoRA r=24 / α=48,
  dropout 0.05, target `model.language_model.*(q/k/v/o/gate/up/down)_proj`.
- 1 epoch, batch 1, grad-accum 8 (100 optimizer steps), AdamW8bit lr 2e-4,
  cosine + 10 warmup steps, seed 42, max_length 1024, prompt tokens masked from loss.
- Adapters (new, never overwriting `checkpoints/gemma_lora` / `gemma_lora_pilot`):
  - `checkpoints/redesign_pilot_A`
  - `checkpoints/redesign_pilot_B`
  - `checkpoints/redesign_pilot_C`

| Variant | Train avg_loss | Val eval_loss |
|---|---|---|
| A | 0.4301 | 0.3088 |
| B | 0.1699 | 0.1102 |
| C | 0.1674 | 0.1100 |

B/C converge far better: the canonical target is learnable; the arbitrary-name target is
not (the loss gap is the mechanism behind the metric gap).

## 7. Evaluation methodology

`backend/training/gemma/phase8_redesign_pilot_eval.py` — the corrected methodology
(non-truncating `normalize_full`, FULL verbatim targets, contract on the full generated
graph, greedy/seed 42/rep 1.1/ngram 0/768 tokens/batch 3) plus dual metrics per proposal
§6.2:

- **Structure-level (primary):** node F1 over the (type) inventory; edge F1 over the
  (source-type, target-type, label) multiset; canonical exact match. Representation-
  independent; these are the proposal's success-gate metrics.
- **Name-level (legacy, directly comparable to the baseline):** exact node-id set F1 and
  exact edge-key set F1 in the variant's own encoding.
- For B/C an informational original-name score is computed via `id_map`
  (note: with canonical ids this is set-equivalent to the structure-level node score, so
  it is not an independent semantic-re-identification metric).

Evaluated on the **same 100 held-out validation records** (never in any pilot training).
A fourth run evaluates the existing full adapter `checkpoints/gemma_lora` on the same
records (`redesign_A.jsonl`) as the current-representation reference at full training
scale. Eval artifacts: `dataset/docs/redesign_pilot_{A,B,C,ref}_eval.json`.

## 8. Results table (n = 100 validation records)

| Metric | A (800-rec control) | B (canonical) | C (hybrid) | REF (full gemma_lora, current rep) | Full-run baseline (2,575 test) |
|---|---|---|---|---|---|
| Parse rate | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| Schema-valid (full graph) | 0.04 | **1.0** | 1.0 | 0.98 | 0.988 |
| **Contract-valid (≤10/≤15)** | 0.04 | **1.0** | 1.0 | 0.98 | 0.988 |
| **Connected** | 0.98 | **1.0** | 0.95 | 1.0 | 0.9996 |
| Structurally weak | 0.02 | 0.0 | 0.05 | 0.0 | 0.0004 |
| **Node F1 — structure (types)** | 0.7203 | **0.7903** | 0.7903 | 0.7543 | (not measured) |
| Node precision / recall (structure) | 0.6427 / 0.8191 | 0.7840 / 0.7967 | 0.7840 / 0.7967 | 0.7475 / 0.7612 | — |
| **Edge F1 — structure (type-pair,label)** | 0.556 | **0.6302** | 0.6254 | 0.6328 | — |
| Edge precision / recall (structure) | 0.5004 / 0.6254 | 0.6350 / 0.6254 | 0.6254 / 0.6254 | 0.6349 / 0.6308 | — |
| **Node F1 — name-level (exact ids)** | 0.2243 | **0.7903** | 0.7903 | 0.2246 | 0.2370 |
| **Edge F1 — name-level (exact keys)** | 0.0813 | **0.1518** | 0.1539 | 0.0691 | 0.0688 |
| Exact match (canonical / structure) | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.01 / 0.0 | 0.0 |
| Repetition failure | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Mean generated / target nodes | 12.54 / 9.84 | **10.0 / 9.84** | 10.0 / 9.84 | 10.02 / 9.84 | 10.01 / 9.88 |
| Mean generated / target edges | 11.61 / 9.29 | 9.15 / 9.29 | 9.29 / 9.29 | 9.23 / 9.29 | 9.21 / 9.51 |
| Node / edge count error | 2.72 / 2.44 | **0.16 / 0.66** | 0.16 / 0.88 | 0.18 / 0.68 | 0.13 / 0.82 |
| Max generated nodes / edges | 17 / 16 | 10 / 10 | 10 / 14 | 11 / 13 | 11 / 14 |
| Size-guardrail issues | 96 | 0 | 0 | 2 | 31 |

## 9. Error analysis

- **A (800-record control) is severely undertrained and is NOT a fair "current
  representation" control at 800 records.** It never learns the node cap (96/100 outputs
  exceed 10 nodes, max 17; contract-valid 4%) and its loss plateaus high (0.309). The
  arbitrary-name + arbitrary-order task is too hard to learn from 800 records. The fair
  current-representation reference is the full `gemma_lora` adapter (REF column).
- **B/C outputs are clean**: 100% parse, 100% schema, 100% contract, node count error
  0.16 (the model emits exactly 10.0 nodes vs 9.84 target; count conditioning now works
  because the prompt caps match the targets).
- **C's connectivity regression** (95% vs B's 100%): 5 outputs contain an orphan node
  (e.g. `PILOT-C-SFT-047144`, 10 nodes/14 edges, 1 orphan). Small-n noise or a mild
  effect of the added instruction line shifting generation; would need a larger sample to
  distinguish.
- **Exact match is 0% for B/C** (and 1% for REF). Structure-exact requires a perfect type
  multiset *and* a perfect (source-type, target-type, label) edge multiset; B's node
  structure recall is 0.797 and edge structure F1 0.63, so perfection is rare. The
  proposal's own risk table (§9) documents an irreducible noise floor from non-
  deterministic targets, but at pilot scale the exact-match failure is dominated by
  imperfect type/edge prediction, not the noise floor.

## 10. Statistical / qualitative comparison

- **B vs full-run baseline (primary decision metrics):**
  Node F1 0.790 (name-level now equals structure-level) vs 0.237; Edge F1 0.630 (structure)
  / 0.152 (name) vs 0.069; Contract-valid 1.0 vs 0.988; Connected 1.0 vs 0.9996; Exact 0.
  B dominates the baseline on every decision metric except exact match (tied at 0).
- **B vs full gemma_lora on the same records (REF):** structure node F1 0.790 vs 0.754
  (+0.036), structure edge F1 0.630 vs 0.633 (≈0), contract 1.0 vs 0.98, connected 1.0 vs
  1.0. B reaches or exceeds the full model's structural fidelity with **1/58th of the
  training data**.
- **B vs C:** no gain from the explicit naming instruction (node identical 0.7903;
  edge 0.6302 vs 0.6254; connectivity worse). The FORMAT example in B already conveys the
  role+number style; the extra line adds prompt tokens (~23) without benefit.
- **Secondary analysis (800 train records):**

| Property | A | B/C | Full artifact |
|---|---|---|---|
| Node-id vocabulary (unique / slots) | 1734 / 7901 | **26 / 7901** | 4,068 / 25,469 (val) |
| Singleton-id rate | 0.149 | **0.0** | 0.109 |
| Node lists sorted by (type, id) | 0% | **100%** | 1.0% |
| Edge lists sorted | 3.3% | **100%** | 3.0% |
| Structural fragmentation (distinct structures / records) | 1.000 (naming-inflated) | **0.988** | 0.979 |

  Canonicalization collapses the id vocabulary 1734→26, makes all emission deterministic,
  and reveals the true structural fragmentation (0.988, dominated by edge topology —
  canonicalization removes the naming-inflated uniqueness, not the real structure).
- **What actually drives the improvement** (not memorization: val records are held out,
  B trains on only 800 records):
  1. Reduced arbitrary-ID entropy (vocab 1734→26, singleton 0.149→0) — the model only
     needs to learn "emit `type-1..type-k` for each type present", a learnable rule.
  2. Deterministic ordering (0%→100% sorted) — removes the unlearnable Phase 6
     emission-order noise that was the dominant edge-F1 killer.
  3. Fixed prompt caps (10/15) — count conditioning now works (B avg 10.0 vs target 9.84;
     node count error 0.16 vs A's 2.72).
  4. Better edge prediction appears as the structure-level edge F1 (0.63) — topology by
     type-pair is predictable even though exact canonical-edge keys stay low (0.15) due to
     index-assignment ambiguity within a type.

## 11. Recommended variant

**B — canonical type-anchored IDs + deterministic ordering + fixed caps.** It is the
minimal transformation that delivers the full measured benefit; C's explicit naming
instruction adds nothing and slightly hurts connectivity. Proposal success gates:

| Gate | Requirement | B (pilot) | Pass? |
|---|---|---|---|
| Structure-level node F1 | ≥ 0.6 | 0.79 | ✅ |
| Structure-level edge F1 | ≥ 0.25 | 0.63 | ✅ |
| Canonical exact match | ≥ 0.10 | 0.00 | ❌ |
| Contract validity | ≥ 0.999 | 1.0 | ✅ |
| Connectedness | ≥ 0.999 | 1.0 | ✅ |

4/5 gates pass; the exact-match gate fails.

## 12. Is the improvement strong enough to justify full redesign?

**Partial — yes for node/edge fidelity, no for exact match.**

- The canonical representation is dramatically more learnable: it reaches or exceeds the
  full model's structural fidelity with 1/58th of the data, fixes the prompt/contract
  mismatch (which demonstrably corrupted count conditioning), and turns the reported node
  F1 metric from an unlearnable arbitrary-name task (0.237) into an honest type-inventory
  metric (0.79).
- However, per the proposal's own gates, the canonical exact-match gate (≥10%) is **not
  met** (0%). A full redesign should not be sold on exact-match gains; it should be sold
  on node/edge F1 and contract metrics, with the exact-match expectation reset (or the
  gate replaced by structure-exact as informational). The pilot evidence says exact match
  will remain near 0 even at full scale.
- Also note the existing full model already reaches structure-level node F1 0.754 / edge
  F1 0.633; the *marginal* structural gain of canonicalization over the current full model
  is modest (+0.036 node, ≈0 edge). The decisive advantages are learnability (data
  efficiency), contract correctness, and a measurable fidelity metric — not a large
  structural jump at full training scale.

## 13. Risks and limitations

- **Pilot A is not a fair small-scale control** — it under-trains badly (4% contract-valid,
  max 17 nodes). The full gemma_lora REF column is the honest current-representation
  reference; this confound must be remembered when quoting "A vs B".
- **n=100 validation is small**; C's 95% vs B's 100% connectivity and B vs REF edge F1
  (0.630 vs 0.633) differences are within noise. Single seed, single run; no repeated-seed
  variance estimated.
- **Canonical ids trade component-identity fidelity for type-inventory fidelity.** Node F1
  0.79 measures whether the model identifies the right types+counts, not whether canonical
  index `k` maps to the same semantic component (index assignment derives from the
  alphabetical order of the original arbitrary names and is unlearnable by design). The
  `id_map` preserves provenance and display mapping, but semantic re-identification is
  not evaluated.
- **Exact match floor:** non-deterministic targets (1.4% duplicate instructions with
  different targets; 3.4% same-id-set different edge sets) cap exact match regardless of
  representation.
- **Label skew persists** (HTTP-dominant); structure-level edge F1 0.63 already reflects
  this ceiling for rare labels (DB Query, Cache, Async).
- **Prompt length grows** for C (~23 extra tokens); negligible for B.

## 14. Exact next step

On your approval:

1. Adopt the **B encoding** (`canonical_type_anchored_v1`) as the redesign target:
   type-anchored ids, deterministic (type,id)/(source,target,label) ordering, prompt caps
   fixed to 10/15, id_map + original_architecture metadata.
2. Implement it in `dataset/scripts/format_sft.py` as a new transform version
   (`canonical_v2`) behind a flag, applying cluster-wise dedup at full scale (~20%
   reduction expected), preserving split/leakage safety.
3. Regenerate the artifact, pin its SHA-256 in the phase7 spec and `verify_sft.py`,
   and publish the regeneration diff.
4. Re-baseline the existing `checkpoints/gemma_lora` against the new artifact (corrected
   methodology + hash preflight) before training.
5. Train one full E2b run on the canonical artifact; evaluate with the dual metrics used
   here; update phase8 docs with structure-level results and explicit name-level caveats.
6. **Reset the exact-match expectation** (pilot says it will stay ≈0; treat structure-exact
   as informational, or set a realistic gate) before authorizing the full run.

No full dataset generation or full retraining was performed during this pilot, and none
will be performed without your explicit authorization.

## Appendix — artifacts produced

| Artifact | Content |
|---|---|
| `dataset/pilots/redesign_A.jsonl` | 900-record pilot, current representation |
| `dataset/pilots/redesign_B.jsonl` | 900-record pilot, canonical (B) |
| `dataset/pilots/redesign_C.jsonl` | 900-record pilot, hybrid (C) |
| `checkpoints/redesign_pilot_A/B/C/adapter_model.safetensors` | pilot LoRA adapters (r24/α48, 1 epoch, 800 train) |
| `dataset/docs/redesign_pilot_{A,B,C}_eval.json` | corrected-methodology eval results (100 val each) |
| `dataset/docs/redesign_pilot_ref_eval.json` | `checkpoints/gemma_lora` on the same 100 val (current-rep reference) |
| `dataset/docs/redesign_pilot_{A,B,C}_train.out` | training logs |
| `backend/training/gemma/phase8_redesign_pilot_data.py` | dataset generator (deterministic, provenance) |
| `backend/training/gemma/phase8_redesign_pilot_eval.py` | corrected-methodology pilot evaluator |

Sources: `dataset/docs/dataset_redesign_proposal.md` (§5–§7, §6.1), the corrected
baseline `dataset/docs/phase8_corrected_test_eval.json` / `phase8_corrected_evaluation.md`,
and the Phase 8 final evaluation `dataset/docs/phase8_final_evaluation.md`.