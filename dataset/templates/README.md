# Templates

Domain knowledge templates consumed by `backend/dataset/dataset_generator.py`.
One file per domain, named `domain_<domain>.json`.

## Domains

banking, healthcare, cybersecurity, cloud, iot, e-commerce, education,
smart-city, logistics, microservices, devops, ai-platform

## File format

```json
{
  "domain": "banking",
  "version": "1.0",
  "description": "...",
  "typical_components": [ {"id": "...", "type": "ui|service|database|..."} ],
  "services": ["..."],
  "databases": ["..."],
  "apis": ["..."],
  "expected_security_controls": ["MFA", "..."],
  "common_attack_vectors": ["Credential Stuffing", "..."],
  "seed_instructions": ["...", "..."],
  "difficulty_map": {"easy": 4, "medium": 6, "hard": 8}
}
```

## Alignment rules

- Component `type` values come from the app's allowed set:
  `ui, service, database, cache, queue, container` (`backend/core/inference.py`).
- `expected_security_controls` use the exact catalog names from
  `backend/security/security_catalog.py` - the security engine matches
  control names as substrings in node ids/types, so names must be exact.
- `common_attack_vectors` are drawn from `THREAT_KNOWLEDGE_BASE` in
  `backend/security/threat_detector.py` so threat names validate against the
  app's threat engine.
- `difficulty_map` controls how many components a generated sample has:
  easy 4, medium 6, hard 8.