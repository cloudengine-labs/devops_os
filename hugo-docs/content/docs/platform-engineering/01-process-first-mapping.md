---
title: "Process-First Mapping: From DevOps Tools to Platform Engineering"
description: "Map traditional DevOps tools to Process-First SDLC principles and understand how this foundation enables platform engineering."
weight: 15
---

# Process-First Mapping: From DevOps Tools to Platform Engineering

The **Process-First** philosophy is foundational to platform engineering. It states that business processes should drive technology choices, not the reverse. This document maps traditional DevOps tools to the Process-First SDLC phases and shows how this bridge enables platform engineering.

## The Process-First SDLC

The Process-First approach divides software delivery into five phases:

```
┌─────────────────────────────────────────────────────────┐
│ PLAN │ CREATE │ VERIFY │ RUN │ MONITOR                │
└─────────────────────────────────────────────────────────┘
```

### **PLAN Phase** 🎯
**Intent**: Understand what needs to be built and how it will be delivered.

**Activities**:
- Define requirements and acceptance criteria
- Design system architecture and deployment topology
- Choose deployment patterns (blue-green, canary, rolling)
- Define monitoring and alerting strategy
- Establish compliance and security requirements

**Platform Engineering Mapping**:
- **Golden Path Templates**: Define "how we build and deploy X" for different application types
- **Template Catalog**: Self-service discovery of available patterns
- **Guardrails Definition**: Document organizational standards and constraints
- **Template Versioning**: Track evolution of patterns over time

### **CREATE Phase** 🏗️
**Intent**: Write code and infrastructure as code in a way that's reproducible and testable.

**Activities**:
- Write application code
- Write unit tests
- Create infrastructure-as-code (IaC) configurations
- Define deployment manifests (Docker, Kubernetes, etc.)
- Document architecture and runbooks

**Platform Engineering Mapping**:
- **Scaffold Generators**: Use DevOps-OS to generate boilerplate CI/CD pipelines, Kubernetes manifests, IaC templates
- **Code Generation**: Template-driven scaffolding reduces copy-paste errors
- **Repository Structure**: Platform-standardized directory layouts
- **Development Environment**: Dev containers with standardized tools and dependencies
- **Runbook Templates**: Auto-generate basic runbooks from deployment configuration

### **VERIFY Phase** ✅
**Intent**: Ensure code and configuration meet quality, security, and compliance standards before deployment.

**Activities**:
- Run unit tests and integration tests
- Perform static code analysis and linting
- Conduct security scanning (SAST, dependency checks)
- Validate infrastructure configuration (policy-as-code)
- Perform compliance checks against standards
- Build and publish container images

**Platform Engineering Mapping**:
- **CI Pipeline Templates**: GitHub Actions, GitLab CI, Jenkins workflows with standard test/lint/scan stages
- **Policy-as-Code**: Kyverno, Checkov, InSpec policies enforce standards automatically
- **Test Scaffold**: Generate pytest, Jest, Mocha, or Go test configurations
- **Hardening Policies**: Auto-generate security baselines (CIS, STIG, NSA/CISA, Essential Eight)
- **Container Registry**: Standardized image naming, scanning, and promotion policies
- **Approval Gates**: Automated compliance checks before deployment eligibility

### **RUN Phase** 🚀
**Intent**: Deploy and operate the application in production with confidence.

**Activities**:
- Deploy to production (or production-like environments)
- Execute deployment validation checks
- Monitor for deployment errors and automatic rollback
- Manage configuration changes safely
- Handle secrets and credentials securely
- Coordinate multi-environment deployments (dev → staging → prod)

**Platform Engineering Mapping**:
- **Deployment Automation**: ArgoCD, Flux CD templates for GitOps-driven deployments
- **Progressive Delivery**: Canary and blue-green deployment strategies via Flagger
- **Kubernetes Manifests**: Generated Deployment, StatefulSet, DaemonSet templates
- **Configuration Management**: ConfigMap and Secret templates with secure handling
- **Multi-Environment Promotion**: Templated promotion pipelines across environments
- **Rollback Automation**: Policy-driven automatic rollback on deployment failures
- **Multi-Cluster Orchestration**: Templates for deploying across multiple clusters/regions

### **MONITOR Phase** 📊
**Intent**: Measure system health, user experience, and operational effectiveness. Use insights to improve.

**Activities**:
- Collect application metrics (RED: Rate, Errors, Duration)
- Collect infrastructure metrics (USE: Utilization, Saturation, Errors)
- Implement distributed tracing
- Define and track SLOs and error budgets
- Alert on anomalies and SLO violations
- Create dashboards for team situational awareness
- Collect cost metrics and optimize spending
- Analyze logs for debugging and trend analysis

