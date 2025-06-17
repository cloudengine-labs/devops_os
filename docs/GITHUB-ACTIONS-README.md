# Creating Customized GitHub Actions Templates

This guide covers how to create and customize GitHub Actions workflow templates using DevOps-OS tooling. The GitHub Actions generator helps you create workflows that integrate with your development environment and deployment needs.

## Table of Contents

- [Understanding the GitHub Actions Generator](#understanding-the-github-actions-generator)
- [Basic Usage](#basic-usage)
- [Workflow Types](#workflow-types)
- [Customization Options](#customization-options)
- [Matrix Builds](#matrix-builds)
- [Kubernetes Integration](#kubernetes-integration)
- [Reusable Workflows](#reusable-workflows)
- [Environment Variables](#environment-variables)
- [Advanced Customization](#advanced-customization)
- [Examples](#examples)

## Understanding the GitHub Actions Generator

The GitHub Actions generator (`github-actions-generator-improved.py`) creates YAML workflow files that orchestrate continuous integration and deployment processes using GitHub's action system. The workflows leverage the DevOps-OS container to provide a consistent environment for building, testing, and deploying your applications.

## Basic Usage

To generate a basic GitHub Actions workflow:

```bash
python github-actions-generator-improved.py --name "My Workflow" --type complete
```

This generates a complete CI/CD workflow including build, test, and deploy stages.

## Workflow Types

The generator supports several types of workflows:

1. **Build Workflow** (`--type build`): Focuses on building and packaging your application.
2. **Test Workflow** (`--type test`): Focuses on running tests and validating your application.
3. **Deploy Workflow** (`--type deploy`): Focuses on deploying your application to the target environment.
4. **Complete Workflow** (`--type complete`): Combines build, test, and deploy stages.
5. **Reusable Workflow** (`--type reusable` or `--reusable`): Creates a reusable workflow that can be called from other workflows.

## Customization Options

### Basic Options

- `--name`: The name of the workflow (e.g., "Backend CI/CD")
- `--languages`: Comma-separated list of languages to enable (e.g., "python,java,javascript,go")
- `--output`: Output directory for the generated workflow file

### Example with Basic Options

```bash
python github-actions-generator-improved.py --name "Python API" --languages python --output ./.github/workflows
```

## Matrix Builds

Matrix builds allow you to run your workflows across multiple configurations, such as different operating systems or language versions:

```bash
python github-actions-generator-improved.py --matrix
```

This creates a workflow with a matrix strategy that runs on multiple platforms.

### Custom Matrix Configuration

For more advanced matrix configurations, you can provide a custom values file:

```json
{
  "matrix": {
    "os": ["ubuntu-latest", "windows-latest", "macos-latest"],
    "python-version": ["3.8", "3.9", "3.10", "3.11"],
    "exclude": [
      {
        "os": "windows-latest",
        "python-version": "3.11"
      }
    ]
  }
}
```

```bash
python github-actions-generator-improved.py --custom-values matrix-config.json
```

## Kubernetes Integration

To include Kubernetes deployment steps in your workflow:

```bash
python github-actions-generator-improved.py --kubernetes --k8s-method kubectl
```

### Kubernetes Deployment Methods

Four Kubernetes deployment methods are supported:

1. **kubectl** (`--k8s-method kubectl`): Direct deployment using kubectl commands.
2. **kustomize** (`--k8s-method kustomize`): Deployment using Kustomize for environment-specific configurations.
3. **argocd** (`--k8s-method argocd`): GitOps deployment using ArgoCD.
4. **flux** (`--k8s-method flux`): GitOps deployment using Flux CD.

## Reusable Workflows

Reusable workflows can be called from other workflows, making them ideal for creating standardized CI/CD templates:

```bash
python github-actions-generator-improved.py --type reusable
```

### Using a Reusable Workflow

The generated reusable workflow can be called from another workflow:

```yaml
jobs:
  call-devops-os-workflow:
    uses: ./.github/workflows/devops-os-reusable.yml
    with:
      languages: '{"python": true, "java": true}'
      deploy_environment: 'production'
```

## Environment Variables

All options can be set using environment variables prefixed with `DEVOPS_OS_GHA_`:

```bash
export DEVOPS_OS_GHA_NAME="API Service"
export DEVOPS_OS_GHA_TYPE="complete"
export DEVOPS_OS_GHA_LANGUAGES="python,go"
export DEVOPS_OS_GHA_KUBERNETES="true"
export DEVOPS_OS_GHA_K8S_METHOD="kustomize"
export DEVOPS_OS_GHA_MATRIX="true"

python github-actions-generator-improved.py
```

## Advanced Customization

### Custom Values File

For advanced customization, create a custom values JSON file:

```json
{
  "build": {
    "cache": true,
    "timeout_minutes": 30,
    "artifact_paths": ["dist/**", "build/**"]
  },
  "test": {
    "coverage": true,
    "junit_reports": true,
    "parallel": 4,
    "timeout_minutes": 20
  },
  "deploy": {
    "environments": ["dev", "staging", "prod"],
    "approval_required": true,
    "rollback_enabled": true
  },
  "notifications": {
    "slack": {
      "channel": "deployments",
      "success": true,
      "failure": true
    },
    "email": {
      "recipients": ["team@example.com"],
      "on_failure_only": true
    }
  }
}
```

```bash
python github-actions-generator-improved.py --custom-values advanced-config.json
```

### Integration with DevOps-OS Configuration

The generator integrates with the DevOps-OS `devcontainer.env.json` file to ensure consistency between your development environment and CI/CD workflows:

```bash
python github-actions-generator-improved.py --env-file ./devcontainer.env.json
```

## Examples

### Basic Python Application Workflow

```bash
python github-actions-generator-improved.py --name "Python App" --languages python --type complete
```

### Java Application with Maven

```bash
python github-actions-generator-improved.py --name "Java Service" --languages java --custom-values maven-config.json
```

### Multi-language Microservices

```bash
python github-actions-generator-improved.py --name "Microservices" --languages python,javascript,go --kubernetes --k8s-method kustomize
```

### Cross-platform Node.js Application

```bash
python github-actions-generator-improved.py --name "Node.js App" --languages javascript --matrix --custom-values node-matrix.json
```

### Complete Docker and Kubernetes Workflow

```bash
python github-actions-generator-improved.py --name "Container Deploy" --languages go --kubernetes --k8s-method argocd --registry ghcr.io
```

## Understanding the Generated Workflow

The generated GitHub Actions workflow includes:

1. **Triggers**: Configures when the workflow runs (push, pull request, workflow dispatch).
2. **Jobs**: Defines the jobs to run (build, test, deploy).
3. **Steps**: Details the steps within each job.
4. **Environment**: Sets up the execution environment using the DevOps-OS container.
5. **Artifacts**: Configures artifact handling for sharing between jobs.
6. **Deployments**: Includes deployment steps if Kubernetes is enabled.

### Example Structure

```yaml
name: My CI/CD
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: Environment to deploy to
        required: true
        default: dev
        type: choice
        options: [dev, test, staging, prod]

jobs:
  build:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/yourorg/devops-os:latest
    steps:
      # Build steps here
      
  test:
    needs: build
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/yourorg/devops-os:latest
    steps:
      # Test steps here
      
  deploy:
    needs: test
    if: github.event_name == 'push' || github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/yourorg/devops-os:latest
    steps:
      # Deploy steps here
```

## Best Practices

1. **Start Simple**: Begin with a basic workflow and add complexity as needed.
2. **Use Environment Variables**: Use environment variables for secrets and configuration.
3. **Leverage Matrix Builds**: Use matrix builds for testing across multiple configurations.
4. **Use Reusable Workflows**: Create reusable workflows for common patterns.
5. **Custom Values**: Use custom values files for advanced configuration.
6. **Integration with DevOps-OS**: Integrate with your DevOps-OS configuration for consistency.

## Next Steps

- Explore the [Jenkins Pipeline Generator](./JENKINS-PIPELINE-README.md) for creating Jenkins pipelines.
- Learn about [Kubernetes deployments](./KUBERNETES-DEPLOYMENT-README.md) for deploying your applications.
- Implement [CI/CD pipelines for technology stacks](./CICD-TECH-STACK-README.md) specific to your project.
