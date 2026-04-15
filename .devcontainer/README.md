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

#### Option A — Use the CLI (recommended)

Generate `devcontainer.json` and `devcontainer.env.json` with a single command:

```bash
# From the repository root
python -m cli.scaffold_devcontainer \
  --languages python,java,go \
  --cicd-tools docker,terraform,kubectl,helm \
  --kubernetes-tools k9s,kustomize,argocd_cli,flux \
  --devops-tools prometheus,grafana

# Or via the unified CLI
python -m cli.devopsos scaffold devcontainer
```

Run `python -m cli.scaffold_devcontainer --help` to see all available options including version overrides (`--python-version`, `--go-version`, etc.).

#### Option B — Edit JSON manually

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
    "python": "3.12",
    "java": "21",
    "node": "22",
    "go": "1.25.0",
    "k9s": "0.50.16",
    "argocd": "3.3.6",
    "flux": "2.8.5",
    "kustomize": "5.8.0"
  }
}
```

2. Run the configuration script:

```bash
cd .devcontainer
python3 configure.py
```

#### Open in VS Code

After configuring (via either option), open the project in VS Code and click "Reopen in Container" when prompted.

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
