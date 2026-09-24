/**
 * Semantic Enrichment Layer — Acceptance Tests
 *
 * Node-runner harness (no framework): bundle with esbuild and execute.
 *
 *   npx esbuild src/enrichment/acceptance.test.ts --bundle --platform=node \
 *     --format=esm --outfile=.tmp-enrichment-tests.mjs && node .tmp-enrichment-tests.mjs
 *
 * Throws on the first failure (non-zero exit). No @types/node dependency.
 */

import type { Architecture, ArchitectureNode } from "../types";
import { detectTechnologies } from "./extract";
import { bindTechnologies } from "./bind";
import { enrichArchitecture } from "./index";
import { getTechnologyRegistry } from "../technology/registry";

let passed = 0;
let failed = 0;

function assert(condition: boolean, message: string): void {
  if (condition) {
    passed += 1;
    return;
  }
  failed += 1;
  console.error(`FAIL: ${message}`);
  throw new Error(`Assertion failed: ${message}`);
}

function test(name: string, fn: () => void): void {
  try {
    fn();
    console.log(` PASS  ${name}`);
  } catch (error) {
    console.error(` FAIL  ${name} — ${(error as Error).message}`);
  }
}

function nodes(...pairs: Array<[string, string]>): ArchitectureNode[] {
  return pairs.map(([id, type]) => ({ id, type }));
}

function architecture(nodeList: [string, string][]): Architecture {
  return { nodes: nodes(...nodeList), edges: [] };
}

const registry = getTechnologyRegistry();

// ─── Detection tests ────────────────────────────────────────────────────────

test('detect: "postgres" → PostgreSQL', () => {
  const { detected } = detectTechnologies("Use postgres for the database.");
  const pg = detected.find((d) => d.technologyId === "postgresql");
  assert(!!pg, "postgresql should be detected");
  assert(pg!.technologyName === "PostgreSQL", "technologyName is PostgreSQL");
  assert(pg!.source === "deterministic-match", "alias match is deterministic-match");
  assert(pg!.confidence === "confirmed", "alias match is confirmed");
});

test('detect: "postgres database" → PostgreSQL (role folding)', () => {
  const { detected } = detectTechnologies("Store events in a postgres database.");
  const pg = detected.find((d) => d.technologyId === "postgresql");
  assert(!!pg, "postgresql should be detected");
  assert(pg!.mentions.some((m) => m.toLowerCase().includes("database")), "qualifier folded into mention");
});

test('detect: "s3" → Amazon S3', () => {
  const { detected } = detectTechnologies("Persist media to s3.");
  const s3 = detected.find((d) => d.technologyId === "amazons3");
  assert(!!s3, "amazons3 should be detected");
  assert(s3!.technologyName === "Amazon S3", "technologyName is Amazon S3");
});

test('detect: "aws s3" → Amazon S3 (provider compound)', () => {
  const { detected } = detectTechnologies("Store files in aws s3 buckets.");
  const s3 = detected.find((d) => d.technologyId === "amazons3");
  assert(!!s3, "amazons3 should be detected via provider compound");
  assert(s3!.technologyName === "Amazon S3", "technologyName is Amazon S3");
});

test('detect: "React frontend" → React (label + role folding)', () => {
  const { detected } = detectTechnologies("Build the React frontend with a SPA.");
  const react = detected.find((d) => d.technologyId === "react");
  assert(!!react, "react should be detected");
  assert(react!.source === "explicit-user", "canonical label is explicit-user");
  assert(react!.mentions.some((m) => m.toLowerCase().includes("frontend")), "frontend folded into mention");
});

test('detect: "MySQL or MariaDB" → ambiguous, no fabricated single claim', () => {
  const { detected, conflicts } = detectTechnologies("Use MySQL or MariaDB.");
  const mysql = detected.find((d) => d.technologyId === "mysql");
  const mariadb = detected.find((d) => d.technologyId === "mariadb");
  assert(!!mysql, "mysql detected");
  assert(!!mariadb, "mariadb detected");
  assert(conflicts.length > 0, "overlapping/coequal conflict recorded");
});

test('detect: "SQL database" → no technology detected', () => {
  const { detected } = detectTechnologies("A SQL database for reporting.");
  assert(detected.length === 0, "no technology should be detected for a generic SQL database");
});

test('detect: "database compatible with PostgreSQL" → hedged, not confirmed', () => {
  const { detected } = detectTechnologies("A database compatible with PostgreSQL.");
  const pg = detected.find((d) => d.technologyId === "postgresql");
  assert(!!pg, "postgresql mention is still visible");
  assert(pg!.hedged === true, "mention is hedged");
  assert(pg!.confidence === "possible", "hedged mention is possible, not confirmed");
});

