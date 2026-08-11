# Parsed Architectures

Structured architecture graphs converted from Mermaid diagrams.

Each file is the output of `dataset/scripts/convert_dataset.py` (which uses
`dataset/scripts/mermaid_parser.py`):

```json
{
  "id": "CSA-000001",
  "instruction": "Design ...",
  "architecture": {
    "nodes": [{"id": "WebUI", "type": "ui"}, ...],
    "edges": [{"source": "WebUI", "target": "APIGW", "label": "HTTP"}, ...]
  },
  "metadata": {
    "domain": "MLOps",
    "style": "Event-Driven",
    "cloud": "On-Premises",
    "complexity": "Enterprise",
    "constraints": [...],
    "diagram_type": "flowchart LR",
    "source_nodes": 67,
    "source_edges": 50,
    "source": "Technical-Architectures-Large",
    "version": "1.0"
  }
}
```

The `nodes`/`edges` shapes follow the application contract exactly
(`backend/core/inference.py`): node types are limited to
`ui, service, database, cache, queue, container` and edge labels to
`HTTP, DB Query, Async, Cache`.

Files are named `CSA-######.json` in raw source order. Conversion is
resumable: existing ids are skipped unless `--force` is passed.