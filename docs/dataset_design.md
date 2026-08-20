# CyberShield-Arch Dataset Design

## 1. Motivation and contribution

CyberShield-Arch is a threat-aware software architecture generator: a local
LLM converts natural-language system descriptions into architecture graphs,
and a deterministic security engine (FastAPI + React frontend) scores each
graph against a catalog of 12 security controls and 11 threat types.

This dataset is the supervised fine-tuning corpus that teaches the generator
to produce *secure* architecture graphs out of the box. Its distinctive
feature is that every sample carries a **machine-verified security label**
computed by the same production security engine used at inference time.
There is no gap between training labels and deployment behaviour: a sample
whose security section says `missing_controls: ["WAF"]` is a graph that the
deployed engine would indeed flag for a missing WAF.

**Contribution of the dataset:** a domain-diverse, deterministically
labelled, human-reviewed corpus of (description, architecture, security)
triples with a fully auditable provenance pipeline.

## 2. Dataset scope and composition

- **12 domains**: banking, healthcare, cybersecurity, cloud, IoT, e-commerce,
  education, smart city, logistics, microservices, DevOps, AI platforms.
- **3 difficulty tiers** per domain: easy (4 nodes), medium (6), hard (8).
- **2 security variants** per (domain, difficulty): *insecure* (no controls
  embedded; engine reports most required controls missing) and *hardened*
  (critical controls embedded as first-class nodes; engine reports few or no
  missing controls).
- Target size: 500-1500 samples after human review.

The node vocabulary is fixed to the application's allowed types
(`ui, service, database, cache, queue, container`) and edge labels
(`HTTP, DB Query, Async, Cache`), so every sample is directly consumable by
the existing React Flow renderer and the security engine's substring matcher.

## 3. Sample schema

```json
{
  "id": "banking-hard-hardened",
  "domain": "banking",
  "difficulty": "hard",
  "instruction": "<natural language or prompt-rendered task>",
  "architecture": { "nodes": [...], "edges": [...] },
  "security": {
    "required_controls": [...],
    "missing_controls": [...],
    "threats": [...],
    "recommendations": [...],
    "risk_level": "LOW|MEDIUM|HIGH",
    "security_score": 0
  },
  "metadata": { "source": "...", "generated_by": "...", "reviewed": false, "version": "1.0" }
}
```

The structural contract is machine-enforced by
`dataset/schemas/architecture_schema.json` (JSON Schema, draft-07). The
semantic contract (control names, threat names, node types, edge labels,
risk levels) is enforced by constants imported from the application's
security engine, so the dataset vocabulary *cannot* drift from the runtime
vocabulary.

## 4. Generation

Two complementary generators, both writing to `dataset/generated/`:

1. **Template generator** (`dataset_generator.py --mode template`): fully
   deterministic, GPU-free synthesis from per-domain knowledge templates
   (`dataset/templates/domain_*.json`). For each (domain, difficulty) it
   emits an insecure and a hardened variant. Security labels are computed by
   calling the production engine on the synthesized graph.
2. **Model generator** (`--mode model`): feeds the same domain templates'
   seed instructions to the local Gemma 3 generator, using the prompt
   library (`dataset/prompts/`) which guarantees deterministic JSON output
   (greedy decode, strict formatting instructions). Only graphs that pass
   the application's own `_validate_architecture` are retained.

Prompt templates cover four tasks: architecture generation,
security-aware generation, threat analysis, and secure-architecture
improvement.

## 5. Validation

Every candidate sample must pass the validation gate
(`dataset_validator.py`) before it may be reviewed:

- **Structural**: JSON Schema compliance.
- **Graph integrity**: unique node ids, edges referencing existing nodes,
  no self-loops, no duplicate edges, allowed types and labels.
- **Security consistency**: the stored `missing_controls`, `required_controls`,
  `security_score`, `risk_level`, and threat names must equal a fresh run of
  the production security engine on the same graph. Labels cannot be
  hand-edited into falsehood.
- **Batch-level**: no duplicate sample ids, no duplicate architectures.

Valid samples are copied into `dataset/validated/`; a machine-readable
report is written to `dataset/docs/validation_report.json`.

## 6. Human review

A CLI reviewer (`review_dataset.py`) presents each validated sample with its
graph, missing controls, threats, and recommendations, and offers
approve / reject / edit / skip. Approved samples are stamped
`metadata.reviewed: true` and moved to `dataset/reviewed/`. Every decision is
logged in `dataset/docs/review_log.json`, preserving provenance for the
paper's reproducibility statement.

## 7. From reviewed samples to training data

`export_jsonl.py` reads the reviewed corpus, deduplicates, and writes
training-ready JSONL records containing `instruction` (prompt-rendered task)
and `response` (compact architecture JSON), plus the full structured payload
and a deterministic 85/15 train/validation split. The fine-tuning harness
applies Gemma 3's chat template (single user turn) and masks the prompt
tokens in the loss.

## 8. Reproducibility and provenance

- Generation is deterministic (`--mode template`), and model mode uses
  greedy decoding.
- Every sample records `source`, `generated_by`, and `version`.
- Every pipeline stage writes an audit report (`validation_report.json`,
  `review_log.json`, `split_manifest.json`) into `dataset/docs/`.
- All schema, template, and prompt files are versioned in the repository.

## 9. Limitations

- Template samples are synthetic and may be structurally repetitive; the
  model generator and human editing are the diversity levers.
- Security labels reflect the engine's rule-based catalog, not a formal
  threat model; adversarial examples may require extending the catalog.
- The engine's substring matching rewards control-friendly node ids (e.g.
  `api gateway`); the dataset intentionally mirrors this behaviour so
  training distribution matches deployment distribution.

## 10. How the dataset supports Gemma 3 LoRA fine-tuning

The final JSONL feeds a LoRA adapter on `unsloth/gemma-3-4b-it-bnb-4bit`
(NF4, r=16). The instruction/response pairs teach the model to (a) emit
valid graph JSON in the app's vocabulary, (b) embed required security
controls as nodes, and (c) implicitly learn which controls each domain
needs — because the supervised signal is the engine-verified security label,
the loss directly optimises the quantity the app scores. See
`docs/training_plan.md` for hyperparameters, memory, and evaluation metrics.
