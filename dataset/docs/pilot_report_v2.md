# CyberShield Pilot Report v2 — 2,000-Record Measurement Run

**Date:** 2026-08-11
**Source:** `ajibawa-2023/Technical-Architectures-Large` (train split), HF rows **500–2,499**
**Policy:** corrected pipeline — parser fix + component-level validation (P1, orphan-free). Unchanged during this run.
**Environment:** `uv run python` (uv 0.11.1, Python 3.12.13)

---

## 1. Funnel (Pilot v2)

| # | Stage | Count | Notes |
|---|---|---|---|
| 1 | raw | **2,000** | HF rows 500–2499, no synthetic/template records |
| 2 | parsed | **1,885** | |
| 3 | parse failures | **115** | see reasons below |
| 4 | enriched | **1,876** | |
| 5 | enrichment failures | **9** | all `empty architecture` (CSA-000614, 000965, 000994, 001032, 001156, 001498, 001748, 002191, 002240) |
| 6 | validated | **617** | |
| 7 | rejected | **1,259** | 100% `isolated node(s) present` (measured directly; no other reason fired) |
| 8 | reviewed | **617** | auto-approved (`--auto a`), all logged |
| 9 | final | **617** | → `dataset/final/CyberShield_Dataset_Pilot_v2.jsonl` |
| 10 | acceptance rate | **32.9% of enriched** (617/1,876) · 30.9% of raw (617/2,000) | |

**Parse-failure reasons (115):** `no flowchart or graph directive found` ×104,
`unsupported diagram type: 'DR'` ×5, `'high'` ×3, `'auto'` ×1, `'User'` ×1, `'mermaid'` ×1
— all non-flowchart content in source records.

## 2. Structure distributions (617 accepted)

| Metric | Distribution |
|---|---|
| 11. Node count | range 10–113, mean 45.6; mode 38 (×32), 36 (×25), 44 (×25), 47 (×24), 32 (×24) |
| 12. Edge count | range 11–128, mean 55.0; mode 54 (×24), 57 (×21), 67 (×20) |
| 13. Connected components | 1 (×208, 33.7%), 2 (×172), 3 (×89), 4 (×64), 5 (×35), 6 (×16), …up to 28; mean 2.7 |
| 14. Isolated nodes | **0 in all 617** (policy guarantee) |

## 3. Security distributions (617 accepted)

| Metric | Distribution |
|---|---|
| 16. Risk level | HIGH 613 (99.4%), MEDIUM 3, LOW 1 |
| 17. Threats per record | 8 (×237), 10 (×320), 9 (×12), 7 (×9), 6 (×20), 3–5 (×4) — all non-empty |
| 18. Missing controls | 2–10 per record; modes 6 (×174), 8 (×133), 9 (×131), 5 (×100); all non-empty |
| — | required_controls 617/617, recommendations 617/617, security_summary 617/617; security_score min 0, max 85, mean 13.3 |

## 4. Metadata distributions (617 accepted)

| Metric | Distribution (top) |
|---|---|
| 19. Domain | 42 distinct: Travel 24, Blockchain 24, IoT 21, MLOps 19, ERP 18, Energy 18, Defense 18, Agentic AI 17… |
| 20. Style | 8 distinct: Modular Monolith 84, Serverless 83, CQRS 80, Microservices 79, Event-Driven 79, Hexagonal 76, Data Mesh 72, Zero-Trust 64 |
| 21. Cloud | 6 distinct: On-Premises 118, GCP 111, Hybrid Cloud 103, Azure 96, AWS 96, Multi-Cloud 93 |
| 22. Complexity | 4 distinct: Small 206, Medium 152, Enterprise 148, Large 111 |

## 5. Duplicates & provenance (23, 24)

- **23. Duplicate rate: 0** — no duplicate architectures among the 617 (canonical
  node-set/edge-set fingerprint), consistent with the validator's duplicate rejection.
- **24. Provenance: PASS** — 617/617 unique ids; all ids in range 501–2488 ⊂ 500–2499;
  617/617 `source == "Technical-Architectures-Large"`, `version == "1.0"`,
  `reviewed == true`; each id maps 1:1 to an HF row.

