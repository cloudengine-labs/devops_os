---
title: "Cloud-Based Platform Engineering"
description: "Multi-cloud abstractions, serverless patterns, and FinOps integration for cloud-native platform engineering."
weight: 30
---

# Cloud-Based Platform Engineering

Cloud-native platform engineering extends beyond Kubernetes to include managed services, serverless computing, and cloud-specific operational patterns. This document covers multi-cloud strategies, serverless architectures, and financial operations integration.

## Multi-Cloud Abstraction Layer

### Challenge: Cloud Lock-in

Each cloud provider has proprietary services:
- **AWS**: EC2, S3, RDS, Lambda, DynamoDB, Route53
- **Azure**: VMs, Blob Storage, SQL Database, Azure Functions, CosmosDB, Traffic Manager
- **GCP**: Compute Engine, Cloud Storage, Cloud SQL, Cloud Functions, Firestore, Cloud Load Balancing

Organizations want portability without recreating infrastructure for each cloud.

### Solution: Cloud-Agnostic Templates

```
┌─────────────────────────────────────────────────────┐
│ Application Intent Layer                             │
│ "Deploy a REST API with 99.9% availability"         │
│ + "Store data in managed database"                  │
│ + "Serve static assets from CDN"                    │
├─────────────────────────────────────────────────────┤
│ Cloud Abstraction Layer (Terraform)                 │
│ ├── AWS: Lambda + RDS + CloudFront                  │
│ ├── Azure: Azure Functions + SQL Database + CDN     │
│ └── GCP: Cloud Functions + Cloud SQL + Cloud CDN    │
├─────────────────────────────────────────────────────┤
│ Cloud Provider APIs                                  │
└─────────────────────────────────────────────────────┘
```

### Terraform Module Strategy

```hcl
# modules/rest-api/main.tf
# Abstract REST API that works on any cloud

variable "cloud_provider" {
  type = string
  validation {
    condition     = contains(["aws", "azure", "gcp"], var.cloud_provider)
    error_message = "Must be aws, azure, or gcp"
  }
}

module "api_compute" {
  source = "./compute/${var.cloud_provider}"
  
  name             = var.api_name
  runtime          = "python39"
  memory_mb        = 1024
  timeout_seconds  = 30
}

module "database" {
  source = "./database/${var.cloud_provider}"
  
  name     = var.db_name
  engine   = "postgres"
  version  = "14"
  instance_class = "small"
}

module "cdn" {
  source = "./cdn/${var.cloud_provider}"
  
  origin        = module.api_compute.url
  cache_ttl_s   = 3600
}

output "api_endpoint" {
  value = module.api_compute.url
}

output "database_host" {
  value = module.database.host
}

output "cdn_url" {
  value = module.cdn.url
}
```

**Usage**:
```bash
# Deploy to AWS
terraform apply -var cloud_provider=aws

# Deploy to Azure
terraform apply -var cloud_provider=azure

# Deploy to GCP
terraform apply -var cloud_provider=gcp
```

### Container Registry Abstraction

```yaml
# GitOps manifest works with any registry
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-service
spec:
  template:
    spec:
      containers:
      - image: ${REGISTRY}/${ORG}/api-service:${TAG}
        # Registry is injected based on cloud:
        # AWS: 123456789.dkr.ecr.us-east-1.amazonaws.com/myorg/api-service:v1
        # Azure: myregistry.azurecr.io/myorg/api-service:v1
        # GCP: gcr.io/myproject/myorg/api-service:v1
```

---

## Serverless Patterns

### When to Use Serverless

| Use Case | Ideal | Consider | Avoid |
|----------|-------|----------|-------|
| REST API | ✅ | ✅ | ❌ |
| Event-driven job | ✅ | ✅ | |
| Batch processing | | ✅ | |
| Long-running service | ❌ | | ❌ |
| High-throughput streaming | ❌ | | ❌ |
| Real-time interactive | | ✅ | |

### Serverless Template: REST API + Event Handler

**Deployment Pattern**:
```
┌───────────────────────────────────────────┐
│ API Gateway (public endpoint)              │
├───────────────────────────────────────────┤
│ └──→ Lambda Function 1 (compute)          │
│     └──→ RDS Database                     │
│     └──→ S3 Storage                       │
│     └──→ EventBridge (async)              │
│                                           │
│ EventBridge Rule (on events)              │
│ └──→ Lambda Function 2 (processing)       │
│     └──→ DynamoDB                         │
│     └──→ SQS (queueing)                   │
│                                           │
│ Lambda Function 3 (queue worker)          │
│ └──→ External API call                    │
│ └──→ Webhook callback                     │
└───────────────────────────────────────────┘
```

