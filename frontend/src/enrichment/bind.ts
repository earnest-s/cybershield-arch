/**
 * Semantic Enrichment Layer — Deterministic Node Binding
 *
 * Places detected technologies onto v2 generated nodes. Rules:
 *
 * R1 model-metadata   node.metadata.technology resolves in the registry (dormant today).
 * R2 unique-cardinality  1:1 categories (databases→database, cache→cache,
 *                      messaging→queue, frontend→ui): exactly one detected tech of
 *                      the category AND exactly one compatible node → bind.
 *                      Counts only — never node order.
 * R3 candidate surfacing  every other case → candidates on compatible nodes.
 * R4 manual-pick      user assignment wins; displaced auto-bind is marked overridden.
 * R5 reset            handled by facade callers (drop manualAssignments).
 *
 * Hard invariants:
 *   - Never binds by emission order.
 *   - Never binds hedged mentions (suggestions stay visible but unclaimed).
 *   - Never uses connectivity/topology as evidence.
 *   - Non-1:1 categories are never auto-bound.
 *   - No fragment/node fabrication: only generated node ids are returned.
 */

import type { ArchitectureNode, NodeMetadata } from "../types";
import type { TechnologyCategory, TechnologyMetadata } from "../technology/types";
import { getTechnologyRegistry, TechnologyRegistry } from "../technology/registry";
import type {
  AssignmentConfidence,
  DetectedTechnology,
  EnrichedNode,
  EnrichmentConflict,
  TechnologyAssignment,
  TechnologyCandidate,
} from "./types";

/** Minimal manual assignment input from the UI. */
export interface ManualAssignmentInput {
  technologyId: string;
  technologyName: string;
}

/** Category → compatible v2 node types. */
const NODE_TYPES_BY_CATEGORY: Record<TechnologyCategory, string[]> = {
  databases: ["database"],
  cache: ["cache"],
  messaging: ["queue"],
  frontend: ["ui"],
  backend: ["service"],
  "api-gateway": ["service"],
  "load-balancing": ["service"],
  "auth-identity": ["service"],
  security: ["service"],
  observability: ["service"],
  storage: ["database"],
  cloud: ["service", "container"],
  aws: ["service", "container"],
  azure: ["service", "container"],
  gcp: ["service", "container"],
  kubernetes: ["service", "container"],
  containers: ["service", "container"],
  networking: ["service"],
  "devops-cicd": ["service"],
  generic: [],
};

/** Categories eligible for R2 unique-cardinality auto-binding. */
const AUTO_BIND_CATEGORIES = new Set<TechnologyCategory>([
  "databases",
  "cache",
  "messaging",
  "frontend",
]);

function resolveTech(reg: TechnologyRegistry, idOrLabel: string): TechnologyMetadata | undefined {
  return reg.get(idOrLabel) || reg.getByLabel(idOrLabel) || reg.getByAlias(idOrLabel);
}

function genericLabel(nodeId: string, nodeType: string, metadata?: NodeMetadata): string {
  if (metadata?.label && metadata.label.trim()) return metadata.label.trim();
  const match = nodeId.match(/^([a-z]+)-(\d+)$/i);
  if (match) {
    const typePart = match[1].toLowerCase();
    const numPart = match[2];
    const canonicalType = typePart === "ui" ? "UI" : typePart.charAt(0).toUpperCase() + typePart.slice(1);
    return `${canonicalType} ${numPart}`;
  }
  const fallbackType = nodeType.charAt(0).toUpperCase() + nodeType.slice(1);
  return fallbackType;
}

export interface BindingResult {
  enrichedNodes: EnrichedNode[];
  /** Detected technologies that were not bound (candidates-only or no compatible node). */
  unplaced: DetectedTechnology[];
  conflicts: EnrichmentConflict[];
  /** Node ids whose auto-bind was displaced by a manual pick. */
  overriddenNodeIds: string[];
}

/**
 * Bind detected technologies to generated nodes.
 */
