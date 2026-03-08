<div align="center">

# 🚀 DevOps-OS

**Automate your entire DevOps lifecycle — from CI/CD pipelines to Kubernetes deployments and SRE dashboards — using a conversational AI assistant or a single CLI command.**

[![CI](https://github.com/cloudengine-labs/devops_os/actions/workflows/ci.yml/badge.svg)](https://github.com/cloudengine-labs/devops_os/actions/workflows/ci.yml)
[![Sanity Tests](https://github.com/cloudengine-labs/devops_os/actions/workflows/sanity.yml/badge.svg)](https://github.com/cloudengine-labs/devops_os/actions/workflows/sanity.yml)
[![Version](https://img.shields.io/badge/version-0.1.0-blue)](CHANGELOG.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Open Source](https://img.shields.io/badge/open%20source-%E2%9D%A4-red)](https://github.com/cloudengine-labs/devops_os)

<br/>

> **Category:** DevOps Automation · AI-Assisted Infrastructure · GitOps · SRE Tooling

</div>

---

## ✨ What is DevOps-OS?

DevOps-OS is an open-source DevOps automation platform that scaffolds production-ready CI/CD pipelines, Kubernetes configurations, and SRE observability configs — in seconds, from a single CLI command or an AI chat prompt.

| Feature | Description |
|---------|-------------|
| 🚀 **CI/CD Generators** | One-command scaffolding for GitHub Actions, GitLab CI, and Jenkins pipelines |
| ☸️ **GitOps Config Generator** | Kubernetes manifests, ArgoCD Applications, and Flux CD Kustomizations |
| 📊 **SRE Config Generator** | Prometheus alert rules, Grafana dashboards, and SLO manifests |
| 🤖 **MCP Server** | Plug DevOps-OS tools into Claude or ChatGPT as native AI skills |
| 🛠️ **Dev Container** | Pre-configured multi-language environment (Python · Java · Go · JavaScript) |
| 🔄 **Process-First** | Built-in education on the Process-First SDLC philosophy and how it maps to every DevOps-OS tool |

---

## 🏗️ Tech Stack

<div align="center">

### CI/CD & GitOps
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![GitLab CI](https://img.shields.io/badge/GitLab%20CI-FC6D26?style=for-the-badge&logo=gitlab&logoColor=white)
![Jenkins](https://img.shields.io/badge/Jenkins-D24939?style=for-the-badge&logo=jenkins&logoColor=white)
![ArgoCD](https://img.shields.io/badge/ArgoCD-EF7B4D?style=for-the-badge&logo=argo&logoColor=white)
![Flux CD](https://img.shields.io/badge/Flux%20CD-5468FF?style=for-the-badge&logo=flux&logoColor=white)

### Kubernetes & Infrastructure
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Helm](https://img.shields.io/badge/Helm-0F1689?style=for-the-badge&logo=helm&logoColor=white)
![Kustomize](https://img.shields.io/badge/Kustomize-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

### Observability
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)

### Languages
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Go](https://img.shields.io/badge/Go-00ADD8?style=for-the-badge&logo=go&logoColor=white)
![Java](https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

### AI Integration
![Claude](https://img.shields.io/badge/Claude%20MCP-7C3AED?style=for-the-badge&logo=anthropic&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI%20Functions-412991?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyByb2xlPSJpbWciIHZpZXdCb3g9IjAgMCAyNCAyNCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48dGl0bGU+T3BlbkFJPC90aXRsZT48cGF0aCBkPSJNMjIuMjgxOSA5LjgyMTFhNS45ODQ3IDUuOTg0NyAwIDAgMC0uNTE1Ny00LjkxMDggNi4wNDYyIDYuMDQ2MiAwIDAgMC02LjUwOTgtMi45QTYuMDY1MSA2LjA2NTEgMCAwIDAgNC45ODA3IDQuMTgxOGE1Ljk4NDcgNS45ODQ3IDAgMCAwLTMuOTk3NyAyLjkgNi4wNDYyIDYuMDQ2MiAwIDAgMCAuNzQyNyA3LjA5NjYgNS45OCA1Ljk4IDAgMCAwIC41MTEgNC45MTA3IDYuMDUxIDYuMDUxIDAgMCAwIDYuNTE0NiAyLjkwMDFBNS45ODQ3IDUuOTg0NyAwIDAgMCAxMy4yNTk5IDI0YTYuMDU1NyA2LjA1NTcgMCAwIDAgNS43NzE4LTQuMjA1OCA1Ljk4OTQgNS45ODk0IDAgMCAwIDMuOTk3Ny0yLjkwMDEgNi4wNTU3IDYuMDU1NyAwIDAgMC0uNzQ3NS03LjA3Mjl6bS05LjAyMiAxMi42MDgxYTQuNDc1NSA0LjQ3NTUgMCAwIDEtMi44NzY0LTEuMDQwOGwuMTQxOS0uMDgwNCA0Ljc3ODMtMi43NTgyYS43OTQ4Ljc5NDggMCAwIDAgLjM5MjctLjY4MTN2LTYuNzM2OWwyLjAyIDEuMTY4NmEuMDcxLjA3MSAwIDAgMSAuMDM4LjA1MnY1LjU4MjZhNC41MDQgNC41MDQgMCAwIDEtNC40OTQ1IDQuNDk0NHptLTkuNjYwNy00LjEyNTRhNC40NzA4IDQuNDcwOCAwIDAgMS0uNTM0Ni0zLjAxMzdsLjE0Mi4wODUyIDQuNzgzIDIuNzU4MmEuNzcxMi43NzEyIDAgMCAwIC43ODA2IDBsNS44NDI4LTMuMzY4NXYyLjMzMjRhLjA4MDQuMDgwNCAwIDAgMS0uMDMzMi4wNjE1TDkuNzQgMTkuOTUwMmE0LjQ5OTIgNC40OTkyIDAgMCAxLTYuMTQwOC0xLjY0NjR6TTIuMzQwOCA3Ljg5NTZhNC40ODUgNC40ODUgMCAwIDEgMi4zNjU1LTEuOTcyOFYxMS42YS43NjY0Ljc2NjQgMCAwIDAgLjM4NzkuNjc2NWw1LjgxNDQgMy4zNTQzLTIuMDIwMSAxLjE2ODVhLjA3NTcuMDc1NyAwIDAgMS0uMDcxIDBsLTQuODMwMy0yLjc4NjVBNC41MDQgNC41MDQgMCAwIDEgMi4zNDA4IDcuODcyem0xNi41OTYzIDMuODU1OEwxMy4xMDM4IDguMzY0IDE1LjExOTIgNy4yYS4wNzU3LjA3NTcgMCAwIDEgLjA3MSAwbDQuODMwMyAyLjc5MTNhNC40OTQ0IDQuNDk0NCAwIDAgMS0uNjc2NSA4LjEwNDJ2LTUuNjc3MmEuNzkuNzkgMCAwIDAtLjQwNy0uNjY3em0yLjAxMDctMy4wMjMxbC0uMTQyLS4wODUyLTQuNzczNS0yLjc4MThhLjc3NTkuNzc1OSAwIDAgMC0uNzg1NCAwTDkuNDA5IDkuMjI5N1Y2Ljg5NzRhLjA2NjIuMDY2MiAwIDAgMSAuMDI4NC0uMDYxNWw0LjgzMDMtMi43ODY2YTQuNDk5MiA0LjQ5OTIgMCAwIDEgNi42ODAyIDQuNjZ6TTguMzA2NSAxMi44NjNsLTIuMDItMS4xNjM4YS4wODA0LjA4MDQgMCAwIDEtLjAzOC0uMDU2N1Y2LjA3NDJhNC40OTkyIDQuNDk5MiAwIDAgMSA3LjM3NTctMy40NTM3bC0uMTQyLjA4MDVMOC43MDQgNS40NTlhLjc5NDguNzk0OCAwIDAgMC0uMzkyNy42ODEzem0xLjA5NzYtMi4zNjU0bDIuNjAyLTEuNDk5OCAyLjYwNjkgMS40OTk4djIuOTk5NGwtMi41OTc0IDEuNDk5Ny0yLjYwNjctMS40OTk3WiIvPjwvc3ZnPg==&logoColor=white)
![GitHub Copilot](https://img.shields.io/badge/GitHub%20Copilot-000000?style=for-the-badge&logo=githubcopilot&logoColor=white)

</div>

---

## ⚡ Quick Start

### Prerequisites

- Python 3.10+ and `pip`
- Docker *(for the dev container)*
- VS Code + [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) *(optional)*

---

### 1 — Clone & install

```bash
git clone https://github.com/cloudengine-labs/devops_os.git
cd devops_os

# Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows (cmd / PowerShell)

pip install -r cli/requirements.txt
```

---

### 2 — Learn the Process-First philosophy *(recommended first step)*

DevOps-OS is built on the **Process-First** SDLC philosophy from [cloudenginelabs.io](https://cloudenginelabs.io). Run the `process-first` command to understand *why* each tool exists before you start using it:

```bash
# Full overview — what Process-First is, how it maps to DevOps-OS, and learning tips
python -m cli.devopsos process-first

# Just the 5 core principles
python -m cli.devopsos process-first --section what

# Table: which scaffold command encodes which principle
python -m cli.devopsos process-first --section mapping

# AI prompts and book recommendations for beginners
python -m cli.devopsos process-first --section tips
```

> **Tip:** Run `--section mapping` to see exactly which `devopsos scaffold` command to use for each DevOps goal before generating any config.  
> See [docs/PROCESS-FIRST.md](docs/PROCESS-FIRST.md) for the full reference.

---

### 3 — Generate a GitHub Actions workflow

```bash
# Complete CI/CD for a Python + JavaScript project
python -m cli.scaffold_gha --name my-app --languages python,javascript --type complete

# With Kubernetes deployment via Kustomize
python -m cli.scaffold_gha --name my-app --languages python --kubernetes --k8s-method kustomize
```

---

### 4 — Generate other pipelines & configs

```bash
# Jenkins pipeline → Jenkinsfile
python -m cli.scaffold_jenkins --name my-app --languages java --type complete

# GitLab CI pipeline → .gitlab-ci.yml
python -m cli.scaffold_gitlab --name my-app --languages python,go --type complete

# ArgoCD GitOps configs → argocd/application.yaml + argocd/appproject.yaml
python -m cli.scaffold_argocd --name my-app --repo https://github.com/myorg/my-app.git

# Flux GitOps configs → flux/git-repository.yaml + flux/kustomization.yaml + flux/image-update-automation.yaml
python -m cli.scaffold_argocd --name my-app --method flux --repo https://github.com/myorg/my-app.git

# SRE configs (Prometheus, Grafana, SLO) → sre/ directory
python -m cli.scaffold_sre --name my-app --team platform --slo-target 99.9

# Dev container configuration → .devcontainer/devcontainer.json + .devcontainer/devcontainer.env.json
python -m cli.scaffold_devcontainer --languages python,go --cicd-tools docker,terraform --kubernetes-tools k9s,flux

# Kubernetes manifests
python kubernetes/k8s-config-generator.py --name my-app --image ghcr.io/myorg/my-app:v1
```

> See [CLI Commands Reference](docs/CLI-COMMANDS-REFERENCE.md) for the full option tables and every default output path.

---

### 5 — Interactive wizard (all-in-one) - **WIP**

```bash
python -m cli.devopsos init              # interactive project configurator
python -m cli.devopsos scaffold gha      # scaffold GitHub Actions
python -m cli.devopsos scaffold gitlab   # scaffold GitLab CI
python -m cli.devopsos scaffold jenkins  # scaffold Jenkins
python -m cli.devopsos scaffold argocd       # scaffold ArgoCD / Flux
python -m cli.devopsos scaffold sre          # scaffold SRE configs
python -m cli.devopsos scaffold devcontainer # scaffold dev container config
```

Single Click Platform Engineering Capabilities

---

### 6 — Use with AI (MCP Server) - **WIP**

```bash
pip install -r mcp_server/requirements.txt
python mcp_server/server.py
```

Add to your `claude_desktop_config.json` and ask Claude:
> *"Generate a complete CI/CD GitHub Actions workflow for my Python API with Kubernetes deployment using ArgoCD."*

See **[mcp_server/README.md](mcp_server/README.md)** for full setup and **[skills/README.md](skills/README.md)** for Claude API & OpenAI function-calling examples.

---

## 📁 Repository Structure

```text
devops_os/
├── .devcontainer/      # Dev container config (Dockerfile, devcontainer.json, setup scripts)
├── .github/workflows/  # CI, Sanity Tests, and GitHub Pages workflows
├── cli/                # CLI scaffold tools (scaffold_gha, gitlab, jenkins, argocd, sre, devopsos)
├── kubernetes/         # Kubernetes manifest generator
├── mcp_server/         # MCP server for AI assistant integration (Claude, ChatGPT)
├── skills/             # Claude & OpenAI tool/function definitions
├── docs/               # Detailed guides and test reports
├── tests/              # Comprehensive test suite
├── go-project/         # Example Go application
└── scripts/            # Helper scripts
```

---

## 🧪 Testing

[![Sanity Tests](https://github.com/cloudengine-labs/devops_os/actions/workflows/sanity.yml/badge.svg)](https://github.com/cloudengine-labs/devops_os/actions/workflows/sanity.yml)

All tests run without real infrastructure — everything uses in-memory mock data.

```bash
pip install -r cli/requirements.txt -r mcp_server/requirements.txt pytest pytest-html
python -m pytest cli/test_cli.py mcp_server/test_server.py tests/test_comprehensive.py -v
```

**Latest results:** ✅ 162 passed · ⚠️ 3 xfailed (known tracked bugs) · ❌ 0 failed

| Report | Description |
|--------|-------------|
| [📋 Detailed Test Report](docs/TEST_REPORT.md) | Full results with CLI output samples for every scaffold command |
| [🌐 Interactive HTML Report](docs/test-reports/test-report.html) | Self-contained pytest HTML report |
| [📄 CLI Output Examples](docs/test-reports/cli-output-examples.md) | Real captured output for all scaffold sub-commands |
| [⚙️ Sanity Workflow](.github/workflows/sanity.yml) | GitHub Actions workflow running all scenarios on every push |

---

## 🛠️ Dev Container

The pre-configured dev container gives you a consistent multi-language environment with all CI/CD tools included.

<details>
<summary><strong>Supported languages & tools</strong></summary>

| Category | Tools |
|----------|-------|
| **Languages** | Python 3.11 · Java 17 · Node.js 20 · Go 1.21 |
| **Build tools** | pip · Maven · Gradle · npm · yarn |
| **Linting/Testing** | pytest · black · flake8 · mypy · Jest · ESLint · golangci-lint |
| **Containers** | Docker CLI · Docker Compose |
| **IaC** | Terraform |
| **Kubernetes** | kubectl · Helm · Kustomize · K9s · KinD · Minikube |
| **GitOps** | ArgoCD CLI · Flux CD |
| **Secrets** | Kubeseal (Sealed Secrets) |
| **Observability** | Prometheus · Grafana |

</details>


Generate a dev container configuration from the CLI instead of editing JSON by hand:

```bash
# Generate devcontainer.json and devcontainer.env.json for a Python + Go project
python -m cli.scaffold_devcontainer \
  --languages python,go \
  --cicd-tools docker,terraform,kubectl \
  --kubernetes-tools k9s,flux \
  --devops-tools prometheus,grafana

# Or use the unified CLI
python -m cli.devopsos scaffold devcontainer
```

You can also customize `.devcontainer/devcontainer.env.json` directly to enable or disable any language or tool, then reopen in VS Code.

---

## 📚 Documentation

| Guide | Description |
|-------|-------------|
| [🚀 Getting Started](docs/GETTING-STARTED.md) | Easy step-by-step guide — **start here** |
| [📖 CLI Commands Reference](docs/CLI-COMMANDS-REFERENCE.md) | **Complete reference** — every option, input file, and output location |
| [🔄 Process-First Philosophy](docs/PROCESS-FIRST.md) | What Process-First means, how it maps to DevOps-OS, and AI learning tips |
| [📦 Dev Container Setup](docs/DEVOPS-OS-README.md) | Set up and customize the dev container |
| [⚡ Quick Start Reference](docs/DEVOPS-OS-QUICKSTART.md) | Essential CLI commands for all features |
| [⚙️ GitHub Actions Generator](docs/GITHUB-ACTIONS-README.md) | Generate and customize GitHub Actions workflows |
| [🦊 GitLab CI Generator](docs/GITLAB-CI-README.md) | Generate and customize GitLab CI pipelines |
| [🔧 Jenkins Pipeline Generator](docs/JENKINS-PIPELINE-README.md) | Generate and customize Jenkins pipelines |
| [🔄 ArgoCD / Flux GitOps](docs/ARGOCD-README.md) | Generate ArgoCD Applications and Flux Kustomizations |
| [📊 SRE Configuration](docs/SRE-CONFIGURATION-README.md) | Prometheus rules, Grafana dashboards, SLO manifests |
| [☸️ Kubernetes Deployments](docs/KUBERNETES-DEPLOYMENT-README.md) | Generate and manage Kubernetes deployment configs |
| [🤖 MCP Server](mcp_server/README.md) | Connect DevOps-OS tools to Claude or ChatGPT |
| [🧠 AI Skills](skills/README.md) | Use DevOps-OS with the Anthropic API or OpenAI function calling |

---

## 🤝 Contributing

Contributions are welcome! Whether it's a bug fix, a new scaffold generator, or documentation improvement — feel free to open an issue or submit a pull request.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'feat: add my feature'`
4. Push and open a pull request

Read contribution guideline [here](CONTRIBUTING.md)

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
Made with ❤️ by <a href="https://github.com/cloudengine-labs">CloudEngine Labs</a>
</div>
