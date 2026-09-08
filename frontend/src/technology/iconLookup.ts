/**
 * Icon Lookup
 *
 * Provides simple-icons SVG data and lucide-react icon components.
 * Uses a preloaded cache for common icons with async fallback.
 */

import type { TechnologyIcon as TechnologyIconType } from "./types";

// ─── simple-icons lazy cache ────────────────────────────────────────────────

type SimpleIconEntry = { title: string; path: string } | null;

const simpleIconCache = new Map<string, SimpleIconEntry>();

/** Dynamically import a single simple-icons icon by its package export name */
async function importSimpleIcon(slug: string): Promise<SimpleIconEntry> {
  if (simpleIconCache.has(slug)) return simpleIconCache.get(slug)!;
  try {
    const mod = await import("simple-icons");
    const icon = mod[slug as keyof typeof mod];
    if (icon && typeof icon === "object" && "path" in icon && "title" in icon) {
      const entry: SimpleIconEntry = { title: icon.title, path: icon.path };
      simpleIconCache.set(slug, entry);
      return entry;
    }
  } catch {
    // not available
  }
  simpleIconCache.set(slug, null);
  return null;
}

/**
 * Synchronously get a cached simple-icons path.
 * Returns null if not yet loaded or unavailable.
 * Kicks off async load if not cached.
 */
export function getSimpleIconPath(slug: string): { title: string; path: string } | null {
  const entry = simpleIconCache.get(slug);
  if (entry !== undefined) return entry;
  // Not loaded yet — start async
  importSimpleIcon(slug);
  return null;
}

/**
 * Preload common simple-icons at module init (non-blocking).
 * Call this once at app startup.
 */
const PRELOAD_SLUGS = [
  "siPostgresql", "siMysql", "siMongodb", "siRedis", "siAmazondynamodb",
  "siDocker", "siKubernetes", "siNginx", "siApachekafka", "siRabbitmq",
  "siNatsdotio", "siAmazonsqs", "siGooglepubsub",
  "siReact", "siNextdotjs", "siVuedotjs", "siAngular", "siSvelte",
  "siPython", "siFastapi", "siFlask", "siDjango", "siNodedotjs",
  "siExpress", "siSpring", "siDotnet", "siGo", "siRust",
  "siGrafana", "siPrometheus", "siOpentelemetry", "siJaeger",
  "siElasticsearch", "siKong", "siEnvoyproxy", "siIstio", "siLinkerd",
  "siKeycloak", "siOkta", "siAuth0", "siVault",
  "siTerraform", "siAnsible", "siJenkins", "siGithubactions", "siGitlab",
  "siAmazonwebservices", "siGooglecloud", "siCloudflare",
  "siTailwindcss", "siVite", "siWebpack", "siTypescript", "siJavascript",
  "siSnowflake", "siDatabricks", "siSnyk", "siTrivy",
  "siDatadog", "siNewrelic", "siSplunk", "siOpenvpn", "siWireguard",
  "siSwagger", "siGraphql", "siSqlite", "siMariadb", "siApachecassandra",
  "siClickhouse", "siTimescale", "siOracle", "siHeroku", "siDigitalocean",
  "siSonarqube", "siFlux", "siAmazonelasticache", "siAmazondocumentdb",
  "siAmazonrds", "siAmazonredshift", "siAmazons3", "siAmazoneks",
  "siAmazonecs", "siAwslambda", "siAmazonapigateway",
  "siAwselasticloadbalancing", "siAmazoncloudwatch", "siAwssecretsmanager",
  "siAmazoniam", "siAmazoncognito", "siAwsfargate",
  "siGooglebigquery", "siGooglecloudstorage", "siVictoriametrics",
  "siRubyonrails", "siRuby", "siPhp", "siApachepulsar",
  "siApacherocketmq", "siApacheflink", "siApache",
  "siElasticstack", "siKibana", "siLogstash", "siTraefikproxy",
] as const;

let preloadDone = false;

export function preloadSimpleIcons(): void {
  if (preloadDone) return;
  preloadDone = true;
  // Fire and forget — don't block rendering
  void (async () => {
    try {
      const mod = await import("simple-icons");
      for (const exportName of PRELOAD_SLUGS) {
        const icon = mod[exportName as keyof typeof mod];
        if (icon && typeof icon === "object" && "path" in icon && "title" in icon) {
          // Cache using slug (e.g., "postgresql") not export name (e.g., "siPostgresql")
          const slug = exportName.startsWith("si")
            ? exportName.slice(2).toLowerCase()
            : exportName.toLowerCase();
          simpleIconCache.set(slug, { title: icon.title, path: icon.path });
        }
      }
    } catch {
      // simple-icons not available at runtime
    }
  })();
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
