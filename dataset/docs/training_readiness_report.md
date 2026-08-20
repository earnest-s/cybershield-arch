# CyberShield Training Readiness Report — v1_FULL Corpus

**Date:** 2026-08-12
**Phase:** 5 — Training Dataset Analysis / Readiness (analysis only; no training started)
**Source corpus (immutable):** `dataset/final/CyberShield_Dataset_v1_FULL.jsonl`
**Environment:** `uv run python` (Python 3.12.x; networkx 3.6.1; Gemma tokenizer offline)
**Method:** Fresh, independently reproduced measurement via
`dataset/scripts/training_readiness.py --provenance-audit`, reusing the canonical
backend vocabulary and validator (`backend.core.architecture_schema`,
`backend.core.architecture_validator.collect_issues`). Sequence lengths are measured
with the **actual Gemma 3 4B tokenizer** (offline, cached). Provenance is verified for
**100% of records** against the raw HF snapshot. All numbers below are measurements of
the corpus itself, not estimates.

---

## 0. Executive verdict

**READY WITH FILTERING.**

- The full 51,498-record corpus is **not** suitable as an unchanged monolithic Gemma SFT
  set: **99.75% of records exceed the runtime hard guardrail** (10 nodes / 15 edges;
  `raise_if_invalid` in the runtime rejects such outputs).
- A **filtered, contract-aligned subset is ready**: the **≤ 20-node tier (501 records)**
  as the strict core, or the **≤ 30-node tier (5,748 records)** for more data, with
  risk stratification (include all 645 non-HIGH records), a **cluster-based
  leakage-safe split**, and a corrected `max_length` (the current `lora_train.py`
  default of 384 tokens truncates ~100% of records).
- Security content must **not** be a generation target (the runtime computes it
  deterministically); the SFT target is the architecture JSON only.
- Provenance is fully verified: 51,498/51,498 records trace to real HF source rows and
  every node id appears verbatim in the source mermaid text. **Zero fabricated content.**

---

## STEP 1 — Dataset audit

### 1.1 Identity

| Item | Value |
|---|---|
| Filename | `dataset/final/CyberShield_Dataset_v1_FULL.jsonl` |
| Record count | **51,498** |
| Size | 391 MB (408,960,412 bytes) |
| SHA256 (pre/post analysis) | `e3ee9810e13ba660f6f39b93f35e318aa26f22eccf5b7ea59c57ef05f5a1b36b` (unchanged) |
| Related pilots | `CyberShield_Dataset_Pilot_v1.jsonl` (152), `_Pilot_v2.jsonl` (617) — untouched |

### 1.2 Source

`ajibawa-2023/Technical-Architectures-Large` (HuggingFace), train split, 293,640 rows.
Pipeline funnel (measured at full-run time, `full_scale_report.md`): raw 293,640 →
parsed 285,561 (97.2%) → enriched 284,686 (97.0%) → validated/final **51,498**
(18.1% of enriched). Rejections: 233,121 isolated-node, 57 canonical duplicates.
Raw snapshot retained at `dataset/raw/samples.jsonl` (1.3 GB, git-ignored, regenerable
via `download_dataset.py`).

### 1.3 Record schema (canonical, v1.0)

```
{
  "id": "CSA-000002",                       # CSA-<HF source row> (provenance anchor)
  "instruction": "Design a E-Commerce architecture. using a Serverless style. ...",
  "architecture": { "nodes": [{"id","type"}], "edges": [{"source","target","label"}] },
  "security": { required_controls, missing_controls, threats, recommendations,
                risk_level, security_score, attack_surface, security_summary },
  "metadata": { domain, style, cloud, complexity, source, reviewed, version }
}
```
Node types: ui, service, database, cache, queue, container. Edge labels: HTTP,
DB Query, Async, Cache (canonical `ALLOWED_*` vocabularies).

### 1.4 Provenance verification — **100% coverage, not spot-checked**

Full audit against `dataset/raw/samples.jsonl` (`--provenance-audit`):

| Check | Result |
|---|---|
| Accepted source rows matched in raw snapshot | **51,498 / 51,498** |
| Missing source rows | **0** |
| Records with every node id found in source mermaid text | **51,498 / 51,498** |
| Node ids absent from source mermaid | **0** |

### 1.5 Quality gates (confirmed)

