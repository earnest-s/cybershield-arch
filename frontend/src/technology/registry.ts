/**
 * Technology Registry
 *
 * Centralized registry for technology metadata, resolution, and rendering.
 * Provides a single source of truth for all technology-related information.
 */

import type {
  TechnologyMetadata,
  TechnologyCategory,
  TechnologyCategoryInfo,
  ResolvedTechnology,
  ResolutionSource,
  TechnologyRegistryConfig,
  TechnologyIcon,
  C4Classification,
} from "./types";

import { technologies as rawTechnologies } from "./data";

/**
 * Default category ordering for UI display
 */
export const DEFAULT_CATEGORY_ORDER: TechnologyCategory[] = [
  "cloud",
  "aws",
  "azure",
  "gcp",
  "kubernetes",
  "containers",
  "frontend",
  "backend",
  "databases",
  "cache",
  "messaging",
  "api-gateway",
  "load-balancing",
  "auth-identity",
  "security",
  "observability",
  "storage",
  "networking",
  "devops-cicd",
  "generic",
];

/**
 * Category display information
 */
export const CATEGORY_INFO: Record<TechnologyCategory, TechnologyCategoryInfo> = {
  cloud: { id: "cloud", label: "Cloud Platforms", description: "Major cloud providers", icon: "cloud", color: "#6366f1", order: 1 },
  aws: { id: "aws", label: "AWS Services", description: "Amazon Web Services", icon: "cube", color: "#ff9900", order: 2 },
  azure: { id: "azure", label: "Azure Services", description: "Microsoft Azure", icon: "cube", color: "#0078d4", order: 3 },
  gcp: { id: "gcp", label: "GCP Services", description: "Google Cloud Platform", icon: "cube", color: "#4285f4", order: 4 },
  kubernetes: { id: "kubernetes", label: "Kubernetes", description: "Container orchestration", icon: "boxes", color: "#326ce5", order: 5 },
  containers: { id: "containers", label: "Containers", description: "Container runtimes and tools", icon: "box", color: "#2496ed", order: 6 },
  frontend: { id: "frontend", label: "Frontend", description: "Frontend frameworks and tools", icon: "layout", color: "#61dafb", order: 7 },
  backend: { id: "backend", label: "Backend", description: "Backend frameworks and runtimes", icon: "server", color: "#68a063", order: 8 },
  databases: { id: "databases", label: "Databases", description: "Database systems", icon: "database", color: "#336791", order: 9 },
  cache: { id: "cache", label: "Cache", description: "Caching systems", icon: "zap", color: "#dc382d", order: 10 },
  messaging: { id: "messaging", label: "Messaging", description: "Message queues and event streaming", icon: "message-square", color: "#f59e0b", order: 11 },
  "api-gateway": { id: "api-gateway", label: "API Gateway", description: "API management and gateways", icon: "git-branch", color: "#8b5cf6", order: 12 },
  "load-balancing": { id: "load-balancing", label: "Load Balancing", description: "Load balancers and proxies", icon: "git-merge", color: "#ec4899", order: 13 },
  "auth-identity": { id: "auth-identity", label: "Auth & Identity", description: "Authentication and identity providers", icon: "shield", color: "#10b981", order: 14 },
  security: { id: "security", label: "Security", description: "Security tools and infrastructure", icon: "lock", color: "#ef4444", order: 15 },
  observability: { id: "observability", label: "Observability", description: "Monitoring, logging, tracing", icon: "activity", color: "#06b6d4", order: 16 },
  storage: { id: "storage", label: "Storage", description: "Object and file storage", icon: "hard-drive", color: "#8b5cf6", order: 17 },
  networking: { id: "networking", label: "Networking", description: "Network infrastructure", icon: "globe", color: "#64748b", order: 18 },
  "devops-cicd": { id: "devops-cicd", label: "DevOps / CI/CD", description: "Continuous integration and deployment", icon: "refresh-cw", color: "#84cc16", order: 19 },
  generic: { id: "generic", label: "Generic Components", description: "Generic architecture components", icon: "box", color: "#94a3b8", order: 20 },
};

/**
 * Technology Registry Class
 *
 * Singleton registry providing technology metadata, resolution, and utilities.
 */
export class TechnologyRegistry {
  private technologies: Map<string, TechnologyMetadata> = new Map();
  private aliasIndex: Map<string, string> = new Map(); // alias -> technology id
  private labelIndex: Map<string, string> = new Map(); // normalized label -> technology id
  private categoryIndex: Map<TechnologyCategory, Set<string>> = new Map();
  private providerIndex: Map<string, Set<string>> = new Map();
  private config: TechnologyRegistryConfig;

