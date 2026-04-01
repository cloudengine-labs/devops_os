# DevOps-OS MCP Server

The DevOps-OS **Model Context Protocol (MCP) server** turns any MCP-compatible AI assistant into a DevOps automation engine. Ask it in plain English and it generates production-ready CI/CD pipelines, Kubernetes manifests, SRE dashboards, and more — no YAML knowledge required.

## Available Tools

| Tool | What it generates |
|------|-------------------|
| `generate_github_actions_workflow` | GitHub Actions CI/CD workflow YAML |
| `generate_jenkins_pipeline` | Jenkins Declarative Pipeline (Jenkinsfile) |
| `generate_gitlab_ci_pipeline` | GitLab CI/CD pipeline (`.gitlab-ci.yml`) |
| `generate_k8s_config` | Kubernetes Deployment + Service manifests |
| `generate_argocd_config` | Argo CD Application / AppProject or Flux CRs |
| `generate_sre_configs` | Prometheus alert rules, Grafana dashboards, SLO manifests |
| `scaffold_devcontainer` | `devcontainer.json` + `devcontainer.env.json` |
| `generate_unittest_config` | Unit test configs for pytest, Jest, Vitest, Mocha, Go |

---

## Quick Start — Which Method Is Right for You?

| Your situation | Recommended method |
|---------------|--------------------|
| Use **Claude Code** (CLI) | [Automated setup script](#-option-a-automated-setup-claude-code-cli) |
| Use **Claude Desktop** (GUI app) | [Claude Desktop config](#-option-b-claude-desktop-app) |
| Use **Cursor** IDE | [Cursor MCP config](#-option-c-cursor-ide) |
| Use **VS Code** with GitHub Copilot | [VS Code MCP config](#-option-d-vs-code--github-copilot) |
| Use **Windsurf** | [Windsurf config](#-option-e-windsurf) |
| Use **Zed** editor | [Zed config](#-option-f-zed-editor) |
| Already cloned the repo | Add `--local` to any script below |

---

## Step 0 — Prerequisites (all methods)

| Requirement | Minimum version | Check |
|-------------|----------------|-------|
| Python | 3.10+ | `python3 --version` |
| pip | any recent | `pip --version` |
| git | any recent | `git --version` |

You do **not** need Docker, Kubernetes, or any cloud accounts.

---

## Option A — Automated Setup (Claude Code CLI)

The fastest path. One command clones the repo, installs dependencies, and registers the server.

```bash
# Download and run the setup script
curl -fsSL https://raw.githubusercontent.com/cloudengine-labs/devops_os/main/mcp_server/setup_devops_os_mcp.sh | bash
```

**Already cloned the repo?** Run the script in local mode instead of downloading it:

```bash
# From inside your devops_os clone:
bash mcp_server/setup_devops_os_mcp.sh --local
```

**Custom install directory:**

```bash
INSTALL_DIR=~/projects/devops_os bash mcp_server/setup_devops_os_mcp.sh
```

**Verify it worked:**

```bash
claude mcp list          # should show "devops-os"
claude mcp get devops-os # shows the full config
```

**Test it:**

```
claude
> Generate a GitHub Actions workflow for a Python + Node.js app with Docker build and Kubernetes deployment
```

---

## Option B — Claude Desktop App

1. **Clone and install:**

   ```bash
   git clone https://github.com/cloudengine-labs/devops_os.git ~/devops_os
   cd ~/devops_os
   python3 -m venv .venv
   source .venv/bin/activate          # macOS/Linux
   # .venv\Scripts\activate           # Windows
   pip install -r mcp_server/requirements.txt
   ```

2. **Find your config file:**

   | OS | Path |
   |----|------|
   | macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
   | Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
   | Linux | `~/.config/Claude/claude_desktop_config.json` |

3. **Add this block** (replace `/YOUR/HOME` with the actual path from step 1):

   ```json
   {
     "mcpServers": {
       "devops-os": {
         "command": "/YOUR/HOME/devops_os/.venv/bin/python",
         "args": ["-m", "mcp_server.server"],
         "cwd": "/YOUR/HOME/devops_os"
       }
     }
   }
   ```

   > **Tip:** Use the full venv path, not just `python`, so the correct dependencies are used.

4. **Restart Claude Desktop**, then ask:
   > *"Generate a Jenkins pipeline for a Java Spring Boot app that builds a Docker image and deploys to Kubernetes."*

---

## Option C — Cursor IDE

1. **Clone and install** (same as step 1 above).

2. **Create `.cursor/mcp.json`** in your project root (or copy from the devops_os repo):

   ```json
   {
     "mcpServers": {
       "devops-os": {
         "command": "/YOUR/HOME/devops_os/.venv/bin/python",
         "args": ["-m", "mcp_server.server"],
         "cwd": "/YOUR/HOME/devops_os"
       }
     }
   }
   ```

3. **Reload Cursor** (Cmd+Shift+P → "Developer: Reload Window").

4. Open the Cursor chat panel and ask:
   > *"Scaffold a devcontainer for a Go + Python project with Terraform and kubectl."*

> **Project-level config:** The `.cursor/mcp.json` in this repo is pre-configured and works if you clone devops_os and open it directly in Cursor.

---

## Option D — VS Code + GitHub Copilot

VS Code 1.99+ supports MCP servers in GitHub Copilot Agent mode.

1. **Clone and install** (same as step 1 in Option B).

2. **Create `.vscode/mcp.json`** in your workspace:

   ```json
   {
     "servers": {
       "devops-os": {
         "type": "stdio",
         "command": "/YOUR/HOME/devops_os/.venv/bin/python",
         "args": ["-m", "mcp_server.server"],
         "cwd": "/YOUR/HOME/devops_os"
       }
     }
   }
   ```

3. Open **GitHub Copilot Chat** in Agent mode and ask:
   > *"Use devops-os to generate Kubernetes manifests for my app."*

> **Note:** VS Code MCP support requires GitHub Copilot and VS Code 1.99 or later.

---

## Option E — Windsurf

1. **Clone and install** (same as step 1 in Option B).

2. Open Windsurf settings: **Windsurf → Preferences → Cascade → MCP Servers**.

3. Add this configuration:

   ```json
   {
     "mcpServers": {
       "devops-os": {
         "command": "/YOUR/HOME/devops_os/.venv/bin/python",
         "args": ["-m", "mcp_server.server"],
         "cwd": "/YOUR/HOME/devops_os"
       }
     }
   }
   ```

   Alternatively, edit `~/.codeium/windsurf/mcp_config.json` directly.

4. Restart Windsurf and ask Cascade:
   > *"Generate SRE configs for my payment-service with a 99.9% SLO target."*

---

## Option F — Zed Editor

1. **Clone and install** (same as step 1 in Option B).

2. Open `~/.config/zed/settings.json` and add:

   ```json
   {
     "context_servers": {
       "devops-os": {
         "command": {
           "path": "/YOUR/HOME/devops_os/.venv/bin/python",
           "args": ["-m", "mcp_server.server"],
           "env": {
             "PYTHONPATH": "/YOUR/HOME/devops_os"
           }
         }
       }
     }
   }
   ```

3. Restart Zed and use the Assistant panel to ask:
   > *"Create a GitLab CI pipeline for a Python microservice."*

---

## Example Prompts

Once connected, try these prompts in any AI tool:

```
Generate a complete GitHub Actions CI/CD workflow for a Python + Node.js project
with Docker build and Kubernetes deployment using Kustomize.

Create a Jenkins pipeline for a Java Spring Boot service with Maven build,
Docker image push to ECR, and ArgoCD deployment.

Generate Kubernetes manifests for 'api-service' using image
'ghcr.io/myorg/api-service:v1.2.3' with 3 replicas on port 8080.

Scaffold a devcontainer for a Go + Python project with Terraform, kubectl, and k9s.

Generate SRE configs (Prometheus alerts, Grafana dashboard, SLO manifest)
for 'payment-service' owned by team 'platform' with 99.9% availability target.

Create unit test configuration for a Python project named 'data-pipeline'.

Generate a GitLab CI pipeline with Docker build and Kubernetes deployment stages
for a Python microservice.
```

---

## Architecture

```
AI Assistant (Claude / Cursor / VS Code / Windsurf / Zed)
        │  MCP stdio request
        ▼
DevOps-OS MCP Server  (mcp_server/server.py)
        │  calls Python scaffold functions
        ▼
DevOps-OS CLI modules
  ├─ cli/scaffold_gha.py         → GitHub Actions YAML
  ├─ cli/scaffold_jenkins.py     → Jenkinsfile
  ├─ cli/scaffold_gitlab.py      → .gitlab-ci.yml
  ├─ cli/scaffold_argocd.py      → ArgoCD / Flux manifests
  ├─ cli/scaffold_sre.py         → Prometheus / Grafana / SLO
  ├─ cli/scaffold_devcontainer.py→ devcontainer.json
  ├─ cli/scaffold_unittest.py    → pytest / Jest / Go test
  └─ kubernetes/k8s-config-generator.py → K8s manifests
```

---

## Troubleshooting

### "Module not found" or "No module named mcp"
The venv is missing or incomplete. Re-run:
```bash
/path/to/devops_os/.venv/bin/pip install -r /path/to/devops_os/mcp_server/requirements.txt
```

### "command not found: claude" (during setup)
Install Claude Code first: [claude.ai/code](https://claude.ai/code)

### Server shows in `claude mcp list` but tools don't appear
Check that `PYTHONPATH` points to the repo root:
```bash
claude mcp get devops-os   # inspect the registered command
```
Re-register manually if needed:
```bash
claude mcp remove devops-os
claude mcp add --transport stdio devops-os --scope user \
  -- /path/to/devops_os/.venv/bin/python -m mcp_server.server \
  --env PYTHONPATH=/path/to/devops_os
```

### Tools appear but return errors
Run the test suite to verify the installation:
```bash
cd /path/to/devops_os
.venv/bin/python -m pytest mcp_server/test_server.py -v
```

### Windows path format
On Windows, use forward slashes or escaped backslashes in JSON config:
```json
"command": "C:/Users/you/devops_os/.venv/Scripts/python.exe"
```

---

## Using with Claude API / OpenAI function calling

See [`../skills/README.md`](../skills/README.md) for examples of calling the DevOps-OS tools directly from the Anthropic or OpenAI Python SDKs (no MCP client required).
