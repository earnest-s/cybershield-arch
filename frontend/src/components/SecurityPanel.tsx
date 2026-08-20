import { SecurityData, ThreatInfo, NodeThreat } from "../types";

function severityClass(level: string | undefined): "danger" | "warning" | "info" {
  if (level === "danger" || level === "warning") return level;
  return "info";
}

function RiskBadge({ level }: { level: string }) {
  const normalized = String(level || "").toUpperCase();
  const cls = normalized === "LOW" ? "low" : normalized === "MEDIUM" ? "medium" : "high";
  return <span className={`risk-badge risk-${cls}`}>{normalized || "UNKNOWN"}</span>;
}

function ThreatItem({ threat }: { threat: ThreatInfo | NodeThreat }) {
  const name = "name" in threat ? threat.name : threat.threat;
  const missing = "missing_control" in threat ? threat.missing_control : undefined;
  return (
    <li className="threat-item">
      <span className={`severity-dot severity-${severityClass(threat.severity_level || threat.severity)}`} aria-hidden="true" />
      <div className="threat-item-body">
        <span className="threat-item-title">{name}</span>
        <span className="threat-item-severity">{threat.severity}</span>
        {missing ? <span className="threat-item-missing">Missing control: {missing}</span> : null}
      </div>
    </li>
  );
}

export default function SecurityPanel({ security }: { security: SecurityData | null }) {
  if (!security) {
    return (
      <section className="analysis-card">
        <h2>Security</h2>
        <p className="muted">Security analysis was not produced for this response.</p>
      </section>
    );
  }

  const nodeThreatGroups = Object.entries(security.node_threats ?? {});
  const edgeThreatGroups = Object.entries(security.edge_threats ?? {});

  return (
    <section className="analysis-card security-card">
      <div className="analysis-card-header">
        <h2>Security Posture</h2>
        <RiskBadge level={security.risk_level} />
      </div>

      <div className="score-row">
        <div className="score-value">
          <span className="score-number">{security.security_score}</span>
          <span className="score-max">/ 100</span>
        </div>
        <div className="score-label">Security score</div>
      </div>

      {security.security_summary ? <p className="security-summary">{security.security_summary}</p> : null}

      {security.attack_surface ? (
        <div className="metric-grid">
          <div className="metric">
            <span className="metric-value">{security.attack_surface.attack_surface_score}</span>
            <span className="metric-label">Attack surface</span>
          </div>
          <div className="metric">
            <span className="metric-value">{security.attack_surface.public_endpoints}</span>
            <span className="metric-label">Public endpoints</span>
          </div>
          <div className="metric">
            <span className="metric-value">{security.attack_surface.services}</span>
            <span className="metric-label">Services</span>
          </div>
          <div className="metric">
            <span className="metric-value">{security.attack_surface.databases}</span>
            <span className="metric-label">Databases</span>
          </div>
        </div>
      ) : null}

      {security.threats && security.threats.length > 0 ? (
        <div className="analysis-block">
          <h3>Threats</h3>
          <ul className="threat-list">
            {security.threats.map((threat, index) => (
              <ThreatItem key={index} threat={threat} />
            ))}
          </ul>
        </div>
      ) : null}

      {nodeThreatGroups.length > 0 ? (
        <div className="analysis-block">
          <h3>Affected Components</h3>
          <ul className="threat-list">
            {nodeThreatGroups.map(([nodeId, threats]) =>
              threats.map((threat, index) => (
                <ThreatItem key={`${nodeId}-${index}`} threat={threat} />
              ))
            )}
          </ul>
        </div>
      ) : null}

      {edgeThreatGroups.length > 0 ? (
        <div className="analysis-block">
          <h3>Connection Threats</h3>
          <ul className="threat-list">
            {edgeThreatGroups.map(([key, threats]) =>
              threats.map((threat, index) => (
                <li className="threat-item" key={`${key}-${index}`}>
                  <span className="edge-threat-key">{key.replace("->", " → ")}</span>
                  <span className="threat-item-severity">{threat.severity}</span>
                </li>
              ))
            )}
          </ul>
        </div>
      ) : null}

      {security.recommendations && security.recommendations.length > 0 ? (
        <div className="analysis-block">
          <h3>Recommendations</h3>
          <ul className="rec-list">
            {security.recommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </div>
      ) : null}

      {security.missing_controls && security.missing_controls.length > 0 ? (
        <div className="analysis-block">
          <h3>Missing Controls</h3>
          <ul className="rec-list">
            {security.missing_controls.map((control, index) => (
              <li key={index}>{control}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </section>
  );
}