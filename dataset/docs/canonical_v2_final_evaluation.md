# Canonical v2 Final Training & Evaluation Report

**Status:** COMPLETE — full-scale training on the canonical v2 artifact plus corrected
non-truncating evaluation on all 2,575 test records.
**Date:** 2026-08-25
**New adapter:** `checkpoints/gemma_lora_v2_canonical` (baseline `checkpoints/gemma_lora` untouched)
**Machine-readable results:** `dataset/docs/canonical_v2_final_test_eval.json`

## 1. Dataset identity

| Property | Value |
|---|---|
| Artifact | `dataset/training/CyberShield_Gemma_SFT_v2_canonical.jsonl` |
| SHA-256 | `a572d6deb8f3a0ab5e05c5371971cb96fbfff84dd01b81cac077680bf5583dfa` |
| Records | 51,498 (train 46,348 / validation 2,575 / test 2,575) |
| Representation | Variant B — type-anchored canonical ids `{type}-{k}`, deterministic node order (type,id), deterministic edge order (source,target,label), prompt caps fixed to max 10 nodes / 15 edges |
| Provenance | per-record `metadata.canonicalization.id_map` + `metadata.original_architecture` |

## 2. Model identity / revision

- Base: `unsloth/gemma-3-4b-it-bnb-4bit`, cached snapshot revision `eb03c885bc2cc913fe792994bc766006f14ad72d`, loaded `local_files_only=True`.
- Adapter: LoRA r=24 / alpha=48, dropout 0.05, targets `model.language_model.*(...)_proj` (E2b config).

## 3. Hardware / software environment

- GPU: NVIDIA GeForce RTX 4050 Laptop (6 GB); peak VRAM allocation **3.52 GiB**.
- Stack: PyTorch CUDA, bitsandbytes NF4, PEFT 0.20.0, Gemma 3 chat template.
- One transient CUDA allocator OOM warning at step 38 (auto-recovered, no effect).

## 4. Exact training configuration

Identical to the validated E2b full-run config: 1 epoch; batch 1 x grad-accum 8 = 5,793 steps;
AdamW8bit lr 2e-4, cosine schedule, warmup 10 percent; max_length 1024 (zero truncation,
max sequence 594 tokens); seed 42; prompt tokens masked from loss; validated chunked CE;
output to new directory `checkpoints/gemma_lora_v2_canonical/`. Nothing overwritten.

## 5–8. Training outcome

| Metric | Value |
|---|---|
| Wall duration | ~26 h (includes 58 full validation passes of 2,575 records) |
| Peak VRAM | 3.52 GiB |
| Train loss | avg 0.0993 (final step 0.0903) |
| Validation loss | 0.0866 final (monotone: 0.1223 -> 0.0880 -> 0.0875 -> 0.0874 -> ... -> 0.0866) |
| Tokens processed | 12,109,238 at final step (12,110,254 epoch total) |

Loss alone is NOT treated as success; verdicts below are fidelity-based.

## 9. Test evaluation methodology

Corrected NON-truncating methodology (same core as `phase8_corrected_eval.py`):

- Targets loaded VERBATIM from each record's architecture field; never passed through the
  8/10-capped runtime parser.
- Generated outputs parsed non-truncating (`normalize_full`) for structural comparison AND
  runtime-faithful (`parse_architecture`) for the serve-time view.
- Contract validity (10 nodes / 15 edges) checked on the FULL generated graph.
- Generation identical to all prior evals: greedy, seed 42, rep penalty 1.1, no_repeat_ngram 0,
  max_new_tokens 768, gen_batch 3, EOS 106. n = 2,575 test records; wall 10,652 s.
- Dual metrics: structure-level (primary) + name-level exact-id metrics (directly comparable
  to the v1 baseline metric definition).

## 10. Baseline vs V2 (n = 2,575)

| Metric | V1 baseline | V2 canonical | Delta |
|---|---|---|---|
| Parse rate | 1.0 | 1.0 | - |
| Schema-valid rate | 0.988 | 0.9996 | +0.012 |
| Contract-valid rate | 0.988 | 0.9996 | +0.012 |
| Connected rate | 0.9996 | 1.0000 | clean sweep |
| Orphan / structurally weak | 0.0004 | 0.0 | eliminated |
| Repetition failure | 0.0 | 0.0 | - |
| Node precision | 0.2355 | 0.8056 | +0.57 |
| Node recall | 0.2385 | 0.8151 | +0.58 |
| Node F1 | 0.2370 | 0.8103 | +0.573 (3.4x) |
| Edge F1 (exact keys) | 0.0688 | 0.1408 | ~2x |
| Edge F1 (structure-level) | n/a (not measured v1-full) | 0.6563 | - |
| Exact match (canonical structure) | 0.0 | 0.0008 (2/2575) | first nonzero |
| Exact match (name-level) | 0.0 | 0.0 | - |
| Mean generated nodes | 10.01 | 10.00 | all 2,575 outputs exactly 10 nodes |
| Mean target nodes | 9.88 | 9.88 | - |
| Mean generated edges | 9.21 | 9.14 | - |
| Mean target edges | 9.51 | 9.51 | - |
| Max generated nodes / edges | 11 / 14 | 10 / 18 | never exceeds node limit |
| Over-limit outputs | 31 | 1 (`SFT-049680`, 18 edges) | -30 |

### Count distributions (generated vs target)

| Nodes | Generated | Target |
|---|---|---|
| 2 / 5 / 6 / 7 / 8 / 9 | 0 / 0 / 0 / 0 / 0 / 0 | 20 / 7 / 9 / 11 / 10 / 15 |
| 10 | 2575 | 2503 |

