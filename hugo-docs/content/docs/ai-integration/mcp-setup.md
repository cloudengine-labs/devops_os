---
title: "MCP Setup & Configuration"
weight: 20
---

# MCP Setup & Configuration Guide

This guide covers detailed setup and configuration of DevOps-OS as an MCP (Model Context Protocol) server for local and remote use with Claude, ChatGPT, and other AI assistants.

---

## What is MCP?

**MCP (Model Context Protocol)** is an open standard that lets AI assistants directly call tools and functions in your applications. DevOps-OS exposes all its pipeline generators as MCP tools, allowing Claude or ChatGPT to generate CI/CD pipelines, Kubernetes configs, and SRE dashboards on your behalf.

### MCP vs. Traditional Integration

| Aspect | Traditional API | MCP |
|--------|-----------------|-----|
| **Setup** | Manual HTTP server + OpenAPI spec | Built-in, auto-discovered |
| **Discovery** | Must document endpoints | Tools automatically discovered |
| **Execution** | Sync HTTP requests | Async, integrated into chat |
| **Debugging** | View logs manually | Built-in error messaging |
| **Authentication** | API keys everywhere | Scoped per transport (stdio/HTTP) |

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│          AI Assistant (Claude / ChatGPT)    │
│     (understands your request in natural    │
│          language, selects tools)           │
└────────────────────┬────────────────────────┘
                     │ MCP message
                     ▼
┌─────────────────────────────────────────────┐
│     DevOps-OS MCP Server (FastMCP)          │
│  ┌─────────────────────────────────────┐   │
│  │   Tool Discovery                    │   │
│  │   - generate_github_actions         │   │
│  │   - generate_jenkins_pipeline       │   │
│  │   - generate_k8s_config             │   │
│  │   - generate_argocd_config          │   │
│  │   - generate_sre_configs            │   │
│  │   - ... and more                    │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │   Transport Layer                   │   │
│  │   - Stdio (for Claude Desktop)      │   │
│  │   - HTTP (for remote/ChatGPT)       │   │
│  │   - Auth (JWT/OIDC for remote)      │   │
│  └─────────────────────────────────────┘   │
└─────────────┬───────────────────────────────┘
              │ Invokes Python generators
              ▼
┌─────────────────────────────────────────────┐
│     DevOps-OS CLI Generators (shared)       │
│  - scaffold_gha()                           │
│  - scaffold_jenkins()                       │
│  - scaffold_k8s()                           │
│  - scaffold_argocd()                        │
│  - scaffold_sre()                           │
│  - ... and more                             │
└─────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│   Generated DevOps Artifacts                │
│  - GitHub Actions workflow YAML             │
│  - Jenkins Declarative Pipeline             │
│  - Kubernetes manifests                     │
│  - ArgoCD Application CRs                   │
│  - Prometheus alert rules                   │
│  - Grafana dashboards                       │
│  - SLO definitions                          │
└─────────────────────────────────────────────┘
```

---

## Installation

### 1. Prerequisites

- **Python 3.10+**
- **pip** (Python package manager)
- **Git** (to clone the repo)
- For Claude Desktop: **Claude Desktop** installed
- For ChatGPT: **ChatGPT Developer Mode** (requires Plus subscription)

### 2. Clone and Install

```bash
git clone https://github.com/cloudengine-labs/devops_os.git
cd devops_os

# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Install MCP server dependencies
pip install -r mcp_server/requirements.txt
```

---

## Local Setup: Claude Desktop

### Step 1: Get Your DevOps-OS Path

```bash
# From the devops_os directory, get the absolute path
pwd  # macOS/Linux
# Output: /Users/yourname/projects/devops_os

