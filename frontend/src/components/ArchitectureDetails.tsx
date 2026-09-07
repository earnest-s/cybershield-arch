import { Architecture, ArchitectureMetadata, ValidationResult, NodeMetadata, EdgeMetadata, ArchitectureBoundary } from "../types";
import { getTechnology, TECHNOLOGY_CATEGORIES } from "../technologyCatalog";

function formatDisplayLabel(nodeId: string, nodeType: string, metadata?: NodeMetadata): string {
  // Use explicit label from metadata if available
  if (metadata?.label && metadata.label.trim()) {
    return metadata.label.trim();
  }
  // Use technology name from metadata if available
  if (metadata?.technology) {
    const tech = getTechnology(metadata.technology);
    if (tech) return tech.name;
  }
  // Final fallback: canonical ID format
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

function ValidationStatus({ validation }: { validation: ValidationResult }) {
  if (validation.valid) {
    return (
      <div className="validation-status valid">
        <span className="validation-dot" aria-hidden="true" />
        Validated — conforms to the architecture contract
      </div>
    );
  }
  return (
    <div className="validation-status invalid">
      <span className="validation-dot" aria-hidden="true" />
      Validation issues found
    </div>
  );
}

export default function ArchitectureDetails({
  architecture,
  validation,
  metadata,
}: {
  architecture: Architecture;
  validation: ValidationResult;
  metadata: ArchitectureMetadata;
}) {
  const nodeTypes = new Set(architecture.nodes.map((node) => node.type));
  const edgeLabels = new Set(architecture.edges.map((edge) => edge.label ?? "HTTP"));

  return (
    <section className="analysis-card details-card">
      <h2>Architecture Details</h2>

      <div className="metric-grid">
        <div className="metric">
          <span className="metric-value">{architecture.nodes.length}</span>
          <span className="metric-label">Components</span>
        </div>
        <div className="metric">
          <span className="metric-value">{architecture.edges.length}</span>
          <span className="metric-label">Connections</span>
        </div>
        <div className="metric">
          <span className="metric-value">{nodeTypes.size}</span>
          <span className="metric-label">Node types</span>
        </div>
        <div className="metric">
          <span className="metric-value">{edgeLabels.size}</span>
          <span className="metric-label">Edge types</span>
        </div>
      </div>

      <div className="analysis-block">
        <h3>Components</h3>
        <ul className="detail-list">
          {architecture.nodes.map((node) => (
            <li key={node.id}>
              <span className="detail-node-label">{formatDisplayLabel(node.id, node.type, node.metadata)}</span>
              <span className="detail-node-type">{node.type}</span>
              <span className="detail-node-id">{node.id}</span>
              {node.metadata?.technology && (
                <span className="detail-node-tech" title={node.metadata.technology}>
                  🔧 {getTechnology(node.metadata.technology)?.name || node.metadata.technology}
                </span>
              )}
              {node.metadata?.provider && (
                <span className="detail-node-provider" title={node.metadata.provider}>
                  ☁ {node.metadata.provider.toUpperCase()}
                </span>
              )}
              {node.metadata?.boundary && (
                <span className="detail-node-boundary" title={node.metadata.boundary}>
                  🔒 {node.metadata.boundary}
                </span>
              )}
              {node.metadata?.environment && (
                <span className="detail-node-env" title={node.metadata.environment}>
                  🌍 {node.metadata.environment}
                </span>
              )}
            </li>
          ))}
        </ul>
      </div>

      <div className="analysis-block">
        <h3>Data Flow</h3>
        <ul className="detail-list">
          {architecture.edges.map((edge, index) => (
            <li key={index}>
              <span className="detail-flow">{edge.source} → {edge.target}</span>
              <span className={`detail-edge-label${edge.dashed ? " async" : ""}`}>
                {edge.label ?? "HTTP"}{edge.dashed ? " (async)" : ""}
              </span>
              {edge.metadata?.protocol && (
                <span className="detail-edge-protocol" title={edge.metadata.protocol}>
                  📡 {edge.metadata.protocol}
                </span>
              )}
              {edge.metadata?.relationship && (
                <span className="detail-edge-relationship" title={edge.metadata.relationship}>
                  ↔ {edge.metadata.relationship}
                </span>
              )}
              {edge.metadata?.encryption && (
                <span className="detail-edge-encryption" title={edge.metadata.encryption}>
                  🔐 {edge.metadata.encryption}
                </span>
              )}
            </li>
          ))}
        </ul>
      </div>

      <div className="analysis-block">
        <h3>Validation</h3>
        <ValidationStatus validation={validation} />
        {validation.issues && validation.issues.length > 0 ? (
          <ul className="detail-list">
            {validation.issues.map((issue, index) => (
              <li key={index}>
                <span className="detail-issue">{issue.rule}: {issue.message}</span>
              </li>
            ))}
          </ul>
        ) : null}
      </div>

      <div className="analysis-block">
        <h3>Boundaries & Groups</h3>
        {architecture.boundaries && architecture.boundaries.length > 0 ? (
          <ul className="detail-list">
            {architecture.boundaries.map((boundary) => (
              <li key={boundary.id}>
                <span className="detail-boundary-name">{boundary.name}</span>
                <span className="detail-boundary-type">{boundary.type}</span>
                <span className="detail-boundary-nodes">{boundary.nodes?.length || 0} nodes</span>
                {boundary.boundaries && boundary.boundaries.length > 0 && (
                  <span className="detail-boundary-nested">{boundary.boundaries.length} nested</span>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p className="muted">No boundaries defined</p>
        )}
      </div>

      <div className="analysis-block">
        <h3>Metadata</h3>
        <ul className="detail-list meta-list">
          {metadata.provider ? <li><span>Provider</span><span>{metadata.provider}</span></li> : null}
          {metadata.source ? <li><span>Source</span><span>{metadata.source}</span></li> : null}
          {metadata.version ? <li><span>Contract version</span><span>{metadata.version}</span></li> : null}
          {typeof metadata.duration_ms === "number" ? <li><span>Generation time</span><span>{metadata.duration_ms} ms</span></li> : null}
        </ul>
      </div>
    </section>
  );
}