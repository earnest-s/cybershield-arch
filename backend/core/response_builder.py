"""Canonical response builder.

Single assembly point producing the canonical ``ArchitectureResponse`` from a
parsed architecture plus optional security data. Replaces the manual response
assembly previously in backend/api/main.py (/explain handler) and gives the
dataset pipeline the same shape for its security section.

Wire compatibility: the /explain payload served by the API keeps the top-level
``architecture`` / ``raw_model_output`` / ``security`` keys the frontend
reads (frontend/src/types.ts), and additionally exposes ``metadata`` and
``validation``.
"""

from __future__ import annotations

from typing import Any

from backend.core.architecture_enricher import build_security_data
from backend.core.architecture_models import (
    ArchitectureGraph,
    ArchitectureMetadata,
    ArchitectureResponse,
    ArchitectureBoundary,
    ExplainResponse,
    SecurityData,
    ValidationResult,
)
from backend.core.architecture_schema import (
    EDGE_DASHED_LABELS,
    NODE_TYPE_LAYERS,
    derive_node_icon,
)
from backend.core.architecture_validator import validate_architecture


def _apply_visual_metadata(architecture: dict[str, Any]) -> dict[str, Any]:
    """Attach canonical presentation metadata (icon/layer/dashed).

    The renderer consumes these fields instead of re-inferring node kinds or
    edge styling; the same tables in architecture_schema.py are the single
    source of truth.
    """
    nodes: list[dict[str, Any]] = []
    for node in architecture.get("nodes", []):
        node_type = str(node.get("type", "service"))
        annotated = dict(node)
        annotated["icon"] = derive_node_icon(str(node.get("id", "")))
        annotated["layer"] = NODE_TYPE_LAYERS.get(node_type, "service")
        nodes.append(annotated)

    edges: list[dict[str, Any]] = []
    for edge in architecture.get("edges", []):
        edge = dict(edge)
        edge["dashed"] = edge.get("label") in EDGE_DASHED_LABELS
        edges.append(edge)

    return {**architecture, "nodes": nodes, "edges": edges}


def infer_boundaries(architecture: dict[str, Any]) -> list[ArchitectureBoundary]:
    """Infer logical boundaries from the architecture topology.

    Creates C4-style containers based on node types and connectivity patterns.
    This is a best-effort heuristic for visualization purposes only.
    """
    nodes = architecture.get("nodes", [])
    edges = architecture.get("edges", [])

    boundaries: list[ArchitectureBoundary] = []
    node_types = {n["id"]: n["type"] for n in nodes}

    # Group nodes by type for boundary creation
    ui_nodes = [n["id"] for n in nodes if n["type"] == "ui"]
    service_nodes = [n["id"] for n in nodes if n["type"] == "service"]
    data_nodes = [n["id"] for n in nodes if n["type"] in ("database", "cache", "queue")]

    # Internet boundary (always present for context)
    boundaries.append(ArchitectureBoundary(
        id="boundary-internet",
        name="Internet",
        type="system",
        nodes=[],
        style={"color": "#64748b", "dashed": True, "labelPosition": "top-left"},
    ))

    # Public Zone: UI nodes + internet-facing services
    public_nodes = ui_nodes[:]
    # Find services directly connected to UI
    for edge in edges:
        if edge["source"] in ui_nodes and edge["target"] in service_nodes:
            if edge["target"] not in public_nodes:
                public_nodes.append(edge["target"])
        elif edge["target"] in ui_nodes and edge["source"] in service_nodes:
            if edge["source"] not in public_nodes:
                public_nodes.append(edge["source"])

    if public_nodes:
        boundaries.append(ArchitectureBoundary(
            id="boundary-public",
            name="Public Zone",
            type="deployment-zone",
            nodes=public_nodes,
            style={"color": "#3b82f6", "dashed": False, "labelPosition": "top-left"},
        ))

    # Application Zone: All services
    if service_nodes:
        boundaries.append(ArchitectureBoundary(
            id="boundary-application",
            name="Application Zone",
            type="container",
            nodes=service_nodes,
            boundaries=["boundary-public"] if public_nodes else [],
            style={"color": "#8b5cf6", "dashed": False, "labelPosition": "top-left"},
        ))

    # Data Zone: Databases, caches, queues
    if data_nodes:
        boundaries.append(ArchitectureBoundary(
            id="boundary-data",
            name="Data Zone",
            type="deployment-zone",
            nodes=data_nodes,
            style={"color": "#10b981", "dashed": False, "labelPosition": "top-left"},
        ))

    return boundaries


def build_response(
    architecture: dict[str, Any],
    *,
    raw_model_output: str | None = None,
    duration_ms: int | None = None,
    provider: str = "gemma",
    source: str = "runtime",
    run_security: bool = True,
) -> ArchitectureResponse:
    """Build the canonical response: parse -> validate -> enrich -> assemble."""
    architecture = _apply_visual_metadata(architecture)

    # Infer boundaries before validation
    boundaries = infer_boundaries(architecture)
    if boundaries:
        architecture = {**architecture, "boundaries": [b.model_dump(mode="json") for b in boundaries]}

    graph = ArchitectureGraph.model_validate(architecture)
    validation = validate_architecture(architecture)

    security: SecurityData | None = None
    if run_security and graph.nodes:
        security = build_security_data(
            [node.model_dump(mode="json") for node in graph.nodes],
            [edge.model_dump(mode="json") for edge in graph.edges],
        )

    return ArchitectureResponse(
        architecture=graph,
        security=security,
        metadata=ArchitectureMetadata(
            source=source,
            provider=provider,
            duration_ms=duration_ms,
            raw_output=raw_model_output,
        ),
        validation=validation,
    )


def response_to_explain_payload(response: ArchitectureResponse) -> ExplainResponse:
    """Wire-compatible payload for the /explain endpoint."""
    return ExplainResponse(
        **response.model_dump(mode="json"),
        raw_model_output=response.metadata.raw_output,
    )


def build_security_dict(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> dict[str, Any]:
    """Standalone security dict used by the dataset pipeline scripts."""
    return build_security_data(nodes, edges).model_dump(mode="json")


def validation_to_dict(validation: ValidationResult) -> dict[str, Any]:
    """Serialization helper for validation results."""
    return validation.model_dump(mode="json")