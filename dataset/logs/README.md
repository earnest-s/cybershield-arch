# Logs

Runtime logs and audit trails written by the pipeline scripts (one `.log` per script, plus `review_decisions.jsonl`). Human-readable provenance for the paper's reproducibility statement.

Expected log files (created on first run of each script):
- `download_dataset.log`
- `inspect_dataset.log`
- `convert_dataset.log`
- `enrich_dataset.log`
- `validate_dataset.log`
- `review_dataset.log`
- `export_jsonl.log`
- `review_decisions.jsonl` — append-only audit trail of human review decisions

Temporary/test logs (e.g., `convert_test.log`, `validate_test.log`) are created during development and should be cleaned before production runs.