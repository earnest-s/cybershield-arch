# Validation Policy Analysis — 500-Record Pilot

**Date:** 2026-08-10
**Scope:** Pilot of `ajibawa-2023/Technical-Architectures-Large` (500 samples)
**Environment:** `uv run python` (uv 0.11.1, Python 3.12.13, pydantic 2.13.4)
**Status:** Analysis only — no pipeline, parser, schema, or backend code was modified.

---

## 1. Summary

The pilot converted 478 of 500 raw records into architecture JSON; 477 were enriched;
**validation accepted 20 records and rejected 457**, every one with the reason
`disconnected graph`. The 96% rejection rate is caused by **two compounding defects**:

1. **Parser/conversion defect (`FIX`):** `mermaid_parser.py` silently drops every edge
   whose source node carries a bracket or quoted label (`WebUI[Web UI] -->|HTTPS| APIGW`).
   This destroys relationships, orphans nodes, and shreds otherwise connected graphs.
2. **Validation policy defect (`MODIFY`):** the pipeline requires the whole graph to be
   one weakly-connected component (`is_weakly_connected`), which rejects legitimate
   multi-component architectures and multi-region deployments, and conflates them with
   genuinely broken diagrams.

Neither change alone recovers the rejected samples; both are required.

## 2. Rejection path (evidence, not assumption)

The end-to-end path for a disconnected-graph rejection:

```
HF record (mermaid text)
  → dataset/scripts/convert_dataset.py:26  parse_to_json()
  → dataset/scripts/mermaid_parser.py:153  parse_mermaid()   # edges dropped HERE
  → dataset/scripts/enrich_dataset.py      stores {"architecture": {nodes, edges}}
  → backend/core/architecture_validator.py:34  is_weakly_connected()
  → dataset/scripts/validate_dataset.py:122   if not is_weakly_connected(nodes, edges):
  → dataset/scripts/validate_dataset.py:123   LOG.warning("%s: disconnected graph", ...)
  → dataset/scripts/validate_dataset.py:124   rejected += 1
```

- `validate_dataset.py:29` imports `is_weakly_connected` from
  `backend/core/architecture_validator.py`.
- **The string "disconnected graph" is generated only at `validate_dataset.py:123`.**
  All 457 rejected records reached exactly this line; no other rejection reason fired
  (confirmed by the validated count and by re-running the checks from the enriched
  records: all 457 pass node-type, edge-label, dangling-edge, and security checks and
  fail only the connectivity gate at `validate_dataset.py:122`).
- The backend's own `validate_architecture()` (`architecture_validator.py:164-180`) is
  **not** used by the dataset pipeline; the pipeline re-implements a subset of checks.

## 3. Methodology

- **Population:** all 477 enriched records (the 1 enrichment failure, CSA-000153 empty
  architecture, is out of scope; the 21 records rejected at conversion for "no flowchart
  or graph directive found" and 1 for "unsupported diagram type: 'mermaid'" are conversion
  rejects described in §9).
- **Reference implementation:** `parse_mermaid()` re-run via an in-memory, patched copy of
  `_extract_edges` (`/tmp/opencode/mermaid_patch_lib.py`. **No repository file was touched.**
  The patch only adds an optional `[label]`/quoted-label match on the **source** side of an
  arrow; every other parser behavior is identical.
- **Analysis per record:** original vs patched node/edge counts, connected components,
  per-node degree (orphans), subgraph blocks, dropped-edge lines, orphan identity.
- **Exact verification:** on the first 40 rejected records, the heuristic "arrow whose
  source prefix ends in `]`/`}`/`"`" matched the true edge delta **36/40** (the 4
  mismatches are over-counts by 1-3 from quoted labels in node definitions).

## 4. Defect 1 — Parser drops labeled-source edges (FIX)

At `mermaid_parser.py:127-133`, for each arrow token the source is matched with:

```python
source_match = re.search(rf"({_ID})\s*$", prefix)      # line 130
```

