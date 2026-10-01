---
title: "DevOps-OS"
type: "docs"
---

# 🚀 DevOps-OS MCP Server

**Model Context Protocol implementation of DevOps-OS — Generate production-ready CI/CD pipelines, Kubernetes configs, and SRE dashboards using Claude, ChatGPT, or any MCP-compatible AI assistant.**

[![CI](https://github.com/chefgs/devops_os_mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/chefgs/devops_os_mcp/actions/workflows/ci.yml)
[![Sanity Tests](https://github.com/chefgs/devops_os_mcp/actions/workflows/sanity.yml/badge.svg)](https://github.com/chefgs/devops_os_mcp/actions/workflows/sanity.yml)
[![Version](https://img.shields.io/badge/version-0.4.7-blue)](https://github.com/chefgs/devops_os_mcp/blob/main/CHANGELOG.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://github.com/chefgs/devops_os_mcp/blob/main/LICENSE)

---

## 📌 About DevOps-OS MCP

This project is the **MCP Server implementation** of DevOps-OS, designed to integrate with AI assistants. It's a separate project from the original CLI:

| Project | Purpose | URL |
|---------|---------|-----|
| **DevOps-OS MCP** (this repo) | MCP server for AI assistants (Claude, ChatGPT, Cursor, etc.) | [chefgs/devops_os_mcp](https://github.com/chefgs/devops_os_mcp) |
| **DevOps-OS CLI** | Original command-line tool for automation scripts and CI/CD | [chefgs/devops_os](https://github.com/chefgs/devops_os) |

Both projects share the same **core scaffold modules** but serve different use cases:
- **Use MCP** if you want to integrate with Claude, ChatGPT, Cursor, or other AI assistants
- **Use CLI** if you want to run generators in scripts, pipelines, or local automation

---

## What is DevOps-OS MCP?

DevOps-OS MCP is an open-source MCP server that scaffolds production-ready CI/CD pipelines, Kubernetes configurations, and SRE observability configs — in seconds, through conversational AI.

## Features

| | Feature | Description |
|--|---------|-------------|
| 🤖 | **MCP Server (Claude & ChatGPT)** | Plug DevOps-OS tools into Claude or ChatGPT as native AI skills — [→ AI Integration]({{< relref "/docs/ai-integration" >}}) |
| 🚀 | **CI/CD Generators** | Generate GitHub Actions, GitLab CI, and Jenkins pipelines — [→ CI/CD Generators]({{< relref "/docs/ci-cd" >}}) |
| ☸️ | **GitOps Config Generator** | Kubernetes manifests, ArgoCD Applications, and Flux CD Kustomizations — [→ GitOps & ArgoCD]({{< relref "/docs/gitops" >}}) |
| 📊 | **SRE Config Generator** | Prometheus alert rules, Grafana dashboards, and SLO manifests — [→ SRE Configuration]({{< relref "/docs/sre" >}}) |
| 🔐 | **Infrastructure Hardening** | Generate Kyverno policies, InSpec profiles, Checkov checks, and compliance mappings — [→ Infrastructure Hardening]({{< relref "/docs/platform-engineering/hardening" >}}) |
| 🛠️ | **Dev Container** | Pre-configured multi-language environment: Python · Java · Go · JavaScript — [→ Dev Container]({{< relref "/docs/dev-container" >}}) |
| 🔄 | **Process-First** | Built-in education on the Process-First SDLC philosophy and how every tool maps to an SDLC principle — [→ Process-First guide]({{< relref "/docs/getting-started/process-first" >}}) |

---

## ⚡ Quick Start (MCP with Claude)

```bash
# 1. Clone and install MCP server
git clone https://github.com/chefgs/devops_os_mcp.git
cd devops_os_mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r mcp_server/requirements.txt

# 2. Get your path
pwd
# Copy the output (e.g., /Users/alice/projects/devops_os_mcp)

# 3. Add to Claude Desktop config
# macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
# Windows: %APPDATA%\Claude\claude_desktop_config.json
# Add this (replace path):
# {
#   "mcpServers": {
#     "devops-os": {
#       "command": "python",
#       "args": ["-m", "mcp_server.server"],
#       "cwd": "/your/path/here"
#     }
#   }
# }

# 4. Restart Claude Desktop
# You'll see a wrench icon 🔧 at the bottom right

# 5. Ask Claude to generate!
# "Generate a GitHub Actions workflow for a Python Flask API with Docker and Kubernetes deployment"
```

> [!NOTE]
> **New here?** Start with the [Easy Getting Started guide]({{< relref "/docs/getting-started/easy-getting-started" >}}) — copy-paste 3 commands + restart Claude.

---

## Supported Platforms

| Category | Tools |
|----------|-------|
| **CI/CD** | GitHub Actions, GitLab CI, Jenkins |
| **GitOps / Deploy** | ArgoCD, Flux CD, kubectl, Kustomize |
| **Containers** | Docker, Helm |
| **Hardening / Compliance** | Kyverno, InSpec, Checkov, Pod Security Standards, CIS / STIG / NSA baselines |
| **SRE / Observability** | Prometheus, Grafana, SLO (Sloth-compatible) |
| **AI Integration** | Claude MCP Server, OpenAI function calling |
| **Languages** | Python · Java · Go · JavaScript / TypeScript |

---

## Documentation

| Guide | Description |
|-------|-------------|
| [Easy Getting Started]({{< relref "/docs/getting-started/easy-getting-started" >}}) | **Fastest way:** Copy-paste 3 commands + restart Claude |
| [Getting Started]({{< relref "/docs/getting-started" >}}) | Step-by-step MCP setup walkthrough |
| [MCP Quick Start]({{< relref "/docs/getting-started/mcp-quickstart" >}}) | 5-minute Claude Desktop setup |
| [MCP Setup & Configuration]({{< relref "/docs/ai-integration/mcp-setup" >}}) | ChatGPT, HTTP endpoints, Docker, troubleshooting |
| [AI Integration]({{< relref "/docs/ai-integration" >}}) | MCP server & AI skills overview |
| [Process-First Philosophy]({{< relref "/docs/getting-started/process-first" >}}) | What Process-First means and how it maps to DevOps-OS tools |
| [Infrastructure Hardening]({{< relref "/docs/platform-engineering/hardening" >}}) | Generate security baselines and compliance mappings |
| [GitHub Actions]({{< relref "/docs/ci-cd/github-actions" >}}) | Generate and customize GHA workflows |
| [GitLab CI]({{< relref "/docs/ci-cd/gitlab-ci" >}}) | Generate and customize GitLab pipelines |
| [Jenkins]({{< relref "/docs/ci-cd/jenkins" >}}) | Generate and customize Jenkinsfiles |
| [ArgoCD & Flux]({{< relref "/docs/gitops" >}}) | Generate GitOps configs |
| [SRE Configuration]({{< relref "/docs/sre" >}}) | Generate monitoring & alerting configs |
| [Kubernetes]({{< relref "/docs/kubernetes" >}}) | Generate K8s manifests |
| [Dev Container]({{< relref "/docs/dev-container" >}}) | Configure the dev container |
| [Reference (Archives)]({{< relref "/docs/reference" >}}) | Historical CLI command options — for reference only |
| [Chennai FOSS 2026 Presentation]({{< relref "/docs/talks/chennai-foss-2026" >}}) | Conference deck with playback |
