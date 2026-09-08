/**
 * TechnologyNodePresentation
 *
 * Upgrades architecture nodes so known technologies have a visually
 * identifiable presentation: provider badge + technology icon + display name
 * + architecture role/category.
 *
 * Generic nodes remain honest (Service 1, Database, External System, User).
 * Canonical IDs are preserved internally.
 */

import React, { useMemo } from "react";
import { getTechnologyRegistry } from "./registry";
import { TechnologyIcon } from "./TechnologyIcon";
import type { TechnologyMetadata } from "./types";

export interface TechnologyNodePresentationProps {
  /** Node id (used for resolution fallback) */
  nodeId: string;
  /** Node type (ui, service, database, cache, queue, container) */
  nodeType: string;
  /** Explicit technology from metadata */
  technologyId?: string;
  /** Explicit provider from metadata */
  provider?: string;
  /** Node display label */
  label: string;
  /** Icon size in px */
  iconSize?: number;
  /** Whether to show provider badge */
  showProvider?: boolean;
  /** Whether to show role/category line */
  showRole?: boolean;
  /** Layout: "row" (horizontal, default) or "column" */
  layout?: "row" | "column";
  className?: string;
}

function ProviderBadge({ provider }: { provider: string }) {
  const labels: Record<string, string> = {
    aws: "AWS",
    azure: "Azure",
    gcp: "GCP",
    cloudflare: "Cloudflare",
    oracle: "Oracle",
    digitalocean: "DigitalOcean",
    "multi-cloud": "Multi-Cloud",
    "on-premise": "On-Prem",
  };
  const actual = labels[provider] || provider;
  return (
    <span className={`tech-provider-badge tech-provider-badge--${provider ?? "default"}`}>
      {actual}
    </span>
  );
}

/**
 * Resolve a technology from node data.
 */
export function resolveNodeTechnology(
  nodeId: string,
  nodeType: string,
  technologyId?: string,
  label?: string
): { technology: TechnologyMetadata | undefined; label: string } {
  const registry = getTechnologyRegistry();

  // 1. Explicit technology from metadata
  if (technologyId) {
    const tech = registry.get(technologyId) || registry.getByLabel(technologyId) || registry.getByAlias(technologyId);
    if (tech) {
      return { technology: tech, label: label || tech.name };
    }
  }

  // 2. Resolve through the registry pipeline
  const resolved = registry.resolve(nodeId, nodeType, {
    label,
    technology: technologyId,
  });

  // Only use the resolved technology if it came from a reliable source
  // (not a generic fallback for a generic node id like service-1)
  if (resolved.resolutionSource === "generic-fallback") {
    return { technology: undefined, label };
  }

  return { technology: resolved.technology, label: resolved.technology.name };
}

/**
 * Enhanced node presentation combining provider badge + icon + label.
 */
export function TechnologyNodePresentation({
  nodeId,
  nodeType,
  technologyId,
  provider,
  label,
  iconSize = 16,
  showProvider = true,
  showRole = false,
  layout = "row",
  className,
}: TechnologyNodePresentationProps): React.ReactElement {
  const { technology } = resolveNodeTechnology(nodeId, nodeType, technologyId, label);

  return (
    <div className={`tech-node-presentation tech-node-presentation--${layout} ${className || ""}`}>
      {showProvider && provider && <ProviderBadge provider={provider} />}
      <div className="tech-node-presentation__icon">
        <TechnologyIcon technology={technology} technologyId={technologyId} size={iconSize} showFallback={false} />
      </div>
      <div className="tech-node-presentation__text">
        <span className="tech-node-presentation__name">{label}</span>
        {showRole && (
          <span className="tech-node-presentation__role">{nodeType}</span>
        )}
      </div>
    </div>
  );
}

/**
 * Small inline provider label.
 */
export function TechnologyProviderLabel({ provider }: { provider?: string }): React.ReactElement | null {
  if (!provider) return null;
  return <ProviderBadge provider={provider} />;
}
