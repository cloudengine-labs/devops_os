---
title: "DevOps-OS"
type: "docs"
---

# 🚀 DevOps-OS

**Automate your entire DevOps lifecycle — from CI/CD pipelines to Kubernetes deployments and SRE dashboards — using a conversational AI assistant or a single CLI command.**

[![CI](https://github.com/cloudengine-labs/devops_os/actions/workflows/ci.yml/badge.svg)](https://github.com/cloudengine-labs/devops_os/actions/workflows/ci.yml)
[![Sanity Tests](https://github.com/cloudengine-labs/devops_os/actions/workflows/sanity.yml/badge.svg)](https://github.com/cloudengine-labs/devops_os/actions/workflows/sanity.yml)
[![Version](https://img.shields.io/badge/version-0.2.0-blue)](https://github.com/cloudengine-labs/devops_os/blob/main/CHANGELOG.md)
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
| 🔄 | **Process-First** | Built-in education on the Process-First SDLC philosophy and how every tool maps to an SDLC principle — [→ Process-First guide]({{< relref "/docs/getting-started/process-first" >}}) |
| 📖 | **CLI Reference** | Complete option tables, input files, and exact output paths for every command — [→ CLI Reference]({{< relref "/docs/reference" >}}) |

---

## ⚡ Quick Start

```bash
# 1. Clone and install
git clone https://github.com/cloudengine-labs/devops_os.git
cd devops_os
pip install -r cli/requirements.txt

# 2. Learn the Process-First philosophy (recommended first step)
python -m cli.devopsos process-first

# 3. Generate a GitHub Actions workflow
python -m cli.devopsos scaffold gha --name my-app --languages python,javascript --type complete
# Output: .github/workflows/my-app-complete.yml

# 4. Generate a GitLab CI pipeline
python -m cli.devopsos scaffold gitlab --name my-app --languages python --type complete
# Output: .gitlab-ci.yml

# 5. Generate SRE configs (Prometheus + Grafana + SLO)
python -m cli.devopsos scaffold sre --name my-app --team platform
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
| [Process-First Philosophy]({{< relref "/docs/getting-started/process-first" >}}) | What Process-First means, how it maps to DevOps-OS, and AI learning tips |
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
