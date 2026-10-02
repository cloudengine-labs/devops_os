---
title: "ChatGPT Custom GPT Integration"
weight: 30
---

# ChatGPT Custom GPT Integration Guide

This guide covers setting up and using DevOps-OS with **ChatGPT and Custom GPTs** for pipeline generation and DevOps automation.

---

## What is ChatGPT and Custom GPTs?

**ChatGPT** is an advanced AI chatbot that understands natural language and can perform complex tasks. **Custom GPTs** let you create specialized versions of ChatGPT with custom instructions, knowledge files, and function calling capabilities.

### Why Use ChatGPT with DevOps-OS?

| Feature | Benefit |
|---------|---------|
| **User-friendly UI** | No coding required, just chat |
| **Custom GPT** | Create a specialized DevOps assistant for your team |
| **Function calling** | ChatGPT directly invokes DevOps-OS generators |
| **Knowledge base** | Attach your org's runbooks and best practices |
| **Shareable** | Create a GPT once, share with your team |
| **Web search** | ChatGPT can research infrastructure patterns for you |

---

## Prerequisites

- **ChatGPT Plus account** (paid subscription required for Custom GPTs)
- **DevOps-OS repository** cloned locally or deployed to a server
- **Python 3.10+** (for running the HTTP server)
- **HTTPS endpoint** (ChatGPT requires HTTPS, not HTTP)

### Get ChatGPT Plus