  constructor(config: Partial<TechnologyRegistryConfig> = {}) {
    this.config = {
      includeDeprecated: false,
      categoryOrder: DEFAULT_CATEGORY_ORDER,
      iconOverrides: {},
      ...config,
    };
    this.initialize();
  }

  /**
   * Initialize the registry with built-in technology data
   */
  private initialize(): void {
    // Initialize category index
    for (const cat of DEFAULT_CATEGORY_ORDER) {
      this.categoryIndex.set(cat, new Set());
    }

    // Load technologies from data file
    for (const tech of rawTechnologies) {
      this.register(tech);
    }
  }

  /**
   * Register a technology in the registry
   */
  register(tech: TechnologyMetadata): void {
    if (this.technologies.has(tech.id)) {
      console.warn(`Technology ${tech.id} already registered, skipping`);
      return;
    }

    // Apply icon overrides if any
    if (this.config.iconOverrides[tech.id]) {
      tech.icon = this.config.iconOverrides[tech.id];
    }

    this.technologies.set(tech.id, tech);
    this.categoryIndex.get(tech.category)?.add(tech.id);

    if (tech.provider) {
      if (!this.providerIndex.has(tech.provider)) {
        this.providerIndex.set(tech.provider, new Set());
      }
      this.providerIndex.get(tech.provider)!.add(tech.id);
    }

    // Index aliases
    for (const alias of tech.aliases) {
      const normalized = alias.toLowerCase().trim();
      this.aliasIndex.set(normalized, tech.id);
    }

    // Index primary label
    this.labelIndex.set(tech.name.toLowerCase().trim(), tech.id);
  }

  /**
   * Get technology by ID
   */
  get(id: string): TechnologyMetadata | undefined {
    return this.technologies.get(id);
  }

  /**
   * Get technology by exact label match
   */
  getByLabel(label: string): TechnologyMetadata | undefined {
    const normalized = label.toLowerCase().trim();
    const id = this.labelIndex.get(normalized);
    return id ? this.technologies.get(id) : undefined;
  }

  /**
   * Get technology by alias
   */
  getByAlias(alias: string): TechnologyMetadata | undefined {
    const normalized = alias.toLowerCase().trim();
    const id = this.aliasIndex.get(normalized);
    return id ? this.technologies.get(id) : undefined;
  }

  /**
   * Get all technologies in a category
   */
  getByCategory(category: TechnologyCategory): TechnologyMetadata[] {
    const ids = this.categoryIndex.get(category) || new Set();
    return Array.from(ids)
      .map((id) => this.technologies.get(id)!)
      .filter((t) => this.config.includeDeprecated || !t.deprecated)
      .sort((a, b) => a.name.localeCompare(b.name));
  }

  /**
   * Get all technologies by provider
   */
  getByProvider(provider: string): TechnologyMetadata[] {
    const ids = this.providerIndex.get(provider) || new Set();
    return Array.from(ids)
      .map((id) => this.technologies.get(id)!)
      .filter((t) => this.config.includeDeprecated || !t.deprecated)
      .sort((a, b) => a.name.localeCompare(b.name));
  }

  /**
   * Search technologies by query string
   */
  search(query: string): TechnologyMetadata[] {
    const normalized = query.toLowerCase().trim();
    if (!normalized) return [];

    const results = new Set<TechnologyMetadata>();

    // Exact ID match
    const byId = this.technologies.get(normalized);
    if (byId) results.add(byId);

    // Exact label match
    const byLabel = this.getByLabel(normalized);
    if (byLabel) results.add(byLabel);

    // Alias match
    const byAlias = this.getByAlias(normalized);
    if (byAlias) results.add(byAlias);

    // Partial matches on name and aliases
    for (const tech of this.technologies.values()) {
      if (this.config.includeDeprecated || !tech.deprecated) {
        if (tech.name.toLowerCase().includes(normalized)) {
          results.add(tech);
        } else if (tech.aliases.some((a) => a.toLowerCase().includes(normalized))) {
          results.add(tech);
        }
      }
    }

    return Array.from(results).sort((a, b) => a.name.localeCompare(b.name));
  }