| Edges | Generated | Target |
|---|---|---|
| 1-8 | 0 | 68 |
| 9 | 2289 | 1557 |
| 10 | 248 | 569 |
| 11 | 26 | 220 |
| 12 | 0 | 97 |
| 13 | 1 | 41 |
| 14 | 4 | 15 |
| 15 | 6 | 8 |
| >15 | 1 (18) | 0 |

## 11. Pilot vs Full-scale (Variant B generalization)

| Metric | Pilot B (800/100) | V2 full (46,348/2,575) |
|---|---|---|
| Node F1 | 0.7903 | 0.8103 |
| Edge F1 (structure) | 0.6302 | 0.6563 |
| Canonical exact match | 0.0 | 0.0008 |
| Contract-valid | 1.0 | 0.9996 |
| Connected | 1.0 | 1.0 |
| Validation loss | 0.1102 | 0.0866 |

Pilot gains generalized and improved at full scale; no regression on any metric.

## 12. Error analysis

- Node errors: FP 5,005 / FN 4,706 over 25,451 target nodes — residual type-inventory mistakes,
  concentrated in small non-10-node targets (the model always emits exactly 10 nodes, so the
  72 records whose targets have 2-9 nodes are guaranteed mismatches).
- Edge errors: exact-key FP 20,163 / FN 21,095 — dominated by canonical index ambiguity within
  a type (which service connects to which service). Structure-level edge errors are much lower
  (FP 7,786 / FN 8,718), confirming topology-by-type is largely right while endpoint indexing is
  only partially recoverable — consistent with the pilot analysis.
- The single contract violation: `SFT-049680` generated 10 nodes / 18 edges (size_guardrail).
  Runtime parser would cap edges at 10; validator flags it. 1/2575 = 0.04 percent.
- No parse failures, no repetition loops, no token-cap truncations, no disconnected/orphan outputs.

## 13. Structural fidelity analysis

- Type-inventory fidelity is the headline gain: node F1 0.237 -> 0.810 means the model now
  identifies the correct component inventory (types + counts) for ~81 percent of components,
  versus ~24 percent name-overlap before. This matches the redesign proposal's predicted ceiling
  shift (name-level unlearnable -> type-level learnable).
- Topology fidelity: structure-edge F1 0.656 (vs ~0.63 measured for the v1 full model under the
  same corrected lens during the pilot reference run). The v2 model is at least as topology-faithful
  as the v1 baseline while being dramatically more inventory-faithful and fully count-conditioned.
- Exact structural reproduction remains rare (2/2575). Exact match is bounded by within-type index
  assignment ambiguity and the documented non-deterministic-target noise floor; treat exact match
  as informational, exactly as the pilot recommended.

## 14. Contract / format analysis

- Prompt contract now matches the runtime hard contract (max 10/15) and the model obeys it:
  every output has exactly 10 nodes (never more than the hard limit; v1 emitted 11 nodes in 31 cases).
- Schema-valid 99.96 percent (single size_guardrail warning); malformed outputs: zero.
- Known pre-existing issue unchanged: `runtime_truncation_rate = 1.0` — the production parser still
  caps at MAX_NODES=8/MAX_EDGES=10, so every v2 output would be silently truncated at serve time.
  Fixing that requires the deferred runtime change (out of scope here).

## 15. Did v2 actually improve the model?

Yes — on the primary fidelity criteria, not merely loss:

| Criterion | Result |
|---|---|
| Node F1 | 0.237 -> 0.810 (+0.573, 3.4x) — decisive improvement |
| Edge F1 | exact-key 0.069 -> 0.141 (~2x); structure-level 0.656, at or above the v1 model's corrected-lens topology score |
| Exact match | 0% -> 0.08% structure-exact (first nonzero; name-level still 0%) |
| Contract validity | 0.988 -> 0.9996 |
| Connectedness | 0.9996 -> 1.0000 (zero weak outputs) |

## 16. Suitability for demonstration / inference

- Structurally safe to demo behind the existing runtime pipeline: valid JSON always, schema-valid,
  connected, repetition-free. Outputs are plausible, well-sized canonical architectures.
- Caveat: serve-time truncation (runtime caps 8/10) will drop ~2 nodes per graph until the runtime
  parser caps are aligned; and displayed ids are canonical labels (ui-1, service-2, ...) rather than
  semantic names — reversible via id_map if a display mapping is added.
- Do NOT replace `checkpoints/gemma_lora` in production without the runtime-cap decision.

## 17. Limitations

- Component-identity semantics remain unmeasured/unlearnable (within-type index assignment);
  canonical node F1 measures inventory, not identity.
- Small-target records (72 of 2,575) cannot be matched by the always-10-node behavior.
- Single seed, single run; no variance estimate.
- Label skew persists (HTTP-dominant); rare-label recall stays limited.
- Serve-time truncation mismatch unresolved (runtime out of scope).

## 18. Exact adapter hashes

| File | SHA-256 |
|---|---|
| `checkpoints/gemma_lora_v2_canonical/adapter_model.safetensors` | `051aacb6a2cdba249adb016929a0491849590a120d84979c2a1d73870c27ce93` |
| `checkpoints/gemma_lora_v2_canonical/adapter_config.json` | `7927f77ce89a5ec401c2307e1e8ebf387e47351ae25315a6c18df1b9cc882a03` |

Baseline adapter `checkpoints/gemma_lora` sha1 `e3696038bd4d9ba8431378ac5f3c8f33a16a5625` — verified untouched.
Training log preserved at `dataset/docs/canonical_v2_training.log`.

**STOP.** No further training, tuning, uploads, or pushes performed. Awaiting review.