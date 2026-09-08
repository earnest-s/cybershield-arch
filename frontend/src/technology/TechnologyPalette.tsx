/**
 * TechnologyPalette
 *
 * Professional technology browser/palette for the design system.
 *
 * - Searchable
 * - Categorized (20 categories)
 * - Keyboard accessible
 * - Dark/light compatible (uses CSS variables)
 * - Scalable to hundreds of technologies (paged, not a wall of icons)
 * - Provider/category filtering
 * - Favorites/popular section
 *
 * This is a visualization/design-system capability only. It does NOT change
 * model generation or node/edge limits.
 */

import React, { useMemo, useState } from "react";
import { Search, X, ChevronDown, Star, Filter } from "lucide-react";
import { getTechnologyRegistry, getCategories } from "./registry";
import type { TechnologyMetadata, TechnologyCategory } from "./types";
import { TechnologyIcon } from "./TechnologyIcon";

export interface TechnologyPaletteProps {
  /** Optional: callback when a technology is selected (clicked) */
  onSelect?: (tech: TechnologyMetadata) => void;
  /** Initial category filter (optional) */
  initialCategory?: TechnologyCategory | "all";
  /** Optional: preferred/favorites technology IDs to show first */
  favorites?: string[];
  /** Optional: maximum items to render before collapsing a category */
  maxItemsPerCategory?: number;
  className?: string;
}

const POPULAR_IDS = [
  "postgresql",
  "redis",
  "kafka",
  "react",
  "nextdotjs",
  "kubernetes",
  "docker",
  "aws",
  "fastapi",
  "graphql",
  "prometheus",
  "nginx",
  "mongodb",
  "python",
];

export function TechnologyPalette({
  onSelect,
  initialCategory = "all",
  favorites = [],
  maxItemsPerCategory = 12,
  className,
}: TechnologyPaletteProps): React.ReactElement {
  const [query, setQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<TechnologyCategory | "all">(initialCategory);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const registry = getTechnologyRegistry();
  const allCategories = getCategories();

  // Popular / favorites
  const popularTechs = useMemo(() => {
    const ids = [...favorites, ...POPULAR_IDS];
    const seen = new Set<string>();
    const result: TechnologyMetadata[] = [];
    for (const id of ids) {
      if (seen.has(id)) continue;
      const tech = registry.get(id);
      if (tech) {
        seen.add(id);
        result.push(tech);
      }
    }
    return result;
  }, [favorites, registry]);

  // Filtered search results
  const searchResults = useMemo(() => {
    if (!query.trim()) return [];
    return registry.search(query.trim());
  }, [query, registry]);

  // Grouped result by category (when searching)
  const groupedByCategory = useMemo(() => {
    if (query.trim().length > 0) return null;
    // Group all by category when filtering by category
    let techs = registry.getAll();
    if (categoryFilter !== "all") {
      techs = registry.getByCategory(categoryFilter);
    }
    const groups = new Map<TechnologyCategory, TechnologyMetadata[]>();
    for (const tech of techs) {
      let cat = tech.category;
      // Assign provider-specific categories for filtering display
      if (tech.provider === "aws" && cat === "cloud") cat = "aws";
      if (tech.provider === "azure" && cat === "cloud") cat = "azure";
      if (tech.provider === "gcp" && cat === "cloud") cat = "gcp";
      const arr = groups.get(cat) || [];
      arr.push(tech);
      groups.set(cat, arr);
    }
    return groups;
  }, [query, categoryFilter, registry]);

  // Determine whether we're in search mode
  const isSearching = query.trim().length > 0;

  const toggleCategory = (id: string) => {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const providerFilterOptions = useMemo(() => {
    const providers = new Set<string>();
    for (const tech of registry.getAll()) {
      if (tech.provider) providers.add(tech.provider);
    }
    return Array.from(providers).sort();
  }, [registry]);

  return (
    <div className="tech-palette">
      {/* Search */}
      <div className="tech-palette__search">
        <Search size={14} className="tech-palette__search-icon" />
        <input
          type="text"
          placeholder="Search technologies..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Escape") setQuery("");
          }}
          aria-label="Search technologies"
          className="tech-palette__search-input"
        />
        {query && (
          <button
            className="tech-palette__clear"
            onClick={() => setQuery("")}
            aria-label="Clear search"
          >
            <X size={12} />
          </button>
        )}
      </div>

      {/* Category filter */}
      <div className="tech-palette__filters">
        <Filter size={13} className="tech-palette__filter-icon" />
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value as TechnologyCategory | "all")}
          className="tech-palette__select"
          aria-label="Filter by category"
        >
          <option value="all">All Categories</option>
          {allCategories.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.label} ({cat.count})
            </option>
          ))}
        </select>
      </div>

      {/* Content */}
      <div className="tech-palette__body">
        {isSearching ? (
          <div className="tech-palette__search-results">
            <div className="tech-palette__group-header">Search Results ({searchResults.length})</div>
            {searchResults.length === 0 ? (
              <div className="tech-palette__empty">No technologies found for "{query}"</div>
            ) : (
              <div className="tech-palette__grid">
                {searchResults.map((tech) => (
                  <button
                    key={tech.id}
                    className="tech-palette__item"
                    onClick={() => onSelect?.(tech)}
                    tabIndex={0}
                    title={tech.description}
                  >
                    <TechnologyIcon technologyId={tech.id} size={18} />
                    <span className="tech-palette__item-name">{tech.name}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : (
          <>
            {/* Popular / Favorites */}
            {categoryFilter === "all" && popularTechs.length > 0 && (
              <div className="tech-palette__group">
                <div className="tech-palette__group-header">
                  <Star size={12} /> Popular
                </div>
                <div className="tech-palette__grid">
                  {popularTechs.map((tech) => (
                    <button
                      key={tech.id}
                      className="tech-palette__item"
                      onClick={() => onSelect?.(tech)}
                      tabIndex={0}
                      title={tech.description}
                    >
                      <TechnologyIcon technologyId={tech.id} size={18} />
                      <span className="tech-palette__item-name">{tech.name}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Categories */}
            {groupedByCategory && Array.from(groupedByCategory.entries()).map(([catId, techs]) => {
              const info = allCategories.find((c) => c.id === catId);
              if (!info) return null;
              const isOpen = expanded[catId] ?? techs.length <= maxItemsPerCategory;
              const visible = isOpen ? techs : techs.slice(0, maxItemsPerCategory);
              return (
                <div className="tech-palette__group" key={catId}>
                  <button
                    className="tech-palette__group-toggle"
                    onClick={() => toggleCategory(catId)}
                    aria-expanded={isOpen}
                  >
                    <span
                      className="tech-palette__group-dot"
                      style={{ backgroundColor: info.color }}
                    />
                    <span className="tech-palette__group-title">
                      {info.label} <span className="tech-palette__group-count">({techs.length})</span>
                    </span>
                    <ChevronDown
                      size={14}
                      className={`tech-palette__chevron ${isOpen ? "tech-palette__chevron--open" : ""}`}
                    />
                  </button>
                  {isOpen && (
                    <div className="tech-palette__grid">
                      {techs.map((tech) => (
                        <button
                          key={tech.id}
                          className="tech-palette__item"
                          onClick={() => onSelect?.(tech)}
                          tabIndex={0}
                          title={tech.description}
                        >
                          <TechnologyIcon technologyId={tech.id} size={18} />
                          <span className="tech-palette__item-name">{tech.name}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </>
        )}
      </div>
    </div>
  );
}

export default TechnologyPalette;
