# CyberShield Pilot Report — 500-Record Validation (v1)

**Date:** 2026-08-11
**Source:** `ajibawa-2023/Technical-Architectures-Large` (train split, 293,640 total) — 500 records, **no new downloads, no synthetic data**
**Environment:** `uv run python` (uv 0.11.1, Python 3.12.13, pydantic 2.13.4)
**Status:** Pilot complete. Awaiting decision on full-scale generation.

---

## 1. Files changed (this correction round)

| File | Change |
|---|---|
| `dataset/scripts/mermaid_parser.py` | **Correction 1** — labeled-source edge bug fixed |
| `dataset/scripts/validate_dataset.py` | **Correction 2** — connectivity gate → orphan-free component-level rule |
| `dataset/scripts/export_jsonl.py` | Added `--output` flag (default unchanged: production filename) |
| `dataset/docs/validation_policy_analysis.md` | Analysis report (previous step) |
| `dataset/docs/pilot_report.md` | This report |

**Untouched:** `backend/core/*` (only imports reused), security engine, API, schema, frontend, Gemma/LoRA.

## 2. Exact fixes applied

### Correction 1 — parser (`mermaid_parser.py`, `_extract_edges`)

```python
# before (line 130) — dropped every edge whose source carries a label:
source_match = re.search(rf"({_ID})\s*$", prefix)
# after — optional bracket or quoted label on the source side:
source_match = re.search(rf"({_ID})\s*(?:\[[^\]\n]*\]|\"[^\"]*\")?\s*$", prefix)
```

Recovers `WebUI[Web UI] -->|HTTPS| APIGW[API Gateway]` → edge `WebUI → APIGW`.
No schema/security changes; no hardcoded node names; no fabricated edges; edges that
cannot be parsed are still skipped (never invented).

### Correction 2 — dataset validation policy (`validate_dataset.py`)

```python
# before: global weak-connectivity requirement
from backend.core.architecture_validator import is_weakly_connected
...
if not is_weakly_connected(nodes, edges):
    LOG.warning("%s: disconnected graph", sample_id); rejected += 1; continue

# after: component-level rule reusing the canonical backend function
from backend.core.architecture_validator import has_orphan_node
...
if has_orphan_node(architecture):
    LOG.warning("%s: isolated node(s) present", sample_id); rejected += 1; continue
```

Multiple connected components are now allowed; completely isolated nodes are not.
No change to backend code (function reused), no weakening of schema / node-edge
integrity / security checks.

## 3. Funnel — before vs after

| Stage | Before fixes | After fixes | Delta |
|---|---|---|---|
| raw | 500 | 500 | 0 |
| parsed | 478 | 478 | 0 |
| parse failures | 22 (21× no flowchart/graph directive, 1× unsupported `mermaid` type) | 22 (same) | 0 |
| enriched | 477 | **478** | **+1** (CSA-000153 recovered by parser fix) |
| enrichment failures | 1 (CSA-000153 empty architecture) | 0 | −1 |
| validated | 20 | **152** | **+132** |
| validation failures | 457 (all "disconnected graph") | 326 (all "isolated node(s) present") | −131 |
| reviewed | 20 | **152** (20 prior + 132 auto-approved, `--auto a`) | +132 |
| **final** | 20 | **152** | **+132** |

## 4. Recovery attribution (exact, via `git show 0e81a11` original parser vs fixed parser × old gate vs new gate, all 478 parsed records)

| Path | Accepted | Notes |
|---|---|---|
| Baseline (old parser + old gate) | 20 | |
| **A — parser fix alone** (old gate + fixed parser) | **+38** → 58 | fully-connected-after-fix victims of the dropped-label bug (e.g. CSA-000007, 31 dropped edges) |
| **B — policy change alone** (new gate + old parser) | **+21** → 41 | no-orphan multi-component records whose disconnect came only from source structure, not drops |
| **C — both required** | **+73** → 152 | needed the parser repair *and* component-level policy |
| **Final** | **152** | |

Monotonicity check: **zero** records accepted before are rejected now (132 gained, 0 lost).

## 5. Remaining rejections (326) — categories

