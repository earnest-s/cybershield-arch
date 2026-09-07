/**
 * Canonical frontend contract for the /explain endpoint.
 *
 * These types mirror backend/core/architecture_models.py (the single source
 * of truth). The wire shape is produced by response_builder.build_response /
 * response_to_explain_payload. Keep field-compatible with the backend models;
 * do not rename or remove keys the backend reads without re-approval.
 */

export const NODE_TYPES = ["ui", "service", "database", "cache", "queue", "container"] as const;

export type NodeType = (typeof NODE_TYPES)[number];

/** Extended node metadata (all optional for backward compatibility) */
export interface NodeMetadata {
  /** Human-readable label (may differ from canonical ID) */
  label?: string;
  /** Technology identifier (e.g., "postgresql", "kafka", "react") */
  technology?: string;
  /** Cloud provider (aws, azure, gcp, cloudflare, oracle, on-premise, multi-cloud) */
  provider?: string;
  /** Component category */
  category?: string;
  /** Free-form description */
  description?: string;
  /** Environment (prod, staging, dev, etc.) */
  environment?: string;
  /** Security/trust boundary identifier */
  boundary?: string;
  /** Deployment zone (public, private, dmz, etc.) */
  zone?: string;
  /** Arbitrary additional metadata */
  [key: string]: unknown;
}

/** Extended edge metadata (all optional for backward compatibility) */
export interface EdgeMetadata {
  /** Protocol (HTTPS, REST, gRPC, Kafka, AMQP, etc.) */
  protocol?: string;
  /** Relationship type (sync, async, event, replication, auth, data-flow) */
  relationship?: string;
  /** Direction (unidirectional, bidirectional) */
  direction?: "unidirectional" | "bidirectional";
  /** Whether this is an asynchronous connection */
  asynchronous?: boolean;
  /** Encryption status (encrypted, unencrypted, mutual-tls) */
  encryption?: string;
  /** Authentication mechanism (mtls, oauth, api-key, none) */
  authentication?: string;
  /** Arbitrary additional metadata */
  [key: string]: unknown;
}

export type ArchitectureNode = {
  id: string;
  type: string;
  icon?: string | null;
  layer?: string | null;
  /** Optional extended metadata */
  metadata?: NodeMetadata;
};

export type ArchitectureEdge = {
  source: string;
  target: string;
  label?: string;
  dashed?: boolean | null;
  /** Optional extended metadata */
  metadata?: EdgeMetadata;
};

export type Architecture = {
  nodes: ArchitectureNode[];
  edges: ArchitectureEdge[];
  /** Optional boundary/group definitions for C4-style views */
  boundaries?: ArchitectureBoundary[];
};

/** Boundary/container for grouping nodes (C4 containers, deployment zones, etc.) */
export interface ArchitectureBoundary {
  id: string;
  name: string;
  type: "system" | "container" | "deployment-zone" | "trust-boundary" | "cloud-account" | "k8s-namespace" | "vpc" | "subnet" | "custom";
  /** Child node IDs contained in this boundary */
  nodes?: string[];
  /** Child boundary IDs for nesting */
  boundaries?: string[];
  /** Visual style hints */
  style?: {
    color?: string;
    dashed?: boolean;
    labelPosition?: "top-left" | "top-center" | "top-right";
  };
}

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