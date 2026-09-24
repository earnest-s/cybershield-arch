/**
 * AssignTechnologyControl
 *
 * Property-panel control for assigning a technology to a single component node.
 * Surfaces candidate technologies detected in the requirement, plus a registry
 * search for manual assignment. Picking a candidate or a search result records a
 * manual assignment (manual-user / manual-pick) that the binding layer
 * prioritizes and that the export never includes.
 */

import { useMemo, useState } from "react";
import { InlineTechnologyIcon } from "../technology/TechnologyIcon";
import { searchTechnologies } from "../technology/registry";
import type { AssignmentConfidence, TechnologyAssignment, TechnologyCandidate } from "../enrichment/types";
import type { ManualAssignmentInput } from "../enrichment/bind";

interface AssignTechnologyControlProps {
  nodeId: string;
  current: TechnologyAssignment | null;
  candidates: TechnologyCandidate[];
  onAssign: (nodeId: string, assignment: ManualAssignmentInput | null) => void;
}

const CONFIDENCE_TITLE: Record<AssignmentConfidence, string> = {
  confirmed: "matched to one detected technology",
  possible: "possible match (suggested, not auto-claimed)",
  ambiguous: "several detected technologies could fit",
  unknown: "no detected technology",
};

type Option = {
  technologyId: string;
  technologyName: string;
  isCandidate: boolean;
  confidence: AssignmentConfidence;
};

export function AssignTechnologyControl({ nodeId, current, candidates, onAssign }: AssignTechnologyControlProps) {
  const [query, setQuery] = useState("");

  const candidateOptions = useMemo<Option[]>(() => {
    const seen = new Set<string>();
    const options: Option[] = [];
    for (const candidate of candidates) {
      const tech = candidate.technology;
      if (seen.has(tech.technologyId)) continue;
      seen.add(tech.technologyId);
      options.push({
        technologyId: tech.technologyId,
        technologyName: tech.technologyName,
        isCandidate: true,
        confidence: candidate.confidence,
      });
    }
    return options;
  }, [candidates]);

  const searchOptions = useMemo<Option[]>(() => {
    const q = query.trim();
    if (!q) return [];
    return searchTechnologies(q)
      .slice(0, 15)
      .map((tech) => ({
        technologyId: tech.id,
        technologyName: tech.name,
        isCandidate: false,
        confidence: "possible" as AssignmentConfidence,
      }));
  }, [query]);

  const selectable = [...candidateOptions, ...searchOptions.filter((option) => !candidateOptions.some((c) => c.technologyId === option.technologyId))];

  const handlePick = (technologyId: string) => {
    const option = selectable.find((entry) => entry.technologyId === technologyId);
    if (!option) return;
    onAssign(nodeId, { technologyId: option.technologyId, technologyName: option.technologyName });
    setQuery("");
  };

  return (
    <div className="assign-tech-control">
      <div className="assign-tech-head">
        <span className="assign-tech-label">Technology</span>
        {current ? (
          <button type="button" className="link-btn" onClick={() => onAssign(nodeId, null)}>Not specified</button>
        ) : null}
      </div>

      {current ? (
        <p className="assign-tech-current">
          <InlineTechnologyIcon technologyId={current.technologyId} size={14} />
          <span>{current.technologyName}</span>
          <span className="assign-tech-source" title="This assignment is live in this session only; it is not part of the exported architecture.">manual</span>
        </p>
      ) : null}

      {selectable.length > 0 ? (
        <>
          <select
            className="assign-tech-select"
            value=""
            title={candidateOptions.length > 0 ? `Detected recommendations — ${candidateOptions.length}` : "Registry search"}
            onChange={(event) => handlePick(event.target.value)}
          >
            <option value="">Assign a technology…</option>
            {candidateOptions.length > 0 ? (
              <optgroup label="Detected in request">
                {candidateOptions.map((option) => (
                  <option key={option.technologyId} value={option.technologyId} title={CONFIDENCE_TITLE[option.confidence]}>
                    {option.isCandidate && option.confidence !== "confirmed" ? "? " : ""}{option.technologyName}
                  </option>
                ))}
              </optgroup>
            ) : null}
            {searchOptions.length > 0 ? (
              <optgroup label="Registry search">
                {searchOptions.map((option) => (
                  <option key={`search-${option.technologyId}`} value={option.technologyId}>{option.technologyName}</option>
                ))}
              </optgroup>
            ) : null}
          </select>
          <input
            className="assign-tech-search"
            type="text"
            placeholder="Search registry…"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </>
      ) : (
        <p className="muted assign-tech-empty">No detected technologies for a {candidates.length === 0 ? "component" : "node"}. Use the search to assign one.</p>
      )}
    </div>
  );
}