**Terraform Template**:
```hcl
module "api_lambda" {
  source = "./modules/lambda-function"
  
  name           = "payment-api"
  runtime        = "python39"
  handler        = "index.handler"
  source_file    = "src/payment_api.py"
  environment = {
    DB_HOST = module.database.host
    S3_BUCKET = module.storage.bucket
  }
}

module "api_gateway" {
  source = "./modules/api-gateway"
  
  name            = "payment-api"
  target_lambda   = module.api_lambda.arn
  routes = {
    "POST /payments"       = module.api_lambda.arn
    "GET /payments/{id}"   = module.api_lambda.arn
    "POST /refunds"        = module.api_lambda.arn
  }
}

module "event_handler" {
  source = "./modules/lambda-function"
  
  name    = "payment-events-handler"
  runtime = "python39"
  handler = "index.handler"
  source_file = "src/event_handler.py"
}

module "event_rule" {
  source = "./modules/eventbridge-rule"
  
  name            = "payment-completed"
  pattern = {
    source      = ["custom.payments"]
    detail-type = ["paymentCompleted"]
  }
  target_lambda = module.event_handler.arn
}
```

### Event-Driven Architecture

```yaml
# AWS EventBridge Rules (Terraform)
resource "aws_cloudwatch_event_rule" "payment_completed" {
  name        = "payment-completed-rule"
  description = "Trigger when payment completes"
  
  event_pattern = jsonencode({
    source      = ["custom.payments"]
    detail-type = ["paymentCompleted"]
    detail = {
      status = ["SUCCESS"]
    }
  })
}

resource "aws_cloudwatch_event_target" "invoice_generator" {
  rule      = aws_cloudwatch_event_rule.payment_completed.name
  arn       = aws_lambda_function.invoice_generator.arn
  role_arn  = aws_iam_role.eventbridge.arn
}

resource "aws_cloudwatch_event_target" "send_confirmation" {
  rule      = aws_cloudwatch_event_rule.payment_completed.name
  arn       = aws_sqs_queue.email_queue.arn
  role_arn  = aws_iam_role.eventbridge.arn
}
```

---

## FinOps Integration: Cost Awareness in Platform

### Cost Awareness at Every Layer

```
┌─────────────────────────────────────────────────────┐
│ Application Layer                                    │
│ ├── Memory allocation (128MB → 10GB Lambda)         │
│ ├── Compute type (general, GPU, ARM)                │
│ └── Auto-scaling rules (min/max replicas)           │
├─────────────────────────────────────────────────────┤
│ Infrastructure Layer                                 │
│ ├── Instance type (t3.micro, c5.2xlarge)           │
│ ├── Reservation vs. on-demand pricing               │
│ └── Regional cost variance (us-east vs eu-west)     │
├─────────────────────────────────────────────────────┤
│ Data Layer                                           │
│ ├── Data storage class (hot, warm, cold)            │
│ ├── Data transfer costs (inter-region, egress)      │
│ └── Backup retention policies                       │
├─────────────────────────────────────────────────────┤
│ Operations Layer                                     │
│ ├── API call costs (AWS API Gateway, DataTransfer)  │
│ ├── Logging and monitoring costs                    │
│ └── Support plan costs                              │
└─────────────────────────────────────────────────────┘
```

### Cost-Aware Template Design

**Example: Database Right-Sizing**

```hcl
variable "data_storage_gb" {
  type = number
  description = "Expected data storage needs"
}

variable "query_throughput_rps" {
  type = number
  description = "Expected queries per second"
}

# Automatically select instance size based on needs
locals {
  instance_class = (
    var.query_throughput_rps < 100 && var.data_storage_gb < 100 ? "db.t3.micro" :
    var.query_throughput_rps < 500 && var.data_storage_gb < 500 ? "db.t3.small" :
    var.query_throughput_rps < 2000 && var.data_storage_gb < 1000 ? "db.m5.large" :
    "db.m5.2xlarge"
  )
  
  estimated_monthly_cost = (
    local.instance_class == "db.t3.micro" ? 15 :
    local.instance_class == "db.t3.small" ? 30 :
    local.instance_class == "db.m5.large" ? 200 :
    500
  )
}

module "database" {
  source = "./modules/rds"
  
  instance_class = local.instance_class
  # Notify team of estimated cost
  tags = {
    "estimated-monthly-cost" = local.estimated_monthly_cost
  }
}

output "cost_warning" {
  value = local.estimated_monthly_cost > 100 ? "⚠️  High estimated cost: $${local.estimated_monthly_cost}/month" : ""
}
```

### FinOps Dashboard Template

