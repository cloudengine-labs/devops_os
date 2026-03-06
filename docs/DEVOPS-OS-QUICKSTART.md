# DevOps-OS Quick Start Guide

This guide provides the essential CLI commands for using all functionalities of the DevOps-OS development container project.

> 📖 **Full reference:** For the complete list of every option, input file, and output location see [CLI-COMMANDS-REFERENCE.md](CLI-COMMANDS-REFERENCE.md).

## Table of Contents
- [Setting Up DevOps-OS](#setting-up-devops-os)
- [Process-First Philosophy](#process-first-philosophy)
- [GitHub Actions Workflows](#github-actions-workflows)
- [GitLab CI Pipelines](#gitlab-ci-pipelines)
- [Jenkins Pipelines](#jenkins-pipelines)
- [GitOps / ArgoCD & Flux CD](#gitops--argocd--flux-cd)
- [SRE Configuration](#sre-configuration)
- [Container Configuration](#container-configuration)
- [Common Options for All Generators](#common-options-for-all-generators)
- [Troubleshooting](#troubleshooting)

## Setting Up DevOps-OS

### Clone the DevOps-OS Repository
```bash
git clone https://github.com/cloudengine-labs/devops_os.git
cd devops_os
```

### Set Up a Python Virtual Environment (Recommended)

A virtual environment isolates DevOps-OS dependencies from your system Python and avoids version conflicts with other projects.

```bash
# Create the virtual environment
python -m venv .venv

# Activate it — run this every time you open a new terminal
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows (cmd)
# .venv\Scripts\Activate.ps1     # Windows (PowerShell)

# Install CLI dependencies
pip install -r cli/requirements.txt
```

You will see `(.venv)` in your prompt when the environment is active.  
To deactivate it later, simply run `deactivate`.

> **Skip the venv** only when running inside a Docker container or CI/CD runner
> where environment isolation is already provided.

### Configure Development Container
```bash
# Generate dev container config via CLI (recommended)
# Output: .devcontainer/devcontainer.json
#         .devcontainer/devcontainer.env.json
python -m cli.scaffold_devcontainer \
  --languages python,go \
  --cicd-tools docker,terraform,kubectl,helm \
  --kubernetes-tools k9s,flux

# Or edit configuration manually before building
vim .devcontainer/devcontainer.env.json

# Open in VS Code and reopen in container
code .
# Then use Command Palette (Cmd+Shift+P): "Remote-Containers: Reopen in Container"
```

## Process-First Philosophy

**CloudEngineLabs** ([cloudenginelabs.io](https://cloudenginelabs.io)) is a **Process-First** SDLC automation company. Before running any scaffold command,
use the `process-first` CLI option to understand the philosophy behind DevOps-OS and how it drives
every tool in this project.

```bash
# Full overview — ideology, tooling map, and beginner tips
python -m cli.devopsos process-first

# What is Process-First? (core principles)
python -m cli.devopsos process-first --section what

# How each principle maps to a DevOps-OS scaffold command
python -m cli.devopsos process-first --section mapping

# AI prompts and book recommendations for DevOps beginners
python -m cli.devopsos process-first --section tips
```

### Where does process-first help?

| When you are… | Run |
|---------------|-----|
| New to DevOps-OS | `process-first` — understand *why* before *how* |
| Onboarding a team | `process-first --section mapping` — show how each scaffold encodes a process |
| Learning DevOps from scratch | `process-first --section tips` — get AI prompts to study CI/CD, GitOps, and SRE |
| Choosing which scaffold to run first | `process-first --section what` — align on the 5 core principles first |

> **Tip:** Run `process-first --section mapping` alongside `scaffold` commands to see exactly which
> Process-First principle each generated artefact satisfies.

## GitHub Actions Workflows

### Generate GitHub Actions Workflows
```bash
# Basic complete CI/CD workflow
# Output: .github/workflows/devops-os-complete.yml
python -m cli.scaffold_gha

# Build-only workflow
# Output: .github/workflows/devops-os-build.yml
python -m cli.scaffold_gha --type build

# Complete CI/CD workflow for a named application
# Output: .github/workflows/my-app-complete.yml
python -m cli.scaffold_gha --name my-app --type complete

# Workflow with Kubernetes deployment
# Output: .github/workflows/my-app-complete.yml
python -m cli.scaffold_gha --name my-app --kubernetes --k8s-method kubectl

# Matrix build across multiple platforms
# Output: .github/workflows/devops-os-complete.yml
python -m cli.scaffold_gha --matrix

# Reusable workflow
# Output: .github/workflows/devops-os-reusable.yml
python -m cli.scaffold_gha --type reusable

# Specify languages to enable
# Output: .github/workflows/devops-os-complete.yml
python -m cli.scaffold_gha --languages python,java,go

# Custom container image
python -m cli.scaffold_gha --image ghcr.io/myorg/devops-os:latest

# Custom output location
# Output: my-workflows/devops-os-complete.yml
python -m cli.scaffold_gha --output my-workflows
```

### Use Environment Variables Instead
```bash
# Set environment variables
export DEVOPS_OS_GHA_NAME=my-app
export DEVOPS_OS_GHA_TYPE=complete
export DEVOPS_OS_GHA_LANGUAGES=python,javascript
export DEVOPS_OS_GHA_KUBERNETES=true
export DEVOPS_OS_GHA_K8S_METHOD=kustomize

# Run generator (will use environment variables)
# Output: .github/workflows/my-app-complete.yml
python -m cli.scaffold_gha
```

## GitLab CI Pipelines

### Generate GitLab CI Pipelines
```bash
# Complete pipeline for a Python project
# Output: .gitlab-ci.yml
python -m cli.scaffold_gitlab --name my-app --languages python --type complete

# Build + test for Java
# Output: .gitlab-ci.yml
python -m cli.scaffold_gitlab --name java-api --languages java --type test

# Pipeline with Kubernetes deploy via ArgoCD
# Output: .gitlab-ci.yml
python -m cli.scaffold_gitlab --name my-app --languages python,go \
       --kubernetes --k8s-method argocd

# Custom output path
# Output: ci/my-pipeline.yml
python -m cli.scaffold_gitlab --name my-app --output ci/my-pipeline.yml
```

### Use Environment Variables Instead
```bash
export DEVOPS_OS_GITLAB_NAME=my-app
export DEVOPS_OS_GITLAB_TYPE=complete
export DEVOPS_OS_GITLAB_LANGUAGES=python,javascript
export DEVOPS_OS_GITLAB_KUBERNETES=true
export DEVOPS_OS_GITLAB_K8S_METHOD=kustomize

# Output: .gitlab-ci.yml
python -m cli.scaffold_gitlab
```

## Jenkins Pipelines

### Generate Jenkins Pipelines
```bash
# Basic complete CI/CD pipeline
# Output: Jenkinsfile
python -m cli.scaffold_jenkins

# Build-only pipeline
# Output: Jenkinsfile
python -m cli.scaffold_jenkins --type build

# Complete CI/CD pipeline for a named application
# Output: Jenkinsfile
python -m cli.scaffold_jenkins --name my-app --type complete

# Pipeline with Kubernetes deployment
# Output: Jenkinsfile
python -m cli.scaffold_jenkins --name my-app --kubernetes --k8s-method kubectl

# Parameterized pipeline
# Output: Jenkinsfile
python -m cli.scaffold_jenkins --parameters

# Specify languages to enable
# Output: Jenkinsfile
python -m cli.scaffold_jenkins --languages java,go

# Specify SCM type
python -m cli.scaffold_jenkins --scm git

# Custom output location
# Output: pipelines/Jenkinsfile
python -m cli.scaffold_jenkins --output pipelines/Jenkinsfile
```

### Use Environment Variables Instead
```bash
export DEVOPS_OS_JENKINS_NAME=my-app
export DEVOPS_OS_JENKINS_TYPE=complete
export DEVOPS_OS_JENKINS_LANGUAGES=python,javascript
export DEVOPS_OS_JENKINS_KUBERNETES=true
export DEVOPS_OS_JENKINS_K8S_METHOD=kustomize
export DEVOPS_OS_JENKINS_PARAMETERS=true

# Output: Jenkinsfile
python -m cli.scaffold_jenkins
```

## GitOps / ArgoCD & Flux CD

### Generate ArgoCD Configurations
```bash
# ArgoCD Application CR + AppProject CR
# Output: argocd/application.yaml
#         argocd/appproject.yaml
python -m cli.scaffold_argocd --name my-app \
       --repo https://github.com/myorg/my-app.git \
       --namespace production

# ArgoCD with automated sync and canary rollout
# Output: argocd/application.yaml
#         argocd/appproject.yaml
#         argocd/rollout.yaml
python -m cli.scaffold_argocd --name my-app \
       --repo https://github.com/myorg/my-app.git \
       --auto-sync --rollouts

# Custom output directory
# Output: gitops/argocd/application.yaml  (etc.)
python -m cli.scaffold_argocd --name my-app \
       --repo https://github.com/myorg/my-app.git \
       --output-dir gitops
```

### Generate Flux CD Configurations
```bash
# Flux GitRepository + Kustomization + Image Automation
# Output: flux/git-repository.yaml
#         flux/kustomization.yaml
#         flux/image-update-automation.yaml
python -m cli.scaffold_argocd --name my-app --method flux \
       --repo https://github.com/myorg/my-app.git \
       --image ghcr.io/myorg/my-app
```

## SRE Configuration

### Generate SRE Configs
```bash
# All SRE configs
# Output: sre/alert-rules.yaml
#         sre/grafana-dashboard.json
#         sre/slo.yaml
#         sre/alertmanager-config.yaml
python -m cli.scaffold_sre --name my-app --team platform

# Availability-only SLO
# Output: sre/alert-rules.yaml  (etc.)
python -m cli.scaffold_sre --name my-app --slo-type availability --slo-target 99.9

# Latency SLO with 200ms threshold
python -m cli.scaffold_sre --name my-app --slo-type latency --latency-threshold 0.2

# With PagerDuty integration
python -m cli.scaffold_sre --name my-app \
       --pagerduty-key YOUR_PD_KEY \
       --slack-channel "#platform-alerts"

# Custom output directory
# Output: monitoring/alert-rules.yaml  (etc.)
python -m cli.scaffold_sre --name my-app --output-dir monitoring
```

## Container Configuration

### Generate Dev Container Config via CLI
```bash
# Python + Go dev container
# Output: .devcontainer/devcontainer.json
#         .devcontainer/devcontainer.env.json
python -m cli.scaffold_devcontainer \
  --languages python,go \
  --cicd-tools docker,kubectl,helm

# Full-stack container with Kubernetes tools
# Output: .devcontainer/devcontainer.json
#         .devcontainer/devcontainer.env.json
python -m cli.scaffold_devcontainer \
  --languages python,java,javascript \
  --cicd-tools docker,terraform,kubectl,helm \
  --kubernetes-tools k9s,kustomize,argocd_cli,flux \
  --devops-tools prometheus,grafana \
  --python-version 3.12

# Write to a specific project directory
# Output: /path/to/myproject/.devcontainer/devcontainer.json
#         /path/to/myproject/.devcontainer/devcontainer.env.json
python -m cli.scaffold_devcontainer \
  --languages python,go \
  --output-dir /path/to/myproject

# Or via the unified CLI
python -m cli.devopsos scaffold devcontainer

# See all available options
python -m cli.scaffold_devcontainer --help
```

### Configure Development Container Manually
```bash
# Edit the devcontainer.env.json file
cat > .devcontainer/devcontainer.env.json << EOF
{
  "languages": {
    "python": true,
    "java": true,
    "javascript": true,
    "go": true
  },
  "cicd": {
    "docker": true,
    "terraform": true,
    "kubectl": true,
    "helm": true,
    "github_actions": true
  },
  "kubernetes": {
    "k9s": true,
    "kustomize": true,
    "argocd_cli": true,
    "flux": true
  },
  "versions": {
    "python": "3.11",
    "java": "17",
    "node": "20",
    "go": "1.21"
  }
}
EOF
```

## Common Options for All Generators

| Option | `scaffold_gha` | `scaffold_gitlab` | `scaffold_jenkins` | `scaffold_argocd` | `scaffold_sre` | `scaffold_devcontainer` | Description |
|--------|:-:|:-:|:-:|:-:|:-:|:-:|-------------|
| `--name` | ✓ | ✓ | ✓ | ✓ | ✓ | — | Name of the workflow/pipeline/app |
| `--type` | ✓ | ✓ | ✓ | — | — | — | Type of workflow/pipeline |
| `--languages` | ✓ | ✓ | ✓ | — | — | ✓ | Languages to enable |
| `--kubernetes` | ✓ | ✓ | ✓ | — | — | — | Include K8s deployment steps |
| `--k8s-method` | ✓ | ✓ | ✓ | — | — | — | K8s deployment method |
| `--output` | ✓ | ✓ | ✓ | — | — | — | Output file path |
| `--output-dir` | — | — | — | ✓ | ✓ | ✓ | Output directory |
| `--custom-values` | ✓ | ✓ | ✓ | — | — | — | Custom configuration JSON file |
| `--image` | ✓ | ✓ | ✓ | ✓ | — | — | Container image to use |

## Troubleshooting

```bash
# Show help for each generator
python -m cli.scaffold_gha --help
python -m cli.scaffold_gitlab --help
python -m cli.scaffold_jenkins --help
python -m cli.scaffold_argocd --help
python -m cli.scaffold_sre --help
python -m cli.scaffold_devcontainer --help

# Verify generated output locations
ls -la .github/workflows/      # GitHub Actions
cat .gitlab-ci.yml             # GitLab CI
cat Jenkinsfile                # Jenkins
ls -la argocd/                 # ArgoCD
ls -la flux/                   # Flux CD
ls -la sre/                    # SRE configs
ls -la .devcontainer/          # Dev container

# Verify dev container configuration
cat .devcontainer/devcontainer.env.json
```
