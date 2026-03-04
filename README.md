# DevOps-OS

> **Automate your entire DevOps lifecycle** — from CI/CD pipelines to Kubernetes deployments and SRE dashboards — using a conversational AI assistant or a single CLI command.

DevOps-OS is an open-source DevOps automation platform that provides:

- 🚀 **CI/CD Generators** — one-command GitHub Actions, **GitLab CI**, & Jenkins pipeline scaffolding
- ☸️ **GitOps Config Generator** — Kubernetes manifests, **ArgoCD** Applications, Flux CD Kustomizations
- 📊 **SRE Config Generator** — Prometheus alert rules, Grafana dashboards, SLO manifests
- 🤖 **MCP Server** — plug DevOps-OS tools into Claude or ChatGPT as native AI skills
- 🛠️ **Dev Container** — pre-configured multi-language environment (Python, Java, Go, JS, ...)

---

## ⚡ Quick Start

### Prerequisites

- Python 3.10+ and `pip`
- Docker (for the dev container)
- VS Code + [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) *(optional)*

### 1 — Clone & install

```bash
git clone https://github.com/cloudengine-labs/devops_os.git
cd devops_os

# Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows (cmd / PowerShell)

pip install -r cli/requirements.txt
```

> **Why a virtual environment?**  A venv keeps the DevOps-OS dependencies isolated from
> your system Python, preventing version conflicts with other projects.  
> Skip this step only if you are already inside a container or a CI environment.

### 2 — Generate a GitHub Actions workflow

```bash
# Complete CI/CD for a Python + JavaScript project
python -m cli.scaffold_gha --name my-app --languages python,javascript --type complete

# With Kubernetes deployment via Kustomize
python -m cli.scaffold_gha --name my-app --languages python --kubernetes --k8s-method kustomize
```

### 3 — Generate a Jenkins pipeline

```bash
python -m cli.scaffold_jenkins --name my-app --languages java --type complete
```

### 3b — Generate a GitLab CI pipeline

```bash
python -m cli.scaffold_gitlab --name my-app --languages python,go --type complete
```

### 3c — Generate ArgoCD / Flux GitOps configs

```bash
python -m cli.scaffold_argocd --name my-app --repo https://github.com/myorg/my-app.git
python -m cli.scaffold_argocd --name my-app --method flux --repo https://github.com/myorg/my-app.git
```

### 3d — Generate SRE configs (Prometheus, Grafana, SLO)

```bash
python -m cli.scaffold_sre --name my-app --team platform --slo-target 99.9
```

### 4 — Generate Kubernetes manifests

```bash
python kubernetes/k8s-config-generator.py --name my-app --image ghcr.io/myorg/my-app:v1
```

### 5 — Interactive wizard (all-in-one)

```bash
python -m cli.devopsos init        # interactive project configurator
python -m cli.devopsos scaffold gha      # scaffold GitHub Actions
python -m cli.devopsos scaffold gitlab   # scaffold GitLab CI
python -m cli.devopsos scaffold jenkins  # scaffold Jenkins
python -m cli.devopsos scaffold argocd   # scaffold ArgoCD / Flux
python -m cli.devopsos scaffold sre      # scaffold SRE configs
```

### 6 — Use with AI (MCP Server)

Make sure your virtual environment is active, then install the MCP dependencies and start the server:

```bash
pip install -r mcp_server/requirements.txt
python mcp_server/server.py
```

Add to your `claude_desktop_config.json` and ask Claude:
> *"Generate a complete CI/CD GitHub Actions workflow for my Python API with
>  Kubernetes deployment using ArgoCD."*

See **[mcp_server/README.md](mcp_server/README.md)** for full setup instructions and
**[skills/README.md](skills/README.md)** for Claude API & OpenAI function-calling examples.

---

## 📁 Repository Structure

