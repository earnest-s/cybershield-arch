export type ThreatInfo = {
  name: string;
  severity: string;
  description: string;
  missing_control?: string;
};

export type NodeThreat = {
  threat: string;
  severity: string;
  missing_control: string;
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
