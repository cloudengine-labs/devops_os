# DevOps-OS Documentation

Welcome to the DevOps-OS documentation! This set of guides will help you use and customize the DevOps-OS development container and its CI/CD generators.

## Available Guides

| Guide | Description |
|-------|-------------|
| [**CLI Commands Reference**](docs/CLI-COMMANDS-REFERENCE.md) | **Complete reference** — every option, input file, and output location for all CLI commands |
| [Getting Started](docs/GETTING-STARTED.md) | First pipeline in 5 minutes |
| [Quick Start Guide](docs/DEVOPS-OS-QUICKSTART.md) | Essential CLI commands for all functionality |
| [Process-First Philosophy](docs/PROCESS-FIRST.md) | What Process-First means, how it maps to DevOps-OS, and AI learning tips for beginners |
| [GitHub Actions Generator](docs/GITHUB-ACTIONS-README.md) | Generate and customize GitHub Actions workflows |
| [GitLab CI Generator](docs/GITLAB-CI-README.md) | Generate and customize GitLab CI pipelines |
| [Jenkins Pipeline Generator](docs/JENKINS-PIPELINE-README.md) | Generate and customize Jenkins pipelines |
| [ArgoCD / Flux CD Generator](docs/ARGOCD-README.md) | Generate ArgoCD and Flux CD GitOps configs |
| [SRE Configuration Generator](docs/SRE-CONFIGURATION-README.md) | Generate Prometheus, Grafana, SLO, and Alertmanager configs |
| [Kubernetes Deployment](docs/KUBERNETES-DEPLOYMENT-README.md) | Generate and manage Kubernetes deployment configurations |
| [CI/CD for Technology Stacks](docs/CICD-TECH-STACK-README.md) | Implement CI/CD for specific technology stacks |
| [DevOps-OS Dev Container](docs/DEVOPS-OS-README.md) | Set up and customize the dev container |

## CLI Generator Quick Reference

| Command | Default output |
|---------|---------------|
| `python -m cli.scaffold_gha` | `.github/workflows/<name>-<type>.yml` |
| `python -m cli.scaffold_gitlab` | `.gitlab-ci.yml` |
| `python -m cli.scaffold_jenkins` | `Jenkinsfile` |
| `python -m cli.scaffold_argocd` | `argocd/` directory |
| `python -m cli.scaffold_argocd --method flux` | `flux/` directory |
| `python -m cli.scaffold_sre` | `sre/` directory |
| `python -m cli.scaffold_devcontainer` | `.devcontainer/` directory |

See [CLI Commands Reference](docs/CLI-COMMANDS-REFERENCE.md) for the full option tables, input files, and output path details.

## Quick Start

```bash
git clone https://github.com/cloudengine-labs/devops_os.git
cd devops_os
pip install -r cli/requirements.txt

# GitHub Actions complete pipeline
python -m cli.scaffold_gha --name my-app --languages python,javascript --type complete
# Output: .github/workflows/my-app-complete.yml

# GitLab CI pipeline
python -m cli.scaffold_gitlab --name my-app --languages python
# Output: .gitlab-ci.yml

# SRE monitoring stack
python -m cli.scaffold_sre --name my-app --team platform
# Output: sre/ directory
```

For more examples and detailed usage, see the [Getting Started guide](docs/GETTING-STARTED.md).

## Features

- **Multi-language Support**: Python, Java, JavaScript/TypeScript, Go
- **CI/CD Configuration**: GitHub Actions, GitLab CI, Jenkins
- **GitOps**: ArgoCD, Flux CD
- **SRE Observability**: Prometheus alert rules, Grafana dashboards, SLO manifests, Alertmanager configs
- **Kubernetes Deployment**: kubectl, kustomize, ArgoCD, Flux
- **Customization**: Environment variables, command-line options, custom JSON configurations
- **AI Integration**: Claude MCP server, OpenAI function calling

## Getting Help

If you need additional help or have questions about DevOps-OS, please refer to the specific guides or open an issue in the repository.

## Contributing

Contributions to DevOps-OS are welcome! Please see the contributing guidelines in the repository for more information.
