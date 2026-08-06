"""Canonical security enrichment layer.

Wraps the production security engine (backend/security/*) behind one function
so the runtime /explain endpoint, the dataset pipeline, and the response
builder all compute identical security data. Replaces the duplicated assembly
that previously lived in:
- backend/api/main.py (manual security_result dict)
- dataset/scripts/enrich_dataset.py (_controls_present + security dict)
- backend/dataset/security.py (CONTROL_SUBSTRINGS + SecuritySection builder)
"""

from __future__ import annotations

from typing import Any

from backend.core.architecture_models import (
    AttackSurface,
    NodeThreat,
    SecurityData,
    ThreatInfo,
)
from backend.security.security_catalog import SECURITY_CATALOG
from backend.security.security_analyzer import analyze_architecture_security
from backend.security.threat_detector import calculate_attack_surface, detect_threats

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


def detect_present_controls(nodes: list[dict[str, Any]]) -> set[str]:
    """Detect which catalog controls are present in the architecture text."""
    present: set[str] = set()
    for node in nodes:
        try:
            node_text = " ".join(str(value).lower() for value in node.values())
        except (TypeError, AttributeError):
            node_text = str(node).lower()
        for control, needle in CONTROL_SUBSTRINGS.items():
            if needle in node_text:
                present.add(control)
        for control in SECURITY_CATALOG:
            if control.lower() in node_text:
                present.add(control)
    return present


def build_security_data(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> SecurityData:
    """Run the full security engine and return the canonical SecurityData."""
    analysis = analyze_architecture_security(nodes, edges)
    threats_result = detect_threats(nodes, edges)
    attack_surface = calculate_attack_surface(nodes, edges)

    missing_controls = sorted(component["name"] for component in analysis.get("missing_components", []))
    present_controls = detect_present_controls(nodes)
    required_controls = sorted(present_controls | set(missing_controls))

    threats = [
        ThreatInfo(
            name=str(threat.get("name", "")),
            severity=str(threat.get("severity", "")),
            description=str(threat.get("description", "")),
            missing_control=str(threat.get("missing_control", "")) or None,
        )
        for threat in threats_result.get("threats", [])
    ]

    node_threats = {
        node_id: [NodeThreat(**entry) for entry in entries]
        for node_id, entries in threats_result.get("node_threats", {}).items()
    }
    edge_threats = {
        edge_id: [NodeThreat(**entry) for entry in entries]
        for edge_id, entries in threats_result.get("edge_threats", {}).items()
    }

    return SecurityData(
        security_score=int(analysis.get("security_score", 0)),
        risk_level=str(analysis.get("risk_level", "HIGH")),
        missing_components=analysis.get("missing_components", []),
        recommendations=list(analysis.get("recommendations", [])),
        threats=threats,
        node_threats=node_threats,
        edge_threats=edge_threats,
        attack_surface=AttackSurface(
            attack_surface_score=int(attack_surface.get("attack_surface_score", 0)),
            public_endpoints=int(attack_surface.get("public_endpoints", 0)),
            databases=int(attack_surface.get("databases", 0)),
            services=int(attack_surface.get("services", 0)),
        ),
        security_summary=str(analysis.get("security_summary", "")),
        required_controls=required_controls,
        missing_controls=missing_controls,
    )


def enrich_architecture(architecture: dict[str, Any]) -> SecurityData:
    """Enrich a canonical {nodes, edges} dict with security analysis."""
    return build_security_data(architecture.get("nodes", []), architecture.get("edges", []))


def security_data_to_dict(security: SecurityData) -> dict[str, Any]:
    """Serialization helper producing the legacy wire-compatible security dict."""
    return security.model_dump(mode="json")
