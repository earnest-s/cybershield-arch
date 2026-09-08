/**
 * C4 Boundary Foundation
 *
 * Prepares the frontend architecture model for spatial C4 boundaries
 * (System, Container, Component, Infrastructure, External System).
 *
 * Important: this module is a *vocabulary and preparation* layer only.
 * It does NOT generate boundaries, does NOT invent them, and does not alter
 * the existing graph layout. Boundaries are only represented when the backend
 * supplies them via the existing ArchitectureBoundary contract.
 *
 * The existing ArchitectureBoundary.type already accommodates system/container
 * levels, and its `boundaries` field already permits nesting. This module adds
 * the C4 level vocabulary and deterministic classification helpers so future
 * spatial layouts can consume it.
 */

import type { ArchitectureBoundary } from "../types";
import type { C4Classification } from "./types";

export type C4Level = "system" | "container" | "component" | "infrastructure" | "external-system";

/** Boundary type strings the backend may emit → C4 level classification */
const BOUNDARY_TO_C4: Record<string, C4Level> = {
  system: "system",
  container: "container",
  "deployment-zone": "infrastructure",
  "trust-boundary": "infrastructure",
  "cloud-account": "infrastructure",
  "k8s-namespace": "infrastructure",
  vpc: "infrastructure",
  subnet: "infrastructure",
  custom: "infrastructure",
};

/**
 * Classify an existing boundary's backend type into a C4 level.
 * Deterministic — never invents a classification for an unknown type.
 */
export function classifyBoundary(type: string): C4Level {
  return BOUNDARY_TO_C4[type] ?? "infrastructure";
}

/**
 * Mapping of C4 level → display metadata.
 */
export const C4_LEVEL_INFO: Record<C4Level, { label: string; description: string; color: string }> = {
  system: { label: "System", description: "Highest-level deployment / software system", color: "#3b82f6" },
  container: { label: "Container", description: "Deployable/executable unit", color: "#10b981" },
  component: { label: "Component", description: "Internal structural element", color: "#f59e0b" },
  infrastructure: { label: "Infrastructure", description: "Deployment/infrastructure boundary", color: "#8b5cf6" },
  "external-system": { label: "External System", description: "External/third-party system", color: "#64748b" },
};

/**
 * Compute the nesting depth of a boundary in the boundary tree.
 * Root boundaries are depth 0.
 */
export function boundaryDepth(boundary: ArchitectureBoundary, allBoundaries: ArchitectureBoundary[]): number {
  let depth = 0;
  let current: ArchitectureBoundary | undefined = boundary;
  const visited = new Set<string>();

  while (current) {
    if (visited.has(current.id)) break; // guard against cycles
    visited.add(current.id);
    const parent = allBoundaries.find((b) => b.boundaries?.includes(current!.id));
    if (parent) {
      depth += 1;
      current = parent;
    } else {
      current = undefined;
    }
  }
  return depth;
}

/**
 * Collect the C4 level for every boundary in a set, keyed by boundary id.
 */
export function classifyAllBoundaries(boundaries: ArchitectureBoundary[]): Map<string, C4Level> {
  const map = new Map<string, C4Level>();
  for (const b of boundaries) {
    map.set(b.id, classifyBoundary(b.type));
  }
  return map;
}

/**
 * Resolve a C4 level for a node based on its metadata boundary, if any.
 * Returns undefined when no boundary metadata is present (do not invent).
 */
export function c4LevelForNode(node: { metadata?: { boundary?: string } }, boundaries: ArchitectureBoundary[]): C4Level | undefined {
  const boundaryRef = node.metadata?.boundary;
  if (!boundaryRef) return undefined;
  const boundary = boundaries.find((b) => b.id === boundaryRef);
  if (!boundary) return undefined;
  return classifyBoundary(boundary.type);
}
