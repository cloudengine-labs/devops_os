# Creating Customized Jenkins Pipeline Templates

This guide covers how to create and customize Jenkins pipeline templates using DevOps-OS tooling. The Jenkins pipeline generator helps you create Jenkinsfiles that integrate with your development environment and deployment needs.

## Table of Contents

- [Understanding the Jenkins Pipeline Generator](#understanding-the-jenkins-pipeline-generator)
- [Basic Usage](#basic-usage)
- [Pipeline Types](#pipeline-types)
- [Customization Options](#customization-options)
- [Parameterized Pipelines](#parameterized-pipelines)
- [Kubernetes Integration](#kubernetes-integration)
- [Credentials Management](#credentials-management)
- [Environment Variables](#environment-variables)
- [Advanced Customization](#advanced-customization)
- [Examples](#examples)

## Understanding the Jenkins Pipeline Generator

The Jenkins pipeline generator (`jenkins-pipeline-generator-improved.py`) creates Jenkinsfile scripts that define your CI/CD pipeline using the Jenkins declarative pipeline syntax. The pipelines leverage the DevOps-OS container to provide a consistent environment for building, testing, and deploying your applications.

## Basic Usage

To generate a basic Jenkins pipeline:

```bash
python jenkins-pipeline-generator-improved.py --name "My Pipeline" --type complete
```

This generates a complete CI/CD pipeline including build, test, and deploy stages.

## Pipeline Types

The generator supports several types of pipelines:

1. **Build Pipeline** (`--type build`): Focuses on building and packaging your application.
2. **Test Pipeline** (`--type test`): Focuses on running tests and validating your application.
3. **Deploy Pipeline** (`--type deploy`): Focuses on deploying your application to the target environment.
4. **Complete Pipeline** (`--type complete`): Combines build, test, and deploy stages.
5. **Parameterized Pipeline** (`--type parameterized`): Creates a pipeline with parameters for runtime configuration.

## Customization Options

### Basic Options

- `--name`: The name of the pipeline (e.g., "Backend CI/CD")
- `--languages`: Comma-separated list of languages to enable (e.g., "python,java,javascript,go")
- `--output`: Output file path for the generated Jenkinsfile

### Example with Basic Options

```bash
python jenkins-pipeline-generator-improved.py --name "Python API" --languages python --output ./Jenkinsfile
```

## Parameterized Pipelines

Parameterized pipelines allow for runtime configuration of the pipeline:

```bash
python jenkins-pipeline-generator-improved.py --parameters
```

This creates a pipeline with parameters that can be configured when the pipeline is run.

### Parameter Types

Various parameter types are supported:

- **Boolean Parameters**: For toggle options (e.g., enable/disable a feature).
- **Choice Parameters**: For selecting from predefined options (e.g., environment).
- **String Parameters**: For free-form string input (e.g., version tag).

### Example Parameters

```groovy
parameters {
    booleanParam(name: 'PYTHON_ENABLED', defaultValue: true, description: 'Enable Python tools')
    choice(name: 'ENVIRONMENT', choices: ['dev', 'test', 'staging', 'prod'], defaultValue: 'dev')
    string(name: 'IMAGE_TAG', defaultValue: 'latest', description: 'Container image tag')
}
```

## Kubernetes Integration

To include Kubernetes deployment steps in your pipeline:

```bash
python jenkins-pipeline-generator-improved.py --kubernetes --k8s-method kubectl
```

### Kubernetes Deployment Methods

Four Kubernetes deployment methods are supported:

1. **kubectl** (`--k8s-method kubectl`): Direct deployment using kubectl commands.
2. **kustomize** (`--k8s-method kustomize`): Deployment using Kustomize for environment-specific configurations.
3. **argocd** (`--k8s-method argocd`): GitOps deployment using ArgoCD.
4. **flux** (`--k8s-method flux`): GitOps deployment using Flux CD.

## Credentials Management

The pipeline generator integrates with Jenkins credentials for secure management of sensitive information:

```bash
python jenkins-pipeline-generator-improved.py --type complete --kubernetes
```

### Credentials in Generated Pipelines

The generated pipelines use Jenkins credentials for:

- **Docker Registry**: Authenticating with container registries.
- **Kubernetes**: Accessing Kubernetes clusters.
- **Source Control**: Authenticating with SCM providers.
- **External Services**: Authenticating with external services like ArgoCD.

### Example Credentials Usage

```groovy
withCredentials([
    file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')
]) {
    sh 'kubectl apply -f ./k8s/deployment.yaml'
}

withCredentials([
    usernamePassword(credentialsId: 'registry-credentials', usernameVariable: 'REGISTRY_USER', passwordVariable: 'REGISTRY_PASSWORD')
]) {
    sh 'docker login -u $REGISTRY_USER -p $REGISTRY_PASSWORD'
}
```

## Environment Variables

All options can be set using environment variables prefixed with `DEVOPS_OS_JENKINS_`:

```bash
export DEVOPS_OS_JENKINS_NAME="API Service"
export DEVOPS_OS_JENKINS_TYPE="complete"
export DEVOPS_OS_JENKINS_LANGUAGES="python,go"
export DEVOPS_OS_JENKINS_KUBERNETES="true"
export DEVOPS_OS_JENKINS_K8S_METHOD="kustomize"
export DEVOPS_OS_JENKINS_PARAMETERS="true"

python jenkins-pipeline-generator-improved.py
```

## Advanced Customization

### Custom Values File

For advanced customization, create a custom values JSON file:

```json
{
  "build": {
    "timeout_minutes": 30,
    "artifact_paths": ["dist/**", "build/**"],
    "tool_options": {
      "maven": {
        "goals": ["clean", "package"],
        "options": "-DskipTests=false -P production"
      },
      "gradle": {
        "tasks": ["build"],
        "options": "--no-daemon"
      }
    }
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
  "credentials": {
    "docker": "docker-registry-credentials",
    "kubernetes": "kubeconfig",
    "git": "git-credentials",
    "argocd": "argocd-credentials"
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
python jenkins-pipeline-generator-improved.py --custom-values advanced-config.json
```

### Integration with DevOps-OS Configuration

The generator integrates with the DevOps-OS `devcontainer.env.json` file to ensure consistency between your development environment and CI/CD pipelines:

```bash
python jenkins-pipeline-generator-improved.py --env-file ./devcontainer.env.json
```

## Examples

### Basic Python Application Pipeline

```bash
python jenkins-pipeline-generator-improved.py --name "Python App" --languages python --type complete
```

### Java Application with Maven

```bash
python jenkins-pipeline-generator-improved.py --name "Java Service" --languages java --custom-values maven-config.json
```

### Multi-language Microservices

```bash
python jenkins-pipeline-generator-improved.py --name "Microservices" --languages python,javascript,go --kubernetes --k8s-method kustomize
```

### Parameterized Deployment Pipeline

```bash
python jenkins-pipeline-generator-improved.py --name "Deployment" --languages go --kubernetes --k8s-method argocd --parameters
```

### Complete Docker and Kubernetes Pipeline

```bash
python jenkins-pipeline-generator-improved.py --name "Container Deploy" --languages go --kubernetes --k8s-method kubectl --registry docker.io
```

## Understanding the Generated Pipeline

The generated Jenkinsfile defines a declarative pipeline with:

1. **Agent**: Configures the execution environment using the DevOps-OS container.
2. **Parameters**: Defines parameters for customizing pipeline execution (if enabled).
3. **Environment**: Sets environment variables for the pipeline.
4. **Options**: Configures pipeline options like timeout and build history.
5. **Stages**: Defines the stages of the pipeline (build, test, deploy).
6. **Post**: Defines actions to take after pipeline execution.

### Example Structure

```groovy
pipeline {
    agent {
        docker {
            image 'docker.io/yourorg/devops-os:latest'
            args '-v /var/run/docker.sock:/var/run/docker.sock -u root'
        }
    }
    parameters {
        // Parameters here
    }
    environment {
        // Environment variables here
    }
    options {
        // Pipeline options here
    }
    stages {
        stage('Build') {
            steps {
                // Build steps here
            }
        }
        stage('Test') {
            steps {
                // Test steps here
            }
        }
        stage('Deploy') {
            steps {
                // Deploy steps here
            }
        }
    }
    post {
        // Post-execution actions here
    }
}
```

## Best Practices

1. **Start Simple**: Begin with a basic pipeline and add complexity as needed.
2. **Use Parameters**: Use parameters for configurable pipelines.
3. **Manage Credentials**: Use Jenkins credentials for sensitive information.
4. **Structure Stages**: Organize your pipeline into logical stages.
5. **Handle Failures**: Add appropriate post-failure actions.
6. **Custom Values**: Use custom values files for advanced configuration.
7. **Integration with DevOps-OS**: Integrate with your DevOps-OS configuration for consistency.

## Next Steps

- Explore the [GitHub Actions Generator](./GITHUB-ACTIONS-README.md) for creating GitHub Actions workflows.
- Learn about [Kubernetes deployments](./KUBERNETES-DEPLOYMENT-README.md) for deploying your applications.
- Implement [CI/CD pipelines for technology stacks](./CICD-TECH-STACK-README.md) specific to your project.
