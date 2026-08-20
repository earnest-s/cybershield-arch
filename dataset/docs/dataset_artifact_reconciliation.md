# Dataset Artifact Reconciliation Report

**Date:** 2026-08-20
**Status:** READ-ONLY audit complete. No dataset, model, training, or code was modified,
deleted, or regenerated during this audit.

---

## I. Classification

**#4 — CURRENT ARTIFACT INCONSISTENCY.**

The shipped SFT artifact is internally inconsistent: its instructions say
"Max nodes: 8 / Max edges: 10" while 97.8% of its targets exceed 8 nodes (up to 10) and
14.7% exceed 10 edges (up to 15). Furthermore, the Phase 8 evaluation metrics were
computed through a **parser that silently truncates every target to 8 nodes / 10 edges**,
so the reported fidelity numbers (node F1 0.224, edge F1 0.065, exact 0%) do not describe
fidelity to the artifact's actual targets.

The originally suspected **training/evaluation mismatch against a different (older)
artifact is refuted by this audit**: training and evaluation both ran against the
currently shipped file. The "8-node-era artifact" hypothesis was an artifact of the
truncating parser, which reproduces the reported "8-node" statistics exactly from the
current file.

Not #1 (the mismatch observation was real, though its cause is parser-side, not a file
swap). Not #2 (no older artifact — reports that appear to describe one are the truncated
view of the current file). Not #3 (training and evaluation used the same current file).

---

## II. Corrected provenance chain (what actually happened)

```
phase7 pipeline (extract_subgraphs.py, HARD 10/15 contract)
        │  deterministic, provenance-preserving
        ▼
dataset/training/CyberShield_Gemma_SFT_v1.jsonl   ← 51,498 records, 97.2% at 10 nodes
        │  created 2026-08-17 23:13:53.514 (+0530), unchanged since
        │  (byte-identical to a fresh regeneration of the current pipeline)
        ├─► Tuning  (Aug 18 16:08–19:10): lora_train.py reads SAME file,
        │     targets = raw response strings (real 10-node JSON)
        ├─► Full run (Aug 18 19:28:18 → Aug 19 09:15:31, 49,648 s ≈ 13.8 h):
        │     "Loaded 46348 train / 2575 validation samples from
        │      .../dataset/training/CyberShield_Gemma_SFT_v1.jsonl"
        │     → adapter saved to checkpoints/gemma_lora (mtime Aug 19 09:15:31.519)
        └─► Final eval (Aug 19 ≈14:45–17:27, 9,761 s):
              phase8_generate_eval.py reads SAME file (test split, 2,575),
              parses targets via parse_architecture() →
              SILENT TRUNCATION to MAX_NODES=8 / MAX_EDGES=10
              → reported metrics computed against truncated targets
```

No file swap occurred. All timestamps are mutually consistent (artifact Aug 17 < tuning
Aug 18 < training Aug 18–19 < eval Aug 19). The evaluation JSON's target statistics
(avg 7.93 nodes / 7.26 edges) are the **parser-truncated view of the current file's
targets**, verified per-record on all 2,575 test records.

---

## III. Evidence

### D. Current shipped artifact (independently measured)

File: `dataset/training/CyberShield_Gemma_SFT_v1.jsonl`
- SHA-256: `8c91e5cd017df9490f24b5c9f016f01c871e5531b4072c7f83d6959301b851ec`
- SHA-1 (raw): `227dcb5b2176d1fb87982ca04935ef128af12af2`
- Git blob SHA-1 (with header): `2a0820104c676833cc65550eb5b1e70a6eae56e7`
- Size: 200,254,229 bytes; records: **51,498**; splits **46,348 / 2,575 / 2,575**
- mtime: 2026-08-17 23:13:53.514 (+0530) — unchanged since creation
- Regeneration check: `format_sft.py` re-run to `/tmp` is **byte-identical**
  (raw SHA-1 `227dcb5b…` both) → the file is exactly the current pipeline's output.

