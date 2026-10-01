---
title: "Pipeline Templatization Fundamentals"
description: "Design principles for creating reusable pipeline templates, establishing guardrails, and managing template evolution."
weight: 20
---

# Pipeline Templatization Fundamentals

Pipeline templatization is the process of identifying common patterns in CI/CD workflows and codifying them as reusable, parameterized templates. This enables consistency, reduces errors, and accelerates team onboarding.

## Template vs. Bespoke Pipeline

### **Reusable Template**
- Solves a **common problem** (e.g., "build and test a Python Flask app")
- Uses **parameters** to customize behavior (language, test framework, Docker registry)
- Enforces **guardrails** (e.g., "always run security scan before deploy")
- **Versioned** and **documented**
- Can be **discovered and reused** by multiple teams

### **Bespoke Pipeline**
- Solves a **unique problem** (e.g., "deploy legacy mainframe batch job hourly")
- **Custom logic** specific to one application
- May **bypass guardrails** for legitimate business reasons
- Created **once** and rarely changed
- Knowledge exists in **one person's head**

**Best Practice**: 80% of pipelines should be based on templates; 20% can be bespoke.

---

## Template Design Principles

### 1. **Single Responsibility**
Each template should solve one problem well.

❌ **Bad**: "Universal deployment pipeline" that tries to handle Python, Java, Go, and Node.js
✅ **Good**: Separate templates for each language and application type

### 2. **Parametrization Over Customization**
Use parameters for common variations; extend for complex needs.

❌ **Bad**: Teams copy template and modify multiple files
✅ **Good**: Single parameter `docker_registry: "gcr.io/myorg"` changes behavior

### 3. **Sensible Defaults**
Most teams should use the default configuration without modification.

❌ **Bad**: Template requires 20 input parameters to function
✅ **Good**: Template works with just `app_name` and `language`

### 4. **Discoverable and Documented**
Templates should be easy to find and understand.

- **Catalog**: Central registry of available templates (README, example outputs)
- **Runbooks**: Step-by-step guide for template usage
- **Video tutorials**: 5-minute demo of template in action

### 5. **Versioned and Evolving**
Templates should evolve safely over time.

- **Semantic versioning**: v1.0.0, v1.1.0 (bug fixes), v2.0.0 (breaking changes)
- **Changelog**: Document what changed in each version
- **Migration guide**: How to upgrade from v1 to v2

---

## Template Composition Strategy

Templates can be composed hierarchically:

```
┌──────────────────────────────────────────┐
│ Application Template                      │
│ (e.g., "Python Flask Microservice")       │
├──────────────────────────────────────────┤
│ ├─ CI/CD Stage Template (Build & Test)   │
│ ├─ Deploy Stage Template (Kubernetes)    │
│ ├─ Observability Stage Template (Prometheus/Grafana)
│ └─ Security Stage Template (Scanning)    │
└──────────────────────────────────────────┘
```

Each **stage template** is:
- Independently versioned
- Reusable across multiple application templates
- Composable with other stage templates

### Example: Building a Node.js Template

**Ingredients**:
1. **CI/CD Base** (GitHub Actions, GitLab CI, Jenkins generic structure)
2. **Node.js-specific stages**:
   - `npm install` + `npm run test`
   - `npm run build` + Docker build
   - Linting with ESLint
   - Security scan with npm audit / Snyk
3. **Deployment stages**:
   - Kubernetes manifests with Node.js defaults
   - Helm chart for service mesh integration
   - Prometheus monitoring for Node.js metrics
4. **Dev container**:
   - Node.js version management (nvm)
   - npm/yarn/pnpm support
   - Pre-installed debug tools

**Output**: A complete Node.js microservice ready to deploy.

---

## Guardrails & Trade-offs

Guardrails are constraints built into templates that prevent common mistakes while allowing flexibility.

### Examples of Guardrails

