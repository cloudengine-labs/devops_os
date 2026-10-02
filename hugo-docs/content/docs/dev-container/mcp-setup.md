---
title: "MCP Dev Container Setup"
weight: 61
---

# MCP Dev Container Module

The DevOps-OS MCP Dev Container module enables AI assistants (Claude, ChatGPT, Cursor, etc.) to generate production-ready development container configurations through natural language prompts.

---

## Overview

The MCP Dev Container module provides an intelligent API for creating customized dev container configurations that include:

- **Multi-language support**: Python, Java, Go, Node.js, Rust, Ruby, C/C++, PHP, C#, Kotlin, and more
- **CI/CD tool integration**: Docker, Podman, GitHub Actions, Jenkins, GitLab CI, Terraform, Kubectl, Helm
- **Kubernetes utilities**: K9s, Kustomize, ArgoCD, Flux, KinD, Minikube, OpenShift CLI
- **Build systems**: Maven, Gradle, Make, CMake, Ant
- **Code analysis tools**: SonarQube, ESLint, Pylint, Checkstyle, PMD
- **DevOps platforms**: Prometheus, Grafana, ELK Stack, Nexus Repository
- **Automatic VS Code extension recommendations** based on selected tools
- **Port forwarding setup** for services like Grafana, Prometheus, Jenkins, etc.

---

## Using with AI Assistants

### Claude Desktop

Configure your Claude Desktop to use the DevOps-OS MCP server:

```json
{
  "mcpServers": {
    "devops-os": {
      "command": "python",
      "args": ["-m", "mcp_server.server"]
    }
  }
}
```

Then ask Claude:

```
Generate a dev container for a full-stack application with Python 3.12,
Node.js 22, Docker, Kubernetes tools (k9s, kustomize, ArgoCD), and Prometheus
for monitoring.
```

Claude will generate the complete devcontainer.json and devcontainer.env.json configuration.

### Cursor IDE

Add to your Cursor configuration to use DevOps-OS as an AI skill:

```json
{
  "customInstructions": {
    "devopsAutomation": {
      "tools": ["scaffold_devcontainer"],
      "description": "Generate DevOps automation artifacts including dev containers"
    }
  }
}
```

### ChatGPT with MCP

Use the DevOps-OS MCP server with ChatGPT by configuring a custom tool that calls the `scaffold_devcontainer` endpoint.

---

## API Reference

### scaffold_devcontainer

Generate a complete dev container configuration.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `languages` | string | `python` | Comma-separated languages (python, java, javascript, node, typescript, go, rust, ruby, csharp, php, kotlin, c, cpp) |
| `cicd_tools` | string | `docker,github_actions` | Comma-separated CI/CD tools (docker, podman, terraform, kubectl, helm, github_actions, jenkins, gitlab) |
| `kubernetes_tools` | string | `k9s,kustomize` | Comma-separated K8s tools (k9s, kustomize, argocd_cli, flux, lens, kubeseal, kind, minikube, openshift_cli) |
| `build_tools` | string | _(empty)_ | Comma-separated build tools (maven, gradle, make, cmake, ant) |
| `code_analysis_tools` | string | _(empty)_ | Comma-separated analysis tools (sonarqube, eslint, pylint, checkstyle, pmd) |
| `devops_tools` | string | _(empty)_ | Comma-separated DevOps tools (prometheus, grafana, elk, nexus) |
| `python_version` | string | `3.12` | Python version |
| `java_version` | string | `21` | Java JDK version |
| `node_version` | string | `22` | Node.js version |
| `go_version` | string | `1.25.0` | Go version |
| `ruby_version` | string | `3.3` | Ruby version |
| `rust_version` | string | `latest` | Rust version |

**Returns:**

A JSON object containing:

```json
{
  "devcontainer_json": { /* devcontainer.json config */ },
  "devcontainer_env_json": { /* devcontainer.env.json config */ },
  "suggestions": "AI-generated customization suggestions (optional)"
}
```

---

## Usage Examples

### Example 1: Full-Stack Web Application

**Prompt:** "I'm building a full-stack web application with Python backend and React frontend. I also need Kubernetes deployment capabilities."

**Generated config will include:**
- Python 3.12
- Node.js 22
- Docker, Podman
- Kubectl, Helm, K9s, Kustomize
- Docker and Kubernetes VS Code extensions
- Port forwarding for development servers

### Example 2: Microservices Platform

**Prompt:** "Create a dev container for microservices development with Go, Java, and TypeScript, with GitOps capabilities using ArgoCD and Flux."

**Generated config will include:**
- Go 1.25.0
- Java 21
- Node.js 22 (for TypeScript)
- Docker, Terraform
- ArgoCD CLI, Flux
- All required VS Code extensions
- Port forwarding for ArgoCD and service meshes

### Example 3: DevOps & SRE Platform

**Prompt:** "I need a development environment for SRE work with Python for automation, Kubernetes management tools, and observability stack (Prometheus, Grafana)."

**Generated config will include:**
- Python 3.12
- Docker, Kubectl, Helm
- K8s tools (K9s, KinD, Minikube)
- Prometheus 3.5.1
- Grafana 12.4.2
- SonarQube for code analysis
- Port forwarding: 9090 (Prometheus), 3000 (Grafana)

---

## Features

### Intelligent Extension Recommendations

The module automatically recommends VS Code extensions based on selected tools:

- **Python** → Python, Pylance, Black Formatter
- **Java** → Java Pack, Maven, Gradle
- **Go** → Go, Go Nightly
- **Docker** → Docker extension
- **Kubernetes** → Kubernetes Tools, Mindaro (Bridge to K8s)
- **GitOps** → GitOps Toolkit (for Flux), ArgoCD Extension
- **CI/CD** → GitHub Actions, GitLab Workflow, Jenkinsfile Support
- **General** → GitHub Copilot, Live Share, Spell Checker, GitLens

### Automatic Port Forwarding

The module configures port forwarding for services that typically run in containers:

- **Prometheus**: 9090
- **Grafana**: 3000
- **Jenkins**: 8080
- **Nexus**: 8081
- **ELK Stack**: 9200, 9300, 5601

### Version Management

Each tool has sensible defaults, but all versions are configurable:

- Python: 3.12 (supports 3.7 - 3.12+)
- Java: 21 (supports 8 - 21)
- Node.js: 22 (supports 14 - 22)
- Go: 1.25.0 (supports 1.19+)
- And many more...

---

## Integration with CLI

The MCP module shares the same underlying configuration logic as the CLI tool:

```bash
# CLI-based generation
python -m devops_os.core.scaffold_devcontainer \
  --languages python,go \
  --cicd-tools docker,kubernetes \
  --kubernetes-tools k9s,argocd_cli,flux

# MCP-based generation (via AI assistant)
# Ask Claude: "Generate a dev container for Python and Go with Kubernetes tools..."
```

Both methods produce identical results, allowing you to choose the interface that works best for your workflow.

---

## Next Steps

- Refer to [Language Guides](./language-guides.md) for language-specific recommendations
- Check the [Dev Container Setup](./index.md) guide for CLI usage
- See [Getting Started with MCP](../getting-started/mcp-quickstart.md) for integration steps
