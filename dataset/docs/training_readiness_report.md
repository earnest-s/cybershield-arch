# CyberShield Training Readiness Report — v1_FULL Corpus

**Date:** 2026-08-12
**Phase:** 5 — Training Dataset Analysis / Readiness (analysis only; no training started)
**Source corpus (immutable):** `dataset/final/CyberShield_Dataset_v1_FULL.jsonl`
**Environment:** `uv run python` (uv, Python 3.12.x; networkx 3.6.1)
**Method:** Fresh, independent re-computation via `dataset/scripts/training_readiness.py`,
reusing the canonical backend vocabulary and validator
(`backend.core.architecture_schema`, `backend.core.architecture_validator.collect_issues`)
and the canonical dedup fingerprint. Every number in this report was re-measured from the
corpus itself; figures agree with the prior `training_readiness_stats.json` where the same
metric/definition was used.

---

## 1. Corpus at a glance

| Metric | Value |
|---|---|
| **Total accepted records** | **51,498** |
| Source | `ajibawa-2023/Technical-Architectures-Large` (293,640 rows) |
| Schema | Canonical CyberShield sample schema v1.0 |
| Security enrichment | 51,498 / 51,498 (100%) |
| Provenance | 51,498 / 51,498 (id suffix = HF source row) |
| Corpus SHA256 (pre-analysis) | `e3ee9810e13ba660f6f39b93f35e318aa26f22eccf5b7ea59c57ef05f5a1b36b` |

---

## 2. Node distribution

| Stat | Value |
|---|---|
| Min | 2 |
| Max | 658 |
| Mean | 45.12 |
| Median (p50) | 44 |
| p75 | 53 |
| p90 | 62 |
| p95 | 69 |
| p99 | 84 |

**Node buckets:**

| Bucket | Count | Percent | Cumulative |
|---|---|---|---|
| 0–10 | 128 | 0.25% | 0.25% |
| 11–20 | 373 | 0.72% | 0.97% |
| 21–30 | 5,247 | 10.19% | 11.16% |
| 31–50 | 30,184 | 58.61% | 69.77% |
| 51–100 | 15,491 | 30.08% | 99.85% |
| 101–200 | 72 | 0.14% | 99.99% |
| 201–500 | 2 | <0.01% | — |
| 501+ | 1 | <0.01% | — |

---

## 3. Edge distribution

| Stat | Value |
|---|---|
| Min | 1 |
| Max | 358 |
| Mean | 53.61 |
| Median (p50) | 52 |
| p75 | 63 |
| p90 | 74 |
| p95 | 82 |
| p99 | 99 |

**Edge buckets:**

| Bucket | Count | Percent |
|---|---|---|
| 0–10 | 131 | 0.25% |
| 11–20 | 142 | 0.28% |
| 21–30 | 1,940 | 3.77% |
| 31–50 | 21,426 | 41.61% |
| 51–100 | 27,389 | 53.18% |
| 101–200 | 467 | 0.91% |
| 201–500 | 3 | 0.01% |

---

## 4. Component distribution

| Stat | Value |
|---|---|
| Min | 1 |
| Max | 310 |
| Mean | 2.97 |
| Median (p50) | 2 |
| p90 | 6 |
| p95 | 8 |
| p99 | 16 |
| **Single-component share** | **34.1%** |

Weakly connected components (undirected), per the canonical validator semantics.
The frozen orphan policy (multiple components allowed, isolated nodes rejected) means
65.9% of records legitimately contain 2+ components.

---

## 5. Application compatibility

Runtime generation contract (from `backend/core/architecture_schema.py`):
soft target `MAX_NODES = 8`, `MAX_EDGES = 10`; **hard guardrail `HARD_NODE_LIMIT = 10`,
`HARD_EDGE_LIMIT = 15`** (exceeding it raises in the runtime retry loop).

| Cutoff | Count | Percent |
|---|---|---|
| ≤ 8 nodes (soft target) | 114 | 0.22% |
| **≤ 10 nodes (hard guardrail)** | **128** | **0.25%** |
| ≤ 15 nodes | 188 | 0.37% |
| ≤ 20 nodes | 501 | 0.97% |
| ≤ 30 nodes | 5,748 | 11.16% |
| > 30 nodes | 45,750 | 88.84% |
| **> hard guardrail (nodes >10 or edges >15)** | **51,370** | **99.75%** |

