---
title: "Easy Getting Started"
weight: 12
---

# 🚀 Easy Getting Started — Just Copy & Paste

This is the **simplest way** to start using DevOps-OS MCP with Claude or ChatGPT.

> **🔗 Two Versions of DevOps-OS**
> - **DevOps-OS MCP** (this repo): Use with AI assistants (Claude, ChatGPT, Cursor, etc.)
> - **DevOps-OS CLI** ([cloudengine-labs/devops_os](https://github.com/cloudengine-labs/devops_os)): Use in scripts and automation
> 
> This guide covers MCP. For the CLI version, see the original project.

No complex configuration, just 3 commands + restart Claude.

---

## Setup (Just Copy & Paste)

### 1️⃣ Install in 30 Seconds

Copy and paste this in your terminal:

```bash
git clone https://github.com/chefgs/devops_os_mcp.git && cd devops_os_mcp && python3 -m venv .venv && source .venv/bin/activate && pip install -r mcp_server/requirements.txt
```

(On Windows, use `.venv\Scripts\activate` instead of `source .venv/bin/activate`)

### 2️⃣ Get Your Path

```bash
pwd
```

Copy the output (example: `/Users/alice/projects/devops_os_mcp`)

### 3️⃣ Add to Claude

**macOS:**
- Press `⌘ Cmd + Shift + .` to show hidden files
- Navigate to: `~/Library/Application Support/Claude/`
- Open `claude_desktop_config.json` in any text editor
- Replace the content with this (paste your path from Step 2):

```json
{
  "mcpServers": {
    "devops-os": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/paste/your/path/here"
    }
  }
}
```

**Windows:**
- Press `Win + R`, type: `%APPDATA%\Claude\`
- Open `claude_desktop_config.json` in any text editor
- Replace with the JSON above (use your Windows path)

**Linux:**
- Edit: `~/.config/Claude/claude_desktop_config.json`

### 4️⃣ Restart Claude

- Quit Claude completely
- Reopen Claude
- You should see a wrench icon 🔧 at the bottom right

---

## Use It!

Ask Claude anything:

```
Generate a GitHub Actions workflow for my Python Flask API with Docker and pytest.
```

Done! Claude generates production-ready YAML.

---

## Try These Prompts

| What | Prompt |
|------|--------|
| **GitHub Actions** | Generate a GitHub Actions workflow for a Python Flask API with Docker build and Kubernetes deployment |
| **Jenkins** | Create a Jenkins Declarative Pipeline for a Java app with Maven and ArgoCD deployment |
| **Kubernetes** | Generate Kubernetes manifests (Deployment + Service) for a Node.js app with 3 replicas |
| **SRE** | Generate Prometheus alerts and Grafana dashboard for a payment microservice |
| **Hardening** | Generate Kyverno policies for Kubernetes based on CIS Benchmarks |
| **Dev Container** | Scaffold a dev container for Python + Go + Docker development |

---

## Stuck?

- ❌ **"Wrench icon shows error?"** — Make sure you copied the path correctly in Step 2
- ❌ **"Tool not found?"** — Do `git pull` and `pip install -r mcp_server/requirements.txt` again
- ❌ **"Still stuck?"** — See [Troubleshooting]({{< relref "/docs/ai-integration/mcp-setup#troubleshooting" >}})

---

## Next Steps

- 📖 [Full Getting Started Guide]({{< relref "/docs/getting-started" >}}) — More detailed walkthrough
- 🔧 [MCP Setup & Configuration]({{< relref "/docs/ai-integration/mcp-setup" >}}) — Advanced setup (ChatGPT, Docker, auth)
- 🧠 [Process-First Philosophy]({{< relref "/docs/getting-started/process-first" >}}) — Understand *why* each tool exists