# Windows
cd  # will show your current directory
```

### Step 2: Locate Claude Desktop Config

**macOS/Linux:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

### Step 3: Edit the Config

Add the DevOps-OS MCP server to your config:

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

**Example (macOS):**
```json
{
  "mcpServers": {
    "devops-os": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/Users/alice/projects/devops_os"
    }
  }
}
```

### Step 4: Restart Claude Desktop

1. Quit Claude completely (⌘Q on macOS, Alt+F4 on Windows)
2. Reopen Claude Desktop
3. You should see a small wrench icon (🔧) at the bottom right of the chat — this indicates MCP is connected

### Step 5: Test It

In Claude Desktop, ask:

> *"Generate a GitHub Actions CI/CD workflow for a Python and Node.js application with Kubernetes deployment using Kustomize."*

Claude will:
1. Understand your request
2. Call the `generate_github_actions_workflow` tool
3. Pass the parameters (name, languages, deployment method)
4. Return the generated workflow YAML
5. Explain what each stage does

---

## Remote Setup: HTTP Endpoint

For ChatGPT, custom GPTs, or remote clients, you can run DevOps-OS as an HTTP server.

### Step 1: Install HTTP Dependencies

```bash
pip install -r mcp_server/requirements.txt
```

### Step 2: Start the HTTP Server

```bash
# Start the server (default: localhost:8000)
DEVOPS_OS_TRANSPORT=streamable-http python -m mcp_server.server

# Or with explicit configuration
DEVOPS_OS_PROFILE=local \
DEVOPS_OS_TRANSPORT=streamable-http \
DEVOPS_OS_HOST=0.0.0.0 \
DEVOPS_OS_PORT=8000 \
  python -m mcp_server.server
```

**Output:**
```
[2024-09-11 10:30:42,123] INFO mcp_server.server - Starting DevOps-OS MCP server in local profile (stdio transport)
[2024-09-11 10:30:42,456] INFO mcp_server.server - HTTP endpoint available at http://localhost:8000/mcp
[2024-09-11 10:30:42,789] INFO mcp_server.server - MCP tools discovered: 15
```

### Step 3: Test the Endpoint

```bash
# In a new terminal, test that tools are discoverable
curl http://localhost:8000/mcp/tools

# Should return JSON list of available tools
```

### Step 4: Connect ChatGPT or Custom Client

See the [ChatGPT Integration](#chatgpt-setup-custom-gpt) section below.

---

## Remote Setup: Authenticated Access

For production deployments, enable authentication with JWT/OIDC.

### Step 1: Configure JWT Settings

```bash
# Use Auth0, Keycloak, or another OIDC provider
# Set these environment variables:

DEVOPS_OS_PROFILE=remote \
DEVOPS_OS_TRANSPORT=streamable-http \
DEVOPS_OS_JWT_ISSUER=https://your-auth.provider.com/ \
DEVOPS_OS_JWT_AUDIENCE=devops-os-service \
DEVOPS_OS_JWT_JWKS_URL=https://your-auth.provider.com/.well-known/jwks.json \
  python -m mcp_server.server
```

### Step 2: Obtain Access Token

From your identity provider (Auth0, Azure AD, Keycloak, etc.):

```bash
# Example: Auth0
curl -X POST https://your-tenant.auth0.com/oauth/token \
  -H 'Content-Type: application/json' \
  -d '{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "audience": "devops-os-service",
    "grant_type": "client_credentials"
  }'

# Response includes: access_token
```

### Step 3: Use the Token

When calling the MCP server, include the token in the `Authorization` header:

```bash
curl -X POST http://your-server:8000/mcp \
  -H "Authorization: ******" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "resources/list"
  }'
```

---

## ChatGPT Setup: Custom GPT

### Step 1: Deploy to Public HTTPS

Your DevOps-OS HTTP server must be accessible from the internet over HTTPS.

**Options:**
- Deploy to AWS Lambda + API Gateway
- Deploy to Heroku, Render, or Railway
- Use ngrok for local development: `ngrok http 8000`

### Step 2: Create a Custom GPT

1. Go to [ChatGPT → My GPTs → Create a GPT](https://chatgpt.com/gpts/editor)
2. Give it a name: *"DevOps-OS Generator"*
3. Click **"Configure"** → **"Actions"** → **"Create new action"**

### Step 3: Add OpenAPI Schema

Paste the OpenAPI schema from `skills/openai_functions.json`:

```bash
# View the schema
cat skills/openai_functions.json
```

Paste the entire JSON into the Custom GPT action editor.

### Step 4: Configure Authentication

- Set **Server URL** to your deployed endpoint: `https://your-domain.com/mcp`
- Choose **Authentication type** based on your deployment:
  - **None** (for local/testing with ngrok)
  - ******** (for JWT-authenticated endpoints)
  - **OAuth** (if your provider supports it)

