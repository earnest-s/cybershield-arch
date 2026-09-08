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
      const tech = this.getByLabel(metadata.label);
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
      const tech = this.getByAlias(part);
      if (tech) {
        return {
          technology: tech,
          resolutionSource: "alias",
          confidence: 0.75,
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
   * Get category-appropriate fallback technology
   */
  getCategoryFallback(nodeType) {
    const fallbackMap = {
      ui: "web-ui",
      frontend: "web-ui",
      service: "service",
      microservice: "microservice",
      backend: "service",
      api: "rest-api",
      database: "postgresql",
      db: "postgresql",
      cache: "redis",
      queue: "kafka",
      messaging: "kafka",
      container: "docker",
      kubernetes: "kubernetes",
      k8s: "kubernetes",
      loadbalancer: "nginx",
      gateway: "kong",
      "api-gateway": "kong",
      auth: "keycloak",
      identity: "keycloak",
      monitoring: "prometheus",
      logging: "elasticsearch",
      tracing: "jaeger",
      storage: "s3",
      cdn: "cloudflare",
      firewall: "aws-waf",
      vpc: "aws-vpc",
      subnet: "aws-subnet"
    };
    const fallbackId = fallbackMap[nodeType.toLowerCase()];
    if (fallbackId) {
      return this.get(fallbackId);
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
   * Get generic fallback for node type
   */
  getGenericFallback(nodeType) {
    const genericMap = {
      ui: this.get("web-ui"),
      service: this.get("service"),
      microservice: this.get("microservice"),
      backend: this.get("service"),
      api: this.get("rest-api"),
      database: this.get("postgresql"),
      db: this.get("postgresql"),
      cache: this.get("redis"),
      queue: this.get("kafka"),
      container: this.get("docker"),
      kubernetes: this.get("kubernetes"),
      k8s: this.get("kubernetes"),
      loadbalancer: this.get("nginx"),
      gateway: this.get("kong"),
      auth: this.get("keycloak"),
      monitoring: this.get("prometheus"),
      storage: this.get("s3")
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
function resolveTechnology(nodeId, nodeType, metadata) {
  return getTechnologyRegistry().resolve(nodeId, nodeType, metadata);
}
function searchTechnologies(query) {
  return getTechnologyRegistry().search(query);
}

// src/technology/TechnologyIcon.tsx
import React, { useMemo } from "react";

// src/technology/iconIndex.ts
import {
  siAmazon,
  siApachekafka,
  siApachepulsar,
  siApacherocketmq,
  siApachecassandra,
  siApacheflink,
  siApache,
  siAmazonapigateway,
  siAmazoncloudwatch,
  siAmazoncognito,
  siAmazondocumentdb,
  siAmazondynamodb,
  siAmazonecs,
  siAmazoneks,
  siAmazonelasticache,
  siAmazoniam,
  siAmazonrds,
  siAmazonredshift,
  siAmazons3,
  siAmazonsqs,
  siAngular,
  siAnsible,
  siAuth0,
  siAwselasticloadbalancing,
  siAwsfargate,
  siAwslambda,
  siAwssecretsmanager,
  siClickhouse,
  siCloudflare,
  siDatabricks,
  siDatadog,
  siDigitalocean,
  siDjango,
  siDocker,
  siDotnet,
  siElasticsearch,
  siExpress,
  siFastapi,
  siFlask,
  siFlux,
  siGithubactions,
  siGitlab,
  siGo,
  siGooglebigquery,
  siGooglecloud,
  siGooglecloudstorage,
  siGooglepubsub,
  siGrafana,
  siGraphql,
  siHeroku,
  siIstio,
  siJaeger,
  siJenkins,
  siJavascript,
  siKeycloak,
  siKibana,
  siKong,
  siKubernetes,
  siLinkerd,
  siMariadb,
  siMongodb,
  siMysql,
  siNatsdotio,
  siNginx,
  siNewrelic,
  siNodedotjs,
  siOkta,
  siOpentelemetry,
  siOpenvpn,
  siOracle,
  siPhp,
  siPostgresql,
  siPrometheus,
  siRabbitmq,
  siReact,
  siRedis,
  siRubyonrails,
  siRuby,
  siRust,
  siSnowflake,
  siSnyk,
  siSonarqube,
  siSplunk,
  siSpring,
  siSvelte,
  siSwagger,
  siTailwindcss,
  siTerraform,
  siTimescale,
  siTraefikproxy,
  siTrivy,
  siTypescript,
  siVault,
  siVictoriametrics,
  siVite,
  siVuedotjs,
  siWebpack,
  siWireguard
} from "simple-icons";
function icon(value) {
  if (!value || !value.path) return null;
  return { title: value.title, path: value.path };
}
var SIMPLE_ICON_INDEX = {
  amazon: icon(siAmazon),
  amazonapigateway: icon(siAmazonapigateway),
  amazoncloudwatch: icon(siAmazoncloudwatch),
  amazoncognito: icon(siAmazoncognito),
  amazondocumentdb: icon(siAmazondocumentdb),
  amazondynamodb: icon(siAmazondynamodb),
  amazonecs: icon(siAmazonecs),
  amazoneks: icon(siAmazoneks),
  amazonelasticache: icon(siAmazonelasticache),
  amazoniam: icon(siAmazoniam),
  amazonrds: icon(siAmazonrds),
  amazonredshift: icon(siAmazonredshift),
  amazons3: icon(siAmazons3),
  amazonsqs: icon(siAmazonsqs),
  angular: icon(siAngular),
  ansible: icon(siAnsible),
  apache: icon(siApache),
  apachecassandra: icon(siApachecassandra),
  apacheflink: icon(siApacheflink),
  apachekafka: icon(siApachekafka),
  apachepulsar: icon(siApachepulsar),
  apacherocketmq: icon(siApacherocketmq),
  auth0: icon(siAuth0),
  awselasticloadbalancing: icon(siAwselasticloadbalancing),
  awsfargate: icon(siAwsfargate),
  awslambda: icon(siAwslambda),
  awssecretsmanager: icon(siAwssecretsmanager),
  clickhouse: icon(siClickhouse),
  cloudflare: icon(siCloudflare),
  databricks: icon(siDatabricks),
  datadog: icon(siDatadog),
  digitalocean: icon(siDigitalocean),
  django: icon(siDjango),
  docker: icon(siDocker),
  dotnet: icon(siDotnet),
  elasticsearch: icon(siElasticsearch),
  express: icon(siExpress),
  fastapi: icon(siFastapi),
  flask: icon(siFlask),
  flux: icon(siFlux),
  githubactions: icon(siGithubactions),
  gitlab: icon(siGitlab),
  go: icon(siGo),
  googlebigquery: icon(siGooglebigquery),
  googlecloud: icon(siGooglecloud),
  googlecloudstorage: icon(siGooglecloudstorage),
  googlepubsub: icon(siGooglepubsub),
  grafana: icon(siGrafana),
  graphql: icon(siGraphql),
  heroku: icon(siHeroku),
  istio: icon(siIstio),
  jaeger: icon(siJaeger),
  javascript: icon(siJavascript),
  jenkins: icon(siJenkins),
  keycloak: icon(siKeycloak),
  kibana: icon(siKibana),
  kong: icon(siKong),
  kubernetes: icon(siKubernetes),
  linkerd: icon(siLinkerd),
  mariadb: icon(siMariadb),
  mongodb: icon(siMongodb),
  mysql: icon(siMysql),
  natsdotio: icon(siNatsdotio),
  nginx: icon(siNginx),
  newrelic: icon(siNewrelic),
  nodedotjs: icon(siNodedotjs),
  okta: icon(siOkta),
  opentelemetry: icon(siOpentelemetry),
  openvpn: icon(siOpenvpn),
  oracle: icon(siOracle),
  php: icon(siPhp),
  postgresql: icon(siPostgresql),
  prometheus: icon(siPrometheus),
  rabbitmq: icon(siRabbitmq),
  react: icon(siReact),
  redis: icon(siRedis),
  rubyonrails: icon(siRubyonrails),
  ruby: icon(siRuby),
  rust: icon(siRust),
  snowflake: icon(siSnowflake),
  snyk: icon(siSnyk),
  sonarqube: icon(siSonarqube),
  splunk: icon(siSplunk),
  spring: icon(siSpring),
  svelte: icon(siSvelte),
  swagger: icon(siSwagger),
  tailwindcss: icon(siTailwindcss),
  terraform: icon(siTerraform),
  timescale: icon(siTimescale),
  traefikproxy: icon(siTraefikproxy),
  trivy: icon(siTrivy),
  typescript: icon(siTypescript),
  vault: icon(siVault),
  victoriametrics: icon(siVictoriametrics),
  vite: icon(siVite),
  vuedotjs: icon(siVuedotjs),
  webpack: icon(siWebpack),
  wireguard: icon(siWireguard)
};

// src/technology/iconLookup.ts
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
  MessageSquare
} from "lucide-react";

// src/technology/TechnologyNodePresentation.tsx
import React2 from "react";

// src/technology/TechnologyPalette.tsx
import React3, { useMemo as useMemo3, useState } from "react";
import { Search as Search2, X, ChevronDown, Star, Filter } from "lucide-react";

// src/technology/protocols.ts
var PROTOCOLS = [
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
  { id: "CQL", name: "CQL", defaultPort: 9042, encryptedByDefault: false }
];
var PROTOCOL_MAP = new Map(
  PROTOCOLS.map((p) => [p.id.toLowerCase(), p])
);
var RELATIONSHIPS = [
  { id: "sync", label: "Synchronous", asynchronous: false, description: "Direct request/response call" },
  { id: "async", label: "Asynchronous", asynchronous: true, description: "Non-blocking call" },
  { id: "event", label: "Event", asynchronous: true, description: "Event-driven communication" },
  { id: "replication", label: "Replication", asynchronous: true, description: "Data replication" },
  { id: "auth", label: "Auth", asynchronous: false, description: "Authentication/authorization" },
  { id: "data-flow", label: "Data Flow", asynchronous: false, description: "Data transfer" },
  { id: "dns", label: "DNS", asynchronous: false, description: "Domain name resolution" },
  { id: "unknown", label: "Unknown", asynchronous: false, description: "Relationship type not specified" }
];
var RELATIONSHIP_MAP = new Map(
  RELATIONSHIPS.map((r) => [r.id.toLowerCase(), r])
);

// ../../../../../tmp/opencode/tech-test.ts
var registry = getTechnologyRegistry();
var all = registry.getAll();
console.log("=== REGISTRY STATS ===");
console.log("Total non-deprecated:", registry.getCount());
console.log("Total raw (incl deprecated):", all.length);
var byCat = /* @__PURE__ */ new Map();
for (const t of all) byCat.set(t.category, (byCat.get(t.category) || 0) + 1);
console.log("\nCategory counts:");
for (const [c, n] of Array.from(byCat.entries()).sort()) console.log(`  ${c}: ${n}`);
var ownIconBySI = 0;
var byLucide = 0;
var missing = 0;
for (const t of all) {
  if (t.icon.source === "simple-icons") ownIconBySI++;
  else if (t.icon.source === "lucide") byLucide++;
  else missing++;
}
console.log("\nIcon configs: simple-icons:", ownIconBySI, " lucide:", byLucide, " other:", missing);
console.log("\n=== RESOLUTION TESTS ===");
function show(label, r) {
  console.log(`  ${label} -> ${r.technology.name} [${r.resolutionSource}]`);
}
show("explicit 'postgresql'", resolveTechnology("x", "service", { technology: "postgresql" }));
show("label 'PostgreSQL'", resolveTechnology("x", "database", { label: "PostgreSQL" }));
show("label 'Postgres DB'", resolveTechnology("x", "database", { label: "Postgres DB" }));
show("role 'database'", resolveTechnology("service-1", "database", {}));
show("generic 'service-1'", resolveTechnology("service-1", "service", {}));
show("generic 'ui-1'", resolveTechnology("ui-1", "ui", {}));
show("by id 'postgresql-1'", resolveTechnology("postgresql-1", "service", {}));
console.log("\n=== SEARCH ===");
console.log("  'postgres':", searchTechnologies("postgres").map((t) => t.name).join(", "));
console.log("  'k8s':", searchTechnologies("k8s").map((t) => t.name).join(", "));
console.log("  'db':", searchTechnologies("db").slice(0, 10).map((t) => t.name).join(", "));
console.log("  'azure':", searchTechnologies("azure").slice(0, 5).map((t) => t.name).join(", "));