export function bindTechnologies(
  detected: DetectedTechnology[],
  nodes: ArchitectureNode[],
  manualAssignments: Record<string, ManualAssignmentInput>,
  registry?: TechnologyRegistry
): BindingResult {
  const reg = registry ?? getTechnologyRegistry();

  const conflicts: EnrichmentConflict[] = [];
  const tentative = new Map<string, TechnologyAssignment>();
  const boundTechIds = new Set<string>();

  // ── R2: unique-cardinality auto-bind for 1:1 categories ───────────────────
  for (const category of AUTO_BIND_CATEGORIES) {
    const candidates = detected.filter(
      (d) => d.category === category && !d.hedged && d.confidence !== "possible"
    );
    if (candidates.length > 1) {
      // Multiple identified technologies of the same category compete.
      const compatibleNodes = nodes.some((node) => NODE_TYPES_BY_CATEGORY[category].includes(node.type));
      if (compatibleNodes) {
        conflicts.push({
          span: candidates[0].positions[0],
          technologyIds: candidates.map((c) => c.technologyId),
          reason: "coequal-category",
        });
      }
      continue;
    }
    if (candidates.length !== 1) continue;

    const tech = candidates[0];
    const compatible = nodes.filter(
      (node) => NODE_TYPES_BY_CATEGORY[category].includes(node.type) && !tentative.has(node.id)
    );
    if (compatible.length === 1) {
      const node = compatible[0];
      tentative.set(node.id, {
        nodeId: node.id,
        technologyId: tech.technologyId,
        technologyName: tech.technologyName,
        source: tech.source,
        confidence: "confirmed",
        basis: "unique-cardinality",
        detectedId: tech.technologyId,
        evidenceText: tech.mentions[0] ?? tech.technologyName,
      });
      boundTechIds.add(tech.technologyId);
    }
  }

  // ── R1: model-provided metadata (dormant with v2, codified for the future) ─
  for (const node of nodes) {
    if (tentative.has(node.id)) continue;
    const technology = node.metadata?.technology;
    if (!technology) continue;
    const tech = resolveTech(reg, technology);
    if (!tech) continue;
    tentative.set(node.id, {
      nodeId: node.id,
      technologyId: tech.id,
      technologyName: tech.name,
      source: "model-provided",
      confidence: "confirmed",
      basis: "model-metadata",
      evidenceText: technology,
    });
    boundTechIds.add(tech.id);
  }

  // ── R4: manual assignments override tentative auto-binds ──────────────────
  const overriddenNodeIds: string[] = [];
  const final = new Map<string, TechnologyAssignment>();
  const manualNodeIds = new Set(Object.keys(manualAssignments));

  for (const node of nodes) {
    if (manualNodeIds.has(node.id)) {
      const manual = manualAssignments[node.id];
      if (tentative.has(node.id)) overriddenNodeIds.push(node.id);
      final.set(node.id, {
        nodeId: node.id,
        technologyId: manual.technologyId,
        technologyName: manual.technologyName,
        source: "manual-user",
        confidence: "confirmed",
        basis: "manual-pick",
        evidenceText: "Manual assignment",
      });
      continue;
    }
    const auto = tentative.get(node.id);
    if (auto) final.set(node.id, auto);
  }

  // ── R3: candidates for nodes without assignments ──────────────────────────
  const candidatesByNode = new Map<string, TechnologyCandidate[]>();
  const candidatePool = detected.filter((d) => !boundTechIds.has(d.technologyId));

  for (const node of nodes) {
    if (final.has(node.id)) continue;
    const compatible = candidatePool.filter((d) =>
      NODE_TYPES_BY_CATEGORY[d.category].includes(node.type)
    );
    const distinctIds = Array.from(new Set(compatible.map((c) => c.technologyId)));
    const confidence: AssignmentConfidence = distinctIds.length > 1 ? "ambiguous" : "possible";
    candidatesByNode.set(
      node.id,
      compatible.map((tech) => ({
        technology: tech,
        confidence,
        basis: "manual-pick",
      }))
    );
  }

  // ── Assemble EnrichedNodes ─────────────────────────────────────────────────
  const enrichedNodes: EnrichedNode[] = nodes.map((node) => {
    const assignment = final.get(node.id) ?? null;
    const candidates = candidatesByNode.get(node.id) ?? [];
    return {
      nodeId: node.id,
      nodeType: node.type,
      raw: node,
      label: assignment ? assignment.technologyName : genericLabel(node.id, node.type, node.metadata),
      assignment,
      candidates,
      overriddenByManual: overriddenNodeIds.includes(node.id),
    };
  });

  const unplaced = detected
    .filter((d) => !boundTechIds.has(d.technologyId))
    .sort((a, b) => (a.positions[0]?.start ?? 0) - (b.positions[0]?.start ?? 0));

  return { enrichedNodes, unplaced, conflicts, overriddenNodeIds };
}

/** Resolve a technology reference (id, label, or alias) for the Assign UI. */
export function resolveTechnologyReference(reference: string): TechnologyMetadata | undefined {
  return resolveTech(getTechnologyRegistry(), reference);
}