---
title: "Infrastructure Hardening Made Easy: Kyverno, InSpec, and Checkov With DevOps-OS"
slug: "infrastructure-hardening-kyverno-inspec-checkov-devops-os"
description: "DevOps-OS scaffold hardening generates CIS, STIG, and NSA/CISA-compliant Kyverno policies, InSpec profiles, and Checkov checks — in one command."
topic: "platform-engineering"
tags: ["InfrastructureHardening", "Kyverno", "InSpec", "Checkov", "PlatformEngineering", "Compliance"]
publishedAt: "2026-08-11"
featured: false
---

# Infrastructure Hardening Made Easy: Kyverno, InSpec, and Checkov With DevOps-OS

Compliance is one of the most time-consuming activities in platform engineering. Writing Kyverno ClusterPolicies for CIS Kubernetes benchmarks by hand takes days. DevOps-OS compresses that to seconds.

## The command

```bash
# CIS Kubernetes benchmark — Kyverno policies
python -m cli.devopsos scaffold hardening \
  --standard cis-k8s \
  --type kyverno \
  --environment production

# Output: hardening/kyverno/cis-k8s/
```

## Standards supported

| Standard | Target | Tool |
|----------|--------|------|
| CIS Kubernetes Benchmark v1.9 | Kubernetes cluster | Kyverno |
| DISA STIG for Kubernetes | Kubernetes cluster | Kyverno |
| NSA/CISA Kubernetes Hardening Guide | Kubernetes cluster | Kyverno + NetworkPolicy |
| CIS Docker Benchmark v1.6 | Container runtime | InSpec |
| CIS RHEL 9 Benchmark | Operating system | InSpec |
| CIS Ubuntu 22.04 Benchmark | Operating system | InSpec |
| Pod Security Standards (Kubernetes) | Pod admission | Kyverno ClusterPolicy |
| Container Image Signing | CI/CD + admission | Kyverno + Cosign |
| OWASP ASVS L1 (infra layer) | Application deployment | Kyverno + Checkov |
| Essential Eight (Australia ASD) | General controls | Checkov |

## Generate multiple standards at once

```bash
# All Kyverno policies for a production cluster — every supported standard
python -m cli.devopsos scaffold hardening \
  --standard all \
  --type kyverno \
  --environment production

# OS hardening profile for RHEL 9
python -m cli.devopsos scaffold hardening \
  --standard cis-rhel9 \
  --type inspec

# With compliance framework tagging for audit evidence
python -m cli.devopsos scaffold hardening \
  --standard cis-k8s \
  --compliance-framework pci-dss
```

The `--compliance-framework` flag adds NIST/PCI-DSS/SOC2 control IDs to every policy so your gap register and audit evidence link back automatically.

## Output structure

```
hardening/
├── kyverno/
│   ├── cis-k8s/
│   │   ├── 1-master-node-config.yaml
│   │   ├── 2-etcd-config.yaml
│   │   ├── 3-control-plane.yaml
│   │   ├── 4-worker-node.yaml
│   │   └── 5-policies.yaml
│   ├── stig-k8s/
│   │   └── stig-cluster-policies.yaml
│   └── pod-security-standards.yaml
└── inspec/
    ├── docker-cis/
    └── rhel9-cis/
```

## Environment-aware policies

The `--environment` flag adjusts Kyverno's `validationFailureAction`:

| Environment | Kyverno action |
|-------------|---------------|
| `dev` | `audit` (log violations, never block) |
| `staging` | `audit` (log violations) |
| `production` | `enforce` (block non-compliant workloads) |

Start with `audit` in development to understand what your current workloads violate, then switch to `enforce` in production once policies are tuned.

## Options reference

| Option | Default | Description |
|--------|---------|-------------|
| `--standard` | `all` | Hardening standard: `cis-k8s`, `stig-k8s`, `nsa-k8s`, `cis-docker`, `cis-rhel9`, `cis-ubuntu22`, `pod-security`, `image-signing`, `asvs-l1`, `essential-eight`, `all` |
| `--type` | `all` | Output type: `kyverno`, `inspec`, `checkov`, or `all` |
| `--environment` | `production` | `dev`, `staging`, or `production` |
| `--compliance-framework` | _(none)_ | Tag with `pci-dss`, `hipaa`, `iso27001`, `nist-800-53`, `soc2` |
| `--severity` | `medium` | Minimum severity filter: `critical`, `high`, `medium`, `low` |
| `--output` | `./hardening/` | Output directory |

## Where hardening fits in the platform

Infrastructure hardening belongs in the platform-engineering layer, not the application layer. Use DevOps-OS to generate the policies once, store them in a dedicated Git repository, and apply them via ArgoCD or Flux to every cluster. Application teams never need to know the policies exist — they just get blocked when their workloads violate a control, with a clear error message pointing to the violated policy.

That is the Platform Engineering Internal Developer Platform (IDP) model: encode the standards into automation, expose a self-service scaffold, and let the platform enforce compliance transparently.
