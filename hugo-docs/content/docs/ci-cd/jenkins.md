---
title: "Jenkins"
weight: 23
---

# Jenkins Pipeline Generator

Generate `Jenkinsfile` scripts using the declarative pipeline syntax. Pipelines leverage the DevOps-OS container for a consistent build environment.

---

## Basic Usage

```bash
python -m cli.scaffold_jenkins --name "my-app" --type complete
```

**Output:** `Jenkinsfile` (default)  
Change the output path with `--output <path>`.

---

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--name NAME` | `DevOps-OS` | Pipeline name |
| `--type TYPE` | `complete` | `build` \| `test` \| `deploy` \| `complete` \| `parameterized` |
| `--languages LANGS` | `python,javascript` | Comma-separated: `python`, `java`, `javascript`, `go` |
| `--kubernetes` | off | Add Kubernetes deploy stage |
| `--registry URL` | `docker.io` | Container registry URL |
| `--k8s-method METHOD` | `kubectl` | `kubectl` \| `kustomize` \| `argocd` \| `flux` |
| `--output FILE` | `Jenkinsfile` | Output file path |
| `--custom-values FILE` | _(none)_ | Path to custom values JSON file |
| `--image IMAGE` | `docker.io/yourorg/devops-os:latest` | DevOps-OS container image |
| `--scm SCM` | `git` | Source control: `git` \| `svn` \| `none` |
| `--parameters` | off | Add runtime parameters (auto-enabled for `--type parameterized`) |
| `--env-file FILE` | _(cli dir)_ | Path to `devcontainer.env.json` |

All options can be set via environment variables prefixed `DEVOPS_OS_JENKINS_`.

---

## Pipeline Types

| Type | Description |
|------|-------------|
| `build` | Focuses on building and packaging your application |
| `test` | Focuses on running tests |
| `deploy` | Focuses on deploying to the target environment |
| `complete` | Combines build, test, and deploy stages |
| `parameterized` | Adds runtime parameters for interactive runs |

---

## Examples

### Complete Java pipeline

```bash
python -m cli.scaffold_jenkins --name my-app --languages java --type complete
# Output: Jenkinsfile
```

### Parameterized deployment pipeline

```bash
python -m cli.scaffold_jenkins \
  --name "Deployment" \
  --languages go \
  --kubernetes --k8s-method argocd \
  --parameters
# Output: Jenkinsfile
```

### Custom output location

```bash
python -m cli.scaffold_jenkins \
  --name my-app \
  --languages python \
  --output pipelines/Jenkinsfile
# Output: pipelines/Jenkinsfile
```

---

## Generated Pipeline Structure

```groovy
pipeline {
    agent {
        docker {
            image 'docker.io/yourorg/devops-os:latest'
            args '-v /var/run/docker.sock:/var/run/docker.sock -u root'
        }
    }
    parameters {
        booleanParam(name: 'PYTHON_ENABLED', defaultValue: true, ...)
        choice(name: 'ENVIRONMENT', choices: ['dev', 'test', 'staging', 'prod'], ...)
        string(name: 'IMAGE_TAG', defaultValue: 'latest', ...)
    }
    environment {
        REGISTRY     = 'docker.io'
        IMAGE_NAME   = 'myorg/my-app'
    }
    stages {
        stage('Build') { ... }
        stage('Test')  { ... }
        stage('Deploy') { ... }
    }
    post {
        always { cleanWs() }
        failure { mail to: 'team@example.com', subject: 'Build failed' }
    }
}
```

---

## Parameterized Pipelines

Parameterized pipelines accept runtime inputs:

```groovy
parameters {
    booleanParam(name: 'PYTHON_ENABLED', defaultValue: true,
                 description: 'Enable Python tools')
    choice(name: 'ENVIRONMENT',
           choices: ['dev', 'test', 'staging', 'prod'],
           defaultValue: 'dev')
    string(name: 'IMAGE_TAG', defaultValue: 'latest',
           description: 'Container image tag')
}
```

---

## Credentials Management

The generated pipeline uses Jenkins credentials:

```groovy
withCredentials([
    file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')
]) {
    sh 'kubectl apply -f ./k8s/deployment.yaml'
}

withCredentials([
    usernamePassword(
        credentialsId: 'registry-credentials',
        usernameVariable: 'REGISTRY_USER',
        passwordVariable: 'REGISTRY_PASSWORD'
    )
]) {
    sh 'docker login -u $REGISTRY_USER -p $REGISTRY_PASSWORD'
}
```

---

## Environment Variables

```bash
export DEVOPS_OS_JENKINS_NAME="API Service"
export DEVOPS_OS_JENKINS_TYPE="complete"
export DEVOPS_OS_JENKINS_LANGUAGES="python,go"
export DEVOPS_OS_JENKINS_KUBERNETES="true"
export DEVOPS_OS_JENKINS_K8S_METHOD="kustomize"
export DEVOPS_OS_JENKINS_PARAMETERS="true"

python -m cli.scaffold_jenkins
# Output: Jenkinsfile
```

---

## Custom Values File

```json
{
  "build": {
    "timeout_minutes": 30,
    "tool_options": {
      "maven": { "goals": ["clean", "package"] }
    }
  },
  "credentials": {
    "docker": "docker-registry-credentials",
    "kubernetes": "kubeconfig",
    "argocd": "argocd-credentials"
  },
  "notifications": {
    "slack": { "channel": "deployments", "failure": true }
  }
}
```

```bash
python -m cli.scaffold_jenkins --custom-values advanced-config.json
# Output: Jenkinsfile
```

---

## Best Practices

1. Use `--parameters` for environments that benefit from manual approval gates
2. Store credentials in Jenkins Credentials Store, never in the Jenkinsfile
3. Use `--env-file` to align with your dev container configuration
4. Start with `--type complete` and remove stages you don't need
5. Set appropriate timeouts in `--custom-values` for long builds