### Step 5: Test the GPT

Ask your Custom GPT:

> *"Generate a Jenkins pipeline for a Java Spring Boot microservice with Docker build and ArgoCD deployment stages."*

---

## Docker Deployment

For containerized deployment, use the provided Dockerfile.

### Step 1: Build the Image

```bash
docker build -t devops-os-mcp:latest .
```

### Step 2: Run with Docker Compose

```bash
# Local development (stdio)
docker compose up --profile stdio

# HTTP development (no auth)
docker compose up --profile local

# Remote with mock JWT (for testing)
docker compose up --profile remote
```

### Step 3: Configure Environment

Create a `.env` file:

```bash
# .env
DEVOPS_OS_PROFILE=remote
DEVOPS_OS_TRANSPORT=streamable-http
DEVOPS_OS_HOST=0.0.0.0
DEVOPS_OS_PORT=8000
DEVOPS_OS_JWT_ISSUER=https://your-auth.provider.com/
DEVOPS_OS_JWT_AUDIENCE=devops-os-service
DEVOPS_OS_JWT_JWKS_URL=https://your-auth.provider.com/.well-known/jwks.json
```

Then:

```bash
docker run --env-file .env -p 8000:8000 devops-os-mcp:latest
```

---

## Configuration Reference

### Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DEVOPS_OS_PROFILE` | `local` (dev) or `remote` (production) | `local` | `remote` |
| `DEVOPS_OS_TRANSPORT` | `stdio` or `streamable-http` | `stdio` | `streamable-http` |
| `DEVOPS_OS_HOST` | Bind address for HTTP server | `127.0.0.1` | `0.0.0.0` |
| `DEVOPS_OS_PORT` | Bind port for HTTP server | `8000` | `8000` |
| `DEVOPS_OS_MCP_ENDPOINT` | MCP protocol endpoint path | `/mcp` | `/tools/mcp` |
| `DEVOPS_OS_REQUEST_TIMEOUT` | Request timeout in seconds | `300` | `120` |
| `DEVOPS_OS_MAX_CONCURRENT_CALLS` | Max concurrent tool calls | `10` | `5` |
| `DEVOPS_OS_LOG_LEVEL` | Log verbosity | `INFO` | `DEBUG` |
| `DEVOPS_OS_JWT_ISSUER` | JWT issuer URL (remote only) | None | `https://auth.example.com/` |
| `DEVOPS_OS_JWT_AUDIENCE` | JWT audience (remote only) | None | `devops-os-service` |
| `DEVOPS_OS_JWT_JWKS_URL` | JWKS endpoint URL | Auto-derived | `https://auth.example.com/.well-known/jwks.json` |
| `DEVOPS_OS_JWT_ALGORITHMS` | Allowed JWT algorithms | `RS256,ES256` | `RS256` |

### Configuration Profiles

**Local Profile (Development)**
```bash
DEVOPS_OS_PROFILE=local \
DEVOPS_OS_TRANSPORT=stdio \
  python -m mcp_server.server
```
- No authentication required
- Loopback-only for HTTP
- For Claude Desktop or local testing

**Remote Profile (Production)**
```bash
DEVOPS_OS_PROFILE=remote \
DEVOPS_OS_TRANSPORT=streamable-http \
DEVOPS_OS_JWT_ISSUER=https://auth.example.com/ \
DEVOPS_OS_JWT_AUDIENCE=devops-os-service \
  python -m mcp_server.server
```
- Requires valid JWT token
- Can bind to all interfaces
- For ChatGPT, custom GPTs, and remote clients

---

## Troubleshooting

### Claude Desktop: "MCP connection failed"

**Symptoms:**
- Claude shows error: "MCP server not responding"
- Wrench icon (🔧) shows error badge

**Solutions:**

