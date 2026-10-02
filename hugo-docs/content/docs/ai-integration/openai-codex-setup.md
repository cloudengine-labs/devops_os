---
title: "OpenAI Codex Integration"
weight: 25
---

# OpenAI Codex Integration Guide

This guide covers setting up and using DevOps-OS with **OpenAI Codex** for code generation and pipeline automation.

---

## What is OpenAI Codex?

**OpenAI Codex** is a powerful AI model trained on publicly available code from the internet. It understands dozens of programming languages and can generate, edit, and explain code in context.

### Why Use Codex with DevOps-OS?

| Feature | Benefit |
|---------|---------|
| **Natural language to code** | Describe your pipeline in plain English, get YAML/Jenkinsfile back |
| **Code completion** | Start a pipeline definition, let Codex finish it |
| **Multi-language support** | Generate pipelines for GitHub Actions, Jenkins, GitLab CI, etc. |
| **Context awareness** | Understands your existing infrastructure patterns |
| **Integration with your IDE** | Use Codex plugins in VS Code, JetBrains, or other editors |

---

## Architecture Overview

```
┌──────────────────────────────────────┐
│    Developer (IDE or Chat)           │
│  "Generate a Python CI/CD pipeline"  │
└────────────────┬─────────────────────┘
                 │
                 ▼
    ┌────────────────────────────┐
    │  OpenAI Codex API          │
    │  (davinci-codex model)     │
    └────────────────┬───────────┘
                     │
                     ▼
    ┌────────────────────────────┐
    │  DevOps-OS Skills          │
    │  (openai_functions.json)   │
    └────────────────┬───────────┘
                     │
                     ▼
    ┌────────────────────────────┐
    │  Generated Artifacts       │
    │  - GitHub Actions YAML     │
    │  - Jenkins Declarative     │
    │  - Kubernetes manifests    │
    │  - ArgoCD configs          │
    └────────────────────────────┘
```

---

## Prerequisites

- **OpenAI API Key** with access to Codex models
- **Python 3.10+**
- **pip** (Python package manager)
- **DevOps-OS repository** cloned locally

