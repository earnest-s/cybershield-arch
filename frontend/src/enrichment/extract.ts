/**
 * Semantic Enrichment Layer — Deterministic Technology Extraction
 *
 * Detects technologies explicitly mentioned in the requirement text using ONLY
 * the Technology Registry as vocabulary (labels, aliases, provider compounds).
 * It is deterministic: same text → same results. It never invents identities.
 *
 * Rules:
 * - Word tokens scanned with windows of 3 → 2 → 1 (longest match wins).
 * - Generic-category role technologies ("Database", "Queue", "User", ...) are
 *   excluded from detection — they carry no identity, so they are never
 *   "detected" and never reported.
 * - Adjacent generic qualifier words ("db", "frontend", "cluster", ...) fold
 *   into the mention span, e.g. "postgres database" → PostgreSQL.
 * - Hedge/suggestion language ("compatible with", "such as", "like", "e.g.")
 *   immediately adjacent to a mention downgrades it to `confidence: "possible"`
 *   and marks `hedged`, so binding never auto-claims it.
 * - Two different technologies claiming the same span produce a conflict.
 */

import type { TechnologyMetadata, TechnologyCategory } from "../technology/types";
import { getTechnologyRegistry, TechnologyRegistry } from "../technology/registry";
import type { DetectedTechnology, EnrichmentConflict, TextPosition } from "./types";

const MAX_WINDOW = 3;

/**
 * Generic qualifier words that may follow/precede a recognized brand and fold
 * into the mention span (mirrors registry.matchCompositeLabel vocabulary).
 * Kept in one place to avoid a second catalog.
 */
export const GENERIC_QUALIFIERS = new Set([
  "db", "database", "databases", "service", "services", "server", "servers",
  "cache", "caching", "cluster", "clusters", "instance", "instances",
  "runtime", "engine", "broker", "gw", "gateway", "api", "queue", "queues",
  "node", "nodes", "component", "components", "app", "web",
  "store", "storage", "message", "messaging", "stream", "streaming",
  "frontend", "backend", "middleware", "layer", "storefront",
  "monolith", "service1", "service2", "v1", "v2",
]);

/**
 * Hedge / suggestion markers. A mention immediately preceded or followed by one
 * of these is treated as "suggested, not committed" — it becomes visible but is
 * never automatically bound.
 */
export const HEDGE_PHRASES = [
  "compatible with",
  "compatible",
  "similar to",
  "similar",
  "same as",
  "based on",
  "inspired by",
  "such as",
  "for example",
  "e.g.",
  "e.g",
  "eg",
  "like",
  "analogous to",
  "equivalent to",
  "interchangeable with",
  "drop-in for",
  "drop in for",
  "or similar",
];

interface Token {
  word: string;
  start: number;
  end: number;
}

interface Mention {
  technologyId: string;
  tech: TechnologyMetadata;
  start: number;
  end: number;
  tokensStart: number;
  tokensEnd: number;
}

/** Normalize a phrase for indexing / comparison. */
export function normalizePhrase(phrase: string): string {
  return phrase
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim()
    .replace(/\s+/g, " ");
}

/** Split text into alphanumeric word tokens with character offsets. */
export function tokenize(text: string): Token[] {
  const tokens: Token[] = [];
  const re = /[a-z0-9]+/gi;
  let match: RegExpExecArray | null;
  while ((match = re.exec(text)) !== null) {
    tokens.push({ word: match[0].toLowerCase(), start: match.index, end: match.index + match[0].length });
  }
  return tokens;
}

/**
 * Build the phrase index from the registry.
 *
 * Entries:
 *   - every tech's primary label,
 *   - every alias,
 *   - provider compounds, generated data-driven: for each provider short-name
 *     (the provider tech's label + aliases) × each child name (label + aliases),
 *     e.g. "aws s3" → amazons3. Pure derivation from registry data.
 *
 * Generic-category technologies are excluded: they carry no identity.
 */
function buildPhraseIndex(
  techs: TechnologyMetadata[],
  get: (id: string) => TechnologyMetadata | undefined
): Map<string, Set<string>> {
  const index = new Map<string, Set<string>>();
  const add = (phrase: string, technologyId: string) => {
    const norm = normalizePhrase(phrase);
    if (!norm) return;
    let set = index.get(norm);
    if (!set) {
      set = new Set();
      index.set(norm, set);
    }
    set.add(technologyId);
  };

  for (const tech of techs) {
    if (tech.category === "generic") continue;

    add(tech.name, tech.id);
    for (const alias of tech.aliases) add(alias, tech.id);

    if (tech.provider) {
      const providerTech = get(tech.provider);
      const providerNames = providerTech ? [providerTech.name, ...providerTech.aliases] : [tech.provider];
      const childNames = [tech.name, ...tech.aliases];
      for (const providerName of providerNames) {
        for (const childName of childNames) {
          add(`${providerName} ${childName}`, tech.id);
        }
      }
    }
  }

  return index;
}

