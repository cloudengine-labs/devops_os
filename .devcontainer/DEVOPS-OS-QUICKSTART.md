# DevOps-OS Quick Start Guide

This guide provides the essential CLI commands for using all functionalities of the DevOps-OS development container project.

## Table of Contents
- [Setting Up DevOps-OS](#setting-up-devops-os)
- [Creating CI/CD Configurations](#creating-cicd-configurations)
- [GitHub Actions Workflows](#github-actions-workflows)
- [Jenkins Pipelines](#jenkins-pipelines)
- [Kubernetes Deployments](#kubernetes-deployments)
- [Container Configuration](#container-configuration)

## Setting Up DevOps-OS

### Clone the DevOps-OS Repository
```bash
git clone https://github.com/yourusername/devops-os.git
cd devops-os
```

### Configure Development Container
```bash
# Edit configuration before building
vim .devcontainer/devcontainer.env.json

# Open in VS Code and reopen in container
code .
# Then use Command Palette (Cmd+Shift+P): "Remote-Containers: Reopen in Container"
```

### Manually Configure Container (After Building)
```bash
# Run configuration script manually
python3 .devcontainer/configure.py

# Check installed tools
docker --version
kubectl version --client
helm version
terraform --version
```

## Creating CI/CD Configurations

### Unified CI/CD Generator (Simplest Option)
```bash
# Generate both GitHub Actions and Jenkins pipelines with defaults
.devcontainer/generate-cicd.py

# Generate build-only configurations for specific languages
.devcontainer/generate-cicd.py --type build --languages python,javascript

# Generate with Kubernetes deployment
.devcontainer/generate-cicd.py --kubernetes --k8s-method kustomize

# Generate with matrix builds for GitHub Actions
.devcontainer/generate-cicd.py --github --matrix

# Generate with parameters for Jenkins
.devcontainer/generate-cicd.py --jenkins --parameters

# Generate with custom values file
.devcontainer/generate-cicd.py --custom-values my-config.json

# Generate for specific output location
.devcontainer/generate-cicd.py --output-dir /path/to/my/project
```

## GitHub Actions Workflows

### Generate GitHub Actions Workflows
```bash
# Basic GitHub Actions workflow
python3 .devcontainer/github-actions-generator-improved.py

# Build-only workflow
python3 .devcontainer/github-actions-generator-improved.py --type build

# Complete CI/CD workflow
python3 .devcontainer/github-actions-generator-improved.py --type complete

# Workflow with Kubernetes deployment
python3 .devcontainer/github-actions-generator-improved.py --kubernetes --k8s-method kubectl

# Matrix build across multiple platforms
python3 .devcontainer/github-actions-generator-improved.py --matrix

# Reusable workflow
python3 .devcontainer/github-actions-generator-improved.py --type reusable

# Specify languages to enable
python3 .devcontainer/github-actions-generator-improved.py --languages python,java,go

# Custom container image
python3 .devcontainer/github-actions-generator-improved.py --image ghcr.io/myorg/devops-os:latest

# Custom output location
python3 .devcontainer/github-actions-generator-improved.py --output ./my-workflows
```

### Use Environment Variables Instead
```bash
# Set environment variables
export DEVOPS_OS_GHA_TYPE=complete
export DEVOPS_OS_GHA_LANGUAGES=python,javascript
export DEVOPS_OS_GHA_KUBERNETES=true
export DEVOPS_OS_GHA_K8S_METHOD=kustomize

# Run generator (will use environment variables)
python3 .devcontainer/github-actions-generator-improved.py
```

## Jenkins Pipelines

### Generate Jenkins Pipelines
```bash
# Basic Jenkins pipeline
python3 .devcontainer/jenkins-pipeline-generator-improved.py

# Build-only pipeline
python3 .devcontainer/jenkins-pipeline-generator-improved.py --type build

# Complete CI/CD pipeline
python3 .devcontainer/jenkins-pipeline-generator-improved.py --type complete

# Pipeline with Kubernetes deployment
python3 .devcontainer/jenkins-pipeline-generator-improved.py --kubernetes --k8s-method kubectl

# Parameterized pipeline
python3 .devcontainer/jenkins-pipeline-generator-improved.py --parameters

# Specify languages to enable
python3 .devcontainer/jenkins-pipeline-generator-improved.py --languages java,go

# Specify SCM type
python3 .devcontainer/jenkins-pipeline-generator-improved.py --scm git

# Custom container image
python3 .devcontainer/jenkins-pipeline-generator-improved.py --image docker.io/myorg/devops-os:latest

# Custom output location
python3 .devcontainer/jenkins-pipeline-generator-improved.py --output ./Jenkinsfile
```

### Use Environment Variables Instead
```bash
# Set environment variables
export DEVOPS_OS_JENKINS_TYPE=complete
export DEVOPS_OS_JENKINS_LANGUAGES=python,javascript
export DEVOPS_OS_JENKINS_KUBERNETES=true
export DEVOPS_OS_JENKINS_K8S_METHOD=kustomize
export DEVOPS_OS_JENKINS_PARAMETERS=true

# Run generator (will use environment variables)
python3 .devcontainer/jenkins-pipeline-generator-improved.py
```

## Kubernetes Deployments

### Generate Kubernetes Configurations
```bash
# Generate basic Kubernetes configuration
python3 .devcontainer/k8s-config-generator.py

# Specify application name
python3 .devcontainer/k8s-config-generator.py --name my-app

# Multi-container application
python3 .devcontainer/k8s-config-generator.py --containers app,db,cache

# Generate with specific namespace
python3 .devcontainer/k8s-config-generator.py --namespace my-namespace

# Generate with Ingress
python3 .devcontainer/k8s-config-generator.py --ingress

# Generate with specific resource limits
python3 .devcontainer/k8s-config-generator.py --cpu 500m --memory 512Mi

# Generate with persistent storage
python3 .devcontainer/k8s-config-generator.py --storage

# Generate with Kustomize support
python3 .devcontainer/k8s-config-generator.py --kustomize

# Generate configurations for multiple environments
python3 .devcontainer/k8s-config-generator.py --environments dev,test,prod

# Custom output directory
python3 .devcontainer/k8s-config-generator.py --output ./k8s-configs
```

### Deploy Kubernetes Resources
```bash
# Apply generated configurations
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Apply with Kustomize
kubectl apply -k k8s/overlays/dev

# Deploy with ArgoCD
argocd app create my-app --repo https://github.com/myorg/myrepo.git --path k8s --dest-server https://kubernetes.default.svc --dest-namespace default
argocd app sync my-app

# Deploy with Flux
flux create source git my-app --url=https://github.com/myorg/myrepo.git --branch=main
flux create kustomization my-app --source=my-app --path="./k8s" --prune=true --interval=10m
```

## Container Configuration

### Configure Development Container
```bash
# Edit the devcontainer.env.json file
cat > .devcontainer/devcontainer.env.json << EOF
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
    "flux": true
  },
  "versions": {
    "python": "3.11",
    "java": "17",
    "node": "20",
    "go": "1.21"
  }
}
EOF
```

### Build Custom DevOps-OS Container
```bash
# Build container with custom name and tag
docker build -t myorg/devops-os:latest -f .devcontainer/Dockerfile .

# Push custom container to registry
docker push myorg/devops-os:latest

# Use custom container in generators
python3 .devcontainer/github-actions-generator-improved.py --image myorg/devops-os:latest
python3 .devcontainer/jenkins-pipeline-generator-improved.py --image myorg/devops-os:latest
```

## Examples for Common Technology Stacks

### Python Web Application (FastAPI)
```bash
# Generate Python-focused CI/CD
.devcontainer/generate-cicd.py --languages python --name "FastAPI CI/CD"

# Add Python test stage with coverage
python3 .devcontainer/github-actions-generator-improved.py --type test --languages python
```

### Java Spring Boot Application
```bash
# Generate Java-focused CI/CD
.devcontainer/generate-cicd.py --languages java --name "Spring Boot CI/CD"

# Generate Kubernetes deployment for Spring Boot
python3 .devcontainer/k8s-config-generator.py --name spring-app --port 8080
```

### JavaScript/Node.js Application
```bash
# Generate JavaScript-focused CI/CD
.devcontainer/generate-cicd.py --languages javascript --name "Node.js CI/CD"

# Generate with npm caching
python3 .devcontainer/github-actions-generator-improved.py --languages javascript --custom-values node-config.json
```

### Microservices Project
```bash
# Generate complete CI/CD for multiple services
.devcontainer/generate-cicd.py --kubernetes --k8s-method kustomize --custom-values microservices.json
```

## Common Options for All Generators

|Option|GitHub Actions|Jenkins|Kubernetes|Description|
|------|--------------|-------|----------|-----------|
|`--name`|✓|✓|✓|Name of the workflow/pipeline/app|
|`--type`|✓|✓|✗|Type of workflow/pipeline|
|`--languages`|✓|✓|✗|Languages to enable|
|`--kubernetes`|✓|✓|✗|Include K8s deployment steps|
|`--k8s-method`|✓|✓|✗|K8s deployment method|
|`--output`|✓|✓|✓|Output directory/file path|
|`--custom-values`|✓|✓|✓|Custom configuration file|
|`--image`|✓|✓|✗|Container image to use|

## Troubleshooting

```bash
# Show help for each generator
python3 .devcontainer/github-actions-generator-improved.py --help
python3 .devcontainer/jenkins-pipeline-generator-improved.py --help
python3 .devcontainer/k8s-config-generator.py --help
python3 .devcontainer/generate-cicd.py --help

# Verify container configuration
cat .devcontainer/devcontainer.env.json

# Check generator output
ls -la .github/workflows/
cat Jenkinsfile
ls -la k8s/
```
