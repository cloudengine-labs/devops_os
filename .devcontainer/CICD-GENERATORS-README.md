# DevOps-OS CI/CD Generators

This project provides powerful tools for generating customizable CI/CD configurations that leverage the DevOps-OS development container. These generators create GitHub Actions workflows and Jenkins pipelines designed to integrate with your DevOps-OS environment.

## Features

- **GitHub Actions Generator**: Creates complete or specialized workflows for your projects
  - Matrix builds across multiple platforms
  - Conditional stages based on repo content
  - Reusable workflow support
  - Container-based execution environment
  - Kubernetes deployment integration

- **Jenkins Pipeline Generator**: Creates sophisticated Jenkins pipelines
  - Parameterized run configurations
  - Integration with Jenkins credentials
  - Docker and Kubernetes integration
  - Shared library compatibility
  - Advanced post-execution actions

- **Unified Generator Helper**: A single script to generate both GitHub Actions and Jenkins configurations with consistent settings

## Quick Start

### Generate Both CI/CD Configurations

```bash
# Generate complete CI/CD configurations with defaults
./generate-cicd.py

# Generate build-only configurations for Python projects
./generate-cicd.py --type build --languages python

# Generate complete CI/CD with Kubernetes deployment
./generate-cicd.py --kubernetes --k8s-method kustomize
```

### Generate GitHub Actions Only

```bash
# Generate GitHub Actions workflow with matrix builds
./generate-cicd.py --github --matrix

# Generate GitHub Actions workflow with specific name
./generate-cicd.py --github --name "My CI Pipeline"
```

### Generate Jenkins Pipeline Only

```bash
# Generate parameterized Jenkins pipeline
./generate-cicd.py --jenkins --parameters

# Generate Jenkins pipeline for Java builds
./generate-cicd.py --jenkins --type build --languages java
```

## Detailed Documentation

For more detailed information about the generators and their options, see:

- [CI/CD Generators Usage Guide](CI-CD-GENERATORS-USAGE.md)
- [How To Create DevOps-OS GHA & Jenkins](HowTo-Create-DevOps-Os-GHA-Jenkins.md)
- [Kubernetes Capabilities](kubernetes-capabilities.md)

## GitHub Actions Generator

The GitHub Actions generator creates workflows that use the DevOps-OS container for consistent execution environments.

```bash
# Basic usage
python github-actions-generator-improved.py --name "CI Workflow" --type complete

# With Kubernetes deployment
python github-actions-generator-improved.py --kubernetes --k8s-method argocd

# Reusable workflow
python github-actions-generator-improved.py --type reusable
```

See all options:
```bash
python github-actions-generator-improved.py --help
```

## Jenkins Pipeline Generator

The Jenkins pipeline generator creates Jenkinsfiles that use the DevOps-OS container for consistent execution environments.

```bash
# Basic usage
python jenkins-pipeline-generator-improved.py --name "Jenkins Build" --type build

# With parameters for manual configuration
python jenkins-pipeline-generator-improved.py --parameters

# Complete CI/CD with Kubernetes
python jenkins-pipeline-generator-improved.py --type complete --kubernetes
```

See all options:
```bash
python jenkins-pipeline-generator-improved.py --help
```

## Environment Variable Configuration

Both generators support configuration via environment variables:

- GitHub Actions: `DEVOPS_OS_GHA_*` (e.g., `DEVOPS_OS_GHA_TYPE=complete`)
- Jenkins: `DEVOPS_OS_JENKINS_*` (e.g., `DEVOPS_OS_JENKINS_PARAMETERS=true`)

This allows for easy integration with automated tools and scripts.

## Integration with DevOps-OS

The generators integrate with your DevOps-OS development container configuration, ensuring the CI/CD environments match your development environment. This is done by reading the `devcontainer.env.json` file to determine which languages and tools to enable.

## Advanced Configuration

For advanced configuration options, you can provide a custom values JSON file:

```bash
./generate-cicd.py --custom-values my-config.json
```

The custom values file lets you specify advanced options for your CI/CD pipeline.

## License

This project is licensed under the terms specified in the LICENSE file.