/** Compute token-index ranges covered by hedge phrases in the text. */
function findHedgeRanges(tokens: Token[]): Array<[number, number]> {
  const hedgeTokenArrays = HEDGE_PHRASES.map((phrase) => normalizePhrase(phrase).split(" ").filter(Boolean));
  const ranges: Array<[number, number]> = [];
  for (const words of hedgeTokenArrays) {
    if (words.length === 0) continue;
    for (let i = 0; i + words.length <= tokens.length; i++) {
      let matches = true;
      for (let k = 0; k < words.length; k++) {
        if (tokens[i + k].word !== words[k]) {
          matches = false;
          break;
        }
      }
      if (matches) ranges.push([i, i + words.length]);
    }
  }
  return ranges;
}

/**
 * Detect technologies explicitly mentioned in the requirement text.
 */
export function detectTechnologies(
  requirement: string,
  registry?: TechnologyRegistry
): { detected: DetectedTechnology[]; conflicts: EnrichmentConflict[] } {
  const reg = registry ?? getTechnologyRegistry();
  const techs = reg.getAll();
  const index = buildPhraseIndex(techs, (id: string) => reg.get(id));
  const tokens = tokenize(requirement);
  if (tokens.length === 0) {
    return { detected: [], conflicts: [] };
  }

  const hedgeRanges = findHedgeRanges(tokens);
  const isHedged = (tokensStart: number, tokensEnd: number): boolean =>
    hedgeRanges.some(([a, b]) => b === tokensStart || a === tokensEnd);

  const mentions: Mention[] = [];
  const consumed = new Set<number>();

  for (let len = MAX_WINDOW; len >= 1; len--) {
    for (let i = 0; i + len <= tokens.length; i++) {
      const windowTokens = tokens.slice(i, i + len);
      if (windowTokens.some((_, offset) => consumed.has(i + offset))) continue;

      const phrase = windowTokens.map((token) => token.word).join(" ");
      const ids = index.get(normalizePhrase(phrase));
      if (!ids || ids.size === 0) continue;

      // Role folding: extend left/right over adjacent generic qualifier tokens.
      let s = i;
      let e = i + len;
      while (s > 0 && GENERIC_QUALIFIERS.has(tokens[s - 1].word) && !consumed.has(s - 1)) s--;
      while (e < tokens.length && GENERIC_QUALIFIERS.has(tokens[e].word) && !consumed.has(e)) e++;

      for (let t = s; t < e; t++) consumed.add(t);

      const start = tokens[s].start;
      const end = tokens[e - 1].end;
      for (const technologyId of ids) {
        const tech = reg.get(technologyId);
        if (!tech) continue;
        mentions.push({ technologyId, tech, start, end, tokensStart: s, tokensEnd: e });
      }
    }
  }

  // Conflicts: two+ distinct technologies claiming the same span.
  const conflicts: EnrichmentConflict[] = [];
  const bySpan = new Map<string, Mention[]>();
  for (const mention of mentions) {
    const key = `${mention.start}:${mention.end}`;
    const list = bySpan.get(key) ?? [];
    list.push(mention);
    bySpan.set(key, list);
  }
  for (const [, list] of bySpan) {
    const ids = Array.from(new Set(list.map((m) => m.technologyId)));
    if (ids.length > 1) {
      conflicts.push({ span: { start: list[0].start, end: list[0].end }, technologyIds: ids, reason: "overlapping-span" });
    }
  }

  // Group by technology, preserving mention order.
  const mentionsByTech = new Map<string, Mention[]>();
  for (const mention of mentions) {
    const list = mentionsByTech.get(mention.technologyId) ?? [];
    list.push(mention);
    mentionsByTech.set(mention.technologyId, list);
  }

  const detected: DetectedTechnology[] = [];
  for (const [technologyId, list] of mentionsByTech) {
    const tech = list[0].tech;
    const hedged = list.some((m) => isHedged(m.tokensStart, m.tokensEnd));
    const snippets = list.map((m) => requirement.slice(m.start, m.end).trim());
    const positions: TextPosition[] = list.map((m) => ({ start: m.start, end: m.end }));
    detected.push({
      technologyId,
      technologyName: tech.name,
      source: list.some((m) => normalizePhrase(m.tech.name) === normalizePhrase(requirement.slice(m.start, m.end)))
        ? "explicit-user"
        : "deterministic-match",
      confidence: hedged ? "possible" : "confirmed",
      hedged,
      mentions: snippets,
      positions,
      category: tech.category as TechnologyCategory,
      c4Classification: tech.c4Classification,
      provider: tech.provider,
      protocols: tech.protocols,
    });
  }

  detected.sort((a, b) => (a.positions[0]?.start ?? 0) - (b.positions[0]?.start ?? 0));
  return { detected, conflicts };
}