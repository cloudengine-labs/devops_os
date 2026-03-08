---
title: "AI Integration"
weight: 70
---

# AI Integration — MCP Server & AI Skills

DevOps-OS exposes all its pipeline automation tools as an **MCP (Model Context Protocol) server** and as **AI skill definitions** for Claude and OpenAI.

---

## Available Tools

| Tool | What it generates |
|------|-------------------|
| `generate_github_actions_workflow` | GitHub Actions workflow YAML |
| `generate_jenkins_pipeline` | Jenkins Declarative Pipeline (Jenkinsfile) |
| `generate_k8s_config` | Kubernetes Deployment + Service manifests |
| `scaffold_devcontainer` | `devcontainer.json` + `devcontainer.env.json` |
| `generate_gitlab_ci_pipeline` | GitLab CI/CD pipeline (`.gitlab-ci.yml`) |
| `generate_argocd_config` | Argo CD Application and AppProject manifests |
| `generate_sre_configs` | SRE / observability configs (Prometheus, Grafana, SLO) |

---

## MCP Server

### Installation

```bash
pip install -r mcp_server/requirements.txt
```

### Running the server

```bash
# Run as a stdio MCP server (default — for Claude Desktop and most MCP clients)
python -m mcp_server.server

# Or directly
python mcp_server/server.py
```

### Connecting to Claude Desktop

Add to `claude_desktop_config.json`  
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

Restart Claude Desktop, then ask it:

> *"Generate a complete GitHub Actions CI/CD workflow for a Python + Node.js project with Kubernetes deployment using Kustomize."*

> *"Create a Jenkins pipeline for a Python microservice with Docker build and push stages."*

> *"Scaffold a devcontainer for a Go + Python project with Terraform and kubectl."*

---

## Architecture

```
AI Assistant (Claude / ChatGPT)
        │  MCP / function-call request
        ▼
DevOps-OS MCP Server  ←──────────┐
        │                        │
        │  calls Python functions │
        ▼                        │
  devopsos scaffold gha          │
  devopsos scaffold gitlab  (same generators
  devopsos scaffold jenkins  used by the CLI)
  devopsos scaffold argocd        │
  devopsos scaffold sre           │
        │                        │
        ▼                        │
  Generated files ───────────────┘
```

---

## Using with Claude (Anthropic API)

Load `skills/claude_tools.json` as the `tools` parameter:

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

for block in response.content:
    if block.type == "tool_use":
        print(f"Tool: {block.name}")
        print(f"Input: {json.dumps(block.input, indent=2)}")
```

---

## Using with OpenAI (function calling)

Load `skills/openai_functions.json` as the `tools` parameter:

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

for choice in response.choices:
    if choice.message.tool_calls:
        for tc in choice.message.tool_calls:
            print(f"Function: {tc.function.name}")
            print(f"Args: {tc.function.arguments}")
```

---

## Custom GPT / GPT Actions

Use `skills/openai_functions.json` as the OpenAPI schema for a Custom GPT Action:

1. Open **ChatGPT → Create a GPT → Configure → Actions → Create new action**
2. Paste the contents of `skills/openai_functions.json`
3. Set the server URL to your deployed MCP server endpoint
4. Save and test the GPT

---

## Example Prompts

```
Generate a GitHub Actions workflow for a Java Spring Boot app with kubectl deployment.

Create a Jenkins pipeline for a Python microservice with Docker build and push stages.

Scaffold a devcontainer for a Go + Python project with Terraform and kubectl.

Generate Kubernetes manifests for an app called 'api-service' using image
'ghcr.io/myorg/api-service:v1.2.3' with 3 replicas on port 8080.

Create a GitLab CI pipeline with Python testing and ArgoCD deployment.

Generate SRE configs for my-service with a 99.9% availability SLO and PagerDuty alerts.
```