test("detect: duplicate mentions collapse to one DetectedTechnology", () => {
  const { detected } = detectTechnologies("PostgreSQL powers A. PostgreSQL also powers B.");
  const pg = detected.filter((d) => d.technologyId === "postgresql");
  assert(pg.length === 1, "single DetectedTechnology");
  assert(pg[0].mentions.length === 2, "both mentions recorded");
  assert(pg[0].source === "explicit-user", "canonical label → explicit-user");
});

test("detect: unregistered terms never produce identities", () => {
  const { detected } = detectTechnologies("Use SuperDB and a MegaQueue to scale.");
  assert(detected.length === 0, "nothing fabricated for unknown jargon");
});

// ─── Binding tests ──────────────────────────────────────────────────────────

test("bind: single database node + single database tech → confirmed unique-cardinality", () => {
  const { detected } = detectTechnologies("Persist to Postgres.");
  const result = bindTechnologies(detected, nodes(["database-1", "database"]), {});
  const db = result.enrichedNodes.find((n) => n.nodeId === "database-1")!;
  assert(db.assignment?.technologyId === "postgresql", "database-1 bound to postgresql");
  assert(db.assignment?.basis === "unique-cardinality" && db.assignment?.confidence === "confirmed", "confirmed unique-cardinality");
  assert(result.unplaced.length === 0, "tech placed");
});

test("bind: technology mentioned but no compatible node → detected but unplaced", () => {
  const { detected } = detectTechnologies("Cache everything in Redis.");
  const result = bindTechnologies(detected, nodes(["service-1", "service"]), {});
  const cache = result.enrichedNodes.find((n) => n.nodeId === "service-1")!;
  assert(cache.assignment === null, "no cache node → no assignment");
  assert(result.unplaced.some((u) => u.technologyId === "redis"), "redis reported unplaced");
});

test("bind: multiple compatible service nodes → candidates, never arbitrary binding", () => {
  const { detected } = detectTechnologies("Backing services run FastAPI.");
  const result = bindTechnologies(detected, nodes(["service-1", "service"], ["service-2", "service"]), {});
  for (const node of result.enrichedNodes) {
    assert(node.assignment === null, `no auto-bind for ${node.nodeId}`);
    assert(node.candidates.some((c) => c.technology.technologyId === "fastapi"), `fastapi candidate on ${node.nodeId}`);
  }
  assert(result.unplaced.some((u) => u.technologyId === "fastapi"), "fastapi reported unplaced (candidate)");
});

test("bind: hedged mention is never automatically claimed", () => {
  const { detected } = detectTechnologies("A database compatible with PostgreSQL.");
  const result = bindTechnologies(detected, nodes(["database-1", "database"]), {});
  const db = result.enrichedNodes.find((n) => n.nodeId === "database-1")!;
  assert(db.assignment === null, "hedged postgresql not claimed");
  assert(result.unplaced.some((u) => u.technologyId === "postgresql"), "hedged mention still visible as unplaced");
});

test("bind: MySQL or MariaDB → ambiguous, no automatic assignment", () => {
  const { detected } = detectTechnologies("Use MySQL or MariaDB.");
  const result = bindTechnologies(detected, nodes(["database-1", "database"]), {});
  const db = result.enrichedNodes.find((n) => n.nodeId === "database-1")!;
  assert(db.assignment === null, "no automatic assignment on ambiguous conflict");
  assert(db.candidates.length === 2, "both competitors offered as manual candidates");
  assert(db.candidates.every((c) => c.confidence === "ambiguous"), "candidates marked ambiguous");
  assert(result.conflicts.length > 0, "conflict recorded");
});

test("bind: no assignment based solely on node order", () => {
  const { detected } = detectTechnologies("Use React, PostgreSQL and Redis.");
  const result = bindTechnologies(
    detected,
    nodes(["ui-1", "ui"], ["service-1", "service"], ["database-1", "database"], ["cache-1", "cache"]),
    {}
  );
  const byId = new Map(result.enrichedNodes.map((n) => [n.nodeId, n]));
  assert(byId.get("ui-1")!.assignment?.technologyId === "react", "ui-1 ← React");
  assert(byId.get("database-1")!.assignment?.technologyId === "postgresql", "database-1 ← PostgreSQL");
  assert(byId.get("cache-1")!.assignment?.technologyId === "redis", "cache-1 ← Redis");
  assert(["service-1"].every((id) => byId.get(id)!.assignment === null), "services stay generic");
});

