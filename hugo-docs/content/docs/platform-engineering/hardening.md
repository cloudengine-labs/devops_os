---
title: "Infrastructure Hardening"
weight: 16
---

# Infrastructure Hardening

DevOps-OS includes `python -m cli.devopsos scaffold hardening` to generate reusable hardening baselines for Kubernetes clusters, container runtimes, and operating systems.

---

## What it generates

| Output type | Purpose | Default location |
|-------------|---------|------------------|
| Kyverno policies | Kubernetes admission guardrails for CIS, STIG, NSA/CISA, Pod Security Standards, image signing, and OWASP ASVS L1 | `hardening/kyverno/` |
| InSpec profiles | Compliance profiles for Docker, RHEL 9, and Ubuntu 22.04 | `hardening/inspec/` |
| ASVS L1 checks | OWASP ASVS L1 infra-layer Kyverno policies and Checkov checks | `hardening/asvs-l1-checks/` |
| Checkov checks | Essential Eight checks and supporting metadata | `hardening/essential-eight/` |
| Compliance mapping | Rule-to-framework mapping for catalog linking | `hardening/compliance-mapping.yaml` |

---

## Supported standards

| Standard | Primary output |
|----------|----------------|
| CIS Kubernetes Benchmark v1.9 | Kyverno policies |
| DISA STIG for Kubernetes | Kyverno policies |
| NSA/CISA Kubernetes Hardening Guide | Kyverno policies + network policies |
| Pod Security Standards | Kyverno policy |
| Container image signing | Kyverno policy |
| OWASP ASVS L1 (infra layer) | Kyverno policies + Checkov checks |
| CIS Docker Benchmark v1.6 | InSpec profile |
| CIS RHEL 9 Benchmark | InSpec profile |
| CIS Ubuntu 22.04 Benchmark | InSpec profile |
| Essential Eight | Checkov checks + README |

---

## Quick start

```bash
# CIS Kubernetes guardrails
python -m cli.devopsos scaffold hardening --standard cis-k8s --type kyverno --environment production

# OWASP ASVS L1 infra-layer checks
python -m cli.devopsos scaffold hardening --standard asvs-l1

# Operating system baseline
python -m cli.devopsos scaffold hardening --standard cis-rhel9 --type inspec

# Full baseline set with compliance tagging
python -m cli.devopsos scaffold hardening --standard all --compliance-framework pci-dss
```

---

## Key options

| Option | Default | Description |
|--------|---------|-------------|
| `--standard` | `all` | Select a single baseline or generate all supported standards |
| `--type` | `all` | Limit output to `kyverno`, `inspec`, `checkov`, or generate all applicable artifacts |
| `--output` | `hardening` | Root directory for generated artifacts |
| `--compliance-framework` | _(none)_ | Add compliance control IDs for `pci-dss`, `hipaa`, `iso27001`, `rbi`, `nist-800-53`, or `soc2` |
| `--severity` | `medium` | Filter generated rules by minimum severity |
| `--environment` | `production` | Use `production` for `Enforce`; `dev` and `staging` generate `Audit` mode policies |

---

## Typical output layout

```text
hardening/
├── kyverno/
│   ├── cis-k8s/
│   ├── stig-k8s/
│   ├── nsa-k8s/
│   ├── pod-security-standards.yaml
│   └── image-signing.yaml
├── inspec/
│   ├── docker-cis/
│   ├── rhel9-cis/
│   └── ubuntu22-cis/
├── asvs-l1-checks/
│   ├── README.md
│   ├── kyverno/
│   └── checkov/
├── essential-eight/
└── compliance-mapping.yaml
```

---

## Validation examples

```bash
pytest tests/test_hardening_scaffold.py
kubectl apply --dry-run=client -f hardening/kyverno/
python -c "import yaml; yaml.safe_load(open('hardening/compliance-mapping.yaml'))"
```

For the full option table, environment variables, and examples, see the [CLI Reference]({{< relref "/docs/reference" >}}).
