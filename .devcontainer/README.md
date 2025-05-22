# Multi-Language Development Container

This development container provides a consistent environment for Java, JavaScript, Go, and Python development, along with CI/CD tools.

## Features

- **Multiple Languages**: Java, JavaScript/TypeScript, Go, and Python with all necessary build tools
- **CI/CD Tools**: Docker, Terraform, Kubernetes (kubectl), Helm, GitHub Actions
- **Customizable**: Configure which languages and tools to include

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Configuration

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

For detailed information on using the Kubernetes capabilities, see [kubernetes-capabilities.md](kubernetes-capabilities.md).

## Customization

You can:

1. Disable languages or tools you don't need
2. Change versions of languages
3. Add additional tools by editing the Dockerfile

## Troubleshooting

- **Docker Access Issues**: Make sure the Docker socket is properly mounted
- **Performance Issues**: Adjust Docker Desktop resource settings
- **Missing Tools**: Check the logs during container build or modify the Dockerfile

## Contributing

Feel free to submit issues or pull requests to improve this development container.
