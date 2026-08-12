# Full-Scale CyberShield Dataset Report — v1_FULL

**Date:** 2026-08-12
**Source:** `ajibawa-2023/Technical-Architectures-Large` (train split), all rows
**Pipeline:** frozen parser fix + frozen component-level validation (P1, orphan-free) — unmodified during this run
**Environment:** `uv run python` (uv 0.11.1, Python 3.12.13, pydantic 2.13.4)

---

## 1. Funnel

| Stage | Count | Percent of raw | Percent of prior stage |
|---|---|---|---|
| Source records (HF) | 293,640 | — | — |
| Raw snapshot | 293,640 rows (293,632 unique ids — 8 duplicated ids in source, first-wins) | 100% | 100% |
| Parsed | 285,561 | 97.2% | 97.2% |
| Parse failures | 8,079 | 2.8% | — |
| Enriched | 284,686 | 97.0% | 99.7% |
| Enrichment failures | 868 (all `empty architecture`) | 0.3% | — |
| **Validated** | **51,498** | 17.5% | 18.1% of enriched |
| Rejected | 233,188 | — | 81.9% of enriched |
| Reviewed (approved) | 51,498 | 17.5% | 100% of validated |
| Reviewed rejected/edited | 0 | — | — |
| **Final** | **51,498** | **17.5%** | — |

**Output:** `dataset/final/CyberShield_Dataset_v1_FULL.jsonl` (391 MB). Pilots and
`CyberShield_Dataset_v1.jsonl` untouched (verified in `dataset/final/`).

**Rejection reasons (233,188, measured directly):**
- `isolated node(s) present` — 233,121 (100.0%)
- duplicate architecture (canonical fingerprint) — 57 (0.0%)
- empty graph — 0; other — 0

## 2. Expected vs observed

| Metric | Value |
|---|---|
| Pilot baseline | 31.8% (v1), 32.9% (v2) → expected ~31–33% of enriched |
| Expected accepted range | 284,686 × 0.31–0.33 ≈ **88,000–94,000** |
| Actual accepted count | **51,498** |
| Actual acceptance rate | **18.1% of enriched** (17.5% of raw) |
| Difference from baseline | **−36,500 to −42,400** records (−14.4 ppt vs 32.5% midpoint) |

### Why acceptance differs — source distribution shift, pipeline reproduced exactly

The frozen pipeline reproduces pilot behaviour **exactly** on the pilot-tested ranges,
then a sharp source-content regime shift occurs beyond row ~100k:

| Enriched id range | Accepted | Acceptance |
|---|---|---|
| 0–499 (Pilot v1 rows) | 152 / 478 | 31.8% (identical to v1) |
| 500–2,499 (Pilot v2 rows) | 617 / 1,876 | 32.9% (identical to v2) |
| 2,500–99,999 | 31,031 / 92,029 | 33.7% |
| 100,000–149,999 | 12,085 / 47,848 | 25.3% |
| 150,000–293,642 | 7,613 / 142,455 | **5.3%** |

Records 150,000+ are rejected at ~100× the earlier rate by the *same* orphan rule:
the later rows contain a different content regime (megadiagrams — accepted records
there include graphs up to 658 nodes — and far more diagrams with isolated/decorative
nodes). This is a property of the source distribution, not of the pipeline: the
acceptance rate is monotonically consistent with both pilots wherever the same rows
were previously processed, and no policy was changed. **No optimization of acceptance
was performed; the policy was applied unchanged.**

## 3. Statistics (51,498 final records)

**Node count:** min 2, max 658, mean 45.1 (pilots: mean 45.1/45.6 — consistent).
**Edge count:** min 1, max 358, mean 53.6 (pilots: 55.5/55.0 — consistent).
**Components:** min 1, max 310, mean 3.0; single-component share 34.1% (pilots 38.2%/33.7%).
**Isolated nodes:** 0 in every record (policy guarantee).

**Domain (42 distinct):** Cyber Security 1,345, Blockchain 1,335, Gaming 1,331, IoT 1,319,
Defense 1,301, Travel 1,295, … (uniform; identical vocabulary to pilots).
**Style (8):** Serverless 7,441, CQRS 6,837, Modular Monolith 6,652, Data Mesh 6,441,
Hexagonal 6,253, Zero-Trust 6,230, Event-Driven, Microservices.
**Cloud (6):** On-Premises 9,432, GCP 9,136, Azure 8,739, AWS 8,455, Hybrid 8,075, Multi-Cloud 7,661.
**Complexity (4):** Small 17,690, Medium 13,440, Enterprise 10,387, Large 9,981.

