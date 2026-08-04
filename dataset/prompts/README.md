# Prompts

Reusable prompt templates for the local Gemma 3 model. Each template is
rendered by `backend/dataset/dataset_generator.py` with `{{placeholder}}`
substitution and produces **deterministic JSON** output.

## Templates

| File | Task | Output |
| --- | --- | --- |
| `architecture_generation.json` | Convert a description into a graph | `{nodes, edges}` |
| `security_aware_generation.json` | Generate a graph with embedded security controls | `{nodes, edges}` (controls as nodes) |
| `threat_analysis.json` | Analyze an architecture's security posture | `{missing_controls, threats, recommendations, risk_level, security_score}` |
| `secure_improvement.json` | Harden a vulnerable architecture | `{architecture, applied_controls}` |

## File format

```json
{
  "name": "architecture-generation",
  "task": "architecture_generation",
  "purpose": "...",
  "defaults": { "temperature": 0.3, "top_p": 0.9, "max_new_tokens": 512, "deterministic": true },
  "placeholders": ["instruction", ...],
  "template": "... {{placeholder}} ..."
}
```

`defaults` mirror the generation settings used by
`backend/core/inference.py` (`temperature 0.3, top_p 0.9, max_new_tokens 512`,
greedy when `deterministic`). Every template closes with
`ONLY return JSON. No explanation.` so the model emits parseable output.