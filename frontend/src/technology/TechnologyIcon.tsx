/**
 * TechnologyIcon
 *
 * Reusable icon component for technology visualization.
 * Renders known technology icons consistently across the UI.
 *
 * Supports:
 * - simple-icons SVG paths
 * - lucide-react components
 * - Light/dark theme awareness
 * - Accessible labels
 * - Graceful fallback (never broken images, never emoji)
 */

import React, { useMemo } from "react";
import type { TechnologyMetadata } from "./types";
import { resolveIcon, getLucideIcon, getSimpleIconPath } from "./iconLookup";
import { getTechnologyRegistry } from "./registry";

export interface TechnologyIconProps {
  /** Technology ID from the registry */
  technologyId?: string;
  /** Direct TechnologyMetadata (avoids lookup) */
  technology?: TechnologyMetadata;
  /** Icon override slug for simple-icons */
  simpleIconSlug?: string;
  /** Icon override name for lucide */
  lucideIcon?: string;
  /** Icon size in pixels */
  size?: number;
  /** Additional CSS class */
  className?: string;
  /** Accessible label override */
  ariaLabel?: string;
  /** Whether to show a fallback placeholder when icon is unavailable */
  showFallback?: boolean;
}

function FallbackPlaceholder({
  size,
  className,
  ariaLabel,
}: {
  size: number;
  className?: string;
  ariaLabel?: string;
}) {
  return (
    <span
      className={`tech-icon tech-icon--fallback ${className || ""}`}
      style={{ width: size, height: size, display: "inline-flex", alignItems: "center", justifyContent: "center" }}
      role="img"
      aria-label={ariaLabel || "Technology icon"}
    >
      <svg viewBox="0 0 24 24" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.5">
        <rect x="3" y="3" width="18" height="18" rx="3" strokeOpacity={0.4} />
        <circle cx="12" cy="12" r="4" fill="currentColor" fillOpacity={0.25} />
      </svg>
    </span>
  );
}

/**
 * TechnologyIcon component.
 *
 * Resolution order:
 * 1. Direct simpleIconSlug / lucideIcon props
 * 2. Technology metadata from registry
 * 3. Fallback placeholder
 */
export function TechnologyIcon({
  technologyId,
  technology,
  simpleIconSlug,
  lucideIcon,
  size = 16,
  className,
  ariaLabel,
  showFallback = true,
}: TechnologyIconProps): React.ReactElement {
  // Resolve the technology metadata
  const tech = useMemo(() => {
    if (technology) return technology;
    if (technologyId) {
      return getTechnologyRegistry().get(technologyId);
    }
    return undefined;
  }, [technology, technologyId]);

  // Resolve the icon
  const resolved = useMemo(() => {
    // 1. Direct slug overrides take priority
    if (simpleIconSlug) {
      const entry = getSimpleIconPath(simpleIconSlug);
      if (entry) return { source: "simple-icons" as const, title: entry.title, path: entry.path };
    }
    if (lucideIcon) {
      const Component = getLucideIcon(lucideIcon);
      if (Component) return { source: "lucide" as const, Component };
    }

    // 2. Technology metadata icon
    if (tech?.icon) {
      return resolveIcon(tech.icon);
    }

    return null;
  }, [tech, simpleIconSlug, lucideIcon]);

  // 3. Render
  if (!resolved) {
    if (showFallback) {
      return <FallbackPlaceholder size={size} className={className} ariaLabel={ariaLabel} />;
    }
    // Return invisible placeholder when fallback disabled
    return (
      <span
        className="tech-icon tech-icon--hidden"
        style={{ width: size, height: size, display: "inline-block" }}
      />
    );
  }

  if (resolved.source === "simple-icons") {
    return (
      <svg
        className={`tech-icon tech-icon--svg ${className || ""}`}
        viewBox="0 0 24 24"
        width={size}
        height={size}
        role="img"
        aria-label={ariaLabel || resolved.title}
        style={{ display: "inline-block", verticalAlign: "middle" }}
      >
        <path d={resolved.path} fill="currentColor" />
      </svg>
    );
  }

  if (resolved.source === "lucide") {
    const IconComponent = resolved.Component;
    return (
      <IconComponent
        className={`tech-icon tech-icon--lucide ${className || ""}`}
        size={size}
      />
    );
  }

  return <FallbackPlaceholder size={size} className={className} ariaLabel={ariaLabel} />;
}

/**
 * Lightweight inline icon for use inside text/labels.
 * Resolves technology by ID and renders inline SVG or lucide icon.
 */
export function InlineTechnologyIcon({
  technologyId,
  technology,
  size = 14,
  className,
}: {
  technologyId?: string;
  technology?: TechnologyMetadata;
  size?: number;
  className?: string;
}): React.ReactElement | null {
  const tech = technology || (technologyId ? getTechnologyRegistry().get(technologyId) : undefined);

  if (!tech?.icon) return null;

  const resolved = resolveIcon(tech.icon);

  if (!resolved) return null;

  if (resolved.source === "simple-icons") {
    return (
      <svg
        className={`tech-icon-inline ${className || ""}`}
        viewBox="0 0 24 24"
        width={size}
        height={size}
        role="img"
        aria-label={resolved.title}
        style={{ display: "inline-block", verticalAlign: "middle", marginRight: 4 }}
      >
        <path d={resolved.path} fill="currentColor" />
      </svg>
    );
  }

  if (resolved.source === "lucide") {
    const IconComponent = resolved.Component;
    return (
      <span
        className={`tech-icon-inline ${className || ""}`}
        style={{ display: "inline-flex", alignItems: "center", marginRight: 4 }}
      >
        <IconComponent size={size} />
      </span>
    );
  }

  return null;
}