`_ID` is `[A-Za-z0-9_][A-Za-z0-9_-]*` (line 33). When the source node carries a label
bracket (or quoted label), the character immediately before the arrow is `]` or `"`, so
this regex cannot match and **the edge is silently dropped** (`continue`, line 133).
The node may still be created later by `_NODE_DEF`, leaving it orphaned.

Affected syntax (extremely common in this dataset — every subgraph-layered diagram
uses it):

```mermaid
WebUI[Web UI] -->|HTTPS| APIGW[API Gateway]
MobileApp[Mobile Apps] -->|REST/GraphQL| APIGW
CDN[CDN Edge] -.->|Cache| APIGW
```

Measured impact (see §7 for per-sample numbers):

- **2,826** edge lines at risk across the **215/457** (47.1%) rejected records that contain
  at least one such arrow.
- Across **all 478 parsed records**: original parse yields **22,601** edges; patched parse
  yields **25,302** — **≈2,700 edges (≈11%) destroyed** (25,776 arrow tokens ⇒ 12.3% loss
  under the original parser vs 1.8% under the patch).
- **1,947 of 4,444 orphan nodes** in the rejected records (43.8%) are *parser-caused*:
  they have ≥1 incident edge once the labeled-source edge is preserved.
- **205/457** rejected records have fewer connected components under the patched parse;
  **38** become fully connected.

### 4.1 Subgraph/cluster investigation

All 457 rejected records use `subgraph` blocks (`subgraph` titles recorded at
`mermaid_parser.py:192-197`; subgraph ids become nodes only if referenced by edges —
there is no subgraph-id → cluster node registration). Two findings:

1. **No separate subgraph-cluster defect exists.** Edges that reference a subgraph *id*
   (`S1 --> S2`) or cross cluster boundaries parse correctly when the source is a bare id.
   Cluster boundaries themselves do not break connectivity in the parser.
2. **Cluster-scoped labeled sources are the dominant loss pattern.** Edges *inside* a
   subgraph that point at labeled client/badge nodes (`WebUI[Web UI] -->|HTTPS| APIGW`
   inside `subgraph CLIENTS`) are dropped by Defect 1. This is a parser bug, not a
   subgraph semantic loss. The one genuine *diagram-level* pattern is **annotative
   clusters** — self-contained compliance/observability subgraphs (`PCI-DSS`,
   observability tiles) that the author never wires into the main flow (see §5).

## 5. Defect 2 — Connectivity policy rejects legitimate architectures (MODIFY)

`validate_dataset.py:122` requires the *entire* graph to be one weakly-connected
component. Orphan nodes (`has_orphan_node`, `architecture_validator.py:59-81`) are not
checked by the pipeline at all — the pipeline rejects purely on connectivity, which
subsumes orphans. This rule treats three structurally different cases identically:

| Case | Example | Correct handling |
|---|---|---|
| Genuinely broken (unwired placeholder nodes) | CSA-000033 | Reject |
| Legitimate multi-component / multi-region | CSA-000008 | Accept |
| Isolated decorative/compliance tile | CSA-000030 | Reject (or warn) |

The backend already expresses the component-level semantics:
`is_structurally_weak = not connected or has_orphan_node` (`architecture_validator.py:84-88`)
— a diagram with zero orphan nodes but several components is *not* structurally weak
there. The pipeline hardens this into a global-connectivity requirement.

### 5.1 Rejection categories (patched-parse basis, n = 457)

| Category | Count | Share | Definition |
|---|---|---|---|
| **A. Legitimate multi-component architecture** | 94 | 20.6% | No orphan nodes; ≥2 components, each substantial (≥2 nodes). E.g. CSA-000008 (two 32-node regions), CSA-000013 (51-node core + 5 workstreams). |
| **B. Parser/conversion defect (primary victim or contributor)** | 215 | 47.1% | ≥1 edge dropped by the labeled-source bug; includes the 38 fully-connected-after-fix records that are rejected *for no reason other than the parser bug*. |
| **C. Genuinely malformed / debris** | 67 | 14.7% | Scattered components plus orphan nodes (e.g. CSA-000030: components [17,16,10,8,6,2] + 5 orphans). |
| **D. Isolated decorative/annotative node** | 325 | 71.1% | ≥1 genuine orphan (no incident edge even in the source). 2,497 genuine orphans across 457 records; 576 (23%) are compliance/ops tiles (PCI, HIPAA, GDPR, SOC2, ISO, monitoring/observability ids). |
| **E. Isolated annotative cluster** (subset of A/D) | — | — | Self-contained compliance/observability subgraph never wired into the main flow (e.g. the `COMPLIANCE` cluster in CSA-000030). |

