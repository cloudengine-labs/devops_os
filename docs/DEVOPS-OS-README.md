# Creating DevOps-OS Using Dev Container

This guide explains how to set up and use the DevOps-OS development container, a comprehensive multi-language development environment with integrated CI/CD capabilities.

## What is DevOps-OS?

DevOps-OS is a development container that provides a pre-configured environment for multi-language development and DevOps operations. It includes support for:

- Multiple programming languages (Python, Java, JavaScript/TypeScript, Go)
- CI/CD tools and pipelines
- Kubernetes and container orchestration
- Infrastructure as Code (IaC)
- Testing and code quality tools

## Prerequisites

Before getting started, ensure you have the following installed:

- [Docker](https://www.docker.com/products/docker-desktop) (Latest version)
- [Visual Studio Code](https://code.visualstudio.com/) (Latest version)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) for VS Code

## Setting Up DevOps-OS

### Option 1: Use with an Existing Project

1. Clone your project repository:
   ```bash
   git clone https://github.com/yourusername/your-project.git
   cd your-project
   ```

2. Copy the DevOps-OS .devcontainer files to your project:
   ```bash
   mkdir -p .devcontainer
   cp -r /path/to/devops-os/.devcontainer/* ./.devcontainer/
   ```

3. Open the project in VS Code and click "Reopen in Container" when prompted, or run the "Dev Containers: Reopen in Container" command from the Command Palette.

### Option 2: Create a New DevOps-OS Container from Scratch

1. Create a new directory for your project:
   ```bash
   mkdir my-devops-project
   cd my-devops-project
   ```

2. Create a `.devcontainer` directory:
   ```bash
   mkdir -p .devcontainer
   ```

3. Create the following files in the `.devcontainer` directory:

   **devcontainer.json**:
   ```json
   {
     "name": "DevOps-OS",
     "build": {
       "dockerfile": "Dockerfile",
       "context": ".",
       "args": {}
     },
     "runArgs": [
       "--init",
       "--privileged"
     ],
     "overrideCommand": false,
     "customizations": {
       "vscode": {
         "extensions": [
           "ms-python.python",
           "ms-azuretools.vscode-docker",
           "redhat.vscode-yaml",
           "ms-kubernetes-tools.vscode-kubernetes-tools",
           "redhat.java",
           "vscjava.vscode-java-debug",
           "dbaeumer.vscode-eslint",
           "golang.go",
           "hashicorp.terraform"
         ]
       }
     },
     "mounts": [
       "source=/var/run/docker.sock,target=/var/run/docker.sock,type=bind"
     ],
     "postCreateCommand": "python3 .devcontainer/configure.py"
   }
   ```

   **devcontainer.env.json**:
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
       "go": "1.21"
     }
   }
   ```

4. Copy the Dockerfile from this repository to your `.devcontainer` directory.

5. Open the project in VS Code and click "Reopen in Container" when prompted, or run the "Dev Containers: Reopen in Container" command from the Command Palette.

## Customizing DevOps-OS

The DevOps-OS container is highly customizable through the `devcontainer.env.json` file. This file lets you specify which languages, tools, and features to include in your environment.

### Language Configuration

Enable or disable languages by setting their value to `true` or `false`:

```json
"languages": {
  "python": true,
  "java": true,
  "javascript": true,
  "go": false
}
```

### Tool Configuration

Enable or disable various CI/CD and DevOps tools:

```json
"cicd": {
  "docker": true,
  "terraform": true,
  "kubectl": true,
  "helm": true,
  "github_actions": true
}
```

### Kubernetes Tools

Select which Kubernetes tools to install:

```json
"kubernetes": {
  "k9s": true,
  "kustomize": true,
  "argocd_cli": true,
  "lens": false,
  "kubeseal": true,
  "flux": true
}
```

### Version Selection

Specify the versions of languages and tools to use:

```json
"versions": {
  "python": "3.11",
  "java": "17",
  "node": "20",
  "go": "1.21"
}
```

## Using DevOps-OS Container

Once the container is built and running, you can:

1. Use the integrated terminal in VS Code to run commands with all tools pre-installed
2. Develop in any of the enabled languages with full IDE support
3. Build and run containers using Docker
4. Deploy to Kubernetes clusters
5. Set up automated CI/CD pipelines (see companion README files)

## Included Tools

Depending on your configuration, DevOps-OS includes:

- **Languages**: Python, Java, JavaScript/TypeScript, Go
- **Build Tools**: Maven, Gradle, npm, pip, Go tools
- **Container Tools**: Docker, Docker Compose
- **Kubernetes**: kubectl, helm, k9s, kustomize, ArgoCD CLI, Flux
- **IaC**: Terraform, AWS CLI, Azure CLI
- **CI/CD**: GitHub Actions configs, Jenkins pipelines
- **Code Quality**: SonarQube, ESLint, Pylint, CheckStyle

## Troubleshooting

### Container Build Issues

If the container fails to build:

1. Check Docker is running
2. Ensure you have sufficient disk space
3. Review Docker build logs for specific errors

### Tool Configuration Issues

If a specific tool isn't working properly:

1. Check the tool is enabled in `devcontainer.env.json`
2. Run the configuration script again: `python3 .devcontainer/configure.py`
3. Check if the tool requires additional configuration

## Next Steps

After setting up DevOps-OS, consider exploring:

1. [Creating Customized GitHub Actions Templates](./GITHUB-ACTIONS-README.md)
2. [Creating Customized Jenkins Templates](./JENKINS-PIPELINE-README.md)
3. [Creating Kubernetes Deployments](./KUBERNETES-DEPLOYMENT-README.md)
4. [Implementing CI/CD Pipelines for Technology Stacks](./CICD-TECH-STACK-README.md)
