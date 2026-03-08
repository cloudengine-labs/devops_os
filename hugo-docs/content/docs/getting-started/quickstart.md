---
title: "Quick Start Reference"
weight: 11
---

# Quick Start Reference

All essential CLI commands in one place, with default output paths for every generator.

> [!NOTE]
> 📖 **Full reference:** For the complete option tables, input files, and all output locations see the [CLI Commands Reference]({{< relref "/docs/reference" >}}).

---

## Installation

```bash
git clone https://github.com/cloudengine-labs/devops_os.git
cd devops_os
python -m venv .venv && source .venv/bin/activate
pip install -r cli/requirements.txt
```

---

## Process-First Philosophy

Before running any generator, learn *why* each tool exists:

```bash
# Full overview (Process-First ideology + tooling map + beginner tips)
python -m cli.devopsos process-first

# Core principles only
python -m cli.devopsos process-first --section what

# Principle → devopsos scaffold command mapping
python -m cli.devopsos process-first --section mapping

# AI prompts for deeper learning
python -m cli.devopsos process-first --section tips
```

See the [Process-First guide]({{< relref "/docs/getting-started/process-first" >}}) for the full reference.

---

## GitHub Actions Workflows

```bash
# Complete CI/CD pipeline
# Output: .github/workflows/my-app-complete.yml
python -m cli.devopsos scaffold gha --name my-app --languages python,javascript --type complete

# Build-only workflow
# Output: .github/workflows/my-app-build.yml
python -m cli.devopsos scaffold gha --name my-app --type build

# With Kubernetes deployment via ArgoCD
# Output: .github/workflows/my-app-complete.yml
python -m cli.devopsos scaffold gha --name my-app --kubernetes --k8s-method argocd

# Reusable workflow
# Output: .github/workflows/shared-reusable.yml
python -m cli.devopsos scaffold gha --name shared --type reusable

# Matrix build
python -m cli.devopsos scaffold gha --name my-app --matrix
```

### Environment Variables

```bash
export DEVOPS_OS_GHA_NAME=my-app
export DEVOPS_OS_GHA_TYPE=complete
export DEVOPS_OS_GHA_LANGUAGES=python,javascript
export DEVOPS_OS_GHA_KUBERNETES=true
export DEVOPS_OS_GHA_K8S_METHOD=kustomize
python -m cli.devopsos scaffold gha
# Output: .github/workflows/my-app-complete.yml
```

---

## GitLab CI Pipelines

```bash
# Complete pipeline
# Output: .gitlab-ci.yml
python -m cli.devopsos scaffold gitlab --name my-app --languages python --type complete

# With Kubernetes deployment via ArgoCD
# Output: .gitlab-ci.yml
python -m cli.devopsos scaffold gitlab --name my-app --languages python,go \
       --kubernetes --k8s-method argocd

# Custom output path
# Output: ci/my-pipeline.yml
python -m cli.devopsos scaffold gitlab --name my-app --output ci/my-pipeline.yml
```

---

## Jenkins Pipelines

```bash
# Complete pipeline
# Output: Jenkinsfile
python -m cli.devopsos scaffold jenkins --name my-app --languages java --type complete

# Parameterized pipeline
# Output: Jenkinsfile
python -m cli.devopsos scaffold jenkins --name my-app --languages python --type parameterized

# Custom output path
# Output: pipelines/Jenkinsfile
python -m cli.devopsos scaffold jenkins --name my-app --output pipelines/Jenkinsfile
```

---

## GitOps — ArgoCD & Flux CD

```bash
# ArgoCD Application + AppProject
# Output: argocd/application.yaml + argocd/appproject.yaml
python -m cli.devopsos scaffold argocd --name my-app \
       --repo https://github.com/myorg/my-app.git \
       --namespace production

# ArgoCD with automated sync + canary rollout
# Output: argocd/application.yaml + argocd/appproject.yaml + argocd/rollout.yaml
python -m cli.devopsos scaffold argocd --name my-app \
       --repo https://github.com/myorg/my-app.git \
       --auto-sync --rollouts

# Flux CD (GitRepository + Kustomization + Image Automation)
# Output: flux/git-repository.yaml + flux/kustomization.yaml + flux/image-update-automation.yaml
python -m cli.devopsos scaffold argocd --name my-app --method flux \
       --repo https://github.com/myorg/my-app.git \
       --image ghcr.io/myorg/my-app
```

---

## SRE Configuration

```bash
# All SRE configs
# Output: sre/alert-rules.yaml + sre/grafana-dashboard.json + sre/slo.yaml + sre/alertmanager-config.yaml
python -m cli.devopsos scaffold sre --name my-app --team platform

# Availability-only SLO
python -m cli.devopsos scaffold sre --name my-app --slo-type availability --slo-target 99.9

# Latency SLO with 200ms threshold + PagerDuty alerting
python -m cli.devopsos scaffold sre --name my-app --slo-type latency \
       --latency-threshold 0.2 \
       --pagerduty-key YOUR_PD_KEY \
       --slack-channel "#platform-alerts"

# Custom output directory
# Output: monitoring/alert-rules.yaml  (etc.)
python -m cli.devopsos scaffold sre --name my-app --output-dir monitoring
```

---

## Dev Container Configuration

```bash
# Python + Go dev container
# Output: .devcontainer/devcontainer.json + .devcontainer/devcontainer.env.json
python -m cli.devopsos scaffold devcontainer \
  --languages python,go \
  --cicd-tools docker,kubectl,helm

# Full-stack with Kubernetes tools
python -m cli.devopsos scaffold devcontainer \
  --languages python,java,javascript \
  --cicd-tools docker,terraform,kubectl,helm \
  --kubernetes-tools k9s,kustomize,argocd_cli,flux \
  --devops-tools prometheus,grafana \
  --python-version 3.12
```

---

## Common Options Quick Reference

| Option | `scaffold gha` | `scaffold gitlab` | `scaffold jenkins` | `scaffold argocd` | `scaffold sre` |
|--------|:-:|:-:|:-:|:-:|:-:|
| `--name` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `--type` | ✓ | ✓ | ✓ | — | — |
| `--languages` | ✓ | ✓ | ✓ | — | — |
| `--kubernetes` | ✓ | ✓ | ✓ | — | — |
| `--k8s-method` | ✓ | ✓ | ✓ | — | — |
| `--output` | ✓ | ✓ | ✓ | — | — |
| `--output-dir` | — | — | — | ✓ | ✓ |
| `--custom-values` | ✓ | ✓ | ✓ | — | — |

---

## Troubleshooting

```bash
# Show help for each generator
python -m cli.devopsos scaffold gha --help
python -m cli.devopsos scaffold gitlab --help
python -m cli.devopsos scaffold jenkins --help
python -m cli.devopsos scaffold argocd --help
python -m cli.devopsos scaffold sre --help
python -m cli.devopsos scaffold devcontainer --help
python -m cli.devopsos process-first --help

# Verify generated output
ls -la .github/workflows/      # GitHub Actions
cat .gitlab-ci.yml             # GitLab CI
cat Jenkinsfile                # Jenkins
ls -la argocd/                 # ArgoCD
ls -la flux/                   # Flux CD
ls -la sre/                    # SRE configs
ls -la .devcontainer/          # Dev container
```
