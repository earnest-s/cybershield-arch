/**
 * Canonical frontend contract for the /explain endpoint.
 *
 * These types mirror backend/core/architecture_models.py (the single source
 * of truth). The wire shape is produced by response_builder.build_response /
 * response_to_explain_payload. Keep field-compatible with the backend models;
 * do not rename or remove keys the backend serves.
 */

export const NODE_TYPES = ["ui", "service", "database", "cache", "queue", "container"] as const;

export type NodeType = (typeof NODE_TYPES)[number];

export type ArchitectureNode = {
  id: string;
  type: string;
  icon?: string | null;
  layer?: string | null;
};

export type ArchitectureEdge = {
  source: string;
  target: string;
  label?: string;
  dashed?: boolean | null;
};

export type Architecture = {
  nodes: ArchitectureNode[];
  edges: ArchitectureEdge[];
};

export type ThreatInfo = {
  name: string;
  severity: string;
  description: string;
  missing_control?: string | null;
  severity_level?: string;
};

export type NodeThreat = {
  threat: string;
  severity: string;
  missing_control: string;
  severity_level?: string;
};

export type AttackSurface = {
  attack_surface_score: number;
  public_endpoints: number;
  databases: number;
  services: number;
};

export type SecurityData = {
  security_score: number;
  risk_level: string;
  missing_components: Array<Record<string, unknown>>;
  recommendations: string[];
  threats: ThreatInfo[];
  node_threats: Record<string, NodeThreat[]>;
  edge_threats: Record<string, NodeThreat[]>;
  attack_surface: AttackSurface;
  security_summary: string;
  required_controls?: string[];
  missing_controls?: string[];
};

export type ValidationIssue = {
  rule: string;
  severity: string;
  message: string;
};

export type ValidationResult = {
  valid: boolean;
  issues: ValidationIssue[];
  structurally_weak: boolean;
};

export type ArchitectureMetadata = {
  source: string;
  version: string;
  provider: string;
  duration_ms?: number | null;
  raw_output?: string | null;
};

/** Canonical /explain wire contract (backend ExplainResponse). */
export type ExplainResponse = {
  architecture: Architecture;
  security: SecurityData | null;
  metadata: ArchitectureMetadata;
  validation: ValidationResult;
  raw_model_output: string | null;
};

export type EditorCommand = {
  id: number;
  action: "reset" | "clear";
};