**Schema / structural compatibility (measured with the canonical validator, size rule excluded):**

| Check | Result |
|---|---|
| Unsupported node types | 0 records |
| Unsupported edge labels | 0 records |
| Dangling edges | 0 |
| Self-loops | 0 |
| Duplicate edges | 0 |
| Node-id collisions | 0 |
| Extra keys on nodes/edges | 0 / 0 |
| Missing metadata fields | 0 |
| **Records exceeding schema `nodes.maxItems=100`** | **75** (0.15%) |
| **Records exceeding schema `edges.maxItems=200`** | **3** (0.01%) |

All 51,498 records are structurally valid under the pipeline's validator, but 75 records
(101–658 nodes) technically violate the canonical dataset schema's 100-node cap and
3 records exceed the 200-edge cap — they are incompatible with the schema document as
written, independent of the runtime guardrail.

**Takeaway:** 99.75% of the corpus exceeds the runtime hard guardrail. The corpus is a
*real-world reference corpus*, not a runtime-shaped generation corpus.

---

## 6. Security analysis

**Risk level:** HIGH 50,853 (98.75%), MEDIUM 625 (1.21%), LOW 20 (0.04%).
Extreme label imbalance — a model trained on this corpus would rarely predict non-HIGH.

**Threat severity (458,406 threats total):** CRITICAL 103,288 (22.5%), HIGH 269,104
(58.7%), MEDIUM 86,014 (18.8%), **LOW 0**. The corpus contains no LOW-severity threats
at all; severity vocabulary for SFT is effectively 3 of 4 classes.

**Threats per record:** 10 (×23,543), 8 (×22,734), 11 (×1,463), 6 (×1,198), 7 (×993),
9 (×809), 5 (×643), 4 (×67), 3 (×30), 1 (×18) — all non-empty.

**Missing controls per record:** 5 (×13,012), 6 (×12,790), 8 (×10,050), 9 (×9,002),
7 (×4,053), 4 (×1,143), 10 (×819), 3 (×571), 2 (×18), 11 (×22), 1 (×18) — all non-empty.

**Required controls per record:** 11 (×15,753), 8 (×11,836), 7 (×7,406), 5 (×6,444),
10 (×4,351), 9 (×4,120), 6 (×1,157), 3 (×365), 4 (×48), 1 (×17), 2 (×1).

**Completeness:** `security_summary` present 51,498/51,498; all required security keys
present in every record. 13,061 records (25.4%) carry `security_score = 0` (valid —
maximal-risk posture), the rest 1–95.

**Domain vs risk:** HIGH dominates every one of the 42 domains (99.0–100% per domain);
IoT has the most non-HIGH (54 MEDIUM + 5 LOW).

**Style vs risk:** HIGH ≥ 99.0% in every style; Data Mesh has the most MEDIUM (160).

**Cloud vs risk:** HIGH ≥ 98.2% for all 6 clouds; GCP most MEDIUM (143).

---

## 7. Data diversity

| Axis | Cardinality | Counts (min → max) | Imbalance (max/min) |
|---|---|---|---|
| Domain | 42 | Autonomous Vehicles 1,039 → Cyber Security 1,345 | 1.29× |
| Style | 8 | Microservices 5,417 → Serverless 7,441 | 1.37× |
| Cloud | 6 | Multi-Cloud 7,661 → On-Premises 9,432 | 1.23× |
| Complexity | 4 | Large 9,981 → Small 17,690 | 1.77× |

Category balance is **mild**: no axis exceeds a 1.8× max/min ratio, and all 42 domains,
8 styles, 6 clouds, 4 complexity tiers are well populated. The genuine imbalances are
(1) node/edge *size* (88.8% > 30 nodes), (2) risk level (98.75% HIGH), and (3) severity
(no LOW) — not category coverage.

---

## 8. Duplication

| Check | Result |
|---|---|
| Duplicate IDs | **0** |
| Exact duplicates (canonical architecture fingerprint) | **0 groups / 0 records** |
| Exact duplicates (full record, id excluded) | **0 groups / 0 records** |
| Identical node-id set shared with ≥1 other record | 3,587 records (7.0%) |
| Near-duplicates (identical node set, edge-set Jaccard ≥ 0.9, non-identical canonical) | 7 pairs / 14 records (0.03%) |

