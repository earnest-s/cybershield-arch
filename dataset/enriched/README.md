# Enriched

Samples from parsed/ enriched with a full security analysis computed by the production security engine (backend/security/*). Each file adds a 'security' block with required_controls, missing_controls, threats, recommendations, risk_level, security_score, attack_surface, and security_summary. Enrichment is resumable: existing ids are skipped unless --force is passed.
