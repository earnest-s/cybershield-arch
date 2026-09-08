/**
 * Protocol & Relationship Vocabulary
 *
 * Typed vocabulary of network protocols and connection relationships for
 * architecture edges. This is a *vocabulary / metadata* capability:
 * protocols are ONLY rendered against an edge when the actual edge metadata
 * declares them. Existing edges are never retro-fitted with fabricated
 * protocols.
 *
 * Future phases can use this vocabulary to style edges (dash patterns,
 * security/encryption indicators, badges) based on real metadata.
 */

import type { TechnologyProtocol } from "./types";

// ─── Protocol registry ──────────────────────────────────────────────────────

/**
 * All known protocols in the vocabulary.
 * `id` is the canonical internal identifier; `name` is the display label.
 */
export const PROTOCOLS: TechnologyProtocol[] = [
  { id: "HTTP", name: "HTTP", defaultPort: 80, encryptedByDefault: false },
  { id: "HTTPS", name: "HTTPS", defaultPort: 443, encryptedByDefault: true },
  { id: "REST", name: "REST", defaultPort: 443, encryptedByDefault: false },
  { id: "graphql", name: "GraphQL", defaultPort: 443, encryptedByDefault: false },
  { id: "gRPC", name: "gRPC", defaultPort: 443, encryptedByDefault: false },
  { id: "WebSocket", name: "WebSocket", defaultPort: 443, encryptedByDefault: false },
  { id: "TCP", name: "TCP", encryptedByDefault: false },
  { id: "UDP", name: "UDP", encryptedByDefault: false },
  { id: "TLS", name: "TLS", defaultPort: 443, encryptedByDefault: true },
  { id: "OAuth", name: "OAuth", defaultPort: 443, encryptedByDefault: true },
  { id: "OIDC", name: "OIDC", defaultPort: 443, encryptedByDefault: true },
  { id: "Kafka", name: "Kafka", defaultPort: 9092, encryptedByDefault: false },
  { id: "AMQP", name: "AMQP", defaultPort: 5672, encryptedByDefault: false },
  { id: "SQS", name: "SQS", defaultPort: 443, encryptedByDefault: true },
  { id: "SNS", name: "SNS", defaultPort: 443, encryptedByDefault: true },
  { id: "SQL", name: "SQL", encryptedByDefault: false },
  { id: "JDBC", name: "JDBC", encryptedByDefault: false },
  { id: "DNS", name: "DNS", defaultPort: 53, encryptedByDefault: false },
  { id: "SSH", name: "SSH", defaultPort: 22, encryptedByDefault: true },
  { id: "MongoDB", name: "MongoDB", defaultPort: 27017, encryptedByDefault: false },
  { id: "Redis", name: "Redis", defaultPort: 6379, encryptedByDefault: false },
  { id: "CQL", name: "CQL", defaultPort: 9042, encryptedByDefault: false },
];

const PROTOCOL_MAP: Map<string, TechnologyProtocol> = new Map(
  PROTOCOLS.map((p) => [p.id.toLowerCase(), p])
);

/**
 * Looks up a protocol by ID (case-insensitive).
 * Accepts common aliases (e.g. "graphql" → GraphQL).
 */
export function getProtocol(id: string): TechnologyProtocol | undefined {
  const key = id.toLowerCase();
  return PROTOCOL_MAP.get(key);
}

/**
 * Normalize a raw protocol string to a canonical protocol ID.
 * Returns undefined if no match (unknown protocols are not fabricated).
 */
export function normalizeProtocol(raw: string | null | undefined): string | undefined {
  if (!raw) return undefined;
  const trimmed = raw.trim();
  if (!trimmed) return undefined;
  const proto = getProtocol(trimmed);
  return proto?.id;
}

// ─── Relationship vocabulary ────────────────────────────────────────────────

export type RelationshipType =
  | "sync"
  | "async"
  | "event"
  | "replication"
  | "auth"
  | "data-flow"
  | "dns"
  | "unknown";

export interface RelationshipInfo {
  id: RelationshipType;
  label: string;
  /** Whether this relationship is asynchronous by nature */
  asynchronous?: boolean;
  description: string;
}

export const RELATIONSHIPS: RelationshipInfo[] = [
  { id: "sync", label: "Synchronous", asynchronous: false, description: "Direct request/response call" },
  { id: "async", label: "Asynchronous", asynchronous: true, description: "Non-blocking call" },
  { id: "event", label: "Event", asynchronous: true, description: "Event-driven communication" },
  { id: "replication", label: "Replication", asynchronous: true, description: "Data replication" },
  { id: "auth", label: "Auth", asynchronous: false, description: "Authentication/authorization" },
  { id: "data-flow", label: "Data Flow", asynchronous: false, description: "Data transfer" },
  { id: "dns", label: "DNS", asynchronous: false, description: "Domain name resolution" },
  { id: "unknown", label: "Unknown", asynchronous: false, description: "Relationship type not specified" },
];

const RELATIONSHIP_MAP: Map<string, RelationshipInfo> = new Map(
  RELATIONSHIPS.map((r) => [r.id.toLowerCase(), r])
);

export function getRelationship(id: string): RelationshipInfo | undefined {
  return RELATIONSHIP_MAP.get(id.toLowerCase());
}

// ─── Security semantics (rendered only from real metadata) ─────────────────

export type EncryptionStatus = "encrypted" | "unencrypted" | "mutual-tls" | "unknown";
export type AuthenticationMechanism = "mtls" | "oauth" | "api-key" | "none" | "unknown";

/**
 * Determines if a protocol implies encryption *by default* per its spec.
 * This is a static property of the protocol, not a fabrication about an edge.
 */
export function protocolEncryptedByDefault(id: string): boolean {
  return getProtocol(id)?.encryptedByDefault ?? false;
}
