# Multi-Language Development Container

This development container provides a toolbox-style environment across the major languages supported by DevOps-OS, along with CI/CD and Kubernetes tooling.

## Features

- **Hybrid Runtime Strategy**: official Dev Container Features install mainstream runtimes, while the repo Dockerfile keeps Ubuntu 24.04 plus unsupported language/toolbox extras
- **Multiple Languages**: Python, Java, Node.js/JavaScript/TypeScript, Go, Ruby, PHP, Rust, C#, Kotlin, and C/C++ are available by default
- **CI/CD Tools**: Docker, Terraform, Kubernetes (kubectl), Helm, GitHub Actions
- **Customizable**: `.devcontainer/devcontainer.env.json` remains the single control plane for languages and tools

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
    "node": true,
    "ruby": true,
    "csharp": true,
    "php": true,
    "rust": true,
    "typescript": true,
    "kotlin": true,
    "c": true,
    "cpp": true,
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
- **Java/Kotlin**: JDK, Maven, Gradle, Ant, Kotlin compiler
- **JavaScript/TypeScript**: Node.js, npm, yarn, TypeScript, Jest, ESLint, Prettier
- **Go**: Go compiler, golangci-lint
- **Ruby/PHP/Rust/C#**: runtime/compiler support installed for toolbox workflows
- **C/C++**: build-essential, clang, gdb, cmake

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
2. Change pinned versions for Python, Java, Node, and Go
3. Add additional repo-local tools in `bootstrap-toolbox.sh` or the Dockerfile

## Troubleshooting

- **Docker Access Issues**: Make sure the Docker socket is properly mounted
- **Performance Issues**: Adjust Docker Desktop resource settings
- **Missing Tools**: Check the logs during container build or modify the Dockerfile

## Contributing

Feel free to submit issues or pull requests to improve this development container.
