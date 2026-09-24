/**
 * Semantic Enrichment Layer — Facade
 *
 * Pure frontend entry point: requirement text + v2 topology → presentation
 * model. The /explain contract is never mutated; everything returned is
 * derived state layered over the frozen response.
 */

import type { Architecture } from "../types";
import type { EnrichmentConflict, SemanticEnrichmentResult } from "./types";
import { detectTechnologies } from "./extract";
import { bindTechnologies, type ManualAssignmentInput } from "./bind";

export interface EnrichOptions {
  manualAssignments?: Record<string, ManualAssignmentInput>;
}

/**
 * Compute the semantic enrichment for a generated architecture.
 *
 * Deterministic for given `(requirement, architecture, manualAssignments)`.
 */
export function enrichArchitecture(
  requirement: string,
  architecture: Architecture,
  manualAssignments: Record<string, ManualAssignmentInput> = {}
): SemanticEnrichmentResult {
  const { detected, conflicts: detectConflicts } = detectTechnologies(requirement);
  const { enrichedNodes, unplaced, conflicts: bindConflicts, overriddenNodeIds } = bindTechnologies(
    detected,
    architecture.nodes ?? [],
    manualAssignments
  );

  const merged: EnrichmentConflict[] = [];
  const seen = new Set<string>();
  for (const conflict of [...detectConflicts, ...bindConflicts]) {
    const key = `${conflict.span?.start ?? -1}:${conflict.span?.end ?? -1}:${conflict.reason}:${[...conflict.technologyIds].sort().join(",")}`;
    if (seen.has(key)) continue;
    seen.add(key);
    merged.push(conflict);
  }

  return {
    requirement,
    detected,
    enrichedNodes,
    unplaced,
    genericNodeIds: enrichedNodes.filter((node) => node.assignment === null).map((node) => node.nodeId),
    conflicts: merged,
    builtAt: Date.now(),
  };
}