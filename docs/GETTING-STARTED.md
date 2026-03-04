# Getting Started with DevOps-OS

Welcome! This guide walks you through DevOps-OS from **zero to your first generated pipeline** in under five minutes. No prior DevOps experience is assumed.

---

## What is DevOps-OS?

DevOps-OS is a toolkit that generates production-ready CI/CD pipelines, Kubernetes manifests, and SRE monitoring configs so you can stop writing boilerplate and start shipping.

**Supported platforms:**

| Category | Tools |
|----------|-------|
| CI/CD | GitHub Actions, GitLab CI, Jenkins, CircleCI* |
| GitOps / Deploy | ArgoCD, Flux CD, kubectl, Kustomize |
| Containers | Docker, Helm |
| SRE / Observability | Prometheus alert rules, Grafana dashboards, SLO configs |
| AI Integration | Claude (MCP Server), OpenAI (function calling) |

> \* CircleCI support is planned. See the [roadmap](https://github.com/cloudengine-labs/devops_os/issues).

---

## Prerequisites

| Requirement | Why |
|------------|-----|
| Python 3.10+ | Runs the CLI generators |
| pip | Installs Python dependencies |
| Git | Clones the repo |
| Docker *(optional)* | Builds/runs the dev container |
| VS Code + Dev Containers extension *(optional)* | Opens the pre-configured dev environment |

---

## 1 — Clone and install

```bash
git clone https://github.com/cloudengine-labs/devops_os.git
cd devops_os
```

**Set up a virtual environment** (strongly recommended — keeps DevOps-OS dependencies isolated from your system Python):

```bash
# Create the virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows (cmd)
# .venv\Scripts\Activate.ps1     # Windows (PowerShell)
```

You will see `(.venv)` at the start of your prompt once the venv is active.  
Run the same `activate` command every time you open a new terminal window.

**Install the CLI dependencies:**

```bash
pip install -r cli/requirements.txt
```

> **Do I always need to activate the venv?**  
> Yes — run `source .venv/bin/activate` (or the Windows equivalent) in every new
> terminal session before running `python -m cli.*` commands.  
> You can skip the venv entirely if you are already inside a Docker container or a
> CI/CD runner, where dependency isolation is handled by the environment.

---

## 2 — Pick your CI/CD platform

Choose the tab that matches your CI/CD system.

### GitHub Actions

```bash
# Complete pipeline for a Python + Node.js project
python -m cli.scaffold_gha --name my-app --languages python,javascript --type complete

# With Kubernetes deployment via kubectl
python -m cli.scaffold_gha --name my-app --languages python --kubernetes --k8s-method kubectl

# With Kubernetes deployment via Kustomize
python -m cli.scaffold_gha --name my-app --languages python --kubernetes --k8s-method kustomize
```

**Output:** `.github/workflows/my-app-complete.yml`  
The filename is built as `<name-hyphenated>-<type>.yml` inside the output directory (default: `.github/workflows/`).  
Override the directory with `--output <dir>`.

---

### GitLab CI

```bash
# Complete pipeline for a Python project
python -m cli.scaffold_gitlab --name my-app --languages python --type complete

# With Docker build and Kubernetes deploy via ArgoCD
python -m cli.scaffold_gitlab --name my-app --languages python,go --kubernetes --k8s-method argocd
```

**Output:** `.gitlab-ci.yml` (default)  
Override the file path with `--output <path>` (e.g. `--output ci/my-pipeline.yml`).

---

### Jenkins

```bash
# Complete Declarative Pipeline
python -m cli.scaffold_jenkins --name my-app --languages java --type complete

# Parameterised pipeline (select env at runtime)
python -m cli.scaffold_jenkins --name my-app --languages python --type parameterized
```

**Output:** `Jenkinsfile` (default)  
Override the file path with `--output <path>` (e.g. `--output pipelines/Jenkinsfile`).

---

## 3 — Generate Kubernetes / GitOps configs

```bash
# Plain kubectl Deployment + Service
python kubernetes/k8s-config-generator.py --name my-app --image ghcr.io/myorg/my-app:v1

# ArgoCD Application CR + AppProject
python -m cli.scaffold_argocd --name my-app --repo https://github.com/myorg/my-app.git \
       --namespace production

# Flux Kustomization + GitRepository + Image Automation
python -m cli.scaffold_argocd --name my-app --method flux --repo https://github.com/myorg/my-app.git
```

**Output — ArgoCD:** `argocd/application.yaml` and `argocd/appproject.yaml` (in current directory)  
**Output — Flux:** `flux/git-repository.yaml`, `flux/kustomization.yaml`, `flux/image-update-automation.yaml`  
Override the root directory with `--output-dir <dir>`.

---

## 4 — Generate SRE configs

```bash
# Prometheus alert rules + Grafana dashboard + SLO manifest + Alertmanager config
python -m cli.scaffold_sre --name my-app --team platform

# Latency SLO only
python -m cli.scaffold_sre --name my-app --slo-type latency --slo-target 99.5
```

**Output:** `sre/` directory containing:
- `sre/alert-rules.yaml` — Prometheus PrometheusRule CR
- `sre/grafana-dashboard.json` — Grafana importable dashboard
- `sre/slo.yaml` — Sloth-compatible SLO manifest
- `sre/alertmanager-config.yaml` — Alertmanager routing stub

Override the directory with `--output-dir <dir>`.

---

## 5 — Interactive all-in-one wizard

Not sure which options to pick? Run the interactive wizard and answer the prompts:

```bash
python -m cli.devopsos init           # configure languages and tools
python -m cli.devopsos scaffold gha   # generate GitHub Actions
python -m cli.devopsos scaffold gitlab  # generate GitLab CI
python -m cli.devopsos scaffold jenkins
python -m cli.devopsos scaffold argocd
python -m cli.devopsos scaffold sre
```

---

## 6 — Use with an AI assistant

Install the MCP server and connect it to Claude Desktop or any OpenAI-compatible tool.

Make sure your virtual environment is active (`source .venv/bin/activate`), then:

```bash
pip install -r mcp_server/requirements.txt
python mcp_server/server.py
```

**Claude Desktop** — add to `claude_desktop_config.json`:

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

Then ask Claude:
> *"Generate a complete GitLab CI pipeline for a Python Flask API with Docker build and ArgoCD deployment."*

See [mcp_server/README.md](../mcp_server/README.md) and [skills/README.md](../skills/README.md) for details.

---

## Directory Layout

```
devops_os/
├── cli/                     # Generators (GHA, GitLab CI, Jenkins, ArgoCD, SRE)
├── kubernetes/              # Kubernetes manifest templates and generator
├── mcp_server/              # MCP server for AI assistant integration
├── skills/                  # Claude & OpenAI tool definitions
├── docs/                    # Detailed per-tool documentation
├── .devcontainer/           # VS Code dev container (Dockerfile, config)
└── scripts/examples/        # Complete example pipeline files
```

---

## Common Questions

**Q: Do I need Docker to use the generators?**  
A: No. Docker is only needed if you want to run the dev container. The generators are plain Python scripts.

**Q: Where do the generated files go?**  
A: Each generator has its own default output location:
- `scaffold_gha` → `.github/workflows/<name>-<type>.yml`
- `scaffold_gitlab` → `.gitlab-ci.yml`
- `scaffold_jenkins` → `Jenkinsfile`
- `scaffold_argocd` → `argocd/` (ArgoCD) or `flux/` (Flux CD) directory in the current directory
- `scaffold_sre` → `sre/` directory
- `scaffold_devcontainer` → `.devcontainer/` directory

Use `--output` / `--output-dir` to change the location.
See [CLI-COMMANDS-REFERENCE.md](CLI-COMMANDS-REFERENCE.md) for the full details.

**Q: Can I customise the generated output?**  
A: Yes — use `--custom-values path/to/values.json` to override any default value.

**Q: How do I add the generated workflow to my own project?**  
A: Copy the generated file(s) to your project repository, commit, and push. No further configuration is needed for GitHub Actions or GitLab CI.

---

## Next Steps

| I want to… | Read |
|-----------|------|
| See every option and output path | [CLI-COMMANDS-REFERENCE.md](CLI-COMMANDS-REFERENCE.md) |
| Deep-dive GitHub Actions options | [GITHUB-ACTIONS-README.md](GITHUB-ACTIONS-README.md) |
| Deep-dive GitLab CI options | [GITLAB-CI-README.md](GITLAB-CI-README.md) |
| Deep-dive Jenkins options | [JENKINS-PIPELINE-README.md](JENKINS-PIPELINE-README.md) |
| Learn ArgoCD integration | [ARGOCD-README.md](ARGOCD-README.md) |
| Set up SRE monitoring configs | [SRE-CONFIGURATION-README.md](SRE-CONFIGURATION-README.md) |
| Set up the dev container | [DEVOPS-OS-README.md](DEVOPS-OS-README.md) |
| Use with Claude / ChatGPT | [mcp_server/README.md](../mcp_server/README.md) |