Categories overlap by design — a record can be B and D at once (drops *and* genuine
decoration). Percentages are shares of 457.

### 5.2 Representative rejected records (verified line-by-line)

| Record | Original | Patched | Verdict |
|---|---|---|---|
| CSA-000007 | N=50, E=30, 21 orphans, disconnected | N=50, E=61, **one component of 50**, 0 orphans | **B** — rejected solely by parser bug (31 dropped edges incl. `CDN[CDN Edge] -.->|Cache| APIGW`). High-quality architecture. |
| CSA-000002 | 14 dropped edges | fully connected [N=33] | **B** — parser bug only. |
| CSA-000031 | 22 dropped edges | fully connected [N=43] | **B** — parser bug only. |
| CSA-000008 | 26 dropped edges, 21 orphans | N=64, E=74, components **[32,32]**, 0 orphans | **A** — two-region active/active topology (subgraphs "Microservices – Region A/B", "Data Layer – Region A/B"); regions never share a direct edge in the source: parallel deployment of identical architecture. |
| CSA-000013 | 45 dropped edges, 28 orphans | components [51,7,4,3,3,3], 0 orphans | **A** — core platform + satellite workstreams; drops shredded it further. |
| CSA-000030 | 32 dropped (e.g. `WebUI[Web UI] -->|REST/GraphQL| APIGW[API Gateway]`) | components [17,16,10,8,6,2] + **5 genuine orphans** (VPC, CloudDNS, CloudIAM, CloudLoad, CloudScheduler) | **C+D** — even perfectly parsed it is debris plus an unwired `COMPLIANCE` cluster (PCI badge annotating `LOG[Logging & Monitoring]`). Correctly rejected under any policy. |
| CSA-000033 | **0 drops** | 10 genuine orphans: WEB, MOBILE, ADMIN, CDN, WAF, LB, IAM, OIDC, MFA, VAULT — defined in the source but never wired | **C/D** — genuine source flaw; the orphan rule correctly rejects it. |
| CSA-000001 | 19 dropped | 5 badge orphans (PCI/HIPAA/GDPR/SOC2/ISO) + dominant comp (78%) | **D+B** — decorative compliance badges recover under a no-orphan rule. |

### 5.3 Accepted-20 comparison

All 20 accepted records are single-component with zero orphans (their selection is the
artifact of the gate itself — e.g., CSA-000004 N=57/E=70, CSA-000407 N=56/E=84). They
contain almost no labeled-source edge patterns of the Defect-1 form (measured: only 1
risk line across all 20, in CSA-000004) — the accepted set structurally avoided the
parser defect by chance. The accepted set shows no
meaningful structural advantage over the 94 Category-A rejects besides connectivity;
the rejects at [32,32] component size are architecturally richer than most accepted
records.

## 6. Policy × parser interaction matrix (the decisive numbers)

Measured on the 457 rejected records (policy applied to the parsed graph):

| Policy | Original parse (current pipeline) | Patched parse |
|---|---|---|
| **P0** weakly connected (current) | 0 pass | 38 pass |
| **P1** orphan-free (every node has ≥1 edge; components allowed) | 21 pass | **132 pass** |
| **P3** orphan-free AND largest component ≥50% of nodes | — | 126 pass |

Including the 20 already accepted (of 478 parsed):

- Current (P0 + original parser): **20 records – 4.2%**
- Parser fix only (P0 + patched): **58 – 12.1%**
- Policy fix only (P1 + original parser): **41 – 8.6%**
- **Both fixes (P1 + patched): 152 – 31.8%**
- **Both fixes, P3 version (dominant-component guard): 146 – 30.5%**

