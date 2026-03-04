---
title: "DevOps-OS"
type: "docs"
---

# 🚀 DevOps-OS

**Automate your entire DevOps lifecycle — from CI/CD pipelines to Kubernetes deployments and SRE dashboards — using a conversational AI assistant or a single CLI command.**

[![CI](https://github.com/cloudengine-labs/devops_os/actions/workflows/ci.yml/badge.svg)](https://github.com/cloudengine-labs/devops_os/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://github.com/cloudengine-labs/devops_os/blob/main/LICENSE)

---

## What is DevOps-OS?

DevOps-OS is an open-source DevOps automation platform that scaffolds production-ready CI/CD pipelines, Kubernetes configurations, and SRE observability configs — in seconds, from a single CLI command or an AI chat prompt.

## Features

| | Feature | Description |
|--|---------|-------------|
| 🚀 | **CI/CD Generators** | One-command scaffolding for GitHub Actions, GitLab CI, and Jenkins pipelines — [→ CI/CD Generators]({{< relref "/docs/ci-cd" >}}) |
| ☸️ | **GitOps Config Generator** | Kubernetes manifests, ArgoCD Applications, and Flux CD Kustomizations — [→ GitOps & ArgoCD]({{< relref "/docs/gitops" >}}) |
| 📊 | **SRE Config Generator** | Prometheus alert rules, Grafana dashboards, and SLO manifests — [→ SRE Configuration]({{< relref "/docs/sre" >}}) |
| 🤖 | **MCP Server** | Plug DevOps-OS tools into Claude or ChatGPT as native AI skills — [→ AI Integration]({{< relref "/docs/ai-integration" >}}) |
| 🛠️ | **Dev Container** | Pre-configured multi-language environment: Python · Java · Go · JavaScript — [→ Dev Container]({{< relref "/docs/dev-container" >}}) |
| 📖 | **CLI Reference** | Complete option tables, input files, and exact output paths for every command — [→ CLI Reference]({{< relref "/docs/reference" >}}) |

---

## ⚡ Quick Start

```bash
# 1. Clone and install
git clone https://github.com/cloudengine-labs/devops_os.git
cd devops_os
pip install -r cli/requirements.txt

# 2. Generate a GitHub Actions workflow
python -m cli.scaffold_gha --name my-app --languages python,javascript --type complete
# Output: .github/workflows/my-app-complete.yml

# 3. Generate a GitLab CI pipeline
python -m cli.scaffold_gitlab --name my-app --languages python --type complete
# Output: .gitlab-ci.yml

# 4. Generate SRE configs (Prometheus + Grafana + SLO)
python -m cli.scaffold_sre --name my-app --team platform
# Output: sre/ directory
```

> [!NOTE]
> **New here?** Start with the [Getting Started guide]({{< relref "/docs/getting-started" >}}) for a step-by-step walkthrough.

---

## Supported Platforms

| Category | Tools |
|----------|-------|
| **CI/CD** | GitHub Actions, GitLab CI, Jenkins |
| **GitOps / Deploy** | ArgoCD, Flux CD, kubectl, Kustomize |
| **Containers** | Docker, Helm |
| **SRE / Observability** | Prometheus, Grafana, SLO (Sloth-compatible) |
| **AI Integration** | Claude MCP Server, OpenAI function calling |
| **Languages** | Python · Java · Go · JavaScript / TypeScript |

---

## Documentation

| Guide | Description |
|-------|-------------|
| [Getting Started]({{< relref "/docs/getting-started" >}}) | Zero to first pipeline in 5 minutes |
| [Quick Start Reference]({{< relref "/docs/getting-started/quickstart" >}}) | All CLI commands at a glance |
| [GitHub Actions]({{< relref "/docs/ci-cd/github-actions" >}}) | Generate GHA workflows |
| [GitLab CI]({{< relref "/docs/ci-cd/gitlab-ci" >}}) | Generate GitLab pipelines |
| [Jenkins]({{< relref "/docs/ci-cd/jenkins" >}}) | Generate Jenkinsfiles |
| [ArgoCD & Flux]({{< relref "/docs/gitops" >}}) | Generate GitOps configs |
| [SRE Configuration]({{< relref "/docs/sre" >}}) | Generate monitoring & alerting configs |
| [Kubernetes]({{< relref "/docs/kubernetes" >}}) | Generate K8s manifests |
| [Dev Container]({{< relref "/docs/dev-container" >}}) | Configure the dev container |
| [AI Integration]({{< relref "/docs/ai-integration" >}}) | MCP server & AI skills |
| [CLI Reference]({{< relref "/docs/reference" >}}) | Full CLI options and output paths |
