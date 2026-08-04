"""Ground-truth security computation for dataset samples.

Runs the application's own security engine (backend/security) over an
architecture so that dataset labels are identical to what the production
/explain endpoint would produce. Nothing here modifies the engine.
"""

from __future__ import annotations

from typing import Any

from backend.dataset.models import SecuritySection, Threat
from backend.dataset.schema import CONTROLS
from backend.security.security_analyzer import analyze_architecture_security
from backend.security.threat_detector import detect_threats

CONTROL_SUBSTRINGS: dict[str, str] = {
    "Authentication": "authentication",
    "RBAC": "rbac",
    "API Gateway": "api gateway",
    "Audit Logging": "audit logging",
    "Monitoring": "monitoring",
    "Secrets Manager": "secrets manager",
    "SIEM": "siem",
    "WAF": "waf",
    "IDS": "ids",
    "IPS": "ips",
    "Encryption Service": "encryption service",
    "MFA": "mfa",
}


def _controls_present_in_architecture(nodes: list[dict[str, Any]]) -> set[str]:
    present: set[str] = set()
    for node in nodes:
        try:
            node_text = " ".join(str(value).lower() for value in node.values())
        except (TypeError, AttributeError):
            node_text = str(node).lower()
        for control, needle in CONTROL_SUBSTRINGS.items():
            if needle in node_text:
                present.add(control)
    return present


def compute_security_section(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> SecuritySection:
    """Compute the full security section for a sample using the app engine."""
    analysis = analyze_architecture_security(nodes, edges)
    threats_result = detect_threats(nodes, edges)

    missing_controls = sorted(c["name"] for c in analysis.get("missing_components", []))
    present_controls = _controls_present_in_architecture(nodes)
    required_controls = sorted(present_controls | set(missing_controls))

    threats = [
        Threat(
            name=str(threat.get("name", "")),
            severity=str(threat.get("severity", "")),
            description=str(threat.get("description", "")),
            missing_control=str(threat.get("missing_control", "")) or None,
        )
        for threat in threats_result.get("threats", [])
    ]

    return SecuritySection(
        required_controls=[c for c in sorted(CONTROLS) if c in required_controls],
        missing_controls=missing_controls,
        threats=threats,
        recommendations=list(analysis.get("recommendations", [])),
        risk_level=str(analysis.get("risk_level", "HIGH")),
        security_score=int(analysis.get("security_score", 0)),
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