### Get Your OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up or log in with your OpenAI account
3. Create a new API key
4. Copy and save it securely (you won't be able to view it again)

---

## Installation

### Step 1: Clone and Install DevOps-OS

```bash
git clone https://github.com/cloudengine-labs/devops_os.git
cd devops_os

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r mcp_server/requirements.txt
pip install openai  # For direct API usage
```

### Step 2: Set Your OpenAI API Key

```bash
# macOS/Linux
export OPENAI_API_KEY="sk-your-api-key-here"

# Windows (PowerShell)
$env:OPENAI_API_KEY = "sk-your-api-key-here"

# Or add to your shell profile for persistence:
# ~/.bashrc, ~/.zshrc, or ~/.bash_profile
echo 'export OPENAI_API_KEY="sk-your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

---

## Method 1: Direct API Integration

Use OpenAI Codex directly with DevOps-OS skill definitions.

### Step 1: Load DevOps-OS Skills

```python
import json
import openai

# Load skill definitions
with open("skills/openai_functions.json") as fh:
    functions = json.load(fh)

# Initialize OpenAI client
client = openai.OpenAI()
```

### Step 2: Make a Request to Codex

```python
# Example: Generate a GitHub Actions workflow
response = client.chat.completions.create(
    model="gpt-4o",  # or "gpt-3.5-turbo" for faster responses
    tools=functions,
    messages=[{
        "role": "user",
        "content": (
            "Generate a GitHub Actions CI/CD workflow for a Python web application "
            "with pytest testing, Docker build, and Kubernetes deployment."
        )
    }],
)

# Process the response
for choice in response.choices:
    if choice.message.tool_calls:
        for tool_call in choice.message.tool_calls:
            print(f"Tool: {tool_call.function.name}")
            print(f"Arguments: {tool_call.function.arguments}")
```

### Step 3: Call the DevOps-OS Generator

```python
import subprocess
import json

# Extract tool call details
tool_name = tool_call.function.name
args = json.loads(tool_call.function.arguments)

# Map tool names to CLI commands
TOOL_COMMANDS = {
    "generate_github_actions_workflow": "devopsos scaffold gha",
    "generate_jenkins_pipeline": "devopsos scaffold jenkins",
    "generate_k8s_config": "devopsos scaffold k8s",
    "generate_argocd_config": "devopsos scaffold argocd",
    "generate_sre_configs": "devopsos scaffold sre",
}

# Execute the generator
cmd = TOOL_COMMANDS.get(tool_name, "").split()
cmd.extend([f"--{k}={v}" for k, v in args.items()])

result = subprocess.run(cmd, capture_output=True, text=True)
print("Generated output:")
print(result.stdout)
```

### Complete Example Script

```python
#!/usr/bin/env python3
import json
import openai
import subprocess
import sys

def generate_pipeline(description: str):
    """Generate a DevOps pipeline using Codex"""
    
    # Load skill definitions
    with open("skills/openai_functions.json") as fh:
        functions = json.load(fh)
    
    # Initialize OpenAI client
    client = openai.OpenAI()
    
    # Call Codex
    response = client.chat.completions.create(
        model="gpt-4o",
        tools=functions,
        messages=[{
            "role": "user",
            "content": description
        }],
    )
    
    # Process tool calls
    for choice in response.choices:
        if choice.message.tool_calls:
            for tool_call in choice.message.tool_calls:
                tool_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                print(f"\n✓ Codex selected tool: {tool_name}")
                print(f"✓ Arguments: {json.dumps(args, indent=2)}")
                
                # Execute generator (pseudo-code)
                # result = execute_devopsos_generator(tool_name, args)
                # print(result.stdout)

if __name__ == "__main__":
    prompt = (
        "Generate a GitHub Actions workflow for a Node.js app with "
        "Jest testing, Docker push, and ArgoCD deployment."
    )
    generate_pipeline(prompt)
```

---

## Method 2: Using in VS Code with Copilot

If you have **GitHub Copilot** (which uses Codex technology), you can use DevOps-OS suggestions directly in VS Code.

### Step 1: Install GitHub Copilot

1. Install the [GitHub Copilot extension](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) in VS Code
2. Sign in with your GitHub account (requires a Copilot subscription)

### Step 2: Create a Skills Reference File

Create a file at the root of your DevOps-OS project:

```bash
cat > COPILOT_INSTRUCTIONS.md << 'EOF'
# DevOps-OS Copilot Instructions

When generating CI/CD pipelines, consider these tools:

- generate_github_actions_workflow: For GitHub Actions workflows
- generate_jenkins_pipeline: For Jenkins Declarative Pipelines
- generate_k8s_config: For Kubernetes manifests
- generate_argocd_config: For Argo CD applications
- generate_sre_configs: For Prometheus, Grafana, and SLO configs

Example input:
name: my-app
languages: python,javascript
workflow_type: complete

See skills/openai_functions.json for full schema.
EOF
```

### Step 3: Use Copilot in Your Files

In VS Code:

1. Create a new file (e.g., `my-workflow.yml`)
2. Type a comment describing what you want:
   ```yaml
   # Generate a GitHub Actions workflow for a Python+Node.js app with Docker and K8s deployment
   ```
3. Press `Ctrl+Enter` (or `Cmd+Enter` on macOS) to trigger Copilot suggestions
4. Accept, reject, or refine the suggestions

---

## Method 3: ChatGPT with Function Calling

Use ChatGPT Plus with DevOps-OS functions (requires ChatGPT Plus subscription):

1. Go to [ChatGPT](https://chatgpt.com)
2. Create a Custom GPT with the schema from `skills/openai_functions.json`
3. Ask: *"Generate a Kubernetes deployment for my Python API with 3 replicas"*

See the [ChatGPT Integration Guide]({{< relref "/docs/ai-integration/chatgpt-setup" >}}) for detailed steps.

---

## Model Selection

Different models have different capabilities and pricing:

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| `gpt-4o` | Medium | Higher | Complex pipelines, context-aware generation |
| `gpt-4-turbo` | Medium | Medium | Balanced speed and quality |
| `gpt-3.5-turbo` | Fast | Lower | Quick prototypes, simple pipelines |
| `text-davinci-003` | Fast | Lower | Legacy Codex workloads |

**Recommendation:** Start with `gpt-3.5-turbo` for testing, then upgrade to `gpt-4o` for production use.

---

## Example Prompts

```
Generate a GitHub Actions workflow for a Python microservice with:
- Pytest unit tests
- Docker build and push to ECR
- Deployment to EKS via Helm

Generate a Jenkins pipeline for a Java Spring Boot app with:
- Maven build
- SonarQube analysis
- Docker image creation
- Deployment to Kubernetes

Generate Kubernetes manifests for an API service with:
- Name: api-gateway
- Image: ghcr.io/myorg/api:v1.0.0
- 5 replicas
- Port 8080

Create a GitLab CI pipeline with:
- Python 3.10 test job
- Docker build stage
- ArgoCD deployment stage
- Slack notifications on failure

Generate SRE configs for my-api with:
- 99.95% availability SLO
- P99 latency < 200ms
- Error rate < 0.1%
- PagerDuty alerts
```

---

## Troubleshooting

### Error: "Invalid API key"

```
openai.error.AuthenticationError: Incorrect API key provided
```

**Solution:**
1. Verify your API key is correct at [OpenAI Platform](https://platform.openai.com/api-keys)
2. Check the environment variable is set:
   ```bash
   echo $OPENAI_API_KEY  # Should print your key
   ```
3. Restart your terminal or Python session after setting the key

### Error: "Model not found: gpt-4o"

```
openai.error.InvalidRequestError: The model `gpt-4o` does not exist
```

**Solution:**
- Use a model you have access to: `gpt-3.5-turbo`, `gpt-4-turbo`, or `text-davinci-003`
- Check your API key has access to the model
- Request model access at [OpenAI Platform](https://platform.openai.com/account/billing/limits)

### Error: "Rate limit exceeded"

```
openai.error.RateLimitError: Rate limit exceeded
```

**Solution:**
1. Add exponential backoff to your requests:
   ```python
   import time
   import random
   
   max_retries = 5
   for attempt in range(max_retries):
       try:
           response = client.chat.completions.create(...)
           break
       except openai.RateLimitError:
           if attempt < max_retries - 1:
               wait_time = 2 ** attempt + random.random()
               print(f"Rate limited. Waiting {wait_time:.1f}s...")
               time.sleep(wait_time)
           else:
               raise
   ```

2. Upgrade your OpenAI plan for higher rate limits

### Generated Pipeline is Invalid

**Symptoms:**
- Syntax errors in generated YAML
- Missing required fields
- Invalid container images

**Solutions:**

1. **Provide more context:**
   ```python
   "Generate a GitHub Actions workflow following our team standards: "
   "- Use Python 3.11 "
   "- Test with pytest "
   "- Build Docker image named ghcr.io/myorg/my-app "
   "- Deploy to EKS with Kustomize "
   "- Notify Slack on failure"
   ```

2. **Validate and refine:**
   ```python
   # Get initial response, validate it, then refine
   if not is_valid_yaml(generated_yaml):
       # Ask Codex to fix it
       messages.append({
           "role": "user",
           "content": f"Fix this YAML error: {error_message}"
       })
       response = client.chat.completions.create(...)
   ```

3. **Use examples:**
   Include example pipelines in your prompt to guide Codex

---

## Next Steps

- [ChatGPT Integration Guide]({{< relref "/docs/ai-integration/chatgpt-setup" >}}) — Use DevOps-OS with ChatGPT
- [MCP Setup & Configuration]({{< relref "/docs/ai-integration/mcp-setup" >}}) — Run DevOps-OS as an MCP server
- [CLI Reference]({{< relref "/docs/reference" >}}) — Full list of generators and options
- [OpenAI API Docs](https://platform.openai.com/docs/guides/gpt) — Official OpenAI documentation

---

## Support

- 🐛 **Bug reports:** [GitHub Issues](https://github.com/cloudengine-labs/devops_os/issues)
- 💬 **Questions:** [GitHub Discussions](https://github.com/cloudengine-labs/devops_os/discussions)
- 📖 **Documentation:** [Full Docs](https://devops-os.io/docs/)
- 🔗 **OpenAI Help:** [OpenAI Support](https://help.openai.com)
