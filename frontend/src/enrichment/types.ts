/**
 * Semantic Enrichment Layer — Data Model
 *
 * Frontend-only presentation model layered over the frozen /explain contract.
 * These types never flow back into the backend response; `ArchitectureNode`
 * objects are preserved verbatim inside `EnrichedNode.raw`.
 */

import type { ArchitectureNode, NodeMetadata } from "../types";
import type { C4Classification, TechnologyCategory, TechnologyMetadata } from "../technology/types";

/** Provenance of a technology mention or assignment. One enum, two contexts. */
export type AssignmentSource =
  | "explicit-user"        // verbatim canonical registry label in the requirement ("PostgreSQL")
  | "deterministic-match"  // alias / compound / role-qualified phrase ("postgres", "aws s3", "React frontend")
  | "model-provided"       // technology emitted in backend node.metadata.technology (dormant today)
  | "manual-user"          // user picked a technology in the Assign Technology UI
  | "inferred";            // structural heuristic — allowed to surface CANDIDATES only,
                           // never allowed to auto-bind (confidence capped at "possible")

export type AssignmentConfidence =
  | "confirmed"   // deterministic, high evidence
  | "possible"    // plausible candidate; shown grouped, NOT rendered on canvas as fact
  | "ambiguous"   // conflicting / insufficient evidence; no automatic placement
  | "unknown";    // no evidence (generic node, role-language without a brand)

/** Character range in the requirement text. */
export interface TextPosition {
  start: number;
  end: number;
}

/**
 * A technology recognized in the requirement text (detection stage).
 * `mentions`/`positions` hold every occurrence.
 */
export interface DetectedTechnology {
  technologyId: string;            // registry id, e.g. "postgresql"
  technologyName: string;          // registry display name, e.g. "PostgreSQL"
  source: AssignmentSource;        // "explicit-user" | "deterministic-match"
  confidence: AssignmentConfidence;
  /** Hedged/suggestion language ("compatible with", "such as", "like", ...). */
  hedged: boolean;
  mentions: string[];              // raw snippets as written ("postgres", "PostgreSQL")
  positions: TextPosition[];       // char ranges, used for <mark> hover + diagnostics
  category: TechnologyCategory;    // from registry
  c4Classification: C4Classification; // from registry (refines cache/queue node compat)
  provider?: TechnologyMetadata["provider"];
  protocols: string[];
}

/** How a binding was placed. */
export type AssignmentBasis =
  | "unique-cardinality"   // R2: exactly one slot + exactly one candidate of a 1:1 category
  | "model-metadata"       // R1: backend node metadata
  | "manual-pick";         // R4: user chose it

/** A bound technology for a specific node. */
export interface TechnologyAssignment {
  nodeId: string;
  technologyId: string;
  technologyName: string;
  /** Who placed it. Never "inferred" for a binding. */
  source: AssignmentSource;
  confidence: AssignmentConfidence;
  basis: AssignmentBasis;
  detectedId?: string;             // back-reference to the DetectedTechnology that drove it
  evidenceText?: string;           // snippet shown in tooltip (e.g. "well PostgreSQL")
}

/** A candidate offered in the Assign UI without having been placed. */
export interface TechnologyCandidate {
  technology: DetectedTechnology;
  confidence: AssignmentConfidence; // "possible" | "ambiguous"
  basis: AssignmentBasis;
}

/** Unresolved ambiguity recorded during detection/binding. */
export interface EnrichmentConflict {
  span: TextPosition;
  technologyIds: string[];
  reason: "overlapping-span" | "coequal-category";
}

/** Presentation model layered over an untouched backend node. */
export interface EnrichedNode {
  nodeId: string;
  nodeType: string;                 // ui | service | database | cache | queue | container
  raw: ArchitectureNode;            // the frozen backend node (do not mutate)
  label: string;                    // final display label (tech name, or generic "Service 1")
  assignment: TechnologyAssignment | null;  // null ⇒ "Technology not specified"
  candidates: TechnologyCandidate[];
  overriddenByManual: boolean;     // true if a manual pick displaced an auto-bind
}

/** Whole-request enrichment result. */
export interface SemanticEnrichmentResult {
  requirement: string;
  detected: DetectedTechnology[];          // ordered by first mention
  enrichedNodes: EnrichedNode[];           // one per generated node
  unplaced: DetectedTechnology[];          // detected but honestly not placeable
  genericNodeIds: string[];                // nodes with no evidence at all
  conflicts: EnrichmentConflict[];
  builtAt: number;
}