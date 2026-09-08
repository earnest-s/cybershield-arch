/**
 * Technology Module
 *
 * Centralized technology registry for CyberShield-Arch.
 * Provides technology metadata, resolution, icon rendering,
 * and UI components for architecture visualization.
 */

export type {
  TechnologyMetadata,
  TechnologyCategory,
  TechnologyCategoryInfo,
  C4Classification,
  ResolutionSource,
  TechnologyIcon as TechnologyIconConfig,
  TechnologyProtocol,
  ResolvedTechnology,
  TechnologyRegistryConfig,
} from "./types";

export {
  TechnologyRegistry,
  getTechnologyRegistry,
  resetTechnologyRegistry,
  resolveTechnology,
  getTechnology,
  searchTechnologies,
  getTechnologiesByCategory,
  getCategories,
  CATEGORY_INFO,
  DEFAULT_CATEGORY_ORDER,
} from "./registry";

// Icon system
export { TechnologyIcon, InlineTechnologyIcon } from "./TechnologyIcon";
export type { TechnologyIconProps } from "./TechnologyIcon";
export { getSimpleIconPath, getLucideIcon, resolveIcon, preloadSimpleIcons } from "./iconLookup";

// Node presentation
export { TechnologyNodePresentation, TechnologyProviderLabel, resolveNodeTechnology } from "./TechnologyNodePresentation";
export type { TechnologyNodePresentationProps } from "./TechnologyNodePresentation";