**Prometheus Metrics**:
```yaml
# Scrape cloud cost APIs
- job_name: 'finops'
  scrape_interval: 6h  # Cost data updated daily
  
  relabel_configs:
  - source_labels: [__address__]
    target_label: __param_target
  - source_labels: [__param_target]
    target_label: instance
  - target_label: __address__
    replacement: localhost:9090
```

**Grafana Dashboard**:
```json
{
  "dashboard": {
    "title": "FinOps Dashboard",
    "panels": [
      {
        "title": "Monthly Cost Trend",
        "targets": [{"expr": "increase(cloud_monthly_cost_usd[30d])"}]
      },
      {
        "title": "Cost by Service",
        "targets": [{"expr": "cloud_monthly_cost_usd by (service)"}]
      },
      {
        "title": "Cost per User/Request",
        "targets": [{"expr": "cloud_monthly_cost_usd / app_requests_total"}]
      },
      {
        "title": "Budget vs. Actual",
        "targets": [
          {"expr": "cloud_monthly_cost_usd", "legendFormat": "Actual"},
          {"expr": "cloud_budget_usd", "legendFormat": "Budget"}
        ]
      }
    ]
  }
}
```

### Cost Optimization Policies

```yaml
# Kyverno policy: Enforce resource requests/limits
# (prevents over-provisioning)
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-resource-limits
spec:
  validationFailureAction: audit
  rules:
  - name: cpu-and-memory-limits
    match:
      resources:
        kinds:
        - Pod
    validate:
      message: "CPU and memory limits required"
      pattern:
        spec:
          containers:
          - resources:
              limits:
                memory: "?*"
                cpu: "?*"
              requests:
                memory: "?*"
                cpu: "?*"
```

---

## Multi-Region Deployment Strategy

### Regional Cost Considerations

```
┌─────────────────────────────────────────────┐
│ Region Selection                             │
├─────────────────────────────────────────────┤
│ AWS us-east-1     (Ohio)    - ✅ Cheap      │
│ AWS eu-west-1     (Ireland) - €€ Moderate   │
│ AWS ap-southeast-1 (Singapore) - €€€ Expensive
│                                             │
│ Data transfer costs (EGRESS):               │
│ us-east-1 → eu-west-1: $0.02 per GB        │
│ us-east-1 → ap-southeast-1: $0.05 per GB   │
└─────────────────────────────────────────────┘
```

### Multi-Region Template

```hcl
variable "regions" {
  type = map(object({
    primary = bool
    cost_factor = number  # Relative cost (1.0 = baseline)
  }))
  default = {
    "us-east-1" = { primary = true, cost_factor = 1.0 }
    "eu-west-1" = { primary = true, cost_factor = 1.1 }
    "ap-southeast-1" = { primary = false, cost_factor = 1.3 }
  }
}

module "deployment" {
  for_each = var.regions
  
  source = "./modules/regional-deployment"
  
  region = each.key
  replicas = each.value.primary ? 3 : 1  # Primary has more replicas
  
  # Right-size based on regional cost
  instance_type = (
    each.value.cost_factor > 1.2 ? "t3.micro" :
    each.value.cost_factor > 1.1 ? "t3.small" :
    "t3.medium"
  )
  
  tags = {
    "estimated-cost-multiplier" = each.value.cost_factor
  }
}

output "deployment_costs" {
  value = {
    for region, config in var.regions :
    region => config.cost_factor
  }
}
```

---

## Cloud Security & Compliance

### Infrastructure Security Template

```hcl
# AWS Security Group (Network ACLs)
resource "aws_security_group" "api" {
  name = "api-security-group"
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # HTTPS only
  }
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Redirect to HTTPS
  }
  
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # HTTPS outbound
  }
  
  egress {
    from_port   = 3306  # MySQL
    to_port     = 3306
    protocol    = "tcp"
    security_groups = [aws_security_group.database.id]
  }
  
  # Deny everything else (deny by default)
}

# Checkov policy validation
# checkov -f main.tf --framework terraform --check CKV_AWS_23
```

### IAM & Access Control Template

```hcl
# Principle of Least Privilege
resource "aws_iam_role" "lambda_role" {
  name = "lambda-api-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Only allow specific S3 bucket, specific action
resource "aws_iam_policy" "lambda_s3_policy" {
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:PutObject"]
        Resource = "${aws_s3_bucket.uploads.arn}/api-uploads/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_s3" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_s3_policy.arn
}
```

---

## Next Steps

- **Ready to build your IDP?** → [Internal Developer Portal](05-internal-developer-portal.md)
- **Want to see a complete architecture?** → [Reference Architecture](06-reference-architecture.md)
- **Looking for examples?** → [Case Studies](07-case-studies.md)