| Split | records | mean nodes | p50/p95/max nodes | mean edges | p50/p95/max edges |
|---|---|---|---|---|---|
| train | 46,348 | 9.899 | 10 / 10 / 10 | 9.515 | 9 / 12 / 15 |
| validation | 2,575 | 9.891 | 10 / 10 / 10 | 9.489 | 9 / 12 / 15 |
| test | 2,575 | 9.884 | 10 / 10 / 10 | 9.505 | 9 / 12 / 15 |
| **all** | 51,498 | 9.898 | 10 / 10 / 10 | 9.514 | 9 / 12 / 15 |

Node-count distribution (all): `{2:58, 3:104, 4:175, 5:191, 6:165, 7:229, 8:207, 9:297,
10:50,072}` → 97.2% at exactly 10 nodes.
Edge-count distribution: mode 9 (31,324, 60.8%), max 15.

Instruction vs target caps:
- Instructions containing "Max nodes: 8": **51,498 / 51,498** (100%); "Max nodes: 10": 0.
- Targets with **>8 nodes: 50,369 (97.8%)**; targets with **>10 edges: 7,583 (14.7%)**.

### A. Training data

- File: `dataset/training/CyberShield_Gemma_SFT_v1.jsonl` — same path & bytes as shipped
  (log: `[INFO] Loaded 46348 train / 2575 validation samples from
  /home/earnest/Downloads/cybershield-arch/dataset/training/CyberShield_Gemma_SFT_v1.jsonl`,
  `dataset/docs/phase8_full_run.out`).
- SHA-256: `8c91e5cd…` (see D — file unchanged since Aug 17 23:13, before training).
- Records: 51,498 total; train split 46,348; mean 9.899 nodes / 9.515 edges.
- Targets: `lora_train.py` (line 87) uses `row["response"]` **verbatim** as the model
  target — the model was trained on the real 10-node JSON strings, **not** truncated.
- Run evidence: start step timestamp `W818 19:28:18` + wall_seconds 49,648.2 (13.8 h)
  → end matches adapter save mtime Aug 19 09:15:31.519; config E2b (r24/α48, lr 2e-4,
  1 epoch, grad_accum 8, cosine warmup 10%, seed 42, max_length 1024); final train loss
  avg 0.2331, eval loss 0.1912 (matches `phase8_full_run_metrics.json`).

### B. Validation data (during training)

- Same file, validation split: **2,575 records**, mean 9.891 nodes / 9.489 edges
  (log line quoted above). No separate validation artifact exists.

### C. Test data (final evaluation)

- Same file, test split: **2,575 records** (IDs `SFT-…` identical and in the same order
  as the eval output list — verified: 2,575/2,575 present, 0 missing, 0 extra).
- Eval run evidence: `phase8_final_test_eval.out` (progress 60→2575, 9,761 s),
  JSON written 2026-08-19 17:27:48.591; report 17:28:44.
- **Target side used by the eval** = `parse_architecture(extract_json_object_comments(
  row["response"]))` — the truncating parser. Verified per-record: parsing the current
  file's test responses with this exact path reproduces the eval JSON's target node and
  edge counts for **all 2,575 / 2,575 records** (match 2575, differ 0 for both nodes
  and edges).
- Real (untruncated) test targets: mean 9.884 nodes / 9.505 edges.
- Eval-truncated targets: mean 7.934 nodes / 7.261 edges; node dist
  `{2:20, 5:7, 6:9, 7:11, 8:2528}`, edge dist
  `{1:20, 4:5, 5:8, 6:13, 7:1936, 8:413, 9:116, 10:64}`.

### E. Record-level comparison

- **Training**: no per-record output artifact exists, but the training process read the
  same byte-identical file (path + unchanged mtime + byte-identical regeneration).
  Targets were the raw 10-node responses.