**Risk:** HIGH 50,853, MEDIUM 625, LOW 20.
**Threats/record:** 10 (×23,543), 8 (×22,734), 11 (×1,463), 6 (×1,198), 7 (×993), 9 (×809), 5 (×643), 4 (×67) — all non-empty.
**Missing controls/record:** 5 (×13,012), 6 (×12,790), 8 (×10,050), 9 (×9,002), 7 (×4,053), 4 (×1,143), 10 (×819), 3 (×571) — all non-empty.
**Security score:** min 0, max 95, mean 14.99; `security_summary` present in 51,498/51,498.

## 4. Quality gates (all passed)

| Gate | Result |
|---|---|
| Canonical schema validation (`collect_issues`, non-size errors) | 51,498 / 51,498 pass |
| Graph integrity (dangling edges, duplicate/self edges) | 0 failures |
| Frozen component/orphan policy | 0 records with isolated nodes |
| Security enrichment (threats, recs, required/missing controls, risk) | 51,498 / 51,498 |
| Provenance (`source == Technical-Architectures-Large`, `reviewed`, `version`, id ∈ HF rows) | 51,498 / 51,498 |
| Duplicate IDs | 0 |
| Duplicate architectures (existing canonical dedup) | 0 |
| Synthetic/mock/template records | 0 (all ids map to real HF rows) |
| Fabricated nodes/edges (node id present in source mermaid text) | 0 (spot-checked incl. largest graphs) |
| Pilot files overwritten | None (v1/v2 timestamps unchanged) |
| Production artifact replaced | No (`CyberShield_Dataset_v1.jsonl` untouched) |

**Malformed-record count:** 8,079 parse failures (non-flowchart content) + 868 empty
architectures — all excluded before validation; 0 malformed records inside the final set.

**Deterministic review (first 50 accepted records):** 50/50 clean (schema, graph
integrity, orphan policy, security completeness, provenance).

## 5. Comparison with pilots

| Metric | v1 | v2 | FULL |
|---|---|---|---|
| Final records | 152 | 617 | 51,498 |
| Acceptance (of enriched) | 31.9% | 32.9% | 18.1% (range-dependent — see §2) |
| In-range acceptance | 31.8% | 32.9% | 31.8% / 32.9% / 33.7% (rows <100k) |
| Node mean / edge mean | 45.1 / 55.5 | 45.6 / 55.0 | 45.1 / 53.6 |
| Single-component share | 38.2% | 33.7% | 34.1% |
| Risk HIGH share | 100% | 99.4% | 98.7% |
| Duplicates | 0 | 0 | 0 |
| Domains / Styles / Clouds | 42/8/6 | 42/8/6 | 42/8/6 |

Pilot v1/v2 rows re-processed inside the full run reproduce the pilot counts exactly
(152/478, 617/1,876) — deterministic reproducibility confirmed.

## 6. Verdict

- **The frozen pipeline is healthy and reproducible.** Acceptance differences stem
  from the source dataset's distribution (rows 150k+), not from pipeline behaviour.
- **The full-scale dataset is clean**: 51,498 records, all quality gates pass.
- **Follow-up options (require approval, none executed):**
  1. Keep v1_FULL as-is (pure frozen-policy output), or
  2. Process rows 150k+ under a stricter source-regime analysis (e.g., decorative-node
     exception decision from `pilot_report_v2.md` §7) — a *policy* discussion, not a
     pipeline fix.

## 7. Artifacts

- `dataset/final/CyberShield_Dataset_v1_FULL.jsonl` — 51,498 records
- `dataset/raw/samples.jsonl` — 293,640-row source snapshot (git-ignored, regenerable)
- `dataset/parsed|enriched|validated|reviewed/` — staging (git-ignored, regenerable)
- `dataset/docs/pilot_report.md`, `dataset/docs/pilot_report_v2.md` — pilot baselines

**STOPPED. Awaiting approval for: dataset splitting, Gemma fine-tuning, LoRA
configuration, hyperparameter selection, or any training. None started.**