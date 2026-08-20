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