- Schema-valid (canonical validator, non-size): 51,498/51,498 (0 unsupported types,
  0 unsupported labels, 0 dangling edges, 0 self-loops, 0 duplicate edges, 0 id
  collisions, 0 extra node/edge keys).
- Orphan policy (frozen): 0 isolated-node records.
- Security completeness: 51,498/51,498 (all fields present; `security_summary` in all;
  13,061 records legitimately at `security_score = 0`).
- Duplicate IDs: 0. Duplicate architectures (canonical): 0. Full-record duplicates: 0.

---

## STEP 2 — Training corpus analysis

### 2.1 Node distribution

min **2**, max **658**, mean **45.12**, median **44**, p75 **53**, p90 **62**, p95 **69**,
p99 **84**.

| Bucket | Count | % | | Bucket | Count | % |
|---|---|---|---|---|---|---|
| 0–10 | 128 | 0.25 | | 51–100 | 15,491 | 30.08 |
| 11–20 | 373 | 0.72 | | 101–200 | 72 | 0.14 |
| 21–30 | 5,247 | 10.19 | | 201–500 | 2 | <0.01 |
| 31–50 | 30,184 | 58.61 | | 501+ | 1 | <0.01 |

### 2.2 Edge distribution

min **1**, max **358**, mean **53.61**, median **52**, p75 **63**, p90 **74**, p95 **82**,
p99 **99**.

| Bucket | Count | % | | Bucket | Count | % |
|---|---|---|---|---|---|---|
| 0–10 | 131 | 0.25 | | 51–100 | 27,389 | 53.18 |
| 11–20 | 142 | 0.28 | | 101–200 | 467 | 0.91 |
| 21–30 | 1,940 | 3.77 | | 201–500 | 3 | 0.01 |
| 31–50 | 21,426 | 41.61 | | | | |

### 2.3 Component distribution

min **1**, max **310**, mean **2.97**, median **2**, p90 **6**, p95 **8**, p99 **16**.
**Single-component share: 34.1%** (65.9% are legitimately multi-component per the
frozen orphan policy).

### 2.4 Application compatibility (runtime contract)

Runtime: soft target 8 nodes / 10 edges; **hard guardrail 10 nodes / 15 edges**
(`raise_if_invalid` → retry loop → hard failure if exceeded).

| Cutoff | Count | Percent |
|---|---|---|
| ≤ 8 nodes (soft target) | 114 | 0.22% |
| **≤ 10 nodes (hard guardrail)** | **128** | **0.25%** |
| ≤ 15 nodes | 188 | 0.37% |
| ≤ 20 nodes | 501 | 0.97% |
| ≤ 30 nodes | 5,748 | 11.16% |
| > 30 nodes | 45,750 | 88.84% |
| **> hard guardrail (nodes >10 or edges >15)** | **51,370** | **99.75%** |

Schema-cap violations: **75 records > 100 nodes** and **3 records > 200 edges**
(exceed the canonical dataset schema `maxItems`; not direct-use candidates).

### 2.5 Risk / threat / control distributions

- **Risk:** HIGH 50,853 (98.75%), MEDIUM 625 (1.21%), LOW 20 (0.04%). Extreme
  imbalance — the model would rarely predict non-HIGH.
- **Threat severity (458,406 threats):** CRITICAL 103,288 (22.5%), HIGH 269,104
  (58.7%), MEDIUM 86,014 (18.8%), **LOW 0**. The corpus has no LOW-severity threat.
- **Threats/record:** 10 (×23,543), 8 (×22,734), 11 (×1,463), 6 (×1,198), 7 (×993),
  9 (×809), 5 (×643), 4 (×67), 3 (×30), 1 (×18) — all non-empty.
- **Missing controls/record:** 5 (×13,012), 6 (×12,790), 8 (×10,050), 9 (×9,002),
  7 (×4,053), 4 (×1,143), 10 (×819), 3 (×571), 11 (×22), 2 (×18), 1 (×18).
- **Required controls/record:** 11 (×15,753), 8 (×11,836), 7 (×7,406), 5 (×6,444),
  10 (×4,351), 9 (×4,120), 6 (×1,157), 3 (×365), 4 (×48), 1 (×17), 2 (×1).
- **Risk × domain/style/cloud:** HIGH ≥ 98.2% in every one of the 42 domains, 8
  styles, 6 clouds. Data Mesh has the most MEDIUM (160); IoT the most non-HIGH (59).

### 2.6 Diversity and imbalance

