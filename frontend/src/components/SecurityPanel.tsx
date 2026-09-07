import { SecurityData, ThreatInfo, NodeThreat, Architecture } from "../types";

function severityClass(level: string | undefined): "danger" | "warning" | "info" {
  if (level === "danger" || level === "warning") return level;
  return "info";
}

function RiskBadge({ level }: { level: string }) {
  const normalized = String(level || "").toUpperCase();
  const cls = normalized === "LOW" ? "low" : normalized === "MEDIUM" ? "medium" : "high";
  return <span className={`risk-badge risk-${cls}`}>{normalized || "UNKNOWN"}</span>;
}

function ThreatItem({ threat, showNode = false }: { threat: ThreatInfo | NodeThreat; showNode?: boolean }) {
  const name = "name" in threat ? threat.name : threat.threat;
  const missing = "missing_control" in threat ? threat.missing_control : undefined;
  const nodeId = "threat" in threat ? undefined : threat.threat;
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

function TrustBoundaryLegend() {
  return (
    <div className="trust-boundary-legend">
      <h4>Trust Boundaries</h4>
      <div className="legend-items">
        <div className="legend-item"><span className="legend-color" style={{ background: "#3b82f6" }} /> Public Zone</div>
        <div className="legend-item"><span className="legend-color" style={{ background: "#8b5cf6" }} /> Application Zone</div>
        <div className="legend-item"><span className="legend-color" style={{ background: "#10b981" }} /> Data Zone</div>
        <div className="legend-item"><span className="legend-color dashed" style={{ background: "#64748b" }} /> Internet / Untrusted</div>
      </div>
    </div>
  );
}

function EncryptionLegend() {
  return (
    <div className="encryption-legend">
      <h4>Connection Security</h4>
      <div className="legend-items">
        <div className="legend-item"><span className="legend-edge encrypted" /> Encrypted (TLS/mTLS)</div>
        <div className="legend-item"><span className="legend-edge unencrypted" /> Unencrypted</div>
        <div className="legend-item"><span className="legend-edge mutual-tls" /> Mutual TLS</div>
      </div>
    </div>
  );
}

function ThreatSeverityLegend() {
  return (
    <div className="severity-legend">
      <h4>Threat Severity</h4>
      <div className="legend-items">
        <div className="legend-item"><span className="severity-dot severity-danger" /> CRITICAL</div>
        <div className="legend-item"><span className="severity-dot severity-warning" /> HIGH</div>
        <div className="legend-item"><span className="severity-dot severity-info" /> MEDIUM</div>
      </div>
    </div>
  );
}

export default function SecurityPanel({ security, architecture }: { security: SecurityData | null; architecture?: Architecture | null }) {
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

  // Count threats by severity
  const threatCounts = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 };
  security.threats?.forEach((t) => { threatCounts[t.severity as keyof typeof threatCounts]++; });
  nodeThreatGroups.forEach(([, threats]) => threats.forEach((t) => { threatCounts[t.severity as keyof typeof threatCounts]++; }));
  edgeThreatGroups.forEach(([, threats]) => threats.forEach((t) => { threatCounts[t.severity as keyof typeof threatCounts]++; }));

  // Check for encrypted connections
  const hasEncryptedEdges = architecture?.edges?.some((e) => e.metadata?.encryption === "encrypted" || e.metadata?.encryption === "mutual-tls");
  const hasUnencryptedEdges = architecture?.edges?.some((e) => e.metadata?.encryption === "unencrypted");
  const hasMutualTlsEdges = architecture?.edges?.some((e) => e.metadata?.encryption === "mutual-tls");

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

      {/* Threat Summary */}
      <div className="threat-summary">
        <div className="threat-count critical" title="CRITICAL threats">
          <span className="count">{threatCounts.CRITICAL}</span>
          <span className="label">CRITICAL</span>
        </div>
        <div className="threat-count high" title="HIGH threats">
          <span className="count">{threatCounts.HIGH}</span>
          <span className="label">HIGH</span>
        </div>
        <div className="threat-count medium" title="MEDIUM threats">
          <span className="count">{threatCounts.MEDIUM}</span>
          <span className="label">MEDIUM</span>
        </div>
      </div>

      {/* Connection Security Summary */}
      {(hasEncryptedEdges || hasUnencryptedEdges || hasMutualTlsEdges) && (
        <div className="analysis-block">
          <h3>Connection Security</h3>
          <div className="connection-security-grid">
            {hasMutualTlsEdges && <span className="conn-sec mutual-tls">🔐 Mutual TLS</span>}
            {hasEncryptedEdges && <span className="conn-sec encrypted">🔒 TLS Encrypted</span>}
            {hasUnencryptedEdges && <span className="conn-sec unencrypted">⚠️ Unencrypted</span>}
          </div>
        </div>
      )}

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
                <ThreatItem key={`${nodeId}-${index}`} threat={threat} showNode />
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

      {/* Visual Legends */}
      <div className="security-legends">
        <TrustBoundaryLegend />
        <EncryptionLegend />
        <ThreatSeverityLegend />
      </div>
    </section>
  );
}