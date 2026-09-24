/**
 * TechnologiesPanel
 *
 * Shows technologies detected in the requirement, separated from how they were
 * placed on the diagram. Provenance is shown (source + confidence); the panel
 * never implies a technology was auto-assigned when it wasn't.
 */

import { useMemo } from "react";
import { InlineTechnologyIcon } from "../technology/TechnologyIcon";
import type { DetectedTechnology, SemanticEnrichmentResult } from "../enrichment/types";

interface TechnologiesPanelProps {
  enrichment: SemanticEnrichmentResult;
}

type TechStatus = "assigned" | "select-component" | "no-component";

const SOURCE_LABEL: Record<string, string> = {
  "explicit-user": "explicit in request",
  "deterministic-match": "deterministic match",
  "model-provided": "model metadata",
  "manual-user": "assigned by you",
  inferred: "inferred",
};

function statusFor(
  tech: DetectedTechnology,
  enrichment: SemanticEnrichmentResult
): { status: TechStatus; boundNodes: string[] } {
  const boundNodes = enrichment.enrichedNodes
    .filter((node) => node.assignment?.technologyId === tech.technologyId)
    .map((node) => node.nodeId);
  if (boundNodes.length > 0) return { status: "assigned", boundNodes };

  const hasCandidateSlot = enrichment.enrichedNodes.some((node) =>
    node.candidates.some((candidate) => candidate.technology.technologyId === tech.technologyId)
  );
  return { status: hasCandidateSlot ? "select-component" : "no-component", boundNodes };
}

function TechRow({ tech, enrichment }: { tech: DetectedTechnology; enrichment: SemanticEnrichmentResult }) {
  const { status, boundNodes } = statusFor(tech, enrichment);
  const source = SOURCE_LABEL[tech.source] ?? tech.source;
  const confidenceClass = tech.confidence === "possible" ? "tech-conf--possible" : "tech-conf--confirmed";

  return (
    <li className="tech-detect-row" title={tech.mentions.join(", ")}>
      <InlineTechnologyIcon technologyId={tech.technologyId} size={15} />
      <div className="tech-detect-main">
        <span className="tech-detect-name">{tech.technologyName}</span>
        <span className="tech-detect-src">{source}{tech.hedged ? " · suggestion" : ""}</span>
      </div>
      <span className={`tech-detect-status tech-status--${status} ${confidenceClass}`}>
        {status === "assigned" ? `→ ${boundNodes.join(", ")}` : status === "select-component" ? "select component" : "no matching component"}
      </span>
    </li>
  );
}

export function TechnologiesPanel({ enrichment }: TechnologiesPanelProps) {
  const groups = useMemo(() => {
    const confirmed = enrichment.detected.filter((d) => d.confidence === "confirmed");
    const tentative = enrichment.detected.filter((d) => d.confidence !== "confirmed");
    return { confirmed, tentative };
  }, [enrichment]);

  if (enrichment.detected.length === 0) return null;

  return (
    <section className="technologies-panel">
      <h3 className="control-label">Technologies Detected</h3>
      {groups.confirmed.length > 0 && (
        <ul className="tech-detect-list">
          {groups.confirmed.map((tech) => (
            <TechRow key={tech.technologyId} tech={tech} enrichment={enrichment} />
          ))}
        </ul>
      )}
      {groups.tentative.length > 0 && (
        <>
          <p className="muted tech-detect-sub">Suggested in request — not auto-claimed</p>
          <ul className="tech-detect-list">
            {groups.tentative.map((tech) => (
              <TechRow key={tech.technologyId} tech={tech} enrichment={enrichment} />
            ))}
          </ul>
        </>
      )}
      {enrichment.conflicts.length > 0 && (
        <p className="muted tech-detect-sub">Ambiguous mentions — assign a technology to resolve.</p>
      )}
    </section>
  );
}