| Axis | Cardinality | Min → max count | Imbalance (max/min) |
|---|---|---|---|
| Domain | 42 | Autonomous Vehicles 1,039 → Cyber Security 1,345 | 1.29× |
| Style | 8 | Microservices 5,417 → Serverless 7,441 | 1.37× |
| Cloud | 6 | Multi-Cloud 7,661 → On-Premises 9,432 | 1.23× |
| Complexity | 4 | Large 9,981 → Small 17,690 | 1.77× |

Category coverage is balanced (all axes < 1.8×). The genuine imbalances are
**(1) size** (88.8% > 30 nodes), **(2) risk** (98.75% HIGH), **(3) severity** (no LOW).

### 2.7 Duplication

| Check | Result |
|---|---|
| Duplicate IDs | 0 |
| Exact duplicates (canonical architecture fingerprint) | 0 groups / 0 records |
| Exact duplicates (full record, id excluded) | 0 groups / 0 records |
| Identical node-id set shared with ≥1 record | 3,587 records (7.0%), 177 clusters, max cluster 132 |
| Near-duplicates (same node set, edge Jaccard ≥ 0.9, non-canonical) | 7 pairs / 14 records (0.03%) |

No exact duplicates. Near-duplication is negligible and is handled by the cluster split.

### 2.8 Prompt/response quality

- **Instructions are real and source-derived:** all 51,498 are built from genuine
  source metadata — `"Design a {domain} architecture. using a {style} style. deployed
  on {cloud}. satisfying: {constraint list}."` — where the constraint lists (e.g.,
  "Rate Limiting, GraphRAG Integration, Disaster Recovery") are real source fields.
- **51,133 unique instructions** (max reuse 3, avg 1.0) — effectively one instruction
  per record; no instruction templating collapse.
- Instruction length: 24–58 tokens (mean 36.6) — compact inputs.
- **Documented weakness:** the templated grammar has imperfections
  ("Design a E-Commerce architecture." / "using a Serverless style."). Content is
  real; the punctuation/style is template-constructed. Phase 7 formatting may
  normalize this (a documented decision, not a data change).
- Response (architecture JSON) is genuine parsed source content — the model should
  learn to reproduce this. Security JSON is **engine-computed, not human or source
  authored** — it must not be a generation target (see STEP 3).

### 2.9 Outliers / extremely large records

Top outliers: CSA-188561 (658 nodes / 351 edges), CSA-281879 (360/358), CSA-171108
(202/111), CSA-267789 (157/118), CSA-136463 (142/82), CSA-245570 (139/137),
CSA-225432 (135/85), CSA-249347 (131/114), CSA-082332 (130/118), CSA-201851 (129/131).
All 75 records > 100 nodes and the 3 records > 200 edges fall into the
"exclude from direct use / transformation source only" category.

### 2.10 Sequence length — exact tokenizer measurement (Gemma 3 4B tokenizer)

| Measure | p50 | p90 | p95 | p99 | max |
|---|---|---|---|---|---|
| Instruction | 36 | 46 | 48 | 52 | 58 |
| Architecture JSON | 1,617 | 2,289 | 2,517 | 3,024 | 14,269 |
| Security JSON | 617 | 724 | 724 | 757 | 807 |
| Runtime generation prompt (fixed template + instruction) | 216 | 226 | 228 | 232 | 238 |
| **Generation prompt + architecture target** | **1,833** | **2,505** | **2,733** | **3,241** | **14,496** |

Full-corpus thresholds: **98.37% > 1,024 tokens, 32.87% > 2,048, 0.06% > 4,096.**

Model context (from tokenizer config) is **131,072 tokens** — context is **not** a
blocker, even for the 658-node record (14,496 tokens). The real concern is the stale
`backend/training/gemma/lora_train.py` default `--max-length 384`, which truncates
~100% of records, plus per-record compute. Recommended `max_length` for the selected
subset: **4,096** (covers p99 of the ≤30-node tier with margin).

### 2.11 Source-generation metadata leakage

Scanned every record for extra keys beyond the canonical schema:

| Scope | Extra keys found |
|---|---|
| Top level (allowed: id, instruction, architecture, security, metadata) | **0** |
| Metadata (allowed: domain, style, cloud, complexity, source, reviewed, version) | **0** |
| Security (allowed: 8 canonical fields) | **0** |
| Node / edge objects | **0** |