The 7 near-duplicate pairs correspond to the "exact_dup_groups: 7" figure in the earlier
stats file; under stricter fingerprints (canonical architecture, full record) there are
**zero** exact duplicates. Near-duplication is negligible for training.

---

## 9. Source regime shift

Staging dirs (`parsed/`, `enriched/`, `validated/`, `reviewed/`) were purged after the
full run (git-ignored, regenerable), so per-50k-range parsed/enriched counts are not
recomputable offline. The authoritative full-run funnel and range funnels below come
from `full_scale_report.md` (measured during the run); per-50k-range *accepted* counts
and node/edge means are re-measured here from the corpus (id suffix = HF source row).

**Full funnel:** raw 293,640 → parsed 285,561 (97.2%) → enriched 284,686 (97.0%) →
validated **51,498** (18.1% of enriched). Rejections: 233,121 isolated-node, 57 canonical dup.

**Accepted per source-row range (measured on the corpus):**

| Range | Accepted | Raw rows | Acceptance (accepted/raw) | Node mean | Edge mean |
|---|---|---|---|---|---|
| 0–49,999 | 15,863 | 50,000 | 31.7% | 45.0 | 54.5 |
| 50,000–99,999 | 15,937 | 50,000 | 31.9% | 45.0 | 54.5 |
| 100,000–149,999 | 12,085 | 50,000 | 24.2% | 45.1 | 54.2 |
| 150,000–199,999 | 2,715 | 50,000 | 5.4% | 45.4 | 49.3 |
| 200,000–249,999 | 2,609 | 50,000 | 5.2% | 45.5 | 48.7 |
| 250,000–293,640 | 2,289 | 43,641 | 5.2% | 46.2 | 49.4 |

Full-run range funnels (from `full_scale_report.md`): 0–499: 31.8% (of enriched);
500–2,499: 32.9%; 2,500–99,999: 33.7%; 100,000–149,999: 25.3%; 150,000+: 5.3%.

**Confirmed:** the acceptance cliff at ~row 150k is a real source-content regime shift
(megadiagrams with decorative/isolated nodes), reproduced exactly by the frozen pipeline.
The accepted records from the late regime are *node-comparable* (node mean 45.4→46.2)
but *edge-sparser* (edge mean 49) — same scale problem, slightly different density.

---

## 10. Training strategy evaluation

Measurements that constrain the decision:

- Node mean 45.1 vs hard guardrail 10 → 99.75% of records exceed the runtime limit.
- Only 128 records (0.25%) fit the hard guardrail; 5,748 (11.2%) fit ≤ 30 nodes.
- 75 records violate the canonical schema's 100-node cap.
- Risk 98.75% HIGH; zero LOW-severity threats.
- No exact duplicates; negligible near-duplicates; mild category imbalance.

**A. Train on all 51,498 unchanged — REJECT.**
The distribution is 4.5× the runtime's hard node limit (44-node median). SFT on this
corpus would teach Gemma to emit 40–50-node diagrams that the runtime's `raise_if_invalid`
retry loop rejects — a direct train/inference contract mismatch. 75 records also violate
the schema cap. Using the corpus unchanged is not viable for the compact-generation objective.

**B. Train only on records matching application constraints — PARTIAL.**
≤ 10 nodes = 128 records — far too few for LoRA SFT. ≤ 20 nodes = 501, ≤ 30 nodes = 5,748:
usable in principle, but spread over 42×8×6 = 2,016 domain×style×cloud cells (~2.9
records/cell) and ~99% HIGH risk. Too thin to be the whole strategy.

**C. Principled transformation of large architectures — RECOMMENDED AS THE ENABLER.**
45,750 records (88.8%) are > 30 nodes and otherwise unusable. A principled
connected-subgraph extraction (e.g., seeded at entry/API-gateway nodes, or per connected
component) can derive compact 8–10-node sub-architectures that preserve *real* node ids,
edges, and provenance. This is selection/derivation of real content — not fabrication —
but it is a new policy and must be explicitly approved, piloted on a sample (yield must
be measured), and every derived record must re-pass the frozen validation + security
enrichment. The 75 records > 100 nodes and the 3 records > 200 edges are transformation
*sources only*, never direct-use.

