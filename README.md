<div align="center">

# 🚀 DevOps-OS MCP Server

**MCP (Model Context Protocol) implementation of DevOps-OS — Generate production-ready CI/CD pipelines, Kubernetes configs, and SRE dashboards using Claude Desktop, ChatGPT, or any MCP-compatible AI assistant.**

- 💬 **Ask Claude / ChatGPT:** Use DevOps-OS MCP server to generate pipelines and configs with conversational AI
- 🔌 **Plug into APIs:** Integrate with Anthropic and OpenAI function calling
- 🚀 **AI-First Interface:** High-performance MCP backend for seamless AI integration

**📌 Note:** This is the MCP implementation. For the original CLI tool, see [cloudengine-labs/devops_os](https://github.com/cloudengine-labs/devops_os).

[![CI](https://github.com/cloudengine-labs/devops_os/actions/workflows/ci.yml/badge.svg)](https://github.com/cloudengine-labs/devops_os/actions/workflows/ci.yml)
[![Sanity Tests](https://github.com/cloudengine-labs/devops_os/actions/workflows/sanity.yml/badge.svg)](https://github.com/cloudengine-labs/devops_os/actions/workflows/sanity.yml)
[![Version](https://img.shields.io/badge/version-0.4.7-blue)](CHANGELOG.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Open Source](https://img.shields.io/badge/open%20source-%E2%9D%A4-red)](https://github.com/chefgs/devops_os_mcp)
[![GitHub Stars](https://img.shields.io/github/stars/chefgs/devops_os_mcp?style=social)](https://github.com/chefgs/devops_os_mcp/stargazers)

<br/>

> **Category:** DevOps Automation · AI-Assisted Infrastructure · GitOps · SRE Tooling · MCP Integration

</div>

---

## 📊 How It Works

<div align="center">
  <img src="https://raw.githubusercontent.com/chefgs/devops_os_mcp/main/assets/devops-os-mcp-how-it-works.png" alt="DevOps-OS MCP Architecture" width="100%" style="max-width: 1200px;"/>
</div>

---

## ✨ What is DevOps-OS MCP?

**DevOps-OS MCP** is the Model Context Protocol implementation of DevOps-OS that bridges AI assistants (Claude, ChatGPT, etc.) with production-ready DevOps configuration generators. It exposes all DevOps-OS scaffolding capabilities as MCP tools, enabling seamless AI-driven infrastructure automation.

### Two Projects, One Platform

| Project | Purpose | Use Case |
|---------|---------|----------|
| [**DevOps-OS CLI**](https://github.com/cloudengine-labs/devops_os) | Original command-line interface | Automation scripts, CI/CD pipelines, local development |
| **DevOps-OS MCP** (this repo) | MCP server implementation | Claude Desktop, ChatGPT, Cursor, VS Code Copilot integration |

Both projects share the same **core scaffold modules** for generating:

| Feature | Description |
|---------|-------------|
| 🤖 **MCP Server (Claude & ChatGPT)** | Use DevOps-OS MCP as an AI skill — ask Claude or ChatGPT in natural language, get production-ready configs and pipelines |
| 🚀 **CI/CD Generators** | One-command scaffolding for GitHub Actions, GitLab CI, and Jenkins pipelines |
| ☸️ **GitOps Config Generator** | Kubernetes manifests, ArgoCD Applications, and Flux CD Kustomizations |
| 📊 **SRE Config Generator** | Prometheus alert rules, Grafana dashboards, and SLO manifests |
| 🔐 **Infrastructure Hardening** | Generate Kyverno policies, InSpec profiles, Checkov checks, and compliance mappings for CIS, STIG, NSA/CISA, Pod Security Standards, and Essential Eight baselines |
| 🧪 **Unit Test Scaffold** | Generate pytest, Jest, Vitest, Mocha, or Go test configs with one command |
| 🛠️ **Dev Container** | Pre-configured multi-language environment (Python · Java · Go · JavaScript) |
| 🔄 **Process-First** | Built-in education on the Process-First SDLC philosophy and how it maps to every DevOps-OS tool |

---

## 👥 Who Is This For?

DevOps-OS is built for anyone who wants to **move faster** and **stop writing boilerplate DevOps configs by hand**.

| Audience | How DevOps-OS helps |
|----------|---------------------|
| **Solo developers** | Get a production-ready CI/CD pipeline in under a minute — no DevOps expertise needed |
| **DevOps / platform engineers** | Standardise pipeline templates across teams via AI chat interface |
| **SRE teams** | Generate Prometheus alert rules, Grafana dashboards, and SLO manifests instantly |
| **DevOps learners & students** | Learn the *Process-First* SDLC philosophy through runnable examples, not just theory |
| **AI / LLM builders** | Plug every scaffold tool into Claude or ChatGPT via the built-in MCP server |
| **Open-source contributors** | A well-structured Python project with a clean architecture and full test suite |

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

### Unit Testing
![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![Jest](https://img.shields.io/badge/Jest-C21325?style=for-the-badge&logo=jest&logoColor=white)
![Mocha](https://img.shields.io/badge/Mocha-8D6748?style=for-the-badge&logo=mocha&logoColor=white)
![Vitest](https://img.shields.io/badge/Vitest-6E9F18?style=for-the-badge&logo=vitest&logoColor=white)
![Go Test](https://img.shields.io/badge/Go%20Test-00ADD8?style=for-the-badge&logo=go&logoColor=white)

### AI Integration
![Claude](https://img.shields.io/badge/Claude%20MCP-7C3AED?style=for-the-badge&logo=anthropic&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI%20Functions-412991?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyByb2xlPSJpbWciIHZpZXdCb3g9IjAgMCAyNCAyNCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48dGl0bGU+T3BlbkFJPC90aXRsZT48cGF0aCBkPSJNMjIuMjgxOSA5LjgyMTFhNS45ODQ3IDUuOTg0NyAwIDAgMC0uNTE1Ny00LjkxMDggNi4wNDYyIDYuMDQ2MiAwIDAgMC02LjUwOTgtMi45QTYuMDY1MSA2LjA2NTEgMCAwIDAgNC45ODA3IDQuMTgxOGE1Ljk4NDcgNS45ODQ3IDAgMCAwLTMuOTk3NyAyLjkgNi4wNDYyIDYuMDQ2MiAwIDAgMCAuNzQyNyA3LjA5NjYgNS45OCA1Ljk4IDAgMCAwIC41MTEgNC45MTA3IDYuMDUxIDYuMDUxIDAgMCAwIDYuNTE0NiAyLjkwMDFBNS45ODQ3IDUuOTg0NyAwIDAgMCAxMy4yNTk5IDI0YTYuMDU1NyA2LjA1NTcgMCAwIDAgNS43NzE4LTQuMjA1OCA1Ljk4OTQgNS45ODk0IDAgMCAwIDMuOTk3Ny0yLjkwMDEgNi4wNTU3IDYuMDU1NyAwIDAgMC0uNzQ3NS03LjA3Mjl6bS05LjAyMiAxMi42MDgxYTQuNDc1NSA0LjQ3NTUgMCAwIDEtMi44NzY0LTEuMDQwOGwuMTQxOS0uMDgwNCA0Ljc3ODMtMi43NTgyYS43OTQ4Ljc5NDggMCAwIDAgLjM5MjctLjY4MTN2LTYuNzM2OWwyLjAyIDEuMTY4NmEuMDcxLjA3MSAwIDAgMSAuMDM4LjA1MnY1LjU4MjZhNC41MDQgNC41MDQgMCAwIDEtNC40OTQ1IDQuNDk0NHptLTkuNjYwNy00LjEyNTRhNC40NzA4IDQuNDcwOCAwIDAgMS0uNTM0Ni0zLjAxMzdsLjE0Mi4wODUyIDQuNzgzIDIuNzU4MmEuNzcxMi43NzEyIDAgMCAwIC43ODA2IDBsNS44NDI4LTMuMzY4NXYyLjMzMjRhLjA4MDQuMDgwNCAwIDAgMS0uMDMzMi4wNjE1TDkuNzQgMTkuOTUwMmE0LjQ5OTIgNC40OTkyIDAgMCAxLTYuMTQwOC0xLjY0NjR6TTIuMzQwOCA3Ljg5NTZhNC40ODUgNC40ODUgMCAwIDEgMi4zNjU1LTEuOTcyOFYxMS42YS43NjY0Ljc2NjQgMCAwIDAgLjM4NzkuNjc2NWw1LjgxNDQgMy4zNTQzLTIuMDIwMSAxLjE2ODVhLjA3NTcuMDc1NyAwIDAgMS0uMDcxIDBsLTQuODMwMy0yLjc4NjVBNC41MDQgNC41MDQgMCAwIDEgMi4zNDA4IDcuODcyem0xNi41OTYzIDMuODU1OEwxMy4xMDM4IDguMzY0IDE1LjExOTIgNy4yYS4wNzU3LjA3NTcgMCAwIDEgLjA3MSAwbDQuODMwMyAyLjc5MTNhNC40OTQ0IDQuNDk0NCAwIDAgMS0uNjc2NSA4LjEwNDJ2LTUuNjc3MmEuNzkuNzkgMCAwIDAtLjQwNy0uNjY3em0yLjAxMDctMy4wMjMxbC0uMTQyLS4wODUyLTQuNzczNS0yLjc4MThhLjc3NTkuNzc1OSAwIDAgMC0uNzg1NCAwTDkuNDA5IDkuMjI5N1Y2Ljg5NzRhLjA2NjIuMDY2MiAwIDAgMSAuMDI4NC0uMDYxNWw0LjgzMDMtMi43ODY2YTQuNDk5MiA0LjQ5OTIgMCAwIDEgNi42ODAyIDQuNjZ6TTguMzA2NSAxMi44NjNsLTIuMDItMS4xNjM4YS4wODA0LjA4MDQgMCAwIDEtLjAzOC0uMDU2N1Y2LjA3NDJhNC40OTkyIDQuNDk5MiAwIDAgMSA3LjM3NTctMy40NTM3bC0uMTQyLjA4MDVMOC43MDQgNS40NTlhLjc5NDguNzk0OCAwIDAgMC0uMzkyNy42ODEzem0xLjA5NzYtMi4zNjU0bDIuNjAyLTEuNDk5OCAyLjYwNjkgMS40OTk4djIuOTk5NGwtMi41OTc0IDEuNDk5Ny0yLjYwNjctMS40OTk3WiIvPjwvc3ZnPg==&logoColor=white)
![GitHub Copilot](https://img.shields.io/badge/GitHub%20Copilot-000000?style=for-the-badge&logo=githubcopilot&logoColor=white)

</div>

---

## 🤖 MCP Quick Start (5 Minutes)

### The Easiest Way: Use Claude Desktop or ChatGPT

DevOps-OS exposes all its generators as an **MCP server**, so you can ask Claude or ChatGPT to generate your configs using natural language.

#### Install & Connect to Claude Desktop

```bash
git clone https://github.com/cloudengine-labs/devops_os.git
cd devops_os

python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux

pip install -r mcp_server/requirements.txt
```

Get your path: `pwd`, then edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "devops-os": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/your/path/to/devops_os"
    }
  }
}
```

Restart Claude. You should see a wrench icon 🔧 at the bottom right.

#### Ask Claude to Generate

> *"Generate a complete GitHub Actions CI/CD workflow for a Python Flask API with Docker build, pytest tests, and deployment to Kubernetes."*

Claude will use DevOps-OS to generate the workflow and explain each stage.

#### Learn More

- **[🚀 MCP Getting Started](GETTING-STARTED-MCP.md)** — 5-minute quick start
- **[🔧 MCP Setup & Configuration](hugo-docs/content/docs/ai-integration/mcp-setup.md)** — ChatGPT, HTTP endpoints, authentication, Docker
- **[📖 Full MCP Docs](hugo-docs/content/docs/ai-integration/)** — Complete reference

---

---

## 🗂️ Quick Reference

**DevOps-OS MCP** is the MCP server implementation. Access features through AI assistants like Claude, ChatGPT, Cursor, VS Code Copilot, Windsurf, or Zed.

For the **original CLI tool**, see [cloudengine-labs/devops_os](https://github.com/cloudengine-labs/devops_os).

### Setup

```bash
# Clone and install MCP server dependencies
git clone https://github.com/cloudengine-labs/devops_os.git && cd devops_os
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r mcp_server/requirements.txt

# For Claude Desktop
# Edit ~/Library/Application Support/Claude/claude_desktop_config.json (macOS)
# Or %APPDATA%\Claude\claude_desktop_config.json (Windows)
# Add the MCP server configuration from GETTING-STARTED-MCP.md
```

### Example Prompts

Ask your AI assistant:

```
# Generate GitHub Actions workflow
"Generate a complete GitHub Actions CI/CD workflow for a Python Flask API with Docker build, pytest, and Kubernetes deployment via ArgoCD"

# Generate Jenkins pipeline
"Create a Jenkins Declarative Pipeline for a Java Spring Boot microservice with Maven build and ArgoCD deployment"

# Generate Kubernetes configs
"Generate Kubernetes manifests for a Node.js service with 3 replicas on port 3000 using image ghcr.io/myorg/my-service:v1.0"

# Generate SRE configs
"Generate Prometheus alert rules and Grafana dashboard for a payment-processing microservice with 99.9% SLO"

# Generate dev container
"Scaffold a devcontainer for a Go + Python project with Terraform, kubectl, and k9s"

# Generate hardening policies
"Generate Kyverno policies for a production Kubernetes cluster based on CIS benchmarks"
```

**[Full MCP Guide →](GETTING-STARTED-MCP.md)** — Setup for Claude Desktop, Cursor, VS Code, Windsurf, Zed, and troubleshooting.

---

## 📁 Repository Structure

```text
devops_os/
├── .devcontainer/      # Dev container configuration
├── .legacy/            # Archived implementations
├── .github/workflows/  # CI and test workflows
├── devops_os/core/     # Core scaffold modules (GitHub Actions, Jenkins, GitLab, ArgoCD, SRE, etc.)
├── kubernetes/         # Kubernetes manifest generator
├── mcp_server/         # MCP server for AI assistant integration (Claude, ChatGPT)
├── skills/             # Claude & OpenAI tool/function definitions
├── docs/               # Detailed guides
├── tests/              # Comprehensive test suite
├── go-project/         # Example Go application
└── scripts/            # Helper scripts
```

---

## 🧪 Testing

All tests run without real infrastructure — everything uses in-memory mock data.

```bash
pip install -r mcp_server/requirements.txt pytest pytest-html
python -m pytest mcp_server/test_server.py tests/ -v
```

**Latest results:** ✅ All MCP server tests passing

| Test Suite | Description |
|------------|-------------|
| [MCP Server Tests](mcp_server/test_server.py) | MCP tool function tests |
| [Comprehensive Tests](tests/test_comprehensive.py) | Integration tests for all scaffold modules |
| [MCP Protocol Tests](tests/test_mcp_protocol.py) | MCP protocol compliance tests |
| [Hardening Tests](tests/test_hardening_scaffold.py) | Infrastructure hardening policy generation tests |
| [Sanity Workflow](.github/workflows/sanity.yml) | GitHub Actions workflow running tests on every push |

---

## 🛠️ Dev Container

The pre-configured dev container gives you a consistent multi-language environment with all CI/CD tools included.

<details>
<summary><strong>Supported languages & tools</strong></summary>

| Category | Tools |
|----------|-------|
| **Languages** | Python 3.12 · Java 21 · Node.js 22 · Go 1.25 · Ruby · PHP · Rust · C# · Kotlin · C/C++ |
| **Build tools** | pip · Maven · Gradle · npm · yarn · Composer · dotnet · Kotlin compiler · clang |
| **Linting/Testing** | pytest · black · flake8 · mypy · Jest · ESLint · golangci-lint |
| **Containers** | Docker CLI · Docker Compose |
| **IaC** | Terraform |
| **Kubernetes** | kubectl · Helm · Kustomize · K9s · KinD · Minikube |
| **GitOps** | ArgoCD CLI · Flux CD |
| **Secrets** | Kubeseal (Sealed Secrets) |
| **Observability** | Prometheus · Grafana |

</details>

Generate a dev container configuration by asking Claude:

```
"Generate a dev container (devcontainer.json) for a Python + Go project with Terraform, kubectl, and k9s for Kubernetes development."
```

The MCP server will generate all necessary dev container configuration files for your project.

---

## 📚 Documentation

### 🤖 AI & MCP Integration (Recommended)

| Guide | Description |
|-------|-------------|
| [🚀 MCP Quick Start](GETTING-STARTED-MCP.md) | Connect to Claude Desktop in 5 minutes — **recommended starting point** |
| [🔧 MCP Setup & Configuration](hugo-docs/content/docs/ai-integration/mcp-setup.md) | Install, configure, deploy with Docker, ChatGPT setup, troubleshooting |
| [🧠 AI Skills with OpenAI/Anthropic](skills/README.md) | Integrate with API function calling (alternative to MCP) |

### 🏗️ Generators & Configuration

| Guide | Description |
|-------|-------------|
| [🔄 Process-First Philosophy](docs/PROCESS-FIRST.md) | What Process-First means, how it maps to DevOps-OS, and AI learning tips |
| [⚙️ GitHub Actions Generator](docs/GITHUB-ACTIONS-README.md) | Generate and customize GitHub Actions workflows |
| [🦊 GitLab CI Generator](docs/GITLAB-CI-README.md) | Generate and customize GitLab CI pipelines |
| [🔧 Jenkins Pipeline Generator](docs/JENKINS-PIPELINE-README.md) | Generate and customize Jenkins pipelines |
| [🔄 ArgoCD / Flux GitOps](docs/ARGOCD-README.md) | Generate ArgoCD Applications and Flux Kustomizations |
| [📊 SRE Configuration](docs/SRE-CONFIGURATION-README.md) | Prometheus rules, Grafana dashboards, SLO manifests |
| [🔐 Infrastructure Hardening](docs/devops-os-hardening-sprint.md) | Standards, output layout, and examples for the hardening scaffold |
| [🧪 Unit Test Scaffold](docs/CLI-COMMANDS-REFERENCE.md#devopsos-scaffold-unittest--unit-test-scaffold-generator) | Generate pytest, Jest, Vitest, Mocha, or Go test configs |
| [☸️ Kubernetes Deployments](docs/KUBERNETES-DEPLOYMENT-README.md) | Generate and manage Kubernetes deployment configs |

### 🛠️ Development & Deployment

| Guide | Description |
|-------|-------------|
| [🤖 MCP Server Architecture](mcp_server/README.md) | Technical details about the MCP implementation |

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
