---
title: "GitHub Actions"
weight: 21
---

# GitHub Actions Workflow Generator

The GitHub Actions generator creates YAML workflow files that orchestrate CI/CD processes using GitHub's built-in action system. Workflows leverage the DevOps-OS container for a consistent build environment.

---

## Basic Usage

```bash
python -m cli.scaffold_gha --name "my-app" --type complete
```

**Output:** `.github/workflows/my-app-complete.yml`

The filename pattern is `<name-hyphenated>-<type>.yml` inside the output directory.  
Change the output directory with `--output <dir>` (default: `.github/workflows/`).

---

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--name NAME` | `DevOps-OS` | Workflow name |
| `--type TYPE` | `complete` | `build` \| `test` \| `deploy` \| `complete` \| `reusable` |
| `--languages LANGS` | `python,javascript` | Comma-separated: `python`, `java`, `javascript`, `go` |
| `--kubernetes` | off | Include Kubernetes deployment steps |
| `--registry URL` | `ghcr.io` | Container registry URL |
| `--k8s-method METHOD` | `kubectl` | `kubectl` \| `kustomize` \| `argocd` \| `flux` |
| `--output DIR` | `.github/workflows` | Output directory |
| `--custom-values FILE` | _(none)_ | Path to custom values JSON file |
| `--image IMAGE` | `ghcr.io/yourorg/devops-os:latest` | DevOps-OS container image |
| `--branches BRANCHES` | `main` | Comma-separated branches that trigger the workflow |
| `--matrix` | off | Enable matrix builds across OS/architectures |
| `--env-file FILE` | _(cli dir)_ | Path to `devcontainer.env.json` |
| `--reusable` | off | Generate a reusable workflow |

---

## Workflow Types

| Type | Description |
|------|-------------|
| `build` | Focuses on building and packaging your application |
| `test` | Focuses on running tests |
| `deploy` | Focuses on deploying to the target environment |
| `complete` | Combines build, test, and deploy stages |
| `reusable` | Creates a workflow callable from other workflows |

---

## Examples

### Python application — complete pipeline

```bash
python -m cli.scaffold_gha --name "Python App" --languages python --type complete
# Output: .github/workflows/python-app-complete.yml
```

### Java with Maven

```bash
python -m cli.scaffold_gha --name "Java Service" --languages java --custom-values maven-config.json
# Output: .github/workflows/java-service-complete.yml
```

### Multi-language microservices with Kubernetes

```bash
python -m cli.scaffold_gha \
  --name "Microservices" \
  --languages python,javascript,go \
  --kubernetes --k8s-method kustomize
# Output: .github/workflows/microservices-complete.yml
```

### Matrix build (cross-platform)

```bash
python -m cli.scaffold_gha --name "Node.js App" --languages javascript --matrix
# Output: .github/workflows/node-js-app-complete.yml
```

### Reusable workflow

```bash
python -m cli.scaffold_gha --name "shared" --type reusable
# Output: .github/workflows/shared-reusable.yml
```

---

## Environment Variables

All options can be set using environment variables prefixed with `DEVOPS_OS_GHA_`:

```bash
export DEVOPS_OS_GHA_NAME="API Service"
export DEVOPS_OS_GHA_TYPE="complete"
export DEVOPS_OS_GHA_LANGUAGES="python,go"
export DEVOPS_OS_GHA_KUBERNETES="true"
export DEVOPS_OS_GHA_K8S_METHOD="kustomize"
export DEVOPS_OS_GHA_MATRIX="true"

python -m cli.scaffold_gha
# Output: .github/workflows/api-service-complete.yml
```

---

## Kubernetes Deployment Methods

| Method | What happens |
|--------|-------------|
| `kubectl` | Direct deployment using `kubectl set image` and rollout status |
| `kustomize` | `kustomize edit set image` + `kubectl apply -k` |
| `argocd` | `argocd app set` + sync + wait |
| `flux` | `flux reconcile` + kustomization reconcile |

---

## Reusable Workflows

Call the generated reusable workflow from another workflow:

```yaml
jobs:
  call-devops-os-workflow:
    uses: ./.github/workflows/shared-reusable.yml
    with:
      languages: '{"python": true, "java": true}'
      deploy_environment: 'production'
```

---

## Custom Values File

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
    "parallel": 4
  },
  "deploy": {
    "environments": ["dev", "staging", "prod"],
    "approval_required": true,
    "rollback_enabled": true
  },
  "matrix": {
    "os": ["ubuntu-latest", "windows-latest", "macos-latest"],
    "architecture": ["x86_64", "arm64"]
  }
}
```

```bash
python -m cli.scaffold_gha --custom-values advanced-config.json
```

---

## Generated Workflow Structure

```yaml
name: My CI/CD
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/yourorg/devops-os:latest
    steps:
      - uses: actions/checkout@v3
      # Language-specific build steps...

  test:
    needs: build
    # ...

  deploy:
    needs: test
    if: github.event_name == 'push'
    # ...
```

---

## Best Practices

1. Start with `--type complete` and remove stages you don't need
2. Pin the `--image` to a specific tag in production
3. Use `--env-file` to align CI/CD with your local dev container
4. Use reusable workflows to standardize pipelines across multiple repos
5. Store secrets in GitHub Secrets, reference them with `${{ secrets.MY_SECRET }}`