- **Validation**: same file, 2,575 records, raw responses.
- **Test (eval)**: 2,575/2,575 IDs match the current file, prompts are the rendered
  instruction strings (identical template), and per-record target counts match the
  current file **through the truncating parser** (all 2,575). The 57 records where the
  *raw* target node count equals the eval's tp+fn are exactly the 57 records with ≤8
  real nodes (`2+7+9+11+10 = 57`); the remaining 2,518 records are precisely those with
  >8 real nodes (`10-node: 2,503 + 9-node: 15 = 2,518`). This is a complete,
  deterministic explanation of the observed "2,518 / 2,575 differ".

### F. Model training provenance

- `checkpoints/gemma_lora` **is** the full-run adapter: the training log's final lines
  are `Saved LoRA adapter to …/checkpoints/gemma_lora`; adapter mtime
  `2026-08-19 09:15:31.519` equals the run end; `adapter_config.json` (r=24, α=48,
  CAUSAL_LM, base `unsloth/gemma-3-4b-it-bnb-4bit`, PEFT 0.20.0) matches the E2b
  configuration; and the eval's `config.adapter` = `checkpoints/gemma_lora`.
- `release/huggingface/` is a byte-for-byte copy of `checkpoints/gemma_lora`
  (adapter_config SHA-1 `99fb1953…` and adapter_model SHA-1 `e3696038…` in both),
  staged for the Hugging Face upload on Aug 19 18:14.
- A different weights file of the same byte size (178,885,992) exists only inside the
  pre-rewrite git history at `release/huggingface/adapter_model.safetensors`
  (blob `345c38b3…`); it matches **none** of the on-disk adapters
  (`gemma_lora`/`release` `e3696038…`, pilot `80a715f8…`, exp_E1 `fb03ef1a…`,
  exp_E2b `58ff5568…`) and its origin is unverified. It does not affect the
  training/eval provenance conclusions above.

### G. Evaluation provenance (the reported metrics)

Node F1 **0.2242**, edge F1 **0.0647**, exact match **0.0** were computed against:
**the currently shipped artifact's test split, after the parser truncated every target
to ≤8 nodes / ≤10 edges** (see C). They were not computed against an older artifact, an
intermediate artifact, or a different dataset.

Bias direction vs the real targets (bounds, exact recomputation requires regenerating
the 2,575 outputs — deferred):
- The truncated target is a strict subset of the real target (parser takes the first 8
  nodes of the real 10-node list, then drops incident edges and caps at 10).
- ⇒ real node recall **≤ 0.2252** (real FN ≥ reported FN), real node precision
  **≥ 0.2233** (real FP ≤ reported FP). Same for edges: real edge recall ≤ 0.0642,
  real edge precision ≥ 0.0652.
- Exact match 0.0 is unaffected (correct either way).
- The model was trained on real 10-node targets but is prompted with "Max nodes: 8", so
  its outputs average 8.0 nodes (max 8); the 2+ real target nodes per record are never
  reachable, additionally depressing true recall.

### H. Prompt/contract mismatch timeline

- `MAX_NODES = 8`, `MAX_EDGES = 10`, `HARD_NODE_LIMIT = 10`, `HARD_EDGE_LIMIT = 15`
  coexist in `backend/core/architecture_schema.py` since the earliest tracked commit
  (2026-08-06). Two different contracts in one module:
  - **8/10** = parser cap (`parse_architecture`, `architecture_parser.py:205,238`,
    silent slice) and prompt template ("Max nodes: 8 / Max edges: 10").
  - **10/15** = Phase 6 extraction contract and validator guardrail
    (`architecture_validator.py` RULE_SIZE).
- The prompt caps are present in `dataset/scripts/format_sft.py` and
  `backend/core/inference.py` (identical; a drift check lives in `verify_sft.py`) in
  every tracked commit — present during dataset creation (Aug 17), tuning (Aug 18),
  training (Aug 18–19), evaluation (Aug 19), and current inference.