| Directory | Contents |
|-----------|----------|
| `.devcontainer/` | Dev container configuration (Dockerfile, devcontainer.json, environment setup scripts) |
| `cli/` | CLI scaffold tools: `scaffold_gha.py`, `scaffold_gitlab.py`, `scaffold_jenkins.py`, `scaffold_argocd.py`, `scaffold_sre.py`, unified `devopsos.py` |
| `kubernetes/` | Kubernetes manifest generator and documentation |
| `mcp_server/` | MCP server exposing DevOps-OS tools to AI assistants (Claude, ChatGPT) |
| `skills/` | Claude & OpenAI tool/function definitions (`claude_tools.json`, `openai_functions.json`) |
| `docs/` | Detailed documentation, guides, and test reports |
| `tests/` | Comprehensive test suite (`test_comprehensive.py`) |
| `go-project/` | Example Go application |
| `scripts/` | Helper scripts |

## Multi-Language Development Container

This development container provides a consistent environment for Java, JavaScript, Go, and Python development, along with CI/CD tools.

### Features

- **Multiple Languages**: Java, JavaScript/TypeScript, Go, and Python with all necessary build tools
- **CI/CD Tools**: Docker, Terraform, Kubernetes (kubectl), Helm, GitHub Actions
- **Customizable**: Configure which languages and tools to include

### Getting Started

#### Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

#### Configuration

1. Customize the environment by editing `.devcontainer/devcontainer.env.json`:

```json
{
  "languages": {
    "python": true,
    "java": true,
    "javascript": true,
    "go": true
  },
  "cicd": {
    "docker": true,
    "terraform": true,
    "kubectl": true,
    "helm": true,
    "github_actions": true
  },
  "kubernetes": {
    "k9s": true,
    "kustomize": true,
    "argocd_cli": true,
    "lens": false,
    "kubeseal": true,
    "flux": true,
    "kind": true,
    "minikube": true,
    "openshift_cli": false
  },
  "versions": {
    "python": "3.11",
    "java": "17",
    "node": "20",
    "go": "1.21",
    "k9s": "0.29.1",
    "argocd": "2.8.4", 
    "flux": "2.1.2",
    "kustomize": "5.2.1"
  }
}
```

2. Run the configuration script:

```bash
cd .devcontainer
python3 configure.py
```

3. Open the project in VS Code and click "Reopen in Container" when prompted

## CI/CD Generator Tools

DevOps-OS includes powerful generators for creating CI/CD configurations:

1. **GitHub Actions Generator**: `cli/scaffold_gha.py`
2. **GitLab CI Generator**: `cli/scaffold_gitlab.py`
3. **Jenkins Pipeline Generator**: `cli/scaffold_jenkins.py`
4. **ArgoCD / Flux GitOps Generator**: `cli/scaffold_argocd.py`
5. **SRE Config Generator**: `cli/scaffold_sre.py`
6. **Kubernetes Config Generator**: `kubernetes/k8s-config-generator.py`
7. **Unified CLI**: `cli/devopsos.py`

### Quick Start

To quickly generate both GitHub Actions and Jenkins pipelines:

```bash
python -m cli.scaffold_gha --name "My Project" --languages python,javascript --kubernetes
python -m cli.scaffold_jenkins --name "My Project" --languages python,javascript
```

For more examples and detailed usage, see the [DevOps-OS Quick Start Guide](docs/DEVOPS-OS-QUICKSTART.md).

## What's Included

### Languages and Tools

- **Python**: Python interpreter, pip, pytest, black, flake8, mypy
- **Java**: JDK, Maven, Gradle
- **JavaScript/TypeScript**: Node.js, npm, yarn, TypeScript, Jest, ESLint, Prettier
- **Go**: Go compiler, golangci-lint

### CI/CD Tools

- **Docker**: Docker CLI, Docker Compose
- **Infrastructure as Code**: Terraform
- **Kubernetes**: kubectl, Helm
- **Workflows**: GitHub Actions runner

### Kubernetes Tools