1. **Check the path is correct:**
   ```bash
   # Ensure the cwd exists
   ls /path/to/devops_os/mcp_server/server.py
   ```

2. **Verify Python is accessible:**
   ```bash
   # From the devops_os directory
   python -c "from mcp_server import server; print('OK')"
   ```

3. **Check for startup errors:**
   ```bash
   # Run the server manually to see errors
   python -m mcp_server.server
   # Ctrl+C to stop
   ```

4. **Restart Claude entirely:**
   - On macOS: `⌘Q` then reopen
   - On Windows: Alt+F4 then reopen

### HTTP Server: "Address already in use"

**Symptoms:**
```
OSError: [Errno 48] Address already in use
```

**Solutions:**

1. **Use a different port:**
   ```bash
   DEVOPS_OS_PORT=8001 python -m mcp_server.server
   ```

2. **Kill the existing process:**
   ```bash
   # Find the process
   lsof -i :8000
   # Kill it
   kill -9 <PID>
   ```

### HTTP Server: "Connection refused" from ChatGPT

**Symptoms:**
- Custom GPT shows: "Server returned an error"
- Endpoint is unreachable

**Solutions:**

1. **Verify server is running:**
   ```bash
   curl http://localhost:8000/mcp/tools
   # Should return JSON list of tools
   ```

2. **Check if endpoint is public:**
   ```bash
   # From a different machine or phone
   curl https://your-domain.com/mcp/tools
   ```

3. **Check firewall rules:**
   - Ensure port 8000 (or your chosen port) is open
   - For cloud deployments, check security group rules

4. **Verify HTTPS for remote:**
   - ChatGPT requires HTTPS (not HTTP)
   - Use ngrok for local testing: `ngrok http 8000`

### Authentication: "Invalid token"

**Symptoms:**
```json
{
  "error": "Invalid token",
  "details": "Token signature verification failed"
}
```

**Solutions:**

1. **Verify token is not expired:**
   ```bash
   # Decode the JWT (without verifying)
   # Use https://jwt.io or:
   python -c "
   import json
   import base64
   token = 'your.jwt.token'
   parts = token.split('.')
   payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))
   print(json.dumps(payload, indent=2))
   "
   ```

2. **Check issuer and audience match:**
   ```bash
   # In your token, these must match config:
   # iss: matches DEVOPS_OS_JWT_ISSUER
   # aud: matches DEVOPS_OS_JWT_AUDIENCE
   ```

3. **Verify JWKS is accessible:**
   ```bash
   curl https://your-auth.provider.com/.well-known/jwks.json
   ```

### Generator Tool Error: "ValidationError"

**Symptoms:**
```
ValidationError: name must be 1-63 characters
```

**Solutions:**

1. **Check input constraints:**
   - `name`: 1-63 alphanumeric characters (hyphens allowed)
   - `languages`: comma-separated, lowercase (e.g., `python,javascript`)
   - `workflow_type`: one of `build`, `test`, `deploy`, `complete`

2. **Ask Claude to fix it:**
   > *"Generate a GitHub Actions workflow for a valid project name 'my-app' with Python and JavaScript."*

3. **Check the docs:**
   See [CLI Reference]({{< relref "/docs/reference" >}}) for all options and constraints.

---

## Next Steps

- [AI Integration Overview]({{< relref "/docs/ai-integration" >}})
- [MCP Quick Start (5 minutes)]({{< relref "/docs/getting-started/mcp-quickstart" >}})
- [Authentication Setup Details]({{< relref "/docs/ai-integration/mcp-setup#remote-setup-authenticated-access" >}})
- [Troubleshooting & FAQ]({{< relref "/docs/ai-integration/mcp-setup#troubleshooting" >}})
- [CLI Reference]({{< relref "/docs/reference" >}})

---

## Support

- 🐛 **Bug reports:** [GitHub Issues](https://github.com/cloudengine-labs/devops_os/issues)
- 💬 **Questions:** [GitHub Discussions](https://github.com/cloudengine-labs/devops_os/discussions)
- 📖 **Documentation:** [Full Docs](https://devops-os.io/docs/)
