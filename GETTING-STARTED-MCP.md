# Getting Started with DevOps-OS MCP Server

**DevOps-OS exposes all its CI/CD, Kubernetes, and SRE generators as an MCP server**, allowing you to use them directly in Claude Desktop, ChatGPT, or any MCP-compatible AI assistant.

---

## 🚀 Quick Start (5 Minutes)

### 1. Install

```bash
git clone https://github.com/cloudengine-labs/devops_os.git
cd devops_os

python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux

pip install -r mcp_server/requirements.txt
```

### 2. Add to Claude Desktop Config

Get your path:
```bash
pwd  # Copy this output
```

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):
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

**Windows:** Edit `%APPDATA%\Claude\claude_desktop_config.json` instead.

Restart Claude Desktop. You should see a wrench icon 🔧 at the bottom right.

### 3. Generate Your First Config

Ask Claude:

> *"Generate a GitHub Actions workflow for a Python project with pytest, Docker build, and deployment to AWS."*

Done! Claude will generate the workflow using DevOps-OS tools.

---

## 📖 Full Documentation

| Guide | For… |
|-------|------|
| **[MCP Quick Start](hugo-docs/content/docs/getting-started/mcp-quickstart.md)** | Get running in 5 minutes with Claude Desktop |
| **[MCP Setup & Configuration](hugo-docs/content/docs/ai-integration/mcp-setup.md)** | Deep dive: Claude, ChatGPT, HTTP endpoints, authentication, Docker deployment |
| **[AI Integration Overview](hugo-docs/content/docs/ai-integration/_index.md)** | See all available tools and prompts |
| **[Getting Started Guide](hugo-docs/content/docs/getting-started/_index.md)** | CLI commands and all features |

---

## 💬 What Can You Generate?

| Category | Tools | Example |
|----------|-------|---------|
| **CI/CD** | GitHub Actions, GitLab CI, Jenkins | Workflows for Python, Node.js, Java, Go |
| **Kubernetes** | Deployments, Services, ArgoCD, Flux | Production-ready manifests with monitoring |
| **GitOps** | ArgoCD Applications, Flux Kustomizations | Multi-environment deployments |
| **Hardening** | Kyverno policies, InSpec profiles, Checkov | CIS Kubernetes, STIG, NSA/CISA baselines |
| **Observability** | Prometheus rules, Grafana dashboards, SLOs | Service monitoring and alerting |
| **Dev Environment** | Dev Containers | Multi-language development setup |
| **Unit Tests** | pytest, Jest, Vitest, Mocha, Go test | Test scaffolding and CI integration |

---

## 🎯 Example Prompts

### Generate a GitHub Actions Workflow

```
Generate a GitHub Actions CI/CD workflow for a Python Flask API.
Include:
- Lint and test stages
- Docker build and push to Docker Hub
- Deployment to Kubernetes via kubectl
- Notifications on failure
```

### Generate Kubernetes Manifests

```
Create Kubernetes manifests for a Node.js microservice:
- Deployment with 3 replicas
- Service exposing port 3000
- Image: myregistry/my-service:v1.0
- Production namespace
```

### Generate Observability Configs

```
Generate Prometheus alert rules and a Grafana dashboard for a payment-processing microservice.
Include:
- High latency alerts (p99 > 500ms)
- Error rate alerts (> 1%)
- SLO dashboard with error budget tracking
```

### Generate Hardening Policies

```
Generate Kyverno policies for a production Kubernetes cluster based on CIS Kubernetes Benchmarks.
Include:
- Network policies
- Pod security standards
- RBAC baseline
```

---

## 🔧 Transports

DevOps-OS MCP can run in different modes:

| Mode | Use Case | Setup |
|------|----------|-------|
| **Stdio** | Claude Desktop (local) | `python -m mcp_server.server` |
| **HTTP (Local)** | Testing, custom clients | `DEVOPS_OS_TRANSPORT=streamable-http python -m mcp_server.server` |
| **HTTP (Remote)** | ChatGPT, production | Deployed on server + JWT auth |