No `model`, `input_tokens`, `output_tokens`, `finish_reason`, `diagram_type`,
`constraints`, `source_nodes`, `source_edges`, or any other source-generation field
leaked into final records.

---

## STEP 3 — Training record definition (SFT format)

Grounded in the actual runtime (`backend/core/inference.py`), not invented:

**Runtime model touchpoints:**
1. `generate_architecture`: natural-language description → **architecture JSON only**
   (nodes/edges), max 8 nodes / 10 edges, validated by `raise_if_invalid` +
   structural checks, retry loop on violation.
2. `generate_explanation`: architecture JSON → natural-language explanation
   (Components / Data flow / Architecture type sections). Same prompt shape as the
   stale `lora_train.py` template.

**Recommended SFT format (primary objective — architecture generation):**

```
Input (user):
  <runtime generation prompt template with the record's instruction>
Output (target, loss-masked):
  {"nodes": [...], "edges": [...]}          # architecture JSON ONLY
```

- **Target = architecture JSON only.** Security JSON is computed deterministically by
  the runtime security engine (`build_security_data`); making it a target would teach
  the model to duplicate a deterministic pipeline stage and create a second,
  divergent source of truth.
- **Prompt masking is required** (only target tokens contribute to loss). The stale
  `lora_train.py` trains on the full sequence and labels the prompt too — this must be
  fixed in the Phase 7 training spec.
- **Record packaging (per the canonical schema, unchanged):** `instruction` →
  input text; `architecture` → target; `metadata.domain/style/cloud/complexity` →
  retained for stratification/grouping only (not part of the prompt unless a decision
  is made to inject them).
- **Explanation objective (generate_explanation):** the corpus contains no
  human-written explanations. `security.security_summary` is engine-derived text;
  using it as an explanation target is possible but must be an explicit, labeled
  decision. Recommendation: **defer explanation SFT** until real explanations exist;
  focus SFT on the generation objective.
- **What the model should NOT learn:** reproducing security JSON, source-generation
  metadata, or diagram-internal decorative ids. Node ids and edges are real source
  content and are the intended target vocabulary.

---

## STEP 4 — Split recommendation (leakage-safe)

**Methodology:** group records into **clusters by identical node-id set** (3,587
records share a node set with at least one other record; 177 clusters; max cluster
132 records; the 7 near-dup pairs already live inside shared clusters; 0 exact
duplicates). Allocate **whole clusters** to splits with a deterministic largest-first
greedy fill of the target ratio — no random split, no leakage across splits for
identical/near-identical structures.

**Proposed split (90 / 5 / 5), measured allocations:**

| Subset | Total | Clusters | Train | Validation | Test |
|---|---|---|---|---|---|
| Full corpus (reference only) | 51,498 | 48,088 | 46,348 | 2,575 | 2,575 |
| **≤ 30 nodes (recommended Tier 2)** | **5,748** | 5,060 | **5,173** | **288** | **287** |
| ≤ 20 nodes (recommended Tier 1) | 501 | 448 | 451 | 25 | 25 |
| ≤ 10 nodes (hard-guardrail-faithful) | 128 | 106 | 115 | 7 | 6 |

Duplicate prevention: cluster-level assignment guarantees identical node sets and
near-duplicates never straddle splits; nothing is deleted.

---

## STEP 5 — Is 51,498 the right final training size?

**No — not as an unchanged set.** Evidence-based tiers, no arbitrary caps:

| Tier | Definition | Count | Use |
|---|---|---|---|
| 1 | ≤ 20 nodes | 501 | **Strict SFT core** (closest to runtime scale; still >10 nodes for most) |
| 2 | ≤ 30 nodes | 5,748 | **Primary SFT pool** (adds coverage across 42 domains/8 styles/6 clouds) |
| 3 | 31–100 nodes | 45,673 | Transformation sources only (Phase 6, pending approval) |
| 4 | > 100 nodes / > 200 edges | 75 / 3 | Exclude from direct use; transformation sources only |

- **Include all 645 non-HIGH-risk records** in the training pool (risk stratification
  against the 98.75% HIGH bias).
- **Oversized records (> 30 nodes) need their own policy** (approved subgraph
  transformation in Phase 6) — never direct SFT, never silent truncation.
- No domain/style/cloud **rebalancing** is necessary now (imbalance < 1.8×); the size
  and risk axes are the ones that matter.

---

