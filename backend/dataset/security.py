"""Ground-truth security computation for dataset samples.

Thin wrapper around the canonical security layer (backend/core/architecture_
enricher) so dataset labels are identical to what the production /explain
endpoint produces. Nothing here re-implements the engine.
"""

from __future__ import annotations

from typing import Any

from backend.core.architecture_enricher import build_security_data
from backend.dataset.models import SecuritySection, Threat
from backend.dataset.schema import CONTROLS


def compute_security_section(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> SecuritySection:
    """Compute the full security section for a sample using the app engine."""
    security = build_security_data(nodes, edges)

    return SecuritySection(
        required_controls=[c for c in sorted(CONTROLS) if c in security.required_controls],
        missing_controls=security.missing_controls,
        threats=[
            Threat(
                name=threat.name,
                severity=threat.severity,
                description=threat.description,
                missing_control=threat.missing_control,
            )
            for threat in security.threats
        ],
        recommendations=security.recommendations,
        risk_level=security.risk_level,
        security_score=security.security_score,
    )


def assert_security_consistency(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    sample_security: dict[str, Any],
) -> list[str]:
    """Compare a sample's stored security section against a fresh engine run.

    Returns a list of inconsistency messages; an empty list means the stored
    security labels are exactly what the production engine computes.
    """
    expected = compute_security_section(nodes, edges)
    issues: list[str] = []

    stored_missing = sorted(sample_security.get("missing_controls", []))
    stored_required = sorted(sample_security.get("required_controls", []))
    stored_score = int(sample_security.get("security_score", -1))
    stored_risk = str(sample_security.get("risk_level", ""))

    if stored_missing != sorted(expected.missing_controls):
        issues.append(
            f"missing_controls mismatch: stored={stored_missing} engine={sorted(expected.missing_controls)}"
        )
    if stored_required != sorted(expected.required_controls):
        issues.append(
            f"required_controls mismatch: stored={stored_required} engine={sorted(expected.required_controls)}"
        )
    if stored_score != expected.security_score:
        issues.append(f"security_score mismatch: stored={stored_score} engine={expected.security_score}")
    if stored_risk != expected.risk_level:
        issues.append(f"risk_level mismatch: stored={stored_risk} engine={expected.risk_level}")

    stored_threat_names = sorted(t.get("name", "") for t in sample_security.get("threats", []))
    expected_threat_names = sorted(t.name for t in expected.threats)
    if stored_threat_names != expected_threat_names:
        issues.append(
            f"threat names mismatch: stored={stored_threat_names} engine={expected_threat_names}"
        )

    return issues