test("bind: full example React + FastAPI + PostgreSQL + Redis", () => {
  const { detected } = detectTechnologies(
    "React frontend calling a FastAPI backend that persists orders to PostgreSQL and caches product listings in Redis."
  );
  const result = bindTechnologies(
    detected,
    nodes(
      ["ui-1", "ui"],
      ["service-1", "service"],
      ["service-2", "service"],
      ["service-3", "service"],
      ["database-1", "database"],
      ["cache-1", "cache"]
    ),
    {}
  );
  const byId = new Map(result.enrichedNodes.map((n) => [n.nodeId, n]));
  assert(byId.get("ui-1")!.assignment?.technologyId === "react", "ui-1 ← React");
  assert(byId.get("database-1")!.assignment?.technologyId === "postgresql", "database-1 ← PostgreSQL");
  assert(byId.get("cache-1")!.assignment?.technologyId === "redis", "cache-1 ← Redis");
  for (const id of ["service-1", "service-2", "service-3"]) {
    assert(byId.get(id)!.assignment === null, `${id} stays generic`);
    assert(byId.get(id)!.candidates.some((c) => c.technology.technologyId === "fastapi"), `fastapi candidate on ${id}`);
  }
  assert(result.unplaced.some((u) => u.technologyId === "fastapi"), "fastapi unplaced");
});

test("bind: manual assignment wins and overrides auto-bind", () => {
  const { detected } = detectTechnologies("Persist to Postgres.");
  const result = bindTechnologies(detected, nodes(["database-1", "database"]), {
    "database-1": { technologyId: "mongodb", technologyName: "MongoDB" },
  });
  const db = result.enrichedNodes.find((n) => n.nodeId === "database-1")!;
  assert(db.assignment?.technologyId === "mongodb", "manual assignment wins");
  assert(db.assignment?.source === "manual-user" && db.assignment?.basis === "manual-pick", "manual provenance");
  assert(db.overriddenByManual === true, "auto-bind marked overridden");
});

test("bind: manual assignment clears via missing entry (reset)", () => {
  const { detected } = detectTechnologies("Persist to Postgres.");
  const manual: Record<string, { technologyId: string; technologyName: string }> = {};
  const result = bindTechnologies(detected, nodes(["database-1", "database"]), manual);
  const db = result.enrichedNodes.find((n) => n.nodeId === "database-1")!;
  assert(db.assignment?.technologyId === "postgresql", "postgresql restored after reset");
});

// ─── Facade invariants ───────────────────────────────────────────────────────

test("facade: no fabricated nodes — enriched count equals generated count", () => {
  const arch = architecture([["service-1", "service"], ["database-1", "database"]]);
  const enriched = enrichArchitecture("Use PostgreSQL.", arch);
  assert(enriched.enrichedNodes.length === 2, "same node count");
  for (const en of enriched.enrichedNodes) {
    assert(arch.nodes.some((n) => n.id === en.nodeId), "each enriched node exists in generated graph");
  }
});

test("facade: no fabricated technology identities — every assignment is registered", () => {
  const arch = architecture([["database-1", "database"], ["cache-1", "cache"]]);
  const enriched = enrichArchitecture("Use PostgreSQL and Redis.", arch);
  for (const en of enriched.enrichedNodes) {
    if (en.assignment) {
      assert(!!registry.get(en.assignment.technologyId), `registered technology: ${en.assignment.technologyId}`);
      assert(en.label === en.assignment.technologyName, "enriched label uses registry name");
    }
  }
});

test("facade: security independence — enrichment never touches security", () => {
  const arch = { nodes: nodes(["database-1", "database"]), edges: [] };
  const enriched = enrichArchitecture("Use PostgreSQL.", arch);
  assert(!("security" in enriched), "enrichment result has no security surface");
  assert(JSON.stringify(enriched.enrichedNodes[0].raw) === JSON.stringify(arch.nodes[0]), "raw node unchanged");
});

test("facade: generic node ids reported and label stays honest", () => {
  const arch = architecture([["service-1", "service"]]);
  const enriched = enrichArchitecture("Backend uses FastAPI.", arch);
  assert(enriched.genericNodeIds.includes("service-1"), "service-1 listed as generic");
  assert(enriched.enrichedNodes[0].label === "Service 1", "label stays generic " + enriched.enrichedNodes[0].label);
});

// ─── Summary ─────────────────────────────────────────────────────────────────

console.log(`\n${passed} assertions passed, ${failed} failed.`);
if (failed > 0) {
  console.error("ENRICHMENT TESTS FAILED");
  throw new Error("Enrichment acceptance tests failed");
}
console.log("ALL ENRICHMENT TESTS PASSED");