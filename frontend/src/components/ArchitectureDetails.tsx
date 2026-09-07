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
              <span className="detail-node-label">{formatDisplayLabel(node.id, node.type)}</span>
              <span className="detail-node-type">{node.type}</span>
              <span className="detail-node-id">{node.id}</span>
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
              <span className={`detail-edge-label${edge.dashed ? " async" : ""}`}>{edge.label ?? "HTTP"}{edge.dashed ? " (async)" : ""}</span>
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