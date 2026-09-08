/**
 * Icon Lookup
 *
 * Provides simple-icons SVG data and lucide-react icon components.
 * Uses a tree-shakeable static index for simple-icons (only the icons we
 * explicitly import get bundled) with graceful fallback.
 */

import type { TechnologyIcon as TechnologyIconType } from "./types";
import { SIMPLE_ICON_INDEX } from "./iconIndex";

// ─── simple-icons lookups ───────────────────────────────────────────────────

/**
 * Synchronously get a simple-icons {title, path} by slug.
 * Returns null if the icon is not in our imported index.
 */
export function getSimpleIconPath(slug: string): { title: string; path: string } | null {
  const entry = SIMPLE_ICON_INDEX[slug];
  return entry || null;
}

/**
 * Preload is a no-op now since icons are statically imported and tree-shaken;
 * retained as a compatibility hook.
 */
export function preloadSimpleIcons(): void {
  // Icons are already statically imported (tree-shaken).
}

// ─── lucide-react icon map ──────────────────────────────────────────────────

import {
  Server,
  Database,
  Globe,
  Shield,
  Lock,
  Key,
  Eye,
  Activity,
  Zap,
  HardDrive,
  Box,
  Cpu,
  Cloud,
  GitBranch,
  GitMerge,
  Network,
  Layers,
  Code,
  Monitor,
  Smartphone,
  Terminal,
  BarChart3,
  LayoutGrid,
  Target,
  Fingerprint,
  Radio,
  Cog,
  Search,
  Clock,
  MessageSquare,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

const LUCIDE_ICON_MAP: Record<string, LucideIcon> = {
  server: Server,
  database: Database,
  globe: Globe,
  shield: Shield,
  lock: Lock,
  key: Key,
  "key-round": Key,
  eye: Eye,
  activity: Activity,
  zap: Zap,
  "hard-drive": HardDrive,
  box: Box,
  cpu: Cpu,
  cloud: Cloud,
  "git-branch": GitBranch,
  "git-merge": GitMerge,
  network: Network,
  layers: Layers,
  boxes: Layers,
  code: Code,
  monitor: Monitor,
  smartphone: Smartphone,
  terminal: Terminal,
  "bar-chart-3": BarChart3,
  "layout-grid": LayoutGrid,
  target: Target,
  fingerprint: Fingerprint,
  radio: Radio,
  cog: Cog,
  search: Search,
  clock: Clock,
  "message-square": MessageSquare,
  "shield-check": Shield,
  "shield-alert": Shield,
};

/**
 * Get a lucide-react icon component by name
 */
export function getLucideIcon(name: string): LucideIcon | null {
  return LUCIDE_ICON_MAP[name.toLowerCase()] || null;
}

// ─── resolve icon to renderable data ────────────────────────────────────────

/**
 * Resolve a TechnologyIcon to either an SVG path (simple-icons) or a lucide component.
 */
export function resolveIcon(
  icon: TechnologyIconType
): { source: "simple-icons"; title: string; path: string } | { source: "lucide"; Component: LucideIcon } | null {
  if (icon.source === "simple-icons") {
    const entry = getSimpleIconPath(icon.id);
    if (entry) return { source: "simple-icons", title: entry.title, path: entry.path };
    return null;
  }
  if (icon.source === "lucide") {
    const Component = getLucideIcon(icon.id);
    if (Component) return { source: "lucide", Component };
    return null;
  }
  return null;
}
