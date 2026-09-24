// src/technology/data.ts
var cloudProviders = [
  {
    id: "aws",
    name: "AWS",
    aliases: ["amazon", "amazon-web-services"],
    category: "cloud",
    provider: "aws",
    c4Classification: "infrastructure",
    icon: { id: "amazonwebservices", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://aws.amazon.com",
    description: "Amazon Web Services"
  },
  {
    id: "azure",
    name: "Azure",
    aliases: ["microsoft-azure"],
    category: "cloud",
    provider: "azure",
    c4Classification: "infrastructure",
    icon: { id: "cloud", source: "lucide" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://azure.microsoft.com",
    description: "Microsoft Azure"
  },
  {
    id: "gcp",
    name: "Google Cloud",
    aliases: ["google-cloud-platform", "gcloud"],
    category: "cloud",
    provider: "gcp",
    c4Classification: "infrastructure",
    icon: { id: "googlecloud", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://cloud.google.com",
    description: "Google Cloud Platform"
  },
  {
    id: "cloudflare",
    name: "Cloudflare",
    aliases: ["cf"],
    category: "cloud",
    provider: "cloudflare",
    c4Classification: "infrastructure",
    icon: { id: "cloudflare", source: "simple-icons" },
    protocols: ["HTTPS", "HTTP", "DNS"],
    managed: true,
    website: "https://www.cloudflare.com",
    description: "Cloudflare edge and security platform"
  },
  {
    id: "digitalocean",
    name: "DigitalOcean",
    aliases: ["do"],
    category: "cloud",
    provider: "digitalocean",
    c4Classification: "infrastructure",
    icon: { id: "digitalocean", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://www.digitalocean.com",
    description: "DigitalOcean cloud infrastructure"
  },
  {
    id: "heroku",
    name: "Heroku",
    aliases: [],
    category: "cloud",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "heroku", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://www.heroku.com",
    description: "Heroku platform as a service"
  },
  {
    id: "oracle",
    name: "Oracle Cloud",
    aliases: ["oci", "oracle-cloud"],
    category: "cloud",
    provider: "oracle",
    c4Classification: "infrastructure",
    icon: { id: "oracle", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://www.oracle.com/cloud",
    description: "Oracle Cloud Infrastructure"
  }
];
var awsServices = [
  {
    id: "amazoneks",
    name: "Amazon EKS",
    aliases: ["eks", "elastic-kubernetes-service"],
    category: "aws",
    provider: "aws",
    c4Classification: "infrastructure",
    icon: { id: "amazoneks", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://aws.amazon.com/eks",
    description: "Amazon Elastic Kubernetes Service"
  },
  {
    id: "amazonecs",
    name: "Amazon ECS",
    aliases: ["ecs", "elastic-container-service"],
    category: "aws",
    provider: "aws",
    c4Classification: "infrastructure",
    icon: { id: "amazonecs", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://aws.amazon.com/ecs",
    description: "Amazon Elastic Container Service"
  },
  {
    id: "awslambda",
    name: "AWS Lambda",
    aliases: ["lambda", "faas", "serverless-function"],
    category: "aws",
    provider: "aws",
    c4Classification: "component",
    icon: { id: "awslambda", source: "simple-icons" },
    protocols: ["HTTPS", "EventBridge"],
    managed: true,
    website: "https://aws.amazon.com/lambda",
    description: "AWS serverless compute"
  },
  {
    id: "amazons3",
    name: "Amazon S3",
    aliases: ["s3", "object-storage"],
    category: "aws",
    provider: "aws",
    c4Classification: "database",
    icon: { id: "amazons3", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://aws.amazon.com/s3",
    description: "Amazon Simple Storage Service"
  },
  {
    id: "amazonrds",
    name: "Amazon RDS",
    aliases: ["rds", "relational-database-service"],
    category: "aws",
    provider: "aws",
    c4Classification: "database",
    icon: { id: "amazonrds", source: "simple-icons" },
    protocols: ["HTTPS", "SQL"],
    managed: true,
    website: "https://aws.amazon.com/rds",
    description: "Amazon Relational Database Service"
  },
  {
    id: "amazondynamodb",
    name: "Amazon DynamoDB",
    aliases: ["dynamodb", "dynamo"],
    category: "aws",
    provider: "aws",
    c4Classification: "database",
    icon: { id: "amazondynamodb", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://aws.amazon.com/dynamodb",
    description: "Amazon DynamoDB NoSQL database"
  },
  {
    id: "amazonelasticache",
    name: "Amazon ElastiCache",
    aliases: ["elasticache"],
    category: "aws",
    provider: "aws",
    c4Classification: "cache",
    icon: { id: "amazonelasticache", source: "simple-icons" },
    protocols: ["TCP", "HTTPS"],
    managed: true,
    website: "https://aws.amazon.com/elasticache",
    description: "Amazon ElastiCache in-memory caching"
  },
  {
    id: "amazondocumentdb",
    name: "Amazon DocumentDB",
    aliases: ["documentdb"],
    category: "aws",
    provider: "aws",
    c4Classification: "database",
    icon: { id: "amazondocumentdb", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://aws.amazon.com/documentdb",
    description: "Amazon DocumentDB MongoDB-compatible database"
  },
  {
    id: "amazonredshift",
    name: "Amazon Redshift",
    aliases: ["redshift", "data-warehouse"],
    category: "aws",
    provider: "aws",
    c4Classification: "database",
    icon: { id: "amazonredshift", source: "simple-icons" },
    protocols: ["HTTPS", "SQL"],
    managed: true,
    website: "https://aws.amazon.com/redshift",
    description: "Amazon Redshift data warehouse"
  },
  {
    id: "amazonsqs",
    name: "Amazon SQS",
    aliases: ["sqs", "simple-queue-service"],
    category: "aws",
    provider: "aws",
    c4Classification: "queue",
    icon: { id: "amazonsqs", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://aws.amazon.com/sqs",
    description: "Amazon Simple Queue Service"
  },
  {
    id: "amazonsns",
    name: "Amazon SNS",
    aliases: ["sns", "simple-notification-service"],
    category: "aws",
    provider: "aws",
    c4Classification: "queue",
    icon: { id: "amazonsns", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://aws.amazon.com/sns",
    description: "Amazon Simple Notification Service"
  },
  {
    id: "amazonapigateway",
    name: "Amazon API Gateway",
    aliases: ["apigateway", "aws-api-gateway"],
    category: "aws",
    provider: "aws",
    c4Classification: "container",
    icon: { id: "amazonapigateway", source: "simple-icons" },
    protocols: ["HTTPS", "REST", "HTTP"],
    managed: true,
    website: "https://aws.amazon.com/api-gateway",
    description: "Amazon API Gateway"
  },
  {
    id: "awsalb",
    name: "AWS ALB",
    aliases: ["alb", "application-load-balancer", "aws-elastic-load-balancing"],
    category: "aws",
    provider: "aws",
    c4Classification: "infrastructure",
    icon: { id: "awselasticloadbalancing", source: "simple-icons" },
    protocols: ["HTTPS", "HTTP"],
    managed: true,
    website: "https://aws.amazon.com/elasticloadbalancing",
    description: "AWS Application Load Balancer"
  },
  {
    id: "awscloudwatch",
    name: "Amazon CloudWatch",
    aliases: ["cloudwatch"],
    category: "aws",
    provider: "aws",
    c4Classification: "infrastructure",
    icon: { id: "amazoncloudwatch", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://aws.amazon.com/cloudwatch",
    description: "Amazon CloudWatch monitoring and observability"
  },
  {
    id: "awssecretsmanager",
    name: "AWS Secrets Manager",
    aliases: ["secrets-manager", "aws-secrets"],
    category: "aws",
    provider: "aws",
    c4Classification: "infrastructure",
    icon: { id: "awssecretsmanager", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://aws.amazon.com/secrets-manager",
    description: "AWS Secrets Manager"
  },
  {
    id: "awsiam",
    name: "AWS IAM",
    aliases: ["iam", "aws-identity"],
    category: "aws",
    provider: "aws",
    c4Classification: "infrastructure",
    icon: { id: "amazoniam", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://aws.amazon.com/iam",
    description: "AWS Identity and Access Management"
  },
  {
    id: "awscognito",
    name: "Amazon Cognito",
    aliases: ["cognito"],
    category: "aws",
    provider: "aws",
    c4Classification: "container",
    icon: { id: "amazoncognito", source: "simple-icons" },
    protocols: ["HTTPS", "OAuth", "OIDC"],
    managed: true,
    website: "https://aws.amazon.com/cognito",
    description: "Amazon Cognito user pools and identity pools"
  },
  {
    id: "awsfargate",
    name: "AWS Fargate",
    aliases: ["fargate", "serverless-containers"],
    category: "aws",
    provider: "aws",
    c4Classification: "infrastructure",
    icon: { id: "awsfargate", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://aws.amazon.com/fargate",
    description: "AWS Fargate serverless containers"
  }
];
var azureServices = [
  {
    id: "azureaks",
    name: "Azure AKS",
    aliases: ["aks", "azure-kubernetes-service"],
    category: "azure",
    provider: "azure",
    c4Classification: "infrastructure",
    icon: { id: "cloud", source: "lucide" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://azure.microsoft.com/products/kubernetes-service",
    description: "Azure Kubernetes Service"
  },
  {
    id: "azurefunctions",
    name: "Azure Functions",
    aliases: ["azure-function", "azure-faas"],
    category: "azure",
    provider: "azure",
    c4Classification: "component",
    icon: { id: "cloud", source: "lucide" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://azure.microsoft.com/products/functions",
    description: "Azure serverless compute"
  },
  {
    id: "azuredevops",
    name: "Azure DevOps",
    aliases: ["devops", "azure-pipelines"],
    category: "azure",
    provider: "azure",
    c4Classification: "infrastructure",
    icon: { id: "cloud", source: "lucide" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://azure.microsoft.com/products/devops",
    description: "Azure DevOps services"
  },
  {
    id: "azureservicebus",
    name: "Azure Service Bus",
    aliases: ["servicebus", "azure-service-bus"],
    category: "azure",
    provider: "azure",
    c4Classification: "queue",
    icon: { id: "cloud", source: "lucide" },
    protocols: ["HTTPS", "AMQP"],
    managed: true,
    website: "https://azure.microsoft.com/products/service-bus",
    description: "Azure Service Bus messaging"
  },
  {
    id: "azuremonitor",
    name: "Azure Monitor",
    aliases: ["azure-monitoring", "application-insights"],
    category: "azure",
    provider: "azure",
    c4Classification: "infrastructure",
    icon: { id: "cloud", source: "lucide" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://azure.microsoft.com/products/monitor",
    description: "Azure Monitor observability"
  }
];
var gcpServices = [
  {
    id: "gke",
    name: "Google GKE",
    aliases: ["google-kubernetes-engine", "gcp-kubernetes"],
    category: "gcp",
    provider: "gcp",
    c4Classification: "infrastructure",
    icon: { id: "googlecloud", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://cloud.google.com/kubernetes-engine",
    description: "Google Kubernetes Engine"
  },
  {
    id: "googlecloudrun",
    name: "Google Cloud Run",
    aliases: ["cloud-run", "gcp-cloud-run"],
    category: "gcp",
    provider: "gcp",
    c4Classification: "component",
    icon: { id: "googlecloud", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://cloud.google.com/run",
    description: "Google Cloud Run serverless containers"
  },
  {
    id: "googlecloudfunctions",
    name: "Google Cloud Functions",
    aliases: ["cloud-functions", "gcp-faas"],
    category: "gcp",
    provider: "gcp",
    c4Classification: "component",
    icon: { id: "googlecloud", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://cloud.google.com/functions",
    description: "Google Cloud Functions serverless compute"
  },
  {
    id: "googlepubsub",
    name: "Google Pub/Sub",
    aliases: ["pub-sub", "gcp-pubsub", "google-pubsub"],
    category: "gcp",
    provider: "gcp",
    c4Classification: "queue",
    icon: { id: "googlepubsub", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://cloud.google.com/pubsub",
    description: "Google Cloud Pub/Sub messaging"
  },
  {
    id: "googlebigquery",
    name: "Google BigQuery",
    aliases: ["bigquery", "gcp-bigquery"],
    category: "gcp",
    provider: "gcp",
    c4Classification: "database",
    icon: { id: "googlebigquery", source: "simple-icons" },
    protocols: ["HTTPS", "SQL"],
    managed: true,
    website: "https://cloud.google.com/bigquery",
    description: "Google BigQuery data warehouse"
  },
  {
    id: "googlecloudstorage",
    name: "Google Cloud Storage",
    aliases: ["gcs", "gcp-storage", "cloud-storage"],
    category: "gcp",
    provider: "gcp",
    c4Classification: "database",
    icon: { id: "googlecloudstorage", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://cloud.google.com/storage",
    description: "Google Cloud Storage object storage"
  },
  {
    id: "gcpmonitoring",
    name: "Google Cloud Monitoring",
    aliases: ["stackdriver", "gcp-monitoring", "cloud-monitoring"],
    category: "gcp",
    provider: "gcp",
    c4Classification: "infrastructure",
    icon: { id: "googlecloud", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://cloud.google.com/monitoring",
    description: "Google Cloud Monitoring and Stackdriver"
  }
];
var kubernetesTech = [
  {
    id: "kubernetes",
    name: "Kubernetes",
    aliases: ["k8s", "k3s"],
    category: "kubernetes",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "kubernetes", source: "simple-icons" },
    protocols: ["HTTPS"],
    description: "Container orchestration platform"
  }
];
var containers = [
  {
    id: "docker",
    name: "Docker",
    aliases: ["containerd", "container-runtime"],
    category: "containers",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "docker", source: "simple-icons" },
    protocols: [],
    description: "Container runtime and tooling"
  }
];
var frontendTech = [
  {
    id: "react",
    name: "React",
    aliases: ["reactjs", "react-js"],
    category: "frontend",
    c4Classification: "component",
    icon: { id: "react", source: "simple-icons" },
    protocols: [],
    license: "MIT",
    website: "https://react.dev",
    description: "JavaScript UI library"
  },
  {
    id: "nextdotjs",
    name: "Next.js",
    aliases: ["next", "nextjs", "next-js"],
    category: "frontend",
    c4Classification: "component",
    icon: { id: "nextdotjs", source: "simple-icons" },
    protocols: ["HTTPS", "HTTP"],
    license: "MIT",
    website: "https://nextjs.org",
    description: "React framework for production"
  },
  {
    id: "vuedotjs",
    name: "Vue.js",
    aliases: ["vue", "vuejs", "vue-js"],
    category: "frontend",
    c4Classification: "component",
    icon: { id: "vuedotjs", source: "simple-icons" },
    protocols: [],
    license: "MIT",
    website: "https://vuejs.org",
    description: "Progressive JavaScript framework"
  },
  {
    id: "angular",
    name: "Angular",
    aliases: ["angularjs", "angular-js"],
    category: "frontend",
    c4Classification: "component",
    icon: { id: "angular", source: "simple-icons" },
    protocols: [],
    license: "MIT",
    website: "https://angular.dev",
    description: "Platform for web applications"
  },
  {
    id: "svelte",
    name: "Svelte",
    aliases: ["sveltejs", "svelte-js"],
    category: "frontend",
    c4Classification: "component",
    icon: { id: "svelte", source: "simple-icons" },
    protocols: [],
    license: "MIT",
    website: "https://svelte.dev",
    description: "Cybernetically enhanced web apps"
  },
  {
    id: "web-ui",
    name: "Web UI",
    aliases: ["frontend", "web-app", "spa", "dashboard", "web-frontend"],
    category: "frontend",
    c4Classification: "container",
    icon: { id: "monitor", source: "lucide" },
    protocols: ["HTTPS", "HTTP"],
    description: "Web-based user interface"
  },
  {
    id: "mobile-app",
    name: "Mobile App",
    aliases: ["ios", "android", "mobile", "react-native", "flutter"],
    category: "frontend",
    c4Classification: "container",
    icon: { id: "smartphone", source: "lucide" },
    protocols: ["HTTPS"],
    description: "Mobile application"
  },
  {
    id: "tailwindcss",
    name: "Tailwind CSS",
    aliases: ["tailwind", "tailwindcss"],
    category: "frontend",
    c4Classification: "component",
    icon: { id: "tailwindcss", source: "simple-icons" },
    protocols: [],
    license: "MIT",
    website: "https://tailwindcss.com",
    description: "Utility-first CSS framework"
  },
  {
    id: "vite",
    name: "Vite",
    aliases: ["vitejs"],
    category: "frontend",
    c4Classification: "infrastructure",
    icon: { id: "vite", source: "simple-icons" },
    protocols: [],
    license: "MIT",
    website: "https://vite.dev",
    description: "Next generation frontend tooling"
  },
  {
    id: "webpack",
    name: "Webpack",
    aliases: ["webpackjs"],
    category: "frontend",
    c4Classification: "infrastructure",
    icon: { id: "webpack", source: "simple-icons" },
    protocols: [],
    license: "MIT",
    website: "https://webpack.js.org",
    description: "Module bundler for JavaScript"
  },
  {
    id: "typescript",
    name: "TypeScript",
    aliases: ["ts"],
    category: "frontend",
    c4Classification: "component",
    icon: { id: "typescript", source: "simple-icons" },
    protocols: [],
    license: "Apache-2.0",
    website: "https://www.typescriptlang.org",
    description: "Typed superset of JavaScript"
  },
  {
    id: "javascript",
    name: "JavaScript",
    aliases: ["js", "ecmascript"],
    category: "frontend",
    c4Classification: "component",
    icon: { id: "javascript", source: "simple-icons" },
    protocols: [],
    license: "N/A",
    website: "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
    description: "High-level programming language"
  }
];
var backendTech = [
  {
    id: "python",
    name: "Python",
    aliases: ["py"],
    category: "backend",
    c4Classification: "component",
    icon: { id: "python", source: "simple-icons" },
    protocols: [],
    license: "PSF",
    website: "https://www.python.org",
    description: "High-level programming language"
  },
  {
    id: "fastapi",
    name: "FastAPI",
    aliases: ["fast-api"],
    category: "backend",
    c4Classification: "component",
    icon: { id: "fastapi", source: "simple-icons" },
    protocols: ["HTTPS", "HTTP", "REST", "WebSocket"],
    license: "MIT",
    website: "https://fastapi.tiangolo.com",
    description: "Modern Python web framework for APIs"
  },
  {
    id: "flask",
    name: "Flask",
    aliases: [],
    category: "backend",
    c4Classification: "component",
    icon: { id: "flask", source: "simple-icons" },
    protocols: ["HTTPS", "HTTP", "REST"],
    license: "BSD-3-Clause",
    website: "https://flask.palletsprojects.com",
    description: "Lightweight Python web framework"
  },
  {
    id: "django",
    name: "Django",
    aliases: [],
    category: "backend",
    c4Classification: "component",
    icon: { id: "django", source: "simple-icons" },
    protocols: ["HTTPS", "HTTP", "REST"],
    license: "BSD-3-Clause",
    website: "https://www.djangoproject.com",
    description: "High-level Python web framework"
  },
  {
    id: "nodedotjs",
    name: "Node.js",
    aliases: ["node", "nodejs", "node-js"],
    category: "backend",
    c4Classification: "component",
    icon: { id: "nodedotjs", source: "simple-icons" },
    protocols: ["HTTP", "HTTPS"],
    license: "MIT",
    website: "https://nodejs.org",
    description: "JavaScript runtime built on V8"
  },
  {
    id: "express",
    name: "Express",
    aliases: ["expressjs", "express-js"],
    category: "backend",
    c4Classification: "component",
    icon: { id: "express", source: "simple-icons" },
    protocols: ["HTTP", "HTTPS", "REST"],
    license: "MIT",
    website: "https://expressjs.com",
    description: "Fast, unopinionated Node.js web framework"
  },
  {
    id: "rust",
    name: "Rust",
    aliases: ["rustlang"],
    category: "backend",
    c4Classification: "component",
    icon: { id: "rust", source: "simple-icons" },
    protocols: [],
    license: "MIT/Apache-2.0",
    website: "https://www.rust-lang.org",
    description: "Systems programming language"
  },
  {
    id: "go",
    name: "Go",
    aliases: ["golang"],
    category: "backend",
    c4Classification: "component",
    icon: { id: "go", source: "simple-icons" },
    protocols: [],
    license: "BSD-3-Clause",
    website: "https://go.dev",
    description: "Fast, compiled language for systems"
  },
  {
    id: "dotnet",
    name: ".NET",
    aliases: ["dotnet-core", "aspnet", "aspnetcore", "csharp", "dotnetcore"],
    category: "backend",
    c4Classification: "component",
    icon: { id: "dotnet", source: "simple-icons" },
    protocols: ["HTTPS", "HTTP", "gRPC"],
    license: "MIT",
    website: "https://dotnet.microsoft.com",
    description: ".NET developer platform"
  },
  {
    id: "java",
    name: "Java",
    aliases: ["jdk", "jre", "openjdk"],
    category: "backend",
    c4Classification: "component",
    icon: { id: "oracle", source: "simple-icons" },
    protocols: [],
    license: "GPL-2.0",
    website: "https://openjdk.org",
    description: "Object-oriented programming language"
  },
  {
    id: "php",
    name: "PHP",
    aliases: ["php8"],
    category: "backend",
    c4Classification: "component",
    icon: { id: "php", source: "simple-icons" },
    protocols: ["HTTP", "HTTPS"],
    license: "PHP License",
    website: "https://www.php.net",
    description: "General-purpose scripting language"
  },
  {
    id: "ruby",
    name: "Ruby",
    aliases: ["ruby-lang"],
    category: "backend",
    c4Classification: "component",
    icon: { id: "ruby", source: "simple-icons" },
    protocols: [],
    license: "Ruby License",
    website: "https://www.ruby-lang.org",
    description: "Dynamic programming language"
  },
  {
    id: "rubyonrails",
    name: "Ruby on Rails",
    aliases: ["rails", "ror"],
    category: "backend",
    c4Classification: "component",
    icon: { id: "rubyonrails", source: "simple-icons" },
    protocols: ["HTTPS", "HTTP", "REST"],
    license: "MIT",
    website: "https://rubyonrails.org",
    description: "Full-stack Ruby web framework"
  },
  {
    id: "spring",
    name: "Spring",
    aliases: ["springboot", "spring-boot", "spring-framework"],
    category: "backend",
    c4Classification: "component",
    icon: { id: "spring", source: "simple-icons" },
    protocols: ["HTTPS", "HTTP", "gRPC", "REST"],
    license: "Apache-2.0",
    website: "https://spring.io",
    description: "Java application framework"
  },
  {
    id: "graphql",
    name: "GraphQL",
    aliases: ["gql"],
    category: "backend",
    c4Classification: "component",
    icon: { id: "graphql", source: "simple-icons" },
    protocols: ["HTTPS", "HTTP", "GraphQL"],
    license: "OWFa-1.0",
    website: "https://graphql.org",
    description: "Query language for APIs"
  },
  {
    id: "grpc",
    name: "gRPC",
    aliases: ["grpc-service", "grpc-api"],
    category: "backend",
    c4Classification: "component",
    icon: { id: "code", source: "lucide" },
    protocols: ["HTTPS", "HTTP/2", "gRPC"],
    license: "Apache-2.0",
    website: "https://grpc.io",
    description: "High-performance RPC framework"
  },
  {
    id: "rest-api",
    name: "REST API",
    aliases: ["rest", "api", "http-api"],
    category: "backend",
    c4Classification: "container",
    icon: { id: "code", source: "lucide" },
    protocols: ["HTTPS", "HTTP", "REST"],
    description: "RESTful API service"
  }
];
var databases = [
  {
    id: "postgresql",
    name: "PostgreSQL",
    aliases: ["postgres", "psql", "pg"],
    category: "databases",
    provider: "multi-cloud",
    c4Classification: "database",
    icon: { id: "postgresql", source: "simple-icons" },
    protocols: ["SQL", "TCP"],
    license: "PostgreSQL License",
    website: "https://www.postgresql.org",
    description: "Advanced open source SQL database"
  },
  {
    id: "mysql",
    name: "MySQL",
    aliases: ["mariadb"],
    category: "databases",
    provider: "multi-cloud",
    c4Classification: "database",
    icon: { id: "mysql", source: "simple-icons" },
    protocols: ["SQL", "TCP"],
    license: "GPL-2.0",
    website: "https://www.mysql.com",
    description: "Open source relational database"
  },
  {
    id: "mariadb",
    name: "MariaDB",
    aliases: [],
    category: "databases",
    provider: "multi-cloud",
    c4Classification: "database",
    icon: { id: "mariadb", source: "simple-icons" },
    protocols: ["SQL", "TCP"],
    license: "GPL-2.0",
    website: "https://mariadb.org",
    description: "Fork of MySQL by original developers"
  },
  {
    id: "mongodb",
    name: "MongoDB",
    aliases: ["mongo", "document-db"],
    category: "databases",
    provider: "multi-cloud",
    c4Classification: "database",
    icon: { id: "mongodb", source: "simple-icons" },
    protocols: ["MongoDB", "TCP", "HTTPS"],
    license: "SSPL",
    website: "https://www.mongodb.com",
    description: "Document-oriented NoSQL database"
  },
  {
    id: "sqlite",
    name: "SQLite",
    aliases: [],
    category: "databases",
    provider: "multi-cloud",
    c4Classification: "database",
    icon: { id: "sqlite", source: "simple-icons" },
    protocols: ["SQL"],
    license: "Public Domain",
    website: "https://www.sqlite.org",
    description: "Self-contained SQL database engine"
  },
  {
    id: "cassandra",
    name: "Cassandra",
    aliases: ["scylla", "scylladb"],
    category: "databases",
    provider: "multi-cloud",
    c4Classification: "database",
    icon: { id: "apachecassandra", source: "simple-icons" },
    protocols: ["CQL", "TCP"],
    license: "Apache-2.0",
    website: "https://cassandra.apache.org",
    description: "Distributed NoSQL wide-column store"
  },
  {
    id: "elasticsearch",
    name: "Elasticsearch",
    aliases: ["es", "elastic"],
    category: "databases",
    provider: "multi-cloud",
    c4Classification: "database",
    icon: { id: "elasticsearch", source: "simple-icons" },
    protocols: ["HTTPS", "REST"],
    license: "Elastic License 2.0",
    website: "https://www.elastic.co/elasticsearch",
    description: "Distributed search and analytics engine"
  },
  {
    id: "dynamodb",
    name: "DynamoDB",
    aliases: ["dynamo"],
    category: "databases",
    provider: "aws",
    c4Classification: "database",
    icon: { id: "amazondynamodb", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://aws.amazon.com/dynamodb",
    description: "Amazon DynamoDB key-value database"
  },
  {
    id: "redis",
    name: "Redis",
    aliases: ["redis-cache"],
    category: "databases",
    provider: "multi-cloud",
    c4Classification: "cache",
    icon: { id: "redis", source: "simple-icons" },
    protocols: ["TCP"],
    license: "BSD-3-Clause",
    website: "https://redis.io",
    description: "In-memory data store"
  },
  {
    id: "snowflake",
    name: "Snowflake",
    aliases: ["data-warehouse", "redshift", "bigquery", "synapse"],
    category: "databases",
    provider: "multi-cloud",
    c4Classification: "database",
    icon: { id: "snowflake", source: "simple-icons" },
    protocols: ["HTTPS", "SQL"],
    managed: true,
    website: "https://www.snowflake.com",
    description: "Cloud data warehouse"
  },
  {
    id: "cockroachdb",
    name: "CockroachDB",
    aliases: ["cockroach", "crdb"],
    category: "databases",
    provider: "multi-cloud",
    c4Classification: "database",
    icon: { id: "database", source: "lucide" },
    protocols: ["SQL", "TCP", "HTTPS"],
    license: "BSL-1.1",
    website: "https://www.cockroachlabs.com",
    description: "Distributed SQL database"
  },
  {
    id: "clickhouse",
    name: "ClickHouse",
    aliases: [],
    category: "databases",
    provider: "multi-cloud",
    c4Classification: "database",
    icon: { id: "clickhouse", source: "simple-icons" },
    protocols: ["TCP", "HTTPS"],
    license: "Apache-2.0",
    website: "https://clickhouse.com",
    description: "Column-oriented OLAP database"
  },
  {
    id: "timescaledb",
    name: "TimescaleDB",
    aliases: ["timescale"],
    category: "databases",
    provider: "multi-cloud",
    c4Classification: "database",
    icon: { id: "timescale", source: "simple-icons" },
    protocols: ["SQL", "TCP"],
    license: "Apache-2.0",
    website: "https://www.timescale.com",
    description: "Time-series database on PostgreSQL"
  },
  {
    id: "memcached",
    name: "Memcached",
    aliases: ["memcache", "memcache"],
    category: "databases",
    provider: "multi-cloud",
    c4Classification: "cache",
    icon: { id: "database", source: "lucide" },
    protocols: ["TCP"],
    license: "BSD",
    website: "https://memcached.org",
    description: "High-performance distributed memory caching"
  }
];
var messaging = [
  {
    id: "kafka",
    name: "Apache Kafka",
    aliases: ["kafka", "event-stream", "message-broker", "apachekafka"],
    category: "messaging",
    provider: "multi-cloud",
    c4Classification: "queue",
    icon: { id: "apachekafka", source: "simple-icons" },
    protocols: ["TCP", "HTTPS"],
    license: "Apache-2.0",
    website: "https://kafka.apache.org",
    description: "Distributed event streaming platform"
  },
  {
    id: "rabbitmq",
    name: "RabbitMQ",
    aliases: ["amqp", "message-queue"],
    category: "messaging",
    provider: "multi-cloud",
    c4Classification: "queue",
    icon: { id: "rabbitmq", source: "simple-icons" },
    protocols: ["AMQP", "TCP", "HTTPS"],
    license: "MPL-2.0",
    website: "https://www.rabbitmq.com",
    description: "Open source message broker"
  },
  {
    id: "nats",
    name: "NATS",
    aliases: ["natsio", "nats-io"],
    category: "messaging",
    provider: "multi-cloud",
    c4Classification: "queue",
    icon: { id: "natsdotio", source: "simple-icons" },
    protocols: ["TCP", "TLS"],
    license: "Apache-2.0",
    website: "https://nats.io",
    description: "Cloud-native messaging system"
  },
  {
    id: "pulsar",
    name: "Apache Pulsar",
    aliases: ["pulsar"],
    category: "messaging",
    provider: "multi-cloud",
    c4Classification: "queue",
    icon: { id: "apachepulsar", source: "simple-icons" },
    protocols: ["TCP", "TLS"],
    license: "Apache-2.0",
    website: "https://pulsar.apache.org",
    description: "Multi-tenant, high-performance messaging"
  },
  {
    id: "rocketmq",
    name: "Apache RocketMQ",
    aliases: ["rocketmq"],
    category: "messaging",
    provider: "multi-cloud",
    c4Classification: "queue",
    icon: { id: "apacherocketmq", source: "simple-icons" },
    protocols: ["TCP"],
    license: "Apache-2.0",
    website: "https://rocketmq.apache.org",
    description: "Distributed messaging and streaming"
  },
  {
    id: "sqs",
    name: "Amazon SQS",
    aliases: ["sqs", "simple-queue-service"],
    category: "messaging",
    provider: "aws",
    c4Classification: "queue",
    icon: { id: "amazonsqs", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://aws.amazon.com/sqs",
    description: "Amazon Simple Queue Service"
  },
  {
    id: "sns",
    name: "Amazon SNS",
    aliases: ["sns", "simple-notification-service"],
    category: "messaging",
    provider: "aws",
    c4Classification: "queue",
    icon: { id: "amazonsns", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://aws.amazon.com/sns",
    description: "Amazon Simple Notification Service"
  },
  {
    id: "googlepubsub-messaging",
    name: "Google Pub/Sub",
    aliases: ["pub-sub", "gcp-pubsub", "google-pubsub"],
    category: "messaging",
    provider: "gcp",
    c4Classification: "queue",
    icon: { id: "googlepubsub", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://cloud.google.com/pubsub",
    description: "Google Cloud Pub/Sub",
    deprecated: true,
    replacement: "googlepubsub"
  },
  {
    id: "eventbridge",
    name: "EventBridge",
    aliases: ["event-bus", "aws-eventbridge"],
    category: "messaging",
    provider: "aws",
    c4Classification: "queue",
    icon: { id: "amazoneventbridge", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://aws.amazon.com/eventbridge",
    description: "AWS serverless event bus"
  },
  {
    id: "activemq",
    name: "Apache ActiveMQ",
    aliases: ["activemq"],
    category: "messaging",
    provider: "multi-cloud",
    c4Classification: "queue",
    icon: { id: "apache", source: "simple-icons" },
    protocols: ["AMQP", "TCP", "STOMP"],
    license: "Apache-2.0",
    website: "https://activemq.apache.org",
    description: "Open source message broker"
  },
  {
    id: "flink",
    name: "Apache Flink",
    aliases: ["flink", "stream-processing"],
    category: "messaging",
    provider: "multi-cloud",
    c4Classification: "component",
    icon: { id: "apacheflink", source: "simple-icons" },
    protocols: ["TCP"],
    license: "Apache-2.0",
    website: "https://flink.apache.org",
    description: "Stream processing framework"
  }
];
var apiGateways = [
  {
    id: "kong",
    name: "Kong",
    aliases: ["kong-gateway"],
    category: "api-gateway",
    provider: "multi-cloud",
    c4Classification: "container",
    icon: { id: "kong", source: "simple-icons" },
    protocols: ["HTTPS", "HTTP", "gRPC", "REST"],
    license: "Apache-2.0",
    website: "https://konghq.com",
    description: "Cloud-native API gateway"
  },
  {
    id: "envoy",
    name: "Envoy",
    aliases: ["envoyproxy", "envoy-proxy"],
    category: "api-gateway",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "envoyproxy", source: "simple-icons" },
    protocols: ["HTTPS", "HTTP", "gRPC"],
    license: "Apache-2.0",
    website: "https://www.envoyproxy.io",
    description: "Edge and service proxy"
  },
  {
    id: "nginx-ingress",
    name: "NGINX Ingress",
    aliases: ["nginx-ingress-controller"],
    category: "api-gateway",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "nginx", source: "simple-icons" },
    protocols: ["HTTPS", "HTTP", "TCP"],
    license: "BSD-2-Clause",
    website: "https://www.nginx.com",
    description: "NGINX Ingress Controller for Kubernetes"
  },
  {
    id: "api-gateway",
    name: "API Gateway",
    aliases: ["gateway", "api-gw"],
    category: "api-gateway",
    provider: "multi-cloud",
    c4Classification: "container",
    icon: { id: "git-branch", source: "lucide" },
    protocols: ["HTTPS", "HTTP", "REST"],
    description: "Generic API gateway"
  },
  {
    id: "swagger",
    name: "Swagger",
    aliases: ["openapi", "openapi-swagger"],
    category: "api-gateway",
    provider: "multi-cloud",
    c4Classification: "component",
    icon: { id: "swagger", source: "simple-icons" },
    protocols: ["HTTPS", "HTTP"],
    license: "Apache-2.0",
    website: "https://swagger.io",
    description: "API description and documentation"
  }
];
var loadBalancers = [
  {
    id: "nginx",
    name: "NGINX",
    aliases: ["nginx-proxy", "reverse-proxy", "traefik", "haproxy", "caddy"],
    category: "load-balancing",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "nginx", source: "simple-icons" },
    protocols: ["HTTPS", "HTTP", "TCP", "UDP", "TLS"],
    license: "BSD-2-Clause",
    website: "https://www.nginx.com",
    description: "Web server and reverse proxy"
  },
  {
    id: "traefik",
    name: "Traefik",
    aliases: ["traefik-proxy"],
    category: "load-balancing",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "traefikproxy", source: "simple-icons" },
    protocols: ["HTTPS", "HTTP", "TCP"],
    license: "MIT",
    website: "https://traefik.io",
    description: "Cloud-native edge router"
  },
  {
    id: "haproxy",
    name: "HAProxy",
    aliases: [],
    category: "load-balancing",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "loadbalancer", source: "lucide" },
    protocols: ["HTTPS", "HTTP", "TCP", "UDP"],
    license: "GPL-2.0",
    website: "https://www.haproxy.org",
    description: "High availability load balancer"
  },
  {
    id: "load-balancer",
    name: "Load Balancer",
    aliases: ["lb", "alb", "nlb", "elb"],
    category: "load-balancing",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "git-merge", source: "lucide" },
    protocols: ["HTTPS", "HTTP", "TCP"],
    description: "Generic load balancer"
  }
];
var authIdentity = [
  {
    id: "keycloak",
    name: "Keycloak",
    aliases: ["keycloak-sso"],
    category: "auth-identity",
    provider: "multi-cloud",
    c4Classification: "container",
    icon: { id: "keycloak", source: "simple-icons" },
    protocols: ["HTTPS", "OAuth", "OIDC", "SAML"],
    license: "Apache-2.0",
    website: "https://www.keycloak.org",
    description: "Open source identity and access management"
  },
  {
    id: "okta",
    name: "Okta",
    aliases: [],
    category: "auth-identity",
    provider: "multi-cloud",
    c4Classification: "container",
    icon: { id: "okta", source: "simple-icons" },
    protocols: ["HTTPS", "OAuth", "OIDC", "SAML"],
    managed: true,
    website: "https://www.okta.com",
    description: "Identity and access management"
  },
  {
    id: "auth0",
    name: "Auth0",
    aliases: [],
    category: "auth-identity",
    provider: "multi-cloud",
    c4Classification: "container",
    icon: { id: "auth0", source: "simple-icons" },
    protocols: ["HTTPS", "OAuth", "OIDC"],
    managed: true,
    website: "https://auth0.com",
    description: "Identity platform for developers"
  },
  {
    id: "oauth-oidc",
    name: "OAuth / OIDC",
    aliases: ["oauth2", "openid-connect", "oidc", "sso"],
    category: "auth-identity",
    c4Classification: "component",
    icon: { id: "shield", source: "lucide" },
    protocols: ["HTTPS", "OAuth", "OIDC"],
    description: "OAuth 2.0 and OpenID Connect"
  },
  {
    id: "vault",
    name: "Vault",
    aliases: ["hashicorp-vault", "secrets-manager", "secrets-vault"],
    category: "auth-identity",
    provider: "multi-cloud",
    c4Classification: "container",
    icon: { id: "vault", source: "simple-icons" },
    protocols: ["HTTPS", "TCP"],
    license: "BSL-1.1",
    website: "https://www.vaultproject.io",
    description: "HashiCorp secrets management"
  },
  {
    id: "jwt",
    name: "JWT",
    aliases: ["json-web-token", "jwt-tokens"],
    category: "auth-identity",
    c4Classification: "component",
    icon: { id: "key-round", source: "lucide" },
    protocols: ["HTTPS"],
    description: "JSON Web Token authentication"
  },
  {
    id: "rbac",
    name: "RBAC",
    aliases: ["role-based-access-control", "authorization"],
    category: "auth-identity",
    c4Classification: "component",
    icon: { id: "shield-check", source: "lucide" },
    protocols: [],
    description: "Role-based access control"
  }
];
var securityTech = [
  {
    id: "cloudflare-waf",
    name: "Cloudflare WAF",
    aliases: ["waf", "web-application-firewall"],
    category: "security",
    provider: "cloudflare",
    c4Classification: "infrastructure",
    icon: { id: "cloudflare", source: "simple-icons" },
    protocols: ["HTTPS", "HTTP"],
    managed: true,
    website: "https://www.cloudflare.com/waf",
    description: "Cloudflare Web Application Firewall"
  },
  {
    id: "aws-waf",
    name: "AWS WAF",
    aliases: ["aws-waf"],
    category: "security",
    provider: "aws",
    c4Classification: "infrastructure",
    icon: { id: "shield", source: "lucide" },
    protocols: ["HTTPS"],
    managed: true,
    description: "AWS Web Application Firewall"
  },
  {
    id: "snyk",
    name: "Snyk",
    aliases: [],
    category: "security",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "snyk", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://snyk.io",
    description: "Developer-first security platform"
  },
  {
    id: "trivy",
    name: "Trivy",
    aliases: [],
    category: "security",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "trivy", source: "simple-icons" },
    protocols: [],
    license: "Apache-2.0",
    website: "https://trivy.dev",
    description: "Comprehensive vulnerability scanner"
  },
  {
    id: "firewall",
    name: "Firewall",
    aliases: ["network-firewall", "security-group", "nsg"],
    category: "security",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "shield-alert", source: "lucide" },
    protocols: [],
    description: "Network firewall"
  },
  {
    id: "waf",
    name: "WAF",
    aliases: ["web-application-firewall"],
    category: "security",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "shield-check", source: "lucide" },
    protocols: ["HTTPS"],
    description: "Web Application Firewall"
  },
  {
    id: "kms",
    name: "KMS / Key Management",
    aliases: ["key-management", "encryption-keys", "aws-kms"],
    category: "security",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "key", source: "lucide" },
    protocols: ["HTTPS"],
    description: "Key management service"
  },
  {
    id: "certificate-authority",
    name: "Certificate Authority",
    aliases: ["ca", "pki", "tls-certificates", "letsencrypt"],
    category: "security",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "shield", source: "lucide" },
    protocols: ["HTTPS", "TLS"],
    description: "Certificate authority and PKI"
  },
  {
    id: "openvpn",
    name: "OpenVPN",
    aliases: ["openvpn-access-server"],
    category: "security",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "openvpn", source: "simple-icons" },
    protocols: ["TCP", "UDP", "TLS"],
    license: "GPL-2.0",
    website: "https://openvpn.net",
    description: "Open source VPN solution"
  },
  {
    id: "wireguard",
    name: "WireGuard",
    aliases: [],
    category: "security",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "wireguard", source: "simple-icons" },
    protocols: ["UDP"],
    license: "GPL-2.0",
    website: "https://www.wireguard.com",
    description: "Modern VPN tunnel protocol"
  }
];
var observability = [
  {
    id: "prometheus",
    name: "Prometheus",
    aliases: ["metrics", "monitoring"],
    category: "observability",
    provider: "multi-cloud",
    c4Classification: "container",
    icon: { id: "prometheus", source: "simple-icons" },
    protocols: ["HTTP", "HTTPS"],
    license: "Apache-2.0",
    website: "https://prometheus.io",
    description: "Open source monitoring and alerting"
  },
  {
    id: "grafana",
    name: "Grafana",
    aliases: ["dashboards", "visualization"],
    category: "observability",
    provider: "multi-cloud",
    c4Classification: "container",
    icon: { id: "grafana", source: "simple-icons" },
    protocols: ["HTTPS", "HTTP"],
    license: "AGPL-3.0",
    website: "https://grafana.com",
    description: "Open source analytics and visualization"
  },
  {
    id: "opentelemetry",
    name: "OpenTelemetry",
    aliases: ["otel", "tracing", "instrumentation"],
    category: "observability",
    provider: "multi-cloud",
    c4Classification: "component",
    icon: { id: "opentelemetry", source: "simple-icons" },
    protocols: ["HTTPS", "gRPC"],
    license: "Apache-2.0",
    website: "https://opentelemetry.io",
    description: "Observability framework and instrumentation"
  },
  {
    id: "jaeger",
    name: "Jaeger",
    aliases: ["distributed-tracing"],
    category: "observability",
    provider: "multi-cloud",
    c4Classification: "container",
    icon: { id: "jaeger", source: "simple-icons" },
    protocols: ["HTTPS", "gRPC"],
    license: "Apache-2.0",
    website: "https://www.jaegertracing.io",
    description: "Distributed tracing platform"
  },
  {
    id: "elk",
    name: "ELK Stack",
    aliases: ["elastic-stack", "logstash", "kibana"],
    category: "observability",
    provider: "multi-cloud",
    c4Classification: "container",
    icon: { id: "elasticstack", source: "simple-icons" },
    protocols: ["HTTPS", "TCP"],
    license: "Elastic License 2.0",
    website: "https://www.elastic.co/elastic-stack",
    description: "Elasticsearch, Logstash, Kibana stack"
  },
  {
    id: "kibana",
    name: "Kibana",
    aliases: [],
    category: "observability",
    provider: "multi-cloud",
    c4Classification: "container",
    icon: { id: "kibana", source: "simple-icons" },
    protocols: ["HTTPS"],
    license: "Elastic License 2.0",
    website: "https://www.elastic.co/kibana",
    description: "Kibana analytics dashboard"
  },
  {
    id: "cloudwatch",
    name: "CloudWatch",
    aliases: ["aws-cloudwatch", "aws-monitoring"],
    category: "observability",
    provider: "aws",
    c4Classification: "infrastructure",
    icon: { id: "amazoncloudwatch", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://aws.amazon.com/cloudwatch",
    description: "Amazon CloudWatch monitoring"
  },
  {
    id: "azure-monitor",
    name: "Azure Monitor",
    aliases: ["azure-monitoring"],
    category: "observability",
    provider: "azure",
    c4Classification: "infrastructure",
    icon: { id: "cloud", source: "lucide" },
    protocols: ["HTTPS"],
    managed: true,
    description: "Azure Monitor observability"
  },
  {
    id: "gcp-monitoring",
    name: "Google Cloud Monitoring",
    aliases: ["stackdriver", "gcp-monitoring"],
    category: "observability",
    provider: "gcp",
    c4Classification: "infrastructure",
    icon: { id: "googlecloud", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    description: "Google Cloud Monitoring"
  },
  {
    id: "datadog",
    name: "Datadog",
    aliases: [],
    category: "observability",
    provider: "multi-cloud",
    c4Classification: "container",
    icon: { id: "datadog", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://www.datadoghq.com",
    description: "Cloud monitoring and analytics"
  },
  {
    id: "newrelic",
    name: "New Relic",
    aliases: [],
    category: "observability",
    provider: "multi-cloud",
    c4Classification: "container",
    icon: { id: "newrelic", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://newrelic.com",
    description: "Full stack observability platform"
  },
  {
    id: "splunk",
    name: "Splunk",
    aliases: [],
    category: "observability",
    provider: "multi-cloud",
    c4Classification: "container",
    icon: { id: "splunk", source: "simple-icons" },
    protocols: ["HTTPS", "TCP"],
    managed: true,
    website: "https://www.splunk.com",
    description: "Data platform for monitoring and analytics"
  },
  {
    id: "victoriametrics",
    name: "VictoriaMetrics",
    aliases: ["vm"],
    category: "observability",
    provider: "multi-cloud",
    c4Classification: "container",
    icon: { id: "victoriametrics", source: "simple-icons" },
    protocols: ["HTTPS"],
    license: "Apache-2.0",
    website: "https://victoriametrics.com",
    description: "Time-series database and monitoring"
  }
];
var storageTech = [
  {
    id: "s3",
    name: "S3 / Object Storage",
    aliases: ["object-storage", "blob-storage", "minio"],
    category: "storage",
    provider: "aws",
    c4Classification: "database",
    icon: { id: "amazons3", source: "simple-icons" },
    protocols: ["HTTPS"],
    managed: true,
    website: "https://aws.amazon.com/s3",
    description: "Amazon S3 object storage"
  },
  {
    id: "cloudfront",
    name: "CloudFront",
    aliases: ["cdn", "content-delivery", "cloudflare-cdn"],
    category: "storage",
    provider: "aws",
    c4Classification: "infrastructure",
    icon: { id: "cloudflare", source: "simple-icons" },
    protocols: ["HTTPS", "HTTP"],
    managed: true,
    description: "AWS CloudFront CDN"
  },
  {
    id: "elasticsearch-storage",
    name: "Elasticsearch Storage",
    aliases: ["elasticsearch", "elastic-search"],
    category: "storage",
    provider: "multi-cloud",
    c4Classification: "database",
    icon: { id: "elasticsearch", source: "simple-icons" },
    protocols: ["HTTPS", "REST"],
    managed: false,
    description: "Elasticsearch storage backend"
  }
];
var networkingTech = [
  {
    id: "vpc",
    name: "VPC / VNet",
    aliases: ["vpc", "vnet", "virtual-network", "private-network"],
    category: "networking",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "network", source: "lucide" },
    protocols: [],
    description: "Virtual private cloud / network"
  },
  {
    id: "subnet",
    name: "Subnet",
    aliases: ["sub-network"],
    category: "networking",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "layers", source: "lucide" },
    protocols: [],
    description: "Network subnet"
  },
  {
    id: "nat-gateway",
    name: "NAT Gateway",
    aliases: ["nat", "nat-gw"],
    category: "networking",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "globe", source: "lucide" },
    protocols: [],
    description: "Network address translation gateway"
  },
  {
    id: "internet-gateway",
    name: "Internet Gateway",
    aliases: ["igw", "internet-gw"],
    category: "networking",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "globe", source: "lucide" },
    protocols: [],
    description: "Internet gateway"
  },
  {
    id: "dns",
    name: "DNS",
    aliases: ["domain-name-system", "route53", "cloudflare-dns"],
    category: "networking",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "globe", source: "lucide" },
    protocols: ["DNS", "HTTPS"],
    description: "Domain Name System"
  },
  {
    id: "istio",
    name: "Istio",
    aliases: ["istio-service-mesh"],
    category: "networking",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "istio", source: "simple-icons" },
    protocols: ["HTTPS", "TCP", "TLS"],
    license: "Apache-2.0",
    website: "https://istio.io",
    description: "Service mesh platform"
  },
  {
    id: "linkerd",
    name: "Linkerd",
    aliases: ["linkerd-service-mesh"],
    category: "networking",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "linkerd", source: "simple-icons" },
    protocols: ["HTTPS", "TCP", "TLS"],
    license: "Apache-2.0",
    website: "https://linkerd.io",
    description: "Ultralight service mesh"
  }
];
var devopsCicd = [
  {
    id: "terraform",
    name: "Terraform",
    aliases: ["tf", "hashicorp-terraform"],
    category: "devops-cicd",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "terraform", source: "simple-icons" },
    protocols: [],
    license: "BSL-1.1",
    website: "https://www.terraform.io",
    description: "Infrastructure as code tool"
  },
  {
    id: "ansible",
    name: "Ansible",
    aliases: ["redhat-ansible"],
    category: "devops-cicd",
    provider: "multi-cloud",
    c4Classification: "infrastructure",
    icon: { id: "ansible", source: "simple-icons" },
    protocols: ["SSH", "HTTPS"],
    license: "GPL-3.0",
    website: "https://www.ansible.com",
    description: "IT automation and configuration management"
  },
  {
    id: "jenkins",
    name: "Jenkins",
    aliases: [],
    category: "devops-cicd",
    provider: "multi-cloud",
    c4Classification: "container",
    icon: { id: "jenkins", source: "simple-icons" },
    protocols: ["HTTPS"],
    license: "MIT",
    website: "https://www.jenkins.io",
    description: "Automation server for CI/CD"
  },
  {
    id: "github-actions",
    name: "GitHub Actions",
    aliases: ["gh-actions", "gha"],
    category: "devops-cicd",
    provider: "multi-cloud",
    c4Classification: "container",
    icon: { id: "githubactions", source: "simple-icons" },
    protocols: ["HTTPS"],
    website: "https://github.com/features/actions",
    description: "GitHub CI/CD automation"
  },
  {
    id: "gitlab",
    name: "GitLab",
    aliases: [],
    category: "devops-cicd",
    provider: "multi-cloud",
    c4Classification: "container",
    icon: { id: "gitlab", source: "simple-icons" },
    protocols: ["HTTPS"],
    website: "https://about.gitlab.com",
    description: "DevSecOps platform"
  },
  {
    id: "argocd",
    name: "Argo CD",
    aliases: ["argocd"],
    category: "devops-cicd",
    provider: "multi-cloud",
    c4Classification: "container",
    icon: { id: "git-branch", source: "lucide" },
    protocols: ["HTTPS"],
    license: "Apache-2.0",
    website: "https://argo-cd.readthedocs.io",
    description: "GitOps continuous delivery for Kubernetes"
  },
  {
    id: "flux",
    name: "Flux",
    aliases: ["fluxcd", "flux-cd"],
    category: "devops-cicd",
    provider: "multi-cloud",
    c4Classification: "container",
    icon: { id: "flux", source: "simple-icons" },
    protocols: ["HTTPS"],
    license: "Apache-2.0",
    website: "https://fluxcd.io",
    description: "GitOps toolkit for Kubernetes"
  },
  {
    id: "sonarqube",
    name: "SonarQube",
    aliases: [],
    category: "devops-cicd",
    provider: "multi-cloud",
    c4Classification: "container",
    icon: { id: "sonarqube", source: "simple-icons" },
    protocols: ["HTTPS"],
    license: "LGPL-3.0",
    website: "https://www.sonarsource.com/products/sonarqube",
    description: "Code quality and security analysis"
  }
];
var genericComponents = [
  {
    id: "service",
    name: "Service",
    aliases: ["microservice", "backend-service", "api-service", "micro-service"],
    category: "generic",
    c4Classification: "component",
    icon: { id: "server", source: "lucide" },
    protocols: ["HTTPS", "HTTP"],
    description: "Backend service or microservice"
  },
  {
    id: "microservice",
    name: "Microservice",
    aliases: ["micro-service"],
    category: "generic",
    c4Classification: "component",
    icon: { id: "server", source: "lucide" },
    protocols: ["HTTPS", "HTTP"],
    description: "Microservice component"
  },
  {
    id: "worker",
    name: "Worker",
    aliases: ["background-worker", "job-processor", "consumer"],
    category: "generic",
    c4Classification: "component",
    icon: { id: "cpu", source: "lucide" },
    protocols: [],
    description: "Background worker or job processor"
  },
  {
    id: "container-generic",
    name: "Container",
    aliases: ["docker-container"],
    category: "generic",
    c4Classification: "container",
    icon: { id: "box", source: "lucide" },
    protocols: [],
    description: "Generic container workload"
  },
  {
    id: "vm",
    name: "Virtual Machine",
    aliases: ["ec2", "vm-instance", "compute-instance"],
    category: "generic",
    c4Classification: "infrastructure",
    icon: { id: "server", source: "lucide" },
    protocols: [],
    description: "Virtual machine instance"
  },
  {
    id: "serverless-function",
    name: "Serverless Function",
    aliases: ["function", "faas", "cloud-function"],
    category: "generic",
    c4Classification: "component",
    icon: { id: "zap", source: "lucide" },
    protocols: ["HTTPS"],
    description: "Serverless function / FaaS"
  },
  {
    id: "k8s-pod",
    name: "Kubernetes Pod",
    aliases: ["pod", "k8s-pod"],
    category: "generic",
    c4Classification: "container",
    icon: { id: "boxes", source: "lucide" },
    protocols: [],
    description: "Kubernetes pod"
  },
  {
    id: "k8s-deployment",
    name: "Kubernetes Deployment",
    aliases: ["deployment", "k8s-deployment"],
    category: "generic",
    c4Classification: "container",
    icon: { id: "boxes", source: "lucide" },
    protocols: [],
    description: "Kubernetes deployment"
  },
  {
    id: "bff",
    name: "BFF (Backend for Frontend)",
    aliases: ["backend-for-frontend"],
    category: "generic",
    c4Classification: "container",
    icon: { id: "server", source: "lucide" },
    protocols: ["HTTPS", "HTTP", "REST"],
    description: "Backend for Frontend pattern"
  },
  {
    id: "external-system",
    name: "External System",
    aliases: ["external", "third-party", "saas", "s3-storage"],
    category: "generic",
    c4Classification: "external-system",
    icon: { id: "globe", source: "lucide" },
    protocols: ["HTTPS"],
    description: "External or third-party system"
  },
  {
    id: "user",
    name: "User",
    aliases: ["end-user", "client", "customer"],
    category: "generic",
    c4Classification: "external-system",
    icon: { id: "user", source: "lucide" },
    protocols: ["HTTPS"],
    description: "End user or client"
  },
  {
    id: "database",
    name: "Database",
    aliases: ["db", "data-store", "datasource"],
    category: "generic",
    c4Classification: "database",
    icon: { id: "database", source: "lucide" },
    protocols: ["SQL"],
    description: "Generic database"
  },
  {
    id: "cache",
    name: "Cache",
    aliases: ["caching-layer", "in-memory-cache"],
    category: "generic",
    c4Classification: "cache",
    icon: { id: "zap", source: "lucide" },
    protocols: ["TCP"],
    description: "Generic caching layer"
  },
  {
    id: "queue",
    name: "Queue",
    aliases: ["message-queue", "job-queue"],
    category: "generic",
    c4Classification: "queue",
    icon: { id: "message-square", source: "lucide" },
    protocols: [],
    description: "Generic message queue"
  },
  {
    id: "stream",
    name: "Stream",
    aliases: ["event-stream", "data-stream", "stream-processing"],
    category: "generic",
    c4Classification: "queue",
    icon: { id: "radio", source: "lucide" },
    protocols: [],
    description: "Generic event or data stream"
  },
  {
    id: "cdn",
    name: "CDN",
    aliases: ["content-delivery-network", "edge-network"],
    category: "generic",
    c4Classification: "infrastructure",
    icon: { id: "globe", source: "lucide" },
    protocols: ["HTTPS", "HTTP"],
    description: "Content delivery network"
  },
  {
    id: "monitoring",
    name: "Monitoring",
    aliases: ["monitoring-system"],
    category: "generic",
    c4Classification: "container",
    icon: { id: "activity", source: "lucide" },
    protocols: ["HTTPS"],
    description: "Generic monitoring or observability"
  },
  {
    id: "loadbalancer",
    name: "Load Balancer",
    aliases: ["lb", "alb", "nlb", "elb", "load-balancer"],
    category: "generic",
    c4Classification: "infrastructure",
    icon: { id: "git-merge", source: "lucide" },
    protocols: ["HTTPS", "HTTP", "TCP"],
    description: "Generic load balancer"
  },
  {
    id: "gateway",
    name: "Gateway",
    aliases: ["api-gateway", "edge-gateway"],
    category: "generic",
    c4Classification: "container",
    icon: { id: "git-branch", source: "lucide" },
    protocols: ["HTTPS", "HTTP"],
    description: "Generic gateway"
  },
  {
    id: "auth",
    name: "Auth",
    aliases: ["authentication", "authorization"],
    category: "generic",
    c4Classification: "component",
    icon: { id: "shield", source: "lucide" },
    protocols: ["HTTPS"],
    description: "Authentication or authorization service"
  },
  {
    id: "secret",
    name: "Secrets Manager",
    aliases: ["secrets", "secret-store"],
    category: "generic",
    c4Classification: "container",
    icon: { id: "lock", source: "lucide" },
    protocols: ["HTTPS"],
    description: "Secrets management service"
  },
  {
    id: "search",
    name: "Search",
    aliases: ["search-engine", "full-text-search"],
    category: "generic",
    c4Classification: "container",
    icon: { id: "search", source: "lucide" },
    protocols: ["HTTPS", "REST"],
    description: "Search engine or service"
  },
  {
    id: "cron",
    name: "Cron Job",
    aliases: ["scheduler", "scheduled-task", "cron"],
    category: "generic",
    c4Classification: "component",
    icon: { id: "clock", source: "lucide" },
    protocols: [],
    description: "Scheduled job or cron task"
  },
  {
    id: "data-warehouse",
    name: "Data Warehouse",
    aliases: ["warehouse", "analytics-db"],
    category: "generic",
    c4Classification: "database",
    icon: { id: "database", source: "lucide" },
    protocols: ["HTTPS", "SQL"],
    description: "Data warehouse for analytics"
  },
  {
    id: "data-lake",
    name: "Data Lake",
    aliases: ["lake", "delta-lake"],
    category: "generic",
    c4Classification: "database",
    icon: { id: "database", source: "lucide" },
    protocols: ["HTTPS"],
    description: "Data lake for raw data storage"
  }
];
var technologies = [
  ...cloudProviders,
  ...awsServices,
  ...azureServices,
  ...gcpServices,
  ...kubernetesTech,
  ...containers,
  ...frontendTech,
  ...backendTech,
  ...databases,
  ...messaging,
  ...apiGateways,
  ...loadBalancers,
  ...authIdentity,
  ...securityTech,
  ...observability,
  ...storageTech,
  ...networkingTech,
  ...devopsCicd,
  ...genericComponents
];

// src/technology/registry.ts
var DEFAULT_CATEGORY_ORDER = [
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
  "generic"
];
var CATEGORY_INFO = {
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
  generic: { id: "generic", label: "Generic Components", description: "Generic architecture components", icon: "box", color: "#94a3b8", order: 20 }
};
var TechnologyRegistry = class {
  technologies = /* @__PURE__ */ new Map();
  aliasIndex = /* @__PURE__ */ new Map();
  // alias -> technology id
  labelIndex = /* @__PURE__ */ new Map();
  // normalized label -> technology id
  categoryIndex = /* @__PURE__ */ new Map();
  providerIndex = /* @__PURE__ */ new Map();
  config;
  constructor(config = {}) {
    this.config = {
      includeDeprecated: false,
      categoryOrder: DEFAULT_CATEGORY_ORDER,
      iconOverrides: {},
      ...config
    };
    this.initialize();
  }
  /**
   * Initialize the registry with built-in technology data
   */
  initialize() {
    for (const cat of DEFAULT_CATEGORY_ORDER) {
      this.categoryIndex.set(cat, /* @__PURE__ */ new Set());
    }
    for (const tech of technologies) {
      this.register(tech);
    }
  }
  /**
   * Register a technology in the registry
   */
  register(tech) {
    if (this.technologies.has(tech.id)) {
      console.warn(`Technology ${tech.id} already registered, skipping`);
      return;
    }
    if (this.config.iconOverrides[tech.id]) {
      tech.icon = this.config.iconOverrides[tech.id];
    }
    this.technologies.set(tech.id, tech);
    this.categoryIndex.get(tech.category)?.add(tech.id);
    if (tech.provider) {
      if (!this.providerIndex.has(tech.provider)) {
        this.providerIndex.set(tech.provider, /* @__PURE__ */ new Set());
      }
      this.providerIndex.get(tech.provider).add(tech.id);
    }
    for (const alias of tech.aliases) {
      const normalized = alias.toLowerCase().trim();
      this.aliasIndex.set(normalized, tech.id);
    }
    this.labelIndex.set(tech.name.toLowerCase().trim(), tech.id);
  }
  /**
   * Get technology by ID
   */
  get(id) {
    return this.technologies.get(id);
  }
  /**
   * Get technology by exact label match
   */
  getByLabel(label) {
    const normalized = label.toLowerCase().trim();
    const id = this.labelIndex.get(normalized);
    return id ? this.technologies.get(id) : void 0;
  }
  /**
   * Get technology by alias
   */
  getByAlias(alias) {
    const normalized = alias.toLowerCase().trim();
    const id = this.aliasIndex.get(normalized);
    return id ? this.technologies.get(id) : void 0;
  }
  /**
   * Get all technologies in a category
   */
  getByCategory(category) {
    const ids = this.categoryIndex.get(category) || /* @__PURE__ */ new Set();
    return Array.from(ids).map((id) => this.technologies.get(id)).filter((t) => this.config.includeDeprecated || !t.deprecated).sort((a, b) => a.name.localeCompare(b.name));
  }
  /**
   * Get all technologies by provider
   */
  getByProvider(provider) {
    const ids = this.providerIndex.get(provider) || /* @__PURE__ */ new Set();
    return Array.from(ids).map((id) => this.technologies.get(id)).filter((t) => this.config.includeDeprecated || !t.deprecated).sort((a, b) => a.name.localeCompare(b.name));
  }
  /**
   * Search technologies by query string
   */
  search(query) {
    const normalized = query.toLowerCase().trim();
    if (!normalized) return [];
    const results = /* @__PURE__ */ new Set();
    const byId = this.technologies.get(normalized);
    if (byId) results.add(byId);
    const byLabel = this.getByLabel(normalized);
    if (byLabel) results.add(byLabel);
    const byAlias = this.getByAlias(normalized);
    if (byAlias) results.add(byAlias);
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
  resolve(nodeId, nodeType, metadata) {
    const originalInput = metadata?.technology || metadata?.label || nodeId;
    if (metadata?.technology) {
      const tech = this.get(metadata.technology) || this.getByLabel(metadata.technology) || this.getByAlias(metadata.technology);
      if (tech) {
        return {
          technology: tech,
          resolutionSource: "explicit-metadata",
          confidence: 1,
          originalInput
        };
      }
    }
    if (metadata?.label) {
      const tech = this.getByLabel(metadata.label) || this.get(metadata.label) || this.getByAlias(metadata.label);
      if (tech) {
        return {
          technology: tech,
          resolutionSource: "exact-label",
          confidence: 0.95,
          originalInput
        };
      }
    }
    const techFromId = this.getByLabel(nodeId) || this.getByAlias(nodeId);
    if (techFromId) {
      return {
        technology: techFromId,
        resolutionSource: "normalized-label",
        confidence: 0.85,
        originalInput
      };
    }
    const idParts = nodeId.toLowerCase().split(/[-_]/);
    for (const part of idParts) {
      const byId = this.get(part);
      const byLabel = this.getByLabel(part);
      const byAlias = this.getByAlias(part);
      const tech = byId || byLabel || byAlias;
      if (tech) {
        return {
          technology: tech,
          resolutionSource: "alias",
          confidence: 0.75,
          originalInput
        };
      }
    }
    if (metadata?.label) {
      const composite = this.matchCompositeLabel(metadata.label);
      if (composite) {
        return {
          technology: composite,
          resolutionSource: "alias",
          confidence: 0.8,
          originalInput
        };
      }
    }
    const fallbackTech = this.getCategoryFallback(nodeType);
    if (fallbackTech) {
      return {
        technology: fallbackTech,
        resolutionSource: "category-fallback",
        confidence: 0.5,
        originalInput
      };
    }
    const genericTech = this.getGenericFallback(nodeType);
    return {
      technology: genericTech,
      resolutionSource: "generic-fallback",
      confidence: 0.3,
      originalInput
    };
  }
  /**
   * Composite label matcher.
   *
   * Resolves a label like "Postgres DB" → PostgreSQL when the label is a known
   * technology token plus one or more generic qualifier words. Never infers a
   * specific brand from a purely generic role ("service-1" stays generic).
   */
  matchCompositeLabel(label) {
    const GENERIC_QUALIFIERS2 = /* @__PURE__ */ new Set([
      "db",
      "database",
      "databases",
      "service",
      "services",
      "server",
      "servers",
      "cache",
      "caching",
      "cluster",
      "clusters",
      "instance",
      "instances",
      "runtime",
      "engine",
      "broker",
      "gw",
      "gateway",
      "api",
      "queue",
      "queues",
      "node",
      "nodes",
      "component",
      "components",
      "app",
      "web",
      "store",
      "storage",
      "message",
      "messaging",
      "stream",
      "streaming",
      "v1",
      "v2"
    ]);
    const words = label.toLowerCase().split(/[\s\-_]+/).filter((w) => w.length > 0);
    if (words.length < 2) return void 0;
    for (let i = 0; i < words.length; i++) {
      const techWord = words[i];
      const remaining = words.slice(0, i).concat(words.slice(i + 1));
      const allQualifiers = remaining.every((w) => GENERIC_QUALIFIERS2.has(w));
      if (!allQualifiers) continue;
      const tech = this.getByLabel(techWord) || this.get(techWord) || this.getByAlias(techWord);
      if (tech) return tech;
    }
    return void 0;
  }
  /**
   * Get category-appropriate fallback technology.
   *
   * IMPORTANT: generic roles resolve to GENERIC technologies, never to a
   * specific brand. e.g. nodeType "database" → generic "Database" (not
   * "PostgreSQL"), "cache" → generic "Cache" (not "Redis"). Specific-brand
   * resolution only happens via explicit metadata / label / alias matches.
   */
  getCategoryFallback(nodeType) {
    const fallbackMap = {
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
      subnet: "subnet"
    };
    const fallbackId = fallbackMap[nodeType.toLowerCase()];
    if (fallbackId) {
      const tech = this.get(fallbackId);
      if (tech) return tech;
    }
    const categoryMap = {
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
      subnet: "networking"
    };
    const category = categoryMap[nodeType.toLowerCase()];
    if (category) {
      const techs = this.getByCategory(category);
      if (techs.length > 0) return techs[0];
    }
    return void 0;
  }
  /**
   * Get the ultimate generic fallback for a node type.
   * Always returns a GENERIC technology — never a specific brand.
   */
  getGenericFallback(nodeType) {
    const genericMap = {
      ui: this.get("web-ui"),
      frontend: this.get("web-ui"),
      service: this.get("service"),
      microservice: this.get("microservice"),
      backend: this.get("service"),
      api: this.get("rest-api"),
      database: this.get("database"),
      db: this.get("database"),
      cache: this.get("cache"),
      queue: this.get("queue"),
      messaging: this.get("queue"),
      container: this.get("container-generic"),
      kubernetes: this.get("kubernetes"),
      k8s: this.get("kubernetes"),
      loadbalancer: this.get("loadbalancer"),
      gateway: this.get("gateway"),
      auth: this.get("auth"),
      monitoring: this.get("monitoring"),
      storage: this.get("database")
    };
    return genericMap[nodeType.toLowerCase()] || this.get("service");
  }
  /**
   * Get all registered technologies
   */
  getAll() {
    return Array.from(this.technologies.values()).filter((t) => this.config.includeDeprecated || !t.deprecated).sort((a, b) => a.name.localeCompare(b.name));
  }
  /**
   * Get all categories with technology counts
   */
  getCategories() {
    return DEFAULT_CATEGORY_ORDER.map((cat) => ({
      ...CATEGORY_INFO[cat],
      count: this.getByCategory(cat).length
    }));
  }
  /**
   * Get technology icon configuration
   */
  getIcon(techId) {
    const tech = this.get(techId);
    return tech?.icon;
  }
  /**
   * Check if a technology is deprecated
   */
  isDeprecated(techId) {
    return this.get(techId)?.deprecated === true;
  }
  /**
   * Get replacement for deprecated technology
   */
  getReplacement(techId) {
    const tech = this.get(techId);
    if (tech?.deprecated && tech.replacement) {
      return this.get(tech.replacement);
    }
    return void 0;
  }
  /**
   * Get total technology count
   */
  getCount() {
    return this.getAll().length;
  }
  /**
   * Update configuration
   */
  configure(config) {
    this.config = { ...this.config, ...config };
  }
};
var registryInstance = null;
function getTechnologyRegistry(config) {
  if (!registryInstance) {
    registryInstance = new TechnologyRegistry(config);
  }
  return registryInstance;
}

// src/enrichment/extract.ts
var MAX_WINDOW = 3;
var GENERIC_QUALIFIERS = /* @__PURE__ */ new Set([
  "db",
  "database",
  "databases",
  "service",
  "services",
  "server",
  "servers",
  "cache",
  "caching",
  "cluster",
  "clusters",
  "instance",
  "instances",
  "runtime",
  "engine",
  "broker",
  "gw",
  "gateway",
  "api",
  "queue",
  "queues",
  "node",
  "nodes",
  "component",
  "components",
  "app",
  "web",
  "store",
  "storage",
  "message",
  "messaging",
  "stream",
  "streaming",
  "frontend",
  "backend",
  "middleware",
  "layer",
  "storefront",
  "monolith",
  "service1",
  "service2",
  "v1",
  "v2"
]);
var HEDGE_PHRASES = [
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
  "or similar"
];
function normalizePhrase(phrase) {
  return phrase.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim().replace(/\s+/g, " ");
}
function tokenize(text) {
  const tokens = [];
  const re = /[a-z0-9]+/gi;
  let match;
  while ((match = re.exec(text)) !== null) {
    tokens.push({ word: match[0].toLowerCase(), start: match.index, end: match.index + match[0].length });
  }
  return tokens;
}
function buildPhraseIndex(techs, get) {
  const index = /* @__PURE__ */ new Map();
  const add = (phrase, technologyId) => {
    const norm = normalizePhrase(phrase);
    if (!norm) return;
    let set = index.get(norm);
    if (!set) {
      set = /* @__PURE__ */ new Set();
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
function findHedgeRanges(tokens) {
  const hedgeTokenArrays = HEDGE_PHRASES.map((phrase) => normalizePhrase(phrase).split(" ").filter(Boolean));
  const ranges = [];
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
function detectTechnologies(requirement, registry2) {
  const reg = registry2 ?? getTechnologyRegistry();
  const techs = reg.getAll();
  const index = buildPhraseIndex(techs, (id) => reg.get(id));
  const tokens = tokenize(requirement);
  if (tokens.length === 0) {
    return { detected: [], conflicts: [] };
  }
  const hedgeRanges = findHedgeRanges(tokens);
  const isHedged = (tokensStart, tokensEnd) => hedgeRanges.some(([a, b]) => b === tokensStart || a === tokensEnd);
  const mentions = [];
  const consumed = /* @__PURE__ */ new Set();
  for (let len = MAX_WINDOW; len >= 1; len--) {
    for (let i = 0; i + len <= tokens.length; i++) {
      const windowTokens = tokens.slice(i, i + len);
      if (windowTokens.some((_, offset) => consumed.has(i + offset))) continue;
      const phrase = windowTokens.map((token) => token.word).join(" ");
      const ids = index.get(normalizePhrase(phrase));
      if (!ids || ids.size === 0) continue;
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
  const conflicts = [];
  const bySpan = /* @__PURE__ */ new Map();
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
  const mentionsByTech = /* @__PURE__ */ new Map();
  for (const mention of mentions) {
    const list = mentionsByTech.get(mention.technologyId) ?? [];
    list.push(mention);
    mentionsByTech.set(mention.technologyId, list);
  }
  const detected = [];
  for (const [technologyId, list] of mentionsByTech) {
    const tech = list[0].tech;
    const hedged = list.some((m) => isHedged(m.tokensStart, m.tokensEnd));
    const snippets = list.map((m) => requirement.slice(m.start, m.end).trim());
    const positions = list.map((m) => ({ start: m.start, end: m.end }));
    detected.push({
      technologyId,
      technologyName: tech.name,
      source: list.some((m) => normalizePhrase(m.tech.name) === normalizePhrase(requirement.slice(m.start, m.end))) ? "explicit-user" : "deterministic-match",
      confidence: hedged ? "possible" : "confirmed",
      hedged,
      mentions: snippets,
      positions,
      category: tech.category,
      provider: tech.provider,
      protocols: tech.protocols
    });
  }
  detected.sort((a, b) => (a.positions[0]?.start ?? 0) - (b.positions[0]?.start ?? 0));
  return { detected, conflicts };
}

// src/enrichment/bind.ts
var NODE_TYPES_BY_CATEGORY = {
  databases: ["database"],
  cache: ["cache"],
  messaging: ["queue"],
  frontend: ["ui"],
  backend: ["service"],
  "api-gateway": ["service"],
  "load-balancing": ["service"],
  "auth-identity": ["service"],
  security: ["service"],
  observability: ["service"],
  storage: ["database"],
  cloud: ["service", "container"],
  aws: ["service", "container"],
  azure: ["service", "container"],
  gcp: ["service", "container"],
  kubernetes: ["service", "container"],
  containers: ["service", "container"],
  networking: ["service"],
  "devops-cicd": ["service"],
  generic: []
};
var AUTO_BIND_CATEGORIES = /* @__PURE__ */ new Set([
  "databases",
  "cache",
  "messaging",
  "frontend"
]);
function resolveTech(reg, idOrLabel) {
  return reg.get(idOrLabel) || reg.getByLabel(idOrLabel) || reg.getByAlias(idOrLabel);
}
function genericLabel(nodeId, nodeType, metadata) {
  if (metadata?.label && metadata.label.trim()) return metadata.label.trim();
  const match = nodeId.match(/^([a-z]+)-(\d+)$/i);
  if (match) {
    const typePart = match[1].toLowerCase();
    const numPart = match[2];
    const canonicalType = typePart === "ui" ? "UI" : typePart.charAt(0).toUpperCase() + typePart.slice(1);
    return `${canonicalType} ${numPart}`;
  }
  const fallbackType = nodeType.charAt(0).toUpperCase() + nodeType.slice(1);
  return fallbackType;
}
function bindTechnologies(detected, nodes2, manualAssignments, registry2) {
  const reg = registry2 ?? getTechnologyRegistry();
  const conflicts = [];
  const tentative = /* @__PURE__ */ new Map();
  const boundTechIds = /* @__PURE__ */ new Set();
  for (const category of AUTO_BIND_CATEGORIES) {
    const candidates = detected.filter(
      (d) => d.category === category && !d.hedged && d.confidence !== "possible"
    );
    if (candidates.length > 1) {
      const compatibleNodes = nodes2.some((node) => NODE_TYPES_BY_CATEGORY[category].includes(node.type));
      if (compatibleNodes) {
        conflicts.push({
          span: candidates[0].positions[0],
          technologyIds: candidates.map((c) => c.technologyId),
          reason: "coequal-category"
        });
      }
      continue;
    }
    if (candidates.length !== 1) continue;
    const tech = candidates[0];
    const compatible = nodes2.filter(
      (node) => NODE_TYPES_BY_CATEGORY[category].includes(node.type) && !tentative.has(node.id)
    );
    if (compatible.length === 1) {
      const node = compatible[0];
      tentative.set(node.id, {
        nodeId: node.id,
        technologyId: tech.technologyId,
        technologyName: tech.technologyName,
        source: tech.source,
        confidence: "confirmed",
        basis: "unique-cardinality",
        detectedId: tech.technologyId,
        evidenceText: tech.mentions[0] ?? tech.technologyName
      });
      boundTechIds.add(tech.technologyId);
    }
  }
  for (const node of nodes2) {
    if (tentative.has(node.id)) continue;
    const technology = node.metadata?.technology;
    if (!technology) continue;
    const tech = resolveTech(reg, technology);
    if (!tech) continue;
    tentative.set(node.id, {
      nodeId: node.id,
      technologyId: tech.id,
      technologyName: tech.name,
      source: "model-provided",
      confidence: "confirmed",
      basis: "model-metadata",
      evidenceText: technology
    });
    boundTechIds.add(tech.id);
  }
  const overriddenNodeIds = [];
  const final = /* @__PURE__ */ new Map();
  const manualNodeIds = new Set(Object.keys(manualAssignments));
  for (const node of nodes2) {
    if (manualNodeIds.has(node.id)) {
      const manual = manualAssignments[node.id];
      if (tentative.has(node.id)) overriddenNodeIds.push(node.id);
      final.set(node.id, {
        nodeId: node.id,
        technologyId: manual.technologyId,
        technologyName: manual.technologyName,
        source: "manual-user",
        confidence: "confirmed",
        basis: "manual-pick",
        evidenceText: "Manual assignment"
      });
      continue;
    }
    const auto = tentative.get(node.id);
    if (auto) final.set(node.id, auto);
  }
  const candidatesByNode = /* @__PURE__ */ new Map();
  const candidatePool = detected.filter((d) => !boundTechIds.has(d.technologyId));
  for (const node of nodes2) {
    if (final.has(node.id)) continue;
    const compatible = candidatePool.filter(
      (d) => NODE_TYPES_BY_CATEGORY[d.category].includes(node.type)
    );
    const distinctIds = Array.from(new Set(compatible.map((c) => c.technologyId)));
    const confidence = distinctIds.length > 1 ? "ambiguous" : "possible";
    candidatesByNode.set(
      node.id,
      compatible.map((tech) => ({
        technology: tech,
        confidence,
        basis: "manual-pick"
      }))
    );
  }
  const enrichedNodes = nodes2.map((node) => {
    const assignment = final.get(node.id) ?? null;
    const candidates = candidatesByNode.get(node.id) ?? [];
    return {
      nodeId: node.id,
      nodeType: node.type,
      raw: node,
      label: assignment ? assignment.technologyName : genericLabel(node.id, node.type, node.metadata),
      assignment,
      candidates,
      overriddenByManual: overriddenNodeIds.includes(node.id)
    };
  });
  const unplaced = detected.filter((d) => !boundTechIds.has(d.technologyId)).sort((a, b) => (a.positions[0]?.start ?? 0) - (b.positions[0]?.start ?? 0));
  return { enrichedNodes, unplaced, conflicts, overriddenNodeIds };
}

// src/enrichment/index.ts
function enrichArchitecture(requirement, architecture2, manualAssignments = {}) {
  const { detected, conflicts: detectConflicts } = detectTechnologies(requirement);
  const { enrichedNodes, unplaced, conflicts: bindConflicts, overriddenNodeIds } = bindTechnologies(
    detected,
    architecture2.nodes ?? [],
    manualAssignments
  );
  const merged = [];
  const seen = /* @__PURE__ */ new Set();
  for (const conflict of [...detectConflicts, ...bindConflicts]) {
    const key = `${conflict.span?.start ?? -1}:${conflict.span?.end ?? -1}:${conflict.reason}:${[...conflict.technologyIds].sort().join(",")}`;
    if (seen.has(key)) continue;
    seen.add(key);
    merged.push(conflict);
  }
  return {
    requirement,
    detected,
    enrichedNodes,
    unplaced,
    genericNodeIds: enrichedNodes.filter((node) => node.assignment === null).map((node) => node.nodeId),
    conflicts: merged,
    builtAt: Date.now()
  };
}

// src/enrichment/acceptance.test.ts
var passed = 0;
var failed = 0;
function assert(condition, message) {
  if (condition) {
    passed += 1;
    return;
  }
  failed += 1;
  console.error(`FAIL: ${message}`);
  throw new Error(`Assertion failed: ${message}`);
}
function test(name, fn) {
  try {
    fn();
    console.log(` PASS  ${name}`);
  } catch (error) {
    console.error(` FAIL  ${name} \u2014 ${error.message}`);
  }
}
function nodes(...pairs) {
  return pairs.map(([id, type]) => ({ id, type }));
}
function architecture(nodeList) {
  return { nodes: nodes(...nodeList), edges: [] };
}
var registry = getTechnologyRegistry();
test('detect: "postgres" \u2192 PostgreSQL', () => {
  const { detected } = detectTechnologies("Use postgres for the database.");
  const pg = detected.find((d) => d.technologyId === "postgresql");
  assert(!!pg, "postgresql should be detected");
  assert(pg.technologyName === "PostgreSQL", "technologyName is PostgreSQL");
  assert(pg.source === "deterministic-match", "alias match is deterministic-match");
  assert(pg.confidence === "confirmed", "alias match is confirmed");
});
test('detect: "postgres database" \u2192 PostgreSQL (role folding)', () => {
  const { detected } = detectTechnologies("Store events in a postgres database.");
  const pg = detected.find((d) => d.technologyId === "postgresql");
  assert(!!pg, "postgresql should be detected");
  assert(pg.mentions.some((m) => m.toLowerCase().includes("database")), "qualifier folded into mention");
});
test('detect: "s3" \u2192 Amazon S3', () => {
  const { detected } = detectTechnologies("Persist media to s3.");
  const s3 = detected.find((d) => d.technologyId === "amazons3");
  assert(!!s3, "amazons3 should be detected");
  assert(s3.technologyName === "Amazon S3", "technologyName is Amazon S3");
});
test('detect: "aws s3" \u2192 Amazon S3 (provider compound)', () => {
  const { detected } = detectTechnologies("Store files in aws s3 buckets.");
  const s3 = detected.find((d) => d.technologyId === "amazons3");
  assert(!!s3, "amazons3 should be detected via provider compound");
  assert(s3.technologyName === "Amazon S3", "technologyName is Amazon S3");
});
test('detect: "React frontend" \u2192 React (label + role folding)', () => {
  const { detected } = detectTechnologies("Build the React frontend with a SPA.");
  const react = detected.find((d) => d.technologyId === "react");
  assert(!!react, "react should be detected");
  assert(react.source === "explicit-user", "canonical label is explicit-user");
  assert(react.mentions.some((m) => m.toLowerCase().includes("frontend")), "frontend folded into mention");
});
test('detect: "MySQL or MariaDB" \u2192 ambiguous, no fabricated single claim', () => {
  const { detected, conflicts } = detectTechnologies("Use MySQL or MariaDB.");
  const mysql = detected.find((d) => d.technologyId === "mysql");
  const mariadb = detected.find((d) => d.technologyId === "mariadb");
  assert(!!mysql, "mysql detected");
  assert(!!mariadb, "mariadb detected");
  assert(conflicts.length > 0, "overlapping/coequal conflict recorded");
});
test('detect: "SQL database" \u2192 no technology detected', () => {
  const { detected } = detectTechnologies("A SQL database for reporting.");
  assert(detected.length === 0, "no technology should be detected for a generic SQL database");
});
test('detect: "database compatible with PostgreSQL" \u2192 hedged, not confirmed', () => {
  const { detected } = detectTechnologies("A database compatible with PostgreSQL.");
  const pg = detected.find((d) => d.technologyId === "postgresql");
  assert(!!pg, "postgresql mention is still visible");
  assert(pg.hedged === true, "mention is hedged");
  assert(pg.confidence === "possible", "hedged mention is possible, not confirmed");
});
test("detect: duplicate mentions collapse to one DetectedTechnology", () => {
  const { detected } = detectTechnologies("PostgreSQL powers A. PostgreSQL also powers B.");
  const pg = detected.filter((d) => d.technologyId === "postgresql");
  assert(pg.length === 1, "single DetectedTechnology");
  assert(pg[0].mentions.length === 2, "both mentions recorded");
  assert(pg[0].source === "explicit-user", "canonical label \u2192 explicit-user");
});
test("detect: unregistered terms never produce identities", () => {
  const { detected } = detectTechnologies("Use SuperDB and a MegaQueue to scale.");
  assert(detected.length === 0, "nothing fabricated for unknown jargon");
});
test("bind: single database node + single database tech \u2192 confirmed unique-cardinality", () => {
  const { detected } = detectTechnologies("Persist to Postgres.");
  const result = bindTechnologies(detected, nodes(["database-1", "database"]), {});
  const db = result.enrichedNodes.find((n) => n.nodeId === "database-1");
  assert(db.assignment?.technologyId === "postgresql", "database-1 bound to postgresql");
  assert(db.assignment?.basis === "unique-cardinality" && db.assignment?.confidence === "confirmed", "confirmed unique-cardinality");
  assert(result.unplaced.length === 0, "tech placed");
});
test("bind: technology mentioned but no compatible node \u2192 detected but unplaced", () => {
  const { detected } = detectTechnologies("Cache everything in Redis.");
  const result = bindTechnologies(detected, nodes(["service-1", "service"]), {});
  const cache = result.enrichedNodes.find((n) => n.nodeId === "service-1");
  assert(cache.assignment === null, "no cache node \u2192 no assignment");
  assert(result.unplaced.some((u) => u.technologyId === "redis"), "redis reported unplaced");
});
test("bind: multiple compatible service nodes \u2192 candidates, never arbitrary binding", () => {
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
  const db = result.enrichedNodes.find((n) => n.nodeId === "database-1");
  assert(db.assignment === null, "hedged postgresql not claimed");
  assert(result.unplaced.some((u) => u.technologyId === "postgresql"), "hedged mention still visible as unplaced");
});
test("bind: MySQL or MariaDB \u2192 ambiguous, no automatic assignment", () => {
  const { detected } = detectTechnologies("Use MySQL or MariaDB.");
  const result = bindTechnologies(detected, nodes(["database-1", "database"]), {});
  const db = result.enrichedNodes.find((n) => n.nodeId === "database-1");
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
  assert(byId.get("ui-1").assignment?.technologyId === "react", "ui-1 \u2190 React");
  assert(byId.get("database-1").assignment?.technologyId === "postgresql", "database-1 \u2190 PostgreSQL");
  assert(byId.get("cache-1").assignment?.technologyId === "redis", "cache-1 \u2190 Redis");
  assert(["service-1"].every((id) => byId.get(id).assignment === null), "services stay generic");
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
  assert(byId.get("ui-1").assignment?.technologyId === "react", "ui-1 \u2190 React");
  assert(byId.get("database-1").assignment?.technologyId === "postgresql", "database-1 \u2190 PostgreSQL");
  assert(byId.get("cache-1").assignment?.technologyId === "redis", "cache-1 \u2190 Redis");
  for (const id of ["service-1", "service-2", "service-3"]) {
    assert(byId.get(id).assignment === null, `${id} stays generic`);
    assert(byId.get(id).candidates.some((c) => c.technology.technologyId === "fastapi"), `fastapi candidate on ${id}`);
  }
  assert(result.unplaced.some((u) => u.technologyId === "fastapi"), "fastapi unplaced");
});
test("bind: manual assignment wins and overrides auto-bind", () => {
  const { detected } = detectTechnologies("Persist to Postgres.");
  const result = bindTechnologies(detected, nodes(["database-1", "database"]), {
    "database-1": { technologyId: "mongodb", technologyName: "MongoDB" }
  });
  const db = result.enrichedNodes.find((n) => n.nodeId === "database-1");
  assert(db.assignment?.technologyId === "mongodb", "manual assignment wins");
  assert(db.assignment?.source === "manual-user" && db.assignment?.basis === "manual-pick", "manual provenance");
  assert(db.overriddenByManual === true, "auto-bind marked overridden");
});
test("bind: manual assignment clears via missing entry (reset)", () => {
  const { detected } = detectTechnologies("Persist to Postgres.");
  const manual = {};
  const result = bindTechnologies(detected, nodes(["database-1", "database"]), manual);
  const db = result.enrichedNodes.find((n) => n.nodeId === "database-1");
  assert(db.assignment?.technologyId === "postgresql", "postgresql restored after reset");
});
test("facade: no fabricated nodes \u2014 enriched count equals generated count", () => {
  const arch = architecture([["service-1", "service"], ["database-1", "database"]]);
  const enriched = enrichArchitecture("Use PostgreSQL.", arch);
  assert(enriched.enrichedNodes.length === 2, "same node count");
  for (const en of enriched.enrichedNodes) {
    assert(arch.nodes.some((n) => n.id === en.nodeId), "each enriched node exists in generated graph");
  }
});
test("facade: no fabricated technology identities \u2014 every assignment is registered", () => {
  const arch = architecture([["database-1", "database"], ["cache-1", "cache"]]);
  const enriched = enrichArchitecture("Use PostgreSQL and Redis.", arch);
  for (const en of enriched.enrichedNodes) {
    if (en.assignment) {
      assert(!!registry.get(en.assignment.technologyId), `registered technology: ${en.assignment.technologyId}`);
      assert(en.label === en.assignment.technologyName, "enriched label uses registry name");
    }
  }
});
test("facade: security independence \u2014 enrichment never touches security", () => {
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
console.log(`
${passed} assertions passed, ${failed} failed.`);
if (failed > 0) {
  console.error("ENRICHMENT TESTS FAILED");
  throw new Error("Enrichment acceptance tests failed");
}
console.log("ALL ENRICHMENT TESTS PASSED");
