/**
 * Technology Catalog — Compatibility Shim
 *
 * This file provides backward-compatible exports that delegate to the new
 * technology registry module. New code should import from ./technology instead.
 *
 * @module technologyCatalog
 * @deprecated Use ../technology for new code.
 */

import type { TechnologyMetadata, TechnologyCategory as NewCategory } from "./technology/types";
import { getTechnologyRegistry, CATEGORY_INFO } from "./technology/registry";

// ─── Old category → New category mapping ────────────────────────────────────

type LegacyCategory =
  | "application"
  | "compute"
  | "database"
  | "messaging"
  | "network"
  | "security"
  | "observability"
  | "cloud-provider"
  | "container-kubernetes"
  | "other";

export type TechnologyCategory = LegacyCategory;

const TO_LEGACY: Record<NewCategory, LegacyCategory> = {
  cloud: "cloud-provider",
  aws: "cloud-provider",
  azure: "cloud-provider",
  gcp: "cloud-provider",
  kubernetes: "container-kubernetes",
  containers: "container-kubernetes",
  frontend: "application",
  backend: "compute",
  databases: "database",
  cache: "database",
  messaging: "messaging",
  "api-gateway": "application",
  "load-balancing": "network",
  "auth-identity": "security",
  security: "security",
  observability: "observability",
  storage: "database",
  networking: "network",
  "devops-cicd": "other",
  generic: "other",
};

const TO_NEW: Record<LegacyCategory, NewCategory> = {
  application: "generic",
  compute: "generic",
  database: "databases",
  messaging: "messaging",
  network: "networking",
  security: "security",
  observability: "observability",
  "cloud-provider": "cloud",
  "container-kubernetes": "kubernetes",
  other: "generic",
};

// ─── Legacy Technology interface ────────────────────────────────────────────

export interface Technology {
  id: string;
  name: string;
  category: TechnologyCategory;
  icon: string;
  provider?: TechnologyMetadata["provider"];
  aliases?: string[];
  description?: string;
  managed?: boolean;
  related?: string[];
}

function toLegacy(tech: TechnologyMetadata): Technology {
  return {
    id: tech.id,
    name: tech.name,
    category: TO_LEGACY[tech.category],
    icon: tech.icon.source === "simple-icons" ? tech.icon.id : tech.icon.id,
    provider: tech.provider,
    aliases: tech.aliases,
    description: tech.description,
    managed: tech.managed,
  };
}

// ─── Legacy TECHNOLOGY_CATEGORIES ───────────────────────────────────────────

export const TECHNOLOGY_CATEGORIES: Record<
  TechnologyCategory,
  { label: string; icon: string; color: string }
> = {
  application: { label: "Application", icon: "monitor", color: "#3b82f6" },
  compute: { label: "Compute", icon: "server", color: "#8b5cf6" },
  database: { label: "Database", icon: "database", color: "#10b981" },
  messaging: { label: "Messaging", icon: "message-square", color: "#f59e0b" },
  network: { label: "Network", icon: "globe", color: "#ec4899" },
  security: { label: "Security", icon: "shield", color: "#ef4444" },
  observability: { label: "Observability", icon: "activity", color: "#06b6d4" },
  "cloud-provider": { label: "Cloud Provider", icon: "cloud", color: "#6366f1" },
  "container-kubernetes": { label: "Container/K8s", icon: "kubernetes", color: "#326ce5" },
  other: { label: "Other", icon: "box", color: "#64748b" },
};

// ─── Legacy TECHNOLOGY_CATALOG ──────────────────────────────────────────────

export const TECHNOLOGY_CATALOG: Technology[] = getTechnologyRegistry()
  .getAll()
  .map(toLegacy);

// ─── Legacy functions ───────────────────────────────────────────────────────

/**
 * Lookup technology by ID
 */
export function getTechnology(id: string): Technology | undefined {
  const tech = getTechnologyRegistry().get(id);
  return tech ? toLegacy(tech) : undefined;
}

/**
 * Lookup technology by alias
 */
export function findTechnologyByAlias(alias: string): Technology | undefined {
  const tech = getTechnologyRegistry().getByAlias(alias);
  return tech ? toLegacy(tech) : undefined;
}

/**
 * Get all technologies in a legacy category
 */
export function getTechnologiesByCategory(category: TechnologyCategory): Technology[] {
  const newCat = TO_NEW[category];
  return getTechnologyRegistry()
    .getByCategory(newCat)
    .map(toLegacy)
    .filter((t) => t.category === category);
}

/**
 * Get technologies by provider
 */
export function getTechnologiesByProvider(provider: Technology["provider"]): Technology[] {
  if (!provider) return [];
  return getTechnologyRegistry()
    .getByProvider(provider)
    .map(toLegacy);
}

/**
 * Infer technology from node ID and type
 */
export function inferTechnology(nodeId: string, nodeType: string): Technology | undefined {
  const result = getTechnologyRegistry().resolve(nodeId, nodeType);
  // Only return concrete results, not generic fallbacks
  if (result.resolutionSource === "generic-fallback") return undefined;
  return toLegacy(result.technology);
}

/**
 * Get display label for a node
 */
export function getDisplayLabel(
  nodeId: string,
  nodeType: string,
  explicitLabel?: string,
  technology?: Technology
): string {
  if (explicitLabel && explicitLabel.trim()) {
    return explicitLabel.trim();
  }
  if (technology) {
    return technology.name;
  }
  const inferred = inferTechnology(nodeId, nodeType);
  if (inferred) return inferred.name;

  const categoryNames: Record<string, string> = {
    ui: "UI",
    service: "Service",
    database: "Database",
    cache: "Cache",
    queue: "Queue",
    container: "Container",
  };
  const categoryName = categoryNames[nodeType] || "Component";
  const match = nodeId.match(/^([a-z]+)-(\d+)$/i);
  if (match) return `${categoryName} ${match[2]}`;
  return nodeId;
}
