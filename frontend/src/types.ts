export const NODE_TYPES = ["ui", "service", "database", "cache", "queue", "container"] as const;

export type NodeType = (typeof NODE_TYPES)[number];

export type ArchitectureNode = {
  id: string;
  type: NodeType;
  icon?: string | null;
  layer?: string | null;
  [key: string]: unknown;
};

export type ArchitectureEdge = {
  source: string;
  target: string;
  label?: string;
  dashed?: boolean | null;
  [key: string]: unknown;
};

export type Architecture = {
  nodes: ArchitectureNode[];
  edges: ArchitectureEdge[];
  [key: string]: unknown;
};

export type EditorCommand = {
  id: number;
  action: "reset" | "clear";
};

export type ThreatInfo = {
  name: string;
  severity: string;
  description: string;
  missing_control?: string;
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
};