---
title: "Getting Started"
weight: 10
bookCollapseSection: true
---

# Getting Started with DevOps-OS

Welcome! This guide walks you through DevOps-OS from **zero to your first generated pipeline** in under five minutes.

---

## What is DevOps-OS?

DevOps-OS is a toolkit that generates production-ready CI/CD pipelines, Kubernetes manifests, and SRE monitoring configs — so you can stop writing boilerplate and start shipping.

| Category | Tools |
|----------|-------|
| CI/CD | GitHub Actions, GitLab CI, Jenkins |
| GitOps / Deploy | ArgoCD, Flux CD, kubectl, Kustomize |
| Containers | Docker, Helm |
| SRE / Observability | Prometheus alert rules, Grafana dashboards, SLO configs |
| AI Integration | Claude (MCP Server), OpenAI (function calling) |

---

## Prerequisites

| Requirement | Why |
|------------|-----|
| Python 3.10+ | Runs the CLI generators |
| pip | Installs Python dependencies |
| Git | Clones the repo |
| Docker *(optional)* | Builds / runs the dev container |
| VS Code + Dev Containers extension *(optional)* | Opens the pre-configured dev environment |

---

## 1 — Clone and install

```bash
git clone https://github.com/cloudengine-labs/devops_os.git
cd devops_os
```

**Set up a virtual environment** (strongly recommended):

```bash
python -m venv .venv

# Activate
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows (cmd)
# .venv\Scripts\Activate.ps1     # Windows (PowerShell)
```

**Install the CLI dependencies:**

```bash
pip install -r cli/requirements.txt
```

> [!WARNING]
> Run `source .venv/bin/activate` in every new terminal session before using `python -m cli.*` commands.

---

## 2 — Generate your first CI/CD pipeline

### GitHub Actions

```bash
python -m cli.scaffold_gha --name my-app --languages python,javascript --type complete
```

**Output:** `.github/workflows/my-app-complete.yml`

### GitLab CI

```bash
python -m cli.scaffold_gitlab --name my-app --languages python --type complete
```

**Output:** `.gitlab-ci.yml`

### Jenkins

```bash
python -m cli.scaffold_jenkins --name my-app --languages java --type complete
```

**Output:** `Jenkinsfile`

---

## 3 — Generate Kubernetes / GitOps configs

```bash
# ArgoCD Application CR + AppProject
python -m cli.scaffold_argocd --name my-app \
       --repo https://github.com/myorg/my-app.git \
       --namespace production
# Output: argocd/application.yaml + argocd/appproject.yaml

# Flux CD configs
python -m cli.scaffold_argocd --name my-app --method flux \
       --repo https://github.com/myorg/my-app.git
# Output: flux/ directory
```

---

## 4 — Generate SRE configs

```bash
python -m cli.scaffold_sre --name my-app --team platform
```

**Output:** `sre/` directory containing:
- `alert-rules.yaml` — Prometheus PrometheusRule CR
- `grafana-dashboard.json` — Grafana importable dashboard
- `slo.yaml` — Sloth-compatible SLO manifest
- `alertmanager-config.yaml` — Alertmanager routing stub

---

## 5 — Interactive wizard (all-in-one)

```bash
python -m cli.devopsos init              # interactive project configurator
python -m cli.devopsos scaffold gha      # scaffold GitHub Actions
python -m cli.devopsos scaffold gitlab   # scaffold GitLab CI
python -m cli.devopsos scaffold jenkins  # scaffold Jenkins
python -m cli.devopsos scaffold argocd   # scaffold ArgoCD / Flux
python -m cli.devopsos scaffold sre      # scaffold SRE configs
```

---

## 6 — Use with an AI assistant

```bash
pip install -r mcp_server/requirements.txt
python mcp_server/server.py
```

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "devops-os": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/path/to/devops_os"
    }
  }
}
```

Then ask Claude: *"Generate a complete GitLab CI pipeline for a Python Flask API with Docker build and ArgoCD deployment."*

---

## Next steps

| I want to… | Read |
|-----------|------|
| See every CLI option and output path | [CLI Reference]({{< relref "/docs/reference" >}}) |
| Deep-dive GitHub Actions | [GitHub Actions]({{< relref "/docs/ci-cd/github-actions" >}}) |
| Deep-dive GitLab CI | [GitLab CI]({{< relref "/docs/ci-cd/gitlab-ci" >}}) |
| Deep-dive Jenkins | [Jenkins]({{< relref "/docs/ci-cd/jenkins" >}}) |
| Learn ArgoCD integration | [GitOps & ArgoCD]({{< relref "/docs/gitops" >}}) |
| Set up SRE monitoring configs | [SRE Configuration]({{< relref "/docs/sre" >}}) |
| Set up the dev container | [Dev Container]({{< relref "/docs/dev-container" >}}) |
| Use with Claude / ChatGPT | [AI Integration]({{< relref "/docs/ai-integration" >}}) |