1. Go to [ChatGPT](https://chatgpt.com)
2. Click **"Upgrade to Plus"** (bottom left)
3. Choose your plan ($20/month)
4. Complete payment

---

## Architecture Overview

```
┌──────────────────────────────────────┐
│  ChatGPT (Web or Mobile App)         │
│  "Generate a Kubernetes config       │
│   for my Node.js microservice"       │
└────────────────┬─────────────────────┘
                 │ HTTPS request
                 ▼
    ┌────────────────────────────────┐
    │  Custom GPT (Your DevOps Bot)  │
    │  ┌──────────────────────────┐  │
    │  │ System Instructions      │  │
    │  │ - DevOps best practices  │  │
    │  │ - Your team's standards  │  │
    │  └──────────────────────────┘  │
    └────────────────┬────────────────┘
                     │
                     ▼
    ┌────────────────────────────────┐
    │  DevOps-OS HTTP Server         │
    │  (Running on your infrastructure) │
    │  ┌──────────────────────────┐  │
    │  │ Function Definitions     │  │
    │  │ (openai_functions.json)  │  │
    │  └──────────────────────────┘  │
    └────────────────┬────────────────┘
                     │
                     ▼
    ┌────────────────────────────────┐
    │  DevOps-OS Generators          │
    │  - Python CLI functions        │
    │  - Validation and constraints  │
    └────────────────┬────────────────┘
                     │
                     ▼
    ┌────────────────────────────────┐
    │  Generated Artifacts           │
    │  - GitHub Actions YAML         │
    │  - Jenkins Declarative         │
    │  - Kubernetes manifests        │
    │  - ArgoCD configs              │
    │  - Prometheus alerts           │
    └────────────────────────────────┘
```

---

## Step 1: Deploy DevOps-OS as HTTP Server

Your DevOps-OS must be accessible from the internet over HTTPS for ChatGPT to call it.

### Option A: Local Development (ngrok Tunnel)

For testing, use **ngrok** to expose your local server:

```bash
# Install ngrok if you haven't already
# macOS with Homebrew:
brew install ngrok

# Create ngrok account and get auth token at https://dashboard.ngrok.com/auth/your-authtoken

# Authenticate
ngrok config add-authtoken YOUR_AUTH_TOKEN

# In terminal 1: Start DevOps-OS HTTP server
export DEVOPS_OS_TRANSPORT=streamable-http
export DEVOPS_OS_HOST=127.0.0.1
export DEVOPS_OS_PORT=8000
python -m mcp_server.server

# In terminal 2: Start ngrok tunnel
ngrok http 8000

# You'll see output like:
# Forwarding     https://abc123.ngrok.io -> http://localhost:8000
# Use https://abc123.ngrok.io as your Server URL in Custom GPT
```

**Note:** ngrok URLs are temporary and change on restart. Use this only for testing.

### Option B: Cloud Deployment (Production)

Deploy to AWS Lambda, Heroku, Render, or Railway:

**AWS Lambda + API Gateway:**

```bash
# Install deployment tools
pip install zappa  # AWS Lambda deployment

# Configure zappa_settings.json
cat > zappa_settings.json << 'EOF'
{
    "production": {
        "app_function": "mcp_server.server:app",
        "aws_region": "us-east-1",
        "profile_name": "default",
        "project_name": "devops-os",
        "runtime": "python3.11",
        "s3_bucket": "zappa-deployments-your-bucket",
        "environment_variables": {
            "DEVOPS_OS_PROFILE": "remote",
            "DEVOPS_OS_TRANSPORT": "streamable-http"
        }
    }
}
EOF

# Deploy
zappa deploy production

# Output will include your HTTPS URL
# https://your-api-id.execute-api.us-east-1.amazonaws.com/production
```

**Heroku Deployment:**

```bash
# Install Heroku CLI
# macOS: brew install heroku/brew/heroku

# Login to Heroku
heroku login

# Create app
heroku create devops-os-app

# Set environment variables
heroku config:set DEVOPS_OS_PROFILE=remote
heroku config:set DEVOPS_OS_TRANSPORT=streamable-http

# Deploy
git push heroku main

# Get your URL
heroku open
# Your HTTPS endpoint: https://devops-os-app.herokuapp.com
```

### Step 2: Verify the Server is Running

```bash
# Test that your server is accessible
curl https://your-domain.com/mcp/tools

# Should return JSON list of available tools:
# [
#   {"name": "generate_github_actions_workflow", ...},
#   {"name": "generate_jenkins_pipeline", ...},
#   ...
# ]
```

---

## Step 2: Create a Custom GPT

### A. Access GPT Editor

1. Go to [ChatGPT](https://chatgpt.com)
2. Click your profile icon (top-right corner) → **"My GPTs"**
3. Click **"Create a GPT"**

### B. Configure Basic Info

In the **"Create"** tab (left side):

1. **Name:** *"DevOps-OS Generator"* (or your preferred name)
2. **Description:** *"AI assistant for generating CI/CD pipelines, Kubernetes configs, and DevOps infrastructure"*
3. **Instructions:** Paste the following:

```
You are an expert DevOps engineer assistant. Your role is to help generate:
- GitHub Actions CI/CD workflows
- Jenkins declarative pipelines
- Kubernetes manifests
- GitLab CI pipelines
- Argo CD configurations
- SRE monitoring configs (Prometheus, Grafana, SLO)
- Dev containers

Always ask clarifying questions about:
1. The project type and languages
2. The deployment target (Kubernetes, VM, serverless)
3. The desired workflow type (build, test, deploy, or complete)
4. Specific requirements (databases, message queues, etc.)

When the user requests pipeline generation, use the appropriate function based on their needs. Always explain what each stage does and provide tips for customization.

For Kubernetes configs, provide both a basic version and an advanced version with best practices like health checks, resource limits, and security policies.
```

4. **Conversation starters** (optional):
   ```
   - Generate a GitHub Actions workflow for my Python + Node.js app
   - Create a Kubernetes deployment for my microservice
   - Build a complete CI/CD pipeline with Docker and ArgoCD
   - Generate an SRE config with Prometheus monitoring
   ```

### C. Add Knowledge Files (Optional)

In the **"Create"** tab, scroll down to **"Knowledge"**:

1. Click **"Add files"**
2. Upload your documentation:
   - Internal DevOps standards guide
   - Your team's architecture diagrams
   - CI/CD pipeline examples
   - Kubernetes best practices

This helps ChatGPT align with your organization's standards.

### D. Configure Actions (Function Calling)

1. Switch to the **"Configure"** tab (top-right)
2. Scroll to **"Actions"**
3. Click **"Create new action"**

**In the new action dialog:**

1. **Authentication:** Select based on your setup:
   - **None** (for ngrok or local testing)
   - **API Key** (for simple static authentication)
   - **OAuth** (for OAuth2-based services)

2. **Server URL:** Enter your HTTPS endpoint:
   ```
   https://your-domain.com  # or your ngrok URL
   ```

3. **Schema:** Paste the full contents of `skills/openai_functions.json`

   ```bash
   # Get the schema
   cat skills/openai_functions.json
   ```

   Paste everything (or upload the file if the dialog supports it)

4. Click **"Save"**

### E. Finalize and Publish

1. Click **"Save"** (top-right)
2. Choose **"Only me"** to keep it private, or **"Anyone with the link"** to share
3. Get your GPT's sharing link from **"My GPTs"**

---

## Step 3: Test the Custom GPT

### Test 1: Basic Workflow Generation

Ask your Custom GPT:

> *"Generate a GitHub Actions CI/CD workflow for a Python Flask web application. It should include:*
> *- Unit tests with pytest*
> *- Docker image build*
> *- Push to DockerHub*
> *- Deployment to Kubernetes using kubectl apply"*

Expected flow:
1. ChatGPT asks clarifying questions (if needed)
2. ChatGPT calls `generate_github_actions_workflow` function
3. DevOps-OS returns the workflow YAML
4. ChatGPT displays the result with explanations

### Test 2: Kubernetes Deployment

> *"Create a Kubernetes deployment for my Node.js API server with these details:*
> *- App name: api-gateway*
> *- Docker image: ghcr.io/myorg/api-gateway:v1.0.0*
> *- 3 replicas*
> *- Port 8080*
> *- Include health checks and resource limits"*

### Test 3: Multi-Stage Pipeline

> *"Generate a complete Jenkins declarative pipeline for a Java Spring Boot microservice that:*
> *- Builds with Maven*
> *- Runs SonarQube analysis*
> *- Builds Docker image*
> *- Pushes to ECR*
> *- Deploys to EKS via Helm*
> *- Sends Slack notifications"*

---

## Advanced: Authentication

For production deployments with authentication:

### JWT Authentication

If your DevOps-OS server requires JWT tokens:

1. In the Custom GPT **Actions** dialog, set **Authentication** to **API Key**
2. Copy your JWT token and paste it as the API Key
3. ChatGPT will include it in all requests

**To generate a token (using your auth provider):**

```bash
# Example with Auth0
curl -X POST https://your-tenant.auth0.com/oauth/token \
  -H 'Content-Type: application/json' \
  -d '{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "audience": "devops-os-service",
    "grant_type": "client_credentials"
  }'

# Response:
# {
#   "access_token": "******",
#   "token_type": "Bearer",
#   "expires_in": 86400
# }

# Use the access_token in ChatGPT
```

### OAuth2 Authentication

For OAuth2-compatible providers:

1. Set **Authentication** to **OAuth**
2. Provide:
   - **Authorization URL:** `https://your-auth-provider.com/oauth/authorize`
   - **Token URL:** `https://your-auth-provider.com/oauth/token`
   - **Client ID:** Your OAuth app's client ID
3. ChatGPT handles the OAuth flow automatically

---

## Example Prompts

### GitHub Actions

```
Generate a GitHub Actions workflow for a Node.js app that:
- Runs on: push to main, pull_request
- Node 18.x and 20.x matrices
- Install dependencies with npm ci
- Run ESLint for linting
- Run Jest unit tests
- Build Docker image
- Push to ghcr.io/myorg/my-app:${{ github.sha }}
- Deploy to production with kubectl if on main branch
- Send Slack notifications for failures
```

### Jenkins Pipeline

```
Create a Jenkins declarative pipeline for a Python microservice:
- Stage 1: Checkout from GitHub
- Stage 2: Build with Poetry, run black/flake8 linting
- Stage 3: Run pytest with coverage report
- Stage 4: Build Docker image with version tag
- Stage 5: Push to AWS ECR
- Stage 6: Deploy to EKS with Helm, waiting for healthy pod
- Post-build: Archive test reports, notify via email on failure
```

### Kubernetes

```
Generate Kubernetes manifests for a production-ready deployment:
- App name: checkout-api
- Namespace: production
- Docker image: registry.example.com/checkout-api:1.2.3
- 5 replicas with pod disruption budget
- Port 8080, service type LoadBalancer
- Health checks: liveness at /health, readiness at /ready (10s interval)
- Resource limits: CPU 500m, memory 512Mi; requests: CPU 250m, memory 256Mi
- Environment variables: LOG_LEVEL=info, DB_POOL_SIZE=20
- Secrets from vault-db-credentials
- ConfigMap for application.conf
```

### Complete CI/CD Stack

```
I need a complete CI/CD pipeline for my team:
- GitHub Actions for CI (test + build)
- Docker image push to ECR
- Argo CD for GitOps deployment
- Kubernetes manifests with health checks
- SRE monitoring with Prometheus and Grafana
- Alert rules for error rates and latency
- 99.9% availability SLO

Please generate:
1. GitHub Actions workflow
2. Kubernetes deployment and service
3. ArgoCD Application manifest
4. Prometheus recording rules and alerts
5. Grafana dashboard JSON

App details: name=payment-service, language=Python, image=ghcr.io/myorg/payment:v2.0
```

---

## Troubleshooting

### "Connection refused" or "Server not responding"

**Symptoms:**
- Custom GPT shows: "The server did not respond"
- Action fails silently

**Solutions:**

1. **Verify server is running:**
   ```bash
   curl https://your-domain.com/mcp/tools
   # Should return JSON list, not 404 or connection error
   ```

2. **Check HTTPS requirement:**
   - ChatGPT **only** accepts HTTPS endpoints
   - HTTP (without SSL) will be rejected
   - If using ngrok, ensure you use the `https://` URL

3. **Verify CORS headers** (if applicable):
   ```bash
   curl -i https://your-domain.com/mcp/tools
   # Check for: Access-Control-Allow-Origin: *
   ```

4. **Check firewall and security groups:**
   - AWS Security Group: Allow port 443 (HTTPS) from anywhere
   - Firewall: Allow outbound HTTPS to your endpoint
   - Rate limiting: Ensure your CDN/WAF isn't blocking requests

### "Action failed" with no details

**Symptoms:**
- Custom GPT reports: "Something went wrong"
- No error details in the response

**Solutions:**

1. **Check server logs:**
   ```bash
   # Tail the server logs (if running locally)
   python -m mcp_server.server 2>&1 | grep -i error
   ```

2. **Test the action schema:**
   ```bash
   # Try a manual request to verify your endpoint
   curl -X POST https://your-domain.com/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
   ```

3. **Verify the schema is valid:**
   - Copy your `skills/openai_functions.json` to [JSON Validator](https://jsonlint.com)
   - Check for syntax errors (missing quotes, commas, brackets)

4. **Check authentication:**
   - If using API Key, verify the token is valid and not expired
   - If using OAuth, ensure credentials are correct

### Custom GPT won't call the functions

**Symptoms:**
- Custom GPT talks about generating pipelines but doesn't call functions
- Functions aren't being invoked

**Solutions:**

1. **Update system instructions:**
   ```
   When the user asks to generate a pipeline, ALWAYS use the appropriate function:
   - Use 'generate_github_actions_workflow' for GitHub Actions
   - Use 'generate_jenkins_pipeline' for Jenkins
   - Use 'generate_k8s_config' for Kubernetes
   
   Do not generate YAML manually; call the function.
   ```

2. **Make the action more prominent:**
   - In **Configure** tab, ensure the action is properly saved
   - Edit and re-save the action to refresh it

3. **Test with specific request:**
   ```
   User: "I need to generate a GitHub Actions workflow. Call the generate_github_actions_workflow function with name=my-app and languages=python,javascript."
   ```

### Generated output has validation errors

**Symptoms:**
- YAML syntax errors in generated pipelines
- Missing required fields
- Invalid container images

**Solutions:**

1. **Ask ChatGPT to validate:**
   > *"Check this workflow for errors and fix any issues"* [paste YAML]

2. **Provide constraints in instructions:**
   Add to your Custom GPT instructions:
   ```
   When generating workflows:
   - Always validate YAML syntax
   - Use image tags, not 'latest'
   - Include resource limits for Kubernetes
   - Add health checks (liveness, readiness probes)
   - Ensure proper Secret/ConfigMap references
   ```

3. **Test with simplified requests:**
   Start with minimal requirements, then add complexity:
   ```
   "Generate a simple Kubernetes deployment for a Python app on port 8000"
   ```

---

## Tips and Best Practices

### 1. Share Custom GPT with Your Team

Once configured, share your Custom GPT:

1. In **My GPTs**, click your GPT
2. Click **"Share"** (top-right)
3. Choose **"Anyone with the link"**
4. Send the link to your team

Everyone can now use your configured DevOps assistant without setting it up themselves.

### 2. Use Knowledge Files for Consistency

Upload your team's standards:
- Architecture decision records (ADRs)
- Infrastructure diagrams
- CI/CD pipeline examples
- Kubernetes namespace policies
- Security scanning requirements

This ensures generated pipelines align with your organization's best practices.

### 3. Create Multiple Specialized GPTs

Create different GPTs for different purposes:
- **DevOps-K8s:** Specialized for Kubernetes
- **DevOps-GitHub:** Specialized for GitHub Actions
- **DevOps-SRE:** Specialized for monitoring and observability

Each can have custom instructions and knowledge files.

### 4. Iterate on Generated Code

Don't use generated code as-is. Ask ChatGPT to improve it:

```
"Add the following to this pipeline:
- Timeout after 30 minutes
- Retry policy for failed jobs
- Dependency caching
- Artifact upload to S3"
```

### 5. Monitor Generated Pipelines

After deploying generated pipelines:
- Review logs for any issues
- Adjust parameters based on actual performance
- Ask ChatGPT to refine future generations based on what you learned

---

## Next Steps

- [OpenAI Codex Integration]({{< relref "/docs/ai-integration/openai-codex-setup" >}}) — Use Codex for code generation
- [MCP Setup & Configuration]({{< relref "/docs/ai-integration/mcp-setup" >}}) — Run DevOps-OS as an MCP server
- [MCP Quick Start]({{< relref "/docs/getting-started/mcp-quickstart" >}}) — Get started in 5 minutes with Claude
- [CLI Reference]({{< relref "/docs/reference" >}}) — Full list of generators and options

---

## Support

- 🐛 **Bug reports:** [GitHub Issues](https://github.com/cloudengine-labs/devops_os/issues)
- 💬 **Questions:** [GitHub Discussions](https://github.com/cloudengine-labs/devops_os/discussions)
- 📖 **Documentation:** [Full Docs](https://devops-os.io/docs/)
- 🤖 **ChatGPT Help:** [OpenAI Support](https://help.openai.com)
