import { Architecture, ArchitectureMetadata, ValidationResult } from "../types";

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
              <span className="detail-node-id">{node.id}</span>
              <span className="detail-node-type">{node.type}</span>
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