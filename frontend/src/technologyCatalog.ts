/**
 * Centralized Technology Catalog for CyberShield-Arch
 *
 * Single source of truth for technology metadata, icons, and categorization.
 * Extensible without modifying diagram rendering code.
 */

export type TechnologyCategory =
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

export interface Technology {
  /** Unique identifier for the technology */
  id: string;
  /** Human-readable display name */
  name: string;
  /** Category for grouping and filtering */
  category: TechnologyCategory;
  /** Icon identifier (matches simple-icons or lucide-react names) */
  icon: string;
  /** Optional: cloud provider this technology belongs to */
  provider?: "aws" | "azure" | "gcp" | "cloudflare" | "oracle" | "on-premise" | "multi-cloud";
  /** Optional: alternative names/aliases for matching */
  aliases?: string[];
  /** Optional: description */
  description?: string;
  /** Optional: whether this is a managed service */
  managed?: boolean;
  /** Optional: related technologies */
  related?: string[];
}

export interface TechnologyGroup {
  id: string;
  name: string;
  category: TechnologyCategory;
  technologies: Technology[];
}

/**
 * Comprehensive technology catalog organized by category
 */
export const TECHNOLOGY_CATALOG: Technology[] = [
  // APPLICATION
  { id: "web-ui", name: "Web UI", category: "application", icon: "monitor", aliases: ["frontend", "web-app", "spa", "dashboard"] },
  { id: "mobile-app", name: "Mobile App", category: "application", icon: "smartphone", aliases: ["ios", "android", "mobile"] },
  { id: "api-gateway", name: "API Gateway", category: "application", icon: "apigateway", aliases: ["gateway", "api-gw"] },
  { id: "bff", name: "BFF (Backend for Frontend)", category: "application", icon: "server", aliases: ["backend-for-frontend"] },
  { id: "rest-api", name: "REST API", category: "application", icon: "rest", aliases: ["rest", "api", "http-api"] },
  { id: "graphql", name: "GraphQL", category: "application", icon: "graphql", aliases: ["gql"] },
  { id: "grpc", name: "gRPC", category: "application", icon: "grpc", aliases: ["grpc-service"] },

  // COMPUTE
  { id: "service", name: "Service", category: "compute", icon: "server", aliases: ["microservice", "backend-service", "api-service"] },
  { id: "microservice", name: "Microservice", category: "compute", icon: "server", aliases: ["micro-service"] },
  { id: "worker", name: "Worker", category: "compute", icon: "cpu", aliases: ["background-worker", "job-processor", "consumer"] },
  { id: "container", name: "Container", category: "compute", icon: "docker", aliases: ["docker-container"] },
  { id: "vm", name: "Virtual Machine", category: "compute", icon: "server", aliases: ["ec2", "vm-instance", "compute-instance"] },
  { id: "serverless-function", name: "Serverless Function", category: "compute", icon: "lambda", aliases: ["function", "faas", "cloud-function"] },
  { id: "k8s-pod", name: "Kubernetes Pod", category: "compute", icon: "kubernetes", aliases: ["pod", "k8s-pod"] },
  { id: "k8s-deployment", name: "Kubernetes Deployment", category: "compute", icon: "kubernetes", aliases: ["deployment", "k8s-deployment"] },

  // DATABASE
  { id: "postgresql", name: "PostgreSQL", category: "database", icon: "postgresql", aliases: ["postgres", "psql"], provider: "multi-cloud" },
  { id: "mysql", name: "MySQL", category: "database", icon: "mysql", aliases: ["mariadb"], provider: "multi-cloud" },
  { id: "mongodb", name: "MongoDB", category: "database", icon: "mongodb", aliases: ["mongo", "document-db"], provider: "multi-cloud" },
  { id: "redis", name: "Redis", category: "database", icon: "redis", aliases: ["cache", "redis-cache"], provider: "multi-cloud" },
  { id: "dynamodb", name: "DynamoDB", category: "database", icon: "dynamodb", aliases: ["dynamo"], provider: "aws" },
  { id: "cassandra", name: "Cassandra", category: "database", icon: "cassandra", aliases: ["scylla"], provider: "multi-cloud" },
  { id: "elasticsearch", name: "Elasticsearch", category: "database", icon: "elasticsearch", aliases: ["es", "elastic"], provider: "multi-cloud" },
  { id: "opensearch", name: "OpenSearch", category: "database", icon: "opensearch", provider: "multi-cloud" },
  { id: "s3", name: "S3 / Object Storage", category: "database", icon: "amazons3", aliases: ["object-storage", "blob-storage", "minio"], provider: "aws" },
  { id: "data-warehouse", name: "Data Warehouse", category: "database", icon: "snowflake", aliases: ["warehouse", "redshift", "bigquery", "synapse"], provider: "multi-cloud" },
  { id: "data-lake", name: "Data Lake", category: "database", icon: "databricks", aliases: ["lake", "delta-lake"], provider: "multi-cloud" },

  // MESSAGING
  { id: "kafka", name: "Apache Kafka", category: "messaging", icon: "apachekafka", aliases: ["kafka", "event-stream", "message-broker"], provider: "multi-cloud" },
  { id: "rabbitmq", name: "RabbitMQ", category: "messaging", icon: "rabbitmq", aliases: ["amqp", "message-queue"], provider: "multi-cloud" },
  { id: "sqs", name: "Amazon SQS", category: "messaging", icon: "amazonsqs", aliases: ["sqs", "simple-queue"], provider: "aws" },
  { id: "sns", name: "Amazon SNS", category: "messaging", icon: "amazonsns", aliases: ["sns", "pubsub", "notification"], provider: "aws" },
  { id: "pubsub", name: "Google Pub/Sub", category: "messaging", icon: "googlecloud", aliases: ["pub-sub", "gcp-pubsub"], provider: "gcp" },
  { id: "service-bus", name: "Azure Service Bus", category: "messaging", icon: "microsoftazure", aliases: ["servicebus", "azure-sb"], provider: "azure" },
  { id: "eventbridge", name: "EventBridge", category: "messaging", icon: "amazoneventbridge", aliases: ["event-bus", "eventbridge"], provider: "aws" },
  { id: "event-bus", name: "Event Bus", category: "messaging", icon: "eventbus", aliases: ["eventbus"] },
  { id: "stream", name: "Stream Processing", category: "messaging", icon: "apacheflink", aliases: ["flink", "ksql", "stream-processing"] },

  // NETWORK
  { id: "load-balancer", name: "Load Balancer", category: "network", icon: "loadbalancer", aliases: ["lb", "alb", "nlb", "elb"], provider: "multi-cloud" },
  { id: "reverse-proxy", name: "Reverse Proxy", category: "network", icon: "nginx", aliases: ["proxy", "nginx", "traefik", "haproxy"] },
  { id: "cdn", name: "CDN", category: "network", icon: "cloudflare", aliases: ["content-delivery", "cloudfront", "cloudflare-cdn"], provider: "multi-cloud" },
  { id: "waf", name: "WAF", category: "network", icon: "shield", aliases: ["web-application-firewall", "firewall"], provider: "multi-cloud" },
  { id: "firewall", name: "Firewall", category: "network", icon: "firewall", aliases: ["network-firewall", "security-group"], provider: "multi-cloud" },
  { id: "vpc", name: "VPC / VNet", category: "network", icon: "vpc", aliases: ["vpc", "vnet", "virtual-network", "private-network"], provider: "multi-cloud" },
  { id: "subnet", name: "Subnet", category: "network", icon: "subnet", aliases: ["sub-network"], provider: "multi-cloud" },
  { id: "nat-gateway", name: "NAT Gateway", category: "network", icon: "natgateway", aliases: ["nat", "nat-gw"], provider: "multi-cloud" },
  { id: "vpn", name: "VPN", category: "network", icon: "vpn", aliases: ["virtual-private-network", "site-to-site"], provider: "multi-cloud" },
  { id: "internet-gateway", name: "Internet Gateway", category: "network", icon: "internetgateway", aliases: ["igw", "internet-gw"], provider: "multi-cloud" },

  // SECURITY
  { id: "iam", name: "IAM", category: "security", icon: "iam", aliases: ["identity-access-management", "identity"], provider: "multi-cloud" },
  { id: "oauth-oidc", name: "OAuth / OIDC", category: "security", icon: "oauth", aliases: ["oauth2", "openid-connect", "oidc", "sso"] },
  { id: "identity-provider", name: "Identity Provider", category: "security", icon: "auth0", aliases: ["idp", "keycloak", "okta", "auth0", "cognito"] },
  { id: "rbac", name: "RBAC", category: "security", icon: "rbac", aliases: ["role-based-access-control", "authorization"] },
  { id: "secrets-manager", name: "Secrets Manager", category: "security", icon: "secretsmanager", aliases: ["secrets", "vault", "parameter-store"], provider: "multi-cloud" },
  { id: "kms", name: "KMS / Key Management", category: "security", icon: "kms", aliases: ["key-management", "encryption-keys"], provider: "multi-cloud" },
  { id: "certificate-authority", name: "Certificate Authority", category: "security", icon: "letsencrypt", aliases: ["ca", "pki", "tls-certificates"], provider: "multi-cloud" },
  { id: "encryption-boundary", name: "Encryption Boundary", category: "security", icon: "lock", aliases: ["encryption", "encrypted-zone"] },

  // OBSERVABILITY
  { id: "prometheus", name: "Prometheus", category: "observability", icon: "prometheus", aliases: ["metrics", "monitoring"] },
  { id: "grafana", name: "Grafana", category: "observability", icon: "grafana", aliases: ["dashboards", "visualization"] },
  { id: "opentelemetry", name: "OpenTelemetry", category: "observability", icon: "opentelemetry", aliases: ["otel", "tracing", "instrumentation"] },
  { id: "jaeger", name: "Jaeger", category: "observability", icon: "jaeger", aliases: ["distributed-tracing", "tracing"] },
  { id: "elk", name: "ELK Stack", category: "observability", icon: "elasticsearch", aliases: ["elastic-stack", "logstash", "kibana"] },
  { id: "cloudwatch", name: "CloudWatch", category: "observability", icon: "amazoncloudwatch", aliases: ["cw", "aws-monitoring"], provider: "aws" },
  { id: "azure-monitor", name: "Azure Monitor", category: "observability", icon: "microsoftazure", aliases: ["monitor", "azure-monitoring"], provider: "azure" },
  { id: "gcp-monitoring", name: "Google Cloud Monitoring", category: "observability", icon: "googlecloud", aliases: ["stackdriver", "gcp-monitoring"], provider: "gcp" },

  // CLOUD PROVIDERS
  { id: "aws", name: "AWS", category: "cloud-provider", icon: "amazonwebservices", provider: "aws" },
  { id: "azure", name: "Azure", category: "cloud-provider", icon: "microsoftazure", provider: "azure" },
  { id: "gcp", name: "Google Cloud", category: "cloud-provider", icon: "googlecloud", provider: "gcp" },
  { id: "oracle-cloud", name: "Oracle Cloud", category: "cloud-provider", icon: "oracle", provider: "oracle" },
  { id: "cloudflare", name: "Cloudflare", category: "cloud-provider", icon: "cloudflare", provider: "cloudflare" },

  // CONTAINER / KUBERNETES
  { id: "kubernetes", name: "Kubernetes", category: "container-kubernetes", icon: "kubernetes", aliases: ["k8s", "k3s", "eks", "aks", "gke"], provider: "multi-cloud" },
  { id: "eks", name: "Amazon EKS", category: "container-kubernetes", icon: "amazoneks", aliases: ["elastic-kubernetes"], provider: "aws" },
  { id: "aks", name: "Azure AKS", category: "container-kubernetes", icon: "azureaks", aliases: ["azure-kubernetes"], provider: "azure" },
  { id: "gke", name: "Google GKE", category: "container-kubernetes", icon: "googlecloud", aliases: ["gke", "google-kubernetes"], provider: "gcp" },
  { id: "docker", name: "Docker", category: "container-kubernetes", icon: "docker", aliases: ["containerd", "container-runtime"] },
  { id: "ecs", name: "Amazon ECS", category: "container-kubernetes", icon: "amazonecs", aliases: ["elastic-container-service"], provider: "aws" },
  { id: "fargate", name: "AWS Fargate", category: "container-kubernetes", icon: "awsfargate", aliases: ["serverless-containers"], provider: "aws" },
];