**D. Different subsets for different objectives — RECOMMENDED FRAME.**
1. **Compact-generation SFT set:** ≤ 30-node records used as-is (5,748), plus approved
   C-derived sub-architectures from the large-record majority. This is the primary set
   for the current `/explain` contract.
2. **Large-graph / analysis corpus:** > 30-node records kept intact for future
   objectives (architecture understanding, summarization, long-context work) — not for
   the current compact generator.
3. **Security-priority set:** stratified sampling to surface the 645 non-HIGH records
   and the MEDIUM/Critical severity tail, addressing the risk/severity label imbalance
   before SFT.

**E. Other — NOT recommended without approval.**
Relaxing the runtime guardrail or schema to fit the corpus is explicitly out of scope
(the runtime contract is fixed by the backend). Truncating/inventing content is
forbidden by Phase 5 policy.

### Recommendation

**Adopt D, with C as the enabling transformation and B's ≤ 30-node records as the seed
direct-use set:**

1. **Do not** use the 51,498 records unchanged as a monolithic SFT set.
2. Direct-use core: the 5,748 records ≤ 30 nodes (start with ≤ 20 nodes / 501 records
   for the strictest contract), used as-is.
3. Transform (upon approval): connected-subgraph extraction on the 45,750 > 30-node
   records to recover compact examples with full provenance; pilot the yield first.
4. Exclude from direct use: 75 records > 100 nodes and 3 records > 200 edges
   (schema-cap violations) — transformation sources only.
5. Address label imbalance: stratify by risk (include all 645 non-HIGH records) and
   audit severity; LOW severity is absent corpus-wide.
6. Any training set is a **new artifact** at `dataset/training/CyberShield_Gemma_SFT_v1.jsonl`;
   `CyberShield_Dataset_v1_FULL.jsonl` remains the immutable source corpus.

---

## 11. Explicit answer

**Should the current 51,498 records be used directly for Gemma SFT?**

**No.** The full corpus should **not** be used unchanged for Gemma SFT under the
application's compact-generation objective, because the measured distribution is
incompatible with the runtime contract:

1. **99.75% of records exceed the runtime hard guardrail** (10 nodes / 15 edges); the
   mean is 45.1 nodes — 4.5× the hard limit — and p99 is 84 nodes (8.4×). The runtime
   rejects such outputs (`raise_if_invalid` → retry loop), so training on them would
   teach exactly the behaviour the application cannot serve.
2. **75 records violate the canonical schema's 100-node cap** and 3 violate the
   200-edge cap — schema-incompatible as written.
3. **Label imbalance is extreme**: 98.75% HIGH risk and zero LOW-severity threats would
   bias generation and the security layer.
4. The corpus is a high-quality, provenance-tracked **reference corpus**; its value is
   best recovered by selection (≤ 30-node subset = 11.2%) plus an approved, principled
   subgraph-derivation strategy for the remaining 88.8% — not by bulk SFT.

---

## 12. Artifacts & verification

**Created (Phase 5 analysis only):**
- `dataset/scripts/training_readiness.py` — reproducible analysis script (reuses
  canonical backend schema/validator; networkx for components).
- `dataset/docs/training_readiness_stats.json` — regenerated, independently verified
  statistics (superset of the prior file; severity now counted from the canonical
  `severity` field only).
- `dataset/docs/training_readiness_report.md` — this report.

**Verification:**
- Corpus SHA256 recorded **before** analysis: `e3ee9810e13ba660f6f39b93f35e318aa26f22eccf5b7ea59c57ef05f5a1b36b`
  (re-checked after — unchanged).
- All distributions re-measured from the corpus agree with the prior
  `training_readiness_stats.json` (node/edge buckets, percentiles, regime counts, risk,
  diversity — identical values).
- No corpus records were modified; no pipeline policy changed; no training data created;
  no split performed.

---

## 13. STOP — next phases require approval

NOT executed (awaiting explicit approval): train/validation/test split, Gemma LoRA
training, hyperparameter tuning, model selection, synthetic data generation, and any
principled subgraph transformation of the corpus. None were started.