| Guardrail | Benefit | Trade-off |
|-----------|---------|-----------|
| All pipelines must include unit tests | Catches bugs early | Slower pipeline (few seconds) |
| All container images scanned for vulnerabilities | Prevents malware deployment | Dependency on vulnerability database |
| RBAC enforced for production deployments | Prevents accidental deletion | More API calls for permission checks |
| Automatic rollback on deployment failure | Faster error recovery | May hide root cause (needs debugging) |
| Cost alerts at 80% of budget | Prevents surprise bills | May over-alert (false positives) |
| Canary deployments mandatory | Limits blast radius of bugs | Slower deployment (phased rollout) |

### Flexibility Escape Hatches

Guardrails should allow legitimate exceptions:

```yaml
# Template-enforced guardrail
require_security_scan: true

# But teams can request exception with justification
security_scan_exception:
  enabled: true
  reason: "Internal tool, no external attack surface"
  approved_by: "SecurityTeam"
  expires: "2025-12-31"
```

---

## Template Versioning Strategy

### Semantic Versioning: MAJOR.MINOR.PATCH

#### **MAJOR** (v1.0 → v2.0)
Breaking changes. Old pipelines **must update**.
- Example: "Kubernetes API v1 to v2" or "Python 2.7 to Python 3.8"
- Impact: All users must update
- Migration path: Provide side-by-side documentation

#### **MINOR** (v1.0 → v1.1)
New features, backward compatible.
- Example: "Add option to use Helm instead of Kustomize"
- Impact: Existing pipelines continue to work unchanged
- Upgrade path: Optional, users choose timing

#### **PATCH** (v1.0.0 → v1.0.1)
Bug fixes and security updates.
- Example: "Fix security scanning tool version"
- Impact: Automatic or recommended upgrade
- Upgrade path: Immediate (low risk)

### Template Lifecycle

```
Experimental (v0.x)
  ↓
  [Gather community feedback and iterate]
  ↓
Stable (v1.0) → [Minor updates] → v1.1, v1.2, ...
  ↓
  [Years of use, community mature]
  ↓
Enhanced (v2.0) [Major feature additions or redesign]
  ↓
  [Eventually]
  ↓
Deprecated (v3.0 released)
  ↓
  [6 month sunset period]
  ↓
End of Life (removed from catalog)
```

---

## Reference Implementations

### **Template 1: Python Flask Microservice**

**Goals**:
- Unit tests with pytest
- Docker container
- Kubernetes deployment
- Prometheus monitoring

**Template Structure**:
```
python-flask-microservice/
├── .github/workflows/
│   └── ci-cd.yml (template with parameters)
├── kubernetes/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── servicemonitor.yaml
├── docker/
│   └── Dockerfile (multi-stage)
├── .devcontainer/
│   └── devcontainer.json
├── README.md (usage guide)
├── CHANGELOG.md (version history)
└── example-outputs/ (shows generated files)
```

**Parameters**:
- `app_name`: Application identifier
- `python_version`: 3.9, 3.10, 3.11, 3.12
- `test_framework`: pytest (default) or unittest
- `docker_registry`: gcr.io, ghcr.io, ECR URL
- `deploy_strategy`: rolling, canary, blue-green
- `environment`: dev, staging, prod

**Guardrails**:
- ✅ Unit tests required (fail if coverage < 80%)
- ✅ Linting with black + flake8
- ✅ Security scan (Bandit)
- ✅ Container image scan (Trivy)
- ✅ Helm chart validation
- ✅ SLO defined (99.9% uptime, p95 < 500ms)

### **Template 2: Multi-Language Monorepo**

**Goals**:
- Support Python + Node.js + Go in one repo
- Independent CI paths per language
- Coordinated deployment

**Template Structure**:
```
monorepo-ci/
├── python/
│   ├── Makefile (test, build, lint)
│   └── .ci/python.yml (stage template)
├── node/
│   ├── Makefile (test, build, lint)
│   └── .ci/node.yml (stage template)
├── go/
│   ├── Makefile (test, build, lint)
│   └── .ci/go.yml (stage template)
├── .github/workflows/
│   └── ci.yml (orchestrates all stages)
├── .ci/ (shared CI components)
│   ├── _common.yml
│   └── _deploy.yml
└── README.md (monorepo guide)
```

**Guardrails**:
- ✅ Changed language triggers only that language's tests
- ✅ All languages must pass before deployment
- ✅ Deployment requires approval from code owner
- ✅ Each service has independent SLO