- **Cluster Management**: K9s terminal UI, KinD, Minikube
- **Application Deployment**: Kustomize, Helm
- **GitOps**: ArgoCD CLI, Flux CD
- **Secret Management**: Kubeseal for Sealed Secrets
- **Observability**: Integrated with Prometheus and Grafana
- **Configuration Generator**: Built-in tool to generate Kubernetes manifests for kubectl, Kustomize, ArgoCD, and Flux

## 🧪 Testing

The test suite covers all CLI scaffold commands, the MCP server, and AI skill definitions.
A dedicated **Sanity Tests** GitHub Actions workflow (`.github/workflows/sanity.yml`) runs every scenario automatically on every push and pull request — no real infrastructure required; all tests use in-memory mock data.

```bash
pip install -r cli/requirements.txt -r mcp_server/requirements.txt pytest pytest-html
python -m pytest cli/test_cli.py mcp_server/test_server.py tests/test_comprehensive.py -v
```

**Latest results:** 162 passed · 3 xfailed (known bugs tracked for future fixes) · 0 failed

| Test report | Description |
|-------------|-------------|
| [**Detailed Test Report**](docs/TEST_REPORT.md) | Full test results with CLI output samples for every scaffold command |
| [**Interactive HTML Report**](docs/test-reports/test-report.html) | Self-contained pytest HTML report (download and open in browser) |
| [**CLI Output Examples**](docs/test-reports/cli-output-examples.md) | Real captured output for all scaffold sub-commands |
| [**Sanity Workflow**](.github/workflows/sanity.yml) | GitHub Actions workflow that runs all scenario tests on every push |

---

## 📚 Available Documentation

| Guide | Description |
|-------|-------------|
| [**Getting Started**](docs/GETTING-STARTED.md) | Easy step-by-step guide — start here! |
| [Dev Container Setup](docs/DEVOPS-OS-README.md) | How to set up and customize the DevOps-OS development container |
| [Quick Start Reference](docs/DEVOPS-OS-QUICKSTART.md) | Essential CLI commands for all functionality |
| [GitHub Actions Generator](docs/GITHUB-ACTIONS-README.md) | How to generate and customize GitHub Actions workflows |
| [GitLab CI Generator](docs/GITLAB-CI-README.md) | How to generate and customize GitLab CI pipelines |
| [Jenkins Pipeline Generator](docs/JENKINS-PIPELINE-README.md) | How to generate and customize Jenkins pipelines |
| [ArgoCD / Flux GitOps](docs/ARGOCD-README.md) | Generate ArgoCD Applications and Flux Kustomizations |
| [SRE Configuration](docs/SRE-CONFIGURATION-README.md) | Prometheus rules, Grafana dashboards, SLO manifests |
| [Kubernetes Deployments](docs/KUBERNETES-DEPLOYMENT-README.md) | How to generate and manage Kubernetes deployment configurations |
| [Kubernetes Capabilities](docs/kubernetes-capabilities.md) | Detailed guide for all Kubernetes tooling |
| [CI/CD Tech Stack Guide](docs/CICD-TECH-STACK-README.md) | Implementing CI/CD pipelines for specific technology stacks |
| [CI/CD Generators Usage](docs/CI-CD-GENERATORS-USAGE.md) | Detailed options and examples for the CI/CD generators |
| [MCP Server](mcp_server/README.md) | Connect DevOps-OS tools to Claude or ChatGPT |
| [AI Skills](skills/README.md) | Use DevOps-OS with the Anthropic API or OpenAI function calling |

## Customization

You can:

1. Disable languages or tools you don't need
2. Change versions of languages
3. Add additional tools by editing the Dockerfile

## Troubleshooting

- **Docker Access Issues**: Make sure the Docker socket is properly mounted
- **Performance Issues**: Adjust Docker Desktop resource settings
- **Missing Tools**: Check the logs during container build or modify the Dockerfile

## Getting Help

If you need additional help or have questions about DevOps-OS, please refer to the specific guides or open an issue in the repository.

## Contributing

Contributions to DevOps-OS are welcome! Please see the contributing guidelines in the repository for more information.