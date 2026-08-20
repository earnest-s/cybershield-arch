"""Canonical Pydantic models for the architecture contract.

These models mirror the frozen frontend contract (frontend/src/types.ts) and
the wire shape served by /explain. ``ArchitectureResponse`` is the single
canonical object produced by ``response_builder.build_response`` and consumed
by the API, the runtime pipeline, and (in a data-oriented subset) the dataset
pipeline.

Keep these models field-compatible with frontend/src/types.ts; do not rename
or remove keys the frontend reads without re-approval.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ArchitectureNode(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    type: str
    icon: str | None = None
    layer: str | None = None


class ArchitectureEdge(BaseModel):
    model_config = ConfigDict(extra="ignore")

    source: str
    target: str
    label: str = "HTTP"
    dashed: bool | None = None


class ArchitectureGraph(BaseModel):
    model_config = ConfigDict(extra="ignore")

    nodes: list[ArchitectureNode] = Field(default_factory=list)
    edges: list[ArchitectureEdge] = Field(default_factory=list)

    def to_core_dict(self) -> dict[str, list[dict]]:
        return {
            "nodes": [n.model_dump(mode="json") for n in self.nodes],
            "edges": [e.model_dump(mode="json") for e in self.edges],
        }


class ThreatInfo(BaseModel):
    """Matches frontend `ThreatInfo`."""

    model_config = ConfigDict(extra="ignore")

    name: str
    severity: str
    description: str = ""
    missing_control: str | None = None
    severity_level: str = ""


class NodeThreat(BaseModel):
    """Matches frontend `NodeThreat`."""

    model_config = ConfigDict(extra="ignore")

    threat: str
    severity: str
    missing_control: str
    severity_level: str = ""


class AttackSurface(BaseModel):
    """Matches frontend `AttackSurface`."""

    model_config = ConfigDict(extra="ignore")

    attack_surface_score: int = 0
    public_endpoints: int = 0
    databases: int = 0
    services: int = 0


class SecurityData(BaseModel):
    """Superset of the frontend `SecurityData` (adds dataset-style controls)."""

    model_config = ConfigDict(extra="ignore")

    security_score: int = 0
    risk_level: str = "HIGH"
    missing_components: list[dict] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    threats: list[ThreatInfo] = Field(default_factory=list)
    node_threats: dict[str, list[NodeThreat]] = Field(default_factory=dict)
    edge_threats: dict[str, list[NodeThreat]] = Field(default_factory=dict)
    attack_surface: AttackSurface = Field(default_factory=AttackSurface)
    security_summary: str = ""
    required_controls: list[str] = Field(default_factory=list)
    missing_controls: list[str] = Field(default_factory=list)


class ValidationIssue(BaseModel):
    model_config = ConfigDict(extra="ignore")

    rule: str
    severity: str = "error"  # error | warning
    message: str


class ValidationResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    valid: bool = True
    issues: list[ValidationIssue] = Field(default_factory=list)
    structurally_weak: bool = False


class ArchitectureMetadata(BaseModel):
    model_config = ConfigDict(extra="ignore")

    source: str = "runtime"
    version: str = "1.0"
    provider: str = ""
    duration_ms: int | None = None
    raw_output: str | None = None


class ArchitectureResponse(BaseModel):
    """Canonical response object for a generated/parsed architecture."""

    model_config = ConfigDict(extra="ignore")

    architecture: ArchitectureGraph = Field(default_factory=ArchitectureGraph)
    security: SecurityData | None = None
    metadata: ArchitectureMetadata = Field(default_factory=ArchitectureMetadata)
    validation: ValidationResult = Field(default_factory=ValidationResult)


class ExplainResponse(ArchitectureResponse):
    """Wire contract served by /explain.

    Adds the top-level ``raw_model_output`` the frontend reads; every other
    field is inherited from the canonical ``ArchitectureResponse``.
    """

    raw_model_output: str | None = None


class HealthResponse(BaseModel):
    """Canonical health probe; no free-form dicts from endpoints."""

    model_config = ConfigDict(extra="ignore")

    status: str = "ok"