  /**
   * Resolve a technology from available node information
   *
   * Resolution order:
   * 1. Explicit metadata.technology
   * 2. Exact label match
   * 3. Normalized label match
   * 4. Alias match
   * 5. Category fallback (based on node type)
   * 6. Generic fallback
   */
  resolve(
    nodeId: string,
    nodeType: string,
    metadata?: { label?: string; technology?: string; provider?: string }
  ): ResolvedTechnology {
    const originalInput = metadata?.technology || metadata?.label || nodeId;

    // 1. Explicit metadata.technology
    if (metadata?.technology) {
      const tech = this.get(metadata.technology) || this.getByLabel(metadata.technology) || this.getByAlias(metadata.technology);
      if (tech) {
        return {
          technology: tech,
          resolutionSource: "explicit-metadata",
          confidence: 1.0,
          originalInput,
        };
      }
    }

    // 2. Exact label match
    if (metadata?.label) {
      const tech = this.getByLabel(metadata.label);
      if (tech) {
        return {
          technology: tech,
          resolutionSource: "exact-label",
          confidence: 0.95,
          originalInput,
        };
      }
    }

    // 3. Normalized label match (nodeId often contains technology hints)
    const techFromId = this.getByLabel(nodeId) || this.getByAlias(nodeId);
    if (techFromId) {
      return {
        technology: techFromId,
        resolutionSource: "normalized-label",
        confidence: 0.85,
        originalInput,
      };
    }

    // 4. Alias/ID/label match on nodeId parts
    //    e.g. "postgresql-1" → PostgreSQL, "redis-cache-2" → Redis
    const idParts = nodeId.toLowerCase().split(/[-_]/);
    for (const part of idParts) {
      // Match against tech id, primary label, or any alias
      const byId = this.get(part);
      const byLabel = this.getByLabel(part);
      const byAlias = this.getByAlias(part);
      const tech = byId || byLabel || byAlias;
      if (tech) {
        return {
          technology: tech,
          resolutionSource: "alias",
          confidence: 0.75,
          originalInput,
        };
      }
    }

    // 4.5 Composite label match (e.g. "Postgres DB" → PostgreSQL)
    //    If a label or nodeId is exactly a known tech token plus one or more
    //    generic qualifier words ("db", "service", "cache", ...), resolve to
    //    that technology WITHOUT inferring a semantic identity.
    if (metadata?.label) {
      const composite = this.matchCompositeLabel(metadata.label);
      if (composite) {
        return {
          technology: composite,
          resolutionSource: "alias",
          confidence: 0.8,
          originalInput,
        };
      }
    }

    // 5. Category fallback based on node type
    const fallbackTech = this.getCategoryFallback(nodeType);
    if (fallbackTech) {
      return {
        technology: fallbackTech,
        resolutionSource: "category-fallback",
        confidence: 0.5,
        originalInput,
      };
    }

    // 6. Generic fallback
    const genericTech = this.getGenericFallback(nodeType);
    return {
      technology: genericTech,
      resolutionSource: "generic-fallback",
      confidence: 0.3,
      originalInput,
    };
  }

  /**
   * Get category-appropriate fallback technology.
   *
   * IMPORTANT: generic roles resolve to GENERIC technologies, never to a
   * specific brand. e.g. nodeType "database" → generic "Database" (not
   * "PostgreSQL"), "cache" → generic "Cache" (not "Redis"). Specific-brand
   * resolution only happens via explicit metadata / label / alias matches.
   */
  private getCategoryFallback(nodeType: string): TechnologyMetadata | undefined {    const fallbackMap: Record<string, string> = {
      ui: "web-ui",
      frontend: "web-ui",
      service: "service",
      microservice: "microservice",
      backend: "service",
      api: "rest-api",
      database: "database",
      db: "database",
      cache: "cache",
      queue: "queue",
      messaging: "queue",
      container: "container-generic",
      kubernetes: "kubernetes",
      k8s: "kubernetes",
      loadbalancer: "loadbalancer",
      loadbalancing: "loadbalancer",
      gateway: "gateway",
      "api-gateway": "gateway",
      auth: "auth",
      identity: "auth",
      monitoring: "monitoring",
      logging: "monitoring",
      tracing: "monitoring",
      storage: "database",
      cdn: "cdn",
      firewall: "firewall",
      vpc: "vpc",
      subnet: "subnet",
    };

    const fallbackId = fallbackMap[nodeType.toLowerCase()];
    if (fallbackId) {
      const tech = this.get(fallbackId);
      if (tech) return tech;
    }

    // Try to find any technology in the matching category
    const categoryMap: Record<string, TechnologyCategory> = {
      ui: "frontend",
      frontend: "frontend",
      service: "backend",
      microservice: "backend",
      backend: "backend",
      api: "api-gateway",
      database: "databases",
      db: "databases",
      cache: "cache",
      queue: "messaging",
      messaging: "messaging",
      container: "containers",
      kubernetes: "kubernetes",
      k8s: "kubernetes",
      loadbalancer: "load-balancing",
      gateway: "api-gateway",
      "api-gateway": "api-gateway",
      auth: "auth-identity",
      identity: "auth-identity",
      monitoring: "observability",
      logging: "observability",
      tracing: "observability",
      storage: "storage",
      cdn: "networking",
      firewall: "security",
      vpc: "networking",
      subnet: "networking",
    };

    const category = categoryMap[nodeType.toLowerCase()];
    if (category) {
      const techs = this.getByCategory(category);
      if (techs.length > 0) return techs[0];
    }

    return undefined;
  }

