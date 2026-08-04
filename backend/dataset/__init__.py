"""Dataset pipeline package for CyberShield-Arch.

This package is the data-engineering layer that produces the fine-tuning
dataset. It does NOT load the model, run training, or import GPU-heavy modules
beyond the lightweight security engine.

Stage modules (invoke as ``python -m backend.dataset.<module>``):

- dataset_generator  : candidate generation into dataset/generated/
- dataset_validator  : schema + semantic gate into dataset/validated/
- review_dataset     : human approval gate into dataset/reviewed/
- export_jsonl       : reviewed -> training-ready JSONL in dataset/final/
"""

from __future__ import annotations

__version__ = "1.0"