All 326 rejected under the new gate contain ≥1 completely isolated node (every node
must participate in at least one relationship):

| Orphan nodes per record | Records | Share |
|---|---|---|
| 1 | 80 | 24.5% |
| 2 | 46 | 14.1% |
| 3–9 | 140 | 42.9% |
| 10–99 | 60 | 18.4% |

- 277 of 326 (85%) still have a dominant component (≥50% of nodes) — they fail **only**
  because of isolated/decorative nodes (compliance badges such as PCI/HIPAA/GDPR,
  observability tiles, unwired client placeholders), not because they are fragmented.
- Genuinely fragmented debris (e.g. CSA-000030: components [17,16,10,8,6,2] + 5 orphans;
  CSA-000033: 10 unwired placeholder nodes) remain rejected, as intended.
- Note for the deferred ≥50% dominant-component rule: it would **not recover any** of the
  326 (all contain orphans); it only tightens P1 by excluding 6 multi-component records.

## 6. Provenance verification (final pilot, 152 records)

- 152/152 unique ids; every id maps 1:1 to an HF row (ids 2–499 of the raw sample set).
- 152/152 `metadata.source == "Technical-Architectures-Large"`, `version == "1.0"`,
  `reviewed == true`.
- 0 provenance issues found. No template/legacy records, no synthetic records.

## 7. Deterministic quality review (first 25 accepted records in id order)

| Check | Result |
|---|---|
| Nodes valid type (schema) | 25/25 |
| Edges valid source/target/label | 25/25 |
| Components ≥1, all nodes in a component | 25/25 (e.g. CSA-000008 [32,32] two-region topology) |
| Isolated nodes | 0 in all 25 |
| Security enrichment: threats, recommendations, required controls, missing controls, risk level | 25/25 complete |
| `collect_issues` errors | none structural (see size note below) |

**Size note:** `backend/core/architecture_validator.py` flags `size_guardrail` for graphs
>10 nodes / >15 edges. These are **runtime generator limits** (the demo inference path),
not dataset limits — `validate_dataset.py` intentionally does not apply them, and the
backend's `raise_if_invalid` is not part of the dataset pipeline. All pilot records
(24–101 nodes) exceed the runtime limit by design; this is an expected boundary between
curated dataset content and runtime generation, not a data defect.

**Full-pilot aggregates:** risk level HIGH 152/152 (all real architectures with open
security gaps — consistent with enrichment semantics); threats, recommendations,
required controls, and missing controls present in 152/152.

## 8. Application impact verification

- All backend modules import cleanly (core, security analyzer/catalog/report/validator/
  threat detector, API main).
- Frontend TypeScript check: `npx tsc --noEmit` — **passes**.
- No API contract, frontend behavior, or security-engine logic changed.

## 9. Readiness for full-scale generation

**Recommended path is now viable, with the following positions:**

1. **Yes** — the pipeline mechanics (convert → enrich → validate → review → export) and
   the two corrected behaviors are verified on real data; expected yield at scale:
   ≈30% of *parseable* records (152/478 ≈ 31.8%), which at 293,640 total would produce
   a large representative dataset without fabrication.
2. **Before full scale, decide:**
   - Keep P1 (orphan-free) as validated here, or evaluate P3 (dominant ≥50% guard) —
     P3 would recover 0 additional records and exclude only 6 multi-component records
     from the pilot.
   - Set a size guardrail appropriate for *dataset* records if runtime compatibility
     matters (currently none; records up to 101 nodes).
   - Review policy for the 60 heavily-decorative records (≥10 orphans) if compliance/
     observability tiles should be tolerated in future batches.
3. **Do not start full-scale generation without explicit approval.**

## 10. Artifacts

- `dataset/final/CyberShield_Dataset_Pilot_v1.jsonl` — **152 records** (pilot)
- `dataset/final/CyberShield_Dataset_v1.jsonl` — **restored** to production state
  (1 record, CSA-000004) from commit `dc0ea0f`; not overwritten by the pilot export
- `dataset/docs/validation_policy_analysis.md` — root-cause analysis
- `dataset/logs/` — per-stage logs from this run