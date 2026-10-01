---
title: "Getting Started"
weight: 10
bookCollapseSection: true
---

# Getting Started with DevOps-OS MCP Server

Welcome! **DevOps-OS MCP Server** is the Model Context Protocol implementation that connects AI assistants (Claude, ChatGPT, etc.) with DevOps-OS generators.

> **📌 About the Two Projects**
> - **DevOps-OS MCP** (this repo): MCP server for AI assistant integration
> - **DevOps-OS CLI** (see [chefgs/devops_os](https://github.com/chefgs/devops_os)): Original command-line tool
> 
> Both share the same core scaffold modules. Choose based on your use case:
> - **Use MCP** if you want to integrate with Claude, ChatGPT, Cursor, or other AI assistants
> - **Use CLI** if you want to run generators in scripts, pipelines, or local automation

---

## What is DevOps-OS MCP?

DevOps-OS MCP is a toolkit that generates production-ready CI/CD pipelines, Kubernetes manifests, infrastructure hardening baselines, and SRE monitoring configs — **through conversational AI** using the MCP server.

Ask Claude or ChatGPT:

```
"Generate a complete GitHub Actions CI/CD workflow for a Python Flask API with Docker build, pytest tests, and deployment to Kubernetes."
```

You get production-ready YAML in seconds.

| Category | What You Can Generate |
|----------|-------|
| CI/CD | GitHub Actions, GitLab CI, Jenkins workflows |
| GitOps / Deploy | ArgoCD Applications, Flux CD Kustomizations |
| Containers | Docker configs, Helm charts |
| Hardening / Compliance | Kyverno policies, InSpec profiles, Checkov checks |
| SRE / Observability | Prometheus alert rules, Grafana dashboards, SLO configs |
| Unit Testing | pytest, Jest, Vitest, Mocha, Go test scaffolds |
| Dev Environment | Dev container configuration |

---

## Prerequisites

| Requirement | Why |
|------------|-----|
| Python 3.10+ | Runs the MCP server |
| pip | Installs Python dependencies |
| Git | Clones the repo |
| Claude Desktop or ChatGPT | The AI assistant you'll use to generate configs |

---

## Quick Start: 5 Minutes to First Generated Config

### Step 1: Clone and Install

```bash
git clone https://github.com/chefgs/devops_os_mcp.git
cd devops_os_mcp

# Set up Python environment
python3 -m venv .venv
source .venv/bin/activate  # macOS / Linux
# .venv\Scripts\activate   # Windows (cmd)

# Install MCP server dependencies
pip install -r mcp_server/requirements.txt
```

### Step 2: Configure Claude Desktop (or ChatGPT)

**For Claude Desktop:**

1. Get your repo path: `pwd` (copy output)
2. Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
3. Add this config:

```json
{
  "mcpServers": {
    "devops-os": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/your/repo/path/here"
    }
  }
}
```

4. Restart Claude Desktop. You'll see a wrench icon 🔧 at the bottom right.

**For ChatGPT or other MCP clients:**

See [MCP Setup & Configuration]({{< relref "/docs/ai-integration/mcp-setup" >}}) for detailed instructions.

### Step 3: Generate Your First Config

Ask Claude:

```
Generate a GitHub Actions workflow for a Python Flask API with:
- Lint and test stages (using pytest)
- Docker build and push to Docker Hub
- Deployment to Kubernetes
```

Done! Claude will generate the complete workflow YAML.

---

## 🎯 Example Prompts to Try

Once connected, try these prompts:

| What You Want | Prompt |
|---------------|--------|
| GitHub Actions Workflow | Generate a GitHub Actions CI/CD workflow for a Python project with Docker build and deployment to AWS |
| Jenkins Pipeline | Create a Declarative Jenkins Pipeline for a Java Spring Boot app with Maven build and ArgoCD deployment |
| Kubernetes Manifests | Generate Kubernetes manifests for a Node.js microservice with 3 replicas and a LoadBalancer service |
| SRE Dashboards | Generate Prometheus alert rules and Grafana dashboards for a microservice with 99.9% SLO |
| Hardening Policies | Generate Kyverno policies for a production Kubernetes cluster based on CIS Benchmarks |
| Dev Container | Scaffold a dev container for Python + Go development with Terraform, kubectl, and k9s |

---

## Learn More About DevOps-OS Philosophy

**[Process-First SDLC Philosophy →]({{< relref "/docs/getting-started/process-first" >}})**

Understand *why* each generator exists and how it maps to software development best practices.

See the [Process-First guide]({{< relref "/docs/getting-started/process-first" >}}) for the full reference.

---

## 3 — Generate your first CI/CD pipeline

All scaffold generators are subcommands of the unified `devopsos scaffold` command. Use `--help` on any subcommand to see all options.

### GitHub Actions

```bash
python -m cli.devopsos scaffold gha --name my-app --languages python,javascript --type complete
```

**Output:** `.github/workflows/my-app-complete.yml`

### GitLab CI

```bash
python -m cli.devopsos scaffold gitlab --name my-app --languages python --type complete
```

**Output:** `.gitlab-ci.yml`

### Jenkins

```bash
python -m cli.devopsos scaffold jenkins --name my-app --languages java --type complete
```

**Output:** `Jenkinsfile`

---

## 4 — Generate Kubernetes / GitOps configs

```bash
# ArgoCD Application CR + AppProject
python -m cli.devopsos scaffold argocd --name my-app \
       --repo https://github.com/myorg/my-app.git \
       --namespace production
# Output: argocd/application.yaml + argocd/appproject.yaml

# Flux CD configs
python -m cli.devopsos scaffold argocd --name my-app --method flux \
       --repo https://github.com/myorg/my-app.git
# Output: flux/ directory
```

---

## 5 — Generate infrastructure hardening baselines

```bash
# Kubernetes policy baselines
python -m cli.devopsos scaffold hardening --standard cis-k8s --type kyverno --environment production

# Operating system compliance profiles
python -m cli.devopsos scaffold hardening --standard cis-rhel9 --type inspec
```

**Output:** `hardening/` directory containing Kyverno policies, InSpec profiles, Checkov checks, and a compliance mapping file.

See [Infrastructure Hardening]({{< relref "/docs/platform-engineering/hardening" >}}) for supported standards and validation examples.

---

## 6 — Generate SRE configs

```bash
python -m cli.devopsos scaffold sre --name my-app --team platform
```

**Output:** `sre/` directory containing:
- `alert-rules.yaml` — Prometheus PrometheusRule CR
- `grafana-dashboard.json` — Grafana importable dashboard
- `slo.yaml` — Sloth-compatible SLO manifest
- `alertmanager-config.yaml` — Alertmanager routing stub

---

## 7 — Generate unit test configs

```bash
# Python — generates pytest.ini, conftest.py, and a sample test file
python -m cli.devopsos scaffold unittest --name my-app --languages python

# JavaScript with Jest
python -m cli.devopsos scaffold unittest --name my-app --languages javascript --framework jest

# TypeScript with Vitest
python -m cli.devopsos scaffold unittest --name my-app --languages typescript --framework vitest

# Multi-stack (Python + JavaScript + Go) in one command
python -m cli.devopsos scaffold unittest --name my-platform --languages python,javascript,go
```

See [CLI Reference]({{< relref "/docs/reference" >}}) for all options and output file paths.

---

## 8 — Interactive wizard (all-in-one)

```bash
python -m cli.devopsos init              # interactive project configurator
python -m cli.devopsos scaffold gha      # scaffold GitHub Actions
python -m cli.devopsos scaffold gitlab   # scaffold GitLab CI
python -m cli.devopsos scaffold jenkins  # scaffold Jenkins
python -m cli.devopsos scaffold argocd   # scaffold ArgoCD / Flux
python -m cli.devopsos scaffold hardening # scaffold hardening baselines
python -m cli.devopsos scaffold sre      # scaffold SRE configs
python -m cli.devopsos scaffold cicd     # scaffold GHA + Jenkins in one step
python -m cli.devopsos scaffold unittest # scaffold unit test configs
```

---

## 9 — Use with an AI assistant

### Via MCP (Recommended — Native Integration)

Use DevOps-OS as an **MCP server in Claude Desktop or ChatGPT** for seamless integration.

**For Claude Desktop (5-minute setup):**
```bash
pip install -r mcp_server/requirements.txt
```
Then see **[MCP Quick Start]({{< relref "/docs/getting-started/mcp-quickstart" >}})** for step-by-step instructions.

**For ChatGPT, HTTP endpoints, and production deployment:**
See **[MCP Setup & Configuration]({{< relref "/docs/ai-integration/mcp-setup" >}})** for detailed setup guide.

### Via API (Alternative — Direct API Calls)

Load tools from `skills/` directory and call Claude or OpenAI APIs directly:

---

## 10 — Next steps

| I want to… | Read |
|-----------|------|
| **Use MCP with Claude Desktop** | [MCP Quick Start]({{< relref "/docs/getting-started/mcp-quickstart" >}}) (5 minutes) |
| **Set up MCP for ChatGPT, HTTP, production** | [MCP Setup & Configuration]({{< relref "/docs/ai-integration/mcp-setup" >}}) (detailed) |
| Understand the Process-First philosophy | [Process-First guide]({{< relref "/docs/getting-started/process-first" >}}) |
| See every CLI option and output path | [CLI Reference]({{< relref "/docs/reference" >}}) |
| Generate infrastructure hardening baselines | [Infrastructure Hardening]({{< relref "/docs/platform-engineering/hardening" >}}) |
| Deep-dive GitHub Actions | [GitHub Actions]({{< relref "/docs/ci-cd/github-actions" >}}) |
| Deep-dive GitLab CI | [GitLab CI]({{< relref "/docs/ci-cd/gitlab-ci" >}}) |
| Deep-dive Jenkins | [Jenkins]({{< relref "/docs/ci-cd/jenkins" >}}) |
| Learn ArgoCD integration | [GitOps & ArgoCD]({{< relref "/docs/gitops" >}}) |
| Set up SRE monitoring configs | [SRE Configuration]({{< relref "/docs/sre" >}}) |
| Set up the dev container | [Dev Container]({{< relref "/docs/dev-container" >}}) |
| Explore all AI integration options | [AI Integration Overview]({{< relref "/docs/ai-integration" >}}) |