### **Template 3: Database Migration Pipeline**

**Goals**:
- Schema versioning with Flyway/Liquibase
- Rollback testing
- Zero-downtime migration validation

**Template Structure**:
```
db-migration-template/
├── migrations/
│   ├── V001__initial_schema.sql
│   └── V002__add_users_table.sql
├── test/
│   ├── test_forward_migration.sql
│   └── test_rollback.sql
├── .github/workflows/
│   └── migration-ci.yml
└── docs/
    ├── migration-checklist.md
    └── rollback-procedure.md
```

**Guardrails**:
- ✅ Rollback tested before deployment
- ✅ Data backup created before migration
- ✅ Canary migration to single pod first
- ✅ Automatic rollback if health checks fail

---

## Template Discovery & Catalog

### **Catalog Structure**
```
Platform Engineering Templates Catalog
├── By Language
│   ├── Python (Flask, Django, FastAPI)
│   ├── Node.js (Express, NestJS)
│   ├── Go (Gin, Echo)
│   └── Java (Spring Boot, Quarkus)
├── By Deployment Model
│   ├── Kubernetes (most common)
│   ├── Serverless (Lambda, Cloud Functions)
│   └── VMs (legacy)
├── By Application Type
│   ├── Microservice
│   ├── Data Pipeline
│   ├── Frontend/SPA
│   └── Worker Job
└── By Compliance Level
    ├── General (no special requirements)
    ├── HIPAA (healthcare)
    ├── PCI-DSS (payment processing)
    └── SOC2 (enterprise SaaS)
```

### **Catalog Entry Template**
```markdown
# Python Flask Microservice Template

**Latest**: v2.1.0 (updated Oct 2024)
**Stability**: Stable (3+ years of production use)
**Users**: 80+ services

## What it generates
- GitHub Actions CI/CD workflow (build, test, deploy)
- Kubernetes Deployment + Service manifests
- Prometheus monitoring configuration
- Grafana dashboard template

## Prerequisites
- Python 3.9+
- Docker installed locally
- Kubernetes cluster access

## Quick Start
1. Copy template: `devops-os scaffold template:python-flask`
2. Fill parameters: `app_name=my-service docker_registry=gcr.io/myorg`
3. Review output and commit

## Guardrails
- ✅ Unit tests required (80%+ coverage)
- ✅ Security scanning (Bandit, Snyk)
- ✅ Container vulnerability scanning
- ✅ Helm validation

## Customization Examples
- Using uWSGI instead of Gunicorn
- Adding Redis caching
- Multi-region deployment

## Support
- Documentation: [link]
- Issues: GitHub Discussions
- Support: #platform-eng Slack
```

---

## Template Maintenance & Evolution

### **Quarterly Template Review**
- Gather usage metrics (which templates most used, customization patterns)
- Collect feedback from teams
- Plan updates (bug fixes, new features)
- Schedule deprecation of old versions

### **Deprecation Policy**
- **Announce**: 6 months before end-of-life
- **Support**: Bug fixes still provided during sunset period
- **Migration**: Detailed guide to upgrade to new version
- **Sunset**: Remove from catalog after 6 months

### **Continuous Integration of Templates**
- Template syntax validated on every change
- Example output generated and tested
- Documentation generated from template
- Security scan applied to template itself

---

## Measuring Template Adoption

| Metric | What it means |
|--------|---------------|
| % of pipelines using templates | How many teams leverage standards |
| Template customization rate | Is template flexible enough? (target: <20% custom modifications) |
| Time from template to production | Has platform reduced deployment time? (target: <1 hour) |
| SLO compliance | Do templated services maintain reliability? (target: >99%) |
| Developer satisfaction | Do teams like using templates? (target: >8/10 score) |
| Template version adoption | Are teams staying current? (target: 80% on latest major version) |

---

## Next Steps

- **Ready to implement in Kubernetes?** → [Kubernetes Platform Engineering](03-kubernetes-platform-engineering.md)
- **Want to see a complete architecture?** → [Reference Architecture](06-reference-architecture.md)
- **Looking for examples?** → [Case Studies](07-case-studies.md)