- The resulting prompt-vs-target mismatch is **documented in
  `phase7_training_report.md` §2 item 2** ("Prompt soft-target mismatch … retained for
  deployment") — it was a known, deliberate retention, not an accident.

### Key files and hashes

| File | SHA-256 (raw SHA-1) | Notes |
|---|---|---|
| `dataset/training/CyberShield_Gemma_SFT_v1.jsonl` | `8c91e5cd…` (`227dcb5b…`) | 51,498 recs; shipped, trained, and evaluated file |
| `dataset/docs/phase8_final_test_eval.json` | — (`2eb69cd0…` git blob) | per-output tp/fp/fn vs truncated targets |
| `checkpoints/gemma_lora/adapter_model.safetensors` | — (`e3696038…`) | full-run adapter (E2b), saved Aug 19 09:15:31 |
| `dataset/docs/phase8_full_run.out/.log/.metrics.json` | — | training provenance (path, config, losses, 49,648 s) |
| `dataset/docs/phase8_final_test_eval.out` | — | eval provenance (9,761 s, adapter, config) |

---

## IV. Root cause

Two conflicting size contracts were introduced together in `architecture_schema.py`
(Aug 6) and never reconciled:

1. The **production contract (10 nodes / 15 edges)** — used by Phase 6 extraction and the
   validator — produced an artifact that is 97.2% ten-node.
2. The **legacy contract (8 nodes / 10 edges)** — used by the prompt template and by
   `parse_architecture`, which **silently truncates** (`[:MAX_NODES]`, edge cap) any
   graph, including evaluation targets — made the eval report 8-node targets and
   constrained the model's outputs to ≤8 nodes.

The parser's silent truncation is the direct cause of the "7.93-node targets vs
9.88-node artifact" observation and of the reported metrics not reflecting the real
targets. The prompt-vs-target mismatch was knowingly retained (phase7 report) but its
effect on evaluation was not accounted for.

---

## V. Corrective recommendations (for approval; NOT executed)

1. **Fix the evaluation target path (lowest risk, ~2.7 h GPU):** parse eval targets
   without the MAX caps (raw `json.loads` of `response`, or a no-truncate flag in
   `parse_architecture`) and re-run the 2,575-record test evaluation; publish both the
   legacy-truncated and the true-target metrics.
2. **Reconcile the contract (product decision, requires regeneration + retrain):**
   - If 10/15 is the production contract (validator + Phase 6 already enforce it):
     update `MAX_NODES=10`/`MAX_EDGES=15`, update the prompt template in
     `format_sft.py` + `inference.py` to "Max nodes: 10 / Max edges: 15", regenerate
     the artifact (currently byte-deterministic), retrain.
   - Or keep 8/10 at runtime and regenerate targets to ≤8/≤10.
   This is exactly the design space already analyzed in
   `dataset/docs/dataset_redesign_proposal.md` (§5–§7).
3. **Tooling:** pin the artifact SHA-256 in the phase7 spec and make the eval fail
   loudly on truncation; record the hash in eval JSON config.
4. **Documentation:** the redesign proposal's §3.3 / §6.3 ("artifact swap; baseline not
   reproducible; artifact never trained on") is **superseded** — the baseline IS
   reproducible from the current artifact, and the eval DID use it (through the
   truncating parser). Its §3.1–§3.2, §4, §5–§7 findings (naming/order arbitrariness,
   contract mismatch, representation strategies) remain valid.

## VI. Impact on reported model metrics

- The published numbers (node F1 0.2242, edge F1 0.0647, exact 0%) are valid as "fidelity
  vs the parser-truncated 8/10 view of the targets" but **understate/overstate the true
  fidelity vs the artifact's 10/15 targets in opposite directions**: true node recall
  ≤ 0.2252 (lower), true node precision ≥ 0.2233 (higher); edge equivalents ≤ 0.0642 /
  ≥ 0.0652. Exact match 0.0 stands.
- Structural-quality gates (parse 1.0, schema-valid 1.0, contract-valid 1.0, connected
  0.9996, repetition 0) are unaffected by the truncation and remain valid.

---

*End of reconciliation report. No repository files other than this document were
created; nothing was deleted, regenerated, retrained, committed, or pushed.*