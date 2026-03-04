# DevOps-OS AI Skills

DevOps-OS exposes its pipeline automation capabilities as **AI tool/function definitions**
that can be loaded into Claude (via the Anthropic API) or ChatGPT / Custom GPTs
(via OpenAI function calling or GPT Actions).

## Available Skills / Tools

| Tool | What it generates |
|------|-------------------|
| `generate_github_actions_workflow` | GitHub Actions workflow YAML (build / test / deploy / complete) |
| `generate_jenkins_pipeline` | Jenkins Declarative Pipeline (Jenkinsfile) |
| `generate_k8s_config` | Kubernetes Deployment + Service manifests |
| `scaffold_devcontainer` | `devcontainer.json` + `devcontainer.env.json` |
| `generate_gitlab_ci_pipeline` | GitLab CI/CD pipeline configuration (`.gitlab-ci.yml`) |
| `generate_argocd_config` | Argo CD application/project configuration manifests |
| `generate_sre_configs` | SRE / observability configs (e.g., alerting/monitoring rules) |

---

## Using with Claude (Anthropic API)

Load `claude_tools.json` as the `tools` parameter when calling the Claude API:

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
    messages=[
        {
            "role": "user",
            "content": (
                "Generate a complete GitHub Actions CI/CD workflow for a "
                "Python + Node.js project with Kubernetes deployment via Kustomize."
            ),
        }
    ],
)

# Handle tool_use blocks
for block in response.content:
    if block.type == "tool_use":
        print(f"Tool: {block.name}")
        print(f"Input: {json.dumps(block.input, indent=2)}")
        # Forward block.input to the MCP server or call the tool function directly
```

---

## Using with OpenAI (function calling)

Load `openai_functions.json` as the `tools` parameter:

```python
import json
from openai import OpenAI

with open("skills/openai_functions.json") as fh:
    tools = json.load(fh)

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    tools=tools,
    messages=[
        {
            "role": "user",
            "content": (
                "Create a Jenkins pipeline for a Java Spring Boot service "
                "that builds a Docker image and deploys to Kubernetes with ArgoCD."
            ),
        }
    ],
)

# Handle tool calls
for choice in response.choices:
    msg = choice.message
    if msg.tool_calls:
        for call in msg.tool_calls:
            print(f"Function: {call.function.name}")
            print(f"Arguments: {call.function.arguments}")
            # Forward to the MCP server or invoke the function directly
```

---

## Using with Custom GPTs (GPT Actions)

You can add DevOps-OS as a **GPT Action** by exposing the MCP server over HTTP
and providing an OpenAPI schema. See the [MCP Server README](../mcp_server/README.md)
for server setup instructions.

---

## End-to-End Example (Claude + MCP Server)

```python
import json
import anthropic
import subprocess

with open("skills/claude_tools.json") as fh:
    tools = json.load(fh)

client = anthropic.Anthropic()

# 1. Ask Claude to plan the DevOps pipeline
response = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=4096,
    tools=tools,
    messages=[
        {
            "role": "user",
            "content": (
                "I have a Python Flask API. Generate a complete GitHub Actions "
                "CI/CD workflow with Docker build and Kubernetes deployment using kubectl."
            ),
        }
    ],
)

# 2. Execute the tool call via the MCP server
for block in response.content:
    if block.type == "tool_use":
        result = subprocess.run(
            ["python", "-c",
             f"from mcp_server.server import {block.name}; "
             f"print({block.name}(**{block.input!r}))"],
            capture_output=True, text=True, check=True
        )
        print(result.stdout)
```
