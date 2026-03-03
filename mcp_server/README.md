# DevOps-OS MCP Server

The DevOps-OS MCP (Model Context Protocol) server exposes the DevOps-OS pipeline
automation tools to any MCP-compatible AI assistant — including **Claude** (via
Claude Desktop / Claude API) and **ChatGPT** (via custom GPT Actions).

## Available Tools

| Tool | Description |
|------|-------------|
| `generate_github_actions_workflow` | Generate a GitHub Actions CI/CD workflow YAML |
| `generate_jenkins_pipeline` | Generate a Jenkins Declarative Pipeline (Jenkinsfile) |
| `generate_k8s_config` | Generate Kubernetes Deployment + Service manifests |
| `scaffold_devcontainer` | Generate `devcontainer.json` and `devcontainer.env.json` |

## Installation

```bash
pip install -r mcp_server/requirements.txt
```

## Running the Server

```bash
# Run as a stdio MCP server (default — for Claude Desktop and most MCP clients)
python -m mcp_server.server

# Or directly
python mcp_server/server.py
```

## Connecting to Claude Desktop

Add the following to your `claude_desktop_config.json`
(`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

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

Restart Claude Desktop and ask it to:

> "Generate a complete GitHub Actions CI/CD workflow for a Python + Node.js project
>  with Kubernetes deployment using Kustomize."

## Example Prompts

```
Generate a GitHub Actions workflow for a Java Spring Boot app with kubectl deployment.

Create a Jenkins pipeline for a Python microservice with Docker build and push stages.

Scaffold a devcontainer for a Go + Python project with Terraform and kubectl.

Generate Kubernetes manifests for an app called 'api-service' using image
'ghcr.io/myorg/api-service:v1.2.3' with 3 replicas on port 8080.
```

## Using with OpenAI / Custom GPT

See [`../skills/README.md`](../skills/README.md) for instructions on adding the
DevOps-OS tools to a Custom GPT via OpenAI function calling or GPT Actions.

## Architecture

```
AI Assistant (Claude / ChatGPT)
        │  MCP / function-call request
        ▼
DevOps-OS MCP Server (mcp_server/server.py)
        │  calls Python functions
        ▼
DevOps-OS CLI scaffold modules
  ├─ cli/scaffold_gha.py       → GitHub Actions YAML
  ├─ cli/scaffold_jenkins.py   → Jenkinsfile
  └─ kubernetes/k8s-config-generator.py → K8s manifests
```