See [MCP Setup & Configuration](hugo-docs/content/docs/ai-integration/mcp-setup.md) for detailed setup of each transport.

---

## 🐳 Docker Deployment

```bash
docker build -t devops-os-mcp .
docker compose up --profile local  # HTTP (no auth)
docker compose up --profile remote # HTTP with JWT auth
```

Environment variables:
```bash
DEVOPS_OS_PROFILE=remote
DEVOPS_OS_TRANSPORT=streamable-http
DEVOPS_OS_JWT_ISSUER=https://auth.provider.com/
DEVOPS_OS_JWT_AUDIENCE=devops-os-service
```

---

## 🆘 Troubleshooting

### Claude says "MCP server not responding"

1. Check the path in your config is correct
2. Verify Python can run it:
   ```bash
   python -m mcp_server.server
   ```
3. Restart Claude completely (⌘Q then reopen)

### "Tool not found" or "unknown tool"

- Update to latest: `git pull origin main`
- Reinstall: `pip install -r mcp_server/requirements.txt`
- Restart Claude

See [MCP Setup & Configuration - Troubleshooting](hugo-docs/content/docs/ai-integration/mcp-setup.md#troubleshooting) for more.

---

## 💡 Prompt Improvement Suggestions

DevOps-OS MCP now includes an intelligent **prompt suggestion system** that analyzes your prompts and recommends improvements to get better configurations.

### How It Works

When you ask Claude to generate a config:

> **You:** "Generate a Kubernetes deployment"

Claude receives:
1. **Generated manifest** - Your requested YAML/config
2. **Suggestions** - Recommendations to improve your prompt:
   - "Consider specifying a namespace (e.g., production, staging, development)"
   - "Specify the number of replicas for high availability and load balancing"

### Example Suggestions

```json
{
  "prompt_suggestions": [
    {
      "suggestion_text": "Specify a namespace for proper resource isolation",
      "suggestion_category": "context",
      "confidence": "high",
      "example_improvement": "Generate Kubernetes deployment in the payments namespace..."
    }
  ]
}
```

### Disable Suggestions (Optional)

If you prefer just the raw output:

```bash
export DEVOPS_OS_ENABLE_SUGGESTIONS=false
python -m mcp_server.server
```

### Configuration

Customize suggestion behavior:

```bash
# Only show high-confidence suggestions
export DEVOPS_OS_SUGGESTION_CONFIDENCE_THRESHOLD=high

# Show up to 3 suggestions per response
export DEVOPS_OS_MAX_SUGGESTIONS_PER_RESPONSE=3

# Disable example improved prompts
export DEVOPS_OS_INCLUDE_EXAMPLES_IN_SUGGESTIONS=false
```

👉 **Full details:** See [Prompt Improvement Suggestions Guide](PROMPT_SUGGESTIONS.md)

---

## 📚 Next Steps

- **[MCP Quick Start](hugo-docs/content/docs/getting-started/mcp-quickstart.md)** — 5-minute guide for Claude Desktop
- **[MCP Setup Guide](hugo-docs/content/docs/ai-integration/mcp-setup.md)** — Detailed configuration for all transports
- **[CLI Commands](hugo-docs/content/docs/getting-started/_index.md)** — Run generators from command line instead
- **[Full Documentation](https://devops-os.io/)** — All features and guides

---

## 🤝 Support

- **Questions?** [GitHub Discussions](https://github.com/cloudengine-labs/devops_os/discussions)
- **Found a bug?** [GitHub Issues](https://github.com/cloudengine-labs/devops_os/issues)
- **Full docs:** [https://devops-os.io/](https://devops-os.io/)

---

## 📄 License

DevOps-OS is MIT licensed. See [LICENSE](LICENSE) for details.
