"""Typed data models for the CyberShield-Arch dataset.

These dataclasses mirror the JSON shape defined in
``dataset/schemas/architecture_schema.json`` and the runtime contract used by
the app (frontend/src/types.ts and the /explain response).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Node:
    id: str
    type: str

    def to_dict(self) -> dict[str, str]:
        return {"id": self.id, "type": self.type}


@dataclass(slots=True)
class Edge:
    source: str
    target: str
    label: str

    def to_dict(self) -> dict[str, str]:
        return {"source": self.source, "target": self.target, "label": self.label}


@dataclass(slots=True)
class Threat:
    name: str
    severity: str
    description: str
    missing_control: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "severity": self.severity,
            "description": self.description,
        }
        if self.missing_control:
            payload["missing_control"] = self.missing_control
        return payload


@dataclass(slots=True)
class SecuritySection:
    required_controls: list[str] = field(default_factory=list)
    missing_controls: list[str] = field(default_factory=list)
    threats: list[Threat] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    risk_level: str = "HIGH"
    security_score: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "required_controls": sorted(self.required_controls),
            "missing_controls": sorted(self.missing_controls),
            "threats": [t.to_dict() for t in self.threats],
            "recommendations": list(self.recommendations),
            "risk_level": self.risk_level,
            "security_score": int(self.security_score),
        }


@dataclass(slots=True)
class Metadata:
    source: str = "synthetic"
    generated_by: str = "template-v1"
    reviewed: bool = False
    version: str = "1.0"

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "generated_by": self.generated_by,
            "reviewed": self.reviewed,
            "version": self.version,
        }


@dataclass(slots=True)
class Architecture:
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
        }


@dataclass(slots=True)
class Sample:
    id: str
    domain: str
    difficulty: str
    instruction: str
    architecture: Architecture = field(default_factory=Architecture)
    security: SecuritySection = field(default_factory=SecuritySection)
    metadata: Metadata = field(default_factory=Metadata)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "domain": self.domain,
            "difficulty": self.difficulty,
            "instruction": self.instruction,
            "architecture": self.architecture.to_dict(),
            "security": self.security.to_dict(),
            "metadata": self.metadata.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Sample":
        if not isinstance(data, dict):
            raise ValueError("sample must be a JSON object")

        architecture = data.get("architecture", {})
        security = data.get("security", {})
        metadata = data.get("metadata", {})

        return cls(
            id=str(data.get("id", "")),
            domain=str(data.get("domain", "")),
            difficulty=str(data.get("difficulty", "")),
            instruction=str(data.get("instruction", "")),
            architecture=Architecture(
                nodes=[
                    Node(id=str(node.get("id", "")), type=str(node.get("type", "")))
                    for node in architecture.get("nodes", [])
                    if isinstance(node, dict)
                ],
                edges=[
                    Edge(
                        source=str(edge.get("source", "")),
                        target=str(edge.get("target", "")),
                        label=str(edge.get("label", "")),
                    )
                    for edge in architecture.get("edges", [])
                    if isinstance(edge, dict)
                ],
            ),
            security=SecuritySection(
                required_controls=[str(c) for c in security.get("required_controls", [])],
                missing_controls=[str(c) for c in security.get("missing_controls", [])],
                threats=[
                    Threat(
                        name=str(t.get("name", "")),
                        severity=str(t.get("severity", "")),
                        description=str(t.get("description", "")),
                        missing_control=(t.get("missing_control") if isinstance(t, dict) else None),
                    )
                    for t in security.get("threats", [])
                    if isinstance(t, dict)
                ],
                recommendations=[str(r) for r in security.get("recommendations", [])],
                risk_level=str(security.get("risk_level", "")),
                security_score=int(security.get("security_score", 0)),
            ),
            metadata=Metadata(
                source=str(metadata.get("source", "synthetic")),
                generated_by=str(metadata.get("generated_by", "unknown")),
                reviewed=bool(metadata.get("reviewed", False)),
                version=str(metadata.get("version", "1.0")),
            ),
        )