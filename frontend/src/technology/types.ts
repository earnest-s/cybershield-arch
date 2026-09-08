/**
 * Technology Registry Types
 *
 * Core type definitions for the technology registry system.
 * These types define the contract for technology metadata,
 * resolution, and rendering.
 */

export type TechnologyCategory =
  | "cloud"
  | "aws"
  | "azure"
  | "gcp"
  | "kubernetes"
  | "containers"
  | "frontend"
  | "backend"
  | "databases"
  | "cache"
  | "messaging"
  | "api-gateway"
  | "load-balancing"
  | "auth-identity"
  | "security"
  | "observability"
  | "storage"
  | "networking"
  | "devops-cicd"
  | "generic";

export type C4Classification =
  | "system"
  | "container"
  | "component"
  | "infrastructure"
  | "external-system"
  | "database"
  | "queue"
  | "cache"
  | "unknown";

export type ResolutionSource =
  | "explicit-metadata"
  | "exact-label"
  | "normalized-label"
  | "alias"
  | "category-fallback"
  | "generic-fallback";

export interface TechnologyIcon {
  /** Identifier for the icon (e.g., "postgresql", "aws-lambda") */
  id: string;
  /** Source of the icon: "simple-icons" | "lucide" | "custom" */
  source: "simple-icons" | "lucide" | "custom";
  /** Optional custom SVG path if using custom icons */
  customPath?: string;
  /** Whether the icon supports dark/light variants */
  supportsThemeVariants?: boolean;
}

export interface TechnologyProtocol {
  /** Protocol identifier (e.g., "HTTP", "gRPC", "Kafka") */
  id: string;
  /** Display name */
  name: string;
  /** Default port if applicable */
  defaultPort?: number;
  /** Whether this protocol implies encryption */
  encryptedByDefault?: boolean;
  /** Authentication methods commonly used */
  authMethods?: string[];
}

export interface TechnologyMetadata {
  /** Unique identifier */
  id: string;
  /** Human-readable display name */
  name: string;
  /** Alternative names for matching */
  aliases: string[];
  /** Primary category */
  category: TechnologyCategory;
  /** Cloud provider if applicable */
  provider?: "aws" | "azure" | "gcp" | "cloudflare" | "oracle" | "digitalocean" | "on-premise" | "multi-cloud";
  /** C4 model classification */
  c4Classification: C4Classification;
  /** Icon configuration */
  icon: TechnologyIcon;
  /** Protocols this technology typically uses */
  protocols: string[];
  /** Whether this is a managed service */
  managed?: boolean;
  /** License information for the technology (for attribution) */
  license?: string;
  /** Official website */
  website?: string;
  /** Short description */
  description?: string;
  /** Deprecated flag */
  deprecated?: boolean;
  /** Replacement technology ID if deprecated */
  replacement?: string;
}

export interface ResolvedTechnology {
  /** The resolved technology metadata */
  technology: TechnologyMetadata;
  /** How the technology was resolved */
  resolutionSource: ResolutionSource;
  /** Confidence score (0-1) */
  confidence: number;
  /** Original input that was resolved */
  originalInput: string;
}

export interface TechnologyCategoryInfo {
  id: TechnologyCategory;
  label: string;
  description: string;
  icon: string; // lucide icon name for category header
  color: string; // theme color for category
  order: number; // display order
  /** Number of technologies in this category */
  count?: number;
}

export interface TechnologyRegistryConfig {
  /** Whether to include deprecated technologies in searches */
  includeDeprecated: boolean;
  /** Default category order for display */
  categoryOrder: TechnologyCategory[];
  /** Custom icon overrides */
  iconOverrides: Record<string, TechnologyIcon>;
}