## STEP 6 — Contamination / fabrication audit

| Gate | Result |
|---|---|
| Full provenance (source row match, 100% of records) | 51,498 / 51,498 |
| Node ids present in source mermaid (100% of records) | 51,498 / 51,498, 0 missing |
| Marker scan (placeholder/demo/mock/fake/synthetic/template/dummy/…) — instruction | 0 |
| Marker scan — security | 0 |
| Marker scan — metadata | 0 |
| Marker scan — architecture | 49 records (0.095%) — **all genuine source node ids** (e.g., `CFN_Templates`, `XXX`, `MOCK`, `meshToDomains`, `syntheticMonitoring`), confirmed against source mermaid |
| Key-leakage scan (extra top/meta/security/node/edge keys) | 0 everywhere |
| Project-created fake/test/template records | **0** |

Note on terminology: the word "generated" in project docs refers to the HF source
dataset, which is itself model-generated at the source; none of the 51,498 records
are project-created. Every record retains provenance to a real HF row.

---

## STEP 7 — Final recommendation

**READY WITH FILTERING.**

Conditions to be satisfied in Phase 6/7 (all evidence-backed, none require relaxing
the frozen pipeline):

1. **Filter:** train on the ≤ 20–30 node tier (start 501, expand to 5,748); include
   all 645 non-HIGH-risk records; exclude the 75 (>100 nodes) and 3 (>200 edges)
   records from direct use.
2. **Format:** input = runtime generation prompt + real instruction; loss-masked
   target = architecture JSON only (never security JSON).
3. **Split:** cluster-based (node-id set) 90/5/5 — 5,173/288/287 for the ≤30 tier.
4. **Sequence length:** `max_length = 4096` for the selected subset (p99 3,241);
   replace the stale 384 default; model context (131k) is not a constraint.
5. **Do not** train the explanation objective until real explanations exist; the
   stale `lora_train.py` (synthetic-data default, no masking, no eval split) is
   Phase 7 training-spec debt, not a data problem.
6. **Deliverable:** any training set is a NEW artifact
   (`dataset/training/CyberShield_Gemma_SFT_v1.jsonl`); `v1_FULL` stays immutable.

---

## PHASE 5 STATUS

```
Dataset:              dataset/final/CyberShield_Dataset_v1_FULL.jsonl (immutable)
Records:              51,498
Source:               ajibawa-2023/Technical-Architectures-Large (HF), rows 2..293,642
Provenance:           51,498/51,498 (source-row match + every node id in source mermaid)
Duplicates:           0 exact; 3,587 records share node sets (177 clusters); 7 near-dup pairs
Quality:              schema/graph/orphan/security gates pass; 0 malformed; 0 leaked keys
Main imbalance:       size (88.8% >30 nodes); risk HIGH 98.75%; severity has no LOW
Main risk:            training the full corpus unchanged teaches outputs the runtime
                      rejects (99.75% > hard guardrail of 10 nodes / 15 edges)
Recommended subset:   ≤20 nodes (501) strict core → ≤30 nodes (5,748) primary pool,
                      incl. all 645 non-HIGH-risk records; >30-node records only via
                      approved subgraph transformation (Phase 6)
Recommended split:    cluster-based (node-id set), 90/5/5 → 5,173 / 288 / 287 (≤30 tier)
Sequence-length:      gen prompt+target p50 1,833 / p95 2,733 / p99 3,241 tokens;
                      model context 131,072; set max_length=4096 (stale 384 truncates all)
Training format:      NL instruction → architecture JSON only (loss-masked);
                      security is engine-computed at runtime and is NOT a target
READY / NOT READY:    READY WITH FILTERING
```

---

## Verification of this report

- Corpus SHA256 before and after analysis: `e3ee9810…` — **unchanged**; 51,498 rows
  confirmed.
- All distribution figures re-measured from the corpus agree with the prior
  `training_readiness_stats.json` (identical values).
- Full provenance audit re-run over 100% of records against the 1.3 GB raw snapshot.
- Git diff contains only Phase 5 analysis artifacts
  (`dataset/scripts/training_readiness.py`, `dataset/docs/training_readiness_stats.json`,
  `dataset/docs/training_readiness_report.md`).

**STOPPED at Phase 5. No split created, no training data generated, no `lora_train.py`
or pipeline/backend/frontend change, no training started. Proceeding to Phase 6/7
requires explicit approval.**