## 6. Deterministic review (50 accepted records, first 50 by id)

| Check | Result |
|---|---|
| Node ids/types valid | 50/50 |
| Edges reference existing nodes (no dangling) | 50/50 |
| Components ≥1, no isolated nodes | 50/50 |
| Threats, recommendations, required/missing controls, risk level present | 50/50 |
| `collect_issues` errors | none (except runtime `size_guardrail` for >10 nodes — excluded from dataset policy by decision 2; every pilot record exceeds it by design) |
| Spot-check examples | CSA-000501 [24,3], CSA-000550, CSA-002488 — multi-component topologies, valid security enrichment |

## 7. Decorative/compliance-node investigation (decision 3 — measured, policy unchanged)

Analyzed all **10,018 orphan occurrences (2,929 unique ids)** in the 1,259 rejected
records:

| Category | Occurrences | Share | Examples |
|---|---|---|---|
| Architectural component (genuinely unwired in source) | 7,579 | 75.7% | VPN, RedisCache, S3, RDS, ACR, CDN, LoadBalancer, VPCs, Istio, CI/CD |
| Security control node (unwired) | 1,193 | 11.9% | MFA 124, KMS 117, Vault 95, PKI 107, RBAC, SSO, WAF |
| Security/compliance metadata | 959 | 9.6% | GDPR 200, PCI 173, SOC2 132, HIPAA 116, ISO 69 |
| Observability/decorative annotation | 287 | 2.9% | Prometheus 45, ELK 49, OTEL 60, Grafana, Datadog |

**Conclusion:**
- The overwhelming majority of isolated nodes are **genuine architectural components the
  diagram author never wired** — rejecting them is correct under the current policy.
- Only **~12.5%** (compliance badges + observability tiles) are annotation-like.
- Recommendation (no action taken this run): if full-scale generation should tolerate
  compliance/observability tiles, introduce a narrowly-scoped exception list at the
  *validator* level (metadata-only nodes) — NOT a blanket orphan relaxation. Keep the
  current policy for now; revisit after full-scale yield review.

## 8. Pilot v1 vs Pilot v2

| Metric | v1 (500) | v2 (2,000) |
|---|---|---|
| Final records | 152 | 617 |
| Acceptance (of enriched) | 31.9% | **32.9%** (consistent) |
| Node count | 19–101, mean 45.1 | 10–113, mean 45.6 |
| Edge count | 24–117, mean 55.5 | 11–128, mean 55.0 |
| Components | 1–11, mean 2.5 | 1–28, mean 2.7 |
| Single-component share | 38.2% | 33.7% |
| Risk HIGH share | 100% | 99.4% |
| Domains | 42 | 42 (same vocabulary) |
| Complexity | S55/M37/E36/L24 | S206/M152/E148/L111 (same shape) |

v1 and v2 are statistically consistent: same acceptance rate (~32–33%), same size
profiles, same metadata vocabulary. The pipeline is stable across batches.

## 9. Freeze recommendation

**Yes — freeze the current pipeline as the production dataset-generation policy** for
full-scale processing, based on:
- two independent pilots with consistent ~33% acceptance of enriched records;
- zero duplicates, full provenance, 50/50 deterministic review passing all
  dataset-relevant checks;
- rejection is now exclusively the intended "isolated node" rule.

Freeze = parser fix + component-level validation (P1) + current schema/security engine.
Explicitly **not** in the freeze: dominant-component ≥50% rule (deferred), runtime
size limits on dataset records (excluded), decorative-node exception list (open item
from §7).

## 10. Artifacts

- `dataset/final/CyberShield_Dataset_Pilot_v2.jsonl` — **617 records**
- `dataset/raw/samples.jsonl` — pilot v2 raw (rows 500–2499)
- `dataset/raw/samples_pilot1.jsonl` — pilot v1 raw preserved
- `dataset/pilot1_staging/{parsed,enriched,validated,reviewed}` — pilot v1 staging preserved
- `dataset/docs/pilot_report.md` — v1 report (unchanged)

**STOP — awaiting decision on full-scale 293k generation. Not started.**