The matrix proves neither defect explains the funnel alone; **both repairs are
necessary** for the pilot to be representative.

## 7. Numbers at a glance

```
Rejected records analyzed          457
Records with ≥1 dropped edge      215  (47.1%)     ← Defect 1
Edges dropped (arrow lines)     2,826  (est.)
Records whose component count
  shrinks under patched parse     205
Records fully connected after
  parser fix                       38  (8.3%)
Orphan nodes in original parse   4,444
  - parser-caused                1,947  (43.8%)
  - genuine, incl. decorative    2,497
      badge/ops-like orphans       576  (23% of genuine)
Records with ≥1 genuine orphan    325  (71.1%)     ← Defect 2 surface
Records with no orphans but
  multiple components              94              ← legitimate topologies
```

## 8. Recommendation

### DO ALL THREE — with FIX and MODIFY as a pair

1. **FIX — `dataset/scripts/mermaid_parser.py`**
   Repair `_extract_edges` (line 130): allow the source to carry an optional
   bracket/quoted label, e.g.
   `source_match = re.search(rf"({_ID})\s*(?:\[[^\]\n]*\]|\"[^\"]*\")?\s*$", prefix)`.
   This is a pure correctness repair of the conversion stage: it restores
   ~2,700 genuine relationships and 38 instantly-valid records. It does not weaken
   anything; it makes the converter faithful to the source.

2. **MODIFY — `dataset/scripts/validate_dataset.py` (pipeline policy only)**
   Replace the global `is_weakly_connected` gate (line 122) with the component-level
   rule the backend already implements: **reject iff any node has incident degree 0**
   (use `has_orphan_node`, `architecture_validator.py:59`), optionally adding the
   dominant-component guard (largest component ≥50% of nodes, P3) to exclude debris
   like CSA-000030. Keep rejecting:
   - genuinely unwired placeholder graphs (CSA-000033, CSA-000030) and
   - the existing empty-graph / dangling-edge / duplicate checks (no changes there).
   Legitimate multi-region and multi-workstream topologies (CSA-000008, CSA-000013)
   then pass **for architectural reasons, not by weakening** — the rule is
   "every declared node must participate in the architecture", which is exactly the
   definition of structurally-sound at component level.

3. **KEEP** the connectivity concept and the backend unchanged:
   - Do **not** remove validation, and **do not** touch
     `backend/core/architecture_validator.py` / `architecture_schema.py` / the
     security engine — the backend contract stays the runtime-facing one.
   - The pipeline script (a `dataset/` artifact) is the only place the policy lives.

**Why both:** the matrix above. Parser-only yields 58/478; policy-only yields 41/478;
together 146–152/478 (≈30% representativeness vs 4.2% now). The pilot's goal is a
representative first sample; 20 records cannot represent the distribution of
architectures in this source, and 457 rejections are mostly measurement error, not
architecture quality.

**Expected outcome for the pilot:** 146–152 records accepted (P1/P3 versions differ by
6 debris-like records), re-exported pilot `CyberShield_Dataset_Pilot_v1.jsonl`, and
production `CyberShield_Dataset_v1.jsonl` restored from git (it was overwritten by the
earlier pilot export run).

## 9. Out-of-scope conversion rejects (for completeness)

Of 500 raw records: 21 rejected at conversion ("no flowchart or graph directive found")
and 1 ("unsupported diagram type: 'mermaid'") — these are records whose *text is not a
Mermaid flowchart* (prose articles, sequence diagrams). Counted as genuinely unusable
source for this pipeline (Category C equivalent at conversion stage), not policy issues.

## 10. Open questions / next step

- If FIX+MODIFY (P1 or P3) is approved: implement, re-run
  convert → enrich → validate → review for the affected records, then export the pilot
  and write `dataset/docs/pilot_report.md`.
- Record-level spot check of the ~146 candidates before export (25-record quality
  review) to confirm the component-level verdicts on Category-A records.