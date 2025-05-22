# DevOps-OS CI/CD Generators

This document describes how to use the improved CI/CD generators included with DevOps-OS. These generators create GitHub Actions workflows and Jenkins pipelines that leverage the DevOps-OS container for consistent CI/CD environments.

## Table of Contents

- [GitHub Actions Workflow Generator](#github-actions-workflow-generator)
  - [Features](#github-actions-features)
  - [Usage](#github-actions-usage)
  - [Environment Variables](#github-actions-environment-variables)
  - [Examples](#github-actions-examples)
- [Jenkins Pipeline Generator](#jenkins-pipeline-generator)
  - [Features](#jenkins-features)
  - [Usage](#jenkins-usage)
  - [Environment Variables](#jenkins-environment-variables)
  - [Examples](#jenkins-examples)
- [Integration with DevContainer Configuration](#integration-with-devcontainer-configuration)
- [Advanced Usage](#advanced-usage)

## GitHub Actions Workflow Generator

The GitHub Actions workflow generator creates customizable workflows for your projects that use the DevOps-OS container as the execution environment.

### GitHub Actions Features

- Multiple workflow types: build, test, deploy, complete, or reusable
- Environment variable configuration (`DEVOPS_OS_GHA_*`)
- Matrix builds for multiple OS/architecture combinations
- YAML-based output format
- Kubernetes deployment integration (kubectl, kustomize, ArgoCD, Flux)
- Reusable workflow generation
- Integration with DevOps-OS container configuration

### GitHub Actions Usage

```bash
python github-actions-generator-improved.py [options]
```

Options:
- `--name`: Workflow name (default: "DevOps-OS")
- `--type`: Workflow type (build, test, deploy, complete, reusable)
- `--languages`: Comma-separated list of languages (python,java,javascript,go)
- `--kubernetes`: Include Kubernetes deployment steps
- `--registry`: Container registry URL
- `--k8s-method`: Kubernetes deployment method (kubectl, kustomize, argocd, flux)
- `--output`: Output directory for generated workflow files
- `--custom-values`: Path to custom values JSON file
- `--image`: DevOps-OS container image to use
- `--branches`: Comma-separated list of branches to trigger workflow
- `--matrix`: Enable matrix builds (multiple OS/architectures)
- `--env-file`: Path to devcontainer.env.json
- `--reusable`: Generate a reusable workflow

### GitHub Actions Environment Variables

All command-line options can be configured using environment variables with the `DEVOPS_OS_GHA_` prefix:

- `DEVOPS_OS_GHA_NAME`: Workflow name
- `DEVOPS_OS_GHA_TYPE`: Workflow type
- `DEVOPS_OS_GHA_LANGUAGES`: Languages to enable
- `DEVOPS_OS_GHA_KUBERNETES`: Enable Kubernetes deployment (true/false)
- `DEVOPS_OS_GHA_REGISTRY`: Container registry URL
- `DEVOPS_OS_GHA_K8S_METHOD`: Kubernetes deployment method
- `DEVOPS_OS_GHA_OUTPUT`: Output directory
- `DEVOPS_OS_GHA_CUSTOM_VALUES`: Custom values file path
- `DEVOPS_OS_GHA_IMAGE`: Container image
- `DEVOPS_OS_GHA_BRANCHES`: Branches to trigger workflow
- `DEVOPS_OS_GHA_MATRIX`: Enable matrix builds (true/false)
- `DEVOPS_OS_GHA_ENV_FILE`: Path to devcontainer.env.json
- `DEVOPS_OS_GHA_REUSABLE`: Generate reusable workflow (true/false)

### GitHub Actions Examples

Basic build workflow:
```bash
python github-actions-generator-improved.py --name "Build Workflow" --type build --languages python,javascript
```

Complete CI/CD workflow with Kubernetes deployment:
```bash
python github-actions-generator-improved.py --name "CI/CD Pipeline" --type complete --languages python,java,javascript,go --kubernetes --k8s-method kustomize
```

Reusable workflow:
```bash
python github-actions-generator-improved.py --name "Reusable DevOps-OS" --type reusable --languages python,javascript
```

Matrix build across multiple platforms:
```bash
python github-actions-generator-improved.py --name "Cross-Platform Build" --type build --languages go --matrix
```

## Jenkins Pipeline Generator

The Jenkins pipeline generator creates customizable Jenkinsfile scripts for your projects that use the DevOps-OS container as the execution environment.

### Jenkins Features

- Multiple pipeline types: build, test, deploy, complete, parameterized
- Environment variable configuration (`DEVOPS_OS_JENKINS_*`)
- Parameterized build support
- Integration with Jenkins credentials
- Kubernetes deployment integration (kubectl, kustomize, ArgoCD, Flux)
- Advanced post-build actions
- Integration with DevOps-OS container configuration

### Jenkins Usage

```bash
python jenkins-pipeline-generator-improved.py [options]
```

Options:
- `--name`: Pipeline name (default: "DevOps-OS")
- `--type`: Pipeline type (build, test, deploy, complete, parameterized)
- `--languages`: Comma-separated list of languages (python,java,javascript,go)
- `--kubernetes`: Include Kubernetes deployment steps
- `--registry`: Container registry URL
- `--k8s-method`: Kubernetes deployment method (kubectl, kustomize, argocd, flux)
- `--output`: Output file path for generated Jenkinsfile
- `--custom-values`: Path to custom values JSON file
- `--image`: DevOps-OS container image to use
- `--scm`: Source Control Management system (git, svn, none)
- `--parameters`: Generate pipeline with parameters
- `--env-file`: Path to devcontainer.env.json

### Jenkins Environment Variables

All command-line options can be configured using environment variables with the `DEVOPS_OS_JENKINS_` prefix:

- `DEVOPS_OS_JENKINS_NAME`: Pipeline name
- `DEVOPS_OS_JENKINS_TYPE`: Pipeline type
- `DEVOPS_OS_JENKINS_LANGUAGES`: Languages to enable
- `DEVOPS_OS_JENKINS_KUBERNETES`: Enable Kubernetes deployment (true/false)
- `DEVOPS_OS_JENKINS_REGISTRY`: Container registry URL
- `DEVOPS_OS_JENKINS_K8S_METHOD`: Kubernetes deployment method
- `DEVOPS_OS_JENKINS_OUTPUT`: Output file path
- `DEVOPS_OS_JENKINS_CUSTOM_VALUES`: Custom values file path
- `DEVOPS_OS_JENKINS_IMAGE`: Container image
- `DEVOPS_OS_JENKINS_SCM`: Source Control Management system
- `DEVOPS_OS_JENKINS_PARAMETERS`: Generate parameterized pipeline (true/false)
- `DEVOPS_OS_JENKINS_ENV_FILE`: Path to devcontainer.env.json

### Jenkins Examples

Basic build pipeline:
```bash
python jenkins-pipeline-generator-improved.py --name "Build Pipeline" --type build --languages python,javascript
```

Complete CI/CD pipeline with Kubernetes deployment:
```bash
python jenkins-pipeline-generator-improved.py --name "CI/CD Pipeline" --type complete --languages python,java,javascript,go --kubernetes --k8s-method kustomize --parameters
```

Parameterized pipeline:
```bash
python jenkins-pipeline-generator-improved.py --name "Parameterized Pipeline" --type parameterized --languages python,javascript --parameters
```

## Integration with DevContainer Configuration

Both generators integrate with the DevOps-OS `devcontainer.env.json` configuration file to automatically configure features based on your development container setup. This ensures consistency between your development environment and CI/CD pipelines.

The integration works by:

1. Reading the `devcontainer.env.json` file
2. Extracting language and tool settings
3. Configuring the generated workflows to match your development environment

This provides a seamless experience where your CI/CD pipelines will have the same capabilities as your local development environment.

## Advanced Usage

### Custom Values

Both generators support a `--custom-values` option that allows you to provide a JSON file with additional configuration options. This can be used to override defaults or provide additional settings not covered by the command-line options.

Example `custom-values.json`:
```json
{
  "build": {
    "cache": true,
    "timeout": 30
  },
  "test": {
    "coverage": true,
    "parallel": true
  },
  "deploy": {
    "approvals": true,
    "notifications": ["email", "slack"]
  },
  "environments": {
    "dev": {
      "url": "dev.example.com",
      "replicas": 1
    },
    "prod": {
      "url": "example.com",
      "replicas": 3
    }
  }
}
```

### Matrix Build Configuration

For GitHub Actions, matrix builds can be customized through custom values:

```json
{
  "matrix": {
    "os": ["ubuntu-latest", "windows-latest", "macos-latest"],
    "architecture": ["x86_64", "arm64"],
    "exclude": [
      {
        "os": "windows-latest",
        "architecture": "arm64"
      }
    ]
  }
}
```

### Jenkins Credentials Integration

The Jenkins pipeline generator can integrate with Jenkins credentials:

```bash
python jenkins-pipeline-generator-improved.py --name "Secure Pipeline" --type complete --custom-values credentials.json
```

Example `credentials.json`:
```json
{
  "credentials": {
    "docker": "docker-registry-credentials",
    "kubernetes": "k8s-credentials",
    "git": "git-credentials",
    "sonarqube": "sonar-credentials"
  }
}
```
