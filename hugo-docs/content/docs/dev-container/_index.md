---
title: "Dev Container"
weight: 60
---

# Dev Container Setup

DevOps-OS provides a pre-configured VS Code Dev Container that gives you a consistent, multi-language development environment with all CI/CD tools included. Configure programming language and tool versions via environment variables with security-aware recommendations.

---

## Quick Start

```bash
python -m devops_os.core.scaffold_devcontainer \
  --languages python,go \
  --cicd-tools docker,kubectl,helm \
  --kubernetes-tools k9s,argocd_cli,flux
# Output: .devcontainer/devcontainer.json
#         .devcontainer/devcontainer.env.json
```

Then open VS Code and run **"Dev Containers: Reopen in Container"** from the Command Palette.

Run `python -m devops_os.core.scaffold_devcontainer --help` to see all available options.

---

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--languages LANGS` | `python` | Comma-separated languages: `python`, `java`, `node`, `ruby`, `csharp`, `php`, `rust`, `typescript`, `kotlin`, `c`, `cpp`, `javascript`, `go` |
| `--cicd-tools TOOLS` | `docker,github_actions` | CI/CD tools: `docker`, `terraform`, `kubectl`, `helm`, `github_actions`, `jenkins` |
| `--kubernetes-tools TOOLS` | _(none)_ | K8s tools: `k9s`, `kustomize`, `argocd_cli`, `lens`, `kubeseal`, `flux`, `kind`, `minikube`, `openshift_cli` |
| `--build-tools TOOLS` | _(none)_ | Build tools: `gradle`, `maven`, `ant`, `make`, `cmake` |
| `--code-analysis TOOLS` | _(none)_ | Analysis tools: `sonarqube`, `checkstyle`, `pmd`, `eslint`, `pylint` |
| `--devops-tools TOOLS` | _(none)_ | DevOps tools: `nexus`, `prometheus`, `grafana`, `elk`, `jenkins` |
| `--python-version VER` | `3.12` | Python version (via `DEVOPS_OS_VERSION_PYTHON` env var) |
| `--java-version VER` | `21` | Java JDK version (via `DEVOPS_OS_VERSION_JAVA` env var) |
| `--node-version VER` | `22` | Node.js version (via `DEVOPS_OS_VERSION_NODE` env var) |
| `--go-version VER` | `1.25.0` | Go version (via `DEVOPS_OS_VERSION_GO` env var) |
| `--output-dir DIR` | `.` | Root directory; files written to `<dir>/.devcontainer/` |

All options can be set via environment variables prefixed `DEVOPS_OS_DEVCONTAINER_` or `DEVOPS_OS_VERSION_` for version configuration.

---
## Generated Files

```
.devcontainer/
├── devcontainer.json     VS Code dev container configuration
└── devcontainer.env.json Tool / language selection & versions
```

**`devcontainer.json`** contains: build args, VS Code extensions, forwarded ports, and post-create commands.

**`devcontainer.env.json`** controls which languages and tools are enabled — it drives the Dockerfile build args.

---

## Full-stack Example

```bash
python -m devops_os.core.scaffold_devcontainer \
  --languages python,java,javascript \
  --cicd-tools docker,terraform,kubectl,helm \
  --kubernetes-tools k9s,kustomize,argocd_cli,flux \
  --devops-tools prometheus,grafana \
  --python-version 3.12
```

This generates a dev container with:
- Python 3.12, Java 21, Node.js 22
- Docker, Terraform, kubectl, Helm
- K9s, Kustomize, ArgoCD CLI, Flux CD
- Prometheus (port 9090) and Grafana (port 3000) forwarded

---

## Version Management

All tool and language versions are managed via environment variables with security-aware recommendations. Learn more in the [Version Management Guide](version-management/).

### Quick Version Update

Set versions via environment variables:

```bash
export DEVOPS_OS_VERSION_PYTHON=3.13
export DEVOPS_OS_VERSION_GO=1.25.0
export DEVOPS_OS_VERSION_NODE=22
```

Or use the `.env` file approach:

```env
# .env
DEVOPS_OS_VERSION_PYTHON=3.12
DEVOPS_OS_VERSION_JAVA=21
DEVOPS_OS_VERSION_GO=1.25.0
DEVOPS_OS_VERSION_NODE=22
DEVOPS_OS_VERSION_DOCKER=27.0.0
```

### Check for Security Updates

Use MCP tools to check for security issues and get recommendations:

```bash
check_security_issues(tools="python,java,docker")
suggest_versions(prefer_lts=true)
```

---

## Manual Configuration

Edit the generated `.devcontainer/devcontainer.env.json` directly:

```json
{
  "languages": {
    "python": true,
    "java": true,
    "javascript": true,
    "go": false
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
    "flux": true
  },
  "versions": {
    "python": "3.12",
    "java": "21",
    "node": "22",
    "go": "1.25.0"
  }
}
```

After editing, rebuild the container: **"Dev Containers: Rebuild Container"**.

---

## Using with Existing Projects

Copy the generated `.devcontainer/` directory to your project:

```bash
# In the devops_os repo:
python -m devops_os.core.scaffold_devcontainer \
  --languages python,go \
  --output-dir /path/to/my-project

# Open your project in VS Code and reopen in container
cd /path/to/my-project
code .
```

---

## Included Tools (by category)

| Category | Tools |
|----------|-------|
| **Languages** | Python · Java · Node.js · Go · Ruby · C/C++ · Rust |
| **Containers** | Docker CLI · Docker Compose |
| **IaC** | Terraform · AWS CLI · Azure CLI |
| **Kubernetes** | kubectl · Helm · K9s · Kustomize · KinD · Minikube |
| **GitOps** | ArgoCD CLI · Flux CD |
| **Observability** | Prometheus · Grafana · ELK Stack |
| **Build** | Maven · Gradle · npm · pip · Go tools |
| **Code Quality** | SonarQube · ESLint · Pylint · CheckStyle |

---

## Troubleshooting

### Container fails to build

1. Check Docker is running
2. Ensure sufficient disk space (>5 GB free)
3. Review Docker build logs for specific errors

### Tool not available after build

1. Check the tool is `true` in `devcontainer.env.json`
2. Rebuild the container: **"Dev Containers: Rebuild Container"**
3. Regenerate the devcontainer files with `python -m devops_os.core.scaffold_devcontainer ...` if you changed the selected tools

### Version environment variables not taking effect

1. Export variables before building: `export DEVOPS_OS_VERSION_PYTHON=3.13`
2. Source your `.env` file: `source .env`
3. Rebuild the container to apply new versions
4. Check [Version Management](version-management/) guide for detailed configuration options

---

## Related Documentation

- [Version Management](version-management/) - Manage tool versions and security updates
- [MCP Setup](mcp-setup/) - Configure MCP tools for dev containers
- [Language Guides](language-guides/) - Language-specific setup and examples
