# GitLab CI Pipeline Generator

DevOps-OS can generate a complete `.gitlab-ci.yml` for your project in a single command.

## Quick Start

```bash
# Complete pipeline for a Python project
python -m cli.scaffold_gitlab --name my-app --languages python --type complete

# Build + test for a Java project
python -m cli.scaffold_gitlab --name java-api --languages java --type test

# Complete pipeline with Kubernetes deploy via ArgoCD
python -m cli.scaffold_gitlab --name my-app --languages python,go \
       --type complete --kubernetes --k8s-method argocd
```

## Command-Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `my-app` | Application / pipeline name |
| `--type` | `complete` | Pipeline type: `build`, `test`, `deploy`, `complete` |
| `--languages` | `python` | Comma-separated: `python`, `java`, `javascript`, `go` |
| `--kubernetes` | off | Include a Kubernetes deploy stage |
| `--k8s-method` | `kubectl` | Deployment method: `kubectl`, `kustomize`, `argocd`, `flux` |
| `--branches` | `main` | Branches that trigger deploy jobs |
| `--output` | `.gitlab-ci.yml` | Output file path |
| `--custom-values` | — | JSON file to override generated values |

All options can also be set via environment variables prefixed with `DEVOPS_OS_GITLAB_`
(e.g. `DEVOPS_OS_GITLAB_LANGUAGES=python,go`).

## Generated Pipeline Stages

### `build` stage

- Logs in to the GitLab Container Registry
- Runs language-specific compile / install steps (detected from project files)
- Builds and pushes a Docker image tagged with `$CI_COMMIT_SHORT_SHA` and `latest`

### `test` stage

Runs language-appropriate test jobs in separate CI jobs:

| Language | Image | Test command |
|----------|-------|-------------|
| Python | `python:3.11-slim` | `pytest --cov` |
| Java | `maven:3.9-eclipse-temurin-17` | `mvn test` / `gradle test` |
| JavaScript | `node:20-slim` | `npm test` |
| Go | `golang:1.21` | `go test ./...` |

Each test job uploads JUnit / coverage artifacts automatically.

### `deploy` stage (requires `--kubernetes`)

Deploys to your cluster using the selected method:

| Method | What happens |
|--------|-------------|
| `kubectl` | `kubectl set image` + rollout status check |
| `kustomize` | `kustomize edit set image` + `kubectl apply` |
| `argocd` | `argocd app set` + sync + wait |
| `flux` | `flux reconcile image repository` + kustomization |

## Example: Python + Docker + kubectl deploy

```bash
python -m cli.scaffold_gitlab \
  --name flask-api \
  --languages python \
  --type complete \
  --kubernetes \
  --k8s-method kubectl \
  --branches main,production
```

Generated file:

```yaml
stages:
  - build
  - test
  - deploy

variables:
  APP_NAME: flask-api
  IMAGE_TAG: $CI_COMMIT_SHORT_SHA
  REGISTRY: $CI_REGISTRY
  REGISTRY_IMAGE: $CI_REGISTRY_IMAGE

build:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker login ...
    - docker build ...
    - docker push ...

test:python:
  stage: test
  image: python:3.11-slim
  script:
    - pip install -r requirements.txt pytest pytest-cov
    - python -m pytest --cov=./ --cov-report=xml -v
  artifacts:
    reports:
      coverage_report: ...

deploy:kubernetes:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl set image deployment/flask-api ...
    - kubectl rollout status ...
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

## CI/CD Variables You Must Set

Set these in **GitLab → Settings → CI/CD → Variables**:

| Variable | Description |
|----------|-------------|
| `CI_REGISTRY_USER` | GitLab registry username (auto-set for GitLab) |
| `CI_REGISTRY_PASSWORD` | GitLab registry password (auto-set for GitLab) |
| `KUBE_CONTEXT` | kubectl context name |
| `KUBE_NAMESPACE` | Target Kubernetes namespace |
| `ARGOCD_SERVER` | ArgoCD server hostname (if using ArgoCD) |
| `ARGOCD_TOKEN` | ArgoCD API token (if using ArgoCD) |

## Related Guides

- [Getting Started](GETTING-STARTED.md)
- [GitHub Actions Generator](GITHUB-ACTIONS-README.md)
- [ArgoCD / Flux Config](ARGOCD-README.md)
- [Jenkins Pipeline Generator](JENKINS-PIPELINE-README.md)
