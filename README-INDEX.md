# DevOps-OS Documentation

Welcome to the DevOps-OS documentation! This set of guides will help you use and customize the DevOps-OS development container and its CI/CD generators.

## Available Guides

| Guide | Description |
|-------|-------------|
| [Creating DevOps-OS Using Dev Container](.devcontainer/DEVOPS-OS-README.md) | How to set up and customize the DevOps-OS development container |
| [DevOps-OS Quick Start Guide](.devcontainer/DEVOPS-OS-QUICKSTART.md) | Essential CLI commands for all functionality in the project |
| [Creating Customized GitHub Actions Templates](.devcontainer/GITHUB-ACTIONS-README.md) | How to generate and customize GitHub Actions workflows |
| [Creating Customized Jenkins Templates](.devcontainer/JENKINS-PIPELINE-README.md) | How to generate and customize Jenkins pipelines |
| [Creating Kubernetes Deployments](.devcontainer/KUBERNETES-DEPLOYMENT-README.md) | How to generate and manage Kubernetes deployment configurations |
| [Implementing CI/CD for Technology Stacks](.devcontainer/CICD-TECH-STACK-README.md) | How to implement CI/CD pipelines for specific technology stacks |
| [CI/CD Generators Usage Guide](.devcontainer/CI-CD-GENERATORS-USAGE.md) | Detailed options and examples for the CI/CD generators |

## CI/CD Generator Tools

DevOps-OS includes powerful generators for creating CI/CD configurations:

1. **GitHub Actions Generator**: `github-actions-generator-improved.py`
2. **Jenkins Pipeline Generator**: `jenkins-pipeline-generator-improved.py`
3. **Kubernetes Config Generator**: `k8s-config-generator.py`
4. **Unified CI/CD Generator**: `generate-cicd.py`

## Quick Start

To quickly generate both GitHub Actions and Jenkins pipelines:

```bash
.devcontainer/generate-cicd.py --name "My Project" --languages python,javascript --kubernetes
```

For more examples and detailed usage, see the [DevOps-OS Quick Start Guide](DEVOPS-OS-QUICKSTART.md).

## Features

- **Multi-language Support**: Python, Java, JavaScript/TypeScript, Go
- **CI/CD Configuration**: GitHub Actions, Jenkins
- **Kubernetes Deployment**: kubectl, kustomize, ArgoCD, Flux
- **Customization**: Environment variables, command-line options, custom JSON configurations
- **Integration**: Container registries, credentials management, external services

## Getting Help

If you need additional help or have questions about DevOps-OS, please refer to the specific guides or open an issue in the repository.

## Contributing

Contributions to DevOps-OS are welcome! Please see the contributing guidelines in the repository for more information.
