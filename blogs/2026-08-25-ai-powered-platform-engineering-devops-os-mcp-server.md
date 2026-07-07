---
title: "AI-Powered Platform Engineering: Using DevOps-OS as an MCP Server"
slug: "ai-powered-platform-engineering-devops-os-mcp-server"
description: "Connect DevOps-OS to Claude, ChatGPT, or any MCP-compatible AI assistant and generate production-ready DevOps configs directly from natural language prompts."
topic: "ai-devops"
tags: ["MCPServer", "AIDevOps", "PlatformEngineering", "Claude", "DevOpsOS", "OpenAI"]
publishedAt: "2026-08-25"
featured: false
---

# AI-Powered Platform Engineering: Using DevOps-OS as an MCP Server

What if you could ask your AI assistant: *"Generate a Jenkins pipeline for a Java Spring Boot app with Docker build, push to GHCR, and Kustomize deployment"* — and receive a production-ready `Jenkinsfile` back in seconds?

With DevOps-OS's built-in MCP server, you can.

## What is MCP?

MCP (Model Context Protocol) is an open standard that lets AI assistants call external tools with structured inputs and receive structured outputs. Claude, GitHub Copilot, Cursor, Windsurf, and Zed all support MCP natively.

DevOps-OS exposes every scaffold generator as an MCP tool — so your AI assistant becomes a DevOps platform engineer.

## Start the MCP server

```bash
pip install -r mcp_server/requirements.txt
python -m mcp_server.server
```

The server runs as a stdio MCP process — the standard integration mode for Claude Desktop, Claude Code, and most MCP clients.

## Connect to Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

Restart Claude Desktop. DevOps-OS tools now appear as native Claude skills.

## Available tools

| Tool | What it generates |
|------|-------------------|
| `generate_github_actions_workflow` | GitHub Actions workflow YAML |
| `generate_jenkins_pipeline` | Declarative Jenkinsfile |
| `generate_k8s_config` | Kubernetes Deployment + Service manifests |
| `scaffold_devcontainer` | `devcontainer.json` + `devcontainer.env.json` |
| `generate_gitlab_ci_pipeline` | GitLab CI/CD pipeline YAML |
| `generate_argocd_config` | ArgoCD Application and AppProject manifests |
| `generate_sre_configs` | Prometheus rules, Grafana dashboard, SLO manifest |

## Example prompts

```
Generate a complete GitHub Actions CI/CD workflow for a Python + Node.js
project with Kubernetes deployment via Kustomize.

Create a Jenkins pipeline for a Python microservice with Docker build,
push to GHCR, and deploy to a staging cluster using ArgoCD.

Scaffold a devcontainer for a Go + Python project with Terraform, kubectl,
k9s, and Flux CD.

Generate Kubernetes manifests for an API service using image
ghcr.io/myorg/api:v1.2.3 with 3 replicas on port 8080.

Generate SRE configs for payment-service with a 99.95% SLO and PagerDuty routing.
```

## Use DevOps-OS from the Anthropic API

```python
import json
import anthropic

with open("skills/claude_tools.json") as fh:
    tools = json.load(fh)

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=4096,
    tools=tools,
    messages=[{
        "role": "user",
        "content": (
            "Generate a complete GitHub Actions CI/CD workflow for a "
            "Python + Node.js project with Kubernetes deployment via Kustomize."
        ),
    }],
)
```

## Use DevOps-OS from the OpenAI API

```python
import json
import openai

with open("skills/openai_functions.json") as fh:
    functions = json.load(fh)

client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    tools=functions,
    messages=[{
        "role": "user",
        "content": "Generate a Jenkins pipeline for a Java Spring Boot app."
    }],
)
```

## Custom GPT / GPT Actions

Use `skills/openai_functions.json` as the OpenAPI schema for a Custom GPT Action:

1. Open ChatGPT → Create a GPT → Configure → Actions → Create new action
2. Paste the contents of `skills/openai_functions.json`
3. Set the server URL to your deployed MCP server endpoint
4. Save and test

Platform teams can expose a Custom GPT to their developers as a self-service DevOps assistant — no CLI knowledge required.

## The architecture

```
AI Assistant (Claude / ChatGPT)
        │  MCP / function-call request
        ▼
DevOps-OS MCP Server
        │  calls Python scaffold functions
        ▼
  Same generators used by the CLI
        │
        ▼
  Generated files returned to AI assistant
```

The MCP server is a thin protocol adapter — it calls the exact same Python functions as the CLI. Every improvement to the generators benefits both the CLI and the AI integration simultaneously.