  /**
   * Get the ultimate generic fallback for a node type.
   * Always returns a GENERIC technology — never a specific brand.
   */
  private getGenericFallback(nodeType: string): TechnologyMetadata {
    const genericMap: Record<string, TechnologyMetadata> = {
      ui: this.get("web-ui")!,
      frontend: this.get("web-ui")!,
      service: this.get("service")!,
      microservice: this.get("microservice")!,
      backend: this.get("service")!,
      api: this.get("rest-api")!,
      database: this.get("database")!,
      db: this.get("database")!,
      cache: this.get("cache")!,
      queue: this.get("queue")!,
      messaging: this.get("queue")!,
      container: this.get("container-generic")!,
      kubernetes: this.get("kubernetes")!,
      k8s: this.get("kubernetes")!,
      loadbalancer: this.get("loadbalancer")!,
      gateway: this.get("gateway")!,
      auth: this.get("auth")!,
      monitoring: this.get("monitoring")!,
      storage: this.get("database")!,
    };

    return genericMap[nodeType.toLowerCase()] || this.get("service")!;
  }

  /**
   * Get all registered technologies
   */
  getAll(): TechnologyMetadata[] {
    return Array.from(this.technologies.values())
      .filter((t) => this.config.includeDeprecated || !t.deprecated)
      .sort((a, b) => a.name.localeCompare(b.name));
  }

  /**
   * Get all categories with technology counts
   */
  getCategories(): TechnologyCategoryInfo[] {
    return DEFAULT_CATEGORY_ORDER.map((cat) => ({
      ...CATEGORY_INFO[cat],
      count: this.getByCategory(cat).length,
    }));
  }

  /**
   * Get technology icon configuration
   */
  getIcon(techId: string): TechnologyIcon | undefined {
    const tech = this.get(techId);
    return tech?.icon;
  }

  /**
   * Check if a technology is deprecated
   */
  isDeprecated(techId: string): boolean {
    return this.get(techId)?.deprecated === true;
  }

  /**
   * Get replacement for deprecated technology
   */
  getReplacement(techId: string): TechnologyMetadata | undefined {
    const tech = this.get(techId);
    if (tech?.deprecated && tech.replacement) {
      return this.get(tech.replacement);
    }
    return undefined;
  }

  /**
   * Get total technology count
   */
  getCount(): number {
    return this.getAll().length;
  }

  /**
   * Update configuration
   */
  configure(config: Partial<TechnologyRegistryConfig>): void {
    this.config = { ...this.config, ...config };
  }
}

/**
 * Singleton instance
 */
let registryInstance: TechnologyRegistry | null = null;

/**
 * Get the singleton registry instance
 */
export function getTechnologyRegistry(config?: Partial<TechnologyRegistryConfig>): TechnologyRegistry {
  if (!registryInstance) {
    registryInstance = new TechnologyRegistry(config);
  }
  return registryInstance;
}

/**
 * Reset the singleton (useful for testing)
 */
export function resetTechnologyRegistry(): void {
  registryInstance = null;
}

/**
 * Convenience function to resolve technology
 */
export function resolveTechnology(
  nodeId: string,
  nodeType: string,
  metadata?: { label?: string; technology?: string; provider?: string }
): ResolvedTechnology {
  return getTechnologyRegistry().resolve(nodeId, nodeType, metadata);
}

/**
 * Convenience function to get technology by ID
 */
export function getTechnology(id: string): TechnologyMetadata | undefined {
  return getTechnologyRegistry().get(id);
}

/**
 * Convenience function to search technologies
 */
export function searchTechnologies(query: string): TechnologyMetadata[] {
  return getTechnologyRegistry().search(query);
}

/**
 * Convenience function to get technologies by category
 */
export function getTechnologiesByCategory(category: TechnologyCategory): TechnologyMetadata[] {
  return getTechnologyRegistry().getByCategory(category);
}

/**
 * Convenience function to get all categories
 */
export function getCategories(): TechnologyCategoryInfo[] {
  return getTechnologyRegistry().getCategories();
}