/**
 * Technology categories with display metadata
 */
export const TECHNOLOGY_CATEGORIES: Record<TechnologyCategory, { label: string; icon: string; color: string }> = {
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

/**
 * Lookup technology by ID
 */
export function getTechnology(id: string): Technology | undefined {
  return TECHNOLOGY_CATALOG.find((t) => t.id === id);
}

/**
 * Lookup technology by alias (case-insensitive)
 */
export function findTechnologyByAlias(alias: string): Technology | undefined {
  const normalized = alias.toLowerCase().trim();
  return TECHNOLOGY_CATALOG.find(
    (t) => t.id.toLowerCase() === normalized || t.aliases?.some((a) => a.toLowerCase() === normalized)
  );
}

/**
 * Get all technologies in a category
 */
export function getTechnologiesByCategory(category: TechnologyCategory): Technology[] {
  return TECHNOLOGY_CATALOG.filter((t) => t.category === category);
}

/**
 * Get technologies by provider
 */
export function getTechnologiesByProvider(provider: Technology["provider"]): Technology[] {
  return TECHNOLOGY_CATALOG.filter((t) => t.provider === provider);
}

/**
 * Infer technology from node ID and type (for backward compatibility with model output)
 * This is a best-effort heuristic when the model doesn't provide explicit technology
 */
export function inferTechnology(nodeId: string, nodeType: string): Technology | undefined {
  const normalizedId = nodeId.toLowerCase();

  // Check for technology keywords in the node ID
  for (const tech of TECHNOLOGY_CATALOG) {
    if (tech.aliases) {
      for (const alias of tech.aliases) {
        if (normalizedId.includes(alias.toLowerCase())) {
          return tech;
        }
      }
    }
    if (normalizedId.includes(tech.id.toLowerCase())) {
      return tech;
    }
  }

  // Fallback: infer from node type
  const typeInference: Record<string, string[]> = {
    ui: ["web-ui"],
    service: ["service"],
    database: ["postgresql"],
    cache: ["redis"],
    queue: ["kafka"],
    container: ["container"],
  };

  const inferredIds = typeInference[nodeType] || [];
  for (const inferredId of inferredIds) {
    const tech = getTechnology(inferredId);
    if (tech) return tech;
  }

  return undefined;
}

/**
 * Get display label for a node with technology awareness
 * Priority: explicit label > technology name > category default > canonical ID
 */
export function getDisplayLabel(
  nodeId: string,
  nodeType: string,
  explicitLabel?: string,
  technology?: Technology
): string {
  // 1. Explicit label from backend (highest priority)
  if (explicitLabel && explicitLabel.trim()) {
    return explicitLabel.trim();
  }

  // 2. Technology name if available
  if (technology) {
    return technology.name;
  }

  // 3. Infer technology from ID
  const inferred = inferTechnology(nodeId, nodeType);
  if (inferred) {
    return inferred.name;
  }

  // 4. Category default (e.g., "Service 1", "Database 2")
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
  if (match) {
    return `${categoryName} ${match[2]}`;
  }

  return nodeId;
}