**Platform Engineering Mapping**:
- **Observability Scaffolding**: Generate Prometheus ServiceMonitor, Grafana dashboard, SLO manifests
- **Alert Rule Templates**: Standardized alert rules for common failure modes
- **Distributed Tracing**: Jaeger, OpenTelemetry instrumentation templates
- **Cost Monitoring**: FinOps dashboards and cost allocation policies
- **Audit Logging**: Compliance and security audit trail templates
- **Runbook Automation**: Automated remediation policies for common issues
- **Learning & Feedback**: Metrics showing platform adoption and developer velocity

---

## Traditional DevOps Tools → Platform Engineering

### **CI/CD Tools in the Process-First Context**

#### GitHub Actions
| Phase | Use Case |
|-------|----------|
| **PLAN** | Workflow templates defining CI/CD strategy |
| **CREATE** | Automated builds on code commit |
| **VERIFY** | Test, lint, security scan, compliance check jobs |
| **RUN** | Deploy to staging/production via workflow dispatch |
| **MONITOR** | Artifact metadata, deployment status tracking |

**Platform Engineering Evolution**:
- Individual workflows → Reusable workflow templates (via `uses:` syntax)
- Manual YAML authoring → Scaffold-generated workflows with guardrails
- Copy-paste patterns → Parameterized workflow templates with inputs
- No versioning → Semantic versioning of workflow templates

#### GitLab CI
| Phase | Use Case |
|-------|----------|
| **PLAN** | `.gitlab-ci.yml` defines pipeline structure |
| **CREATE** | `script:` stages handle build and test |
| **VERIFY** | `test:`, `security:`, `compliance:` jobs |
| **RUN** | `deploy:` stages manage deployment |
| **MONITOR** | Pipeline artifacts, deployment tracking |

**Platform Engineering Evolution**:
- Monolithic `.gitlab-ci.yml` → Modular includes and templates
- Manual trigger paths → Automated promotion pipelines
- Inconsistent naming → Standardized stage names and job structures
- Limited re-use → Component templates via `include:`

#### Jenkins
| Phase | Use Case |
|-------|----------|
| **PLAN** | Pipeline design and parameterization |
| **CREATE** | Build and compilation stages |
| **VERIFY** | Test execution and code quality checks |
| **RUN** | Deployment orchestration across environments |
| **MONITOR** | Build artifacts, test reports, logs |

**Platform Engineering Evolution**:
- Freestyle jobs → Declarative/Scripted Pipeline as code
- Manual pipeline creation → Jenkins Job DSL/Pipeline templates
- Scattered configuration → Centralized shared library patterns
- Limited guardrails → Shared library functions enforcing standards

### **Deployment & GitOps Tools**

#### ArgoCD / Flux CD
| Phase | Use Case |
|-------|----------|
| **PLAN** | Application definitions and sync policies |
| **CREATE** | Kustomize/Helm templates for deployment |
| **VERIFY** | Pre-sync validation hooks and policies |
| **RUN** | GitOps-driven continuous deployment |
| **MONITOR** | Application health status and sync state |

**Platform Engineering Evolution**:
- Manual kubectl apply → GitOps declarative desired state
- Environment-specific manifests → Kustomization-based templating
- Ad-hoc deployment scripts → Policy-driven automatic reconciliation
- No audit trail → Git commit history as deployment audit log

### **Observability Tools**

#### Prometheus / Grafana
| Phase | Use Case |
|-------|----------|
| **PLAN** | Define SLOs and alert thresholds |
| **CREATE** | Instrument code with metrics |
| **VERIFY** | Pre-deploy validation against SLO targets |
| **RUN** | Real-time health monitoring during deployment |
| **MONITOR** | Dashboards, alerts, SLO tracking |

**Platform Engineering Evolution**:
- Manual metric definition → Auto-generated ServiceMonitor templates
- Ad-hoc dashboards → Templated dashboards per application type
- Static alerts → Dynamic alert rules based on SLO definitions
- No cost visibility → Cost metrics and FinOps dashboards

---

## From Manual DevOps to Templated Platform Engineering

### Example Evolution: "Deploy a Node.js Microservice"

**Year 1: Manual DevOps Era**
```
Platform Team → Creates custom Jenkins pipeline (1-2 days)
             → Creates Kubernetes manifests (1-2 days)
             → Creates Prometheus/Grafana dashboards (1-2 days)
             → Documents in Confluence (outdated within weeks)

Total time: 3-5 days per new service
Consistency: Variable (depends on who built it)
```

