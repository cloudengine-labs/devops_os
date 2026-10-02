# DevOps-OS Skills Usage Guide

**Practical guide to using DevOps-OS skills with Claude, ChatGPT, and other AI assistants. Includes examples, best practices, and troubleshooting.**

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Claude Desktop / API Usage](#claude-desktop--api-usage)
3. [ChatGPT / OpenAI Usage](#chatgpt--openai-usage)
4. [Example Prompts by Use Case](#example-prompts-by-use-case)
5. [Skill Parameters Guide](#skill-parameters-guide)
6. [Output Handling](#output-handling)
7. [Troubleshooting](#troubleshooting)

---

## Quick Reference

### Available Skills

| Skill | What it generates | Best for |
|-------|-------------------|----------|
| **generate_github_actions_workflow** | GitHub Actions CI/CD YAML | Python, Node.js, Java, Go projects |
| **generate_jenkins_pipeline** | Jenkins Declarative Pipeline | Enterprise CI/CD systems |
| **generate_gitlab_ci_pipeline** | GitLab CI .gitlab-ci.yml | GitLab-hosted projects |
| **generate_k8s_config** | Kubernetes Deployment + Service | Microservices, container orchestration |
| **generate_argocd_config** | ArgoCD Application CRs | GitOps continuous delivery |
| **generate_sre_configs** | Prometheus + Grafana + SLO configs | Observability and alerting |
| **scaffold_devcontainer** | devcontainer.json + .env | Reproducible dev environments |
| **generate_unittest_config** | Unit test scaffolding | Test automation setup |

---

## Claude Desktop / API Usage

### Method 1: Claude Desktop (Recommended)

**Setup:**
```bash
# 1. Clone and install
git clone https://github.com/chefgs/devops_os_mcp.git
cd devops_os_mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r mcp_server/requirements.txt

# 2. Get the path
pwd  # Copy this

# 3. Edit Claude config
# macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
# Windows: %APPDATA%\Claude\claude_desktop_config.json

# Add to config:
{
  "mcpServers": {
    "devops-os": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/your/path/from/step-2"
    }
  }
}

# 4. Restart Claude Desktop
```

**Usage:**
```
User: "Generate a complete GitHub Actions workflow for a Python Flask API with:
- pytest for testing
- Docker build and push to Docker Hub
- Deployment to Kubernetes with kubectl
- Matrix builds for Python 3.9, 3.10, 3.11"

Claude: [Uses generate_github_actions_workflow skill]

Result: Complete workflow.yml with:
✓ Lint stage (black, flake8)
✓ Test stage (pytest matrix)
✓ Build stage (Docker)
✓ Deploy stage (kubectl)
✓ Notification on failure
```

### Method 2: Anthropic API (Programmatic)

**Python Example:**
```python
import json
import anthropic

# Load skill definitions
with open("skills/claude_tools.json") as f:
    tools = json.load(f)

# Initialize client
client = anthropic.Anthropic()

# Make request with skills enabled
response = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=4096,
    tools=tools,
    messages=[
        {
            "role": "user",
            "content": "Generate a GitHub Actions workflow for a Node.js Express API"
        }
    ]
)

# Process response
for block in response.content:
    if block.type == "tool_use":
        print(f"Skill: {block.name}")
        print(f"Parameters: {json.dumps(block.input, indent=2)}")
        # Invoke the skill via MCP server or directly
```

---

## ChatGPT / OpenAI Usage

### Method 1: Custom GPT (GUI)

**Setup:**
1. Go to [ChatGPT Custom GPT Builder](https://chatgpt.com/gpts/editor)
2. Copy schema from `skills/openai_functions.json`
3. Add DevOps-OS MCP server HTTP endpoint
4. Configure authentication (if deployed to production)

**Usage:**
```
User: "Create a Jenkins pipeline for a Java Maven service"

ChatGPT: [Uses generate_jenkins_pipeline skill]

Result: Jenkinsfile with Maven build stages
```

### Method 2: OpenAI API (Programmatic)

**Python Example:**
```python
import json
from openai import OpenAI

# Load skill definitions
with open("skills/openai_functions.json") as f:
    tools = json.load(f)

# Initialize client
client = OpenAI()

# Make request with skills enabled
response = client.chat.completions.create(
    model="gpt-4o",
    tools=tools,
    messages=[
        {
            "role": "user",
            "content": "Generate Kubernetes manifests for a microservice"
        }
    ]
)

# Process response
for choice in response.choices:
    if choice.message.tool_calls:
        for call in choice.message.tool_calls:
            print(f"Skill: {call.function.name}")
            print(f"Parameters: {call.function.arguments}")
```

---

## Example Prompts by Use Case

### GitHub Actions Workflows

**Example 1: Python + Docker + Kubernetes**
```
Generate a complete GitHub Actions CI/CD workflow for a Python Flask API:
- Application name: payment-service
- Use pytest for testing
- Build a Docker image and push to ghcr.io/myorg/payment-service
- Deploy to Kubernetes using kubectl
- Enable matrix builds for Python 3.9, 3.10, 3.11
```

**Result:**
```yaml
name: payment-service
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r requirements.txt
      - run: pytest tests/
  
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/myorg/payment-service:${{ github.sha }}
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: kubectl apply -f k8s/ --kubeconfig=${{ secrets.KUBECONFIG }}
```

**Example 2: Node.js + Multi-language Matrix**
```
Generate a GitHub Actions workflow for a Node.js service:
- Test with Jest
- Support Node 18 and 20
- Run on ubuntu-latest and macos-latest
- Build Docker image on Linux only
```

### Jenkins Pipelines

**Example 1: Java Spring Boot with Kubernetes**
```
Generate a Jenkins Declarative Pipeline for a Java Spring Boot microservice:
- Build with Maven
- Run SonarQube code analysis
- Build Docker image
- Deploy to Kubernetes with ArgoCD
```

**Result:**
```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                sh 'mvn sonar:sonar'
            }
        }
        
        stage('Docker Build') {
            steps {
                sh 'docker build -t myregistry/myapp:$BUILD_NUMBER .'
                sh 'docker push myregistry/myapp:$BUILD_NUMBER'
            }
        }
        
        stage('Deploy') {
            steps {
                sh 'kubectl set image deployment/myapp myapp=myregistry/myapp:$BUILD_NUMBER'
            }
        }
    }
}
```

### Kubernetes Configurations

**Example 1: Microservice Deployment**
```
Generate Kubernetes manifests for:
- App name: user-service
- Docker image: gcr.io/myproject/user-service:v1.0
- 3 replicas for high availability
- Port 8080 (API)
- Namespace: production
- Use kustomize for deployment
```

**Result:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: gcr.io/myproject/user-service:v1.0
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
---
apiVersion: v1
kind: Service
metadata:
  name: user-service
  namespace: production
spec:
  selector:
    app: user-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: ClusterIP
```

### SRE Observability

**Example 1: Prometheus + Grafana + SLOs**
```
Generate SRE configuration for a payment-processing microservice:
- Setup Prometheus alert rules for:
  - High latency (p99 > 500ms)
  - High error rate (> 1%)
  - Memory leaks (memory growing consistently)
- Create a Grafana dashboard with:
  - Request rate and latency graphs
  - Error rate breakdown by endpoint
  - SLO error budget tracking
- Define 99.9% SLO with OpenSLO format
```

### Development Containers

**Example 1: Multi-language DevContainer**
```
Scaffold a development container for a Python + Go + Kubernetes project:
- Python 3.12 with pip and virtualenv
- Go 1.22 with golangci-lint
- Kubernetes tools: kubectl, helm, kustomize, k9s
- Container: Docker CLI
- Git and git-lfs
- VS Code extensions: Python, Go, Kubernetes
```

---

## Skill Parameters Guide

### Common Parameters

#### `name` / `app_name`
- **Type:** String
- **Default:** "my-app"
- **Description:** Name of your application
- **Usage:** Used in resource names, labels, and configuration keys
- **Example:** "payment-service", "user-api", "order-processor"

#### `languages`
- **Type:** Comma-separated string
- **Options:** python, javascript, java, go, ruby, php, rust, c++
- **Default:** "python"
- **Description:** Programming languages used in your project
- **Example:** "python,javascript" (for polyglot project)

#### `kubernetes`
- **Type:** Boolean
- **Default:** false
- **Description:** Include Kubernetes deployment in pipeline
- **Usage:** Set to `true` for cloud-native projects

#### `k8s_method`
- **Type:** String (enum)
- **Options:** 
  - `kubectl` — Direct imperative deployment (simple, not recommended for production)
  - `kustomize` — Template overlays for multi-environment (recommended)
  - `argocd` — GitOps continuous delivery (advanced)
  - `flux` — Flux CD alternative to ArgoCD
- **Default:** "kubectl"
- **Usage:** Choose based on your GitOps maturity

#### `workflow_type` / `pipeline_type`
- **Type:** String (enum)
- **Options:**
  - `build` — Only build steps
  - `test` — Build + test steps
  - `deploy` — Build + test + deploy
  - `complete` — All stages (recommended)
  - `reusable` / `parameterized` — Parameterized for reuse
- **Default:** "complete"
- **Usage:** "complete" for most new projects

#### `branches`
- **Type:** Comma-separated string
- **Default:** "main"
- **Description:** Git branches that trigger the pipeline
- **Example:** "main,develop" (trigger on both branches)

#### `matrix`
- **Type:** Boolean
- **Default:** false
- **Description:** Enable matrix builds across multiple OS/language versions
- **Usage:** Set to `true` for testing on multiple Python versions, Node versions, etc.

### Skill-Specific Parameters

#### GitHub Actions

**`matrix`** (boolean)
- Enables testing across multiple:
  - Python versions: 3.8, 3.9, 3.10, 3.11, 3.12
  - Node versions: 16, 18, 20
  - Go versions: 1.19, 1.20, 1.21, 1.22
  - Java versions: 11, 17, 21

#### Jenkins

**`parameters`** (boolean)
- Adds Jenkins Parameters for:
  - Environment selection (dev, staging, prod)
  - Feature flags for deployment
  - Build options (skip tests, force deploy, etc.)

#### ArgoCD

**`enable_canary`** (boolean)
- Adds Argo Rollouts Canary deployment strategy
- Enables gradual rollout with automated rollback

---

## Output Handling

### Output Format

Each skill returns:

```python
{
    "generated_config": "---\napiVersion: v1\n...",  # The actual YAML/JSON
    "format": "yaml",  # Output format type
    "type": "kubernetes_deployment",  # Configuration type
    "prompt_suggestions": [  # Recommendations to improve next request
        {
            "suggestion_text": "Consider adding resource limits",
            "suggestion_category": "best_practice",
            "confidence": "high",
            "example_improvement": "Add resources: {requests: {cpu: 100m}}"
        }
    ]
}
```

### Saving Output

**From Claude Desktop:**
1. Select the generated YAML code block
2. Click "Copy"
3. Create file in your project: `git checkout workflow.yml`
4. Paste content

**From API Response:**
```python
response = client.messages.create(...)
for block in response.content:
    if block.type == "tool_use":
        # Get result from invoke_tool()
        result = invoke_tool(block.name, block.input)
        
        with open("workflow.yml", "w") as f:
            f.write(result["generated_config"])
```

### Validating Output

**Before committing:**

```bash
# Validate YAML syntax
python -m yaml workflow.yml

# Validate GitHub Actions
gh workflow validate workflow.yml

# Validate Kubernetes
kubectl apply -f deployment.yaml --dry-run=client

# Validate Jenkins
groovysh -e 'import static groovy.lang.GroovyShell.*; load("Jenkinsfile")'
```

---

## Troubleshooting

### Skill Not Available

**Symptom:** Claude says "Tool not found" or "Unknown skill"

**Solutions:**
1. Restart Claude Desktop completely (⌘Q, then reopen)
2. Update the repo: `git pull origin main`
3. Reinstall: `pip install -r mcp_server/requirements.txt`
4. Check MCP server is running: Look for 🔧 wrench icon in Claude

### Poor Quality Output

**Symptom:** Generated workflow is too simple or missing important stages

**Solutions:**
1. Be more specific in your prompt:
   - ❌ "Generate a workflow"
   - ✅ "Generate a complete GitHub Actions workflow with build, test, and Kubernetes deployment stages"

2. Specify parameters explicitly:
   - Add languages: "for a Python and Node.js project"
   - Add Kubernetes: "with Kubernetes deployment using ArgoCD"
   - Add matrix: "with matrix builds for Python 3.9 and 3.10"

3. Ask for step-by-step generation:
   - First: "Generate the build stage with..."
   - Then: "Now add a test stage with..."
   - Finally: "Now add a deploy stage with..."

### Output Doesn't Match My Setup

**Symptom:** Generated config references wrong image registry, namespace, or tool

**Solutions:**
1. Mention specifics in prompt:
   - "Push image to ghcr.io/myorg/myapp"
   - "Deploy to production namespace"
   - "Use ArgoCD for continuous delivery"

2. After generation, ask Claude to modify:
   - "Change the registry to quay.io/myteam"
   - "Update the namespace to staging"
   - "Replace kubectl with ArgoCD"

### Validation Errors

**Symptom:** Generated YAML fails validation

**Solutions:**
1. Show error to Claude:
   - "The generated workflow fails validation: [error message]"
   - "Fix the YAML to resolve: [issue]"

2. Claude will revise the configuration

---

## Best Practices

### Prompt Writing Tips

1. **Be Specific**
   ```
   ✓ Good: "Generate a complete GitHub Actions workflow for a Python Flask API with Docker build and Kubernetes deployment using ArgoCD"
   ✗ Vague: "Generate a workflow"
   ```

2. **Mention All Key Details**
   ```
   ✓ Include: framework (Flask), language (Python), registry (Docker Hub), deployment method (ArgoCD)
   ✗ Assume: Claude will guess your setup
   ```

3. **Ask for Explanation**
   ```
   ✓ "Generate the workflow AND explain each stage"
   ✗ Just generate, no context
   ```

4. **Iterate Incrementally**
   ```
   ✓ First: "Generate basic workflow"
     Then: "Add SonarQube analysis"
     Then: "Add Kubernetes deployment"
   ✗ Try to get everything in one prompt
   ```

### Output Validation

1. **Always Review Generated Code**
   - Check for correct image registries
   - Verify namespace and resource names
   - Ensure authentication is properly configured

2. **Test Before Committing**
   ```bash
   # Dry-run the generated configuration
   kubectl apply -f deployment.yaml --dry-run=client -o yaml
   ```

3. **Store in Version Control**
   - Commit generated configs to git
   - Track changes over time
   - Enable code review process

---

## Example Workflow: Start to Production

```
1. Clarify Requirements
   User: "I have a Python Flask API. What do I need?"
   Claude: "I'll generate GitHub Actions, Kubernetes config, and monitoring"

2. Generate CI/CD Pipeline
   User: "Generate GitHub Actions for Flask API with Docker and Kubernetes"
   Claude: [Uses generate_github_actions_workflow]

3. Generate Infrastructure
   User: "Generate Kubernetes manifests for my Flask API"
   Claude: [Uses generate_k8s_config]

4. Generate Observability
   User: "Generate Prometheus alerts and Grafana dashboard"
   Claude: [Uses generate_sre_configs]

5. Review & Customize
   User: Shows generated configs to team
   Team: "Change registry to quay.io, use ArgoCD instead of kubectl"
   User: "Update the workflow to use quay.io and ArgoCD"
   Claude: Modifies configs accordingly

6. Commit & Deploy
   User: Commits all configs to git
   User: Deploys to production
```

---

**Last Updated:** October 2, 2026  
**DevOps-OS MCP Version:** 0.4.7