**Year 2: Early Templating**
```
Platform Team → Publishes Jenkins pipeline template
             → Publishes Kubernetes manifest template
             → Publishes monitoring template

Developer → Copies template
          → Modifies for their specific needs
          → Submits PR to infrastructure repo
          → Platform team reviews and merges

Total time: 2-3 days per new service
Consistency: Improved but still variable (custom modifications)
```

**Year 3: Scaffold Generators + IDP**
```
Developer → Opens Claude Desktop / ChatGPT
          → "Generate a Node.js microservice deployment pipeline"
          → DevOps-OS MCP server generates:
             - GitHub Actions / GitLab CI / Jenkins workflow
             - Kubernetes Deployment manifests
             - Prometheus ServiceMonitor
             - Grafana dashboard
             - Dev container config
          → Review and commit to repo

Total time: 15 minutes per new service
Consistency: 99% (guardrails in generator prevent mistakes)
DX Improvement: No DevOps expertise needed
```

### The Three Transformation Steps

1. **Manual → Documented**: Document "how we do it" in runbooks and examples
2. **Documented → Templated**: Create reusable templates teams can copy and customize
3. **Templated → Scaffolded**: Build generators that produce templates automatically, reducing manual work

Each step removes cognitive load and reduces error potential.

---

## Guardrails in Each Phase

Platform engineering embeds guardrails into templates that prevent common mistakes:

### **PLAN Phase Guardrails**
- Limit template choices to organization-approved patterns
- Validate template selection against compliance requirements
- Enforce SLO minimums (99.9% uptime, max 1-hour deployment)

### **CREATE Phase Guardrails**
- Generated code follows organization naming conventions
- Dev container includes organization-standardized tools
- Scaffold-generated IaC follows security best practices

### **VERIFY Phase Guardrails**
- All pipelines include unit test, lint, and security scan stages
- Policy-as-code blocks non-compliant configurations
- Approval gates prevent unsafe deployments

### **RUN Phase Guardrails**
- Deployment templates enforce blue-green or canary strategies
- RBAC prevents unauthorized deployments
- Automated rollback on error conditions

### **MONITOR Phase Guardrails**
- All deployments include observability (metrics, traces, logs)
- SLO thresholds prevent silent failures
- Cost alerts prevent budget overruns

---

## Benefits of Process-First Platform Engineering

| Benefit | Traditional DevOps | Process-First Platform |
|---------|-------------------|------------------------|
| **Time to Deploy** | Days (manual processes) | Minutes (automated) |
| **Consistency** | 60-70% | 95%+ |
| **Developer Experience** | Requires DevOps expertise | Self-service |
| **Error Rate** | 15-20% (manual mistakes) | <1% (automated checks) |
| **Knowledge Silos** | Tight (depends on individuals) | Loose (documented in templates) |
| **Compliance** | Manual audits | Automated verification |
| **Cost Visibility** | Limited | Real-time tracking |
| **Deployment Confidence** | Low (manual validation) | High (automated testing + rollback) |

---

## Mapping Checklist: Is Your Organization Platform-Engineering Ready?

Use this checklist to assess your current state:

### **PLAN Phase**
- [ ] Organization has documented deployment patterns
- [ ] Teams know "the approved way" to deploy services
- [ ] Deployment patterns include security and compliance requirements
- [ ] Patterns are versioned and evolve over time

### **CREATE Phase**
- [ ] Code and IaC repositories follow naming conventions
- [ ] Developers have standardized development environments
- [ ] Boilerplate code generation is available
- [ ] IaC follows organization standards automatically

### **VERIFY Phase**
- [ ] All CI/CD pipelines include testing and security scanning
- [ ] Policy-as-code blocks non-compliant configurations
- [ ] Compliance checks are automated
- [ ] No manual approval gates for standard deployments

### **RUN Phase**
- [ ] Deployments use GitOps principles (Git as source of truth)
- [ ] Rollback is automated and tested
- [ ] Multi-environment promotion is standardized
- [ ] Secrets and configuration are managed securely

### **MONITOR Phase**
- [ ] All applications include standardized observability
- [ ] SLOs are defined and tracked automatically
- [ ] Alerts are generated from SLO violations
- [ ] Cost is visible and tracked per application/team

---

## Next Steps

- **Ready to design templates?** → [Pipeline Templatization](02-pipeline-templatization.md)
- **Want to see this in a Kubernetes context?** → [Kubernetes Platform Engineering](03-kubernetes-platform-engineering.md)
- **Looking for the complete architecture?** → [Reference Architecture](06-reference-architecture.md)

